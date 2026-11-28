# Controle do Projeto — Portal Multi-Sistemas RPG

Este diretório centraliza a governança, o escopo, as pendências e o histórico de entregas de cada sistema suportado pelo portal (`/`).

## Sistemas

| Sistema | Rota Web | Base de Dados | Motor | Governança |
| :--- | :--- | :--- | :--- | :--- |
| **Pathfinder 2e** | `/pf2` | `dados/dadospf2/` | `motor/` | [escopo.md](pf2/escopo.md) · [pendencias.md](pf2/pendencias.md) · [finalizado.md](pf2/finalizado.md) |
| **Castle and Crusades** *(1ª Ed. Brasileira)* | `/cc` | `dados/dadosc&c/` | `motor_cc/` | [escopo.md](cc/escopo.md) · [pendencias.md](cc/pendencias.md) · [finalizado.md](cc/finalizado.md) |

---

> **Regra de Registro:** Cada sistema mantém sua própria numeração sequencial de entregas concluídas dentro de `controleprojeto/<sistema>/finalizado/` (`01.md`, `02.md`, ...), sempre com data, hora, resumo e arquivos afetados.
