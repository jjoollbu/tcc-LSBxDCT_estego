# AUC do p_max com IC 95% por bootstrap estratificado

Fonte: `C:\Faculdade TCC\Resultados` (commit da coleta a8ef486) e `p_max_absoluto.csv`. Análise exploratória posterior à coleta.
AUC = P(p_estego > p_limpa) + 0,5·P(empate), 90 estego × 90 capas limpas do mesmo formato, por técnica e taxa (definição da Tabela 6). Bootstrap estratificado por classe, 2000 reamostragens, IC por percentil; semente: fluxo 5 da SeedSequence(2026). As duas classes são as mesmas 90 imagens; o bootstrap não usa esse pareamento.
Conferência com a Tabela 6 (2 casas): lsb_baixa ok, lsb_media ok, lsb_alta ok, dct_baixa ok, dct_media ok, dct_alta ok.

| Regra | Técnica | Taxa | AUC | IC 95% | Reamostragens com AUC = 1 |
|---|---|---|---|---|---|
| Original (janelas de 1%) | LSB | baixa | 0,618 | [0,530; 0,698] | 0,0% |
| Original (janelas de 1%) | LSB | media | 0,877 | [0,821; 0,930] | 0,0% |
| Original (janelas de 1%) | LSB | alta | 0,893 | [0,839; 0,941] | 0,0% |
| Original (janelas de 1%) | DCT | baixa | 0,951 | [0,911; 0,981] | 0,0% |
| Original (janelas de 1%) | DCT | media | 0,999 | [0,997; 1,000] | 16,1% |
| Original (janelas de 1%) | DCT | alta | 1,000 | [0,999; 1,000] | 39,8% |
| Absoluta, passo 128 | LSB | baixa | 0,769 | [0,699; 0,841] | 0,0% |
| Absoluta, passo 128 | LSB | media | 0,860 | [0,799; 0,914] | 0,0% |
| Absoluta, passo 128 | LSB | alta | 0,872 | [0,815; 0,922] | 0,0% |
| Absoluta, passo 128 | DCT | baixa | 0,939 | [0,894; 0,977] | 0,0% |
| Absoluta, passo 128 | DCT | media | 0,986 | [0,969; 0,999] | 1,6% |
| Absoluta, passo 128 | DCT | alta | 0,992 | [0,981; 0,999] | 1,6% |
| Absoluta, passo 256 | LSB | baixa | 0,770 | [0,690; 0,838] | 0,0% |
| Absoluta, passo 256 | LSB | media | 0,860 | [0,800; 0,914] | 0,0% |
| Absoluta, passo 256 | LSB | alta | 0,874 | [0,814; 0,925] | 0,0% |
| Absoluta, passo 256 | DCT | baixa | 0,945 | [0,905; 0,979] | 0,0% |
| Absoluta, passo 256 | DCT | media | 0,992 | [0,978; 1,000] | 7,4% |
| Absoluta, passo 256 | DCT | alta | 0,995 | [0,987; 1,000] | 6,3% |
| Absoluta, passo 512 | LSB | baixa | 0,769 | [0,692; 0,841] | 0,0% |
| Absoluta, passo 512 | LSB | media | 0,862 | [0,804; 0,917] | 0,0% |
| Absoluta, passo 512 | LSB | alta | 0,877 | [0,822; 0,929] | 0,0% |
| Absoluta, passo 512 | DCT | baixa | 0,950 | [0,911; 0,982] | 0,0% |
| Absoluta, passo 512 | DCT | media | 0,991 | [0,977; 1,000] | 6,0% |
| Absoluta, passo 512 | DCT | alta | 0,995 | [0,986; 1,000] | 7,5% |

## Leitura

- Regra original: LSB baixa 0,618 [0,530; 0,698], media 0,877 [0,821; 0,930], alta 0,893 [0,839; 0,941]; DCT baixa 0,951 [0,911; 0,981], media 0,999 [0,997; 1,000], alta 1,000 [0,999; 1,000].
- Os IC de LSB e DCT não se sobrepõem na taxa baixa; não se sobrepõem na taxa media; não se sobrepõem na taxa alta. IC sem sobreposição não é um teste formal da diferença; a comparação pareada pré-registrada é o McNemar.
- Janelas absolutas (passo 256): LSB baixa 0,770 [0,690; 0,838], media 0,860 [0,800; 0,914], alta 0,874 [0,814; 0,925]; DCT baixa 0,945 [0,905; 0,979], media 0,992 [0,978; 1,000], alta 0,995 [0,987; 1,000].
- Com AUC perto de 1 (DCT, taxas média e alta), parte das reamostragens dá AUC = 1 (16,1% e 39,8% na regra original) e o limite superior do IC fica em 1; o IC por percentil é pouco informativo nesse extremo.

