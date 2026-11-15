"""Histograma dos coeficientes da banda DCT, capa × estego — objetivo específico (e). Reanálise pós-feedback.

Análise posterior à coleta; não altera resultados.csv nem a regra de detecção (D-12).
O objetivo (e) prevê a análise de histograma dos coeficientes para a DCT. O Jsteg troca o LSB dos
coeficientes elegíveis (diferentes de 0 e de 1), e com bits pseudoaleatórios isso tende a igualar as
frequências dos pares de valores (2k, 2k+1): é o efeito que o qui-quadrado explora.

Para cada capa JPEG e a estego de cada taxa (regenerada em memória, conferida pelo SHA-256 de
resultados.csv), toma os coeficientes da banda nas posições elegíveis (v = coeficientes_banda(Y);
v[posicoes_elegiveis(v)], na ordem de inserção, D-18) e calcula:
- o histograma de -20 a 20, sem 0 e 1, como proporção dos coeficientes elegíveis;
- o índice de assimetria dos pares, A = Σ|h(2k) − h(2k+1)| / Σ(h(2k) + h(2k+1)), nos 19 pares
  (2k, 2k+1) de -20 a 19, exceto (0, 1). A = 0 é o equilíbrio total entre os pares;
em duas regiões: "global" (todos os coeficientes elegíveis) e "inserida" (as n primeiras posições
elegíveis, n = bits do payload, onde a inserção acontece; na capa, as mesmas posições).
A troca de LSB não cria nem remove 0 e 1, então as posições elegíveis são as mesmas na capa e na estego.

Diferença capa × estego por taxa: mediana [Q1; Q3] de ΔA = A_estego − A_capa e Wilcoxon pareado
(descritivo), com BH na família das 3 taxas de cada região.
Figura: proporção por valor (mediana com interquartil) e |assimetria| por par (mediana com
interquartil) na região inserida, capa × estego, uma coluna por taxa.

Uso: python scripts/histograma_dct.py <pasta da coleta> [pasta de saída]
"""
import hashlib, tempfile, pathlib
import numpy as np, pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import reanalise_comum as rc
from estatistica import corrigir_bh

VALORES = np.array([x for x in range(-20, 21) if x not in (0, 1)])
PARES = [(2 * k, 2 * k + 1) for k in range(-10, 10) if k != 0]          # 19 pares, -20..19
COR_CAPA, COR_ESTEGO = "#2a78d6", "#eb6834"                              # slots 1 e 2 da paleta categórica
fonte, saida = rc.argumentos()
res, lim = rc.ler_coleta(fonte)


def histograma(a):
    """Contagem por valor em VALORES e proporção sobre todos os coeficientes da amostra."""
    c = np.array([(a == x).sum() for x in VALORES], float)
    return c, c / max(len(a), 1)


def assimetria(cont):
    h = dict(zip(VALORES, cont))
    dif = sum(abs(h[a] - h[b]) for a, b in PARES); tot = sum(h[a] + h[b] for a, b in PARES)
    return dif / tot if tot else np.nan, [(h[a] - h[b]) / (h[a] + h[b]) if h[a] + h[b] else np.nan for a, b in PARES]


linhas, bins, pares_l = [], [], []
with tempfile.TemporaryDirectory() as tmp:
    for r in res[res.tecnica == "dct"].itertuples():
        jp = rc.capa_jpeg(r.id); Y0 = jp.Y; Y1 = rc.estego_dct(r.id, r.taxa, Y0)
        jp.Y = Y1; jp.write_dct(f"{tmp}/e.jpg")
        assert hashlib.sha256(pathlib.Path(f"{tmp}/e.jpg").read_bytes()).hexdigest() == r.sha256_estego, r.id
        c0, c1 = rc.amostra_dct(Y0), rc.amostra_dct(Y1)
        assert len(c0) == len(c1)                                      # mesmas posições elegíveis
        n = 8 * len(rc.payload(r.taxa))
        for regiao, (a0, a1) in {"global": (c0, c1), "inserida": (c0[:n], c1[:n])}.items():
            for papel, a in (("capa", a0), ("estego", a1)):
                cont, prop = histograma(a)
                A, por_par = assimetria(cont)
                linhas.append({"id": r.id, "categoria": r.categoria, "taxa": r.taxa, "regiao": regiao, "papel": papel,
                               "n_coef": len(a), "n_no_intervalo": int(cont.sum()), "assimetria": A})
                bins += [{"id": r.id, "taxa": r.taxa, "regiao": regiao, "papel": papel, "valor": int(v), "proporcao": p}
                         for v, p in zip(VALORES, prop)]
                pares_l += [{"id": r.id, "taxa": r.taxa, "regiao": regiao, "papel": papel, "par": f"{a}/{b}",
                             "assimetria_par": s} for (a, b), s in zip(PARES, por_par)]

df = pd.DataFrame(linhas); bins = pd.DataFrame(bins); pares_df = pd.DataFrame(pares_l)
w = df.pivot_table(index=["id", "categoria", "taxa", "regiao"], columns="papel", values="assimetria").reset_index()
w["delta"] = w.estego - w.capa


def q3(x):
    return float(np.median(x)), float(np.quantile(x, .25)), float(np.quantile(x, .75))


resumo = []
for regiao in ("global", "inserida"):
    bloco = []
    for tx in rc.TAXAS:
        g = w[(w.regiao == regiao) & (w.taxa == tx)]
        row = {"regiao": regiao, "taxa": tx, "n": len(g)}
        for k in ("capa", "estego", "delta"):
            row[f"{k}_mediana"], row[f"{k}_q1"], row[f"{k}_q3"] = q3(g[k])
        row["reducao_relativa_mediana"] = float(np.median(g.delta / g.capa))
        row["n_estego_menor"] = int((g.delta < 0).sum())
        row["p_wilcoxon"] = float(stats.wilcoxon(g.estego, g.capa).pvalue)
        bloco.append(row)
    for row, pb in zip(bloco, corrigir_bh([b["p_wilcoxon"] for b in bloco])):
        row["p_bh"] = float(pb)
    resumo += bloco
resumo = pd.DataFrame(resumo)
# mediana por textura (região inserida), para contexto
tex = (w[w.regiao == "inserida"].groupby(["taxa", "categoria"])[["capa", "estego", "delta"]].median().reset_index())

w.to_csv(saida / "histograma_dct_assimetria.csv", index=False, lineterminator="\n", float_format="%.17g")
resumo.to_csv(saida / "histograma_dct_resumo.csv", index=False, lineterminator="\n", float_format="%.17g")
agg = (bins.groupby(["taxa", "regiao", "papel", "valor"]).proporcao
       .agg(mediana="median", q1=lambda s: s.quantile(.25), q3=lambda s: s.quantile(.75)).reset_index())
agg.to_csv(saida / "histograma_dct_bins.csv", index=False, lineterminator="\n", float_format="%.17g")
aggp = (pares_df.assign(abs_assim=pares_df.assimetria_par.abs()).groupby(["taxa", "regiao", "papel", "par"], sort=False)
        .abs_assim.agg(mediana="median", q1=lambda s: s.quantile(.25), q3=lambda s: s.quantile(.75)).reset_index())
aggp.to_csv(saida / "histograma_dct_pares.csv", index=False, lineterminator="\n", float_format="%.17g")

# Figura: linha 1 = histograma global (proporção, escala log); linha 2 = |assimetria| por par na região inserida
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#8a8a85", "axes.labelcolor": "#3d3d3a", "xtick.color": "#5f5e5a",
                     "ytick.color": "#5f5e5a", "grid.color": "#e6e5e0", "grid.linewidth": 0.6})
fig, ax = plt.subplots(2, 3, figsize=(11, 6.2), sharey="row", constrained_layout=True)
NOME = {"baixa": "Taxa baixa (0,004 bpp)", "media": "Taxa média (0,03 bpp)", "alta": "Taxa alta (0,06 bpp)"}
rot_par = [f"{a}/{b}" for a, b in PARES]; xp = np.arange(len(PARES))
for j, tx in enumerate(rc.TAXAS):
    a0 = ax[0, j]
    for papel, cor, ls, nome in (("capa", COR_CAPA, "--", "Capa"), ("estego", COR_ESTEGO, "-", "Estego")):
        g = agg[(agg.taxa == tx) & (agg.regiao == "global") & (agg.papel == papel)].sort_values("valor")
        for lado in (g.valor < 0, g.valor > 0):                        # 0 e 1 ficam de fora: quebra a linha no meio
            h = g[lado]
            a0.fill_between(h.valor, h.q1, h.q3, color=cor, alpha=0.18, linewidth=0)
            a0.plot(h.valor, h.mediana, color=cor, ls=ls, lw=2, label=nome if lado.iloc[0] else None)
    a0.set_yscale("log"); a0.set_title(NOME[tx], fontsize=10, color="#1f1f1d"); a0.grid(axis="y")
    a0.set_xlabel("Valor do coeficiente (sem 0 e 1)")
    a1 = ax[1, j]
    for papel, cor, ls, nome in (("capa", COR_CAPA, "--", "Capa (mesmas posições)"), ("estego", COR_ESTEGO, "-", "Estego")):
        g = aggp[(aggp.taxa == tx) & (aggp.regiao == "inserida") & (aggp.papel == papel)].set_index("par").loc[rot_par]
        a1.fill_between(xp, g.q1, g.q3, color=cor, alpha=0.18, linewidth=0)
        a1.plot(xp, g.mediana, color=cor, ls=ls, lw=2, marker="o", ms=4, label=nome)
    a1.set_xticks(xp, rot_par, rotation=90, fontsize=6.5); a1.grid(axis="y")
    a1.set_xlabel("Par (2k / 2k+1)")
ax[0, 0].set_ylabel("Proporção dos coeficientes elegíveis\n(todas as posições; escala log)")
ax[1, 0].set_ylabel("|h(2k) − h(2k+1)| / (h(2k) + h(2k+1))\nnas n posições usadas pela inserção")
ax[0, 0].legend(frameon=False, loc="upper left"); ax[1, 0].legend(frameon=False, loc="upper left")
fig.suptitle("Coeficientes da banda DCT nas posições elegíveis: capa × estego (mediana e intervalo interquartil, n = 90 por curva)",
             fontsize=10, color="#1f1f1d")
fig.savefig(saida / "histograma_dct.png", dpi=200); plt.close(fig)

# Relatório
b = rc.br
md = ["# Histograma dos coeficientes da banda DCT: capa × estego (objetivo e)", "",
      f"Fonte: `{fonte}` (commit da coleta a8ef486). Estego DCT regeneradas em memória: 270/270 com o mesmo SHA-256 de "
      "resultados.csv. Análise posterior à coleta e descritiva; a detecção pré-registrada continua sendo o qui-quadrado (D-12).",
      "Coeficientes da banda nas posições elegíveis (≠ 0 e ≠ 1), na ordem de inserção. Assimetria dos pares "
      "A = Σ|h(2k) − h(2k+1)| / Σ(h(2k) + h(2k+1)) nos 19 pares de −20 a 19 (sem 0/1); A = 0 é o equilíbrio total. "
      "Região global = todas as posições elegíveis; região inserida = as n primeiras (n = 1.048, 7.864 e 15.728 bits).", "",
      "| Região | Taxa | A capa: mediana [Q1; Q3] | A estego: mediana [Q1; Q3] | ΔA: mediana [Q1; Q3] | Redução relativa mediana | Estego < capa | Wilcoxon p | p BH |",
      "|---|---|---|---|---|---|---|---|---|"]
for r in resumo.itertuples():
    md.append(f"| {r.regiao} | {r.taxa} | {b(r.capa_mediana, 4)} [{b(r.capa_q1, 4)}; {b(r.capa_q3, 4)}] | "
              f"{b(r.estego_mediana, 4)} [{b(r.estego_q1, 4)}; {b(r.estego_q3, 4)}] | {b(r.delta_mediana, 4)} "
              f"[{b(r.delta_q1, 4)}; {b(r.delta_q3, 4)}] | {rc.pc(-r.reducao_relativa_mediana)} | {r.n_estego_menor}/{r.n} | "
              f"{r.p_wilcoxon:.1e} | {r.p_bh:.1e} |".replace("e-", "e−").replace(".", ","))
md += ["", "Mediana de A na região inserida por textura:", "",
       "| Taxa | Textura | A capa | A estego | ΔA |", "|---|---|---|---|---|"]
for r in tex.sort_values(["taxa", "categoria"], key=lambda s: s.map({t: i for i, t in enumerate(rc.TAXAS)})).itertuples():
    md.append(f"| {r.taxa} | {r.categoria} | {b(r.capa, 4)} | {b(r.estego, 4)} | {b(r.delta, 4)} |")
G = resumo[resumo.regiao == "global"].set_index("taxa"); I = resumo[resumo.regiao == "inserida"].set_index("taxa")
md += ["", "Figura: `histograma_dct.png`.", "", "## Leitura", "",
       f"- Na região inserida, a assimetria dos pares cai de {b(I.loc['baixa'].capa_mediana, 3)} → {b(I.loc['baixa'].estego_mediana, 3)} "
       f"(taxa baixa), {b(I.loc['media'].capa_mediana, 3)} → {b(I.loc['media'].estego_mediana, 3)} (média) e "
       f"{b(I.loc['alta'].capa_mediana, 3)} → {b(I.loc['alta'].estego_mediana, 3)} (alta), medianas, com a estego abaixo da capa em "
       f"{I.loc['baixa'].n_estego_menor}, {I.loc['media'].n_estego_menor} e {I.loc['alta'].n_estego_menor} das 90 imagens: é o "
       "equilíbrio dos pares 2k/2k+1 esperado do Jsteg.",
       f"- No histograma global (todas as posições elegíveis), o efeito é diluído: a redução relativa mediana de A é "
       f"{rc.pc(-G.loc['baixa'].reducao_relativa_mediana)}, {rc.pc(-G.loc['media'].reducao_relativa_mediana)} e "
       f"{rc.pc(-G.loc['alta'].reducao_relativa_mediana)}, porque o payload ocupa só as primeiras posições elegíveis.",
       "- Os p-valores do Wilcoxon são descritivos (análise não prevista na metodologia).", ""]
rc.escrever(saida / "histograma_dct.md", "\n".join(md) + "\n")
rc.proveniencia(saida, "histograma_dct", fonte, {
    "valores": [int(v) for v in VALORES], "pares": [list(p) for p in PARES], "estego_sha256_confere": "270/270",
    "indice_assimetria": "A = soma|h(2k)-h(2k+1)| / soma(h(2k)+h(2k+1)) nos 19 pares",
    "regioes": {"global": "todas as posições elegíveis", "inserida": "n primeiras posições elegíveis, n = bits do payload"},
    "teste": "Wilcoxon pareado (scipy.stats.wilcoxon), BH na família das 3 taxas de cada região",
    "cores_figura": {"capa": COR_CAPA, "estego": COR_ESTEGO}})
print("\n".join(md))
