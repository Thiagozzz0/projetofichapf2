(() => {
  "use strict";

  const { ORDEM_ATRIBUTOS, fmtMod, escapeHtml } = window.CCApp;

  function fmtMov(m) {
    const n = Number(m) || 9;
    return Number.isInteger(n) ? `${n} m` : `${String(n).replace(".", ",")} m`;
  }

  function renderizarFichaCC(ficha) {
    const container = document.getElementById("cc-ficha-pronta");
    if (!container || !ficha) return;

    const cab = ficha.cabecalho;
    const attrBloco = ficha.atributos;
    const attrs = attrBloco.atributos;
    const comb = ficha.combate;
    const ca = comb.ca;
    const pv = comb.pv;
    const habs = ficha.habilidades;
    const eq = ficha.equipamentos;
    const sc = eq.sobrecarga;
    const moedas = eq.moedas_restantes;
    const magias = ficha.magias;
    const notas = ficha.notas || {};
    const avisos = ficha.avisos || [];

    const racaTxt = cab.linhagem_meio_elfo
      ? `${cab.raca_nome} (Linhagem ${cab.linhagem_meio_elfo.charAt(0).toUpperCase() + cab.linhagem_meio_elfo.slice(1)})`
      : cab.raca_nome;
    const proxExp = cab.prox_exp !== null && cab.prox_exp !== undefined ? cab.prox_exp : "Máx.";

    const attrHtml = ORDEM_ATRIBUTOS.map((k) => {
      const a = attrs[k];
      const bonusMe = a.bonus_extra_teste ? ` • +${a.bonus_extra_teste} teste` : "";
      return `
        <div class="cc-attr-linha-ficha">
          <span class="cc-bolinha${a.primario ? " cheia" : ""}" title="${a.primario ? "Atributo Primário (CB 12)" : "Atributo Secundário (CB 18)"}"></span>
          <strong>${escapeHtml(a.sigla)}</strong>
          <span><strong>${a.valor}</strong></span>
          <span>(${fmtMod(a.modificador)})</span>
          <small style="color: var(--cc-text-muted)">
            CB ${a.classe_base_siege}${escapeHtml(bonusMe)} — JP: ${escapeHtml((a.jogadas_protecao || []).join(", "))}
          </small>
        </div>
      `;
    }).join("");

    const pvPorNivelHtml = (pv.por_nivel || [])
      .map((p) => `<span class="cc-badge cc-badge-secundario">${p.nivel}º: <strong>${p.pv}</strong></span>`)
      .join(" ");

    const ataquesHtml =
      comb.ataques && comb.ataques.length
        ? `
          <table class="cc-tabela">
            <thead>
              <tr><th>Arma</th><th>BpA</th><th>Mod</th><th>Total</th><th>Dano</th><th>Alcance</th></tr>
            </thead>
            <tbody>
              ${comb.ataques
                .map(
                  (atq) => `
                  <tr>
                    <td><strong>${escapeHtml(atq.nome)}</strong></td>
                    <td>${fmtMod(atq.bpa)}</td>
                    <td>${fmtMod(atq.mod_ataque)}</td>
                    <td><strong>${fmtMod(atq.total_ataque)}</strong></td>
                    <td><strong>${escapeHtml(atq.total_dano)}</strong></td>
                    <td>${escapeHtml(atq.alcance)}</td>
                  </tr>
                `
                )
                .join("")}
            </tbody>
          </table>
        `
        : `<p class="cc-nota">Nenhuma arma equipada.</p>`;

    const habRacaHtml = (habs.raca || []).length
      ? `<ul class="cc-lista-limpa">${habs.raca
          .map((h) => `<li><strong>${escapeHtml(h.nome)}:</strong> ${escapeHtml(h.descricao)}</li>`)
          .join("")}</ul>`
      : `<p class="cc-nota">Nenhum traço racial registrado.</p>`;

    const habClasseHtml = (habs.classe || []).length
      ? `<ul class="cc-lista-limpa">${habs.classe
          .map((h) => `<li><strong>${escapeHtml(h.nome)} (${h.nivel}º):</strong> ${escapeHtml(h.resumo)}</li>`)
          .join("")}</ul>`
      : `<p class="cc-nota">Nenhuma habilidade de classe desbloqueada.</p>`;

    const itensHtml = (eq.todos_itens_resumo || []).length
      ? `<ul class="cc-lista-limpa">${eq.todos_itens_resumo
          .map((it) => `<li>${escapeHtml(it.nome)} <small>(SB ${it.sb}, ${escapeHtml(it.custo)})</small></li>`)
          .join("")}</ul>`
      : `<p class="cc-nota">Nenhum equipamento comprado.</p>`;

    let magiasHtml = "";
    if (magias && magias.conjurador) {
      const espacos = magias.espacos_por_circulo || {};
      const porCirc = magias.feiticos_por_circulo || {};
      const linhasMag = Object.keys(espacos)
        .sort((a, b) => Number(a) - Number(b))
        .map((circ) => {
          const info = espacos[circ];
          const lista = porCirc[circ] || [];
          const bonusTxt = info.bonus_atributo ? ` (+${info.bonus_atributo} bônus)` : "";
          const nomes = lista.length
            ? lista.map((f) => `${escapeHtml(f.nome)}${f.reversivel ? "*" : ""}`).join(", ")
            : "<em>(Nenhum feitiço selecionado)</em>";
          return `
            <tr>
              <td><strong>Nível ${escapeHtml(circ)}</strong></td>
              <td>${info.total}/dia${escapeHtml(bonusTxt)}</td>
              <td>${nomes}</td>
            </tr>
          `;
        })
        .join("");

      magiasHtml = `
        <div class="cc-secao-box">
          <h3>Feitiços Conhecidos / Preparados (${escapeHtml(String(magias.tradicao || "").toUpperCase())} — ${escapeHtml(String(magias.atributo_conjuracao || "").toUpperCase())} ${magias.valor_atributo_conjuracao})</h3>
          <table class="cc-tabela">
            <thead><tr><th>Círculo</th><th>Espaços</th><th>Feitiços</th></tr></thead>
            <tbody>${linhasMag}</tbody>
          </table>
        </div>
      `;
    }

    const avisosHtml = avisos.length
      ? `<div class="cc-status-msg aviso"><strong>Avisos:</strong><ul class="cc-lista-limpa">${avisos
          .map((a) => `<li>${escapeHtml(a)}</li>`)
          .join("")}</ul></div>`
      : "";

    container.innerHTML = `
      <div class="cc-ficha-toolbar nao-imprimir">
        <div>
          <strong>Ficha Pronta para Mesa e Exportação</strong>
          <div class="cc-nota">O método de criação dos atributos fica registrado no cabeçalho em todos os formatos.</div>
        </div>
        <div class="cc-ficha-export-acoes">
          <button type="button" id="btn-cc-export-pdf" class="cc-btn cc-btn-primario">📄 Baixar PDF Oficial</button>
          <button type="button" id="btn-cc-export-docx" class="cc-btn cc-btn-secundario">📝 Baixar DOCX</button>
          <button type="button" id="btn-cc-export-txt" class="cc-btn cc-btn-secundario">📃 Baixar TXT</button>
          <button type="button" id="btn-cc-imprimir" class="cc-btn cc-btn-secundario">🖨 Imprimir</button>
        </div>
      </div>

      <div class="cc-ficha-header">
        <div>
          <h2>${escapeHtml(cab.nome)}</h2>
          <div class="cc-nota">${escapeHtml(cab.titulos || "Aventureiro de Castles & Crusades")}${cab.jogador ? ` • Jogador: ${escapeHtml(cab.jogador)}` : ""}</div>
        </div>
        <span class="cc-metodo-pill">${escapeHtml(cab.rotulo_metodo)}</span>
      </div>

      <div class="cc-ficha-id-grid">
        <div class="cc-dado-cell"><small>Raça</small><strong>${escapeHtml(racaTxt)}</strong></div>
        <div class="cc-dado-cell"><small>Classe &amp; Nível</small><strong>${escapeHtml(cab.classe_nome)} — Nv. ${cab.nivel}</strong></div>
        <div class="cc-dado-cell"><small>Disposição</small><strong>${escapeHtml(cab.disposicao_nome)}</strong></div>
        <div class="cc-dado-cell"><small>Movimento</small><strong>${escapeHtml(fmtMov(cab.movimento_m))}</strong></div>
        <div class="cc-dado-cell"><small>Exp / Próx. Nível</small><strong>${cab.exp} / ${escapeHtml(String(proxExp))}</strong></div>
        <div class="cc-dado-cell"><small>Idiomas</small><strong>${escapeHtml((cab.idiomas || []).join(", "))}</strong></div>
      </div>

      <div class="cc-ficha-colunas">
        <div>
          <div class="cc-secao-box">
            <h3>Atributos &amp; Sistema SIEGE</h3>
            ${attrHtml}
          </div>

          <div class="cc-secao-box">
            <h3>Equipamentos &amp; Moedas</h3>
            <p class="cc-nota" style="margin-bottom: 8px">
              <strong>Sobrecarga:</strong> SB ${sc.sb_total} / CS ${sc.categoria_sobrecarga_cs} (<strong>${escapeHtml(sc.categoria_nome)}</strong>) — ${escapeHtml(sc.efeito)}
            </p>
            ${itensHtml}
            <p style="margin: 10px 0 0; font-size: 0.86rem">
              <strong>Moedas:</strong> ${moedas.ouro} po • ${moedas.prata} pp • ${moedas.cobre} pc
            </p>
          </div>
        </div>

        <div>
          <div class="cc-secao-box">
            <h3>Combate, CA &amp; Pontos de Vida</h3>
            <div class="cc-ficha-id-grid" style="margin-bottom: 10px">
              <div class="cc-dado-cell">
                <small>Classe de Armadura (CA)</small>
                <strong>${ca.total}</strong>
                <small style="text-transform:none">(10 + Arm ${ca.armadura} + Esc ${ca.escudo} + DES ${fmtMod(ca.mod_destreza)})</small>
              </div>
              <div class="cc-dado-cell">
                <small>Pontos de Vida (PV)</small>
                <strong>${pv.total} (${escapeHtml(pv.dado_vida)})</strong>
              </div>
              <div class="cc-dado-cell">
                <small>Bônus para Acertar (BpA)</small>
                <strong>${fmtMod(comb.bpa)}</strong>
              </div>
            </div>
            <p class="cc-nota" style="margin-bottom: 8px">
              <strong>Armadura:</strong> ${escapeHtml(ca.armadura_nome)} |
              <strong>Escudo:</strong> ${escapeHtml(ca.escudo_nome)} |
              <strong>Elmo:</strong> ${escapeHtml(ca.elmo_nome)}
            </p>
            <div style="margin-bottom: 10px; display: flex; flex-wrap: wrap; gap: 4px">${pvPorNivelHtml}</div>
            ${ataquesHtml}
          </div>

          <div class="cc-secao-box">
            <h3>Habilidades da Raça</h3>
            ${habRacaHtml}
          </div>

          <div class="cc-secao-box">
            <h3>Habilidades da Classe</h3>
            ${habClasseHtml}
          </div>

          ${magiasHtml}

          ${
            notas.anotacoes || (notas.itens_magicos && notas.itens_magicos.length) || (notas.pocoes && notas.pocoes.length)
              ? `<div class="cc-secao-box">
                  <h3>Itens Mágicos, Poções &amp; Anotações</h3>
                  ${notas.itens_magicos?.length ? `<p class="cc-nota"><strong>Itens Mágicos:</strong> ${escapeHtml(notas.itens_magicos.join(", "))}</p>` : ""}
                  ${notas.pocoes?.length ? `<p class="cc-nota"><strong>Poções:</strong> ${escapeHtml(notas.pocoes.join(", "))}</p>` : ""}
                  ${notas.anotacoes ? `<p class="cc-nota"><strong>Anotações:</strong> ${escapeHtml(notas.anotacoes)}</p>` : ""}
                </div>`
              : ""
          }
        </div>
      </div>

      ${avisosHtml}
    `;

    container.classList.remove("oculto");
  }

  window.CCApp.renderizarFichaCC = renderizarFichaCC;
})();
