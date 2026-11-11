# Diário de decisões — TCC stegware (LSB × DCT)

Registro das decisões da Metodologia e de todo desvio posterior. Regra: qualquer mudança
(plano B acionado, ajuste do piloto) é registrada aqui **antes** de ser aplicada.
Em caso de conflito com os arquivos 04, 05 e 08, vale este diário.

---

## Decisões aprovadas na reunião de travamento (T0.1)

## D-01 — LSB sequencial
- Data: 06/10/2026 · Participantes: Jonmar, Oséias, Osmar, Luiz, Ana
- Decisão: inserção sequencial, do primeiro pixel em diante, linha a linha
- Justificativa: o qui-quadrado (teste principal) foi criado para inserção sequencial
- Alternativas descartadas: pseudoaleatória (exigiria RS/SPA, que ficam como extensão)
- Onde aparece no texto: 3.3.1

## D-02 — LSB por substituição (replacement)
- Data: 06/10/2026 · Participantes: Jonmar, Oséias, Osmar, Luiz, Ana
- Decisão: substituir o último bit do pixel; 1 bit por pixel
- Justificativa: a substituição equilibra os pares de valores, que é o que o qui-quadrado mede
- Alternativas descartadas: LSB matching (anularia o teste principal; vira trabalho futuro); 2 a 4 bits por pixel
- Onde aparece no texto: 3.3.1

## D-03 — DCT com jpeglib e lógica de embutimento própria
- Data: 06/10/2026 · Participantes: Jonmar, Oséias, Osmar, Luiz, Ana
- Decisão: jpeglib lê e grava os coeficientes quantizados sem recomprimir; a equipe escreve só esconder/extrair
- Justificativa: não reimplementa a transformada e evita a recompressão que apagaria bits
- Alternativas descartadas: reimplementar a DCT; voltar a pixels e salvar de novo em JPEG (como na ferramenta de El_Rahman, 2018)
- Plano B: jpegio; em último caso, Python 3.11
- Onde aparece no texto: 3.3.2

## D-04 — Base BOSSBase 1.01, tons de cinza
- Data: 06/10/2026 · Participantes: Jonmar, Oséias, Osmar, Luiz, Ana
- Decisão: BOSSBase 1.01 (10.000 imagens, cinza, sem compressão); imagens fora do Git, com script de download e manifest com SHA-256
- Justificativa: base de referência da esteganálise; uso acadêmico; mesma imagem vira PNG e JPEG sem herdar perdas
- Alternativas descartadas: StegoAppDB (recomendada no Parecer; feita para identificar aplicativos, tamanhos variados, JPEG já comprimido); ALASKA2 (já em JPEG); USC-SIPI (poucas imagens, licenças mistas); RGB
- Plano B: BOWS2
- Onde aparece no texto: 3.2.1 (e 3.7 para a limitação de cor)

## D-05 — 512×512 pixels, 8 bits, sem redimensionar
- Data: 06/10/2026 · Participantes: Jonmar, Oséias, Osmar, Luiz, Ana
- Decisão: formato nativo da base; redimensionar é proibido
- Justificativa: 4.096 blocos 8×8 exatos; no teste, imagem redimensionada deu p = 1,00 sem nada escondido
- Alternativas descartadas: redimensionar
- Onde aparece no texto: 3.2.1

## D-06 — Textura pela magnitude média do gradiente de Sobel
- Data: 06/10/2026 · Participantes: Jonmar, Oséias, Osmar, Luiz, Ana
- Decisão: gradiente médio das 10.000 imagens; categorias = quintis 1 (baixa), 3 (média) e 5 (alta)
- Justificativa: mede bordas e textura, que é o que disfarça alterações; pular os quintis 2 e 4 cria margem entre categorias
- Alternativas descartadas: entropia (ignora a organização espacial dos pixels)
- Onde aparece no texto: 3.2.1

## D-07 — Fator de qualidade JPEG 95
- Data: 06/10/2026 · Participantes: Jonmar, Oséias, Osmar, Luiz, Ana
- Decisão: QF 95, tabelas padrão, um canal
- Justificativa: com QF 75 a taxa média não cabe e com QF 90 a taxa alta não cabe em imagens lisas (teste de viabilidade)
- Alternativas descartadas: QF 75; QF 90
- Onde aparece no texto: 3.2.1

## D-08 — Payloads de bytes pseudoaleatórios
- Data: 06/10/2026 · Participantes: Jonmar, Oséias, Osmar, Luiz, Ana
- Decisão: PCG64 do NumPy, seed mestra 2026, três arquivos fixos; tamanho informado ao extrator, sem cabeçalho
- Justificativa: alta entropia, como carga cifrada; pior caso para a detecção
- Alternativas descartadas: arquivo "dummy" de baixa entropia; cabeçalho de comprimento (somaria bits)
- Onde aparece no texto: 3.2.2

## D-09 — Taxas de inserção 0,004 · 0,03 · 0,06 bpp
- Data: 06/10/2026 · Participantes: Jonmar, Oséias, Osmar, Luiz, Ana
- Decisão: 131 · 983 · 1.966 bytes (0,4% · 3% · 6% da capacidade LSB), iguais para as duas técnicas
- Justificativa: atravessam o limiar de 0,005 bpp (Fridrich et al., 2001) e a zona de ~3% (Dumitrescu et al., 2003); DCT também reporta % da capacidade DCT e bpnzAC
- Alternativas descartadas: 1% / 10% / 50–70%; 0,10 bpp (não cabe no DCT das imagens lisas)
- Plano B: taxa alta 0,05 bpp (1.638 bytes) se faltarem imagens elegíveis
- Onde aparece no texto: 3.4.2

## D-10 — 30 imagens por categoria, com filtro de capacidade
- Data: 06/10/2026 · Participantes: Jonmar, Oséias, Osmar, Luiz, Ana
- Decisão: 30 por categoria (90 no experimento) + 10 por categoria para o piloto; elegível se capacidade DCT ≥ 17.301 bits
- Justificativa: a imagem é a unidade estatística; 90 pares detectam d ≈ 0,30 com ~80% de poder; custo de tempo baixo
- Alternativas descartadas: menos imagens
- Onde aparece no texto: 3.2.1 e 3.4.3

## D-11 — 30 repetições medidas + 5 de aquecimento
- Data: 06/10/2026 · Participantes: Jonmar, Oséias, Osmar, Luiz, Ana
- Decisão: cada repetição mede um bloco de 100 chamadas; a observação é a mediana das 30
- Justificativa: topo da faixa 20–30 de Kalibera e Jones (2013); blocos tiram o LSB da zona de ruído do cronômetro
- Alternativas descartadas: mínimo 5 / recomendado 10 (arquivo 04)
- Plano B (R-05): 1º repetições 30 → 20; 2º imagens 30 → 20 por categoria
- Onde aparece no texto: 3.4.3

## D-12 — Detectado se p ≥ 0,95 no qui-quadrado
- Data: 06/10/2026 · Participantes: Jonmar, Oséias, Osmar, Luiz, Ana
- Decisão: estatística = maior p-valor entre janelas acumuladas de 1% a 100%; detectado se p ≥ 0,95
- Justificativa: neste teste p alto indica pares equilibrados, isto é, esteganografia
- Alternativas descartadas: p < 0,05 (marcaria todas as capas limpas)
- Calibração pré-registrada: mais de 3 de 30 FP no piloto → limiar 0,99 (único ajuste permitido)
- Onde aparece no texto: 3.5.3

## D-13 — Recuperação por SHA-256 exato + BER
- Data: 06/10/2026 · Participantes: Jonmar, Oséias, Osmar, Luiz, Ana
- Decisão: acerto exato (sim/não) e taxa de erro de bits
- Justificativa: um critério binário e um contínuo
- Alternativas descartadas: só um dos dois
- Onde aparece no texto: 3.5.3

## D-14 — Outliers por 1,5×IQR
- Data: 06/10/2026 · Participantes: Jonmar, Oséias, Osmar, Luiz, Ana
- Decisão: dentro de cada combinação; marcar em coluna do CSV; excluir só com causa técnica registrada
- Justificativa: regra a priori; nada é apagado em silêncio
- Alternativas descartadas: exclusão automática
- Onde aparece no texto: 3.6

## D-15 — α = 0,05 com Benjamini-Hochberg por objetivo
- Data: 06/10/2026 · Participantes: Jonmar, Oséias, Osmar, Luiz, Ana
- Decisão: correção dentro de cada família: custo (c), qualidade (d), detecção (e)
- Justificativa: muitas comparações em estudo exploratório; controla a taxa de falsas descobertas
- Alternativas descartadas: Bonferroni (esconderia diferenças reais); sem correção
- Onde aparece no texto: 3.6

## D-16 — A imagem é a unidade de análise
- Data: 06/10/2026 · Participantes: Jonmar, Oséias, Osmar, Luiz, Ana
- Decisão: métricas determinísticas calculadas uma vez por combinação; só tempo, CPU e memória são repetidos
- Justificativa: evita pseudorreplicação
- Alternativas descartadas: tratar repetições como amostras
- Onde aparece no texto: 3.4.3

## D-17 — Testes pareados
- Data: 06/10/2026 · Participantes: Jonmar, Oséias, Osmar, Luiz, Ana
- Decisão: Shapiro-Wilk nas diferenças → t pareado (d) ou Wilcoxon (r); McNemar exato para detecção; Kruskal-Wallis para textura
- Justificativa: a mesma imagem passa pelas duas técnicas
- Alternativas descartadas: Welch e Mann-Whitney (independentes)
- Onde aparece no texto: 3.6

## D-18 — Qui-quadrado na ordem do algoritmo
- Data: 06/10/2026 · Participantes: Jonmar, Oséias, Osmar, Luiz, Ana
- Decisão: o analista lê pixels/coeficientes na mesma ordem usada para esconder
- Justificativa: princípio de Kerckhoffs; análise informada nas duas técnicas mantém a comparação justa
- Alternativas descartadas: análise cega de todos os coeficientes AC no DCT
- Onde aparece no texto: 3.5.3

## D-19 — Referência da qualidade no DCT
- Data: 06/10/2026 · Participantes: Jonmar, Oséias, Osmar, Luiz, Ana
- Decisão: capa JPEG × estego JPEG, ambas decodificadas; LSB: capa PNG × estego PNG
- Justificativa: separa o efeito de esconder do efeito da compressão
- Alternativas descartadas: comparar com a imagem original sem compressão
- Onde aparece no texto: 3.5.2

## D-20 — Máquina de medição
- Data: 06/10/2026 · Participantes: Jonmar, Oséias, Osmar, Luiz, Ana
- Decisão: uma única VM local e dedicada (Ubuntu 24.04 LTS, vCPUs e RAM fixas), 1 thread, sem rede
- Justificativa: tempo e CPU só são comparáveis no mesmo ambiente; a razão DCT/LSB vale em máquina física ou virtual
- Alternativas descartadas: VMs de nuvem compartilhadas ou burstable
- Plano B: máquina física, repetindo o piloto
- Onde aparece no texto: 3.2.3 (e 3.7)

---

## Registros de execução
(preencher conforme as tarefas avançam)

- Configuração da VM (T0.4): hospedeiro ___, hipervisor ___, vCPUs ___, RAM ___
- Licença da BOSSBase (T1.1): texto, endereço e data do download ___
- SHA-256 dos payloads (T1.2): baixa cb6e98cb… · media ff5b3217… · alta d0b3d6a8… (completos em "Payloads gerados (T1.2)")
- Revisão de inércia dos payloads (T1.3): ___
- Elegíveis por quintil (T1.4): Q1 799 de 2.000 · Q3 1.994 de 2.000 · Q5 2.000 de 2.000 (detalhes em "Seleção das imagens (T1.4)")
- Citações faltantes no referencial (T1.17): ___
- Piloto (T2.1): tempo ___, estimativa do experimento ___, mediana do CV ___, steal time ___
- Limiar final do detector (T2.2): ___
- Tag protocolo-v1 (T3.4): data ___, commit ___
- Experimento (T4.2): início ___, fim ___, interrupções ___
- Tag dados-v1 e backup (T4.4): SHA-256 do backup ___

## Payloads gerados (T1.2)
- Data: 11/10/2026 · Seed mestra: 2026 (fluxo RNG_PAYLOADS) · Gerador: PCG64
- payload_baixa.bin · 131 bytes · SHA-256: cb6e98cb149f6485a1fe164cebc2f2b685d1d731b1a6898105a02252cea41774
- payload_media.bin · 983 bytes · SHA-256: ff5b3217d621c6dcea8b543e24d60c7fceaacc1500e4036f10b528e7dca19d03
- payload_alta.bin  · 1.966 bytes · SHA-256: d0b3d6a8c88e7a575ba0ae7d992dfb4d5cb880f9401865bfb74bba689c3bd462
- Observação: se a T1.4 acionar o plano B de capacidade (taxa alta 0,05 bpp), só o
  payload_alta é refeito com 1.638 bytes; baixa e média não mudam (são gerados antes)

## Seleção das imagens (T1.4)
- Data: 11/10/2026 · Seed mestra: 2026 (fluxo RNG_SORTEIO) · Script: scripts/selecionar_imagens.py
- Base: 10.000 imagens .pgm 512×512 da BOSSBase 1.01; filtro de capacidade ≥ 17.301 bits (110% da taxa alta)
- Saída do script:
  - quintil 1: 799 elegíveis de 2000
  - quintil 3: 1994 elegíveis de 2000
  - quintil 5: 2000 elegíveis de 2000
- Plano B (taxa alta 0,05 bpp) não foi necessário: o menor quintil tem 799 elegíveis (mínimo 40)
- selecao.csv: 120 linhas, 40 por categoria (30 experimento + 10 piloto), ids sem repetição
- SHA-256 (arquivos com fim de linha LF): selecao.csv f39e72f26f6f762b8aaf396ea4826036e10165713b03d21e698e3867ead9ef23 ·
  todas_imagens.csv d64d81eb6711939116c2daea9af3a0396c86cae40554a60a7396aea2211a6449
- Reprodutibilidade: segunda execução gerou selecao.csv idêntico byte a byte
- Ambiente: mesmo do DESVIO-01 (fora da VM), numpy 2.5.4, jpeglib 1.0.2, pandas 3.0.6, scikit-image 0.26.0
- Observação: o quintil 1 (textura baixa) perde 60% das imagens no filtro de capacidade
  (mediana 15.061 bits, abaixo do mínimo); a categoria "baixa" representa a parte mais
  texturizada desse quintil, o que deve ser citado como limitação no texto

## Capas e manifest (T1.5)
- Data: 11/10/2026 · Script: scripts/preparar_capas.py
- 120 PNG (compress_level 6) em dataset/capas/png/ e 120 JPEG (QF 95, jpeglib) em dataset/capas/jpeg/ (fora do Git)
- Conferido: PNG idêntico pixel a pixel ao .pgm original; SHA-256 de .pgm, PNG e JPEG batem com o manifest
- manifest.csv (LF): 120 linhas, sem campos vazios · SHA-256 07fb82c56ddd4520667bb24d224a8e1e8335ef96128c431715943c31b215bb1b
- Reprodutibilidade: segunda execução gerou manifest.csv idêntico

## Reanálise de sensibilidade ao limiar 0,99 (D-12)
- Data: 11/11/2026 · Responsável: Jonmar · Registro posterior à execução do experimento
- Motivo: a banca apontou 17,8% de falsos positivos (16 de 90) nas capas PNG limpas com o limiar
  0,95; a D-12 pré-registra 0,99 como único ajuste permitido. Objetivo: medir o efeito desse limiar
  sobre FP, FN e o teste principal sem refazer a coleta
- Gatilho da D-12 no piloto (resultados/piloto/limpas.csv): PNG 8 de 30 FP com 0,95 (acima de 3);
  com 0,99 ainda seriam 6 de 30. JPEG 0 de 30 nos dois limiares
- Método: só reclassificação. O p_max contínuo já gravado pela coleta é comparado com cada limiar
  (detectado/FP se p_max ≥ limiar, regra da D-12). Nada foi re-medido (tempo, CPU, memória e
  qualidade não dependem do limiar), nenhuma imagem foi aberta e o p_max não foi recalculado, então
  seed e ordem de janelas (D-18) são as da coleta. IC de Wilson, McNemar exato e BH na família de
  detecção vêm de src/estatistica.py, como em analise.py
- Script: scripts/reanalise_limiar.py (recusa gravar em resultados/experimento/)
- Fonte: resultados.csv (540 linhas) e limpas.csv (180 linhas) da coleta, commit a8ef486, fora do
  Git (C:\Faculdade TCC\Resultados; tag dados-v1 ainda não criada)
  - SHA-256 resultados.csv 12da2baf74be36774113af828197238d6f27df42147fdc3ac6c27a077f980022
  - SHA-256 limpas.csv 67b4112daf792b855f3c5a219263fe032b75b17b94a1c623c629bc18b7b4d3d4
  - Nenhum p_max nan nas duas tabelas
- Saída: resultados/experimento_lim099/ (tabela_fp/fn/deteccao_lim099.csv, comparativo_limiar_lim099.csv/.md,
  comparativo_mcnemar_lim099.csv, proveniencia_lim099.json); cada tabela traz os dois limiares
- Conferência: com 0,95 a reanálise reproduz exatamente tabela_fn.csv, tabela_fp.csv e
  tabela_deteccao.csv da coleta
- Ambiente: fora da VM (como no DESVIO-01), Windows 10, Python 3.12.3, numpy 2.5.4, pandas 3.0.6,
  scipy 1.18.1, statsmodels 0.15.0
- Resultado — capas limpas (FP, IC 95% de Wilson):
  - PNG: 16/90 = 17,8% [11,2%; 26,9%] → 12/90 = 13,3% [7,8%; 21,9%]
  - JPEG: 0/90 = 0,0% [0,0%; 4,1%] nos dois limiares
  - Das 16 capas PNG marcadas com 0,95, 10 têm p_max ≥ 0,999 e 2 chegam a 1,000; 9 são de textura
    alta, 6 de média e 1 de baixa
- Resultado — estego (sensibilidade 0,95 → 0,99):
  - PNG/LSB: baixa 31,1% → 21,1% · média 82,2% → 65,6% · alta 83,3% → 72,2% · agregado 65,6% → 53,0%
  - JPEG/DCT: baixa 35,6% → 10,0% · média 86,7% → 62,2% · alta 93,3% → 76,7% · agregado 71,9% → 49,6%
  - Especificidade: PNG 82,2% → 86,7%; JPEG 100% nos dois
- Resultado — McNemar LSB × DCT (pares discordantes só LSB × só DCT; p ajustado por BH):
  - 0,95: baixa 9 × 13 (p_BH 0,557) · média 11 × 15 (0,557) · alta 5 × 14 (0,191)
  - 0,99: baixa 17 × 7 (0,192) · média 22 × 19 (0,755) · alta 15 × 19 (0,755)
- Conclusão: o 0,99 não leva o FP em PNG a um nível aceitável (o limite inferior do IC segue acima
  de 5%) e o FP restante não se resolve com limiar, pois várias capas limpas têm p_max ≈ 1. O custo é
  de 12,6 p.p. de sensibilidade no PNG e de 22,2 p.p. no JPEG, que não tinha FP a reduzir. Nenhuma
  diferença LSB × DCT é significativa em nenhum dos limiares; a direção pontual muda (com 0,95 a DCT
  é a mais detectada nas três taxas; com 0,99 o LSB passa à frente nas taxas baixa e média)
- Esta reanálise não define o limiar final da T2.2; ela é a análise de sensibilidade ao limiar

## Desvios
(modelo: data · o que o protocolo previa · o que foi observado · o que foi adotado · quem aprovou)

## DESVIO-01 — Payloads gerados fora da VM oficial
- Data: 11/10/2026 · Responsável: Jonmar
- Previsto: T1.2 executada na máquina oficial (VM Ubuntu 24.04)
- Feito: geração em outra máquina, com NumPy travado em `numpy==2.5.4` no requirements.txt
  (Python 3.12.3, sistema Windows 10 Pro 10.0.19045)
- Motivo: VM (T0.4) ainda não disponível; payloads não dependem da VM nem das imagens
- Garantia: a VM instala a mesma versão do NumPy; a T1.3 confirma a reprodução idêntica;
  os .bin versionados no Git e os SHA-256 acima são a referência definitiva
- Impacto: nenhum nas medições
