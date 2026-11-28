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
    atributosUI,
    renderizarFichaCC,
  } = window.CCApp;

  function setupAcordeao() {
    if (window.matchMedia && window.matchMedia("(max-width: 640px)").matches) {
      ["cc-corpo-raca-classe", "cc-corpo-primarios"].forEach((id) => {
        document.getElementById(id)?.classList.add("oculto");
        const hdr = document.querySelector(`[data-cc-toggle="${id}"]`);
        if (hdr) hdr.setAttribute("aria-expanded", "false");
      });
    }
    document.querySelectorAll("[data-cc-toggle]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const alvoId = btn.getAttribute("data-cc-toggle");
        const corpo = document.getElementById(alvoId);
        if (!corpo) return;
        const aberto = !corpo.classList.contains("oculto");
        corpo.classList.toggle("oculto", aberto);
        btn.setAttribute("aria-expanded", String(!aberto));
      });
    });
  }

  function obterClasseAtual() {
    return (estado.opcoes?.classes || []).find((c) => c.id === estado.classe_id) || null;
  }

  function obterRacaAtual() {
    return (estado.opcoes?.racas || []).find((r) => r.id === estado.raca_id) || null;
  }

  function atualizarResumosEtapas() {
    const raca = obterRacaAtual();
    const cls = obterClasseAtual();
    const resRC = document.getElementById("resumo-cc-raca-classe");
    if (resRC && raca && cls) {
      resRC.textContent = `${raca.nome} • ${cls.nome} Nv. ${estado.nivel}`;
    }

    const resPrim = document.getElementById("resumo-cc-primarios");
    if (resPrim && raca && cls) {
      const total = raca.total_atributos_primarios || 2;
      resPrim.textContent = `${total} Primários (${SIGLAS_ATRIBUTOS[cls.atributo_principal]} + livres)`;
    }

    const resEq = document.getElementById("resumo-cc-equipamentos");
    if (resEq) {
      const qtd =
        (estado.armadura_id ? 1 : 0) +
        (estado.escudo_id ? 1 : 0) +
        (estado.elmo_id ? 1 : 0) +
        estado.armas_ids.length +
        estado.itens_ids.length;
      resEq.textContent = `${qtd} ite${qtd === 1 ? "m" : "ns"} selecionado${qtd === 1 ? "" : "s"}`;
    }

    const resMag = document.getElementById("resumo-cc-magias");
    if (resMag && cls) {
      resMag.textContent = cls.conjurador
        ? estado.auto_completar_feiticos
          ? "Automático"
          : "Seleção manual"
        : "Não conjurador";
    }
  }

  function renderizarControlesMeioElfo() {
    const box = document.getElementById("cc-box-meio-elfo");
    const boxSec = document.getElementById("cc-box-meio-elfo-secundario");
    const selSec = document.getElementById("cc-meio-elfo-secundario");
    if (!box) return;

    const isME = estado.raca_id === "meio_elfo";
    box.classList.toggle("oculto", !isME);
    if (!isME) return;

    const linHumana = estado.linhagem_meio_elfo === "humana";
    if (boxSec) boxSec.classList.toggle("oculto", !linHumana);

    if (linHumana && selSec) {
      const cls = obterClasseAtual();
      const prims = new Set([cls?.atributo_principal, ...estado.primariosEscolhidos].filter(Boolean));
      const secs = ORDEM_ATRIBUTOS.filter((a) => !prims.has(a));
      if (!secs.includes(estado.atributo_secundario_meio_elfo)) {
        estado.atributo_secundario_meio_elfo = secs[0] || "";
      }
      selSec.innerHTML = secs
        .map((a) => `<option value="${a}" ${a === estado.atributo_secundario_meio_elfo ? "selected" : ""}>${escapeHtml(NOMES_ATRIBUTOS[a])}</option>`)
        .join("");
    }
  }

  function renderizarPrimariosSIEGE() {
    const container = document.getElementById("cc-primarios-container");
    const info = document.getElementById("cc-primarios-info");
    if (!container || !estado.opcoes) return;

    const raca = obterRacaAtual();
    const cls = obterClasseAtual();
    if (!raca || !cls) return;

    const obrigatorio = cls.atributo_principal;
    const qtdLivres = Number(raca.primarios_escolha_jogador || 1);

    // Mantém apenas escolhidos válidos que não sejam o obrigatório
    estado.primariosEscolhidos = estado.primariosEscolhidos
      .filter((a) => a !== obrigatorio && ORDEM_ATRIBUTOS.includes(a))
      .slice(0, qtdLivres);

    if (info) {
      info.innerHTML = `Atributo fixo da classe (${escapeHtml(cls.nome)}): <strong>${escapeHtml(NOMES_ATRIBUTOS[obrigatorio])}</strong>. Como <strong>${escapeHtml(raca.nome)}</strong>, escolha mais <strong>${qtdLivres}</strong> atributo(s) primário(s) livre(s).`;
    }

    container.innerHTML = ORDEM_ATRIBUTOS.map((attr) => {
      const isObr = attr === obrigatorio;
      const checked = isObr || estado.primariosEscolhidos.includes(attr);
      return `
        <label class="cc-check-pill">
          <input
            type="checkbox"
            value="${attr}"
            data-primario-check="${attr}"
            ${checked ? "checked" : ""}
            ${isObr ? "disabled" : ""}
          >
          <span>${SIGLAS_ATRIBUTOS[attr]} — ${escapeHtml(NOMES_ATRIBUTOS[attr])}${isObr ? " (Classe)" : ""}</span>
        </label>
      `;
    }).join("");

    container.querySelectorAll("[data-primario-check]").forEach((chk) => {
      chk.addEventListener("change", () => {
        const selecionados = Array.from(container.querySelectorAll("[data-primario-check]:not(:disabled):checked")).map(
          (el) => el.value
        );
        if (selecionados.length > qtdLivres) {
          chk.checked = false;
          return;
        }
        estado.primariosEscolhidos = selecionados;
        atributosUI.renderizarGridAtributos(window.CCApp._onAtributosAlterados);
        renderizarControlesMeioElfo();
        atualizarResumoEquipamentosAoVivo();
        atualizarResumosEtapas();
      });
    });
  }

  function calcularEspacosConjuracaoCliente() {
    const cls = obterClasseAtual();
    if (!cls || !cls.conjurador || !cls.conjuracao) return {};

    const conj = cls.conjuracao;
    const tabela = conj.feiticos_diarios || {};
    let chaveNv = String(estado.nivel);
    if (!tabela[chaveNv]) {
      const disp = Object.keys(tabela)
        .map(Number)
        .filter((n) => n <= estado.nivel)
        .sort((a, b) => a - b);
      chaveNv = disp.length ? String(disp[disp.length - 1]) : Object.keys(tabela)[0];
    }

    const baseCirc = tabela[chaveNv] || {};
    const attrConj = conj.atributo_conjuracao || cls.atributo_principal;
    const modsRaciais = atributosUI.obterAjustesRaciaisAtuais();
    const valorAttr = (Number(estado.valoresBase[attrConj]) || 10) + Number(modsRaciais[attrConj] || 0);

    const bonusMap = {};
    (conj.feiticos_bonus_por_atributo || []).forEach((r) => {
      const circStr = String(r.circulo);
      if (valorAttr >= r.min && (baseCirc[circStr] || 0) > 0) {
        bonusMap[circStr] = (bonusMap[circStr] || 0) + Number(r.quantidade || 0);
      }
    });

    const resultado = {};
    Object.entries(baseCirc).forEach(([c, q]) => {
      const baseQ = Number(q || 0);
      if (baseQ > 0) {
        resultado[c] = { base: baseQ, bonus: bonusMap[c] || 0, total: baseQ + (bonusMap[c] || 0) };
      }
    });
    return resultado;
  }

  function renderizarEtapaMagias() {
    const card = document.getElementById("cc-etapa-magias");
    const boxLista = document.getElementById("cc-magias-selecao");
    const cls = obterClasseAtual();
    if (!card || !boxLista) return;

    if (!cls || !cls.conjurador) {
      card.classList.add("oculto");
      atualizarResumosEtapas();
      return;
    }

    card.classList.remove("oculto");
    boxLista.classList.toggle("oculto", Boolean(estado.auto_completar_feiticos));

    if (!estado.auto_completar_feiticos) {
      const espacos = calcularEspacosConjuracaoCliente();
      const listaClasse = estado.opcoes?.listas_magias?.[cls.id] || {};
      const circs = Object.keys(espacos).sort((a, b) => Number(a) - Number(b));

      boxLista.innerHTML = `<div class="cc-circulos-grid">${circs
        .map((c) => {
          const info = espacos[c];
          const disp = listaClasse[c] || [];
          const sels = estado.feiticos_escolhidos[c] || [];
          return `
            <div class="cc-circulo-box">
              <h4><span>Nível ${escapeHtml(c)}</span><span>${sels.length}/${info.total} espaços</span></h4>
              <div class="cc-catalogo-lista" style="max-height: 170px">
                ${disp
                  .map((f) => {
                    const checked = sels.includes(f.id) ? "checked" : "";
                    return `
                      <label class="cc-catalogo-item" style="cursor:pointer">
                        <span><input type="checkbox" data-feitico-circ="${escapeHtml(c)}" value="${escapeHtml(f.id)}" ${checked}> ${escapeHtml(f.nome)}${f.reversivel ? "*" : ""}</span>
                      </label>
                    `;
                  })
                  .join("")}
              </div>
            </div>
          `;
        })
        .join("")}</div>`;

      boxLista.querySelectorAll("[data-feitico-circ]").forEach((chk) => {
        chk.addEventListener("change", () => {
          const c = chk.getAttribute("data-feitico-circ");
          const fid = chk.value;
          const lim = espacos[c]?.total || 0;
          const arr = estado.feiticos_escolhidos[c] ? [...estado.feiticos_escolhidos[c]] : [];
          if (chk.checked) {
            if (arr.length >= lim) {
              chk.checked = false;
              return;
            }
            if (!arr.includes(fid)) arr.push(fid);
          } else {
            const idx = arr.indexOf(fid);
            if (idx >= 0) arr.splice(idx, 1);
          }
          estado.feiticos_escolhidos[c] = arr;
          renderizarEtapaMagias();
        });
      });
    }

    atualizarResumosEtapas();
  }

  function atualizarResumoEquipamentosAoVivo() {
    const box = document.getElementById("cc-equip-resumo-ao-vivo");
    if (!box || !estado.opcoes) return;

    const eq = estado.opcoes.equipamentos;
    const mapa = {};
    Object.values(eq).forEach((lista) => {
      (lista || []).forEach((it) => {
        mapa[it.id] = it;
      });
    });

    const selecionados = [
      estado.armadura_id,
      estado.escudo_id,
      estado.elmo_id,
      ...estado.armas_ids,
      ...estado.itens_ids,
    ]
      .filter(Boolean)
      .map((id) => mapa[id])
      .filter(Boolean);

    const custoPo = selecionados.reduce((acc, it) => acc + Number(it.custo_pc || 0), 0) / 100.0;
    const sbTotal = selecionados.reduce((acc, it) => acc + Number(it.sb || 0), 0);

    const modsRaciais = atributosUI.obterAjustesRaciaisAtuais();
    const forFinal = (Number(estado.valoresBase.forca) || 10) + Number(modsRaciais.forca || 0);
    const cls = obterClasseAtual();
    const prims = new Set([cls?.atributo_principal, ...estado.primariosEscolhidos].filter(Boolean));
    const bonusCS = (prims.has("forca") && prims.has("constituicao")) ? 6 : (prims.has("forca") || prims.has("constituicao") ? 3 : 0);
    const cs = Math.max(1, forFinal + bonusCS);
    const catCarga = sbTotal <= cs ? "Descarregado" : sbTotal <= cs * 3 ? "Carregado" : "Sobrecarregado";

    box.innerHTML = `<strong>Resumo Atual:</strong> Custo total: <strong>${custoPo.toFixed(2)} po</strong> | Sobrecarga: <strong>SB ${sbTotal.toFixed(1)} / CS ${cs} (${catCarga})</strong>`;
  }

  function renderizarEquipamentosUI() {
    const eq = estado.opcoes?.equipamentos;
    if (!eq) return;

    const popSelect = (selId, lista, atual, placeholder) => {
      const sel = document.getElementById(selId);
      if (!sel) return;
      sel.innerHTML = `<option value="">${escapeHtml(placeholder)}</option>` +
        (lista || [])
          .map((it) => `<option value="${escapeHtml(it.id)}" ${it.id === atual ? "selected" : ""}>${escapeHtml(it.nome)} (${escapeHtml(it.custo)}${it.ca ? `, CA ${it.ca}` : ""}, SB ${it.sb})</option>`)
          .join("");
    };

    popSelect("cc-armadura", eq.armaduras, estado.armadura_id, "Nenhuma armadura (CA base 10)");
    popSelect("cc-escudo", eq.escudos, estado.escudo_id, "Nenhum escudo");
    popSelect("cc-elmo", eq.elmos, estado.elmo_id, "Nenhum elmo");

    const todasArmas = [...(eq.armas_corpo_a_corpo || []), ...(eq.armas_projeteis || [])];
    const selArma = document.getElementById("cc-select-arma");
    if (selArma) {
      selArma.innerHTML = todasArmas
        .map((a) => `<option value="${escapeHtml(a.id)}">${escapeHtml(a.nome)} (${escapeHtml(a.dano)}, ${escapeHtml(a.custo)}, SB ${a.sb})</option>`)
        .join("");
    }

    const renderChips = (containerId, ids, arrTarget) => {
      const el = document.getElementById(containerId);
      if (!el) return;
      const mapa = {};
      Object.values(eq).forEach((l) => (l || []).forEach((it) => (mapa[it.id] = it)));
      el.innerHTML = ids
        .map((id, idx) => {
          const it = mapa[id];
          if (!it) return "";
          return `<span class="cc-chip">${escapeHtml(it.nome)} (${escapeHtml(it.custo)}) <button type="button" data-rem-idx="${idx}" aria-label="Remover">×</button></span>`;
        })
        .join("");
      el.querySelectorAll("[data-rem-idx]").forEach((btn) => {
        btn.addEventListener("click", () => {
          const idx = parseInt(btn.getAttribute("data-rem-idx"), 10);
          arrTarget.splice(idx, 1);
          renderizarEquipamentosUI();
        });
      });
    };

    renderChips("cc-armas-chips", estado.armas_ids, estado.armas_ids);
    renderChips("cc-itens-chips", estado.itens_ids, estado.itens_ids);

    // Catálogo filtrável de outros equipamentos
    const filtro = (document.getElementById("cc-busca-item")?.value || "").trim().toLowerCase();
    const catalogoEl = document.getElementById("cc-catalogo-itens");
    if (catalogoEl) {
      const outros = [
        ...(eq.equipamento_geral || []),
        ...(eq.roupas || []),
        ...(eq.provisoes_e_alojamento || []),
        ...(eq.transporte_e_arreios || []),
      ];
      const filtrados = filtro
        ? outros.filter((it) => it.nome.toLowerCase().includes(filtro))
        : outros.slice(0, 40);

      catalogoEl.innerHTML = filtrados
        .map(
          (it) => `
          <div class="cc-catalogo-item">
            <span><strong>${escapeHtml(it.nome)}</strong> — ${escapeHtml(it.custo)} (SB ${it.sb})</span>
            <button type="button" class="cc-btn cc-btn-secundario cc-btn-mini" data-add-item="${escapeHtml(it.id)}">+ Adicionar</button>
          </div>
        `
        )
        .join("");

      catalogoEl.querySelectorAll("[data-add-item]").forEach((btn) => {
        btn.addEventListener("click", () => {
          const iid = btn.getAttribute("data-add-item");
          if (iid) {
            estado.itens_ids.push(iid);
            renderizarEquipamentosUI();
          }
        });
      });
    }

    atualizarResumoEquipamentosAoVivo();
    atualizarResumosEtapas();
  }

  function montarPayloadGeracao() {
    const parseListaTxt = (id) =>
      (document.getElementById(id)?.value || "")
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);

    const ouroManualEl = document.getElementById("cc-ouro-manual");
    const ouroManualVal =
      estado.modo_ouro === "manual" && ouroManualEl && ouroManualEl.value !== ""
        ? Number(ouroManualEl.value)
        : null;

    return {
      nome: document.getElementById("cc-nome")?.value || "Herói de C&C",
      titulos: document.getElementById("cc-titulos")?.value || "",
      jogador: document.getElementById("cc-jogador")?.value || "",
      raca_id: estado.raca_id,
      linhagem_meio_elfo: estado.raca_id === "meio_elfo" ? estado.linhagem_meio_elfo : null,
      atributo_secundario_meio_elfo:
        estado.raca_id === "meio_elfo" && estado.linhagem_meio_elfo === "humana"
          ? estado.atributo_secundario_meio_elfo
          : null,
      classe_id: estado.classe_id,
      nivel: estado.nivel,
      disposicao_id: estado.disposicao_id,
      metodo_geracao: estado.metodo_geracao,
      regra_pv: estado.regra_pv,
      atributos_base: { ...estado.valoresBase },
      primarios_escolhidos: [...estado.primariosEscolhidos],
      armadura_id: estado.armadura_id || null,
      escudo_id: estado.escudo_id || null,
      elmo_id: estado.elmo_id || null,
      armas_ids: [...estado.armas_ids],
      itens_ids: [...estado.itens_ids],
      modo_ouro: estado.modo_ouro === "manual" ? "media" : estado.modo_ouro,
      ouro_manual_po: ouroManualVal,
      auto_completar_feiticos: estado.auto_completar_feiticos,
      feiticos_escolhidos: estado.auto_completar_feiticos ? {} : estado.feiticos_escolhidos,
      itens_magicos: parseListaTxt("cc-itens-magicos"),
      pocoes: parseListaTxt("cc-pocoes"),
      anotacoes: document.getElementById("cc-anotacoes")?.value || "",
    };
  }

  async function exportarFormato(formato) {
    if (!estado.fichaAtual) return;
    const resp = await fetch(`/api/cc/exportar/${formato}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ficha: estado.fichaAtual }),
    });
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({}));
      throw new Error(err.erro || `Falha ao exportar ${formato.toUpperCase()}.`);
    }

    const disp = resp.headers.get("Content-Disposition") || "";
    const match = disp.match(/filename="?([^"]+)"?/i);
    const nomeArq = match ? match[1] : `ficha_cc.${formato}`;
    const blob = await resp.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = nomeArq;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  }

  async function iniciar() {
    setupAcordeao();

    window.CCApp._onAtributosAlterados = () => {
      renderizarEtapaMagias();
      atualizarResumoEquipamentosAoVivo();
    };

    const resp = await fetch("/api/cc/opcoes");
    const opcoes = await resp.json();
    estado.opcoes = opcoes;

    // Popular selects principais
    const selRaca = document.getElementById("cc-raca");
    if (selRaca) {
      selRaca.innerHTML = opcoes.racas
        .map((r) => `<option value="${escapeHtml(r.id)}">${escapeHtml(r.nome)} (${r.total_atributos_primarios} Primários, Mov. ${r.movimento_m}m)</option>`)
        .join("");
      selRaca.value = estado.raca_id;
    }

    const selClasse = document.getElementById("cc-classe");
    if (selClasse) {
      selClasse.innerHTML = opcoes.classes
        .map((c) => `<option value="${escapeHtml(c.id)}">${escapeHtml(c.nome)} (${SIGLAS_ATRIBUTOS[c.atributo_principal]}, ${c.dado_vida})</option>`)
        .join("");
      selClasse.value = estado.classe_id;
    }

    const selDisp = document.getElementById("cc-disposicao");
    if (selDisp) {
      selDisp.innerHTML = opcoes.disposicoes
        .map((d) => `<option value="${escapeHtml(d.id)}">${escapeHtml(d.nome)}</option>`)
        .join("");
      selDisp.value = estado.disposicao_id;
    }

    const selPV = document.getElementById("cc-regra-pv");
    if (selPV) {
      selPV.innerHTML = opcoes.regras_pv
        .map((p) => `<option value="${escapeHtml(p.id)}">${escapeHtml(p.nome)}</option>`)
        .join("");
      selPV.value = estado.regra_pv;
    }

    // Eventos dos controles
    selRaca?.addEventListener("change", () => {
      estado.raca_id = selRaca.value;
      renderizarPrimariosSIEGE();
      renderizarControlesMeioElfo();
      atributosUI.renderizarGridAtributos(window.CCApp._onAtributosAlterados);
      renderizarEtapaMagias();
      atualizarResumoEquipamentosAoVivo();
      atualizarResumosEtapas();
    });

    document.getElementById("cc-meio-elfo-linhagem")?.addEventListener("change", (e) => {
      estado.linhagem_meio_elfo = e.target.value;
      renderizarControlesMeioElfo();
      atributosUI.renderizarGridAtributos(window.CCApp._onAtributosAlterados);
      renderizarEtapaMagias();
    });

    document.getElementById("cc-meio-elfo-secundario")?.addEventListener("change", (e) => {
      estado.atributo_secundario_meio_elfo = e.target.value;
    });

    selClasse?.addEventListener("change", () => {
      estado.classe_id = selClasse.value;
      estado.feiticos_escolhidos = {};
      renderizarPrimariosSIEGE();
      renderizarControlesMeioElfo();
      atributosUI.renderizarGridAtributos(window.CCApp._onAtributosAlterados);
      renderizarEtapaMagias();
      atualizarResumoEquipamentosAoVivo();
      atualizarResumosEtapas();
    });

    document.getElementById("cc-nivel")?.addEventListener("change", (e) => {
      let nv = parseInt(e.target.value, 10) || 1;
      nv = Math.max(1, Math.min(24, nv));
      e.target.value = String(nv);
      estado.nivel = nv;
      renderizarEtapaMagias();
      atualizarResumosEtapas();
    });

    selDisp?.addEventListener("change", () => {
      estado.disposicao_id = selDisp.value;
    });

    selPV?.addEventListener("change", () => {
      estado.regra_pv = selPV.value;
    });

    document.getElementById("btn-cc-rolar-atributos")?.addEventListener("click", () => {
      atributosUI.rolarOuInicializarAtributos();
    });

    document.getElementById("btn-cc-otimizar-classe")?.addEventListener("click", () => {
      atributosUI.otimizarValoresParaClasseAtual();
    });

    document.getElementById("cc-armadura")?.addEventListener("change", (e) => {
      estado.armadura_id = e.target.value;
      atualizarResumoEquipamentosAoVivo();
      atualizarResumosEtapas();
    });
    document.getElementById("cc-escudo")?.addEventListener("change", (e) => {
      estado.escudo_id = e.target.value;
      atualizarResumoEquipamentosAoVivo();
      atualizarResumosEtapas();
    });
    document.getElementById("cc-elmo")?.addEventListener("change", (e) => {
      estado.elmo_id = e.target.value;
      atualizarResumoEquipamentosAoVivo();
      atualizarResumosEtapas();
    });

    document.getElementById("btn-cc-add-arma")?.addEventListener("click", () => {
      const sel = document.getElementById("cc-select-arma");
      if (sel && sel.value) {
        estado.armas_ids.push(sel.value);
        renderizarEquipamentosUI();
      }
    });

    document.getElementById("cc-busca-item")?.addEventListener("input", () => {
      renderizarEquipamentosUI();
    });

    document.getElementById("cc-modo-ouro")?.addEventListener("change", (e) => {
      estado.modo_ouro = e.target.value;
      document.getElementById("cc-box-ouro-manual")?.classList.toggle("oculto", estado.modo_ouro !== "manual");
    });

    document.getElementById("cc-auto-feiticos")?.addEventListener("change", (e) => {
      estado.auto_completar_feiticos = e.target.checked;
      renderizarEtapaMagias();
    });

    // Submissão do formulário
    document.getElementById("form-cc-gerador")?.addEventListener("submit", async (e) => {
      e.preventDefault();
      const erroBox = document.getElementById("cc-erro-geracao");
      if (erroBox) {
        erroBox.classList.add("oculto");
        erroBox.textContent = "";
      }

      try {
        const payload = montarPayloadGeracao();
        const r = await fetch("/api/cc/gerar", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        const dados = await r.json();
        if (!r.ok) {
          throw new Error(dados.erro || "Erro ao gerar a ficha.");
        }
        estado.fichaAtual = dados;
        renderizarFichaCC(dados);

        // Conectar botões de exportação e impressão recém-renderizados
        document.getElementById("btn-cc-export-pdf")?.addEventListener("click", () => exportarFormato("pdf"));
        document.getElementById("btn-cc-export-docx")?.addEventListener("click", () => exportarFormato("docx"));
        document.getElementById("btn-cc-export-txt")?.addEventListener("click", () => exportarFormato("txt"));
        document.getElementById("btn-cc-imprimir")?.addEventListener("click", () => window.print());

        document.getElementById("cc-ficha-pronta")?.scrollIntoView({ behavior: "smooth", block: "start" });
      } catch (err) {
        if (erroBox) {
          erroBox.textContent = err.message || String(err);
          erroBox.classList.remove("oculto");
        }
      }
    });

    // Renderizações iniciais
    atributosUI.renderizarMetodosAtributos();
    renderizarPrimariosSIEGE();
    renderizarControlesMeioElfo();
    renderizarEquipamentosUI();
    renderizarEtapaMagias();
    atualizarResumosEtapas();
    await atributosUI.rolarOuInicializarAtributos();
  }

  document.addEventListener("DOMContentLoaded", iniciar);
})();
