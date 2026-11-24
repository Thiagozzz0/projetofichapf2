(() => {
  "use strict";

  const STORAGE_KEY = "pf2e_tema";

  function aplicarTema(tema) {
    const escuro = tema === "escuro";
    if (escuro) {
      document.documentElement.dataset.tema = "escuro";
    } else {
      delete document.documentElement.dataset.tema;
    }

    const btn = document.getElementById("btn-alternar-tema");
    if (btn) {
      btn.setAttribute("aria-pressed", String(escuro));
      btn.textContent = escuro ? "☀ Pergaminho Claro" : "🌙 Grimório Noturno";
      btn.title = escuro ? "Voltar para o tema Pergaminho Claro" : "Alternar para o modo escuro (Grimório Noturno)";
    }
  }

  let temaSalvo = "claro";
  try {
    temaSalvo = localStorage.getItem(STORAGE_KEY) === "escuro" ? "escuro" : "claro";
  } catch {
    temaSalvo = "claro";
  }
  aplicarTema(temaSalvo);

  document.getElementById("btn-alternar-tema")?.addEventListener("click", () => {
    const proximo = document.documentElement.dataset.tema === "escuro" ? "claro" : "escuro";
    aplicarTema(proximo);
    try {
      localStorage.setItem(STORAGE_KEY, proximo);
    } catch {
      /* ignore storage errors */
    }
  });
})();
