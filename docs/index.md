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
bash bin/poe_exec.sh unit_tests    # roda a suíte de testes
bash bin/poe_exec.sh docs_serve   # serve esta documentação em http://0.0.0.0:8000
```

---

Gerado a partir do template **lib-minimal** via [BlueprintX](https://github.com/guilhermegor/BlueprintX).
