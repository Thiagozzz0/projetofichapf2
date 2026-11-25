(() => {
  "use strict";

  const app = window.PF2EApp;
  const { esc } = window.PF2EFichaUI;
  const { ORDEM_ATRIBUTOS, IDS_LIVRES_N1, TALENTOS_PERICIAS_ANC_UI } = app;

  function _calcularModIntAtualUI() {
    const ancId = document.getElementById("ancestralidade")?.value || "aleatorio";
    const bioId = document.getElementById("biografia")?.value || "procedural";
    const clsId = document.getElementById("classe")?.value || "aleatorio";
    const conId = document.getElementById("conceito")?.value || "aleatorio";
    const ancObj = app.opcoes?.ancestralidades?.find((a) => a.id === ancId) || null;
    const bioObj = app.opcoes?.biografias?.find((b) => b.id === bioId) || null;
    const clsObj = app.opcoes?.classes?.find((c) => c.id === clsId) || null;
    const conObj = clsObj ? clsObj.conceitos.find((x) => x.id === conId) : null;
    const pri = conObj?.prioridade_atributos || [];

    let intVal = 10;

    // A — Ancestralidade
    if (ancObj) {
      if ((ancObj.melhorias_fixas_ids || []).includes("int")) intVal += 2;
      if (ancObj.defeito_atributo_id === "int") intVal -= 2;
      const bloqA = new Set(ancObj.atributos_bloqueados_livres_ids || []);
      const qtdLivA = Number(ancObj.qtd_melhorias_livres || 1);
      const idsA = qtdLivA >= 2 ? ["attr-anc-livre-1", "attr-anc-livre-2"] : ["attr-anc-livre-1"];
      const usadosA = new Set(bloqA);
      let pegouIntA = false;
      idsA.forEach((id) => {
        const v = document.getElementById(id)?.value || "procedural";
        if (ORDEM_ATRIBUTOS.includes(v)) {
          usadosA.add(v);
          if (v === "int") pegouIntA = true;
        }
      });
      if (!pegouIntA) {
        idsA.forEach((id) => {
          const v = document.getElementById(id)?.value || "procedural";
          if (v === "procedural" && pri.length) {
            const escA = pri.find((a) => !usadosA.has(a));
            if (escA) {
              usadosA.add(escA);
              if (escA === "int") pegouIntA = true;
            }
          }
        });
      }
      if (pegouIntA) intVal += 2;
    }

    // B — Biografia
    const vBioRes = document.getElementById("attr-bio-restrito")?.value || "procedural";
    const vBioLiv = document.getElementById("attr-bio-livre")?.value || "procedural";
    let bioResFinal = ORDEM_ATRIBUTOS.includes(vBioRes) ? vBioRes : null;
    let bioLivFinal = ORDEM_ATRIBUTOS.includes(vBioLiv) ? vBioLiv : null;
    if (!bioResFinal && vBioRes === "procedural" && bioObj && pri.length) {
      const opBio = bioObj.melhorias_atributo_ids || [];
      bioResFinal = pri.find((a) => opBio.includes(a) && a !== bioLivFinal) || opBio[0] || null;
    }
    if (!bioLivFinal && vBioLiv === "procedural" && pri.length) {
      bioLivFinal = pri.find((a) => a !== bioResFinal) || null;
    }
    if (bioResFinal === "int" || bioLivFinal === "int") intVal += 2;

    // C — Classe
    if (clsObj) {
      const chaves = conObj?.atributo_chave_opcoes?.length ? conObj.atributo_chave_opcoes : clsObj.atributo_chave_ids || [];
      const vCls = document.getElementById("attr-classe-chave")?.value || "procedural";
      let chaveFinal = chaves.length === 1 ? chaves[0] : ORDEM_ATRIBUTOS.includes(vCls) ? vCls : null;
      if (!chaveFinal && vCls === "procedural" && pri.length) {
        chaveFinal = pri.find((a) => chaves.includes(a)) || chaves[0] || null;
      }
      if (chaveFinal === "int") intVal += 2;
    }

    // D — 4 Livres N1
    const usadosD = new Set();
    let procCountD = 0;
    IDS_LIVRES_N1.forEach((id) => {
      const v = document.getElementById(id)?.value || "procedural";
      if (ORDEM_ATRIBUTOS.includes(v)) usadosD.add(v);
      else if (v === "procedural") procCountD += 1;
    });
    if (!usadosD.has("int") && procCountD > 0 && pri.length) {
      for (let i = 0; i < procCountD; i += 1) {
        const cand = pri.find((a) => !usadosD.has(a));
        if (!cand) break;
        usadosD.add(cand);
      }
    }
    if (usadosD.has("int")) intVal += 2;

    intVal = Math.min(18, intVal);
    return { intVal, modInt: Math.floor((intVal - 10) / 2) };
  }

  function _preencherSelectPericiaOpcao(sel, opcoesIds, mapaPer, textoProc) {
    if (!sel) return;
    const ant = sel.value || "procedural";
    sel.innerHTML = `<option value="procedural">${esc(textoProc || "Procedural (melhor p/ conceito)")}</option>`;
    opcoesIds.forEach((pid) => {
      const p = mapaPer[pid];
      if (!p) return;
      const opt = document.createElement("option");
      opt.value = pid;
      opt.textContent = `${p.nome} (${p.atributo_sigla})`;
      sel.appendChild(opt);
    });
    sel.value = ant === "procedural" || opcoesIds.includes(ant) ? ant : "procedural";
  }

  function calcularEstadoPericiasUI() {
    const catPer = app.opcoes?.catalogo_pericias || [];
    const mapaPer = Object.fromEntries(catPer.map((p) => [p.id, p]));
    const herId = document.getElementById("heranca")?.value || "aleatorio";
    const bioId = document.getElementById("biografia")?.value || "procedural";
    const clsId = document.getElementById("classe")?.value || "aleatorio";
    const conId = document.getElementById("conceito")?.value || "aleatorio";
    const divId = document.getElementById("divindade")?.value || "";

    const bioObj = app.opcoes?.biografias?.find((b) => b.id === bioId) || null;
    const clsObj = app.opcoes?.classes?.find((c) => c.id === clsId) || null;
    const conObj = clsObj ? clsObj.conceitos.find((x) => x.id === conId) : null;
    const divObj = (app.opcoes?.divindades || []).find((d) => d.id === divId) || null;

    if (!clsObj || clsId === "aleatorio" || !clsObj.pericias_classe) {
      return { disponivel: false, bioObj, mapaPer };
    }

    const fixasMap = new Map();
    const sobreposicoes = [];
    const concederFixa = (pid, origem) => {
      if (!pid || !mapaPer[pid]) return;
      if (fixasMap.has(pid)) sobreposicoes.push({ id: pid, origem });
      else fixasMap.set(pid, origem);
    };

    // 1. Biografia
    const opBioIds = bioObj?.pericia_treinada_ids || [];
    let temOpcaoBio = false;
    if (opBioIds.length === 1) {
      concederFixa(opBioIds[0], `Biografia (${bioObj.nome})`);
    } else if (opBioIds.length > 1) {
      temOpcaoBio = true;
      const selBioOp = document.getElementById("per-bio-opcao");
      _preencherSelectPericiaOpcao(selBioOp, opBioIds, mapaPer, `Procedural (${opBioIds.map((id) => mapaPer[id]?.nome).join(" / ")})`);
      const valBio = selBioOp?.value || "procedural";
      if (valBio !== "procedural" && opBioIds.includes(valBio)) {
        concederFixa(valBio, `Biografia (${bioObj.nome})`);
      } else {
        concederFixa(opBioIds[0], `Biografia (${bioObj.nome} — Proc.)`);
      }
    }

    // 2. Classe (fixas e opções fixas como Guerreiro)
    const perCls = clsObj.pericias_classe;
    (perCls.fixas || []).forEach((pid) => concederFixa(pid, `Classe (${clsObj.nome})`));

    const opClsIds = perCls.opcoes_fixas || [];
    let temOpcaoCls = false;
    if (opClsIds.length > 0) {
      temOpcaoCls = true;
      const selClsOp = document.getElementById("per-cls-opcao");
      _preencherSelectPericiaOpcao(selClsOp, opClsIds, mapaPer, `Procedural (${opClsIds.map((id) => mapaPer[id]?.nome).join(" / ")})`);
      const valCls = selClsOp?.value || "procedural";
      if (valCls !== "procedural" && opClsIds.includes(valCls)) {
        concederFixa(valCls, `Classe (${clsObj.nome})`);
      } else {
        const prefCls = opClsIds.find((id) => !fixasMap.has(id)) || opClsIds[0];
        concederFixa(prefCls, `Classe (${clsObj.nome} — Proc.)`);
      }
    }

    // 3. Subclasse (quando determinística pelo conceito)
    const subId = conObj?.subclasse_oficial_id || "";
    const candsSub = conObj?.subclasses_oficiais_candidatas || (subId ? [subId] : []);
    if (candsSub.length === 1 && perCls.subclasses_pericias?.[subId]) {
      perCls.subclasses_pericias[subId].forEach((pid) => concederFixa(pid, `Subclasse (${conObj.subclasse_oficial_nome})`));
    }

    // 4. Divindade (Clérigo / Campeão)
    let temOpcaoDiv = false;
    if (perCls.usa_pericia_divindade && divObj && Array.isArray(divObj.pericia_divina)) {
      const opDivIds = divObj.pericia_divina.filter((id) => Boolean(mapaPer[id]));
      if (opDivIds.length === 1) {
        concederFixa(opDivIds[0], `Divindade (${divObj.nome})`);
      } else if (opDivIds.length > 1) {
        temOpcaoDiv = true;
        const selDivOp = document.getElementById("per-div-opcao");
        _preencherSelectPericiaOpcao(selDivOp, opDivIds, mapaPer, `Procedural (${opDivIds.map((id) => mapaPer[id]?.nome).join(" / ")})`);
        const valDiv = selDivOp?.value || "procedural";
        if (valDiv !== "procedural" && opDivIds.includes(valDiv)) {
          concederFixa(valDiv, `Divindade (${divObj.nome})`);
        } else {
          const prefDiv = opDivIds.find((id) => !fixasMap.has(id)) || opDivIds[0];
          concederFixa(prefDiv, `Divindade (${divObj.nome} — Proc.)`);
        }
      }
    }

    // 5. Talentos Ancestrais (se o jogador já selecionou na Etapa 3)
    let extrasTalento = 0;
    if ((document.getElementById("modo-talentos")?.value || "procedural") === "personalizado") {
      const elTalAnc = document.getElementById("tal-ancestralidade");
      const talAncVal = elTalAnc && !elTalAnc.disabled && !elTalAnc.closest(".oculto") ? elTalAnc.value : "procedural";
      const regTal = TALENTOS_PERICIAS_ANC_UI[talAncVal];
      if (regTal) {
        extrasTalento += regTal.extras;
        regTal.fixas.forEach((pid) => concederFixa(pid, "Talento Ancestral"));
      }
    }

    // 6. Matemática das vagas livres: max(0, base + mod_int) + Herança Perita + Sobreposições + Talentos
    const { intVal, modInt } = _calcularModIntAtualUI();
    const baseCls = Number(perCls.adicionais_base || 0);
    const poolClsInt = perCls.soma_modificador_inteligencia ? Math.max(0, baseCls + modInt) : baseCls;
    const bonusHeranca = herId === "heranca_perita" ? 1 : 0;
    const bonusSobreposicao = sobreposicoes.length;
    const maxPossivelNaoFixas = Math.max(0, catPer.length - fixasMap.size);
    const vagasLivresTotal = Math.min(maxPossivelNaoFixas, poolClsInt + bonusHeranca + bonusSobreposicao + extrasTalento);

    const partesFormula = [`Classe (${baseCls})`];
    if (perCls.soma_modificador_inteligencia) {
      partesFormula.push(`INT ${intVal} (${modInt >= 0 ? `+${modInt}` : modInt})`);
    }
    if (bonusHeranca > 0) partesFormula.push("Herança Perita (+1)");
    if (bonusSobreposicao > 0) partesFormula.push(`Sobreposição (+${bonusSobreposicao})`);
    if (extrasTalento > 0) partesFormula.push(`Talento Ancestral (+${extrasTalento})`);

    return {
      disponivel: true,
      clsObj,
      bioObj,
      mapaPer,
      fixasMap,
      sobreposicoes,
      vagasLivresTotal,
      formulaTxt: partesFormula.join(" + "),
      temOpcaoBio,
      temOpcaoCls,
      temOpcaoDiv,
    };
  }

  function atualizarCatalogoPericiasUI() {
    const catPer = app.opcoes?.catalogo_pericias;
    if (!catPer) return;

    const st = calcularEstadoPericiasUI();
    document.getElementById("card-per-bio-opcao")?.classList.toggle("oculto", !st.temOpcaoBio);
    document.getElementById("card-per-cls-opcao")?.classList.toggle("oculto", !st.temOpcaoCls);
    document.getElementById("card-per-div-opcao")?.classList.toggle("oculto", !st.temOpcaoDiv);

    const infoSaber = document.getElementById("info-per-saber");
    if (infoSaber) {
      if (st.bioObj) {
        infoSaber.textContent = `${st.bioObj.saber_treinado} (Biografia: ${st.bioObj.nome})`;
        infoSaber.classList.add("ativo");
      } else {
        infoSaber.textContent = "Automático: será definido pela Biografia sorteada/escolhida.";
        infoSaber.classList.remove("ativo");
      }
    }

    const elVagas = document.getElementById("per-resumo-vagas");
    const elFormula = document.getElementById("per-detalhe-formula");
    const grid = document.getElementById("grid-pericias-checkboxes");

    if (!st.disponivel) {
      app.perEstado.selecionadas = [];
      if (elVagas) {
        elVagas.textContent = "Selecione uma Classe fixa";
        elVagas.className = "saldo-alerta";
      }
      if (elFormula) elFormula.textContent = "Escolha uma Classe em Criação Inicial para liberar a seleção manual de perícias.";
      if (grid) {
        grid.innerHTML = `<div class="box-tal-auto">Classe Aleatória ativa: as perícias serão calculadas automaticamente conforme a classe sorteada.</div>`;
      }
      app.atualizarResumosEtapasUI?.();
      return;
    }

    app.perEstado.selecionadas = app.perEstado.selecionadas
      .filter((pid) => st.mapaPer[pid] && !st.fixasMap.has(pid))
      .slice(0, st.vagasLivresTotal);

    const qtdSel = app.perEstado.selecionadas.length;
    const cheio = qtdSel >= st.vagasLivresTotal;

    if (elVagas) {
      elVagas.textContent = `${qtdSel} / ${st.vagasLivresTotal} selecionadas`;
      elVagas.className = "saldo-ok";
    }
    if (elFormula) {
      elFormula.textContent = st.formulaTxt;
    }

    const elNotaProg = document.getElementById("per-nota-progressao");
    if (elNotaProg) {
      const nivel = app.obterNivelSelecionadoUI?.() || 1;
      const ehRandNiv = app.ehNivelAleatorioUI?.() || false;
      if (ehRandNiv || nivel > 1) {
        elNotaProg.classList.remove("oculto");
        elNotaProg.textContent = ehRandNiv
          ? "Se o nível sorteado for 2–5, incrementos de perícia adicionais (até Especialista) serão aplicados automaticamente pelo motor."
          : `Nível ${nivel}: os incrementos de perícia de progressão N2–N${nivel} (até Especialista) são aplicados automaticamente pelo motor.`;
      } else {
        elNotaProg.classList.add("oculto");
        elNotaProg.textContent = "";
      }
    }

    if (grid) {
      grid.innerHTML = catPer
        .map((p) => {
          const origemFixa = st.fixasMap.get(p.id);
          if (origemFixa) {
            return (
              `<label class="pericia-check-card fixa" title="${esc(p.descricao)}">` +
              `<input type="checkbox" checked disabled>` +
              `<span class="pericia-check-info">` +
              `<span class="pericia-check-titulo">${esc(p.nome)}<span class="pericia-check-atb">(${esc(p.atributo_sigla)})</span></span>` +
              `<span class="pericia-check-badge fixa">Fixa: ${esc(origemFixa)}</span>` +
              `</span></label>`
            );
          }
          const marcada = app.perEstado.selecionadas.includes(p.id);
          const bloqueada = !marcada && cheio;
          const clsCard = `pericia-check-card${marcada ? " selecionada" : ""}${bloqueada ? " bloqueada" : ""}`;
          return (
            `<label class="${clsCard}" title="${esc(p.descricao)}">` +
            `<input type="checkbox" data-pericia-id="${esc(p.id)}" ${marcada ? "checked" : ""} ${bloqueada ? "disabled" : ""}>` +
            `<span class="pericia-check-info">` +
            `<span class="pericia-check-titulo">${esc(p.nome)}<span class="pericia-check-atb">(${esc(p.atributo_sigla)})</span></span>` +
            (marcada ? `<span class="pericia-check-badge manual">Escolhida</span>` : "") +
            `</span></label>`
          );
        })
        .join("");
    }

    app.atualizarPreRequisitosTalentosPericiaUI?.();
    app.atualizarResumosEtapasUI?.();
  }

  function atualizarVisibilidadePericiasUI() {
    const modo = document.getElementById("modo-pericias")?.value || "procedural";
    document.getElementById("painel-pericias-custom")?.classList.toggle("oculto", modo !== "personalizado");
    atualizarCatalogoPericiasUI();
    app.atualizarPreRequisitosTalentosPericiaUI?.();
    app.atualizarResumosEtapasUI?.();
  }

  function resetarPericiasProcedural() {
    const modoEl = document.getElementById("modo-pericias");
    if (modoEl) modoEl.value = "procedural";
    ["per-bio-opcao", "per-cls-opcao", "per-div-opcao"].forEach((id) => {
      const el = document.getElementById(id);
      if (el) el.value = "procedural";
    });
    app.perEstado.selecionadas = [];
    atualizarVisibilidadePericiasUI();
  }

  function montarPayloadPericiasUI() {
    if (document.getElementById("modo-pericias")?.value !== "personalizado") {
      return { modo: "procedural" };
    }
    const valAtivo = (cardId, selId) => {
      const card = document.getElementById(cardId);
      const sel = document.getElementById(selId);
      if (!sel || card?.classList.contains("oculto")) return "procedural";
      return sel.value || "procedural";
    };
    return {
      modo: "personalizado",
      pericia_biografia_id: valAtivo("card-per-bio-opcao", "per-bio-opcao"),
      pericia_classe_fixa_id: valAtivo("card-per-cls-opcao", "per-cls-opcao"),
      pericia_divindade_id: valAtivo("card-per-div-opcao", "per-div-opcao"),
      pericias_livres: app.perEstado.selecionadas.length ? [...app.perEstado.selecionadas] : "procedural",
    };
  }

  function registrarEventosPericias() {
    document.getElementById("modo-pericias")?.addEventListener("change", atualizarVisibilidadePericiasUI);
    ["per-bio-opcao", "per-cls-opcao", "per-div-opcao"].forEach((id) => {
      document.getElementById(id)?.addEventListener("change", atualizarCatalogoPericiasUI);
    });
    document.getElementById("grid-pericias-checkboxes")?.addEventListener("change", (e) => {
      const chk = e.target.closest('input[type="checkbox"][data-pericia-id]');
      if (!chk) return;
      const pid = chk.dataset.periciaId;
      const st = calcularEstadoPericiasUI();
      if (!st.disponivel || st.fixasMap.has(pid)) return;
      if (chk.checked) {
        if (!app.perEstado.selecionadas.includes(pid) && app.perEstado.selecionadas.length < st.vagasLivresTotal) {
          app.perEstado.selecionadas.push(pid);
        }
      } else {
        app.perEstado.selecionadas = app.perEstado.selecionadas.filter((x) => x !== pid);
      }
      atualizarCatalogoPericiasUI();
    });
    document.getElementById("btn-per-reset-procedural")?.addEventListener("click", () => {
      resetarPericiasProcedural();
      const modoEl = document.getElementById("modo-pericias");
      if (modoEl) modoEl.value = "personalizado";
      atualizarVisibilidadePericiasUI();
    });
  }

  Object.assign(app, {
    calcularEstadoPericiasUI,
    atualizarCatalogoPericiasUI,
    atualizarVisibilidadePericiasUI,
    resetarPericiasProcedural,
    montarPayloadPericiasUI,
    registrarEventosPericias,
  });
})();
