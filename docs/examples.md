# **Exemplos**

Trechos autocontidos e orientados a tarefas para os usos mais comuns desta biblioteca. Cada
receita é independente — copie e ajuste.

> **Veja também:** [Uso](usage.md) para o básico · [Referência da API](api/index.md) para cada
> símbolo público.

---

## Receita: limpar uma coluna de CPF

Valores lidos de uma planilha chegam com ou sem máscara, e um CPF numérico lido como `float` vira
`"52998224725.0"`. `unmask_cpf` normaliza os dois casos antes de comparar.

```python
from pure_docs_br import is_valid_cpf, unmask_cpf

list_raw = ["529.982.247-25", "52998224725.0", "11111111111"]
list_clean = [unmask_cpf(str_raw) for str_raw in list_raw]
list_valid = [is_valid_cpf(str_clean) for str_clean in list_clean]
# list_valid == [True, True, False]
```

## Receita: aceitar o CNPJ alfanumérico

`is_valid_cnpj` aceita o formato numérico antigo e o alfanumérico de 2026 com a mesma função, então
não há desvio por formato no código de quem chama.

```python
from pure_docs_br import is_valid_cnpj, mask_cnpj

is_valid_cnpj("12.abc.345/01de-35")  # True, minúsculas e máscara são toleradas
mask_cnpj("12ABC34501DE35")  # "12.ABC.345/01DE-35"
```
