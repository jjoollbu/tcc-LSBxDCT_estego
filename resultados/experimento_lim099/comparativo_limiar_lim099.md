# Detecção: limiar 0,95 (vigente) × 0,99 (calibração D-12)

Fonte: `C:\Faculdade TCC\Resultados` (commit da coleta a8ef486). Só reclassificação do p_max já gravado; nada foi re-medido.

## Capas limpas — falso positivo e especificidade (IC 95% de Wilson)

| Formato | Limiar | FP | Taxa de FP | Especificidade |
|---|---|---|---|---|
| PNG | 0.95 | 16/90 | 17.8% [11.2%; 26.9%] | 82.2% [73.1%; 88.8%] |
| PNG | 0.99 | 12/90 | 13.3% [7.8%; 21.9%] | 86.7% [78.1%; 92.2%] |
| JPEG | 0.95 | 0/90 | 0.0% [0.0%; 4.1%] | 100.0% [95.9%; 100.0%] |
| JPEG | 0.99 | 0/90 | 0.0% [0.0%; 4.1%] | 100.0% [95.9%; 100.0%] |

## Estego — falso negativo e sensibilidade (IC 95% de Wilson)

| Formato (técnica) | Taxa | FN 0,95 | FN 0,99 | Sensib. 0,95 | Sensib. 0,99 | Δ sensib. |
|---|---|---|---|---|---|---|
| JPEG (DCT) | baixa | 58/90 | 81/90 | 35.6% [26.4%; 45.8%] | 10.0% [5.4%; 17.9%] | -25.6 p.p. |
| JPEG (DCT) | media | 12/90 | 34/90 | 86.7% [78.1%; 92.2%] | 62.2% [51.9%; 71.5%] | -24.4 p.p. |
| JPEG (DCT) | alta | 6/90 | 21/90 | 93.3% [86.2%; 96.9%] | 76.7% [66.9%; 84.2%] | -16.7 p.p. |
| JPEG (DCT) | agregado | 76/270 | 136/270 | 71.9% [66.2%; 76.9%] | 49.6% [43.7%; 55.6%] | -22.2 p.p. |
| PNG (LSB) | baixa | 62/90 | 71/90 | 31.1% [22.5%; 41.3%] | 21.1% [14.0%; 30.6%] | -10.0 p.p. |
| PNG (LSB) | media | 16/90 | 31/90 | 82.2% [73.1%; 88.8%] | 65.6% [55.3%; 74.6%] | -16.7 p.p. |
| PNG (LSB) | alta | 15/90 | 25/90 | 83.3% [74.3%; 89.6%] | 72.2% [62.2%; 80.4%] | -11.1 p.p. |
| PNG (LSB) | agregado | 93/270 | 127/270 | 65.6% [59.7%; 71.0%] | 53.0% [47.0%; 58.8%] | -12.6 p.p. |

No agregado, as 3 taxas usam as mesmas 90 imagens; o IC trata as 270 estego como independentes (aproximação).

## Teste principal — McNemar exato LSB × DCT por taxa (BH na família de 3)

| Limiar | Taxa | Só LSB | Só DCT | p | p (BH) | Mais detectada | Signif. (BH < 0,05) |
|---|---|---|---|---|---|---|---|
| 0.95 | baixa | 9 | 13 | 0.5235 | 0.5572 | DCT | não |
| 0.95 | media | 11 | 15 | 0.5572 | 0.5572 | DCT | não |
| 0.95 | alta | 5 | 14 | 0.0636 | 0.1907 | DCT | não |
| 0.99 | baixa | 17 | 7 | 0.0639 | 0.1917 | LSB | não |
| 0.99 | media | 22 | 19 | 0.7552 | 0.7552 | LSB | não |
| 0.99 | alta | 15 | 19 | 0.6076 | 0.7552 | DCT | não |

## Conferência com a coleta (0,95)

- tabela_fn.csv: True
- tabela_fp.csv: True
- tabela_deteccao.csv: True
- limpas.csv: falso_positivo == p_max >= 0.95: True
