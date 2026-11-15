"""Funções comuns das reanálises pós-feedback (nov/2026). Não é executado sozinho.

Análises de sensibilidade feitas depois da coleta congelada (commit a8ef486). Nada aqui altera
resultados.csv, limpas.csv ou src/quiquadrado.p_max; os resultados pré-registrados continuam os principais.

- argumentos(): lê <pasta da coleta> [pasta de saída] e recusa gravar na pasta da coleta.
- ler_coleta(): resultados.csv e limpas.csv lidos com round-trip de float (p_max exato).
- capa_png / capa_jpeg / estego_lsb / estego_dct: regeneram capas e estego em memória. A inserção é
  sequencial e determinística (payloads em dataset/payloads), igual ao executar.py.
- amostra_lsb / amostra_dct: mesma ordem de leitura do detector (D-18).
- conferir_p(): compara p-valores recalculados com os da coleta. Aceita igualdade exata ou diferença de
  até 1 ULP (decisão do autor em 15/11/2026: a coleta rodou em Linux/WSL2 e esta reanálise em Windows,
  e chi2.sf difere no último bit em poucos casos), desde que TODAS as decisões em 0,95 e 0,99 sejam
  idênticas. Qualquer outra diferença interrompe o script.
- ambientes(): ambiente da coleta (lido de "Ambiente do Experimento.txt") e desta reanálise, para a
  proveniência.
"""
import sys, json, hashlib, pathlib, subprocess, datetime, platform
import numpy as np, pandas as pd, jpeglib
from PIL import Image

RAIZ = pathlib.Path(__file__).parents[1]
if str(RAIZ / "src") not in sys.path:
    sys.path.insert(0, str(RAIZ / "src"))
from lsb import esconder_lsb
from dct import esconder_dct, coeficientes_banda, posicoes_elegiveis

TAXAS = ("baixa", "media", "alta")
CATEGORIAS = ("baixa", "media", "alta")
FORMATO = {"lsb": "png", "dct": "jpeg"}
LIMIAR, LIMIAR_CALIBRACAO = 0.95, 0.99           # D-12 (vigente) e calibração pré-registrada
N_PIXELS = 512 * 512
SAIDA_PADRAO = RAIZ / "resultados" / "reanalise_pos_feedback"


def argumentos():
    if len(sys.argv) < 2:
        sys.exit("Uso: python scripts/<script>.py <pasta da coleta> [pasta de saída]")
    fonte = pathlib.Path(sys.argv[1]).resolve()
    saida = pathlib.Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else SAIDA_PADRAO
    if saida == fonte or saida == (RAIZ / "resultados" / "experimento").resolve():
        sys.exit(f"Recusado: {saida} é a pasta da coleta congelada. Grave em outra pasta.")
    saida.mkdir(parents=True, exist_ok=True)
    return fonte, saida


def ler_coleta(fonte):
    res = pd.read_csv(fonte / "resultados.csv", dtype={"id": str}, float_precision="round_trip")
    lim = pd.read_csv(fonte / "limpas.csv", dtype={"id": str}, float_precision="round_trip")
    assert len(res) == 540 and not res.duplicated(["tecnica", "taxa", "id"]).any(), "resultados.csv inesperado"
    assert len(lim) == 180 and not lim.duplicated(["formato", "id"]).any(), "limpas.csv inesperado"
    cat = lim.drop_duplicates("id").set_index("id").categoria
    res["categoria"] = res.id.map(cat); res["formato"] = res.tecnica.map(FORMATO)
    assert not res.categoria.isna().any()
    return res, lim


def payload(taxa):
    return (RAIZ / f"dataset/payloads/payload_{taxa}.bin").read_bytes()


def capa_png(img_id):
    return np.array(Image.open(RAIZ / f"dataset/capas/png/{img_id}.png"))


def capa_jpeg(img_id):
    """Objeto jpeglib (coeficientes quantizados em .Y, tabelas em .qt)."""
    return jpeglib.read_dct(str(RAIZ / f"dataset/capas/jpeg/{img_id}.jpg"))


def estego_lsb(img_id, taxa):
    return esconder_lsb(capa_png(img_id), payload(taxa))


def estego_dct(img_id, taxa, Y=None):
    return esconder_dct(capa_jpeg(img_id).Y if Y is None else Y, payload(taxa))


def amostra_lsb(img):
    return img.ravel()


def amostra_dct(Y):
    v = coeficientes_banda(Y)
    return v[posicoes_elegiveis(v)]


def conferir_p(recalc, coleta, rotulo):
    """Igual ou até 1 ULP, com decisões idênticas em 0,95 e 0,99. Devolve o resumo para a proveniência."""
    a, b = np.asarray(recalc, float), np.asarray(coleta, float)
    assert a.shape == b.shape
    nan_ok = np.isnan(a) == np.isnan(b)
    a0, b0 = np.nan_to_num(a, nan=0.0), np.nan_to_num(b, nan=0.0)
    dif = np.abs(a0 - b0)
    ulp = np.spacing(np.maximum(np.abs(a0), np.abs(b0)))
    exato = (a0 == b0) & nan_ok
    ate_1ulp = (dif <= ulp) & nan_ok
    decisoes = {f"{L}": bool(((a >= L) == (b >= L)).all()) for L in (LIMIAR, LIMIAR_CALIBRACAO)}
    r = {"rotulo": rotulo, "n": int(a.size), "n_identicos": int(exato.sum()), "n_ate_1ulp": int(ate_1ulp.sum()),
         "diferenca_absoluta_maxima": float(dif.max()) if a.size else 0.0,
         "diferenca_relativa_maxima": float((dif / np.where(b0 == 0, 1, np.abs(b0))).max()) if a.size else 0.0,
         "decisoes_identicas": decisoes,
         "casos_nao_identicos": [{"indice": int(i), "recalculado": repr(float(a[i])), "coleta": repr(float(b[i]))}
                                 for i in np.flatnonzero(~exato)]}
    print(f"[{rotulo}] idênticos {r['n_identicos']}/{r['n']} · até 1 ULP {r['n_ate_1ulp']}/{r['n']} · "
          f"dif. abs. máx. {r['diferenca_absoluta_maxima']:.3g} · decisões iguais {decisoes}")
    if not (ate_1ulp.all() and all(decisoes.values())):
        sys.exit(f"PARE: {rotulo} não reproduz a coleta (diferença > 1 ULP ou decisão diferente).")
    return r


def ambientes(fonte):
    amb_coleta = None
    arq = fonte / "Ambiente do Experimento.txt"
    if arq.exists():
        t = arq.read_text(encoding="utf-8")
        d, _ = json.JSONDecoder().raw_decode(t[t.index("{"):])
        amb_coleta = {"sistema": d["sistema_operacional"]["plataforma"], "python": d["python"],
                      "bibliotecas": d["bibliotecas"], "commit": d.get("git", {}).get("commit")}
    import scipy, PIL, statsmodels
    amb_atual = {"sistema": platform.platform(), "python": platform.python_version(),
                 "bibliotecas": {"numpy": np.__version__, "pandas": pd.__version__, "scipy": scipy.__version__,
                                 "statsmodels": statsmodels.__version__, "jpeglib": jpeglib.__version__,
                                 "Pillow": PIL.__version__}}
    return {"coleta": amb_coleta, "reanalise": amb_atual}


def proveniencia(saida, nome, fonte, extra):
    sha = lambda q: hashlib.sha256(q.read_bytes()).hexdigest()
    git = lambda *a: subprocess.run(["git", *a], cwd=RAIZ, capture_output=True, text=True).stdout.strip()
    prov = {"gerado_em": datetime.datetime.now(datetime.timezone.utc).isoformat(), "script": f"scripts/{nome}.py",
            "commit_repositorio": git("rev-parse", "HEAD"),
            "arvore_suja_src_scripts": bool(git("status", "--porcelain", "src", "scripts")),
            "nota_arvore": "script e saídas entram no mesmo commit; o código executado fica identificado pelos SHA-256 abaixo",
            "sha256_codigo": {str(q.relative_to(RAIZ)).replace("\\", "/"): sha(q) for q in
                              [RAIZ / "scripts" / f"{nome}.py", RAIZ / "scripts" / "reanalise_comum.py",
                               *sorted((RAIZ / "src").glob("*.py"))]},
            "fonte": str(fonte), "sha256_resultados.csv": sha(fonte / "resultados.csv"),
            "sha256_limpas.csv": sha(fonte / "limpas.csv"), "commit_coleta": "a8ef486b9ca8c77c2e7f0efc53856d5527879d8f",
            "ambientes": ambientes(fonte), **extra}
    (saida / f"proveniencia_{nome}.json").write_text(json.dumps(prov, indent=2, ensure_ascii=False, default=str) + "\n",
                                                     encoding="utf-8")


def br(x, d=3):
    """Número com vírgula decimal."""
    return "nan" if x != x else f"{x:.{d}f}".replace(".", ",")


def pc(x, d=1):
    return f"{100 * x:.{d}f}%".replace(".", ",")
