(() => {
  "use strict";

  let OPCOES = null;
  let ULTIMA_FICHA = null;
  let ABA_ATIVA = "todas";
  let BIO_MANUAL_EXP_AUTOMATICA = false;

  const NOMES_ATRIBUTOS = {
    for: ["FOR", "Força"],
    des: ["DES", "Destreza"],
    con: ["CON", "Constituição"],
    int: ["INT", "Inteligência"],
    sab: ["SAB", "Sabedoria"],
    car: ["CAR", "Carisma"],
  };

  function esc(valor) {
    if (valor === null || valor === undefined) return "";
    return String(valor)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function fmtMod(v) {
    const n = Number(v || 0);
    return n >= 0 ? `+${n}` : `${n}`;
  }

  function fmtAcaoIcone(acoes) {
    const mapa = {
      "1": "◆ 1 Ação",
      "2": "◆◆ 2 Ações",
      "3": "◆◆◆ 3 Ações",
      livre: "◇ Ação Livre",
      reacao: "↺ Reação",
      "AÇÃO LIVRE": "◇ Ação Livre",
      "REAÇÃO": "↺ Reação",
    };
    return mapa[acoes] || esc(acoes || "—");
  }

  function renderTeml(grau) {
    const sigla = {
      treinado: "T",
      especialista: "E",
      mestre: "M",
      lendario: "L",
    }[grau] || "";

    const itens = ["T", "E", "M", "L"].map(
      (letra) => `<span class="${letra === sigla ? "ativo" : ""}">${letra}</span>`
    );
    return `<span class="teml" title="${esc(grau || "destreinado")}">${itens.join("")}</span>`;
  }

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
      document.getElementById("heranca").addEventListener("change", atualizarResumoAncestralidade);
      selBio.addEventListener("change", () => {
        if (selBio.value !== "procedural" && selBio.value !== "aleatoria") {
          BIO_MANUAL_EXP_AUTOMATICA = false;
        }
        atualizarResumoBiografia();
        atualizarSeletoresAtributosBiografia();
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
      });

      IDS_LIVRES_N1.forEach((id) => {
        preencherSelectAtributo(document.getElementById(id), ORDEM_ATRIBUTOS, {
          textoProcedural: "Procedural (melhor p/ conceito)",
          textoAleatorio: "Aleatório (sortear distinto)",
          preservar: false,
        });
      });
      ["attr-anc-livre-1", "attr-anc-livre-2", "attr-bio-restrito", "attr-bio-livre", ...IDS_LIVRES_N1].forEach(
        (id) => {
          const el = document.getElementById(id);
          if (el) el.addEventListener("change", sincronizarExclusaoAtributos);
        }
      );

      atualizarHerancas();
      atualizarResumoBiografia();
      atualizarSeletoresAtributosBiografia();
      atualizarConceitos();
    } catch (err) {
      setStatus(`Erro ao carregar opções: ${err.message}`, "erro");
    }
  }

  function renderCampo(rotulo, valorHtml, spanClasse = "") {
    return `<div class="campo-ficha ${spanClasse}"><span class="rot">${esc(rotulo)}</span><span class="val">${valorHtml}</span></div>`;
  }

  function renderListaTalentos(slots, mostrarVazios) {
    return slots
      .map((s) => {
        const preenchido = s.nome && s.nome !== "—";
        if (!preenchido && !mostrarVazios) return "";
        return (
          `<li class="slot-item ${preenchido ? "" : "vazio"}">` +
          `<span class="slot-nivel-tag">${esc(s.rotulo_oficial)}</span> ` +
          `<strong>${esc(preenchido ? s.nome : "(espaço livre para progressão)")}</strong>` +
          (preenchido && s.origem_regra ? `<span class="slot-origem">${esc(s.origem_regra)}</span>` : "") +
          (preenchido && s.resumo ? `<span class="slot-resumo">${esc(s.resumo)}</span>` : "") +
          `</li>`
        );
      })
      .join("");
  }

  function renderGolpes(slots) {
    return slots
      .map((g) => {
        if (!g.arma) {
          return `<div class="golpe-card vazio"><div class="golpe-topo"><span>Slot de Ataque Livre</span></div></div>`;
        }
        const modDano = g.dano.for !== undefined ? g.dano.for : g.dano.especial || 0;
        const modTxt = modDano ? fmtMod(modDano) : "";
        const tipos = (g.dano.tipos_dano || []).join("/");
        const tracos = (g.dano.tracos || []).map((t) => `<span class="pill">${esc(t)}</span>`).join("");
        return (
          `<div class="golpe-card">` +
          `<div class="golpe-topo"><span>${esc(g.arma)}</span><span class="golpe-atk">Ataque ${fmtMod(g.ataque.total)} ${renderTeml(g.ataque.grau_proficiencia)}</span></div>` +
          `<div class="golpe-det"><strong>Dano:</strong> ${esc(g.dano.dados)}${esc(modTxt)} ${esc(tipos)} • <em>Atb ${fmtMod(g.ataque.mod_atributo)} + Prof ${fmtMod(g.ataque.proficiencia)}</em></div>` +
          `<div>${tracos}</div>` +
          `</div>`
        );
      })
      .join("");
  }

  function renderizarFicha(res) {
    ULTIMA_FICHA = res;
    const f = res.ficha;
    const m = res.meta_geracao;

    document.getElementById("area-ficha").hidden = false;
    document.getElementById("btn-pdf").disabled = false;
    document.getElementById("btn-docx").disabled = false;
    document.getElementById("btn-txt").disabled = false;
    document.getElementById("btn-imprimir").disabled = false;

    const cab = f.cabecalho;
    const heroPips = [1, 2, 3]
      .map((i) => `<span class="hero-pip ${i <= cab.pontos_heroismo ? "ativo" : ""}"></span>`)
      .join("");

    document.getElementById("p1-cabecalho").innerHTML = [
      renderCampo("Nome do Personagem", esc(cab.nome_personagem), "span-2"),
      renderCampo("Classe & Conceito", esc(cab.classe), "span-2"),
      renderCampo("Nível / XP", `Nível ${esc(cab.nivel)} • ${esc(cab.pontos_experiencia)} XP`),
      renderCampo("Pontos de Heroísmo", `<div class="heroismo-pontos">${heroPips}</div>`),
      renderCampo("Ancestralidade e Herança", esc(cab.ancestralidade_e_heranca), "span-2"),
      renderCampo("Biografia", `${esc(cab.biografia)} (${m.biografia_procedural ? "Procedural" : "Manual"})`, "span-2"),
      renderCampo("Tamanho / Tendência", `${esc(cab.tamanho)} • ${esc(cab.tendencia)}`),
      renderCampo("Nome do Jogador", esc(cab.nome_jogador || "—")),
      renderCampo("Traços", (cab.tracos || []).map((t) => `<span class="pill">${esc(t)}</span>`).join(""), "span-2"),
      renderCampo(
        "Subclasse PF2E",
        esc(
          (m.subclasse_oficial_nome || "—") +
            (m.tese_arcana_nome ? ` • Tese: ${m.tese_arcana_nome}` : "")
        ),
        "span-2"
      ),
      renderCampo("Divindade", esc(cab.divindade || "—")),
      renderCampo("Seed / Saldo", `${esc(m.seed)} • ${esc(m.saldo_restante)}`),
    ].join("");

    // Atributos
    document.getElementById("p1-atributos").innerHTML = Object.entries(NOMES_ATRIBUTOS)
      .map(([aid, [sigla, nome]]) => {
        const a = f.atributos[aid];
        return (
          `<div class="atributo-row">` +
          `<span class="atributo-sigla">${sigla}</span>` +
          `<span class="atributo-nome">${nome}</span>` +
          `<div class="caixa-numero"><small>Mod</small><strong>${fmtMod(a.modificador)}</strong></div>` +
          `<div class="caixa-numero"><small>Valor</small><strong>${esc(a.valor)}</strong></div>` +
          `</div>`
        );
      })
      .join("");

    document.getElementById("p1-abcd").innerHTML =
      `<strong>Composição ABCD:</strong>` +
      (m.historico_abcd || [])
        .map((et) => {
          const d = Object.entries(et.deltas).map(([k, v]) => `${k.toUpperCase()} ${fmtMod(v)}`).join(", ");
          return `<div><strong>[${esc(et.etapa)}]</strong> ${esc(et.origem)}: ${esc(d)}</div>`;
        })
        .join("");

    // CD e Velocidade
    document.getElementById("p1-cd-velocidade").innerHTML =
      `<div class="stat-linha">` +
      `<div><strong>CD de Classe:</strong> <span class="pv-badge">${esc(f.cd_classe.total)}</span> ${renderTeml(f.cd_classe.grau_proficiencia)}</div>` +
      `<div><strong>Velocidade:</strong> <span class="pv-badge">${esc(f.velocidade.metros)} m</span></div>` +
      `</div>` +
      (f.velocidade.tipos_movimento_anotacoes
        ? `<div class="nota-campo">${esc(f.velocidade.tipos_movimento_anotacoes)}</div>`
        : `<div class="nota-campo">Movimento terrestre padrão</div>`);

    // Proficiência com Armas
    document.getElementById("p1-prof-armas").innerHTML = f.proficiencia_armas
      .map((w) => `<div class="prof-item"><span>${esc(w.rotulo)}</span>${renderTeml(w.grau_proficiencia)}</div>`)
      .join("");

    // CA e Escudo
    const ca = f.classe_armadura;
    const escu = ca.escudo;
    const profArmHtml = Object.entries(ca.proficiencias_armadura)
      .map(([k, v]) => `<div class="prof-item"><span>${esc(k.replace("_", " ").toUpperCase())}</span>${renderTeml(v)}</div>`)
      .join("");

    const obsComb = m.observacoes_combate || {};
    const caEscudoTxt = obsComb.ca_com_escudo ? ` (${obsComb.ca_com_escudo} c/ Escudo)` : "";
    document.getElementById("p1-ca").innerHTML =
      `<div class="ca-destaque">` +
      `<div class="escudo-ca"><small>CA</small><strong>${esc(ca.total)}</strong></div>` +
      `<div class="formula-ca">` +
      `<div><strong>10</strong> Base + <strong>${fmtMod(ca.des_ou_limite)}</strong> DES${ca.limite_des_armadura !== null ? ` (Lim +${ca.limite_des_armadura})` : ""} + <strong>${fmtMod(ca.proficiencia)}</strong> Prof ${renderTeml(ca.grau_proficiencia)} + <strong>+${esc(ca.item)}</strong> Item${esc(caEscudoTxt)}</div>` +
      `<div><strong>Armadura:</strong> ${esc(m.armadura_equipada_resumo || m.armadura_equipada)}</div>` +
      (obsComb.nota_postura ? `<div class="nota-campo">${esc(obsComb.nota_postura)}</div>` : "") +
      `</div>` +
      `</div>` +
      `<div class="prof-tira">${profArmHtml}</div>` +
      (escu.nome
        ? `<div class="abcd-historico"><strong>Escudo:</strong> ${esc(escu.nome)} (+${esc(escu.bonus_ca)} CA ao Erguer • Dureza ${esc(escu.dureza)} • PV ${esc(escu.pv_max)} • LQ ${esc(escu.limiar_quebra)})</div>`
        : "");

    // Salvamentos
    const salv = f.jogadas_salvamento;
    const nomesSalv = { fortitude: "Fortitude (CON)", reflexos: "Reflexos (DES)", vontade: "Vontade (SAB)" };
    document.getElementById("p1-salvamentos").innerHTML =
      `<div class="salvamentos-grid">` +
      ["fortitude", "reflexos", "vontade"]
        .map((k) => {
          const s = salv[k];
          return (
            `<div class="salv-card">` +
            `<div class="rot">${nomesSalv[k]}</div>` +
            `<div class="num">${fmtMod(s.total)}</div>` +
            `<div class="det">Atb ${fmtMod(s.mod_atributo)} + Prof ${fmtMod(s.proficiencia)}</div>` +
            `${renderTeml(s.grau_proficiencia)}` +
            `</div>`
          );
        })
        .join("") +
      `</div>` +
      (salv.anotacoes ? `<div class="nota-campo" style="margin-top:6px"><strong>Anotações:</strong> ${esc(salv.anotacoes)}</div>` : "");

    // PV & Percepção
    const pv = f.pontos_vida;
    const perc = f.percepcao;
    const morrLim = m.limite_morrendo || 4;
    const cdRec = m.cd_recuperacao_base || 10;
    document.getElementById("p1-pv-percepcao").innerHTML =
      `<div class="stat-linha">` +
      `<div><strong>Pontos de Vida Máx:</strong> <span class="pv-badge">${esc(pv.max)}</span></div>` +
      `<div><strong>Percepção:</strong> <span class="pv-badge">${fmtMod(perc.total)}</span> ${renderTeml(perc.grau_proficiencia)}</div>` +
      `</div>` +
      (morrLim !== 4 || cdRec !== 10 ? `<div class="nota-campo"><strong>Morrendo Máx:</strong> ${esc(morrLim)} • <strong>CD Recuperação:</strong> ${esc(cdRec)} + Morrendo</div>` : "") +
      (pv.resistencias_e_imunidades ? `<div><strong>Resistências:</strong> ${esc(pv.resistencias_e_imunidades)}</div>` : "") +
      `<div class="nota-campo"><strong>Sentidos:</strong> ${esc((perc.sentidos || []).join(", ") || "Visão normal")}</div>`;

    // Golpes
    document.getElementById("p1-golpes-cc").innerHTML = renderGolpes(f.golpes_corpo_a_corpo);
    document.getElementById("p1-golpes-dist").innerHTML = renderGolpes(f.golpes_a_distancia);

    // 18 Perícias
    const linhasPer = f.pericias
      .map((p) => {
        const treinada = p.grau_proficiencia !== "destreinado";
        const rot = p.especializacao ? `${p.rotulo_oficial} (${p.especializacao})` : p.rotulo_oficial;
        const pen = p.penalidade_armadura ? ` ${p.penalidade_armadura}` : "";
        return (
          `<tr class="${treinada ? "treinada" : ""}">` +
          `<td>${esc(rot)}</td>` +
          `<td class="num">${fmtMod(p.total)}</td>` +
          `<td>${esc(p.atributo_chave.toUpperCase())} ${fmtMod(p.mod_atributo)}${esc(pen)}</td>` +
          `<td>${renderTeml(p.grau_proficiencia)}</td>` +
          `</tr>`
        );
      })
      .join("");
    document.getElementById("p1-pericias").innerHTML =
      `<table class="tabela-pericias">` +
      `<thead><tr><th>Perícia</th><th>Total</th><th>Atb/Arm</th><th>Prof</th></tr></thead>` +
      `<tbody>${linhasPer}</tbody></table>`;

    document.getElementById("p1-idiomas").innerHTML =
      (f.idiomas || []).map((id) => `<span class="pill">${esc(id)}</span>`).join("") || "—";

    // Página 2
    const hab = f.habilidades_e_talentos;
    document.getElementById("p2-tal-anc").innerHTML = renderListaTalentos(hab.ancestralidade, false);
    document.getElementById("p2-tal-per").innerHTML = renderListaTalentos(hab.pericia, false);
    document.getElementById("p2-tal-ger").innerHTML = renderListaTalentos(hab.gerais, true);
    document.getElementById("p2-tal-cls").innerHTML = renderListaTalentos(hab.classe, false);
    document.getElementById("p2-tal-bon").innerHTML = renderListaTalentos(hab.bonus, true);

    const inv = f.inventario;
    const pctVol = Math.min(100, Math.round((inv.volume_total / Math.max(1, inv.volume_maximo)) * 100));
    const sobre = inv.volume_total > inv.volume_sobrecarregado;
    const renderSecaoInv = (titulo, lista) =>
      `<div style="margin-bottom:8px"><strong>${titulo}:</strong>` +
      (lista.length
        ? `<ul class="slot-lista">${lista.map((it) => {
            const jaTemQtd = /\(Qtd:/.test(it.nome) || it.nome.includes(`(${it.quantidade})`);
            const qtdTxt = it.quantidade > 1 && !jaTemQtd ? ` ×${esc(it.quantidade)}` : "";
            return `<li class="slot-item">${esc(it.nome)}${qtdTxt} <span class="nota-campo" style="display:inline">(Vol ${esc(it.volume)})</span></li>`;
          }).join("")}</ul>`
        : `<div class="nota-campo">Nenhum item</div>`) +
      `</div>`;

    document.getElementById("p2-inventario").innerHTML =
      renderSecaoInv("Itens Vestidos", inv.itens_vestidos) +
      renderSecaoInv("Itens Preparados", inv.itens_preparados) +
      renderSecaoInv("Outros Itens", inv.outros_itens) +
      `<div><strong>Volume Total: ${esc(inv.volume_total)}</strong> (Sobrecarregado = ${esc(inv.volume_sobrecarregado)} / Máximo = ${esc(inv.volume_maximo)})</div>` +
      `<div class="barra-volume-track"><div class="barra-volume-fill ${sobre ? "alerta" : ""}" style="width:${pctVol}%"></div></div>` +
      `<div class="moedas-grid">` +
      `<div class="moeda-card"><small>PC</small><strong>${esc(inv.riqueza.pc)}</strong></div>` +
      `<div class="moeda-card"><small>PP</small><strong>${esc(inv.riqueza.pp)}</strong></div>` +
      `<div class="moeda-card"><small>PO</small><strong>${esc(inv.riqueza.po)}</strong></div>` +
      `<div class="moeda-card"><small>PL</small><strong>${esc(inv.riqueza.pl)}</strong></div>` +
      `</div>`;

    // Companheiro Animal ou Familiar (Página 2)
    const compWrap = document.getElementById("p2-companheiro-wrap");
    const compBox = document.getElementById("p2-companheiro");
    const comp = m.companheiro_ou_familiar;
    if (compWrap && compBox) {
      if (!comp) {
        compWrap.hidden = true;
        compBox.innerHTML = "";
      } else if (comp.categoria === "Companheiro Animal") {
        compWrap.hidden = false;
        const atks = (comp.ataques || [])
          .map((a) => `<li><strong>${esc(a.nome)}</strong> ${fmtMod(a.ataque_total)} • ${esc(a.dano)} (${esc((a.tracos || []).join(", "))})</li>`)
          .join("");
        const pers = (comp.pericias || []).map((p) => `${esc(p.nome)} ${fmtMod(p.total)}`).join(" • ");
        compBox.innerHTML =
          `<div><strong>${esc(comp.nome)}</strong> (${esc(comp.estagio)} • ${esc(comp.tamanho)})</div>` +
          `<div>PV <strong>${esc(comp.pv_max)}</strong> • CA <strong>${esc(comp.ca)}</strong> • Vel: ${esc(comp.velocidades)} • Perc ${fmtMod(comp.percepcao)}</div>` +
          `<div>Fort ${fmtMod(comp.fortitude)} • Ref ${fmtMod(comp.reflexos)} • Von ${fmtMod(comp.vontade)}</div>` +
          `<div class="nota-campo"><strong>Sentidos:</strong> ${esc(comp.sentidos)} • <strong>Perícias:</strong> ${pers}</div>` +
          `<ul class="slot-lista" style="margin-top:6px">${atks}</ul>` +
          `<div class="slot-resumo" style="margin-top:4px"><strong>Benefício de Suporte:</strong> ${esc(comp.beneficio_de_suporte)}</div>`;
      } else {
        compWrap.hidden = false;
        const habs = (comp.habilidades_selecionadas || [])
          .map((h) => `<li class="slot-item"><strong>${esc(h.nome)}</strong> <span class="slot-origem">${esc(h.tipo)}</span><span class="slot-resumo">${esc(h.descricao)}</span></li>`)
          .join("");
        compBox.innerHTML =
          `<div><strong>${esc(comp.nome)}</strong> (${esc(comp.tamanho)})</div>` +
          `<div>PV <strong>${esc(comp.pv_max)}</strong> • CA <strong>${esc(comp.ca)}</strong> • Vel: ${esc(comp.velocidade)}</div>` +
          `<div>Percepção / Acrobatismo / Furtividade: <strong>${fmtMod(comp.percepcao)}</strong> • Salvamentos: Fort ${fmtMod(comp.fortitude)}, Ref ${fmtMod(comp.reflexos)}, Von ${fmtMod(comp.vontade)}</div>` +
          `<div class="nota-campo"><strong>Sentidos:</strong> ${esc(comp.sentidos)}</div>` +
          `<ul class="slot-lista" style="margin-top:6px">${habs}</ul>`;
      }
    }

    // Página 3
    document.getElementById("p3-rascunho").innerHTML =
      `<strong style="color:var(--accent);font-size:1.1rem">${esc(cab.nome_personagem)}</strong>` +
      `<div style="margin-top:6px;font-size:0.85rem">${esc(cab.ancestralidade_e_heranca)}</div>` +
      `<div style="font-size:0.85rem;color:var(--muted)">${esc(cab.classe)}</div>` +
      `<div style="margin-top:8px"><span class="pill">Nível ${esc(cab.nivel)}</span><span class="pill">${esc(cab.tamanho)}</span><span class="pill">${esc(cab.tendencia)}</span></div>`;

    const perf = f.perfil_e_campanha;
    const divDet = m.divindade_detalhes;
    document.getElementById("p3-perfil").innerHTML =
      `<div><strong>Idade Base:</strong> ${esc(perf.dados_biograficos.idade || "—")} anos</div>` +
      `<div style="margin-top:6px"><strong>Conceito &amp; Biografia:</strong> ${esc(perf.anotacoes_campanha.anotacoes || "—")}</div>` +
      (divDet
        ? `<div class="abcd-historico" style="margin-top:8px">` +
          `<strong>Divindade: ${esc(divDet.nome)} (${esc(divDet.tendencia)})</strong> • Arma Favorecida: ${esc(divDet.arma_favorecida_nome)} • Domínios: ${esc((divDet.dominios || []).join(", "))}` +
          `<div><strong>Éditos:</strong> ${esc(divDet.editos)}</div>` +
          `<div><strong>Anátema:</strong> ${esc(divDet.anatema)}</div>` +
          `</div>`
        : "");

    document.getElementById("p3-acoes").innerHTML = f.acoes_e_atividades
      .map((a) =>
        a.nome
          ? `<div class="acao-card"><strong>${esc(a.nome)}</strong> <span class="pill">${fmtAcaoIcone(a.acoes)}</span><div>${(a.tracos || []).map((t) => `<span class="pill">${esc(t)}</span>`).join("")}</div><div class="slot-resumo">${esc(a.descricao)}</div></div>`
          : `<div class="acao-card vazio"><em>Espaço de ação livre</em></div>`
      )
      .join("");

    document.getElementById("p3-reacoes").innerHTML = f.acoes_livres_e_reacoes
      .map((a) =>
        a.nome
          ? `<div class="acao-card"><strong>${esc(a.nome)}</strong> <span class="pill">${fmtAcaoIcone(a.tipo)}</span>` +
            (a.acionamento ? `<div class="nota-campo"><strong>Acionamento:</strong> ${esc(a.acionamento)}</div>` : "") +
            `<div class="slot-resumo">${esc(a.descricao)}</div></div>`
          : `<div class="acao-card vazio"><em>Espaço de reação / ação livre</em></div>`
      )
      .join("");

    // Página 4
    const conj = f.conjuracao;
    const temMagia =
      Object.values(conj.tradicoes_marcadas).some(Boolean) ||
      conj.truques_magicos.some((s) => s.nome) ||
      conj.magias_foco.slots.some((s) => s.nome) ||
      conj.magias_inatas.some((s) => s.nome);

    const p4 = document.getElementById("p4-conteudo");
    if (!temMagia) {
      p4.innerHTML = `<div class="bloco"><em>Este personagem não possui conjuração de classe, foco ou magias inatas no 1º nível.</em></div>`;
    } else {
      const trads = Object.entries(conj.tradicoes_marcadas)
        .filter(([, v]) => v)
        .map(([k]) => k.toUpperCase())
        .join(", ") || "INATA / FOCO";
      const est = Object.entries(conj.estilo_conjuracao)
        .filter(([, v]) => v)
        .map(([k]) => k.toUpperCase())
        .join(", ") || "FOCO / INATA";

      const colsEspacos = Array.from({ length: 10 }, (_, i) => i + 1);
      const renderSlotsMagia = (titulo, lista, comPrep) => {
        const ativos = lista.filter((x) => x.nome);
        if (!ativos.length) return "";
        return (
          `<div class="bloco"><h3 class="bloco-titulo">${titulo}</h3><div class="magias-grid-2">` +
          ativos
            .map((s) => {
              const comp = (s.componentes || []).join(", ");
              const tagPrep = comPrep && s.preparada ? `<span class="pill">Preparada</span>` : "";
              const tagFreq = s.frequencia ? `<span class="pill">${esc(s.frequencia)}</span>` : "";
              return (
                `<div class="acao-card"><strong>${esc(s.nome)}</strong> ${tagPrep}${tagFreq}` +
                `<div class="nota-campo">Ações: ${esc(s.acoes || "—")} • Comp: ${esc(comp || "—")}</div>` +
                (s.anotacoes ? `<div class="slot-resumo">${esc(s.anotacoes)}</div>` : "") +
                `</div>`
              );
            })
            .join("") +
          `</div></div>`
        );
      };

      p4.innerHTML =
        `<div class="p4-topo">` +
        renderCampo("Ataque de Magia", `${fmtMod(conj.ataque_magia.total)} ${renderTeml(conj.ataque_magia.grau_proficiencia)}`) +
        renderCampo("CD de Magia", `${esc(conj.cd_magia.total)} ${renderTeml(conj.cd_magia.grau_proficiencia)}`) +
        renderCampo("Tradição & Estilo", `${esc(trads)} • ${esc(est)}`) +
        renderCampo("Nível de Truque / Pontos de Foco", `Truque ${esc(conj.nivel_truque)} • Foco ${esc(conj.magias_foco.pontos_foco.maximo)}`) +
        `</div>` +
        `<table class="espacos-tabela"><thead><tr><th>Espaços / Dia</th>${colsEspacos.map((n) => `<th>${n}º</th>`).join("")}</tr></thead>` +
        `<tbody><tr><td><strong>Por Dia</strong></td>${colsEspacos.map((n) => {
          const v = conj.espacos_magia_por_dia[String(n)] || 0;
          return `<td class="${v > 0 ? "ativo" : ""}">${v}</td>`;
        }).join("")}</tr></tbody></table>` +
        renderSlotsMagia("Truques Mágicos", conj.truques_magicos, false) +
        renderSlotsMagia("Magias de Foco", conj.magias_foco.slots, false) +
        renderSlotsMagia("Magias Inatas", conj.magias_inatas, false) +
        renderSlotsMagia("Magias de 1º Círculo", conj.magias, true);
    }

    document.getElementById("json-bruto").textContent = JSON.stringify(res, null, 2);
    aplicarAba(ABA_ATIVA);
  }

  function aplicarAba(aba) {
    ABA_ATIVA = aba;
    document.querySelectorAll(".aba-btn").forEach((b) => {
      b.classList.toggle("ativa", b.dataset.aba === aba);
    });
    document.querySelectorAll(".pagina-ficha").forEach((pag) => {
      const mostrar = aba === "todas" || pag.dataset.pagina === aba;
      pag.classList.toggle("oculta", !mostrar);
    });
  }

  async function gerarFichaAtual(forcarNovaSeed = false) {
    const form = document.getElementById("form-gerador");
    if (form && !form.reportValidity()) {
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
    atualizarResumoAncestralidade();
    atualizarSeletoresAtributosAncestralidade();
    atualizarResumoBiografia();
    atualizarSeletoresAtributosBiografia();
    atualizarResumoConceito();
    atualizarSeletoresAtributosClasse();
    gerarFichaAtual(true);
  }

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
