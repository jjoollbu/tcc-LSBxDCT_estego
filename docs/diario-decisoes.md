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
  - Das 16 capas PNG marcadas com 0,95, 10 têm p_max ≥ 0,999 e 3 têm p_max ≥ 0,99999 (máximo
    0,9999999542); nenhuma tem p_max = 1 exato; 9 são de textura alta, 6 de média e 1 de baixa
    (corrigido em 11/11/2026: o registro anterior dizia "2 chegam a 1,000", valor arredondado; ver
    seção "Análise do FP estrutural em PNG")
- Resultado — estego (sensibilidade 0,95 → 0,99):
  - PNG/LSB: baixa 31,1% → 21,1% · média 82,2% → 65,6% · alta 83,3% → 72,2% · agregado 65,6% → 53,0%
  - JPEG/DCT: baixa 35,6% → 10,0% · média 86,7% → 62,2% · alta 93,3% → 76,7% · agregado 71,9% → 49,6%
  - Especificidade: PNG 82,2% → 86,7%; JPEG 100% nos dois
- Resultado — McNemar LSB × DCT (pares discordantes só LSB × só DCT; p ajustado por BH):
  - 0,95: baixa 9 × 13 (p_BH 0,557) · média 11 × 15 (0,557) · alta 5 × 14 (0,191)
  - 0,99: baixa 17 × 7 (0,192) · média 22 × 19 (0,755) · alta 15 × 19 (0,755)
- Conclusão: o 0,99 não leva o FP em PNG a um nível aceitável (o limite inferior do IC segue acima
  de 5%), e o FP restante só cai a ≤ 5% com limiares colados em 1, que derrubam a detecção (ver
  seção "Análise do FP estrutural em PNG"; corrigido em 11/11/2026: o registro anterior atribuía isso
  a capas limpas com p_max ≈ 1, o que não se confirma com o valor exato). O custo do 0,99 é
  de 12,6 p.p. de sensibilidade no PNG e de 22,2 p.p. no JPEG, que não tinha FP a reduzir. Nenhuma
  diferença LSB × DCT é significativa em nenhum dos limiares; a direção pontual muda (com 0,95 a DCT
  é a mais detectada nas três taxas; com 0,99 o LSB passa à frente nas taxas baixa e média)
- Esta reanálise não define o limiar final da T2.2; ela é a análise de sensibilidade ao limiar

## Análise do FP estrutural em PNG
- Data: 11/11/2026 · Responsável: Jonmar · Registro posterior à execução do experimento
- Pergunta: o FP em PNG se resolve com algum limiar < 1 (problema de calibração) ou não (problema
  estrutural)?
- Método: só leitura do p_max já gravado (regra da D-12: FP/detectado se p_max ≥ L). Distribuição
  do p_max das capas limpas por faixa e por textura; FP nos limiares 0,95 · 0,99 · 0,999 · 0,9999 ·
  1,0 (estrito, p_max ≥ 1); menor limiar < 1 com FP ≤ 5% (pela taxa pontual e pelos dois limites
  do IC); detecção das estego nesses mesmos limiares. Nada foi re-medido e nenhuma imagem foi aberta.
  IC de Wilson de src/estatistica.py
- Script: scripts/fp_estrutural.py (recusa gravar em resultados/experimento/)
- Fonte: limpas.csv e resultados.csv da coleta (commit a8ef486), os mesmos SHA-256 da seção anterior
- Saída: resultados/experimento_lim099/ (fp_estrutural.csv, fp_estrutural.md,
  proveniencia_fp_estrutural.json)
- Conferência: com 0,95 e 0,99 a sensibilidade reproduz exatamente tabela_fn_lim099.csv
- Ambiente: Windows 10, Python 3.12.3, numpy 2.5.4, pandas 3.0.6, scipy 1.18.1, statsmodels 0.15.0
- Resultado — capas PNG limpas:
  - Nenhuma tem p_max = 1 exato; o máximo é 0,9999999542
  - Faixas: < 0,95: 74 · [0,95; 0,99): 4 · [0,99; 0,999): 2 · [0,999; 0,99999): 7 · ≥ 0,99999: 3
  - FP por limiar: 0,95 → 16/90 (17,8%) · 0,99 → 12 (13,3%) · 0,999 → 10 (11,1%) ·
    0,9999 → 6 (6,7%) · 1,0 estrito → 0
  - Menor limiar com FP ≤ 5%: L > 0,9999734 pela taxa pontual (até 4 FP); L > 0,9999999542 para o
    limite superior do IC ficar ≤ 5% (0 FP)
  - Textura com 0,95: baixa 1 · média 6 · alta 9 (de 30 cada)
- Resultado — JPEG limpas: 0 FP em todos os limiares; máximo 0,9286
- Resultado — detecção das estego (agregado das 3 taxas):
  - 0,95: FP PNG 17,8% · LSB 65,6% · DCT 71,9%
  - L = 0,9999867 (menor limiar concreto com FP PNG ≤ 5%): FP PNG 4,4% · LSB 17,4% · DCT 3,7%
  - L logo acima de 0,9999999542 (FP PNG 0): LSB 3,7% · DCT 0,0%
- Conclusão: em sentido estrito existe limiar < 1 que zera o FP, porque nenhuma capa limpa chega a
  p_max = 1. Mas esse limiar fica colado em 1, ajustado ao máximo desta amostra, e derruba a
  detecção: levar o FP do PNG a ≤ 5% custa 48,1 p.p. de sensibilidade no LSB. As notas das capas
  limpas e das estego se sobrepõem perto de 1, e por isso nenhum limiar separa as duas. O FP em PNG
  não é um problema de calibração do limiar. Ele se concentra nas texturas média e alta

## Reanálises pós-Feedback (nov/2026)
- Data: 15/11/2026 · Responsável: Jonmar · Registro posterior à execução do experimento
- Status: análises de sensibilidade feitas depois da coleta. Não alteram resultados.csv, limpas.csv
  nem src/quiquadrado.p_max; **os resultados pré-registrados (D-12, janelas de 1% a 100%, limiar
  0,95) continuam sendo os principais**
- Motivo: parecer externo sobre (1) as janelas de 1% do qui-quadrado, ligadas ao FP em PNG; (2) a
  distorção da DCT, que deveria ser explicada pelo teorema de Parseval e pelos passos de quantização;
  (3) a AUC exploratória da Tabela 6, apresentada sem intervalo de confiança; (4) o objetivo
  específico (e), que prevê a análise de histograma dos coeficientes DCT
- Fonte: resultados.csv e limpas.csv da coleta (commit a8ef486), os mesmos SHA-256 das seções
  anteriores (12da2baf… e 67b4112d…), lidos sem alteração
- Saída: resultados/reanalise_pos_feedback/ (CSV, .md e proveniencia_*.json por script; RESUMO.md
  com os números principais). Os scripts recusam gravar na pasta da coleta
- Scripts (funções comuns em scripts/reanalise_comum.py):
  - scripts/diag_fp_janelas.py: p de cada uma das 100 janelas nas 180 capas limpas; janela do
    máximo, p na janela de 100% e na de 1%; FP se só a janela de 100% fosse usada
  - scripts/reanalise_janelas_absolutas.py: nova função src/quiquadrado.p_max_absoluto (janelas
    acumuladas de 128, 256 ou 512 amostras até o total; p_max não foi alterada); sensibilidade, FP,
    McNemar exato pareado com BH e pares discordantes no formato de tabela_deteccao.csv
  - scripts/verif_parseval.py: MSE previsto Σ(Δ·q)²/262144 e esperado 0,5·Σq²/262144 com a tabela
    de quantização do Y de cada capa, contra o mse medido; E[q²] × razão MSE_DCT/MSE_LSB; textura
  - scripts/auc_bootstrap.py: AUC da Tabela 6 com IC 95% por bootstrap estratificado (2.000
    reamostragens, percentil, semente = 5º fluxo da SeedSequence(2026), independente dos 4 de
    sementes.py), também para p_max_absoluto
  - scripts/histograma_dct.py: histograma dos coeficientes elegíveis da banda (−20 a 20, sem 0 e 1)
    e assimetria dos pares 2k/2k+1, capa × estego por taxa; figura histograma_dct.png
- Preparação: dataset/capas/ não existia neste checkout. Os 120 .pgm sorteados foram copiados da
  BOSSBase local para dataset/bossbase/ (SHA-256 = sha256_original do manifest, 120/120) e as capas
  foram geradas com scripts/preparar_capas.py. JPEG: SHA-256 igual ao manifest (120/120) e ao
  sha256_capa de resultados.csv (90/90). PNG: SHA-256 igual ao manifest (120/120), mas diferente do
  sha256_capa de resultados.csv (0/90), porque os bytes da compressão zlib diferem entre o Windows e
  o Linux da coleta (também com Pillow 12.3.0); os pixels são idênticos ao .pgm. No manifest.csv
  regravado pelo script só a coluna gradiente mudou, a partir do 17º dígito (diferença máxima
  9,7e−17, formatação de float do pandas mais novo); o arquivo versionado foi restaurado.
  ordem_execucao.csv não existe neste checkout; nenhuma reanálise depende dele (as 540 combinações
  vêm de resultados.csv)
- Validação da regeneração (obrigatória antes de usar p_max_absoluto):
  - Estego idênticas bit a bit: DCT com o mesmo SHA-256 de resultados.csv (270/270); LSB com o mesmo
    MSE exato (270/270); mse da DCT recalculado (JPEG × JPEG decodificados) igual à coluna mse
  - p_max com a função original: 539/540 estego idênticos a resultados.csv e 540/540 até 1 ULP
    (diferença absoluta máxima 3,5e−18: LSB baixa 9333, 0,026055418872759122 na coleta ×
    0,026055418872759126); 179/180 capas limpas idênticas a limpas.csv e 180/180 até 1 ULP
    (máxima 1,1e−16: JPEG 9020, 0,928568206741158 × 0,9285682067411579). Nenhuma decisão muda em
    0,95 nem em 0,99; a regra original reproduz tabela_deteccao.csv
  - Critério aprovado pelo autor em 15/11/2026: aceitar igualdade exata ou diferença ≤ 1 ULP, com
    todas as decisões em 0,95 e 0,99 idênticas (o script para em qualquer outro caso). A diferença
    vem do chi2.sf na biblioteca matemática de cada sistema; um teste com numpy 2.2.6 e scipy 1.15.3
    no Windows reproduziu menos (510/540), então foi mantido o ambiente do requirements.txt
  - Ambiente da coleta: Linux-6.18.54.1-microsoft-standard-WSL2-x86_64-with-glibc2.35, Python
    3.10.12, numpy 2.2.6, scipy 1.15.3, pandas 2.3.3, statsmodels 0.15.0, jpeglib 1.0.2, Pillow 12.3.0
  - Ambiente das reanálises: Windows 10 (10.0.19045), Python 3.12.3, numpy 2.5.4, scipy 1.18.1,
    pandas 3.1.1, statsmodels 0.15.0, jpeglib 1.0.2, Pillow 12.3.0, matplotlib 3.11.2
- Resultado — janelas e FP em PNG: nos 16 FP o máximo saiu na janela de 1% em 8 casos, em ≤ 5% em
  12 e no máximo em 14%; a janela de 1% (2.621 pixels) já dá p ≥ 0,95 nas 16 e em nenhuma das 74 PNG
  sem FP. Só com a janela de 100%: 0/90 FP no PNG e 0/90 no JPEG
- Resultado — janelas absolutas (FP PNG · FP JPEG · sensibilidade LSB/DCT na taxa baixa):
  - Original: 16/90 · 0/90 · 31,1% / 35,6%
  - Passo 128: 25/90 · 4/90 · 72,2% / 43,3%
  - Passo 256: 23/90 · 2/90 · 68,9% / 40,0%
  - Passo 512: 21/90 · 2/90 · 62,2% / 30,0%
  - McNemar: na taxa baixa, LSB mais detectado nos três passos (passo 256: 32 × 6; p_BH < 0,001);
    nas taxas média e alta, nada significativo em nenhuma regra
- Resultado — Parseval: MSE medido/previsto com mediana 1,21 (r = 0,990); com arredondamento e corte
  dos pixels, 1,001 (r = 0,999997). E[q²] 10,2 · 12,3 · 12,9 contra razão MSE_DCT/MSE_LSB de
  13,4 · 14,3 · 14,5. Na taxa alta, PSNR da DCT 1,03 dB menor na textura alta (modelo: 1,04 dB)
- Resultado — AUC [IC 95%], regra original: LSB 0,618 [0,530; 0,698] · 0,877 [0,821; 0,930] ·
  0,893 [0,839; 0,941]; DCT 0,951 [0,911; 0,981] · 0,999 [0,997; 1,000] · 0,9996 [0,999; 1,000].
  IC de LSB e DCT sem sobreposição em todas as taxas e regras
- Resultado — histograma: assimetria dos pares nas posições usadas cai de 0,498/0,365/0,329 para
  0,064/0,027/0,021 (taxas baixa/média/alta; estego < capa em 89, 90 e 90 de 90)
- Conclusão: o FP do PNG está ligado às primeiras janelas, mas janelas absolutas pequenas não o
  resolvem (o FP aumenta nos dois formatos), e a comparação LSB × DCT na taxa baixa depende do
  tamanho das janelas; isso vai para as limitações. A distorção da DCT é explicada pelos passos de
  quantização (Parseval) mais o arredondamento na decodificação. Nada aqui substitui os resultados
  pré-registrados

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
