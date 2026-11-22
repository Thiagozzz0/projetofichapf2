# Pendências do Projeto

Lista viva de todas as entregas e tarefas que ainda precisam ser realizadas até a finalização do gerador procedural.

---

## Etapa 1 — Conversão de PDFs (`ref/`) para JSON (`dados/`)

> Regra de trabalho: converter **um arquivo por vez**, com leitura cuidadosa de tabelas, caixas de texto e regras, criando script de geração/validação quando necessário.

- [x] **`ref/Tools.pdf` → `dados/equipamentos.json`** *(Concluído em `18/11/2026 — 11:36` — ver [02.md](finalizado/02.md))*
  - Moedas, Volume, Armaduras, Escudos, Armas, Equipamentos de Aventura, Kits de Classe, Alquímicos, Mágicos, Fórmulas, Serviços, Animais e Tamanhos.
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

- [x] **Definir e estruturar `dados/conceitos_subclasses.json`** *(Concluído em `19/11/2026 — 10:54` → [finalizado/13.md](finalizado/13.md); atualizado em `21/11/2026 — 10:35` → [finalizado/20.md](finalizado/20.md))*
  - Substituído para `56` conceitos ("nortes") cobrindo todas as `12` classes (com descrição, sinergia e resolução procedural da subclasse oficial PF2E mais próxima/exata), prioridade de atributos, biografias recomendadas, perícias/saberes, talentos (Classe, Perícia, Gerais e afinidade ancestral), equipamentos compatíveis com `15 po` e diretrizes de conjuração, validados 1:1 contra todos os JSONs de `dados/`.

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

## Etapa 4 — Interface Front-End (`templates/` & `templates/static/`) e Exportação

- [x] **Tela de Criação do Personagem** *(Concluído em `19/11/2026 — 14:29` → [finalizado/16.md](finalizado/16.md))*
  - Interface responsiva com seleção dinâmica de Ancestralidade & Herança, Biografia (modo Procedural ou Escolha Manual), Classe & Subclasse/Conceito com cartões de resumo, Nome/Jogador, Nível (1º nível ativo com nota de expansão 2–20), Seed e atalhos rápidos.
- [x] **Tela da Ficha Final Pronta para Uso + Exportação `.docx` / `.txt` e `requirements.txt`** *(Concluído em `19/11/2026 — 14:29` → [finalizado/16.md](finalizado/16.md) e [17.md](finalizado/17.md))*
  - Visualizador das 4 páginas oficiais (`pp. 580–583`) com marcadores `[T][E][M][L]`, Pontos de Heroísmo, Escudo de CA, histórico ABCD, `18` linhas de Perícias, Inventário/Volume/Moedas, Ações/Reações, Conjuração e estilos de impressão `@media print`.
  - Endpoints `POST /api/exportar/docx` e `POST /api/exportar/txt` (`motor/exportacao.py`), criação de `requirements.txt` e organização de estáticos em `templates/static/`.

---

## Etapa 5 — Testes e Validação Final

- [x] **Testes integrados ponta a ponta via Flask (`scripts/validar_motor_procedural.py`)** *(Concluído em `19/11/2026 — 14:29` → [finalizado/16.md](finalizado/16.md))*
  - Cobertura de todos os `56` conceitos nas `12` classes, `29` heranças das `6` ancestralidades, `10` casos especiais, `8` endpoints Flask + arquivos estáticos e validação estrutural completa das exportações `.txt` e `.docx` (OOXML/XML).
- [x] **Suíte unitária dedicada de casos de borda matemáticos de PF2E + Correções de Regras PF2E (`scripts/validar_casos_borda_pf2e.py`)** *(Concluído em `21/11/2026 — 11:50` → [finalizado/21.md](finalizado/21.md))*
  - Correção integral de bugs de regras encontrados na auditoria (`idiomas` de Humano e texto descritivo bruto, ações de classe/subclasse na Pág. 3, preservação sem descarte de >2 talentos bônus, consumo de `regras_especificas.json` com `Duro de Matar`/`Carregador Robusto` e isenção de mochila, `Barulhenta`/`Flexível`, `Propulsiva`, `Adaga de Clã` em destreinado, `6` magias N1 no grimório de especialista, golpes de Postura do Monge e `Instinto Animal`), validada pela suíte dedicada.
- [x] **Divindades Reais (`dados/divindades.json`), Companheiros Animais e Familiares (`motor/companheiros.py`)** *(Concluído em `21/11/2026 — 11:50` → [finalizado/22.md](finalizado/22.md))*
  - Extração integral das `20` divindades principais e `37` domínios do Livro Básico (`scripts/gerar_divindades_json.py`), seleção manual/procedural em API/UI, regras de `Simplicidade Mortal` e magias de divindade/domínio, além de geração matemática pronta de Companheiro Animal Jovem e Familiar no motor, interface web e exportadores `.txt`/`.docx`.
- [x] **Revisão Técnica Geral + Divindade Obrigatória/Opcional (`motor/`, `dados/`, `app.py`, UI e exportadores)** *(Concluído em `21/11/2026 — 21:55` → [finalizado/23.md](finalizado/23.md))*
  - Obrigatoriedade de Divindade restrita a `Clérigo` e `Campeão` (UI filtrada e validação HTTP `400`), modo opcional (`Nenhuma` / `Aleatória`) para as demais `10` classes, eliminação de conflito Arma 2M + Escudo, ativação de `Arma Deificada`, efeitos mecânicos de talentos ancestrais/gerais, limpeza de hifenização/tokens em `magias01/02.json`, padronização ASCII de `dados/regras_especificas.json` e melhorias nos exportadores `.txt`/`.docx`.
- [ ] **Validação visual interativa em navegador real (`python app.py`)**
  - Conferir layout desktop/mobile, impressão/PDF pelo navegador e abertura real dos arquivos `.docx` baixados no Microsoft Word / LibreOffice.
- [x] **Atualização do `README.md`** com instruções de instalação (`requirements.txt`) e execução do projeto Flask. *(Concluído em `19/11/2026 — 14:29`)*

---

## Melhorias e Lacunas do 1º Nível (Preparação antes dos Níveis 2–20)

- [x] **Etapa de Perícias (Manual ou Procedural)** *(Concluído em `22/11/2026`)*
  - Aba dedicada antes de Talentos, lendo `dados/pericias.json`, com trava automática do limite de vagas (`Classe + Mod. INT + Herança Perita + Sobreposições + Talentos Ancestrais`).
- [ ] **Escolha Manual de Idiomas Extras**
  - Permitir escolher manualmente os idiomas adicionais concedidos por Inteligência, Ancestralidade e Herança (`motor/biografia_pericias.py`).
- [ ] **Etapa de Magias e Truques para Conjuradores (Manual ou Procedural)**
  - Nova seção na UI (exibida apenas para classes conjuradoras: Bardo, Clérigo, Druida, Feiticeiro e Mago) para escolha manual de truques, repertório ou grimório inicial (`motor/magias.py`).
- [ ] **Personalização de Companheiro Animal / Familiar e Dados Biográficos (Pág. 3)**
  - Permitir escolher manualmente o tipo do Companheiro Animal ou habilidades do Familiar (`motor/companheiros.py`), além de tendência (quando não travada por classe/divindade), idade, gênero, aparência, crenças e anátemas.
- [ ] **Validação de Equipamentos no Back-end e Atalho de Kit de Classe**
  - Espelhar em `motor/equipamentos.py` a validação de Anátema do Druida (sem metal) e proficiências para requisições diretas via API `/api/gerar`.
  - Adicionar botão `+ Kit de <Classe>` na loja de equipamentos consumindo `kits_de_classe` de `dados/equipamentos.json`.
- [ ] **Cruzamento de Pré-requisitos de Perícia nos Talentos da UI**
  - Fazer a Etapa 3 (Talentos) consultar em tempo real as perícias marcadas na Etapa 2 para liberar/bloquear pré-requisitos de perícia na interface.
- [ ] **Refatoração Arquitetural Pré-Níveis 2–20**
  - Modularizar `templates/static/js/app.js` em arquivos menores por responsabilidade (`atributos`, `pericias`, `talentos`, `equipamentos`, `magias`).
  - Desacoplar contratos fixados em 1º nível no motor (`listar_catalogo_talentos_n1`, `magias_n1`, `espacos_nivel_1`, `caracteristicas_classe_n1`, `ORCAMENTO_INICIAL_PC`).
  - Atualizar `controleprojeto/finalizado/` e `melhorias.txt` com as últimas entregas (filtragem de equipamentos por classe e etapa de perícias).

---

## Expansões Futuras (Pós-MVP 1º Nível)

> Detalhamento completo e propostas adicionais estão catalogados em [`controleprojeto/sugestoes/`](sugestoes/README.md).

- [ ] **Geração de Fichas Acima do 1º Nível (Níveis `2` a `20`)** *(solicitado pelo usuário em `19/11/2026`)*
  - Expandir `motor/` (`regras_atributos.py` com melhorias nos níveis `5/10/15/20`, incremento de perícias e proficiências de armas/armaduras/salvamentos/conjuração conforme `tabela_progressao` das 12 classes, seleção de talentos por nível de Classe, Perícia, Geral e Ancestralidade até o 20º nível, além de espaços/repertório/grimório de magias dos círculos `2–10`).
- [ ] **Itens Mágicos, Runas e Tesouros**
  - Retomar conversão de `ref/Compendium specific tools.pdf` → `dados/itens_magicos_tesouros.json` e integrá-lo ao motor para personagens de nível `2+`.
