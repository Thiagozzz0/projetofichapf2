(() => {
  "use strict";

  const ORDEM_ATRIBUTOS = [
    "forca",
    "destreza",
    "constituicao",
    "inteligencia",
    "sabedoria",
    "carisma",
  ];

  const NOMES_ATRIBUTOS = {
    forca: "Força",
    destreza: "Destreza",
    constituicao: "Constituição",
    inteligencia: "Inteligência",
    sabedoria: "Sabedoria",
    carisma: "Carisma",
  };

  const SIGLAS_ATRIBUTOS = {
    forca: "FOR",
    destreza: "DES",
    constituicao: "CON",
    inteligencia: "INT",
    sabedoria: "SAB",
    carisma: "CAR",
  };

  function calcularModCC(valor) {
    const v = Number(valor) || 10;
    if (v <= 1) return -4;
    if (v <= 3) return -3;
    if (v <= 5) return -2;
    if (v <= 8) return -1;
    if (v <= 12) return 0;
    if (v <= 15) return 1;
    if (v <= 17) return 2;
    if (v <= 19) return 3;
    return 3 + Math.floor((v - 18) / 2);
  }

  function fmtMod(n) {
    const num = Number(n) || 0;
    return num > 0 ? `+${num}` : String(num);
  }

  function escapeHtml(str) {
    return String(str ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  const estado = {
    opcoes: null,
    metodo_geracao: "classico_3d6_livre",
    valoresBase: {
      forca: 12,
      destreza: 11,
      constituicao: 11,
      inteligencia: 10,
      sabedoria: 9,
      carisma: 9,
    },
    rolagens: [],
    sugestoesClasses: [],
    raca_id: "humano",
    linhagem_meio_elfo: "elfica",
    atributo_secundario_meio_elfo: "",
    classe_id: "combatente",
    nivel: 1,
    disposicao_id: "neutro",
    regra_pv: "opcional_1_maximo_n1",
    primariosEscolhidos: [],
    armadura_id: "",
    escudo_id: "",
    elmo_id: "",
    armas_ids: [],
    itens_ids: [],
    modo_ouro: "media",
    ouro_manual_po: null,
    auto_completar_feiticos: true,
    feiticos_escolhidos: {},
    fichaAtual: null,
  };

  window.CCApp = {
    ORDEM_ATRIBUTOS,
    NOMES_ATRIBUTOS,
    SIGLAS_ATRIBUTOS,
    calcularModCC,
    fmtMod,
    escapeHtml,
    estado,
  };
})();
