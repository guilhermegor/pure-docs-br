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

## CNH

O número de registro da CNH (Carteira Nacional de Habilitação) tem 11 dígitos: 9 da base e 2 dígitos
verificadores. Só esse formato é oficial (Resolução CONTRAN 886/2021, art. 4º, I). A fórmula dos
dígitos verificadores não é publicada, e a biblioteca usa a variante `dsc` reconstruída pela
comunidade.

Formatos aceitos: sem máscara (`12345678900`), com espaços ou pontuação e o artefato de float
(`12345678900.0`). Sempre uma `str`.

```python
from pure_docs_br import is_valid_cnh, unmask_cnh

is_valid_cnh("12345678900")  # True
is_valid_cnh("12345678901")  # False, dígito verificador errado
unmask_cnh("12345678900.0")  # "12345678900"
unmask_cnh("119")  # "00000000119"
```

Casos extremos: não existe `mask_cnh`, pois a CNH não tem máscara oficial e a estratégia de máscara
fica para a issue #53. `unmask_cnh` completa zeros à esquerda até 11 dígitos. Os 11 dígitos todos
iguais são inválidos. Como o algoritmo não é oficial, `is_valid_cnh` pode reprovar uma CNH real e
aprovar um número inventado; não use como único critério para bloquear ou aprovar alguém. Também não
confirma que a CNH existe, está vigente ou pertence a quem a apresenta; para isso use o serviço
"Validar CNH" do SENATRAN (gov.br). Se o órgão mudar a regra, a biblioteca não percebe.

## RENAVAM

O RENAVAM (Registro Nacional de Veículos Automotores) tem 11 dígitos: 10 da base e 1 dígito
verificador. O cálculo do dígito segue o Comunicado de Importação nº 064/2025 do Siscomex (módulo 11,
pesos `3,2,9,8,7,6,5,4,3,2`). Não há norma do SENATRAN publicando a especificação completa.

Formatos aceitos: sem máscara (`22500062413`), com espaços ou pontuação, o artefato de float
(`1234567897.0`) e o número antigo de 9 dígitos (`000123455`). Sempre uma `str`.

```python
from pure_docs_br import is_valid_renavam, unmask_renavam

is_valid_renavam("22500062413")  # True
is_valid_renavam("22500062414")  # False, dígito verificador errado
is_valid_renavam("000123455")  # True, 9 dígitos equivalem a 00000123455
unmask_renavam("1234567897.0")  # "01234567897"
```

Casos extremos: não existe `mask_renavam`, pois o RENAVAM não tem máscara oficial e a estratégia de
máscara fica para a issue #53. `unmask_renavam` completa zeros à esquerda até 11 dígitos. Aceitar 9
dígitos (completados com zeros) e rejeitar números com todos os dígitos iguais são convenções da
comunidade, não regras do SENATRAN. Um número de 10 dígitos é inválido. A validação é aritmética
local: não confirma que o veículo existe, que o RENAVAM está ativo, que pertence a quem o informa
nem que a placa corresponde; para isso consulte o serviço do SENATRAN/DETRAN. Se o órgão mudar a
regra, a biblioteca não percebe.

## RG e CIN

Não existe norma nacional para o RG: cada UF numera o seu. A biblioteca valida por UF
(`is_valid_rg(valor, str_uf="SP")`), com a sigla em maiúsculas e comparada exatamente. SP usa o dígito
verificador módulo 11, **não oficial** (reconstruído pela comunidade); RJ usa módulo 10 de **uma única
fonte comunitária**; MG só tem formato (7 ou 8 dígitos). Outra UF lança `NotImplementedError` e UF desconhecida lança
`ValueError`. Sem UF vale uma heurística (7 a 10 caracteres, `X` só no fim), não uma norma. Na CIN o
número é o CPF: use `is_valid_cin`, que não tem relação com o RG.

Formatos aceitos: com pontuação (`12.030.001-1`), sem máscara (`120300011`), dígito `x` minúsculo e a
cauda de float (`123456789.0`). Sempre uma `str`.

```python
from pure_docs_br import is_valid_cin, is_valid_rg, unmask_rg

is_valid_rg("12.030.001-1", str_uf="SP")  # True
is_valid_rg("123456783", str_uf="SP")  # False, dígito verificador errado
is_valid_rg("12345678", str_uf="SP")  # True, 8 dígitos só têm o formato verificado
is_valid_rg("123456782", str_uf="RJ")  # True
unmask_rg("10.000.006-x")  # "10000006X"
is_valid_cin("529.982.247-25")  # True
```

Casos extremos: não existe `mask_rg` (a estratégia de máscara fica para a issue #53). `unmask_rg` não
completa zeros. `True` significa "parece um RG": não confirma que o RG existe, que pertence a quem o
informa, que não foi cancelado nem que foi emitido por aquela UF. Se o órgão mudar a regra, a
biblioteca não percebe.

## CAEPF

O CAEPF (Cadastro de Atividade Econômica da Pessoa Física) tem 14 dígitos: os 9 primeiros do CPF do
titular, 3 de sequencial (`001` a `999`) e 2 dígitos verificadores. A estrutura e a máscara
`NNN.NNN.NNN/NNN-NN` são oficiais (IN RFB nº 1.828/2018). **A fórmula dos dígitos verificadores não é
publicada pela Receita Federal.** A usada aqui foi reconstruída a partir de uma fonte comunitária
(ghiorzi.org/DVnew.htm), inclui o ajuste `+ 12` (soma 12 aos dois dígitos lidos como um número e
subtrai 100 se passar de 99) e reproduz o exemplo oficial da documentação da API Cadastro CAEPF do
SERPRO (`00000002500171`); sem o `+ 12` ele não fecha. **Seguem sem confirmação** o ramo `> 99`
(subtrair 100) e o tratamento do resto 10 como 0.

Formatos aceitos: com máscara (`000.000.025/001-71`), sem máscara (`00000002500171`), com a cauda de
float (`11144477700154.0`) e com zeros à esquerda perdidos. Sempre uma `str`.

```python
from pure_docs_br import is_valid_caepf, mask_caepf, unmask_caepf

is_valid_caepf("00000002500171")  # True, exemplo oficial do SERPRO
is_valid_caepf("11144477700155")  # False, dígito verificador errado
mask_caepf("11144477700154")  # "111.444.777/001-54"
unmask_caepf("111.444.777/001-54")  # "11144477700154"
```

Casos extremos: sequencial `000` e base de CPF com os 9 dígitos iguais são rejeitados (não há outra
verificação da base). `mask_caepf` devolve o valor sem máscara quando passa de 14 dígitos. Pode
reprovar um CAEPF real e aprovar um número nunca emitido, e a biblioteca não percebe se a Receita
mudar a regra. Não confirma que o CAEPF existe, está ativo, pertence ao titular nem que o CPF-base
está regular; use a consulta oficial no e-CAC.

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
mask_chave_acesso(
    "35231111222333000181550010000000011123456789"
)  # "3523 1111 2223 3300 0181 5500 1000 0000 0111 2345 6789"
unmask_chave_acesso(
    "NFe35231111222333000181550010000000011123456789"
)  # "35231111222333000181550010000000011123456789"
```

Casos extremos: o DV usa o valor `ord(c) - 48` de cada caractere (letras valem 17 a 42), pesos 2 a 9 da
direita para a esquerda; resto 0 ou 1 dá DV 0. `unmask_chave_acesso` mantém dígitos e letras ASCII em
maiúsculas, não completa zeros e descarta dígitos fora de ASCII (largura total). `mask_chave_acesso`
devolve o valor sem máscara quando o tamanho não fecha em 44. Não se valida o CNPJ embutido, a `cUF`
nem o `mod`, nem que o documento existe.

## Boleto de cobrança bancária

O boleto de cobrança tem duas representações: o código de barras, com 44 dígitos (banco 3, moeda 1,
DV geral 1, fator de vencimento 4, valor 10 e campo livre 25), e a linha digitável, com 47 dígitos,
`AAABC.CCCCX DDDDD.DDDDDY EEEEE.EEEEEZ K UUUUVVVVVVVVVV`. O boleto de arrecadação/convênio (48 dígitos,
começa com 8) é outro documento e não é coberto aqui.

Formatos aceitos: a linha digitável com ou sem pontos e espaços, ou o código de barras só com dígitos.
A cauda `.0` de conversão float só é removida de um valor só com dígitos, a forma que uma conversão
float→str produz; um valor com pontos ou espaços nunca foi float. Sempre uma `str`.

```python
from pure_docs_br import is_valid_boleto_cobranca, mask_boleto_cobranca, unmask_boleto_cobranca

is_valid_boleto_cobranca("00191999900000123450000000000000000000000001")  # True, código de barras
is_valid_boleto_cobranca(
    "00190.00009 00000.000000 00000.000018 1 99990000012345"
)  # True, linha digitável
is_valid_boleto_cobranca(
    "00192999900000123450000000000000000000000001"
)  # False, o DV geral correto é 1
mask_boleto_cobranca(
    "00190000090000000000000000000018199990000012345"
)  # "00190.00009 00000.000000 00000.000018 1 99990000012345"
unmask_boleto_cobranca(
    "00190.00009 00000.000000 00000.000018 1 99990000012345"
)  # "00190000090000000000000000000018199990000012345"
```

Casos extremos: os campos 1 a 3 da linha têm DV módulo 10 (soma dos algarismos de cada produto) e o
DV geral é o módulo 11 com pesos 2 a 9 sobre as outras 43 posições; resultado 0, 10 ou 11 vira 1.
`unmask_boleto_cobranca` não completa zeros e descarta dígitos fora de ASCII (largura total).
`mask_boleto_cobranca` só formata a linha de 47 dígitos: um código de barras de 44 sai sem máscara,
assim como qualquer outro tamanho. Não se valida o fator de vencimento, o valor nem a existência do
banco, e a linha não é convertida em código de barras.

## Boleto de arrecadação / convênio

O boleto de arrecadação (contas de consumo e tributos) tem duas representações: o código de barras,
com 44 dígitos, que começa sempre com 8 (produto 1, segmento 1, identificação do valor 1, DV geral 1 e
40 dígitos de valor, empresa/órgão e campo livre), e a linha digitável, com 48 dígitos: quatro blocos de
11 dígitos, cada um seguido do seu DV. O boleto de cobrança bancária (47 dígitos) é outro documento e
não é coberto aqui.

Formatos aceitos: a linha digitável com ou sem hifens e espaços, ou o código de barras só com dígitos.
A cauda `.0` de conversão float só é removida de um valor só com dígitos, a forma que uma conversão
float→str produz; um valor com hifens ou espaços nunca foi float. Sempre uma `str`.

```python
from pure_docs_br import (
    is_valid_boleto_arrecadacao,
    mask_boleto_arrecadacao,
    unmask_boleto_arrecadacao,
)

is_valid_boleto_arrecadacao(
    "81680000001234500000000000000000000000000000"
)  # True, código de barras
is_valid_boleto_arrecadacao(
    "81680000001-9 23450000000-0 00000000000-0 00000000000-0"
)  # True, linha digitável
is_valid_boleto_arrecadacao(
    "81690000001234500000000000000000000000000000"
)  # False, o DV geral correto é 8
mask_boleto_arrecadacao(
    "816800000019234500000000000000000000000000000000"
)  # "81680000001-9 23450000000-0 00000000000-0 00000000000-0"
unmask_boleto_arrecadacao(
    "81680000001-9 23450000000-0 00000000000-0 00000000000-0"
)  # "816800000019234500000000000000000000000000000000"
```

Casos extremos: o 3º dígito escolhe o módulo, 6 ou 7 módulo 10 e 8 ou 9 módulo 11; qualquer outro
valor torna o boleto inválido. No módulo 11, resto 0 ou 1 dá DV 0 e resto 10 dá DV 1 (regra distinta da
cobrança). A linha só é válida quando os quatro DV de bloco conferem e o código de barras reconstruído
dos quatro blocos também é válido. `unmask_boleto_arrecadacao` não completa zeros e descarta dígitos
fora de ASCII (largura total). `mask_boleto_arrecadacao` só formata a linha de 48 dígitos: um código de
barras de 44 sai sem máscara, assim como qualquer outro tamanho. A máscara com hifens é uma convenção de
exibição, não texto da norma. Não se valida segmento, valor nem empresa/órgão.

## Inscrição Estadual (IE)

A Inscrição Estadual identifica o contribuinte do ICMS e é emitida por cada UF, com tamanho, pesos e
regra de dígito verificador próprios (de 8 a 14 dígitos). O número não carrega a UF, então ela é um
argumento obrigatório e nomeado, `str_uf`, com a sigla em maiúsculas. As 27 UFs são suportadas.

Formatos aceitos: com ou sem pontuação e o artefato de float (`110042490114.0`). Sempre uma `str`.

```python
from pure_docs_br import (
    is_valid_inscricao_estadual,
    mask_inscricao_estadual,
    unmask_inscricao_estadual,
)

is_valid_inscricao_estadual("110.042.490.114", str_uf="SP")  # True
is_valid_inscricao_estadual("110042490115", str_uf="SP")  # False, DV2 errado
mask_inscricao_estadual("110042490114", str_uf="SP")  # "110.042.490.114"
unmask_inscricao_estadual("110.042.490.114")  # "110042490114"
```

Casos extremos:

- UF fora das 27 siglas (inclusive minúscula, como `"sp"`) não lança exceção: `is_valid_inscricao_estadual`
  devolve `False`. Atenção: uma UF digitada errado faz toda IE parecer inválida. `mask_inscricao_estadual`
  com UF desconhecida devolve o valor sem máscara.
- `ISENTO` devolve `False`: a literal não é um número, e a aplicação deve tratá-la antes de chamar.
- Qualquer valor com letra é inválido. O produtor rural de SP (`P-...`) está fora de escopo.
- `unmask_inscricao_estadual` mantém só dígitos ASCII e não completa zeros. A cauda `.0` só é
  removida de um valor só com dígitos; um valor pontuado nunca foi float.
- `mask_inscricao_estadual` não confere os dígitos verificadores e devolve o valor sem máscara quando
  o tamanho não é um dos da UF.
- A validação não consulta o cadastro: não diz se a inscrição existe ou está ativa.
- Variantes: BA (8 ou 9 dígitos, módulo 10 ou 11), PE (9 dígitos e-Fisco, ou 14 da numeração antiga),
  RN (9 ou 10), RO (14, ou 9 da numeração anterior a 2000) e GO (faixa 10103105 a 10119997 e a
  inscrição 11094402).
