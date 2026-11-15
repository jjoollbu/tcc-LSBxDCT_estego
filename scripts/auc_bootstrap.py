"""IC 95% por bootstrap da AUC do p_max (estego × capas limpas). Reanálise pós-feedback.

Análise exploratória posterior à coleta; não altera os resultados pré-registrados.
Definição da AUC (a mesma da Tabela 6 do artigo; scripts/analise.py não calcula AUC): área sob a curva
ROC do p_max, comparando as 90 capas limpas e as 90 estego do mesmo formato (LSB × PNG, DCT × JPEG),
por técnica e taxa, sem limiar de decisão. Pela estatística de Mann-Whitney,
    AUC = P(p_estego > p_limpa) + 0,5 · P(p_estego = p_limpa).
IC 95%: bootstrap estratificado (reamostra com reposição, separadamente, as 90 estego e as 90 capas
limpas), 2.000 reamostragens, intervalo por percentil (2,5% e 97,5%). Semente fixa: fluxo 5 da
SeedSequence da semente mestra 2026 (sementes.py usa os fluxos 1 a 4; o 5º é novo e independente).
O mesmo é feito com o p_max_absoluto (passos 128, 256 e 512) gravado por reanalise_janelas_absolutas.py.
A reamostragem estratificada trata as duas classes como amostras independentes, embora sejam as mesmas
90 imagens (com e sem payload); não usa esse pareamento.

Uso: python scripts/auc_bootstrap.py <pasta da coleta> [pasta de saída]
     (requer <saída>/p_max_absoluto.csv de reanalise_janelas_absolutas.py)
"""
import numpy as np, pandas as pd
import reanalise_comum as rc
from sementes import SEED_MESTRA

B, NIVEL = 2000, 0.95
SEED_SEQ = np.random.SeedSequence(SEED_MESTRA).spawn(5)[4]
fonte, saida = rc.argumentos()
res, lim = rc.ler_coleta(fonte)
pabs = pd.read_csv(saida / "p_max_absoluto.csv", dtype={"id": str}, **rc.CSV_FLOAT)
REGRAS = {"original_1pct": None, "absoluta_128": "p_abs_128", "absoluta_256": "p_abs_256", "absoluta_512": "p_abs_512"}

# confere que p_max_absoluto.csv corresponde a esta coleta (mesmo p_max da coleta em todas as linhas)
chave = ["grupo", "tecnica", "taxa", "id"]
col = pd.concat([res.assign(grupo="estego")[["grupo", "tecnica", "taxa", "id", "p_max"]],
                 lim.assign(grupo="limpa", tecnica=lim.formato.map({"png": "lsb", "jpeg": "dct"}), taxa="limpa")
                 [["grupo", "tecnica", "taxa", "id", "p_max"]]])
m = pabs.merge(col, on=chave, how="outer", validate="1:1", indicator=True)
assert (m._merge == "both").all() and (m.p_max_coleta == m.p_max).all(), "p_max_absoluto.csv não corresponde à coleta"


def auc(pos, neg):
    """Mann-Whitney: P(pos > neg) + 0,5 P(pos = neg). pos/neg em 2D (reamostragens × n) ou 1D. nan conta como 0."""
    pos, neg = np.nan_to_num(np.atleast_2d(pos), nan=0.0), np.nan_to_num(np.atleast_2d(neg), nan=0.0)
    gt = (pos[:, :, None] > neg[:, None, :]).mean(axis=(1, 2)); eq = (pos[:, :, None] == neg[:, None, :]).mean(axis=(1, 2))
    return gt + 0.5 * eq


rng = np.random.default_rng(SEED_SEQ)
linhas = []
for regra, coluna in REGRAS.items():
    for tc, f in rc.FORMATO.items():
        if coluna is None:
            neg_all = lim[lim.formato == f].sort_values("id").p_max.to_numpy()
        else:
            neg_all = pabs[(pabs.grupo == "limpa") & (pabs.tecnica == tc)].sort_values("id")[coluna].to_numpy()
        for tx in rc.TAXAS:
            if coluna is None:
                pos = res[(res.tecnica == tc) & (res.taxa == tx)].sort_values("id").p_max.to_numpy()
            else:
                pos = pabs[(pabs.grupo == "estego") & (pabs.tecnica == tc) & (pabs.taxa == tx)].sort_values("id")[coluna].to_numpy()
            assert len(pos) == len(neg_all) == 90
            a = float(auc(pos, neg_all)[0])
            ip = rng.integers(0, len(pos), (B, len(pos))); ineg = rng.integers(0, len(neg_all), (B, len(neg_all)))
            boot = auc(pos[ip], neg_all[ineg])
            lo, hi = np.quantile(boot, [(1 - NIVEL) / 2, 1 - (1 - NIVEL) / 2])
            linhas.append({"regra": regra, "tecnica": tc, "formato": f, "taxa": tx, "n_estego": len(pos), "n_limpas": len(neg_all),
                           "auc": a, "ic_inf": float(lo), "ic_sup": float(hi), "boot_media": float(boot.mean()),
                           "boot_dp": float(boot.std(ddof=1)), "frac_boot_igual_1": float((boot == 1).mean())})
tab = pd.DataFrame(linhas)
tab.to_csv(saida / "auc_bootstrap.csv", index=False, lineterminator="\n", float_format="%.17g")

# a AUC original tem de reproduzir os valores da Tabela 6 do artigo (2 casas)
ARTIGO = {("lsb", "baixa"): 0.62, ("lsb", "media"): 0.88, ("lsb", "alta"): 0.89,
          ("dct", "baixa"): 0.95, ("dct", "media"): 1.00, ("dct", "alta"): 1.00}
o = tab[tab.regra == "original_1pct"].set_index(["tecnica", "taxa"]).auc
confere = {f"{k[0]}_{k[1]}": {"artigo": v, "recalculado": round(float(o.loc[k]), 4), "igual_2_casas": round(float(o.loc[k]), 2) == v}
           for k, v in ARTIGO.items()}

rot = {"original_1pct": "Original (janelas de 1%)", "absoluta_128": "Absoluta, passo 128",
       "absoluta_256": "Absoluta, passo 256", "absoluta_512": "Absoluta, passo 512"}
b = rc.br
md = ["# AUC do p_max com IC 95% por bootstrap estratificado", "",
      f"Fonte: `{fonte}` (commit da coleta a8ef486) e `p_max_absoluto.csv`. Análise exploratória posterior à coleta.",
      "AUC = P(p_estego > p_limpa) + 0,5·P(empate), 90 estego × 90 capas limpas do mesmo formato, por técnica e taxa "
      f"(definição da Tabela 6). Bootstrap estratificado por classe, {B} reamostragens, IC por percentil; semente: fluxo 5 "
      "da SeedSequence(2026). As duas classes são as mesmas 90 imagens; o bootstrap não usa esse pareamento.",
      "Conferência com a Tabela 6 (2 casas): " + ", ".join(f"{k} {'ok' if v['igual_2_casas'] else 'DIFERE'}" for k, v in confere.items()) + ".",
      "", "| Regra | Técnica | Taxa | AUC | IC 95% | Reamostragens com AUC = 1 |", "|---|---|---|---|---|---|"]
for r in tab.itertuples():
    md.append(f"| {rot[r.regra]} | {r.tecnica.upper()} | {r.taxa} | {b(r.auc, 3)} | [{b(r.ic_inf, 3)}; {b(r.ic_sup, 3)}] | "
              f"{rc.pc(r.frac_boot_igual_1)} |")
O = tab[tab.regra == "original_1pct"].set_index(["tecnica", "taxa"])
A = tab[tab.regra == "absoluta_256"].set_index(["tecnica", "taxa"])
f = lambda T, tc, tx: f"{b(T.loc[(tc, tx)].auc, 3)} [{b(T.loc[(tc, tx)].ic_inf, 3)}; {b(T.loc[(tc, tx)].ic_sup, 3)}]"
sobrepoe = {tx: bool(O.loc[("lsb", tx)].ic_sup >= O.loc[("dct", tx)].ic_inf) for tx in rc.TAXAS}
md += ["", "## Leitura", "",
       "- Regra original: LSB " + ", ".join(f"{tx} {f(O, 'lsb', tx)}" for tx in rc.TAXAS) + "; DCT "
       + ", ".join(f"{tx} {f(O, 'dct', tx)}" for tx in rc.TAXAS) + ".",
       "- Os IC de LSB e DCT " + "; ".join(f"{'se sobrepõem' if v else 'não se sobrepõem'} na taxa {tx}" for tx, v in sobrepoe.items())
       + ". IC sem sobreposição não é um teste formal da diferença; a comparação pareada pré-registrada é o McNemar.",
       "- Janelas absolutas (passo 256): LSB " + ", ".join(f"{tx} {f(A, 'lsb', tx)}" for tx in rc.TAXAS) + "; DCT "
       + ", ".join(f"{tx} {f(A, 'dct', tx)}" for tx in rc.TAXAS) + ".",
       f"- Com AUC perto de 1 (DCT, taxas média e alta), parte das reamostragens dá AUC = 1 "
       f"({rc.pc(O.loc[('dct', 'media')].frac_boot_igual_1)} e {rc.pc(O.loc[('dct', 'alta')].frac_boot_igual_1)} na regra original) "
       "e o limite superior do IC fica em 1; o IC por percentil é pouco informativo nesse extremo.", ""]
rc.escrever(saida / "auc_bootstrap.md", "\n".join(md) + "\n")
rc.proveniencia(saida, "auc_bootstrap", fonte, {
    "definicao_auc": "Mann-Whitney: P(p_estego > p_limpa) + 0,5 P(empate); nan conta como 0",
    "bootstrap": {"tipo": "estratificado por classe (estego e limpas reamostradas separadamente)", "reamostragens": B,
                  "ic": "percentil 2,5% e 97,5%", "semente": "SeedSequence(2026).spawn(5)[4] (fluxo 5)"},
    "confere_tabela6_artigo": confere})
print("\n".join(md))
