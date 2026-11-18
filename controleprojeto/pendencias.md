# Pendências do Projeto

Lista viva de todas as entregas e tarefas que ainda precisam ser realizadas até a finalização do gerador procedural.

---

## Etapa 1 — Conversão de PDFs (`ref/`) para JSON (`dados/`)

> Regra de trabalho: converter **um arquivo por vez**, com leitura cuidadosa de tabelas, caixas de texto e regras, criando script de geração/validação quando necessário.

- [ ] **`ref/Anc Race.pdf` → `dados/ancestralidades_biografias.json`**
  - Regras passo a passo de criação de personagem e cálculo de atributos (ABCD).
  - Todas as Ancestralidades básicas (PV, tamanho, velocidade, melhorias/defeitos, idiomas, sentidos, traços especiais).
  - Todas as Heranças de cada ancestralidade.
  - Talentos de Ancestralidade.
  - Todas as Biografias / Antecedentes (melhorias de atributo, perícia treinada, Saber, talento de perícia).
- [ ] **`ref/Class Multi.pdf` → `dados/classes.json`**
  - Todas as 12 Classes do Livro Básico (Alquimista, Bárbaro, Bardo, Campeão, Clérigo, Druida, Feiticeiro, Guerreiro, Ladino, Mago, Monge, Patrulheiro).
  - Atributo-chave, PV por nível, proficiências iniciais (Percepção, Fortitude, Reflexos, Vontade, Perícias, Ataques, Defesas, CD de Classe), tabela de progressão, características de classe, subclasses oficiais da classe (doutrinas, linhagens, instintos, etc.), talentos de classe e arquétipos multiclasse.
- [ ] **`ref/Skill sfots.pdf` → `dados/pericias.json`**
  - Lista completa de perícias e atributo associado.
  - Ações destreinadas e treinadas de cada perícia, graus de proficiência (Destreinado, Treinado, Especialista, Mestre, Lendário) e regras de Saber.
- [ ] **`ref/Gifts.pdf` → `dados/talentos.json`**
  - Talentos Gerais e Talentos de Perícia (nível, pré-requisitos, traços, frequência/ações e efeitos).
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
