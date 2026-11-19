# Escopo do Projeto — Gerador Procedural de Fichas Pathfinder 2E

> Este documento é o norte oficial do projeto. Todas as etapas de extração de dados, modelagem de regras, desenvolvimento do backend Flask e construção da interface Front-End devem seguir as diretrizes aqui definidas.

---

## 1. Visão Geral e Objetivo

Construir um **gerador procedural completo de fichas de jogadores para Pathfinder 2ª Edição (Livro Básico)** utilizando **Python + Flask**.

O sistema deve abranger desde a **matemática básica dos atributos (sistema ABCD)** até os **últimos detalhes de finalização da ficha** (Classe de Armadura, Pontos de Vida, Testes de Resistência, Percepção, Perícias, Talentos, Magias, Equipamentos, Volume, Dinheiro restante e Ataques calculados), entregando uma ficha pronta para o jogador utilizar em mesa.

---

## 2. Stack Tecnológica e Estrutura de Pastas

- **Backend & Motor de Regras:** Python + **Flask** (`app.py` e módulos auxiliares).
- **Front-End (`templates/`):** Templates HTML/CSS/JS renderizados pelo Flask para o formulário de configuração do personagem e exibição/impressão da ficha final.
- **Base de Dados em JSON (`dados/`):** Todas as regras, tabelas, classes, ancestralidades, heranças, biografias, perícias, talentos, magias, equipamentos e mapeamento da ficha convertidas em arquivos `.json` estruturados e normalizados.
- **Materiais de Referência (`ref/` e `pdf_fonte/`):**
  - `pdf_fonte/P Basic 2.0 Teste_compressed.pdf` (Livro Básico completo comprimido).
  - `ref/` com os recortes temáticos do livro para conversão gradual, **um arquivo por vez**:
    - `ref/Tools.pdf` — Equipamentos (Capítulo 6)
    - `ref/Anc Race.pdf` — Criação, Ancestralidades, Heranças e Biografias
    - `ref/Classes 01.pdf` → `dados/classes01.json` — Classes (Parte 1: Introdução, Alquimista, Bárbaro, Bardo e Campeão)
    - `ref/Classes 02.pdf` → `dados/classes02.json` — Classes (Parte 2: Clérigo, Druida, Feiticeiro e Guerreiro)
    - `ref/Classes 03.pdf` → `dados/classes03.json`, `dados/companheiros_familiares.json` e `dados/arquetipos_multiclasse.json` — Classes (Parte 3: Ladino, Mago, Monge e Patrulheiro), Companheiros Animais/Familiares e Arquétipos Multiclasse
    - `ref/Skill sfots.pdf` — Perícias
    - `ref/Gifts.pdf` → `dados/talentos.json` — Talentos (Capítulo 5: Talentos Gerais e Talentos de Perícia)
    - `ref/Enchanced 01.pdf` → `dados/magias01.json` — Magias (Parte 1: Regras Gerais, Listas Completas e Descrições A–M)
    - `ref/Enchacent02.pdf` → `dados/magias02.json` — Magias (Parte 2: Descrições M–Z, Magias de Foco e complementos)
    - `ref/Compendium specific tools.pdf` — Itens Mágicos e Tesouros
    - `ref/Sheet Update.pdf` — Estrutura da Ficha de Personagem
- **Scripts Auxiliares (`scripts/`):** Scripts Python de extração, normalização e validação dos arquivos JSON em `dados/`.
- **Governança (`controleprojeto/`):** Documentação viva do projeto (`escopo.md`, `pendencias.md`, `finalizado.md`) e registros sequenciais de entregas concluídas em `controleprojeto/finalizado/` (`01.md`, `02.md`, ...), sempre datados com data e hora a cada alteração ou etapa finalizada.

---

## 3. Fluxo de Criação e Geração Procedural do Personagem

A criação do personagem segue a estrutura definida para equilibrar **escolhas do jogador** e **automação procedural inteligente guiada por conceito**:

1. **Ancestralidade e Herança** *(Escolha do usuário)*
   - O usuário seleciona a **Ancestralidade** e sua respectiva **Herança**.
   - Aplica automaticamente: Pontos de Vida ancestrais, Tamanho, Velocidade base, Traços, Idiomas base, Melhorias e Defeitos de atributo (incluindo alocação coerente das melhorias livres ancestrais) e Sentidos (ex.: Visão na Penumbra, Visão no Escuro).

2. **Biografia / Antecedente** *(Escolha do usuário ou Geração Procedural)*
   - O usuário pode **escolher manualmente** uma biografia da lista disponível **ou** optar pela **geração procedural**, que selecionará uma biografia condizente com a classe e o conceito/subclasse escolhidos.
   - Aplica automaticamente: duas melhorias de atributo (uma restrita da biografia + uma livre alocada pelo conceito), treinamento em perícia, Saber específico e Talento de Perícia concedido pela biografia.

3. **Classe e Subclasse / Conceito ("Norte" do Personagem)** *(Escolha do usuário)*
   - O usuário escolhe a **Classe** (dentre as 12 classes do Livro Básico) e define uma **Subclasse / Conceito** que funciona como o norte mecânico e narrativo da ficha (ex.: *Guerreiro → Combatente de 2 Espadas*, *Guerreiro → Arqueiro*, *Guerreiro → Baluarte de Escudo*, *Ladino → Ladrão Acrobata*, *Clérigo → Clérigo de Linha de Frente*, etc.).
   - Esse conceito orienta todas as decisões procedurais subsequentes para garantir sinergia mecânica e fidelidade temática.

4. **Atributos e Melhorias Livres (Sistema ABCD)** *(Cálculo Procedural)*
   - Inicia todos os 6 atributos (**Força, Destreza, Constituição, Inteligência, Sabedoria, Carisma**) em **10**.
   - Soma as etapas **A** (Ancestralidade), **B** (Biografia), **C** (Atributo-chave de Classe) e **D** (4 melhorias livres de 1º nível).
   - Todas as melhorias livres (ancestral, biografia e etapa D) são distribuídas automaticamente de acordo com as prioridades do conceito/subclasse, garantindo um personagem crível, otimizado e sem violações de regra (ex.: máximo de +1 por atributo na mesma etapa e limite de 18 no 1º nível).

5. **Perícias** *(Geração Procedural)*
   - Combina treinamentos fixos de Biografia + Classe com as escolhas livres (`número base da classe + modificador de Inteligência`), priorizando perícias alinhadas ao conceito/subclasse escolhido.

6. **Talentos** *(Geração Procedural)*
   - Seleciona automaticamente talentos válidos (respeitando pré-requisitos de nível, atributo, proficiência e traços) coerentes com o conceito/subclasse para:
     - **Talentos de Ancestralidade**
     - **Talentos de Classe**
     - **Talentos de Perícia**
     - **Talentos Gerais**

7. **Equipamentos, Armas, Armaduras e Moedas** *(Geração Procedural)*
   - Orçamento inicial padrão de **15 po (150 pp / 1.500 pc)**.
   - Seleciona armadura, escudo (se aplicável), armas principais/secundárias e kit de aventura/ferramentas adequados ao conceito/subclasse, respeitando proficiências da classe, limite de Força da armadura, orçamento disponível e cálculo de **Volume** (normal e sobrecarregado).

8. **Magias (Quando Aplicável)** *(Geração Procedural)*
   - Para classes conjuradoras, seleciona tradição mágica, truques mágicos, magias de 1º nível (preparadas, repertório ou grimório inicial) e calcula **CD de Magia** e **Ataque de Magia**, em consonância com o conceito escolhido.

9. **Matemática Final e Ficha Pronta**
   - Calcula e consolida todos os valores finais na ficha:
     - Modificadores de atributo e valores finais;
     - Pontos de Vida totais (`PV ancestral + (PV classe + mod. CON) × nível`);
     - Classe de Armadura (`10 + min(DES, Limite DES) + proficiência + bônus de item`);
     - Testes de Resistência (**Fortitude, Reflexos, Vontade**), **Percepção / Iniciativa** e **CD de Classe**;
     - Bônus de ataque e rolagem de dano de cada arma equipada (incluindo traços como *Acuidade*, *Propulsiva*, *Ágil*, *Duas Mãos*, etc.);
     - Velocidade final (ajustada por penalidades de armadura/escudo/sobrecarga);
     - Inventário detalhado, Volume total/máximo e saldo de moedas restante.

---

## 4. Fases Macro de Execução

| Fase | Descrição | Estratégia |
| :--- | :--- | :--- |
| **Fase 1** | Conversão dos PDFs em `ref/` para JSONs estruturados em `dados/` | Um PDF por vez, com validação numérica e de completude via scripts em `scripts/`. |
| **Fase 2** | Modelagem dos Conceitos/Subclasses (`dados/conceitos_subclasses.json`) | Definir "nortes" claros para cada classe (prioridade de atributos, perícias, talentos, armas/armaduras, magias). |
| **Fase 3** | Motor Procedural e Backend Flask (`app.py` + módulos de regras) | Implementar toda a matemática de PF2E, regras de pré-requisitos e gerador procedural. |
| **Fase 4** | Front-End (`templates/`) | Tela de configuração interativa + visualização completa e imprimível da ficha final. |
| **Fase 5** | Testes Integrados e Refinamento | Validar fichas geradas para múltiplas combinações de ancestralidade, classe e conceito. |
