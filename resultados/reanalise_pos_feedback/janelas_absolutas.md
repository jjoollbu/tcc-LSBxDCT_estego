# Detecção com janelas acumuladas de tamanho absoluto (p_max_absoluto)

Fonte: `C:\Faculdade TCC\Resultados` (commit da coleta a8ef486). Reanálise posterior à coleta; a regra pré-registrada (D-12, janelas de 1% a 100%) e seus resultados continuam sendo os principais.
Janelas acumuladas de passo, 2·passo, ... amostras até o total (a amostra inteira entra como última janela). Detectado/FP se p ≥ 0,95. IC 95% de Wilson; McNemar exato pareado LSB × DCT com BH na família das 3 taxas.

## Validação da regeneração

- Estego: 539/540 p_max idênticos a resultados.csv e 540/540 até 1 ULP (diferença absoluta máxima 3,5e-18); decisões em 0,95 e 0,99 idênticas.
- Capas limpas: 179/180 idênticos a limpas.csv e 180/180 até 1 ULP (máx. 1,1e-16); decisões idênticas.
- A regra original reproduz tabela_deteccao.csv da coleta: sim.

## Falsos positivos nas capas limpas

| Regra | PNG: FP (IC 95%) | PNG por textura (baixa/media/alta) | JPEG: FP (IC 95%) |
|---|---|---|---|
| Original (janelas de 1%) | 16/90 — 17,8% [11,2%; 26,9%] | 1/6/9 | 0/90 — 0,0% [0,0%; 4,1%] |
| Absoluta, passo 128 | 25/90 — 27,8% [19,6%; 37,8%] | 5/8/12 | 4/90 — 4,4% [1,7%; 10,9%] |
| Absoluta, passo 256 | 23/90 — 25,6% [17,7%; 35,4%] | 5/7/11 | 2/90 — 2,2% [0,6%; 7,7%] |
| Absoluta, passo 512 | 21/90 — 23,3% [15,8%; 33,1%] | 4/7/10 | 2/90 — 2,2% [0,6%; 7,7%] |

## Sensibilidade (estego detectadas, IC 95%)

| Regra | Técnica | baixa | media | alta | agregado |
|---|---|---|---|---|---|
| Original (janelas de 1%) | LSB | 28/90 — 31,1% [22,5%; 41,3%] | 74/90 — 82,2% [73,1%; 88,8%] | 75/90 — 83,3% [74,3%; 89,6%] | 177/270 — 65,6% [59,7%; 71,0%] |
| Original (janelas de 1%) | DCT | 32/90 — 35,6% [26,4%; 45,8%] | 78/90 — 86,7% [78,1%; 92,2%] | 84/90 — 93,3% [86,2%; 96,9%] | 194/270 — 71,9% [66,2%; 76,9%] |
| Absoluta, passo 128 | LSB | 65/90 — 72,2% [62,2%; 80,4%] | 81/90 — 90,0% [82,1%; 94,6%] | 80/90 — 88,9% [80,7%; 93,9%] | 226/270 — 83,7% [78,8%; 87,6%] |
| Absoluta, passo 128 | DCT | 39/90 — 43,3% [33,6%; 53,6%] | 82/90 — 91,1% [83,4%; 95,4%] | 86/90 — 95,6% [89,1%; 98,3%] | 207/270 — 76,7% [71,3%; 81,3%] |
| Absoluta, passo 256 | LSB | 62/90 — 68,9% [58,7%; 77,5%] | 81/90 — 90,0% [82,1%; 94,6%] | 78/90 — 86,7% [78,1%; 92,2%] | 221/270 — 81,9% [76,8%; 86,0%] |
| Absoluta, passo 256 | DCT | 36/90 — 40,0% [30,5%; 50,3%] | 81/90 — 90,0% [82,1%; 94,6%] | 85/90 — 94,4% [87,6%; 97,6%] | 202/270 — 74,8% [69,3%; 79,6%] |
| Absoluta, passo 512 | LSB | 56/90 — 62,2% [51,9%; 71,5%] | 81/90 — 90,0% [82,1%; 94,6%] | 78/90 — 86,7% [78,1%; 92,2%] | 215/270 — 79,6% [74,4%; 84,0%] |
| Absoluta, passo 512 | DCT | 27/90 — 30,0% [21,5%; 40,1%] | 77/90 — 85,6% [76,8%; 91,4%] | 85/90 — 94,4% [87,6%; 97,6%] | 189/270 — 70,0% [64,3%; 75,2%] |

## McNemar exato LSB × DCT por taxa (BH na família de 3)

| Regra | Taxa | Só LSB | Só DCT | Ambas | Nenhuma | p | p ajustado (BH) | Mais detectada |
|---|---|---|---|---|---|---|---|---|
| Original (janelas de 1%) | baixa | 9 | 13 | 19 | 49 | 0,523 | 0,557 | dct |
| Original (janelas de 1%) | media | 11 | 15 | 63 | 1 | 0,557 | 0,557 | dct |
| Original (janelas de 1%) | alta | 5 | 14 | 70 | 1 | 0,064 | 0,191 | dct |
| Absoluta, passo 128 | baixa | 32 | 6 | 33 | 19 | < 0,001 | < 0,001 | lsb (sig.) |
| Absoluta, passo 128 | media | 8 | 9 | 73 | 0 | 1,000 | 1,000 | dct |
| Absoluta, passo 128 | alta | 4 | 10 | 76 | 0 | 0,180 | 0,269 | dct |
| Absoluta, passo 256 | baixa | 32 | 6 | 30 | 22 | < 0,001 | < 0,001 | lsb (sig.) |
| Absoluta, passo 256 | media | 9 | 9 | 72 | 0 | 1,000 | 1,000 | empate |
| Absoluta, passo 256 | alta | 4 | 11 | 74 | 1 | 0,118 | 0,178 | dct |
| Absoluta, passo 512 | baixa | 34 | 5 | 22 | 29 | < 0,001 | < 0,001 | lsb (sig.) |
| Absoluta, passo 512 | media | 13 | 9 | 68 | 0 | 0,523 | 0,523 | lsb |
| Absoluta, passo 512 | alta | 4 | 11 | 74 | 1 | 0,118 | 0,178 | dct |

## Leitura

- FP: no PNG, 16/90 com a regra original e 25/90, 23/90, 21/90 com passo 128, 256, 512; no JPEG, 0/90 com a regra original e 4/90, 2/90, 2/90. Janelas absolutas pequenas não reduzem o FP; aumentam-no nos dois formatos.
- Sensibilidade na taxa baixa: LSB 31,1% com a regra original e 62,2% a 72,2% com janelas absolutas; DCT 35,6% e 30,0% a 43,3%. No LSB, o payload da taxa baixa ocupa 1048 pixels, menos que a primeira janela relativa (2621 pixels), de modo que a regra original nunca testa um trecho só com pixels alterados; as janelas absolutas de 128 a 512 testam. Parte desse ganho, porém, vem com mais FP.
- Diferenças LSB × DCT significativas após BH: Absoluta, passo 128, taxa baixa (32 só LSB × 6 só DCT; p_BH = 7,3e-05); Absoluta, passo 256, taxa baixa (32 só LSB × 6 só DCT; p_BH = 7,3e-05); Absoluta, passo 512, taxa baixa (34 só LSB × 5 só DCT; p_BH = 7,3e-06). Com a regra original: nenhuma. Taxas sem diferença significativa em nenhuma regra: media, alta.

