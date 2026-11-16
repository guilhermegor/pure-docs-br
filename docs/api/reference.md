# **Referência da API**

Interface pública desta biblioteca.

> **Veja também:** [Uso](../usage.md)

---

## Módulo: `br_identifiers`

Funções puras para CPF e CNPJ, importadas da raiz do pacote. Todas recebem `str`; um valor que
não seja `str` lança `TypeError`.

| Função | Retorno | Comportamento |
|--------|---------|---------------|
| `unmask_cpf(str_value)` | `str` | Mantém só dígitos, descarta a cauda `.0` e completa com zeros à esquerda até 11. Entrada vazia devolve `""`. |
| `mask_cpf(str_value)` | `str` | Formata como `XXX.XXX.XXX-XX`; se não chegar a 11 dígitos, devolve o valor sem máscara. |
| `is_valid_cpf(str_value)` | `bool` | Confere os dois dígitos verificadores; rejeita dígitos repetidos. |
| `unmask_cnpj(str_value)` | `str` | Mantém `A-Z` e `0-9` em maiúsculas; completa com zeros até 14 só quando o valor é numérico. |
| `mask_cnpj(str_value)` | `str` | Formata como `XX.XXX.XXX/XXXX-XX`; se não chegar a 14 caracteres, devolve o valor sem máscara. |
| `is_valid_cnpj(str_value)` | `bool` | Confere os dois dígitos verificadores, numéricos ou alfanuméricos (valor de cada caractere igual ao código ASCII menos 48, módulo 11); rejeita CNPJ numérico de dígitos repetidos. |

```python
from pure_docs_br import is_valid_cnpj, mask_cnpj

mask_cnpj("12ABC34501DE35")  # "12.ABC.345/01DE-35"
is_valid_cnpj("12ABC34501DE35")  # True
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
| Testes | `unittest`; uma asserção por teste; nome no formato `test_<unit>_<scenario>_<expected>` |
