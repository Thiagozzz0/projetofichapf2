(() => {
  "use strict";

  const app = window.PF2EApp;
  const { esc } = window.PF2EFichaUI;
  const { CLASSES_CONJURADORAS_UI, IDS_TAL_CLASSE, IDS_TAL_GERAIS, normTxt, criarOptgroup, fmtPrecoEq } = app;

  function _custoVariadoSelectPc() {
    const varId = document.getElementById("eq-variado-select")?.value || "procedural";
    if (!app.mapaEq.variados[varId]) return 0;
    const qtd = Math.max(1, parseInt(document.getElementById("eq-variado-qtd")?.value || "1", 10) || 1);
    return app.mapaEq.variados[varId].preco_pc * qtd;
  }

  function gastoManualEquipamentosPc() {
    let gasto = 0;
    const armId = document.getElementById("eq-armadura")?.value || "procedural";
    if (app.mapaEq.armaduras[armId]) {
      gasto += app.mapaEq.armaduras[armId].preco_pc;
    }
    const escId = document.getElementById("eq-escudo")?.value || "procedural";
    if (app.mapaEq.escudos[escId]) {
      gasto += app.mapaEq.escudos[escId].preco_pc;
    }
    const ccId = document.getElementById("eq-arma-cc-select")?.value || "procedural";
    if (app.mapaEq.armas_cc[ccId]) {
      gasto += app.mapaEq.armas_cc[ccId].preco_pc;
    }
    app.eqEstado.armas_cc.forEach((w) => {
      gasto += w.preco_pc;
    });
    const distId = document.getElementById("eq-arma-dist-select")?.value || "procedural";
    if (app.mapaEq.armas_dist[distId]) {
      gasto += app.mapaEq.armas_dist[distId].preco_pc;
    }
    app.eqEstado.armas_dist.forEach((w) => {
      gasto += w.preco_pc;
    });
    gasto += _custoVariadoSelectPc();
    app.eqEstado.variados.forEach((it) => {
      gasto += it.preco_pc * it.quantidade;
    });
    return gasto;
  }

  function _renderListaEquipamentos(ulId, lista, tipoChave) {
    const ul = document.getElementById(ulId);
    if (!ul) return;
    if (!lista.length) {
      ul.innerHTML = "";
      return;
    }
    ul.innerHTML = lista
      .map((item, idx) => {
        const qtd = item.quantidade ? `${item.quantidade}× ` : "";
        const custo = item.preco_pc * (item.quantidade || 1);
        return (
          `<li class="item-eq-chip">` +
          `<span>${esc(qtd)}${esc(item.nome)} (${esc(fmtPrecoEq(custo))})</span>` +
          `<button type="button" class="btn-rem-eq" data-eq-rem="${tipoChave}" data-idx="${idx}" title="Remover e estornar">×</button>` +
          `</li>`
        );
      })
      .join("");
  }

  function _sincronizarLimitesCompraUI(saldoPc) {
    const armAtual = app.mapaEq.armaduras[document.getElementById("eq-armadura")?.value]?.preco_pc || 0;
    const escAtual = app.mapaEq.escudos[document.getElementById("eq-escudo")?.value]?.preco_pc || 0;
    const ccAtual = app.mapaEq.armas_cc[document.getElementById("eq-arma-cc-select")?.value]?.preco_pc || 0;
    const distAtual = app.mapaEq.armas_dist[document.getElementById("eq-arma-dist-select")?.value]?.preco_pc || 0;
    const varAtual = _custoVariadoSelectPc();

    const atualizarSelectSaldo = (selId, mapa, saldoPermitido, qtdMult = 1) => {
      const sel = document.getElementById(selId);
      if (!sel) return;
      Array.from(sel.options).forEach((opt) => {
        const obj = mapa[opt.value];
        if (!obj) return;
        if (!opt.dataset.baseLabel) opt.dataset.baseLabel = opt.textContent;
        const semSaldo = obj.preco_pc * qtdMult > saldoPermitido;
        opt.disabled = semSaldo;
        opt.textContent = semSaldo ? `${opt.dataset.baseLabel} (saldo insuf.)` : opt.dataset.baseLabel;
      });
    };

    atualizarSelectSaldo("eq-armadura", app.mapaEq.armaduras, saldoPc + armAtual);
    atualizarSelectSaldo("eq-escudo", app.mapaEq.escudos, saldoPc + escAtual);
    atualizarSelectSaldo("eq-arma-cc-select", app.mapaEq.armas_cc, saldoPc + ccAtual);
    atualizarSelectSaldo("eq-arma-dist-select", app.mapaEq.armas_dist, saldoPc + distAtual);
    const qtdVar = Math.max(1, parseInt(document.getElementById("eq-variado-qtd")?.value || "1", 10) || 1);
    atualizarSelectSaldo("eq-variado-select", app.mapaEq.variados, saldoPc + varAtual, qtdVar);

    const setAddDisabled = (btnId, selId, mapa) => {
      const btn = document.getElementById(btnId);
      const val = document.getElementById(selId)?.value;
      if (btn) btn.disabled = !mapa[val];
    };
    setAddDisabled("btn-add-arma-cc", "eq-arma-cc-select", app.mapaEq.armas_cc);
    setAddDisabled("btn-add-arma-dist", "eq-arma-dist-select", app.mapaEq.armas_dist);
    setAddDisabled("btn-add-variado", "eq-variado-select", app.mapaEq.variados);
  }

  function _renderPreviewItemEq(elId, titulo, pills, texto, conteudo = []) {
    const box = document.getElementById(elId);
    if (!box) return;
    if (!titulo) {
      box.innerHTML = "";
      box.classList.add("oculto");
      return;
    }
    const pillsHtml = pills
      .filter(Boolean)
      .map((p) => `<span class="desc-preview-pill">${esc(p)}</span>`)
      .join("");
    const conteudoHtml = conteudo.length
      ? `<div class="desc-preview-conteudo"><strong>Conteúdo:</strong> ${esc(conteudo.join(", "))}</div>`
      : "";
    const textoHtml = texto ? `<div class="desc-preview-texto">${esc(texto)}</div>` : "";

    box.innerHTML =
      `<div class="desc-preview-topo"><span class="desc-preview-titulo">${esc(titulo)}</span></div>` +
      (pillsHtml ? `<div class="desc-preview-pills">${pillsHtml}</div>` : "") +
      conteudoHtml +
      textoHtml;
    box.classList.remove("oculto");
  }

  function atualizarDescricoesEquipamentosUI() {
    // 1. Armadura
    const armId = document.getElementById("eq-armadura")?.value || "procedural";
    const arm = app.mapaEq.armaduras[armId];
    if (arm && !document.getElementById("card-eq-armadura")?.classList.contains("oculto")) {
      const pillsArm = [
        arm.categoria,
        `+${arm.bonus_ca} CA`,
        arm.limite_destreza !== null ? `Lim DES +${arm.limite_destreza}` : "Sem Limite DES",
        arm.penalidade_testes ? `Pen. Testes ${arm.penalidade_testes}` : null,
        arm.penalidade_velocidade_m < 0 ? `Vel. ${String(arm.penalidade_velocidade_m).replace(".", ",")}m` : null,
        arm.forca_minima ? `FOR mín. ${arm.forca_minima}` : null,
        `Vol. ${arm.volume}`,
        arm.material ? `Material: ${arm.material}` : null,
        ...(arm.tracos || []),
      ];
      _renderPreviewItemEq("desc-eq-armadura", arm.nome, pillsArm, arm.descricao);
    } else {
      _renderPreviewItemEq("desc-eq-armadura", null, [], "");
    }

    // 2. Escudo
    const escId = document.getElementById("eq-escudo")?.value || "procedural";
    const escudo = app.mapaEq.escudos[escId];
    if (escudo) {
      const pillsEsc = [
        `+${escudo.bonus_ca} CA (erguido)`,
        escudo.bonus_ca_cobertura ? `Cobertura +${escudo.bonus_ca_cobertura} CA` : null,
        `Dureza ${escudo.dureza}`,
        `PV ${escudo.pv} (LQ ${escudo.limiar_quebra})`,
        escudo.penalidade_velocidade_m < 0 ? `Vel. ${String(escudo.penalidade_velocidade_m).replace(".", ",")}m` : null,
        `Vol. ${escudo.volume}`,
        escudo.permite_mao_livre ? "Permite mão livre" : null,
      ];
      _renderPreviewItemEq("desc-eq-escudo", escudo.nome, pillsEsc, escudo.descricao);
    } else {
      _renderPreviewItemEq("desc-eq-escudo", null, [], "");
    }

    // 3 e 4. Armas (Corporais e à Distância)
    const renderArmaPreview = (selId, boxId, mapa) => {
      const wid = document.getElementById(selId)?.value || "procedural";
      const w = mapa[wid];
      if (!w) {
        _renderPreviewItemEq(boxId, null, [], "");
        return;
      }
      const pillsW = [
        w.categoria,
        w.grupo ? `Grupo: ${w.grupo}` : null,
        `Dano ${w.dano}`,
        `${w.maos} Mão(s)`,
        w.distancia_m ? `Alcance ${w.distancia_m}m` : null,
        w.recarga ? `Recarga ${w.recarga}` : null,
        w.municao ? `Munição: ${w.municao}` : null,
        `Vol. ${w.volume}`,
        ...(w.tracos || []),
      ];
      _renderPreviewItemEq(boxId, w.nome, pillsW, w.descricao);
    };
    renderArmaPreview("eq-arma-cc-select", "desc-eq-arma-cc", app.mapaEq.armas_cc);
    renderArmaPreview("eq-arma-dist-select", "desc-eq-arma-dist", app.mapaEq.armas_dist);

    // 5. Equipamento Variado
    const varId = document.getElementById("eq-variado-select")?.value || "procedural";
    const itemVar = app.mapaEq.variados[varId];
    if (itemVar) {
      const pillsV = [
        itemVar.subcategoria,
        fmtPrecoEq(itemVar.preco_pc),
        `Vol. ${itemVar.volume}`,
        itemVar.maos ? `${itemVar.maos} Mão(s)` : null,
        itemVar.bonus_item ? `Bônus: ${itemVar.bonus_item}` : null,
      ];
      _renderPreviewItemEq("desc-eq-variado", itemVar.nome, pillsV, itemVar.descricao, itemVar.conteudo || []);
    } else {
      _renderPreviewItemEq("desc-eq-variado", null, [], "");
    }
  }

  function atualizarOrcamentoEquipamentosUI() {
    const cat = app.opcoes?.catalogo_equipamentos;
    if (!cat) return;
    const orcPc = Number(cat.orcamento_inicial_pc || 1500);
    const gastoPc = gastoManualEquipamentosPc();
    const saldoPc = orcPc - gastoPc;

    const elGasto = document.getElementById("eq-resumo-gasto");
    const elSaldo = document.getElementById("eq-resumo-saldo");
    if (elGasto) elGasto.textContent = fmtPrecoEq(gastoPc);
    if (elSaldo) {
      elSaldo.textContent = saldoPc >= 0 ? fmtPrecoEq(saldoPc) : `Excedido em ${fmtPrecoEq(Math.abs(saldoPc))}`;
      elSaldo.className = saldoPc <= 0 ? "saldo-alerta" : "saldo-ok";
    }

    _renderListaEquipamentos("lista-eq-armas-cc", app.eqEstado.armas_cc, "cc");
    _renderListaEquipamentos("lista-eq-armas-dist", app.eqEstado.armas_dist, "dist");
    _renderListaEquipamentos("lista-eq-variados", app.eqEstado.variados, "var");
    _sincronizarLimitesCompraUI(Math.max(0, saldoPc));
    atualizarDescricoesEquipamentosUI();
    app.atualizarResumosEtapasUI?.();
  }

  function atualizarVisibilidadeEquipamentosUI() {
    const modo = document.getElementById("modo-equipamentos")?.value || "procedural";
    const painel = document.getElementById("painel-equipamentos-custom");
    if (painel) painel.classList.toggle("oculto", modo !== "personalizado");
    atualizarOrcamentoEquipamentosUI();
    app.atualizarResumosEtapasUI?.();
  }

  function resetarEquipamentosProcedural() {
    const setVal = (id, v) => {
      const el = document.getElementById(id);
      if (el) el.value = v;
    };
    setVal("modo-equipamentos", "procedural");
    setVal("eq-armadura", "procedural");
    setVal("eq-escudo", "procedural");
    setVal("eq-arma-cc-select", "procedural");
    setVal("eq-arma-dist-select", "procedural");
    setVal("eq-variado-select", "procedural");
    setVal("eq-variado-qtd", "1");
    setVal("eq-filtro-busca", "");
    app.eqEstado.armas_cc = [];
    app.eqEstado.armas_dist = [];
    app.eqEstado.variados = [];
    const notaHib = document.getElementById("eq-nota-hibrida");
    if (notaHib) {
      notaHib.textContent = 'Categorias deixadas em "Procedural" usarão automaticamente o saldo restante ao gerar a ficha.';
    }
    atualizarVisibilidadeEquipamentosUI();
  }

  function _calcularProficienciasEquipamentosUI() {
    const cat = app.opcoes?.catalogo_equipamentos;
    const clsId = document.getElementById("classe")?.value || "aleatorio";
    const conId = document.getElementById("conceito")?.value || "aleatorio";
    const divId = document.getElementById("divindade")?.value || "";
    const clsObj = app.opcoes?.classes?.find((c) => c.id === clsId) || null;
    const conObj = clsObj ? clsObj.conceitos.find((x) => x.id === conId) : null;
    const divObj = (app.opcoes?.divindades || []).find((d) => d.id === divId) || null;

    if (!clsObj || clsId === "aleatorio" || !clsObj.proficiencias_equipamento) {
      return { filtrando: false, clsId, clsNome: null };
    }

    const base = clsObj.proficiencias_equipamento;
    const armaduras = {
      sem_armadura: Boolean(base.armaduras?.sem_armadura),
      leve: Boolean(base.armaduras?.leve),
      media: Boolean(base.armaduras?.media),
      pesada: Boolean(base.armaduras?.pesada),
    };
    const armas = {
      simples: Boolean(base.armas?.simples),
      marcial: Boolean(base.armas?.marcial),
      avancada: Boolean(base.armas?.avancada),
      especificas: new Set(base.armas?.especificas_norm || []),
      especificasIds: new Set(),
      especificasNomes: [...(base.armas?.especificas_nomes || [])],
      armasAncestrais: new Set(),
      tracoAncestral: null,
      armamentoNaoConvencional: false,
      armasTracoMonge: false,
    };

    const subId = conObj?.subclasse_oficial_id || "";
    let notaArmaduraExtra = "";
    if (clsId === "clerigo") {
      if (subId === "capelao_da_guerra") {
        armaduras.leve = true;
        armaduras.media = true;
      } else if (conId === "aleatorio") {
        armaduras.leve = true;
        armaduras.media = true;
        notaArmaduraExtra = "Armaduras leves/médias liberadas caso sorteie Capelão da Guerra.";
      }
      if (divObj && divObj.arma_favorecida_id && divObj.arma_favorecida_id !== "punho") {
        armas.especificas.add(normTxt(divObj.arma_favorecida_nome));
        armas.especificasIds.add(divObj.arma_favorecida_id);
        if (!armas.especificasNomes.includes(divObj.arma_favorecida_nome)) {
          armas.especificasNomes.push(`${divObj.arma_favorecida_nome} (${divObj.nome})`);
        }
      }
    } else if (clsId === "ladino" && (subId === "rufiao" || conId === "aleatorio")) {
      armaduras.media = true;
      if (conId === "aleatorio") {
        notaArmaduraExtra = "Armaduras médias liberadas caso sorteie o esquema Rufião.";
      }
    }

    if ((document.getElementById("modo-talentos")?.value || "procedural") === "personalizado") {
      const selAtivoVal = (id) => {
        const el = document.getElementById(id);
        return el && !el.disabled && !el.closest(".oculto") ? el.value : "procedural";
      };
      const talAnc = selAtivoVal("tal-ancestralidade");
      const famMap = cat?.familiaridade_armas_ancestral || {};
      if (famMap[talAnc]) {
        (famMap[talAnc].armas || []).forEach((w) => armas.armasAncestrais.add(normTxt(w)));
        armas.tracoAncestral = famMap[talAnc].traco || null;
      }
      if (talAnc === "armamento_nao_convencional") {
        armas.armamentoNaoConvencional = true;
      }

      const talsCls = IDS_TAL_CLASSE.map(selAtivoVal);
      if (clsId === "monge" && talsCls.includes("arsenal_monastico")) {
        armas.armasTracoMonge = true;
      }

      const talsGer = IDS_TAL_GERAIS.map(selAtivoVal);
      if (talsGer.includes("proficiencia_com_armaduras")) {
        if (!armaduras.leve) armaduras.leve = true;
        else if (!armaduras.media) armaduras.media = true;
        else if (!armaduras.pesada) armaduras.pesada = true;
      }
      if (talsGer.includes("proficiencia_com_armas")) {
        if (!armas.simples) armas.simples = true;
        else if (!armas.marcial) armas.marcial = true;
        else if (!armas.avancada) armas.avancada = true;
      }
    }

    return {
      filtrando: true,
      clsId,
      clsNome: clsObj.nome,
      divObj,
      armaduras,
      armas,
      restricaoNaoMetal: Boolean(base.restricao_nao_metal),
      ferramentasRecomendadas: new Set(base.ferramentas_recomendadas || []),
      notaArmaduraExtra,
    };
  }

  function _armaPermitidaParaBuild(w, profs) {
    if (!profs.filtrando) return true;
    const catNorm = normTxt(w.categoria);
    const nomeNorm = normTxt(w.nome);
    const tracosNorm = (w.tracos || []).map(normTxt);
    const a = profs.armas;

    if (a.armasTracoMonge && tracosNorm.includes("monge") && (catNorm.includes("simples") || catNorm.includes("marcial"))) {
      return true;
    }
    if (a.especificas.has(nomeNorm) || a.especificasIds.has(w.id)) {
      return true;
    }
    if (a.tracoAncestral && tracosNorm.includes(a.tracoAncestral)) {
      if (catNorm.includes("marcial")) return a.simples;
      if (catNorm.includes("avancada")) return a.marcial;
      return a.simples;
    }
    if (a.armamentoNaoConvencional && normTxt(w.raridade) === "incomum") {
      if (catNorm.includes("simples") || catNorm.includes("marcial")) return a.marcial || a.simples;
      if (catNorm.includes("avancada")) return a.marcial || a.avancada;
    }
    if (catNorm.includes("simples") && a.simples) return true;
    if (catNorm.includes("marcial") && a.marcial) return true;
    if (catNorm.includes("avancada") && a.avancada) return true;
    if (a.armasAncestrais.has(nomeNorm)) return true;
    return false;
  }

  function _itemVariadoPermitidoParaBuild(it, profs) {
    if (!profs.filtrando) return true;
    if (it.id === "azevinho_e_visco") return profs.clsId === "druida";
    if (it.id === "ferramentas_de_alquimista") return profs.clsId === "alquimista";
    if (it.id === "bolsa_de_componentes_materiais") return CLASSES_CONJURADORAS_UI.has(profs.clsId);
    if (it.id === "simbolo_religioso_madeira" || it.id === "simbolo_religioso_prata") {
      return profs.clsId === "clerigo" || profs.clsId === "campeao" || Boolean(profs.divObj);
    }
    return true;
  }

  function _itemEqCorrespondeBusca(item, termo) {
    if (!termo) return true;
    const campos = [
      item.nome,
      item.categoria,
      item.subcategoria,
      item.grupo,
      item.material,
      ...(item.tracos || []),
      item.descricao,
    ]
      .filter(Boolean)
      .join(" ");
    return normTxt(campos).includes(termo);
  }

  function atualizarCatalogoEquipamentosUI() {
    const cat = app.opcoes?.catalogo_equipamentos;
    if (!cat) return;

    const termoBusca = normTxt(document.getElementById("eq-filtro-busca")?.value || "");
    document.getElementById("btn-eq-limpar-busca")?.classList.toggle("oculto", !termoBusca);
    let totalEncontrados = 0;

    const profs = _calcularProficienciasEquipamentosUI();
    app.mapaEq.armaduras = {};
    app.mapaEq.escudos = {};
    app.mapaEq.armas_cc = {};
    app.mapaEq.armas_dist = {};
    app.mapaEq.variados = {};

    // 1. Armaduras — oculta o card inteiro se a classe não usa armaduras (ex.: Mago, Feiticeiro, Monge)
    const cardArm = document.getElementById("card-eq-armadura");
    const selArm = document.getElementById("eq-armadura");
    const notaArm = document.getElementById("nota-eq-armadura");
    const usaAlgumaArmadura =
      !profs.filtrando || profs.armaduras.leve || profs.armaduras.media || profs.armaduras.pesada;

    if (!usaAlgumaArmadura) {
      cardArm?.classList.add("oculto");
      if (selArm) {
        selArm.innerHTML = `<option value="procedural">Sem armadura</option>`;
        selArm.value = "procedural";
      }
      if (notaArm) notaArm.textContent = "";
    } else {
      cardArm?.classList.remove("oculto");
      if (selArm) {
        const antArm = selArm.value || "procedural";
        selArm.innerHTML = `<option value="procedural">Procedural (recomendada pelo conceito)</option><option value="nenhuma">Nenhuma armadura (0 pp)</option>`;
        const gruposArm = [
          ["Sem Armadura", true],
          ["Armadura Leve", !profs.filtrando || profs.armaduras.leve],
          ["Armadura Média", !profs.filtrando || profs.armaduras.media],
          ["Armadura Pesada", !profs.filtrando || profs.armaduras.pesada],
        ];
        gruposArm.forEach(([grupo, permitido]) => {
          if (!permitido) return;
          const lista = (cat.armaduras || []).filter((a) => {
            if (a.categoria !== grupo) return false;
            if (profs.restricaoNaoMetal && normTxt(a.material) === "metal") return false;
            return true;
          });
          lista.forEach((a) => {
            app.mapaEq.armaduras[a.id] = a;
            if (_itemEqCorrespondeBusca(a, termoBusca)) totalEncontrados += 1;
          });
          const visiveis = lista.filter((a) => _itemEqCorrespondeBusca(a, termoBusca) || a.id === antArm);
          if (!visiveis.length) return;
          const og = criarOptgroup(selArm, grupo);
          visiveis.forEach((a) => {
            const opt = document.createElement("option");
            opt.value = a.id;
            const lim = a.limite_destreza !== null ? `Lim DES +${a.limite_destreza}` : "Sem Lim DES";
            opt.textContent = `${a.nome} (+${a.bonus_ca} CA, ${lim}) — ${fmtPrecoEq(a.preco_pc)}`;
            og.appendChild(opt);
          });
        });
        selArm.value = antArm === "procedural" || antArm === "nenhuma" || app.mapaEq.armaduras[antArm] ? antArm : "procedural";
      }
      if (notaArm) {
        const partes = [];
        if (profs.restricaoNaoMetal) partes.push("Anátema de Druida: armaduras de metal ocultadas.");
        if (profs.notaArmaduraExtra) partes.push(profs.notaArmaduraExtra);
        notaArm.textContent = partes.join(" ");
      }
    }

    // 2. Escudos (Druida não usa escudos de metal)
    const selEsc = document.getElementById("eq-escudo");
    const notaEsc = document.getElementById("nota-eq-escudo");
    if (selEsc) {
      const antEsc = selEsc.value || "procedural";
      selEsc.innerHTML = `<option value="procedural">Procedural (conforme conceito)</option><option value="nenhum">Nenhum escudo (0 pp)</option>`;
      (cat.escudos || [])
        .filter((s) => !(profs.restricaoNaoMetal && s.eh_metal))
        .forEach((s) => {
          app.mapaEq.escudos[s.id] = s;
          const bate = _itemEqCorrespondeBusca(s, termoBusca);
          if (bate) totalEncontrados += 1;
          if (!bate && s.id !== antEsc) return;
          const opt = document.createElement("option");
          opt.value = s.id;
          opt.textContent = `${s.nome} (+${s.bonus_ca} CA, Dureza ${s.dureza}, PV ${s.pv}) — ${fmtPrecoEq(s.preco_pc)}`;
          selEsc.appendChild(opt);
        });
      selEsc.value = antEsc === "procedural" || antEsc === "nenhum" || app.mapaEq.escudos[antEsc] ? antEsc : "procedural";
    }
    if (notaEsc) {
      notaEsc.textContent = profs.restricaoNaoMetal ? "Anátema de Druida: apenas escudos sem metal." : "";
    }

    // 3 e 4. Armas Corporais e à Distância filtradas pelas proficiências da build
    const popularArmasFiltradas = (cardId, selId, notaId, listaBruta, mapaDestino, estadoChave, labelTipo) => {
      const card = document.getElementById(cardId);
      const sel = document.getElementById(selId);
      const nota = document.getElementById(notaId);
      const permitidas = (listaBruta || []).filter((w) => _armaPermitidaParaBuild(w, profs));

      const idsPermitidos = new Set(permitidas.map((w) => w.id));
      app.eqEstado[estadoChave] = app.eqEstado[estadoChave].filter((w) => idsPermitidos.has(w.id));

      if (!permitidas.length) {
        card?.classList.add("oculto");
        if (sel) {
          sel.innerHTML = `<option value="procedural">Nenhuma disponível</option>`;
          sel.value = "procedural";
        }
        if (nota) nota.textContent = "";
        return 0;
      }

      card?.classList.remove("oculto");
      if (sel) {
        const antVal = sel.value || "procedural";
        sel.innerHTML =
          `<option value="procedural">Procedural (escolhidas pelo conceito)</option>` +
          `<option value="nenhuma">Nenhuma ${labelTipo} (ou usar lista abaixo)</option>`;
        [
          ["Arma Simples", "Armas Simples"],
          ["Arma Marcial", "Armas Marciais"],
          ["Arma Avançada", "Armas Avançadas"],
        ].forEach(([catNome, rotulo]) => {
          const itens = permitidas.filter((w) => w.categoria === catNome);
          itens.forEach((w) => {
            mapaDestino[w.id] = w;
            if (_itemEqCorrespondeBusca(w, termoBusca)) totalEncontrados += 1;
          });
          const visiveis = itens.filter((w) => _itemEqCorrespondeBusca(w, termoBusca) || w.id === antVal);
          if (!visiveis.length) return;
          const og = criarOptgroup(sel, rotulo);
          visiveis.forEach((w) => {
            const opt = document.createElement("option");
            opt.value = w.id;
            const alc = w.distancia_m ? ` • Alc ${w.distancia_m}m` : "";
            opt.textContent = `${w.nome} (${w.dano}, ${w.maos}M${alc}) — ${fmtPrecoEq(w.preco_pc)}`;
            og.appendChild(opt);
          });
        });
        sel.value = antVal === "procedural" || antVal === "nenhuma" || mapaDestino[antVal] ? antVal : "procedural";
      }
      if (nota) {
        nota.textContent = profs.filtrando
          ? `${permitidas.length} opç${permitidas.length === 1 ? "ão" : "ões"} compatíve${permitidas.length === 1 ? "l" : "is"} com ${profs.clsNome}.`
          : "";
      }
      return permitidas.length;
    };

    popularArmasFiltradas(
      "card-eq-arma-cc",
      "eq-arma-cc-select",
      "nota-eq-arma-cc",
      cat.armas_corpo_a_corpo,
      app.mapaEq.armas_cc,
      "armas_cc",
      "arma corporal"
    );
    popularArmasFiltradas(
      "card-eq-arma-dist",
      "eq-arma-dist-select",
      "nota-eq-arma-dist",
      cat.armas_distancia,
      app.mapaEq.armas_dist,
      "armas_dist",
      "arma à distância"
    );

    // 5. Equipamentos Variados
    const selVar = document.getElementById("eq-variado-select");
    const variadosPermitidos = (cat.equipamentos_variados || []).filter((it) => _itemVariadoPermitidoParaBuild(it, profs));
    const idsVarPerm = new Set(variadosPermitidos.map((it) => it.id));
    app.eqEstado.variados = app.eqEstado.variados.filter((it) => idsVarPerm.has(it.id));

    if (selVar) {
      const antVar = selVar.value || "procedural";
      selVar.innerHTML =
        `<option value="procedural">Procedural (itens básicos de viagem + ferramentas da classe)</option>` +
        `<option value="nenhum">Nenhum item variado (ou usar lista abaixo)</option>`;

      variadosPermitidos.forEach((it) => {
        app.mapaEq.variados[it.id] = it;
        if (_itemEqCorrespondeBusca(it, termoBusca)) totalEncontrados += 1;
      });

      const addItemOpt = (og, it) => {
        const opt = document.createElement("option");
        opt.value = it.id;
        const pac = it.quantidade_pacote > 1 && !it.nome.includes(`(${it.quantidade_pacote})`) ? ` (${it.quantidade_pacote} un.)` : "";
        opt.textContent = `${it.nome}${pac} — ${fmtPrecoEq(it.preco_pc)}`;
        og.appendChild(opt);
      };

      const usadosRec = new Set();
      if (profs.filtrando && profs.ferramentasRecomendadas.size > 0) {
        const recItens = variadosPermitidos.filter(
          (it) => profs.ferramentasRecomendadas.has(it.id) && (_itemEqCorrespondeBusca(it, termoBusca) || it.id === antVar)
        );
        if (recItens.length) {
          const ogRec = criarOptgroup(selVar, `Essenciais de ${profs.clsNome}`);
          recItens.forEach((it) => {
            usadosRec.add(it.id);
            addItemOpt(ogRec, it);
          });
        }
      }

      ["Equipamentos de Aventura", "Equipamentos Incomuns", "Munições"].forEach((subcat) => {
        const itens = variadosPermitidos.filter(
          (it) => it.subcategoria === subcat && !usadosRec.has(it.id) && (_itemEqCorrespondeBusca(it, termoBusca) || it.id === antVar)
        );
        if (!itens.length) return;
        const og = criarOptgroup(selVar, subcat);
        itens.forEach((it) => addItemOpt(og, it));
      });
      selVar.value = antVar === "procedural" || antVar === "nenhum" || app.mapaEq.variados[antVar] ? antVar : "procedural";
    }

    const elBuscaStatus = document.getElementById("eq-busca-status");
    if (elBuscaStatus) {
      elBuscaStatus.classList.toggle("oculto", !termoBusca);
      elBuscaStatus.textContent = termoBusca
        ? totalEncontrados
          ? `${totalEncontrados} equipamento(s) encontrado(s) nos seletores abaixo.`
          : "Nenhum equipamento compatível encontrado para o filtro informado."
        : "";
    }

    const elCurEq = document.getElementById("eq-nota-curadoria");
    if (elCurEq) {
      if (!profs.filtrando) {
        elCurEq.textContent = "Classe Aleatória: exibindo catálogo completo. Selecione uma classe fixa em Criação Inicial para filtrar automaticamente por proficiência.";
      } else {
        const catsArm = [];
        if (profs.armaduras.leve) catsArm.push("Leves");
        if (profs.armaduras.media) catsArm.push("Médias");
        if (profs.armaduras.pesada) catsArm.push("Pesadas");
        const txtArm = catsArm.length
          ? `Armaduras: ${catsArm.join(", ")}${profs.restricaoNaoMetal ? " (sem metal)" : ""}`
          : "Armaduras: Nenhuma (campo oculto)";

        const catsArma = [];
        if (profs.armas.simples) catsArma.push("Simples");
        if (profs.armas.marcial) catsArma.push("Marciais");
        if (profs.armas.avancada) catsArma.push("Avançadas");
        if (profs.armas.especificasNomes.length) catsArma.push(`Específicas (${profs.armas.especificasNomes.join(", ")})`);
        const txtArma = `Armas: ${catsArma.join(" + ") || "Nenhuma"}`;
        elCurEq.textContent = `Filtro da Classe (${profs.clsNome}): ${txtArm} • ${txtArma}.`;
      }
    }

    atualizarOrcamentoEquipamentosUI();
  }

  function inicializarCatalogoEquipamentosUI() {
    atualizarCatalogoEquipamentosUI();
    atualizarVisibilidadeEquipamentosUI();
  }

  function montarPayloadEquipamentosUI() {
    if (document.getElementById("modo-equipamentos")?.value !== "personalizado") {
      return { modo: "procedural" };
    }
    const cardArmOculto = document.getElementById("card-eq-armadura")?.classList.contains("oculto");
    const ccVal = document.getElementById("eq-arma-cc-select")?.value || "procedural";
    let armasCcPayload = "procedural";
    if (app.eqEstado.armas_cc.length || ccVal !== "procedural") {
      armasCcPayload = app.eqEstado.armas_cc.map((w) => w.id);
      if (app.mapaEq.armas_cc[ccVal]) armasCcPayload.push(ccVal);
    }

    const distVal = document.getElementById("eq-arma-dist-select")?.value || "procedural";
    let armasDistPayload = "procedural";
    if (app.eqEstado.armas_dist.length || distVal !== "procedural") {
      armasDistPayload = app.eqEstado.armas_dist.map((w) => w.id);
      if (app.mapaEq.armas_dist[distVal]) armasDistPayload.push(distVal);
    }

    const varVal = document.getElementById("eq-variado-select")?.value || "procedural";
    let variadosPayload = "procedural";
    if (app.eqEstado.variados.length || varVal !== "procedural") {
      const acum = new Map();
      app.eqEstado.variados.forEach((it) => acum.set(it.id, (acum.get(it.id) || 0) + it.quantidade));
      if (app.mapaEq.variados[varVal]) {
        const q = Math.max(1, parseInt(document.getElementById("eq-variado-qtd")?.value || "1", 10) || 1);
        acum.set(varVal, (acum.get(varVal) || 0) + q);
      }
      variadosPayload = Array.from(acum.entries()).map(([id, quantidade]) => ({ id, quantidade }));
    }

    return {
      modo: "personalizado",
      armadura_id: cardArmOculto ? "procedural" : document.getElementById("eq-armadura")?.value || "procedural",
      escudo_id: document.getElementById("eq-escudo")?.value || "procedural",
      armas_corpo_a_corpo_ids: armasCcPayload,
      armas_distancia_ids: armasDistPayload,
      equipamentos_variados: variadosPayload,
    };
  }

  function _adicionarItemListaEq(tipo) {
    if (tipo === "cc" || tipo === "dist") {
      const selId = tipo === "cc" ? "eq-arma-cc-select" : "eq-arma-dist-select";
      const mapa = tipo === "cc" ? app.mapaEq.armas_cc : app.mapaEq.armas_dist;
      const lista = tipo === "cc" ? app.eqEstado.armas_cc : app.eqEstado.armas_dist;
      const sel = document.getElementById(selId);
      const item = mapa[sel?.value];
      if (!item) return;
      lista.push(item);
      if (sel) sel.value = "nenhuma";
    } else if (tipo === "var") {
      const sel = document.getElementById("eq-variado-select");
      const qtdEl = document.getElementById("eq-variado-qtd");
      const qtd = Math.max(1, parseInt(qtdEl?.value || "1", 10) || 1);
      const item = app.mapaEq.variados[sel?.value];
      if (!item) return;
      const existente = app.eqEstado.variados.find((x) => x.id === item.id);
      if (existente) {
        existente.quantidade += qtd;
      } else {
        app.eqEstado.variados.push({ ...item, quantidade: qtd });
      }
      if (sel) sel.value = "nenhum";
      if (qtdEl) qtdEl.value = "1";
    }

    atualizarOrcamentoEquipamentosUI();
  }

  const STORAGE_REGRAS_CASA_LEGADO = "pf2e_regras_casa_v1";
  let _regrasCasaDesbloqueado = false;
  let _modoRegrasCasaConfirmado = "regras_da_casa";

  function _obterCatalogoRegrasCasa() {
    return app.opcoes?.catalogo_regras_casa || { perfis: [], regras: [], padrao_modo: "regras_da_casa" };
  }

  function obterRegrasCasaAtivasIdsUI() {
    const catRc = _obterCatalogoRegrasCasa();
    const modo = document.getElementById("modo-regras-casa")?.value || "regras_da_casa";
    if (modo !== "regras_da_casa") return [];
    const perfil = (catRc.perfis || []).find((p) => p.id === modo);
    return perfil ? [...(perfil.regras_ativas || [])] : [];
  }

  function montarPayloadRegrasCasaUI() {
    const modo = document.getElementById("modo-regras-casa")?.value || "regras_da_casa";
    return { modo };
  }

  function _aplicarOverrideItemCatalogo(itemBase, regrasAtivasObjs) {
    let copia = { ...itemBase, conteudo: [...(itemBase.conteudo || [])] };
    regrasAtivasObjs.forEach((regra) => {
      const ov = regra?.overrides_itens?.[copia.id];
      if (!ov) return;
      ["nome", "quantidade_pacote", "volume", "volume_valor", "descricao"].forEach((campo) => {
        if (ov[campo] !== undefined) copia[campo] = ov[campo];
      });
      if (ov.substituir_conteudo && Array.isArray(copia.conteudo)) {
        copia.conteudo = copia.conteudo.map((c) => ov.substituir_conteudo[c] || c);
      }
    });
    return copia;
  }

  function aplicarRegrasCasaNoCatalogoUI() {
    const catRc = _obterCatalogoRegrasCasa();
    const catEq = app.opcoes?.catalogo_equipamentos;
    const ativasIds = obterRegrasCasaAtivasIdsUI();
    const ativasSet = new Set(ativasIds);
    const regrasAtivasObjs = (catRc.regras || []).filter((r) => ativasSet.has(r.id));

    if (catEq && Array.isArray(catEq.equipamentos_variados)) {
      if (!app._variadosOriginais) {
        app._variadosOriginais = catEq.equipamentos_variados.map((it) => ({
          ...it,
          conteudo: [...(it.conteudo || [])],
        }));
      }
      catEq.equipamentos_variados = app._variadosOriginais.map((orig) =>
        _aplicarOverrideItemCatalogo(orig, regrasAtivasObjs)
      );
      const porId = new Map(catEq.equipamentos_variados.map((it) => [it.id, it]));
      app.eqEstado.variados = app.eqEstado.variados.map((it) => {
        const atualizado = porId.get(it.id);
        return atualizado ? { ...atualizado, quantidade: it.quantidade } : it;
      });
      atualizarCatalogoEquipamentosUI();
    }
  }

  function _atualizarEstadoBloqueioRegrasCasaUI() {
    const selModo = document.getElementById("modo-regras-casa");
    const btnCadeado = document.getElementById("btn-desbloquear-regras-casa");
    const boxSenha = document.getElementById("box-senha-regras-casa");
    if (selModo) {
      selModo.disabled = !_regrasCasaDesbloqueado;
    }
    if (btnCadeado) {
      btnCadeado.classList.toggle("desbloqueado", _regrasCasaDesbloqueado);
      const caixaAberta = Boolean(boxSenha && !boxSenha.classList.contains("oculto"));
      btnCadeado.setAttribute("aria-expanded", String(_regrasCasaDesbloqueado || caixaAberta));
      btnCadeado.textContent = _regrasCasaDesbloqueado ? "🔓 Cancelar" : "🔒 Alterar";
    }
  }

  function _fecharCaixaSenhaRegrasCasa() {
    const boxSenha = document.getElementById("box-senha-regras-casa");
    const inputSenha = document.getElementById("input-senha-regras-casa");
    const msgSenha = document.getElementById("msg-senha-regras-casa");
    if (boxSenha) boxSenha.classList.add("oculto");
    if (inputSenha) inputSenha.value = "";
    if (msgSenha) msgSenha.textContent = "";
    _atualizarEstadoBloqueioRegrasCasaUI();
  }

  function _abrirCaixaSenhaRegrasCasa() {
    const boxSenha = document.getElementById("box-senha-regras-casa");
    const inputSenha = document.getElementById("input-senha-regras-casa");
    const msgSenha = document.getElementById("msg-senha-regras-casa");
    if (!boxSenha) return;
    boxSenha.classList.remove("oculto");
    if (msgSenha) msgSenha.textContent = "";
    if (inputSenha) {
      inputSenha.value = "";
      inputSenha.focus();
    }
    _atualizarEstadoBloqueioRegrasCasaUI();
  }

  async function _confirmarSenhaRegrasCasaUI() {
    const inputSenha = document.getElementById("input-senha-regras-casa");
    const msgSenha = document.getElementById("msg-senha-regras-casa");
    const btnConfirmar = document.getElementById("btn-confirmar-senha-regras-casa");
    const selModo = document.getElementById("modo-regras-casa");
    const senha = (inputSenha?.value || "").trim();

    if (!senha) {
      if (msgSenha) msgSenha.textContent = "Informe a senha.";
      inputSenha?.focus();
      return;
    }

    if (btnConfirmar) btnConfirmar.disabled = true;
    if (msgSenha) msgSenha.textContent = "Validando...";

    try {
      const resp = await fetch("/api/regras-casa/validar-senha", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ senha }),
      });
      const dados = await resp.json().catch(() => ({}));
      if (!resp.ok || !dados.autorizado) {
        _regrasCasaDesbloqueado = false;
        if (msgSenha) msgSenha.textContent = dados.erro || "Senha incorreta.";
        if (inputSenha) {
          inputSenha.select();
          inputSenha.focus();
        }
        _atualizarEstadoBloqueioRegrasCasaUI();
        return;
      }

      _regrasCasaDesbloqueado = true;
      _fecharCaixaSenhaRegrasCasa();
      if (selModo) selModo.focus();
      app.setStatus?.("Senha confirmada. Escolha a opção desejada em Sistema de Regras.", "ok");
    } catch (err) {
      if (msgSenha) msgSenha.textContent = `Erro ao validar: ${err.message}`;
    } finally {
      if (btnConfirmar) btnConfirmar.disabled = false;
    }
  }

  function inicializarRegrasCasaUI() {
    try {
      window.localStorage?.removeItem(STORAGE_REGRAS_CASA_LEGADO);
    } catch (_) {
      // Ignora indisponibilidade de localStorage
    }

    const catRc = _obterCatalogoRegrasCasa();
    const selModo = document.getElementById("modo-regras-casa");
    const padrao = catRc.padrao_modo || "regras_da_casa";

    if (selModo && (catRc.perfis || []).length) {
      selModo.innerHTML = "";
      catRc.perfis.forEach((p) => {
        const opt = document.createElement("option");
        opt.value = p.id;
        opt.textContent = p.nome;
        selModo.appendChild(opt);
      });
      selModo.value = (catRc.perfis || []).some((p) => p.id === padrao) ? padrao : "regras_da_casa";
    } else if (selModo) {
      selModo.value = "regras_da_casa";
    }

    _modoRegrasCasaConfirmado = selModo?.value || "regras_da_casa";
    _regrasCasaDesbloqueado = false;
    _fecharCaixaSenhaRegrasCasa();
    aplicarRegrasCasaNoCatalogoUI();
  }

  function registrarEventosEquipamentos() {
    document.getElementById("btn-desbloquear-regras-casa")?.addEventListener("click", () => {
      if (_regrasCasaDesbloqueado) {
        _regrasCasaDesbloqueado = false;
        _atualizarEstadoBloqueioRegrasCasaUI();
        return;
      }
      const boxSenha = document.getElementById("box-senha-regras-casa");
      if (boxSenha && !boxSenha.classList.contains("oculto")) {
        _fecharCaixaSenhaRegrasCasa();
      } else {
        _abrirCaixaSenhaRegrasCasa();
      }
    });
    document.getElementById("wrap-modo-regras-casa")?.addEventListener("click", (e) => {
      if (_regrasCasaDesbloqueado) return;
      if (e.target?.closest("#btn-desbloquear-regras-casa")) return;
      _abrirCaixaSenhaRegrasCasa();
    });
    document.getElementById("btn-confirmar-senha-regras-casa")?.addEventListener("click", _confirmarSenhaRegrasCasaUI);
    document.getElementById("btn-cancelar-senha-regras-casa")?.addEventListener("click", _fecharCaixaSenhaRegrasCasa);
    document.getElementById("input-senha-regras-casa")?.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        _confirmarSenhaRegrasCasaUI();
      } else if (e.key === "Escape") {
        e.preventDefault();
        _fecharCaixaSenhaRegrasCasa();
      }
    });
    document.getElementById("modo-regras-casa")?.addEventListener("change", async (e) => {
      const selModo = e.currentTarget;
      if (!_regrasCasaDesbloqueado) {
        selModo.value = _modoRegrasCasaConfirmado;
        _abrirCaixaSenhaRegrasCasa();
        return;
      }
      _modoRegrasCasaConfirmado = selModo.value;
      aplicarRegrasCasaNoCatalogoUI();
      _regrasCasaDesbloqueado = false;
      _atualizarEstadoBloqueioRegrasCasaUI();
      const rotulo = selModo.options[selModo.selectedIndex]?.textContent || selModo.value;
      if (app.ultimaFicha && document.getElementById("form-gerador")?.checkValidity()) {
        await app.gerarFichaAtual?.(false);
        app.setStatus?.(
          `Sistema de Regras alterado para "${rotulo}" e ficha atualizada. Seletor bloqueado novamente.`,
          "ok"
        );
      } else {
        app.setStatus?.(`Sistema de Regras alterado para "${rotulo}". Seletor bloqueado novamente.`, "ok");
      }
    });
    ["modo-equipamentos", "eq-armadura", "eq-escudo", "eq-arma-cc-select", "eq-arma-dist-select", "eq-variado-select"].forEach(
      (id) => {
        document.getElementById(id)?.addEventListener("change", atualizarVisibilidadeEquipamentosUI);
      }
    );
    document.getElementById("eq-variado-qtd")?.addEventListener("input", atualizarOrcamentoEquipamentosUI);
    document.getElementById("eq-filtro-busca")?.addEventListener("input", atualizarCatalogoEquipamentosUI);
    document.getElementById("btn-eq-limpar-busca")?.addEventListener("click", () => {
      const inp = document.getElementById("eq-filtro-busca");
      if (inp) {
        inp.value = "";
        inp.focus();
      }
      atualizarCatalogoEquipamentosUI();
    });
    document.getElementById("btn-eq-reset-procedural")?.addEventListener("click", () => {
      resetarEquipamentosProcedural();
      const modoEl = document.getElementById("modo-equipamentos");
      if (modoEl) modoEl.value = "personalizado";
      atualizarVisibilidadeEquipamentosUI();
    });
    document.getElementById("btn-add-arma-cc")?.addEventListener("click", () => _adicionarItemListaEq("cc"));
    document.getElementById("btn-add-arma-dist")?.addEventListener("click", () => _adicionarItemListaEq("dist"));
    document.getElementById("btn-add-variado")?.addEventListener("click", () => _adicionarItemListaEq("var"));
    document.getElementById("painel-equipamentos-custom")?.addEventListener("click", (e) => {
      const btn = e.target.closest("[data-eq-rem]");
      if (!btn) return;
      const tipo = btn.dataset.eqRem;
      const idx = Number(btn.dataset.idx);
      if (tipo === "cc") app.eqEstado.armas_cc.splice(idx, 1);
      else if (tipo === "dist") app.eqEstado.armas_dist.splice(idx, 1);
      else if (tipo === "var") app.eqEstado.variados.splice(idx, 1);
      atualizarOrcamentoEquipamentosUI();
    });
  }

  Object.assign(app, {
    gastoManualEquipamentosPc,
    atualizarOrcamentoEquipamentosUI,
    atualizarVisibilidadeEquipamentosUI,
    resetarEquipamentosProcedural,
    atualizarCatalogoEquipamentosUI,
    inicializarCatalogoEquipamentosUI,
    montarPayloadEquipamentosUI,
    inicializarRegrasCasaUI,
    obterRegrasCasaAtivasIdsUI,
    montarPayloadRegrasCasaUI,
    aplicarRegrasCasaNoCatalogoUI,
    registrarEventosEquipamentos,
  });
})();
