# Pendências do Projeto — Castles & Crusades (1ª Ed. Brasileira)

Lista viva e priorizada das etapas para construir o gerador de fichas de **Castles & Crusades**. Tudo o que já foi concluído encontra-se registrado em [`finalizado.md`](finalizado.md) e nos logs numerados em [`finalizado/`](finalizado/).

---

## 1. Materiais de Referência e Conversão para JSON (`ref/cc/` → `dados/dadosc&c/`)

- [ ] **Receber e mapear os PDFs recortados em `ref/cc/`**
  - Organizar os recortes temáticos da 1ª Edição Brasileira (Atributos/Regras Básicas, Raças, Classes, Equipamentos, Magias e Ficha Oficial) para conversão gradual, um arquivo por vez.
- [ ] **Converter Atributos, Sistema SIEGE e Regras Básicas** → `dados/dadosc&c/regras_basicas.json`
- [ ] **Converter Raças** → `dados/dadosc&c/racas.json`
- [ ] **Converter Classes** → `dados/dadosc&c/classes.json` (ou dividido por leva, se necessário)
- [ ] **Converter Equipamentos (Armas, Armaduras, Escudos, Itens e Carga)** → `dados/dadosc&c/equipamentos.json`
- [ ] **Converter Magias (Listas por Classe e Descrições)** → `dados/dadosc&c/magias.json`
- [ ] **Mapear a Ficha Oficial de C&C** → `dados/dadosc&c/estrutura_ficha.json` (e template PDF, se aplicável)

---

## 2. Motor de Regras (`motor_cc/`) e API (`/api/cc/*`)

- [ ] **Carregador e cache da base (`motor_cc/dados.py`)**
- [ ] **Regras de Atributos, Primários/Secundários e Sistema SIEGE**
- [ ] **Aplicação de Raça, Classe, PV, CA, Bônus de Ataque Base e Habilidades**
- [ ] **Compra/alocação de Equipamentos, Moedas e Carga (EV / Peso)**
- [ ] **Seleção de Magias para Classes Conjuradoras**
- [ ] **Endpoints REST no Flask (`/api/cc/opcoes`, `/api/cc/gerar`, `/api/cc/exportar/*`)**

---

## 3. Interface Web (`/cc`) e Exportadores

- [ ] **Montador interativo de fichas em `templates/cc.html` + `static/js/cc/`**
- [ ] **Visualização da ficha pronta e impressão (`@media print`)**
- [ ] **Exportadores `.txt`, `.docx` e `.pdf` para Castles & Crusades**

---

## 4. Qualidade e Testes Automatizados

- [ ] **Suíte de testes `tests/test_cc_*.py`** cobrindo todas as raças, classes, cálculos matemáticos, casos de borda, rotas Flask e exportadores.
