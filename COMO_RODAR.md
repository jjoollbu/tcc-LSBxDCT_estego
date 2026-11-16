# Como rodar o tcc-LSBxDCT_estego na sua máquina

Roteiro para os colegas da equipe rodarem o projeto do zero. São 3 níveis: o Nível 1
funciona na hora (não precisa de imagem nenhuma); os Níveis 2 e 3 precisam das imagens,
que ficam **fora do Git**.

---

## 0. Pré-requisitos

- **Git** instalado.
- **Python 3.12** — use exatamente a **3.12**, que é o padrão combinado da equipe.
  NÃO use 3.13 ou 3.14: o `jpeglib` e o `numpy` travados no projeto podem não ter versão
  pronta pra elas, e misturar versões quebra a venv.
  - Baixe em https://www.python.org/downloads/ e, na instalação, marque **"py launcher"**.
  - Confira o que você tem: `py --list` (tem que aparecer `-V:3.12`).

---

## 1. Clonar e preparar o ambiente  (TODO MUNDO faz)

No PowerShell / terminal:

```powershell
git clone https://github.com/jjoollbu/tcc-LSBxDCT_estego
cd tcc-LSBxDCT_estego
py -3.12 -m venv .venv
.venv\Scripts\activate
python --version          # tem que dizer 3.12.x
pip install -r requirements.txt
```

- No PowerShell, se `activate` der erro de permissão, use `.venv\Scripts\Activate.ps1`
  e, uma vez só, rode `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.
- Na **VM / Linux**: `python3.12 -m venv .venv` e depois `source .venv/bin/activate`.

O clone já traz os payloads (`dataset/payloads/*.bin`) e os CSVs (`selecao.csv`,
`manifest.csv`, `todas_imagens.csv`). Só as imagens é que não vêm.

---

## 2. Validar as técnicas  (NÃO precisa de nenhuma imagem)

```powershell
python -m pytest -q
```

**Resultado esperado: `13 passed`.** Esses testes (LSB e DCT: ida-e-volta, alteração
mínima, capacidade) usam uma imagem de exemplo embutida na biblioteca, então rodam em
qualquer máquina sem a BOSSBase. Se deu `13 passed`, seu ambiente está 100%.

---

## 3. Rodar com as imagens do experimento

As pastas `dataset/bossbase/` (10.000 `.pgm`) e `dataset/capas/` ficam fora do Git
(ver `.gitignore`). Escolha o caminho conforme o que você precisa:

### Caminho A — rápido (para a maioria)
Só quer rodar/olhar as 120 imagens selecionadas (round-trip, qualidade, visualização):

1. Peça ao Jonmar a pasta **`dataset/capas/`** (120 PNG + 120 JPEG — poucos MB).
2. Cole dentro de `dataset/capas/` no seu clone.
Pronto. As capas abrem em qualquer visualizador e os scripts que usam as capas já rodam.

### Caminho B — completo (reproduzir a seleção do zero)
Quer provar que o sorteio das imagens é reprodutível, ou refazer tudo:

1. Coloque a **BOSSBase 1.01** (10.000 arquivos `.pgm`, 512x512, tons de cinza) em
   `dataset/bossbase/`.
   - **Recomendado:** peça a cópia exata ao Jonmar — garante o mesmo SHA-256 do
     `manifest.csv`.
   - Alternativa: baixar a BOSSBase 1.01 oficial (projeto BOSS / espelho confiável).
2. Gere a seleção e as capas:
   ```powershell
   python scripts/selecionar_imagens.py
   python scripts/preparar_capas.py
   ```
3. O `selecao.csv` gerado deve sair **idêntico** ao que já está no repo — essa é a prova
   de reprodutibilidade (mesma seed 2026 + mesmas imagens + mesmo ambiente = mesmo sorteio).

---

## Teste manual de ida-e-volta (opcional)

Com uma imagem em `dataset/bossbase/` (ex.: `6073.pgm`), num Python interativo:

```python
import sys; sys.path.insert(0, "src")
import numpy as np, hashlib
from PIL import Image
from lsb import esconder_lsb, extrair_lsb

capa = np.array(Image.open("dataset/bossbase/6073.pgm"))
payload = open("dataset/payloads/payload_media.bin", "rb").read()
estego = esconder_lsb(capa, payload)
recuperado = extrair_lsb(estego, len(payload))
print("idêntico?", hashlib.sha256(recuperado).hexdigest() == hashlib.sha256(payload).hexdigest())
```

---

## Problemas comuns

- **`ModuleNotFoundError: numpy._core._multiarray_umath`** — a venv foi criada/misturada
  com outra versão de Python. Apague a pasta `.venv` e recrie com `py -3.12`:
  ```powershell
  deactivate
  Remove-Item -Recurse -Force .venv
  py -3.12 -m venv .venv
  .venv\Scripts\activate
  pip install -r requirements.txt
  ```
- **`jpeglib` não instala** — confirme que a venv está em Python 3.12 (`python --version`).
- **`python` abre a versão errada** — use sempre `py -3.12` para criar a venv.
- **pytest não dá 13 passed** — rode sempre a partir da **raiz** do repositório, com a venv ativa.

---

## Regra de ouro da equipe
Todo mundo na **mesma versão de Python (3.12)** e com o **mesmo `requirements.txt`**.
É isso que garante os mesmos números em todas as máquinas e na VM.
