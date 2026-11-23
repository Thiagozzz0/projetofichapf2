(() => {
  "use strict";

  const app = window.PF2EApp;
  const { CLASSES_CONJURADORAS_UI, IDS_TAL_CLASSE, IDS_TAL_GERAIS, normTxt } = app;

  function _preencherSelectTalento(sel, lista, { textoProcedural, preservar = true, disabledTexto = null, verificarOpcao = null } = {}) {
    if (!sel) return;
    const anterior = preservar ? sel.value : "procedural";
    sel.innerHTML = "";

    const optProc = document.createElement("option");
    optProc.value = "procedural";
    optProc.textContent = disabledTexto || textoProcedural || "Procedural (melhor p/ conceito)";
    sel.appendChild(optProc);

    if (disabledTexto) {
      sel.value = "procedural";
      sel.disabled = true;
      return;
    }

    sel.disabled = false;
    (lista || []).forEach((t) => {
      const opt = document.createElement("option");
      opt.value = t.id;
      const reqTxt = t.pre_requisitos ? ` [Req: ${t.pre_requisitos}]` : "";
      const motivoInv = verificarOpcao ? verificarOpcao(t) : null;
      const base = `${t.nome}${reqTxt}`;
      opt.dataset.baseLabel = base;
      if (motivoInv) {
        opt.disabled = true;
        opt.dataset.reqBloqueado = "1";
        opt.textContent = `${base} (${motivoInv})`;
      } else {
        opt.textContent = base;
      }
      if (t.resumo) opt.title = t.resumo;
      sel.appendChild(opt);
    });

    const optValida = Array.from(sel.options).find((o) => o.value === anterior && !o.disabled);
    sel.value = optValida ? anterior : "procedural";
  }

  function _sincronizarExclusaoGrupoTalentos(ids) {
    const ativos = ids
      .map((id) => document.getElementById(id))
      .filter((sel) => sel && !sel.disabled && !sel.closest(".oculto"));
    ativos.forEach((sel, idx) => {
      const usadosOutros = new Set(
        ativos.filter((outro, oIdx) => oIdx !== idx && outro.value !== "procedural").map((o) => o.value)
      );
      Array.from(sel.options).forEach((opt) => {
        if (opt.value === "procedural" || opt.dataset.reqBloqueado === "1") return;
        if (!opt.dataset.baseLabel) opt.dataset.baseLabel = opt.textContent;
        const dup = usadosOutros.has(opt.value);
        opt.disabled = dup;
        opt.textContent = dup ? `${opt.dataset.baseLabel} (já escolhido acima)` : opt.dataset.baseLabel;
      });
      if (sel.value !== "procedural" && usadosOutros.has(sel.value)) sel.value = "procedural";
    });
  }

  function _verificarReqPericiaTalento(t) {
    if ((document.getElementById("modo-pericias")?.value || "procedural") !== "personalizado") {
      return null;
    }
    const stPer = app.calcularEstadoPericiasUI?.();
    if (!stPer || !stPer.disponivel) return null;
    const reqNorm = normTxt(t.pre_requisitos || "");
    if (!reqNorm || reqNorm.includes("pelo menos uma pericia") || reqNorm.includes("recordar conhecimento") || reqNorm.includes("saber")) {
      return null;
    }
    const catPer = app.opcoes?.catalogo_pericias || [];
    const citadas = catPer.filter((p) => reqNorm.includes(normTxt(p.nome)));
    if (!citadas.length) return null;

    const treinadas = new Set([...stPer.fixasMap.keys(), ...(app.perEstado?.selecionadas || [])]);
    const atende = citadas.some((p) => treinadas.has(p.id));
    if (atende) return null;
    return `requer ${citadas.map((p) => p.nome).join(" ou ")} em Perícias`;
  }

  function atualizarPreRequisitosTalentosPericiaUI() {
    const selPer = document.getElementById("tal-pericia-1");
    const cat = app.opcoes?.catalogo_talentos;
    if (!selPer || selPer.disabled || !cat) return;
    const mapaT = Object.fromEntries((cat.pericia_n1 || []).map((t) => [t.id, t]));
    Array.from(selPer.options).forEach((opt) => {
      if (opt.value === "procedural") return;
      const t = mapaT[opt.value];
      if (!t) return;
      if (!opt.dataset.baseLabel) opt.dataset.baseLabel = opt.textContent;
      const motivo = _verificarReqPericiaTalento(t);
      if (motivo) {
        opt.disabled = true;
        opt.dataset.reqBloqueado = "1";
        opt.textContent = `${opt.dataset.baseLabel} (${motivo})`;
      } else {
        opt.disabled = false;
        delete opt.dataset.reqBloqueado;
        opt.textContent = opt.dataset.baseLabel;
      }
    });
    if (selPer.selectedOptions[0]?.disabled) {
      selPer.value = "procedural";
    }
  }

  function sincronizarExclusaoTalentos() {
    _sincronizarExclusaoGrupoTalentos(IDS_TAL_CLASSE);
    _sincronizarExclusaoGrupoTalentos(IDS_TAL_GERAIS);
  }

  function atualizarCatalogoTalentosUI() {
    const cat = app.opcoes?.catalogo_talentos;
    if (!cat) return;

    const ancId = document.getElementById("ancestralidade")?.value || "aleatorio";
    const herId = document.getElementById("heranca")?.value || "aleatorio";
    const bioId = document.getElementById("biografia")?.value || "procedural";
    const clsId = document.getElementById("classe")?.value || "aleatorio";
    const conId = document.getElementById("conceito")?.value || "aleatorio";
    const ancObj = app.opcoes.ancestralidades.find((a) => a.id === ancId);
    const bioObj = app.opcoes.biografias.find((b) => b.id === bioId);
    const clsObj = app.opcoes.classes.find((c) => c.id === clsId);
    const conObj = clsObj ? clsObj.conceitos.find((x) => x.id === conId) : null;

    // 1. Talento de Ancestralidade (1º Nível) — oculto se Ancestralidade estiver Aleatória
    const selAnc = document.getElementById("tal-ancestralidade");
    const badgeAnc = document.getElementById("badge-tal-ancestralidade");
    const notaAnc = document.getElementById("nota-tal-ancestralidade");
    const cardAnc = document.getElementById("card-tal-ancestralidade");
    let slotsVisiveisTotal = 0;
    if (!ancObj || ancId === "aleatorio") {
      _preencherSelectTalento(selAnc, [], { disabledTexto: "Procedural (conforme ancestralidade sorteada)", preservar: false });
      cardAnc?.classList.add("oculto");
    } else {
      cardAnc?.classList.remove("oculto");
      slotsVisiveisTotal += 1;
      const poolMap = new Map();
      (cat.ancestralidade_por_id[ancId] || []).forEach((t) => poolMap.set(t.id, t));
      if (herId === "meio_elfo") {
        (cat.ancestralidade_por_id.elfo || []).forEach((t) => { if (!poolMap.has(t.id)) poolMap.set(t.id, t); });
        (cat.mesticos?.meio_elfo || []).forEach((t) => { if (!poolMap.has(t.id)) poolMap.set(t.id, t); });
      } else if (herId === "meio_orc") {
        (cat.mesticos?.meio_orc || []).forEach((t) => { if (!poolMap.has(t.id)) poolMap.set(t.id, t); });
      }
      _preencherSelectTalento(selAnc, Array.from(poolMap.values()), {
        textoProcedural: "Procedural (melhor p/ conceito)",
        verificarOpcao: (t) => {
          if (t.id === "truque_magico_adaptado" && clsId !== "aleatorio" && !CLASSES_CONJURADORAS_UI.has(clsId)) {
            return "requer conjuração plena";
          }
          if (t.id === "longevidade_ancestral" && ancId !== "elfo") return "requer ancestralidade Elfo";
          return null;
        },
      });
      if (badgeAnc) {
        badgeAnc.className = "badge-tal-liberado";
        badgeAnc.textContent = "1 Slot Liberado";
      }
      if (notaAnc) {
        if (selAnc?.value === "ambicao_natural") {
          notaAnc.textContent = "Ambição Natural selecionada: +1 slot de Talento de Classe (1º Nível) liberado abaixo!";
        } else if (selAnc?.value === "treinamento_geral") {
          notaAnc.textContent = "Treinamento Geral selecionado: +1 slot de Talento Geral (1º Nível) liberado abaixo!";
        } else {
          const extraPool = herId === "meio_elfo" ? " + pool Élfico/Meio-Elfo" : herId === "meio_orc" ? " + pool Meio-Orc" : "";
          notaAnc.textContent = `${poolMap.size} talentos de 1º nível disponíveis para ${ancObj.nome}${extraPool}.`;
        }
      }
    }

    const talAncVal = selAnc?.value || "procedural";
    const ambicaoAtiva = talAncVal === "ambicao_natural";
    const treinamentoGeralAtivo = talAncVal === "treinamento_geral";

    // 2. Talento de Biografia (Automático — sempre visível)
    const infoBio = document.getElementById("info-tal-biografia");
    if (infoBio) {
      if (bioObj) {
        infoBio.textContent = `Automático pela Biografia (${bioObj.nome}): ${bioObj.talento_pericia}`;
        infoBio.classList.add("ativo");
      } else {
        infoBio.textContent = "Automático: será concedido pela Biografia escolhida/sorteada ao gerar a ficha.";
        infoBio.classList.remove("ativo");
      }
    }

    // 3. Talentos de Classe (1º Nível) — exibido apenas se houver ao menos 1 slot selecionável
    const cardCls = document.getElementById("card-tal-classe");
    const badgeCls = document.getElementById("badge-tal-classe");
    const notaCls = document.getElementById("nota-tal-classe");
    const clsCat = cat.classe_por_id?.[clsId];
    const autoClasseIds = new Set();
    const autoClasseNomes = [];

    let temClasseSelecionavel = false;
    if (clsObj && clsId !== "aleatorio" && clsCat) {
      const subId = conObj?.subclasse_oficial_id || "";
      const conjCandidatas = conObj?.subclasses_oficiais_candidatas || (subId ? [subId] : []);
      if (conjCandidatas.length === 1 && clsCat.subclasses_concedido?.[subId]) {
        const autoId = clsCat.subclasses_concedido[subId];
        autoClasseIds.add(autoId);
        const autoObj = clsCat.talentos_n1.find((t) => t.id === autoId);
        if (autoObj) autoClasseNomes.push(autoObj.nome);
      }
      if (clsId === "clerigo" && subId === "sacerdote_enclausurado") {
        autoClasseIds.add("iniciado_no_dominio");
        autoClasseNomes.push("Iniciado no Domínio");
      }
      if (clsId === "mago" && conObj?.tese_arcana_id === "sintonizacao_com_familiar_aprimorada") {
        autoClasseIds.add("familiar");
        autoClasseNomes.push("Familiar");
      }

      const slotsCls = [];
      if (clsCat.tem_slot_n1_base || conObj?.mago_universalista) {
        slotsCls.push({ rotulo: `Classe (${clsObj.nome} 1º Nível)`, apenasMeta: false });
      }
      if (clsId === "barbaro" && subId === "instinto_do_furor") {
        slotsCls.push({ rotulo: "Subclasse (Instinto do Furor)", apenasMeta: false });
      }
      if (clsId === "mago" && conObj?.tese_arcana_id === "experimentacao_metamagica") {
        slotsCls.push({ rotulo: "Tese (Experimentação Metamágica)", apenasMeta: true });
      }
      if (ambicaoAtiva) {
        slotsCls.push({ rotulo: "Ambição Natural (Humano)", apenasMeta: false });
      }

      if (slotsCls.length > 0) {
        temClasseSelecionavel = true;
        slotsVisiveisTotal += slotsCls.length;
        cardCls?.classList.remove("oculto");
        if (badgeCls) {
          badgeCls.className = "badge-tal-liberado";
          badgeCls.textContent = `${slotsCls.length} Slot${slotsCls.length > 1 ? "s" : ""} Liberado${slotsCls.length > 1 ? "s" : ""}`;
        }
        IDS_TAL_CLASSE.forEach((id, idx) => {
          const grp = document.getElementById(`grupo-tal-classe-${idx + 1}`);
          const lbl = document.getElementById(`lbl-tal-classe-${idx + 1}`);
          const sel = document.getElementById(id);
          if (idx < slotsCls.length) {
            grp?.classList.remove("oculto");
            if (lbl) lbl.textContent = `${idx + 1}º Slot — ${slotsCls[idx].rotulo}`;
            const poolC = clsCat.talentos_n1.filter(
              (t) => !autoClasseIds.has(t.id) && (!slotsCls[idx].apenasMeta || t.eh_metamagia)
            );
            _preencherSelectTalento(sel, poolC, { textoProcedural: "Procedural (melhor p/ conceito)" });
          } else {
            grp?.classList.add("oculto");
            _preencherSelectTalento(sel, [], { disabledTexto: "Slot inativo", preservar: false });
          }
        });
        if (notaCls) {
          const origTxt = slotsCls.map((s) => s.rotulo).join(" + ");
          const autoTxt = autoClasseNomes.length ? ` • Automático pela subclasse/tese: ${autoClasseNomes.join(", ")}.` : "";
          notaCls.textContent = `Liberado por: ${origTxt}.${autoTxt}`;
        }
      }
    }
    if (!temClasseSelecionavel) {
      cardCls?.classList.add("oculto");
      IDS_TAL_CLASSE.forEach((id, i) => {
        document.getElementById(`grupo-tal-classe-${i + 1}`)?.classList.toggle("oculto", i > 0);
        _preencherSelectTalento(document.getElementById(id), [], { disabledTexto: "Slot inativo", preservar: false });
      });
    }

    // 4A. Talento de Perícia Extra (1º Nível) — exibido apenas para Ladino
    const subPer = document.getElementById("subcard-tal-pericia");
    const badgePer = document.getElementById("badge-tal-pericia");
    const notaPer = document.getElementById("nota-tal-pericia");
    const selPer = document.getElementById("tal-pericia-1");
    const temPericiaSelecionavel = clsId === "ladino";
    if (temPericiaSelecionavel) {
      slotsVisiveisTotal += 1;
      subPer?.classList.remove("oculto");
      const bioTalNorm = bioObj && !bioObj.talento_pericia.includes(" ou ")
        ? normTxt(bioObj.talento_pericia.split(" para ")[0])
        : "";
      const poolPer = (cat.pericia_n1 || []).filter((t) => !bioTalNorm || normTxt(t.nome) !== bioTalNorm);
      _preencherSelectTalento(selPer, poolPer, {
        textoProcedural: "Procedural (melhor p/ conceito)",
        verificarOpcao: _verificarReqPericiaTalento,
      });
      if (badgePer) { badgePer.className = "badge-tal-liberado"; badgePer.textContent = "1 Slot Liberado (Ladino)"; }
      if (notaPer) notaPer.textContent = "Ladino recebe +1 talento de perícia adicional no 1º nível além do da Biografia.";
    } else {
      subPer?.classList.add("oculto");
      _preencherSelectTalento(selPer, [], { disabledTexto: "Slot inativo", preservar: false });
    }

    // 4B. Talentos Gerais (1º Nível) — exibido apenas quando Herança Versátil / Treinamento Geral estiver ativo
    const subGer = document.getElementById("subcard-tal-geral");
    const badgeGer = document.getElementById("badge-tal-geral");
    const notaGer = document.getElementById("nota-tal-geral");
    const origensGerais = [];
    if (herId === "heranca_versatil") origensGerais.push("Herança Versátil (Humano)");
    if (treinamentoGeralAtivo) origensGerais.push("Treinamento Geral (Humano)");

    const bloqueioEscudoAuto =
      new Set(["guerreiro", "campeao", "druida"]).has(clsId) ||
      (clsId === "clerigo" && conObj?.subclasse_oficial_id === "capelao_da_guerra");

    const temGeralSelecionavel = origensGerais.length > 0;
    if (temGeralSelecionavel) {
      slotsVisiveisTotal += origensGerais.length;
      subGer?.classList.remove("oculto");
      const poolGer = (cat.gerais_n1 || []).filter(
        (t) => !(bloqueioEscudoAuto && t.id === "bloqueio_com_escudo") && !(talAncVal === "cavaleiro_brusco" && t.id === "cavalgar")
      );
      if (badgeGer) {
        badgeGer.className = "badge-tal-liberado";
        badgeGer.textContent = `${origensGerais.length} Slot${origensGerais.length > 1 ? "s" : ""} Liberado${origensGerais.length > 1 ? "s" : ""}`;
      }
      IDS_TAL_GERAIS.forEach((id, idx) => {
        const grp = document.getElementById(`grupo-tal-geral-${idx + 1}`);
        const lbl = document.getElementById(`lbl-tal-geral-${idx + 1}`);
        const sel = document.getElementById(id);
        if (idx < origensGerais.length) {
          grp?.classList.remove("oculto");
          if (lbl) lbl.textContent = `${idx + 1}º Slot — ${origensGerais[idx]}`;
          _preencherSelectTalento(sel, poolGer, { textoProcedural: "Procedural (melhor p/ conceito)" });
        } else {
          grp?.classList.add("oculto");
          _preencherSelectTalento(sel, [], { disabledTexto: "Slot inativo", preservar: false });
        }
      });
      if (notaGer) notaGer.textContent = `Liberado por: ${origensGerais.join(" + ")}.`;
    } else {
      subGer?.classList.add("oculto");
      IDS_TAL_GERAIS.forEach((id, i) => {
        document.getElementById(`grupo-tal-geral-${i + 1}`)?.classList.toggle("oculto", i > 0);
        _preencherSelectTalento(document.getElementById(id), [], { disabledTexto: "Slot inativo", preservar: false });
      });
    }

    document.getElementById("card-tal-demais")?.classList.toggle("oculto", !temPericiaSelecionavel && !temGeralSelecionavel);

    const elCur = document.getElementById("tal-resumo-curadoria");
    if (elCur) {
      elCur.textContent = slotsVisiveisTotal > 0
        ? `Curadoria PF2E (1º Nível): ${slotsVisiveisTotal} slot${slotsVisiveisTotal > 1 ? "s" : ""} selecionável${slotsVisiveisTotal > 1 ? "is" : ""} disponível${slotsVisiveisTotal > 1 ? "is" : ""} para esta ficha.`
        : "Escolha uma Ancestralidade ou Classe fixa em Criação Inicial para liberar seletores manuais de talentos.";
    }

    sincronizarExclusaoTalentos();
    app.atualizarCatalogoPericiasUI?.();
    app.atualizarCatalogoMagiasUI?.();
    app.atualizarCatalogoEquipamentosUI?.();
    app.atualizarPerfilUI?.();
    app.atualizarResumosEtapasUI?.();
  }

  function atualizarVisibilidadeTalentosUI() {
    const modo = document.getElementById("modo-talentos")?.value || "procedural";
    document.getElementById("painel-talentos-custom")?.classList.toggle("oculto", modo !== "personalizado");
    app.atualizarCatalogoPericiasUI?.();
    app.atualizarCatalogoEquipamentosUI?.();
    app.atualizarPerfilUI?.();
    app.atualizarResumosEtapasUI?.();
  }

  function resetarTalentosProcedural() {
    const modoEl = document.getElementById("modo-talentos");
    if (modoEl) modoEl.value = "procedural";
    ["tal-ancestralidade", ...IDS_TAL_CLASSE, "tal-pericia-1", ...IDS_TAL_GERAIS].forEach((id) => {
      const el = document.getElementById(id);
      if (el) el.value = "procedural";
    });
    atualizarCatalogoTalentosUI();
    atualizarVisibilidadeTalentosUI();
  }

  function montarPayloadTalentosUI() {
    if (document.getElementById("modo-talentos")?.value !== "personalizado") {
      return { modo: "procedural" };
    }
    const selAtivos = (ids) =>
      ids
        .map((id) => document.getElementById(id))
        .filter((el) => el && !el.disabled && !el.closest(".oculto"))
        .map((el) => el.value || "procedural");
    const clsVals = selAtivos(IDS_TAL_CLASSE);
    const perEl = document.getElementById("tal-pericia-1");
    const perVals = perEl && !perEl.disabled ? [perEl.value || "procedural"] : "procedural";
    const gerVals = selAtivos(IDS_TAL_GERAIS);
    return {
      modo: "personalizado",
      ancestralidade_id: document.getElementById("tal-ancestralidade")?.disabled
        ? "procedural"
        : document.getElementById("tal-ancestralidade")?.value || "procedural",
      classe_ids: clsVals.length ? clsVals : "procedural",
      pericia_ids: perVals,
      gerais_ids: gerVals.length ? gerVals : "procedural",
    };
  }

  function registrarEventosTalentos() {
    document.getElementById("modo-talentos")?.addEventListener("change", atualizarVisibilidadeTalentosUI);
    document.getElementById("tal-ancestralidade")?.addEventListener("change", atualizarCatalogoTalentosUI);
    [...IDS_TAL_CLASSE, ...IDS_TAL_GERAIS].forEach((id) => {
      document.getElementById(id)?.addEventListener("change", () => {
        sincronizarExclusaoTalentos();
        app.atualizarCatalogoEquipamentosUI?.();
        app.atualizarPerfilUI?.();
        app.atualizarResumosEtapasUI?.();
      });
    });
    document.getElementById("tal-pericia-1")?.addEventListener("change", () => app.atualizarResumosEtapasUI?.());
    document.getElementById("btn-tal-reset-procedural")?.addEventListener("click", () => {
      resetarTalentosProcedural();
      const modoEl = document.getElementById("modo-talentos");
      if (modoEl) modoEl.value = "personalizado";
      atualizarVisibilidadeTalentosUI();
    });
  }

  Object.assign(app, {
    sincronizarExclusaoTalentos,
    atualizarPreRequisitosTalentosPericiaUI,
    atualizarCatalogoTalentosUI,
    atualizarVisibilidadeTalentosUI,
    resetarTalentosProcedural,
    montarPayloadTalentosUI,
    registrarEventosTalentos,
  });
})();
