"""Diagnóstico das janelas do qui-quadrado nas capas limpas (FP em PNG). Reanálise pós-feedback.

Análise de sensibilidade posterior à coleta; não altera resultados.csv, limpas.csv nem p_max.
Para cada uma das 180 capas limpas (90 PNG, 90 JPEG) recalcula o p-valor de cada uma das 100 janelas
acumuladas (1%, 2%, ..., 100%) com a mesma lógica de src/quiquadrado.p_max e a mesma ordem de leitura
de analisar_limpas.py (D-18), e registra: a janela k% em que saiu o máximo (a primeira, se houver
empate), o p só na janela de 100% e o p na janela de 1%. Compara as capas PNG com p_max >= 0,95
(os FP da coleta) com todas as capas de cada formato e conta quantas capas seriam FP se a regra usasse
só a janela de 100%.

Validação: o máximo recalculado tem de reproduzir o p_max de limpas.csv (igual ou até 1 ULP, com todas
as decisões em 0,95 e 0,99 idênticas; ver reanalise_comum.conferir_p).

Uso: python scripts/diag_fp_janelas.py <pasta da coleta> [pasta de saída]
     (saída padrão: resultados/reanalise_pos_feedback; recusa gravar em resultados/experimento)
"""
import numpy as np, pandas as pd
import reanalise_comum as rc
from quiquadrado import p_valor_janela, p_max
from estatistica import taxa_com_ic

PASSOS = 100
fonte, saida = rc.argumentos()
res, lim = rc.ler_coleta(fonte)


def ps_janelas(a, passos=PASSOS):
    """p-valor de cada janela k = 1..passos, como em p_max (nan = janela vazia ou pequena demais)."""
    ps = np.full(passos, np.nan)
    for k in range(1, passos + 1):
        n = int(len(a) * k / passos)
        if n > 0:
            ps[k - 1] = p_valor_janela(a[:n])
    return ps


linhas, matriz = [], []
for r in lim.itertuples():
    a = rc.amostra_lsb(rc.capa_png(r.id)) if r.formato == "png" else rc.amostra_dct(rc.capa_jpeg(r.id).Y)
    ps = ps_janelas(a)
    validos = ps[~np.isnan(ps)]
    pm = float(validos.max())
    assert pm == p_max(a), "máximo das janelas difere de p_max"
    k_max = int(np.flatnonzero(ps == pm)[0]) + 1
    linhas.append({"formato": r.formato, "id": r.id, "categoria": r.categoria, "n_amostra": len(a),
                   "p_max_coleta": r.p_max, "p_max_recalc": pm, "k_max": k_max,
                   "n_janela_max": int(len(a) * k_max / PASSOS), "p_100": ps[-1], "p_1": ps[0],
                   "n_janelas_validas": int(validos.size), "n_janelas_p_ge_095": int((validos >= rc.LIMIAR).sum()),
                   "fp_coleta": bool(r.falso_positivo), "fp_so_100": bool(ps[-1] >= rc.LIMIAR)})
    matriz.append({"formato": r.formato, "id": r.id, **{f"p_{k:03d}": ps[k - 1] for k in range(1, PASSOS + 1)}})

df = pd.DataFrame(linhas)
conf = rc.conferir_p(df.p_max_recalc, df.p_max_coleta, "p_max das 180 capas limpas × limpas.csv")
conf["casos_nao_identicos"] = [{**c, "formato": df.formato[c["indice"]], "id": df.id[c["indice"]]}
                               for c in conf["casos_nao_identicos"]]
fp = df[(df.formato == "png") & (df.p_max_coleta >= rc.LIMIAR)]
assert len(fp) == 16 and fp.categoria.value_counts().to_dict() == {"alta": 9, "media": 6, "baixa": 1}, \
    f"esperados 16 FP PNG (1/6/9): {fp.categoria.value_counts().to_dict()}"


def resumo(g, nome):
    k = g.k_max
    w100 = taxa_com_ic(int(g.fp_so_100.sum()), len(g)); wcol = taxa_com_ic(int(g.fp_coleta.sum()), len(g))
    return {"grupo": nome, "n": len(g),
            "k_max_mediana": float(k.median()), "k_max_q1": float(k.quantile(.25)), "k_max_q3": float(k.quantile(.75)),
            "k_max_le_5": int((k <= 5).sum()), "k_max_le_10": int((k <= 10).sum()), "k_max_eq_1": int((k == 1).sum()),
            "k_max_eq_100": int((k == 100).sum()),
            "p_100_mediana": float(g.p_100.median()), "p_100_max": float(g.p_100.max()),
            "p_1_mediana": float(g.p_1.median()), "p_1_ge_095": int((g.p_1 >= rc.LIMIAR).sum()),
            "fp_coleta": int(g.fp_coleta.sum()), "fp_coleta_taxa": wcol[0], "fp_coleta_ic_inf": wcol[1], "fp_coleta_ic_sup": wcol[2],
            "fp_so_100": int(g.fp_so_100.sum()), "fp_so_100_taxa": w100[0], "fp_so_100_ic_inf": w100[1],
            "fp_so_100_ic_sup": w100[2]}


png, jpg = df[df.formato == "png"], df[df.formato == "jpeg"]
grupos = [resumo(fp, "png_fp_coleta"), resumo(png[png.p_max_coleta < rc.LIMIAR], "png_sem_fp"),
          resumo(png, "png_todas"), resumo(jpg, "jpeg_todas")]
for f, g in (("png", png), ("jpeg", jpg)):
    for c in rc.CATEGORIAS:
        grupos.append(resumo(g[g.categoria == c], f"{f}_{c}"))
tab = pd.DataFrame(grupos)

df.to_csv(saida / "diag_fp_janelas.csv", index=False, lineterminator="\n", float_format="%.17g")
pd.DataFrame(matriz).to_csv(saida / "diag_fp_janelas_p_por_janela.csv", index=False, lineterminator="\n", float_format="%.17g")
tab.to_csv(saida / "diag_fp_janelas_resumo.csv", index=False, lineterminator="\n", float_format="%.17g")

# Relatório
def nm(x, d=4):
    if x != x: return "nan"
    if x != 0 and abs(x) < 1e-3: return f"{x:.1e}".replace(".", ",")
    return f"{x:.{d}f}".replace(".", ",")


T = {r.grupo: r for r in tab.itertuples()}
g_ = lambda x: f"{x:g}".replace(".", ",")
n1_png = int(png.n_amostra.iloc[0] * 1 / PASSOS); n1_jpg = (jpg.n_amostra * 1 / PASSOS).astype(int)
assert (png.n_amostra == rc.N_PIXELS).all()
t0, tp, tj, ts = T["png_fp_coleta"], T["png_todas"], T["jpeg_todas"], T["png_sem_fp"]
md = ["# Diagnóstico das janelas do qui-quadrado nas capas limpas", "",
      f"Fonte: `{fonte}` (limpas.csv, commit da coleta a8ef486). Reanálise posterior à coleta; p_max e os "
      "resultados pré-registrados não mudam.",
      f"Validação: o máximo das 100 janelas recalculado reproduz o p_max de limpas.csv — {conf['n_identicos']}/180 "
      f"idênticos e {conf['n_ate_1ulp']}/180 até 1 ULP (diferença absoluta máxima {conf['diferenca_absoluta_maxima']:.1e}); "
      "decisões em 0,95 e 0,99 idênticas.", "",
      "## Capas PNG com FP na coleta (p_max ≥ 0,95)", "",
      "| id | textura | p_max | janela do máximo (k%) | n na janela | p na janela de 100% | p na janela de 1% | janelas com p ≥ 0,95 |",
      "|---|---|---|---|---|---|---|---|"]
for r in fp.sort_values(["categoria", "k_max", "id"]).itertuples():
    md.append(f"| {r.id} | {r.categoria} | {nm(r.p_max_recalc, 6)} | {r.k_max} | {r.n_janela_max} | {nm(r.p_100)} | "
              f"{nm(r.p_1)} | {r.n_janelas_p_ge_095}/100 |")
md += ["", "## Comparação por grupo", "",
       "| Grupo | n | k do máximo: mediana [Q1; Q3] | k = 1% | k ≤ 5% | k = 100% | p(100%) mediana | p(100%) máx. | p(1%) ≥ 0,95 | FP (regra D-12) | FP só com a janela de 100% (IC 95%) |",
       "|---|---|---|---|---|---|---|---|---|---|---|"]
for r in tab.itertuples():
    md.append(f"| {r.grupo} | {r.n} | {g_(r.k_max_mediana)} [{g_(r.k_max_q1)}; {g_(r.k_max_q3)}] | {r.k_max_eq_1} | {r.k_max_le_5} | "
              f"{r.k_max_eq_100} | {nm(r.p_100_mediana)} | {nm(r.p_100_max)} | {r.p_1_ge_095} | {r.fp_coleta} | "
              f"{r.fp_so_100}/{r.n} — {rc.pc(r.fp_so_100_taxa)} [{rc.pc(r.fp_so_100_ic_inf)}; {rc.pc(r.fp_so_100_ic_sup)}] |")
md += ["", "## Leitura", "",
       f"- Nos {t0.n} FP em PNG, o máximo saiu na janela de 1% em {t0.k_max_eq_1} casos e em k ≤ 5% em {t0.k_max_le_5} "
       f"(k mediano {g_(t0.k_max_mediana)}%; Q1–Q3 {g_(t0.k_max_q1)}–{g_(t0.k_max_q3)}%); em nenhum caso o máximo esteve na janela "
       f"de 100% ({t0.k_max_eq_100} de {t0.n}). Nos {t0.p_1_ge_095} de {t0.n}, a janela de 1% sozinha já dá p ≥ 0,95; "
       f"nenhuma das 74 PNG sem FP tem p ≥ 0,95 nessa janela. Na janela de 100%, o p mediano desses FP é "
       f"{nm(t0.p_100_mediana)} (máximo {nm(t0.p_100_max)}).",
       f"- Se a regra usasse só a janela de 100%, seriam FP {tp.fp_so_100} de 90 capas PNG "
       f"({rc.pc(tp.fp_so_100_taxa)} [{rc.pc(tp.fp_so_100_ic_inf)}; {rc.pc(tp.fp_so_100_ic_sup)}]) e {tj.fp_so_100} de 90 JPEG, "
       f"contra {tp.fp_coleta} e {tj.fp_coleta} com a regra da D-12.",
       f"- Comparação: nas 74 PNG sem FP, k = 1% em {ts.k_max_eq_1}; nas 90 JPEG, k = 1% em {tj.k_max_eq_1} "
       f"(k mediano {g_(tj.k_max_mediana)}%). A janela de 1% tem {n1_png} pixels no PNG (as ~5 primeiras linhas da imagem) e "
       f"de {n1_jpg.min()} a {n1_jpg.max()} coeficientes elegíveis no JPEG.", ""]
(saida / "diag_fp_janelas.md").write_text("\n".join(md) + "\n", encoding="utf-8")
rc.proveniencia(saida, "diag_fp_janelas", fonte, {
    "validacao_p_max": conf, "regra_k_max": "primeira janela k (1..100) cujo p é igual ao máximo",
    "limiar": rc.LIMIAR, "regra_so_100": "FP se p da janela de 100% >= 0,95"})
print("\n".join(md))
