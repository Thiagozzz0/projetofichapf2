(() => {
  "use strict";

  const app = window.PF2EApp;
  const { renderSeloAcao, renderBadgeTradicao } = window.PF2EFichaUI;
  const { esc, CLASSES_CONJURADORAS_UI, IDS_TAL_GERAIS, normTxt } = app;

  const NOMES_TRADICAO = {
    arcana: "Arcana",
    divina: "Divina",
    ocultista: "Ocultista",
    primal: "Primal",
  };

  function _obterOrigemTruqueInatoHerancaUI() {
    const ancId = document.getElementById("ancestralidade")?.value || "aleatorio";
    const herId = document.getElementById("heranca")?.value || "aleatorio";
    if (ancId === "gnomo" && herId === "gnomo_tocado_pelas_fadas") {
      return {
        ativo: true,
        tradicoes: ["primal"],
        tradNome: "Primal",
        herancaId: herId,
        origemLabel: "Herança (Gnomo Tocado pelas Fadas)",
      };
    }
    if (ancId === "gnomo" && herId === "gnomo_manancial") {
      return {
        ativo: true,
        tradicoes: ["arcana", "divina", "ocultista"],
        tradNome: "Arcana / Divina / Ocultista",
        herancaId: herId,
        origemLabel: "Herança (Gnomo Manancial)",
      };
    }
    return { ativo: false };
  }

  function _obterOrigemTruqueInatoUI() {
    if ((document.getElementById("modo-talentos")?.value || "procedural") !== "personalizado") {
      return { ativo: false };
    }
    const elAnc = document.getElementById("tal-ancestralidade");
    const talAnc = elAnc && !elAnc.disabled && !elAnc.closest(".oculto") ? elAnc.value : "procedural";
    const elAncN5 = document.getElementById("tal-ancestralidade-n5");
    const talAncN5 = elAncN5 && !elAncN5.disabled && !elAncN5.closest(".oculto") ? elAncN5.value : "procedural";
    const temAdotada = (IDS_TAL_GERAIS || []).some((id) => {
      const el = document.getElementById(id);
      return el && !el.disabled && !el.closest(".oculto") && el.value === "ancestralidade_adotada";
    });
    const talAdotado = temAdotada ? app.talEstado?.talentoAdotadoId : null;

    let fonte = null;
    if (talAnc === "magia_extraterrena" || talAnc === "magia_do_primeiro_mundo") {
      fonte = { id: talAnc, ehAdotado: false };
    } else if (talAncN5 === "magia_extraterrena" || talAncN5 === "magia_do_primeiro_mundo") {
      fonte = { id: talAncN5, ehAdotado: false };
    } else if (talAdotado === "magia_extraterrena" || talAdotado === "magia_do_primeiro_mundo") {
      fonte = { id: talAdotado, ehAdotado: true };
    }
    if (!fonte) return { ativo: false };

    const ehArcana = fonte.id === "magia_extraterrena";
    const tradicao = ehArcana ? "arcana" : "primal";
    const tradNome = NOMES_TRADICAO[tradicao];
    const talentoNome = ehArcana ? "Magia Extraterrena" : "Magia do Primeiro Mundo";
    const origemLabel = fonte.ehAdotado
      ? `Ancestralidade Adotada (${app.talEstado?.ancestralidadeAdotadaNome || "Outra Ancestralidade"} • ${talentoNome})`
      : `Talento Ancestral (${talentoNome})`;

    return { ativo: true, tradicao, tradNome, talentoId: fonte.id, talentoNome, origemLabel, ehAdotado: fonte.ehAdotado };
  }

  function _renderPreviewTruqueInatoElementoUI(boxId, mid) {
    const box = document.getElementById(boxId);
    if (!box) return;
    const m = mid && mid !== "procedural" ? app.opcoes?.catalogo_magias?.por_id?.[mid] : null;
    if (!m) {
      box.innerHTML = "";
      box.classList.add("oculto");
      return;
    }
    const acaoIco = _iconeAcao(m.acoes);
    box.innerHTML =
      `<div class="desc-preview-topo"><span class="desc-preview-titulo">${esc(m.nome)} ${renderSeloAcao(acaoIco)}</span></div>` +
      `<div class="desc-preview-pills"><span class="desc-preview-pill">Truque Mágico</span>` +
      (m.escola ? `<span class="desc-preview-pill">${esc(m.escola)}</span>` : "") +
      `</div>` +
      `<div class="desc-preview-texto">${esc(m.descricao || m.resumo)}</div>`;
    box.classList.remove("oculto");
  }

  function _renderPreviewTruqueInatoUI(mid) {
    _renderPreviewTruqueInatoElementoUI("desc-truque-inato-ancestral", mid);
  }

  function _renderPreviewTruqueInatoHerancaUI(mid) {
    _renderPreviewTruqueInatoElementoUI("desc-truque-inato-heranca", mid);
  }

  function _atualizarBlocoMagiaInataHerancaUI() {
    const box = document.getElementById("box-magia-inata-heranca");
    const sel = document.getElementById("sel-truque-inato-heranca");
    const lbl = document.getElementById("lbl-magia-inata-heranca");
    const badge = document.getElementById("badge-magia-inata-heranca");
    const nota = document.getElementById("nota-magia-inata-heranca");
    const inatoHer = _obterOrigemTruqueInatoHerancaUI();
    const cat = app.opcoes?.catalogo_magias;

    if (!box || !sel || !inatoHer.ativo || !cat) {
      if (box) box.classList.add("oculto");
      if (app.magEstado) app.magEstado.truqueInatoHerancaId = "procedural";
      _renderPreviewTruqueInatoHerancaUI(null);
      return inatoHer;
    }

    box.classList.remove("oculto");
    if (lbl) lbl.textContent = `Truque Mágico Inato — ${inatoHer.tradNome}`;
    if (badge) badge.textContent = "Herança";
    if (nota) {
      nota.textContent = `Concedido por: ${inatoHer.origemLabel}. Escolha 1 truque mágico à vontade (${inatoHer.tradNome}) ou deixe em Procedural.`;
    }

    const idsSet = new Set();
    inatoHer.tradicoes.forEach((tr) => {
      (cat.por_tradicao?.[tr]?.truques || []).forEach((mid) => idsSet.add(mid));
    });
    const poolOrdenado = Array.from(idsSet)
      .map((mid) => cat.por_id?.[mid])
      .filter(Boolean)
      .sort((a, b) => a.nome.localeCompare(b.nome, "pt-BR"));

    const atual = app.magEstado?.truqueInatoHerancaId || sel.value || "procedural";
    sel.innerHTML = "";
    const optProc = document.createElement("option");
    optProc.value = "procedural";
    optProc.textContent = `Procedural (melhor truque ${inatoHer.tradNome} p/ o conceito)`;
    sel.appendChild(optProc);

    const multiTrad = inatoHer.tradicoes.length > 1;
    poolOrdenado.forEach((m) => {
      const opt = document.createElement("option");
      opt.value = m.id;
      if (multiTrad) {
        const tradsComp = inatoHer.tradicoes
          .filter((t) => (m.tradicoes || []).includes(t))
          .map((t) => NOMES_TRADICAO[t] || t)
          .join("/");
        opt.textContent = tradsComp ? `${m.nome} (${tradsComp})` : m.nome;
      } else {
        opt.textContent = `${m.nome}${m.escola ? ` (${m.escola})` : ""}`;
      }
      sel.appendChild(opt);
    });

    sel.value = idsSet.has(atual) ? atual : "procedural";
    if (app.magEstado) app.magEstado.truqueInatoHerancaId = sel.value;
    _renderPreviewTruqueInatoHerancaUI(sel.value);
    return inatoHer;
  }

  function _atualizarBlocoMagiaInataUI() {
    const box = document.getElementById("box-magia-inata-ancestral");
    const sel = document.getElementById("sel-truque-inato-ancestral");
    const lbl = document.getElementById("lbl-magia-inata-ancestral");
    const badge = document.getElementById("badge-magia-inata-ancestral");
    const nota = document.getElementById("nota-magia-inata-ancestral");
    const inato = _obterOrigemTruqueInatoUI();
    const cat = app.opcoes?.catalogo_magias;

    if (!box || !sel || !inato.ativo || !cat) {
      if (box) box.classList.add("oculto");
      if (app.magEstado) app.magEstado.truqueInatoAncestralId = "procedural";
      _renderPreviewTruqueInatoUI(null);
      return inato;
    }

    box.classList.remove("oculto");
    if (lbl) lbl.textContent = `Truque Mágico Inato (${inato.tradNome})`;
    if (badge) badge.textContent = inato.ehAdotado ? "Ancestralidade Adotada" : "Talento Ancestral";
    if (nota) {
      nota.textContent = `Concedido por: ${inato.origemLabel}. Escolha 1 truque mágico à vontade da tradição ${inato.tradNome} ou deixe em Procedural.`;
    }

    const poolIds = cat.por_tradicao?.[inato.tradicao]?.truques || [];
    const atual = app.magEstado?.truqueInatoAncestralId || sel.value || "procedural";
    sel.innerHTML = "";
    const optProc = document.createElement("option");
    optProc.value = "procedural";
    optProc.textContent = `Procedural (melhor truque ${inato.tradNome} p/ o conceito)`;
    sel.appendChild(optProc);

    poolIds.forEach((mid) => {
      const m = cat.por_id[mid];
      if (!m) return;
      const opt = document.createElement("option");
      opt.value = mid;
      opt.textContent = `${m.nome}${m.escola ? ` (${m.escola})` : ""}`;
      sel.appendChild(opt);
    });

    sel.value = poolIds.includes(atual) ? atual : "procedural";
    if (app.magEstado) app.magEstado.truqueInatoAncestralId = sel.value;
    _renderPreviewTruqueInatoUI(sel.value);
    return inato;
  }

  function obterResumoMagiaInataUI() {
    const partes = [];
    const inatoHer = _obterOrigemTruqueInatoHerancaUI();
    if (inatoHer.ativo) {
      const midHer = app.magEstado?.truqueInatoHerancaId || document.getElementById("sel-truque-inato-heranca")?.value || "procedural";
      if (midHer === "procedural") {
        partes.push("Herança Inata (Proc.)");
      } else {
        const mh = app.opcoes?.catalogo_magias?.por_id?.[midHer];
        partes.push(mh ? `Herança: ${mh.nome}` : "Herança Inata");
      }
    }
    const inato = _obterOrigemTruqueInatoUI();
    if (inato.ativo) {
      const mid = app.magEstado?.truqueInatoAncestralId || document.getElementById("sel-truque-inato-ancestral")?.value || "procedural";
      if (mid === "procedural") {
        partes.push(`Inata ${inato.tradNome} (Proc.)`);
      } else {
        const m = app.opcoes?.catalogo_magias?.por_id?.[mid];
        partes.push(m ? `Inata: ${m.nome}` : `Inata ${inato.tradNome}`);
      }
    }
    return partes.length ? partes.join(" + ") : null;
  }

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

    const nivel = app.obterNivelSelecionadoUI?.() || 1;
    const prog = conjCls.progressao_por_nivel?.[String(nivel)] || null;
    const ehEspecialistaMago = clsId === "mago" && !(subDeterm?.eh_universalista || conObj?.mago_universalista);

    const qtdTruquesTotal = Number(prog?.truques_magicos ?? conjCls.qtd_truques ?? 5);
    const espProg = prog?.espacos_por_circulo || { "1": conjCls.espacos_n1_base ?? 2 };

    const espacosPorCirculo = {};
    const qtdMagiasPorCirculo = {};
    const fixasPorCirculo = { 1: new Map(), 2: new Map(), 3: new Map() };
    const poolsPorCirculo = { 1: [], 2: [], 3: [] };
    const vagasLivresPorCirculo = { 1: 0, 2: 0, 3: 0 };

    const truquesFixos = new Map();
    if (subDeterm?.truque_fixo_id && cat.por_id[subDeterm.truque_fixo_id]) {
      truquesFixos.set(subDeterm.truque_fixo_id, `Linhagem (${conObj.subclasse_oficial_nome})`);
    }
    if (subDeterm?.magia_n1_fixa_id && cat.por_id[subDeterm.magia_n1_fixa_id]) {
      const rot = clsId === "bardo" ? "Musa" : "Linhagem";
      fixasPorCirculo[1].set(subDeterm.magia_n1_fixa_id, `${rot} (${conObj.subclasse_oficial_nome})`);
    }

    const poolTruquesIds = [...(cat.por_tradicao[tradicao]?.truques || [])];
    truquesFixos.forEach((_, mid) => {
      if (!poolTruquesIds.includes(mid)) poolTruquesIds.unshift(mid);
    });

    let magiaDivinaId = null;
    [1, 2, 3].forEach((c) => {
      const baseEsp = Number(espProg[String(c)] || 0);
      if (baseEsp <= 0) {
        espacosPorCirculo[c] = 0;
        qtdMagiasPorCirculo[c] = 0;
        vagasLivresPorCirculo[c] = 0;
        return;
      }
      const espC = baseEsp + (ehEspecialistaMago ? 1 : 0);
      espacosPorCirculo[c] = espC;

      let qtdC = espC;
      if (clsId === "mago") {
        if (c === 1) {
          const baseM1 = ehEspecialistaMago ? 6 : 5;
          qtdC = baseM1 + (nivel >= 2 ? 2 : 0);
        } else {
          qtdC = Math.max(espC, nivel === 2 * c - 1 ? 2 : 4);
        }
      } else if (clsId === "bardo") {
        qtdC = espC + (c === 1 && fixasPorCirculo[1].size > 0 ? 1 : 0);
      } else if (clsId === "feiticeiro") {
        qtdC = c === 1 ? Math.max(espC, 3) : espC;
      }
      qtdMagiasPorCirculo[c] = qtdC;

      const tradObj = cat.por_tradicao[tradicao] || {};
      const listaTrad = tradObj.por_circulo?.[String(c)] || tradObj[`nivel_${c}`] || [];
      const poolC = [...listaTrad];
      fixasPorCirculo[c].forEach((_, mid) => {
        if (!poolC.includes(mid)) poolC.unshift(mid);
      });
      if (c === 1 && clsId === "clerigo" && divObj?.magia_clerigo_n1_id && cat.por_id[divObj.magia_clerigo_n1_id]) {
        magiaDivinaId = divObj.magia_clerigo_n1_id;
        if (!poolC.includes(magiaDivinaId)) poolC.unshift(magiaDivinaId);
      }
      poolsPorCirculo[c] = poolC;
      vagasLivresPorCirculo[c] = Math.max(0, qtdC - fixasPorCirculo[c].size);
    });

    const vagasLivresTruques = Math.max(0, qtdTruquesTotal - truquesFixos.size);

    return {
      ehConjurador: true,
      disponivel: true,
      nivel,
      clsId,
      clsObj,
      conObj,
      divObj,
      tradicao,
      estilo: conjCls.estilo,
      qtdTruquesTotal,
      espacosPorCirculo,
      qtdMagiasPorCirculo,
      vagasLivresPorCirculo,
      fixasPorCirculo,
      poolsPorCirculo,
      espacosN1: espacosPorCirculo[1] || 0,
      qtdMagiasN1Total: qtdMagiasPorCirculo[1] || 0,
      vagasLivresTruques,
      vagasLivresN1: vagasLivresPorCirculo[1] || 0,
      truquesFixos,
      magiasN1Fixas: fixasPorCirculo[1],
      magiaDivinaId,
      poolTruquesIds,
      poolN1Ids: poolsPorCirculo[1],
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
      return normTxt(`${m.nome} ${m.escola} ${(m.tracos || []).join(" ")} ${m.resumo}`).includes(termoBusca);
    });

    if (!filtrados.length) {
      grid.innerHTML = `<div class="box-tal-auto">Nenhuma magia encontrada para o filtro informado.</div>`;
      return 0;
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
            `<span class="pericia-check-titulo">${esc(m.nome)} ${renderSeloAcao(acaoIco)} <span class="pericia-check-atb">${esc(m.escola)}</span></span>` +
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
          `<span class="pericia-check-titulo">${esc(m.nome)} ${renderSeloAcao(acaoIco)} <span class="pericia-check-atb">${esc(m.escola)}</span></span>` +
          `${btnInfo}</span>` +
          (marcada ? `<span class="pericia-check-badge manual">Escolhida</span>` : badgeDiv) +
          `${resumoHtml}</span></label>`
        );
      })
      .join("");
    return filtrados.length;
  }

  function atualizarCatalogoMagiasUI() {
    const st = calcularEstadoMagiasUI();
    const inatoHer = _atualizarBlocoMagiaInataHerancaUI();
    const inato = _atualizarBlocoMagiaInataUI();
    _atualizarNavegacaoEtapaMagias(st.ehConjurador || inato.ativo || inatoHer.ativo);
    document.getElementById("bloco-magias-classe")?.classList.toggle("oculto", !st.ehConjurador);

    if (!st.ehConjurador) {
      app.magEstado.truques = [];
      app.magEstado.magias_n1 = [];
      app.magEstado.magias_n2 = [];
      app.magEstado.magias_n3 = [];
      mostrarDetalheMagiaUI(null);
      app.atualizarResumosEtapasUI?.();
      return;
    }

    const elTrad = document.getElementById("mag-resumo-tradicao");
    const elVagas = document.getElementById("mag-resumo-vagas");
    const elExtra = document.getElementById("mag-info-extra");
    const lblTruq = document.getElementById("lbl-mag-truques");
    const pillTruq = document.getElementById("pill-mag-truques");

    if (!st.disponivel) {
      app.magEstado.truques = [];
      app.magEstado.magias_n1 = [];
      app.magEstado.magias_n2 = [];
      app.magEstado.magias_n3 = [];
      if (elTrad) elTrad.textContent = st.motivoIndisponivel || "Aguardando definição de subclasse.";
      if (elVagas) elVagas.textContent = "—";
      if (elExtra) elExtra.textContent = "";
      const gT = document.getElementById("grid-magias-truques");
      if (gT) gT.innerHTML = `<div class="box-tal-auto">${esc(st.motivoIndisponivel)}</div>`;
      [1, 2, 3].forEach((c) => {
        const gC = document.getElementById(`grid-magias-n${c}`);
        if (gC) gC.innerHTML = "";
        const cardC = document.querySelector(`.mag-circulo-card[data-mag-circulo="n${c}"]`);
        if (cardC && c >= 2) cardC.classList.add("oculto");
      });
      app.atualizarResumosEtapasUI?.();
      return;
    }

    const setPoolT = new Set(st.poolTruquesIds);
    app.magEstado.truques = app.magEstado.truques
      .filter((id) => setPoolT.has(id) && !st.truquesFixos.has(id))
      .slice(0, st.vagasLivresTruques);

    [1, 2, 3].forEach((c) => {
      const chave = `magias_n${c}`;
      if ((st.espacosPorCirculo[c] || 0) <= 0) {
        app.magEstado[chave] = [];
        return;
      }
      const setPoolC = new Set(st.poolsPorCirculo[c] || []);
      const fixasC = st.fixasPorCirculo[c];
      app.magEstado[chave] = (app.magEstado[chave] || [])
        .filter((id) => setPoolC.has(id) && !fixasC.has(id))
        .slice(0, st.vagasLivresPorCirculo[c]);
    });

    const tradNome = NOMES_TRADICAO[st.tradicao] || st.tradicao;
    const estiloNome = st.estilo === "espontanea" ? "Espontânea" : "Preparada";
    const espTextoLista = [1, 2, 3]
      .filter((c) => (st.espacosPorCirculo[c] || 0) > 0)
      .map((c) => `${c}º: ${st.espacosPorCirculo[c]}`);
    const espResumoTrad =
      espTextoLista.length <= 1
        ? `${st.espacosN1} espaço(s) de 1º círculo/dia`
        : `Espaços/dia: ${espTextoLista.join(" • ")}`;

    if (elTrad) {
      elTrad.innerHTML = `Tradição: ${renderBadgeTradicao(st.tradicao, tradNome)} • ${esc(estiloNome)} • ${esc(espResumoTrad)}`;
    }

    const vagasPartes = [`Truques: ${app.magEstado.truques.length}/${st.vagasLivresTruques}`];
    [1, 2, 3].forEach((c) => {
      if ((st.espacosPorCirculo[c] || 0) > 0) {
        vagasPartes.push(`${c}º Círculo: ${app.magEstado[`magias_n${c}`].length}/${st.vagasLivresPorCirculo[c]}`);
      }
    });
    if (elVagas) {
      elVagas.textContent = vagasPartes.join(" • ");
    }

    if (lblTruq) {
      const fixT = st.truquesFixos.size ? ` (+${st.truquesFixos.size} fixa da Linhagem)` : "";
      const nivelTruque = Math.ceil((st.nivel || 1) / 2);
      lblTruq.textContent =
        nivelTruque > 1
          ? `Truques Mágicos — Elevados p/ ${nivelTruque}º Círculo${fixT}`
          : `Truques Mágicos — Nível 0${fixT}`;
    }
    if (pillTruq) {
      pillTruq.textContent = `${app.magEstado.truques.length} / ${st.vagasLivresTruques} livres`;
    }

    const rotCirc = st.clsId === "mago" ? "Grimório" : st.estilo === "espontanea" ? "Repertório" : "Preparadas";
    [1, 2, 3].forEach((c) => {
      const cardC = document.querySelector(`.mag-circulo-card[data-mag-circulo="n${c}"]`);
      const ativoC = (st.espacosPorCirculo[c] || 0) > 0;
      if (cardC) cardC.classList.toggle("oculto", !ativoC);

      const lblC = document.getElementById(`lbl-mag-n${c}`);
      const pillC = document.getElementById(`pill-mag-n${c}`);
      if (lblC) {
        const fixC = st.fixasPorCirculo[c].size ? ` (+${st.fixasPorCirculo[c].size} fixa da Subclasse)` : "";
        lblC.textContent = `Magias de ${c}º Círculo — ${rotCirc}${fixC}`;
      }
      if (pillC) {
        pillC.textContent = `${(app.magEstado[`magias_n${c}`] || []).length} / ${st.vagasLivresPorCirculo[c]} livres`;
      }
    });

    if (elExtra) {
      const notas = [];
      if (st.clsId === "clerigo") {
        notas.push("Clérigo recebe Fonte Divina automática (Curar ou Ferir, 1 + Mod. CAR espaços extras/dia).");
      } else if (st.clsId === "mago") {
        notas.push(
          st.qtdMagiasN1Total >= 6
            ? `Mago Especialista: ${st.qtdMagiasN1Total} magias de 1º círculo no grimório e +1 espaço/dia por círculo desbloqueado.`
            : `Mago Universalista: ${st.qtdMagiasN1Total} magias de 1º círculo no grimório.`
        );
      } else if (st.clsId === "feiticeiro") {
        notas.push("Feiticeiro recebe automaticamente o truque e as magias concedidas pela Linhagem.");
      } else if (st.clsId === "bardo" && st.magiasN1Fixas.size) {
        notas.push("Bardo recebe automaticamente a magia de 1º círculo concedida pela Musa além das livres.");
      }
      notas.push("Vagas deixadas desmarcadas serão completadas automaticamente no modo procedural.");
      elExtra.textContent = notas.join(" ");
    }

    const termoBusca = normTxt(document.getElementById("mag-filtro-busca")?.value || "");
    document.getElementById("btn-mag-limpar-busca")?.classList.toggle("oculto", !termoBusca);
    const qtdTruq = _renderGradeMagias(
      "grid-magias-truques",
      st.poolTruquesIds,
      st.truquesFixos,
      app.magEstado.truques,
      st.vagasLivresTruques,
      "truque",
      st,
      termoBusca
    );
    const qtdPorCirc = {};
    [1, 2, 3].forEach((c) => {
      if ((st.espacosPorCirculo[c] || 0) > 0) {
        qtdPorCirc[c] = _renderGradeMagias(
          `grid-magias-n${c}`,
          st.poolsPorCirculo[c],
          st.fixasPorCirculo[c],
          app.magEstado[`magias_n${c}`],
          st.vagasLivresPorCirculo[c],
          `n${c}`,
          st,
          termoBusca
        );
      } else {
        const gC = document.getElementById(`grid-magias-n${c}`);
        if (gC) gC.innerHTML = "";
      }
    });
    const elBuscaStatus = document.getElementById("mag-busca-status");
    if (elBuscaStatus) {
      elBuscaStatus.classList.toggle("oculto", !termoBusca);
      if (termoBusca) {
        const partesBusca = [`${qtdTruq} truque(s)`];
        [1, 2, 3].forEach((c) => {
          if (qtdPorCirc[c] !== undefined) {
            partesBusca.push(`${qtdPorCirc[c]} magia(s) de ${c}º círculo`);
          }
        });
        elBuscaStatus.textContent = `Encontradas: ${partesBusca.join(" • ")}.`;
      }
    }

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
    app.magEstado.magias_n2 = [];
    app.magEstado.magias_n3 = [];
    app.magEstado.truqueInatoAncestralId = "procedural";
    app.magEstado.truqueInatoHerancaId = "procedural";
    const selInato = document.getElementById("sel-truque-inato-ancestral");
    if (selInato) selInato.value = "procedural";
    const selInatoHer = document.getElementById("sel-truque-inato-heranca");
    if (selInatoHer) selInatoHer.value = "procedural";
    _renderPreviewTruqueInatoUI(null);
    _renderPreviewTruqueInatoHerancaUI(null);
    mostrarDetalheMagiaUI(null);
    atualizarVisibilidadeMagiasUI();
  }

  function montarPayloadMagiasUI() {
    const st = calcularEstadoMagiasUI();
    const inato = _obterOrigemTruqueInatoUI();
    const inatoHer = _obterOrigemTruqueInatoHerancaUI();
    const truqInatoVal = document.getElementById("sel-truque-inato-ancestral")?.value || app.magEstado?.truqueInatoAncestralId || "procedural";
    const truqInatoHerVal = document.getElementById("sel-truque-inato-heranca")?.value || app.magEstado?.truqueInatoHerancaId || "procedural";

    const anexarInatos = (payload) => {
      if (inato.ativo && truqInatoVal !== "procedural") {
        payload.truque_inato_ancestral_id = truqInatoVal;
      }
      if (inatoHer.ativo && truqInatoHerVal !== "procedural") {
        payload.truque_inato_heranca_id = truqInatoHerVal;
      }
      return payload;
    };

    if (!st.ehConjurador) {
      return anexarInatos({ modo: "procedural" });
    }
    const modo = document.getElementById("modo-magias")?.value || "procedural";
    if (modo !== "personalizado") {
      return anexarInatos({ modo });
    }
    const payload = anexarInatos({
      modo: "personalizado",
      truques_ids: app.magEstado.truques.length ? [...app.magEstado.truques] : "procedural",
      magias_n1_ids: app.magEstado.magias_n1.length ? [...app.magEstado.magias_n1] : "procedural",
    });
    if ((st.espacosPorCirculo?.[2] || 0) > 0 && app.magEstado.magias_n2.length) {
      payload.magias_n2_ids = [...app.magEstado.magias_n2];
    }
    if ((st.espacosPorCirculo?.[3] || 0) > 0 && app.magEstado.magias_n3.length) {
      payload.magias_n3_ids = [...app.magEstado.magias_n3];
    }
    return payload;
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
    document.getElementById("sel-truque-inato-heranca")?.addEventListener("change", (e) => {
      const val = e.currentTarget.value || "procedural";
      if (app.magEstado) app.magEstado.truqueInatoHerancaId = val;
      _renderPreviewTruqueInatoHerancaUI(val);
      app.atualizarResumosEtapasUI?.();
    });
    document.getElementById("sel-truque-inato-ancestral")?.addEventListener("change", (e) => {
      const val = e.currentTarget.value || "procedural";
      if (app.magEstado) app.magEstado.truqueInatoAncestralId = val;
      _renderPreviewTruqueInatoUI(val);
      app.atualizarResumosEtapasUI?.();
    });
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
          if (card.classList.contains("oculto")) return;
          card.classList.add("aberta");
          card.querySelector("[data-mag-toggle]")?.setAttribute("aria-expanded", "true");
          card.querySelector(".mag-circulo-corpo")?.classList.remove("oculto");
        });
      }
      atualizarCatalogoMagiasUI();
    });
    document.getElementById("btn-mag-limpar-busca")?.addEventListener("click", () => {
      const inp = document.getElementById("mag-filtro-busca");
      if (inp) {
        inp.value = "";
        inp.focus();
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

      let lista;
      let limite;
      let fixas;
      if (tipo === "truque") {
        lista = app.magEstado.truques;
        limite = st.vagasLivresTruques;
        fixas = st.truquesFixos;
      } else {
        const circ = parseInt(String(tipo || "").replace("n", ""), 10) || 1;
        lista = app.magEstado[`magias_n${circ}`];
        limite = st.vagasLivresPorCirculo[circ] || 0;
        fixas = st.fixasPorCirculo[circ] || new Map();
      }
      if (!lista || fixas.has(mid)) return;

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
    obterResumoMagiaInataUI,
    resetarMagiasProcedural,
    montarPayloadMagiasUI,
    registrarEventosMagias,
  });
})();
