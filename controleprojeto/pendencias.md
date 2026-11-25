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

- [x] **Desacoplar Contratos Fixados em 1º Nível no Motor** *(concluído em `25/11/2026` — Etapa 56)*
  - Generalizar funções e constantes presas ao 1º nível (`listar_catalogo_talentos`, `listar_catalogo_magias`, `resumo_conjuracao_classe` com `progressao_por_nivel`, `espacos_por_circulo`, `magias_por_circulo`, `caracteristicas_classe`, `ORCAMENTO_POR_NIVEL_PC`) mantendo aliases `*_n1` retrocompatíveis e preparando a evolução para os níveis `1` a `5`.
- [x] **Avaliador de Pré-requisitos Completo para Níveis 2+** *(concluído até N5 em `25/11/2026` — Etapa 57)*
  - Expandido `atende_prerequisitos()` em `motor/talentos.py` para listas com vírgulas, alternativas `" ou "`, talentos prévios, atributos, esquemas, linhagens, fontes, capacidades de conjuração (`N3+`) e graus `Especialista`/`Mestre`/`Lendário`.
- [ ] **Validação Automatizada de Contratos Front-End ↔ API** *(sugestão de melhoria)*
  - Ampliar os scripts de validação para checar automaticamente a consistência entre o payload de `/api/opcoes` e os seletores/IDs consumidos pelos módulos JS (`estado.js`, `atributos.js`, `pericias.js`, `talentos.js`, `magias.js`, `equipamentos.js`).

---

## 5. Expansões Futuras (Níveis 2–20 e Tesouros)

> Detalhamento completo e propostas adicionais estão catalogados em [`controleprojeto/sugestoes/`](sugestoes/README.md).

- [ ] **Geração de Fichas Acima do 1º Nível (Níveis `2` a `20`)** *(Etapa 2 Níveis 2–5 concluída no motor em `25/11/2026` — Etapa 57; pendente UI/Exportadores N2–N5 e expansão para N6–N20)*
  - Expandir `motor/` (`regras_atributos.py` com melhorias nos níveis `10/15/20`, incremento de perícias e proficiências acima do 5º nível, talentos e círculos `4–10` de magias), além de liberar seleção e exibição de níveis `2–5` no Front-End e exportadores.
- [ ] **Itens Mágicos, Runas e Tesouros (`ref/Compendium specific tools.pdf` → `dados/itens_magicos_tesouros.json`)** *(Adiado para implementação futura conforme decisão do usuário em `19/11/2026`)*
  - Converter runas fundamentais e de propriedade, materiais preciosos, itens alquímicos completos, poções, pergaminhos, talismãs e itens mágicos permanentes, e integrá-los ao motor para personagens de nível `2+`.

---

## 6. Gestão de Regras da Casa e Acesso do Mestre

- [x] **Padrão "Regras da Casa" e Controle por Senha por Alteração (`dados_houserules/acesso_mestre.json`)** *(concluído em `24/11/2026` — Etapa 51)*
  - Site inicia sempre em `Regras da Casa` com o seletor bloqueado, solicita a senha `"9930"` (lida de `dados_houserules/acesso_mestre.json`) via `/api/regras-casa/validar-senha` antes de liberar a escolha e bloqueia novamente após cada troca.
- [ ] **Persistência Global no Servidor (`dados_houserules/config_ativa.json`)** *(opcional / futuro)*
  - Caso deseje que a troca feita pelo Mestre passe a valer automaticamente para todos os dispositivos sem exibir seletor para os jogadores, salvar o estado ativo em `dados_houserules/config_ativa.json`.
