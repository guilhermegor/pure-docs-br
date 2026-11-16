# **Uso**

Exemplos de instalação e de uso desta biblioteca.

> **Veja também:** [Referência da API](api/index.md)

---

## Instalação

```bash
pip install pure-docs-br
```

Ou com Poetry:

```bash
poetry add pure-docs-br
```

A biblioteca não tem dependências de execução.

---

## CPF

O CPF (Cadastro de Pessoas Físicas) tem 11 dígitos, dois deles de verificação.

Formatos aceitos: com máscara (`529.982.247-25`), sem máscara (`52998224725`) e o artefato de
float (`52998224725.0`, comum em colunas do pandas lidas como número). Sempre uma `str`: um
`float` ou `None` levanta `TypeError`.

```python
from pure_docs_br import is_valid_cpf, mask_cpf, unmask_cpf

is_valid_cpf("529.982.247-25")  # True
is_valid_cpf("52998224725.0")  # True
mask_cpf("52998224725")  # "529.982.247-25"
unmask_cpf("529.982.247-25")  # "52998224725"
```

Casos extremos: sequências repetidas, como `111.111.111-11`, passam na conta dos dígitos mas
`is_valid_cpf` as rejeita (`False`).

---

## CNPJ

O CNPJ (Cadastro Nacional da Pessoa Jurídica) tem 14 caracteres, os dois últimos de verificação.

Formatos aceitos: com máscara (`11.222.333/0001-81`), sem máscara (`11222333000181`) e o
artefato de float (`11222333000181.0`). Sempre uma `str`.

```python
from pure_docs_br import is_valid_cnpj, mask_cnpj, unmask_cnpj

is_valid_cnpj("11.222.333/0001-81")  # True
is_valid_cnpj("11222333000181.0")  # True
mask_cnpj("11222333000181")  # "11.222.333/0001-81"
unmask_cnpj("11.222.333/0001-81")  # "11222333000181"
```

Caso extremo, o CNPJ alfanumérico de 2026: letras e dígitos são aceitos nas mesmas funções, e
`unmask_cnpj` devolve a forma em maiúsculas.

```python
from pure_docs_br import is_valid_cnpj, mask_cnpj, unmask_cnpj

is_valid_cnpj("12.ABC.345/01DE-35")  # True
mask_cnpj("12ABC34501DE35")  # "12.ABC.345/01DE-35"
unmask_cnpj("12.ABC.345/01DE-35")  # "12ABC34501DE35"
```

---

## CEP

O CEP (Código de Endereçamento Postal) tem 8 dígitos.

Formatos aceitos: com máscara (`01310-100`), sem máscara (`01310100`), com o zero inicial perdido
(`1310100`) e o artefato de float (`1310100.0`). Sempre uma `str`.

```python
from pure_docs_br import is_valid_cep, mask_cep, unmask_cep

is_valid_cep("01310-100")  # True
is_valid_cep("1310100.0")  # True
mask_cep("1310100")  # "01310-100"
unmask_cep("01310-100")  # "01310100"
```

Caso extremo: o CEP não tem dígito verificador, então `is_valid_cep` só confere o formato.
`00000-000` é válido nesse sentido (`True`), mesmo sem existir como endereço.

## PIS/PASEP/NIT/NIS

PIS, PASEP, NIT e NIS são o mesmo número de 11 dígitos (10 de base e 1 dígito verificador,
módulo 11), com nomes diferentes conforme o órgão emissor (CAIXA, Banco do Brasil, INSS).

Formatos aceitos: com máscara (`123.45678.90-0`), sem máscara (`12345678900`), com zeros iniciais
perdidos (`1234567890`) e o artefato de float (`12345678900.0`). Sempre uma `str`.

```python
from pure_docs_br import is_valid_pis_pasep, mask_pis_pasep, unmask_pis_pasep

is_valid_pis_pasep("123.45678.90-0")  # True
is_valid_pis_pasep("12345678901")  # False, dígito verificador errado
mask_pis_pasep("12345678900.0")  # "123.45678.90-0"
unmask_pis_pasep("1234567890")  # "01234567890"
```

Casos extremos: valores de um único dígito repetido (`11111111111`) são inválidos, como no CPF.
`mask_pis_pasep` devolve o valor sem máscara quando o tamanho não fecha em 11 dígitos. Os pesos
do módulo 11 vêm de implementações públicas, não de um manual oficial.

## Título de Eleitor

O Título de Eleitor tem 12 dígitos: 8 de sequencial, 2 da UF (`01` a `28`) e 2 dígitos
verificadores (módulo 11).

Formatos aceitos: com espaços (`0043 5687 09 06`), sem máscara (`004356870906`), com zeros iniciais
perdidos (`4356870906`) e o artefato de float (`4356870906.0`). Sempre uma `str`.

```python
from pure_docs_br import is_valid_titulo_eleitor, mask_titulo_eleitor, unmask_titulo_eleitor

is_valid_titulo_eleitor("0043 5687 09 06")  # True
is_valid_titulo_eleitor("123456780397")  # False, segundo dígito verificador errado
mask_titulo_eleitor("4356870906.0")  # "0043 5687 0906"
unmask_titulo_eleitor("0043 5687 0906")  # "004356870906"
```

Casos extremos: não existe máscara oficial, então `XXXX XXXX XXXX` é uma convenção desta
biblioteca. Códigos de UF fora de `01`-`28` são inválidos (`000000000000` é `False`). Títulos
antigos de 13 dígitos (SP/MG) não são suportados: `is_valid_titulo_eleitor` devolve `False` e
`mask_titulo_eleitor` devolve o valor sem máscara.

## CNS

O CNS (Cartão Nacional de Saúde, ou Cartão SUS) tem 15 dígitos. O primeiro define o tipo: `1` e `2`
são definitivos (PIS de 11 dígitos, sufixo e dígito verificador); `7`, `8` e `9` são provisórios
(soma ponderada divisível por 11).

Formatos aceitos: com espaços (`100 0000 0001 0002`), sem máscara (`100000000010002`) e o artefato
de float (`100000000010002.0`). Sempre uma `str`.

```python
from pure_docs_br import is_valid_cns, mask_cns, unmask_cns

is_valid_cns("100 0000 0001 0002")  # True
is_valid_cns("100000000010003")  # False, dígito verificador errado
mask_cns("100000000010002")  # "100 0000 0001 0002"
unmask_cns("100000000010002.0")  # "100000000010002"
```

Casos extremos: não existe máscara oficial, então `XXX XXXX XXXX XXXX` é uma convenção desta
biblioteca. `unmask_cns` não completa zeros, pois nenhum CNS válido começa com 0. Números que
começam com `0`, `3`, `4`, `5` ou `6` são inválidos. `mask_cns` devolve o valor sem máscara quando o
tamanho não fecha em 15 dígitos. A rotina vem de fontes públicas que citam o DATASUS, não do texto
oficial.
