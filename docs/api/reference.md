# **Referência da API**

Interface pública desta biblioteca.

> **Veja também:** [Uso](../usage.md)

---

## Funções de CPF e CNPJ

Funções puras, importadas da raiz do pacote (`from purepii_br import ...`). Todas recebem `str`; um valor que
não seja `str` (`None`, `float`, `NaN`) lança `TypeError`. Dado um `str`, nenhuma lança exceção por causa do valor; as únicas exceções são a UF de `is_valid_rg`
(`NotImplementedError` para UF sem regra com fonte, `ValueError` para UF desconhecida) e o `ValueError`
de `mask_cnh` e `mask_renavam` para um `str_pattern` inválido (sem exatamente 11 `N`).
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
from purepii_br import is_valid_cnpj, mask_cnpj

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
from purepii_br import is_valid_cep, mask_cep

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
from purepii_br import is_valid_titulo_eleitor, mask_titulo_eleitor

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
from purepii_br import is_valid_pis_pasep, mask_pis_pasep

mask_pis_pasep("12345678900")  # "123.45678.90-0"
is_valid_pis_pasep("11111111111")  # False, dígito repetido
```

---

## Funções de CNS

Mesmo contrato das funções acima (`TypeError` para não `str`, nenhuma exceção para `str`). O CNS
(Cartão Nacional de Saúde) tem 15 dígitos ASCII e o primeiro define o tipo: `1` e `2` são
definitivos, `7`, `8` e `9` provisórios; `0`, `3`, `4`, `5` e `6` são inválidos. O `5` é rejeitado
de propósito, mesmo quando a soma ponderada fecha; o motivo e as fontes estão em
[Uso](../usage.md#por-que-um-cns-iniciado-em-5-e-rejeitado). O módulo 11 vem da
rotina do DATASUS, conhecida por fontes públicas e não pelo texto oficial. `is_valid_cns` não
confirma que o cartão foi emitido.

| Função | Retorno | Comportamento |
|--------|---------|---------------|
| `unmask_cns(str_value)` | `str` | Mantém só dígitos ASCII e descarta a cauda `.0`. Não completa zeros, pois nenhum CNS válido começa com 0. Entrada sem dígitos devolve `""`. |
| `mask_cns(str_value)` | `str` | Formata como `XXX XXXX XXXX XXXX` (convenção da biblioteca; o CNS não tem máscara oficial); se o valor sem máscara não tiver 15 dígitos, devolve esse valor sem máscara. |
| `is_valid_cns(str_value)` | `bool` | `True` quando há 15 dígitos e a regra do tipo fecha: dígito verificador e sufixo (definitivo) ou soma ponderada divisível por 11 (provisório). |

```python
from purepii_br import is_valid_cns, mask_cns

mask_cns("100000000010002")  # "100 0000 0001 0002"
is_valid_cns("300000000000000")  # False, começa com 3
```

---

## Funções de CNH

Mesmo contrato das funções acima (`TypeError` para não `str`; o valor do documento em `str` nunca levanta exceção, mas um `str_pattern` inválido, sem exatamente 11 `N`, levanta `ValueError`). O número
de registro da CNH tem 11 dígitos (9 + 2 dígitos verificadores); só esse formato é oficial
(Resolução CONTRAN 886/2021, art. 4º, I). **A fórmula dos dígitos verificadores não é oficial**: é a
variante `dsc` reconstruída pela comunidade e pode errar nos dois sentidos (reprovar CNH real,
aprovar número inventado). A CNH não tem máscara oficial: `mask_cnh` exige o padrão. A validação é só aritmética local e não confirma que a CNH existe, está vigente ou
pertence a quem a apresenta (use o serviço "Validar CNH" do SENATRAN).

| Função | Retorno | Comportamento |
|--------|---------|---------------|
| `unmask_cnh(str_value)` | `str` | Mantém só dígitos ASCII, descarta a cauda `.0` e completa zeros à esquerda até 11. Entrada sem dígitos devolve `""`. |
| `mask_cnh(str_value, *, str_pattern)` | `str` | Aplica o padrão do chamador: cada `N` recebe o próximo dígito, o resto é copiado. Padrão sem exatamente 11 `N` levanta `ValueError`; entrada com menos de 11 dígitos é completada com zeros à esquerda antes do padrão; entrada vazia ou com mais de 11 dígitos volta sem máscara. |
| `is_valid_cnh(str_value)` | `bool` | `True` quando há 11 dígitos não todos iguais e os dois dígitos verificadores fecham na variante `dsc`. |

```python
from purepii_br import is_valid_cnh, mask_cnh, unmask_cnh

unmask_cnh("119")  # "00000000119"
mask_cnh("02650306461", str_pattern="NNN NNNN NNNN")  # "026 5030 6461"
is_valid_cnh("98765432109")  # True
```

---

## Funções de RENAVAM

Mesmo contrato das funções acima (`TypeError` para não `str`; o valor do documento em `str` nunca levanta exceção, mas um `str_pattern` inválido, sem exatamente 11 `N`, levanta `ValueError`). O RENAVAM
tem 11 dígitos (10 da base + 1 dígito verificador). O dígito verificador segue o Comunicado de
Importação nº 064/2025 do Siscomex (módulo 11, pesos `3,2,9,8,7,6,5,4,3,2`); o SENATRAN não publicou
a especificação completa. **Partes não oficiais (convenção da comunidade)**: aceitar o número antigo
de 9 dígitos completando com zeros e rejeitar números com todos os dígitos iguais. O RENAVAM não
tem máscara oficial: `mask_renavam` exige o padrão. A validação é
só aritmética local e não confirma que o veículo existe, que o RENAVAM está ativo, que pertence a
quem o informa nem que a placa corresponde (use o serviço do SENATRAN/DETRAN).

| Função | Retorno | Comportamento |
|--------|---------|---------------|
| `unmask_renavam(str_value)` | `str` | Mantém só dígitos ASCII, descarta a cauda `.0` e completa zeros à esquerda até 11. Entrada sem dígitos devolve `""`. |
| `mask_renavam(str_value, *, str_pattern)` | `str` | Aplica o padrão do chamador: cada `N` recebe o próximo dígito, o resto é copiado; 9 dígitos são completados com zeros até 11. Padrão sem exatamente 11 `N` levanta `ValueError`; entrada com menos de 11 dígitos é completada com zeros à esquerda antes do padrão; entrada vazia ou com mais de 11 dígitos volta sem máscara. |
| `is_valid_renavam(str_value)` | `bool` | `True` quando há 9 ou 11 dígitos, a forma de 11 não é toda igual e o dígito verificador fecha. |

```python
from purepii_br import is_valid_renavam, mask_renavam, unmask_renavam

unmask_renavam("1234567897.0")  # "01234567897"
mask_renavam("22500062413", str_pattern="NNNNNNNNNN-N")  # "2250006241-3"
is_valid_renavam("22500062413")  # True
```

---

## Funções de RG e CIN

`is_valid_rg` e `unmask_rg` têm o mesmo contrato das funções acima para a entrada (`TypeError` para não `str`).
**Não existe norma nacional para o RG**: cada UF numera o seu. `str_uf` roteia por um dicionário de
funções por UF (como a inscrição estadual) e é comparado **exatamente** (sigla em maiúsculas, sem
normalização: `"sp"` é UF desconhecida). Diferente da IE, UF desconhecida lança `ValueError`, e uma UF
sem regra com fonte lança `NotImplementedError`; nunca devolve `False` em silêncio. Não há `mask_rg`:
a estratégia de máscara fica para a issue #53.

| UF | Regra | Fonte e confiança |
|----|-------|-------------------|
| SP | 9 caracteres com DV módulo 11, pesos 9..2, resto 10 vira `X`; 8 dígitos valem só como formato (documentos antigos não têm DV) | 3 fontes comunitárias concordantes, **não oficial** (a SSP-SP não publica); média |
| RJ | 9 dígitos, DV módulo 10, pesos 2,1 a partir da unidade, "noves fora" | **fonte comunitária única** (ghiorzi.org); baixa |
| MG | 7 ou 8 dígitos, só formato (MG não tem DV) | fonte jornalística e registro do TCE-MG com RG de 7 dígitos; média-baixa |
| demais 24 UFs | `NotImplementedError` | nenhuma fonte encontrada |
| sem UF | 7 a 10 caracteres, só dígitos, `X` apenas no fim | heurística, não norma; pode reprovar RG com prefixo de letras |

| Função | Retorno | Comportamento |
|--------|---------|---------------|
| `unmask_rg(str_value)` | `str` | Remove `.`, `-`, `/`, espaços e a cauda `.0`, e põe em maiúsculas. Não completa zeros. |
| `is_valid_rg(str_value, *, str_uf=None)` | `bool` | Valida pela regra da UF. Lança `ValueError` (UF desconhecida) ou `NotImplementedError` (UF sem regra). |
| `is_valid_cin(str_value)` | `bool` | O número da CIN é o CPF (Lei 14.534/2023): reusa `is_valid_cpf`, sem relação com o RG. |

```python
from purepii_br import is_valid_cin, is_valid_rg, unmask_rg

unmask_rg("10.000.006-x")  # "10000006X"
is_valid_rg("12.030.001-1", str_uf="SP")  # True
is_valid_rg("1234567", str_uf=None)  # True, heurística sem UF
is_valid_cin("529.982.247-25")  # True
```

---

## Funções de CAEPF

Mesmo contrato das funções acima (`TypeError` para não `str`, nenhuma exceção para `str`). O CAEPF tem
14 dígitos (9 do CPF, 3 de sequencial, 2 dígitos verificadores) e a máscara `NNN.NNN.NNN/NNN-NN`; só
essa estrutura é oficial. **O cálculo dos dígitos verificadores não é publicado pela Receita Federal**:
a fórmula (com o ajuste `+ 12`) vem de uma fonte comunitária e reproduz o exemplo oficial do SERPRO
`00000002500171`; o ramo `> 99` e o resto 10 como 0 seguem sem confirmação. Pode reprovar um CAEPF
real e aprovar um número nunca emitido, e não confirma que o CAEPF existe, está ativo nem pertence ao
titular (use o e-CAC).

| Função | Retorno | Comportamento |
|--------|---------|---------------|
| `unmask_caepf(str_value)` | `str` | Mantém só dígitos ASCII, descarta a cauda `.0` e completa zeros à esquerda até 14. Entrada sem dígitos devolve `""`. |
| `mask_caepf(str_value)` | `str` | Completa zeros à esquerda até 14 e então, se há 14 dígitos, devolve `NNN.NNN.NNN/NNN-NN`; senão (vazio ou mais de 14) devolve o valor sem máscara. |
| `is_valid_caepf(str_value)` | `bool` | `True` quando, completado com zeros à esquerda até 14, há 14 dígitos, a base de CPF não é toda igual, o sequencial não é `000` e os dígitos verificadores fecham. |

```python
from purepii_br import is_valid_caepf, mask_caepf, unmask_caepf

mask_caepf("11144477700154")  # "111.444.777/001-54"
unmask_caepf("11144477700154.0")  # "11144477700154"
is_valid_caepf("00000002500171")  # True
```

---

## Funções de matrícula de certidão

Mesmo contrato das funções acima (`TypeError` para não `str`, nenhuma exceção para `str`). Uma só
família cobre as certidões de nascimento, casamento e óbito (matrícula de 32 dígitos). A estrutura é
oficial (Provimento CNJ nº 3/2009); **o cálculo dos dígitos verificadores não é publicado pelo CNJ**
e vem de uma fonte secundária (módulo 11, resto 10 vale 1). O dígito do CNS (posições 1-6) é
validado por Luhn (ISO/IEC 7812-1), regra **empírica** não publicada pelo CNJ. Não confirma que a
certidão ou o cartório existem; se o CNJ mudar a regra, a lib não percebe.

| Função | Retorno | Comportamento |
|--------|---------|---------------|
| `unmask_certidao_matricula(str_value)` | `str` | Mantém só dígitos ASCII, descarta a cauda `.0` e completa zeros à esquerda até 32; 30 dígitos seguidos de `xx` ficam como estão, em maiúsculas. Entrada sem dígitos devolve `""`. |
| `mask_certidao_matricula(str_value)` | `str` | Se há 32 posições, devolve `NNNNNN NN NN NNNN N NNNNN NNN NNNNNNN-NN`; senão devolve o valor sem máscara. |
| `is_valid_certidao_matricula(str_value)` | `bool` | `True` com 32 posições, dígitos não todos iguais, CNS aprovado em Luhn, acervo `01`-`99`, serviço `55`, ano de `1800` ao ano corrente, tipo do livro `1`-`9` e dígitos verificadores corretos (ou `xx`). |

```python
from purepii_br import (
    is_valid_certidao_matricula,
    mask_certidao_matricula,
    unmask_certidao_matricula,
)

is_valid_certidao_matricula("10453901552013100012021000012321")  # True
mask_certidao_matricula(
    "10453901552013100012021000012321"
)  # "104539 01 55 2013 1 00012 021 0000123-21"
unmask_certidao_matricula(
    "10453901552013100012021000012321.0"
)  # "10453901552013100012021000012321"
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
from purepii_br import is_valid_placa, mask_placa

mask_placa("abc1234")  # "ABC-1234"
is_valid_placa("ABC12D4")  # False, o 5º caractere deve ser letra no Mercosul
```

---

## Funções de número de processo CNJ

Mesmo contrato das funções acima (`TypeError` para não `str`; o valor do documento em `str` nunca levanta exceção, mas um `str_pattern` inválido, sem exatamente 11 `N`, levanta `ValueError`). O número
único tem 20 dígitos, `NNNNNNN-DD.AAAA.J.TR.OOOO` (Resolução CNJ 65/2008), com dígitos verificadores
ISO 7064 módulo 97-10: `int(N AAAA J TR OOOO DD) % 97 == 1`, com `DD` entre 02 e 98. Fora do escopo:
conferir `J` e `TR` contra as tabelas dos anexos e a numeração anterior a 2008. `is_valid_processo_cnj`
não confirma que o processo existe.

| Função | Retorno | Comportamento |
|--------|---------|---------------|
| `unmask_processo_cnj(str_value)` | `str` | Mantém só dígitos ASCII, remove a cauda `.0` e completa zeros à esquerda até 20. Vazio continua vazio. |
| `mask_processo_cnj(str_value)` | `str` | Formata como `NNNNNNN-DD.AAAA.J.TR.OOOO`; se o tamanho não fecha em 20 dígitos, devolve o valor sem máscara. |
| `is_valid_processo_cnj(str_value)` | `bool` | `True` quando há 20 dígitos, `DD` entre 02 e 98 e o resto módulo 97 é 1. |

```python
from purepii_br import is_valid_processo_cnj, mask_processo_cnj

mask_processo_cnj("00000018420208260001")  # "0000001-84.2020.8.26.0001"
is_valid_processo_cnj("0000001-85.2020.8.26.0001")  # False, o DD correto é 84
```

---

## Funções de chave de acesso (NF-e, NFC-e, CT-e, MDF-e)

Mesmo contrato das funções acima (`TypeError` para não `str`, nenhuma exceção para `str`). A chave tem
44 caracteres no formato `[0-9]{6}[A-Z0-9]{12}[0-9]{26}` (MOC 7.0 e NT Conjunta 2025.001, que admite
letras no CNPJ do emitente). O DV é o módulo 11 dos 43 primeiros caracteres, cada um valendo
`ord(c) - 48`, com pesos 2 a 9 da direita para a esquerda; resto 0 ou 1 dá DV 0. Fora do escopo:
validar o CNPJ embutido, a `cUF` e o `mod`.

| Função | Retorno | Comportamento |
|--------|---------|---------------|
| `unmask_chave_acesso(str_value)` | `str` | Remove o prefixo `NFe`/`CTe`/`MDFe` e a cauda `.0`, mantém dígitos e letras ASCII em maiúsculas. Não completa zeros. |
| `mask_chave_acesso(str_value)` | `str` | 11 grupos de 4 separados por espaço; se o tamanho não fecha em 44, devolve o valor sem máscara. |
| `is_valid_chave_acesso(str_value)` | `bool` | `True` quando o formato fecha e o último caractere é o DV dos 43 primeiros. |

```python
from purepii_br import is_valid_chave_acesso

is_valid_chave_acesso("NFe35231111222333000181550010000000011123456789")  # True
is_valid_chave_acesso("35231111222333000181550010000000011123456780")  # False, o DV correto é 9
```

---

## Funções de boleto de cobrança bancária

Mesmo contrato das funções acima (`TypeError` para não `str`, nenhuma exceção para `str`). Aceita o
código de barras (44 dígitos) ou a linha digitável (47), `AAABC.CCCCX DDDDD.DDDDDY EEEEE.EEEEEZ K
UUUUVVVVVVVVVV`. Os campos 1 a 3 da linha têm DV módulo 10; o DV geral (posição 5 do código de barras,
`K` na linha) é o módulo 11 de 2 a 9 sobre as outras 43 posições, e resultado 0, 10 ou 11 vira 1. Esse
módulo 11 é próprio da cobrança: o boleto de arrecadação (48 dígitos) usa outra regra. Fora do escopo:
fator de vencimento, valor, existência do banco e conversão de linha em código de barras.

| Função | Retorno | Comportamento |
|--------|---------|---------------|
| `unmask_boleto_cobranca(str_value)` | `str` | Mantém só dígitos ASCII e remove a cauda `.0` de um valor só com dígitos. Não completa zeros. |
| `mask_boleto_cobranca(str_value)` | `str` | Formata a linha de 47 dígitos como `AAAAA.AAAAA BBBBB.BBBBBB CCCCC.CCCCCC D EEEEEEEEEEEEEE`; qualquer outro tamanho (inclusive o código de barras de 44) sai sem máscara. |
| `is_valid_boleto_cobranca(str_value)` | `bool` | `True` quando há 44 dígitos com DV geral correto, ou 47 com os três DV de campo e o DV geral corretos. |

```python
from purepii_br import is_valid_boleto_cobranca, mask_boleto_cobranca

mask_boleto_cobranca(
    "00190000090000000000000000000018199990000012345"
)  # "00190.00009 00000.000000 00000.000018 1 99990000012345"
is_valid_boleto_cobranca(
    "00190000090000000000000000000018199990000012346"
)  # False, o DV geral não confere
```

---

## Funções de boleto de arrecadação / convênio

Mesmo contrato das funções acima (`TypeError` para não `str`, nenhuma exceção para `str`). Aceita o
código de barras (44 dígitos, começa com 8) ou a linha digitável (48 dígitos: quatro blocos de 11
dígitos, cada um seguido do seu DV). O 3º dígito (identificação do valor) escolhe o módulo: `6` ou `7`
módulo 10, `8` ou `9` módulo 11; qualquer outro valor é inválido. No módulo 11 desta regra, resto 0 ou
1 dá DV 0 e resto 10 dá DV 1, diferente do boleto de cobrança (47 dígitos). O DV geral fica na posição
4 do código de barras. Fora do escopo: segmento, valor e empresa/órgão.

| Função | Retorno | Comportamento |
|--------|---------|---------------|
| `unmask_boleto_arrecadacao(str_value)` | `str` | Mantém só dígitos ASCII e remove a cauda `.0` de um valor só com dígitos. Não completa zeros. |
| `mask_boleto_arrecadacao(str_value)` | `str` | Formata a linha de 48 dígitos como `XXXXXXXXXXX-X XXXXXXXXXXX-X XXXXXXXXXXX-X XXXXXXXXXXX-X`; qualquer outro tamanho (inclusive o código de barras de 44) sai sem máscara. |
| `is_valid_boleto_arrecadacao(str_value)` | `bool` | `True` quando há 44 dígitos começando em 8 com DV geral correto, ou 48 com os quatro DV de bloco corretos e o código de barras reconstruído válido. |

```python
from purepii_br import is_valid_boleto_arrecadacao, mask_boleto_arrecadacao

mask_boleto_arrecadacao(
    "816800000019234500000000000000000000000000000000"
)  # "81680000001-9 23450000000-0 00000000000-0 00000000000-0"
is_valid_boleto_arrecadacao(
    "81690000001234500000000000000000000000000000"
)  # False, o DV geral correto é 8
```

---

## Funções de Inscrição Estadual (IE)

Mesmo contrato das funções acima (`TypeError` para não `str`, nenhuma exceção para `str`). A UF é o
argumento nomeado `str_uf` (sigla em maiúsculas). Uma UF fora das 27 siglas faz `is_valid_inscricao_estadual`
devolver `False`, então uma UF digitada errado torna toda IE inválida. `ISENTO` e qualquer valor com
letra (inclusive o produtor rural `P-...` de SP) são inválidos. Fonte das regras: páginas do Sintegra
(`http://www.sintegra.gov.br/Cad_Estados/cad_<UF>.html`), SEFAZ-GO para Goiás.

| Função | Retorno | Comportamento |
|--------|---------|---------------|
| `unmask_inscricao_estadual(str_value)` | `str` | Mantém só dígitos ASCII e remove a cauda `.0` de um valor só com dígitos. Não completa zeros. |
| `mask_inscricao_estadual(str_value, *, str_uf)` | `str` | Aplica a máscara da UF conforme o número de dígitos; UF desconhecida ou tamanho fora da tabela devolve o valor sem máscara. |
| `is_valid_inscricao_estadual(str_value, *, str_uf)` | `bool` | `True` quando tamanho, prefixo e dígitos verificadores seguem a regra da UF. |

UFs suportadas (`#` é um dígito):

| UF | Dígitos | Máscara |
|----|---------|---------|
| AC | 13 | `##.###.###/###-##` |
| AL | 9 | `##.###.###-#` |
| AP | 9 | `##.###.###-#` |
| AM | 9 | `##.###.###-#` |
| BA | 8 ou 9 | `######-##` / `#######-##` |
| CE | 9 | `########-#` |
| DF | 13 | `###.#####.###-##` |
| ES | 9 | `########-#` |
| GO | 9 | `##.###.###-#` |
| MA | 9 | `##.###.###-#` |
| MT | 11 | `##########-#` |
| MS | 9 | `##.###.###-#` |
| MG | 13 | `###.###.###/####` |
| PA | 9 | `##-######-#` |
| PB | 9 | `########-#` |
| PR | 10 | `###.#####-##` |
| PE | 9 ou 14 | `#######-##` / `##.#.###.#######-#` |
| PI | 9 | `########-#` |
| RJ | 8 | `##.###.##-#` |
| RN | 9 ou 10 | `##.###.###-#` / `##.#.###.###-#` |
| RS | 10 | `###/#######` |
| RO | 9 ou 14 | `###.#####-#` / `#############-#` |
| RR | 9 | `##.###.###-#` |
| SC | 9 | `###.###.###` |
| SP | 12 | `###.###.###.###` |
| SE | 9 | `########-#` |
| TO | 11 | `##.##.######-#` |

```python
from purepii_br import is_valid_inscricao_estadual, mask_inscricao_estadual

mask_inscricao_estadual("109876547", str_uf="GO")  # "10.987.654-7"
is_valid_inscricao_estadual("110042490114", str_uf="XX")  # False, UF desconhecida
```

---

## Adicionando novos módulos

Coloque os novos módulos em `src/purepii_br/`. Exporte os símbolos públicos em `src/purepii_br/__init__.py` e liste-os em `__all__`, para que quem usa a biblioteca importe direto da raiz do pacote, como `from purepii_br import mask_cpf`.

Siga a convenção de uma classe por arquivo: funções utilitárias sem estado compartilhado ficam no nível do módulo, e não dentro de uma classe.

---

## Convenções

| Convenção | Regra |
|-----------|-------|
| Type hints | Obrigatórias em todas as funções públicas, inclusive o retorno `-> None` |
| Docstrings | Estilo NumPy; explique o *porquê*, não o *quê* |
| Nomes de variáveis | Com prefixo de tipo (`str_`, `list_`, `cls_`, `dict_`, …) |
| Testes | `pytest`; uma asserção por teste; nome no formato `test_<unit>_<scenario>_<expected>` |
