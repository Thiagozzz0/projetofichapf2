(() => {
  "use strict";

  const {
    ORDEM_ATRIBUTOS,
    NOMES_ATRIBUTOS,
    SIGLAS_ATRIBUTOS,
    calcularModCC,
    fmtMod,
    escapeHtml,
    estado,
  } = window.CCApp;

  let atributoSelecionadoTroca = null;

  function obterAjustesRaciaisAtuais() {
    const racas = estado.opcoes?.racas || [];
    const raca = racas.find((r) => r.id === estado.raca_id);
    if (!raca) return {};
    const mods = { ...(raca.modificadores_atributos || {}) };
    if (raca.id === "meio_elfo" && raca.linhagens) {
      const lin = raca.linhagens[estado.linhagem_meio_elfo || "elfica"];
      if (lin && lin.modificadores_atributos) {
        Object.entries(lin.modificadores_atributos).forEach(([k, v]) => {
          mods[k] = (mods[k] || 0) + Number(v || 0);
        });
      }
    }
    return mods;
  }

  function obterPrimariosEfetivos() {
    const classes = estado.opcoes?.classes || [];
    const cls = classes.find((c) => c.id === estado.classe_id);
    const prims = [];
    if (cls) prims.push(cls.atributo_principal);
    (estado.primariosEscolhidos || []).forEach((p) => {
      if (!prims.includes(p)) prims.push(p);
    });
    return prims;
  }

  function atualizarResumoAtributos() {
    const resumo = document.getElementById("resumo-cc-atributos");
    const metodos = estado.opcoes?.metodos_atributos || [];
    const meta = metodos.find((m) => m.id === estado.metodo_geracao);
    const soma = ORDEM_ATRIBUTOS.reduce((acc, k) => acc + (Number(estado.valoresBase[k]) || 0), 0);
    if (resumo) {
      if (estado.metodo_geracao === "distribuido_62") {
        resumo.textContent = `${meta ? meta.rotulo_ficha : "62 pts"} (${soma}/62)`;
      } else {
        resumo.textContent = meta ? meta.rotulo_ficha : estado.metodo_geracao;
      }
    }
  }

  function renderizarMetodosAtributos() {
    const container = document.getElementById("cc-metodos-grid");
    if (!container || !estado.opcoes) return;

    const metodos = estado.opcoes.metodos_atributos || [];
    container.innerHTML = metodos
      .map((m) => {
        const ativo = m.id === estado.metodo_geracao ? " ativo" : "";
        return `
          <button type="button" class="cc-metodo-card${ativo}" data-metodo-id="${escapeHtml(m.id)}">
            <strong>${escapeHtml(m.nome)}</strong>
            <span>${escapeHtml(m.descricao)}</span>
          </button>
        `;
      })
      .join("");

    container.querySelectorAll("[data-metodo-id]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const novo = btn.getAttribute("data-metodo-id");
        if (!novo || novo === estado.metodo_geracao) return;
        estado.metodo_geracao = novo;
        atributoSelecionadoTroca = null;
        await rolarOuInicializarAtributos();
      });
    });
  }

  function renderizarGridAtributos(onMudancaValores) {
    const grid = document.getElementById("cc-atributos-grid");
    const infoBarra = document.getElementById("cc-attr-status-texto");
    const btnRolar = document.getElementById("btn-cc-rolar-atributos");
    const btnOtimizar = document.getElementById("btn-cc-otimizar-classe");
    const boxSug = document.getElementById("cc-sugestoes-old-school");
    const listaSug = document.getElementById("cc-sugestoes-lista");
    if (!grid) return;

    const isOldSchool = estado.metodo_geracao === "old_school_3d6_ordem";
    const isDistribuido = estado.metodo_geracao === "distribuido_62";
    const isAlocacaoLivre = !isOldSchool;

    if (btnRolar) {
      btnRolar.textContent = isDistribuido ? "↺ Resetar 62 pts" : "🎲 Rolar Dados";
    }
    if (btnOtimizar) {
      btnOtimizar.classList.toggle("oculto", isOldSchool || isDistribuido);
    }

    const soma = ORDEM_ATRIBUTOS.reduce((acc, k) => acc + (Number(estado.valoresBase[k]) || 0), 0);
    if (infoBarra) {
      if (isDistribuido) {
        const rest = 62 - soma;
        if (rest === 0) {
          infoBarra.innerHTML = `<strong style="color: var(--cc-ok)">62 / 62 pontos distribuídos corretamente!</strong>`;
        } else {
          const sinal = rest > 0 ? `Faltam ${rest}` : `Excedeu ${Math.abs(rest)}`;
          infoBarra.innerHTML = `<strong style="color: var(--cc-warn)">${sinal} ponto(s) — soma atual: ${soma}/62</strong>`;
        }
      } else if (isOldSchool) {
        infoBarra.textContent = "Ordem fixa FOR → DES → CON → INT → SAB → CAR travada. Use os valores para escolher Raça e Classe!";
      } else {
        infoBarra.textContent = "Clique em 'Trocar' em dois atributos para permutar os resultados sorteados ou edite manualmente (3–18).";
      }
    }

    const modsRaciais = obterAjustesRaciaisAtuais();
    const primarios = obterPrimariosEfetivos();

    grid.innerHTML = ORDEM_ATRIBUTOS.map((attr, idx) => {
      const base = Number(estado.valoresBase[attr]) || 10;
      const ajR = Number(modsRaciais[attr] || 0);
      const finalV = Math.max(1, base + ajR);
      const modF = calcularModCC(finalV);
      const isPrim = primarios.includes(attr);
      const rol = estado.rolagens?.[idx];
      const dadosTxt = rol
        ? `Dados: [${rol.dados.join(", ")}]${rol.descartado !== null && rol.descartado !== undefined ? ` (desc. ${rol.descartado})` : ""}`
        : "";
      const trocaAtiva = atributoSelecionadoTroca === attr;

      return `
        <div class="cc-attr-box${isPrim ? " primario" : ""}">
          <div class="cc-attr-topo">
            <span class="cc-attr-sigla" title="${escapeHtml(NOMES_ATRIBUTOS[attr])}">${SIGLAS_ATRIBUTOS[attr]}</span>
            <span class="cc-badge ${isPrim ? "cc-badge-primario" : "cc-badge-secundario"}">
              ${isPrim ? "Primário (CB 12)" : "Secundário (CB 18)"}
            </span>
          </div>
          <div class="cc-attr-controles">
            ${
              isDistribuido
                ? `<div class="cc-stepper">
                    <button type="button" class="cc-btn cc-btn-secundario cc-stepper-btn" data-attr-step="${attr}:-1" aria-label="Diminuir ${escapeHtml(NOMES_ATRIBUTOS[attr])}">-</button>
                    <input
                      type="number"
                      min="3"
                      max="18"
                      value="${base}"
                      data-attr-input="${attr}"
                      aria-label="${escapeHtml(NOMES_ATRIBUTOS[attr])} base"
                    >
                    <button type="button" class="cc-btn cc-btn-secundario cc-stepper-btn" data-attr-step="${attr}:1" aria-label="Aumentar ${escapeHtml(NOMES_ATRIBUTOS[attr])}">+</button>
                  </div>`
                : `<input
                    type="number"
                    min="3"
                    max="18"
                    value="${base}"
                    data-attr-input="${attr}"
                    ${isOldSchool ? "readonly" : ""}
                    aria-label="${escapeHtml(NOMES_ATRIBUTOS[attr])} base"
                  >`
            }
            <span>→ <strong>${finalV}</strong> (${fmtMod(modF)})</span>
          </div>
          <div class="cc-attr-meta">
            <span>Raça: ${ajR === 0 ? "0" : fmtMod(ajR)}</span>
            ${
              isAlocacaoLivre && !isDistribuido
                ? `<button type="button" class="cc-btn cc-btn-secundario cc-btn-mini" data-attr-troca="${attr}">${trocaAtiva ? "Cancelar" : "⇄ Trocar"}</button>`
                : ""
            }
          </div>
          ${dadosTxt ? `<small style="color: var(--cc-text-muted); font-size: 0.72rem">${escapeHtml(dadosTxt)}</small>` : ""}
        </div>
      `;
    }).join("");

    // Listeners de input manual / distribuído
    if (!isOldSchool) {
      grid.querySelectorAll("[data-attr-input]").forEach((inp) => {
        inp.addEventListener("change", () => {
          const attr = inp.getAttribute("data-attr-input");
          let val = parseInt(inp.value, 10);
          if (Number.isNaN(val)) val = 10;
          val = Math.max(3, Math.min(18, val));
          estado.valoresBase[attr] = val;
          renderizarGridAtributos(onMudancaValores);
          if (onMudancaValores) onMudancaValores();
        });
      });

      grid.querySelectorAll("[data-attr-step]").forEach((btn) => {
        btn.addEventListener("click", () => {
          const [attr, deltaStr] = (btn.getAttribute("data-attr-step") || "").split(":");
          const delta = parseInt(deltaStr, 10) || 0;
          if (!attr || !delta) return;
          const atual = Number(estado.valoresBase[attr]) || 10;
          const novo = Math.max(3, Math.min(18, atual + delta));
          if (novo === atual) return;
          estado.valoresBase[attr] = novo;
          renderizarGridAtributos(onMudancaValores);
          if (onMudancaValores) onMudancaValores();
        });
      });
    }

    // Listeners de troca (clássico / heróico)
    grid.querySelectorAll("[data-attr-troca]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const alvo = btn.getAttribute("data-attr-troca");
        if (!atributoSelecionadoTroca) {
          atributoSelecionadoTroca = alvo;
          renderizarGridAtributos(onMudancaValores);
        } else if (atributoSelecionadoTroca === alvo) {
          atributoSelecionadoTroca = null;
          renderizarGridAtributos(onMudancaValores);
        } else {
          const tmp = estado.valoresBase[atributoSelecionadoTroca];
          estado.valoresBase[atributoSelecionadoTroca] = estado.valoresBase[alvo];
          estado.valoresBase[alvo] = tmp;
          atributoSelecionadoTroca = null;
          renderizarGridAtributos(onMudancaValores);
          if (onMudancaValores) onMudancaValores();
        }
      });
    });

    // Sugestões de classes no modo Old School (ou com base nos valores sorteados)
    if (boxSug && listaSug) {
      const classes = estado.opcoes?.classes || [];
      const ranking = [...classes]
        .map((c) => ({
          id: c.id,
          nome: c.nome,
          attr: c.atributo_principal,
          sigla: SIGLAS_ATRIBUTOS[c.atributo_principal],
          val: Number(estado.valoresBase[c.atributo_principal] || 10),
        }))
        .sort((a, b) => b.val - a.val || a.nome.localeCompare(b.nome))
        .slice(0, 4);

      boxSug.classList.toggle("oculto", !isOldSchool);
      if (isOldSchool) {
        listaSug.innerHTML = ranking
          .map(
            (s) => `
            <button type="button" class="cc-btn cc-btn-secundario cc-btn-mini" data-aplicar-classe="${escapeHtml(s.id)}">
              ${escapeHtml(s.nome)} (${s.sigla} ${s.val})
            </button>
          `
          )
          .join("");
        listaSug.querySelectorAll("[data-aplicar-classe]").forEach((btn) => {
          btn.addEventListener("click", () => {
            const cid = btn.getAttribute("data-aplicar-classe");
            const selClasse = document.getElementById("cc-classe");
            if (selClasse && cid) {
              selClasse.value = cid;
              selClasse.dispatchEvent(new Event("change"));
            }
          });
        });
      }
    }

    atualizarResumoAtributos();
  }

  async function rolarOuInicializarAtributos(onDepois) {
    try {
      const resp = await fetch("/api/cc/rolar-atributos", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ metodo: estado.metodo_geracao }),
      });
      const dados = await resp.json();
      if (!resp.ok) throw new Error(dados.erro || "Falha ao rolar atributos.");

      estado.valoresBase = { ...dados.valores };
      estado.rolagens = dados.rolagens || [];
      estado.sugestoesClasses = dados.sugestoes_classes || [];
      atributoSelecionadoTroca = null;

      renderizarMetodosAtributos();
      renderizarGridAtributos(window.CCApp._onAtributosAlterados);
      if (window.CCApp._onAtributosAlterados) window.CCApp._onAtributosAlterados();
      if (onDepois) onDepois(dados);
    } catch (err) {
      console.error(err);
    }
  }

  function otimizarValoresParaClasseAtual() {
    const classes = estado.opcoes?.classes || [];
    const cls = classes.find((c) => c.id === estado.classe_id);
    if (!cls) return;

    const attrPrincipal = cls.atributo_principal;
    const todosValores = ORDEM_ATRIBUTOS.map((a) => Number(estado.valoresBase[a]) || 10).sort((a, b) => b - a);
    const restantes = ORDEM_ATRIBUTOS.filter((a) => a !== attrPrincipal);

    estado.valoresBase[attrPrincipal] = todosValores[0];
    // Coloca os demais valores na melhor ordem natural: CON, DES, restante
    const ordemSec = ["constituicao", "destreza", "forca", "sabedoria", "inteligencia", "carisma"].filter(
      (a) => restantes.includes(a)
    );
    ordemSec.forEach((a, idx) => {
      estado.valoresBase[a] = todosValores[idx + 1];
    });
    renderizarGridAtributos(window.CCApp._onAtributosAlterados);
    if (window.CCApp._onAtributosAlterados) window.CCApp._onAtributosAlterados();
  }

  window.CCApp.atributosUI = {
    obterAjustesRaciaisAtuais,
    renderizarMetodosAtributos,
    renderizarGridAtributos,
    rolarOuInicializarAtributos,
    otimizarValoresParaClasseAtual,
  };
})();
