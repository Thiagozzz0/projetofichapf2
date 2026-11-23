(() => {
  "use strict";

  const app = window.PF2EApp;
  const { esc } = window.PF2EFichaUI;
  const { CLASSES_CONJURADORAS_UI, normTxt } = app;

  const NOMES_TRADICAO = {
    arcana: "Arcana",
    divina: "Divina",
    ocultista: "Ocultista",
    primal: "Primal",
  };

  function _iconeAcao(acoes) {
    const a = String(acoes || "2").trim();
    if (a === "1") return "◆";
    if (a === "2") return "◆◆";
    if (a === "3") return "◆◆◆";
    if (a.toLowerCase().includes("rea")) return "↺";
    if (a.toLowerCase().includes("liv")) return "◇";
    return a;
  }

  function calcularEstadoMagiasUI() {
    const cat = app.opcoes?.catalogo_magias;
    const clsId = document.getElementById("classe")?.value || "aleatorio";
    const conId = document.getElementById("conceito")?.value || "aleatorio";
    const divId = document.getElementById("divindade")?.value || "";
    const clsObj = app.opcoes?.classes?.find((c) => c.id === clsId) || null;
    const conObj = clsObj ? clsObj.conceitos.find((x) => x.id === conId) : null;
    const divObj = (app.opcoes?.divindades || []).find((d) => d.id === divId) || null;

    if (!cat || !clsObj || !CLASSES_CONJURADORAS_UI.has(clsId) || !clsObj.conjuracao_classe) {
      return { ehConjurador: false, disponivel: false };
    }

    const conjCls = clsObj.conjuracao_classe;
    const subId = conObj?.subclasse_oficial_id || "";
    const candsSub = conObj?.subclasses_oficiais_candidatas || (subId ? [subId] : []);
    const subDeterm = candsSub.length === 1 ? conjCls.subclasses?.[subId] || null : null;

    const tradicao = subDeterm?.tradicao || conjCls.tradicao_fixa || null;
    if (!tradicao) {
      return {
        ehConjurador: true,
        disponivel: false,
        clsObj,
        motivoIndisponivel:
          "Selecione um Conceito/Linhagem em Criação Inicial para definir a Tradição Mágica (Arcana, Divina, Ocultista ou Primal) do Feiticeiro.",
      };
    }

    const qtdTruquesTotal = Number(conjCls.qtd_truques || 5);
    const espacosN1 = Number(subDeterm?.espacos_n1 ?? conjCls.espacos_n1_base ?? 2);
    const qtdMagiasN1Total = Number(subDeterm?.qtd_magias_n1 ?? espacosN1);

    const truquesFixos = new Map();
    const magiasN1Fixas = new Map();
    if (subDeterm?.truque_fixo_id && cat.por_id[subDeterm.truque_fixo_id]) {
      truquesFixos.set(subDeterm.truque_fixo_id, `Linhagem (${conObj.subclasse_oficial_nome})`);
    }
    if (subDeterm?.magia_n1_fixa_id && cat.por_id[subDeterm.magia_n1_fixa_id]) {
      const rot = clsId === "bardo" ? "Musa" : "Linhagem";
      magiasN1Fixas.set(subDeterm.magia_n1_fixa_id, `${rot} (${conObj.subclasse_oficial_nome})`);
    }

    const poolTruquesIds = [...(cat.por_tradicao[tradicao]?.truques || [])];
    truquesFixos.forEach((_, mid) => {
      if (!poolTruquesIds.includes(mid)) poolTruquesIds.unshift(mid);
    });

    const poolN1Ids = [...(cat.por_tradicao[tradicao]?.nivel_1 || [])];
    magiasN1Fixas.forEach((_, mid) => {
      if (!poolN1Ids.includes(mid)) poolN1Ids.unshift(mid);
    });

    let magiaDivinaId = null;
    if (clsId === "clerigo" && divObj?.magia_clerigo_n1_id && cat.por_id[divObj.magia_clerigo_n1_id]) {
      magiaDivinaId = divObj.magia_clerigo_n1_id;
      if (!poolN1Ids.includes(magiaDivinaId)) poolN1Ids.unshift(magiaDivinaId);
    }

    const vagasLivresTruques = Math.max(0, qtdTruquesTotal - truquesFixos.size);
    const vagasLivresN1 = Math.max(0, qtdMagiasN1Total - magiasN1Fixas.size);

    return {
      ehConjurador: true,
      disponivel: true,
      clsId,
      clsObj,
      conObj,
      divObj,
      tradicao,
      estilo: conjCls.estilo,
      qtdTruquesTotal,
      espacosN1,
      qtdMagiasN1Total,
      vagasLivresTruques,
      vagasLivresN1,
      truquesFixos,
      magiasN1Fixas,
      magiaDivinaId,
      poolTruquesIds,
      poolN1Ids,
      porId: cat.por_id,
    };
  }

  function _atualizarNavegacaoEtapaMagias(ehConjurador) {
    const cardMag = document.getElementById("etapa-magias");
    const numEq = document.getElementById("etapa-num-equipamentos");
    const btnTalProx = document.getElementById("btn-tal-avancar");
    const btnEqVolt = document.getElementById("btn-eq-voltar");

    cardMag?.classList.toggle("oculto", !ehConjurador);
    if (!ehConjurador && cardMag?.classList.contains("aberta")) {
      app.alternarEtapaAcordeao?.(null, false);
    }
    if (numEq) numEq.textContent = ehConjurador ? "5" : "4";
    if (btnTalProx) {
      btnTalProx.dataset.etapaIr = ehConjurador ? "magias" : "equipamentos";
      btnTalProx.textContent = ehConjurador ? "Avançar para Magias →" : "Avançar para Equipamentos →";
    }
    if (btnEqVolt) {
      btnEqVolt.dataset.etapaIr = ehConjurador ? "magias" : "talentos";
      btnEqVolt.textContent = ehConjurador ? "← Voltar p/ Magias" : "← Voltar p/ Talentos";
    }
  }

  function mostrarDetalheMagiaUI(mid) {
    const box = document.getElementById("desc-magia-detalhe");
    if (!box) return;
    const m = mid ? app.opcoes?.catalogo_magias?.por_id?.[mid] : null;
    if (!m) {
      box.innerHTML = "";
      box.classList.add("oculto");
      return;
    }
    const acaoIco = _iconeAcao(m.acoes);
    const nivelRot = m.eh_truque ? "Truque Mágico" : `${m.nivel}º Círculo`;
    const tradTxt = (m.tradicoes || []).map((t) => NOMES_TRADICAO[t] || t).join(", ");
    const compTxt = (m.componentes || []).join(", ");
    const pills = [
      nivelRot,
      m.escola || null,
      acaoIco ? `Ações: ${acaoIco}` : null,
      compTxt ? `Comp: ${compTxt}` : null,
      tradTxt ? `Tradição: ${tradTxt}` : null,
      m.distancia ? `Alcance: ${m.distancia}` : null,
      m.alvos ? `Alvos: ${m.alvos}` : null,
      m.area ? `Área: ${m.area}` : null,
      m.duracao ? `Duração: ${m.duracao}` : null,
      m.salvamento ? `Salvamento: ${m.salvamento}` : null,
      m.raridade && m.raridade !== "Comum" ? m.raridade : null,
    ]
      .filter(Boolean)
      .map((p) => `<span class="desc-preview-pill">${esc(p)}</span>`)
      .join("");

    box.innerHTML =
      `<div class="desc-preview-topo">` +
      `<span class="desc-preview-titulo">${esc(m.nome)}</span>` +
      `<button type="button" id="btn-fechar-desc-magia" class="desc-preview-fechar" title="Fechar descrição">×</button>` +
      `</div>` +
      (pills ? `<div class="desc-preview-pills">${pills}</div>` : "") +
      `<div class="desc-preview-texto">${esc(m.descricao || m.resumo)}</div>`;
    box.classList.remove("oculto");
  }

  function _renderGradeMagias(gridId, listaIds, fixasMap, selecionadas, vagasLivres, tipoAttr, st, termoBusca) {
    const grid = document.getElementById(gridId);
    if (!grid) return;
    const cheio = selecionadas.length >= vagasLivres;
    const filtrados = listaIds.filter((mid) => {
      if (!termoBusca) return true;
      const m = st.porId[mid];
      if (!m) return false;
      return normTxt(`${m.nome} ${m.escola} ${m.resumo}`).includes(termoBusca);
    });

    if (!filtrados.length) {
      grid.innerHTML = `<div class="box-tal-auto">Nenhuma magia encontrada para o filtro informado.</div>`;
      return;
    }

    grid.innerHTML = filtrados
      .map((mid) => {
        const m = st.porId[mid];
        if (!m) return "";
        const acaoIco = _iconeAcao(m.acoes);
        const origFixa = fixasMap.get(mid);
        const btnInfo = `<button type="button" class="btn-mag-info" data-magia-detalhe="${esc(mid)}" title="Ver descrição completa">ℹ</button>`;
        const resumoHtml = m.resumo ? `<span class="mag-card-resumo">${esc(m.resumo)}</span>` : "";

        if (origFixa) {
          return (
            `<label class="pericia-check-card fixa" title="${esc(m.resumo)}">` +
            `<input type="checkbox" checked disabled>` +
            `<span class="pericia-check-info" style="width:100%">` +
            `<span class="mag-card-linha-topo">` +
            `<span class="pericia-check-titulo">${esc(m.nome)} <span class="pericia-check-atb">${esc(acaoIco)} • ${esc(m.escola)}</span></span>` +
            `${btnInfo}</span>` +
            `<span class="pericia-check-badge fixa">Fixa: ${esc(origFixa)}</span>` +
            `${resumoHtml}</span></label>`
          );
        }
        const marcada = selecionadas.includes(mid);
        const bloqueada = !marcada && cheio;
        const clsCard = `pericia-check-card${marcada ? " selecionada" : ""}${bloqueada ? " bloqueada" : ""}`;
        const badgeDiv =
          tipoAttr === "n1" && mid === st.magiaDivinaId
            ? `<span class="pericia-check-badge fixa">Divindade (${esc(st.divObj?.nome || "")})</span>`
            : "";
        return (
          `<label class="${clsCard}" title="${esc(m.resumo)}">` +
          `<input type="checkbox" data-magia-tipo="${tipoAttr}" data-magia-id="${esc(mid)}" ${marcada ? "checked" : ""} ${bloqueada ? "disabled" : ""}>` +
          `<span class="pericia-check-info" style="width:100%">` +
          `<span class="mag-card-linha-topo">` +
          `<span class="pericia-check-titulo">${esc(m.nome)} <span class="pericia-check-atb">${esc(acaoIco)} • ${esc(m.escola)}</span></span>` +
          `${btnInfo}</span>` +
          (marcada ? `<span class="pericia-check-badge manual">Escolhida</span>` : badgeDiv) +
          `${resumoHtml}</span></label>`
        );
      })
      .join("");
  }

  function atualizarCatalogoMagiasUI() {
    const st = calcularEstadoMagiasUI();
    _atualizarNavegacaoEtapaMagias(st.ehConjurador);

    if (!st.ehConjurador) {
      app.magEstado.truques = [];
      app.magEstado.magias_n1 = [];
      mostrarDetalheMagiaUI(null);
      app.atualizarResumosEtapasUI?.();
      return;
    }

    const elTrad = document.getElementById("mag-resumo-tradicao");
    const elVagas = document.getElementById("mag-resumo-vagas");
    const elExtra = document.getElementById("mag-info-extra");
    const lblTruq = document.getElementById("lbl-mag-truques");
    const lblN1 = document.getElementById("lbl-mag-n1");
    const pillTruq = document.getElementById("pill-mag-truques");
    const pillN1 = document.getElementById("pill-mag-n1");

    if (!st.disponivel) {
      app.magEstado.truques = [];
      app.magEstado.magias_n1 = [];
      if (elTrad) elTrad.textContent = st.motivoIndisponivel || "Aguardando definição de subclasse.";
      if (elVagas) elVagas.textContent = "—";
      if (elExtra) elExtra.textContent = "";
      const gT = document.getElementById("grid-magias-truques");
      const g1 = document.getElementById("grid-magias-n1");
      if (gT) gT.innerHTML = `<div class="box-tal-auto">${esc(st.motivoIndisponivel)}</div>`;
      if (g1) g1.innerHTML = "";
      app.atualizarResumosEtapasUI?.();
      return;
    }

    const setPoolT = new Set(st.poolTruquesIds);
    const setPool1 = new Set(st.poolN1Ids);
    app.magEstado.truques = app.magEstado.truques
      .filter((id) => setPoolT.has(id) && !st.truquesFixos.has(id))
      .slice(0, st.vagasLivresTruques);
    app.magEstado.magias_n1 = app.magEstado.magias_n1
      .filter((id) => setPool1.has(id) && !st.magiasN1Fixas.has(id))
      .slice(0, st.vagasLivresN1);

    const tradNome = NOMES_TRADICAO[st.tradicao] || st.tradicao;
    const estiloNome = st.estilo === "espontanea" ? "Espontânea" : "Preparada";
    if (elTrad) {
      elTrad.textContent = `Tradição: ${tradNome} • ${estiloNome} • ${st.espacosN1} espaço(s) de 1º círculo/dia`;
    }
    if (elVagas) {
      elVagas.textContent = `Truques: ${app.magEstado.truques.length}/${st.vagasLivresTruques} • 1º Círculo: ${app.magEstado.magias_n1.length}/${st.vagasLivresN1}`;
    }
    if (lblTruq) {
      const fixT = st.truquesFixos.size ? ` (+${st.truquesFixos.size} fixa da Linhagem)` : "";
      lblTruq.textContent = `Truques Mágicos — Nível 0${fixT}`;
    }
    if (pillTruq) {
      pillTruq.textContent = `${app.magEstado.truques.length} / ${st.vagasLivresTruques} livres`;
    }
    if (lblN1) {
      const fix1 = st.magiasN1Fixas.size ? ` (+${st.magiasN1Fixas.size} fixa da Subclasse)` : "";
      const rotN1 = st.clsId === "mago" ? "Grimório" : st.estilo === "espontanea" ? "Repertório" : "Preparadas";
      lblN1.textContent = `Magias de 1º Círculo — ${rotN1}${fix1}`;
    }
    if (pillN1) {
      pillN1.textContent = `${app.magEstado.magias_n1.length} / ${st.vagasLivresN1} livres`;
    }

    if (elExtra) {
      const notas = [];
      if (st.clsId === "clerigo") {
        notas.push("Clérigo recebe Fonte Divina automática (Curar ou Ferir, 1 + Mod. CAR espaços extras/dia).");
      } else if (st.clsId === "mago") {
        notas.push(
          st.qtdMagiasN1Total === 6
            ? "Mago Especialista: 6 magias no grimório inicial e 3 espaços/dia (incluindo o espaço extra da Escola Arcana)."
            : "Mago Universalista: 5 magias no grimório inicial e 2 espaços/dia."
        );
      } else if (st.clsId === "feiticeiro") {
        notas.push("Feiticeiro recebe automaticamente o truque e a magia de 1º círculo concedidos pela Linhagem.");
      } else if (st.clsId === "bardo" && st.magiasN1Fixas.size) {
        notas.push("Bardo recebe automaticamente a magia de 1º círculo concedida pela Musa além das 2 livres.");
      }
      notas.push("Vagas deixadas desmarcadas serão completadas automaticamente no modo procedural.");
      elExtra.textContent = notas.join(" ");
    }

    const termoBusca = normTxt(document.getElementById("mag-filtro-busca")?.value || "");
    _renderGradeMagias(
      "grid-magias-truques",
      st.poolTruquesIds,
      st.truquesFixos,
      app.magEstado.truques,
      st.vagasLivresTruques,
      "truque",
      st,
      termoBusca
    );
    _renderGradeMagias(
      "grid-magias-n1",
      st.poolN1Ids,
      st.magiasN1Fixas,
      app.magEstado.magias_n1,
      st.vagasLivresN1,
      "n1",
      st,
      termoBusca
    );

    app.atualizarResumosEtapasUI?.();
  }

  function atualizarVisibilidadeMagiasUI() {
    const modo = document.getElementById("modo-magias")?.value || "procedural";
    document.getElementById("painel-magias-custom")?.classList.toggle("oculto", modo !== "personalizado");
    atualizarCatalogoMagiasUI();
    app.atualizarResumosEtapasUI?.();
  }

  function resetarMagiasProcedural() {
    const modoEl = document.getElementById("modo-magias");
    if (modoEl) modoEl.value = "procedural";
    const buscaEl = document.getElementById("mag-filtro-busca");
    if (buscaEl) buscaEl.value = "";
    app.magEstado.truques = [];
    app.magEstado.magias_n1 = [];
    mostrarDetalheMagiaUI(null);
    atualizarVisibilidadeMagiasUI();
  }

  function montarPayloadMagiasUI() {
    const st = calcularEstadoMagiasUI();
    if (!st.ehConjurador) return { modo: "procedural" };
    const modo = document.getElementById("modo-magias")?.value || "procedural";
    if (modo !== "personalizado") {
      return { modo };
    }
    return {
      modo: "personalizado",
      truques_ids: app.magEstado.truques.length ? [...app.magEstado.truques] : "procedural",
      magias_n1_ids: app.magEstado.magias_n1.length ? [...app.magEstado.magias_n1] : "procedural",
    };
  }

  function alternarCirculoMagia(chave, forcarEstado = null) {
    const cards = document.querySelectorAll(".mag-circulo-card[data-mag-circulo]");
    cards.forEach((card) => {
      const ehAlvo = card.dataset.magCirculo === chave;
      const jaAberta = card.classList.contains("aberta");
      const abrir = ehAlvo ? (forcarEstado !== null ? Boolean(forcarEstado) : !jaAberta) : false;
      card.classList.toggle("aberta", abrir);
      const btn = card.querySelector("[data-mag-toggle]");
      if (btn) btn.setAttribute("aria-expanded", String(abrir));
      const corpo = card.querySelector(".mag-circulo-corpo");
      if (corpo) corpo.classList.toggle("oculto", !abrir);
    });
  }

  function registrarEventosMagias() {
    document.getElementById("modo-magias")?.addEventListener("change", atualizarVisibilidadeMagiasUI);
    document.getElementById("acordeao-magias")?.addEventListener("click", (e) => {
      const btn = e.target.closest("[data-mag-toggle]");
      if (!btn) return;
      alternarCirculoMagia(btn.dataset.magToggle);
    });
    document.getElementById("mag-filtro-busca")?.addEventListener("input", (e) => {
      const temTexto = Boolean((e.target.value || "").trim());
      if (temTexto) {
        document.querySelectorAll(".mag-circulo-card[data-mag-circulo]").forEach((card) => {
          card.classList.add("aberta");
          card.querySelector("[data-mag-toggle]")?.setAttribute("aria-expanded", "true");
          card.querySelector(".mag-circulo-corpo")?.classList.remove("oculto");
        });
      }
      atualizarCatalogoMagiasUI();
    });
    document.getElementById("painel-magias-custom")?.addEventListener("click", (e) => {
      const btnInfo = e.target.closest("[data-magia-detalhe]");
      if (btnInfo) {
        e.preventDefault();
        e.stopPropagation();
        mostrarDetalheMagiaUI(btnInfo.dataset.magiaDetalhe);
        document.getElementById("desc-magia-detalhe")?.scrollIntoView({ behavior: "smooth", block: "nearest" });
        return;
      }
      if (e.target.closest("#btn-fechar-desc-magia")) {
        mostrarDetalheMagiaUI(null);
      }
    });
    document.getElementById("painel-magias-custom")?.addEventListener("change", (e) => {
      const chk = e.target.closest('input[type="checkbox"][data-magia-id]');
      if (!chk) return;
      const tipo = chk.dataset.magiaTipo;
      const mid = chk.dataset.magiaId;
      const st = calcularEstadoMagiasUI();
      if (!st.disponivel) return;
      const lista = tipo === "truque" ? app.magEstado.truques : app.magEstado.magias_n1;
      const limite = tipo === "truque" ? st.vagasLivresTruques : st.vagasLivresN1;
      const fixas = tipo === "truque" ? st.truquesFixos : st.magiasN1Fixas;
      if (fixas.has(mid)) return;

      if (chk.checked) {
        if (!lista.includes(mid) && lista.length < limite) lista.push(mid);
        mostrarDetalheMagiaUI(mid);
      } else {
        const idx = lista.indexOf(mid);
        if (idx >= 0) lista.splice(idx, 1);
      }
      atualizarCatalogoMagiasUI();
    });
    document.getElementById("btn-mag-reset-procedural")?.addEventListener("click", () => {
      resetarMagiasProcedural();
      const modoEl = document.getElementById("modo-magias");
      if (modoEl) modoEl.value = "personalizado";
      atualizarVisibilidadeMagiasUI();
    });
  }

  Object.assign(app, {
    calcularEstadoMagiasUI,
    atualizarCatalogoMagiasUI,
    atualizarVisibilidadeMagiasUI,
    resetarMagiasProcedural,
    montarPayloadMagiasUI,
    registrarEventosMagias,
  });
})();
