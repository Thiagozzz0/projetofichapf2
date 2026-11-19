# Gerador Procedural de Fichas — Pathfinder 2E (Flask)

Projeto em **Python + Flask** para geração procedural completa de fichas de jogadores de **Pathfinder 2ª Edição (Livro Básico)** — indo desde a matemática básica dos atributos (sistema ABCD) até todos os detalhes finais (equipamentos, cálculo de volume, classe de armadura, pontos de vida, ataques, perícias, talentos e magias), entregando a ficha pronta para o jogador usar.

---

## 1. Conceito e Fluxo de Criação Procedural

O sistema combina escolhas principais do jogador com automação procedural guiada por **Subclasse / Conceito ("norte" do personagem)** para garantir fichas mecanicamente válidas, coerentes e prontas para jogo:

1. **Ancestralidade e Herança** *(Escolha do usuário)*
   - Aplica PV base, tamanho, velocidade, traços, idiomas, sentidos e melhorias/defeitos ancestrais de atributo.
2. **Biografia / Antecedente** *(Escolha manual ou Geração Procedural)*
   - O jogador pode escolher manualmente uma biografia ou deixar o sistema gerar uma opção condizente com a classe e o conceito do personagem.
3. **Classe e Subclasse / Conceito ("Norte")** *(Escolha do usuário)*
   - O jogador escolhe uma das 12 classes básicas e um conceito de build/atuação (ex.: *Guerreiro → Combatente de 2 Espadas*, *Guerreiro → Arqueiro*, *Guerreiro → Escudeiro*, etc.).
4. **Atributos e Melhorias Livres (ABCD)** *(Cálculo Procedural)*
   - Aplica base 10 + Ancestralidade (**A**) + Biografia (**B**) + Classe (**C**) + 4 melhorias livres (**D**), alocando as melhorias livres de forma crível e otimizada para o conceito escolhido.
5. **Perícias e Talentos** *(Geração Procedural)*
   - Seleciona perícias treinadas e talentos (**Ancestralidade, Classe, Perícia e Gerais**) respeitando pré-requisitos e em sinergia com o conceito.
6. **Equipamentos e Magias** *(Geração Procedural)*
   - Compra armas, armadura, escudo e equipamentos iniciais dentro do orçamento de **15 po (150 pp / 1.500 pc)**, calcula Volume/Sobrecarga e, para conjuradores, define tradição, truques e magias iniciais.
7. **Matemática Final da Ficha**
   - Consolida PV, CA, Testes de Resistência, Percepção, CDs, bônus de ataque/dano por arma, velocidade final e inventário pronto para uso na interface Web.

---

## 2. Estrutura de Pastas do Projeto

```text
.
├── app.py                        # Aplicação principal Flask (rotas e interface Web)
├── Prompt.md                     # Contexto e direcionamento inicial do projeto
├── README.md                     # Documentação geral do projeto e governança
├── controleprojeto/              # Gestão e rastreabilidade das entregas
│   ├── escopo.md                 # Escopo completo do início ao fim (norte do projeto)
│   ├── pendencias.md             # Lista de tarefas e conversões ainda pendentes
│   ├── finalizado.md             # Índice geral de entregas concluídas
│   └── finalizado/               # Logs individuais numerados (01.md, 02.md, ...) com data e hora
├── dados/                        # Regras e tabelas do PF2E convertidas em JSON
│   ├── ancestralidades_biografias.json  # Capítulos 1 e 2 (Criação, Ancestralidades, Heranças, Biografias e Idiomas)
│   ├── arquetipos_multiclasse.json      # Capítulo 3 (Regras de Arquétipos e 12 Arquétipos Multiclasse / 85 talentos)
│   ├── classes01.json            # Capítulo 3 (Leva 01: Introdução + Alquimista, Bárbaro, Bardo e Campeão)
│   ├── classes02.json            # Capítulo 3 (Leva 02: Clérigo, Druida, Feiticeiro e Guerreiro)
│   ├── classes03.json            # Capítulo 3 (Leva 03: Ladino, Mago, Monge e Patrulheiro)
│   ├── companheiros_familiares.json     # Capítulo 3 (Companheiros Animais e Familiares)
│   ├── equipamentos.json         # Capítulo 6 completo (Equipamentos) convertido e validado
│   └── pericias.json             # Capítulo 4 completo (Perícias, Ações Gerais e Tabelas 4–1 a 4–4)
├── pdf_fonte/                    # PDF completo comprimido do Livro Básico PF2E
├── ref/                          # PDFs fragmentados por categoria para conversão gradual
├── scripts/                      # Scripts Python de geração, extração e validação de JSONs
│   ├── gerar_ancestralidades_biografias_json.py
│   ├── gerar_arquetipos_multiclasse_json.py
│   ├── gerar_classes_01_json.py
│   ├── gerar_classes_02_json.py
│   ├── gerar_classes_03_json.py
│   ├── gerar_companheiros_familiares_json.py
│   ├── gerar_equipamentos_json.py
│   └── gerar_pericias_json.py
└── templates/                    # Front-End HTML/CSS/JS renderizado pelo Flask
```

---

## 3. Sistema de Registro e Controle de Alterações (`controleprojeto/`)

Para manter rastreabilidade total da evolução do projeto e evitar desvios durante o desenvolvimento, toda a documentação viva fica centralizada em [`controleprojeto/`](controleprojeto/):

- **[`controleprojeto/escopo.md`](controleprojeto/escopo.md):** Documento-mestre com o escopo completo, fluxo de regras, arquitetura e fases do projeto.
- **[`controleprojeto/pendencias.md`](controleprojeto/pendencias.md):** Checklist de todas as etapas pendentes (conversões de PDF para JSON, modelagem de conceitos, backend Flask, templates e testes).
- **[`controleprojeto/finalizado.md`](controleprojeto/finalizado.md):** Índice cronológico geral das entregas já concluídas.
- **[`controleprojeto/finalizado/`](controleprojeto/finalizado/):** Pasta dedicada para o registro individual de **cada alteração, atualização ou etapa finalizada** no projeto.
  - **Padrão de nomenclatura:** Arquivos Markdown numerados sequencialmente (`01.md`, `02.md`, `03.md`, ...).
  - **Conteúdo obrigatório em cada arquivo:**
    - **Data e hora** exatas da conclusão da alteração/etapa;
    - **Resumo objetivo** do que foi implementado ou alterado;
    - **Arquivos criados/modificados** e validações executadas.

> Sempre que uma nova parte do projeto for concluída, um novo arquivo `XX.md` deve ser criado em `controleprojeto/finalizado/` e referenciado no índice `controleprojeto/finalizado.md` (atualizando também `controleprojeto/pendencias.md`).

---

## 4. Status de Conversão dos Dados (`ref/` → `dados/`)

Os PDFs de referência estão sendo convertidos **um por vez** para garantir fidelidade às tabelas, caixas de texto e regras do Pathfinder 2E:

| PDF de Origem (`ref/`) | Destino JSON (`dados/`) | Conteúdo | Status |
| :--- | :--- | :--- | :--- |
| `ref/Tools.pdf` | `dados/equipamentos.json` | Moedas, Volume, Armaduras, Escudos, Armas, Equipamentos de Aventura, Kits de Classe, Alquímicos, Mágicos, Fórmulas, Serviços, Animais e Tamanhos | Concluído (`02.md`) |
| `ref/Anc Race.pdf` | `dados/ancestralidades_biografias.json` | Regras de criação, Ancestralidades, Heranças, Talentos de Ancestralidade e Biografias | Concluído (`04.md`) |
| `ref/Classes 01.pdf` | `dados/classes01.json` | Regras gerais do Cap. 3, visão geral das 12 classes e dados completos de Alquimista, Bárbaro, Bardo e Campeão (`172` talentos) | Concluído (`06.md` / `07.md`) |
| `ref/Classes 02.pdf` | `dados/classes02.json` | Dados completos de Clérigo, Druida, Feiticeiro e Guerreiro (`197` talentos) | Concluído (`07.md`) |
| `ref/Classes 03.pdf` | `dados/classes03.json`, `dados/companheiros_familiares.json`, `dados/arquetipos_multiclasse.json` | Dados completos de Ladino, Mago, Monge e Patrulheiro (`204` talentos), Companheiros Animais/Familiares e Arquétipos Multiclasse (`12` arquétipos, `85` talentos) | Concluído (`08.md`) |
| `ref/Skill sfots.pdf` | `dados/pericias.json` | Perícias, ações treinadas/destreinadas e graus de proficiência | Concluído (`05.md`) |
| `ref/Gifts.pdf` | `dados/talentos.json` | Talentos Gerais e Talentos de Perícia | Pendente |
| `ref/Enchacent.pdf` | `dados/magias.json` | Tradições mágicas, magias e magias de foco | Pendente |
| `ref/Compendium specific tools.pdf` | `dados/itens_magicos_tesouros.json` | Runas, materiais preciosos, itens alquímicos completos e tesouros | Pendente |
| `ref/Sheet Update.pdf` | `dados/estrutura_ficha.json` | Mapeamento dos campos oficiais da ficha de jogador | Pendente |

---

## 5. Como Regenerar e Validar os Dados Atuais

Com **Python 3** instalado, é possível regenerar e validar a integridade dos arquivos JSON executando:

```bash
python scripts/gerar_equipamentos_json.py
python scripts/gerar_ancestralidades_biografias_json.py
python scripts/gerar_pericias_json.py
python scripts/gerar_classes_01_json.py
python scripts/gerar_classes_02_json.py
python scripts/gerar_classes_03_json.py
python scripts/gerar_companheiros_familiares_json.py
python scripts/gerar_arquetipos_multiclasse_json.py
```

Os scripts verificam todas as contagens das tabelas dos respectivos capítulos, unicidade de IDs e integridade estrutural dos dados.
