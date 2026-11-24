(() => {
  "use strict";

  let ABA_ATIVA = "todas";
  let TEM_PAGINA_5 = false;

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
      "◆": "◆ 1 Ação",
      "2": "◆◆ 2 Ações",
      "◆◆": "◆◆ 2 Ações",
      "3": "◆◆◆ 3 Ações",
      "◆◆◆": "◆◆◆ 3 Ações",
      livre: "◇ Ação Livre",
      "◇": "◇ Ação Livre",
      reacao: "↺ Reação",
      "↺": "↺ Reação",
      "AÇÃO LIVRE": "◇ Ação Livre",
      "REAÇÃO": "↺ Reação",
    };
    return mapa[acoes] || esc(acoes || "—");
  }

  function renderSeloAcao(acoes) {
    const raw = String(acoes || "").trim().toLowerCase();
    let clsExtra = "";
    if (raw.includes("livre") || raw === "◇") clsExtra = " acao-livre";
    else if (raw.includes("rea") || raw === "↺") clsExtra = " acao-reacao";
    return `<span class="acao-selo${clsExtra}">${fmtAcaoIcone(acoes)}</span>`;
  }

  function renderBadgeTradicao(tradId, rotulo = null) {
    const chave = String(tradId || "").trim().toLowerCase();
    const validas = new Set(["arcana", "divina", "ocultista", "primal"]);
    const clsTrad = validas.has(chave) ? ` trad-${chave}` : "";
    return `<span class="trad-badge${clsTrad}">${esc(rotulo || tradId || "—")}</span>`;
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
    const rc = m.regras_casa || {};
    const levesPorVol = Number(m.itens_leves_por_volume || rc.itens_leves_por_volume || 10);
    const levesSoltos = Number(m.volume_leves_soltos || 0);
    const bannerRegrasCasa = rc.ativa && (rc.regras_ativas_resumo || []).length
      ? `<div class="banner-regras-casa-ficha"><strong>Regras da Casa Ativas:</strong> ${esc(rc.regras_ativas_resumo.join(" • "))}</div>`
      : "";
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
      bannerRegrasCasa +
      renderSecaoInv("Itens Vestidos", inv.itens_vestidos) +
      renderSecaoInv("Itens Preparados", inv.itens_preparados) +
      renderSecaoInv("Outros Itens", inv.outros_itens) +
      `<div><strong>Volume Total: ${esc(inv.volume_total)}</strong> (Leves soltos: ${esc(levesSoltos)}/${esc(levesPorVol)} L • Regra: ${esc(levesPorVol)} L = 1 Vol • Sobrecarregado = ${esc(inv.volume_sobrecarregado)} / Máximo = ${esc(inv.volume_maximo)})</div>` +
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
    const bioD = perf.dados_biograficos || {};
    const persD = perf.personalidade || {};
    const divDet = m.divindade_detalhes;
    const extrasBio = [
      ["Gênero / Pronomes", bioD.genero_pronomes],
      ["Etnia", bioD.etnia],
      ["Nacionalidade", bioD.nacionalidade],
      ["Altura", bioD.altura],
      ["Peso", bioD.peso],
      ["Aparência", bioD.aparencia],
      ["Crenças / Código", persD.crencas],
      ["Aversões / Anátemas", persD.aversoes],
    ]
      .filter(([, val]) => Boolean(String(val || "").trim()))
      .map(([rot, val]) => `<div><strong>${esc(rot)}:</strong> ${esc(val)}</div>`)
      .join("");

    document.getElementById("p3-perfil").innerHTML =
      `<div><strong>Idade Base:</strong> ${esc(bioD.idade || "—")}</div>` +
      extrasBio +
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
          ? `<div class="acao-card"><strong>${esc(a.nome)}</strong> ${renderSeloAcao(a.acoes)}<div>${(a.tracos || []).map((t) => `<span class="pill">${esc(t)}</span>`).join("")}</div><div class="slot-resumo">${esc(a.descricao)}</div></div>`
          : `<div class="acao-card vazio"><em>Espaço de ação livre</em></div>`
      )
      .join("");

    document.getElementById("p3-reacoes").innerHTML = f.acoes_livres_e_reacoes
      .map((a) =>
        a.nome
          ? `<div class="acao-card"><strong>${esc(a.nome)}</strong> ${renderSeloAcao(a.tipo)}` +
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
      const tradsIds = Object.entries(conj.tradicoes_marcadas)
        .filter(([, v]) => v)
        .map(([k]) => k);
      const tradsHtml = tradsIds.length
        ? tradsIds.map((k) => renderBadgeTradicao(k, k.toUpperCase())).join(" ")
        : `<span class="trad-badge">INATA / FOCO</span>`;
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
                `<div class="acao-card"><strong>${esc(s.nome)}</strong> ${renderSeloAcao(s.acoes || "—")} ${tagPrep}${tagFreq}` +
                `<div class="nota-campo">Comp: ${esc(comp || "—")}</div>` +
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
        renderCampo("Tradição & Estilo", `${tradsHtml} • ${esc(est)}`) +
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

    // Página 5 (Companheiro Animal / Familiar)
    const abaBtn5 = document.getElementById("aba-btn-companheiro");
    const pag5 = document.getElementById("pagina-companheiro");
    const p5Titulo = document.getElementById("p5-titulo");
    const p5Sub = document.getElementById("p5-subtitulo");
    const p5Conteudo = document.getElementById("p5-conteudo");
    TEM_PAGINA_5 = Boolean(comp);

    if (abaBtn5 && pag5 && p5Conteudo) {
      abaBtn5.classList.toggle("oculto", !TEM_PAGINA_5);
      pag5.hidden = !TEM_PAGINA_5;
      if (!TEM_PAGINA_5) {
        pag5.classList.add("oculto");
        p5Conteudo.innerHTML = "";
      } else {
        abaBtn5.textContent = `Pág. 5: ${comp.categoria}`;
        if (p5Titulo) p5Titulo.textContent = `${comp.categoria}: ${comp.nome}`;
        if (p5Sub) p5Sub.textContent = `Página 5 (Mestre: ${cab.nome_personagem} • Nível ${cab.nivel})`;

        if (comp.categoria === "Companheiro Animal") {
          const cardsStats = [
            ["PV Máx", comp.pv_max],
            ["CA", comp.ca],
            ["Fortitude", fmtMod(comp.fortitude)],
            ["Reflexos", fmtMod(comp.reflexos)],
            ["Vontade", fmtMod(comp.vontade)],
            ["Percepção", fmtMod(comp.percepcao)],
          ]
            .map(([rot, val]) => `<div class="comp-stat-box"><small>${esc(rot)}</small><strong>${esc(val)}</strong></div>`)
            .join("");

          const mods = comp.modificadores_atributo || {};
          const atbPills = [
            ["FOR", mods.forca],
            ["DES", mods.destreza],
            ["CON", mods.constituicao],
            ["INT", mods.inteligencia],
            ["SAB", mods.sabedoria],
            ["CAR", mods.carisma],
          ]
            .filter(([, v]) => v !== undefined)
            .map(([sig, v]) => `<span class="comp-atb-pill">${sig} ${fmtMod(v)}</span>`)
            .join("");

          const periciasHtml = (comp.pericias || [])
            .map((p) => `<span class="pill">${esc(p.nome)} ${fmtMod(p.total)}</span>`)
            .join("");

          const golpesHtml = (comp.ataques || [])
            .map((a) => {
              const tr = (a.tracos || []).map((t) => `<span class="pill">${esc(t)}</span>`).join("");
              return (
                `<div class="golpe-card">` +
                `<div class="golpe-topo"><span>${esc(a.nome)} ${renderSeloAcao(a.acoes)}</span><span class="golpe-atk">Ataque ${fmtMod(a.ataque_total)}</span></div>` +
                `<div class="golpe-det"><strong>Dano:</strong> ${esc(a.dano)}</div>` +
                (tr ? `<div>${tr}</div>` : "") +
                `</div>`
              );
            })
            .join("");

          const manDet = comp.manobra_avancada_detalhes || {};
          p5Conteudo.innerHTML =
            `<div class="p5-layout">` +
            `<div>` +
            `<div class="bloco"><h3 class="bloco-titulo">Combate &amp; Salvamentos</h3>` +
            `<div class="p5-stat-cards">${cardsStats}</div>` +
            `<div class="nota-campo"><strong>Estágio:</strong> ${esc(comp.estagio)} • <strong>Tamanho:</strong> ${esc(comp.tamanho)}</div>` +
            `<div class="nota-campo"><strong>Velocidade:</strong> ${esc(comp.velocidades)} • <strong>Sentidos:</strong> ${esc(comp.sentidos)}</div>` +
            (atbPills ? `<div style="margin-top:8px"><strong>Modificadores:</strong><div class="comp-atb-strip" style="margin-top:4px">${atbPills}</div></div>` : "") +
            `</div>` +
            `<div class="bloco"><h3 class="bloco-titulo">Perícias Treinadas</h3><div>${periciasHtml || "—"}</div></div>` +
            `<div class="bloco"><h3 class="bloco-titulo">Descrição</h3><div class="slot-resumo">${esc(comp.descricao)}</div></div>` +
            `</div>` +
            `<div>` +
            `<div class="bloco"><h3 class="bloco-titulo">Golpes &amp; Ataques</h3>${golpesHtml || "—"}</div>` +
            `<div class="bloco"><h3 class="bloco-titulo">Habilidades do Companheiro</h3>` +
            (comp.especial ? `<div style="margin-bottom:6px"><strong>Especial:</strong> ${esc(comp.especial)}</div>` : "") +
            `<div style="margin-bottom:6px"><strong>Benefício de Suporte:</strong> ${esc(comp.beneficio_de_suporte)}</div>` +
            `<div><strong>Manobra Avançada (${esc(comp.manobra_avancada)}${manDet.acoes ? ` ${renderSeloAcao(manDet.acoes)}` : ""}):</strong> ${esc(manDet.descricao || "Disponível quando evoluir para Ágil/Selvagem.")}</div>` +
            `</div>` +
            `</div>` +
            `</div>`;
        } else {
          const cardsFam = [
            ["PV Máx", comp.pv_max],
            ["CA (Mestre)", comp.ca],
            ["Fortitude", fmtMod(comp.fortitude)],
            ["Reflexos", fmtMod(comp.reflexos)],
            ["Vontade", fmtMod(comp.vontade)],
            ["Percepção", fmtMod(comp.percepcao)],
          ]
            .map(([rot, val]) => `<div class="comp-stat-box"><small>${esc(rot)}</small><strong>${esc(val)}</strong></div>`)
            .join("");

          const habsFamHtml = (comp.habilidades_selecionadas || [])
            .map(
              (h) =>
                `<div class="acao-card">` +
                `<strong>${esc(h.nome)}</strong> <span class="pill">${esc(h.tipo)}</span>` +
                `<div class="slot-resumo">${esc(h.descricao)}</div>` +
                `</div>`
            )
            .join("");

          p5Conteudo.innerHTML =
            `<div class="p5-layout">` +
            `<div>` +
            `<div class="bloco"><h3 class="bloco-titulo">Estatísticas Base do Familiar</h3>` +
            `<div class="p5-stat-cards">${cardsFam}</div>` +
            `<div class="nota-campo"><strong>Tamanho:</strong> ${esc(comp.tamanho)} • <strong>Velocidade:</strong> ${esc(comp.velocidade)}</div>` +
            `<div class="nota-campo"><strong>Sentidos:</strong> ${esc(comp.sentidos)}</div>` +
            `<div class="nota-campo" style="margin-top:6px"><strong>Testes Derivados:</strong> Acrobatismo ${fmtMod(comp.acrobatismo)} • Furtividade ${fmtMod(comp.furtividade)} • Outros testes ${fmtMod(comp.outros_testes)}</div>` +
            `</div>` +
            `</div>` +
            `<div>` +
            `<div class="bloco"><h3 class="bloco-titulo">Habilidades Diárias Selecionadas (${esc((comp.habilidades_selecionadas || []).length)} / ${esc(comp.habilidades_diarias_max)})</h3>` +
            `<div class="cards-acoes-grid">${habsFamHtml || "<em>Nenhuma habilidade selecionada</em>"}</div>` +
            `</div>` +
            `</div>` +
            `</div>`;
        }
      }
    }

    document.getElementById("json-bruto").textContent = JSON.stringify(res, null, 2);
    aplicarAba(!TEM_PAGINA_5 && ABA_ATIVA === "5" ? "todas" : ABA_ATIVA);
  }

  function aplicarAba(aba) {
    const alvo = aba === "5" && !TEM_PAGINA_5 ? "todas" : aba;
    ABA_ATIVA = alvo;
    document.querySelectorAll(".aba-btn").forEach((b) => {
      b.classList.toggle("ativa", b.dataset.aba === alvo);
    });
    document.querySelectorAll(".pagina-ficha").forEach((pag) => {
      if (pag.dataset.pagina === "5" && !TEM_PAGINA_5) {
        pag.classList.add("oculta");
        return;
      }
      const mostrar = alvo === "todas" || pag.dataset.pagina === alvo;
      pag.classList.toggle("oculta", !mostrar);
    });
  }

  window.PF2EFichaUI = {
    NOMES_ATRIBUTOS,
    esc,
    fmtMod,
    fmtAcaoIcone,
    renderSeloAcao,
    renderBadgeTradicao,
    renderTeml,
    renderizarFicha,
    aplicarAba,
  };
})();
