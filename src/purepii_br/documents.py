"""Runtime registry mapping a document name to its uniform strategy.

Every strategy wraps the public module-level functions of its document and never
reimplements a rule. Documents whose functions need an extra argument (the UF of
``inscricao_estadual`` and ``rg``) are not registered.
"""

from __future__ import annotations

from purepii_br import (
    boleto_arrecadacao,
    boleto_cobranca,
    caepf,
    cep,
    certidao_matricula,
    chave_acesso,
    cnh,
    cnpj,
    cns,
    cpf,
    pis_pasep,
    placa_veiculo,
    processo_cnj,
    renavam,
    titulo_eleitor,
)
from purepii_br.document_strategy import DocumentStrategy


DICT_DOCUMENTS: dict[str, DocumentStrategy] = {
    "boleto_arrecadacao": DocumentStrategy(
        boleto_arrecadacao.is_valid_boleto_arrecadacao,
        boleto_arrecadacao.mask_boleto_arrecadacao,
        boleto_arrecadacao.unmask_boleto_arrecadacao,
    ),
    "boleto_cobranca": DocumentStrategy(
        boleto_cobranca.is_valid_boleto_cobranca,
        boleto_cobranca.mask_boleto_cobranca,
        boleto_cobranca.unmask_boleto_cobranca,
    ),
    "caepf": DocumentStrategy(caepf.is_valid_caepf, caepf.mask_caepf, caepf.unmask_caepf),
    "cep": DocumentStrategy(cep.is_valid_cep, cep.mask_cep, cep.unmask_cep),
    "certidao_matricula": DocumentStrategy(
        certidao_matricula.is_valid_certidao_matricula,
        certidao_matricula.mask_certidao_matricula,
        certidao_matricula.unmask_certidao_matricula,
    ),
    "chave_acesso": DocumentStrategy(
        chave_acesso.is_valid_chave_acesso,
        chave_acesso.mask_chave_acesso,
        chave_acesso.unmask_chave_acesso,
    ),
    "cnh": DocumentStrategy(cnh.is_valid_cnh, cnh.unmask_cnh, cnh.unmask_cnh),
    "cnpj": DocumentStrategy(cnpj.is_valid_cnpj, cnpj.mask_cnpj, cnpj.unmask_cnpj),
    "cns": DocumentStrategy(cns.is_valid_cns, cns.mask_cns, cns.unmask_cns),
    "cpf": DocumentStrategy(cpf.is_valid_cpf, cpf.mask_cpf, cpf.unmask_cpf),
    "pis_pasep": DocumentStrategy(
        pis_pasep.is_valid_pis_pasep, pis_pasep.mask_pis_pasep, pis_pasep.unmask_pis_pasep
    ),
    "placa": DocumentStrategy(
        placa_veiculo.is_valid_placa, placa_veiculo.mask_placa, placa_veiculo.unmask_placa
    ),
    "processo_cnj": DocumentStrategy(
        processo_cnj.is_valid_processo_cnj,
        processo_cnj.mask_processo_cnj,
        processo_cnj.unmask_processo_cnj,
    ),
    "renavam": DocumentStrategy(
        renavam.is_valid_renavam, renavam.unmask_renavam, renavam.unmask_renavam
    ),
    "titulo_eleitor": DocumentStrategy(
        titulo_eleitor.is_valid_titulo_eleitor,
        titulo_eleitor.mask_titulo_eleitor,
        titulo_eleitor.unmask_titulo_eleitor,
    ),
}
