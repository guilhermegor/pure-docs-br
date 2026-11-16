<!-- readme-archetype: library -->
# pure-docs-br

<p align="center"><img src="https://raw.githubusercontent.com/guilhermegor/pure-docs-br/main/assets/logo.png" width="200" alt="pure-docs-br logo"></p>

[![Project Status: Active](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)
![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)
[![PyPI](https://img.shields.io/pypi/v/pure-docs-br.svg)](https://pypi.org/project/pure-docs-br/)
[![Downloads](https://img.shields.io/pepy/dt/pure-docs-br)](https://pepy.tech/projects/pure-docs-br)
[![Docs](https://img.shields.io/badge/docs-latest-blue.svg)](https://guilhermegor.github.io/pure-docs-br/)
[![Linting](https://img.shields.io/badge/linting-ruff_%7C_codespell-blue)](https://github.com/astral-sh/ruff)
[![Mypy](https://img.shields.io/badge/type--checked-mypy-blue)](https://mypy-lang.org)
![Test Coverage](https://raw.githubusercontent.com/guilhermegor/pure-docs-br/badges/coverage.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Open Issues](https://img.shields.io/github/issues/guilhermegor/pure-docs-br)
![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-darkgreen.svg)

<!-- slug: overview -->
## Visão geral

Validate, mask and unmask Brazilian document numbers (CPF, alphanumeric CNPJ)

<!-- optional section: delete it when the project has no feature list -->
<!-- slug: features -->
## Funcionalidades

- Valida CPF e CNPJ pelos dígitos verificadores, inclusive o CNPJ alfanumérico que passa a existir em 2026.
- Aplica e remove a máscara (`XXX.XXX.XXX-XX` e `XX.XXX.XXX/XXXX-XX`).
- Tolera texto sujo: pontuação, zeros à esquerda perdidos e a cauda `.0` de um número que virou `str` (por exemplo `"52998224725.0"`).
- Funções puras, sem I/O e sem dependências de execução.

<!-- slug: documentation -->
## Documentação

O site de documentação fica em https://guilhermegor.github.io/pure-docs-br/. Para servi-lo localmente, rode `bash bin/poe_exec.sh docs_serve`.

<!-- slug: getting-started -->
## Primeiros passos

O Python 3.11+ é o único pré-requisito; o `bin/venv.sh` instala o [Poetry](https://python-poetry.org/) quando ele estiver ausente.

<!-- slug: install -->
### Instalação

```bash
git clone https://github.com/guilhermegor/pure-docs-br.git
cd pure-docs-br
bash bin/venv.sh
bash bin/poe_exec.sh init
```

O `poe` vive dentro do virtualenv, então o `bin/venv.sh` o cria primeiro; em seguida o
`bin/poe_exec.sh` roda o `poe init` sem ativar nada.

<!-- slug: usage -->
### Uso

```bash
pip install pure-docs-br
```

Toda função recebe e devolve `str` (ou `bool`) e aceita o documento com ou sem máscara.

```python
from pure_docs_br import (
    is_valid_cnpj,
    is_valid_cpf,
    mask_cnpj,
    mask_cpf,
    unmask_cnpj,
    unmask_cpf,
)

mask_cpf("52998224725")  # "529.982.247-25"
unmask_cpf("529.982.247-25")  # "52998224725"
unmask_cpf("1234567")  # "00001234567", completa com zeros à esquerda
is_valid_cpf("529.982.247-25")  # True
is_valid_cpf("11111111111")  # False, dígitos repetidos

mask_cnpj("11222333000181")  # "11.222.333/0001-81"
mask_cnpj("12ABC34501DE35")  # "12.ABC.345/01DE-35"
unmask_cnpj("12.abc.345/01de-35")  # "12ABC34501DE35", maiúsculas
unmask_cnpj("11222333000181.0")  # "11222333000181", descarta a cauda ".0"
is_valid_cnpj("11.222.333/0001-81")  # True
is_valid_cnpj("12.ABC.345/01DE-35")  # True, formato alfanumérico
is_valid_cnpj("11222333000182")  # False, dígito verificador errado
```

### Entrada inválida

- Toda função exige `str`: qualquer outro tipo (`None`, `float`, `int`, inclusive o `NaN` de uma
  coluna do pandas) lança `TypeError`. Converta antes, por exemplo com `.astype(str)`, ou filtre
  os nulos.
- Dado um `str`, nenhuma função lança exceção. `is_valid_*` devolve `False` para texto vazio,
  com tamanho errado ou com dígito verificador errado, então uma linha ruim não interrompe a
  transformação de uma coluna inteira.
- `mask_*` devolve o valor sem máscara (o que `unmask_*` produz) quando ele não tem o tamanho do
  documento. Isso ocorre com texto vazio, com mais de 11 dígitos (CPF) ou 14 caracteres (CNPJ) e
  com CNPJ alfanumérico curto; um CPF ou CNPJ só de dígitos nunca é curto, pois `unmask_*` o
  completa com zeros.
- Entrada numérica curta é completada com zeros à esquerda (11 para CPF, 14 para CNPJ) antes de
  os dígitos verificadores serem testados, o mesmo preenchimento que `unmask_*` aplica. É
  intencional: recupera documentos guardados como número que perderam os zeros (Excel, pandas).
  Por consequência, `is_valid_cpf("191")` e `is_valid_cnpj("191")` devolvem `True`, pois `"191"`
  vira `00000000191`. Valores de um só dígito repetido continuam rejeitados: `"0"` vira
  `00000000000` e `is_valid_cpf("0")` é `False`.
- A cauda `.0` é descartada por `unmask_cpf` e `unmask_cnpj`. A notação científica
  (`"1.1222333000181e+13"`) não é tratada: converta o número para texto sem expoente antes.

O dígito verificador do CNPJ segue o cálculo de módulo 11 do
[Serpro](https://www.serpro.gov.br/menu/noticias/videos/calculodvcnpjalfanaumerico.pdf) e da
[Receita Federal](https://www.gov.br/receitafederal/pt-br/centrais-de-conteudo/publicacoes/perguntas-e-respostas/cnpj/cnpj-alfanumerico.pdf).

<!-- slug: project-structure -->
## Estrutura do projeto

```text
pure-docs-br/
├── .github/        workflows, CODEOWNERS e template de PR
├── .specs/         specs de funcionalidades e trackers de backlog
├── bin/            scripts de gate e utilitários
├── docs/           documentação publicada
├── src/            o pacote `pure_docs_br`
├── tests/
│   ├── unit/
│   └── integration/
├── pyproject.toml
└── poe_tasks.toml  pontos de entrada do task runner
```

<!-- slug: development -->
## Desenvolvimento

Depois do bootstrap descrito em Instalação, qualquer tarefa pode ser executada pelo script de
bootstrap: `bash bin/poe_exec.sh <task>`; e `bash bin/poe_exec.sh` sem tarefa lista todas elas.

```bash
bash bin/poe_exec.sh unit_tests
bash bin/poe_exec.sh integration_tests
```

Quando o deploy da documentação do primeiro release tiver criado a branch `gh-pages`, rode
`bash bin/poe_exec.sh enable_pages` uma vez: até que essa branch exista, o `init` deixa o Pages intocado.

<!-- slug: public-api -->
## API pública

A superfície pública é o que o `__init__.py` do pacote lista em `__all__`:
`__version__`, `is_valid_cnpj`, `is_valid_cpf`, `mask_cnpj`, `mask_cpf`, `unmask_cnpj` e
`unmask_cpf`.

### Garantia de API da 1.x

A partir da 1.0.0 vale o semver completo. Dentro da 1.x, esses nomes continuam importáveis da raiz
do pacote com a mesma assinatura e o mesmo comportamento documentado: remover ou alterar um deles
exige uma 2.0. Uma versão MINOR só acrescenta, e uma PATCH só corrige defeitos. Tudo sob
`pure_docs_br._internal` é privado e fica fora da garantia.

<!-- slug: publishing -->
## Publicação

Os lançamentos saem dos workflows de release em `.github/workflows/`; a tag do git é a versão.

O caminho até a 1.0.0, e o gate de lançamento que o protege, está em
[docs/releasing-1-0-0.md](docs/releasing-1-0-0.md).

<!-- slug: contributing -->
## Contribuindo

Veja o [CONTRIBUTING.md](CONTRIBUTING.md) para as regras de branch, commit e revisão.

<!-- slug: license -->
## Licença

Este projeto é licenciado sob MIT; veja [LICENSE](LICENSE).

<!-- slug: authors -->
## Autores

- guilhermegor — [GitHub](https://github.com/guilhermegor) | [LinkedIn](https://www.linkedin.com/in/guilhermegor)

<!-- slug: useful-links -->
## Links úteis

- [Repositório no GitHub](https://github.com/guilhermegor/pure-docs-br)
- [Issue Tracker](https://github.com/guilhermegor/pure-docs-br/issues)
- [Documentação](https://guilhermegor.github.io/pure-docs-br/)

---

<sub>Gerado a partir do template lib-minimal via [BlueprintX](https://github.com/guilhermegor/blueprintx).</sub>
<!-- add any project disclaimer inside the sub tag above; for a library wrapping a third party, e.g. "Unofficial, community library. Not affiliated with or endorsed by ORG_NAME." -->
