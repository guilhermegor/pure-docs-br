"""pure-docs-br package.

Every ``is_valid_*``, ``mask_*`` and ``unmask_*`` function shares one bad-input contract: a
non-``str`` (``None``, ``float``/``NaN``) raises ``TypeError`` from the runtime type checker,
while any ``str`` never raises because of its value. Stringify or drop nulls first.
"""

from importlib.metadata import PackageNotFoundError, version

from .boleto_arrecadacao import (
    is_valid_boleto_arrecadacao,
    mask_boleto_arrecadacao,
    unmask_boleto_arrecadacao,
)
from .boleto_cobranca import (
    is_valid_boleto_cobranca,
    mask_boleto_cobranca,
    unmask_boleto_cobranca,
)
from .caepf import is_valid_caepf, mask_caepf, unmask_caepf
from .cep import is_valid_cep, mask_cep, unmask_cep
from .certidao_matricula import (
    is_valid_certidao_matricula,
    mask_certidao_matricula,
    unmask_certidao_matricula,
)
from .chave_acesso import is_valid_chave_acesso, mask_chave_acesso, unmask_chave_acesso
from .cnh import is_valid_cnh, mask_cnh, unmask_cnh
from .cnpj import is_valid_cnpj, mask_cnpj, unmask_cnpj
from .cns import is_valid_cns, mask_cns, unmask_cns
from .cpf import is_valid_cpf, mask_cpf, unmask_cpf
from .inscricao_estadual import (
    is_valid_inscricao_estadual,
    mask_inscricao_estadual,
    unmask_inscricao_estadual,
)
from .pis_pasep import is_valid_pis_pasep, mask_pis_pasep, unmask_pis_pasep
from .placa_veiculo import is_valid_placa, mask_placa, unmask_placa
from .processo_cnj import is_valid_processo_cnj, mask_processo_cnj, unmask_processo_cnj
from .renavam import is_valid_renavam, mask_renavam, unmask_renavam
from .rg import is_valid_cin, is_valid_rg, unmask_rg
from .titulo_eleitor import (
    is_valid_titulo_eleitor,
    mask_titulo_eleitor,
    unmask_titulo_eleitor,
)


try:
    __version__ = version("pure-docs-br")
except PackageNotFoundError:  # pragma: no cover - source tree without an installed dist
    __version__ = "0.0.0"


__all__ = [
    "__version__",
    "is_valid_boleto_arrecadacao",
    "is_valid_boleto_cobranca",
    "is_valid_caepf",
    "is_valid_cep",
    "is_valid_certidao_matricula",
    "is_valid_chave_acesso",
    "is_valid_cin",
    "is_valid_cnh",
    "is_valid_cnpj",
    "is_valid_cns",
    "is_valid_cpf",
    "is_valid_inscricao_estadual",
    "is_valid_pis_pasep",
    "is_valid_placa",
    "is_valid_processo_cnj",
    "is_valid_renavam",
    "is_valid_rg",
    "is_valid_titulo_eleitor",
    "mask_boleto_arrecadacao",
    "mask_boleto_cobranca",
    "mask_caepf",
    "mask_cep",
    "mask_certidao_matricula",
    "mask_chave_acesso",
    "mask_cnh",
    "mask_cnpj",
    "mask_cns",
    "mask_cpf",
    "mask_inscricao_estadual",
    "mask_pis_pasep",
    "mask_placa",
    "mask_processo_cnj",
    "mask_renavam",
    "mask_titulo_eleitor",
    "unmask_boleto_arrecadacao",
    "unmask_boleto_cobranca",
    "unmask_caepf",
    "unmask_cep",
    "unmask_certidao_matricula",
    "unmask_chave_acesso",
    "unmask_cnh",
    "unmask_cnpj",
    "unmask_cns",
    "unmask_cpf",
    "unmask_inscricao_estadual",
    "unmask_pis_pasep",
    "unmask_placa",
    "unmask_processo_cnj",
    "unmask_renavam",
    "unmask_rg",
    "unmask_titulo_eleitor",
]
