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

Valida, aplica e remove a máscara de documentos brasileiros

<!-- optional section: delete it when the project has no feature list -->
<!-- slug: features -->
## Funcionalidades

- Valida CPF e CNPJ pelos dígitos verificadores, inclusive o CNPJ alfanumérico que passa a existir em 2026.
- Valida o formato do CEP (8 dígitos; o CEP não tem dígito verificador).
- Valida o Título de Eleitor (12 dígitos, UF e dois dígitos verificadores).
- Valida o CNS (Cartão Nacional de Saúde, 15 dígitos, definitivo ou provisório, módulo 11).
- Aplica e remove a máscara (`XXX.XXX.XXX-XX`, `XX.XXX.XXX/XXXX-XX`, `XXXXX-XXX`, `XXXX XXXX XXXX` e `XXX XXXX XXXX XXXX`).
- Tolera texto sujo: pontuação, zeros à esquerda perdidos e a cauda `.0` de um número que virou `str` (por exemplo `"52998224725.0"`).
- Funções puras, sem I/O e sem dependências de execução.

<!-- slug: documentation -->
## Documentação

O site de documentação fica em https://guilhermegor.github.io/pure-docs-br/. Para servi-lo localmente, rode `poetry run poe docs_serve`.

<!-- slug: getting-started -->
## Primeiros passos

O Python 3.11+ é o único pré-requisito; o `bin/venv.sh` instala o [Poetry](https://python-poetry.org/) quando ele estiver ausente.

<!-- slug: install -->
### Instalação

```bash
git clone https://github.com/guilhermegor/pure-docs-br.git
cd pure-docs-br
bash bin/venv.sh
poetry run poe init
```

O `poe` vive dentro do virtualenv, então o `bin/venv.sh` o cria primeiro; em seguida o
`poetry run poe init` o executa sem ativar nada. Se o `poetry` não estiver no `PATH` (por exemplo
logo depois de o `bin/venv.sh` instalá-lo com `--user`), use `bash bin/poe_exec.sh init`, que
encontra o `poe` do venv sozinho.

<!-- slug: usage -->
### Uso

```bash
pip install pure-docs-br
```

Toda função recebe e devolve `str` (ou `bool`) e aceita o documento com ou sem máscara.

```python
from pure_docs_br import (
    is_valid_boleto_arrecadacao,
    is_valid_boleto_cobranca,
    is_valid_cep,
    is_valid_chave_acesso,
    is_valid_cnpj,
    is_valid_cns,
    is_valid_cpf,
    is_valid_inscricao_estadual,
    is_valid_pis_pasep,
    is_valid_placa,
    is_valid_processo_cnj,
    is_valid_titulo_eleitor,
    mask_boleto_arrecadacao,
    mask_boleto_cobranca,
    mask_cep,
    mask_chave_acesso,
    mask_cnpj,
    mask_cns,
    mask_cpf,
    mask_inscricao_estadual,
    mask_pis_pasep,
    mask_placa,
    mask_processo_cnj,
    mask_titulo_eleitor,
    unmask_boleto_arrecadacao,
    unmask_boleto_cobranca,
    unmask_cep,
    unmask_chave_acesso,
    unmask_cnpj,
    unmask_cns,
    unmask_cpf,
    unmask_inscricao_estadual,
    unmask_pis_pasep,
    unmask_placa,
    unmask_processo_cnj,
    unmask_titulo_eleitor,
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

mask_inscricao_estadual("110042490114", str_uf="SP")  # "110.042.490.114"
unmask_inscricao_estadual("110.042.490.114")  # "110042490114"
is_valid_inscricao_estadual("110.042.490.114", str_uf="SP")  # True
is_valid_inscricao_estadual("110042490114", str_uf="XX")  # False, UF desconhecida nunca lança

mask_cep("01001000")  # "01001-000"
unmask_cep("1001000.0")  # "01001000", restaura o zero à esquerda
is_valid_cep("01001-000")  # True
is_valid_cep("123456789")  # False, 9 dígitos

mask_titulo_eleitor("4356870906.0")  # "0043 5687 0906"
unmask_titulo_eleitor("0043 5687 0906")  # "004356870906"
is_valid_titulo_eleitor("0043 5687 09 06")  # True

mask_pis_pasep("12345678900.0")  # "123.45678.90-0"
unmask_pis_pasep("1234567890")  # "01234567890"
is_valid_pis_pasep("123.45678.90-0")  # True

mask_cns("100000000010002")  # "100 0000 0001 0002"
unmask_cns("100000000010002.0")  # "100000000010002"
is_valid_cns("100 0000 0001 0002")  # True

mask_placa("abc1234")  # "ABC-1234"
unmask_placa("abc-1234")  # "ABC1234"
is_valid_placa("ABC1D23")  # True, padrão Mercosul

mask_processo_cnj("00000018420208260001")  # "0000001-84.2020.8.26.0001"
unmask_processo_cnj("0000001-84.2020.8.26.0001")  # "00000018420208260001"
is_valid_processo_cnj("0000001-84.2020.8.26.0001")  # True

mask_chave_acesso(
    "35231111222333000181550010000000011123456789"
)  # "3523 1111 2223 3300 0181 5500 1000 0000 0111 2345 6789"
unmask_chave_acesso(
    "NFe35231111222333000181550010000000011123456789"
)  # "35231111222333000181550010000000011123456789"
is_valid_chave_acesso("35231111222333000181550010000000011123456789")  # True

mask_boleto_cobranca(
    "00190000090000000000000000000018199990000012345"
)  # "00190.00009 00000.000000 00000.000018 1 99990000012345"
unmask_boleto_cobranca(
    "00190.00009 00000.000000 00000.000018 1 99990000012345"
)  # "00190000090000000000000000000018199990000012345"
is_valid_boleto_cobranca("00191999900000123450000000000000000000000001")  # True, código de barras

mask_boleto_arrecadacao(
    "816800000019234500000000000000000000000000000000"
)  # "81680000001-9 23450000000-0 00000000000-0 00000000000-0"
unmask_boleto_arrecadacao(
    "81680000001-9 23450000000-0 00000000000-0 00000000000-0"
)  # "816800000019234500000000000000000000000000000000"
is_valid_boleto_arrecadacao(
    "81680000001234500000000000000000000000000000"
)  # True, código de barras
```

### CEP

A validação do CEP é só de formato (8 dígitos, `XXXXX-XXX`): o CEP não tem dígito verificador, e a
biblioteca **não consulta a base dos Correios**, então não confirma que o CEP existe. Entrada
numérica curta é completada com zeros à esquerda até 8, por isso `is_valid_cep("1001000")` é
`True`. O `00000-000` passa na checagem de formato. `mask_cep` devolve o valor sem máscara quando
ele não tem 8 dígitos.

### Inscrição Estadual

A IE depende da UF (`str_uf`, obrigatório e nomeado) e as 27 UFs são suportadas. Uma UF fora das 27
siglas devolve `False` em vez de lançar, então uma UF digitada errado faz toda IE parecer inválida.
`ISENTO` e o produtor rural de SP (`P-...`) devolvem `False`.

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

Depois do bootstrap descrito em Instalação, qualquer tarefa pode ser executada com
`poetry run poe <task>`; e `poetry run poe` sem tarefa lista todas elas.

```bash
poetry run poe unit_tests
poetry run poe integration_tests
```

Quando o deploy da documentação do primeiro release tiver criado a branch `gh-pages`, rode
`poetry run poe enable_pages` uma vez: até que essa branch exista, o `init` deixa o Pages intocado.

### `poetry run poe` ou `bash bin/poe_exec.sh`?

Os dois rodam a mesma tarefa do mesmo `poe` do venv. Use `poetry run poe`, o comando que a
comunidade conhece; o `bin/poe_exec.sh` cobre os casos em que ele não basta:

| Situação | `poetry run poe` | `bash bin/poe_exec.sh` |
|---|---|---|
| Máquina comum, `poetry` no `PATH` | funciona | funciona |
| `poetry` fora do `PATH` (ex.: recém-instalado com `--user`) | falha: `poetry: command not found` | funciona: acha `.venv/bin/poe` (ou `.venv/Scripts/poe.exe` no Windows) sem o `poetry` |
| Rede corporativa com inspeção TLS (`bin/corporate_ca.pem` presente) | tarefas que baixam algo podem falhar com erro de certificado | funciona: monta o bundle de CAs e o exporta antes de rodar a tarefa |
| `poe` não instalado | erro genérico do Poetry | lista as formas de instalar (`bin/venv.sh`, `pipx`, plugin do Poetry) |

<!-- slug: public-api -->
## API pública

A superfície pública é o que o `__init__.py` do pacote lista em `__all__`:
`__version__`, `is_valid_boleto_arrecadacao`, `is_valid_boleto_cobranca`, `is_valid_cep`, `is_valid_chave_acesso`, `is_valid_cnpj`, `is_valid_cns`, `is_valid_cpf`,
`is_valid_inscricao_estadual`, `is_valid_pis_pasep`, `is_valid_placa`, `is_valid_processo_cnj`, `is_valid_titulo_eleitor`,
`mask_boleto_arrecadacao`, `mask_boleto_cobranca`, `mask_cep`, `mask_chave_acesso`, `mask_cnpj`, `mask_cns`, `mask_cpf`, `mask_inscricao_estadual`, `mask_pis_pasep`, `mask_placa`,
`mask_processo_cnj`, `mask_titulo_eleitor`, `unmask_boleto_arrecadacao`, `unmask_boleto_cobranca`, `unmask_cep`, `unmask_chave_acesso`, `unmask_cnpj`, `unmask_cns`,
`unmask_cpf`, `unmask_inscricao_estadual`, `unmask_pis_pasep`, `unmask_placa`, `unmask_processo_cnj` e
`unmask_titulo_eleitor`.

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
