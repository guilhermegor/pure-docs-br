@AGENTS.md

Edit AGENTS.md, not this file. Claude-Code-only lines go below this one.

## Convenção da página Uso

Cada novo módulo de documento adiciona a sua própria seção `##` em `docs/usage.md`, depois da
última (ordem: CPF, CNPJ, CEP, ...). A seção traz uma frase sobre o documento, os formatos
aceitos, um exemplo de `is_valid_*` / `mask_*` / `unmask_*` com a API pública real e os casos
extremos. Conteúdo de contribuidor (testes, lint, release) fica em `docs/contributing.md`.
