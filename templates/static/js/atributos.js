(() => {
  "use strict";

  const app = window.PF2EApp;
  const { NOMES_ATRIBUTOS, esc } = window.PF2EFichaUI;
  const { ORDEM_ATRIBUTOS, IDS_LIVRES_N1 } = app;

  function preencherSelectAtributo(sel, listaIds, { textoProcedural, textoAleatorio, rotuloExtras = {}, preservar = true } = {}) {
    if (!sel) return;
    const anterior = preservar ? sel.value : "procedural";
    sel.innerHTML = "";

    const optProc = document.createElement("option");
    optProc.value = "procedural";
    optProc.textContent = textoProcedural || "Procedural (melhor p/ conceito)";
    sel.appendChild(optProc);

    const optRand = document.createElement("option");
    optRand.value = "aleatorio";
    optRand.textContent = textoAleatorio || "Aleatório (sortear)";
    sel.appendChild(optRand);

    listaIds.forEach((aid) => {
      const info = NOMES_ATRIBUTOS[aid];
      if (!info) return;
      const opt = document.createElement("option");
      opt.value = aid;
      const extra = rotuloExtras[aid] ? ` (${rotuloExtras[aid]})` : "";
      opt.textContent = `${info[1]} (${info[0]})${extra}`;
      sel.appendChild(opt);
    });

    const validos = Array.from(sel.options).map((o) => o.value);
    sel.value = validos.includes(anterior) ? anterior : "procedural";
  }

  function _sincronizarGrupoSelects(selects) {
    selects.forEach((sel, idx) => {
      if (!sel) return;
      const usadosOutros = new Set(
        selects
          .filter((outro, oIdx) => outro && oIdx !== idx && ORDEM_ATRIBUTOS.includes(outro.value))
          .map((outro) => outro.value)
      );
      Array.from(sel.options).forEach((opt) => {
        if (!ORDEM_ATRIBUTOS.includes(opt.value)) return;
        if (!opt.dataset.baseLabel) {
          opt.dataset.baseLabel = opt.textContent;
        }
        const ocupado = usadosOutros.has(opt.value);
        opt.disabled = ocupado;
        opt.textContent = ocupado
          ? `${opt.dataset.baseLabel} (já escolhido nesta etapa)`
          : opt.dataset.baseLabel;
      });
      if (ORDEM_ATRIBUTOS.includes(sel.value) && usadosOutros.has(sel.value)) {
        sel.value = "procedural";
      }
    });
  }

  function sincronizarExclusaoAtributos() {
    const grp2 = document.getElementById("grupo-attr-anc-livre-2");
    if (grp2 && !grp2.classList.contains("oculto")) {
      _sincronizarGrupoSelects([
        document.getElementById("attr-anc-livre-1"),
        document.getElementById("attr-anc-livre-2"),
      ]);
    }
    _sincronizarGrupoSelects([
      document.getElementById("attr-bio-restrito"),
      document.getElementById("attr-bio-livre"),
    ]);
    _sincronizarGrupoSelects(IDS_LIVRES_N1.map((id) => document.getElementById(id)));
  }

  function atualizarSeletoresAtributosAncestralidade() {
    if (!app.opcoes) return;
    const ancId = document.getElementById("ancestralidade").value;
    const anc = app.opcoes.ancestralidades.find((a) => a.id === ancId);
    const sub = document.getElementById("subgrupo-atb-ancestralidade");
    const info = document.getElementById("info-atb-anc-fixos");
    const sel1 = document.getElementById("attr-anc-livre-1");
    const sel2 = document.getElementById("attr-anc-livre-2");
    const grp2 = document.getElementById("grupo-attr-anc-livre-2");

    if (!anc || ancId === "aleatorio") {
      if (sub) sub.classList.add("oculto");
      if (info) info.textContent = "";
      preencherSelectAtributo(sel1, [], {
        textoProcedural: "Procedural (conforme ancestralidade sorteada)",
        textoAleatorio: "Aleatório (entre opções válidas da raça)",
        preservar: false,
      });
      if (grp2) grp2.classList.add("oculto");
      preencherSelectAtributo(sel2, [], { preservar: false });
      return;
    }

    if (sub) sub.classList.remove("oculto");
    const fixosLista = anc.melhorias_fixas_ids || [];
    const bloqueadosLista = anc.atributos_bloqueados_livres_ids || [
      ...fixosLista,
      ...(anc.defeito_atributo_id ? [anc.defeito_atributo_id] : []),
    ];
    const bloqueados = new Set(bloqueadosLista);
    if (info) {
      const fixTxt = fixosLista.length
        ? fixosLista.map((id) => `+2 ${NOMES_ATRIBUTOS[id][0]}`).join(", ")
        : "Sem fixos (2 livres à escolha)";
      const defTxt = anc.defeito_atributo_id ? ` • Penalidade: -2 ${NOMES_ATRIBUTOS[anc.defeito_atributo_id][0]}` : "";
      const travaTxt = bloqueadosLista.length ? " (bloqueados nesta etapa)" : "";
      info.textContent = `Da raça: ${fixTxt}${defTxt}${travaTxt}`;
    }

    const elegiveis = ORDEM_ATRIBUTOS.filter((aid) => !bloqueados.has(aid));

    preencherSelectAtributo(sel1, elegiveis, {
      textoProcedural: "Procedural (melhor p/ conceito)",
      textoAleatorio: "Aleatório (sortear livre)",
      preservar: true,
    });

    const temDois = Number(anc.qtd_melhorias_livres || 1) >= 2;
    if (grp2) grp2.classList.toggle("oculto", !temDois);
    if (temDois) {
      preencherSelectAtributo(sel2, elegiveis, {
        textoProcedural: "Procedural (2º melhor p/ conceito)",
        textoAleatorio: "Aleatório (sortear 2º livre)",
        preservar: true,
      });
    } else {
      preencherSelectAtributo(sel2, [], { preservar: false });
    }
    sincronizarExclusaoAtributos();
  }

  function atualizarSeletoresAtributosBiografia() {
    if (!app.opcoes) return;
    const bioId = document.getElementById("biografia").value;
    const bio = app.opcoes.biografias.find((b) => b.id === bioId);
    const sub = document.getElementById("subgrupo-atb-biografia");
    const info = document.getElementById("info-atb-bio-opcoes");
    const btnOpt = document.getElementById("btn-bio-atb-opcional");
    const selRes = document.getElementById("attr-bio-restrito");
    const selLiv = document.getElementById("attr-bio-livre");

    if (bio) {
      app.bioManualExpAutomatica = false;
      if (btnOpt) btnOpt.classList.add("oculto");
      if (sub) sub.classList.remove("oculto");
      const idsBio = bio.melhorias_atributo_ids || [];
      if (info) {
        info.textContent = `Opções de ${bio.nome}: ${idsBio.map((id) => NOMES_ATRIBUTOS[id][0]).join(" ou ")} (+2) + 1 Livre (+2)`;
      }
      preencherSelectAtributo(selRes, idsBio, {
        textoProcedural: "Procedural (melhor entre as 2 opções)",
        textoAleatorio: "Aleatório (sortear entre as 2 opções)",
        preservar: true,
      });
      preencherSelectAtributo(selLiv, ORDEM_ATRIBUTOS, {
        textoProcedural: "Procedural (melhor p/ conceito)",
        textoAleatorio: "Aleatório (sortear livre)",
        preservar: true,
      });
    } else if (!app.bioManualExpAutomatica) {
      if (sub) sub.classList.add("oculto");
      if (btnOpt) btnOpt.classList.remove("oculto");
      if (info) info.textContent = "";
      preencherSelectAtributo(selRes, [], {
        textoProcedural: "Procedural (melhor da biografia sorteada)",
        textoAleatorio: "Aleatório (dentre as 2 opções da biografia)",
        preservar: false,
      });
      preencherSelectAtributo(selLiv, ORDEM_ATRIBUTOS, {
        textoProcedural: "Procedural (melhor p/ conceito)",
        textoAleatorio: "Aleatório (sortear livre)",
        preservar: false,
      });
    } else {
      if (btnOpt) btnOpt.classList.add("oculto");
      if (sub) sub.classList.remove("oculto");
      if (info) {
        info.textContent = "A biografia automática/aleatória respeitará os atributos escolhidos abaixo:";
      }
      preencherSelectAtributo(selRes, ORDEM_ATRIBUTOS, {
        textoProcedural: "Procedural (melhor da biografia)",
        textoAleatorio: "Aleatório (sortear entre as 2 opções)",
        preservar: true,
      });
      preencherSelectAtributo(selLiv, ORDEM_ATRIBUTOS, {
        textoProcedural: "Procedural (melhor p/ conceito)",
        textoAleatorio: "Aleatório (sortear livre)",
        preservar: true,
      });
    }
    sincronizarExclusaoAtributos();
  }

  function atualizarSeletoresAtributosClasse() {
    if (!app.opcoes) return;
    const clsId = document.getElementById("classe").value;
    const conId = document.getElementById("conceito").value;
    const cls = app.opcoes.classes.find((c) => c.id === clsId);
    const con = cls ? cls.conceitos.find((x) => x.id === conId) : null;
    const sub = document.getElementById("subgrupo-atb-classe");
    const info = document.getElementById("info-atb-classe-opcoes");
    const grpChave = document.getElementById("grupo-attr-classe-chave");
    const selChave = document.getElementById("attr-classe-chave");

    if (!cls || clsId === "aleatorio") {
      if (sub) sub.classList.add("oculto");
      if (info) info.textContent = "";
      preencherSelectAtributo(selChave, [], { preservar: false });
      return;
    }

    const opcoesChave =
      con && Array.isArray(con.atributo_chave_opcoes) && con.atributo_chave_opcoes.length
        ? con.atributo_chave_opcoes
        : cls.atributo_chave_ids || [];

    if (sub) sub.classList.remove("oculto");
    if (opcoesChave.length > 1) {
      if (grpChave) grpChave.classList.remove("oculto");
      if (info) {
        info.textContent = `${cls.nome} permite escolher o Atributo-Chave (+2):`;
      }
      preencherSelectAtributo(selChave, opcoesChave, {
        textoProcedural: "Procedural (melhor p/ conceito)",
        textoAleatorio: "Aleatório (entre opções da classe)",
        preservar: true,
      });
    } else {
      const unico = opcoesChave[0];
      const rotUnico =
        unico && NOMES_ATRIBUTOS[unico]
          ? `${NOMES_ATRIBUTOS[unico][1]} (${NOMES_ATRIBUTOS[unico][0]})`
          : (cls.atributo_chave || []).join(" / ");
      if (info) info.textContent = `Atributo-Chave da Classe: ${rotUnico} (+2 fixo)`;
      if (grpChave) grpChave.classList.add("oculto");
      preencherSelectAtributo(selChave, [], { preservar: false });
    }
  }

  function definirModoTodosAtributos(modo) {
    const ids = [
      "attr-anc-livre-1",
      "attr-anc-livre-2",
      "attr-bio-restrito",
      "attr-bio-livre",
      "attr-classe-chave",
      ...IDS_LIVRES_N1,
    ];
    ids.forEach((id) => {
      const sel = document.getElementById(id);
      if (!sel) return;
      const validos = Array.from(sel.options).map((o) => o.value);
      sel.value = validos.includes(modo) ? modo : "procedural";
    });
    sincronizarExclusaoAtributos();
    app.atualizarCatalogoPericiasUI?.();
  }

  function atualizarResumoAncestralidade() {
    const ancId = document.getElementById("ancestralidade").value;
    const herId = document.getElementById("heranca").value;
    const anc = app.opcoes.ancestralidades.find((a) => a.id === ancId);
    const her = anc ? anc.herancas.find((h) => h.id === herId) : null;
    const el = document.getElementById("resumo-ancestralidade");
    if (ancId === "aleatorio" || !anc) {
      el.innerHTML =
        `<strong>Ancestralidade: Aleatória</strong>` +
        `<div>Uma das 6 ancestralidades básicas e uma herança compatível serão sorteadas ao gerar a ficha.</div>`;
      return;
    }
    const def = anc.defeito_atributo ? ` • Defeito: ${anc.defeito_atributo}` : "";
    const herTxt = her ? ` — ${her.nome}` : " — Herança Aleatória";
    const herDesc = her
      ? `<div style="margin-top:4px">${esc(her.descricao)}</div>`
      : `<div style="margin-top:4px">A herança será sorteada dentre as opções desta ancestralidade.</div>`;
    el.innerHTML =
      `<strong>${esc(anc.nome)}${esc(herTxt)}</strong>` +
      `<div>PV Base: ${esc(anc.pontos_vida)} • Tamanho: ${esc(anc.tamanho)} • Vel: ${esc(anc.velocidade_m)}m</div>` +
      `<div>Melhorias: ${esc(anc.melhorias_atributo.join(", "))}${esc(def)}</div>` +
      herDesc;
  }

  function atualizarHerancas() {
    const ancId = document.getElementById("ancestralidade").value;
    const anc = app.opcoes.ancestralidades.find((a) => a.id === ancId);
    const sel = document.getElementById("heranca");
    sel.innerHTML = "";

    const optRand = document.createElement("option");
    optRand.value = "aleatorio";
    optRand.textContent = "Aleatória (sortear herança)";
    sel.appendChild(optRand);

    (anc ? anc.herancas : []).forEach((h) => {
      const opt = document.createElement("option");
      opt.value = h.id;
      opt.textContent = h.nome;
      sel.appendChild(opt);
    });
    sel.value = anc && anc.herancas.length ? anc.herancas[0].id : "aleatorio";
    atualizarResumoAncestralidade();
    atualizarSeletoresAtributosAncestralidade();
    app.atualizarCatalogoTalentosUI?.();
  }

  function atualizarResumoBiografia() {
    const bioId = document.getElementById("biografia").value;
    const el = document.getElementById("resumo-biografia");
    if (bioId === "procedural") {
      el.innerHTML =
        `<strong>Biografia: Modo Procedural</strong>` +
        `<div>Será escolhida automaticamente dentre as biografias mais sinérgicas com o conceito/atributos selecionados.</div>`;
      return;
    }
    if (bioId === "aleatoria") {
      el.innerHTML =
        `<strong>Biografia: Aleatória</strong>` +
        `<div>Será sorteada livremente dentre todas as 35 biografias disponíveis ao gerar a ficha.</div>`;
      return;
    }
    const bio = app.opcoes.biografias.find((b) => b.id === bioId);
    if (!bio) {
      el.innerHTML = "";
      return;
    }
    el.innerHTML =
      `<strong>Biografia: ${esc(bio.nome)}</strong>` +
      `<div>Atributos: ${esc(bio.melhorias_atributo_opcoes.join(" ou "))} + 1 Livre</div>` +
      `<div>Perícia: ${esc(bio.pericia_treinada_opcoes.join(" / "))} • ${esc(bio.saber_treinado)} • Talento: ${esc(bio.talento_pericia)}</div>`;
  }

  function atualizarDivindades() {
    const selDiv = document.getElementById("divindade");
    if (!selDiv || !app.opcoes) return;

    const clsId = document.getElementById("classe").value;
    const conId = document.getElementById("conceito").value;
    const cls = app.opcoes.classes.find((c) => c.id === clsId);
    const con = cls ? cls.conceitos.find((x) => x.id === conId) : null;
    const classeAleatoria = clsId === "aleatorio";
    const obrigatoria = Boolean(cls && cls.divindade_obrigatoria);

    const modoAnterior = selDiv.dataset.modo || "";
    const valorAnterior = selDiv.value;
    const grupoDiv = document.getElementById("grupo-divindade");
    const badgeDiv = document.getElementById("badge-divindade");
    const notaDiv = document.getElementById("nota-divindade");

    selDiv.innerHTML = "";

    if (classeAleatoria) {
      selDiv.required = false;
      selDiv.dataset.modo = "aleatorio_classe";
      if (grupoDiv) grupoDiv.classList.remove("divindade-obrigatoria");
      if (badgeDiv) {
        badgeDiv.textContent = "Automática / Opcional";
        badgeDiv.className = "badge-opcional";
      }
      if (notaDiv) {
        notaDiv.textContent = "Com Classe Aleatória, você pode deixar automático ou fixar divindade/nenhuma (aplica filtro na classe sorteada).";
      }

      const optAuto = document.createElement("option");
      optAuto.value = "procedural";
      optAuto.textContent = "Automática (conforme a classe sorteada)";
      selDiv.appendChild(optAuto);

      const optRand = document.createElement("option");
      optRand.value = "aleatoria";
      optRand.textContent = "Aleatória (sortear divindade)";
      selDiv.appendChild(optRand);

      const optNenhuma = document.createElement("option");
      optNenhuma.value = "nenhuma";
      optNenhuma.textContent = "Nenhuma (somente classes opcionais)";
      selDiv.appendChild(optNenhuma);

      (app.opcoes.divindades || []).forEach((d) => {
        const opt = document.createElement("option");
        opt.value = d.id;
        opt.textContent = `${d.nome} (${d.tendencia} • ${d.arma_favorecida_nome})`;
        selDiv.appendChild(opt);
      });

      const opcoesValidas = Array.from(selDiv.options).map((o) => o.value);
      selDiv.value = modoAnterior === "aleatorio_classe" && opcoesValidas.includes(valorAnterior) ? valorAnterior : "procedural";
    } else if (obrigatoria) {
      selDiv.required = true;
      selDiv.dataset.modo = "obrigatoria";
      if (grupoDiv) grupoDiv.classList.add("divindade-obrigatoria");
      if (badgeDiv) {
        badgeDiv.textContent = "Obrigatória";
        badgeDiv.className = "badge-obrigatoria";
      }
      if (notaDiv) {
        notaDiv.textContent = "Obrigatória para esta classe. Exibindo apenas divindades compatíveis com o conceito.";
      }

      const optPlaceholder = document.createElement("option");
      optPlaceholder.value = "";
      optPlaceholder.disabled = true;
      optPlaceholder.textContent = "Selecione uma divindade...";
      selDiv.appendChild(optPlaceholder);

      const optProc = document.createElement("option");
      optProc.value = "procedural";
      optProc.textContent = "Procedural (recomendada pelo conceito)";
      selDiv.appendChild(optProc);

      const optRand = document.createElement("option");
      optRand.value = "aleatoria";
      optRand.textContent = "Aleatória (sortear divindade compatível)";
      selDiv.appendChild(optRand);

      const compativeis = new Set();
      if (con && Array.isArray(con.divindades_compativeis_ids)) {
        con.divindades_compativeis_ids.forEach((id) => compativeis.add(id));
      } else if (cls && conId === "aleatorio") {
        cls.conceitos.forEach((cItem) => {
          (cItem.divindades_compativeis_ids || []).forEach((id) => compativeis.add(id));
        });
      }
      const lista = (app.opcoes.divindades || []).filter((d) => !compativeis.size || compativeis.has(d.id));
      lista.forEach((d) => {
        const opt = document.createElement("option");
        opt.value = d.id;
        opt.textContent = `${d.nome} (${d.tendencia} • ${d.arma_favorecida_nome})`;
        selDiv.appendChild(opt);
      });

      const opcoesValidas = Array.from(selDiv.options).map((o) => o.value).filter((v) => v !== "");
      selDiv.value = modoAnterior === "obrigatoria" && opcoesValidas.includes(valorAnterior) ? valorAnterior : "";
    } else {
      selDiv.required = false;
      selDiv.dataset.modo = "opcional";
      if (grupoDiv) grupoDiv.classList.remove("divindade-obrigatoria");
      if (badgeDiv) {
        badgeDiv.textContent = "Opcional";
        badgeDiv.className = "badge-opcional";
      }
      if (notaDiv) {
        notaDiv.textContent = "Opcional para esta classe (apenas interpretação; não concede poderes de Clérigo/Campeão).";
      }

      const optNenhuma = document.createElement("option");
      optNenhuma.value = "nenhuma";
      optNenhuma.textContent = "Nenhuma (opcional)";
      selDiv.appendChild(optNenhuma);

      const optAleatoria = document.createElement("option");
      optAleatoria.value = "aleatoria";
      optAleatoria.textContent = "Aleatória (sortear divindade)";
      selDiv.appendChild(optAleatoria);

      (app.opcoes.divindades || []).forEach((d) => {
        const opt = document.createElement("option");
        opt.value = d.id;
        opt.textContent = `${d.nome} (${d.tendencia} • ${d.arma_favorecida_nome})`;
        selDiv.appendChild(opt);
      });

      const opcoesValidas = Array.from(selDiv.options).map((o) => o.value);
      selDiv.value = modoAnterior === "opcional" && opcoesValidas.includes(valorAnterior) ? valorAnterior : "nenhuma";
    }
  }

  function atualizarResumoConceito() {
    const clsId = document.getElementById("classe").value;
    const conId = document.getElementById("conceito").value;
    const cls = app.opcoes.classes.find((c) => c.id === clsId);
    const con = cls ? cls.conceitos.find((x) => x.id === conId) : null;
    const el = document.getElementById("resumo-conceito");
    if (clsId === "aleatorio" || !cls) {
      el.innerHTML =
        `<strong>Classe &amp; Conceito: Aleatórios</strong>` +
        `<div>Uma das 12 classes básicas e um de seus 56 conceitos/subclasses PF2E serão sorteados ao gerar a ficha.</div>`;
      return;
    }
    if (!con) {
      el.innerHTML =
        `<strong>${esc(cls.nome)} — Conceito Aleatório</strong>` +
        `<div>PV/Nível: ${esc(cls.pontos_de_vida_por_nivel)} • Chave: ${esc(cls.atributo_chave.join(" / "))}</div>` +
        `<div class="conceito-desc">Um conceito/subclasse desta classe será sorteado ao gerar a ficha.</div>`;
      return;
    }
    const nomesSubs =
      Array.isArray(con.subclasses_oficiais_nomes) && con.subclasses_oficiais_nomes.length
        ? con.subclasses_oficiais_nomes
        : [con.subclasse_oficial_nome];
    const subTexto =
      nomesSubs.length > 1
        ? `Automática entre: ${nomesSubs.join(" ou ")}`
        : `Automática: ${nomesSubs[0]}`;
    el.innerHTML =
      `<strong>${esc(con.titulo_completo)}</strong>` +
      `<div>PV/Nível: ${esc(cls.pontos_de_vida_por_nivel)} • Chave: ${esc(cls.atributo_chave.join(" / "))}</div>` +
      `<div class="conceito-desc"><b>O que faz:</b> ${esc(con.resumo_proposta)}</div>` +
      (con.sinergia_mecanica
        ? `<div class="conceito-sinergia"><b>Sinergia:</b> ${esc(con.sinergia_mecanica)}</div>`
        : "") +
      `<div class="conceito-sub-tag">Subclasse PF2E: ${esc(subTexto)}</div>`;
  }

  function atualizarConceitos() {
    const clsId = document.getElementById("classe").value;
    const cls = app.opcoes.classes.find((c) => c.id === clsId);
    const sel = document.getElementById("conceito");
    sel.innerHTML = "";

    const optRand = document.createElement("option");
    optRand.value = "aleatorio";
    optRand.textContent = "Aleatório (sortear conceito)";
    sel.appendChild(optRand);

    (cls ? cls.conceitos : []).forEach((c) => {
      const opt = document.createElement("option");
      opt.value = c.id;
      opt.textContent = c.nome;
      sel.appendChild(opt);
    });
    sel.value = cls && cls.conceitos.length ? cls.conceitos[0].id : "aleatorio";
    atualizarResumoConceito();
    atualizarDivindades();
    atualizarSeletoresAtributosClasse();
    app.atualizarCatalogoTalentosUI?.();
  }

  Object.assign(app, {
    preencherSelectAtributo,
    sincronizarExclusaoAtributos,
    atualizarSeletoresAtributosAncestralidade,
    atualizarSeletoresAtributosBiografia,
    atualizarSeletoresAtributosClasse,
    definirModoTodosAtributos,
    atualizarResumoAncestralidade,
    atualizarHerancas,
    atualizarResumoBiografia,
    atualizarDivindades,
    atualizarResumoConceito,
    atualizarConceitos,
  });
})();
