# tcc-stegware

Comparação experimental entre LSB (domínio espacial, PNG) e DCT (domínio da frequência, JPEG QF 95)
na ocultação de artefatos simulados e inertes, em imagens da BOSSBase 1.01.

- Repositório: https://github.com/jjoollbu/tcc-LSBxDCT_estego
- Commit da coleta do experimento: `a8ef486` (a8ef486b9ca8c77c2e7f0efc53856d5527879d8f). Os dados
  da coleta (`resultados.csv`, 540 linhas; `limpas.csv`, 180 linhas) ficam fora do Git.
- Codificador das capas JPEG: jpeglib 1.0.2 (libjpeg), `jpeglib.from_spatial(img).write_spatial(arquivo, qt=95)`
  em `scripts/preparar_capas.py`, com a tabela de quantização padrão da libjpeg escalada para QF 95.
  A estego DCT é gravada com `write_dct`, sem recompressão.
- Reanálises de sensibilidade posteriores à coleta (nov/2026): `resultados/reanalise_pos_feedback/`
  (resumo em `RESUMO.md`). Os resultados pré-registrados continuam sendo os principais.

## Regras
- Todos os scripts rodam a partir da raiz do repositório: `python scripts/<nome>.py`.
- Todo código vai para o repositório com commit antes de qualquer medição.
- Nenhum número é digitado à mão: tudo sai dos CSVs gerados pelos scripts.
- Qualquer mudança em relação às decisões é registrada em `docs/diario-decisoes.md` antes de ser aplicada.
- As imagens (`dataset/bossbase/`, `dataset/capas/`) ficam fora do Git; o `dataset/manifest.csv` traz o SHA-256 de cada uma.

## Estrutura
- `src/` módulos das técnicas, métricas, detector, custo e estatística
- `scripts/` preparação do dataset, execução e análise
- `tests/` testes automáticos (`python -m pytest -q`)
- `dataset/` base, capas, payloads e manifest
- `resultados/` saídas do piloto e do experimento
- `docs/` diário de decisões