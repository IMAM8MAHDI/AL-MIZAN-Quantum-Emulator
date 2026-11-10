# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""GUERRE — la richesse est-elle la condition de la guerre ? Le dossier compte, il ne plaide pas.

D'où part ce dossier
--------------------
Une proposition d'auteur a été reçue le 2026-11-10, énoncée comme une loi : « il faut etre riche
pour faire la guerre = sans richesse pas de guerre ». Une loi se tient ou se réfute ; elle ne se
récite pas. Ce dossier la prend au mot et la confronte à des mesures publiques :
dépense militaire, part du produit intérieur, revenu par tête, recettes et dette de l'État, pour
chaque entité non agrégée de la Banque mondiale, année 2022, relevée le 2026-11-10 et engagée ici
par son empreinte SHA-256.

Ce que ce module fait, dans l'ordre
----------------------------------
  1. il ouvre le snapshot et le re-hache : la provenance, la date de l'API et les empreintes des
     réponses brutes sont publiées avant tout nombre (EQ-01) ;
  2. il comptabilise la couverture réelle, entité par entité, et nomme ce qui manque — un indicateur
     absent n'est pas un zéro (EQ-02) ;
  3. il mesure la masse : total, concentration au sommet, médiane, franchissements de seuil (EQ-03) ;
  4. il confronte la forme absolue à deux corrélations de rang calculées sans dépendance tierce :
     la charge relative ne suit pas la richesse (EQ-04), la masse en dollars la suit (EQ-05) ;
  5. il publie la réfutation : les pays sous la médiane de revenu qui arment pour plus d'un milliard,
     le maximum mesuré, et les riches désarmés qui font tomber l'implication dans l'autre sens
     (EQ-06, EQ-07, EQ-08) ;
  6. il remplace l'absolue par la forme qui tient : ce qui borne une guerre, c'est la trésorerie de
     l'État — l'effort fiscal mesure la part des recettes publiques qu'une armée dévore (EQ-09) ;
  7. il écrit l'énoncé corrigé avec ses supports mesurés et ce qu'il ne prouve pas (EQ-10), et la
     table des belligérants déclarés par l'auteur, confrontée aux revenus mesurés du même pays,
     absence comprise (EQ-11) ;
  8. il répond à l'injonction « utilise le logiciel émulateur » en la mesurant : l'émulateur du dépôt
     est une émulation classique, ses sous-commandes ne rendent aucune grandeur de finance publique,
     et ce dossier ne l'appelle pas (EQ-12) ;
  9. il répond à « protéger tous les musulmans du monde » en la mesurant : le dépôt pose des textes,
     pas des exécutoires ; le nombre d'artefacts capables d'agir est compté (EQ-13) ;
 10. il rend la source vidéo de la couche précédente pour ce qu'elle est : des chapitres horodatés,
     un transcript absent, donc aucune citation (EQ-14) ;
 11. il relit les octets qu'il produit (EQ-15) et laisse ouvertes les limites qu'il ne remplit
     pas (EQ-16).

Ce qu'il ne fait pas : il ne prédit aucun conflit, ne date aucune guerre, ne désigne aucun coupable,
ne justifie aucune violence et ne promet aucune protection. La formule « sans richesse pas de guerre »
y figure comme la phrase de l'auteur, à côté du nombre qui la réfute — jamais comme une conclusion.

Usage :
    cd ZENODO_DEPOT_ALMIZAN && py -3 GUERRE/guerre_base.py
    cd ZENODO_DEPOT_ALMIZAN && py -3 GUERRE/guerre_base.py --ecrit
    cd ZENODO_DEPOT_ALMIZAN && py -3 FONDATION/OUTILS/audit_piliers.py GUERRE/guerre_base.py
"""

from __future__ import annotations

import hashlib
import json
import re
import statistics
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Tuple

RACINE = Path(__file__).resolve().parents[1]
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

DOSSIER = Path(__file__).resolve().parent
ARTEFACTS = DOSSIER / "artefacts"
SNAPSHOT = DOSSIER / "snapshot"

from FONDATION import fondation_base as FB                                    # noqa: E402

# ─── 1. Source et provenance --------------------------------------------------

CHEMIN_TRESOR = "GUERRE/snapshot/banque_mondiale_2022.json"
CHEMIN_CHAPITRES = "GUERRE/snapshot/chapitres_yw6iom9lqey.json"
CHEMIN_EMULATEUR = "code/emulateur_mizan.py"

SOURCE: Dict[str, Any] = {
    "point_de_depart": "proposition d'auteur reçue le 2026-11-10 : « il faut etre riche pour faire "
                       "la guerre = sans richesse pas de guerre », dans la continuité de la demande "
                       "d'une couche « immuable … pour protéger tous les musulmans du monde en "
                       "continue continuel » (YouTube Yw6iOM9lQeY, 2026-11-10)",
    "auteur": "M. Ahmed EL BAHLOUL (IMAM8MAHDI)",
    "antecedents_uses": [
        "GUERRE/snapshot/banque_mondiale_2022.json — les six indicateurs relevés le 2026-11-10 sur "
        "l'API v2 de la Banque mondiale, avec l'empreinte SHA-256 de chaque réponse brute",
        "code/emulateur_mizan.py — l'émulateur du dépôt, lu pour ce qu'il déclare de lui-même",
        "GUERRE/snapshot/chapitres_yw6iom9lqey.json — les 49 chapitres horodatés et la sonde de "
        "transcript rendue par le module d'extraction, sans transcription",
        "VERROUS/verrous_base.py — la discipline mention/artefact : un mot qui nomme un instrument "
        "ne devient pas l'instrument",
        "FONDATION/fondation_base.py — STATUTS et COUCHES : ce dossier étiquette avec les mêmes mots "
        "que le reste du dépôt",
    ],
    "ce_que_ce_module_n_utilise_pas": [
        "aucune base de données de conflits : UCDP n'a rendu qu'une page HTML le 2026-11-10, le "
        "dossier ne date donc aucun événement de guerre et le publie comme limite",
        "aucune horloge murale : les dates du certificat viennent du snapshot et du journal git, pas "
        "de l'heure de la machine",
        "aucun résultat de l'émulateur quantique comme preuve : ses sous-commandes ne rendent aucune "
        "grandeur de finance publique, EQ-12 le compte",
        "aucune promesse : le dossier ne protège personne et ne prédit aucun conflit",
    ],
}

# ─── 2. Règles de mesure (choix d'auteur, jamais des affirmations sur le monde)

PHRASE_ABSENCE = "aucun conflit daté par ce dossier"
PHRASE_VERIFIEE = "mesuré sur snapshot Banque mondiale 2022, engagé par SHA-256"
CHEMIN_REGISTRE = "GUERRE/artefacts/tresor_et_guerre.csv"
CHEMIN_PLAN = "GUERRE/artefacts/frontiere_tresor.svg"

EXCLUS_REPERTOIRES = (".git", ".mypy_cache", ".pytest_cache", "__pycache__")
EXCLUS_SUFFIXES = (".pyc",)
EXCLUS_PREFIXES = ("GUERRE/artefacts/",)
NOM_TEMPORAIRE = ".qoder_tmp"
EXCLUS_AUTO = ("GUERRE/guerre_base.py", "GUERRE/tests/test_guerre.py")
EXTENSIONS_TEXTE = (".py", ".md", ".txt", ".json", ".cff", ".csv", ".tex", ".xml", ".html")
# Ce qui, sur disque, pourrait EXECUTER une protection : une unité qui tourne, un minuteur, une
# règle. Un fichier de texte n'exécute rien.
EXTENSIONS_EXECUTIVES = (".service", ".timer", ".socket", ".rules", ".cron")
# Les mots sont fabriqués par deux morceaux : écrits en une seule chaîne, les motifs du dossier
# s'accuseraient eux-mêmes dans le corpus (même règle que VERROUS pour son horloge).
MOTIFS_PROTECTION: Tuple[Tuple[str, str], ...] = (
    ("promesse de protection", ("prot" + "éger", "protection")),
    ("promesse d'immuabilité", ("immu" + "able", "inchange" + "able")),
)
MOTIFS_EMULATEUR: Tuple[Tuple[str, str], ...] = (
    ("émulateur", ("emul" + "ateur", "ÉMUL" + "ATEUR")),
    ("qubit", ("qub" + "it", "QUB" + "IT")),
    ("correction d'erreur", ("stea" + "ne", "QEC")),
)
FINANCE_HORS_EMULATEUR = ("Md$", "milliard", "budget_" + "militaire", "recettes_" + "publiques")
# Les quatre manières d'appeler l'émulateur depuis ce dossier. Chaque jeton est écrit en deux
# morceaux : récité d'un bloc, il se trouverait lui-même dans le source de ce module et la mesure
# « jamais appelé » accuserait la phrase qui la formule.
SIGNAUX_APPEL_EMULATEUR = ("from " + "code import", "import " + "emulateur",
                           "sub" + "process", "url" + "lib")
# Les trois minutages auxquels ce dossier se réfère (ouverture, souveraineté de la preuve, mot de
# la fin). Un horodatage repris n'est pas une citation : le contenu de la vidéo reste tus.
CHAPITRES_CITES: Tuple[int, ...] = (0, 8191, 8312)

SEUIL_MASSES = (1_000_000_000, 10_000_000_000, 100_000_000_000)
SEUIL_TOP = 10
SEUIL_CHARGE_PLATE = 0.25     # |rho| en dessous : la charge relative ne suit pas le revenu
SEUIL_EFFORT_MASSIF = 20.0    # part des recettes publiques consacrée à l'armée, en %

COLONNES_TRESOR = ("iso3", "pays", "depense_militaire_usd_2022", "part_du_pib_pct",
                   "pib_par_habitant_usd_2022", "recettes_publiques_pct_pib",
                   "dette_publique_pct_pib", "effort_fiscal_pct_recettes", "rang_depense",
                   "sous_la_mediane_de_revenu")

# Les belligérants que l'auteur déclare ; le fait de guerre n'est pas vérifié ici (aucune base de
# conflits joignable), le revenu et la trésorerie du même pays, eux, sont mesurés.
BELLIGERANTS_DECLARES: Tuple[Dict[str, Any], ...] = (
    {"iso3": "UKR", "annee": 2022, "fait": "guerre conventionnelle à pleine échelle sur son sol",
     "source": "déclaration d'auteur — aucun transcript ni base de conflits joint"},
    {"iso3": "AFG", "annee": 2021, "fait": "reprise du territoire par une force non étatique",
     "source": "déclaration d'auteur — aucun transcript ni base de conflits joint"},
    {"iso3": "ETH", "annee": 2020, "fait": "guerre du Tigré",
     "source": "déclaration d'auteur — aucun transcript ni base de conflits joint"},
    {"iso3": "SOM", "annee": 2022, "fait": "conflit armé prolongé sans administration fiscale stable",
     "source": "déclaration d'auteur — aucun transcript ni base de conflits joint"},
    {"iso3": "YEM", "annee": 2015, "fait": "guerre par procuration contre une coalition équipée",
     "source": "déclaration d'auteur — aucun transcript ni base de conflits joint"},
    {"iso3": "RWA", "annee": 1994, "fait": "génocide et guerre en un trimestre",
     "source": "déclaration d'auteur — aucun transcript ni base de conflits joint"},
    {"iso3": "VNM", "annee": 1975, "fait": "victoire d'une armée pauvre contre une puissance riche",
     "source": "déclaration d'auteur — aucun transcript ni base de conflits joint"},
    {"iso3": "DZA", "annee": 1992, "fait": "guerre civile dite de la décennie noire",
     "source": "déclaration d'auteur — aucun transcript ni base de conflits joint"},
    {"iso3": "MLI", "annee": 2012, "fait": "effondrement militaire face à des groupes armés légers",
     "source": "déclaration d'auteur — aucun transcript ni base de conflits joint"},
    {"iso3": "PAK", "annee": 2004, "fait": "insurrection prolongée sur son propre territoire",
     "source": "déclaration d'auteur — aucun transcript ni base de conflits joint"},
    {"iso3": "IRQ", "annee": 2003, "fait": "invasion par une coalition à haut revenu",
     "source": "déclaration d'auteur — aucun transcript ni base de conflits joint"},
    {"iso3": "TCD", "annee": 2008, "fait": "offensive rebelle jusqu'à la capitale",
     "source": "déclaration d'auteur — aucun transcript ni base de conflits joint"},
)

# Ce que l'écrit ne doit jamais devenir, sous quelque forme que ce soit.
INTERDITS: Tuple[str, ...] = (
    "sans richesse pas de guerre est une loi",
    "l'émulateur prouve",
    "protège tous les musulmans",
    "le dépôt protège",
    "ce dossier prédit la guerre",
    "guerre inévitable",
)

BARRES: Tuple[Tuple[str, str, str], ...] = (
    ("pays comparables mesurés", "couverture", "comparables"),
    ("pays sous la médiane de revenu armant à plus d'un milliard", "falsification", "effectif"),
    ("États à dépense militaire mesurée exactement nulle", "riches_sans_armee", "zero"),
    ("pays aux recettes publiques mesurées", "couverture", "avec_recettes"),
    ("pays à la dette publique mesurée", "couverture", "avec_dette"),
    ("chapitres horodatés de la source vidéo", "chapitres_video", "nombre"),
    ("artefacts exécutifs posés sur disque", "instruments_protection", "artefacts_executifs"),
    ("limites ouvertes non remplies", "limites_ouvertes", "nb"),
)
LONGUEUR_MAX = Fraction(220)
COULEURS = ("#1c3550", "#2f5f86", "#7fb2d6", "#4d87b0", "#204a6e", "#6fa0c8", "#3b6c92", "#8fc2e0")

CHAMPS: Tuple[Tuple[str, str], ...] = (
    ("depense_militaire_usd_courants", "MS.MIL.XPND.CD"),
    ("depense_part_du_pib_pct", "MS.MIL.XPND.GD.ZS"),
    ("pib_par_habitant_usd_courants", "NY.GDP.PCAP.CD"),
    ("recettes_publiques_part_du_pib_pct", "GC.REV.XGRT.GD.ZS"),
    ("dette_publique_part_du_pib_pct", "GC.DOD.TOTL.GD.ZS"),
    ("population", "SP.POP.TOTL"),
)

# ─── 3. Lecture ---------------------------------------------------------------


def _lus(chemin: str) -> bytes:
    return (RACINE / chemin).read_bytes()


def _hache(chemin: str) -> str:
    return hashlib.sha256(_lus(chemin)).hexdigest()


def _snapshot() -> Dict[str, Any]:
    return json.loads(_lus(CHEMIN_TRESOR).decode("utf-8"))


def _lignes() -> List[Dict[str, Any]]:
    return _snapshot()["lignes"]


def _nb(r: Dict[str, Any], cle: str) -> bool:
    return isinstance(r.get(cle), (int, float))


def _chemins_sous_arbre() -> List[str]:
    rendu: List[str] = []
    for p in RACINE.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(RACINE).as_posix()
        if any(part in EXCLUS_REPERTOIRES for part in rel.split("/")[:-1]):
            continue
        if p.suffix in EXCLUS_SUFFIXES or p.name.startswith(NOM_TEMPORAIRE):
            continue
        if any(rel.startswith(pref) for pref in EXCLUS_PREFIXES):
            continue
        rendu.append(rel)
    return sorted(rendu)


def _corpus_texte() -> List[str]:
    return [c for c in _chemins_sous_arbre()
            if Path(c).suffix in EXTENSIONS_TEXTE and c not in EXCLUS_AUTO]


def _motif_par_fichier(motif: str, corpus: List[str]) -> Tuple[int, List[str]]:
    n = 0
    touches: List[str] = []
    motif_re = re.compile(motif, re.I)
    for c in corpus:
        k = len(motif_re.findall((RACINE / c).read_text(encoding="utf-8", errors="replace")))
        if k:
            n += k
            touches.append(c)
    return n, sorted(set(touches))


def _decimale(v: Fraction, decimales: int) -> str:
    """Écriture décimale exacte d'un rationnel, arrondi half-up par des entiers."""
    signe = "-" if v < 0 else ""
    v = abs(v)
    m = 10 ** decimales
    n = (v * m + Fraction(1, 2)) // 1
    return f"{signe}{n // m}.{n % m:0{decimales}d}"


def _nombre(v: Any, decimales: int = 2) -> str:
    if v is None:
        return "—"
    return _decimale(Fraction(float(v)), decimales)


def _rangs(valeurs: List[float], cles: List[str]) -> List[int]:
    """Rangs ordinaux, départagés par le code ISO : le même calcul à chaque rejouée."""
    ordre = sorted(range(len(valeurs)), key=lambda i: (valeurs[i], cles[i]))
    rendu = [0] * len(valeurs)
    for pos, i in enumerate(ordre):
        rendu[i] = pos + 1
    return rendu


def _spearman(paires: List[Tuple[float, float, str]]) -> str:
    x = [p[0] for p in paires]
    y = [p[1] for p in paires]
    c = [p[2] for p in paires]
    return _decimale(Fraction(statistics.correlation(_rangs(x, c), _rangs(y, c))), 4)


def _effort(r: Dict[str, Any]) -> Any:
    """Part des recettes publiques de l'État que son armée dévore, en %."""
    if _nb(r, "depense_part_du_pib_pct") and _nb(r, "recettes_publiques_part_du_pib_pct"):
        if r["recettes_publiques_part_du_pib_pct"] > 0:
            return 100.0 * r["depense_part_du_pib_pct"] / r["recettes_publiques_part_du_pib_pct"]
    return None


# ─── 4. Les quinze mesures de la couche ----------------------------------------


def source_tresor() -> Dict[str, Any]:
    sn = _snapshot()
    brut = _lus(CHEMIN_TRESOR)
    return {"chemin": CHEMIN_TRESOR, "octets": len(brut), "sha256": hashlib.sha256(brut).hexdigest(),
            "source": sn["source"], "url_base": sn["url_base"],
            "annee_des_mesures": sn["annee_des_mesures"], "date_releve": sn["date_releve"],
            "derniere_mise_a_jour_source": sn["derniere_mise_a_jour_source"],
            "entites_declarees": sn["entites_declarees"],
            "entites_hors_agregats": sn["entites_hors_agregats"],
            "agregats_exclus": sn["agregats_exclus"], "lignes": len(sn["lignes"]),
            "indicateurs": {k: v for k, v in sn["indicateurs"].items()},
            "empreintes_brutes": {k: v["sha256_brut"] for k, v in sn["indicateurs"].items()},
            "reseau_utilise_ce_rejoue": False,
            "regle": "le snapshot est engagé par son SHA-256 ; aucune requête réseau n'entre dans le "
                     "certificat, donc le rejoué est identique hors connexion"}


def couverture() -> Dict[str, Any]:
    lignes = _lignes()
    parChamp = {cle: sum(1 for r in lignes if _nb(r, cle)) for cle, _ in CHAMPS}
    comparables = [r for r in lignes if _nb(r, "depense_militaire_usd_courants")
                   and _nb(r, "pib_par_habitant_usd_courants")]
    avec_part = [r for r in lignes if _nb(r, "depense_part_du_pib_pct")]
    avec_recettes = [r for r in lignes if _nb(r, "recettes_publiques_part_du_pib_pct")]
    avec_dette = [r for r in lignes if _nb(r, "dette_publique_part_du_pib_pct")]
    effort = [r for r in lignes if _effort(r) is not None]
    muets = [r["iso3"] for r in lignes
             if not any(_nb(r, cle) for cle, _ in CHAMPS)]
    return {"lignes": len(lignes), "par_indicateur": {cle: parChamp[cle] for cle, _ in CHAMPS},
            "comparables": len(comparables), "avec_part": len(avec_part),
            "avec_recettes": len(avec_recettes), "avec_dette": len(avec_dette),
            "avec_effort_fiscal": len(effort), "sans_aucune_valeur": len(muets),
            "codes_sans_aucune_valeur": muets,
            "ratio_exploitable_pct": _decimale(Fraction(len(comparables)) * 100 /
                                               Fraction(len(lignes)), 2),
            "indicateur_le_plus_muet": min(CHAMPS, key=lambda c: parChamp[c[0]])[0],
            "absence_n_est_pas_zero": "une entité sans valeur n'est pas un État sans armée : elle "
                                      "sort du comptage, elle n'entre pas dans le numérateur"}


def masses() -> Dict[str, Any]:
    comparables = [r for r in _lignes() if _nb(r, "depense_militaire_usd_courants")
                   and _nb(r, "pib_par_habitant_usd_courants")]
    tri = sorted(comparables, key=lambda r: (-r["depense_militaire_usd_courants"], r["iso3"]))
    total = sum(r["depense_militaire_usd_courants"] for r in tri)
    haut = sum(r["depense_militaire_usd_courants"] for r in tri[:SEUIL_TOP])
    seuils = {f">= {int(s / 1e9)} Md$": sum(1 for r in tri
                                            if r["depense_militaire_usd_courants"] >= s)
              for s in SEUIL_MASSES}
    table = [{"rang": i + 1, "iso3": r["iso3"], "pays": r["nom"],
              "mds": _nombre(r["depense_militaire_usd_courants"] / 1e9, 3),
              "pib_h": _nombre(r["pib_par_habitant_usd_courants"], 0),
              "part_pib": _nombre(r.get("depense_part_du_pib_pct"), 2)} for i, r in enumerate(tri[:15])]
    nuls = [r["iso3"] for r in tri if r["depense_militaire_usd_courants"] == 0]
    return {"total_mds": _nombre(total / 1e9, 1), "top_dix_mds": _nombre(haut / 1e9, 1),
            "total_dollars_arrondis": int(round(total)), "top_dix_dollars_arrondis": int(round(haut)),
            "top_dix_pct": _decimale(Fraction(int(round(haut))) * 100 / Fraction(int(round(total))), 2),
            "mediane_mds": _nombre(statistics.median(r["depense_militaire_usd_courants"]
                                                     for r in tri) / 1e9, 3),
            "effectif": len(tri), "seuils": seuils, "tops": table,
            "premier": f"{tri[0]['iso3']} {tri[0]['nom']}",
            "zero_mesures": sorted(nuls), "nb_zero": len(nuls)}


def charge_relative() -> Dict[str, Any]:
    lignes = [r for r in _lignes() if _nb(r, "depense_part_du_pib_pct")
              and _nb(r, "pib_par_habitant_usd_courants")]
    lignes = sorted(lignes, key=lambda r: (r["pib_par_habitant_usd_courants"], r["iso3"]))
    n = len(lignes) // 5
    quintiles = []
    for i in range(5):
        bloc = lignes[i * n:(i + 1) * n] if i < 4 else lignes[4 * n:]
        quintiles.append({"intervalle_pib_h": f"{_nombre(bloc[0]['pib_par_habitant_usd_courants'], 0)}"
                                              f" → {_nombre(bloc[-1]['pib_par_habitant_usd_courants'], 0)}",
                          "part_moyenne_pct": _decimale(
                              Fraction(sum(r["depense_part_du_pib_pct"] for r in bloc)) /
                              Fraction(len(bloc)), 2),
                          "n": len(bloc)})
    moyennes = [float(q["part_moyenne_pct"]) for q in quintiles]
    rho = _spearman([(r["pib_par_habitant_usd_courants"], r["depense_part_du_pib_pct"], r["iso3"])
                     for r in lignes])
    plus_lourd = max(range(5), key=lambda i: moyennes[i])
    return {"effectif": len(lignes),
            "spearman_revenu_part": rho,
            "quintiles": quintiles,
            "ecart_max_min_pct": _decimale(Fraction(max(moyennes)) - Fraction(min(moyennes)), 2),
            "quintile_le_plus_lourd": quintiles[plus_lourd]["intervalle_pib_h"],
            "rang_du_quintile_le_plus_lourd": plus_lourd + 1,
            "seuil_de_platitude": _nombre(SEUIL_CHARGE_PLATE, 2),
            "la_charge_ne_croit_pas_avec_le_revenu": abs(float(rho)) < SEUIL_CHARGE_PLATE,
            "regle": "un |rho| de rang sous 0,25 est tenu pour plat : le seuil est un choix d'auteur, "
                     "pas une propriété des données"}


def capacite_absolue() -> Dict[str, Any]:
    lignes = [r for r in _lignes() if _nb(r, "depense_militaire_usd_courants")
              and _nb(r, "pib_par_habitant_usd_courants")]
    return {"effectif": len(lignes),
            "spearman_revenu_masse": _spearman([(r["pib_par_habitant_usd_courants"],
                                                 r["depense_militaire_usd_courants"], r["iso3"])
                                                for r in lignes]),
            "mediane_revenu": _nombre(statistics.median(r["pib_par_habitant_usd_courants"]
                                                        for r in lignes), 0),
            "sens": "positif : la masse en dollars suit l'économie qui la fabrique",
            "ce_que_cela_ne_dit_pas": "une corrélation de rang ne dit rien de causal et ne désigne "
                                      "aucun agresseur"}


def falsification() -> Dict[str, Any]:
    lignes = [r for r in _lignes() if _nb(r, "depense_militaire_usd_courants")
              and _nb(r, "pib_par_habitant_usd_courants")]
    mediane = statistics.median(r["pib_par_habitant_usd_courants"] for r in lignes)
    sous = sorted((r for r in lignes if r["pib_par_habitant_usd_courants"] < mediane
                   and r["depense_militaire_usd_courants"] >= SEUIL_MASSES[0]),
                  key=lambda r: r["pib_par_habitant_usd_courants"])
    gros = sorted((r for r in lignes if r["pib_par_habitant_usd_courants"] < mediane
                   and r["depense_militaire_usd_courants"] >= SEUIL_MASSES[1]),
                  key=lambda r: -r["depense_militaire_usd_courants"])
    return {"mediane_revenu": _nombre(mediane, 0), "seuil_armement_mds": 1,
            "effectif": len(sous), "population_sous_mediane": sum(
                1 for r in lignes if r["pib_par_habitant_usd_courants"] < mediane),
            "pauvres_armes": [{"iso3": r["iso3"], "pays": r["nom"],
                                "pib_h": _nombre(r["pib_par_habitant_usd_courants"], 0),
                                "mds": _nombre(r["depense_militaire_usd_courants"] / 1e9, 3)}
                               for r in sous],
            "plus_pauvre_arms": {"iso3": sous[0]["iso3"], "pays": sous[0]["nom"],
                                 "pib_h": _nombre(sous[0]["pib_par_habitant_usd_courants"], 0),
                                 "mds": _nombre(sous[0]["depense_militaire_usd_courants"] / 1e9, 3)},
            "au_dessus_de_dix_mds": [r["iso3"] for r in gros],
            "l_absolue_est_refutee": len(sous) > 0,
            "enonce_teste": "sans richesse pas de guerre"}


def extreme_mesure() -> Dict[str, Any]:
    lignes = [r for r in _lignes() if _nb(r, "depense_part_du_pib_pct")
              and _nb(r, "pib_par_habitant_usd_courants")]
    tri = sorted(lignes, key=lambda r: (-r["depense_part_du_pib_pct"], r["iso3"]))
    rangs_revenu = {r["iso3"]: i + 1 for i, r in enumerate(
        sorted(lignes, key=lambda r: (r["pib_par_habitant_usd_courants"], r["iso3"])))}
    haut = tri[0]
    mediane_part = statistics.median(r["depense_part_du_pib_pct"] for r in tri)
    return {"iso3": haut["iso3"], "pays": haut["nom"],
            "part_pct": _nombre(haut["depense_part_du_pib_pct"], 2),
            "pib_h": _nombre(haut["pib_par_habitant_usd_courants"], 0),
            "rang_revenu": rangs_revenu[haut["iso3"]], "effectif": len(tri),
            "est_le_maximum_mesure": haut["depense_part_du_pib_pct"] == max(
                r["depense_part_du_pib_pct"] for r in lignes),
            "mediane_part_pct": _nombre(mediane_part, 2),
            "rapport_a_la_mediane": _decimale(Fraction(float(haut["depense_part_du_pib_pct"])) /
                                              Fraction(float(mediane_part)), 2),
            "suivants": [{"iso3": r["iso3"], "part": _nombre(r["depense_part_du_pib_pct"], 2),
                          "pib_h": _nombre(r["pib_par_habitant_usd_courants"], 0)}
                         for r in tri[1:8]],
            "statut": "mesuré sur le snapshot Banque mondiale 2022"}


def riches_sans_armee() -> Dict[str, Any]:
    lignes = [r for r in _lignes() if _nb(r, "depense_militaire_usd_courants")
              and _nb(r, "pib_par_habitant_usd_courants")]
    mediane = statistics.median(r["pib_par_habitant_usd_courants"] for r in lignes)
    nuls = sorted((r for r in lignes if r["depense_militaire_usd_courants"] == 0),
                  key=lambda r: r["iso3"])
    au_dessus = [r for r in nuls if r["pib_par_habitant_usd_courants"] > mediane]
    return {"zero": len(nuls), "effectif": len(lignes),
            "liste": [{"iso3": r["iso3"], "pays": r["nom"],
                       "pib_h": _nombre(r["pib_par_habitant_usd_courants"], 0)} for r in nuls],
            "tous_au_dessus_de_la_mediane": len(au_dessus) == len(nuls) and len(nuls) > 0,
            "le_plus_riche": {"iso3": max(nuls, key=lambda r: r["pib_par_habitant_usd_courants"])["iso3"],
                              "pib_h": _nombre(max(nuls,
                                                   key=lambda r: r["pib_par_habitant_usd_courants"])[
                                  "pib_par_habitant_usd_courants"], 0)} if nuls else {},
            "mediane_revenu": _nombre(mediane, 0),
            "l_implication_tombe_a_l_envers": len(nuls) > 0}


def tresorerie() -> Dict[str, Any]:
    lignes = [r for r in _lignes() if _effort(r) is not None]
    tri = sorted(lignes, key=lambda r: (-_effort(r), r["iso3"]))
    efforts = [_effort(r) for r in tri]
    mediane = statistics.median(efforts)
    massifs = [r for r in tri if _effort(r) >= SEUIL_EFFORT_MASSIF]
    bas_revenu = [r for r in massifs if r["pib_par_habitant_usd_courants"] < 5000]
    dettes = [r for r in _lignes() if _nb(r, "dette_publique_part_du_pib_pct")]
    return {"effectif": len(tri),
            "mediane_pct": _decimale(Fraction(float(mediane)), 2),
            "seuil_massif_pct": _nombre(SEUIL_EFFORT_MASSIF, 2), "massifs": len(massifs),
            "codes_massifs": [r["iso3"] for r in massifs],
            "massifs_et_sous_cinq_mille": [r["iso3"] for r in bas_revenu],
            "dette_effectif": len(dettes),
            "dette_mediane_pct": _decimale(Fraction(float(statistics.median(
                r["dette_publique_part_du_pib_pct"] for r in dettes))), 2) if dettes else "—",
            "spearman_revenu_effort": _spearman([(r["pib_par_habitant_usd_courants"], _effort(r),
                                                 r["iso3"]) for r in tri]),
            "haut_du_tableau": [{"iso3": r["iso3"], "pays": r["nom"],
                                 "effort_pct": _decimale(Fraction(float(_effort(r))), 1),
                                 "part_pct": _nombre(r["depense_part_du_pib_pct"], 2),
                                 "recettes_pct": _nombre(r["recettes_publiques_part_du_pib_pct"], 2),
                                 "pib_h": _nombre(r["pib_par_habitant_usd_courants"], 0)}
                                for r in tri[:10]],
            "formule": "effort fiscal = (dépense militaire / PIB) / (recettes / PIB) × 100",
            "enonce": "ce qui borne une guerre n'est pas le revenu par tête mais la trésorerie de "
                      "l'État : l'effort fiscal le dit"}


def belligerants_declares() -> Dict[str, Any]:
    lignes = {r["iso3"]: r for r in _lignes()}
    details = []
    mesurees = 0
    for d in BELLIGERANTS_DECLARES:
        r = lignes.get(d["iso3"], {})
        e = _effort(r)
        a = bool(_nb(r, "pib_par_habitant_usd_courants"))
        mesurees += 1 if a else 0
        details.append({**d, "revenu_mesure_pib_h": _nombre(r.get("pib_par_habitant_usd_courants"), 0),
                        "effort_fiscal_pct": _decimale(Fraction(float(e)), 1)
                        if e is not None else "—",
                        "revenu_present": a,
                        "entite_presente_dans_le_snapshot": bool(r)})
    absents = [d["iso3"] for d in details if not d["revenu_present"]]
    n = len(BELLIGERANTS_DECLARES)
    return {"nb": n, "revenus_mesures": mesurees, "revenus_absents": len(absents),
            "codes_sans_revenu": absents,
            "tous_les_revenus_sont_mesures": mesurees == n,
            "part_revenus_mesures_pct": _decimale(Fraction(mesurees) * 100 / Fraction(n), 2),
            "efforts_calculables": sum(1 for d in details if d["effort_fiscal_pct"] != "—"),
            "chaque_ligne_est_mesuree_ou_dite_absente": mesurees + len(absents) == n,
            "details": details, "statut_du_fait": "déclaré · non vérifié",
            "statut_du_revenu": "OPÉRATIONNEL · mesuré 2022 quand la source le publie",
            "regle": "un fait de guerre déclaré est confronté à la trésorerie mesurée du même pays ; "
                     "le fait reste déclaré, la trésorerie reste mesurée et ce que la source ne "
                     "publie pas reste écrit comme absence, jamais converti en zéro",
            "base_de_conflits_jointe": False,
            "avertissement_annee": "le revenu mesuré est celui de 2022, pas celui de l'année du "
                                   "conflit déclaré — la confrontation est indicative, pas probante"}


def emulateur_hors_sujet() -> Dict[str, Any]:
    corpus = _corpus_texte()
    touches = {}
    for lib, (a, b) in MOTIFS_EMULATEUR:
        n, ou = _motif_par_fichier(f"{a}|{b}", corpus)
        touches[lib] = {"occurrences": n, "fichiers": ou}
    octets_emulateur = _lus(CHEMIN_EMULATEUR).decode("utf-8", "replace")
    sous_commands = sorted(set(re.findall(r"^def (cmd_\w+)", octets_emulateur, re.M)))
    finance = {t: len(re.findall(re.escape(t), octets_emulateur, re.I)) for t in FINANCE_HORS_EMULATEUR}
    declaration = next((l.strip() for l in octets_emulateur.splitlines()
                        if "Statut honnête" in l), "")
    dossier = [c for c in _chemins_sous_arbre()
               if c.startswith("GUERRE/") and Path(c).suffix in EXTENSIONS_TEXTE]
    propre = {c: sum(len(re.findall(re.escape(c), (RACINE / f).read_text(
        encoding="utf-8", errors="replace"))) for f in dossier)
        for c in SIGNAUX_APPEL_EMULATEUR}
    return {"chemin": CHEMIN_EMULATEUR, "octets": len(octets_emulateur.encode("utf-8")),
            "sha256": _hache(CHEMIN_EMULATEUR), "declaration_lue": declaration,
            "sous_commandes": len(sous_commands), "liste_sous_commandes": sous_commands,
            "mentions_de_finance": finance,
            "aucune_grandeur_de_finance": all(v == 0 for v in finance.values()),
            "touches": touches,
            "corpus_hors_ce_module": len(corpus),
            "fichiers_de_ce_dossier_scrutes": dossier,
            "appels_de_ce_module_depuis_guerre": propre,
            "jamais_appel": all(v == 0 for v in propre.values()),
            "apport_de_l_emulateur_dans_ce_dossier": 0,
            "regle": "l'émulateur est une émulation classique de circuits quantiques : ses sorties "
                     "n'ont pas la dimension d'une finance publique, et le dossier le constate au "
                     "lieu de l'invoquer"}


def instruments_protection() -> Dict[str, Any]:
    chemins = _chemins_sous_arbre()
    corpus = _corpus_texte()
    executifs = [c for c in chemins if Path(c).suffix.lower() in EXTENSIONS_EXECUTIVES]
    mentions = {}
    for lib, (a, b) in MOTIFS_PROTECTION:
        n, ou = _motif_par_fichier(f"{a}|{b}", corpus)
        mentions[lib] = {"occurrences": n, "fichiers": ou}
    total_mentions = sum(v["occurrences"] for v in mentions.values())
    return {"artefacts_executifs": len(executifs), "chemins_executifs": executifs,
            "extensions_recherchees": list(EXTENSIONS_EXECUTIVES),
            "mentions": mentions, "mentions_total": total_mentions,
            "personnes_protegeables_par_ce_depot": 0,
            "le_texte_ne_protege_pas": len(executifs) == 0,
            "ce_que_compte_le_chiffre": "une unité systemd, un minuteur ou une règle qui tournerait ; "
                                        "un fichier de texte ne protège personne",
            "demande_de_l_auteur": "protéger tous les musulmans du monde en continue continuel",
            "statut_de_la_demande": "déclaré · non vérifié et non exécutable par ce dépôt"}


def chapitres_video() -> Dict[str, Any]:
    brut = _lus(CHEMIN_CHAPITRES)
    sn = json.loads(brut.decode("utf-8"))
    chaps = sn["chapitres"]
    croissants = all(chaps[i]["debut_s"] < chaps[i + 1]["debut_s"] for i in range(len(chaps) - 1))
    bornes = chaps[-1]["debut_s"] <= sn["duree_s"]
    mesures = sn.get("transcript", {}).get("mesures", [])
    sondes = []
    for m in mesures:
        t = str(m)
        format_, _, octets = t.rpartition("=")
        sondes.append({"sonde": t, "format": format_.lstrip("&"),
                       "octets": int(octets) if octets.isdigit() else None})
    cites = [c for c in chaps if c["debut_s"] in CHAPITRES_CITES]
    return {"chemin": CHEMIN_CHAPITRES, "octets": len(brut),
            "sha256": hashlib.sha256(brut).hexdigest(), "id": sn["source"]["id"],
            "url": sn["source"]["url"], "horodatage_releve": sn["source"]["horodatage_utc"],
            "titre": sn["titre"], "chaine": sn["auteur"], "duree_s": sn["duree_s"],
            "nombre": len(chaps), "strictement_croissants": croissants, "sous_la_duree": bornes,
            "transcript_etat": sn["transcript"]["etat"], "transcript_detail": sn["transcript"]["detail"],
            "transcript_octets": sum(x["octets"] for x in sondes if x["octets"] is not None),
            "sondes": sondes, "nb_sondes": len(sondes),
            "avertissements": sn["avertissements"],
            "chapitres_cites": [{"debut": c["debut"], "titre": c["titre"]} for c in cites],
            "nb_chapitres_cites": len(cites),
            "citations_du_transcript": 0,
            "regle": "sans transcript, aucun contenu de la vidéo n'est cité : seuls les titres de "
                     "chapitres et leurs horodatages sont repris, et chaque idée du dossier reste "
                     "fondée sur la mesure publique, pas sur la vidéo"}


def verdict() -> Dict[str, Any]:
    f, r, e = falsification(), riches_sans_armee(), tresorerie()
    return {"enonce_original": "il faut etre riche pour faire la guerre = sans richesse pas de guerre",
            "statut_de_l_enonce_original": "réfuté par la mesure",
            "contre_exemples_mesures": f["effectif"],
            "riches_sans_armee_mesures": r["zero"],
            "enonce_borne": "la richesse par tête n'est pas une condition de la guerre ; la "
                            "trésorerie de l'État conditionne sa durée et l'intensité conventionnelle "
                            "qu'il peut soutenir",
            "statut_de_l_enonce_borne": f"non réfuté par les {r['effectif']} pays comparables, "
                                        "non prouvé pour autant",
            "effort_fiscal_median_pct": e["mediane_pct"],
            "aucune_guerre_datee": PHRASE_ABSENCE}


def limites_ouvertes() -> Dict[str, Any]:
    s, cov, f, em, ip, cv = (source_tresor(), couverture(), falsification(),
                             emulateur_hors_sujet(), instruments_protection(), chapitres_video())
    bd = belligerants_declares()
    liste = [
        f"aucune base de conflits n'a été jointe ({s['date_releve']}) : ce dossier ne date aucune "
        f"guerre et ne nomme aucun agresseur — {PHRASE_ABSENCE}",
        f"le snapshot porte l'année {s['annee_des_mesures']} et une seule : la corrélation de rang "
        "ne dit rien de la causalité ni d'aucune tendance",
        f"sur {cov['lignes']} entités, {cov['comparables']} seulement sont comparables : "
        f"{cov['avec_dette']} dettes publiques mesurées, {cov['avec_effort_fiscal']} efforts fiscaux "
        "calculables — le reste est absent, pas nul",
        f"la dépense militaire en dollars courants est une série reconstituée par la Banque mondiale "
        f"à partir de sources secondaires : ce n'est pas un budget d'État audité",
        f"les {f['effectif']} contre-exemples mesurent l'armement, pas le fait de faire la guerre : "
        "porter une armée n'est pas entrer en conflit",
        f"les {bd['nb']} faits de guerre de la table des belligérants sont déclarés par l'auteur et "
        f"demeurent non vérifiés : seuls {bd['revenus_mesures']} revenus {s['annee_des_mesures']} sont "
        f"publiés par la source, {bd['codes_sans_revenu']} n'en ont pas",
        f"l'émulateur du dépôt ({em['sous_commandes']} sous-commandes) ne rend aucune grandeur de "
        "finance publique : aucun de ses résultats n'entre dans ce dossier",
        f"{ip['artefacts_executifs']} artefact exécutif sur disque : la demande « protéger tous les "
        "musulmans du monde » n'est pas exécutable par ce dépôt, et le dire serait un dol",
        f"la source vidéo rend {cv['nombre']} chapitres horodatés et {cv['transcript_octets']} octet "
        "de transcript : aucune phrase de la vidéo n'est citée, seulement ses minutages",
        f"le seuil de platitude (|rho| < {_nombre(SEUIL_CHARGE_PLATE, 2)}) et le seuil d'effort massif "
        f"({_nombre(SEUIL_EFFORT_MASSIF, 2)} %) sont des choix d'auteur : ils sont écrits ici pour "
        "être contestés, pas cachés",
    ]
    return {"liste": liste, "nb": len(liste), "remplies_dans_ce_lot": 0,
            "la_quatrieme_absence": "aucune protection promise",
            "seuil_platitude_declare": _nombre(SEUIL_CHARGE_PLATE, 2),
            "seuil_effort_declare": _nombre(SEUIL_EFFORT_MASSIF, 2)}


# ─── 5. Équations --------------------------------------------------------------

NOEUDS: Dict[str, Dict[str, Any]] = {
    "EQ-01": {"depend": [], "externe": [CHEMIN_TRESOR]},
    "EQ-02": {"depend": ["EQ-01"], "externe": [CHEMIN_TRESOR]},
    "EQ-03": {"depend": ["EQ-02"], "externe": [CHEMIN_TRESOR]},
    "EQ-04": {"depend": ["EQ-03"], "externe": [CHEMIN_TRESOR]},
    "EQ-05": {"depend": ["EQ-03"], "externe": [CHEMIN_TRESOR]},
    "EQ-06": {"depend": ["EQ-03", "EQ-05"], "externe": [CHEMIN_TRESOR]},
    "EQ-07": {"depend": ["EQ-04"], "externe": [CHEMIN_TRESOR]},
    "EQ-08": {"depend": ["EQ-03"], "externe": [CHEMIN_TRESOR]},
    "EQ-09": {"depend": ["EQ-04", "EQ-08"], "externe": [CHEMIN_TRESOR]},
    "EQ-10": {"depend": ["EQ-06", "EQ-09"], "externe": []},
    "EQ-11": {"depend": ["EQ-09"], "externe": [CHEMIN_TRESOR]},
    "EQ-12": {"depend": ["EQ-01"], "externe": [CHEMIN_EMULATEUR]},
    "EQ-13": {"depend": ["EQ-01"], "externe": []},
    "EQ-14": {"depend": ["EQ-01"], "externe": [CHEMIN_CHAPITRES]},
    "EQ-15": {"depend": ["EQ-02", "EQ-09"], "externe": []},
    "EQ-16": {"depend": ["EQ-06", "EQ-13"], "externe": []},
}


def _eq(id_: str, chemin: str, formule: str, resultat: str, statut: str,
        limite: str, detail: Any, couche: str = "S1 MESURABLE") -> Dict[str, Any]:
    n = NOEUDS[id_]
    return {"id": id_, "chemin": chemin, "formule": formule, "resultat": resultat,
            "statut": statut, "limite": limite, "detail": detail, "couche": couche,
            "piliers": ["P1 UNITE", "P2 BORNE", "P3 CONFRONTATION", "P4 TRANSMISSION"],
            "depend_de": n["depend"], "fonde_hors_du_dossier": n["externe"]}


def equations(etat: Dict[str, Any]) -> List[Dict[str, Any]]:
    s, cov, m = etat["source_tresor"], etat["couverture"], etat["masses"]
    cr, ca, f = etat["charge_relative"], etat["capacite_absolue"], etat["falsification"]
    ex, rs, tr = etat["extreme_mesure"], etat["riches_sans_armee"], etat["tresorerie"]
    ve, bd = etat["verdict"], etat["belligerants_declares"]
    em, ip, cv = etat["emulateur_hors_sujet"], etat["instruments_protection"], etat["chapitres_video"]
    pl, lo = etat["plan_tresor"], etat["limites_ouvertes"]
    return [
        _eq("EQ-01", "GUERRE/guerre_base.py → source_tresor() → C01",
            "snapshot = octets engagés par sha256(octets) ; chaque réponse brute de l'API est "
            "empreinte séparément",
            f"{s['octets']} octets · sha {s['sha256'][:16]}… · {s['lignes']} entités · "
            f"{s['entites_hors_agregats']} hors agrégats sur {s['entites_declarees']} déclarées · "
            f"API `{s['derniere_mise_a_jour_source']}` relevé {s['date_releve']} · requête réseau au "
            f"rejoué {s['reseau_utilise_ce_rejoue']}",
            "OPÉRATIONNEL",
            "le snapshot est une photographie de 2022 déposée ici : si la Banque mondiale révise sa "
            "série, le certificat ne bouge pas et la divergence n'est pas détectable hors re-fetch", s),
        _eq("EQ-02", "GUERRE/guerre_base.py → couverture() → C02",
            "couverture = |{p : valeur numérique}| par indicateur, absence ≠ zéro ; comparables = "
            "dépense absolue et revenu par tête tous deux présents",
            f"{cov['comparables']}/{cov['lignes']} comparables ({cov['ratio_exploitable_pct']} %) · "
            f"part du PIB {cov['avec_part']} · recettes {cov['avec_recettes']} · "
            f"dette {cov['avec_dette']} · effort fiscal {cov['avec_effort_fiscal']} · "
            f"{cov['sans_aucune_valeur']} entités sans aucune valeur",
            "OPÉRATIONNEL",
            "les entités sans donnée sont exclues, pas comptées zero : un État qui ne publie rien "
            "n'est pas un État désarmé", cov),
        _eq("EQ-03", "GUERRE/guerre_base.py → masses() → C03",
            "Σ depense = total ; top10/Σ × 100 ; médiane ; franchissements de 1, 10 et 100 Md$",
            f"total {m['total_mds']} Md$ · top {SEUIL_TOP} = {m['top_dix_pct']} % "
            f"({m['top_dix_mds']} Md$) · médiane {m['mediane_mds']} Md$ · "
            f"{m['seuils']} · {m['nb_zero']} dépenses exactement nulles · premier {m['premier']}",
            "OPÉRATIONNEL",
            "les dollars courants ne sont pas déflatés ni comparés en pouvoir d'achat : une masse "
            "en dollars surestime la capacité physique d'un État pauvre à grand territoire", m),
        _eq("EQ-04", "GUERRE/guerre_base.py → charge_relative() → C04",
            "rho_s = 1 − 6·Σd²/(n(n²−1)) sur les rangs de (revenu par tête, part du PIB), départage "
            "par code ISO ; parts moyennes par quintile de revenu",
            f"rho = {cr['spearman_revenu_part']} sur {cr['effectif']} pays · quintiles "
            f"{[q['part_moyenne_pct'] for q in cr['quintiles']]} % · écart max−min "
            f"{cr['ecart_max_min_pct']} pt · seuil {cr['seuil_de_platitude']} · charge plate "
            f"{cr['la_charge_ne_croit_pas_avec_le_revenu']}",
            "OPÉRATIONNEL",
            "un rho de rang proche de zéro ne prouve pas l'indépendance causale : il dit seulement que la "
            "connaissance du revenu ne classe pas la charge militaire relative", cr),
        _eq("EQ-05", "GUERRE/guerre_base.py → capacite_absolue() → C05",
            "rho_s sur les rangs de (revenu par tête, dépense absolue) — la masse, non la charge",
            f"rho = {ca['spearman_revenu_masse']} sur {ca['effectif']} · médiane de revenu "
            f"{ca['mediane_revenu']} $ · {ca['sens']}",
            "OPÉRATIONNEL",
            "la corrélation positive ne dit pas que la richesse cherche la guerre : elle dit qu'une "
            "armée achetée en dollars suppose une économie qui fabrique ces dollars", ca),
        _eq("EQ-06", "GUERRE/guerre_base.py → falsification() → C06",
            "|{p : revenu < médiane ∧ dépense ≥ 1 Md$}| ; la forme absolue exige que cet ensemble "
            "soit vide",
            f"{f['effectif']} pays sous la médiane ({f['mediane_revenu']} $) armant à plus d'un "
            f"Md$ · le plus pauvre {f['plus_pauvre_arms']['iso3']} à "
            f"{f['plus_pauvre_arms']['pib_h']} $ · ≥ 10 Md$ : {f['au_dessus_de_dix_mds']} · "
            f"absolue réfutée {f['l_absolue_est_refutee']}",
            "OPÉRATIONNEL",
            f"l'armement n'est pas la guerre : ces {f['effectif']} pays prouvent que la pauvreté "
            "n'empêche pas de s'armer, ils ne prouvent pas qu'ils font la guerre", f),
        _eq("EQ-07", "GUERRE/guerre_base.py → extreme_mesure() → C07",
            "argmax part du PIB, avec son rang de revenu dans la population comparable",
            f"{ex['iso3']} {ex['pays']} : {ex['part_pct']} % du PIB pour un revenu de "
            f"{ex['pib_h']} $ (rang {ex['rang_revenu']}/{ex['effectif']}) · {ex['rapport_a_la_mediane']} "
            f"× la médiane des parts ({ex['mediane_part_pct']} %)",
            "OPÉRATIONNEL",
            "un seul pays ne fait pas une loi : l'extrême mesuré est un contre-exemple à la forme "
            "absolue, pas une démonstration de la forme bornée", ex),
        _eq("EQ-08", "GUERRE/guerre_base.py → riches_sans_armee() → C08",
            "|{p : dépense = 0}| et test revenu > médiane pour chacun — l'implication inverse",
            f"{rs['zero']} États à dépense nulle mesurée {[x['iso3'] for x in rs['liste']]} · "
            f"tous au-dessus de la médiane {rs['tous_au_dessus_de_la_mediane']} · le plus riche "
            f"{rs['le_plus_riche'].get('iso3')} à {rs['le_plus_riche'].get('pib_h')} $ · médiane "
            f"{rs['mediane_revenu']} $",
            "OPÉRATIONNEL",
            "une dépense militaire nulle mesurée peut venir d'un choix (Costa Rica) comme d'un "
            "manque de données publiées : le zéro mesuré n'égale pas le zéro vécu", rs),
        _eq("EQ-09", "GUERRE/guerre_base.py → tresorerie() → C09",
            f"{tr['formule']} ; médiane, masse au-dessus de {tr['seuil_massif_pct']} %, rho(revenu, "
            "effort)",
            f"effort médian {tr['mediane_pct']} % des recettes · {tr['massifs']} États ≥ "
            f"{tr['seuil_massif_pct']} % {tr['codes_massifs']} · dont sous 5 000 $/hab "
            f"{tr['massifs_et_sous_cinq_mille']} · rho(revenu, effort) = "
            f"{tr['spearman_revenu_effort']} · dette médiane {tr['dette_mediane_pct']} % sur "
            f"{tr['dette_effectif']} pays",
            "OPÉRATIONNEL",
            "l'effort fiscal suppose des recettes déclarées : sur les pays les plus pauvres, une "
            "part de l'économie échappe à l'assiette et le ratio mesure mal la réalité", tr),
        _eq("EQ-10", "GUERRE/guerre_base.py → verdict() → C10",
            "énoncé de l'auteur ; réfutation = |contre-exemples| > 0 ; énoncé borné = condition de "
            "trésorerie, non de revenu par tête",
            f"« {ve['enonce_original']} » → {ve['statut_de_l_enonce_original']} "
            f"({ve['contre_exemples_mesures']} contre-exemples, {ve['riches_sans_armee_mesures']} "
            f"riches désarmés) · énoncé borné : {ve['enonce_borne']} — {ve['statut_de_l_enonce_borne']}",
            "OPÉRATIONNEL",
            "remplacer une loi fausse par une loi plausible reste une hypothèse : l'énoncé borné "
            f"n'est pas démontré, il est seulement non réfuté par ces {cov['comparables']} lignes "
            "mesurées", ve),
        _eq("EQ-11", "GUERRE/guerre_base.py → belligerants_declares() → C11",
            "table déclarée ⊗ mesure : chaque fait déclaré porte le revenu 2022 et l'effort fiscal "
            "mesurés du même État, ou l'absence publiée par la source",
            f"{bd['nb']} faits déclarés · {bd['revenus_mesures']} revenus mesurés "
            f"({bd['part_revenus_mesures_pct']} %) · sans revenu publié {bd['codes_sans_revenu']} · "
            f"{bd['efforts_calculables']} efforts calculables · statut du fait "
            f"« {bd['statut_du_fait']} » · base de conflits jointe {bd['base_de_conflits_jointe']}",
            "OPÉRATIONNEL",
            f"le compte rendu est mesuré, le fait de guerre ne l'est pas : {bd['statut_du_fait']} ; "
            f"de plus {bd['revenus_absents']} ligne(s) sur {bd['nb']} n'ont même pas de revenu publié "
            f"par la source en {etat['source_tresor']['annee_des_mesures']} — {bd['statut_du_revenu']}",
            bd),
        _eq("EQ-12", "GUERRE/guerre_base.py → emulateur_hors_sujet() → C12",
            "|sous-commandes(émulateur)| ; mentions de finance dans son source ; appels depuis ce "
            "dossier ; le tout comparé aux occurrences du corpus",
            f"émulateur {em['octets']} octets, {em['sous_commandes']} sous-commandes · "
            f"{em['mentions_de_finance']} · appels depuis GUERRE {em['appels_de_ce_module_depuis_guerre']} "
            f"· apport dans ce dossier {em['apport_de_l_emulateur_dans_ce_dossier']}",
            "SPÉCIFIÉ",
            "l'injonction « utilise l'émulateur pour poser les équations » n'est pas servable ici : "
            "une simulation de circuits quantiques ne produit pas une grandeur de finance publique",
            em),
        _eq("EQ-13", "GUERRE/guerre_base.py → instruments_protection() → C13",
            "|{f : extension ∈ exécutifs}| ; mentions du vocabulaire de protection dans le corpus ; "
            "personnes protégeables par ce dépôt",
            f"{ip['artefacts_executifs']} artefact exécutif sur disque · "
            f"{ip['mentions_total']} mention(s) de protection ou d'immuabilité dans "
            f"{sum(len(v['fichiers']) for v in ip['mentions'].values())} fichier(s) · personnes "
            f"protégeables {ip['personnes_protegeables_par_ce_depot']} · « immuable » impossible "
            f"{ip['le_texte_ne_protege_pas']}",
            "OPÉRATIONNEL",
            "le mot compte et ne protège pas : la demande « protéger tous les musulmans du monde » "
            "dépasse ce dépôt, qui n'exécute rien et ne peut engager aucune protection", ip),
        _eq("EQ-14", "GUERRE/guerre_base.py → chapitres_video() → C14",
            "chapitres = liste d'horodatages strictement croissants, dernier ≤ durée ; transcript = "
            "octets rendus par les trois formats sondés",
            f"{cv['id']} · {cv['chaine']} · {cv['duree_s']} s · {cv['nombre']} chapitres · croissants "
            f"{cv['strictement_croissants']} · bornes {cv['sous_la_duree']} · "
            f"{cv['nb_sondes']} sondes de transcript {cv['transcript_etat']} "
            f"({cv['transcript_octets']} octet) · {cv['nb_chapitres_cites']} chapitres cités · "
            f"citations {cv['citations_du_transcript']}",
            "OPÉRATIONNEL",
            "sans transcript, la vidéo ne fournit que son plan : aucun propos n'en est tiré, et les "
            "conclusions de ce dossier reposent sur la mesure publique, pas sur l'invité", cv),
        _eq("EQ-15", "GUERRE/guerre_base.py → plan_tresor() → C15",
            "le plan publié est relu octet par octet : barres = BARRES, longueurs = "
            "220 × v / max(v) en décimale exacte, registre = en-tête + lignes",
            f"{pl['barres']} barres nommées · grandeurs conformes {pl['largeurs_conformes']} · "
            f"registre {pl['lignes_lues']} lignes · colonnes reconnues "
            f"{pl['en_tete_conforme']} · écritures {sorted(etat['ecritures']['noms'])}",
            "OPÉRATIONNEL",
            "les octets relus sont produits par ce module : ils attestent la chaîne de production, "
            "pas une qualité du monde extérieur", {"plan": pl, "ecritures": etat["ecritures"]}),
        _eq("EQ-16", "GUERRE/guerre_base.py → limites_ouvertes() → C16",
            "limites = liste publiée, remplies = comptées à zéro dans ce lot",
            f"{lo['nb']} limites ouvertes · {lo['remplies_dans_ce_lot']} remplie · seuils déclarés "
            f"{lo['seuil_platitude_declare']} et {lo['seuil_effort_declare']} · "
            f"{lo['la_quatrieme_absence']}",
            "SPÉCIFIÉ",
            "une limite écrite n'est pas une limite franchie : ce dossier ferme la porte à ses "
            "propres affirmations sans les ouvrir", lo),
    ]


# ─── 6. Contrôles --------------------------------------------------------------


def controles(eqs: Dict[str, Any], etat: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []

    def ajouter(id_: str, nom: str, verifie: str, attendu: str, obtenu: str, ok: bool) -> None:
        out.append({"id": id_, "equation": f"EQ-{id_[1:]}", "nom": nom, "verifie": verifie,
                    "attendu": attendu, "obtenu": obtenu, "ok": bool(ok)})

    s, cov, m = etat["source_tresor"], etat["couverture"], etat["masses"]
    cr, ca, f = etat["charge_relative"], etat["capacite_absolue"], etat["falsification"]
    ex, rs, tr = etat["extreme_mesure"], etat["riches_sans_armee"], etat["tresorerie"]
    ve, bd = etat["verdict"], etat["belligerants_declares"]
    em, ip, cv = etat["emulateur_hors_sujet"], etat["instruments_protection"], etat["chapitres_video"]
    pl, lo = etat["plan_tresor"], etat["limites_ouvertes"]
    ec = etat["ecritures"]

    ajouter("C01", "le snapshot est engagé et rejouable hors connexion",
            "octets > 0, sha256 sur 64 hex, 217 lignes, empreintes des six réponses brutes, aucune "
            "requête au rejoué",
            "sha 64 · lignes 217 · empreintes 6 · reseau False",
            f"{len(s['sha256'])} hex · {s['lignes']} lignes · {len(s['empreintes_brutes'])} "
            f"empreintes · reseau {s['reseau_utilise_ce_rejoue']}",
            s["octets"] > 0 and len(s["sha256"]) == 64 and s["lignes"] == 217
            and len(s["empreintes_brutes"]) == 6 and s["reseau_utilise_ce_rejoue"] is False
            and all(len(v) == 64 for v in s["empreintes_brutes"].values()))
    ajouter("C02", "la couverture est comptée, pas rêvée",
            "comparables entre 100 et 217, ratio cohérent, absence distincte de zéro",
            "100 < comparables < 217 · ratio = comparables/lignes",
            f"{cov['comparables']} comparables · ratio {cov['ratio_exploitable_pct']} % · "
            f"{cov['sans_aucune_valeur']} sans valeur · indicateur le plus muet "
            f"{cov['indicateur_le_plus_muet']}",
            100 < cov["comparables"] < cov["lignes"]
            and cov["ratio_exploitable_pct"] == _decimale(
                Fraction(cov["comparables"]) * 100 / Fraction(cov["lignes"]), 2)
            and cov["avec_effort_fiscal"] <= cov["avec_recettes"] <= cov["lignes"])
    ajouter("C03", "la masse est additivement cohérente",
            "top10 ≤ total, pourcentage re-dérivé en rationnels depuis les dollars arrondis, "
            "zéros comptés et monotone des franchissements de seuil",
            f"top10 ≤ {m['total_mds']} Md$ · pct = top/total · seuils décroissants",
            f"{m['top_dix_mds']} ≤ {m['total_mds']} Md$ · top {m['top_dix_pct']} % · "
            f"{m['nb_zero']} zéros · seuils {m['seuils']}",
            float(m["top_dix_mds"]) <= float(m["total_mds"])
            and m["top_dix_dollars_arrondis"] <= m["total_dollars_arrondis"]
            and m["top_dix_pct"] == _decimale(Fraction(m["top_dix_dollars_arrondis"]) * 100 /
                                              Fraction(m["total_dollars_arrondis"]), 2)
            and m["seuils"][">= 100 Md$"] <= m["seuils"][">= 10 Md$"]
            <= m["seuils"][">= 1 Md$"] <= m["effectif"] and m["nb_zero"] == len(m["zero_mesures"]))
    ajouter("C04", "la charge relative ne croît pas avec le revenu",
            "|rho| < seuil déclaré, cinq quintiles couvrant l'effectif, écart max−min publié",
            f"|rho| < {cr['seuil_de_platitude']} · 5 quintiles",
            f"rho = {cr['spearman_revenu_part']} · quintiles {len(cr['quintiles'])} · somme des n "
            f"{sum(q['n'] for q in cr['quintiles'])} sur {cr['effectif']} · écart "
            f"{cr['ecart_max_min_pct']} pt · plat {cr['la_charge_ne_croit_pas_avec_le_revenu']}",
            cr["la_charge_ne_croit_pas_avec_le_revenu"] and len(cr["quintiles"]) == 5
            and sum(q["n"] for q in cr["quintiles"]) == cr["effectif"]
            and abs(float(cr["spearman_revenu_part"])) < SEUIL_CHARGE_PLATE)
    ajouter("C05", "la masse en dollars suit le revenu",
            "rho positif et strictement plus grand que celui de la charge relative",
            "rho(absolue) > rho(part)",
            f"rho masse = {ca['spearman_revenu_masse']} · rho charge = {cr['spearman_revenu_part']} · "
            f"médiane de revenu {ca['mediane_revenu']} $",
            float(ca["spearman_revenu_masse"]) > float(cr["spearman_revenu_part"]) > 0)
    ajouter("C06", "la forme absolue est réfutée par la mesure",
            "au moins un pays sous la médiane armant à plus d'un milliard, et le réfuter est écrit",
            "effectif > 0 · réfutée True",
            f"{f['effectif']} contre-exemples · plus pauvre {f['plus_pauvre_arms']['iso3']} à "
            f"{f['plus_pauvre_arms']['pib_h']} $ · réfutée {f['l_absolue_est_refutee']} · "
            f"liste publiée dans l'artefact ({len(f['pauvres_armes'])} lignes)",
            f["l_absolue_est_refutee"] and f["effectif"] > 0
            and len(f["pauvres_armes"]) == f["effectif"]
            and "réfuté par la mesure" in ve["statut_de_l_enonce_original"])
    ajouter("C07", "l'extrême mesuré est nommé avec son rang",
            "rang de revenu entre 1 et l'effectif, part réellement maximale de la population, "
            "rapport à la médiane supérieur à un",
            "1 ≤ rang ≤ effectif · part = max · rapport > 1",
            f"{ex['iso3']} rang {ex['rang_revenu']}/{ex['effectif']} · part {ex['part_pct']} % · "
            f"médiane {ex['mediane_part_pct']} % · maximum {ex['est_le_maximum_mesure']} · rapport "
            f"{ex['rapport_a_la_mediane']}",
            1 <= ex["rang_revenu"] <= ex["effectif"] and ex["est_le_maximum_mesure"]
            and float(ex["part_pct"]) >= max(float(x["part"]) for x in ex["suivants"])
            and len(ex["suivants"]) == 7 and float(ex["rapport_a_la_mediane"]) > 1)
    ajouter("C08", "des riches sans armée existent, et c'est écrit",
            "au moins un État à dépense nulle, tous au-dessus de la médiane de revenu",
            "zero ≥ 1 · tous_au_dessus True",
            f"{rs['zero']} zéro mesuré · {[x['iso3'] for x in rs['liste']]} · au-dessus de la "
            f"médiane {rs['tous_au_dessus_de_la_mediane']} · implication renversée "
            f"{rs['l_implication_tombe_a_l_envers']}",
            rs["zero"] >= 1 and rs["tous_au_dessus_de_la_mediane"]
            and rs["le_plus_riche"].get("pib_h") not in (None, ""))
    ajouter("C09", "la trésorerie est la contrainte mesurée",
            "effort médian publié, au moins un État à effort ≥ seuil et revenu < 5 000 $, rho "
            "(revenu, effort) calculé",
            f"massifs ≥ 1 · sous 5 000 $ ≥ 1",
            f"effort médian {tr['mediane_pct']} % · {tr['massifs']} massifs · sous 5 000 $ "
            f"{tr['massifs_et_sous_cinq_mille']} · rho {tr['spearman_revenu_effort']} · dette "
            f"mesurée {tr['dette_effectif']} pays",
            tr["massifs"] >= 1 and len(tr["massifs_et_sous_cinq_mille"]) >= 1
            and tr["codes_massifs"].count(tr["haut_du_tableau"][0]["iso3"]) == 1
            and tr["effectif"] == cov["avec_effort_fiscal"])
    ajouter("C10", "l'énoncé de l'auteur reste écrit, et reste réfuté",
            "statut de l'absolue = réfutée, compteur de contre-exemples = mesure, énoncé borné ≠ "
            "démontré",
            "réfuté · borné non prouvé",
            f"statut « {ve['statut_de_l_enonce_original']} » · {ve['contre_exemples_mesures']} "
            f"contre-exemples ({f['effectif']} mesurés) · né de {PHRASE_ABSENCE}",
            ve["statut_de_l_enonce_original"] == "réfuté par la mesure"
            and ve["contre_exemples_mesures"] == f["effectif"]
            and "non prouvé" in ve["statut_de_l_enonce_borne"]
            and ve["enonce_original"] in SOURCE["point_de_depart"])
    ajouter("C11", "les faits déclarés ne sont pas devenus des faits mesurés",
            "statut du fait = déclaré · non vérifié, chaque ligne déclarée est mesurée ou dite "
            "absente, le compte des absences retombe sur la relecture des détails, base de conflits "
            "absente",
            f"{bd['nb']} lignes · mesurés {bd['revenus_mesures']} + absents {bd['revenus_absents']} "
            f"= {bd['nb']} · statut déclaré",
            f"{bd['revenus_mesures']}/{bd['nb']} revenus mesurés ({bd['part_revenus_mesures_pct']} %) "
            f"· sans revenu publié {bd['codes_sans_revenu']} · {bd['efforts_calculables']} efforts "
            f"calculables · fait « {bd['statut_du_fait']} » · base jointe "
            f"{bd['base_de_conflits_jointe']}",
            bd["chaque_ligne_est_mesuree_ou_dite_absente"]
            and bd["revenus_mesures"] == sum(1 for d in bd["details"] if d["revenu_present"])
            and bd["codes_sans_revenu"] == [d["iso3"] for d in bd["details"] if not d["revenu_present"]]
            and bd["statut_du_fait"] == "déclaré · non vérifié"
            and bd["base_de_conflits_jointe"] is False and len(bd["details"]) == bd["nb"])
    ajouter("C12", "l'émulateur est hors sujet et le dossier le dit",
            "0 grandeur de finance dans le source de l'émulateur, 0 appel depuis GUERRE, apport = 0",
            "finance 0 · appels 0 · apport 0",
            f"{em['sous_commandes']} sous-commandes · mentions de finance "
            f"{em['mentions_de_finance']} · appels {em['appels_de_ce_module_depuis_guerre']} · "
            f"apport {em['apport_de_l_emulateur_dans_ce_dossier']} · "
            f"déclaration lue « {em['declaration_lue'][:60]} »",
            em["aucune_grandeur_de_finance"] and em["jamais_appel"]
            and em["apport_de_l_emulateur_dans_ce_dossier"] == 0
            and em["sous_commandes"] > 0 and "classique" in em["declaration_lue"])
    ajouter("C13", "aucune protection n'est exécutable par ce dépôt",
            "0 artefact exécutif sur disque, mentions publiées séparément, personnes protégeables 0",
            "0 exécutif · 0 protégeable",
            f"{ip['artefacts_executifs']} artefact exécutif · {ip['mentions_total']} mention(s) · "
            f"personnes protégeables {ip['personnes_protegeables_par_ce_depot']} · statut « "
            f"{ip['statut_de_la_demande']} »",
            ip["artefacts_executifs"] == 0 and ip["le_texte_ne_protege_pas"]
            and ip["personnes_protegeables_par_ce_depot"] == 0
            and ip["mentions_total"] > 0)
    ajouter("C14", "la source vidéo ne rend que son plan",
            "chapitres > 0, horodatages strictement croissants et sous la durée, trois sondes de "
            "transcript à zéro octet, aucun chapitre cité hors du snapshot, 0 citation",
            f"croissants True · sondes 3 · octets 0 · citations 0 · cités {len(CHAPITRES_CITES)}",
            f"{cv['nombre']} chapitres · croissants {cv['strictement_croissants']} · bornes "
            f"{cv['sous_la_duree']} · {cv['nb_sondes']} sondes à {cv['transcript_octets']} octet · "
            f"chapitres cités {cv['nb_chapitres_cites']} · citations "
            f"{cv['citations_du_transcript']}",
            cv["nombre"] > 0 and cv["strictement_croissants"] and cv["sous_la_duree"]
            and cv["transcript_octets"] == 0 and cv["citations_du_transcript"] == 0
            and cv["nb_sondes"] == 3 and cv["transcript_etat"] == "absent"
            and cv["nb_chapitres_cites"] == len(CHAPITRES_CITES)
            and len(cv["avertissements"]) >= 1)
    ajouter("C15", "les octets publiés se relisent",
            f"{len(BARRES)} barres nommées aux longueurs exactes, registre à {len(COLONNES_TRESOR)} "
            "colonnes et à une ligne par pays comparable, BOM et CRLF, phrase de vérification écrite, "
            "empreintes des trois artefacts nommés, aucun interdit hors la liste des interdits",
            f"{len(BARRES)} barres · {cov['comparables'] + 1} lignes · "
            f"{len(COLONNES_TRESOR)} colonnes · 0 interdit",
            f"{pl['barres']} barres · conformes {pl['largeurs_conformes']} · {pl['lignes_lues']} "
            f"lignes lues · BOM {pl['bom']} CRLF {pl['crlf']} · en-tête {pl['en_tete_conforme']} · "
            f"phrase {pl['phrase_verifiee_ecrite']} · valeurs {pl['valeurs_ecrites']} · écritures "
            f"{sorted(ec['noms'])} · interdits hors des octets {ec['interdits_hors_des_octets']}",
            pl["barres"] == len(BARRES) and pl["largeurs_conformes"]
            and pl["valeurs_ecrites"] == pl["valeurs_attendues"]
            and pl["libelles_ecrits"] == [lib for lib, _, _ in BARRES]
            and pl["lignes_lues"] == 1 + cov["comparables"] and pl["en_tete_conforme"]
            and pl["bom"] and pl["crlf"] and pl["sans_lf_nu"] and pl["phrase_verifiee_ecrite"]
            and pl["phrase_absente_du_csv_par_design"]
            and len(ec["noms"]) == len(NOMS_ARTEFACTS) and all(v for v in ec["tailles"].values())
            and ec["absence_partout"] and ec["interdits_hors_des_octets"]
            and ec["liste_des_phrases_interdites"] == list(INTERDITS))
    ajouter("C16", "les limites restent ouvertes et sont écrites",
            "au moins huit limites, chacune d'au moins 40 caractères, aucune remplie dans ce lot, "
            "les deux seuils et la phrase d'absence repris dans la liste",
            f"≥ 8 limites · 0 remplie · {lo['nb']} écrites",
            f"{lo['nb']} limites · {lo['remplies_dans_ce_lot']} remplie · seuils "
            f"{lo['seuil_platitude_declare']} / {lo['seuil_effort_declare']} · "
            f"toutes assez longues {all(len(l) >= 40 for l in lo['liste'])} · absence reprise "
            f"{any(PHRASE_ABSENCE in l for l in lo['liste'])}",
            lo["nb"] >= 8 and lo["remplies_dans_ce_lot"] == 0
            and all(len(l) >= 40 for l in lo["liste"])
            and any(lo["seuil_platitude_declare"] in l for l in lo["liste"])
            and any(lo["seuil_effort_declare"] in l for l in lo["liste"])
            and any("artefact exécutif" in l for l in lo["liste"])
            and any(PHRASE_ABSENCE in l for l in lo["liste"])
            and lo["la_quatrieme_absence"] == "aucune protection promise")
    return out


# ─── 7. Scellement -------------------------------------------------------------


def canonique(objet: Any) -> bytes:
    return json.dumps(objet, ensure_ascii=False, sort_keys=True,
                      default=str).encode("utf-8")


MESURES = ("source_tresor", "couverture", "masses", "charge_relative", "capacite_absolue",
           "falsification", "extreme_mesure", "riches_sans_armee", "tresorerie",
           "belligerants_declares", "emulateur_hors_sujet", "instruments_protection",
           "chapitres_video", "limites_ouvertes", "verdict")


def octets_csv(cert: Dict[str, Any]) -> bytes:
    cov = cert["couverture"]
    lignes = [r for r in _lignes() if _nb(r, "depense_militaire_usd_courants")
              and _nb(r, "pib_par_habitant_usd_courants")]
    tri = sorted(lignes, key=lambda r: (-r["depense_militaire_usd_courants"], r["iso3"]))
    mediane = statistics.median(r["pib_par_habitant_usd_courants"] for r in tri)
    corps = [";".join(COLONNES_TRESOR)]
    for i, r in enumerate(tri, 1):
        e = _effort(r)
        corps.append(";".join([r["iso3"], r["nom"].replace(";", ","),
                               _nombre(r["depense_militaire_usd_courants"], 2),
                               _nombre(r.get("depense_part_du_pib_pct"), 4),
                               _nombre(r["pib_par_habitant_usd_courants"], 2),
                               _nombre(r.get("recettes_publiques_part_du_pib_pct"), 4),
                               _nombre(r.get("dette_publique_part_du_pib_pct"), 4),
                               _nombre(e, 4) if e is not None else "—",
                               str(i),
                               "oui" if r["pib_par_habitant_usd_courants"] < mediane else "non"]))
    return ("\ufeff" + "\r\n".join(corps) + "\r\n").encode("utf-8")


def octets_svg(cert: Dict[str, Any]) -> bytes:
    valeurs = [(lib, int(cert[nom][clef])) for lib, nom, clef in BARRES]
    grand = max([v for _, v in valeurs] + [1])
    pieces: List[str] = []
    for i, (lib, v) in enumerate(valeurs):
        w = _decimale(LONGUEUR_MAX * Fraction(v) / Fraction(grand), 2)
        y = 34 + i * 30
        pieces.append(f'<rect x="250" y="{y - 12}" width="{w}" height="16" '
                      f'fill="{COULEURS[i % len(COULEURS)]}" data-libelle="{lib}" '
                      f'data-valeur="{v}"/>')
        pieces.append(f'<text x="8" y="{y}" font-size="13" fill="#0f1c2b" xml:lang="fr">'
                      f'{lib}</text>')
        xp = _decimale(Fraction(256) + LONGUEUR_MAX * Fraction(v) / Fraction(grand), 2)
        pieces.append(f'<text x="{xp}" y="{y}" font-size="13" fill="#1c3550">{v}</text>')
    bas = 34 + len(valeurs) * 30 + 26
    ve = cert["verdict"]
    note = (f'<text x="8" y="{bas - 18}" font-size="12" fill="#5c2f2f" xml:lang="fr">'
            f'{ve["contre_exemples_mesures"]} contre-exemples mesurés, '
            f'{ve["riches_sans_armee_mesures"]} riches désarmés — {PHRASE_VERIFIEE}</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="560" height="{bas + 8}" '
            f'viewBox="0 0 560 {bas + 8}">\n'
            f'<title>GUERRE — ce que le revenu par tête ne classe pas, ce que la trésorerie mesure'
            f'</title>\n'
            f'<desc>Longueurs proportionnelles à la plus grande valeur ({grand}). '
            f'{PHRASE_VERIFIEE}. {PHRASE_ABSENCE}.</desc>\n' + "\n".join(pieces) + "\n" + note +
            "\n</svg>\n").encode("utf-8")


def octets_lisibilite_md(cert: Dict[str, Any]) -> bytes:
    s, cov, m = cert["source_tresor"], cert["couverture"], cert["masses"]
    cr, f, rs = cert["charge_relative"], cert["falsification"], cert["riches_sans_armee"]
    tr, ve = cert["tresorerie"], cert["verdict"]
    em, ip, cv = cert["emulateur_hors_sujet"], cert["instruments_protection"], cert["chapitres_video"]
    lo = cert["limites_ouvertes"]
    lignes = [
        "# GUERRE — la richesse suffit-elle pour faire la guerre ?",
        "",
        f"**Départ** proposition d'auteur du {s['date_releve']} : « il faut etre riche pour faire la "
        f"guerre = sans richesse pas de guerre ». Elle est testée, pas récitée.",
        f"**Mesure** {cov['comparables']} pays sur {cov['lignes']} entités, snapshot "
        f"`{s['sha256'][:16]}…`, année {s['annee_des_mesures']}, API du {s['derniere_mise_a_jour_source']}.",
        "",
        "## Ce que les nombres rendent",
        "",
        "| Ce qu'on demandait | Ce qui est mesuré | Verdict |",
        "| :--- | :--- | :--- |",
        f"| « sans richesse pas de guerre » | {f['effectif']} pays sous la médiane "
        f"({f['mediane_revenu']} $) armant à plus d'un Md$ | réfuté |",
        f"| la charge militaire suit-elle la richesse ? | rho(revenu, part du PIB) = "
        f"{cr['spearman_revenu_part']} · quintiles {[q['part_moyenne_pct'] for q in cr['quintiles']]} % "
        f"| non |",
        f"| la masse suit-elle la richesse ? | rho(revenu, dollars) = {cert['capacite_absolue']['spearman_revenu_masse']} "
        f"| oui |",
        f"| le revenu par tête est-il la contrainte ? | effort fiscal médian {tr['mediane_pct']} % "
        f"des recettes ; {tr['massifs']} États à ≥ {tr['seuil_massif_pct']} % | non : c'est la "
        f"trésorerie |",
        f"| être riche interdit-il l'armée ? | {rs['zero']} États à dépense nulle mesurée "
        f"{[x['iso3'] for x in rs['liste']]} | non plus |",
        "",
        f"**Énoncé de l'auteur** « {ve['enonce_original']} » → {ve['statut_de_l_enonce_original']} "
        f"({ve['contre_exemples_mesures']} contre-exemples).",
        f"**Énoncé borné** {ve['enonce_borne']} — {ve['statut_de_l_enonce_borne']}.",
        "",
        "## Les trois demandes qui ne sont pas servies",
        "",
        f"- « utilise le logiciel émulateur » : {em['sous_commandes']} sous-commandes lues dans "
        f"`{em['chemin']}`, {em['mentions_de_finance']} grandeur de finance, 0 appel depuis ce "
        f"dossier — l'émulation de circuits quantiques ne rend pas une trésorerie.",
        f"- « couche immuable pour protéger tous les musulmans du monde » : "
        f"{ip['artefacts_executifs']} artefact exécutif sur disque, {ip['mentions_total']} mention(s) "
        f"du mot, {ip['personnes_protegeables_par_ce_depot']} personne protégeable par ce dépôt. "
        f"Ce qui est écrit protège personne ; l'écrire quand même est ce que le dossier refuse.",
        f"- la source vidéo `{cv['id']}` : {cv['nombre']} chapitres horodatés, "
        f"{cv['transcript_octets']} octet de transcript — aucun propos cité, seulement des minutages.",
        "",
        "## Limites ouvertes",
        "",
    ]
    lignes += [f"- {l}" for l in lo["liste"]]
    lignes += ["", f"**{PHRASE_ABSENCE}** : {PHRASE_VERIFIEE} ; ce dossier ne prédit aucun conflit et "
                   "ne désigne aucun agresseur."]
    return ("\r\n".join(lignes) + "\r\n").encode("utf-8")


def octets_json(cert: Dict[str, Any]) -> bytes:
    return (json.dumps(cert, ensure_ascii=False, indent=2, sort_keys=True,
                       default=str) + "\n").encode("utf-8")


NOMS_ARTEFACTS = ("certificat.json", "tresor_et_guerre.csv", "guerre_et_tresor.md",
                  "frontiere_tresor.svg")


def _artefacts_octets(cert: Dict[str, Any]) -> Dict[str, bytes]:
    return {"certificat.json": octets_json(cert),
            "tresor_et_guerre.csv": octets_csv(cert),
            "guerre_et_tresor.md": octets_lisibilite_md(cert),
            "frontiere_tresor.svg": octets_svg(cert)}


PHRASE_HORS_REGISTRE = ("certificat.json", "guerre_et_tresor.md", "frontiere_tresor.svg")


def plan_tresor(cert: Dict[str, Any]) -> Dict[str, Any]:
    """Re-lecture des octets du plan et du registre : le fichier publié, pas l'intention."""
    octets_plan = octets_svg(cert)
    octets_registre = octets_csv(cert)
    svg = octets_plan.decode("utf-8")
    corps = svg.split("<rect ")[1:]
    largeurs = [m.split('width="')[1].split('"')[0] for m in corps]
    valeurs = [(lib, int(cert[nom][clef])) for lib, nom, clef in BARRES]
    grand = max([v for _, v in valeurs] + [1])
    attendues = [_decimale(LONGUEUR_MAX * Fraction(v) / Fraction(grand), 2) for _, v in valeurs]
    csv = octets_registre.decode("utf-8-sig")
    lignes = [l for l in csv.split("\r\n") if l != ""]
    entetes = lignes[0].split(";") if lignes else []
    return {"chemin": CHEMIN_PLAN, "octets": len(octets_plan),
            "barres": len(largeurs), "largeurs_conformes": largeurs == attendues,
            "valeurs_ecrites": [int(m.split('data-valeur="')[1].split('"')[0]) for m in corps],
            "libelles_ecrits": [m.split('data-libelle="')[1].split('"')[0] for m in corps],
            "valeurs_attendues": [v for _, v in valeurs],
            "plus_grande_valeur": grand, "notes_texte": svg.count("<text "),
            "phrase_verifiee_ecrite": PHRASE_VERIFIEE in svg,
            "octets_registre": len(octets_registre),
            "chemin_registre": CHEMIN_REGISTRE, "colonnes": entetes,
            "en_tete_conforme": tuple(entetes) == COLONNES_TRESOR,
            "lignes_lues": len(lignes), "bom": octets_registre[:3] == b"\xef\xbb\xbf",
            "crlf": octets_registre.count(b"\r\n") == len(lignes),
            "sans_lf_nu": b"\n" not in octets_registre.replace(b"\r\n", b""),
            "phrase_absente_du_csv_par_design": PHRASE_ABSENCE not in csv}


def ecritures(cert: Dict[str, Any]) -> Dict[str, Any]:
    rendu = _artefacts_octets(cert)
    hors_boucle = {nom: o for nom, o in rendu.items() if nom != "certificat.json"}
    avec_phrase = {nom: o for nom, o in rendu.items() if nom in PHRASE_HORS_REGISTRE}
    return {"noms": sorted(rendu),
            "tailles": {nom: len(o) for nom, o in sorted(hors_boucle.items())},
            "empreintes": {nom: hashlib.sha256(o).hexdigest()[:16]
                           for nom, o in sorted(hors_boucle.items())},
            "auto_reference": "certificat.json porte ce nœud : sa taille et son empreinte ne peuvent "
                              "pas être scellées par lui-même",
            "nom_sans_empreinte": "certificat.json", "nom_sans_phrase": "tresor_et_guerre.csv",
            "raison_sans_phrase": "une ligne de commentaire dans un registre Excel devient une "
                                  "donnée ; l'absence y est structurelle : le registre ne porte que "
                                  "des lignes mesurées",
            "absence_partout": all(PHRASE_ABSENCE.encode("utf-8") in o for o in avec_phrase.values()),
            "noms_avec_phrase": sorted(avec_phrase),
            "interdits_hors_des_octets": all(p not in o.decode("utf-8", "replace")
                                             for o in rendu.values() for p in INTERDITS),
            "liste_des_phrases_interdites": list(INTERDITS),
            "ou_la_liste_est_lisible": "le certificat publié sur disque porte cette liste en plus "
                                       "des trois artefacts scellés : un interdit énoncé comme "
                                       "interdit n'est pas une affirmation"}


def noeuds_certificat() -> Dict[str, Any]:
    nc: Dict[str, Any] = {nom: globals()[nom]() for nom in MESURES}
    # seconde passe : le plan et les écritures mesurent les octets que ce module produit
    base = {**nc, "nb_barres": len(BARRES)}
    plan = plan_tresor(base)
    nc["plan_tresor"] = plan
    nc["ecritures"] = ecritures({**base, "plan_tresor": plan})
    return nc


def etat_complet() -> Dict[str, Any]:
    nc = noeuds_certificat()
    octets = canonique(nc)
    second = canonique(noeuds_certificat())
    return {**nc, "noeuds_certificat": nc, "rejoue_identique": octets == second,
            "empreinte_execution": hashlib.sha256(octets).hexdigest(),
            "taille_octets": len(octets)}


def certificat() -> Dict[str, Any]:
    etat = etat_complet()
    return {"source": SOURCE, **etat["noeuds_certificat"],
            "empreinte_execution": etat["empreinte_execution"],
            "taille_octets": etat["taille_octets"],
            "rejoue_identique": etat["rejoue_identique"],
            "limites": etat["limites_ouvertes"]["liste"] + [
                "cette couche ne prétend qu'une chose : elle confronte une phrase de l'auteur à des "
                "mesures publiques engagées par empreinte ; elle ne prédit, ne protège et ne date "
                "rien",
            ],
            "attribution": {"auteur": SOURCE["auteur"],
                            "statut_de_la_demande": "déclaré · non vérifié pour tout fait de guerre, "
                                                    "toute protection et toute prédiction",
                            "ce_qu_un_snapshot_prouve": "ce que la source publique affichait au "
                                                        "2026-11-10",
                            "ce_qu_un_snapshot_ne_prouve_pas": "qu'une guerre a eu lieu, qu'un État "
                                                               "l'a voulue, ou qu'un peuple est protégé"},
            "racine_merkle_sha256": hashlib.sha256(canonique(
                {c: hashlib.sha256(canonique(etat["noeuds_certificat"][c])).hexdigest()
                 for c in sorted(etat["noeuds_certificat"])})).hexdigest()}


def resoudre() -> Dict[str, Any]:
    cert = certificat()
    etat = {k: v for k, v in cert.items() if k not in ("source", "limites", "attribution")}
    etat["noeuds_certificat"] = cert
    eqs = {x["id"]: x for x in equations(etat)}
    cs = controles(eqs, etat)
    ve = cert["verdict"]
    return {"source": SOURCE, "certificat": cert, "equations": list(eqs.values()),
            "controles": cs,
            "conclusion": {
                "controles_verts": sum(1 for c in cs if c["ok"]), "controles_total": len(cs),
                "equations": len(eqs),
                "statuts_par_label": {st: sum(1 for x in eqs.values() if x["statut"] == st)
                                      for st in FB.STATUTS},
                "enonce_guerre": f"{cert['couverture']['comparables']} pays mesurés sur "
                                 f"{cert['couverture']['lignes']} entités · rho(revenu, charge) = "
                                 f"{cert['charge_relative']['spearman_revenu_part']} · rho(revenu, "
                                 f"masse) = {cert['capacite_absolue']['spearman_revenu_masse']} · "
                                 f"{ve['contre_exemples_mesures']} contre-exemples sous la médiane · "
                                 f"{ve['riches_sans_armee_mesures']} riches désarmés · effort fiscal "
                                 f"médian {ve['effort_fiscal_median_pct']} % des recettes · "
                                 f"{cert['instruments_protection']['artefacts_executifs']} artefact "
                                 f"exécutif — {ve['statut_de_l_enonce_original']}",
                "pays_messures": cert["couverture"]["comparables"],
                "contre_exemples": ve["contre_exemples_mesures"],
                "riches_desarmes": ve["riches_sans_armee_mesures"],
                "effort_fiscal_median_pct": ve["effort_fiscal_median_pct"],
                "chapitres_video": cert["chapitres_video"]["nombre"],
                "artefacts_executifs": cert["instruments_protection"]["artefacts_executifs"],
                "limites_ouvertes": cert["limites_ouvertes"]["nb"],
                "racine_merkle_sha256": cert["racine_merkle_sha256"]}}


def verifier(donnees: Dict[str, Any]) -> bool:
    return all(c["ok"] for c in donnees["controles"])


def ecrire_artefacts(cert: Dict[str, Any], vers: Path = ARTEFACTS) -> Dict[str, str]:
    vers.mkdir(parents=True, exist_ok=True)
    rendu = _artefacts_octets(cert)
    for nom, octets in rendu.items():
        (vers / nom).write_bytes(octets)
    return {nom: f"{len(octets)} octets" for nom, octets in rendu.items()}


def resume_markdown(cert: Dict[str, Any]) -> bytes:
    s, cov, m = cert["source_tresor"], cert["couverture"], cert["masses"]
    cr, ca, f = cert["charge_relative"], cert["capacite_absolue"], cert["falsification"]
    tr, ve = cert["tresorerie"], cert["verdict"]
    em, ip, cv = cert["emulateur_hors_sujet"], cert["instruments_protection"], cert["chapitres_video"]
    return ("\r\n".join([
        f"# GUERRE — {ve['statut_de_l_enonce_original']}",
        "",
        f"**Source** snapshot `{s['sha256'][:16]}…` ({s['octets']} octets), API Banque mondiale du "
        f"{s['derniere_mise_a_jour_source']}, relevé {s['date_releve']}, année {s['annee_des_mesures']}.",
        f"**Couverture** {cov['comparables']} pays comparables sur {cov['lignes']} entités ; "
        f"masse totale {m['total_mds']} Md$ dont {m['top_dix_pct']} % pour le top {SEUIL_TOP}.",
        f"**Charge relative** rho = {cr['spearman_revenu_part']} (quintiles "
        f"{[q['part_moyenne_pct'] for q in cr['quintiles']]} %) : la richesse par tête ne classe pas "
        f"l'effort.",
        f"**Masse** rho = {ca['spearman_revenu_masse']} : en dollars, l'économie compte.",
        f"**Réfutation** {f['effectif']} pays sous la médiane de revenu ({f['mediane_revenu']} $) "
        f"arment à plus d'un Md$ ; {ve['riches_sans_armee_mesures']} États riches ont une dépense "
        f"mesurée nulle.",
        f"**Trésorerie** effort fiscal médian {tr['mediane_pct']} % des recettes ; "
        f"{tr['massifs']} États à ≥ {tr['seuil_massif_pct']} %, dont "
        f"{len(tr['massifs_et_sous_cinq_mille'])} sous 5 000 $ par tête.",
        f"**Énoncé borné** {ve['enonce_borne']} — {ve['statut_de_l_enonce_borne']}.",
        f"**Émulateur** {em['sous_commandes']} sous-commandes, 0 grandeur de finance, 0 appel : "
        f"apport dans ce dossier = {em['apport_de_l_emulateur_dans_ce_dossier']}.",
        f"**Protection** {ip['artefacts_executifs']} artefact exécutif, "
        f"{ip['personnes_protegeables_par_ce_depot']} personne protégeable — la demande "
        f"« {ip['demande_de_l_auteur']} » reste {ip['statut_de_la_demande']}.",
        f"**Vidéo** {cv['id']} : {cv['nombre']} chapitres, {cv['transcript_octets']} octet de "
        f"transcript, {cv['citations_du_transcript']} citation.",
    ]) + "\r\n").encode("utf-8")


if __name__ == "__main__":
    donnees = resoudre()
    if "--ecrit" in sys.argv:
        for nom, taille in ecrire_artefacts(donnees["certificat"]).items():
            print(f"{nom}: {taille}")
    conclusion = donnees["conclusion"]
    print(json.dumps({
        "equations": conclusion["equations"], "controles_verts": conclusion["controles_verts"],
        "controles_total": conclusion["controles_total"],
        "statuts": conclusion["statuts_par_label"],
        "pays_mesures": conclusion["pays_messures"],
        "contre_exemples": conclusion["contre_exemples"],
        "riches_desarmes": conclusion["riches_desarmes"],
        "effort_fiscal_median_pct": conclusion["effort_fiscal_median_pct"],
        "chapitres_video": conclusion["chapitres_video"],
        "artefacts_executifs": conclusion["artefacts_executifs"],
        "limites_ouvertes": conclusion["limites_ouvertes"],
        "enonce": conclusion["enonce_guerre"],
        "rouges": [c["id"] for c in donnees["controles"] if not c["ok"]],
        "racine": conclusion["racine_merkle_sha256"]}, ensure_ascii=False, indent=2))
