# Instruções Permanentes do Projeto — Portal de Fichas RPG

Este arquivo é carregado automaticamente em toda execução no workspace. Siga estas regras em todas as tarefas:

## 1. Versionamento Git Automático (Obrigatório)

- Sempre que realizar qualquer alteração no projeto (criar, editar, corrigir ou remover arquivos), após validar/testar as mudanças:
  1. Verifique `git status --short` (garantindo que arquivos ignorados/PDFs fonte não estejam expostos).
  2. Execute automaticamente `git add .`.
  3. Faça o `git commit -m "<mensagem>"` com um nome claro e descritivo em português (`pt-BR`) que faça sentido com exatamente o que foi criado, atualizado ou alterado.
  4. Execute `git push` para sincronizar com o repositório remoto.
- Não pergunte antes de commitar ou dar push — essa automação faz parte do fluxo padrão do projeto.

## 2. Isolamento Multi-Sistema (PF2e e Castles & Crusades)

- **Pathfinder 2e (`/pf2`):** `dados/dadospf2/`, `motor_pf2/`, `templates/index.html`, `static/css/ficha.css`, `static/css/tema.css`, `static/js/*.js` (exceto `static/js/cc/`).
- **Castles & Crusades (`/cc`):** `dados/dadosc&c/`, `motor_cc/`, `templates/cc.html`, `static/css/cc.css`, `static/js/cc/*.js`, `scripts/cc/`.
- Alterações em um sistema **nunca** devem quebrar rotas, testes ou estilos do outro. Sempre rode os testes relevantes após edições compartilhadas (`app.py`, `templates/hub.html`, etc.).

## 3. Diretrizes de Castles & Crusades (1ª Ed. Brasileira)

- **Atributos:** Suportar os 4 métodos na criação (`Old School: 3d6 em ordem`, `Clássico: 3d6`, `Heróico: 4d6` e `Distribuído: 62 pontos`), sempre estampando o método escolhido no cabeçalho da ficha (Web, `.txt`, `.docx` e `.pdf`).
- **Identidade Visual e Mobile-First (`/cc`):** Manter estética **Old School / AD&D** (pergaminho quente, couro escuro, lacre carmesim e ouro envelhecido, com suporte ao Modo Escuro) e ergonomia para jogadores de **celular** (alvos de toque `>= 44px`, `font-size: 16px` em inputs mobile, tabelas responsivas e passo inicial enxuto).

## 4. Governança e Ambiente Python

- Registre cada entrega concluída em `controleprojeto/<sistema>/finalizado/` (`XX.md` sequencial com **data e hora**, resumo e arquivos afetados) e mantenha `finalizado.md` e `pendencias.md` atualizados.
- Execute Python e testes sempre pelo ambiente virtual do projeto: `.venv\Scripts\python.exe -m unittest discover tests`.
