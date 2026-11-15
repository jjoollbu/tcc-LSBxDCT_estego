# Verificação da distorção da DCT pelo teorema de Parseval

Fonte: `C:\Faculdade TCC\Resultados` (resultados.csv, commit da coleta a8ef486). Análise posterior à coleta; não altera as métricas.
Estego DCT regeneradas em memória: 270/270 com o mesmo SHA-256 de resultados.csv; o mse recalculado (JPEG × JPEG decodificados, D-19) coincide com a coluna mse.
Tabela de quantização do Y igual nas 90 capas: sim. Orientação de qt[0] conferida por IDCT (erro médio 0.014 contra 0.468 com a transposta).

q das 26 posições da banda (ordem zigue-zague): 2, 2, 2, 2, 2, 4, 3, 2, 2, 2, 2, 5, 4, 4, 3, 4, 6, 5, 6, 6, 6, 5, 6, 6, 6, 7.

## MSE medido × modelos

Previsto = Parseval com as alterações reais, Σ(Δ·q)²/262144. Esperado = 0,5·Σq²/262144 nas n primeiras posições elegíveis. Arredondado = decodificador de referência (IDCT em float) com pixels arredondados e cortados em 0–255.

| Taxa | n | Pearson (prev.) | Medido/previsto mediana [Q1; Q3] | Erro rel. mediano (prev.) | Pearson (esp.) | Medido/esperado mediana [Q1; Q3] | Pearson (arred.) | Medido/arredondado mediana [Q1; Q3] |
|---|---|---|---|---|---|---|---|---|
| baixa | 90 | 0,8757 | 1,304 [1,139; 1,559] | 30,4% | 0,8501 | 1,304 [1,127; 1,588] | 0,999385 | 1,0017 [0,9974; 1,0044] |
| media | 90 | 0,9661 | 1,186 [1,102; 1,342] | 18,6% | 0,9611 | 1,183 [1,101; 1,354] | 0,999935 | 1,0007 [0,9998; 1,0019] |
| alta | 90 | 0,9768 | 1,161 [1,091; 1,277] | 16,1% | 0,9755 | 1,157 [1,099; 1,274] | 0,999951 | 1,0006 [0,9998; 1,0015] |
| todas | 270 | 0,9897 | 1,206 [1,104; 1,368] | 20,6% | 0,9896 | 1,191 [1,101; 1,364] | 0,999997 | 1,0007 [0,9994; 1,0023] |

Parseval numérico: a IDCT ortonormal em float da diferença reproduz a energia prevista (erro relativo máximo 2,4e-15).

## Razão MSE_DCT / MSE_LSB × E[q²] nas posições usadas

Razão observada por par (mesma imagem): média geométrica, como no artigo, e mediana [Q1; Q3]. Pelo modelo esperado, a razão seria E[q²].

| Taxa | E[q²] mediana [Q1; Q3] | q médio (√E[q²]) | Razão observada: média geométrica | Razão observada: mediana [Q1; Q3] | Razão prevista (Parseval/LSB), mediana |
|---|---|---|---|---|---|
| baixa | 10,17 [7,43; 13,42] | 3,19 | 13,37 | 13,02 [12,04; 15,19] | 10,29 |
| media | 12,31 [9,46; 14,46] | 3,51 | 14,28 | 14,46 [12,68; 16,10] | 12,26 |
| alta | 12,86 [10,43; 14,87] | 3,59 | 14,49 | 14,59 [13,03; 16,16] | 12,66 |

## Textura: PSNR da DCT por categoria (medianas, dB)

| Taxa | Textura | PSNR DCT observado | Parseval (previsto) | Esperado (E[q²]) | Modelo arredondado | Medido/previsto | E[q²] | PSNR LSB observado |
|---|---|---|---|---|---|---|---|---|
| baixa | baixa | 64,16 | 65,82 | 65,83 | 64,17 | 1,462 | 8,51 | 75,11 |
| baixa | media | 64,05 | 65,28 | 65,43 | 64,06 | 1,382 | 9,32 | 75,14 |
| baixa | alta | 63,24 | 63,64 | 63,63 | 63,22 | 1,099 | 14,09 | 75,10 |
| media | baixa | 55,25 | 56,51 | 56,59 | 55,25 | 1,348 | 9,50 | 66,38 |
| media | media | 54,72 | 55,42 | 55,43 | 54,71 | 1,178 | 12,42 | 66,41 |
| media | alta | 54,26 | 54,74 | 54,72 | 54,26 | 1,092 | 14,64 | 66,38 |
| alta | baixa | 52,19 | 53,31 | 53,31 | 52,20 | 1,294 | 10,11 | 63,36 |
| alta | media | 51,52 | 52,10 | 52,06 | 51,52 | 1,149 | 13,48 | 63,37 |
| alta | alta | 51,16 | 51,52 | 51,53 | 51,16 | 1,082 | 15,23 | 63,37 |

| Taxa | Δ PSNR DCT alta − baixa: observado | Parseval | esperado | modelo arredondado | Δ PSNR LSB alta − baixa | E[q²] alta / baixa |
|---|---|---|---|---|---|---|
| baixa | -0,92 | -2,19 | -2,19 | -0,94 | -0,01 | 1,657 |
| media | -0,99 | -1,77 | -1,88 | -0,99 | 0,01 | 1,540 |
| alta | -1,03 | -1,79 | -1,78 | -1,04 | 0,01 | 1,507 |

## Leitura

- Nas 270 estego DCT, o MSE medido acompanha o previsto por Parseval (Pearson 0,9897), mas fica acima dele: razão medido/previsto com mediana 1,206 [Q1–Q3 1,104–1,368]. Com o arredondamento dos pixels para inteiros e o corte em 0–255, o modelo passa a reproduzir o medido (razão mediana 1,0007; Pearson 0,999997). O excesso sobre Parseval vem, portanto, da decodificação para pixels inteiros.
- E[q²] nas posições usadas tem mediana 10,17, 12,31 e 12,86 (taxas baixa, média e alta; q médio de 3,19 a 3,59). A razão MSE_DCT/MSE_LSB observada é 13,4, 14,3 e 14,5 (média geométrica). E[q²] explica a maior parte dessa razão; o restante corresponde ao excesso do arredondamento.
- Na taxa alta, o PSNR da DCT em textura alta fica 1,03 dB abaixo da textura baixa. O E[q²] é maior na textura alta (15,23 contra 10,11): as posições elegíveis usadas caem mais nas frequências com passo q maior. Parseval sozinho prevê 1,79 dB; com o arredondamento, que pesa mais na textura baixa (medido/previsto 1,29 contra 1,08), o modelo prevê 1,04 dB. No LSB a diferença é 0,01 dB.

