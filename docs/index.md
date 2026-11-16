# **pure-docs-br** <img src="assets/logo.png" align="right" width="200" style="border-radius: 15px;" alt="pure-docs-br">

Valida, aplica e remove a máscara de CPF e CNPJ, inclusive o CNPJ alfanumérico de 2026. Sem dependências de execução.

---

## Conteúdo

| Seção | Descrição |
|-------|-----------|
| [Uso](usage.md) | Instalação, importações e exemplos de uso |
| [Referência da API](api/index.md) | Funções dos módulos e interface pública |

---

## Início rápido

```bash
bash bin/venv.sh   # cria o venv (o poe vive dentro dele, então o bootstrap é em shell)
poetry run poe unit_tests    # roda a suíte de testes
poetry run poe docs_serve   # serve esta documentação em http://0.0.0.0:8000
```

Se o `poetry` não estiver no `PATH` (por exemplo logo depois de o `bin/venv.sh` instalá-lo com
`--user`), troque `poetry run poe` por `bash bin/poe_exec.sh`: ele encontra o `poe` do venv sem o
`poetry`.

---

Gerado a partir do template **lib-minimal** via [BlueprintX](https://github.com/guilhermegor/BlueprintX).
