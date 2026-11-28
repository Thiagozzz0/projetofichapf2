(() => {
  "use strict";

  const app = window.PF2EApp;
  const { fmtMod, renderSeloAcao } = window.PF2EFichaUI;
  const { esc, CLASSES_CONJURADORAS_UI, IDS_TAL_CLASSE, IDS_TAL_GERAIS } = app;

  const TENDENCIAS_LABELS = [
    ["OB", "Ordeiro e Bom (OB)"],
    ["NB", "Neutro e Bom (NB)"],
    ["CB", "Caótico e Bom (CB)"],
    ["ON", "Ordeiro e Neutro (ON)"],
    ["N", "Neutro (N)"],
    ["CN", "Caótico e Neutro (CN)"],
    ["OM", "Ordeiro e Mau (OM)"],
    ["NM", "Neutro e Mau (NM)"],
    ["CM", "Caótico e Mau (CM)"],
  ];
  const TENDENCIAS_DRUIDA = new Set(["NB", "ON", "N", "CN", "NM"]);

  function _tendenciasPermitidasUI() {
    const clsId = document.getElementById("classe")?.value || "aleatorio";
    const conId = document.getElementById("conceito")?.value || "aleatorio";
    const divId = document.getElementById("divindade")?.value || "";
    const clsObj = app.opcoes?.classes?.find((c) => c.id === clsId) || null;
    const conObj = clsObj ? clsObj.conceitos.find((x) => x.id === conId) : null;
    const divObj = (app.opcoes?.divindades || []).find((d) => d.id === divId) || null;

    if (clsId === "campeao") {
      const subId = conObj?.subclasse_oficial_id || "";
      const mapaCausa = { paladino: "OB", redentor: "NB", libertador: "CB" };
      if (conId !== "aleatorio" && mapaCausa[subId]) {
        return {
          permitidas: new Set([mapaCausa[subId]]),
          nota: `Causa do Campeão (${conObj.subclasse_oficial_nome}) exige tendência ${mapaCausa[subId]}.`,
        };
      }
      return {
        permitidas: new Set(["OB", "NB", "CB"]),
        nota: "Campeão (Causas do Livro Básico) aceita OB, NB ou CB conforme a Causa.",
      };
    }

    if (clsId === "druida") {
      return {
        permitidas: TENDENCIAS_DRUIDA,
        nota: "Druida exige componente Neutro na tendência (NB, ON, N, CN ou NM).",
      };
    }

    if (clsId === "clerigo" && divObj?.tendencias_seguidores?.length) {
      return {
        permitidas: new Set(divObj.tendencias_seguidores),
        nota: `Clérigo de ${divObj.nome}: aceita ${divObj.tendencias_seguidores.join(", ")}.`,
      };
    }

    return {
      permitidas: new Set(TENDENCIAS_LABELS.map(([s]) => s)),
      nota: "Escolha livre ou deixe em Procedural para seguir o conceito.",
    };
  }

  function _detectarCompanheiroOuFamiliarUI() {
    const clsId = document.getElementById("classe")?.value || "aleatorio";
    const conId = document.getElementById("conceito")?.value || "aleatorio";
    const clsObj = app.opcoes?.classes?.find((c) => c.id === clsId) || null;
    const conObj = clsObj ? clsObj.conceitos.find((x) => x.id === conId) : null;
    const subId = conObj?.subclasse_oficial_id || "";
    const teseId = conObj?.tese_arcana_id || "";

    const modoTal = document.getElementById("modo-talentos")?.value || "procedural";
    let talAnc = "procedural";
    let talAdotado = null;
    let talsCls = [];
    if (modoTal === "personalizado") {
      const elAnc = document.getElementById("tal-ancestralidade");
      if (elAnc && !elAnc.disabled && !elAnc.closest(".oculto")) talAnc = elAnc.value;
      const temAdotada = (IDS_TAL_GERAIS || []).some((id) => {
        const el = document.getElementById(id);
        return el && !el.disabled && !el.closest(".oculto") && el.value === "ancestralidade_adotada";
      });
      if (temAdotada) talAdotado = app.talEstado?.talentoAdotadoId || null;
      talsCls = IDS_TAL_CLASSE.map((id) => {
        const el = document.getElementById(id);
        return el && !el.disabled && !el.closest(".oculto") ? el.value : "procedural";
      });
    }

    let tipo = null;
    let origem = "";

    if (clsId === "druida" && subId === "animais") {
      tipo = "companheiro_animal";
      origem = "Ordem dos Animais (Druida)";
    } else if (talsCls.includes("companheiro_animal")) {
      tipo = "companheiro_animal";
      origem = "Talento de Classe (Companheiro Animal)";
    } else if (clsId === "druida" && subId === "folha") {
      tipo = "familiar";
      origem = "Ordem da Folha (Familiar Leshy)";
    } else if (clsId === "mago" && teseId === "sintonizacao_com_familiar_aprimorada") {
      tipo = "familiar";
      origem = "Tese Arcana (Familiar Aprimorado)";
    } else if (talsCls.some((t) => t === "familiar" || t === "familiar_alquimico" || t === "familiar_leshy")) {
      tipo = "familiar";
      origem = "Talento de Classe (Familiar)";
    } else if (talAnc === "cumplice_animal") {
      tipo = "familiar";
      origem = "Talento Ancestral (Cúmplice Animal)";
    } else if (talAdotado === "cumplice_animal") {
      tipo = "familiar";
      origem = `Ancestralidade Adotada (${app.talEstado?.ancestralidadeAdotadaNome || "Gnomo"} • Cúmplice Animal)`;
    } else if (modoTal === "procedural" && conObj?.companheiro_padrao_conceito) {
      tipo = conObj.companheiro_padrao_conceito;
      origem = `Conceito (${conObj.nome})`;
    }

    const maxHabs = clsId === "mago" && teseId === "sintonizacao_com_familiar_aprimorada" ? 3 : 2;
    const possuiConjuracao = CLASSES_CONJURADORAS_UI.has(clsId);
    const possuiFoco =
      ["bardo", "campeao", "druida"].includes(clsId) ||
      (clsId === "clerigo" && subId === "sacerdote_enclausurado") ||
      (clsId === "mago" && subId !== "universalista") ||
      (clsId === "monge" && talsCls.some((t) => t === "golpe_de_ki" || t === "disparada_de_ki"));

    return { tipo, origem, clsId, maxHabs, possuiConjuracao, possuiFoco };
  }

  function _renderPreviewCompanheiroAnimal(tipoId) {
    const box = document.getElementById("desc-perfil-comp");
    if (!box) return;
    if (!tipoId || tipoId === "procedural" || tipoId === "aleatorio") {
      const msg =
        tipoId === "aleatorio"
          ? "Um dos 8 tipos de Companheiro Animal será sorteado ao gerar a ficha."
          : "O motor escolherá o Companheiro Animal de melhor sinergia com seu conceito/classe. Selecione um animal específico acima para visualizar todas as estatísticas de 1º nível.";
      box.innerHTML = `<div class="desc-preview-texto">${esc(msg)}</div>`;
      box.classList.remove("oculto");
      return;
    }
    const cat = app.opcoes?.catalogo_companheiros?.companheiros_animais || [];
    const comp = cat.find((t) => t.id === tipoId);
    if (!comp) {
      box.innerHTML = "";
      box.classList.add("oculto");
      return;
    }

    const statsCombate = [
      ["PV (N1)", comp.pv_n1],
      ["CA", comp.ca_n1],
      ["Fort", fmtMod(comp.fortitude_n1)],
      ["Ref", fmtMod(comp.reflexos_n1)],
      ["Von", fmtMod(comp.vontade_n1)],
      ["Percepção", fmtMod(comp.percepcao_n1)],
    ]
      .map(([rot, val]) => `<div class="comp-stat-box"><small>${esc(rot)}</small><strong>${esc(val)}</strong></div>`)
      .join("");

    const mods = comp.modificadores_atributo || {};
    const atbs = [
      ["FOR", mods.forca],
      ["DES", mods.destreza],
      ["CON", mods.constituicao],
      ["INT", mods.inteligencia],
      ["SAB", mods.sabedoria],
      ["CAR", mods.carisma],
    ]
      .map(([sig, v]) => `<span class="comp-atb-pill">${sig} ${fmtMod(v)}</span>`)
      .join("");

    const periciasStr = (comp.pericias_n1 || [])
      .map((p) => `${p.nome} ${fmtMod(p.total)}`)
      .join(", ");

    const pills = [
      `Tamanho: ${comp.tamanho}`,
      `Velocidade: ${comp.velocidades_texto}`,
      comp.sentidos ? `Sentidos: ${comp.sentidos}` : null,
      periciasStr ? `Perícias: ${periciasStr}` : null,
    ]
      .filter(Boolean)
      .map((p) => `<span class="desc-preview-pill">${esc(p)}</span>`)
      .join("");

    const ataquesHtml = (comp.ataques_n1 || [])
      .map((a) => {
        const tr = (a.tracos || []).length ? ` (${a.tracos.join(", ")})` : "";
        return (
          `<li><strong>${esc(a.nome)}</strong> ${renderSeloAcao(a.acoes)}: ` +
          `<strong>${fmtMod(a.ataque_total)}</strong> • ${esc(a.dano)}${esc(tr)}</li>`
        );
      })
      .join("");

    const man = comp.manobra_avancada || {};
    const manHtml = man.nome
      ? `<div class="desc-preview-conteudo"><strong>Manobra Avançada — ${esc(man.nome)} ${renderSeloAcao(man.acoes)}:</strong> ${esc(man.descricao)}</div>`
      : "";

    box.innerHTML =
      `<div class="desc-preview-topo"><span class="desc-preview-titulo">${esc(comp.nome)} (Jovem • ${esc(comp.tamanho)})</span></div>` +
      `<div class="comp-stats-grid">${statsCombate}</div>` +
      `<div class="comp-atb-strip">${atbs}</div>` +
      (pills ? `<div class="desc-preview-pills">${pills}</div>` : "") +
      (ataquesHtml ? `<ul class="comp-ataques-lista">${ataquesHtml}</ul>` : "") +
      (comp.especial ? `<div class="desc-preview-conteudo"><strong>Especial:</strong> ${esc(comp.especial)}</div>` : "") +
      `<div class="desc-preview-conteudo"><strong>Benefício de Suporte:</strong> ${esc(comp.beneficio_de_suporte)}</div>` +
      manHtml +
      `<div class="desc-preview-texto">${esc(comp.descricao)}</div>`;
    box.classList.remove("oculto");
  }

  function _motivoBloqueioHabilidadeFamiliar(hid, selecionadas, stComp) {
    if (hid === "bateria_de_magia") return "requer magias de 4º círculo";
    if (hid === "reagentes_extras" && stComp.clsId !== "alquimista") return "exclusiva de Alquimista";
    if (hid === "foco_de_familiar" && !stComp.possuiFoco) return "requer Reserva de Foco";
    if ((hid === "conexao_de_truque_magico" || hid === "transmitir_magia") && !stComp.possuiConjuracao) {
      return "requer conjuração";
    }
    if (hid === "assistente_de_laboratorio" && !selecionadas.includes("destreza_manual")) {
      return "requer Destreza Manual";
    }
    return null;
  }

  function atualizarPerfilUI() {
    if (!app.opcoes) return;

    // 1. Tendência permitida
    const selTend = document.getElementById("perfil-tendencia");
    const notaTend = document.getElementById("nota-perfil-tendencia");
    const { permitidas, nota } = _tendenciasPermitidasUI();
    if (selTend) {
      const ant = selTend.value || "procedural";
      selTend.innerHTML = `<option value="procedural">Procedural (conforme conceito / classe)</option>`;
      TENDENCIAS_LABELS.forEach(([sigla, rot]) => {
        const opt = document.createElement("option");
        opt.value = sigla;
        const ok = permitidas.has(sigla);
        opt.disabled = !ok;
        opt.textContent = ok ? rot : `${rot} (incompatível)`;
        selTend.appendChild(opt);
      });
      selTend.value = ant === "procedural" || permitidas.has(ant) ? ant : "procedural";
    }
    if (notaTend) notaTend.textContent = nota;

    // 2. Companheiro Animal ou Familiar
    const stComp = _detectarCompanheiroOuFamiliarUI();
    const cardComp = document.getElementById("card-perfil-companheiro");
    const tituloComp = document.getElementById("titulo-perfil-companheiro");
    const badgeComp = document.getElementById("badge-perfil-companheiro");
    const blocoAnimal = document.getElementById("bloco-perfil-comp-animal");
    const blocoFam = document.getElementById("bloco-perfil-familiar");

    if (!stComp.tipo) {
      cardComp?.classList.add("oculto");
      app.perfilEstado.familiarHabs = [];
    } else {
      cardComp?.classList.remove("oculto");
      if (badgeComp) badgeComp.textContent = stComp.origem;

      if (stComp.tipo === "companheiro_animal") {
        if (tituloComp) tituloComp.textContent = "Companheiro Animal";
        blocoAnimal?.classList.remove("oculto");
        blocoFam?.classList.add("oculto");

        const selTipo = document.getElementById("perfil-comp-tipo");
        const tipos = app.opcoes?.catalogo_companheiros?.companheiros_animais || [];
        if (selTipo && selTipo.options.length <= 2) {
          selTipo.innerHTML =
            `<option value="procedural">Procedural (melhor sinergia p/ conceito)</option>` +
            `<option value="aleatorio">Aleatório (sortear tipo)</option>`;
          tipos.forEach((t) => {
            const opt = document.createElement("option");
            opt.value = t.id;
            opt.textContent = `${t.nome} (${t.tamanho} • ${t.pericia})`;
            selTipo.appendChild(opt);
          });
        }
        _renderPreviewCompanheiroAnimal(selTipo?.value || "procedural");
      } else {
        if (tituloComp) tituloComp.textContent = "Familiar";
        blocoAnimal?.classList.add("oculto");
        blocoFam?.classList.remove("oculto");

        const elResumoFam = document.getElementById("resumo-stats-familiar");
        if (elResumoFam) {
          const nivelFam = app.obterNivelSelecionadoUI?.() || 1;
          const pvFam = 5 * nivelFam;
          elResumoFam.innerHTML =
            `<div class="desc-preview-topo"><span class="desc-preview-titulo">Estatísticas Base do Familiar (${nivelFam}º Nível)</span></div>` +
            `<div class="desc-preview-pills">` +
            `<span class="desc-preview-pill">Tamanho: Miúdo</span>` +
            `<span class="desc-preview-pill">PV: 5 / nível (${pvFam} no N${nivelFam})</span>` +
            `<span class="desc-preview-pill">CA &amp; Salvamentos: iguais aos do mestre</span>` +
            `<span class="desc-preview-pill">Velocidade: 7,5 m</span>` +
            `<span class="desc-preview-pill">Sentidos: Visão na Penumbra; empatia até 1,5 km</span>` +
            `</div>` +
            `<div class="desc-preview-texto">Testes de Percepção, Acrobatismo e Furtividade usam <strong>Nível + Mod. do Atributo-Chave</strong> do mestre (${stComp.maxHabs} habilidades diárias neste nível).</div>`;
        }

        const catFam = app.opcoes?.catalogo_companheiros || {};
        const todasHabs = [
          ...(catFam.habilidades_familiar || []),
          ...(catFam.habilidades_mestre || []),
        ];
        const idsValidos = new Set(todasHabs.map((h) => h.id));
        app.perfilEstado.familiarHabs = app.perfilEstado.familiarHabs
          .filter((id) => idsValidos.has(id) && !_motivoBloqueioHabilidadeFamiliar(id, app.perfilEstado.familiarHabs, stComp))
          .slice(0, stComp.maxHabs);

        const qtdSel = app.perfilEstado.familiarHabs.length;
        const cheio = qtdSel >= stComp.maxHabs;
        const elVagas = document.getElementById("perfil-fam-vagas");
        if (elVagas) {
          elVagas.textContent = `${qtdSel} / ${stComp.maxHabs} selecionada(s) — vagas vazias completam no procedural`;
        }

        const gridFam = document.getElementById("grid-perfil-familiar-habs");
        if (gridFam) {
          gridFam.innerHTML = todasHabs
            .map((h) => {
              const marcada = app.perfilEstado.familiarHabs.includes(h.id);
              const motivo = _motivoBloqueioHabilidadeFamiliar(h.id, app.perfilEstado.familiarHabs, stComp);
              const bloqueada = !marcada && (cheio || Boolean(motivo));
              const clsCard = `pericia-check-card${marcada ? " selecionada" : ""}${bloqueada ? " bloqueada" : ""}`;
              const subBadge = motivo
                ? `<span class="pericia-check-badge fixa">${esc(motivo)}</span>`
                : marcada
                  ? `<span class="pericia-check-badge manual">Escolhida</span>`
                  : `<span class="pericia-check-badge fixa">${h.tipo === "mestre" ? "Mestre" : "Familiar"}</span>`;
              return (
                `<label class="${clsCard}" title="${esc(h.descricao)}">` +
                `<input type="checkbox" data-fam-hab-id="${esc(h.id)}" ${marcada ? "checked" : ""} ${bloqueada ? "disabled" : ""}>` +
                `<span class="pericia-check-info">` +
                `<span class="pericia-check-titulo">${esc(h.nome)}</span>` +
                `${subBadge}` +
                `<span class="mag-card-resumo">${esc(h.descricao)}</span>` +
                `</span></label>`
              );
            })
            .join("");
        }
      }
    }

    app.atualizarResumosEtapasUI?.();
  }

  function resetarPerfilUI() {
    const setV = (id, v) => {
      const el = document.getElementById(id);
      if (el) el.value = v;
    };
    setV("perfil-tendencia", "procedural");
    ["perfil-idade", "perfil-genero", "perfil-etnia", "perfil-nacionalidade", "perfil-altura", "perfil-peso", "perfil-aparencia", "perfil-crencas", "perfil-aversoes", "perfil-comp-nome", "perfil-fam-nome"].forEach((id) => setV(id, ""));
    setV("perfil-comp-tipo", "procedural");
    app.perfilEstado.familiarHabs = [];
    atualizarPerfilUI();
  }

  function montarPayloadPerfilUI() {
    const val = (id) => (document.getElementById(id)?.value || "").trim();
    return {
      tendencia: document.getElementById("perfil-tendencia")?.value || "procedural",
      idade: val("perfil-idade"),
      genero_pronomes: val("perfil-genero"),
      etnia: val("perfil-etnia"),
      nacionalidade: val("perfil-nacionalidade"),
      altura: val("perfil-altura"),
      peso: val("perfil-peso"),
      aparencia: val("perfil-aparencia"),
      crencas: val("perfil-crencas"),
      aversoes: val("perfil-aversoes"),
    };
  }

  function montarPayloadCompanheiroUI() {
    const st = _detectarCompanheiroOuFamiliarUI();
    if (!st.tipo) return {};
    if (st.tipo === "companheiro_animal") {
      return {
        tipo_id: document.getElementById("perfil-comp-tipo")?.value || "procedural",
        nome: (document.getElementById("perfil-comp-nome")?.value || "").trim(),
      };
    }
    return {
      habilidades_ids: app.perfilEstado.familiarHabs.length ? [...app.perfilEstado.familiarHabs] : "procedural",
      nome: (document.getElementById("perfil-fam-nome")?.value || "").trim(),
    };
  }

  function registrarEventosPerfil() {
    ["perfil-tendencia", "perfil-comp-tipo"].forEach((id) => {
      document.getElementById(id)?.addEventListener("change", atualizarPerfilUI);
    });
    ["perfil-idade", "perfil-genero", "perfil-etnia", "perfil-nacionalidade", "perfil-altura", "perfil-peso", "perfil-aparencia", "perfil-crencas", "perfil-aversoes", "perfil-comp-nome", "perfil-fam-nome"].forEach((id) => {
      document.getElementById(id)?.addEventListener("input", () => app.atualizarResumosEtapasUI?.());
    });
    document.getElementById("grid-perfil-familiar-habs")?.addEventListener("change", (e) => {
      const chk = e.target.closest('input[type="checkbox"][data-fam-hab-id]');
      if (!chk) return;
      const hid = chk.dataset.famHabId;
      const stComp = _detectarCompanheiroOuFamiliarUI();
      if (!stComp.tipo || stComp.tipo !== "familiar") return;
      if (chk.checked) {
        if (!app.perfilEstado.familiarHabs.includes(hid) && app.perfilEstado.familiarHabs.length < stComp.maxHabs) {
          app.perfilEstado.familiarHabs.push(hid);
        }
      } else {
        app.perfilEstado.familiarHabs = app.perfilEstado.familiarHabs.filter((x) => x !== hid);
        // Se desmarcou Destreza Manual, remove Assistente de Laboratório dependente
        if (hid === "destreza_manual") {
          app.perfilEstado.familiarHabs = app.perfilEstado.familiarHabs.filter((x) => x !== "assistente_de_laboratorio");
        }
      }
      atualizarPerfilUI();
    });
  }

  Object.assign(app, {
    atualizarPerfilUI,
    resetarPerfilUI,
    montarPayloadPerfilUI,
    montarPayloadCompanheiroUI,
    registrarEventosPerfil,
  });
})();
