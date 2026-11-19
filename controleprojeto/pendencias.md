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
- **`ref/Enchanced 01.pdf` e `ref/Enchacent02.pdf` → `dados/magias01.json` e `dados/magias02.json`** *(divisão modular do Capítulo 7)*
  - [x] **`ref/Enchanced 01.pdf` → `dados/magias01.json` (Parte 1)** *(Concluído em `18/11/2026 — 23:20` — ver [10.md](finalizado/10.md))*
    - Regras gerais de conjuração (`pp. 297–306`), listas completas das 4 tradições (`Arcana`, `Divina`, `Ocultista`, `Primal` — `779` entradas / `379` únicas), `3` quadros auxiliares e `220` descrições completas de magias (`Abrandar` a `Melhorar Alimentos`, `pp. 316–358`).
  - [x] **`ref/Enchacent02.pdf` → `dados/magias02.json` (Parte 2)** *(Concluído em `19/11/2026 — 09:02` — ver [11.md](finalizado/11.md))*
    - Todas as `159` descrições restantes (`Mensageiro Animal` a `Zona da Verdade`, completando `379/379` com `magias01.json`), quadro `Servo Invisível Criatura –1`, `158` Magias de Foco (`7` classes), regras completas + Tabelas `7–1`/`7–2` e todos os `20` Rituais.
- [ ] **`ref/Compendium specific tools.pdf` → `dados/itens_magicos_tesouros.json`** *(Adiado para implementação futura conforme decisão do usuário em `19/11/2026`)*
  - Runas fundamentais e de propriedade, materiais preciosos, itens alquímicos completos, poções, pergaminhos, talismãs e itens mágicos permanentes.
- [x] **`ref/Sheet Update.pdf` → `dados/estrutura_ficha.json`** *(Concluído em `19/11/2026 — 09:19` → [finalizado/12.md](finalizado/12.md))*
  - Mapeamento completo das 4 páginas oficiais da ficha (`pp. 580–583`), legendas, fórmulas de cálculo, cruzamento 1:1 com `dados/pericias.json` (`18` linhas) e contrato `modelo_ficha_vazia` validado via `scripts/gerar_estrutura_ficha_json.py`.

---

## Etapa 2 — Subclasses / Conceitos Procedurais

- [x] **Definir e estruturar `dados/conceitos_subclasses.json`** *(Concluído em `19/11/2026 — 10:54` → [finalizado/13.md](finalizado/13.md))*
  - Criados `38` conceitos ("nortes") cobrindo todas as `12` classes (incluindo *Mago — Elementalista*, *Guerreiro — Mestre da Espada de Duas Mãos*, entre outros), com prioridade de atributos, biografias recomendadas, perícias/saberes, talentos (Classe, Perícia, Gerais e afinidade ancestral), equipamentos compatíveis com `15 po` e diretrizes de conjuração, validados 1:1 contra todos os JSONs de `dados/`.

---

## Etapa 3 — Motor Procedural e Backend Flask

- [x] **Estruturar módulos Python do gerador (`motor/`)** *(Concluído em `19/11/2026 — 12:11` → [finalizado/14.md](finalizado/14.md))*
  - Carregamento e cache dos arquivos em `dados/*.json` (`motor/dados.py`).
  - Calculadora de atributos (ABCD) respeitando limites e melhorias livres por conceito (`motor/regras_atributos.py`).
  - Gerador procedural/manual de Biografia, Perícias, Idiomas, Talentos e Magias (`motor/biografia_pericias.py`, `motor/talentos.py`, `motor/magias.py`).
  - Comprador procedural de Equipamentos com o dinheiro inicial (`15 po` / `150 pp`), cálculo de Volume, limites de sobrecarga e saldo restante (`motor/equipamentos.py`).
  - Calculadora de estatísticas finais (PV, CA, Resistências, Percepção, Velocidade, CDs, Golpes e Ações) com `seed` opcional (`motor/combate_matematica.py`, `motor/gerador.py`).
- [x] **Implementar aplicação Flask (`app.py` + `templates/index.html` de teste)** *(Concluído em `19/11/2026 — 12:11` → [finalizado/14.md](finalizado/14.md))*
  - Rotas de página inicial (`/`), saúde (`/api/saude`), listagem de opções (`/api/opcoes`), endpoints dinâmicos de heranças e conceitos (`/api/ancestralidades/<id>/herancas`, `/api/classes/<id>/conceitos`) e geração em JSON (`POST /api/gerar`).
  - Página HTML simples de teste (`templates/index.html`) validando a geração de fichas de 1º nível ponta a ponta.

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

---

## Expansões Futuras (Pós-MVP 1º Nível)

- [ ] **Geração de Fichas Acima do 1º Nível (Níveis `2` a `20`)** *(solicitado pelo usuário em `19/11/2026`)*
  - Expandir `motor/` (`regras_atributos.py` com melhorias nos níveis `5/10/15/20`, incremento de perícias e proficiências de armas/armaduras/salvamentos/conjuração conforme `tabela_progressao` das 12 classes, seleção de talentos por nível de Classe, Perícia, Geral e Ancestralidade até o 20º nível, além de espaços/repertório/grimório de magias dos círculos `2–10`).
- [ ] **Itens Mágicos, Runas e Tesouros**
  - Retomar conversão de `ref/Compendium specific tools.pdf` → `dados/itens_magicos_tesouros.json` e integrá-lo ao motor para personagens de nível `2+`.
