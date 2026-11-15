# Histograma dos coeficientes da banda DCT: capa × estego (objetivo e)

Fonte: `C:\Faculdade TCC\Resultados` (commit da coleta a8ef486). Estego DCT regeneradas em memória: 270/270 com o mesmo SHA-256 de resultados.csv. Análise posterior à coleta e descritiva; a detecção pré-registrada continua sendo o qui-quadrado (D-12).
Coeficientes da banda nas posições elegíveis (≠ 0 e ≠ 1), na ordem de inserção. Assimetria dos pares A = Σ|h(2k) − h(2k+1)| / Σ(h(2k) + h(2k+1)) nos 19 pares de −20 a 19 (sem 0/1); A = 0 é o equilíbrio total. Região global = todas as posições elegíveis; região inserida = as n primeiras (n = 1.048, 7.864 e 15.728 bits).

| Região | Taxa | A capa: mediana [Q1; Q3] | A estego: mediana [Q1; Q3] | ΔA: mediana [Q1; Q3] | Redução relativa mediana | Estego < capa | Wilcoxon p | p BH |
|---|---|---|---|---|---|---|---|---|
| global | baixa | 0,3237 [0,2085; 0,4498] | 0,3060 [0,2053; 0,4153] | -0,0157 [-0,0273; -0,0062] | 4,2% | 90/90 | 1,7e−16 | 1,7e−16 |
| global | media | 0,3237 [0,2085; 0,4498] | 0,2393 [0,1798; 0,2830] | -0,0777 [-0,1612; -0,0360] | 24,6% | 90/90 | 1,7e−16 | 1,7e−16 |
| global | alta | 0,3237 [0,2085; 0,4498] | 0,1505 [0,1162; 0,1867] | -0,1360 [-0,3099; -0,0633] | 44,0% | 90/90 | 1,7e−16 | 1,7e−16 |
| inserida | baixa | 0,4977 [0,3135; 0,7018] | 0,0643 [0,0442; 0,0789] | -0,4299 [-0,6598; -0,2321] | 87,4% | 89/90 | 1,8e−16 | 1,8e−16 |
| inserida | media | 0,3647 [0,2499; 0,4850] | 0,0266 [0,0224; 0,0327] | -0,3357 [-0,4572; -0,2191] | 92,5% | 90/90 | 1,7e−16 | 1,8e−16 |
| inserida | alta | 0,3289 [0,2217; 0,4472] | 0,0206 [0,0176; 0,0241] | -0,3122 [-0,4320; -0,2055] | 94,0% | 90/90 | 1,7e−16 | 1,8e−16 |

Mediana de A na região inserida por textura:

| Taxa | Textura | A capa | A estego | ΔA |
|---|---|---|---|---|
| baixa | baixa | 0,6076 | 0,0525 | -0,5458 |
| baixa | media | 0,4971 | 0,0572 | -0,4251 |
| baixa | alta | 0,2793 | 0,0806 | -0,1861 |
| media | baixa | 0,5282 | 0,0242 | -0,5013 |
| media | media | 0,3478 | 0,0270 | -0,3239 |
| media | alta | 0,2302 | 0,0275 | -0,2096 |
| alta | baixa | 0,4864 | 0,0179 | -0,4675 |
| alta | media | 0,3150 | 0,0220 | -0,2961 |
| alta | alta | 0,1952 | 0,0233 | -0,1746 |

Figura: `histograma_dct.png`.

## Leitura

- Na região inserida, a assimetria dos pares cai de 0,498 → 0,064 (taxa baixa), 0,365 → 0,027 (média) e 0,329 → 0,021 (alta), medianas, com a estego abaixo da capa em 89, 90 e 90 das 90 imagens: é o equilíbrio dos pares 2k/2k+1 esperado do Jsteg.
- No histograma global (todas as posições elegíveis), o efeito é diluído: a redução relativa mediana de A é 4,2%, 24,6% e 44,0%, porque o payload ocupa só as primeiras posições elegíveis.
- Os p-valores do Wilcoxon são descritivos (análise não prevista na metodologia).

