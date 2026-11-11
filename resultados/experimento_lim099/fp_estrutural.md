# FP em capas limpas: estrutural ou de calibração?

Fonte: `C:\Faculdade TCC\Resultados` · limpas.csv SHA-256 `67b4112daf792b85…` · commit da coleta a8ef486. Só leitura do p_max já gravado em limpas.csv (capas sem payload) e resultados.csv (estego, só no item 5); nada foi re-medido.
Regra: FP se p_max ≥ L (D-12). IC 95% de Wilson. Aceitável = FP ≤ 5%, avaliado pela estimativa pontual e pelos dois limites do IC.

## Resumo

- **Onde o FP se concentra (PNG):** das 16 capas limpas marcadas com 0,95, 10 têm p_max ≥ 0,999 e 3 estão em ≥ 0,99999; o máximo é 0,9999999542. Capas com p_max exatamente 1,0: 0.
- **Menor limiar < 1 que resolve (PNG):** pela estimativa pontual, L > 0,9999733918 (1 − L ≈ 2,7e-05, até 4 FP); para o limite superior do IC ficar ≤ 5% (0 FP), L > 0,9999999542 (1 − L ≈ 4,6e-08). Entre os candidatos, atingem ≤ 5% (ponto): 1,0 (estrito) (6/90 ainda marcadas com 0,9999). Existe L < 1 em sentido estrito, mas só colado em 1 e ajustado ao máximo desta amostra; capas com p_max = 1,0 exato que nenhum L < 1 remove: 0.
- **Textura (PNG, 0,95):** baixa 1, media 6, alta 9 de 30 cada.
- **Custo em detecção:** 0,95 — FP PNG 17,8%, sensibilidade LSB 65,6% e DCT 71,9%; mínimo PNG (ic_inf) — FP PNG 8,9%, sensibilidade LSB 32,2% e DCT 13,3%; mínimo PNG (ponto) — FP PNG 4,4%, sensibilidade LSB 17,4% e DCT 3,7%; mínimo PNG (ic_sup) — FP PNG 0,0%, sensibilidade LSB 3,7% e DCT 0,0%. Para levar o FP do PNG a ≤ 5% (ponto), a sensibilidade agregada do LSB cai 48,1 p.p. em relação a 0,95: as caudas de p_max de limpas e estego se sobrepõem perto de 1.
- **JPEG (contraste):** 0 FP em todos os limiares; p_max máximo 0,928568.

## PNG

p_max máximo observado: 0,9999999542 · capas com p_max exatamente 1,0: 0 de 90

### PNG — 1. Distribuição do p_max por faixa

| Faixa | Capas | % (IC 95%) | baixa | media | alta |
|---|---|---|---|---|---|
| <0,95 | 74/90 | 82,2% [73,1%; 88,8%] | 29 | 24 | 21 |
| [0,95; 0,99) | 4/90 | 4,4% [1,7%; 10,9%] | 1 | 0 | 3 |
| [0,99; 0,999) | 2/90 | 2,2% [0,6%; 7,7%] | 0 | 2 | 0 |
| [0,999; 0,99999) | 7/90 | 7,8% [3,8%; 15,2%] | 0 | 3 | 4 |
| ≈1,000 (≥0,99999) | 3/90 | 3,3% [1,1%; 9,3%] | 0 | 1 | 2 |

### PNG — 2. FP sobreviventes a cada limiar candidato

| Limiar L | Marcadas (p_max ≥ L) | Taxa de FP (IC 95%) | ≤5% (ponto) | ≤5% (IC inf) | ≤5% (IC sup) |
|---|---|---|---|---|---|
| 0,95 | 16/90 | 17,8% [11,2%; 26,9%] | não | não | não |
| 0,99 | 12/90 | 13,3% [7,8%; 21,9%] | não | não | não |
| 0,999 | 10/90 | 11,1% [6,1%; 19,3%] | não | não | não |
| 0,9999 | 6/90 | 6,7% [3,1%; 13,8%] | não | sim | não |
| 1,0 (estrito) | 0/90 | 0,0% [0,0%; 4,1%] | sim | sim | sim |

### PNG — 3. Menor limiar < 1 que leva o FP a ≤ 5%

| Critério | Máx. de FP admitido (de 90) | Limiar necessário | 1 − L | Existe L < 1? |
|---|---|---|---|---|
| taxa de FP ≤ 5% | 4 | L > 0,9999733918 | 2,7e-05 | sim |
| limite inferior do IC ≤ 5% (não é maior que 5%) | 8 | L > 0,9996645805 | 3,4e-04 | sim |
| limite superior do IC ≤ 5% (comprovadamente ≤ 5%) | 0 | L > 0,9999999542 | 4,6e-08 | sim |

Capas com p_max = 1,0 exato, que nenhum limiar < 1 removeria: 0.

### PNG — 4. FP × categoria de textura

| Limiar L | baixa (de 30) | media (de 30) | alta (de 30) |
|---|---|---|---|
| 0,95 | 1 — 3,3% [0,6%; 16,7%] | 6 — 20,0% [9,5%; 37,3%] | 9 — 30,0% [16,7%; 47,9%] |
| 0,99 | 0 — 0,0% [0,0%; 11,4%] | 6 — 20,0% [9,5%; 37,3%] | 6 — 20,0% [9,5%; 37,3%] |
| 0,999 | 0 — 0,0% [0,0%; 11,4%] | 4 — 13,3% [5,3%; 29,7%] | 6 — 20,0% [9,5%; 37,3%] |
| 0,9999 | 0 — 0,0% [0,0%; 11,4%] | 2 — 6,7% [1,8%; 21,3%] | 4 — 13,3% [5,3%; 29,7%] |
| 1,0 (estrito) | 0 — 0,0% [0,0%; 11,4%] | 0 — 0,0% [0,0%; 11,4%] | 0 — 0,0% [0,0%; 11,4%] |

### PNG — 5. Custo em detecção (estego LSB, resultados.csv)

Mesmos limiares nos dois formatos (a D-12 usa um limiar só). "mínimo PNG" = menor limiar concreto que atende o critério do item 3 no PNG.

| Limiar L | Valor | FP PNG (limpas) | Sensibilidade agregada (IC 95%) | baixa | media | alta |
|---|---|---|---|---|---|---|
| 0,95 | 0,9500000000 | 16/90 (17,8%) | 177/270 — 65,6% [59,7%; 71,0%] | 31,1% | 82,2% | 83,3% |
| 0,99 | 0,9900000000 | 12/90 (13,3%) | 143/270 — 53,0% [47,0%; 58,8%] | 21,1% | 65,6% | 72,2% |
| 0,999 | 0,9990000000 | 10/90 (11,1%) | 106/270 — 39,3% [33,6%; 45,2%] | 14,4% | 46,7% | 56,7% |
| mínimo PNG (ic_inf) | 0,9996822702220352 | 8/90 (8,9%) | 87/270 — 32,2% [26,9%; 38,0%] | 8,9% | 37,8% | 50,0% |
| 0,9999 | 0,9999000000 | 6/90 (6,7%) | 74/270 — 27,4% [22,4%; 33,0%] | 5,6% | 33,3% | 43,3% |
| mínimo PNG (ponto) | 0,9999867260976176 | 4/90 (4,4%) | 47/270 — 17,4% [13,4%; 22,4%] | 4,4% | 20,0% | 27,8% |
| mínimo PNG (ic_sup) | 0,9999999542096293 | 0/90 (0,0%) | 10/270 — 3,7% [2,0%; 6,7%] | 1,1% | 3,3% | 6,7% |
| 1,0 (estrito) | 1,0000000000 | 0/90 (0,0%) | 0/270 — 0,0% [0,0%; 1,4%] | 0,0% | 0,0% | 0,0% |

## JPEG

p_max máximo observado: 0,9285682067 · capas com p_max exatamente 1,0: 0 de 90

### JPEG — 1. Distribuição do p_max por faixa

| Faixa | Capas | % (IC 95%) | baixa | media | alta |
|---|---|---|---|---|---|
| <0,95 | 90/90 | 100,0% [95,9%; 100,0%] | 30 | 30 | 30 |
| [0,95; 0,99) | 0/90 | 0,0% [0,0%; 4,1%] | 0 | 0 | 0 |
| [0,99; 0,999) | 0/90 | 0,0% [0,0%; 4,1%] | 0 | 0 | 0 |
| [0,999; 0,99999) | 0/90 | 0,0% [0,0%; 4,1%] | 0 | 0 | 0 |
| ≈1,000 (≥0,99999) | 0/90 | 0,0% [0,0%; 4,1%] | 0 | 0 | 0 |

### JPEG — 2. FP sobreviventes a cada limiar candidato

| Limiar L | Marcadas (p_max ≥ L) | Taxa de FP (IC 95%) | ≤5% (ponto) | ≤5% (IC inf) | ≤5% (IC sup) |
|---|---|---|---|---|---|
| 0,95 | 0/90 | 0,0% [0,0%; 4,1%] | sim | sim | sim |
| 0,99 | 0/90 | 0,0% [0,0%; 4,1%] | sim | sim | sim |
| 0,999 | 0/90 | 0,0% [0,0%; 4,1%] | sim | sim | sim |
| 0,9999 | 0/90 | 0,0% [0,0%; 4,1%] | sim | sim | sim |
| 1,0 (estrito) | 0/90 | 0,0% [0,0%; 4,1%] | sim | sim | sim |

### JPEG — 3. Menor limiar < 1 que leva o FP a ≤ 5%

| Critério | Máx. de FP admitido (de 90) | Limiar necessário | 1 − L | Existe L < 1? |
|---|---|---|---|---|
| taxa de FP ≤ 5% | 4 | ≤ 0,95 (já atendido) | — | sim |
| limite inferior do IC ≤ 5% (não é maior que 5%) | 8 | ≤ 0,95 (já atendido) | — | sim |
| limite superior do IC ≤ 5% (comprovadamente ≤ 5%) | 0 | ≤ 0,95 (já atendido) | — | sim |

Capas com p_max = 1,0 exato, que nenhum limiar < 1 removeria: 0.

### JPEG — 4. FP × categoria de textura

| Limiar L | baixa (de 30) | media (de 30) | alta (de 30) |
|---|---|---|---|
| 0,95 | 0 — 0,0% [0,0%; 11,4%] | 0 — 0,0% [0,0%; 11,4%] | 0 — 0,0% [0,0%; 11,4%] |
| 0,99 | 0 — 0,0% [0,0%; 11,4%] | 0 — 0,0% [0,0%; 11,4%] | 0 — 0,0% [0,0%; 11,4%] |
| 0,999 | 0 — 0,0% [0,0%; 11,4%] | 0 — 0,0% [0,0%; 11,4%] | 0 — 0,0% [0,0%; 11,4%] |
| 0,9999 | 0 — 0,0% [0,0%; 11,4%] | 0 — 0,0% [0,0%; 11,4%] | 0 — 0,0% [0,0%; 11,4%] |
| 1,0 (estrito) | 0 — 0,0% [0,0%; 11,4%] | 0 — 0,0% [0,0%; 11,4%] | 0 — 0,0% [0,0%; 11,4%] |

### JPEG — 5. Custo em detecção (estego DCT, resultados.csv)

Mesmos limiares nos dois formatos (a D-12 usa um limiar só). "mínimo PNG" = menor limiar concreto que atende o critério do item 3 no PNG.

| Limiar L | Valor | FP JPEG (limpas) | Sensibilidade agregada (IC 95%) | baixa | media | alta |
|---|---|---|---|---|---|---|
| 0,95 | 0,9500000000 | 0/90 (0,0%) | 194/270 — 71,9% [66,2%; 76,9%] | 35,6% | 86,7% | 93,3% |
| 0,99 | 0,9900000000 | 0/90 (0,0%) | 134/270 — 49,6% [43,7%; 55,6%] | 10,0% | 62,2% | 76,7% |
| 0,999 | 0,9990000000 | 0/90 (0,0%) | 60/270 — 22,2% [17,7%; 27,6%] | 0,0% | 23,3% | 43,3% |
| mínimo PNG (ic_inf) | 0,9996822702220352 | 0/90 (0,0%) | 36/270 — 13,3% [9,8%; 17,9%] | 0,0% | 13,3% | 26,7% |
| 0,9999 | 0,9999000000 | 0/90 (0,0%) | 23/270 — 8,5% [5,7%; 12,5%] | 0,0% | 7,8% | 17,8% |
| mínimo PNG (ponto) | 0,9999867260976176 | 0/90 (0,0%) | 10/270 — 3,7% [2,0%; 6,7%] | 0,0% | 4,4% | 6,7% |
| mínimo PNG (ic_sup) | 0,9999999542096293 | 0/90 (0,0%) | 0/270 — 0,0% [0,0%; 1,4%] | 0,0% | 0,0% | 0,0% |
| 1,0 (estrito) | 1,0000000000 | 0/90 (0,0%) | 0/270 — 0,0% [0,0%; 1,4%] | 0,0% | 0,0% | 0,0% |

## Conferência

No agregado as 3 taxas usam as mesmas 90 imagens; o IC trata as 270 estego como independentes (aproximação, como em reanalise_limiar.py).

- sensibilidade 0,95/0,99 == tabela_fn_lim099.csv: True

