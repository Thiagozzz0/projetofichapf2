# 03 — Melhorias de Interface (Front-End) e Experiência do Usuário

- **Data da Proposta:** `19/11/2026 — 15:06`
- **Objetivo:** Tornar o uso em mesa de RPG ainda mais prático, interativo e personalizável na camada Web (`templates/` e `templates/static/`).

---

## Sugestões de Interface e Fluxo

### 1. Modais / Tooltips de Consulta Rápida das Regras
- Todos os textos completos de **Talentos, Magias, Armas, Armaduras e Ações de Perícia** já estão estruturados nos JSONs de `dados/`.
- **Melhoria:** expor um endpoint leve (`GET /api/detalhes/<categoria>/<id>`) ou embutir um resumo completo no payload da ficha para que, ao clicar em qualquer talento (ex.: *Ataque Poderoso*), magia (ex.: *Mãos Flamejantes*) ou traço de arma (ex.: *Versátil Pf*), um painel lateral ou modal mostre o **alcance, execução, salvamento, resultados (Sucesso Crítico / Falha)** e regras exatas durante a sessão de jogo.

### 2. Edição Pós-Geração e Customização Narrativa (Página 3)
- Permitir editar diretamente na tela antes de exportar `.docx`/`.txt`/PDF:
  - Campos narrativos da Página 3 (`Etnia`, `Nacionalidade`, `Idade`, `Aparência`, `Atitude`, `Crenças`, `Gostos`, `Aversões`, `Bordões`, `Aliados`, `Inimigos`, `Organizações`);
  - Upload/preview de imagem no quadro **Rascunho do Personagem**;
  - Troca rápida de itens individuais (ex.: trocar uma magia preparada por outra válida da mesma lista, ou comprar equipamento extra com o saldo restante de `po`/`pp`/`pc` descontando automaticamente dinheiro e Volume!).

### 3. Histórico Local / Grimório de Personagens Salvos
- Salvar fichas geradas no `localStorage` do navegador (ou SQLite local em `dados_usuario/`) com nome, classe, conceito e `seed`, permitindo:
  - Abrir fichas antigas com 1 clique;
  - Exportar e importar arquivo `.json` da ficha (backup portátil da mesa);
  - Gerar rapidamente **NPCs ou grupo completo de 4 aventureiros** com um botão ("Gerar Grupo de 4 Personagens").

### 4. Modo de Jogo Interativo ("Ficha Viva" em Mesa)
- Adicionar controles interativos não-destrutivos na ficha aberta para uso em mesa no tablet/notebook:
  - Controle rápido de **PV Atuais / Temporários / Ferido / Morrendo** (`+1`, `-1`, `-5`, Descanso);
  - Caixinhas clicáveis para marcar **Espaços de Magia gastos**, **Pontos de Foco usados** e **Pontos de Heroísmo**;
  - Checkbox **"Escudo Erguido"** que mostra dinamicamente na tela a `CA` atualizada com o bônus do escudo!

### 5. Exportação Direta para PDF e VTT (Foundry VTT)
- Além de `.docx`, `.txt` e Impressão do Navegador (`@media print`):
  - Adicionar botão **"Baixar JSON da Ficha"** e um conversor futuro para o formato de importação do **Foundry VTT (PF2e System)**;
  - Avaliar geração de **PDF preenchido** diretamente sobre o PDF oficial (`ref/Sheet Update.pdf`) ou via engine HTML→PDF para download imediato sem passar pelo diálogo de impressão.
