(() => {
  "use strict";

  function setStatus(texto, tipo = "") {
    const el = document.getElementById("mensagem-status");
    if (!el) return;
    el.textContent = texto;
    el.className = `mensagem-status ${tipo}`.trim();
  }

  function normTxt(txt) {
    return String(txt || "")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase()
      .trim();
  }

  function criarOptgroup(sel, label) {
    const og = document.createElement("optgroup");
    og.label = label;
    sel.appendChild(og);
    return og;
  }

  function fmtPrecoEq(pcBruto) {
    const pc = Math.round(Number(pcBruto || 0));
    const ppTot = pc / 10;
    const ppStr = Number.isInteger(ppTot) ? `${ppTot} pp` : `${ppTot.toFixed(1).replace(".", ",")} pp`;
    const po = Math.floor(pc / 100);
    const remPp = Math.floor((pc % 100) / 10);
    const remPc = pc % 10;
    if (po === 0 && remPc === 0) return ppStr;
    const partes = [];
    if (po > 0) partes.push(`${po} po`);
    if (remPp > 0) partes.push(`${remPp} pp`);
    if (remPc > 0) partes.push(`${remPc} pc`);
    return `${ppStr} (${partes.join(", ")})`;
  }

  window.PF2EApp = {
    opcoes: null,
    ultimaFicha: null,
    bioManualExpAutomatica: false,
    perEstado: { selecionadas: [] },
    eqEstado: { armas_cc: [], armas_dist: [], variados: [] },
    mapaEq: { armaduras: {}, escudos: {}, armas_cc: {}, armas_dist: {}, variados: {} },

    ORDEM_ATRIBUTOS: ["for", "des", "con", "int", "sab", "car"],
    IDS_LIVRES_N1: ["attr-livre-1", "attr-livre-2", "attr-livre-3", "attr-livre-4"],
    CLASSES_CONJURADORAS_UI: new Set(["bardo", "clerigo", "druida", "feiticeiro", "mago"]),
    IDS_TAL_CLASSE: ["tal-classe-1", "tal-classe-2", "tal-classe-3"],
    IDS_TAL_GERAIS: ["tal-geral-1", "tal-geral-2"],
    TALENTOS_PERICIAS_ANC_UI: {
      pericia_natural: { extras: 2, fixas: [] },
      longevidade_ancestral: { extras: 1, fixas: [] },
      saber_enanico: { extras: 0, fixas: ["manufatura", "religiao"] },
      saber_elfico: { extras: 0, fixas: ["arcanismo", "natureza"] },
      saber_gnomico: { extras: 0, fixas: ["ocultismo", "natureza"] },
      saber_goblinoide: { extras: 0, fixas: ["natureza", "furtividade"] },
      saber_halfling: { extras: 0, fixas: ["acrobatismo", "furtividade"] },
    },

    setStatus,
    normTxt,
    criarOptgroup,
    fmtPrecoEq,
  };
})();
