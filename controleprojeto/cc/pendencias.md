# Pendências do Projeto — Castles & Crusades (1ª Ed. Brasileira)

Lista viva e priorizada das etapas para construir o gerador de fichas de **Castles & Crusades**. Tudo o que já foi concluído encontra-se registrado em [`finalizado.md`](finalizado.md) e nos logs numerados em [`finalizado/`](finalizado/).

---

## 1. Materiais de Referência e Conversão para JSON (`ref/cc/` → `dados/dadosc&c/`)

- [ ] **Converter Magias restantes (Descrições D–Z)** → `dados/dadosc&c/magias02.json`+ *(concluído: `magias01.json` com regras gerais, todas as 4 listas 0–9 e descrições A–C; aguardando próximos PDFs em `ref/cc/`)*
- [ ] **Mapear a Ficha Oficial de C&C** → `dados/dadosc&c/estrutura_ficha.json` *(aguardando PDF em `ref/cc/`)*

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
