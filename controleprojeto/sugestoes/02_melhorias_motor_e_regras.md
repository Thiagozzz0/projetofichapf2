# 02 — Melhorias no Motor de Regras, Qualidade e Dados

- **Data da Proposta:** `19/11/2026 — 15:06`
- **Objetivo:** Elevar o nível de fidelidade às regras de Pathfinder 2E e blindar a base matemática e os arquivos exportados.

---

## Sugestões Prioritárias

### 1. Suíte Unitária de Casos de Borda Matemáticos (Fechamento da Etapa 5)
- Criar `scripts/validar_casos_borda_pf2e.py` testando isoladamente cenários extremos que testes de geração aleatória nem sempre atingem ao mesmo tempo:
  - **CA com Limite de Destreza:** personagem com `DES 18 (+4)` vestindo armadura com limite `+1` (Cota de Malha) vs sem armadura;
  - **Penalidade de Armadura vs Força Mínima:** armadura quando `FOR < forca_minima` (aplicando penalidade nas 4 perícias físicas e penalidade integral de velocidade) vs `FOR >= forca_minima` vs talento enânico `Ferro Desimpedido`;
  - **Sobrecarga de Volume:** personagem carregando acima de `5 + mod FOR` recebendo `-3m` de penalidade de velocidade (respeitando o mínimo de `1,5m`);
  - **Armas Específicas:** `Acuidade` usando `max(FOR, DES)`, Ladino `Ladrão` usando `DES` no dano, arma `Propulsiva` com `FOR` positiva (`floor(FOR/2)`) vs negativa (`FOR` inteira), armas de arremesso e `Punho Poderoso` do Monge;
  - **Clérigo `Capelão da Guerra`:** Fortitude elevada para `especialista` e proficiência em armaduras leves/médias.

### 2. Bloco Dedicado de Companheiros Animais e Familiares
- Já possuímos `dados/companheiros_familiares.json` completo (`8` tipos de companheiros, `4` estágios, `12` habilidades de familiar e `6` de mestre).
- **Melhoria:** sempre que o personagem escolher talentos como `Companheiro Animal` (Druida, Patrulheiro, Cavaleiro Brusco), `Familiar` / `Familiar Alquímico` / `Familiar Leshy` / `Cúmplice Animal`, gerar automaticamente um sub-bloco com a **ficha pronta do Companheiro ou Familiar** (PV, CA, ataques, sentidos, velocidades e habilidades selecionadas) tanto na tela Web quanto no `.docx`/`.txt`.

### 3. Seleção Real de Divindades (Clérigo e Campeão)
- Atualmente `divindade` exibe `"Sarenrae / Divindade Bondosa"` e a perícia da divindade usa `conceito["pericias_prioritarias"]`.
- **Melhoria:** extrair a tabela de Divindades do Capítulo 8 (pp. 437–441 do `pdf_fonte/P Basic 2.0 Teste_compressed.pdf`) para `dados/divindades.json`, permitindo escolher a divindade real com sua **arma favorita** (aplicando automaticamente o dado da arma no talento `Simplicidade Mortal` do Clérigo!), alinhamentos permitidos, perícia e domínios reais.

### 4. Avaliador de Pré-Requisitos Completo para Todos os Níveis e Talentos
- Expandir `atende_prerequisitos()` em `motor/talentos.py` para cobrir requisitos compostos dos talentos gerais/perícia de nível 1+ (ex.: `Inteligência 12`, `Sabedoria 14`, talento prévio como `Vitalidade` ou `Treinamento em Perícia`, proficiência `Especialista`/`Mestre`).

### 5. Evolução Opcional do Exportador `.docx`
- Manter o gerador `.docx` atual em Python puro como fallback universal (zero dependências C), **ou** oferecer suporte opcional a `python-docx` / template `.docx` base pré-formatado para:
  - Layout em 2 colunas na Página 1 imitando fielmente a ficha impressa oficial;
  - Numeração de páginas no rodapé (`Página X de Y`);
  - Inserção de imagem de retrato do personagem enviada pelo usuário.

### 6. Customização de Conceitos pelo Usuário
- Permitir que o usuário salve seus próprios "Conceitos/Nortes" personalizados em `dados/conceitos_customizados.json` (ou via interface), expandindo além dos `38` conceitos padrão.
