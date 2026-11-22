(() => {
  "use strict";

  const { NOMES_ATRIBUTOS, esc, renderizarFicha, aplicarAba } = window.PF2EFichaUI;

  let OPCOES = null;
  let ULTIMA_FICHA = null;
  let BIO_MANUAL_EXP_AUTOMATICA = false;
  const PER_ESTADO = { selecionadas: [] };
  const EQ_ESTADO = { armas_cc: [], armas_dist: [], variados: [] };
  const MAPA_EQ = { armaduras: {}, escudos: {}, armas_cc: {}, armas_dist: {}, variados: {} };

  function setStatus(texto, tipo = "") {
    const el = document.getElementById("mensagem-status");
    el.textContent = texto;
    el.className = `mensagem-status ${tipo}`.trim();
  }

  const ORDEM_ATRIBUTOS = ["for", "des", "con", "int", "sab", "car"];
  const IDS_LIVRES_N1 = ["attr-livre-1", "attr-livre-2", "attr-livre-3", "attr-livre-4"];

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

  function atualizarSeletoresAtributosAncestralidade() {
    if (!OPCOES) return;
    const ancId = document.getElementById("ancestralidade").value;
    const anc = OPCOES.ancestralidades.find((a) => a.id === ancId);
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
    if (!OPCOES) return;
    const bioId = document.getElementById("biografia").value;
    const bio = OPCOES.biografias.find((b) => b.id === bioId);
    const sub = document.getElementById("subgrupo-atb-biografia");
    const info = document.getElementById("info-atb-bio-opcoes");
    const btnOpt = document.getElementById("btn-bio-atb-opcional");
    const selRes = document.getElementById("attr-bio-restrito");
    const selLiv = document.getElementById("attr-bio-livre");

    if (bio) {
      BIO_MANUAL_EXP_AUTOMATICA = false;
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
    } else if (!BIO_MANUAL_EXP_AUTOMATICA) {
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
    if (!OPCOES) return;
    const clsId = document.getElementById("classe").value;
    const conId = document.getElementById("conceito").value;
    const cls = OPCOES.classes.find((c) => c.id === clsId);
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
  }

  function atualizarHerancas() {
    const ancId = document.getElementById("ancestralidade").value;
    const anc = OPCOES.ancestralidades.find((a) => a.id === ancId);
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
    atualizarCatalogoTalentosUI();
  }

  function atualizarResumoAncestralidade() {
    const ancId = document.getElementById("ancestralidade").value;
    const herId = document.getElementById("heranca").value;
    const anc = OPCOES.ancestralidades.find((a) => a.id === ancId);
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
    const bio = OPCOES.biografias.find((b) => b.id === bioId);
    if (!bio) {
      el.innerHTML = "";
      return;
    }
    el.innerHTML =
      `<strong>Biografia: ${esc(bio.nome)}</strong>` +
      `<div>Atributos: ${esc(bio.melhorias_atributo_opcoes.join(" ou "))} + 1 Livre</div>` +
      `<div>Perícia: ${esc(bio.pericia_treinada_opcoes.join(" / "))} • ${esc(bio.saber_treinado)} • Talento: ${esc(bio.talento_pericia)}</div>`;
  }

  function atualizarConceitos() {
    const clsId = document.getElementById("classe").value;
    const cls = OPCOES.classes.find((c) => c.id === clsId);
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
    atualizarCatalogoTalentosUI();
  }

  function atualizarDivindades() {
    const selDiv = document.getElementById("divindade");
    if (!selDiv || !OPCOES) return;

    const clsId = document.getElementById("classe").value;
    const conId = document.getElementById("conceito").value;
    const cls = OPCOES.classes.find((c) => c.id === clsId);
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

      (OPCOES.divindades || []).forEach((d) => {
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
      const lista = (OPCOES.divindades || []).filter((d) => !compativeis.size || compativeis.has(d.id));
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

      (OPCOES.divindades || []).forEach((d) => {
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
    const cls = OPCOES.classes.find((c) => c.id === clsId);
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

  async function inicializar() {
    try {
      const resp = await fetch("/api/opcoes");
      OPCOES = await resp.json();

      const selAnc = document.getElementById("ancestralidade");
      const optAncRand = document.createElement("option");
      optAncRand.value = "aleatorio";
      optAncRand.textContent = "Aleatória (sortear ancestralidade)";
      selAnc.appendChild(optAncRand);
      OPCOES.ancestralidades.forEach((a) => {
        const opt = document.createElement("option");
        opt.value = a.id;
        opt.textContent = `${a.nome} (PV ${a.pontos_vida})`;
        selAnc.appendChild(opt);
      });
      selAnc.value = "aleatorio";

      const selBio = document.getElementById("biografia");
      const optAuto = document.createElement("option");
      optAuto.value = "procedural";
      optAuto.textContent = "Procedural (recomendada pelo conceito)";
      selBio.appendChild(optAuto);
      const optBioRand = document.createElement("option");
      optBioRand.value = "aleatoria";
      optBioRand.textContent = "Aleatória (sortear qualquer biografia)";
      selBio.appendChild(optBioRand);
      OPCOES.biografias.forEach((b) => {
        const opt = document.createElement("option");
        opt.value = b.id;
        opt.textContent = b.nome;
        selBio.appendChild(opt);
      });

      const selCls = document.getElementById("classe");
      const optClsRand = document.createElement("option");
      optClsRand.value = "aleatorio";
      optClsRand.textContent = "Aleatória (sortear classe)";
      selCls.appendChild(optClsRand);
      OPCOES.classes.forEach((c) => {
        const opt = document.createElement("option");
        opt.value = c.id;
        opt.textContent = c.nome;
        selCls.appendChild(opt);
      });
      selCls.value = "aleatorio";

      selAnc.addEventListener("change", atualizarHerancas);
      document.getElementById("heranca").addEventListener("change", () => {
        atualizarResumoAncestralidade();
        atualizarCatalogoTalentosUI();
      });
      selBio.addEventListener("change", () => {
        if (selBio.value !== "procedural" && selBio.value !== "aleatoria") {
          BIO_MANUAL_EXP_AUTOMATICA = false;
        }
        atualizarResumoBiografia();
        atualizarSeletoresAtributosBiografia();
        atualizarCatalogoTalentosUI();
      });
      const btnBioOpcional = document.getElementById("btn-bio-atb-opcional");
      if (btnBioOpcional) {
        btnBioOpcional.addEventListener("click", () => {
          BIO_MANUAL_EXP_AUTOMATICA = true;
          atualizarSeletoresAtributosBiografia();
        });
      }
      selCls.addEventListener("change", atualizarConceitos);
      document.getElementById("conceito").addEventListener("change", () => {
        atualizarResumoConceito();
        atualizarDivindades();
        atualizarSeletoresAtributosClasse();
        atualizarCatalogoTalentosUI();
      });
      document.getElementById("divindade")?.addEventListener("change", () => {
        atualizarCatalogoPericiasUI();
        atualizarCatalogoEquipamentosUI();
      });

      IDS_LIVRES_N1.forEach((id) => {
        preencherSelectAtributo(document.getElementById(id), ORDEM_ATRIBUTOS, {
          textoProcedural: "Procedural (melhor p/ conceito)",
          textoAleatorio: "Aleatório (sortear distinto)",
          preservar: false,
        });
      });
      ["attr-anc-livre-1", "attr-anc-livre-2", "attr-bio-restrito", "attr-bio-livre", "attr-classe-chave", ...IDS_LIVRES_N1].forEach(
        (id) => {
          const el = document.getElementById(id);
          if (el) {
            el.addEventListener("change", () => {
              sincronizarExclusaoAtributos();
              atualizarCatalogoPericiasUI();
            });
          }
        }
      );

      atualizarHerancas();
      atualizarResumoBiografia();
      atualizarSeletoresAtributosBiografia();
      atualizarConceitos();
      inicializarCatalogoEquipamentosUI();
      atualizarCatalogoTalentosUI();
      atualizarVisibilidadeTalentosUI();
      atualizarCatalogoPericiasUI();
      atualizarVisibilidadePericiasUI();
    } catch (err) {
      setStatus(`Erro ao carregar opções: ${err.message}`, "erro");
    }
  }

  const TALENTOS_PERICIAS_ANC_UI = {
    pericia_natural: { extras: 2, fixas: [] },
    longevidade_ancestral: { extras: 1, fixas: [] },
    saber_enanico: { extras: 0, fixas: ["manufatura", "religiao"] },
    saber_elfico: { extras: 0, fixas: ["arcanismo", "natureza"] },
    saber_gnomico: { extras: 0, fixas: ["ocultismo", "natureza"] },
    saber_goblinoide: { extras: 0, fixas: ["natureza", "furtividade"] },
    saber_halfling: { extras: 0, fixas: ["acrobatismo", "furtividade"] },
  };

  function _calcularModIntAtualUI() {
    const ancId = document.getElementById("ancestralidade")?.value || "aleatorio";
    const bioId = document.getElementById("biografia")?.value || "procedural";
    const clsId = document.getElementById("classe")?.value || "aleatorio";
    const conId = document.getElementById("conceito")?.value || "aleatorio";
    const ancObj = OPCOES?.ancestralidades?.find((a) => a.id === ancId) || null;
    const bioObj = OPCOES?.biografias?.find((b) => b.id === bioId) || null;
    const clsObj = OPCOES?.classes?.find((c) => c.id === clsId) || null;
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

  function _calcularEstadoPericiasUI() {
    const catPer = OPCOES?.catalogo_pericias || [];
    const mapaPer = Object.fromEntries(catPer.map((p) => [p.id, p]));
    const herId = document.getElementById("heranca")?.value || "aleatorio";
    const bioId = document.getElementById("biografia")?.value || "procedural";
    const clsId = document.getElementById("classe")?.value || "aleatorio";
    const conId = document.getElementById("conceito")?.value || "aleatorio";
    const divId = document.getElementById("divindade")?.value || "";

    const bioObj = OPCOES?.biografias?.find((b) => b.id === bioId) || null;
    const clsObj = OPCOES?.classes?.find((c) => c.id === clsId) || null;
    const conObj = clsObj ? clsObj.conceitos.find((x) => x.id === conId) : null;
    const divObj = (OPCOES?.divindades || []).find((d) => d.id === divId) || null;

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
    const catPer = OPCOES?.catalogo_pericias;
    if (!catPer) return;

    const st = _calcularEstadoPericiasUI();
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
      PER_ESTADO.selecionadas = [];
      if (elVagas) {
        elVagas.textContent = "Selecione uma Classe fixa";
        elVagas.className = "saldo-alerta";
      }
      if (elFormula) elFormula.textContent = "Escolha uma Classe em Criação Inicial para liberar a seleção manual de perícias.";
      if (grid) {
        grid.innerHTML = `<div class="box-tal-auto">Classe Aleatória ativa: as perícias serão calculadas automaticamente conforme a classe sorteada.</div>`;
      }
      atualizarResumosEtapasUI();
      return;
    }

    // Limpa seleções que viraram fixas ou que excedem o teto após reduzir INT / trocar classe
    PER_ESTADO.selecionadas = PER_ESTADO.selecionadas
      .filter((pid) => st.mapaPer[pid] && !st.fixasMap.has(pid))
      .slice(0, st.vagasLivresTotal);

    const qtdSel = PER_ESTADO.selecionadas.length;
    const cheio = qtdSel >= st.vagasLivresTotal;

    if (elVagas) {
      elVagas.textContent = `${qtdSel} / ${st.vagasLivresTotal} selecionadas`;
      elVagas.className = cheio ? "saldo-ok" : "saldo-ok";
    }
    if (elFormula) {
      elFormula.textContent = st.formulaTxt;
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
          const marcada = PER_ESTADO.selecionadas.includes(p.id);
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

    atualizarResumosEtapasUI();
  }

  function atualizarVisibilidadePericiasUI() {
    const modo = document.getElementById("modo-pericias")?.value || "procedural";
    document.getElementById("painel-pericias-custom")?.classList.toggle("oculto", modo !== "personalizado");
    atualizarCatalogoPericiasUI();
    atualizarResumosEtapasUI();
  }

  function resetarPericiasProcedural() {
    const modoEl = document.getElementById("modo-pericias");
    if (modoEl) modoEl.value = "procedural";
    ["per-bio-opcao", "per-cls-opcao", "per-div-opcao"].forEach((id) => {
      const el = document.getElementById(id);
      if (el) el.value = "procedural";
    });
    PER_ESTADO.selecionadas = [];
    atualizarVisibilidadePericiasUI();
  }

  function _montarPayloadPericiasUI() {
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
      pericias_livres: PER_ESTADO.selecionadas.length ? [...PER_ESTADO.selecionadas] : "procedural",
    };
  }

  const CLASSES_CONJURADORAS_UI = new Set(["bardo", "clerigo", "druida", "feiticeiro", "mago"]);
  const IDS_TAL_CLASSE = ["tal-classe-1", "tal-classe-2", "tal-classe-3"];
  const IDS_TAL_GERAIS = ["tal-geral-1", "tal-geral-2"];

  function _normTxt(txt) {
    return String(txt || "")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase()
      .trim();
  }

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

  function sincronizarExclusaoTalentos() {
    _sincronizarExclusaoGrupoTalentos(IDS_TAL_CLASSE);
    _sincronizarExclusaoGrupoTalentos(IDS_TAL_GERAIS);
  }

  function atualizarCatalogoTalentosUI() {
    const cat = OPCOES?.catalogo_talentos;
    if (!cat) return;

    const ancId = document.getElementById("ancestralidade")?.value || "aleatorio";
    const herId = document.getElementById("heranca")?.value || "aleatorio";
    const bioId = document.getElementById("biografia")?.value || "procedural";
    const clsId = document.getElementById("classe")?.value || "aleatorio";
    const conId = document.getElementById("conceito")?.value || "aleatorio";
    const ancObj = OPCOES.ancestralidades.find((a) => a.id === ancId);
    const bioObj = OPCOES.biografias.find((b) => b.id === bioId);
    const clsObj = OPCOES.classes.find((c) => c.id === clsId);
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
        ? _normTxt(bioObj.talento_pericia.split(" para ")[0])
        : "";
      const poolPer = (cat.pericia_n1 || []).filter((t) => !bioTalNorm || _normTxt(t.nome) !== bioTalNorm);
      _preencherSelectTalento(selPer, poolPer, { textoProcedural: "Procedural (melhor p/ conceito)" });
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

    // Oculta o container "4. Demais Talentos" inteiro se nem Perícia nem Geral estiverem disponíveis
    document.getElementById("card-tal-demais")?.classList.toggle("oculto", !temPericiaSelecionavel && !temGeralSelecionavel);

    const elCur = document.getElementById("tal-resumo-curadoria");
    if (elCur) {
      elCur.textContent = slotsVisiveisTotal > 0
        ? `Curadoria PF2E (1º Nível): ${slotsVisiveisTotal} slot${slotsVisiveisTotal > 1 ? "s" : ""} selecionável${slotsVisiveisTotal > 1 ? "is" : ""} disponível${slotsVisiveisTotal > 1 ? "is" : ""} para esta ficha.`
        : "Escolha uma Ancestralidade ou Classe fixa em Criação Inicial para liberar seletores manuais de talentos.";
    }

    sincronizarExclusaoTalentos();
    atualizarCatalogoPericiasUI();
    atualizarCatalogoEquipamentosUI();
    atualizarResumosEtapasUI();
  }

  function atualizarVisibilidadeTalentosUI() {
    const modo = document.getElementById("modo-talentos")?.value || "procedural";
    document.getElementById("painel-talentos-custom")?.classList.toggle("oculto", modo !== "personalizado");
    atualizarCatalogoPericiasUI();
    atualizarCatalogoEquipamentosUI();
    atualizarResumosEtapasUI();
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

  function _montarPayloadTalentosUI() {
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

  function fmtPrecoEq(pcBruto) {
    const pc = Math.round(Number(pcBruto || 0));
    const ppTot = pc / 10;
    const ppStr = Number.isInteger(ppTot) ? `${ppTot} pp` : `${ppTot.toFixed(1).replace(".", ",")} pp`;
    const po = Math.floor(pc / 100);
    const remPp = Math.floor((pc % 100) / 10);
    const remPc = pc % 10;
    if (po === 0 && remPc === 0) return ppStr;
    const partes = [];
    if (po > 0) partes.push(`${po} po`);
    if (remPp > 0) partes.push(`${remPp} pp`);
    if (remPc > 0) partes.push(`${remPc} pc`);
    return `${ppStr} (${partes.join(", ")})`;
  }

  function _criarOptgroup(sel, label) {
    const og = document.createElement("optgroup");
    og.label = label;
    sel.appendChild(og);
    return og;
  }

  function _custoVariadoSelectPc() {
    const varId = document.getElementById("eq-variado-select")?.value || "procedural";
    if (!MAPA_EQ.variados[varId]) return 0;
    const qtd = Math.max(1, parseInt(document.getElementById("eq-variado-qtd")?.value || "1", 10) || 1);
    return MAPA_EQ.variados[varId].preco_pc * qtd;
  }

  function _gastoManualEquipamentosPc() {
    let gasto = 0;
    const armId = document.getElementById("eq-armadura")?.value || "procedural";
    if (MAPA_EQ.armaduras[armId]) {
      gasto += MAPA_EQ.armaduras[armId].preco_pc;
    }
    const escId = document.getElementById("eq-escudo")?.value || "procedural";
    if (MAPA_EQ.escudos[escId]) {
      gasto += MAPA_EQ.escudos[escId].preco_pc;
    }
    const ccId = document.getElementById("eq-arma-cc-select")?.value || "procedural";
    if (MAPA_EQ.armas_cc[ccId]) {
      gasto += MAPA_EQ.armas_cc[ccId].preco_pc;
    }
    EQ_ESTADO.armas_cc.forEach((w) => {
      gasto += w.preco_pc;
    });
    const distId = document.getElementById("eq-arma-dist-select")?.value || "procedural";
    if (MAPA_EQ.armas_dist[distId]) {
      gasto += MAPA_EQ.armas_dist[distId].preco_pc;
    }
    EQ_ESTADO.armas_dist.forEach((w) => {
      gasto += w.preco_pc;
    });
    gasto += _custoVariadoSelectPc();
    EQ_ESTADO.variados.forEach((it) => {
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
    const armAtual = MAPA_EQ.armaduras[document.getElementById("eq-armadura")?.value]?.preco_pc || 0;
    const escAtual = MAPA_EQ.escudos[document.getElementById("eq-escudo")?.value]?.preco_pc || 0;
    const ccAtual = MAPA_EQ.armas_cc[document.getElementById("eq-arma-cc-select")?.value]?.preco_pc || 0;
    const distAtual = MAPA_EQ.armas_dist[document.getElementById("eq-arma-dist-select")?.value]?.preco_pc || 0;
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

    atualizarSelectSaldo("eq-armadura", MAPA_EQ.armaduras, saldoPc + armAtual);
    atualizarSelectSaldo("eq-escudo", MAPA_EQ.escudos, saldoPc + escAtual);
    atualizarSelectSaldo("eq-arma-cc-select", MAPA_EQ.armas_cc, saldoPc + ccAtual);
    atualizarSelectSaldo("eq-arma-dist-select", MAPA_EQ.armas_dist, saldoPc + distAtual);
    const qtdVar = Math.max(1, parseInt(document.getElementById("eq-variado-qtd")?.value || "1", 10) || 1);
    atualizarSelectSaldo("eq-variado-select", MAPA_EQ.variados, saldoPc + varAtual, qtdVar);

    const setAddDisabled = (btnId, selId, mapa) => {
      const btn = document.getElementById(btnId);
      const val = document.getElementById(selId)?.value;
      if (btn) btn.disabled = !mapa[val];
    };
    setAddDisabled("btn-add-arma-cc", "eq-arma-cc-select", MAPA_EQ.armas_cc);
    setAddDisabled("btn-add-arma-dist", "eq-arma-dist-select", MAPA_EQ.armas_dist);
    setAddDisabled("btn-add-variado", "eq-variado-select", MAPA_EQ.variados);

    const btnKit = document.getElementById("btn-add-kit-av");
    if (btnKit) btnKit.disabled = saldoPc < 70;
  }

  function atualizarOrcamentoEquipamentosUI() {
    const cat = OPCOES?.catalogo_equipamentos;
    if (!cat) return;
    const orcPc = Number(cat.orcamento_inicial_pc || 1500);
    const gastoPc = _gastoManualEquipamentosPc();
    const saldoPc = orcPc - gastoPc;

    const elGasto = document.getElementById("eq-resumo-gasto");
    const elSaldo = document.getElementById("eq-resumo-saldo");
    if (elGasto) elGasto.textContent = fmtPrecoEq(gastoPc);
    if (elSaldo) {
      elSaldo.textContent = saldoPc >= 0 ? fmtPrecoEq(saldoPc) : `Excedido em ${fmtPrecoEq(Math.abs(saldoPc))}`;
      elSaldo.className = saldoPc <= 0 ? "saldo-alerta" : "saldo-ok";
    }

    _renderListaEquipamentos("lista-eq-armas-cc", EQ_ESTADO.armas_cc, "cc");
    _renderListaEquipamentos("lista-eq-armas-dist", EQ_ESTADO.armas_dist, "dist");
    _renderListaEquipamentos("lista-eq-variados", EQ_ESTADO.variados, "var");
    _sincronizarLimitesCompraUI(Math.max(0, saldoPc));
    atualizarResumosEtapasUI();
  }

  function atualizarVisibilidadeEquipamentosUI() {
    const modo = document.getElementById("modo-equipamentos")?.value || "procedural";
    const painel = document.getElementById("painel-equipamentos-custom");
    if (painel) painel.classList.toggle("oculto", modo !== "personalizado");
    atualizarOrcamentoEquipamentosUI();
    atualizarResumosEtapasUI();
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
    EQ_ESTADO.armas_cc = [];
    EQ_ESTADO.armas_dist = [];
    EQ_ESTADO.variados = [];
    atualizarVisibilidadeEquipamentosUI();
  }

  function _calcularProficienciasEquipamentosUI() {
    const cat = OPCOES?.catalogo_equipamentos;
    const clsId = document.getElementById("classe")?.value || "aleatorio";
    const conId = document.getElementById("conceito")?.value || "aleatorio";
    const divId = document.getElementById("divindade")?.value || "";
    const clsObj = OPCOES?.classes?.find((c) => c.id === clsId) || null;
    const conObj = clsObj ? clsObj.conceitos.find((x) => x.id === conId) : null;
    const divObj = (OPCOES?.divindades || []).find((d) => d.id === divId) || null;

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
        armas.especificas.add(_normTxt(divObj.arma_favorecida_nome));
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
        (famMap[talAnc].armas || []).forEach((w) => armas.armasAncestrais.add(_normTxt(w)));
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
    const catNorm = _normTxt(w.categoria);
    const nomeNorm = _normTxt(w.nome);
    const tracosNorm = (w.tracos || []).map(_normTxt);
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
    if (a.armamentoNaoConvencional && _normTxt(w.raridade) === "incomum") {
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

  function atualizarCatalogoEquipamentosUI() {
    const cat = OPCOES?.catalogo_equipamentos;
    if (!cat) return;

    const profs = _calcularProficienciasEquipamentosUI();
    MAPA_EQ.armaduras = {};
    MAPA_EQ.escudos = {};
    MAPA_EQ.armas_cc = {};
    MAPA_EQ.armas_dist = {};
    MAPA_EQ.variados = {};

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
            if (profs.restricaoNaoMetal && _normTxt(a.material) === "metal") return false;
            return true;
          });
          if (!lista.length) return;
          const og = _criarOptgroup(selArm, grupo);
          lista.forEach((a) => {
            MAPA_EQ.armaduras[a.id] = a;
            const opt = document.createElement("option");
            opt.value = a.id;
            const lim = a.limite_destreza !== null ? `Lim DES +${a.limite_destreza}` : "Sem Lim DES";
            opt.textContent = `${a.nome} (+${a.bonus_ca} CA, ${lim}) — ${fmtPrecoEq(a.preco_pc)}`;
            og.appendChild(opt);
          });
        });
        selArm.value = antArm === "procedural" || antArm === "nenhuma" || MAPA_EQ.armaduras[antArm] ? antArm : "procedural";
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
          MAPA_EQ.escudos[s.id] = s;
          const opt = document.createElement("option");
          opt.value = s.id;
          opt.textContent = `${s.nome} (+${s.bonus_ca} CA, Dureza ${s.dureza}, PV ${s.pv}) — ${fmtPrecoEq(s.preco_pc)}`;
          selEsc.appendChild(opt);
        });
      selEsc.value = antEsc === "procedural" || antEsc === "nenhum" || MAPA_EQ.escudos[antEsc] ? antEsc : "procedural";
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

      // Remove da lista de compradas qualquer arma que deixou de ser permitida ao trocar de classe
      const idsPermitidos = new Set(permitidas.map((w) => w.id));
      EQ_ESTADO[estadoChave] = EQ_ESTADO[estadoChave].filter((w) => idsPermitidos.has(w.id));

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
          if (!itens.length) return;
          const og = _criarOptgroup(sel, rotulo);
          itens.forEach((w) => {
            mapaDestino[w.id] = w;
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
      MAPA_EQ.armas_cc,
      "armas_cc",
      "arma corporal"
    );
    popularArmasFiltradas(
      "card-eq-arma-dist",
      "eq-arma-dist-select",
      "nota-eq-arma-dist",
      cat.armas_distancia,
      MAPA_EQ.armas_dist,
      "armas_dist",
      "arma à distância"
    );

    // 5. Equipamentos Variados (destaca ferramentas essenciais da classe e oculta focos exclusivos de outras classes)
    const selVar = document.getElementById("eq-variado-select");
    const variadosPermitidos = (cat.equipamentos_variados || []).filter((it) => _itemVariadoPermitidoParaBuild(it, profs));
    const idsVarPerm = new Set(variadosPermitidos.map((it) => it.id));
    EQ_ESTADO.variados = EQ_ESTADO.variados.filter((it) => idsVarPerm.has(it.id));

    if (selVar) {
      const antVar = selVar.value || "procedural";
      selVar.innerHTML =
        `<option value="procedural">Procedural (Kit de Aventureiro + ferramentas da classe)</option>` +
        `<option value="nenhum">Nenhum item variado (ou usar lista abaixo)</option>`;

      const addItemOpt = (og, it) => {
        MAPA_EQ.variados[it.id] = it;
        const opt = document.createElement("option");
        opt.value = it.id;
        const pac = it.quantidade_pacote > 1 && !it.nome.includes(`(${it.quantidade_pacote})`) ? ` (${it.quantidade_pacote} un.)` : "";
        opt.textContent = `${it.nome}${pac} — ${fmtPrecoEq(it.preco_pc)}`;
        og.appendChild(opt);
      };

      const usadosRec = new Set();
      if (profs.filtrando && profs.ferramentasRecomendadas.size > 0) {
        const recItens = variadosPermitidos.filter((it) => profs.ferramentasRecomendadas.has(it.id));
        if (recItens.length) {
          const ogRec = _criarOptgroup(selVar, `Essenciais de ${profs.clsNome}`);
          recItens.forEach((it) => {
            usadosRec.add(it.id);
            addItemOpt(ogRec, it);
          });
        }
      }

      ["Equipamentos de Aventura", "Equipamentos Incomuns", "Munições"].forEach((subcat) => {
        const itens = variadosPermitidos.filter((it) => it.subcategoria === subcat && !usadosRec.has(it.id));
        if (!itens.length) return;
        const og = _criarOptgroup(selVar, subcat);
        itens.forEach((it) => addItemOpt(og, it));
      });
      selVar.value = antVar === "procedural" || antVar === "nenhum" || MAPA_EQ.variados[antVar] ? antVar : "procedural";
    }

    // Banner de curadoria de equipamentos por classe
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

  function _montarPayloadEquipamentosUI() {
    if (document.getElementById("modo-equipamentos")?.value !== "personalizado") {
      return { modo: "procedural" };
    }
    const cardArmOculto = document.getElementById("card-eq-armadura")?.classList.contains("oculto");
    const ccVal = document.getElementById("eq-arma-cc-select")?.value || "procedural";
    let armasCcPayload = "procedural";
    if (EQ_ESTADO.armas_cc.length || ccVal !== "procedural") {
      armasCcPayload = EQ_ESTADO.armas_cc.map((w) => w.id);
      if (MAPA_EQ.armas_cc[ccVal]) armasCcPayload.push(ccVal);
    }

    const distVal = document.getElementById("eq-arma-dist-select")?.value || "procedural";
    let armasDistPayload = "procedural";
    if (EQ_ESTADO.armas_dist.length || distVal !== "procedural") {
      armasDistPayload = EQ_ESTADO.armas_dist.map((w) => w.id);
      if (MAPA_EQ.armas_dist[distVal]) armasDistPayload.push(distVal);
    }

    const varVal = document.getElementById("eq-variado-select")?.value || "procedural";
    let variadosPayload = "procedural";
    if (EQ_ESTADO.variados.length || varVal !== "procedural") {
      const acum = new Map();
      EQ_ESTADO.variados.forEach((it) => acum.set(it.id, (acum.get(it.id) || 0) + it.quantidade));
      if (MAPA_EQ.variados[varVal]) {
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

  function alternarEtapaAcordeao(chaveEtapa, forcarEstado = null) {
    const cards = document.querySelectorAll(".etapa-card[data-etapa]");
    if (!cards.length) return;
    let abriuCard = null;
    cards.forEach((card) => {
      const ehAlvo = card.dataset.etapa === chaveEtapa;
      const jaAberta = card.classList.contains("aberta");
      const abrir = ehAlvo ? (forcarEstado !== null ? Boolean(forcarEstado) : !jaAberta) : false;
      card.classList.toggle("aberta", abrir);
      const btn = card.querySelector("[data-etapa-toggle]");
      if (btn) btn.setAttribute("aria-expanded", String(abrir));
      const corpo = card.querySelector(".etapa-corpo");
      if (corpo) corpo.classList.toggle("oculto", !abrir);
      if (abrir) abriuCard = card;
    });
    if (abriuCard && forcarEstado === true) {
      abriuCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  }

  function atualizarResumosEtapasUI() {
    if (!OPCOES) return;
    const elCriacao = document.getElementById("resumo-etapa-criacao");
    if (elCriacao) {
      const ancId = document.getElementById("ancestralidade")?.value || "aleatorio";
      const clsId = document.getElementById("classe")?.value || "aleatorio";
      const conId = document.getElementById("conceito")?.value || "aleatorio";
      const anc = OPCOES.ancestralidades.find((a) => a.id === ancId);
      const cls = OPCOES.classes.find((c) => c.id === clsId);
      const con = cls ? cls.conceitos.find((x) => x.id === conId) : null;
      if (ancId === "aleatorio" && clsId === "aleatorio") {
        elCriacao.textContent = "Aleatório (Procedural)";
      } else {
        const pAnc = anc ? anc.nome : "Anc. Aleatória";
        const pCls = cls ? (con ? `${cls.nome} (${con.nome})` : cls.nome) : "Classe Aleatória";
        elCriacao.textContent = `${pAnc} • ${pCls}`;
      }
    }

    const elPer = document.getElementById("resumo-etapa-pericias");
    if (elPer) {
      if ((document.getElementById("modo-pericias")?.value || "procedural") !== "personalizado") {
        elPer.textContent = "Procedural";
      } else {
        const stPer = _calcularEstadoPericiasUI();
        if (!stPer.disponivel) {
          elPer.textContent = "Personalizado (aguardando classe)";
        } else {
          elPer.textContent = `Personalizado (${PER_ESTADO.selecionadas.length}/${stPer.vagasLivresTotal})`;
        }
      }
    }

    const elTal = document.getElementById("resumo-etapa-talentos");
    if (elTal) {
      if ((document.getElementById("modo-talentos")?.value || "procedural") !== "personalizado") {
        elTal.textContent = "Procedural";
      } else {
        const manuais = ["tal-ancestralidade", ...IDS_TAL_CLASSE, "tal-pericia-1", ...IDS_TAL_GERAIS].filter((id) => {
          const el = document.getElementById(id);
          return el && !el.disabled && !el.closest(".oculto") && el.value !== "procedural";
        }).length;
        elTal.textContent = manuais > 0 ? `Personalizado (${manuais} manual${manuais > 1 ? "is" : ""})` : "Personalizado (Procedural)";
      }
    }

    const elEq = document.getElementById("resumo-etapa-equipamentos");
    if (elEq) {
      if ((document.getElementById("modo-equipamentos")?.value || "procedural") !== "personalizado") {
        elEq.textContent = "Procedural (15 po)";
      } else {
        const orcPc = Number(OPCOES?.catalogo_equipamentos?.orcamento_inicial_pc || 1500);
        const gastoPc = _gastoManualEquipamentosPc();
        const saldoPc = orcPc - gastoPc;
        elEq.textContent = saldoPc >= 0
          ? `Personalizado • Saldo ${fmtPrecoEq(saldoPc)}`
          : `Excedido em ${fmtPrecoEq(Math.abs(saldoPc))}`;
      }
    }
  }

  async function gerarFichaAtual(forcarNovaSeed = false) {
    const form = document.getElementById("form-gerador");
    if (form && !form.checkValidity()) {
      alternarEtapaAcordeao("criacao", true);
      form.reportValidity();
      setStatus("Selecione uma divindade para esta classe antes de gerar a ficha.", "erro");
      return;
    }
    setStatus("Gerando ficha procedural...");
    const seedInput = document.getElementById("seed");
    const divSelect = document.getElementById("divindade");
    const nivelVal = document.getElementById("nivel").value;
    const ancId = document.getElementById("ancestralidade").value;
    const ancObj = OPCOES ? OPCOES.ancestralidades.find((a) => a.id === ancId) : null;
    const ancLivres = [document.getElementById("attr-anc-livre-1")?.value || "procedural"];
    if (ancObj && Number(ancObj.qtd_melhorias_livres || 1) >= 2) {
      ancLivres.push(document.getElementById("attr-anc-livre-2")?.value || "procedural");
    }

    const payload = {
      ancestralidade_id: ancId,
      heranca_id: document.getElementById("heranca").value,
      biografia_id: document.getElementById("biografia").value,
      divindade_id: divSelect ? divSelect.value : "",
      classe_id: document.getElementById("classe").value,
      conceito_id: document.getElementById("conceito").value,
      nivel: nivelVal === "aleatorio" ? "aleatorio" : Number(nivelVal || 1),
      nome_personagem: document.getElementById("nome").value,
      nome_jogador: document.getElementById("jogador").value,
      seed: forcarNovaSeed ? "" : seedInput.value,
      escolhas_atributos: {
        ancestralidade_livres: ancLivres,
        biografia_restrito: document.getElementById("attr-bio-restrito")?.value || "procedural",
        biografia_livre: document.getElementById("attr-bio-livre")?.value || "procedural",
        classe_chave: document.getElementById("attr-classe-chave")?.value || "procedural",
        livres_nivel_1: IDS_LIVRES_N1.map((id) => document.getElementById(id)?.value || "procedural"),
      },
      escolhas_pericias: _montarPayloadPericiasUI(),
      escolhas_talentos: _montarPayloadTalentosUI(),
      escolhas_equipamentos: _montarPayloadEquipamentosUI(),
    };

    try {
      const resp = await fetch("/api/gerar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const dados = await resp.json();
      if (!resp.ok) {
        setStatus(dados.erro || "Erro ao gerar ficha.", "erro");
        return;
      }
      seedInput.value = String(dados.meta_geracao.seed);
      ULTIMA_FICHA = dados;
      renderizarFicha(dados);
      setStatus(`Ficha gerada com sucesso (Seed ${dados.meta_geracao.seed}).`, "ok");
    } catch (err) {
      setStatus(`Falha na comunicação com o servidor: ${err.message}`, "erro");
    }
  }

  async function baixarExportacao(formato) {
    if (!ULTIMA_FICHA) return;
    setStatus(`Preparando arquivo .${formato.toUpperCase()}...`);
    try {
      const resp = await fetch(`/api/exportar/${formato}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ resultado: ULTIMA_FICHA }),
      });
      if (!resp.ok) {
        const err = await resp.json();
        setStatus(err.erro || `Erro ao exportar .${formato}.`, "erro");
        return;
      }
      const blob = await resp.blob();
      const disp = resp.headers.get("Content-Disposition") || "";
      const match = disp.match(/filename="([^"]+)"/);
      const nomeArquivo = match ? match[1] : `ficha_pf2e.${formato}`;

      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = nomeArquivo;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
      setStatus(`Download concluído: ${nomeArquivo}`, "ok");
    } catch (err) {
      setStatus(`Erro ao baixar .${formato}: ${err.message}`, "erro");
    }
  }

  function aplicarPreset(chave) {
    if (!OPCOES) return;
    if (chave === "mago") {
      document.getElementById("ancestralidade").value = "elfo";
      atualizarHerancas();
      document.getElementById("heranca").value = "elfo_vidente";
      document.getElementById("classe").value = "mago";
      atualizarConceitos();
      document.getElementById("conceito").value = "mago_evocador_artilharia";
    } else if (chave === "guerreiro") {
      document.getElementById("ancestralidade").value = "humano";
      atualizarHerancas();
      document.getElementById("heranca").value = "heranca_versatil";
      document.getElementById("classe").value = "guerreiro";
      atualizarConceitos();
      document.getElementById("conceito").value = "guerreiro_colosso_demolidor";
    }
    document.getElementById("biografia").value = "procedural";
    document.getElementById("nome").value = "";
    document.getElementById("seed").value = "";
    BIO_MANUAL_EXP_AUTOMATICA = false;
    definirModoTodosAtributos("procedural");
    resetarPericiasProcedural();
    resetarTalentosProcedural();
    resetarEquipamentosProcedural();
    atualizarResumoAncestralidade();
    atualizarSeletoresAtributosAncestralidade();
    atualizarResumoBiografia();
    atualizarSeletoresAtributosBiografia();
    atualizarResumoConceito();
    atualizarSeletoresAtributosClasse();
    atualizarCatalogoTalentosUI();
    gerarFichaAtual(true);
  }

  document.getElementById("modo-pericias")?.addEventListener("change", atualizarVisibilidadePericiasUI);
  ["per-bio-opcao", "per-cls-opcao", "per-div-opcao"].forEach((id) => {
    document.getElementById(id)?.addEventListener("change", atualizarCatalogoPericiasUI);
  });
  document.getElementById("grid-pericias-checkboxes")?.addEventListener("change", (e) => {
    const chk = e.target.closest('input[type="checkbox"][data-pericia-id]');
    if (!chk) return;
    const pid = chk.dataset.periciaId;
    const st = _calcularEstadoPericiasUI();
    if (!st.disponivel || st.fixasMap.has(pid)) return;
    if (chk.checked) {
      if (!PER_ESTADO.selecionadas.includes(pid) && PER_ESTADO.selecionadas.length < st.vagasLivresTotal) {
        PER_ESTADO.selecionadas.push(pid);
      }
    } else {
      PER_ESTADO.selecionadas = PER_ESTADO.selecionadas.filter((x) => x !== pid);
    }
    atualizarCatalogoPericiasUI();
  });
  document.getElementById("btn-per-reset-procedural")?.addEventListener("click", () => {
    resetarPericiasProcedural();
    const modoEl = document.getElementById("modo-pericias");
    if (modoEl) modoEl.value = "personalizado";
    atualizarVisibilidadePericiasUI();
  });

  document.getElementById("modo-talentos")?.addEventListener("change", atualizarVisibilidadeTalentosUI);
  document.getElementById("tal-ancestralidade")?.addEventListener("change", atualizarCatalogoTalentosUI);
  [...IDS_TAL_CLASSE, ...IDS_TAL_GERAIS].forEach((id) => {
    document.getElementById(id)?.addEventListener("change", () => {
      sincronizarExclusaoTalentos();
      atualizarCatalogoEquipamentosUI();
      atualizarResumosEtapasUI();
    });
  });
  document.getElementById("tal-pericia-1")?.addEventListener("change", atualizarResumosEtapasUI);
  document.getElementById("acordeao-etapas")?.addEventListener("click", (e) => {
    const btnToggle = e.target.closest("[data-etapa-toggle]");
    if (btnToggle) {
      alternarEtapaAcordeao(btnToggle.dataset.etapaToggle);
      return;
    }
    const btnIr = e.target.closest("[data-etapa-ir]");
    if (btnIr) {
      alternarEtapaAcordeao(btnIr.dataset.etapaIr, true);
      return;
    }
    const btnFechar = e.target.closest('[data-etapa-acao="fechar"]');
    if (btnFechar) {
      alternarEtapaAcordeao(null, false);
    }
  });
  document.getElementById("btn-tal-reset-procedural")?.addEventListener("click", () => {
    resetarTalentosProcedural();
    const modoEl = document.getElementById("modo-talentos");
    if (modoEl) modoEl.value = "personalizado";
    atualizarVisibilidadeTalentosUI();
  });

  ["modo-equipamentos", "eq-armadura", "eq-escudo", "eq-arma-cc-select", "eq-arma-dist-select", "eq-variado-select"].forEach(
    (id) => {
      document.getElementById(id)?.addEventListener("change", atualizarVisibilidadeEquipamentosUI);
    }
  );
  document.getElementById("eq-variado-qtd")?.addEventListener("input", atualizarOrcamentoEquipamentosUI);
  document.getElementById("btn-eq-reset-procedural")?.addEventListener("click", () => {
    resetarEquipamentosProcedural();
    document.getElementById("modo-equipamentos").value = "personalizado";
    atualizarVisibilidadeEquipamentosUI();
  });

  function _adicionarItemListaEq(tipo) {
    if (tipo === "cc" || tipo === "dist") {
      const selId = tipo === "cc" ? "eq-arma-cc-select" : "eq-arma-dist-select";
      const mapa = tipo === "cc" ? MAPA_EQ.armas_cc : MAPA_EQ.armas_dist;
      const lista = tipo === "cc" ? EQ_ESTADO.armas_cc : EQ_ESTADO.armas_dist;
      const sel = document.getElementById(selId);
      const item = mapa[sel?.value];
      if (!item) return;
      lista.push(item);
      if (sel) sel.value = "nenhuma";
    } else if (tipo === "var") {
      const sel = document.getElementById("eq-variado-select");
      const qtdEl = document.getElementById("eq-variado-qtd");
      const qtd = Math.max(1, parseInt(qtdEl?.value || "1", 10) || 1);
      const item = MAPA_EQ.variados[sel?.value];
      if (!item) return;
      const existente = EQ_ESTADO.variados.find((x) => x.id === item.id);
      if (existente) {
        existente.quantidade += qtd;
      } else {
        EQ_ESTADO.variados.push({ ...item, quantidade: qtd });
      }
      if (sel) sel.value = "nenhum";
      if (qtdEl) qtdEl.value = "1";
    }
    atualizarOrcamentoEquipamentosUI();
  }

  document.getElementById("btn-add-arma-cc")?.addEventListener("click", () => _adicionarItemListaEq("cc"));
  document.getElementById("btn-add-arma-dist")?.addEventListener("click", () => _adicionarItemListaEq("dist"));
  document.getElementById("btn-add-variado")?.addEventListener("click", () => _adicionarItemListaEq("var"));
  document.getElementById("btn-add-kit-av")?.addEventListener("click", () => {
    const orcPc = Number(OPCOES?.catalogo_equipamentos?.orcamento_inicial_pc || 1500);
    if (orcPc - _gastoManualEquipamentosPc() < 70) return;
    const kit = MAPA_EQ.variados.kit_de_aventureiro;
    if (!kit) return;
    const existente = EQ_ESTADO.variados.find((x) => x.id === "kit_de_aventureiro");
    if (existente) existente.quantidade += 1;
    else EQ_ESTADO.variados.push({ ...kit, quantidade: 1 });
    const sel = document.getElementById("eq-variado-select");
    if (sel && sel.value === "procedural") sel.value = "nenhum";
    atualizarOrcamentoEquipamentosUI();
  });

  document.getElementById("painel-equipamentos-custom")?.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-eq-rem]");
    if (!btn) return;
    const tipo = btn.dataset.eqRem;
    const idx = Number(btn.dataset.idx);
    if (tipo === "cc") EQ_ESTADO.armas_cc.splice(idx, 1);
    else if (tipo === "dist") EQ_ESTADO.armas_dist.splice(idx, 1);
    else if (tipo === "var") EQ_ESTADO.variados.splice(idx, 1);
    atualizarOrcamentoEquipamentosUI();
  });

  document.getElementById("btn-atb-todos-procedural").addEventListener("click", () => {
    definirModoTodosAtributos("procedural");
  });

  document.getElementById("btn-atb-todos-aleatorio").addEventListener("click", () => {
    definirModoTodosAtributos("aleatorio");
  });

  document.getElementById("form-gerador").addEventListener("submit", (e) => {
    e.preventDefault();
    gerarFichaAtual(false);
  });

  document.getElementById("btn-sortear").addEventListener("click", () => {
    document.getElementById("nome").value = "";
    gerarFichaAtual(true);
  });

  document.getElementById("btn-pdf").addEventListener("click", () => baixarExportacao("pdf"));
  document.getElementById("btn-docx").addEventListener("click", () => baixarExportacao("docx"));
  document.getElementById("btn-txt").addEventListener("click", () => baixarExportacao("txt"));
  document.getElementById("btn-imprimir").addEventListener("click", () => window.print());

  document.querySelectorAll(".aba-btn").forEach((btn) => {
    btn.addEventListener("click", () => aplicarAba(btn.dataset.aba));
  });

  document.querySelectorAll("[data-preset]").forEach((btn) => {
    btn.addEventListener("click", () => aplicarPreset(btn.dataset.preset));
  });

  inicializar();
})();
