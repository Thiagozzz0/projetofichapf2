# Pendências do Projeto

Lista viva e priorizada das entregas, melhorias e expansões que ainda precisam ser trabalhadas e finalizadas. Tudo o que já foi concluído encontra-se registrado em [`controleprojeto/finalizado.md`](finalizado.md) e nos logs numerados de [`controleprojeto/finalizado/`](finalizado/).

---

## 1. Validação Final (Navegador / Documentos)

- [ ] **Validação visual interativa em navegador real (`python app.py`)**
  - Conferir layout desktop/mobile, impressão/PDF pelo navegador e abertura real dos arquivos `.docx` e `.pdf` baixados no Microsoft Word / LibreOffice / leitor de PDF.

---

## 2. Melhorias de Interface e Experiência do Usuário (1º Nível)

- [ ] **Histórico Local e Exportação/Importação `.json` da Ficha** *(sugestão de melhoria)*
  - Salvar fichas geradas no `localStorage` do navegador (nome, classe, conceito e `seed`) e permitir baixar/importar o `.json` da ficha para backup ou edição posterior.
- [ ] **Modo "Ficha Viva" em Mesa** *(sugestão de melhoria)*
  - Controles rápidos não-destrutivos na ficha aberta: PV atuais/temporários, caixinhas para Espaços de Magia/Pontos de Foco/Heroísmo e checkbox **"Escudo Erguido"** recalculando a CA dinamicamente na tela.
- [ ] **Gerador de Grupo / NPCs Rápidos (1 clique)** *(sugestão de melhoria)*
  - Botão para gerar rapidamente um grupo completo de 4 aventureiros complementares ou NPCs prontos usando o motor procedural.

---

## 3. Lacunas de Customização (Motor + UI)

- [ ] **Customização de Conceitos pelo Usuário** *(sugestão de melhoria)*
  - Permitir criar e salvar conceitos/nortes próprios (ex.: `dados/conceitos_customizados.json` ou via UI) além dos conceitos padrão.

---

## 4. Refatoração Arquitetural e Qualidade

- [ ] **Validação Automatizada de Contratos Front-End ↔ API** *(sugestão de melhoria)*
  - Ampliar os scripts de validação para checar automaticamente a consistência entre o payload de `/api/opcoes` e os seletores/IDs consumidos pelos módulos JS (`estado.js`, `atributos.js`, `pericias.js`, `talentos.js`, `magias.js`, `equipamentos.js`).

---

## 5. Expansões Futuras (Guia Avançado do Jogador N1–N5 → Níveis 6–20 e Tesouros)

> Detalhamento completo e propostas adicionais estão catalogados em [`controleprojeto/sugestoes/`](sugestoes/README.md).
> **Ordem definida (26/11/2026):** Concluir primeiro a integração completa do **Guia Avançado do Jogador (Níveis 1 a 5)** antes de expandir o motor, front-end e exportadores para os níveis `6` a `20`.

- [ ] **Integração do Guia Avançado do Jogador (Níveis `1` a `5`)** *(Prioridade antes dos Níveis 6+)*
  - **Novas Classes (N1–N5):** Adicionar *Bruxo*, *Espadachim*, *Investigador* e *Oráculo* (tabelas de progressão, características N1–N5, subclasses/patronos/estilos/metodologias/mistérios, talentos até N5, magias de foco/maldições/revelações e novos conceitos procedurais).
  - **Novas Ancestralidades e Heranças Versáteis (N1–N5):** Adicionar as novas ancestralidades e heranças versáteis (com heranças, habilidades especiais, atributos e talentos de ancestralidade de 1º e 5º nível).
  - **Expansões para Conteúdo Existente (N1–N5):** Novas biografias, novas heranças e talentos para as ancestralidades básicas, novas opções de subclasse/talentos N1–N5 para as `12` classes atuais e arquétipos até o 5º nível (slots de classe N2/N4).
  - **Magias, Equipamentos, Talentos Gerais/Perícia e Familiares/Companheiros (N1–N5):** Novos truques e magias até o 3º círculo, novos talentos gerais (`N1`/`N3`) e de perícia (`N1`–`N4`), novas armas/armaduras/equipamentos comuns do livro e novas opções/habilidades de companheiros e familiares.
  - **Front-End, Exportadores & Testes:** Atualizar `/api/opcoes`, interface web, `.txt`/`.docx`/`.pdf` e suíte `tests/` para cobrir todas as novidades do Guia Avançado do Jogador até o 5º nível.

- [ ] **Geração de Fichas Acima do 5º Nível (Níveis `6` a `20`)** *(Níveis `1–5` do Livro Básico concluídos em `25/11/2026` — Etapas 56–58; expansão `N6–N20` será iniciada após o Guia Avançado do Jogador N1–N5)*
  - Expandir `motor/`, Front-End e exportadores além do 5º nível (`regras_atributos.py` com melhorias nos níveis `10/15/20`, incremento de perícias e proficiências acima do 5º nível, talentos e círculos `4–10` de magias).
- [ ] **Itens Mágicos, Runas e Tesouros (`ref/Compendium specific tools.pdf` → `dados/itens_magicos_tesouros.json`)** *(Adiado para implementação futura conforme decisão do usuário em `19/11/2026`)*
  - Converter runas fundamentais e de propriedade, materiais preciosos, itens alquímicos completos, poções, pergaminhos, talismãs e itens mágicos permanentes, e integrá-los ao motor para personagens de nível `2+`.

---

## 6. Gestão de Regras da Casa e Acesso do Mestre

- [ ] **Persistência Global no Servidor (`dados_houserules/config_ativa.json`)** *(opcional / futuro)*
  - Caso deseje que a troca feita pelo Mestre passe a valer automaticamente para todos os dispositivos sem exibir seletor para os jogadores, salvar o estado ativo em `dados_houserules/config_ativa.json`.
