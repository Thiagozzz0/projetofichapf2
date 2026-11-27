(() => {
  "use strict";

  const app = window.PF2EApp;
  const { NOMES_ATRIBUTOS, fmtMod } = window.PF2EFichaUI;
  const { esc, ORDEM_ATRIBUTOS, IDS_LIVRES_N1 } = app;

  function _aplicarBonusSeguro(valores, attrId, delta) {
    if (!attrId || !(attrId in valores)) return;
    if (delta > 0 && valores[attrId] >= 18) return;
    valores[attrId] += delta;
  }

  function atualizarPreviaAtributosABCD() {
    const grid = document.getElementById("grid-previa-atributos");
    const nota = document.getElementById("nota-previa-atributos");
    if (!grid || !app.opcoes) return;

    const valores = { for: 10, des: 10, con: 10, int: 10, sab: 10, car: 10 };
    const pendentes = [];

    // Etapa A: Ancestralidade
    const ancId = document.getElementById("ancestralidade")?.value || "aleatorio";
    const anc = app.opcoes.ancestralidades.find((a) => a.id === ancId) || null;
    if (!anc || ancId === "aleatorio") {
      pendentes.push("A (Ancestralidade aleatória)");
    } else {
      (anc.melhorias_fixas_ids || []).forEach((aid) => _aplicarBonusSeguro(valores, aid, 2));
      if (anc.defeito_atributo_id) _aplicarBonusSeguro(valores, anc.defeito_atributo_id, -2);

      const qtdLivA = Number(anc.qtd_melhorias_livres || 1) >= 2 ? 2 : 1;
      const selsA = [document.getElementById("attr-anc-livre-1")];
      if (qtdLivA >= 2) selsA.push(document.getElementById("attr-anc-livre-2"));

      let pendA = 0;
      selsA.forEach((sel) => {
        const v = sel?.value || "procedural";
        if (ORDEM_ATRIBUTOS.includes(v)) _aplicarBonusSeguro(valores, v, 2);
        else pendA += 1;
      });
      if (pendA > 0) pendentes.push(`A (${pendA} livre${pendA > 1 ? "s" : ""})`);
    }

    // Etapa B: Biografia
    let pendB = 0;
    ["attr-bio-restrito", "attr-bio-livre"].forEach((id) => {
      const v = document.getElementById(id)?.value || "procedural";
      if (ORDEM_ATRIBUTOS.includes(v)) _aplicarBonusSeguro(valores, v, 2);
      else pendB += 1;
    });
    if (pendB > 0) pendentes.push(`B (${pendB})`);

    // Etapa C: Classe / Atributo-Chave
    const clsId = document.getElementById("classe")?.value || "aleatorio";
    const conId = document.getElementById("conceito")?.value || "aleatorio";
    const cls = app.opcoes.classes.find((c) => c.id === clsId) || null;
    const con = cls ? cls.conceitos.find((x) => x.id === conId) : null;
    let chaveDefinida = null;

    if (!cls || clsId === "aleatorio") {
      pendentes.push("C (Classe aleatória)");
    } else {
      const opcoesChave =
        con && Array.isArray(con.atributo_chave_opcoes) && con.atributo_chave_opcoes.length
          ? con.atributo_chave_opcoes
          : cls.atributo_chave_ids || [];

      if (opcoesChave.length === 1) {
        chaveDefinida = opcoesChave[0];
        _aplicarBonusSeguro(valores, chaveDefinida, 2);
      } else {
        const vChave = document.getElementById("attr-classe-chave")?.value || "procedural";
        if (ORDEM_ATRIBUTOS.includes(vChave)) {
          chaveDefinida = vChave;
          _aplicarBonusSeguro(valores, vChave, 2);
        } else {
          pendentes.push("C (Chave)");
        }
      }
    }

    // Etapa D: 4 Bônus Livres N1
    let pendD = 0;
    IDS_LIVRES_N1.forEach((id) => {
      const v = document.getElementById(id)?.value || "procedural";
      if (ORDEM_ATRIBUTOS.includes(v)) _aplicarBonusSeguro(valores, v, 2);
      else pendD += 1;
    });
    if (pendD > 0) pendentes.push(`D (${pendD})`);

    grid.innerHTML = ORDEM_ATRIBUTOS.map((aid) => {
      const val = valores[aid];
      const mod = Math.floor((val - 10) / 2);
      const [sigla, nome] = NOMES_ATRIBUTOS[aid];
      const ehChave = chaveDefinida === aid;
      const clsExtra = val >= 16 ? " previa-atb-alta" : val < 10 ? " previa-atb-baixa" : "";
      const tagChave = ehChave ? `<span class="previa-atb-chave">Chave</span>` : "";
      return (
        `<div class="previa-atb-card${clsExtra}" title="${esc(nome)}">` +
        `<div class="previa-atb-topo"><span class="previa-atb-sigla">${esc(sigla)}</span>${tagChave}</div>` +
        `<strong class="previa-atb-mod">${esc(fmtMod(mod))}</strong>` +
        `<span class="previa-atb-val">${esc(val)}</span>` +
        `</div>`
      );
    }).join("");

    if (nota) {
      const partes = [];
      const nivel = app.obterNivelSelecionadoUI?.() || 1;
      const ehRandNiv = app.ehNivelAleatorioUI?.() || false;
      if (anc && cls && cls.pontos_de_vida_por_nivel !== undefined) {
        const modCon = Math.floor((valores.con - 10) / 2);
        const pvBase = Number(anc.pontos_vida || 0) + Math.max(1, Number(cls.pontos_de_vida_por_nivel || 0) + modCon) * nivel;
        partes.push(ehRandNiv ? `PV N1 est.: ${pvBase} (varia c/ nível)` : `PV N${nivel} est.: ${pvBase}`);
      }
      if (nivel >= 5) {
        partes.push("+4 melhorias livres N5 aplicadas na geração");
      }
      if (pendentes.length) {
        partes.push(`Em Procedural/Aleatório: ${pendentes.join(", ")}`);
      } else {
        partes.push("Todos os bônus ABCD definidos manualmente");
      }
      nota.textContent = partes.join(" • ");
    }
  }

  Object.assign(app, {
    atualizarPreviaAtributosABCD,
  });
})();
