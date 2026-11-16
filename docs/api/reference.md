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
