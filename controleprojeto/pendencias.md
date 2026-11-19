# Pendências do Projeto

Lista viva de todas as entregas e tarefas que ainda precisam ser realizadas até a finalização do gerador procedural.

---

## Etapa 1 — Conversão de PDFs (`ref/`) para JSON (`dados/`)

> Regra de trabalho: converter **um arquivo por vez**, com leitura cuidadosa de tabelas, caixas de texto e regras, criando script de geração/validação quando necessário.

- [x] **`ref/Anc Race.pdf` → `dados/ancestralidades_biografias.json`** *(Concluído em `18/11/2026 — 14:51` — ver [04.md](finalizado/04.md))*
  - Regras passo a passo de criação de personagem e cálculo de atributos (ABCD).
  - Todas as Ancestralidades básicas (PV, tamanho, velocidade, melhorias/defeitos, idiomas, sentidos, traços especiais).
  - Todas as Heranças de cada ancestralidade.
  - Talentos de Ancestralidade.
  - Todas as Biografias / Antecedentes (melhorias de atributo, perícia treinada, Saber, talento de perícia).
- **`ref/Classes 01–03.pdf` → `dados/classes01.json`, `dados/classes02.json`, `dados/classes03.json`, `dados/companheiros_familiares.json`, `dados/arquetipos_multiclasse.json`** *(divisão modular do Capítulo 3)*
  - [x] **`ref/Classes 01.pdf` → `dados/classes01.json` (Leva 01)** *(Concluído em `18/11/2026 — 20:11`, renomeado em `20:41` — ver [06.md](finalizado/06.md) e [07.md](finalizado/07.md))*
    - Regras gerais de classes, visão geral das 12 classes básicas e dados completos de **Alquimista, Bárbaro, Bardo e Campeão** (`172` talentos de classe, progressões de 20 níveis, subclasses e tabelas).
  - [x] **`ref/Classes 02.pdf` → `dados/classes02.json` (Leva 02)** *(Concluído em `18/11/2026 — 20:41` — ver [07.md](finalizado/07.md))*
    - Dados completos de **Clérigo, Druida, Feiticeiro e Guerreiro** (`197` talentos de classe, progressões de 20 níveis, tabelas de magias por dia, doutrinas, ordens druídicas, 10 linhagens e estilos de combate).
  - [x] **`ref/Classes 03.pdf` → `dados/classes03.json`, `dados/companheiros_familiares.json` e `dados/arquetipos_multiclasse.json` (Leva 03)** *(Concluído em `18/11/2026 — 21:41` — ver [08.md](finalizado/08.md))*
    - Dados completos de **Ladino, Mago, Monge e Patrulheiro** (`204` talentos de classe em `classes03.json`), regras completas de **Companheiros Animais e Familiares** (`8` tipos, `4` estágios, `6` especializações, `12` habilidades de familiar e `6` de mestre em `companheiros_familiares.json`) e **Arquétipos Multiclasse** (`12` arquétipos e `85` talentos em `arquetipos_multiclasse.json`).
- [x] **`ref/Skill sfots.pdf` → `dados/pericias.json`** *(Concluído em `18/11/2026 — 17:25` — ver [05.md](finalizado/05.md))*
  - Lista completa de perícias e atributo associado.
  - Ações destreinadas e treinadas de cada perícia, graus de proficiência (Destreinado, Treinado, Especialista, Mestre, Lendário) e regras de Saber.
- [x] **`ref/Gifts.pdf` → `dados/talentos.json`** *(Concluído em `18/11/2026 — 22:15` — ver [09.md](finalizado/09.md))*
  - Talentos Gerais e Talentos de Perícia (`117` talentos completos: `17` da Tabela 5–1 e `100` em `18` grupos da Tabela 5–2, com nível, pré-requisitos, traços, ações, resultados e efeitos).
- [ ] **`ref/Enchacent.pdf` → `dados/magias.json`**
  - Regras de conjuração, tradições mágicas (Arcana, Divina, Ocultista, Primal), listas de truques e magias por círculo, magias de foco e descrições completas.
- [ ] **`ref/Compendium specific tools.pdf` → `dados/itens_magicos_tesouros.json`**
  - Runas fundamentais e de propriedade, materiais preciosos, itens alquímicos completos, poções, pergaminhos, talismãs e itens mágicos permanentes.
- [ ] **`ref/Sheet Update.pdf` → `dados/estrutura_ficha.json`**
  - Mapeamento completo de todos os campos e blocos da ficha oficial de personagem de PF2E para garantir 100% de aderência no Front-End e na saída do gerador.

---

## Etapa 2 — Subclasses / Conceitos Procedurais

- [ ] **Definir e estruturar `dados/conceitos_subclasses.json`**
  - Criar os conceitos ("nortes") disponíveis para cada uma das 12 classes (ex.: *Guerreiro — Combatente de 2 Espadas*, *Guerreiro — Arqueiro*, *Guerreiro — Escudeiro*, *Guerreiro — Arma Pesada*, etc.).
  - Mapear para cada conceito: prioridade de atributos livres, biografias mais condizentes, perícias prioritárias, talentos recomendados por categoria, loadout de equipamentos/armas/armadura compatível com 15 po e magias preferenciais (quando conjurador).

---

## Etapa 3 — Motor Procedural e Backend Flask

- [ ] **Estruturar módulos Python do gerador**
  - Carregamento e cache dos arquivos em `dados/*.json`.
  - Calculadora de atributos (ABCD) respeitando limites e melhorias livres por conceito.
  - Gerador procedural de Biografia (opcional quando o usuário não escolher manualmente), Perícias, Talentos (Ancestralidade, Classe, Perícia, Geral) e Magias.
  - Comprador procedural de Equipamentos com o dinheiro inicial (`15 po` / `150 pp`), cálculo de Volume, limites de sobrecarga e saldo restante.
  - Calculadora de estatísticas finais (PV, CA, Resistências, Percepção, Velocidade, CDs e Ataques/Danos de armas).
- [ ] **Implementar aplicação Flask (`app.py`)**
  - Rotas de página inicial, seleção dinâmica (Ancestralidade/Herança, Biografia manual ou procedural, Classe e Subclasse/Conceito) e geração/exibição da ficha final.
  - Endpoints JSON (API) para carregar opções dinâmicas no Front-End (ex.: listar heranças da ancestralidade escolhida, listar conceitos da classe escolhida).

---

## Etapa 4 — Interface Front-End (`templates/`)

- [ ] **Tela de Criação do Personagem**
  - Interface limpa e intuitiva com seleção de Ancestralidade & Herança, Biografia (modo Procedural ou Escolha Manual), Classe & Subclasse/Conceito e opção de nível/nome do personagem.
- [ ] **Tela da Ficha Final Pronta para Uso**
  - Layout completo inspirado na ficha oficial de Pathfinder 2E (com base em `Sheet Update.pdf`), exibindo atributos, modificadores, CA, PV, resistências, ataques prontos, perícias, talentos, magias, inventário/volume e resumo narrativo, pronta para jogar ou imprimir.

---

## Etapa 5 — Testes e Validação Final

- [ ] **Testes automatizados das regras matemáticas de PF2E** (cálculo de atributos, CA com Limite de Destreza, penalidades de armadura e sobrecarga, proficiências e bônus de ataque/dano).
- [ ] **Testes de geração ponta a ponta** cobrindo todas as 12 classes e múltiplas ancestralidades via Flask.
- [ ] **Atualização do `README.md`** com instruções de instalação e execução do projeto Flask.
