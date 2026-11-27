"""Carregamento, cache, mesclagem modular de expansões e indexação dos JSONs de `dados/`."""

from __future__ import annotations

import json
import threading
from copy import deepcopy
from functools import cached_property
from pathlib import Path
from typing import Any, Iterable

from .util import normalizar, slugify

DIR_DADOS_PADRAO = Path(__file__).resolve().parent.parent / "dados"
SUBDIR_EXPANSOES = "expansoes"
FONTE_BASE_ID = "livro_basico"

_cache_lock = threading.Lock()
_cache_instancias: dict[tuple[Path, tuple[str, ...] | None], "BaseDados"] = {}


def _normalizar_chave_expansoes(
    expansoes_ativas: Iterable[str] | None,
) -> tuple[str, ...] | None:
    """Converte `expansoes_ativas` em tupla ordenada para chave de cache (`None` = padrão do manifest)."""
    if expansoes_ativas is None:
        return None
    vistos: list[str] = []
    for item in expansoes_ativas:
        exp_id = str(item or "").strip()
        if exp_id and exp_id not in vistos:
            vistos.append(exp_id)
    return tuple(vistos)


def listar_expansoes_disponiveis(diretorio: Path | str | None = None) -> list[dict[str, Any]]:
    """Descobre pacotes de expansão em `<dados>/expansoes/<id>/manifest.json` ordenados por `ordem` e `id`."""
    caminho_dados = Path(diretorio).resolve() if diretorio else DIR_DADOS_PADRAO
    dir_exp = caminho_dados / SUBDIR_EXPANSOES
    if not dir_exp.is_dir():
        return []

    encontradas: list[dict[str, Any]] = []
    for pasta in sorted(dir_exp.iterdir()):
        if not pasta.is_dir() or pasta.name.startswith(("_", ".")):
            continue
        manifest_path = pasta / "manifest.json"
        if not manifest_path.is_file():
            continue
        try:
            bruto = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(bruto, dict):
            continue
        exp_id = str(bruto.get("id") or pasta.name).strip()
        if not exp_id:
            continue
        encontradas.append(
            {
                "id": exp_id,
                "nome": str(bruto.get("nome") or exp_id),
                "sigla": str(bruto.get("sigla") or exp_id.upper()[:4]),
                "ativa": bool(bruto.get("ativa", True)),
                "ordem": int(bruto.get("ordem", 100)),
                "descricao": str(bruto.get("descricao") or ""),
                "diretorio": str(pasta),
            }
        )

    encontradas.sort(key=lambda e: (e["ordem"], e["id"]))
    return encontradas


def carregar_dados(
    diretorio: Path | str | None = None,
    expansoes_ativas: Iterable[str] | None = None,
) -> "BaseDados":
    """Retorna uma instância única (cacheada) da base de dados para o diretório e expansões informados.

    - `expansoes_ativas=None` (padrão): carrega Livro Básico + expansões com `"ativa": true` no `manifest.json`.
    - `expansoes_ativas=()` (vazio): carrega somente o Livro Básico.
    - `expansoes_ativas=("guia_avancado_jogador",)`: carrega Livro Básico + expansões selecionadas.
    """
    caminho = Path(diretorio).resolve() if diretorio else DIR_DADOS_PADRAO
    chave_exp = _normalizar_chave_expansoes(expansoes_ativas)
    chave_cache = (caminho, chave_exp)
    with _cache_lock:
        if chave_cache not in _cache_instancias:
            _cache_instancias[chave_cache] = BaseDados(caminho, expansoes_ativas=chave_exp)
        return _cache_instancias[chave_cache]


def limpar_cache_dados() -> None:
    """Limpa o cache em memória de `BaseDados` (útil em testes ou recarga de expansões)."""
    with _cache_lock:
        _cache_instancias.clear()


def _com_fonte(registro: dict[str, Any], fonte_id: str) -> dict[str, Any]:
    """Retorna cópia rasa garantindo o metadado `fonte` sem mutar o JSON bruto em cache."""
    if registro.get("fonte"):
        return dict(registro)
    copia = dict(registro)
    copia["fonte"] = fonte_id
    return copia


def _mesclar_por_id(
    lista_base: list[dict[str, Any]],
    lista_extra: list[dict[str, Any]],
    fonte_id: str,
) -> list[dict[str, Any]]:
    """Adiciona ou substitui itens por `id` preservando ordem determinística."""
    resultado = [dict(it) for it in lista_base]
    indice_por_id = {it["id"]: idx for idx, it in enumerate(resultado) if isinstance(it, dict) and "id" in it}
    for item in lista_extra:
        if not isinstance(item, dict):
            continue
        item_tag = _com_fonte(item, fonte_id)
        item_id = item_tag.get("id")
        if item_id and item_id in indice_por_id:
            resultado[indice_por_id[item_id]] = item_tag
        else:
            if item_id:
                indice_por_id[item_id] = len(resultado)
            resultado.append(item_tag)
    return resultado


class BaseDados:
    """Acesso somente-leitura, indexado e extensível às regras do Livro Básico e expansões."""

    def __init__(
        self,
        diretorio: Path,
        expansoes_ativas: tuple[str, ...] | None = None,
    ):
        self.diretorio = diretorio
        self._brutos: dict[Path, Any] = {}
        self._expansoes_disponiveis = listar_expansoes_disponiveis(diretorio)

        if expansoes_ativas is None:
            self._expansoes_carregadas = [e for e in self._expansoes_disponiveis if e["ativa"]]
        else:
            solicitadas = set(expansoes_ativas)
            self._expansoes_carregadas = [e for e in self._expansoes_disponiveis if e["id"] in solicitadas]

    # ------------------------------------------------------------------
    # Metadados de Expansões e Leitura Básica
    # ------------------------------------------------------------------
    @property
    def expansoes_disponiveis(self) -> list[dict[str, Any]]:
        """Metadados de todas as expansões encontradas em `dados/expansoes/`."""
        return [
            {k: v for k, v in e.items() if k != "diretorio"}
            for e in self._expansoes_disponiveis
        ]

    @property
    def expansoes_ativas(self) -> list[str]:
        """IDs das expansões atualmente mescladas nesta instância de `BaseDados`."""
        return [e["id"] for e in self._expansoes_carregadas]

    def _ler_json_caminho(self, caminho: Path) -> Any:
        if caminho not in self._brutos:
            with caminho.open("r", encoding="utf-8") as f:
                self._brutos[caminho] = json.load(f)
        return self._brutos[caminho]

    def json(self, nome_arquivo: str) -> Any:
        return self._ler_json_caminho(self.diretorio / nome_arquivo)

    def _arquivos_expansoes(self, padrao_glob: str) -> list[tuple[str, Any]]:
        """Retorna pares `(expansao_id, json_carregado)` para todos os arquivos que casam com `padrao_glob`."""
        pares: list[tuple[str, Any]] = []
        for exp in self._expansoes_carregadas:
            pasta = Path(exp["diretorio"])
            for arq in sorted(pasta.glob(padrao_glob)):
                if arq.is_file() and arq.name != "manifest.json":
                    pares.append((exp["id"], self._ler_json_caminho(arq)))
        return pares

    # ------------------------------------------------------------------
    # Ancestralidades, Heranças (Específicas + Versáteis), Biografias, Idiomas
    # ------------------------------------------------------------------
    @cached_property
    def ancestralidades(self) -> dict[str, dict]:
        resultado: dict[str, dict] = {}
        for a in self.json("ancestralidades_biografias.json")["ancestralidades"]:
            copia = deepcopy(a)
            copia.setdefault("fonte", FONTE_BASE_ID)
            for h in copia.get("herancas", []):
                h.setdefault("fonte", FONTE_BASE_ID)
            for t in copia.get("talentos_ancestrais", []):
                t.setdefault("fonte", FONTE_BASE_ID)
            resultado[copia["id"]] = copia

        for fonte_id, bruto in self._arquivos_expansoes("ancestralidades_biografias*.json"):
            for a in bruto.get("ancestralidades", []):
                copia = deepcopy(a)
                copia.setdefault("fonte", fonte_id)
                for h in copia.get("herancas", []):
                    h.setdefault("fonte", fonte_id)
                for t in copia.get("talentos_ancestrais", []):
                    t.setdefault("fonte", fonte_id)
                resultado[copia["id"]] = copia

            for anc_id, ext in (bruto.get("extensoes_ancestralidades") or {}).items():
                if anc_id not in resultado or not isinstance(ext, dict):
                    continue
                alvo = resultado[anc_id]
                if ext.get("herancas"):
                    alvo["herancas"] = _mesclar_por_id(alvo.get("herancas", []), ext["herancas"], fonte_id)
                if ext.get("talentos_ancestrais"):
                    alvo["talentos_ancestrais"] = _mesclar_por_id(
                        alvo.get("talentos_ancestrais", []),
                        ext["talentos_ancestrais"],
                        fonte_id,
                    )

        return resultado

    @cached_property
    def herancas_versateis(self) -> dict[str, dict]:
        """Heranças versáteis (ex.: Aasimar, Tiefling, Changeling, Dhampir) aplicáveis a qualquer ancestralidade."""
        resultado: dict[str, dict] = {}
        base = self.json("ancestralidades_biografias.json").get("herancas_versateis", [])
        for h in base:
            if isinstance(h, dict) and "id" in h:
                copia = deepcopy(h)
                copia.setdefault("fonte", FONTE_BASE_ID)
                copia.setdefault("versatil", True)
                resultado[copia["id"]] = copia

        for fonte_id, bruto in self._arquivos_expansoes("ancestralidades_biografias*.json"):
            for h in bruto.get("herancas_versateis", []):
                if isinstance(h, dict) and "id" in h:
                    copia = deepcopy(h)
                    copia.setdefault("fonte", fonte_id)
                    copia.setdefault("versatil", True)
                    resultado[copia["id"]] = copia
        return resultado

    @cached_property
    def talentos_mesticos(self) -> dict[str, list[dict]]:
        """Talentos de ancestralidade de meio-elfo, meio-orc e heranças versáteis (indexados pelo ID da herança)."""
        bruto = self.json("ancestralidades_biografias.json").get("herancas_mesticas_talentos", {})
        resultado: dict[str, list[dict]] = {
            k: [_com_fonte(t, FONTE_BASE_ID) for t in v]
            for k, v in bruto.items()
            if isinstance(v, list)
        }
        for fonte_id, exp_bruto in self._arquivos_expansoes("ancestralidades_biografias*.json"):
            extra = exp_bruto.get("herancas_mesticas_talentos") or {}
            for k, v in extra.items():
                if not isinstance(v, list):
                    continue
                resultado[k] = _mesclar_por_id(resultado.get(k, []), v, fonte_id)
            for h in exp_bruto.get("herancas_versateis", []):
                if isinstance(h, dict) and h.get("id") and isinstance(h.get("talentos_ancestrais"), list):
                    hid = h["id"]
                    resultado[hid] = _mesclar_por_id(resultado.get(hid, []), h["talentos_ancestrais"], fonte_id)
        return resultado

    @cached_property
    def biografias(self) -> dict[str, dict]:
        resultado: dict[str, dict] = {
            b["id"]: _com_fonte(b, FONTE_BASE_ID)
            for b in self.json("ancestralidades_biografias.json")["biografias"]["lista"]
        }
        for fonte_id, bruto in self._arquivos_expansoes("ancestralidades_biografias*.json"):
            bio_blk = bruto.get("biografias")
            lista = bio_blk.get("lista", []) if isinstance(bio_blk, dict) else (bio_blk or [])
            for b in lista:
                if isinstance(b, dict) and "id" in b:
                    resultado[b["id"]] = _com_fonte(b, fonte_id)
        return resultado

    @cached_property
    def idiomas(self) -> dict[str, Any]:
        """Catálogo de idiomas comuns e incomuns (Livro Básico + expansões)."""
        base = deepcopy(self.json("ancestralidades_biografias.json").get("idiomas", {}))
        comuns = list(base.get("tabela_2_1_idiomas_comuns", []))
        incomuns = list(base.get("tabela_2_2_idiomas_incomuns", []))
        nomes_comuns = {normalizar(i.get("idioma")) for i in comuns}
        nomes_incomuns = {normalizar(i.get("idioma")) for i in incomuns}

        for _, bruto in self._arquivos_expansoes("ancestralidades_biografias*.json"):
            extra = bruto.get("idiomas") or {}
            for item in extra.get("tabela_2_1_idiomas_comuns", []):
                chave = normalizar(item.get("idioma"))
                if chave and chave not in nomes_comuns:
                    nomes_comuns.add(chave)
                    comuns.append(dict(item))
            for item in extra.get("tabela_2_2_idiomas_incomuns", []):
                chave = normalizar(item.get("idioma"))
                if chave and chave not in nomes_incomuns:
                    nomes_incomuns.add(chave)
                    incomuns.append(dict(item))

        base["tabela_2_1_idiomas_comuns"] = comuns
        base["tabela_2_2_idiomas_incomuns"] = incomuns
        return base

    def heranca(self, ancestralidade_id: str, heranca_id: str) -> dict | None:
        anc = self.ancestralidades.get(ancestralidade_id)
        if not anc:
            return None
        encontrada = next((h for h in anc["herancas"] if h["id"] == heranca_id), None)
        if encontrada is not None:
            return encontrada
        return self.herancas_versateis.get(heranca_id)

    def herancas_disponiveis(self, ancestralidade_id: str, incluir_versateis: bool = True) -> list[dict]:
        """Retorna as heranças específicas da ancestralidade seguidas das heranças versáteis compatíveis."""
        anc = self.ancestralidades.get(ancestralidade_id)
        if not anc:
            return []
        lista = list(anc.get("herancas", []))
        if incluir_versateis and self.herancas_versateis:
            ids_existentes = {h["id"] for h in lista}
            for hv in self.herancas_versateis.values():
                if hv["id"] not in ids_existentes:
                    lista.append(hv)
        return lista

    # ------------------------------------------------------------------
    # Classes, Conceitos, Arquétipos
    # ------------------------------------------------------------------
    @cached_property
    def classes(self) -> dict[str, dict]:
        resultado: dict[str, dict] = {}
        arquivos_base = sorted(
            p.name for p in self.diretorio.glob("classes*.json") if p.is_file()
        )
        for arquivo in arquivos_base:
            for c in self.json(arquivo).get("classes", []):
                copia = deepcopy(c)
                copia.setdefault("fonte", FONTE_BASE_ID)
                resultado[copia["id"]] = copia

        for fonte_id, bruto in self._arquivos_expansoes("classes*.json"):
            for c in bruto.get("classes", []):
                copia = deepcopy(c)
                copia.setdefault("fonte", fonte_id)
                resultado[copia["id"]] = copia

            for cls_id, ext in (bruto.get("extensoes_classes") or {}).items():
                if cls_id not in resultado or not isinstance(ext, dict):
                    continue
                alvo = resultado[cls_id]
                if ext.get("subclasses_opcoes"):
                    sub_blk = alvo.setdefault("subclasses", {})
                    sub_blk["opcoes"] = _mesclar_por_id(
                        sub_blk.get("opcoes", []),
                        ext["subclasses_opcoes"],
                        fonte_id,
                    )
                if isinstance(ext.get("talentos_de_classe"), list):
                    alvo["talentos_de_classe"] = _mesclar_por_id(
                        alvo.get("talentos_de_classe", []),
                        ext["talentos_de_classe"],
                        fonte_id,
                    )
                if isinstance(ext.get("caracteristicas_de_classe"), list):
                    alvo["caracteristicas_de_classe"] = _mesclar_por_id(
                        alvo.get("caracteristicas_de_classe", []),
                        ext["caracteristicas_de_classe"],
                        fonte_id,
                    )

        return resultado

    def subclasse(self, classe_id: str, subclasse_id: str) -> dict | None:
        classe = self.classes.get(classe_id)
        if not classe:
            return None
        return next((o for o in classe["subclasses"]["opcoes"] if o["id"] == subclasse_id), None)

    @cached_property
    def conceitos(self) -> dict[str, dict]:
        resultado: dict[str, dict] = {
            c["id"]: _com_fonte(c, FONTE_BASE_ID)
            for c in self.json("conceitos_subclasses.json")["conceitos"]
        }
        for fonte_id, bruto in self._arquivos_expansoes("conceitos_subclasses*.json"):
            for c in bruto.get("conceitos", []):
                if isinstance(c, dict) and "id" in c:
                    resultado[c["id"]] = _com_fonte(c, fonte_id)
        return resultado

    def conceitos_da_classe(self, classe_id: str) -> list[dict]:
        return [c for c in self.conceitos.values() if c["classe_id"] == classe_id]

    @cached_property
    def arquetipos(self) -> dict[str, dict]:
        """Arquétipos de multiclasse e arquétipos de expansão (Livro Básico + expansões)."""
        resultado: dict[str, dict] = {}
        arq_base = self.diretorio / "arquetipos_multiclasse.json"
        if arq_base.is_file():
            for arq in self.json("arquetipos_multiclasse.json").get("arquetipos", []):
                if isinstance(arq, dict) and "id" in arq:
                    resultado[arq["id"]] = _com_fonte(arq, FONTE_BASE_ID)
        for fonte_id, bruto in self._arquivos_expansoes("arquetipos*.json"):
            for arq in bruto.get("arquetipos", []):
                if isinstance(arq, dict) and "id" in arq:
                    resultado[arq["id"]] = _com_fonte(arq, fonte_id)
        return resultado

    # ------------------------------------------------------------------
    # Perícias e Talentos
    # ------------------------------------------------------------------
    @cached_property
    def pericias(self) -> dict[str, dict]:
        resultado: dict[str, dict] = {
            p["id"]: _com_fonte(p, FONTE_BASE_ID)
            for p in self.json("pericias.json")["pericias"]
        }
        for fonte_id, bruto in self._arquivos_expansoes("pericias*.json"):
            for p in bruto.get("pericias", []):
                if isinstance(p, dict) and "id" in p:
                    resultado[p["id"]] = _com_fonte(p, fonte_id)
        return resultado

    @cached_property
    def pericias_por_nome(self) -> dict[str, str]:
        return {normalizar(p["nome"]): p["id"] for p in self.pericias.values()}

    def pericia_id(self, nome: str | None) -> str | None:
        if not nome:
            return None
        chave = normalizar(nome)
        if chave in self.pericias_por_nome:
            return self.pericias_por_nome[chave]
        slug = slugify(nome)
        return slug if slug in self.pericias else None

    @cached_property
    def talentos_gerais_pericia(self) -> dict[str, dict]:
        resultado: dict[str, dict] = {
            t["id"]: _com_fonte(t, FONTE_BASE_ID)
            for t in self.json("talentos.json")["talentos"]
        }
        for fonte_id, bruto in self._arquivos_expansoes("talentos*.json"):
            for t in bruto.get("talentos", []):
                if isinstance(t, dict) and "id" in t:
                    resultado[t["id"]] = _com_fonte(t, fonte_id)
        return resultado

    def resolver_talento_geral_pericia(self, nome: str | None) -> dict | None:
        """Resolve nomes como 'Certeza para Atletismo' ou 'Queda do Gato ou Salto Rápido' (primeira opção)."""
        if not nome:
            return None
        for candidato in self.opcoes_de_nome_talento(nome):
            talento = self.talentos_gerais_pericia.get(slugify(candidato))
            if talento:
                return talento
        return None

    @staticmethod
    def opcoes_de_nome_talento(nome: str) -> list[str]:
        """Separa 'A ou B' e remove complementos ('para X', '(X)')."""
        opcoes = []
        for parte in normalizar(nome).split(" ou "):
            parte = parte.split(" para ")[0]
            opcoes.append(parte)
        return opcoes

    # ------------------------------------------------------------------
    # Equipamentos
    # ------------------------------------------------------------------
    @cached_property
    def equipamentos(self) -> dict:
        extra_arquivos = self._arquivos_expansoes("equipamentos*.json")
        if not extra_arquivos:
            return self.json("equipamentos.json")

        base = deepcopy(self.json("equipamentos.json"))
        for fonte_id, bruto in extra_arquivos:
            if isinstance(bruto.get("armaduras"), dict) and bruto["armaduras"].get("itens"):
                base["armaduras"]["itens"] = _mesclar_por_id(
                    base["armaduras"]["itens"], bruto["armaduras"]["itens"], fonte_id
                )
            if isinstance(bruto.get("escudos"), dict) and bruto["escudos"].get("itens"):
                base["escudos"]["itens"] = _mesclar_por_id(
                    base["escudos"]["itens"], bruto["escudos"]["itens"], fonte_id
                )
            if isinstance(bruto.get("armas"), dict):
                for subchave in ("corpo_a_corpo", "distancia", "ataques_desarmados", "municoes"):
                    if bruto["armas"].get(subchave):
                        base["armas"][subchave] = _mesclar_por_id(
                            base["armas"].get(subchave, []),
                            bruto["armas"][subchave],
                            fonte_id,
                        )
            if bruto.get("kits_de_classe"):
                base["kits_de_classe"] = _mesclar_por_id(
                    base.get("kits_de_classe", []), bruto["kits_de_classe"], fonte_id
                )
            if isinstance(bruto.get("equipamentos_aventura"), dict) and bruto["equipamentos_aventura"].get("comuns"):
                base["equipamentos_aventura"]["comuns"] = _mesclar_por_id(
                    base["equipamentos_aventura"]["comuns"],
                    bruto["equipamentos_aventura"]["comuns"],
                    fonte_id,
                )
            if bruto.get("equipamentos_alquimicos"):
                alqs = base.setdefault("equipamentos_alquimicos", {})
                if isinstance(alqs, dict) and isinstance(bruto["equipamentos_alquimicos"], dict):
                    for k_alq, v_alq in bruto["equipamentos_alquimicos"].items():
                        if isinstance(v_alq, list):
                            alqs[k_alq] = _mesclar_por_id(alqs.get(k_alq, []), v_alq, fonte_id)
                        elif isinstance(v_alq, dict):
                            alqs.setdefault(k_alq, {}).update(v_alq)
        return base

    @cached_property
    def armaduras(self) -> dict[str, dict]:
        return {a["id"]: _com_fonte(a, FONTE_BASE_ID) for a in self.equipamentos["armaduras"]["itens"]}

    @cached_property
    def escudos(self) -> dict[str, dict]:
        return {s["id"]: _com_fonte(s, FONTE_BASE_ID) for s in self.equipamentos["escudos"]["itens"]}

    @cached_property
    def armas(self) -> dict[str, dict]:
        armas = {}
        for chave in ("corpo_a_corpo", "distancia"):
            for w in self.equipamentos["armas"][chave]:
                item = _com_fonte(w, FONTE_BASE_ID)
                item["tipo_ataque"] = chave
                armas[w["id"]] = item
        return armas

    @cached_property
    def ataques_desarmados(self) -> dict[str, dict]:
        return {w["id"]: _com_fonte(w, FONTE_BASE_ID) for w in self.equipamentos["armas"]["ataques_desarmados"]}

    @cached_property
    def municoes(self) -> list[dict]:
        return self.equipamentos["armas"]["municoes"]

    @cached_property
    def kits_de_classe(self) -> dict[str, dict]:
        return {k["id"]: _com_fonte(k, FONTE_BASE_ID) for k in self.equipamentos["kits_de_classe"]}

    @cached_property
    def itens_gerais(self) -> dict[str, dict]:
        """Equipamentos de aventura comuns + itens alquímicos com preço definido."""
        itens: dict[str, dict] = {}
        for item in self.equipamentos["equipamentos_aventura"]["comuns"]:
            itens[item["id"]] = _com_fonte(item, FONTE_BASE_ID)
        alquimicos = self.equipamentos.get("equipamentos_alquimicos")
        for item in _achatar_itens(alquimicos):
            if isinstance(item, dict) and "id" in item and item.get("preco_pc") is not None:
                itens.setdefault(item["id"], _com_fonte(item, FONTE_BASE_ID))
        return itens

    def resolver_item(self, nome: str) -> dict | None:
        """Resolve um nome livre de item ('arpéu', '2 bainhas', 'símbolo religioso (madeira)')."""
        for candidato in (slugify(nome, remover_parenteses=False), slugify(nome)):
            for variante in (candidato, candidato.rstrip("s"), candidato.replace("s_", "_")):
                if variante in self.itens_gerais:
                    return self.itens_gerais[variante]
                if variante in self.armas:
                    return self.armas[variante]
        return None

    # ------------------------------------------------------------------
    # Magias
    # ------------------------------------------------------------------
    @cached_property
    def magias(self) -> dict[str, dict]:
        magias: dict[str, dict] = {}
        arquivos_base = sorted(
            p.name for p in self.diretorio.glob("magias*.json") if p.is_file()
        )
        for arquivo in arquivos_base:
            for m in self.json(arquivo).get("magias", []):
                magias[m["id"]] = _com_fonte(m, FONTE_BASE_ID)

        for fonte_id, bruto in self._arquivos_expansoes("magias*.json"):
            for m in bruto.get("magias", []):
                if isinstance(m, dict) and "id" in m:
                    magias[m["id"]] = _com_fonte(m, fonte_id)
        return magias

    @cached_property
    def magias_foco(self) -> dict[str, dict]:
        foco: dict[str, dict] = {}
        arquivos_base = sorted(
            p.name for p in self.diretorio.glob("magias*.json") if p.is_file()
        )
        for arquivo in arquivos_base:
            bloco = self.json(arquivo).get("magias_de_foco")
            if isinstance(bloco, dict):
                for m in bloco.get("lista", []):
                    foco[m["id"]] = _com_fonte(m, FONTE_BASE_ID)

        for fonte_id, bruto in self._arquivos_expansoes("magias*.json"):
            bloco = bruto.get("magias_de_foco")
            lista = bloco.get("lista", []) if isinstance(bloco, dict) else (bloco or [])
            for m in lista:
                if isinstance(m, dict) and "id" in m:
                    foco[m["id"]] = _com_fonte(m, fonte_id)
        return foco

    @cached_property
    def regras_especificas(self) -> dict[str, Any]:
        nome = (
            "regras_especificas.json"
            if (self.diretorio / "regras_especificas.json").exists()
            else "regras_específicas.json"
        )
        return self.json(nome)

    @cached_property
    def companheiros_familiares(self) -> dict[str, Any]:
        extra_arquivos = self._arquivos_expansoes("companheiros_familiares*.json")
        if not extra_arquivos:
            return self.json("companheiros_familiares.json")

        base = deepcopy(self.json("companheiros_familiares.json"))
        for fonte_id, bruto in extra_arquivos:
            if isinstance(bruto.get("companheiros_animais"), dict):
                ca_base = base.setdefault("companheiros_animais", {})
                if bruto["companheiros_animais"].get("tipos"):
                    ca_base["tipos"] = _mesclar_por_id(
                        ca_base.get("tipos", []),
                        bruto["companheiros_animais"]["tipos"],
                        fonte_id,
                    )
            if isinstance(bruto.get("familiares"), dict):
                fam_base = base.setdefault("familiares", {})
                for subchave in ("habilidades_de_familiar", "habilidades_de_mestre"):
                    if bruto["familiares"].get(subchave):
                        fam_base[subchave] = _mesclar_por_id(
                            fam_base.get(subchave, []),
                            bruto["familiares"][subchave],
                            fonte_id,
                        )
        return base

    @cached_property
    def divindades(self) -> dict[str, dict]:
        resultado: dict[str, dict] = {
            d["id"]: _com_fonte(d, FONTE_BASE_ID)
            for d in self.json("divindades.json")["divindades"]
        }
        for fonte_id, bruto in self._arquivos_expansoes("divindades*.json"):
            for d in bruto.get("divindades", []):
                if isinstance(d, dict) and "id" in d:
                    resultado[d["id"]] = _com_fonte(d, fonte_id)
        return resultado

    @cached_property
    def dominios(self) -> dict[str, dict]:
        resultado: dict[str, dict] = {
            d["id"]: _com_fonte(d, FONTE_BASE_ID)
            for d in self.json("divindades.json")["dominios"]
        }
        for fonte_id, bruto in self._arquivos_expansoes("divindades*.json"):
            for d in bruto.get("dominios", []):
                if isinstance(d, dict) and "id" in d:
                    resultado[d["id"]] = _com_fonte(d, fonte_id)
        return resultado

    def resolver_magia(self, nome: str | None) -> dict | None:
        if not nome:
            return None
        return self.magias.get(slugify(nome))

    def resolver_magia_foco(self, nome: str | None) -> dict | None:
        if not nome:
            return None
        return self.magias_foco.get(slugify(nome))

    # ------------------------------------------------------------------
    # Ficha
    # ------------------------------------------------------------------
    @cached_property
    def estrutura_ficha(self) -> dict:
        return self.json("estrutura_ficha.json")


def _achatar_itens(no: Any) -> list:
    """Percorre estruturas aninhadas (dict/list) devolvendo todos os dicts com 'id'."""
    encontrados: list = []
    if isinstance(no, dict):
        if "id" in no and "nome" in no:
            encontrados.append(no)
        for valor in no.values():
            if isinstance(valor, (dict, list)):
                encontrados.extend(_achatar_itens(valor))
    elif isinstance(no, list):
        for valor in no:
            encontrados.extend(_achatar_itens(valor))
    return encontrados
