# 01 — Evolução para Geração de Fichas do 2º ao 20º Nível

- **Data da Proposta:** `19/11/2026 — 15:06`
- **Contexto Atual:** O motor em `motor/` (`gerador.py`, `regras_atributos.py`, `talentos.py`, `magias.py`) já foi estruturado recebendo `nivel`, mas está travado em `nivel == 1` (`ErroValidacao`). Todos os dados até o **20º nível** (`tabela_progressao`, talentos até N20, magias até 10º círculo e arquétipos multiclasse) já existem convertidos na pasta `dados/`.

---

## O que precisa ser implementado para liberar Níveis `2` a `20`

### 1. Progressão de Atributos (`motor/regras_atributos.py`)
- Aplicar os **4 incrementos de atributo** nos níveis **5, 10, 15 e 20**, seguindo `prioridade_atributos` do conceito.
- Respeitar a regra PF2E já codificada em `_aplicar_melhoria`: `+2` se o valor for `< 18` e `+1` se `>= 18` (removendo `teto_n1 = 18` após o 1º nível).
- Registrar cada bloco (`N5`, `N10`, `N15`, `N20`) em `historico_abcd`.

### 2. Escalonamento de Proficiências via `tabela_progressao` (`dados/classes01..03.json`)
- Ler os marcos da `tabela_progressao` de cada classe até `nivel`:
  - **Incremento de Perícias** (níveis 3, 5, 7, ..., 19 — e todo nível a partir do 2º para **Ladino**): evoluir `treinado → especialista` (a partir do N3), `especialista → mestre` (N7) e `mestre → lendário` (N15), priorizando `conceito["pericias_prioritarias"]`.
  - **Salvamentos, Percepção, Armaduras, Armas, CD de Classe e Conjuração:** atualizar automaticamente os graus (`Especialidade em Armas`, `Resolução`, `Vontade de Ferro`, `Percepção Aguda`, etc.).
  - **Especialização em Armas e Armaduras:** calcular bônus de dano de especialização de arma (`+2` / `+3` / `+4` / `+6` / `+8` conforme grau e nível) e efeitos de especialização crítica/armadura no bloco de combate.

### 3. Seleção de Talentos por Nível (`motor/talentos.py`)
- Preencher dinamicamente os slots da **Página 2** já mapeados em `dados/estrutura_ficha.json`:
  - **Ancestralidade:** níveis `5`, `9`, `13`, `17`;
  - **Classe:** níveis pares `2, 4, 6, ..., 20` (priorizando `talentos_recomendados["classe_nivel_2_mais"]` e pontuando os demais por afinidade/traços + validação completa de pré-requisitos);
  - **Perícia:** níveis pares `2, 4, 6, ..., 20` (todo nível para Ladino);
  - **Gerais:** níveis `3, 7, 11, 15, 19`.
- **Integração com `dados/arquetipos_multiclasse.json`:** permitir opcionalmente ao usuário escolher um **Arquétipo Multiclasse** (usando os 85 talentos já convertidos) consumindo slots de talento de classe a partir do 2º nível.

### 4. Conjuração de Círculos `2–10` (`motor/magias.py`)
- Ler `espacos_por_circulo` completos da tabela de magias por dia de cada classe (até 10º círculo).
- Selecionar magias de círculos `2–10` (e versões **Elevadas**) mantendo coerência temática com `tracos_prioritarios` e `escolas_prioritarias` do conceito.
- Expandir o frontend (`templates/index.html` e `app.js`) e os exportadores (`.docx`/`.txt`) para agrupar magias por círculo (`1º` a `10º`).

### 5. Riqueza por Nível e Itens Mágicos (`ref/Compendium specific tools.pdf`)
- Retomar a conversão de `ref/Compendium specific tools.pdf` → `dados/itens_magicos_tesouros.json`.
- Aplicar tabela oficial de riqueza/itens para personagens criados acima do 1º nível (armas `+1/+2/+3` e `Impactante`, runas de potência/resiliência em armaduras, controle do limite de **10 itens investidos** já mapeado na Página 2 da ficha).
