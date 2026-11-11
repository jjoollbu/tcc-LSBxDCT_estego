"""O FP em PNG é estrutural ou de calibração? Distribuição do p_max nas capas limpas (D-12).

Só leitura. Lê o p_max contínuo que a coleta congelada gravou em limpas.csv e mostra, por formato:
(1) a distribuição do p_max por faixa (e por categoria de textura), (2) quantas capas limpas seguem
marcadas (FP) a cada limiar candidato, com IC 95% de Wilson, (3) o menor limiar < 1 que leva o FP a
≤ 5% sob três critérios, (4) o cruzamento FP × textura e (5) o custo em detecção: quanto das estego
(resultados.csv) continua detectado em cada limiar candidato e nos limiares mínimos do item 3. Não
roda o detector, não abre imagens e não toca em custo computacional nem em qualidade. O commit da
coleta vem de resultados.csv (limpas.csv não tem essa coluna). Com 0,95 e 0,99 a sensibilidade é
conferida com tabela_fn_lim099.csv (de reanalise_limiar.py), quando esse arquivo existe na saída.

Regra de decisão: FP se p_max >= limiar (D-12), a mesma de analisar_limpas.py e reanalise_limiar.py.
"1,0 estrito" = p_max >= 1,0, ou seja, só uma capa com p_max exatamente igual a 1 seria marcada.

Uso: python scripts/fp_estrutural.py <pasta da coleta> [pasta de saída]
     (saída padrão: resultados/experimento_lim099; recusa gravar em resultados/experimento)
"""
import sys, json, hashlib, pathlib, subprocess, datetime, platform
import numpy as np, pandas as pd
RAIZ = pathlib.Path(__file__).parents[1]; sys.path.insert(0, str(RAIZ / "src"))
from estatistica import taxa_com_ic

FORMATO = {"lsb": "png", "dct": "jpeg"}       # LSB em PNG, DCT/Jsteg em JPEG QF95
FORMATOS = tuple(FORMATO.values())
CATEGORIAS = ("baixa", "media", "alta")
LIMIARES = (0.95, 0.99, 0.999, 0.9999, 1.0)   # candidatos; 1.0 = "estrito" (só p_max == 1 marca)
ACEITAVEL = 0.05
TOPO = 0.99999                                # faixa do topo, tratada como "p_max = 1,000"
FAIXAS = (("<0,95", -np.inf, 0.95), ("[0,95; 0,99)", 0.95, 0.99), ("[0,99; 0,999)", 0.99, 0.999),
          ("[0,999; 0,99999)", 0.999, TOPO), ("≈1,000 (≥0,99999)", TOPO, np.inf))
CRITERIOS = {"ponto": "taxa de FP ≤ 5%", "ic_inf": "limite inferior do IC ≤ 5% (não é maior que 5%)",
             "ic_sup": "limite superior do IC ≤ 5% (comprovadamente ≤ 5%)"}
fl = lambda L: "1,0 (estrito)" if L == 1.0 else f"{L:g}".replace(".", ",")   # rótulo de limiar

fonte = pathlib.Path(sys.argv[1]).resolve()
saida = pathlib.Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else RAIZ / "resultados" / "experimento_lim099"
if saida == fonte or saida == (RAIZ / "resultados" / "experimento").resolve():
    sys.exit(f"Recusado: {saida} é a pasta da coleta congelada. Grave em outra pasta.")

lim = pd.read_csv(fonte / "limpas.csv", dtype={"id": str})
assert {"id", "categoria", "formato", "p_max", "falso_positivo"} <= set(lim.columns), "colunas inesperadas em limpas.csv"
assert set(lim.formato) == set(FORMATOS) and set(lim.categoria) == set(CATEGORIAS), "valores inesperados em limpas.csv"
assert not lim.duplicated(["formato", "id"]).any(), "capas repetidas em limpas.csv"
assert (lim.groupby("formato").size() == 90).all(), "esperadas 90 capas por formato"
assert not lim.p_max.isna().any(), "p_max nan em limpas.csv"
assert (lim.falso_positivo == (lim.p_max >= 0.95)).all(), "falso_positivo não bate com p_max >= 0,95"
res = pd.read_csv(fonte / "resultados.csv", dtype={"id": str})
assert set(res.tecnica) == set(FORMATO) and set(res.taxa) == set(CATEGORIAS), "resultados.csv inesperado"
assert not res.duplicated(["tecnica", "taxa", "id"]).any(), "combinações repetidas em resultados.csv"
res["formato"] = res.tecnica.map(FORMATO)
TAXAS = CATEGORIAS                                # taxas de inserção baixa/media/alta (mesmos rótulos)


def wilson(k, n):
    t, i, s = taxa_com_ic(int(k), int(n))
    return {"n": int(n), "contagem": int(k), "proporcao": t, "ic_inf": i, "ic_sup": s}


def aceita(w):
    return {f"aceitavel_{c}": bool(w[{"ponto": "proporcao"}.get(c, c)] <= ACEITAVEL) for c in CRITERIOS}


linhas, minimos = [], {}
for f in FORMATOS:
    g = lim[lim.formato == f]; p = g.p_max.to_numpy(); n = len(g)
    linhas.append({"formato": f, "quadro": "resumo", "item": "p_max_maximo", "valor": float(p.max()), "n": n})
    linhas.append({"formato": f, "quadro": "resumo", "item": "p_max_igual_1", "valor": int((p == 1.0).sum()), "n": n})

    # 1. Distribuição por faixa (todas as capas e por categoria)
    for nome, a, b in FAIXAS:
        dentro = (g.p_max >= a) & (g.p_max < b)
        linhas.append({"formato": f, "quadro": "faixa", "item": nome, "categoria": "todas", **wilson(dentro.sum(), n),
                       "valor": float(g.p_max[dentro].max()) if dentro.any() else np.nan})
        for c in CATEGORIAS:
            h = g.categoria == c
            linhas.append({"formato": f, "quadro": "faixa", "item": nome, "categoria": c, **wilson((dentro & h).sum(), h.sum())})

    # 2 e 4. FP sobreviventes a cada limiar candidato, no total e por textura
    for L in LIMIARES:
        w = wilson((p >= L).sum(), n)
        linhas.append({"formato": f, "quadro": "limiar", "limiar": L, "categoria": "todas", **w, **aceita(w)})
        for c in CATEGORIAS:
            h = g[g.categoria == c]
            linhas.append({"formato": f, "quadro": "textura", "limiar": L, "categoria": c,
                           **wilson((h.p_max >= L).sum(), len(h))})

    # 3. Menor limiar < 1 que atende cada critério. Com p ordenado decrescente (p_(1) ≥ p_(2) ≥ ...),
    # marcar no máximo k capas exige L > p_(k+1); o menor L é então qualquer valor acima de p_(k+1),
    # e L = p_(k) já marca exatamente k (sem empates). k = maior nº de FP que atende o critério.
    desc = np.sort(p)[::-1]
    for c in CRITERIOS:
        k = max(j for j in range(n + 1) if aceita(wilson(j, n))[f"aceitavel_{c}"])
        acima_de = float(desc[k]) if k < n else -np.inf          # p_(k+1): L tem de ser > este valor
        if acima_de < 0.95:                                       # já resolvido no limiar vigente ou abaixo
            m = {"k_max": k, "limiar_maior_que": acima_de, "existe_abaixo_de_1": True,
                 "obs": "atendido com L ≤ 0,95"}
        else:
            m = {"k_max": k, "limiar_maior_que": acima_de, "existe_abaixo_de_1": bool(acima_de < 1.0),
                 "um_menos_L": 1.0 - acima_de,
                 "obs": f"qualquer L em ({acima_de!r}; {float(desc[k - 1])!r}]" if k > 0
                        else f"qualquer L em ({acima_de!r}; 1.0]"}
        m["capas_inremoviveis_p_max_1"] = int((p == 1.0).sum())
        minimos[(f, c)] = m
        linhas.append({"formato": f, "quadro": "limiar_minimo", "item": c, "valor": acima_de, "n": n,
                       "contagem": k, "existe_abaixo_de_1": m["existe_abaixo_de_1"], "obs": m["obs"]})

# 5. Custo em detecção. O limiar da D-12 é um só para os dois formatos, então os dois são avaliados
# nos mesmos L: os candidatos e os limiares mínimos do PNG (item 3), cada um no menor valor concreto
# que atende o critério: L = p_(k) (marca exatamente k capas limpas) ou, para k = 0, o primeiro
# float acima do p_max máximo. p_max nan nas estego => não detectado, como na coleta.
desc_png = np.sort(lim[lim.formato == "png"].p_max.to_numpy())[::-1]
CUSTO = [(fl(L), L) for L in LIMIARES]
for c in CRITERIOS:
    k = minimos[("png", c)]["k_max"]
    if desc_png[k] >= 0.95:                     # só faz sentido se o critério exige subir acima de 0,95
        L = float(desc_png[k - 1]) if k > 0 else float(np.nextafter(desc_png[0], np.inf))
        CUSTO.append((f"mínimo PNG ({c})", L))
CUSTO.sort(key=lambda x: x[1])
for f in FORMATOS:
    pl = lim[lim.formato == f].p_max
    for rot, L in CUSTO:
        linhas.append({"formato": f, "quadro": "custo", "item": rot, "limiar": L, "taxa": "limpas (FP)",
                       **wilson((pl >= L).sum(), len(pl))})
        g = res[res.formato == f]
        for tx, h in [*((t, g[g.taxa == t]) for t in TAXAS), ("agregado", g)]:
            linhas.append({"formato": f, "quadro": "custo", "item": rot, "limiar": L, "taxa": tx,
                           **wilson((h.p_max >= L).sum(), len(h))})

tab = pd.DataFrame(linhas)

# Conferência: com 0,95 e 0,99 a sensibilidade tem de bater com a de reanalise_limiar.py
confere = {}
arq_fn = saida / "tabela_fn_lim099.csv"
if arq_fn.exists():
    o = pd.read_csv(arq_fn)
    c_ = tab[(tab.quadro == "custo") & tab.limiar.isin([0.95, 0.99]) & (tab.taxa != "limpas (FP)")]
    j = c_.merge(o, on=["formato", "limiar", "taxa"])
    confere["sensibilidade 0,95/0,99 == tabela_fn_lim099.csv"] = bool(
        len(j) == len(c_) == 16 and np.allclose(j.proporcao, j.sensibilidade, rtol=0, atol=1e-12))
else:
    confere["tabela_fn_lim099.csv"] = "ausente na saída"

cols = ["formato", "quadro", "item", "limiar", "categoria", "taxa", "n", "contagem", "proporcao", "ic_inf", "ic_sup",
        *(f"aceitavel_{c}" for c in CRITERIOS), "valor", "existe_abaixo_de_1", "obs"]
tab = tab.reindex(columns=cols).astype({"n": "Int64", "contagem": "Int64"})

# Gravação (arquivos novos; não toca nas saídas de reanalise_limiar.py)
saida.mkdir(parents=True, exist_ok=True)
tab.to_csv(saida / "fp_estrutural.csv", index=False, lineterminator="\n", float_format="%.17g")

sha = lambda q: hashlib.sha256(q.read_bytes()).hexdigest()
git = lambda *a: subprocess.run(["git", *a], cwd=RAIZ, capture_output=True, text=True).stdout.strip()
commit = (sorted(lim.commit.unique().tolist()) if "commit" in lim.columns else
          sorted(pd.read_csv(fonte / "resultados.csv", usecols=["commit"]).commit.unique().tolist())
          if (fonte / "resultados.csv").exists() else None)
prov = {"gerado_em": datetime.datetime.now(datetime.timezone.utc).isoformat(), "script": "scripts/fp_estrutural.py",
        "commit_repositorio": git("rev-parse", "HEAD"), "arvore_suja_src_scripts": bool(git("status", "--porcelain", "src", "scripts")),
        "fonte": str(fonte), "sha256_limpas.csv": sha(fonte / "limpas.csv"),
        "commit_coleta": commit, "commit_coleta_origem": "limpas.csv" if "commit" in lim.columns else "resultados.csv (coluna commit)",
        "sha256_resultados.csv": sha(fonte / "resultados.csv") if (fonte / "resultados.csv").exists() else None,
        "regra": "FP se p_max >= limiar (D-12); '1,0 estrito' = p_max >= 1,0",
        "limiares_candidatos": list(LIMIARES), "nivel_aceitavel": ACEITAVEL, "criterios_aceitavel": CRITERIOS,
        "faixas": [[nm, a, b] for nm, a, b in FAIXAS], "faixa_topo": f"p_max >= {TOPO} tratado como 1,000",
        "ic": "Wilson 95% (taxa_com_ic, src/estatistica.py)",
        "n_capas": lim.groupby("formato").size().to_dict(),
        "n_estego": res.groupby("formato").size().to_dict(), "p_max_nan_estego": int(res.p_max.isna().sum()),
        "limiares_custo": [[rot, L] for rot, L in CUSTO],
        "regra_limiar_minimo_concreto": "L = p_(k) (k-ésimo maior p_max PNG limpo) ou, para k = 0, nextafter(max, +inf)",
        "regra_deteccao": "detectado se p_max >= L; nan => não detectado",
        "ic_agregado": "agregado = 270 estego (3 taxas × 90 imagens) tratadas como independentes (aproximação)",
        "confere_reanalise_limiar": confere,
        "python": platform.python_version(), "sistema": platform.platform(),
        "versoes": {m.__name__: m.__version__ for m in (np, pd, __import__("scipy"), __import__("statsmodels"))}}
(saida / "proveniencia_fp_estrutural.json").write_text(json.dumps(prov, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

# Relatório legível
pc = lambda x: f"{100 * x:.1f}%".replace(".", ",")
ic = lambda r: f"{pc(r.proporcao)} [{pc(r.ic_inf)}; {pc(r.ic_sup)}]"
num = lambda x, d=8: f"{x:.{d}f}".replace(".", ",")
sel = lambda f, q: tab[(tab.formato == f) & (tab.quadro == q)]
sim = lambda b: "sim" if b else "não"

md = ["# FP em capas limpas: estrutural ou de calibração?", "",
      f"Fonte: `{fonte}` · limpas.csv SHA-256 `{prov['sha256_limpas.csv'][:16]}…` · commit da coleta "
      f"{', '.join(c[:7] for c in commit or [])}. Só leitura do p_max já gravado em limpas.csv (capas sem payload) "
      "e resultados.csv (estego, só no item 5); nada foi re-medido.",
      "Regra: FP se p_max ≥ L (D-12). IC 95% de Wilson. Aceitável = FP ≤ 5%, avaliado pela estimativa pontual "
      "e pelos dois limites do IC.", "", "## Resumo", "", "RESUMO_AQUI", ""]
for f in FORMATOS:
    F = f.upper(); g = lim[lim.formato == f]
    md += [f"## {F}", "", f"p_max máximo observado: {num(g.p_max.max(), 10)} · capas com p_max exatamente 1,0: "
           f"{int((g.p_max == 1.0).sum())} de {len(g)}", "",
           f"### {F} — 1. Distribuição do p_max por faixa", "",
           "| Faixa | Capas | % (IC 95%) | baixa | media | alta |", "|---|---|---|---|---|---|"]
    fx = sel(f, "faixa")
    for nome, *_ in FAIXAS:
        t = fx[(fx["item"] == nome) & (fx.categoria == "todas")].iloc[0]
        por = [int(fx[(fx["item"] == nome) & (fx.categoria == c)].contagem.iloc[0]) for c in CATEGORIAS]
        md.append(f"| {nome} | {t.contagem}/{t.n} | {ic(t)} | " + " | ".join(map(str, por)) + " |")
    md += ["", f"### {F} — 2. FP sobreviventes a cada limiar candidato", "",
           "| Limiar L | Marcadas (p_max ≥ L) | Taxa de FP (IC 95%) | ≤5% (ponto) | ≤5% (IC inf) | ≤5% (IC sup) |",
           "|---|---|---|---|---|---|"]
    for r in sel(f, "limiar").itertuples():
        md.append(f"| {fl(r.limiar)} | {r.contagem}/{r.n} | {ic(r)} | {sim(r.aceitavel_ponto)} | "
                  f"{sim(r.aceitavel_ic_inf)} | {sim(r.aceitavel_ic_sup)} |")
    md += ["", f"### {F} — 3. Menor limiar < 1 que leva o FP a ≤ 5%", "",
           "| Critério | Máx. de FP admitido (de 90) | Limiar necessário | 1 − L | Existe L < 1? |", "|---|---|---|---|---|"]
    for c, desc_c in CRITERIOS.items():
        m = minimos[(f, c)]
        lim_txt = "≤ 0,95 (já atendido)" if m["obs"].startswith("atendido") else f"L > {num(m['limiar_maior_que'], 10)}"
        um = f"{m['um_menos_L']:.1e}".replace(".", ",") if "um_menos_L" in m else "—"
        md.append(f"| {desc_c} | {m['k_max']} | {lim_txt} | {um} | {sim(m['existe_abaixo_de_1'])} |")
    md += ["", f"Capas com p_max = 1,0 exato, que nenhum limiar < 1 removeria: {minimos[(f, 'ponto')]['capas_inremoviveis_p_max_1']}.",
           "", f"### {F} — 4. FP × categoria de textura", "",
           "| Limiar L | baixa (de 30) | media (de 30) | alta (de 30) |", "|---|---|---|---|"]
    tx = sel(f, "textura")
    for L in LIMIARES:
        md.append(f"| {fl(L)} | " + " | ".join(
            (lambda r: f"{r.contagem} — {ic(r)}")(tx[(tx.limiar == L) & (tx.categoria == c)].iloc[0]) for c in CATEGORIAS) + " |")
    tc = {v: k for k, v in FORMATO.items()}[f].upper()
    md += ["", f"### {F} — 5. Custo em detecção (estego {tc}, resultados.csv)", "",
           "Mesmos limiares nos dois formatos (a D-12 usa um limiar só). \"mínimo PNG\" = menor limiar concreto que "
           "atende o critério do item 3 no PNG.", "",
           f"| Limiar L | Valor | FP {F} (limpas) | Sensibilidade agregada (IC 95%) | baixa | media | alta |",
           "|---|---|---|---|---|---|---|"]
    cu = sel(f, "custo")
    for rot, L in CUSTO:
        r = {t: cu[(cu["item"] == rot) & (cu.taxa == t)].iloc[0] for t in ("limpas (FP)", "agregado", *TAXAS)}
        val = repr(L).replace(".", ",") if rot.startswith("mínimo") else num(L, 10)   # mínimos: precisão total
        md.append(f"| {rot} | {val} | {r['limpas (FP)'].contagem}/{r['limpas (FP)'].n} ({pc(r['limpas (FP)'].proporcao)}) | "
                  f"{r['agregado'].contagem}/{r['agregado'].n} — {ic(r['agregado'])} | "
                  + " | ".join(pc(r[t].proporcao) for t in TAXAS) + " |")
    md.append("")
md += ["## Conferência", "", "No agregado as 3 taxas usam as mesmas 90 imagens; o IC trata as 270 estego como "
       "independentes (aproximação, como em reanalise_limiar.py).", ""] + [f"- {k}: {v}" for k, v in confere.items()] + [""]

# Resumo com os números calculados acima
png, lp = lim[lim.formato == "png"], sel("png", "limiar")
fp95 = png[png.p_max >= 0.95]
conc = {nome: int(((fp95.p_max >= a) & (fp95.p_max < b)).sum()) for nome, a, b in FAIXAS[1:]}
m_p, m_s = minimos[("png", "ponto")], minimos[("png", "ic_sup")]
tx95 = fp95.categoria.value_counts().reindex(CATEGORIAS, fill_value=0)
fp_jpeg = int(sel("jpeg", "limiar").contagem.max())
n1 = m_p["capas_inremoviveis_p_max_1"]; e = lambda x: f"{x:.1e}".replace(".", ",")
ok = [fl(r.limiar) for r in lp.itertuples() if r.aceitavel_ponto]
cu_all = tab[tab.quadro == "custo"]
sv = lambda f, rot, t: cu_all[(cu_all.formato == f) & (cu_all["item"] == rot) & (cu_all.taxa == t)].proporcao.iloc[0]
queda = 100 * (sv("png", "0,95", "agregado") - sv("png", "mínimo PNG (ponto)", "agregado"))
s = lambda f, rot, t: pc(cu_all[(cu_all.formato == f) & (cu_all["item"] == rot) & (cu_all.taxa == t)].proporcao.iloc[0])
resumo = [
    f"- **Onde o FP se concentra (PNG):** das {len(fp95)} capas limpas marcadas com 0,95, "
    f"{conc['[0,999; 0,99999)'] + conc['≈1,000 (≥0,99999)']} têm p_max ≥ 0,999 e {conc['≈1,000 (≥0,99999)']} estão "
    f"em ≥ 0,99999; o máximo é {num(png.p_max.max(), 10)}. Capas com p_max exatamente 1,0: {n1}.",
    f"- **Menor limiar < 1 que resolve (PNG):** pela estimativa pontual, L > {num(m_p['limiar_maior_que'], 10)} "
    f"(1 − L ≈ {e(m_p['um_menos_L'])}, até {m_p['k_max']} FP); para o limite superior do IC ficar ≤ 5% "
    f"(0 FP), L > {num(m_s['limiar_maior_que'], 10)} (1 − L ≈ {e(m_s['um_menos_L'])}). Entre os candidatos, atingem ≤ 5% "
    f"(ponto): {', '.join(ok) or 'nenhum'} ({lp[lp.limiar == 0.9999].contagem.iloc[0]}/90 ainda marcadas com 0,9999). "
    + ("Existe L < 1 em sentido estrito, mas só colado em 1 e ajustado ao máximo desta amostra; "
       if m_s["existe_abaixo_de_1"] else "Nenhum L < 1 zera o FP; ")
    + f"capas com p_max = 1,0 exato que nenhum L < 1 remove: {n1}.",
    f"- **Textura (PNG, 0,95):** baixa {tx95['baixa']}, media {tx95['media']}, alta {tx95['alta']} de 30 cada.",
    f"- **Custo em detecção:** " + "; ".join(
        f"{rot} — FP PNG {s('png', rot, 'limpas (FP)')}, sensibilidade LSB {s('png', rot, 'agregado')} e DCT {s('jpeg', rot, 'agregado')}"
        for rot in ("0,95", *(r for r, _ in CUSTO if r.startswith("mínimo")))) + ". "
    + (f"Para levar o FP do PNG a ≤ 5% (ponto), a sensibilidade agregada do LSB cai {queda:.1f} p.p. em relação a 0,95: "
       "as caudas de p_max de limpas e estego se sobrepõem perto de 1."
       if queda >= 10 else f"Para levar o FP do PNG a ≤ 5% (ponto), a sensibilidade agregada do LSB cai só {queda:.1f} p.p.").replace(".", ",", 1),
    f"- **JPEG (contraste):** {fp_jpeg} FP em todos os limiares; p_max máximo {num(lim[lim.formato == 'jpeg'].p_max.max(), 6)}.",
]
i = md.index("RESUMO_AQUI"); md[i:i + 1] = resumo
(saida / "fp_estrutural.md").write_text("\n".join(md) + "\n", encoding="utf-8")
print(f"Gravado em {saida}: fp_estrutural.csv, fp_estrutural.md, proveniencia_fp_estrutural.json")
