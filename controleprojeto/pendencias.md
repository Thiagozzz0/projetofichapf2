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

## 3. Lacunas de Customização do 1º Nível (Motor + UI)

- [ ] **Escolha Manual de Idiomas Extras**
  - Permitir escolher manualmente os idiomas adicionais concedidos por Inteligência, Ancestralidade e Herança (`motor/biografia_pericias.py` + API/UI).
- [ ] **Customização de Conceitos pelo Usuário** *(sugestão de melhoria)*
  - Permitir criar e salvar conceitos/nortes próprios (ex.: `dados/conceitos_customizados.json` ou via UI) além dos `56` conceitos padrão.

---

## 4. Refatoração Arquitetural e Qualidade (Pré-Níveis 2–20)

- [ ] **Desacoplar Contratos Fixados em 1º Nível no Motor**
  - Generalizar funções e constantes presas ao 1º nível (`listar_catalogo_talentos_n1`, `magias_n1`, `espacos_nivel_1`, `caracteristicas_classe_n1`, `ORCAMENTO_INICIAL_PC`) preparando o caminho para evolução de níveis.
- [ ] **Avaliador de Pré-requisitos Completo para Níveis 2+** *(sugestão de melhoria)*
  - Expandir `atende_prerequisitos()` em `motor/talentos.py` para requisitos compostos de nível `2+` (talento prévio, proficiência `Especialista`/`Mestre`/`Lendário` e combinações de atributos).
- [ ] **Validação Automatizada de Contratos Front-End ↔ API** *(sugestão de melhoria)*
  - Ampliar os scripts de validação para checar automaticamente a consistência entre o payload de `/api/opcoes` e os seletores/IDs consumidos pelos módulos JS (`estado.js`, `atributos.js`, `pericias.js`, `talentos.js`, `magias.js`, `equipamentos.js`).

---

## 5. Expansões Futuras (Níveis 2–20 e Tesouros)

> Detalhamento completo e propostas adicionais estão catalogados em [`controleprojeto/sugestoes/`](sugestoes/README.md).

- [ ] **Geração de Fichas Acima do 1º Nível (Níveis `2` a `20`)** *(solicitado pelo usuário em `19/11/2026`)*
  - Expandir `motor/` (`regras_atributos.py` com melhorias nos níveis `5/10/15/20`, incremento de perícias e proficiências de armas/armaduras/salvamentos/conjuração conforme `tabela_progressao` das 12 classes, seleção de talentos por nível de Classe, Perícia, Geral e Ancestralidade até o 20º nível, além de espaços/repertório/grimório de magias dos círculos `2–10`).
- [ ] **Itens Mágicos, Runas e Tesouros (`ref/Compendium specific tools.pdf` → `dados/itens_magicos_tesouros.json`)** *(Adiado para implementação futura conforme decisão do usuário em `19/11/2026`)*
  - Converter runas fundamentais e de propriedade, materiais preciosos, itens alquímicos completos, poções, pergaminhos, talismãs e itens mágicos permanentes, e integrá-los ao motor para personagens de nível `2+`.
git 