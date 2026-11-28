# Pendências do Projeto — Castles & Crusades (1ª Ed. Brasileira)

Lista viva e priorizada das etapas para construir o gerador de fichas de **Castles & Crusades**. Tudo o que já foi concluído encontra-se registrado em [`finalizado.md`](finalizado.md) e nos logs numerados em [`finalizado/`](finalizado/).

---

## 1. Materiais de Referência e Conversão para JSON (`ref/cc/` → `dados/dadosc&c/`)

- [x] **Converter Magias (Regras, Listas 0–9 e Descrições A–V)** → `dados/dadosc&c/magias01.json`, `magias02.json` e `magias03.json` *(378/378 feitiços validados)*
- [x] **Mapear a Ficha Oficial de C&C** → `dados/dadosc&c/estrutura_ficha.json` e `dados/dadosc&c/templates/ficha_oficial_cc.pdf` *(página única US Letter mapeada com coordenadas vetoriais)*

---

## 2. Motor de Regras (`motor_cc/`) e API (`/api/cc/*`)

- [x] **Carregador e cache da base (`motor_cc/dados.py`)**
- [x] **Regras de Atributos, Primários/Secundários e Sistema SIEGE** (`motor_cc/atributos.py` — 4 métodos de geração, tabela oficial C&C, modificadores raciais e linhagens do Meio-Elfo)
- [x] **Aplicação de Raça, Classe, PV, CA, Bônus de Ataque Base e Habilidades** (`motor_cc/combate.py` e `motor_cc/gerador.py` — níveis 1–24, 3 regras oficiais de PV + média fixa)
- [x] **Compra/alocação de Equipamentos, Moedas e Carga (EV / Peso)** (`motor_cc/equipamentos.py` — ouro inicial, conversão pc/pp/po e Sobrecarga SB/CS)
- [x] **Seleção de Magias para Classes Conjuradoras** (`motor_cc/magias.py` — espaços diários + feitiços bônus cumulativos por INT/SAB 13–19 e validação das listas)
- [ ] **Endpoints REST no Flask (`/api/cc/opcoes`, `/api/cc/gerar`, `/api/cc/exportar/*`)**

---

## 3. Interface Web (`/cc`) e Exportadores

- [ ] **Montador interativo de fichas em `templates/cc.html` + `static/js/cc/`**
- [ ] **Visualização da ficha pronta e impressão (`@media print`)**
- [ ] **Exportadores `.txt`, `.docx` e `.pdf` para Castles & Crusades**

---

## 4. Qualidade e Testes Automatizados

- [ ] **Suíte de testes `tests/test_cc_*.py`** cobrindo todas as raças, classes, cálculos matemáticos, casos de borda, rotas Flask e exportadores.
