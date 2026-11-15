# Reanálises pós-feedback (nov/2026) — resumo para o artigo

Todas as análises abaixo são **análises de sensibilidade posteriores à coleta** (commit da coleta
`a8ef486`), feitas em resposta ao parecer externo sobre as janelas de 1% do qui-quadrado, a distorção
da DCT (Parseval), a AUC sem intervalo de confiança e o objetivo específico (e). Elas não alteram
`resultados.csv`, `limpas.csv` nem `src/quiquadrado.p_max`. **Os resultados pré-registrados continuam
sendo os principais.** Cada número vem dos CSV desta pasta; o detalhe está no `.md` de cada script.

## Reprodutibilidade

As 540 imagens estego foram regeneradas em memória a partir das capas e dos payloads, e a reprodução
foi idêntica bit a bit: as 270 estego DCT têm o mesmo SHA-256 registrado na coleta e as 270 estego LSB
têm o mesmo MSE exato; as capas JPEG têm o mesmo SHA-256 (90/90) e as capas PNG têm os mesmos pixels do
original (os bytes do PNG diferem por causa da compressão zlib de cada sistema). Os valores-p do
detector foram reproduzidos dentro de 1 ULP: 539 de 540 p_max das estego e 179 de 180 das capas limpas
foram idênticos, e os dois restantes diferiram no último bit (diferença absoluta máxima 1,1·10⁻¹⁶). Nenhuma
decisão de detecção mudou, nem com o limiar de 0,95 nem com o de 0,99. A diferença vem da biblioteca
matemática de cada sistema: a coleta rodou em Linux (WSL2, Python 3.10.12, numpy 2.2.6, scipy 1.15.3) e
as reanálises em Windows 10 (Python 3.12.3, numpy 2.5.4, scipy 1.18.1).

## 1. Janelas do qui-quadrado e falsos positivos em PNG (`diag_fp_janelas.md`)

- Nas 16 capas PNG com falso positivo, o maior valor-p saiu nas primeiras janelas acumuladas: na
  janela de 1% em 8 casos, em até 5% em 12 e, no máximo, em 14%. Em todas as 16, a janela de 1%
  (2.621 pixels, as cerca de cinco primeiras linhas da imagem) já tinha p ≥ 0,95, o que não ocorreu em
  nenhuma das 74 capas PNG sem falso positivo.
- Na janela de 100%, o valor-p dessas 16 capas teve mediana de 3,1·10⁻²² (máximo de 0,42). Se a decisão
  usasse só a janela completa, nenhuma das 90 capas PNG e nenhuma das 90 JPEG seria falso positivo
  (0/90; IC 95% de 0,0% a 4,1%), contra 16/90 PNG pela regra pré-registrada.
- Leitura: o falso positivo do PNG está ligado ao trecho inicial da varredura, não à imagem inteira.
  A regra "só a janela de 100%" não foi avaliada nas estego e não é proposta como substituta.

## 2. Janelas de tamanho absoluto (`janelas_absolutas.md`)

- Com janelas acumuladas de 256 amostras (256, 512, ... até o total), o falso positivo aumentou:
  23/90 no PNG (25,6%; IC 95% de 17,7% a 35,4%) e 2/90 no JPEG (2,2%; 0,6% a 7,7%), contra 16/90 e
  0/90 na regra original. Com passos de 128 e 512 o padrão se repete (PNG 25/90 e 21/90; JPEG 4/90 e 2/90).
- Na taxa baixa, a sensibilidade do LSB passou de 31,1% para 68,9% com passo 256 (62,2% a 72,2% entre
  os três passos), e a da DCT ficou entre 30,0% e 43,3% (35,6% na regra original). Nessa taxa, o payload
  do LSB ocupa 1.048 pixels, menos que a primeira janela relativa (2.621 pixels).
- Com janelas absolutas, o McNemar passou a indicar, na taxa baixa, diferença significativa a favor
  de detectar mais o LSB nos três passos (passo 256: 32 pares só LSB × 6 só DCT; p ajustado por BH
  < 0,001). Nas taxas média e alta, nenhuma diferença foi significativa em nenhuma regra, como na
  regra original.
- Leitura: como o falso positivo também aumentou, o ganho de sensibilidade não indica um detector
  melhor. O resultado mostra que, na taxa baixa, a comparação LSB × DCT pelo limiar de 0,95 depende do
  tamanho das janelas, o que deve ser relatado como limitação.

## 3. Distorção da DCT pelo teorema de Parseval (`verif_parseval.md`)

- A tabela de quantização do canal Y foi a mesma nas 90 capas JPEG (tabela padrão da libjpeg escalada
  para QF 95), com passos q de 2 a 7 nas 26 posições da banda.
- O MSE previsto por Parseval a partir dos coeficientes alterados, Σ(Δ·q)²/262.144, acompanhou o MSE
  medido (r = 0,990; n = 270), mas ficou abaixo dele: a razão medido/previsto teve mediana de 1,21
  (intervalo interquartil de 1,10 a 1,37). Quando o modelo inclui o arredondamento dos pixels para
  inteiros e o corte em 0–255 da decodificação, a razão passa a 1,001 (r = 0,999997). O MSE esperado,
  0,5·Σq² nas posições usadas, também acompanhou o medido (r = 0,990; razão mediana de 1,19).
- Nas posições usadas, E[q²] teve mediana de 10,2, 12,3 e 12,9 nas taxas baixa, média e alta (q médio,
  √E[q²], de 3,2 a 3,6), contra uma razão MSE_DCT/MSE_LSB observada de 13,4, 14,3 e 14,5 (média
  geométrica por par). O passo de quantização explica a maior parte da diferença de distorção entre as
  técnicas; o restante corresponde ao arredondamento na decodificação.
- Na taxa alta, o PSNR da DCT foi 1,03 dB menor na textura alta do que na baixa. Nas imagens de textura
  alta, E[q²] é maior (mediana de 15,2 contra 10,1), e o modelo com arredondamento prevê 1,04 dB de
  diferença. Parseval sozinho prevê 1,79 dB, porque o arredondamento aumenta mais o MSE na textura baixa
  (razão medido/previsto de 1,29 contra 1,08). No LSB a diferença entre texturas é de 0,01 dB.

## 4. AUC com intervalo de confiança (`auc_bootstrap.md`)

- AUC do p_max (90 estego × 90 capas limpas do mesmo formato; mesma definição da Tabela 6, cujos
  valores foram reproduzidos), com IC 95% por bootstrap estratificado (2.000 reamostragens, semente
  fixa, percentil):
  - LSB: 0,618 [0,530; 0,698] na taxa baixa, 0,877 [0,821; 0,930] na média e 0,893 [0,839; 0,941] na alta;
  - DCT: 0,951 [0,911; 0,981], 0,999 [0,997; 1,000] e 0,9996 [0,999; 1,000].
- Os intervalos de LSB e DCT não se sobrepõem em nenhuma taxa. Isso é coerente com uma separação maior
  entre estego e capas limpas na DCT, mas não é um teste pareado formal e não estava previsto na
  metodologia; complementa, sem substituir, o McNemar.
- Com janelas absolutas (passo 256), a AUC do LSB subiu na taxa baixa (0,770 [0,690; 0,838]) e ficou em
  0,860 e 0,874 nas taxas média e alta; a da DCT ficou em 0,945, 0,992 e 0,995. Os intervalos continuam
  sem sobreposição nas três taxas e nos três passos.
- A AUC e o McNemar com janelas absolutas apontam em direções diferentes na taxa baixa porque o McNemar
  compara só as estego no limiar de 0,95, sem levar em conta as capas limpas, enquanto a AUC compara
  estego e capas limpas em todos os limiares.
- Com AUC perto de 1 (DCT nas taxas média e alta), o limite superior do IC fica em 1 e o intervalo por
  percentil é pouco informativo.

## 5. Histograma dos coeficientes da DCT, objetivo (e) (`histograma_dct.md`, `histograma_dct.png`)

- Nas posições efetivamente usadas pela inserção (as n primeiras posições elegíveis), a assimetria dos
  pares 2k/2k+1, A = Σ|h(2k) − h(2k+1)| / Σ(h(2k) + h(2k+1)), caiu em mediana de 0,498 para 0,064 na taxa
  baixa, de 0,365 para 0,027 na média e de 0,329 para 0,021 na alta, com redução em 89, 90 e 90 das 90
  imagens (Wilcoxon pareado, p ajustado < 0,001).
- Em todas as posições elegíveis, a redução mediana de A foi de 4,2%, 24,6% e 44,0%: o payload ocupa só
  as primeiras posições, e na taxa baixa o histograma global quase não muda.
- Esse equilíbrio dos pares é o efeito típico do Jsteg e é o mesmo que o qui-quadrado explora. A análise
  é descritiva e não constitui um detector adicional.
