"""Reanálise da detecção sob o limiar 0,99 (calibração pré-registrada da D-12).

Só reclassifica. Lê o p_max contínuo que a coleta congelada já gravou em resultados.csv (estego) e
limpas.csv (capas sem payload) e reaplica a regra da D-12 — detectado se p_max >= limiar — com o
limiar vigente (0,95) e com 0,99. Não roda o detector, não abre imagens e não toca em custo nem em
qualidade: o limiar não afeta essas métricas. Como o p_max não é recalculado, a seed e a ordem das
janelas (D-18) são as da coleta.

A regra de decisão é a mesma comparação usada em analise.py e analisar_limpas.py (src/quiquadrado.py
só documenta a regra; não há função de decisão para importar). FP/FN usam o IC de Wilson e a detecção
usa o McNemar exato com BH dentro da família, todos de src/estatistica.py, como em analise.py.

Uso: python scripts/reanalise_limiar.py <pasta da coleta> [pasta de saída]
     (saída padrão: resultados/experimento_lim099; recusa gravar em resultados/experimento)
"""
import sys, json, hashlib, pathlib, subprocess, datetime
import numpy as np, pandas as pd
RAIZ = pathlib.Path(__file__).parents[1]; sys.path.insert(0, str(RAIZ / "src"))
from estatistica import comparar_deteccao, taxa_com_ic, corrigir_bh

LIMIARES = (0.95, 0.99)                       # vigente (D-12) e calibração pré-registrada (D-12)
TAXAS = ("baixa", "media", "alta")
FORMATO = {"lsb": "png", "dct": "jpeg"}       # LSB em PNG, DCT/Jsteg em JPEG QF95

fonte = pathlib.Path(sys.argv[1]).resolve()
saida = pathlib.Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else RAIZ / "resultados" / "experimento_lim099"
if saida == fonte or saida == (RAIZ / "resultados" / "experimento").resolve():
    sys.exit(f"Recusado: {saida} é a pasta da coleta congelada. Grave a reanálise em outra pasta.")

res = pd.read_csv(fonte / "resultados.csv", dtype={"id": str})
lim = pd.read_csv(fonte / "limpas.csv", dtype={"id": str})
assert set(res.tecnica) == set(FORMATO) and set(res.taxa) == set(TAXAS), "resultados.csv inesperado"
assert not res.duplicated(["tecnica", "taxa", "id"]).any(), "combinações repetidas em resultados.csv"
res["formato"] = res.tecnica.map(FORMATO)


def wilson(eventos, n):
    taxa, inf, sup = taxa_com_ic(int(eventos), int(n))
    return taxa, inf, sup


fp_l, fn_l, det_l = [], [], []
for L in LIMIARES:
    det = res.p_max >= L                       # nan (sem janela válida) => não detectado, como na coleta
    pos = lim.p_max >= L

    # Capas limpas: FP e especificidade por formato
    for f, g in lim.assign(pos=pos).groupby("formato"):
        n, k = len(g), int(g.pos.sum())
        fp, fi, fs = wilson(k, n); es, ei, ess = wilson(n - k, n)
        fp_l.append({"limiar": L, "formato": f, "n": n, "fp_n": k, "fp": fp, "fp_ic_inf": fi, "fp_ic_sup": fs,
                     "especificidade": es, "esp_ic_inf": ei, "esp_ic_sup": ess})

    # Estego: FN e sensibilidade por formato × taxa e no agregado do formato
    for (tc, f), g in res.assign(det=det).groupby(["tecnica", "formato"]):
        for tx, h in [*((t, g[g.taxa == t]) for t in TAXAS), ("agregado", g)]:
            n, k = len(h), int((~h.det).sum())
            fn, fi, fs = wilson(k, n); se, si, ss = wilson(n - k, n)
            fn_l.append({"limiar": L, "tecnica": tc, "formato": f, "taxa": tx, "n": n, "fn_n": k, "fn": fn,
                         "fn_ic_inf": fi, "fn_ic_sup": fs, "sensibilidade": se, "sens_ic_inf": si, "sens_ic_sup": ss})

    # Teste principal: McNemar exato LSB × DCT por taxa (mesmas imagens), BH na família de 3 testes
    linhas = []
    for tx in TAXAS:
        w = res.assign(det=det)[res.taxa == tx].pivot(index="id", columns="tecnica", values="det").dropna()
        a, b = w["lsb"].astype(bool).to_numpy(), w["dct"].astype(bool).to_numpy()
        linhas.append({"limiar": L, "taxa": tx, "n_pares": len(w), "ambos": int((a & b).sum()),
                       "so_lsb": int((a & ~b).sum()), "so_dct": int((~a & b).sum()), "nenhum": int((~a & ~b).sum()),
                       "det_lsb": a.mean(), "det_dct": b.mean(), **comparar_deteccao(a, b)})
    p_bh = corrigir_bh([x["p"] for x in linhas])
    for x, q in zip(linhas, p_bh):
        x["p_bh"] = q
        x["mais_detectada"] = "dct" if x["so_dct"] > x["so_lsb"] else "lsb" if x["so_lsb"] > x["so_dct"] else "empate"
        x["significativo_bh"] = bool(q < 0.05)
    det_l += linhas

tfp, tfn, tdet = pd.DataFrame(fp_l), pd.DataFrame(fn_l), pd.DataFrame(det_l)

# Comparativo lado a lado (formato × taxa): FP/especificidade vêm das capas limpas e não dependem da taxa
lado = lambda t, cols: t.pivot_table(index=[c for c in t.columns if c in ("formato", "taxa")], columns="limiar",
                                       values=cols, aggfunc="first")
fn_w = lado(tfn, ["fn_n", "fn", "sensibilidade"]); fp_w = lado(tfp, ["fp_n", "fp", "especificidade"])
fn_w.columns = [f"{m}_{str(L).replace('.', '')}" for m, L in fn_w.columns]
fp_w.columns = [f"{m}_{str(L).replace('.', '')}" for m, L in fp_w.columns]
comp = fn_w.reset_index().merge(fp_w.reset_index(), on="formato")
comp["d_fn"] = comp.fn_099 - comp.fn_095; comp["d_sens"] = comp.sensibilidade_099 - comp.sensibilidade_095
comp["d_fp"] = comp.fp_099 - comp.fp_095; comp["d_esp"] = comp.especificidade_099 - comp.especificidade_095
ordem = {t: i for i, t in enumerate((*TAXAS, "agregado"))}
comp = comp.sort_values(["formato", "taxa"], key=lambda s: s.map(ordem) if s.name == "taxa" else s,
                        ascending=[False, True]).reset_index(drop=True)
mc = tdet.pivot(index="taxa", columns="limiar", values=["so_lsb", "so_dct", "p", "p_bh", "mais_detectada"])
mc.columns = [f"{m}_{str(L).replace('.', '')}" for m, L in mc.columns]
mc = mc.reindex(TAXAS).reset_index()

# Conferência: com 0,95 a reanálise tem de reproduzir as tabelas originais da coleta
confere = {}
def igual(nome, novo, chaves, col_orig, col_novo):
    arq = fonte / nome
    if not arq.exists():
        confere[nome] = "ausente na fonte"; return
    o = pd.read_csv(arq).merge(novo, on=chaves, suffixes=("_orig", ""))
    confere[nome] = bool(len(o) == len(pd.read_csv(arq)) and np.allclose(o[col_orig], o[col_novo], rtol=0, atol=1e-12))
f95 = tfn[(tfn.limiar == 0.95) & (tfn.taxa != "agregado")]
igual("tabela_fn.csv", f95[["tecnica", "taxa", "fn", "fn_ic_inf", "fn_ic_sup"]].rename(columns={"fn": "fn_novo"}),
      ["tecnica", "taxa"], "fn", "fn_novo")
igual("tabela_fp.csv", tfp[tfp.limiar == 0.95][["formato", "fp"]].rename(columns={"fp": "fp_novo"}), ["formato"], "fp", "fp_novo")
igual("tabela_deteccao.csv", tdet[tdet.limiar == 0.95][["taxa", "p_bh"]].rename(columns={"p_bh": "p_bh_novo"}), ["taxa"], "p_bh", "p_bh_novo")
confere["limpas.csv: falso_positivo == p_max >= 0.95"] = bool((lim.falso_positivo == (lim.p_max >= 0.95)).all())

# Gravação
saida.mkdir(parents=True, exist_ok=True)
for nome, t in (("tabela_fp_lim099", tfp), ("tabela_fn_lim099", tfn), ("tabela_deteccao_lim099", tdet),
                ("comparativo_limiar_lim099", comp), ("comparativo_mcnemar_lim099", mc)):
    t.to_csv(saida / f"{nome}.csv", index=False, lineterminator="\n")

sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
git = lambda *a: subprocess.run(["git", *a], cwd=RAIZ, capture_output=True, text=True).stdout.strip()
prov = {"gerado_em": datetime.datetime.now(datetime.timezone.utc).isoformat(), "script": "scripts/reanalise_limiar.py",
        "commit_repositorio": git("rev-parse", "HEAD"), "arvore_suja_src_scripts": bool(git("status", "--porcelain", "src", "scripts")),
        "fonte": str(fonte), "commit_coleta": sorted(res.commit.unique().tolist()),
        "sha256_fonte": {n: sha(fonte / n) for n in ("resultados.csv", "limpas.csv")},
        "limiares": list(LIMIARES), "regra": "detectado/FP se p_max >= limiar (D-12)",
        "p_max_nan": {"resultados.csv": int(res.p_max.isna().sum()), "limpas.csv": int(lim.p_max.isna().sum())},
        "reproduz_coleta_com_0_95": confere,
        "versoes": {m.__name__: m.__version__ for m in (np, pd, __import__("scipy"), __import__("statsmodels"))}}
(saida / "proveniencia_lim099.json").write_text(json.dumps(prov, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


# Resumo legível (Markdown) com as mesmas contagens dos CSVs
pc = lambda x: f"{100 * x:.1f}%"
ic = lambda r, val, pre: f"{pc(r[val])} [{pc(r[pre + '_ic_inf'])}; {pc(r[pre + '_ic_sup'])}]"
md = ["# Detecção: limiar 0,95 (vigente) × 0,99 (calibração D-12)", "",
      f"Fonte: `{fonte}` (commit da coleta {', '.join(c[:7] for c in prov['commit_coleta'])}). "
      "Só reclassificação do p_max já gravado; nada foi re-medido.", "",
      "## Capas limpas — falso positivo e especificidade (IC 95% de Wilson)", "",
      "| Formato | Limiar | FP | Taxa de FP | Especificidade |", "|---|---|---|---|---|"]
for r in tfp.sort_values(["formato", "limiar"], ascending=[False, True]).to_dict("records"):
    md.append(f"| {r['formato'].upper()} | {r['limiar']:.2f} | {r['fp_n']}/{r['n']} | {ic(r, 'fp', 'fp')} | {ic(r, 'especificidade', 'esp')} |")
md += ["", "## Estego — falso negativo e sensibilidade (IC 95% de Wilson)", "",
       "| Formato (técnica) | Taxa | FN 0,95 | FN 0,99 | Sensib. 0,95 | Sensib. 0,99 | Δ sensib. |", "|---|---|---|---|---|---|---|"]
for (f, tc, tx), g in tfn.groupby(["formato", "tecnica", "taxa"], sort=False):
    a, b = g[g.limiar == 0.95].iloc[0], g[g.limiar == 0.99].iloc[0]
    md.append(f"| {f.upper()} ({tc.upper()}) | {tx} | {a.fn_n}/{a.n} | {b.fn_n}/{b.n} | {ic(a, 'sensibilidade', 'sens')} | {ic(b, 'sensibilidade', 'sens')} | "
              f"{100 * (b.sensibilidade - a.sensibilidade):+.1f} p.p. |")
md += ["", "No agregado, as 3 taxas usam as mesmas 90 imagens; o IC trata as 270 estego como independentes (aproximação).",
       "", "## Teste principal — McNemar exato LSB × DCT por taxa (BH na família de 3)", "",
       "| Limiar | Taxa | Só LSB | Só DCT | p | p (BH) | Mais detectada | Signif. (BH < 0,05) |", "|---|---|---|---|---|---|---|---|"]
for r in tdet.to_dict("records"):
    md.append(f"| {r['limiar']:.2f} | {r['taxa']} | {r['so_lsb']} | {r['so_dct']} | {r['p']:.4f} | {r['p_bh']:.4f} | "
              f"{r['mais_detectada'].upper()} | {'sim' if r['significativo_bh'] else 'não'} |")
md += ["", "## Conferência com a coleta (0,95)", ""] + [f"- {k}: {v}" for k, v in confere.items()]
(saida / "comparativo_limiar_lim099.md").write_text("\n".join(md) + "\n", encoding="utf-8")

with pd.option_context("display.width", 200, "display.max_columns", 30):
    print(tfp.round(4).to_string(), "\n"); print(tfn.round(4).to_string(), "\n"); print(tdet.round(4).to_string(), "\n")
print("Conferência 0,95:", confere)
