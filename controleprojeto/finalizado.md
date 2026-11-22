# Histórico de Tarefas Finalizadas (Índice Geral)

Este arquivo funciona como índice mestre de tudo que já foi finalizado no projeto.

> **Regra de Registro:** Sempre que uma alteração, atualização ou etapa do projeto for concluída, deve ser criado um novo arquivo Markdown numerado sequencialmente dentro de [`controleprojeto/finalizado/`](finalizado/) (ex.: `01.md`, `02.md`, `03.md`, ...) contendo obrigatoriamente **data e hora**, o resumo do que foi feito e os arquivos afetados.

---

## Registros Numerados

| Etapa | Data e Hora | Resumo | Arquivo |
| :--- | :--- | :--- | :--- |
| **01** | `17/11/2026 — 16:36 às 22:36` e `18/11/2026 — 10:36` | Estruturação inicial do repositório, fragmentação dos PDFs em `ref/` e diretrizes em `Prompt.md` | [01.md](finalizado/01.md) |
| **02** | `18/11/2026 — 11:36` | Conversão completa e validada de `ref/Tools.pdf` (Capítulo 6: Equipamentos) para `dados/equipamentos.json` via `scripts/gerar_equipamentos_json.py` | [02.md](finalizado/02.md) |
| **03** | `18/11/2026 — 13:31 às 14:05` | Criação da governança em `controleprojeto/`, implantação da pasta `controleprojeto/finalizado/` com logs numerados (`01.md`–`03.md`) e documentação completa no `README.md` | [03.md](finalizado/03.md) |
| **04** | `18/11/2026 — 14:51` | Conversão completa e validada de `ref/Anc Race.pdf` (Capítulos 1 e 2) para `dados/ancestralidades_biografias.json` via `scripts/gerar_ancestralidades_biografias_json.py` | [04.md](finalizado/04.md) |
| **05** | `18/11/2026 — 17:25` | Conversão completa e validada de `ref/Skill sfots.pdf` (Capítulo 4: Perícias) para `dados/pericias.json` via `scripts/gerar_pericias_json.py` | [05.md](finalizado/05.md) |
| **06** | `18/11/2026 — 20:11` | Conversão completa e validada de `ref/Classes 01.pdf` (Introdução do Cap. 3 + Alquimista, Bárbaro, Bardo e Campeão) para `dados/classes01.json` (originalmente `classes.json`) via `scripts/gerar_classes_01_json.py` | [06.md](finalizado/06.md) |
| **07** | `18/11/2026 — 20:41` | Renomeação de `dados/classes.json` para `dados/classes01.json` e conversão completa e validada de `ref/Classes 02.pdf` (Clérigo, Druida, Feiticeiro e Guerreiro) para `dados/classes02.json` via `scripts/gerar_classes_02_json.py` | [07.md](finalizado/07.md) |
| **08** | `18/11/2026 — 21:41` | Conversão completa e validada de `ref/Classes 03.pdf` em três arquivos modulares: `dados/classes03.json` (Ladino, Mago, Monge e Patrulheiro), `dados/companheiros_familiares.json` e `dados/arquetipos_multiclasse.json` | [08.md](finalizado/08.md) |
| **09** | `18/11/2026 — 22:15` | Conversão completa e validada de `ref/Gifts.pdf` (Capítulo 5: Talentos — `17` talentos gerais e `100` talentos de perícia) para `dados/talentos.json` via `scripts/gerar_talentos_json.py` | [09.md](finalizado/09.md) |
| **10** | `18/11/2026 — 23:20` | Conversão completa e validada de `ref/Enchanced 01.pdf` (Capítulo 7: Magias — Parte 1: regras gerais, 4 listas completas A–Z e 220 descrições A–M) para `dados/magias01.json` via `scripts/gerar_magias_01_json.py` | [10.md](finalizado/10.md) |
| **11** | `19/11/2026 — 09:02` | Conversão completa e validada de `ref/Enchacent02.pdf` (Capítulo 7: Magias — Parte 2: `159` descrições M–Z, quadro Servo Invisível, `158` Magias de Foco, Regras/Tabelas de Rituais e `20` Rituais) para `dados/magias02.json` via `scripts/gerar_magias_02_json.py` | [11.md](finalizado/11.md) |
| **12** | `19/11/2026 — 09:19` | Mapeamento completo e validado de `ref/Sheet Update.pdf` (Ficha Oficial de Personagem PF2E, pp. 580–583, incluindo blueprint das 4 páginas, legendas, fórmulas, fontes e `modelo_ficha_vazia`) para `dados/estrutura_ficha.json` via `scripts/gerar_estrutura_ficha_json.py` | [12.md](finalizado/12.md) |
| **13** | `19/11/2026 — 10:54` | Conclusão da Etapa 2: criação e validação cruzada de `38` conceitos procedurais para todas as `12` classes em `dados/conceitos_subclasses.json` via `scripts/gerar_conceitos_subclasses_json.py` | [13.md](finalizado/13.md) |
| **14** | `19/11/2026 — 12:11` | Conclusão da Etapa 3: implementação do motor procedural PF2E (`motor/`, 1º nível com `seed` opcional), API Flask (`app.py`), página simples de teste (`templates/index.html`) e suíte de validação (`scripts/validar_motor_procedural.py`) | [14.md](finalizado/14.md) |
| **15** | `19/11/2026 — 13:43` | Auditoria completa dos `13` JSONs de `dados/`, correção de equipamentos sem proficiência em `conceitos_subclasses.json`, padronização de ações/`passadela_goblin` em `ancestralidades_biografias.json` e alinhamento de schema em `classes03.json` | [15.md](finalizado/15.md) |
| **16** | `19/11/2026 — 14:29` | Conclusão da Etapa 4: Front-End completo da ficha oficial (`templates/index.html`, `static/css/ficha.css`, `static/js/app.js`), exportação `.docx`/`.txt` (`motor/exportacao.py`, `/api/exportar/*`), `requirements.txt` e testes ampliados | [16.md](finalizado/16.md) |
| **17** | `19/11/2026 — 14:39` | Movimentação dos arquivos estáticos (`css` e `js`) para `templates/static/` com ajuste de `static_folder` em `app.py` | [17.md](finalizado/17.md) |
| **18** | `19/11/2026 — 15:06` | Revisão geral de consistência de `escopo.md`, `pendencias.md`, `finalizado.md` e `README.md`, e criação da pasta `controleprojeto/sugestoes/` com roadmap futuro | [18.md](finalizado/18.md) |
| **19** | `19/11/2026 — 17:05` | Criação de `dados/regras_específicas.json` (centralizador de regras específicas e exceções estruturais: PV por nível, acúmulo `Vitalidade` + `Firmeza da Montanha`, morrendo e bônus/penalidades PF2E) via `scripts/gerar_regras_especificas_json.py` | [19.md](finalizado/19.md) |
| **20** | `21/11/2026 — 10:35` | Substituição integral dos `38` conceitos antigos pelos `56` novos conceitos em `dados/conceitos_subclasses.json`, resolução procedural automática Conceito → Subclasse Oficial no `motor/`, suporte a `Instinto do Furor`, `Tese Arcana`, `Fonte de Ferimento` e `Arsenal Monástico`, e prévia detalhada na interface Web | [20.md](finalizado/20.md) |
| **21** | `21/11/2026 — 11:50` | **Etapa 1:** Correção integral de bugs de regras PF2E (`motor/`, `scripts/gerar_conceitos_subclasses_json.py`) e criação da suíte unitária dedicada `scripts/validar_casos_borda_pf2e.py` | [21.md](finalizado/21.md) |
| **22** | `21/11/2026 — 11:50` | **Etapa 2:** Extração das `20` Divindades + `37` Domínios (`dados/divindades.json`) e ativação ponta a ponta de Divindades, Companheiros Animais e Familiares (`motor/companheiros.py`, API, Web e exportadores `.txt`/`.docx`) | [22.md](finalizado/22.md) |
| **23** | `21/11/2026 — 21:55` | Divindade obrigatória apenas para Clérigo/Campeão, eliminação de conflito 2M+Escudo, `Arma Deificada`, efeitos de talentos ancestrais/gerais, limpeza de `magias01/02.json`, padronização ASCII de `regras_especificas.json` e ajustes de exportação/Flask | [23.md](finalizado/23.md) |
| **24** | `22/11/2026 — 00:55` | Opção **Aleatório** nos 7 seletores de criação (Ancestralidade, Herança, Biografia, Classe, Conceito, Divindade e Nível) e exibição de bônus de CA/dano e quantidades nos itens e na CA | [24.md](finalizado/24.md) |
