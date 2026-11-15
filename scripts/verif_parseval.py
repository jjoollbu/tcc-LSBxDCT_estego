"""Verificação da distorção da DCT pelo teorema de Parseval. Reanálise pós-feedback.

Análise posterior à coleta; não altera resultados.csv nem a métrica de qualidade (D-19).
A DCT 8×8 do JPEG é ortonormal, então a energia de um erro nos coeficientes é a mesma no domínio dos
pixels (antes do arredondamento para inteiros na decodificação). Trocar o LSB de um coeficiente
quantizado muda o coeficiente em Δ = ±1, ou seja, muda o valor desquantizado em Δ·q, em que q é o passo
de quantização daquela posição. Daí:
    energia prevista = Σ (Δ·q)²                 sobre os coeficientes alterados (capa × estego)
    MSE previsto     = energia / 262144         (512 × 512 pixels)
    MSE esperado     = 0,5 · Σ q² / 262144      sobre as n primeiras posições elegíveis (n = bits do payload),
                                                pois cada bit muda o coeficiente com probabilidade 1/2
No LSB cada bit muda o pixel em ±1 com probabilidade 1/2 (MSE esperado = 0,5 · n / 262144), então a razão
esperada MSE_DCT / MSE_LSB é E[q²] nas posições usadas.

Para cada capa JPEG lê a tabela de quantização do canal Y (jpeglib.read_dct(capa).qt[0], ordem natural;
a orientação é conferida por IDCT contra os pixels decodificados) e o q das 26 posições da banda. Para
cada estego DCT (regenerada em memória e conferida pelo SHA-256 de resultados.csv) calcula o MSE
previsto e o esperado e compara com o mse medido em resultados.csv (JPEG × JPEG decodificados, D-19).
Conferências do modelo: (a) a IDCT ortonormal em ponto flutuante da diferença dá exatamente a energia
prevista (Parseval numérico); (b) um decodificador de referência que arredonda os pixels para inteiros
e corta em 0–255 (IDCT ortonormal em float, não a IDCT inteira da libjpeg) mostra quanto do excesso do
mse medido sobre o previsto vem desse arredondamento.

Uso: python scripts/verif_parseval.py <pasta da coleta> [pasta de saída]
"""
import hashlib, tempfile, pathlib
import numpy as np, pandas as pd, jpeglib
from scipy import stats
from scipy.fft import idctn
import reanalise_comum as rc
from dct import BANDA, coeficientes_banda, posicoes_elegiveis

LIN = np.array([p[0] for p in BANDA]); COL = np.array([p[1] for p in BANDA])
fonte, saida = rc.argumentos()
res, lim = rc.ler_coleta(fonte)


def orientacao_ok(img_id):
    """IDCT ortonormal dos coeficientes desquantizados com qt[0] (e com a transposta) contra os pixels decodificados."""
    jp = rc.capa_jpeg(img_id); sp = jpeglib.read_spatial(str(rc.RAIZ / f"dataset/capas/jpeg/{img_id}.jpg")).spatial[..., 0]
    erro = {}
    for nome, q in (("qt", jp.qt[0]), ("qt_transposta", jp.qt[0].T)):
        rec = idctn(jp.Y * q, axes=(-2, -1), norm="ortho") + 128
        img = np.clip(np.round(rec.transpose(0, 2, 1, 3).reshape(sp.shape)), 0, 255)
        erro[nome] = float(np.abs(img - sp).mean())
    return erro


def decodificar(Y, q, arredondar):
    """Pixels a partir dos coeficientes quantizados: IDCT ortonormal 8×8 + 128; opcionalmente arredonda e corta."""
    x = idctn(Y.astype(float) * q, axes=(-2, -1), norm="ortho") + 128
    x = x.transpose(0, 2, 1, 3).reshape(512, 512)
    return np.clip(np.round(x), 0, 255) if arredondar else x


linhas, tabelas_q = [], {}
with tempfile.TemporaryDirectory() as tmp:
    for r in res[res.tecnica == "dct"].itertuples():
        jp = rc.capa_jpeg(r.id)
        assert len(jp.qt) >= 1 and jp.quant_tbl_no[0] == 0, "Y deve usar a tabela 0"
        qt = jp.qt[0].astype(np.int64); tabelas_q[r.id] = qt
        q_banda = qt[LIN, COL]                                       # q das 26 posições, ordem zigue-zague de BANDA
        Y0 = jp.Y; Y1 = rc.estego_dct(r.id, r.taxa, Y0)
        # confere a regeneração pelo SHA-256 da estego gravada na coleta
        jp.Y = Y1; jp.write_dct(f"{tmp}/e.jpg")
        assert hashlib.sha256(pathlib.Path(f"{tmp}/e.jpg").read_bytes()).hexdigest() == r.sha256_estego, r.id
        # mse medido recalculado (D-19: capa JPEG × estego JPEG decodificadas) para conferir a coluna mse
        a = jpeglib.read_spatial(str(rc.RAIZ / f"dataset/capas/jpeg/{r.id}.jpg")).spatial[..., 0].astype(float)
        b = jpeglib.read_spatial(f"{tmp}/e.jpg").spatial[..., 0].astype(float)
        mse_recalc = float(((a - b) ** 2).mean())

        v0, v1 = coeficientes_banda(Y0).astype(np.int64), coeficientes_banda(Y1).astype(np.int64)
        fora = np.ones((8, 8), bool); fora[LIN, COL] = False
        assert (Y0.reshape(-1, 8, 8)[:, fora] == Y1.reshape(-1, 8, 8)[:, fora]).all()
        d = v1 - v0; idx = np.arange(v0.size) % len(BANDA); q_todos = q_banda[idx]
        alt = d != 0
        energia = float(((d * q_todos) ** 2).sum())
        n_bits = 8 * len(rc.payload(r.taxa))
        usadas = posicoes_elegiveis(v0)[:n_bits]; qu = q_banda[usadas % len(BANDA)].astype(float)
        assert not alt[np.setdiff1d(np.arange(v0.size), usadas)].any()
        qf = qt.astype(float)
        mse_float = float(((decodificar(Y1, qf, False) - decodificar(Y0, qf, False)) ** 2).mean())
        mse_arred = float(((decodificar(Y1, qf, True) - decodificar(Y0, qf, True)) ** 2).mean())
        linhas.append({"id": r.id, "categoria": r.categoria, "taxa": r.taxa, "n_bits": n_bits,
                       "n_alterados": int(alt.sum()), "frac_alterados": alt.sum() / n_bits,
                       "energia_prevista": energia, "mse_previsto": energia / rc.N_PIXELS,
                       "mse_esperado": 0.5 * float((qu ** 2).sum()) / rc.N_PIXELS,
                       "mse_idct_float": mse_float, "mse_modelo_arredondado": mse_arred,
                       "E_q2": float((qu ** 2).mean()), "q_medio_rms": float(np.sqrt((qu ** 2).mean())),
                       "q_medio_aritmetico": float(qu.mean()), "frac_q1": float((qu == 1).mean()),
                       "mse_medido": r.mse, "mse_medido_recalc": mse_recalc, "psnr_medido": r.psnr})

df = pd.DataFrame(linhas)
assert np.allclose(df.mse_medido, df.mse_medido_recalc, rtol=1e-12, atol=0), "mse recalculado difere de resultados.csv"
parseval_num = float(np.max(np.abs(df.mse_idct_float - df.mse_previsto) / df.mse_previsto))
assert parseval_num < 1e-9, "IDCT em float não reproduz a energia prevista"
qs = np.stack(list(tabelas_q.values())); tabela_unica = bool((qs == qs[0]).all())
orient = orientacao_ok(df.id.iloc[0])
assert orient["qt"] < orient["qt_transposta"], "orientação de qt inesperada"

# LSB: alterações reais e razão observada por par
lsb = res[res.tecnica == "lsb"][["id", "taxa", "categoria", "mse", "psnr"]].rename(columns={"mse": "mse_lsb", "psnr": "psnr_lsb"})
df = df.merge(lsb, on=["id", "taxa", "categoria"])
df["mse_lsb_esperado"] = 0.5 * df.n_bits / rc.N_PIXELS
df["razao_medido_previsto"] = df.mse_medido / df.mse_previsto
df["erro_rel_previsto"] = (df.mse_medido - df.mse_previsto) / df.mse_previsto
df["razao_medido_esperado"] = df.mse_medido / df.mse_esperado
df["erro_rel_esperado"] = (df.mse_medido - df.mse_esperado) / df.mse_esperado
df["razao_dct_lsb_obs"] = df.mse_medido / df.mse_lsb
df["razao_dct_lsb_prev"] = df.mse_previsto / df.mse_lsb
df["razao_medido_arredondado"] = df.mse_medido / df.mse_modelo_arredondado
df["erro_rel_arredondado"] = (df.mse_medido - df.mse_modelo_arredondado) / df.mse_modelo_arredondado
df["psnr_previsto"] = 10 * np.log10(255 ** 2 / df.mse_previsto)
df["psnr_arredondado"] = 10 * np.log10(255 ** 2 / df.mse_modelo_arredondado)
df["psnr_esperado"] = 10 * np.log10(255 ** 2 / df.mse_esperado)


def q3(x):
    return float(np.median(x)), float(np.quantile(x, .25)), float(np.quantile(x, .75))


res_l = []
for tx, g in [*((t, df[df.taxa == t]) for t in rc.TAXAS), ("todas", df)]:
    row = {"taxa": tx, "n": len(g)}
    for alvo in ("previsto", "esperado", "arredondado"):
        col = "mse_modelo_arredondado" if alvo == "arredondado" else f"mse_{alvo}"
        row[f"pearson_{alvo}"] = float(stats.pearsonr(g.mse_medido, g[col])[0])
        row[f"spearman_{alvo}"] = float(stats.spearmanr(g.mse_medido, g[col])[0])
        row[f"erro_rel_mediano_{alvo}"], row[f"erro_rel_q1_{alvo}"], row[f"erro_rel_q3_{alvo}"] = q3(g[f"erro_rel_{alvo}"])
        row[f"erro_rel_abs_mediano_{alvo}"] = float(np.median(np.abs(g[f"erro_rel_{alvo}"])))
        row[f"razao_mediana_{alvo}"], row[f"razao_q1_{alvo}"], row[f"razao_q3_{alvo}"] = q3(g[f"razao_medido_{alvo}"])
    row["E_q2_mediana"], row["E_q2_q1"], row["E_q2_q3"] = q3(g.E_q2)
    row["q_rms_mediano"] = float(np.median(g.q_medio_rms)); row["frac_q1_mediana"] = float(np.median(g.frac_q1))
    row["razao_dct_lsb_obs_mediana"], row["razao_dct_lsb_obs_q1"], row["razao_dct_lsb_obs_q3"] = q3(g.razao_dct_lsb_obs)
    row["razao_dct_lsb_prev_mediana"] = float(np.median(g.razao_dct_lsb_prev))
    row["razao_dct_lsb_obs_media_geom"] = float(np.exp(np.log(g.razao_dct_lsb_obs).mean()))
    row["frac_alterados_mediana"] = float(np.median(g.frac_alterados))
    res_l.append(row)
resumo = pd.DataFrame(res_l)

# Textura: PSNR por categoria na DCT (observado × previsto × esperado) e E[q²]
tex = []
for (tx, c), g in df.groupby(["taxa", "categoria"]):
    tex.append({"taxa": tx, "categoria": c, "psnr_dct_obs": float(g.psnr_medido.median()),
                "psnr_dct_prev": float(g.psnr_previsto.median()), "psnr_dct_esp": float(g.psnr_esperado.median()),
                "psnr_dct_arred": float(g.psnr_arredondado.median()),
                "razao_medido_previsto_mediana": float(g.razao_medido_previsto.median()),
                "psnr_lsb_obs": float(g.psnr_lsb.median()), "E_q2_mediana": float(g.E_q2.median()),
                "frac_q1_mediana": float(g.frac_q1.median())})
tex = pd.DataFrame(tex)
dif = []
for tx in rc.TAXAS:
    t = tex[tex.taxa == tx].set_index("categoria")
    dif.append({"taxa": tx, **{f"delta_alta_baixa_{k}": float(t.loc["alta", k] - t.loc["baixa", k])
                               for k in ("psnr_dct_obs", "psnr_dct_prev", "psnr_dct_esp", "psnr_dct_arred", "psnr_lsb_obs")},
                "razao_E_q2_alta_baixa": float(t.loc["alta", "E_q2_mediana"] / t.loc["baixa", "E_q2_mediana"])})
dif = pd.DataFrame(dif)

df.to_csv(saida / "verif_parseval.csv", index=False, lineterminator="\n", float_format="%.17g")
resumo.to_csv(saida / "verif_parseval_resumo.csv", index=False, lineterminator="\n", float_format="%.17g")
tex.merge(dif, on="taxa").to_csv(saida / "verif_parseval_textura.csv", index=False, lineterminator="\n", float_format="%.17g")
q_banda0 = tabelas_q[df.id.iloc[0]][LIN, COL]

b = rc.br
R = resumo.set_index("taxa")
md = ["# Verificação da distorção da DCT pelo teorema de Parseval", "",
      f"Fonte: `{fonte}` (resultados.csv, commit da coleta a8ef486). Análise posterior à coleta; não altera as métricas.",
      f"Estego DCT regeneradas em memória: 270/270 com o mesmo SHA-256 de resultados.csv; o mse recalculado (JPEG × JPEG "
      "decodificados, D-19) coincide com a coluna mse.",
      f"Tabela de quantização do Y igual nas 90 capas: {'sim' if tabela_unica else 'não'}. Orientação de qt[0] conferida por "
      f"IDCT (erro médio {orient['qt']:.3f} contra {orient['qt_transposta']:.3f} com a transposta).", "",
      "q das 26 posições da banda (ordem zigue-zague): " + ", ".join(map(str, q_banda0)) + ".", "",
      "## MSE medido × modelos", "",
      "Previsto = Parseval com as alterações reais, Σ(Δ·q)²/262144. Esperado = 0,5·Σq²/262144 nas n primeiras posições "
      "elegíveis. Arredondado = decodificador de referência (IDCT em float) com pixels arredondados e cortados em 0–255.", "",
      "| Taxa | n | Pearson (prev.) | Medido/previsto mediana [Q1; Q3] | Erro rel. mediano (prev.) | Pearson (esp.) | "
      "Medido/esperado mediana [Q1; Q3] | Pearson (arred.) | Medido/arredondado mediana [Q1; Q3] |", "|---|---|---|---|---|---|---|---|---|"]
for tx, r in R.iterrows():
    md.append(f"| {tx} | {r.n:.0f} | {b(r.pearson_previsto, 4)} | {b(r.razao_mediana_previsto)} [{b(r.razao_q1_previsto)}; "
              f"{b(r.razao_q3_previsto)}] | {rc.pc(r.erro_rel_mediano_previsto)} | {b(r.pearson_esperado, 4)} | "
              f"{b(r.razao_mediana_esperado)} [{b(r.razao_q1_esperado)}; {b(r.razao_q3_esperado)}] | {b(r.pearson_arredondado, 6)} | "
              f"{b(r.razao_mediana_arredondado, 4)} [{b(r.razao_q1_arredondado, 4)}; {b(r.razao_q3_arredondado, 4)}] |")
md += ["", f"Parseval numérico: a IDCT ortonormal em float da diferença reproduz a energia prevista (erro relativo máximo "
       + f"{parseval_num:.1e}".replace(".", ",") + ").", "",
       "## Razão MSE_DCT / MSE_LSB × E[q²] nas posições usadas", "",
       "Razão observada por par (mesma imagem): média geométrica, como no artigo, e mediana [Q1; Q3]. Pelo modelo esperado, "
       "a razão seria E[q²].", "",
       "| Taxa | E[q²] mediana [Q1; Q3] | q médio (√E[q²]) | Razão observada: média geométrica | Razão observada: mediana [Q1; Q3] | Razão prevista (Parseval/LSB), mediana |",
       "|---|---|---|---|---|---|"]
for tx in rc.TAXAS:
    r = R.loc[tx]
    md.append(f"| {tx} | {b(r.E_q2_mediana, 2)} [{b(r.E_q2_q1, 2)}; {b(r.E_q2_q3, 2)}] | {b(r.q_rms_mediano, 2)} | "
              f"{b(r.razao_dct_lsb_obs_media_geom, 2)} | {b(r.razao_dct_lsb_obs_mediana, 2)} [{b(r.razao_dct_lsb_obs_q1, 2)}; "
              f"{b(r.razao_dct_lsb_obs_q3, 2)}] | {b(r.razao_dct_lsb_prev_mediana, 2)} |")
md += ["", "## Textura: PSNR da DCT por categoria (medianas, dB)", "",
       "| Taxa | Textura | PSNR DCT observado | Parseval (previsto) | Esperado (E[q²]) | Modelo arredondado | Medido/previsto | E[q²] | PSNR LSB observado |",
       "|---|---|---|---|---|---|---|---|---|"]
for r in tex.sort_values(["taxa", "categoria"], key=lambda s: s.map({t: i for i, t in enumerate(rc.TAXAS)})).itertuples():
    md.append(f"| {r.taxa} | {r.categoria} | {b(r.psnr_dct_obs, 2)} | {b(r.psnr_dct_prev, 2)} | {b(r.psnr_dct_esp, 2)} | "
              f"{b(r.psnr_dct_arred, 2)} | {b(r.razao_medido_previsto_mediana)} | {b(r.E_q2_mediana, 2)} | {b(r.psnr_lsb_obs, 2)} |")
md += ["", "| Taxa | Δ PSNR DCT alta − baixa: observado | Parseval | esperado | modelo arredondado | Δ PSNR LSB alta − baixa | E[q²] alta / baixa |",
       "|---|---|---|---|---|---|---|"]
for r in dif.itertuples():
    md.append(f"| {r.taxa} | {b(r.delta_alta_baixa_psnr_dct_obs, 2)} | {b(r.delta_alta_baixa_psnr_dct_prev, 2)} | "
              f"{b(r.delta_alta_baixa_psnr_dct_esp, 2)} | {b(r.delta_alta_baixa_psnr_dct_arred, 2)} | "
              f"{b(r.delta_alta_baixa_psnr_lsb_obs, 2)} | {b(r.razao_E_q2_alta_baixa, 3)} |")
T = R.loc["todas"]; da = dif.set_index("taxa").loc["alta"]; tb = tex.set_index(["taxa", "categoria"])
md += ["", "## Leitura", "",
       f"- Nas 270 estego DCT, o MSE medido acompanha o previsto por Parseval (Pearson {b(T.pearson_previsto, 4)}), mas fica "
       f"acima dele: razão medido/previsto com mediana {b(T.razao_mediana_previsto)} [Q1–Q3 {b(T.razao_q1_previsto)}–"
       f"{b(T.razao_q3_previsto)}]. Com o arredondamento dos pixels para inteiros e o corte em 0–255, o modelo passa a "
       f"reproduzir o medido (razão mediana {b(T.razao_mediana_arredondado, 4)}; Pearson {b(T.pearson_arredondado, 6)}). "
       "O excesso sobre Parseval vem, portanto, da decodificação para pixels inteiros.",
       f"- E[q²] nas posições usadas tem mediana {b(R.loc['baixa'].E_q2_mediana, 2)}, {b(R.loc['media'].E_q2_mediana, 2)} e "
       f"{b(R.loc['alta'].E_q2_mediana, 2)} (taxas baixa, média e alta; q médio de {b(R.loc['baixa'].q_rms_mediano, 2)} a "
       f"{b(R.loc['alta'].q_rms_mediano, 2)}). A razão MSE_DCT/MSE_LSB observada é {b(R.loc['baixa'].razao_dct_lsb_obs_media_geom, 1)}, "
       f"{b(R.loc['media'].razao_dct_lsb_obs_media_geom, 1)} e {b(R.loc['alta'].razao_dct_lsb_obs_media_geom, 1)} (média geométrica). "
       "E[q²] explica a maior parte dessa razão; o restante corresponde ao excesso do arredondamento.",
       f"- Na taxa alta, o PSNR da DCT em textura alta fica {b(-da.delta_alta_baixa_psnr_dct_obs, 2)} dB abaixo da textura baixa. "
       f"O E[q²] é maior na textura alta ({b(tb.loc[('alta', 'alta')].E_q2_mediana, 2)} contra {b(tb.loc[('alta', 'baixa')].E_q2_mediana, 2)}): "
       f"as posições elegíveis usadas caem mais nas frequências com passo q maior. Parseval sozinho prevê "
       f"{b(-da.delta_alta_baixa_psnr_dct_prev, 2)} dB; com o arredondamento, que pesa mais na textura baixa (medido/previsto "
       f"{b(tb.loc[('alta', 'baixa')].razao_medido_previsto_mediana, 2)} contra {b(tb.loc[('alta', 'alta')].razao_medido_previsto_mediana, 2)}), "
       f"o modelo prevê {b(-da.delta_alta_baixa_psnr_dct_arred, 2)} dB. No LSB a diferença é {b(abs(da.delta_alta_baixa_psnr_lsb_obs), 2)} dB.", ""]
rc.escrever(saida / "verif_parseval.md", "\n".join(md) + "\n")
rc.proveniencia(saida, "verif_parseval", fonte, {
    "tabela_q_unica_nas_90_capas": tabela_unica, "q_banda_zigue_zague": [int(x) for x in q_banda0],
    "orientacao_qt_idct_erro_medio": orient, "estego_sha256_confere": "270/270",
    "mse_recalculado_confere": True, "n_pixels": rc.N_PIXELS, "parseval_numerico_erro_rel_max": parseval_num,
    "modelo_arredondado": "IDCT ortonormal 8x8 em float (scipy.fft.idctn, norm='ortho') + 128, np.round e corte em 0-255; "
                          "não é a IDCT inteira da libjpeg"})
print("\n".join(md))
