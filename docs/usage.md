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

## Placa de veículo

A placa de veículo tem 7 caracteres em dois padrões que coexistem: o antigo `LLLNNNN` (`ABC-1234`) e
o Mercosul `LLLNLNN` (`ABC1D23`).

Formatos aceitos: maiúsculas ou minúsculas, com hífen (`abc-1234`) ou sem. Sempre uma `str`.

```python
from pure_docs_br import is_valid_placa, mask_placa, unmask_placa

is_valid_placa("abc-1234")  # True
is_valid_placa("ABC12D4")  # False, o 5º caractere deve ser letra no Mercosul
mask_placa("ABC1234")  # "ABC-1234"
mask_placa("ABC1D23")  # "ABC1D23", o Mercosul não tem separador
unmask_placa("abc-1234")  # "ABC1234"
```

Casos extremos: a placa não tem dígito verificador, então só o formato é conferido, sem consultar
base de veículos. O hífen do padrão antigo é convenção de escrita, não texto da norma. Placas com
formato próprio (Forças Armadas, diplomáticas, representação, motos de competição) são inválidas.
`unmask_placa` não completa zeros e descarta letras e dígitos fora de ASCII (largura total).
`mask_placa` devolve o valor sem máscara quando nenhum formato fecha.

## Número de processo CNJ

O número único de processo judicial (Resolução CNJ 65/2008) tem 20 dígitos no formato
`NNNNNNN-DD.AAAA.J.TR.OOOO`: sequencial, dígitos verificadores, ano, segmento da Justiça, tribunal e
unidade de origem.

Formatos aceitos: com máscara (`0000001-84.2020.8.26.0001`) ou só dígitos, inclusive com cauda `.0`
de conversão float. Sempre uma `str`.

```python
from pure_docs_br import is_valid_processo_cnj, mask_processo_cnj, unmask_processo_cnj

is_valid_processo_cnj("0000001-84.2020.8.26.0001")  # True
is_valid_processo_cnj("0000001-85.2020.8.26.0001")  # False, o DD correto é 84
mask_processo_cnj("00000018420208260001")  # "0000001-84.2020.8.26.0001"
unmask_processo_cnj("0000001-84.2020.8.26.0001")  # "00000018420208260001"
```

Casos extremos: os dígitos verificadores seguem ISO 7064 módulo 97-10, e `DD` só vale de 02 a 98.
Não se confere `J` nem `TR` contra as tabelas oficiais, e a numeração anterior a 2008 não é coberta.
`unmask_processo_cnj` completa zeros à esquerda até 20 e descarta dígitos fora de ASCII (largura
total). `mask_processo_cnj` devolve o valor sem máscara quando o tamanho não fecha em 20.

## Chave de acesso (NF-e, NFC-e, CT-e, MDF-e)

A chave de acesso dos documentos fiscais eletrônicos tem 44 caracteres: `cUF` (2), `AAMM` (4), CNPJ do
emitente (14), `mod` (2), série (3), número (9), `tpEmis` (1), `cNF` (8) e o dígito verificador. NF-e,
NFC-e, CT-e e MDF-e usam a mesma composição e o mesmo DV (módulo 11, MOC 7.0).

Formatos aceitos: só caracteres, em grupos de 4 separados por espaço (como no DANFE), com o prefixo do
atributo `Id` do XML (`NFe`, `CTe`, `MDFe`) ou com cauda `.0` de conversão float. Desde a NT Conjunta
2025.001 as 12 primeiras posições do CNPJ embutido (posições 7 a 18 da chave) podem ser letras `A` a `Z`;
as demais posições são dígitos.

```python
from pure_docs_br import is_valid_chave_acesso, mask_chave_acesso, unmask_chave_acesso

is_valid_chave_acesso("35231111222333000181550010000000011123456789")  # True
is_valid_chave_acesso("35231111222333000181550010000000011123456780")  # False, o DV correto é 9
mask_chave_acesso("35231111222333000181550010000000011123456789")  # "3523 1111 2223 3300 0181 5500 1000 0000 0111 2345 6789"
unmask_chave_acesso("NFe35231111222333000181550010000000011123456789")  # "35231111222333000181550010000000011123456789"
```

Casos extremos: o DV usa o valor `ord(c) - 48` de cada caractere (letras valem 17 a 42), pesos 2 a 9 da
direita para a esquerda; resto 0 ou 1 dá DV 0. `unmask_chave_acesso` mantém dígitos e letras ASCII em
maiúsculas, não completa zeros e descarta dígitos fora de ASCII (largura total). `mask_chave_acesso`
devolve o valor sem máscara quando o tamanho não fecha em 44. Não se valida o CNPJ embutido, a `cUF`
nem o `mod`, nem que o documento existe.
