# **Referência da API**

Interface pública desta biblioteca.

> **Veja também:** [Uso](../usage.md)

---

## Funções de CPF e CNPJ

Funções puras, importadas da raiz do pacote (`from pure_docs_br import ...`). Todas recebem `str`; um valor que
não seja `str` (`None`, `float`, `NaN`) lança `TypeError`. Dado um `str`, nenhuma lança exceção.
Entrada numérica curta é completada com zeros à esquerda antes de os dígitos verificadores serem
testados (o mesmo preenchimento de `unmask_*`), de propósito, para recuperar documentos guardados
como número. Assim `is_valid_cpf("191")` é `True` (`"191"` vira `00000000191`), mas
`is_valid_cpf("0")` é `False`, pois dígitos repetidos são rejeitados.

| Função | Retorno | Comportamento |
|--------|---------|---------------|
| `unmask_cpf(str_value)` | `str` | Mantém só dígitos, descarta a cauda `.0` e completa com zeros à esquerda até 11. Entrada vazia devolve `""`; mais de 11 dígitos é devolvido como está. |
| `mask_cpf(str_value)` | `str` | Formata como `XXX.XXX.XXX-XX`; se o valor sem máscara não tiver 11 dígitos (vazio ou mais de 11), devolve esse valor sem máscara. |
| `is_valid_cpf(str_value)` | `bool` | Confere os dois dígitos verificadores; rejeita dígitos repetidos. |
| `unmask_cnpj(str_value)` | `str` | Descarta a cauda `.0`, mantém `A-Z` e `0-9` em maiúsculas e completa com zeros até 14 só quando o valor é numérico. Notação científica não é tratada. |
| `mask_cnpj(str_value)` | `str` | Formata como `XX.XXX.XXX/XXXX-XX`; se o valor sem máscara não tiver 14 caracteres (alfanumérico curto, vazio ou mais de 14), devolve esse valor sem máscara. |
| `is_valid_cnpj(str_value)` | `bool` | Confere os dois dígitos verificadores, numéricos ou alfanuméricos (valor de cada caractere igual ao código ASCII menos 48, módulo 11); rejeita CNPJ numérico de dígitos repetidos. |

```python
from pure_docs_br import is_valid_cnpj, mask_cnpj

mask_cnpj("12ABC34501DE35")  # "12.ABC.345/01DE-35"
is_valid_cnpj("12ABC34501DE35")  # True
```

---

## Funções de CEP

Mesmo contrato das funções acima (`TypeError` para não `str`, nenhuma exceção para `str`). O CEP
não tem dígito verificador: `is_valid_cep` confere só o formato e **não consulta a base dos
Correios**, então não confirma que o CEP existe. `00000-000` passa na checagem de formato.

| Função | Retorno | Comportamento |
|--------|---------|---------------|
| `unmask_cep(str_value)` | `str` | Mantém só dígitos, descarta a cauda `.0` e completa com zeros à esquerda até 8. Entrada vazia devolve `""`; mais de 8 dígitos é devolvido como está. |
| `mask_cep(str_value)` | `str` | Formata como `XXXXX-XXX`; se o valor sem máscara não tiver 8 dígitos (vazio ou mais de 8), devolve esse valor sem máscara. |
| `is_valid_cep(str_value)` | `bool` | `True` quando o valor sem máscara tem 8 dígitos. Entrada de 7 dígitos é válida (zero à esquerda restaurado). |

```python
from pure_docs_br import is_valid_cep, mask_cep

mask_cep("01001010")  # "01001-010"
is_valid_cep("123456789")  # False, 9 dígitos
```

---

## Funções de Título de Eleitor

Mesmo contrato das funções acima (`TypeError` para não `str`, nenhuma exceção para `str`). O
algoritmo vem de fonte secundária (Wikipédia); o TSE não publica a fórmula. `is_valid_titulo_eleitor`
não confirma que o título foi emitido.

| Função | Retorno | Comportamento |
|--------|---------|---------------|
| `unmask_titulo_eleitor(str_value)` | `str` | Mantém só dígitos, descarta a cauda `.0` e completa com zeros à esquerda até 12. Entrada vazia devolve `""`; mais de 12 dígitos é devolvido como está. |
| `mask_titulo_eleitor(str_value)` | `str` | Formata como `XXXX XXXX XXXX` (convenção da biblioteca); se o valor sem máscara não tiver 12 dígitos, devolve esse valor sem máscara. |
| `is_valid_titulo_eleitor(str_value)` | `bool` | `True` quando há 12 dígitos, UF de `01` a `28` e os dois dígitos verificadores batem. 13 dígitos é `False`. |

```python
from pure_docs_br import is_valid_titulo_eleitor, mask_titulo_eleitor

mask_titulo_eleitor("004356870906")  # "0043 5687 0906"
is_valid_titulo_eleitor("123456782996")  # False, UF 29 não existe
```

---

## Funções de PIS/PASEP/NIT/NIS

Mesmo contrato das funções acima (`TypeError` para não `str`, nenhuma exceção para `str`). O módulo
11 é oficial; os pesos `3,2,9,8,7,6,5,4,3,2` são consenso de implementações públicas.
`is_valid_pis_pasep` não confirma que o número foi emitido.

| Função | Retorno | Comportamento |
|--------|---------|---------------|
| `unmask_pis_pasep(str_value)` | `str` | Mantém só dígitos, descarta a cauda `.0` e completa com zeros à esquerda até 11. Entrada vazia devolve `""`; mais de 11 dígitos é devolvido como está. |
| `mask_pis_pasep(str_value)` | `str` | Formata como `XXX.XXXXX.XX-X`; se o valor sem máscara não tiver 11 dígitos, devolve esse valor sem máscara. |
| `is_valid_pis_pasep(str_value)` | `bool` | `True` quando há 11 dígitos, não é um único dígito repetido e o dígito verificador bate. |

```python
from pure_docs_br import is_valid_pis_pasep, mask_pis_pasep

mask_pis_pasep("12345678900")  # "123.45678.90-0"
is_valid_pis_pasep("11111111111")  # False, dígito repetido
```

---

## Funções de CNS

Mesmo contrato das funções acima (`TypeError` para não `str`, nenhuma exceção para `str`). O CNS
(Cartão Nacional de Saúde) tem 15 dígitos ASCII e o primeiro define o tipo: `1` e `2` são
definitivos, `7`, `8` e `9` provisórios; `0`, `3`, `4`, `5` e `6` são inválidos. O módulo 11 vem da
rotina do DATASUS, conhecida por fontes públicas e não pelo texto oficial. `is_valid_cns` não
confirma que o cartão foi emitido.

| Função | Retorno | Comportamento |
|--------|---------|---------------|
| `unmask_cns(str_value)` | `str` | Mantém só dígitos ASCII e descarta a cauda `.0`. Não completa zeros, pois nenhum CNS válido começa com 0. Entrada sem dígitos devolve `""`. |
| `mask_cns(str_value)` | `str` | Formata como `XXX XXXX XXXX XXXX` (convenção da biblioteca; o CNS não tem máscara oficial); se o valor sem máscara não tiver 15 dígitos, devolve esse valor sem máscara. |
| `is_valid_cns(str_value)` | `bool` | `True` quando há 15 dígitos e a regra do tipo fecha: dígito verificador e sufixo (definitivo) ou soma ponderada divisível por 11 (provisório). |

```python
from pure_docs_br import is_valid_cns, mask_cns

mask_cns("100000000010002")  # "100 0000 0001 0002"
is_valid_cns("300000000000000")  # False, começa com 3
```

---

## Funções de placa de veículo

Mesmo contrato das funções acima (`TypeError` para não `str`, nenhuma exceção para `str`). A placa
não tem dígito verificador: a validação é só de formato, para o padrão antigo `LLLNNNN`
(Resolução CONTRAN 231/2007) e o Mercosul `LLLNLNN` (Resolução CONTRAN 780/2019). Placas com
formato próprio (Forças Armadas, diplomáticas, representação, motos de competição) não são
cobertas. `is_valid_placa` não confirma que a placa foi emitida.

| Função | Retorno | Comportamento |
|--------|---------|---------------|
| `unmask_placa(str_value)` | `str` | Converte para maiúsculas e mantém só `A-Z0-9` ASCII. Não completa zeros. |
| `mask_placa(str_value)` | `str` | Formata o padrão antigo como `ABC-1234` (convenção de escrita); o Mercosul não tem separador; se nenhum formato fechar, devolve o valor sem máscara. |
| `is_valid_placa(str_value)` | `bool` | `True` quando o valor sem máscara é `LLLNNNN` ou `LLLNLNN`. |

```python
from pure_docs_br import is_valid_placa, mask_placa

mask_placa("abc1234")  # "ABC-1234"
is_valid_placa("ABC12D4")  # False, o 5º caractere deve ser letra no Mercosul
```

---

## Adicionando novos módulos

Coloque os novos módulos em `src/pure_docs_br/`. Exporte os símbolos públicos em `src/pure_docs_br/__init__.py` e liste-os em `__all__`, para que quem usa a biblioteca importe direto da raiz do pacote, como `from pure_docs_br import mask_cpf`.

Siga a convenção de uma classe por arquivo: funções utilitárias sem estado compartilhado ficam no nível do módulo, e não dentro de uma classe.

---

## Convenções

| Convenção | Regra |
|-----------|-------|
| Type hints | Obrigatórias em todas as funções públicas, inclusive o retorno `-> None` |
| Docstrings | Estilo NumPy; explique o *porquê*, não o *quê* |
| Nomes de variáveis | Com prefixo de tipo (`str_`, `list_`, `cls_`, `dict_`, …) |
| Testes | `pytest`; uma asserção por teste; nome no formato `test_<unit>_<scenario>_<expected>` |
