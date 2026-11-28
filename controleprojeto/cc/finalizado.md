# Histórico de Tarefas Finalizadas — Castles & Crusades

Este arquivo funciona como índice mestre de tudo que já foi finalizado no módulo **Castles & Crusades (1ª Edição Brasileira)**.

> **Regra de Registro:** Sempre que uma alteração, extração ou etapa do módulo C&C for concluída, deve ser criado um novo arquivo Markdown numerado sequencialmente dentro de [`finalizado/`](finalizado/) (`01.md`, `02.md`, ...) contendo obrigatoriamente **data e hora**, o resumo do que foi feito e os arquivos afetados.

---

## Registros Numerados

| Etapa | Data e Hora | Resumo | Arquivo |
| :--- | :--- | :--- | :--- |
| **01** | `28/11/2026 — 12:55` | Estruturação inicial do módulo Castles & Crusades: criação de `dados/dadosc&c/`, `controleprojeto/cc/`, `ref/cc/`, `pdf_fonte/cc/`, `motor_cc/`, `scripts/cc/`, `static/js/cc/`, portal `/` e rota `/cc` | [01.md](finalizado/01.md) |
| **02** | `28/11/2026 — 13:05` | Movimentação dos 4 PDFs do C&C para `ref/cc/` e conversão validada de `ref/cc/C&C introdução.pdf` (pp. 7–15) para `dados/dadosc&c/introducao.json` via `scripts/cc/gerar_introducao_json.py` | [02.md](finalizado/02.md) |
| **03** | `28/11/2026 — 13:20` | Conversão validada de `ref/cc/C&C Classes 01.pdf` (pp. 16–39: Bárbaro, Bardo, Cavaleiro, Clérigo e Combatente, níveis 1–24) para `dados/dadosc&c/classes01.json` via `scripts/cc/gerar_classes_01_json.py` | [03.md](finalizado/03.md) |
| **04** | `28/11/2026 — 13:33` | Conversão validada de `ref/cc/C&C classes 02.pdf` (pp. 40–62: Druida, Explorador, Ilusionista e Lutador, níveis 1–24) para `dados/dadosc&c/classes02.json` via `scripts/cc/gerar_classes_02_json.py` | [04.md](finalizado/04.md) |
| **05** | `28/11/2026 — 13:37` | Conversão validada de `ref/cc/C&C classes 03.pdf` (pp. 63–85: Mago, Paladino, Trapaceiro, Assassino + Multiclasse/Classe e Meia, fechando `13/13` classes) para `dados/dadosc&c/classes03.json` via `scripts/cc/gerar_classes_03_json.py` | [05.md](finalizado/05.md) |
| **06** | `28/11/2026 — 14:03` | Conversão validada de `ref/cc/Raças e Tendências.pdf` (pp. 86–103: `7/7` raças com traços, linhagens do Meio-Elfo, idades/altura/peso e `9` combinações de Disposição) para `dados/dadosc&c/racas_tendencias.json` via `scripts/cc/gerar_racas_tendencias_json.py` | [06.md](finalizado/06.md) |
| **07** | `28/11/2026 — 14:14` | Conversão validada de `ref/cc/Equipamentos_e_Sobrecarga_C&C.pdf` (pp. 104–111: `328` itens em 9 tabelas, ouro inicial das 13 classes, sistema de Sobrecarga SB e Obra-Prima) para `dados/dadosc&c/equipamentos.json` via `scripts/cc/gerar_equipamentos_json.py` | [07.md](finalizado/07.md) |
| **08** | `28/11/2026 — 14:46` | Conversão validada de `ref/cc/Magias 01.pdf` (pp. 113–147: regras gerais de magia, `4` listas completas 0–9 com `538` entradas e `75` descrições de feitiços A–C) para `dados/dadosc&c/magias01.json` via `scripts/cc/gerar_magias_01_json.py` | [08.md](finalizado/08.md) |
| **09** | `28/11/2026 — 14:52` | Conversão validada de `ref/cc/Magias 02.pdf` (pp. 148–184: `150` descrições completas de feitiços C–L, `19` reversíveis e `10` tabelas embutidas em 9 feitiços) para `dados/dadosc&c/magias02.json` via `scripts/cc/gerar_magias_02_json.py` | [09.md](finalizado/09.md) |
| **10** | `28/11/2026 — 14:59` | Conversão validada de `ref/cc/Magias 03.pdf` (pp. 185–220: `153` descrições completas L–V, `6` tabelas e nota `Polimorfia`), fechando `378/378` feitiços do Livro do Jogador em `dados/dadosc&c/magias03.json` via `scripts/cc/gerar_magias_03_json.py` | [10.md](finalizado/10.md) |
