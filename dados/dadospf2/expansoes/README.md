# Expansões Modulares (`dados/expansoes/`)

Esta pasta armazena livros e suplementos adicionais do Pathfinder 2E de forma isolada do **Livro Básico** (`dados/*.json`), carregados automaticamente por [`motor/dados.py`](../../motor/dados.py).

## Estrutura de uma Expansão

Cada expansão deve ficar em sua própria subpasta contendo um `manifest.json` e quaisquer arquivos JSON opcionais do conteúdo que ela adiciona:

```text
dados/expansoes/
└── guia_avancado_jogador/
    ├── manifest.json
    ├── classes.json
    ├── ancestralidades_biografias.json
    ├── conceitos_subclasses.json
    ├── talentos.json
    ├── magias.json
    ├── equipamentos.json
    ├── arquetipos.json
    ├── companheiros_familiares.json
    └── divindades.json
```

### Exemplo de `manifest.json`

```json
{
  "id": "guia_avancado_jogador",
  "nome": "Guia Avançado do Jogador",
  "sigla": "GAJ",
  "ativa": true,
  "ordem": 10,
  "descricao": "Classes, ancestralidades, heranças versáteis, arquétipos, talentos, magias e equipamentos do Guia Avançado do Jogador."
}
```

## Recursos Suportados pelo Carregador (`BaseDados`)

- **Ativação seletiva:** `carregar_dados(expansoes_ativas=None)` carrega todas com `"ativa": true`; `expansoes_ativas=()` carrega apenas o Livro Básico; `expansoes_ativas=("guia_avancado_jogador",)` seleciona pacotes específicos.
- **Rastreabilidade:** Todo item carregado recebe automaticamente o campo `"fonte"` (`"livro_basico"` ou o `id` da expansão).
- **Heranças Versáteis:** Chave `"herancas_versateis"` em `ancestralidades_biografias*.json` disponibiliza heranças aplicáveis a qualquer ancestralidade (`dados.herancas_versateis` e `dados.herancas_disponiveis(anc_id)`).
- **Extensão de Conteúdo Existente:**
  - `"extensoes_ancestralidades"` em `ancestralidades_biografias*.json` permite adicionar `herancas` e `talentos_ancestrais` a ancestralidades do Livro Básico.
  - `"extensoes_classes"` em `classes*.json` permite adicionar `subclasses_opcoes`, `talentos_de_classe` e `caracteristicas_de_classe` às 12 classes do Livro Básico.
