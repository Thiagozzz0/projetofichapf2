(() => {
  "use strict";

  const app = window.PF2EApp;
  const { renderizarFicha, aplicarAba } = window.PF2EFichaUI;
  const { ORDEM_ATRIBUTOS, IDS_LIVRES_N1, IDS_TAL_CLASSE, IDS_TAL_GERAIS, setStatus, fmtPrecoEq } = app;

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
      const mobile = window.matchMedia("(max-width: 640px)").matches;
      abriuCard.scrollIntoView({ behavior: "smooth", block: mobile ? "start" : "nearest" });
    }
  }

  function atualizarResumosEtapasUI() {
    if (!app.opcoes) return;
    const nivelVal = document.getElementById("nivel")?.value || "1";
    const ehRandNiv = app.ehNivelAleatorioUI?.() || false;
    const elCriacao = document.getElementById("resumo-etapa-criacao");
    if (elCriacao) {
      const ancId = document.getElementById("ancestralidade")?.value || "aleatorio";
      const clsId = document.getElementById("classe")?.value || "aleatorio";
      const conId = document.getElementById("conceito")?.value || "aleatorio";
      const anc = app.opcoes.ancestralidades.find((a) => a.id === ancId);
      const cls = app.opcoes.classes.find((c) => c.id === clsId);
      const con = cls ? cls.conceitos.find((x) => x.id === conId) : null;
      const prefixoNiv = ehRandNiv ? "N1–5 • " : nivelVal !== "1" ? `N${nivelVal} • ` : "";
      if (ancId === "aleatorio" && clsId === "aleatorio") {
        elCriacao.textContent = `${prefixoNiv}Aleatório (Procedural)`;
      } else {
        const pAnc = anc ? anc.nome : "Anc. Aleatória";
        const pCls = cls ? (con ? `${cls.nome} (${con.nome})` : cls.nome) : "Classe Aleatória";
        elCriacao.textContent = `${prefixoNiv}${pAnc} • ${pCls}`;
      }
    }

    const elPer = document.getElementById("resumo-etapa-pericias");
    if (elPer) {
      if ((document.getElementById("modo-pericias")?.value || "procedural") !== "personalizado") {
        elPer.textContent = "Procedural";
      } else {
        const stPer = app.calcularEstadoPericiasUI();
        const stIdm = app.calcularEstadoIdiomasUI?.();
        if (!stPer.disponivel && !stIdm?.disponivel) {
          elPer.textContent = "Personalizado (aguardando classe/ancestralidade)";
        } else {
          const txtPer = stPer.disponivel
            ? `${app.perEstado.selecionadas.length}/${stPer.vagasLivresTotal} per.`
            : "Perícias auto";
          const txtIdm = stIdm?.disponivel
            ? `${app.perEstado.idiomasExtras.length}/${stIdm.vagasExtras} idi.`
            : "Idiomas auto";
          elPer.textContent = `Personalizado (${txtPer} • ${txtIdm})`;
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

    const elMag = document.getElementById("resumo-etapa-magias");
    if (elMag) {
      const modoMag = document.getElementById("modo-magias")?.value || "procedural";
      if (modoMag === "procedural") {
        elMag.textContent = "Procedural";
      } else if (modoMag === "aleatorio") {
        elMag.textContent = "Aleatório";
      } else {
        const stMag = app.calcularEstadoMagiasUI?.();
        if (!stMag || !stMag.disponivel) {
          elMag.textContent = "Manual (aguardando linhagem)";
        } else {
          const partesMag = [`T:${app.magEstado.truques.length}/${stMag.vagasLivresTruques}`, `N1:${app.magEstado.magias_n1.length}/${stMag.vagasLivresN1}`];
          if ((stMag.espacosPorCirculo?.[2] || 0) > 0) {
            partesMag.push(`N2:${app.magEstado.magias_n2.length}/${stMag.vagasLivresPorCirculo[2]}`);
          }
          if ((stMag.espacosPorCirculo?.[3] || 0) > 0) {
            partesMag.push(`N3:${app.magEstado.magias_n3.length}/${stMag.vagasLivresPorCirculo[3]}`);
          }
          elMag.textContent = `Manual (${partesMag.join(" • ")})`;
        }
      }
    }

    const elEq = document.getElementById("resumo-etapa-equipamentos");
    if (elEq) {
      if ((document.getElementById("modo-equipamentos")?.value || "procedural") !== "personalizado") {
        if (ehRandNiv) {
          elEq.textContent = "Procedural (por nível)";
        } else {
          const orcPc = app.obterOrcamentoAtualPc?.() || 1500;
          const poTot = Math.round(orcPc / 100);
          elEq.textContent = `Procedural (${poTot} po)`;
        }
      } else {
        const orcPc = app.obterOrcamentoAtualPc?.() || 1500;
        const gastoPc = app.gastoManualEquipamentosPc();
        const saldoPc = orcPc - gastoPc;
        elEq.textContent = saldoPc >= 0
          ? `Personalizado • Saldo ${fmtPrecoEq(saldoPc)}`
          : `Excedido em ${fmtPrecoEq(Math.abs(saldoPc))}`;
      }
    }
  }

  async function inicializar() {
    try {
      const resp = await fetch("/api/opcoes");
      app.opcoes = await resp.json();

      const selAnc = document.getElementById("ancestralidade");
      const optAncRand = document.createElement("option");
      optAncRand.value = "aleatorio";
      optAncRand.textContent = "Aleatória (sortear ancestralidade)";
      selAnc.appendChild(optAncRand);
      app.opcoes.ancestralidades.forEach((a) => {
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
      app.opcoes.biografias.forEach((b) => {
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
      app.opcoes.classes.forEach((c) => {
        const opt = document.createElement("option");
        opt.value = c.id;
        opt.textContent = c.nome;
        selCls.appendChild(opt);
      });
      selCls.value = "aleatorio";

      selAnc.addEventListener("change", app.atualizarHerancas);
      document.getElementById("heranca").addEventListener("change", () => {
        app.atualizarResumoAncestralidade();
        app.atualizarCatalogoTalentosUI();
      });
      selBio.addEventListener("change", () => {
        if (selBio.value !== "procedural" && selBio.value !== "aleatoria") {
          app.bioManualExpAutomatica = false;
        }
        app.atualizarResumoBiografia();
        app.atualizarSeletoresAtributosBiografia();
        app.atualizarCatalogoTalentosUI();
      });
      document.getElementById("btn-bio-atb-opcional")?.addEventListener("click", () => {
        app.bioManualExpAutomatica = true;
        app.atualizarSeletoresAtributosBiografia();
      });
      selCls.addEventListener("change", app.atualizarConceitos);
      document.getElementById("conceito").addEventListener("change", () => {
        app.atualizarResumoConceito();
        app.atualizarDivindades();
        app.atualizarSeletoresAtributosClasse();
        app.atualizarCatalogoTalentosUI();
      });
      document.getElementById("divindade")?.addEventListener("change", () => {
        app.atualizarCatalogoPericiasUI();
        app.atualizarCatalogoMagiasUI();
        app.atualizarCatalogoEquipamentosUI();
        app.atualizarPerfilUI();
      });
      document.getElementById("nivel")?.addEventListener("change", () => {
        app.atualizarCatalogoEquipamentosUI();
        app.atualizarCatalogoMagiasUI();
        app.atualizarCatalogoTalentosUI();
        app.atualizarCatalogoPericiasUI();
        app.atualizarPerfilUI();
        app.atualizarPreviaAtributosABCD?.();
        atualizarResumosEtapasUI();
      });

      IDS_LIVRES_N1.forEach((id) => {
        app.preencherSelectAtributo(document.getElementById(id), ORDEM_ATRIBUTOS, {
          textoProcedural: "Procedural (melhor p/ conceito)",
          textoAleatorio: "Aleatório (sortear distinto)",
          preservar: false,
        });
      });
      ["attr-anc-livre-1", "attr-anc-livre-2", "attr-bio-restrito", "attr-bio-livre", "attr-classe-chave", ...IDS_LIVRES_N1].forEach(
        (id) => {
          document.getElementById(id)?.addEventListener("change", () => {
            app.sincronizarExclusaoAtributos();
            app.atualizarCatalogoPericiasUI();
          });
        }
      );

      app.atualizarHerancas();
      app.atualizarResumoBiografia();
      app.atualizarSeletoresAtributosBiografia();
      app.atualizarConceitos();
      app.inicializarRegrasCasaUI?.();
      app.inicializarCatalogoEquipamentosUI();
      app.atualizarCatalogoTalentosUI();
      app.atualizarVisibilidadeTalentosUI();
      app.atualizarCatalogoPericiasUI();
      app.atualizarVisibilidadePericiasUI();
      app.atualizarCatalogoMagiasUI();
      app.atualizarVisibilidadeMagiasUI();
      app.atualizarPerfilUI();
      app.atualizarPreviaAtributosABCD?.();
    } catch (err) {
      setStatus(`Erro ao carregar opções: ${err.message}`, "erro");
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
    const ancObj = app.opcoes ? app.opcoes.ancestralidades.find((a) => a.id === ancId) : null;
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
      escolhas_pericias: app.montarPayloadPericiasUI(),
      escolhas_talentos: app.montarPayloadTalentosUI(),
      escolhas_magias: app.montarPayloadMagiasUI(),
      escolhas_equipamentos: app.montarPayloadEquipamentosUI(),
      escolhas_perfil: app.montarPayloadPerfilUI(),
      escolhas_companheiro: app.montarPayloadCompanheiroUI(),
      escolhas_regras_casa: app.montarPayloadRegrasCasaUI?.() || { modo: "regras_da_casa" },
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
      app.ultimaFicha = dados;
      renderizarFicha(dados);
      setStatus(`Ficha gerada com sucesso (Seed ${dados.meta_geracao.seed}).`, "ok");
      if (window.matchMedia("(max-width: 640px)").matches) {
        document.getElementById("area-ficha")?.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    } catch (err) {
      setStatus(`Falha na comunicação com o servidor: ${err.message}`, "erro");
    }
  }

  function mostrarOverlayDownload(ativo) {
    const overlay = document.getElementById("overlay-download");
    const txt = document.getElementById("overlay-download-texto");
    if (txt) txt.textContent = "Processando seu arquivo";
    if (overlay) {
      overlay.hidden = !ativo;
      overlay.classList.toggle("oculto", !ativo);
    }
    ["btn-pdf", "btn-docx", "btn-txt"].forEach((id) => {
      const btn = document.getElementById(id);
      if (btn) btn.disabled = ativo || !app.ultimaFicha;
    });
  }

  async function baixarExportacao(formato) {
    if (!app.ultimaFicha) return;
    setStatus(`Preparando arquivo .${formato.toUpperCase()}...`);
    mostrarOverlayDownload(true);
    try {
      const resp = await fetch(`/api/exportar/${formato}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ resultado: app.ultimaFicha }),
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
    } finally {
      mostrarOverlayDownload(false);
    }
  }

  function limparFormularioUI({ silencioso = false } = {}) {
    if (!app.opcoes) return;
    document.getElementById("ancestralidade").value = "aleatorio";
    document.getElementById("biografia").value = "procedural";
    document.getElementById("classe").value = "aleatorio";
    document.getElementById("nivel").value = "1";
    document.getElementById("nome").value = "";
    document.getElementById("jogador").value = "";
    document.getElementById("seed").value = "";
    app.bioManualExpAutomatica = false;
    app.atualizarHerancas();
    app.atualizarResumoBiografia();
    app.atualizarSeletoresAtributosBiografia();
    app.atualizarConceitos();
    app.definirModoTodosAtributos("procedural");
    app.resetarPericiasProcedural();
    app.resetarTalentosProcedural();
    app.resetarMagiasProcedural();
    app.resetarEquipamentosProcedural();
    app.resetarPerfilUI();
    app.atualizarPreviaAtributosABCD?.();
    if (!silencioso) {
      setStatus("Formulário restaurado para o padrão inicial.", "ok");
    }
  }

  function aplicarPreset(chave) {
    if (!app.opcoes) return;
    if (chave === "aleatorio") {
      limparFormularioUI({ silencioso: true });
      gerarFichaAtual(true);
      return;
    }
    if (chave === "mago") {
      document.getElementById("ancestralidade").value = "elfo";
      app.atualizarHerancas();
      document.getElementById("heranca").value = "elfo_vidente";
      document.getElementById("classe").value = "mago";
      app.atualizarConceitos();
      document.getElementById("conceito").value = "mago_evocador_artilharia";
    } else if (chave === "guerreiro") {
      document.getElementById("ancestralidade").value = "humano";
      app.atualizarHerancas();
      document.getElementById("heranca").value = "heranca_versatil";
      document.getElementById("classe").value = "guerreiro";
      app.atualizarConceitos();
      document.getElementById("conceito").value = "guerreiro_colosso_demolidor";
    }
    document.getElementById("biografia").value = "procedural";
    document.getElementById("nome").value = "";
    document.getElementById("seed").value = "";
    app.bioManualExpAutomatica = false;
    app.definirModoTodosAtributos("procedural");
    app.resetarPericiasProcedural();
    app.resetarTalentosProcedural();
    app.resetarMagiasProcedural();
    app.resetarEquipamentosProcedural();
    app.resetarPerfilUI();
    app.atualizarResumoAncestralidade();
    app.atualizarSeletoresAtributosAncestralidade();
    app.atualizarResumoBiografia();
    app.atualizarSeletoresAtributosBiografia();
    app.atualizarResumoConceito();
    app.atualizarSeletoresAtributosClasse();
    app.atualizarCatalogoTalentosUI();
    app.atualizarPreviaAtributosABCD?.();
    gerarFichaAtual(true);
  }

  Object.assign(app, {
    alternarEtapaAcordeao,
    atualizarResumosEtapasUI,
    gerarFichaAtual,
    baixarExportacao,
    limparFormularioUI,
    aplicarPreset,
  });

  app.registrarEventosPericias();
  app.registrarEventosTalentos();
  app.registrarEventosMagias();
  app.registrarEventosEquipamentos();
  app.registrarEventosPerfil();

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

  document.getElementById("btn-atb-todos-procedural")?.addEventListener("click", () => {
    app.definirModoTodosAtributos("procedural");
  });
  document.getElementById("btn-atb-todos-aleatorio")?.addEventListener("click", () => {
    app.definirModoTodosAtributos("aleatorio");
  });

  document.getElementById("form-gerador")?.addEventListener("submit", (e) => {
    e.preventDefault();
    gerarFichaAtual(false);
  });
  document.getElementById("btn-sortear")?.addEventListener("click", () => {
    document.getElementById("nome").value = "";
    gerarFichaAtual(true);
  });

  document.getElementById("btn-pdf")?.addEventListener("click", () => baixarExportacao("pdf"));
  document.getElementById("btn-docx")?.addEventListener("click", () => baixarExportacao("docx"));
  document.getElementById("btn-txt")?.addEventListener("click", () => baixarExportacao("txt"));
  document.getElementById("btn-imprimir")?.addEventListener("click", () => window.print());

  document.querySelectorAll(".aba-btn").forEach((btn) => {
    btn.addEventListener("click", () => aplicarAba(btn.dataset.aba, { porUsuario: true }));
  });
  document.getElementById("btn-mobile-gerar")?.addEventListener("click", () => gerarFichaAtual(false));
  document.getElementById("btn-mobile-sortear")?.addEventListener("click", () => {
    document.getElementById("nome").value = "";
    gerarFichaAtual(true);
  });
  document.getElementById("btn-mobile-ir-ficha")?.addEventListener("click", () => {
    document.getElementById("area-ficha")?.scrollIntoView({ behavior: "smooth", block: "start" });
  });
  document.getElementById("btn-mobile-topo")?.addEventListener("click", () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
  document.querySelectorAll("[data-preset]").forEach((btn) => {
    btn.addEventListener("click", () => aplicarPreset(btn.dataset.preset));
  });
  document.getElementById("btn-limpar-form")?.addEventListener("click", () => limparFormularioUI());

  inicializar();
})();
