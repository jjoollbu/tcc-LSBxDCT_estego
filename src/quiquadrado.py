"""Detector qui-quadrado de Westfeld e Pfitzmann. Tarefa T1.10 (Ana). Ver Seção 3.5.3.

A amostra é lida na mesma ordem usada para esconder (decisão D-18):
    LSB: os pixels em ordem de varredura, imagem.ravel()
    DCT: os coeficientes elegíveis da banda, v = coeficientes_banda(Y); v[posicoes_elegiveis(v)]
Detectado se p_max >= 0,95 (decisão D-12). Neste teste p alto indica esteganografia: não usar p < 0,05.
"""
import numpy as np
from scipy.stats import chi2


def p_valor_janela(valores: np.ndarray) -> float:
    """Ataque de Westfeld e Pfitzmann em uma janela. Devolve nan se a janela for pequena demais."""
    v = valores.astype(np.int64)
    base = v.min() - (v.min() % 2)                 # começa num número par
    h = np.bincount(v - base)
    if h.size % 2:
        h = np.append(h, 0)
    pares, impares = h[0::2].astype(float), h[1::2].astype(float)
    esperado = (pares + impares) / 2
    ok = esperado >= 5                             # categorias válidas
    if ok.sum() < 2:
        return float("nan")
    estat = (((pares[ok] - esperado[ok]) ** 2) / esperado[ok]).sum()
    return float(chi2.sf(estat, ok.sum() - 1))     # p alto = pares equilibrados = indício


def p_max(amostra: np.ndarray, passos: int = 100) -> float:
    """Maior p-valor entre janelas acumuladas de 1%, 2%, ..., 100% da amostra."""
    ps = []
    for k in range(1, passos + 1):
        n = int(len(amostra) * k / passos)
        if n > 0:
            p = p_valor_janela(amostra[:n])
            if p == p:                             # descarta nan (janela pequena demais)
                ps.append(p)
    return max(ps) if ps else float("nan")


def p_max_absoluto(amostra: np.ndarray, passo: int = 256) -> float:
    """Maior p-valor entre janelas acumuladas de tamanho absoluto: passo, 2·passo, ... amostras.

    Análise de sensibilidade posterior à coleta (não substitui p_max, que segue sendo a regra
    pré-registrada da D-12). Se o total não for múltiplo do passo, a amostra inteira entra como
    última janela, para a janela de 100% estar sempre incluída. Mesma p_valor_janela e mesmo
    descarte de janelas nan que p_max.
    """
    total = len(amostra)
    tamanhos = list(range(passo, total + 1, passo))
    if total > 0 and (not tamanhos or tamanhos[-1] != total):
        tamanhos.append(total)
    ps = []
    for n in tamanhos:
        p = p_valor_janela(amostra[:n])
        if p == p:                                 # descarta nan (janela pequena demais)
            ps.append(p)
    return max(ps) if ps else float("nan")
