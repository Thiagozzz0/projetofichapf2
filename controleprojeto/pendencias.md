# Pendências do Projeto

Lista viva apenas das entregas e tarefas que ainda precisam ser trabalhadas e finalizadas. Tudo o que já foi concluído encontra-se registrado em [`controleprojeto/finalizado.md`](finalizado.md) e nos logs numerados de [`controleprojeto/finalizado/`](finalizado/).

---

## Validação Final (Navegador / Documentos)

- [ ] **Validação visual interativa em navegador real (`python app.py`)**
  - Conferir layout desktop/mobile, impressão/PDF pelo navegador e abertura real dos arquivos `.docx` baixados no Microsoft Word / LibreOffice.

---

## Melhorias e Lacunas do 1º Nível (Preparação antes dos Níveis 2–20)

- [ ] **Escolha Manual de Idiomas Extras**
  - Permitir escolher manualmente os idiomas adicionais concedidos por Inteligência, Ancestralidade e Herança (`motor/biografia_pericias.py`).
- [ ] **Personalização de Companheiro Animal / Familiar e Dados Biográficos (Pág. 3)**
  - Permitir escolher manualmente o tipo do Companheiro Animal ou habilidades do Familiar (`motor/companheiros.py`), além de tendência (quando não travada por classe/divindade), idade, gênero, aparência, crenças e anátemas.
- [ ] **Atalho de Kit de Classe na Loja de Equipamentos**
  - Adicionar botão `+ Kit de <Classe>` na loja de equipamentos consumindo `kits_de_classe` de `dados/equipamentos.json`.
- [ ] **Refatoração Arquitetural Pré-Níveis 2–20**
  - Desacoplar contratos fixados em 1º nível no motor (`listar_catalogo_talentos_n1`, `magias_n1`, `espacos_nivel_1`, `caracteristicas_classe_n1`, `ORCAMENTO_INICIAL_PC`).

---

## Expansões Futuras (Pós-MVP 1º Nível)

> Detalhamento completo e propostas adicionais estão catalogados em [`controleprojeto/sugestoes/`](sugestoes/README.md).

- [ ] **Geração de Fichas Acima do 1º Nível (Níveis `2` a `20`)** *(solicitado pelo usuário em `19/11/2026`)*
  - Expandir `motor/` (`regras_atributos.py` com melhorias nos níveis `5/10/15/20`, incremento de perícias e proficiências de armas/armaduras/salvamentos/conjuração conforme `tabela_progressao` das 12 classes, seleção de talentos por nível de Classe, Perícia, Geral e Ancestralidade até o 20º nível, além de espaços/repertório/grimório de magias dos círculos `2–10`).
- [ ] **Itens Mágicos, Runas e Tesouros (`ref/Compendium specific tools.pdf` → `dados/itens_magicos_tesouros.json`)** *(Adiado para implementação futura conforme decisão do usuário em `19/11/2026`)*
  - Converter runas fundamentais e de propriedade, materiais preciosos, itens alquímicos completos, poções, pergaminhos, talismãs e itens mágicos permanentes, e integrá-los ao motor para personagens de nível `2+`.
