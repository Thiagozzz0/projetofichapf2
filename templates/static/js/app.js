(() => {
  "use strict";

  let OPCOES = null;
  let ULTIMA_FICHA = null;
  let ABA_ATIVA = "todas";

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

  function atualizarHerancas() {
    const ancId = document.getElementById("ancestralidade").value;
    const anc = OPCOES.ancestralidades.find((a) => a.id === ancId);
    const sel = document.getElementById("heranca");
    sel.innerHTML = "";
    (anc ? anc.herancas : []).forEach((h) => {
      const opt = document.createElement("option");
      opt.value = h.id;
      opt.textContent = h.nome;
      sel.appendChild(opt);
    });
    atualizarResumoAncestralidade();
  }

  function atualizarResumoAncestralidade() {
    const ancId = document.getElementById("ancestralidade").value;
    const herId = document.getElementById("heranca").value;
    const anc = OPCOES.ancestralidades.find((a) => a.id === ancId);
    const her = anc ? anc.herancas.find((h) => h.id === herId) : null;
    const el = document.getElementById("resumo-ancestralidade");
    if (!anc) {
      el.innerHTML = "";
      return;
    }
    const def = anc.defeito_atributo ? ` • Defeito: ${anc.defeito_atributo}` : "";
    el.innerHTML =
      `<strong>${esc(anc.nome)}${her ? " — " + esc(her.nome) : ""}</strong>` +
      `<div>PV Base: ${esc(anc.pontos_vida)} • Tamanho: ${esc(anc.tamanho)} • Vel: ${esc(anc.velocidade_m)}m</div>` +
      `<div>Melhorias: ${esc(anc.melhorias_atributo.join(", "))}${esc(def)}</div>` +
      (her ? `<div style="margin-top:4px">${esc(her.descricao)}</div>` : "");
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
    (cls ? cls.conceitos : []).forEach((c) => {
      const opt = document.createElement("option");
      opt.value = c.id;
      opt.textContent = `${c.nome} (${c.subclasse_oficial_nome})`;
      sel.appendChild(opt);
    });
    atualizarResumoConceito();
  }

  function atualizarResumoConceito() {
    const clsId = document.getElementById("classe").value;
    const conId = document.getElementById("conceito").value;
    const cls = OPCOES.classes.find((c) => c.id === clsId);
    const con = cls ? cls.conceitos.find((x) => x.id === conId) : null;
    const el = document.getElementById("resumo-conceito");
    if (!con) {
      el.innerHTML = "";
      return;
    }
    el.innerHTML =
      `<strong>${esc(con.titulo_completo)} (${esc(con.subclasse_oficial_nome)})</strong>` +
      `<div>PV/Nível: ${esc(cls.pontos_de_vida_por_nivel)} • Chave: ${esc(cls.atributo_chave.join(" / "))}</div>` +
      `<div style="margin-top:4px">${esc(con.resumo_proposta)}</div>`;
  }

  async function inicializar() {
    try {
      const resp = await fetch("/api/opcoes");
      OPCOES = await resp.json();

      const selAnc = document.getElementById("ancestralidade");
      OPCOES.ancestralidades.forEach((a) => {
        const opt = document.createElement("option");
        opt.value = a.id;
        opt.textContent = `${a.nome} (PV ${a.pontos_vida})`;
        selAnc.appendChild(opt);
      });

      const selBio = document.getElementById("biografia");
      const optAuto = document.createElement("option");
      optAuto.value = "procedural";
      optAuto.textContent = "Procedural (recomendada pelo conceito)";
      selBio.appendChild(optAuto);
      OPCOES.biografias.forEach((b) => {
        const opt = document.createElement("option");
        opt.value = b.id;
        opt.textContent = b.nome;
        selBio.appendChild(opt);
      });

      const selCls = document.getElementById("classe");
      OPCOES.classes.forEach((c) => {
        const opt = document.createElement("option");
        opt.value = c.id;
        opt.textContent = c.nome;
        selCls.appendChild(opt);
      });

      selAnc.addEventListener("change", atualizarHerancas);
      document.getElementById("heranca").addEventListener("change", atualizarResumoAncestralidade);
      selBio.addEventListener("change", atualizarResumoBiografia);
      selCls.addEventListener("change", atualizarConceitos);
      document.getElementById("conceito").addEventListener("change", atualizarResumoConceito);

      atualizarHerancas();
      atualizarResumoBiografia();
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
      renderCampo("Traços", (cab.tracos || []).map((t) => `<span class="pill">${esc(t)}</span>`).join(""), "span-3"),
      renderCampo("Divindade", esc(cab.divindade || "—"), "span-2"),
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

    document.getElementById("p1-ca").innerHTML =
      `<div class="ca-destaque">` +
      `<div class="escudo-ca"><small>CA</small><strong>${esc(ca.total)}</strong></div>` +
      `<div class="formula-ca">` +
      `<div><strong>10</strong> Base + <strong>${fmtMod(ca.des_ou_limite)}</strong> DES${ca.limite_des_armadura !== null ? ` (Lim +${ca.limite_des_armadura})` : ""} + <strong>${fmtMod(ca.proficiencia)}</strong> Prof ${renderTeml(ca.grau_proficiencia)} + <strong>+${esc(ca.item)}</strong> Item</div>` +
      `<div><strong>Armadura:</strong> ${esc(m.armadura_equipada)}</div>` +
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
    document.getElementById("p1-pv-percepcao").innerHTML =
      `<div class="stat-linha">` +
      `<div><strong>Pontos de Vida Máx:</strong> <span class="pv-badge">${esc(pv.max)}</span></div>` +
      `<div><strong>Percepção:</strong> <span class="pv-badge">${fmtMod(perc.total)}</span> ${renderTeml(perc.grau_proficiencia)}</div>` +
      `</div>` +
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
        ? `<ul class="slot-lista">${lista.map((it) => `<li class="slot-item">${esc(it.nome)}${it.quantidade > 1 ? ` ×${esc(it.quantidade)}` : ""} <span class="nota-campo" style="display:inline">(Vol ${esc(it.volume)})</span></li>`).join("")}</ul>`
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

    // Página 3
    document.getElementById("p3-rascunho").innerHTML =
      `<strong style="color:var(--accent);font-size:1.1rem">${esc(cab.nome_personagem)}</strong>` +
      `<div style="margin-top:6px;font-size:0.85rem">${esc(cab.ancestralidade_e_heranca)}</div>` +
      `<div style="font-size:0.85rem;color:var(--muted)">${esc(cab.classe)}</div>` +
      `<div style="margin-top:8px"><span class="pill">Nível ${esc(cab.nivel)}</span><span class="pill">${esc(cab.tamanho)}</span><span class="pill">${esc(cab.tendencia)}</span></div>`;

    const perf = f.perfil_e_campanha;
    document.getElementById("p3-perfil").innerHTML =
      `<div><strong>Idade Base:</strong> ${esc(perf.dados_biograficos.idade || "—")} anos</div>` +
      `<div style="margin-top:6px"><strong>Conceito &amp; Biografia:</strong> ${esc(perf.anotacoes_campanha.anotacoes || "—")}</div>`;

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
    setStatus("Gerando ficha procedural...");
    const seedInput = document.getElementById("seed");
    const payload = {
      ancestralidade_id: document.getElementById("ancestralidade").value,
      heranca_id: document.getElementById("heranca").value,
      biografia_id: document.getElementById("biografia").value,
      classe_id: document.getElementById("classe").value,
      conceito_id: document.getElementById("conceito").value,
      nivel: Number(document.getElementById("nivel").value || 1),
      nome_personagem: document.getElementById("nome").value,
      nome_jogador: document.getElementById("jogador").value,
      seed: forcarNovaSeed ? "" : seedInput.value,
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
      document.getElementById("conceito").value = "mago_elementalista";
    } else if (chave === "guerreiro") {
      document.getElementById("ancestralidade").value = "humano";
      atualizarHerancas();
      document.getElementById("heranca").value = "heranca_versatil";
      document.getElementById("classe").value = "guerreiro";
      atualizarConceitos();
      document.getElementById("conceito").value = "guerreiro_espada_duas_maos";
    }
    document.getElementById("biografia").value = "procedural";
    document.getElementById("nome").value = "";
    document.getElementById("seed").value = "";
    atualizarResumoAncestralidade();
    atualizarResumoBiografia();
    atualizarResumoConceito();
    gerarFichaAtual(true);
  }

  document.getElementById("form-gerador").addEventListener("submit", (e) => {
    e.preventDefault();
    gerarFichaAtual(false);
  });

  document.getElementById("btn-sortear").addEventListener("click", () => {
    document.getElementById("nome").value = "";
    gerarFichaAtual(true);
  });

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
