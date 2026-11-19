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
