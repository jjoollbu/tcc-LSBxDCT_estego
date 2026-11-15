"""Detecção com janelas acumuladas de tamanho absoluto (p_max_absoluto). Reanálise pós-feedback.

Análise de sensibilidade posterior à coleta; não altera resultados.csv, limpas.csv nem p_max (D-12).
Pergunta: a regra das janelas de 1%, 2%, ..., 100% (cuja 1ª janela tem 2.621 pixels no PNG e poucas
centenas de coeficientes no JPEG) influencia o FP e a comparação LSB × DCT? Para responder, troca as
janelas relativas por janelas de tamanho absoluto: passo, 2·passo, ... amostras até o total
(src/quiquadrado.p_max_absoluto), com passo = 128, 256 (principal) e 512.

1. Regenera as 540 estego em memória (inserção sequencial e determinística, payloads em
   dataset/payloads): LSB com esconder_lsb e amostra = estego.ravel(); DCT com esconder_dct sobre
   jpeglib.read_dct(capa).Y e amostra = v[posicoes_elegiveis(v)], v = coeficientes_banda(estego),
   igual ao executar.py (D-18).
2. Validação obrigatória: com a p_max original, as 540 estego e as 180 capas limpas regeneradas têm de
   reproduzir o p_max da coleta (igual ou até 1 ULP, com todas as decisões em 0,95 e 0,99 idênticas;
   reanalise_comum.conferir_p). Se não reproduzirem, o script para antes de usar a função nova.
3. Roda p_max_absoluto nas 540 estego e nas 180 capas limpas.
4. Com o limiar 0,95: sensibilidade por técnica × taxa e FP por formato (IC de Wilson), McNemar exato
   pareado LSB × DCT por taxa com BH na família de 3 e pares discordantes, no formato de
   tabela_deteccao.csv (taxa, metrica, p, p_bh, seguidas das contagens). A regra original (p_max de
   resultados.csv/limpas.csv) entra como referência.

Uso: python scripts/reanalise_janelas_absolutas.py <pasta da coleta> [pasta de saída]
     (saída padrão: resultados/reanalise_pos_feedback; recusa gravar em resultados/experimento)
"""
import os
from concurrent.futures import ProcessPoolExecutor
import numpy as np, pandas as pd
import reanalise_comum as rc
from quiquadrado import p_max, p_max_absoluto
from estatistica import comparar_deteccao, taxa_com_ic, corrigir_bh

PASSOS_ABS = (128, 256, 512)
PRINCIPAL = 256


def calcular(tarefa):
    """tarefa = (tipo, tecnica, taxa, id). Devolve p_max original e p_max_absoluto para cada passo."""
    tipo, tec, taxa, img_id = tarefa
    if tipo == "estego":
        a = rc.amostra_lsb(rc.estego_lsb(img_id, taxa)) if tec == "lsb" else rc.amostra_dct(rc.estego_dct(img_id, taxa))
    else:
        a = rc.amostra_lsb(rc.capa_png(img_id)) if tec == "lsb" else rc.amostra_dct(rc.capa_jpeg(img_id).Y)
    return {"n_amostra": len(a), "p_max_recalc": p_max(a), **{f"p_abs_{s}": p_max_absoluto(a, s) for s in PASSOS_ABS}}


def tabelas(df, col, regra):
    """Sensibilidade (estego), FP (limpas) e McNemar LSB × DCT por taxa, com a coluna de p-valor `col`."""
    est, lim = df[df.grupo == "estego"].copy(), df[df.grupo == "limpa"].copy()
    est["det"] = est[col] >= rc.LIMIAR; lim["pos"] = lim[col] >= rc.LIMIAR   # nan => não detectado
    sens, fp, det = [], [], []
    for (tc, f), g in est.groupby(["tecnica", "formato"]):
        for tx, h in [*((t, g[g.taxa == t]) for t in rc.TAXAS), ("agregado", g)]:
            n, k = len(h), int(h.det.sum()); s, si, ss = taxa_com_ic(k, n); fn, fi, fs = taxa_com_ic(n - k, n)
            sens.append({"regra": regra, "tecnica": tc, "formato": f, "taxa": tx, "n": n, "detectadas": k,
                         "sensibilidade": s, "sens_ic_inf": si, "sens_ic_sup": ss, "fn": fn, "fn_ic_inf": fi, "fn_ic_sup": fs})
    for f, g in lim.groupby("formato"):
        n, k = len(g), int(g.pos.sum()); p_, pi, ps = taxa_com_ic(k, n)
        fp.append({"regra": regra, "formato": f, "n": n, "fp_n": k, "fp": p_, "fp_ic_inf": pi, "fp_ic_sup": ps,
                   **{f"fp_{c}": int(g[g.categoria == c].pos.sum()) for c in rc.CATEGORIAS}})
    for tx in rc.TAXAS:
        w = est[est.taxa == tx].pivot_table(index="id", columns="tecnica", values="det", aggfunc="first").astype(bool)
        l, d = w["lsb"].to_numpy(), w["dct"].to_numpy()
        so_l, so_d = int((l & ~d).sum()), int((~l & d).sum())
        det.append({"taxa": tx, "metrica": "deteccao", **comparar_deteccao(l, d), "regra": regra, "n_pares": len(w),
                    "ambos": int((l & d).sum()), "so_lsb": so_l, "so_dct": so_d, "nenhum": int((~l & ~d).sum()),
                    "det_lsb": l.mean(), "det_dct": d.mean(),
                    "mais_detectada": "dct" if so_d > so_l else "lsb" if so_l > so_d else "empate"})
    det = pd.DataFrame(det); det.insert(3, "p_bh", corrigir_bh(det.p.tolist()))
    det["significativo_bh"] = det.p_bh < 0.05
    return pd.DataFrame(sens), pd.DataFrame(fp), det


def main():
    fonte, saida = rc.argumentos()
    res, lim = rc.ler_coleta(fonte)
    tarefas = ([("estego", r.tecnica, r.taxa, r.id) for r in res.itertuples()] +
               [("limpa", {"png": "lsb", "jpeg": "dct"}[r.formato], "limpa", r.id) for r in lim.itertuples()])
    with ProcessPoolExecutor(max(1, min(6, (os.cpu_count() or 2) - 1))) as ex:
        out = list(ex.map(calcular, tarefas, chunksize=4))
    df = pd.DataFrame([{"grupo": t[0], "tecnica": t[1], "formato": rc.FORMATO[t[1]], "taxa": t[2], "id": t[3], **o}
                       for t, o in zip(tarefas, out)])
    cat = lim.drop_duplicates("id").set_index("id").categoria
    df.insert(5, "categoria", df.id.map(cat))
    coleta = pd.concat([res.p_max, lim.p_max], ignore_index=True)
    df.insert(6, "p_max_coleta", coleta.to_numpy())

    # 2. Validação obrigatória antes de usar p_max_absoluto
    conf = {}
    for g, rot in (("estego", "p_max das 540 estego regeneradas × resultados.csv"),
                   ("limpa", "p_max das 180 capas limpas × limpas.csv")):
        h = df[df.grupo == g]
        c = rc.conferir_p(h.p_max_recalc, h.p_max_coleta, rot)
        c["casos_nao_identicos"] = [{**x, "tecnica": h.tecnica.iloc[x["indice"]], "taxa": h.taxa.iloc[x["indice"]],
                                     "id": h.id.iloc[x["indice"]]} for x in c["casos_nao_identicos"]]
        conf[g] = c

    # 3 e 4. Tabelas por regra
    regras = {"original_1pct": "p_max_coleta", **{f"absoluta_{s}": f"p_abs_{s}" for s in PASSOS_ABS}}
    S, F, D = [], [], []
    for regra, col in regras.items():
        s, f, d = tabelas(df, col, regra); S.append(s); F.append(f); D.append(d)
        if regra.startswith("absoluta"):
            d.to_csv(saida / f"tabela_deteccao_abs{regra.split('_')[1]}.csv", index=False, lineterminator="\n", float_format="%.17g")
    S, F, D = pd.concat(S), pd.concat(F), pd.concat(D)
    # a regra original tem de reproduzir a tabela_deteccao.csv da coleta
    orig = pd.read_csv(fonte / "tabela_deteccao.csv", **rc.CSV_FLOAT)
    j = D[D.regra == "original_1pct"].merge(orig, on=["taxa", "metrica"], suffixes=("", "_coleta"))
    confere_tab = bool(len(j) == 3 and np.allclose(j.p, j.p_coleta, rtol=0, atol=1e-12)
                       and np.allclose(j.p_bh, j.p_bh_coleta, rtol=0, atol=1e-12))
    assert confere_tab, "regra original não reproduz tabela_deteccao.csv"

    df.to_csv(saida / "p_max_absoluto.csv", index=False, lineterminator="\n", float_format="%.17g")
    S.to_csv(saida / "janelas_absolutas_sensibilidade.csv", index=False, lineterminator="\n", float_format="%.17g")
    F.to_csv(saida / "janelas_absolutas_fp.csv", index=False, lineterminator="\n", float_format="%.17g")
    D.to_csv(saida / "janelas_absolutas_mcnemar.csv", index=False, lineterminator="\n", float_format="%.17g")

    # Relatório
    rot = {"original_1pct": "Original (janelas de 1%)", **{f"absoluta_{s}": f"Absoluta, passo {s}" for s in PASSOS_ABS}}
    ic = lambda p, i, s: f"{rc.pc(p)} [{rc.pc(i)}; {rc.pc(s)}]"
    md = ["# Detecção com janelas acumuladas de tamanho absoluto (p_max_absoluto)", "",
          f"Fonte: `{fonte}` (commit da coleta a8ef486). Reanálise posterior à coleta; a regra pré-registrada (D-12, "
          "janelas de 1% a 100%) e seus resultados continuam sendo os principais.",
          "Janelas acumuladas de passo, 2·passo, ... amostras até o total (a amostra inteira entra como última janela). "
          "Detectado/FP se p ≥ 0,95. IC 95% de Wilson; McNemar exato pareado LSB × DCT com BH na família das 3 taxas.", "",
          "## Validação da regeneração", "",
          f"- Estego: {conf['estego']['n_identicos']}/540 p_max idênticos a resultados.csv e {conf['estego']['n_ate_1ulp']}/540 "
          f"até 1 ULP (diferença absoluta máxima {rc.sci(conf['estego']['diferenca_absoluta_maxima'])}); decisões em 0,95 e 0,99 idênticas.",
          f"- Capas limpas: {conf['limpa']['n_identicos']}/180 idênticos a limpas.csv e {conf['limpa']['n_ate_1ulp']}/180 até 1 ULP "
          f"(máx. {rc.sci(conf['limpa']['diferenca_absoluta_maxima'])}); decisões idênticas.",
          f"- A regra original reproduz tabela_deteccao.csv da coleta: {'sim' if confere_tab else 'NÃO'}.", "",
          "## Falsos positivos nas capas limpas", "",
          "| Regra | PNG: FP (IC 95%) | PNG por textura (baixa/media/alta) | JPEG: FP (IC 95%) |", "|---|---|---|---|"]
    for regra in regras:
        p_, j_ = (F[(F.regra == regra) & (F.formato == f)].iloc[0] for f in ("png", "jpeg"))
        md.append(f"| {rot[regra]} | {p_.fp_n}/90 — {ic(p_.fp, p_.fp_ic_inf, p_.fp_ic_sup)} | {p_.fp_baixa}/{p_.fp_media}/{p_.fp_alta} | "
                  f"{j_.fp_n}/90 — {ic(j_.fp, j_.fp_ic_inf, j_.fp_ic_sup)} |")
    md += ["", "## Sensibilidade (estego detectadas, IC 95%)", "",
           "| Regra | Técnica | baixa | media | alta | agregado |", "|---|---|---|---|---|---|"]
    for regra in regras:
        for tc in ("lsb", "dct"):
            g = S[(S.regra == regra) & (S.tecnica == tc)].set_index("taxa")
            md.append(f"| {rot[regra]} | {tc.upper()} | " + " | ".join(
                f"{g.loc[t].detectadas}/{g.loc[t].n} — {ic(g.loc[t].sensibilidade, g.loc[t].sens_ic_inf, g.loc[t].sens_ic_sup)}"
                for t in (*rc.TAXAS, "agregado")) + " |")
    md += ["", "## McNemar exato LSB × DCT por taxa (BH na família de 3)", "",
           "| Regra | Taxa | Só LSB | Só DCT | Ambas | Nenhuma | p | p ajustado (BH) | Mais detectada |",
           "|---|---|---|---|---|---|---|---|---|"]
    for r in D.itertuples():
        md.append(f"| {rot[r.regra]} | {r.taxa} | {r.so_lsb} | {r.so_dct} | {r.ambos} | {r.nenhum} | {rc.pval(r.p)} | "
                  f"{rc.pval(r.p_bh)} | {r.mais_detectada}{' (sig.)' if r.significativo_bh else ''} |")
    fpp = F[F.formato == "png"].set_index("regra"); fpj = F[F.formato == "jpeg"].set_index("regra")
    sig = D[D.significativo_bh]; sb = S.set_index(["regra", "tecnica", "taxa"])
    n_baixa = 8 * len(rc.payload("baixa")); jan1 = int(rc.N_PIXELS / 100)
    absol = [f"absoluta_{s}" for s in PASSOS_ABS]
    faixa = lambda tc, tx: (f"{rc.pc(min(sb.loc[(r, tc, tx)].sensibilidade for r in absol))} a "
                            f"{rc.pc(max(sb.loc[(r, tc, tx)].sensibilidade for r in absol))}")
    md += ["", "## Leitura", "",
           f"- FP: no PNG, {fpp.loc['original_1pct'].fp_n}/90 com a regra original e "
           + ", ".join(f"{fpp.loc[r].fp_n}/90" for r in absol) + f" com passo {', '.join(map(str, PASSOS_ABS))}; no JPEG, "
           f"{fpj.loc['original_1pct'].fp_n}/90 com a regra original e " + ", ".join(f"{fpj.loc[r].fp_n}/90" for r in absol)
           + ". Janelas absolutas pequenas não reduzem o FP; aumentam-no nos dois formatos.",
           f"- Sensibilidade na taxa baixa: LSB {rc.pc(sb.loc[('original_1pct', 'lsb', 'baixa')].sensibilidade)} com a regra "
           f"original e {faixa('lsb', 'baixa')} com janelas absolutas; DCT {rc.pc(sb.loc[('original_1pct', 'dct', 'baixa')].sensibilidade)} "
           f"e {faixa('dct', 'baixa')}. No LSB, o payload da taxa baixa ocupa {n_baixa} pixels, menos que a primeira janela "
           f"relativa ({jan1} pixels), de modo que a regra original nunca testa um trecho só com pixels alterados; as janelas "
           "absolutas de 128 a 512 testam. Parte desse ganho, porém, vem com mais FP.",
           "- Diferenças LSB × DCT significativas após BH: "
           + ("; ".join(f"{rot[r.regra]}, taxa {r.taxa} ({r.so_lsb} só LSB × {r.so_dct} só DCT; p_BH = {rc.sci(r.p_bh)})"
                        for r in sig.itertuples()) if len(sig) else "nenhuma, em nenhuma regra")
           + ". Com a regra original: " + (", ".join(sig[sig.regra == "original_1pct"].taxa) or "nenhuma")
           + ". Taxas sem diferença significativa em nenhuma regra: "
           + (", ".join(t for t in rc.TAXAS if t not in set(sig.taxa)) or "nenhuma") + ".", ""]
    rc.escrever(saida / "janelas_absolutas.md", "\n".join(md) + "\n")
    rc.proveniencia(saida, "reanalise_janelas_absolutas", fonte, {
        "validacao_p_max": conf, "regra_original_reproduz_tabela_deteccao": confere_tab,
        "passos": list(PASSOS_ABS), "passo_principal": PRINCIPAL, "limiar": rc.LIMIAR,
        "regra_janelas": "tamanhos passo, 2·passo, ...; se o total não for múltiplo, a amostra inteira entra como última janela",
        "regra_deteccao": "detectado/FP se p >= 0,95; nan => não detectado"})
    print("\n".join(md))


if __name__ == "__main__":
    main()
