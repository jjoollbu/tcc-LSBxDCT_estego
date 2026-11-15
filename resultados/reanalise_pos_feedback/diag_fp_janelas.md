# Diagnóstico das janelas do qui-quadrado nas capas limpas

Fonte: `C:\Faculdade TCC\Resultados` (limpas.csv, commit da coleta a8ef486). Reanálise posterior à coleta; p_max e os resultados pré-registrados não mudam.
Validação: o máximo das 100 janelas recalculado reproduz o p_max de limpas.csv — 179/180 idênticos e 180/180 até 1 ULP (diferença absoluta máxima 1.1e-16); decisões em 0,95 e 0,99 idênticas.

## Capas PNG com FP na coleta (p_max ≥ 0,95)

| id | textura | p_max | janela do máximo (k%) | n na janela | p na janela de 100% | p na janela de 1% | janelas com p ≥ 0,95 |
|---|---|---|---|---|---|---|---|
| 202 | alta | 0,999987 | 1 | 2621 | 2,7e-189 | 1,0000 | 20/100 |
| 4512 | alta | 0,999196 | 1 | 2621 | 7,3e-16 | 0,9992 | 3/100 |
| 6248 | alta | 1,000000 | 1 | 2621 | 5,0e-26 | 1,0000 | 57/100 |
| 713 | alta | 0,999665 | 1 | 2621 | 2,0e-28 | 0,9997 | 8/100 |
| 8892 | alta | 0,980969 | 1 | 2621 | 3,9e-16 | 0,9810 | 1/100 |
| 3963 | alta | 0,989976 | 2 | 5242 | 5,8e-22 | 0,9852 | 3/100 |
| 6293 | alta | 0,979142 | 3 | 7864 | 5,9e-05 | 0,9744 | 4/100 |
| 9020 | alta | 0,999973 | 7 | 18350 | 3,0e-05 | 0,9957 | 38/100 |
| 4777 | alta | 1,000000 | 9 | 23592 | 0,4167 | 0,9892 | 72/100 |
| 1977 | baixa | 0,983666 | 1 | 2621 | 0,0000 | 0,9837 | 1/100 |
| 1938 | media | 0,999706 | 1 | 2621 | 0,0000 | 0,9997 | 3/100 |
| 283 | media | 0,999682 | 1 | 2621 | 4,1e-23 | 0,9997 | 6/100 |
| 2667 | media | 0,997357 | 2 | 5242 | 1,3e-109 | 0,9959 | 7/100 |
| 3194 | media | 0,999997 | 2 | 5242 | 6,6e-21 | 0,9955 | 78/100 |
| 9545 | media | 0,999955 | 9 | 23592 | 1,7e-05 | 0,9951 | 24/100 |
| 2185 | media | 0,998994 | 14 | 36700 | 1,1e-238 | 0,9900 | 13/100 |

## Comparação por grupo

| Grupo | n | k do máximo: mediana [Q1; Q3] | k = 1% | k ≤ 5% | k = 100% | p(100%) mediana | p(100%) máx. | p(1%) ≥ 0,95 | FP (regra D-12) | FP só com a janela de 100% (IC 95%) |
|---|---|---|---|---|---|---|---|---|---|---|
| png_fp_coleta | 16 | 1,5 [1; 4] | 8 | 12 | 0 | 3,1e-22 | 0,4167 | 16 | 16 | 0/16 — 0,0% [0,0%; 19,4%] |
| png_sem_fp | 74 | 1 [1; 2] | 54 | 61 | 1 | 3,3e-104 | 0,0011 | 0 | 0 | 0/74 — 0,0% [0,0%; 4,9%] |
| png_todas | 90 | 1 [1; 2] | 62 | 73 | 1 | 9,3e-86 | 0,4167 | 16 | 16 | 0/90 — 0,0% [0,0%; 4,1%] |
| jpeg_todas | 90 | 1 [1; 1] | 75 | 83 | 0 | 0,0000 | 3,7e-106 | 0 | 0 | 0/90 — 0,0% [0,0%; 4,1%] |
| png_baixa | 30 | 1 [1; 1,75] | 22 | 25 | 0 | 2,4e-212 | 2,3e-05 | 1 | 1 | 0/30 — 0,0% [0,0%; 11,4%] |
| png_media | 30 | 1 [1; 1,75] | 22 | 26 | 0 | 3,9e-77 | 1,7e-05 | 6 | 6 | 0/30 — 0,0% [0,0%; 11,4%] |
| png_alta | 30 | 1 [1; 6,5] | 18 | 22 | 1 | 2,5e-26 | 0,4167 | 9 | 9 | 0/30 — 0,0% [0,0%; 11,4%] |
| jpeg_baixa | 30 | 1 [1; 1] | 23 | 28 | 0 | 0,0000 | 3,9e-276 | 0 | 0 | 0/30 — 0,0% [0,0%; 11,4%] |
| jpeg_media | 30 | 1 [1; 1] | 25 | 27 | 0 | 0,0000 | 4,1e-129 | 0 | 0 | 0/30 — 0,0% [0,0%; 11,4%] |
| jpeg_alta | 30 | 1 [1; 1] | 27 | 28 | 0 | 9,8e-219 | 3,7e-106 | 0 | 0 | 0/30 — 0,0% [0,0%; 11,4%] |

## Leitura

- Nos 16 FP em PNG, o máximo saiu na janela de 1% em 8 casos e em k ≤ 5% em 12 (k mediano 1,5%; Q1–Q3 1–4%); em nenhum caso o máximo esteve na janela de 100% (0 de 16). Nos 16 de 16, a janela de 1% sozinha já dá p ≥ 0,95; nenhuma das 74 PNG sem FP tem p ≥ 0,95 nessa janela. Na janela de 100%, o p mediano desses FP é 3,1e-22 (máximo 0,4167).
- Se a regra usasse só a janela de 100%, seriam FP 0 de 90 capas PNG (0,0% [0,0%; 4,1%]) e 0 de 90 JPEG, contra 16 e 0 com a regra da D-12.
- Comparação: nas 74 PNG sem FP, k = 1% em 54; nas 90 JPEG, k = 1% em 75 (k mediano 1%). A janela de 1% tem 2621 pixels no PNG (as ~5 primeiras linhas da imagem) e de 173 a 840 coeficientes elegíveis no JPEG.

