# Escopo do Projeto — Gerador de Fichas Castles & Crusades (1ª Edição Brasileira)

> Este documento é o norte oficial do módulo **Castles & Crusades** (C&C — 1ª Edição Brasileira com erratas vigentes) dentro do Portal de Fichas RPG.

---

## 1. Visão Geral e Objetivo

Construir um **gerador procedural e montador interativo completo de fichas de personagens para Castles & Crusades (1ª Edição Brasileira)** utilizando **Python + Flask**, seguindo o mesmo padrão de qualidade, rigor matemático e experiência de uso adotado no módulo Pathfinder 2e.

O sistema deve cobrir desde a **definição de Atributos (Primários e Secundários — Sistema SIEGE)** até os **detalhes finais da ficha pronta para mesa** (Classe de Armadura, Pontos de Vida, Bônus de Ataque Base, Habilidades de Raça e Classe, Magias por Círculo, Equipamentos, Carga/Peso, Dinheiro restante e Exportação).

---

## 2. Stack Tecnológica e Estrutura de Pastas (C&C)

- **Backend & Motor de Regras:** Python 3 + Flask (`motor_cc/`, integrado ao `app.py` via rotas `/cc` e `/api/cc/*`).
- **Front-End:** `templates/cc.html`, `static/css/cc.css` e `static/js/cc/`, seguindo estética **Old School (AD&D)** em pergaminho, couro escuro, lacre carmesim e ouro envelhecido (com suporte a Modo Escuro) e design **Mobile-First** otimizado para celulares.
- **Base de Dados em JSON (`dados/dadosc&c/`):** Todas as regras, tabelas, raças, classes, magias, equipamentos e mapeamento da ficha convertidos para arquivos `.json` estruturados e validados.
- **Materiais de Referência (`pdf_fonte/cc/` e `ref/cc/`):**
  - `pdf_fonte/cc/` — Livro completo do Jogador (1ª Edição Brasileira) para referência local (ignorado pelo Git).
  - `ref/cc/` — Recortes temáticos em PDF para conversão gradual, **um arquivo por vez** (ignorado pelo Git).
- **Scripts de Extração e Validação (`scripts/cc/`):** Scripts Python de extração, normalização e validação cruzada dos JSONs em `dados/dadosc&c/` e do motor `motor_cc/`.
- **Testes (`tests/test_cc_*.py`):** Suíte automatizada rodando em `unittest` junto aos demais testes do repositório.
- **Governança (`controleprojeto/cc/`):** `escopo.md`, `pendencias.md`, `finalizado.md`, logs sequenciais em `finalizado/` (`01.md`, `02.md`, ...) e propostas futuras em `sugestoes/`.

---

## 3. Fases Macro de Execução

| Fase | Descrição | Estratégia |
| :--- | :--- | :--- |
| **Fase 0** | Estruturação de Pastas, Governança e Rota `/cc` | Criar `dados/dadosc&c/`, `controleprojeto/cc/`, `ref/cc/`, `pdf_fonte/cc/`, `motor_cc/`, `scripts/cc/`, `static/js/cc/` e tela inicial `/cc`. *(Concluído)* |
| **Fase 1** | Conversão dos PDFs de `ref/cc/` para JSONs em `dados/dadosc&c/` | Um recorte PDF por vez (Atributos/SIEGE, Raças, Classes, Equipamentos, Magias, Ficha), sempre com script gerador e validador em `scripts/cc/`. |
| **Fase 2** | Motor de Regras C&C (`motor_cc/`) e API (`/api/cc/*`) | Regras de atributos (Primários/Secundários, modificadores, rolagens/distribuição), Raças, Classes, PV, CA, Bônus de Ataque, Equipamentos, Carga, Magias e geração procedural/manual com `seed`. |
| **Fase 3** | Interface Web (`/cc`) e Visualização da Ficha | Montador interativo passo a passo + visualização limpa e imprimível da ficha de Castles & Crusades. |
| **Fase 4** | Exportadores (`.txt`, `.docx` e `.pdf`) | Geração de arquivos prontos para mesa (texto, documento editável e PDF preenchido). |
| **Fase 5** | Suíte de Testes Integrados e Casos de Borda C&C | Cobertura completa em `tests/test_cc_*.py` validando matemática, raças, classes, rotas Flask e exportadores. |

---

## 4. Regras Operacionais e Versionamento Git Automático

- **Atributos e Rastreabilidade:** Os 4 modos de geração de atributos (`Old School: 3d6 em ordem`, `Clássico: 3d6`, `Heróico: 4d6` e `Distribuído: 62 pontos`) devem sempre imprimir o método utilizado no cabeçalho da ficha gerada (Web, `.txt`, `.docx` e `.pdf`).
- **Versionamento Automático (espelhado em `AGENTS.md`):** Sempre que qualquer alteração for concluída e validada no projeto, executar automaticamente `git add .`, `git commit -m "<descrição clara do que foi criado/atualizado/alterado>"` e `git push`.
