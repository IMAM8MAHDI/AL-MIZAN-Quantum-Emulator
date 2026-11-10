# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""REDACTION — ce qui est intelligible est mesuré, pas décrété.

Ce que le dépôt contenait déjà, et d'où part ce dossier
-------------------------------------------------------
Vingt et une pages sont publiées en trois langues par `ABONDANCE/moteur_page_trilingue.py`
(7 trios FR/EN/AR : agriculture, eau, électricité, index d'ABONDANCE, chiffres, fondation, index
de FONDATION). Le moteur traduit les titres, les formules et les libellés de statut. Une seule
ligne du corps de table ne se traduisait pas, et c'est la seule qui porte les nombres vérifiables :

    ligne = e["resultat"] if lang == "fr" else eq_texte(e["id"], 1)

Conséquence mesurée avant ce dossier : sur 89 lignes d'équation, la page anglaise ne portait les
nombres de la ligne calculée française que sur 56 lignes, la page arabe sur 55 — quand ces nombres
n'étaient pas d'avance cités dans la phrase traduite. Un lecteur non francophone lisait donc une
traduction sans les valeurs que le contrôle a produites, sur un tiers des lignes environ. Le
garde-fou existant, `verifier_nombres`, va dans l'autre sens : il refuse un nombre énoncé par un
traducteur qui ne figure dans aucun calcul ; il n'a jamais exigé qu'un nombre calculé apparaisse.

Ce que ce module fait, dans l'ordre
-----------------------------------
  1. il inventorie le corpus réellement publié (EQ-01) et son squelette (EQ-02) ;
  2. il sépare ce qui est déjà neutre en langue — les classes de statut (EQ-03), le chemin
     machine (EQ-04) — de ce qui ne l'est pas ;
  3. il mesure le déficit numérique (EQ-05, par ablation confrontée à la révision scellée), la
     correction appliquée au moteur (EQ-06) et l'identité de la ligne calculée entre les trois
     langues (EQ-07), et il dit de combien l'instrument se trompe si l'on oublie de décoder les
     entités HTML (EQ-16) ;
  4. il écrit ce qui reste non traduit : la table de contrôles (EQ-08) ;
  5. il mesure la forme : longueur des phrases (EQ-09), coupe arabe sans laquelle la mesure est
     fausse (EQ-10), distance avant le premier tableau (EQ-11), absence de tout mécanisme de
     définition (EQ-12) ;
  6. il lit le moteur pour dire quelle garde y est écrite et laquelle n'y est pas (EQ-13) ;
  7. il s'applique à lui-même la règle de forme qu'il énonce (EQ-14) et ferme sur la liste de ce
     qu'il ne remplit pas (EQ-15).

Ce qu'il ne fait pas : il ne mesure aucune compréhension humaine (aucun lecteur testé, aucun
questionnaire), n'emprunte aucun indice de lisibilité à une échelle publiée, ne traduit rien
lui-même, et ne corrige pas la table de contrôles dans ce lot.

Usage :
    cd ZENODO_DEPOT_ALMIZAN && py -3 REDACTION/redaction_mizan.py
    cd ZENODO_DEPOT_ALMIZAN && py -3 REDACTION/redaction_mizan.py --ecrit
    cd ZENODO_DEPOT_ALMIZAN && py -3 FONDATION/OUTILS/audit_piliers.py REDACTION/redaction_mizan.py
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

RACINE = Path(__file__).resolve().parents[1]
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

DOSSIER = Path(__file__).resolve().parent
ARTEFACTS = DOSSIER / "artefacts"
MOTEUR = RACINE / "ABONDANCE" / "moteur_page_trilingue.py"
LANGUES: Tuple[str, ...] = ("fr", "en", "ar")

SEUIL_PHRASE = 30          # mots par phrase : cible retenue par l'auteur, non dérivée (EQ-14)

from FONDATION import fondation_base as FB                                  # noqa: E402

# ─── 1. Source et provenance --------------------------------------------------

VIDEO = {
    "url": "https://www.youtube.com/watch?v=iuVxYHTJrhU",
    "id": "iuVxYHTJrhU",
    "titre": "Anthropic et OpenAI deviennent consultants, les Big Four tremblent !",
    "auteur": "Silicon Carne 🌶️",
    "duree_s": 1964,
    "horodatage_utc": "2026-11-09T20:13:32Z",
    "chapitres": [
        {"debut": "00:00", "titre": "— Sommaire"},
        {"debut": "02:20", "titre": "— Anthropic et OpenAI lancent leurs propres armées de "
                                   "consultants"},
        {"debut": "05:57", "titre": "— La fuite des talents a tué la légitimité du conseil"},
        {"debut": "08:44", "titre": "— Big Four : changer la nappe ou renverser la table ?"},
        {"debut": "11:34", "titre": "— Accenture fait des records : les Big Four résistent "
                                    "vraiment ?"},
        {"debut": "13:59", "titre": "— Andreessen : créez des spinoffs AI-native, arrêtez de "
                                    "transformer"},
        {"debut": "17:39", "titre": "— Adopter l'IA maintenant ou attendre les agents autonomes ?"},
        {"debut": "20:05", "titre": "— McKinsey relève ses salaires : la bataille des talents est "
                                    "ouverte"},
        {"debut": "23:01", "titre": "— La formation IA est-elle vraiment inutile ?"},
        {"debut": "25:53", "titre": "— L'État face au conseil : Palantir et Mistral en embuscade"},
        {"debut": "28:53", "titre": "— Les Émirats créent le premier gouvernement full AI-native"},
        {"debut": "30:44", "titre": "— Steve Jobs avait tout prévu sur les consultants"},
    ],
    "transcript": "absent — timedtext 200 avec 0 octet en json3, srv3 et XML (sonde du 2026-11-09)",
    "avertissements": ["aucun en-tête de chapitres dans la description : horodatages pris dans "
                       "toute la description"],
    "ce_que_la_video_n_a_pas_fourni": ["aucun contenu parlé : le transcript est absent",
                                       "aucun chiffre, aucune citation, aucune affirmation reprise",
                                       "aucune mesure de compréhension humaine"],
    "decision_de_forme": "les douze titres de chapitres sont des lignes courtes portant une seule "
                         "idée ; c'est cette forme, et elle seule, qui est reprise ici",
}

SOURCE: Dict[str, Any] = {
    "point_de_depart": "demande d'auteur 2026-11-09 : « pose les équations pour harmoniser et "
                       "répondre à la demande optimalement dans la continuité de ce que tu fais "
                       "déjà et il faut que ce soit simple et efficace pour tout le monde »",
    "auteur": "M. Ahmed EL BAHLOUL (IMAM8MAHDI)",
    "video": VIDEO,
    "antecedents_uses": [
        "ABONDANCE/moteur_page_trilingue.py — l'unique fabriquant des 21 pages publiées",
        "CONTINUITE/continuite_base.py — la couche précédente : le théorème de continuité dont "
        "ces pages sont la sortie",
        "certificats/plan_global.py — les sauts non remplis que la rédaction ne remplit pas",
    ],
    "ce_que_ce_module_n_utilise_pas": [
        "aucun contenu de la vidéo : ni phrase parlée, ni chiffre, ni opinion",
        "aucun indice de lisibilité publié (Flesch, Gunning fog) : aucune échelle externe n'est "
        "invoquée ; le seul seuil est celui que l'auteur a retenu",
        "aucun lecteur testé : ce dossier compte des mots, il n'affirme rien de la compréhension",
    ],
}

# Couverture numérique relevée le 2026-11-09 sur les pages du commit scellé a5f0126 (état
# antérieur à la retouche du moteur), avec la définition de EQ-05 : les nombres de la span
# lecture française, la span calcul retirée, les entités HTML décodées. La session de sonde qui
# avait annoncé 49 et 48 lisait le texte brut, sans décoder « &#x27; » : son nombre fantôme 27
# faisait échouer la comparaison sur sept lignes de plus. EQ-16 mesure cet écart d'instrument.
REVISION_PRECEDENTE: Dict[str, Any] = {
    "commit": "a5f0126",
    "date": "2026-11-09",
    "definition": "nombres de la span lecture française ; span calcul retirée ; entités décodées",
    "couverture": {"fr": 89, "en": 56, "ar": 55},
    "couverture_sans_decodage": {"fr": 89, "en": 49, "ar": 48}}

# ─── 2. Lecture du corpus publié ----------------------------------------------

TAG = re.compile(r"(?s)<[^>]+>")
LIGNE_TR = re.compile(r"(?s)<tr>(.*?)</tr>")
CELLULE = re.compile(r"(?s)<t[dh][^>]*>(.*?)</t[dh]>")
BLOC_PROSE = re.compile(r"(?s)<(p|li)\b[^>]*>(.*?)</\1>")
SPAN = {n: re.compile(r"(?s)<span class=\"%s\">(.*?)</span>" % n)
        for n in ("titre", "formule", "lecture", "chemin", "calcul", "statut", "nb")}
BADGE = re.compile(r"(?s)<span class=\"statut ([ops])\">")
STATUT_MOT = re.compile(r"(?s)<span class=\"statut [ops]\">(.*?)</span>")
ID_LIGNE = re.compile(r"^(EQ-\d+|C\d\d)$")
NOMBRE = re.compile(r"-?\d+(?:[.,]\d+)*")
MOT = re.compile(r"\S+")
_FCT = r"[A-Za-z_0-9.]+"
CHEMIN_MACHINE = re.compile(r"[a-z_0-9]+\.py\s*→\s*" + _FCT + r"\(\)"
                            r"(?:\s*(?:,|→)\s*" + _FCT + r"\(\))*\s*→\s*C\d\d")
ARABE = re.compile(r"[\u0600-\u06ff]")
LATIN = re.compile(r"[A-Za-zÀ-ÿ]")
POINT_VIRGULE_ARABE = "\u061b"
INTERROGATION_ARABE = "\u061f"
VOID = {"br", "img", "meta", "link", "input", "hr", "source"}


def _brut(fragment: str) -> str:
    sans = TAG.sub(" ", fragment)
    for a, b in (("&amp;", "&"), ("&nbsp;", " "), ("\u202f", " "), ("&#x27;", "'")):
        sans = sans.replace(a, b)
    return re.sub(r"\s+", " ", sans).strip()


def _nombres(texte: str) -> Dict[str, int]:
    compte: Dict[str, int] = {}
    for n in NOMBRE.findall(texte):
        cle = n.replace(",", ".")
        compte[cle] = compte.get(cle, 0) + 1
    return compte


def _merge(*textes: str) -> Dict[str, int]:
    compte: Dict[str, int] = {}
    for t in textes:
        for k, v in _nombres(t).items():
            compte[k] = compte.get(k, 0) + v
    return compte


def _couvre(plus_grand: Dict[str, int], plus_petit: Dict[str, int]) -> bool:
    return all(plus_grand.get(k, 0) >= v for k, v in plus_petit.items())


def _langue(nom_fichier: str) -> str:
    if nom_fichier.endswith("_ar.html"):
        return "ar"
    if nom_fichier.endswith("_en.html"):
        return "en"
    return "fr"


_LUC: Dict[str, Tuple[int, str]] = {}


def pages_publiees() -> List[Dict[str, str]]:
    out = []
    for chemin in sorted(RACINE.glob("*/artefacts/pages/*.html")):
        page = re.sub(r"_(en|ar)$", "", chemin.stem)
        out.append({"dossier": chemin.parents[2].name, "page": page,
                    "langue": _langue(chemin.name),
                    "chemin": chemin.relative_to(RACINE).as_posix()})
    return out


def _charger() -> Dict[str, str]:
    """Le corpus, relu à chaque mesure ; une entrée n'est relue que si sonmtime a bougé."""
    out: Dict[str, str] = {}
    for p in pages_publiees():
        f = RACINE / p["chemin"]
        m = f.stat().st_mtime_ns
        if p["chemin"] not in _LUC or _LUC[p["chemin"]][0] != m:
            _LUC[p["chemin"]] = (m, f.read_text(encoding="utf-8"))
        out[p["chemin"]] = _LUC[p["chemin"]][1]
    return out


def _trios() -> Dict[str, Dict[str, str]]:
    par: Dict[str, Dict[str, str]] = {}
    for p in pages_publiees():
        par.setdefault(f"{p['dossier']}/{p['page']}", {})[p["langue"]] = p["chemin"]
    return par


def _lignes(texte_html: str) -> Dict[str, Dict[str, str]]:
    out: Dict[str, Dict[str, str]] = {}
    for ligne in LIGNE_TR.findall(texte_html):
        cellules = CELLULE.findall(ligne)
        if not cellules:
            continue
        cle = _brut(cellules[0])
        if not ID_LIGNE.match(cle) or cle in out:
            continue
        corps = cellules[3] if len(cellules) > 3 else ""
        spans_lecture = SPAN["lecture"].findall(corps)
        spans_calcul = SPAN["calcul"].findall(corps)
        spans_chemin = SPAN["chemin"].findall(corps)
        out[cle] = {
            "id": cle,
            "titre": _brut(cellules[1]) if len(cellules) > 1 else "",
            "attendu": _brut(cellules[2]) if len(cellules) > 2 else "",
            "obtenu": _brut(cellules[3]) if len(cellules) > 3 else "",
            "cellules": str(len(cellules)),
            "lecture": _brut(spans_lecture[0]) if spans_lecture else "",
            "lecture_brute": spans_lecture[0] if spans_lecture else "",
            "calcul": _brut(spans_calcul[0]) if spans_calcul else "",
            "chemin": _brut(spans_chemin[0]) if spans_chemin else "",
        }
    return out


def _prose(texte_html: str) -> List[str]:
    return [_brut(b[1]) for b in BLOC_PROSE.findall(texte_html) if _brut(b[1])]


def _phrases(blocs: List[str], avec_arabe: bool = True) -> List[str]:
    separateur = ("(?<=[.!?%s%s])\\s+" % (POINT_VIRGULE_ARABE, INTERROGATION_ARABE)
                  if avec_arabe else "(?<=[.!?])\\s+")
    out: List[str] = []
    for b in blocs:
        out.extend(p.strip() for p in re.split(separateur, b) if p.strip())
    return out


def _mots(phrase: str) -> int:
    return len(MOT.findall(phrase))


# ─── 3. Les treize mesures ----------------------------------------------------

def corpus() -> Dict[str, Any]:
    pages = pages_publiees()
    par = _trios()
    orphelines = sorted(k for k, v in par.items() if len(v) != 3)
    htmls = _charger()
    return {"nb_pages": len(pages), "nb_trios": len(par),
            "dossiers": sorted({p["dossier"] for p in pages}),
            "pages_par_langue": {lg: sum(1 for p in pages if p["langue"] == lg)
                                 for lg in LANGUES},
            "trios_complets": sum(1 for v in par.values() if len(v) == 3),
            "orphelines": orphelines,
            "pages": sorted(f"{p['dossier']}/{p['page']}·{p['langue']}" for p in pages),
            "empreintes_courtes": {c: hashlib.sha256(t.encode("utf-8")).hexdigest()[:16]
                                   for c, t in sorted(htmls.items())},
            "pages_sans_ligne_de_tableau": sorted(c for c, t in htmls.items()
                                                  if not _lignes(t))}


def structure() -> Dict[str, Any]:
    htmls = _charger()
    largeurs: Dict[str, int] = {}
    profondeur_max = 0
    desequilibres: List[str] = []
    par_langue = {lg: {"eq": 0, "ctrl": 0} for lg in LANGUES}
    h1 = h2 = 0
    for chemin, texte in htmls.items():
        pile: List[str] = []
        for m in re.finditer(r"(?s)<(/?)([a-z0-9]+)([^>]*)>", texte):
            fermeture, balise, attributs = m.group(1), m.group(2), m.group(3)
            if balise in VOID or attributs.rstrip().endswith("/"):
                continue
            if fermeture:
                if pile and pile[-1] == balise:
                    pile.pop()
                else:
                    desequilibres.append(f"{chemin}:{balise}")
            else:
                pile.append(balise)
                profondeur_max = max(profondeur_max, len(pile))
        lg = _langue(chemin)
        for cle, lignes in _lignes(texte).items():
            largeurs[lignes["cellules"]] = largeurs.get(lignes["cellules"], 0) + 1
            par_langue[lg]["eq" if cle.startswith("EQ") else "ctrl"] += 1
        h1 += texte.count("<h1")
        h2 += texte.count("<h2")
    return {"lignes_total": sum(v["eq"] + v["ctrl"] for v in par_langue.values()),
            "par_langue": par_langue,
            "equations_par_langue": {lg: v["eq"] for lg, v in par_langue.items()},
            "controles_par_langue": {lg: v["ctrl"] for lg, v in par_langue.items()},
            "largeurs_de_ligne": largeurs, "profondeur_max": profondeur_max,
            "nb_desequilibres": len(desequilibres), "desequilibres": desequilibres[:8],
            "h1": h1, "h2": h2}


def badges() -> Dict[str, Any]:
    htmls = _charger()
    par: Dict[str, Dict[str, Dict[str, int]]] = {}
    for chemin, texte in htmls.items():
        compte: Dict[str, int] = {}
        for c in BADGE.findall(texte):
            compte[c] = compte.get(c, 0) + 1
        base = re.sub(r"(_en|_ar)?\.html$", "", chemin.split("/")[-1])
        par.setdefault(f"{chemin.split('/')[0]}/{base}", {})[_langue(chemin)] = compte
    ecarts = sorted(k for k, d in par.items()
                    if not (len(d) == 3 and d["fr"] == d["en"] == d["ar"]))
    mots = {lg: sorted({_brut(m) for c, t in htmls.items() if _langue(c) == lg
                        for m in STATUT_MOT.findall(t)}) for lg in LANGUES}
    totaux = {lg: sum(sum(v.get(c, 0) for c in "ops") for d in par.values()
                      for k, v in d.items() if k == lg) for lg in LANGUES}
    return {"totaux_par_langue": totaux, "badges_total": sum(totaux.values()),
            "trios": len(par), "trios_alignes": len(par) - len(ecarts), "ecarts": ecarts,
            "mots_par_langue": {lg: len(mots[lg]) for lg in LANGUES},
            "exemples_mots": {lg: mots[lg][:4] for lg in LANGUES},
            "classes_presentes": sorted({c for d in par.values() for v in d.values() for c in v})}


def chemins_machine() -> Dict[str, Any]:
    htmls = _charger()
    strict = re.compile(r"[a-z_0-9]+\.py\s*→\s*" + _FCT + r"\(\)\s*→\s*C\d\d")
    absents = {lg: [] for lg in LANGUES}
    total = une_fonction = 0
    for cle, d in sorted(_trios().items()):
        if len(d) != 3:
            continue
        R = {lg: _lignes(htmls[chemin]) for lg, chemin in d.items()}
        for k in [x for x in R["fr"] if x.startswith("EQ-") and all(x in R[l] for l in R)]:
            total += 1
            une_fonction += bool(strict.search(R["fr"][k]["chemin"]))
            for lg in R:
                if not CHEMIN_MACHINE.search(R[lg][k]["chemin"]):
                    absents[lg].append(f"{cle}·{k}")
    memes = all(absents[lg] == absents["fr"] for lg in LANGUES)
    with_chemin = total - len(absents["fr"])
    return {"total": total, "avec_chemin": with_chemin, "part": round(
        100.0 * with_chemin / total, 1) if total else 0.0,
        "exceptions": absents["fr"], "exceptions_par_langue": absents,
        "exceptions_identiques_entre_langues": memes,
        "forme": "module.py → une ou plusieurs fonctions() → Cnn",
        "forme_regex": CHEMIN_MACHINE.pattern,
        "une_seule_fonction": une_fonction,
        "part_une_seule_fonction": round(100.0 * une_fonction / total, 1) if total else 0.0}


def harmonisation() -> Dict[str, Any]:
    """Couverture numérique par langue, la span calcul retirée puis rendue."""
    htmls = _charger()
    avec = {lg: 0 for lg in LANGUES}
    sans = {lg: 0 for lg in LANGUES}
    sans_brut = {lg: 0 for lg in LANGUES}
    total = 0
    identiques = 0
    divergentes: List[str] = []
    exemples: Dict[str, str] = {}
    for cle, d in sorted(_trios().items()):
        if len(d) != 3:
            continue
        R = {lg: _lignes(htmls[chemin]) for lg, chemin in d.items()}
        for k in [x for x in R["fr"] if x.startswith("EQ-") and all(x in R[l] for l in R)]:
            total += 1
            ref = _nombres(R["fr"][k]["lecture"])
            ref_brut = _nombres(R["fr"][k]["lecture_brute"])
            for lg in LANGUES:
                sans[lg] += _couvre(_nombres(R[lg][k]["lecture"]), ref)
                sans_brut[lg] += _couvre(_nombres(R[lg][k]["lecture_brute"]), ref_brut)
                avec[lg] += _couvre(_merge(R[lg][k]["lecture"], R[lg][k]["calcul"]), ref)
            for lg in ("en", "ar"):
                if R[lg][k]["calcul"] and R[lg][k]["calcul"] == R["fr"][k]["lecture"]:
                    identiques += 1
                    exemples.setdefault(lg, R[lg][k]["calcul"][:70])
                else:
                    divergentes.append(f"{cle}·{k}·{lg}")
    return {"total": total, "sans_ligne": sans, "avec_ligne": avec,
            "avant_declare": REVISION_PRECEDENTE,
            "ablation_fidele": all(REVISION_PRECEDENTE["couverture"][lg] == sans[lg]
                                   for lg in LANGUES),
            # EQ-16 : la même règle appliquée au texte non décodé. `&#x27;` est une apostrophe ;
            # lu comme du texte il apporte le nombre 27 et la couverture baisse d'autant.
            "sans_decodage_entites": sans_brut,
            "ecart_decodage": {lg: sans[lg] - sans_brut[lg] for lg in LANGUES},
            "entite_en_cause": "&#x27;",
            "gagne": {lg: avec[lg] - sans[lg] for lg in ("en", "ar")},
            "lignes_identiques": identiques, "lignes_comparees": 2 * total,
            "nb_divergentes": len(divergentes), "divergentes": divergentes[:8],
            "span_calcul_par_langue": {lg: sum(len(SPAN["calcul"].findall(t))
                                               for c, t in htmls.items() if _langue(c) == lg)
                                       for lg in LANGUES},
            "exemple_ligne": exemples}


def lignes_de_controle() -> Dict[str, Any]:
    htmls = _charger()
    total = identiques = arabes = 0
    par_dossier: Dict[str, int] = {}
    for cle, d in sorted(_trios().items()):
        if len(d) != 3:
            continue
        R = {lg: _lignes(htmls[chemin]) for lg, chemin in d.items()}
        ids = [k for k in R["fr"] if k.startswith("C") and all(k in R[l] for l in R)]
        for k in ids:
            total += 1
            identiques += all(R["fr"][k][c] == R["en"][k][c] == R["ar"][k][c]
                              for c in ("titre", "attendu", "obtenu"))
            arabes += bool(ARABE.search(R["ar"][k]["titre"]))
        par_dossier[cle] = len(ids)
    return {"total": total, "trois_cellules_identiques": identiques,
            "titres_arabes_en_page_arabe": arabes, "par_dossier": par_dossier,
            "interpretation": "neutralité par absence de traduction, pas par équivalence"}


def prose() -> Dict[str, Any]:
    htmls = _charger()
    par_page: Dict[str, Dict[str, Any]] = {}
    for chemin, texte in htmls.items():
        phrases = _phrases(_prose(texte))
        mots = [_mots(p) for p in phrases]
        par_page[chemin] = {"phrases": len(phrases), "mots": sum(mots),
                            "moyenne": round(sum(mots) / len(mots), 2) if mots else 0.0,
                            "max": max(mots) if mots else 0,
                            "au_dessus": sum(1 for m in mots if m > SEUIL_PHRASE),
                            "part": round(100.0 * sum(1 for m in mots if m > SEUIL_PHRASE)
                                          / len(mots), 1) if mots else 0.0}
    par_langue: Dict[str, Dict[str, Any]] = {}
    for lg in LANGUES:
        vues = {k: v for k, v in par_page.items() if _langue(k) == lg}
        moyennes = [v["moyenne"] for v in vues.values() if v["phrases"]]
        parts = [v["part"] for v in vues.values() if v["phrases"]]
        par_langue[lg] = {"pages": len(vues),
                          "moyenne_min": round(min(moyennes), 2) if moyennes else 0.0,
                          "moyenne_max": round(max(moyennes), 2) if moyennes else 0.0,
                          "part_min": round(min(parts), 1) if parts else 0.0,
                          "part_max": round(max(parts), 1) if parts else 0.0,
                          "phrases": sum(v["phrases"] for v in vues.values()),
                          "mots": sum(v["mots"] for v in vues.values())}
    pire = max(par_page.items(), key=lambda kv: kv[1]["max"])
    hors = {lg: sum(1 for k, v in par_page.items() if _langue(k) == lg and v["part"] > 10.0)
            for lg in LANGUES}
    return {"par_page": {k: {"phrases": v["phrases"], "moyenne": v["moyenne"],
                             "max": v["max"], "part": v["part"]}
                         for k, v in sorted(par_page.items())},
            "par_langue": par_langue,
            "page_la_plus_longue": {"page": pire[0], "mots": pire[1]["max"]},
            "pages_au_dessus_de_10_pct": hors,
            "total_pages_au_dessus": sum(hors.values()),
            "nb_pages_mesurees": len(par_page), "seuil": SEUIL_PHRASE}


def coupe_arabe() -> Dict[str, Any]:
    htmls = _charger()
    moyennes = {"avec": [], "sans": []}
    signes = {POINT_VIRGULE_ARABE: 0, INTERROGATION_ARABE: 0}
    for chemin, texte in htmls.items():
        if _langue(chemin) != "ar":
            continue
        for cle in signes:
            signes[cle] += texte.count(cle)
        blocs = _prose(texte)
        pour_option = {"avec": True, "sans": False}
        for option, drapeau in pour_option.items():
            mots = [_mots(p) for p in _phrases(blocs, avec_arabe=drapeau)]
            moyennes[option].append(round(sum(mots) / len(mots), 2) if mots else 0.0)
    avec = round(sum(moyennes["avec"]) / len(moyennes["avec"]), 2) if moyennes["avec"] else 0.0
    sans = round(sum(moyennes["sans"]) / len(moyennes["sans"]), 2) if moyennes["sans"] else 0.0
    return {"points_virgule_arabes": signes[POINT_VIRGULE_ARABE],
            "interrogations_arabes": signes[INTERROGATION_ARABE],
            "moyenne_avec_coupe": avec, "moyenne_sans_coupe": sans, "ecart": round(sans - avec, 2),
            "pages_arabes": len(moyennes["avec"]),
            "enonce": "le texte arabe sépare ses propositions par « ؛ » ; sans ce séparateur deux "
                      "phrases ne font qu'une ligne comptée et la moyenne est fausse"}


def charge_acces() -> Dict[str, Any]:
    htmls = _charger()
    par_page: Dict[str, Dict[str, int]] = {}
    for chemin, texte in htmls.items():
        premier = texte.find("<table")
        mots_avant = sum(_mots(p) for p in _phrases(_prose(texte[:premier] if premier >= 0
                                                           else texte)))
        par_page[chemin] = {"avant": mots_avant,
                            "total": sum(_mots(p) for p in _phrases(_prose(texte))),
                            "tableau": 1 if premier >= 0 else 0}
    avant = [v["avant"] for v in par_page.values() if v["avant"]]
    tot = sum(v["total"] for v in par_page.values())
    return {"min": min(avant) if avant else 0, "max": max(avant) if avant else 0,
            "moyenne": round(sum(avant) / len(avant), 1) if avant else 0.0,
            "pages": len(par_page),
            "pages_avec_tableau": sum(v["tableau"] for v in par_page.values()),
            "pages_sans_tableau": sum(1 for v in par_page.values() if not v["tableau"]),
            "part_avant": round(100.0 * sum(v["avant"] for v in par_page.values()) / tot, 1)
            if tot else 0.0,
            "par_page": {k: v["avant"] for k, v in sorted(par_page.items())}}


def definitions() -> Dict[str, Any]:
    htmls = _charger()
    out = {"dfn": 0, "abbr": 0, "glossaire": 0, "spans_title": 0}
    for texte in htmls.values():
        out["dfn"] += len(re.findall(r"(?i)<dfn\b", texte))
        out["abbr"] += len(re.findall(r"(?i)<abbr\b", texte))
        out["glossaire"] += len(re.findall(r"(?i)glossaire", texte))
        out["spans_title"] += len(re.findall(r"(?i)<span[^>]*\btitle=", texte))
    return {**out, "nb_pages": len(htmls),
            "mecanisme": "aucun : ni <dfn>, ni <abbr>, ni section glossaire"}


def garde_moteur() -> Dict[str, Any]:
    texte = MOTEUR.read_text(encoding="utf-8")
    lignes = texte.splitlines()
    numero = next((i + 1 for i, l in enumerate(lignes)
                   if 'e["resultat"] if lang == "fr"' in l), 0)
    return {"fichier": MOTEUR.relative_to(RACINE).as_posix(),
            "ligne_de_branche": numero,
            "branche_lue": lignes[numero - 1].strip() if numero else "",
            "appels_garde_une_voie": len(re.findall(r"(?<!def )\bverifier_nombres\(", texte)),
            "langues_controlees": re.findall(r"for code in \(([^)]*)\)", texte)[:1],
            "span_calcul_ecrite": texte.count('class=\\"calcul\\"'),
            "css_calcul": texte.count(".calcul{"),
            "garde_de_ligne_calculee": "ligne calculée absente" in texte,
            "sens_de_la_garde": "refuse un nombre énoncé hors calcul ; n'a jamais exigé la "
                                "présence d'un nombre calculé",
            "nb_lignes_source": len(lignes), "octets_source": len(texte.encode("utf-8"))}


def ouvertures() -> Dict[str, Any]:
    l, p, d = lignes_de_controle(), prose(), definitions()
    liste = [
        f"{l['total']} lignes de contrôle restent en français dans les pages anglaise et arabe",
        f"{p['total_pages_au_dessus']} pages sur {p['nb_pages_mesurees']} dépassent 10 % de "
        f"phrases de plus de {SEUIL_PHRASE} mots",
        f"{d['dfn']} balise <dfn> et {d['glossaire']} occurrence de « glossaire » : aucun terme "
        "n'est défini à sa première occurrence",
        "aucune lecture humaine mesurée : aucun test de compréhension n'a été conduit",
        "la ligne calculée harmonisée n'est pas traduite : elle porte les nombres, pas la phrase "
        "qui les explique",
    ]
    return {"nb": len(liste), "liste": liste, "remplies_dans_ce_lot": 0,
            "ce_que_la_correction_remplit": "la ligne calculée, dans les trois langues "
                                            "(EQ-06, EQ-07)"}


def autoforme(eqs: List[Dict[str, Any]], cs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """La règle de forme est appliquée aux lignes que ce module écrit lui-même."""
    lignes = [e["formule"] for e in eqs] + [c["nom"] for c in cs]
    mots = [_mots(p) for p in _phrases(lignes)]
    mots_limites = [_mots(p) for p in _phrases([e["limite"] for e in eqs])]
    chapitres = [_mots(c["titre"].lstrip("— ").strip()) for c in VIDEO["chapitres"]]
    return {"lignes_mesurees": len(mots), "mots_max": max(mots) if mots else 0,
            "moyenne": round(sum(mots) / len(mots), 2) if mots else 0.0,
            "au_dessus_du_seuil": sum(1 for m in mots if m > SEUIL_PHRASE),
            "seuil": SEUIL_PHRASE,
            "limites_exemptees": len(mots_limites),
            "limites_mots_max": max(mots_limites) if mots_limites else 0,
            "chapitres_video": len(chapitres),
            "chapitres_video_mots_max": max(chapitres) if chapitres else 0,
            "chapitres_video_moyenne": round(sum(chapitres) / len(chapitres), 2)
            if chapitres else 0.0}


# ─── 4. Équations et contrôles -------------------------------------------------

NOEUDS: Dict[str, Dict[str, Any]] = {
    "EQ-01": {"depend": [], "externe": ["*/artefacts/pages/*.html (générés par le moteur)"]},
    "EQ-02": {"depend": ["EQ-01"], "externe": []},
    "EQ-03": {"depend": ["EQ-02"], "externe": []},
    "EQ-04": {"depend": ["EQ-02"], "externe": []},
    "EQ-05": {"depend": ["EQ-04"], "externe": ["révision scellée antérieure aux pages courantes"]},
    "EQ-06": {"depend": ["EQ-05"], "externe": ["ABONDANCE/moteur_page_trilingue.py (retouché)"]},
    "EQ-07": {"depend": ["EQ-06"], "externe": []},
    "EQ-08": {"depend": ["EQ-02"], "externe": []},
    "EQ-09": {"depend": ["EQ-01"], "externe": []},
    "EQ-10": {"depend": ["EQ-09"], "externe": []},
    "EQ-11": {"depend": ["EQ-01"], "externe": []},
    "EQ-12": {"depend": ["EQ-01"], "externe": []},
    "EQ-13": {"depend": ["EQ-06"], "externe": ["ABONDANCE/moteur_page_trilingue.py (lu)"]},
    "EQ-14": {"depend": ["EQ-09"], "externe": ["vidéo iuVxYHTJrhU — forme des titres seulement"]},
    "EQ-15": {"depend": ["EQ-05", "EQ-08", "EQ-12"], "externe": []},
    "EQ-16": {"depend": ["EQ-05"], "externe": []},
}


def _eq(id_: str, chemin: str, formule: str, resultat: str, statut: str,
        limite: str, detail: Any) -> Dict[str, Any]:
    n = NOEUDS[id_]
    return {"id": id_, "chemin": chemin, "formule": formule, "resultat": resultat,
            "statut": statut, "limite": limite, "detail": detail,
            "couche": "S2 REGULARITE",
            "piliers": ["P1 UNITE", "P2 BORNE", "P3 CONFRONTATION", "P4 TRANSMISSION"],
            "depend_de": n["depend"], "fonde_hors_du_dossier": n["externe"]}


def equations(etat: Dict[str, Any]) -> List[Dict[str, Any]]:
    co, st, b, m = (etat["corpus"], etat["structure"], etat["badges"], etat["chemins_machine"])
    h, lc = etat["harmonisation"], etat["lignes_de_controle"]
    pr, ca, ch = etat["prose"], etat["coupe"], etat["charge"]
    de, g, au, ou = etat["definitions"], etat["moteur"], etat["autoforme"], etat["ouvertures"]
    return [
        _eq("EQ-01", "redaction_mizan.py → corpus() → C01",
            "corpus = trios(dossier, page) × langues, trois pages par trio",
            f"{co['nb_pages']} pages · {co['nb_trios']} trios · {co['pages_par_langue']} · "
            f"orphelines {co['orphelines'] or 'aucune'}", "OPÉRATIONNEL",
            "le corpus est celui publié sur disque : une page absente ferait tomber le compte, "
            "rien ici ne compte une page qui n'existe pas", co),
        _eq("EQ-02", "redaction_mizan.py → structure() → C02",
            "toute ligne de tableau porte cinq cellules dans les trois langues",
            f"{st['lignes_total']} lignes · largeurs {st['largeurs_de_ligne']} · profondeur "
            f"{st['profondeur_max']} · déséquilibres {st['nb_desequilibres']}", "OPÉRATIONNEL",
            "la structure est identique, le contenu ne l'est pas : ce contrôle ne dit rien de la "
            "traduction, seulement du squelette", st),
        _eq("EQ-03", "redaction_mizan.py → badges() → C03",
            "rang = classe o/p/s du badge : neutre en langue, le mot seul se traduit",
            f"badges {b['totaux_par_langue']} · trios alignés {b['trios_alignes']}/{b['trios']} · "
            f"mots par langue {b['mots_par_langue']}", "OPÉRATIONNEL",
            "la classe est cherchée dans le fichier : une page qui écrirait le rang en toutes "
            "lettres échapperait au comptage", b),
        _eq("EQ-04", "redaction_mizan.py → chemins_machine() → C04",
            "chemin = module.py → une ou plusieurs fonctions() → Cnn, même chaîne dans les "
            "trois cellules",
            f"{m['avec_chemin']}/{m['total']} lignes ({m['part']} %) · une seule fonction "
            f"{m['une_seule_fonction']} ({m['part_une_seule_fonction']} %) · exceptions "
            f"{m['exceptions']} · partagées {m['exceptions_identiques_entre_langues']}",
            "OPÉRATIONNEL",
            "une ligne sans chemin machine n'est pas une ligne fausse : c'est une ligne que le "
            "lecteur ne peut pas aller revérifier dans le code", m),
        _eq("EQ-05", "redaction_mizan.py → harmonisation() → C05",
            "couverture(lang) = lignes portant les nombres de la ligne calculée française, "
            "span calcul retirée",
            f"sans ligne calculée {h['sans_ligne']} sur {h['total']} · déclaré avant "
            f"{h['avant_declare']} · fidèle {h['ablation_fidele']}", "SIMULÉ",
            "l'état « avant » n'est pas archivé dans le dépôt : il est reconstitué en retirant la "
            "span calcul des pages courantes, puis confronté aux valeurs lues sur la révision "
            "scellée antérieure", h),
        _eq("EQ-06", "redaction_mizan.py → harmonisation() → C06",
            "la ligne calculée est rendue dans les trois langues",
            f"avec ligne calculée {h['avec_ligne']} sur {h['total']} · lignes gagnées "
            f"{h['gagne']} · span par langue {h['span_calcul_par_langue']}", "OPÉRATIONNEL",
            "la ligne rendue n'est pas traduite : c'est la sortie machine, chiffres et symboles, "
            "identique dans les trois langues", h),
        _eq("EQ-07", "redaction_mizan.py → harmonisation() → C07",
            "lecture française = span calcul anglaise = span calcul arabe, ligne à ligne",
            f"{h['lignes_identiques']}/{h['lignes_comparees']} comparaisons identiques · "
            f"divergentes {h['nb_divergentes']}", "OPÉRATIONNEL",
            "égalité de texte, pas égalité de sens : la span calcul peut porter un mot technique "
            "que le lecteur anglais ne connaîtra pas", h),
        _eq("EQ-08", "redaction_mizan.py → lignes_de_controle() → C08",
            "table de contrôles : nom, attendu, obtenu identiques dans les trois langues",
            f"{lc['trois_cellules_identiques']}/{lc['total']} lignes non traduites · titres "
            f"arabes en page arabe {lc['titres_arabes_en_page_arabe']}", "OPÉRATIONNEL",
            "constat, pas un objectif : cette neutralité est une absence de traduction ; elle "
            "n'est pas corrigée dans ce lot et reste ouverte (EQ-15)", lc),
        _eq("EQ-09", "redaction_mizan.py → prose() → C09",
            f"moyenne = mots / phrases sur les blocs <p> et <li> ; part = phrases au-delà de "
            f"{SEUIL_PHRASE} mots",
            f"par langue {pr['par_langue']} · plus longue phrase {pr['page_la_plus_longue']}",
            "OPÉRATIONNEL",
            "les cellules de tableau sont exclues : concaténées, elles produisaient des « phrases » "
            "de plus de 800 mots qui ne mesuraient rien", pr),
        _eq("EQ-10", "redaction_mizan.py → coupe_arabe() → C10",
            "coupe arabe = . ! ? ؛ ؟ — sans « ؛ » la moyenne arabe est fausse",
            f"« ؛ » {ca['points_virgule_arabes']} · « ؟ » {ca['interrogations_arabes']} · "
            f"moyenne avec {ca['moyenne_avec_coupe']} sans {ca['moyenne_sans_coupe']} · écart "
            f"{ca['ecart']}", "OPÉRATIONNEL",
            "ce contrôle porte sur l'instrument, pas sur le texte : il dit que la métrique arabe "
            "dépend du séparateur retenu", ca),
        _eq("EQ-11", "redaction_mizan.py → charge_acces() → C11",
            "mots de prose avant le premier tableau = distance au premier nombre",
            f"{ch['min']}–{ch['max']} mots · moyenne {ch['moyenne']} · {ch['part_avant']} % de la "
            f"prose avant le premier tableau · pages sans tableau {ch['pages_sans_tableau']}",
            "OPÉRATIONNEL",
            "le compte s'arrête à la balise <table> : un lecteur qui saute au tableau n'a pas lu "
            "la prose, et rien ici ne mesure ce comportement", ch),
        _eq("EQ-12", "redaction_mizan.py → definitions() → C12",
            "définition à la première occurrence = <dfn> ou <abbr> ou section glossaire",
            f"<dfn> {de['dfn']} · <abbr> {de['abbr']} · glossaire {de['glossaire']} · spans "
            f"title= {de['spans_title']} sur {de['nb_pages']} pages", "OPÉRATIONNEL",
            "le zéro est la mesure, pas une correction : aucun mécanisme de définition n'existe "
            "et ce dossier n'en installe pas", de),
        _eq("EQ-13", "redaction_mizan.py → garde_moteur() → C13",
            "garde du moteur = refuse un nombre énoncé hors calcul, ne demande jamais un nombre "
            "calculé",
            f"appels {g['appels_garde_une_voie']} · langues {g['langues_controlees']} · branche "
            f"ligne {g['ligne_de_branche']} · garde de ligne {g['garde_de_ligne_calculee']} · css "
            f"{g['css_calcul']}", "OPÉRATIONNEL",
            "lecture statique d'une source : si le moteur est réécrit autrement, cette équation "
            "tombe en rouge au lieu de s'adapter en silence", g),
        _eq("EQ-14", "redaction_mizan.py → autoforme() → C14",
            f"règle retenue : une idée par ligne, {SEUIL_PHRASE} mots au plus, appliquée à ce "
            "module",
            f"{au['lignes_mesurees']} lignes auto-mesurées · max {au['mots_max']} · moyenne "
            f"{au['moyenne']} · dépassements {au['au_dessus_du_seuil']} · titres de chapitres de "
            f"la vidéo max {au['chapitres_video_mots_max']} mots", "SPÉCIFIÉ",
            "le seuil de 30 mots est un choix d'auteur, dérivé de rien dans ce dossier ; les "
            "annotations `limite` y sont soustraites et leur longueur est mesurée à part", au),
        _eq("EQ-15", "redaction_mizan.py → ouvertures() → C15",
            "ce que REDACTION ne remplit pas reste écrit et compté",
            f"{ou['nb']} échelles ouvertes · fermées dans ce lot {ou['remplies_dans_ce_lot']}",
            "SPÉCIFIÉ",
            "aucune de ces lignes n'est tenue pour réglée : la liste est produite par la mesure "
            "des pages, pas par une intention", ou),
        _eq("EQ-16", "redaction_mizan.py → harmonisation() → C16",
            "couverture = nombres comparés après décodage ; avant décodage, l'entité « &#x27; » "
            "apporte son 27 et la couverture baisse",
            f"sans décodage {h['sans_decodage_entites']} · écart {h['ecart_decodage']} · "
            f"entité {h['entite_en_cause']}", "OPÉRATIONNEL",
            "c'est l'instrument qu'on mesure ici, pas le texte : la même page rend deux chiffres "
            "selon que l'entité HTML est décodée ou lue brute", h),
    ]


def controles(eqs: Dict[str, Any], etat: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []

    def ajouter(id_: str, nom: str, verifie: str, attendu: str, obtenu: str, ok: bool) -> None:
        out.append({"id": id_, "equation": f"EQ-{id_[1:]}", "nom": nom, "verifie": verifie,
                    "attendu": attendu, "obtenu": obtenu, "ok": bool(ok)})

    co, st, b, m = (etat["corpus"], etat["structure"], etat["badges"], etat["chemins_machine"])
    h, lc = etat["harmonisation"], etat["lignes_de_controle"]
    pr, ca, ch = etat["prose"], etat["coupe"], etat["charge"]
    de, g, au, ou = etat["definitions"], etat["moteur"], etat["autoforme"], etat["ouvertures"]
    ajouter("C01", "le corpus mesuré est celui publié",
            "trois pages par trio et aucune page orpheline",
            f"{co['nb_trios']}/{co['nb_trios']} trios complets",
            f"{co['trios_complets']}/{co['nb_trios']} · orphelines "
            f"{co['orphelines'] or 'aucune'} · pages {co['nb_pages']}",
            co["trios_complets"] == co["nb_trios"] and not co["orphelines"])
    ajouter("C02", "cinq cellules par ligne et balisage équilibré",
            "une seule largeur de ligne, zéro balise déséquilibrée",
            "largeur 5 partout · 0 déséquilibre",
            f"largeurs {st['largeurs_de_ligne']} · déséquilibres {st['nb_desequilibres']} · "
            f"profondeur {st['profondeur_max']}",
            list(st["largeurs_de_ligne"]) == ["5"] and st["nb_desequilibres"] == 0)
    ajouter("C03", "le rang de chaque badge est le même dans les trois langues",
            "comptes o/p/s égaux langue à langue pour chaque trio",
            f"{b['trios']} trios alignés, un total par langue",
            f"{b['trios_alignes']}/{b['trios']} · écarts {b['ecarts'] or 'aucun'} · "
            f"{b['totaux_par_langue']}",
            b["trios_alignes"] == b["trios"] and len({b["totaux_par_langue"][lg]
                                                      for lg in LANGUES}) == 1)
    ajouter("C04", "les exceptions au chemin machine sont les mêmes lignes dans les trois langues",
            "aucune ligne sans chemin dans une seule langue",
            f"{len(m['exceptions'])} exceptions, identiques langue à langue",
            f"absents {m['exceptions']} · identiques "
            f"{m['exceptions_identiques_entre_langues']} · {m['avec_chemin']}/{m['total']} avec",
            m["exceptions_identiques_entre_langues"])
    ajouter("C05", "l'ablation reproduit l'état mesuré avant la retouche du moteur",
            "couverture sans ligne calculée égale aux valeurs déclarées",
            f"{REVISION_PRECEDENTE}",
            f"ablation {h['sans_ligne']} · fidèle {h['ablation_fidele']}",
            h["ablation_fidele"])
    ajouter("C06", "la ligne calculée est présente dans les trois langues",
            "couverture pleine dans les trois langues",
            f"{h['total']}/{h['total']} × 3",
            f"{h['avec_ligne']} · gagnées {h['gagne']}",
            all(h["avec_ligne"][lg] == h["total"] for lg in LANGUES))
    ajouter("C07", "le texte de la ligne calculée est identique d'une langue à l'autre",
            "zéro divergence sur les deux langues non sources",
            f"{2 * h['total']} comparaisons identiques",
            f"{h['lignes_identiques']}/{h['lignes_comparees']} · divergentes "
            f"{h['divergentes'] or 'aucune'}",
            h["lignes_identiques"] == h["lignes_comparees"])
    ajouter("C08", "les lignes de contrôle ne sont pas traduites",
            "le déficit est compté et écrit, pas masqué",
            f"{lc['total']} lignes comptées · 0 titre arabe",
            f"identiques {lc['trois_cellules_identiques']}/{lc['total']} · titres arabes "
            f"{lc['titres_arabes_en_page_arabe']} · par dossier {lc['par_dossier']}",
            lc["trois_cellules_identiques"] == lc["total"]
            and lc["titres_arabes_en_page_arabe"] == 0)
    ajouter("C09", "toutes les pages sont mesurées et le dépassement est écrit",
            "21 pages mesurées, part maximale non remise à zéro",
            f"{co['nb_pages']} pages · pire part > 0",
            f"{pr['nb_pages_mesurees']} pages · {pr['pages_au_dessus_de_10_pct']} au-dessus de "
            f"10 % · pire {pr['par_langue']['en']['part_max']} %",
            pr["nb_pages_mesurees"] == co["nb_pages"] and pr["total_pages_au_dessus"] > 0)
    ajouter("C10", "la coupe arabe change la mesure",
            "écart de moyenne non nul entre les deux coupes",
            "écart > 0 mot",
            f"avec {ca['moyenne_avec_coupe']} · sans {ca['moyenne_sans_coupe']} · écart "
            f"{ca['ecart']} · « ؛ » {ca['points_virgule_arabes']}",
            abs(ca["ecart"]) > 0.0 and ca["points_virgule_arabes"] > 0)
    ajouter("C11", "la distance au premier tableau est mesurée sur chaque page",
            "toutes les pages comptées, distance non nulle",
            f"{co['nb_pages']} pages · min > 0",
            f"{ch['min']}–{ch['max']} mots · pages {ch['pages']} · sans tableau "
            f"{ch['pages_sans_tableau']}",
            ch["pages"] == co["nb_pages"] and ch["min"] > 0)
    ajouter("C12", "l'absence de mécanisme de définition est écrite",
            "<dfn> = 0 et <abbr> = 0 sur la totalité du corpus",
            "zéro définition sur 21 pages",
            f"dfn {de['dfn']} · abbr {de['abbr']} · glossaire {de['glossaire']} · pages "
            f"{de['nb_pages']}",
            de["dfn"] == 0 and de["abbr"] == 0 and de["nb_pages"] == co["nb_pages"])
    ajouter("C13", "la garde de ligne calculée est écrite dans le moteur",
            "branche, span, css et garde présents",
            "branche > 0 · css ≥ 1 · garde vraie",
            f"ligne {g['ligne_de_branche']} · span {g['span_calcul_ecrite']} · css "
            f"{g['css_calcul']} · garde {g['garde_de_ligne_calculee']}",
            g["ligne_de_branche"] > 0 and g["css_calcul"] >= 1
            and g["span_calcul_ecrite"] >= 1 and g["garde_de_ligne_calculee"])
    ajouter("C14", "le module tient sa propre règle de forme",
            f"aucune formule ni nom de contrôle au-dessus de {SEUIL_PHRASE} mots",
            "0 dépassement",
            f"{au['lignes_mesurees']} lignes · max {au['mots_max']} · dépassements "
            f"{au['au_dessus_du_seuil']}",
            au["au_dessus_du_seuil"] == 0 and au["mots_max"] <= SEUIL_PHRASE)
    ajouter("C15", "les échelles ouvertes sont comptées, aucune déclarée remplie",
            "au moins 5 lignes ouvertes et 0 remplie dans ce lot",
            "≥ 5 · 0",
            f"{ou['nb']} ouvertes · {ou['remplies_dans_ce_lot']} remplies",
            ou["nb"] >= 5 and ou["remplies_dans_ce_lot"] == 0)
    ajouter("C16", "le décodage des entités change la mesure",
            "couverture brute strictement plus basse en anglais et en arabe",
            "écart négatif sur les deux langues traduites",
            f"brute {h['sans_decodage_entites']} · décodée {h['sans_ligne']} · écart "
            f"{h['ecart_decodage']}",
            all(h["sans_decodage_entites"][lg] < h["sans_ligne"][lg] for lg in ("en", "ar"))
            and h["sans_decodage_entites"]["fr"] == h["sans_ligne"]["fr"])
    return out


# ─── 5. État, certificat, empreinte -------------------------------------------

def mesures() -> Dict[str, Any]:
    return {"corpus": corpus(), "structure": structure(), "badges": badges(),
            "chemins_machine": chemins_machine(), "harmonisation": harmonisation(),
            "lignes_de_controle": lignes_de_controle(), "prose": prose(), "coupe": coupe_arabe(),
            "charge": charge_acces(), "definitions": definitions(), "moteur": garde_moteur(),
            "ouvertures": ouvertures()}


def noeuds_certificat() -> Dict[str, Any]:
    # autoforme() mesure les lignes que ce module écrit lui-même : premier passage à blanc,
    # car les formules et les noms de contrôle ne dépendent pas de cette mesure.
    etat = {**mesures(), "autoforme": {"lignes_mesurees": 0, "mots_max": 0, "moyenne": 0.0,
                                       "au_dessus_du_seuil": 0, "seuil": SEUIL_PHRASE,
                                       "limites_exemptees": 0, "limites_mots_max": 0,
                                       "chapitres_video": 0, "chapitres_video_mots_max": 0,
                                       "chapitres_video_moyenne": 0.0}}
    eqs = equations(etat)
    cs = controles({e["id"]: e for e in eqs}, etat)
    return {**etat, "autoforme": autoforme(eqs, cs)}


def canonique(objet: Any) -> bytes:
    return json.dumps(objet, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")


def etat_complet() -> Dict[str, Any]:
    nc = noeuds_certificat()
    octets = canonique(nc)
    second = canonique(noeuds_certificat())
    return {**nc, "noeuds_certificat": nc,
            "empreinte_execution": hashlib.sha256(octets).hexdigest(),
            "rejoue_identique": octets == second, "taille_octets": len(octets)}


def certificat() -> Dict[str, Any]:
    etat = etat_complet()
    nc = etat["noeuds_certificat"]
    return {"source": SOURCE, **nc,
            "empreinte_execution": etat["empreinte_execution"],
            "rejoue_identique": etat["rejoue_identique"],
            "limites": [
                "ce dossier compte des mots et des cellules : il ne mesure pas la compréhension, "
                "aucun lecteur n'a été testé",
                "aucun indice de lisibilité publié n'est utilisé : le seul seuil est celui que "
                "l'auteur a retenu, 30 mots par phrase",
                "la ligne calculée harmonisée n'est pas traduite : elle donne les nombres, pas la "
                "phrase qui les explique dans la langue du lecteur",
                f"{etat['lignes_de_controle']['total']} lignes de contrôle restent en français "
                "dans les pages anglaise et arabe",
                f"{etat['prose']['total_pages_au_dessus']} pages sur "
                f"{etat['prose']['nb_pages_mesurees']} dépassent encore 10 % de phrases de plus "
                "de 30 mots",
                f"{etat['definitions']['dfn']} balise <dfn> : aucun terme n'est défini à sa "
                "première occurrence",
                "les valeurs mesurées sont celles du corpus à l'instant de la lecture : une "
                "régénération des pages peut les déplacer",
                "la vidéo n'a fourni que des titres de chapitres : son contenu parlé est absent "
                "et n'est cité nulle part",
            ],
            "attribution": {"auteur": SOURCE["auteur"],
                            "video": {"url": VIDEO["url"], "titre": VIDEO["titre"],
                                      "auteur": VIDEO["auteur"],
                                      "elements_utilises": "titres et horodatages des "
                                                           f"{len(VIDEO['chapitres'])} chapitres, "
                                                           "rien d'autre"},
                            "statut_de_la_demande": "déclaré · non vérifié pour tout ce qui "
                                                    "déborde la mesure des pages"},
            "racine_merkle_sha256": hashlib.sha256(canonique(
                {c: hashlib.sha256(canonique(nc[c])).hexdigest() for c in sorted(nc)})).hexdigest()}


def resoudre() -> Dict[str, Any]:
    cert = certificat()
    etat = {k: cert[k] for k in ("corpus", "structure", "badges", "chemins_machine",
                                 "harmonisation", "lignes_de_controle", "prose", "coupe", "charge",
                                 "definitions", "moteur", "autoforme", "ouvertures")}
    eqs = {x["id"]: x for x in equations(etat)}
    cs = controles(eqs, etat)
    h = etat["harmonisation"]
    return {"source": SOURCE, "certificat": cert, "equations": list(eqs.values()),
            "controles": cs,
            "conclusion": {
                "controles_verts": sum(1 for c in cs if c["ok"]), "controles_total": len(cs),
                "equations": len(eqs),
                "statuts_par_label": {st: sum(1 for x in eqs.values() if x["statut"] == st)
                                      for st in FB.STATUTS},
                "enonce_harmonisation":
                    "sur le corpus publié, la ligne calculée est la seule ligne qui porte les "
                    "nombres vérifiables ; rendue dans les trois langues elle couvre "
                    f"{h['avec_ligne']['fr']}/{h['total']} lignes par langue, contre "
                    f"{h['sans_ligne']['fr']}, {h['sans_ligne']['en']} et {h['sans_ligne']['ar']} "
                    "quand on la retire",
                "pages": cert["corpus"]["nb_pages"], "lignes": h["total"],
                "couverture_sans": h["sans_ligne"], "couverture_avec": h["avec_ligne"],
                "lignes_non_traduites": cert["lignes_de_controle"]["total"],
                "pages_au_dessus_du_seuil": cert["prose"]["total_pages_au_dessus"],
                "seuil_mots": SEUIL_PHRASE,
                "racine_merkle_sha256": cert["racine_merkle_sha256"]}}


def verifier(donnees: Dict[str, Any]) -> bool:
    return all(c["ok"] for c in donnees["controles"])


# ─── 6. Artefacts -------------------------------------------------------------

def octets_json(cert: Dict[str, Any]) -> bytes:
    return (json.dumps(cert, ensure_ascii=False, indent=2, sort_keys=True,
                       default=str) + "\n").encode("utf-8")


def octets_csv() -> bytes:
    entetes = ["dossier", "page", "langue", "lignes_equation", "lignes_controle",
               "chemins_machines", "badges", "mots_de_prose", "phrases", "moyenne_mots",
               "mots_max", "part_au_dessus_du_seuil", "mots_avant_premier_tableau"]
    lignes: List[List[Any]] = [entetes]
    for chemin, texte in sorted(_charger().items()):
        R = _lignes(texte)
        phrases = _phrases(_prose(texte))
        mots = [_mots(p) for p in phrases]
        premier = texte.find("<table")
        lignes.append([chemin.split("/")[0],
                       re.sub(r"(_en|_ar)?\.html$", "", chemin.split("/")[-1]),
                       _langue(chemin),
                       sum(1 for k in R if k.startswith("EQ")),
                       sum(1 for k in R if k.startswith("C")),
                       sum(1 for k, v in R.items() if k.startswith("EQ")
                           and CHEMIN_MACHINE.search(v["chemin"])),
                       len(BADGE.findall(texte)),
                       sum(_mots(b) for b in _prose(texte)), len(phrases),
                       round(sum(mots) / len(mots), 2) if mots else 0,
                       max(mots) if mots else 0,
                       round(100.0 * sum(1 for m in mots if m > SEUIL_PHRASE) / len(mots), 1)
                       if mots else 0,
                       sum(_mots(p) for p in _phrases(_prose(
                           texte[:premier] if premier >= 0 else texte)))])
    tampon = "\r\n".join(";".join(str(v).replace(".", ",") for v in l) for l in lignes)
    return b"\xef\xbb\xbf" + (tampon + "\r\n").encode("utf-8")


def regles_markdown(cert: Dict[str, Any]) -> bytes:
    h, pr, de, ou, au = (cert["harmonisation"], cert["prose"], cert["definitions"],
                         cert["ouvertures"], cert["autoforme"])
    corps = [
        "# REDACTION — harmoniser ce qui est écrit",
        "",
        f"Corpus mesuré : **{cert['corpus']['nb_pages']} pages**, {cert['corpus']['nb_trios']} "
        f"trios FR/EN/AR, {h['total']} lignes d'équation par langue.",
        "",
        "## Les six règles tenues par le corpus",
        "",
        "1. **Un rang, trois langues.** Le badge porte sa classe `o`/`p`/`s` partout, seul le mot "
        f"se traduit : {cert['badges']['totaux_par_langue']['fr']} badges alignés.",
        "2. **La ligne calculée n'est pas une phrase.** Elle est rendue identiquement dans les "
        f"trois langues : {h['avec_ligne']['fr']}/{h['total']} lignes portant les nombres, contre "
        f"{h['sans_ligne']['en']}/{h['total']} en anglais et {h['sans_ligne']['ar']}/{h['total']} "
        "en arabe quand on la retire.",
        "3. **Un chemin de vérification par équation.** "
        f"{cert['chemins_machine']['avec_chemin']}/{cert['chemins_machine']['total']} lignes "
        "donnent `module.py → une ou plusieurs fonctions() → Cnn` dans les trois langues, dont "
        f"{cert['chemins_machine']['une_seule_fonction']} en une seule fonction.",
        f"4. **Une idée par ligne, {SEUIL_PHRASE} mots au plus.** Ce module s'y tient : "
        f"{au['lignes_mesurees']} lignes auto-mesurées, maximum {au['mots_max']} mots.",
        "5. **La coupe respecte la langue.** L'arabe sépare par « ؛ » : "
        f"{cert['coupe']['points_virgule_arabes']} occurrences ; l'ignorer déplace la moyenne de "
        f"{cert['coupe']['ecart']} mots.",
        f"6. **Ce qui n'est pas traduit est écrit.** {cert['lignes_de_controle']['total']} lignes "
        f"de contrôle restent françaises en EN et AR ; {de['dfn']} balise `<dfn>` sur "
        f"{de['nb_pages']} pages.",
        "",
        "## Les phrases longues, mesurées",
        "",
        f"- moyennes de mots par phrase : FR {pr['par_langue']['fr']['moyenne_min']}–"
        f"{pr['par_langue']['fr']['moyenne_max']}, EN {pr['par_langue']['en']['moyenne_min']}–"
        f"{pr['par_langue']['en']['moyenne_max']}, AR {pr['par_langue']['ar']['moyenne_min']}–"
        f"{pr['par_langue']['ar']['moyenne_max']}",
        f"- phrase la plus longue : {pr['page_la_plus_longue']['mots']} mots, page "
        f"{pr['page_la_plus_longue']['page']}",
        f"- pages au-dessus de 10 % de phrases longues : {pr['pages_au_dessus_de_10_pct']}",
        "",
        "## Ce qui reste ouvert",
        "",
        *[f"- {l}" for l in ou["liste"]],
        "",
        "## Ce que cela ne dit pas",
        "",
        *[f"- {l}" for l in cert["limites"]],
        "",
        f"Racine Merkle : `{cert['racine_merkle_sha256']}`",
        "",
    ]
    return "\n".join(corps).encode("utf-8")


def ecrire_artefacts(cert: Dict[str, Any], vers: Path = ARTEFACTS) -> Dict[str, str]:
    vers.mkdir(parents=True, exist_ok=True)
    rendu = {"certificat.json": octets_json(cert),
             "mesures_par_page.csv": octets_csv(),
             "regles_harmonisation.md": regles_markdown(cert)}
    for nom, octets in rendu.items():
        (vers / nom).write_bytes(octets)
    return {nom: f"{len(octets)} octets" for nom, octets in rendu.items()}


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    donnees = resoudre()
    if "--ecrit" in sys.argv[1:]:
        donnees["artefacts"] = ecrire_artefacts(donnees["certificat"])
    cert = donnees["certificat"]
    sortie = {
        "source": {k: v for k, v in donnees["source"].items() if k != "video"},
        "enonce": donnees["conclusion"]["enonce_harmonisation"],
        "corpus": {k: cert["corpus"][k] for k in ("nb_pages", "nb_trios", "pages_par_langue",
                                                  "orphelines")},
        "harmonisation": {k: cert["harmonisation"][k] for k in
                          ("total", "sans_ligne", "avec_ligne", "avant_declare",
                           "ablation_fidele", "lignes_identiques", "lignes_comparees", "gagne",
                           "sans_decodage_entites", "ecart_decodage")},
        "controles_non_traduits": cert["lignes_de_controle"]["total"],
        "prose": cert["prose"]["par_langue"],
        "coupe_arabe": {k: cert["coupe"][k] for k in
                        ("points_virgule_arabes", "moyenne_avec_coupe", "moyenne_sans_coupe",
                         "ecart")},
        "charge_acces": {k: cert["charge"][k] for k in ("min", "max", "moyenne", "part_avant")},
        "definitions": {k: cert["definitions"][k] for k in ("dfn", "abbr", "glossaire")},
        "moteur": {k: cert["moteur"][k] for k in ("ligne_de_branche", "span_calcul_ecrite",
                                                  "css_calcul", "garde_de_ligne_calculee")},
        "autoforme": cert["autoforme"],
        "ouvertures": cert["ouvertures"]["liste"],
        "limites": cert["limites"],
        "racine_merkle_sha256": cert["racine_merkle_sha256"],
        "controles": donnees["controles"],
        "equations": [{k: v for k, v in x.items() if k != "detail"} for x in donnees["equations"]],
        "conclusion": donnees["conclusion"],
        "artefacts": donnees.get("artefacts", {}),
    }
    print(json.dumps(sortie, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    sys.exit(0 if verifier(donnees) else 1)
