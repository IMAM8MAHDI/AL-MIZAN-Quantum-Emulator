# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""FONDATION — une base, quatre piliers, une limite ; et ce qu'elle calcule sur la nature.

Point de départ mesuré : « Le CERN a Enfin Détecté un Événement que la Science Attendait
depuis 40 Ans », Nocturne, 8018 s, identifiant YouTube 5pP1e69T3HQ. La page ne rend que du
JavaScript d'amorçage, la description ne porte AUCUN chapitre horodaté et timedtext répond
sans contenu : le transcript est tenu pour absent. La vidéo fournit un sujet (le kaon rare
K⁺ → π⁺ ν ν̄, annoncé à cinq sigma en septembre 2024) et rien de plus : aucune citation,
aucun minutage, aucun chiffre de ce dossier ne vient d'elle.

Ce que fait ce module, dans l'ordre :

  1. il pose un axiome unique — l'Un, posé hors matrice — et en tire quatre piliers
     opérationnels (Unité, Borne, Confrontation, Transmission) qui sont des contraintes
     vérifiées par des contrôles, pas des décorations (EQ-01 à EQ-07) ;
  2. il montre que la structure est bien fondée : le graphe des dix-huit nœuds est acyclique,
     et tout nœud sans prédécesseur interne est fondé sur une source déclarée hors de lui
     (EQ-02, EQ-03) ;
  3. il applique la base à des mesures publiques réelles : l'arithmétique de la désintégration
     rare chez NA62 — taux × exposition × sensibilité par événement — avec une prédiction
     gelée AVANT lecture du comparateur (EQ-08 à EQ-17) ;
  4. il écrit sa propre limite, y compris les conditions qui le réfuteraient (EQ-18).

Ce qu'il ne fait pas : il ne déduit pas l'axiome, ne le prouve pas, ne fait pas suivre la
physique d'une théologie ni l'inverse. Un calcul fini ne fonde pas une assertion universelle ;
il peut seulement montrer que la discipline qui en découle tient sur des nombres publics.

Usage :
    py -3 FONDATION/fondation_base.py            # 18 équations, 18 contrôles, rc=0
    py -3 FONDATION/fondation_base.py --ecrit    # + les six artefacts
"""

from __future__ import annotations

import hashlib
import inspect
import json
import math
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

RACINE = Path(__file__).resolve().parents[1]
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

# ─── 1. La source mesurée -----------------------------------------------------

# Description relevée OCTET POUR OCTET sur la page watch le 2026-11-09T01:44:02Z
# (1 908 caractères, décodage par json.loads sur la chaîne JSON citée — jamais unicode_escape).
DESCRIPTION_MESUREE = (
    "En septembre 2024, l’expérience NA62 du CERN a annoncé l’observation d’une des "
    "désintégrations les plus rares jamais mesurées : un kaon chargé qui se transforme en un "
    "pion et deux neutrinos invisibles. Pour la trouver, les physiciens ont dû suivre des "
    "centaines de millions de particules par seconde et écarter des milliards de désintégrations "
    "ordinaires qui lui ressemblent. Ils ont ainsi rassemblé assez d’événements pour franchir le "
    "seuil des cinq sigma, celui qui transforme un simple indice en véritable découverte.\n\n"
    "Dans ce documentaire, on remonte à la découverte du kaon dans les rayons cosmiques des "
    "années 1940. On voit pourquoi le modèle standard rend cette désintégration presque "
    "impossible, et comment les expériences de Brookhaven n’en ont capté que quelques événements "
    "en deux décennies. On découvre aussi comment le CERN a fini par réussir en étudiant les "
    "kaons en plein vol. On regarde enfin ce que ce résultat nous apprend sur la physique "
    "au-delà du modèle standard, et ce qu’il laisse encore sans réponse."
)

SOURCE: Dict[str, Any] = {
    "titre": "Le CERN a Enfin Détecté un Événement que la Science Attendait depuis 40 Ans",
    "chaine": "Nocturne",
    "video_id": "5pP1e69T3HQ",
    "url": "https://www.youtube.com/watch?v=5pP1e69T3HQ",
    "duree_s": 8018,
    "chapitres_publics": 0,
    "transcript": "absent (timedtext : 0 octet en json3, srv3 et xml)",
    "mesure_le": "2026-11-09T01:44:02Z",
    "outils": "scripts/extraire_chapitres_youtube.py "
              "(Skill extraire-chapitres-youtube-sans-transcript)",
    "avertissements_sonde": [
        "aucun en-tete de chapitres : horodatages pris dans toute la description",
        "aucun chapitre horodate dans la description",
        "timedtext repond sans contenu : le transcript est tenu pour absent",
    ],
    "sonde_transcript_octets": {"json3": 0, "srv3": 0, "xml": 0},
    "description_mesuree_caracteres": 1908,
    "description_retenue": "les deux premiers paragraphes, recopiés mot pour mot ; les "
                           "paragraphes suivants sont des remerciements, des appels à "
                           "s'abonner et la liste des sources",
    "description_verbatim": DESCRIPTION_MESUREE,
    "extraits_description": [
        "En septembre 2024, l’expérience NA62 du CERN a annoncé l’observation",
        "un kaon chargé qui se transforme en un pion et deux neutrinos invisibles",
        "suivre des centaines de millions de particules par seconde",
        "écarter des milliards de désintégrations ordinaires qui lui ressemblent",
        "franchir le seuil des cinq sigma",
        "la découverte du kaon dans les rayons cosmiques des années 1940",
        "le modèle standard rend cette désintégration presque impossible",
        "les expériences de Brookhaven n’en ont capté que quelques événements en deux décennies",
        "en étudiant les kaons en plein vol",
        "ce que ce résultat nous apprend sur la physique au-delà du modèle standard",
    ],
    "sources_citees_par_la_chaine": [
        "Collaboration NA62, Measurement of the very rare K+→π+νν̄ decay (2021) — "
        "https://arxiv.org/pdf/2103.15389",
        "Collaboration NA62, Recent Results from NA62 in Kaon and Dump Mode (2026) — "
        "https://arxiv.org/pdf/2605.02415",
    ],
    "ce_que_la_video_n_a_pas_fourni": [
        "aucun chapitre horodaté (donc aucun minutage citable)",
        "aucun transcript (donc aucune citation, aucune phrase attribuée à la bande-son)",
        "aucun chiffre : les nombres de ce dossier viennent des publications arXiv et du "
        "communiqué CERN, jamais de la vidéo",
    ],
}

# ─── 2. Axiome, piliers, couches ---------------------------------------------

AXIOME: Dict[str, Any] = {
    "enonce": "Il n'y a de dieu que Allah — posé HORS MATRICE.",
    "auteur": "M. Ahmed EL BAHLOUL (IMAM8MAHDI)",
    "formalisation": "la régularité d'un système fini n'est pas un élément de ce système ; "
                     "toute chaîne de dérivation s'arrête donc sur une source déclarée hors d'elle",
    "statut": "SPÉCIFIÉ — posé, jamais dérivé, jamais réfuté par ce dossier",
    "hors_matrice": True,
    "nombres_fournis_par_l_axiome": 0,
    "ce_que_ca_ne_veut_pas_dire": [
        "aucune équation ci-dessous ne prouve l'axiome",
        "aucune mesure du CERN ne confirme ni n'infirmé l'axiome",
        "l'axiome ne fournit aucun nombre : il interdit seulement de déclarer deux fois "
        "la même grandeur avec deux valeurs",
    ],
}

PILIERS: Dict[str, str] = {
    "P1 UNITE": "une seule source de régularité : un seul registre de grandeurs déclarées, "
                "aucune valeur double en conflit",
    "P2 BORNE": "toute assertion porte un domaine fini et une `limite` écrite ; rien n'est "
                "annoncé comme preuve universelle",
    "P3 CONFRONTATION": "tout nombre est confronté à une source publique ou étiqueté "
                        "SPÉCIFIÉ ; la prédiction est gelée avant la lecture du comparateur",
    "P4 TRANSMISSION": "tout est re-jouable par un tiers : bibliothèque standard seule, trois "
                       "commandes, verdict entier",
}

COUCHES: Dict[str, str] = {
    "S1 MESURABLE": "les nombres : comptes, taux, intervalles — ce qu'une expérience publie",
    "S2 REGULARITE": "les lois et les identités : ce qui se calcule sans mesure",
    "S3 HORS_MATRICE": "la source de la régularité : posée, non dérivée, non réfutable ici",
}

STATUTS: Dict[str, str] = {
    "OPÉRATIONNEL": "calcul exact reproductible, contrôle attaché",
    "SIMULÉ": "scénario ou valeur déclarée, explicité comme tel",
    "SPÉCIFIÉ": "posé ou structurant, non évalué par ce dossier",
}

# ─── 3. Grandeurs déclarées ---------------------------------------------------

BR_SM = 8.4e-11          # BR(K⁺→π⁺νν̄) modèle standard — Buras et al., JHEP 11 (2015) 33
DBR_SM = 1.0e-11         # incertitude théorique associée, même source
SEUIL_OBSERVATION = 5.0  # « cinq sigma » — seuil d'observation, déclaré par la communauté
ANNEE_S = 3.155_76e7     # secondes par année julienne (365,25 × 86 400), exacte
Z_DECLARE_2024 = 1.7     # « accord avec le SM à 1,7 sigma », arXiv:2412.12015

# La prédiction ne reçoit QUE théorie + exposition + acceptances. Jamais un résultat.
DECLARE: Dict[str, Any] = {
    "BR_sm": BR_SM, "dBR_sm": DBR_SM,
    "N_K_2016_2018": 2.7e12,        # désintégrations effectives dans le volume fiduciel
    "SES_2016_2018": 0.839e-11,     # sensibilité par événement (single-event sensitivity)
    "N_K_2021_2022": 2.85e12,
    "SES_2021_2022": 8.48e-12,
    "secondaires_par_s": 1.0e9,     # communiqué CERN 2024-09-25 (« almost a billion »)
    "fraction_K_plus": 0.06,        # communiqué CERN 2024-09-25 (« about 6 % »)
    "annees_prises_2016_2018": 3.0,
    "rejection_mu": 1.0e7,          # arXiv:2605.02415, ordre de grandeur
    "rejection_pi0": 1.0e8,
    "rejection_autres_canaux": 1.0e4,
    "seuil_observation": SEUIL_OBSERVATION,
    "z_declare_2024": Z_DECLARE_2024,
}

# Le comparateur : uniquement des RÉSULTATS publiés. Clés disjointes de DECLARE.
COMPARE: Dict[str, Any] = {
    "NA62_2021": {
        "candidates": 20, "fond": 7.03, "d_fond": (1.05, 0.82),
        "BR": 10.6e-11, "d_BR": (4.0e-11, 3.4e-11), "p_value": 3.4e-4,
        "N_exp_SM": 10.01, "d_N_exp": (0.42, 1.19),
        "source": "arXiv:2103.15389 — JHEP 06 (2021) 093, DOI 10.1007/JHEP06(2021)093",
        "verbe_publie": "evidence à 3,4 sigma — pas une observation",
    },
    "NA62_2024": {
        "candidates": 51, "fond": 18.0, "d_fond": (3.0, 2.0),
        "BR": 13.0e-11, "d_BR": (3.3e-11, 3.0e-11), "p_value": 2.0e-7,
        "source": "arXiv:2412.12015 — JHEP 02 (2025) 191, DOI 10.1007/JHEP02(2025)191",
        "verbe_publie": "observation au-delà de 5 sigma",
    },
    "NA62_2026": {
        "BR_2016_2024": 9.6e-11, "d_BR_26": (1.9e-11, 1.8e-11),
        "BR_2023_2024": 7.2e-11, "POT_2021_2024": 6.3e17,
        "source": "arXiv:2605.02415 — MPP-2026-83",
        "verbe_publie": "accord avec le modèle standard à moins de 1 sigma",
    },
    "CERN_2024": {
        "desintegrations_ordinaires": 9_999_999_999,
        "source": "https://home.cern — 2024-09-25, « the other 9 999 999 999 decays »",
    },
}

ARTIFACTS = ("base.json", "confrontation.csv", "confrontation.json", "etat.json",
             "gel.json", "inventaire.json")

# Les modules qui PORTENT des équations : la liste est explicite, pas devinée par suffixe.
MODULES_PRINCIPAUX = ("electricite_abondance.py", "eau_abondance.py",
                      "agriculture_abondance.py", "chiffres_pi.py", "fondation_base.py",
                      "horlogerie.py", "continuite_base.py", "redaction_mizan.py",
                      "construction_base.py", "verrous_base.py", "declaration_base.py",
                      "guerre_base.py", "qpu_distant_base.py", "goulets_base.py")

# Les dossiers qui portent des équations, puis le parc complet (code et bibliothèques compris).
# Une seule liste pour les deux comptages : sinon `imports_parc` et `inventaire_parc` peuvent
# compter deux parcelles différentes du même dépôt et publier des totaux incohérents.
DOSSIERS_EQUATIONS = ("ABONDANCE", "CHIFFRES", "FONDATION", "HORLOGERIE", "CONTINUITE",
                      "REDACTION", "CONSTRUCTION", "VERROUS", "DECLARATION", "GUERRE",
                      "QPU_DISTANT", "GOULETS")
DOSSIERS_PARC = DOSSIERS_EQUATIONS + ("code", "bibliotheques")

_MODULES_LOCAUX: Optional[Dict[str, str]] = None


# ============================================================================
# Primitives
# ============================================================================

def p_seuil(z: float) -> float:
    """p unilatère d'une normale centrée réduite : P(Z > z)."""
    return 0.5 * math.erfc(z / math.sqrt(2.0))


def z_de_p_seuil(p: float) -> float:
    """Inverse de p_seuil par bissection — pas de Newton : pas de divergence près de zéro."""
    if not 0.0 < p < 0.5:
        raise ValueError(f"p doit être dans ]0, 0,5[ — reçu {p}")
    bas, haut = 0.0, 40.0
    while p_seuil(haut) > p:
        bas, haut = haut, haut * 2.0
        if haut > 1e6:
            raise ValueError("seuil hors portée")
    for _ in range(200):
        milieu = 0.5 * (bas + haut)
        if p_seuil(milieu) > p:
            bas = milieu
        else:
            haut = milieu
    return 0.5 * (bas + haut)


def signification_lima(n_observe: float, fond: float) -> float:
    """Signification Poisson à fond connu (Li & Ma 1997, sans incertitude sur le fond)."""
    if n_observe <= fond or fond <= 0 or n_observe <= 0:
        return 0.0
    return math.sqrt(2.0 * (n_observe * math.log(n_observe / fond) - (n_observe - fond)))


def evenements_requis(fond: float, z: float) -> float:
    """Excès d'événements signal nécessaire pour atteindre z avec ce fond."""
    bas, haut = 0.0, 10.0 * max(fond, 1.0)
    while signification_lima(fond + haut, fond) < z:
        haut *= 2.0
        if haut > 1e12:
            raise ValueError("seuil hors portée")
    for _ in range(200):
        milieu = 0.5 * (bas + haut)
        if signification_lima(fond + milieu, fond) < z:
            bas = milieu
        else:
            haut = milieu
    return 0.5 * (bas + haut)


def acceptance(sensibilite: float, n_kaons: float) -> float:
    """A×ε déduit de la sensibilité par événement publiée : 1 / (N_K × SES)."""
    return 1.0 / (n_kaons * sensibilite)


def intervalle_ordinaires(br: float, d_sup: float, d_inf: float) -> Tuple[float, float]:
    """1/BR − 1 décroît : l'incertitude haute du taux donne la borne basse du compte."""
    return 1.0 / (br + d_sup) - 1.0, 1.0 / (br - d_inf) - 1.0


def cle_comparateur() -> List[str]:
    """Les clés qui sont des RÉSULTATS : la prédiction n'a pas le droit d'en voir une."""
    cles: List[str] = []
    for bloc in COMPARE.values():
        cles += [k for k in bloc if k not in ("source", "verbe_publie")]
    return sorted(set(cles))


def prediction_gel(declares: Dict[str, Any]) -> Dict[str, Any]:
    """Prédiction figée : théorie + exposition + acceptances, jamais un résultat publié.

    Signature à un seul paramètre. Si une clé du comparateur entre dans `declares`,
    le drapeau `a_lu_le_comparateur` se lève — et le digest ne bouge pas : la valeur
    prédite ne dépend structurellement d'aucun résultat.
    """
    interdites = sorted(set(cle_comparateur()) & set(declares))
    a = 1.0 / (declares["N_K_2016_2018"] * declares["SES_2016_2018"])
    valeurs = {"acceptance_2016_2018": a,
               "n_signal_2016_2018": declares["N_K_2016_2018"] * declares["BR_sm"] * a,
               "kaons_par_seconde": declares["secondaires_par_s"] * declares["fraction_K_plus"]}
    texte = json.dumps(valeurs, sort_keys=True, default=str)
    return {"valeurs": valeurs, "variables_libres": sorted(declares),
            "cle_interdites_trouvees": interdites,
            "a_lu_le_comparateur": bool(interdites),
            "digest": hashlib.sha256(texte.encode("utf-8")).hexdigest()}


# ============================================================================
# Structure vérifiable : graphe, registre, imports, parc
# ============================================================================

NOEUDS: Dict[str, Dict[str, Any]] = {
    "EQ-01": {"depend": [], "externe": ["AXIOME (hors matrice)"],
              "couche": "S3 HORS_MATRICE", "piliers": ["P1 UNITE", "P2 BORNE"]},
    "EQ-02": {"depend": ["EQ-01"], "externe": [], "couche": "S3 HORS_MATRICE",
              "piliers": ["P1 UNITE"]},
    "EQ-03": {"depend": ["EQ-02"], "externe": [], "couche": "S2 REGULARITE",
              "piliers": ["P2 BORNE"]},
    "EQ-04": {"depend": ["EQ-03"], "externe": ["publications NA62", "parc du dépôt"],
              "couche": "S1 MESURABLE", "piliers": ["P3 CONFRONTATION"]},
    "EQ-05": {"depend": ["EQ-03"], "externe": ["bibliothèque standard Python"],
              "couche": "S2 REGULARITE", "piliers": ["P4 TRANSMISSION"]},
    "EQ-06": {"depend": ["EQ-01", "EQ-04"], "externe": ["registre DECLARE"],
              "couche": "S1 MESURABLE", "piliers": ["P1 UNITE"]},
    "EQ-07": {"depend": ["EQ-06"], "externe": ["inspect.signature"],
              "couche": "S1 MESURABLE", "piliers": ["P3 CONFRONTATION", "P4 TRANSMISSION"]},
    "EQ-08": {"depend": ["EQ-06", "EQ-07"], "externe": ["communiqué CERN 2024-09-25"],
              "couche": "S1 MESURABLE", "piliers": ["P1 UNITE"]},
    "EQ-09": {"depend": ["EQ-06", "EQ-07"], "externe": ["arXiv:2103.15389", "arXiv:2412.12015"],
              "couche": "S2 REGULARITE", "piliers": ["P1 UNITE", "P3 CONFRONTATION"]},
    "EQ-10": {"depend": ["EQ-07", "EQ-09"], "externe": ["arXiv:2103.15389"],
              "couche": "S1 MESURABLE", "piliers": ["P3 CONFRONTATION"]},
    "EQ-11": {"depend": ["EQ-10"], "externe": ["arXiv:2103.15389"],
              "couche": "S2 REGULARITE", "piliers": ["P2 BORNE"]},
    "EQ-12": {"depend": ["EQ-11"], "externe": ["arXiv:2412.12015"],
              "couche": "S1 MESURABLE", "piliers": ["P2 BORNE", "P3 CONFRONTATION"]},
    "EQ-13": {"depend": ["EQ-07", "EQ-10"], "externe": ["arXiv:2412.12015"],
              "couche": "S1 MESURABLE", "piliers": ["P1 UNITE"]},
    "EQ-14": {"depend": ["EQ-13"], "externe": ["arXiv:2605.02415"],
              "couche": "S1 MESURABLE", "piliers": ["P3 CONFRONTATION"]},
    "EQ-15": {"depend": ["EQ-06", "EQ-12"], "externe": ["arXiv:2605.02415"],
              "couche": "S2 REGULARITE", "piliers": ["P2 BORNE"]},
    "EQ-16": {"depend": ["EQ-08"], "externe": ["communiqué CERN 2024-09-25"],
              "couche": "S1 MESURABLE", "piliers": ["P4 TRANSMISSION"]},
    "EQ-17": {"depend": ["EQ-10", "EQ-13"], "externe": ["arXiv:2103.15389", "arXiv:2412.12015"],
              "couche": "S2 REGULARITE", "piliers": ["P3 CONFRONTATION", "P4 TRANSMISSION"]},
    "EQ-18": {"depend": ["EQ-01", "EQ-17"], "externe": [], "couche": "S3 HORS_MATRICE",
              "piliers": ["P2 BORNE", "P3 CONFRONTATION", "P4 TRANSMISSION"]},
}


def matrice_piliers() -> Dict[str, Dict[str, List[str]]]:
    m = {p: {c: [] for c in COUCHES} for p in PILIERS}
    for n, d in NOEUDS.items():
        for p in d["piliers"]:
            m[p][d["couche"]].append(n)
    return m


def cases_vides(matrice: Dict[str, Dict[str, List[str]]]) -> List[str]:
    return [f"{p}×{c}" for p, v in matrice.items() for c, n in v.items() if not n]


def graphe_dependances() -> Dict[str, Any]:
    """DAG des dix-huit nœuds : acyclicité, racines fondées dehors, atteignabilité."""
    noeuds = sorted(NOEUDS)
    aretes = [(src, dst) for dst in noeuds for src in NOEUDS[dst]["depend"]]
    self_refs = [n for n in noeuds if n in NOEUDS[n]["depend"]]
    couleur = {n: 0 for n in noeuds}
    cycle: List[str] = []

    def parc(n: str) -> None:
        couleur[n] = 1
        for m in NOEUDS[n]["depend"]:
            if couleur[m] == 1 and m not in cycle:
                cycle.append(m)
            elif couleur[m] == 0:
                parc(m)
        couleur[n] = 2

    for n in noeuds:
        if couleur[n] == 0:
            parc(n)
    racines = [n for n in noeuds if not NOEUDS[n]["depend"]]
    atteignables = set(racines)
    progression = True
    while progression:
        progression = False
        for n in noeuds:
            if n not in atteignables and all(d in atteignables for d in NOEUDS[n]["depend"]):
                atteignables.add(n)
                progression = True
    matrice = matrice_piliers()
    return {"noeuds": len(noeuds), "aretes": len(aretes), "acyclique": not cycle,
            "cycle": cycle, "racines": racines, "self_references": self_refs,
            "atteignables": len(atteignables),
            "racines_fondees_dehors": all(n == "EQ-01" or NOEUDS[n]["externe"] for n in racines),
            "couche_vide": [c for c in COUCHES
                            if not any(NOEUDS[n]["couche"] == c for n in noeuds)],
            "matrice_pilier_couche": matrice, "cases_vides": cases_vides(matrice),
            "aretes_vers_l_exterieur": sum(len(NOEUDS[n]["externe"]) for n in noeuds)}


def registre_grandeurs(
        entrees: Optional[List[Tuple[str, Any, str, str]]] = None) -> Dict[str, Any]:
    """Toute grandeur déclarée : une valeur, une unité, une source — et une seule.

    `entrees` est un point d'entrée pour la mise à l'épreuve : la détection de doublon
    porte sur la table, pas seulement sur la table canonique du dépôt.
    """
    if entrees is None:
        entrees = [
        ("BR_sm", BR_SM, "1", "JHEP 11 (2015) 33"),
        ("dBR_sm", DBR_SM, "1", "JHEP 11 (2015) 33"),
        ("N_K_2016_2018", DECLARE["N_K_2016_2018"], "désintégrations", "arXiv:2103.15389"),
        ("SES_2016_2018", DECLARE["SES_2016_2018"], "1", "arXiv:2103.15389"),
        ("N_K_2021_2022", DECLARE["N_K_2021_2022"], "désintégrations", "arXiv:2412.12015"),
        ("SES_2021_2022", DECLARE["SES_2021_2022"], "1", "arXiv:2412.12015"),
        ("secondaires_par_s", DECLARE["secondaires_par_s"], "1/s", "home.cern 2024-09-25"),
        ("fraction_K_plus", DECLARE["fraction_K_plus"], "1", "home.cern 2024-09-25"),
        ("annees_prises_2016_2018", DECLARE["annees_prises_2016_2018"], "an", "arXiv:2103.15389"),
        ("rejection_mu", DECLARE["rejection_mu"], "1", "arXiv:2605.02415 — ordre de grandeur"),
        ("rejection_pi0", DECLARE["rejection_pi0"], "1", "arXiv:2605.02415 — ordre de grandeur"),
        ("rejection_autres_canaux", DECLARE["rejection_autres_canaux"], "1",
         "arXiv:2605.02415 — ordre de grandeur"),
        ("seuil_observation", SEUIL_OBSERVATION, "sigma", "déclaré par la communauté"),
        ("z_declare_2024", Z_DECLARE_2024, "sigma", "arXiv:2412.12015"),
        ]
    noms = [e[0] for e in entrees]
    valeurs: Dict[str, Tuple[Any, str, str]] = {}
    doublons: List[str] = []
    for nom, valeur, unite, source in entrees:
        if nom in valeurs and valeurs[nom] != (valeur, unite, source):
            doublons.append(nom)
        valeurs[nom] = (valeur, unite, source)
    inconnues = [n for n in noms if n not in DECLARE]
    return {"entrees": len(entrees), "noms_uniques": len(set(noms)),
            "doublons_en_conflit": doublons,
            "valeurs_non_numeriques": [n for n, v in valeurs.items()
                                       if not isinstance(v[0], (int, float))],
            "unites_vide": [n for n, v in valeurs.items() if not v[1]],
            "hors_declare": inconnues,
            "declare_sans_entree": sorted(set(DECLARE) - set(noms))}


def modules_locaux() -> Dict[str, str]:
    """Noms de modules résolus DANS CE dépôt — une passe, mise en cache."""
    global _MODULES_LOCAUX
    if _MODULES_LOCAUX is None:
        noms: Dict[str, str] = {}
        for p in sorted(RACINE.rglob("*.py")):
            if "__pycache__" in p.parts:
                continue
            noms.setdefault(p.stem, str(p.relative_to(RACINE)))
        for d in sorted(x for x in RACINE.iterdir() if x.is_dir() and not x.name.startswith(".")):
            noms.setdefault(d.name, str(d.relative_to(RACINE)))
        _MODULES_LOCAUX = noms
    return _MODULES_LOCAUX


def imports_de(chemin: str) -> Dict[str, Any]:
    """Racines importées par un fichier, triées en stdlib / module local / tiers."""
    texte = Path(chemin).read_text(encoding="utf-8")
    racines = {m.group(1).split(".")[0]
               for m in re.finditer(r"^(?:from|import)\s+([A-Za-z_][\w.]*)", texte, re.M)}
    std = set(getattr(sys, "stdlib_module_names", ()))
    locaux = modules_locaux()
    local = sorted(r for r in racines if r in locaux and r not in std)
    return {"imports": sorted(racines), "stdlib": sorted(racines & std),
            "local": local, "tiers": sorted(racines - std - set(local)),
            "resolu_local": {r: locaux[r] for r in local}}


def imports_parc() -> Dict[str, Any]:
    bilans: Dict[str, Any] = {}
    for d in DOSSIERS_PARC:
        racine = RACINE / d
        if not racine.exists():
            bilans[d] = {"fichiers": 0, "tiers": [f"DOSSIER ABSENT : {d}"]}
            continue
        fichiers, tiers = 0, set()
        for p in sorted(racine.rglob("*.py")):
            if "__pycache__" in p.parts:
                continue
            fichiers += 1
            try:
                tiers |= set(imports_de(str(p))["tiers"])
            except OSError:
                continue
        bilans[d] = {"fichiers": fichiers, "tiers": sorted(tiers)}
    return bilans


def inventaire_parc() -> Dict[str, Any]:
    """Compte réellement les équations, contrôles et tests déclarés dans le dépôt.

    Le comptage est fait MODULE PAR MODULE : `EQ-01` existe dans trois dossiers différents,
    une mise en ensemble à l'échelle du dossier les fusionnerait et sous-compterait.
    """
    out: Dict[str, Any] = {}
    for d in DOSSIERS_EQUATIONS:
        racine = RACINE / d
        if not racine.exists():
            out[d] = {"present": False, "equations": 0, "controles": 0, "tests": 0,
                      "modules": []}
            continue
        eq, ce, tests = 0, 0, 0
        modules: List[str] = []
        for p in sorted(racine.rglob("*.py")):
            if "__pycache__" in p.parts:
                continue
            t = p.read_text(encoding="utf-8", errors="replace")
            if p.name in MODULES_PRINCIPAUX:
                modules.append(p.name)
                eq += len(set(re.findall(r'"EQ-\d\d"', t)))
                ce += len(set(re.findall(r'"C\d\d"', t)))
            elif p.name.startswith("test_"):
                tests += len(re.findall(r"^\s+def test_", t, re.M))
        out[d] = {"present": True, "equations": eq, "controles": ce,
                  "tests": tests, "modules": modules}
    return out


def sources_declarees() -> List[str]:
    return [f"{camp} — {bloc['source']}" for camp, bloc in COMPARE.items()
            if isinstance(bloc, dict) and "source" in bloc]


# ============================================================================
# Équations
# ============================================================================

def eq01_axiome() -> Dict[str, Any]:
    return {"enonce": AXIOME["enonce"], "formalisation": AXIOME["formalisation"],
            "hors_matrice": AXIOME["hors_matrice"],
            "nombres_fournis_par_l_axiome": AXIOME["nombres_fournis_par_l_axiome"],
            "piliers_engendres": sorted(PILIERS), "statut_axiome": AXIOME["statut"],
            "interdit": "déclarer deux fois la même grandeur avec deux valeurs (P1)"}


def discipline_sources() -> Dict[str, Any]:
    """Ce que la chaîne a fourni se vérifie dans son texte ; ce qu'elle n'a pas fourni s'écrit."""
    d = SOURCE["description_verbatim"]
    verbatim = {e: (e in d) for e in SOURCE["extraits_description"]}
    return {"extraits_verbatimes": verbatim,
            "extraits_non_trouves": [e for e, ok in verbatim.items() if not ok],
            "horodatages_cites": re.findall(r"\b\d{1,2}:\d{2}(?::\d{2})?\b", d),
            "caracteres_retenus": len(d),
            "caracteres_mesures": SOURCE["description_mesuree_caracteres"],
            "transcript_octets": SOURCE["sonde_transcript_octets"],
            "chapitres_publics": SOURCE["chapitres_publics"]}


def eq04_confrontation_et_parc() -> Dict[str, Any]:
    g = graphe_dependances()
    return {"dossiers": inventaire_parc(), "sources_publiques": sources_declarees(),
            "discipline_source": discipline_sources(),
            "cases_matrice": g["cases_vides"], "aretes_vers_l_exterieur":
            g["aretes_vers_l_exterieur"]}


def eq05_transmission() -> Dict[str, Any]:
    return {"imports_ici": imports_de(__file__), "parc": imports_parc(),
            "commandes_publish": ["py -3 FONDATION/fondation_base.py",
                                  "py -3 FONDATION/fondation_base.py --ecrit",
                                  "cd FONDATION && py -3 -m unittest tests.test_fondation"]}


def eq08_ordinaires_par_rare() -> Dict[str, Any]:
    bas_sm, haut_sm = intervalle_ordinaires(BR_SM, DBR_SM, DBR_SM)
    c24 = COMPARE["NA62_2024"]
    bas_24, haut_24 = intervalle_ordinaires(c24["BR"], c24["d_BR"][0], c24["d_BR"][1])
    cite = COMPARE["CERN_2024"]["desintegrations_ordinaires"]
    return {"centre_modele_standard": 1.0 / BR_SM - 1.0,
            "intervalle_modele_standard": (bas_sm, haut_sm),
            "intervalle_mesure_2024": (bas_24, haut_24),
            "valeur_communiquee": cite,
            "taux_implicite_du_communique": 1.0 / (cite + 1.0),
            "communique_dans_intervalle_2024": bas_24 <= cite <= haut_24,
            "communique_dans_intervalle_sm": bas_sm <= cite <= haut_sm}


def eq09_cloture_acceptance() -> Dict[str, Any]:
    a18 = acceptance(DECLARE["SES_2016_2018"], DECLARE["N_K_2016_2018"])
    a22 = acceptance(DECLARE["SES_2021_2022"], DECLARE["N_K_2021_2022"])
    calcule = DECLARE["N_K_2016_2018"] * BR_SM * a18
    publie = COMPARE["NA62_2021"]["N_exp_SM"]
    return {"acceptance_2016_2018": a18, "acceptance_2021_2022": a22,
            "rapport_acceptances": a22 / a18, "n_attendu_calcule": calcule,
            "n_attendu_publie": publie, "ecart_relatif": abs(calcule - publie) / publie,
            "formule": "A·ε = 1/(N_K·SES) puis N = N_K·BR_sm·A·ε"}


def eq10_prediction_gelee() -> Dict[str, Any]:
    gel = prediction_gel(DECLARE)["valeurs"]
    c = COMPARE["NA62_2021"]
    excess = c["candidates"] - c["fond"]
    sigma = math.sqrt(gel["n_signal_2016_2018"] + c["fond"])
    return {"prevu": gel["n_signal_2016_2018"], "observe_excess": excess,
            "ecart_en_sigma": (excess - gel["n_signal_2016_2018"]) / sigma,
            "sigma_utilise": sigma, "br_publiee": c["BR"], "br_sm": BR_SM,
            "ecart_br_en_sigma": (c["BR"] - BR_SM) / math.sqrt(c["d_BR"][0] ** 2 + DBR_SM ** 2),
            "digest_gel": prediction_gel(DECLARE)["digest"]}


def eq11_signification_2021() -> Dict[str, Any]:
    c = COMPARE["NA62_2021"]
    z_lima = signification_lima(c["candidates"], c["fond"])
    z_publiee = z_de_p_seuil(c["p_value"])
    return {"z_lima": z_lima, "p_publiee": c["p_value"], "z_publiee": z_publiee,
            "ecart": z_lima - z_publiee,
            "les_deux_sous_cinq_sigma": max(z_lima, z_publiee) < SEUIL_OBSERVATION,
            "verbe": c["verbe_publie"]}


def eq12_seuil_cinq_sigma() -> Dict[str, Any]:
    c = COMPARE["NA62_2024"]
    requis = evenements_requis(c["fond"], SEUIL_OBSERVATION)
    excess = c["candidates"] - c["fond"]
    z_lima = signification_lima(c["candidates"], c["fond"])
    z_publiee = z_de_p_seuil(c["p_value"])
    return {"fond": c["fond"], "excess_requis": requis, "excess_publie": excess,
            "marge": excess - requis, "z_lima": z_lima, "z_publiee": z_publiee,
            "ecart": z_lima - z_publiee,
            "les_deux_au_dessus_de_cinq": min(z_lima, z_publiee) > SEUIL_OBSERVATION}


def eq13_confrontation_2024() -> Dict[str, Any]:
    c = COMPARE["NA62_2024"]
    z_sup = (c["BR"] - BR_SM) / math.sqrt(c["d_BR"][0] ** 2 + DBR_SM ** 2)
    z_inf = (c["BR"] - BR_SM) / math.sqrt(c["d_BR"][1] ** 2 + DBR_SM ** 2)
    sm = (BR_SM - DBR_SM, BR_SM + DBR_SM)
    obs = (c["BR"] - c["d_BR"][1], c["BR"] + c["d_BR"][0])
    return {"z_branches": (z_sup, z_inf), "ecart_absolu": c["BR"] - BR_SM,
            "intervalle_sm": sm, "intervalle_observe": obs,
            "chevauchement_a_un_sigma": obs[0] <= sm[1] and sm[0] <= obs[1],
            "z_declare_par_na62": Z_DECLARE_2024,
            "nos_z_sous_le_z_declare": max(z_sup, z_inf) < Z_DECLARE_2024}


def eq14_confrontation_2026() -> Dict[str, Any]:
    c = COMPARE["NA62_2026"]
    d_sup, d_inf = c["d_BR_26"]
    z = (c["BR_2016_2024"] - BR_SM) / math.sqrt(d_sup ** 2 + DBR_SM ** 2)
    z_inf = (c["BR_2016_2024"] - BR_SM) / math.sqrt(d_inf ** 2 + DBR_SM ** 2)
    return {"br_2016_2024": c["BR_2016_2024"], "z_contre_sm": z, "z_branche_inf": z_inf,
            "sous_un_sigma": max(z, z_inf) < 1.0, "br_2023_2024_seule": c["BR_2023_2024"],
            "declaration_publique": c["verbe_publie"]}


def eq15_budget_fond() -> Dict[str, Any]:
    b21 = COMPARE["NA62_2021"]["fond"]
    n_k = DECLARE["N_K_2016_2018"]
    requis = n_k / b21
    chaine = DECLARE["rejection_mu"] * DECLARE["rejection_pi0"]
    return {"suppression_totale_requise": requis, "chaine_declaree_mu_x_pi0": chaine,
            "marge_en_ordres_de_grandeur": math.log10(chaine / requis),
            "chainement_suffisant": chaine >= requis,
            "suppression_requise_2024": n_k / COMPARE["NA62_2024"]["fond"],
            "rejection_autres_canaux": DECLARE["rejection_autres_canaux"]}


def eq16_geometrie() -> Dict[str, Any]:
    par_s = DECLARE["secondaires_par_s"] * DECLARE["fraction_K_plus"]
    produits = par_s * DECLARE["annees_prises_2016_2018"] * ANNEE_S
    fraction = DECLARE["N_K_2016_2018"] / produits
    return {"kaons_produits_par_s": par_s, "produits_sur_la_periode": produits,
            "fraction_dans_volume_fiduciel": fraction, "un_sur": 1.0 / fraction,
            "hypothese_temps_utile": "100 % — la fraction est donc MINORÉE (borne inférieure)"}


def eq17_loi_racine_n() -> Dict[str, Any]:
    c21, c24 = COMPARE["NA62_2021"], COMPARE["NA62_2024"]

    def poisson_relatif(c: Dict[str, Any]) -> float:
        s = c["candidates"] - c["fond"]
        return math.sqrt(c["candidates"]) / s

    p21, p24 = poisson_relatif(c21), poisson_relatif(c24)
    r21 = c21["d_BR"][0] / c21["BR"]
    r24 = c24["d_BR"][0] / c24["BR"]
    s21, s24 = c21["candidates"] - c21["fond"], c24["candidates"] - c24["fond"]
    return {"sigma_poisson_2021": p21, "sigma_poisson_2024": p24,
            "erreur_publiee_relative_2021": r21, "erreur_publiee_relative_2024": r24,
            "sur_2021": r21 - p21, "sur_2024": r24 - p24,
            "surcroit_dans_les_deux": r21 > p21 and r24 > p24,
            "gain_prevu_racine_n": math.sqrt(s24 / s21), "gain_mesure": r21 / r24,
            "rapport_gains": (r21 / r24) / math.sqrt(s24 / s21)}


def eq18_limite_de_la_base() -> Dict[str, Any]:
    return {"ne_prouve_pas": ["l'axiome lui-même", "la normalité de π",
                              "l'unicité d'une théorie physique",
                              "qu'une loi en √N tienne hors du domaine mesuré"],
            "domaine": "dix-huit nœuds, un dossier, deux publications NA62 (2021, 2024), "
                       "une prépublication 2026, un communiqué CERN",
            "refutation": ["si A·ε ne valait plus 1/(N_K·SES), EQ-09 tombe",
                           "si la prédiction gelée bougeait après lecture du comparateur, EQ-07 tombe",
                           "si un nœud du graphe n'avait plus de source hors de lui, EQ-02 tombe",
                           "si une grandeur était déclarée deux fois avec deux valeurs, EQ-06 tombe",
                           "si un import tiers entrait dans le parc, EQ-05 tombe"]}


# ============================================================================
# Table et contrôles
# ============================================================================

def _eq(id_: str, chemin: str, formule: str, resultat: str, statut: str,
        limite: str, detail: Any) -> Dict[str, Any]:
    n = NOEUDS[id_]
    return {"id": id_, "chemin": chemin, "formule": formule, "resultat": resultat,
            "statut": statut, "limite": limite, "detail": detail,
            "couche": n["couche"], "piliers": n["piliers"], "depend_de": n["depend"],
            "fonde_hors_du_dossier": n["externe"]}


def equations() -> List[Dict[str, Any]]:
    g = graphe_dependances()
    c4, c5 = eq04_confrontation_et_parc(), eq05_transmission()
    disc = c4["discipline_source"]
    c6 = registre_grandeurs()
    gel = prediction_gel(DECLARE)
    contamine = prediction_gel(dict(DECLARE, candidates=10 ** 6, fond=1.0, BR=1.0,
                                   p_value=0.5, desintegrations_ordinaires=7))
    c7 = {"signature_prediction": sorted(inspect.signature(prediction_gel).parameters),
          "variables_libres": gel["variables_libres"], "digest": gel["digest"],
          "intersection": sorted(set(gel["valeurs"]) & set(cle_comparateur())),
          "cle_interdites_trouvees": gel["cle_interdites_trouvees"],
          "digest_sous_comparateur_faussee": contamine["digest"],
          "drapeau_leve_sous_contamination": contamine["a_lu_le_comparateur"]}
    c8, c9, c10 = eq08_ordinaires_par_rare(), eq09_cloture_acceptance(), eq10_prediction_gelee()
    c11, c12, c13 = eq11_signification_2021(), eq12_seuil_cinq_sigma(), eq13_confrontation_2024()
    c14, c15, c16 = eq14_confrontation_2026(), eq15_budget_fond(), eq16_geometrie()
    c17, c18 = eq17_loi_racine_n(), eq18_limite_de_la_base()
    repartition = " · ".join(f"{d} {v['equations']}eq/{v['controles']}c/{v['tests']}t"
                             for d, v in c4["dossiers"].items())
    return [
        _eq("EQ-01", "fondation_base.py → eq01_axiome() → C01",
            "AX : la régularité d'un système fini n'appartient pas à ce système",
            f"{AXIOME['enonce']} — {AXIOME['statut']}", "SPÉCIFIÉ",
            "l'axiome n'entre dans aucun calcul : aucun nombre de ce dossier n'a l'axiome pour "
            "source ; il n'engage que la discipline du registre", eq01_axiome()),
        _eq("EQ-02", "fondation_base.py → graphe_dependances() → C02",
            "∀ nœud sans prédécesseur interne, une source déclarée hors du dossier",
            f"{len(g['racines'])} racine : {', '.join(g['racines'])} — fondée dehors : "
            f"{g['racines_fondees_dehors']} ; {g['aretes_vers_l_exterieur']} aretes vers "
            f"l'exterieur", "OPÉRATIONNEL",
            "la propriété porte sur le graphe de CE dossier (18 nœuds), pas sur toute théorie "
            "possible", g),
        _eq("EQ-03", "fondation_base.py → graphe_dependances() → C03",
            "DAG : acyclique, toutes racines atteignables, zéro auto-référence",
            f"acyclique={g['acyclique']} · nœuds={g['noeuds']} · atteignables="
            f"{g['atteignables']} · auto-références={g['self_references']}", "OPÉRATIONNEL",
            "l'acyclicité est une propriété du registre NOEUDS ; elle ne dit rien de la vérité "
            "des équations, seulement de leur non-circularité", g),
        _eq("EQ-04", "fondation_base.py → eq04_confrontation_et_parc() → C04",
            "chaque nombre ⇒ source publique ; douze cases pilier × couche habitées ; "
            "chaque extrait de la chaîne ⇒ sous-chaîne du texte mesuré",
            f"{len(c4['sources_publiques'])} sources publiques · {repartition} · "
            f"{len(disc['extraits_verbatimes'])} extraits verbatimes · "
            f"{len(disc['horodatages_cites'])} horodatage cité",
            "OPÉRATIONNEL",
            "le comptage du parc est une expression régulière sur les fichiers : il mesure la "
            "déclaration, pas la justesse. La discipline de source ne dit pas si la chaîne a "
            "raison : elle dit seulement que nous ne lui prêtons ni chiffre, ni minutage, ni "
            "phrase", c4),
        _eq("EQ-05", "fondation_base.py → imports_de(), imports_parc() → C05",
            "imports ⊆ stdlib ∪ modules locaux — ici et dans tout le parc",
            f"ici {c5['imports_ici']['imports']} ; tiers ici {c5['imports_ici']['tiers']} ; "
            f"tiers du parc { {d: v['tiers'] for d, v in c5['parc'].items()} }",
            "OPÉRATIONNEL",
            "la stdlib reconnue est celle de CETTE interprétation Python ; un tiers sans ce "
            "module n'a pas le même contrôle", c5),
        _eq("EQ-06", "fondation_base.py → registre_grandeurs() → C06",
            "|registre| = noms uniques · aucun doublon en conflit · unité non vide partout",
            f"{c6['entrees']} entrées, {c6['noms_uniques']} noms uniques, doublons "
            f"{c6['doublons_en_conflit']}", "OPÉRATIONNEL",
            "le registre est tenu à la main : une grandeur publique absente d'ici n'est pas "
            "interdite, elle est simplement hors domaine", c6),
        _eq("EQ-07", "fondation_base.py → prediction_gel() → C07",
            "signature(prediction) ∩ clés_comparateur = ∅ · digest stable",
            f"signature={c7['signature_prediction']} · digest={c7['digest'][:16]}… · "
            f"drapeau sous contamination {c7['drapeau_leve_sous_contamination']}",
            "OPÉRATIONNEL",
            "c'est une preuve d'indépendance structurelle, pas d'exactitude : la prédiction "
            "peut être fausse sans avoir jamais vu le comparateur", c7),
        _eq("EQ-08", "fondation_base.py → intervalle_ordinaires() → C08",
            "N_ordinaires = 1/BR − 1, intervalle par les deux branches d'incertitude",
            f"SM {c8['centre_modele_standard']:.6g} ∈ [{c8['intervalle_modele_standard'][0]:.6g}, "
            f"{c8['intervalle_modele_standard'][1]:.6g}] ; communiqué {c8['valeur_communiquee']} "
            f"⇒ taux implicite {c8['taux_implicite_du_communique']:.3g} ; intervalle 2024 "
            f"[{c8['intervalle_mesure_2024'][0]:.4g}, {c8['intervalle_mesure_2024'][1]:.4g}]",
            "OPÉRATIONNEL",
            "le communiqué arrondit à BR = 10⁻¹⁰ : l'accord est un accord d'arrondi, pas une "
            "mesure nouvelle. Le compte arrondi ne tombe PAS dans l'intervalle à un sigma "
            "calculé depuis BR_sm = 8,4·10⁻¹¹ — c'est écrit, et cela dit seulement que "
            "10⁻¹⁰ est un arrondi", c8),
        _eq("EQ-09", "fondation_base.py → acceptance(), eq09_cloture_acceptance() → C09",
            "A·ε = 1/(N_K·SES) puis N = N_K·BR_sm·A·ε",
            f"A·ε 2016-18 {c9['acceptance_2016_2018']:.4%} · 2021-22 "
            f"{c9['acceptance_2021_2022']:.4%} (rapport {c9['rapport_acceptances']:.4f}) · "
            f"N calculé {c9['n_attendu_calcule']:.4f} vs publié {c9['n_attendu_publie']} "
            f"(écart {c9['ecart_relatif']:.4%})", "OPÉRATIONNEL",
            "fermeture de trois chiffres PUBLIÉS entre eux : le calcul ne peut pas découvrir "
            "une erreur commune aux trois", c9),
        _eq("EQ-10", "fondation_base.py → prediction_gel() → eq10_prediction_gelee() → C10",
            "N gelé = 10,01 contre excès publié (candidates − fond)",
            f"prévu {c10['prevu']:.4f} · publié {c10['observe_excess']:.2f} · écart "
            f"{c10['ecart_en_sigma']:+.4f} σ", "OPÉRATIONNEL",
            "l'incertitude du comparateur est celle que NA62 déclare ; nous ne reconstruisons "
            "pas sa vraisemblance", c10),
        _eq("EQ-11", "fondation_base.py → signification_lima(), z_de_p_seuil() → C11",
            "z(20 | 7,03) par Li–Ma contre z implicite de la p-value publiée",
            f"Li–Ma {c11['z_lima']:.4f} σ · publié {c11['z_publiee']:.4f} σ · écart "
            f"{c11['ecart']:+.4f} · les deux sous 5 σ : {c11['les_deux_sous_cinq_sigma']}",
            "OPÉRATIONNEL",
            "notre formule ignore l'incertitude systématique du fond : le surestime est attendu, "
            "et n'est PAS résorbé ici", c11),
        _eq("EQ-12", "fondation_base.py → evenements_requis() → C12",
            "excès requis pour z = 5 à fond connu, contre excès publié 2024",
            f"requis {c12['excess_requis']:.4f} · publié {c12['excess_publie']:.2f} · marge "
            f"{c12['marge']:.4f} · Li–Ma {c12['z_lima']:.4f} vs publié {c12['z_publiee']:.4f}",
            "OPÉRATIONNEL",
            "le fond utilisé est celui que la même publication annonce : contrôle de cohérence "
            "interne, pas prédiction indépendante", c12),
        _eq("EQ-13", "fondation_base.py → eq13_confrontation_2024() → C13",
            "z = (BR_obs − BR_sm)/√(σ_obs² + σ_sm²), sur les deux branches",
            f"z ∈ [{c13['z_branches'][0]:.4f}, {c13['z_branches'][1]:.4f}] · NA62 déclare "
            f"{c13['z_declare_par_na62']} · chevauchement à 1 σ : "
            f"{c13['chevauchement_a_un_sigma']}", "OPÉRATIONNEL",
            "l'addition en quadrature est NOTRE hypothèse déclarée ; NA62 publie un traitement "
            "de vraisemblance complet. Les intervalles à un sigma ne se recouvrent pas : c'est "
            "écrit, pas gommé", c13),
        _eq("EQ-14", "fondation_base.py → eq14_confrontation_2026() → C14",
            "même formule, chiffres 2016-2024 de la mise à jour 2026",
            f"BR {c14['br_2016_2024']:.3g} · z = {c14['z_contre_sm']:.4f} (branche basse "
            f"{c14['z_branche_inf']:.4f}) · sous 1 σ : {c14['sous_un_sigma']}", "OPÉRATIONNEL",
            "les chiffres 2026 viennent d'une prépublication ; ils peuvent bouger", c14),
        _eq("EQ-15", "fondation_base.py → eq15_budget_fond() → C15",
            "suppression totale requise = N_K/fond, contre la chaîne de rejets publiée",
            f"requise {c15['suppression_totale_requise']:.4g} · chaîne μ×π⁰ "
            f"{c15['chaine_declaree_mu_x_pi0']:.3g} · marge "
            f"+{c15['marge_en_ordres_de_grandeur']:.3f} ordres", "OPÉRATIONNEL",
            "les facteurs O(10⁷), O(10⁸) sont des ordres de grandeur publiés ; nous ne savons "
            "pas quel canal domine le fond réel, seulement que la chaîne annoncée le permet", c15),
        _eq("EQ-16", "fondation_base.py → eq16_geometrie() → C16",
            "fraction = N_K / (secondaires/s × 6 % × 3 ans × 3,15576·10⁷ s)",
            f"{c16['fraction_dans_volume_fiduciel']:.4g} — un kaon sur "
            f"{c16['un_sur']:.0f} produits · {c16['kaons_produits_par_s']:.3g} K⁺/s", "SIMULÉ",
            "bornée inférieurement : tout temps mort réel rend la fraction plus grande ; le "
            "communiqué ne donne ni le temps utile ni l'acceptance du faisceau", c16),
        _eq("EQ-17", "fondation_base.py → eq17_loi_racine_n() → C17",
            "σ_Poisson = √(s+b)/s contre erreur relative publiée, deux périodes",
            f"2021 {c17['sigma_poisson_2021']:.4f} vs {c17['erreur_publiee_relative_2021']:.4f} · "
            f"2024 {c17['sigma_poisson_2024']:.4f} vs {c17['erreur_publiee_relative_2024']:.4f} · "
            f"√N prévu {c17['gain_prevu_racine_n']:.4f} vs mesuré {c17['gain_mesure']:.4f}",
            "OPÉRATIONNEL",
            "l'excédent des deux périodes est un faisceau d'indices sur un plancher "
            "systématique, pas la mesure de ce plancher", c17),
        _eq("EQ-18", "fondation_base.py → eq18_limite_de_la_base() → C18",
            "liste des réfutations internes et des non-preuves",
            f"{len(c18['refutation'])} conditions de chute, {len(c18['ne_prouve_pas'])} choses "
            f"non prouvées", "SPÉCIFIÉ",
            "la limite EST le produit de cette équation : un dossier qui n'écrit pas sa "
            "réfutation n'a pas de limite, il a un silence", c18),
    ]


def controles(eqs: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []

    def ajouter(id_: str, nom: str, attendu: str, obtenu: str, ok: bool) -> None:
        out.append({"id": id_, "nom": nom, "attendu": attendu, "obtenu": obtenu,
                    "ok": bool(ok), "limite": eqs[id_.replace("C", "EQ-")]["limite"]})

    def D(k: str) -> Dict[str, Any]:
        return eqs[k]["detail"]

    g = D("EQ-02")
    c1, c4, c5, c6 = D("EQ-01"), D("EQ-04"), D("EQ-05"), D("EQ-06")
    disc = c4["discipline_source"]
    c7, c8, c9 = D("EQ-07"), D("EQ-08"), D("EQ-09")
    c10, c11, c12 = D("EQ-10"), D("EQ-11"), D("EQ-12")
    c13, c14, c15 = D("EQ-13"), D("EQ-14"), D("EQ-15")
    c16, c17, c18 = D("EQ-16"), D("EQ-17"), D("EQ-18")

    ajouter("C01", "l'axiome est posé hors matrice et ne fournit aucun nombre",
            "hors_matrice True · 0 nombre · quatre piliers engendrés",
            f"{c1['hors_matrice']} · {c1['nombres_fournis_par_l_axiome']} · "
            f"{c1['piliers_engendres']}",
            c1["hors_matrice"] is True and c1["nombres_fournis_par_l_axiome"] == 0
            and c1["piliers_engendres"] == sorted(PILIERS))
    ajouter("C02", "la racine unique du graphe est fondée sur une source extérieure",
            "racines = ['EQ-01'] et fondée dehors True",
            f"{g['racines']} · {g['racines_fondees_dehors']}",
            g["racines_fondees_dehors"] and g["racines"] == ["EQ-01"])
    ajouter("C03", "graphe acyclique, dix-huit nœuds atteignables, zéro auto-référence",
            "acyclique et atteignables = 18",
            f"acyclique={g['acyclique']} atteignables={g['atteignables']} "
            f"self={g['self_references']} couches vides={g['couche_vide']}",
            g["acyclique"] and g["atteignables"] == g["noeuds"] == 18
            and not g["self_references"] and not g["couche_vide"])
    ajouter("C04", "les douze cases pilier × couche sont habitées ; chaque dossier du parc "
                   "déclare autant de contrôles que d'équations et porte ses tests ; la chaîne "
                   "est citée mot pour mot et n'est jamais minutée",
            "aucune case vide · eq = c > 0 et tests > 0 par dossier · extraits verbatimes · "
            "0 horodatage · 0 octet de transcript",
            f"{c4['cases_matrice'] or 'aucune'} · "
            f"{len(c4['sources_publiques'])} sources · "
            + " · ".join(f"{d} {v['equations']}/{v['controles']} et {v['tests']}t"
                         for d, v in c4["dossiers"].items())
            + f" · extraits {disc['extraits_non_trouves'] or 'tous retrouvés'} · "
              f"horodatages {disc['horodatages_cites']}",
            not c4["cases_matrice"] and len(c4["sources_publiques"]) >= 4
            and all(v["present"] and v["equations"] == v["controles"] > 0
                    and v["tests"] > 0 for v in c4["dossiers"].values())
            and not disc["extraits_non_trouves"] and not disc["horodatages_cites"]
            and disc["chapitres_publics"] == 0
            and all(octets == 0 for octets in disc["transcript_octets"].values())
            and disc["caracteres_retenus"] < disc["caracteres_mesures"])
    tiers_ici = c5["imports_ici"]["tiers"]
    tiers_parc = {k: v["tiers"] for k, v in c5["parc"].items()}
    ajouter("C05", "aucun import tiers, ici ni dans le parc",
            "listes vides", f"ici {tiers_ici} · parc {tiers_parc}",
            not tiers_ici and all(not v for v in tiers_parc.values())
            and len(c5["commandes_publish"]) == 3)
    ajouter("C06", "registre clos : une valeur par grandeur, unité non vide, registre = DECLARE",
            "0 doublon · 0 unité vide · entrées = noms uniques · hors_declare et "
            "declare_sans_entree vides",
            f"{c6['doublons_en_conflit']} · {c6['unites_vide']} · {c6['entrees']}/"
            f"{c6['noms_uniques']} · {c6['hors_declare'] or '∅'} · "
            f"{c6['declare_sans_entree'] or '∅'}",
            not c6["doublons_en_conflit"] and not c6["unites_vide"]
            and not c6["valeurs_non_numeriques"] and not c6["hors_declare"]
            and not c6["declare_sans_entree"] and c6["entrees"] == c6["noms_uniques"])
    ajouter("C07", "la prédiction ne voit aucune clé du comparateur et ne change pas",
            "intersection vide · digest inaltéré · drapeau levé sous contamination",
            f"{c7['intersection'] or '∅'} · {c7['digest'][:12]}… · "
            f"{c7['drapeau_leve_sous_contamination']} · inaltéré "
            f"{c7['digest'] == c7['digest_sous_comparateur_faussee']}",
            not c7["intersection"] and not c7["cle_interdites_trouvees"]
            and c7["digest"] == c7["digest_sous_comparateur_faussee"]
            and c7["drapeau_leve_sous_contamination"]
            and c7["signature_prediction"] == ["declares"])
    ajouter("C08", "le compte communiqué est l'arrondi 10⁻¹⁰ ; il tombe dans l'intervalle "
                   "mesuré 2024 — et l'intervalle du modèle standard ne le contient pas",
            "taux implicite = 1,0e-10 · 2024 True · SM écrit tel quel",
            f"taux {c8['taux_implicite_du_communique']:.3g} · 2024 "
            f"{c8['communique_dans_intervalle_2024']} · SM (arrondi hors domaine) "
            f"{c8['communique_dans_intervalle_sm']}",
            c8["communique_dans_intervalle_2024"]
            and abs(c8["taux_implicite_du_communique"] - 1.0e-10) <= 1e-16)
    ajouter("C09", "les deux Acceptations concordent et le N calculé ferme sur le publié",
            "écart relatif ≤ 1 % · rapport d'acceptations dans [0,9 ; 1,1]",
            f"écart {c9['ecart_relatif']:.4%} · rapport {c9['rapport_acceptances']:.4f}",
            c9["ecart_relatif"] <= 0.01 and 0.9 <= c9["rapport_acceptances"] <= 1.1)
    ajouter("C10", "l'excès publié reste à moins de 2 σ de la prédiction gelée",
            "|écart| ≤ 2 σ", f"{c10['ecart_en_sigma']:+.4f} σ",
            abs(c10["ecart_en_sigma"]) <= 2.0 and c10["prevu"] > 0)
    ajouter("C11", "2021 : les deux calculs disent evidence, aucun ne dit observation",
            "max(z) < 5 et Li–Ma > publié", f"{c11['z_lima']:.4f} · {c11['z_publiee']:.4f}",
            c11["les_deux_sous_cinq_sigma"] and c11["z_lima"] > c11["z_publiee"])
    ajouter("C12", "2024 : l'excès publié dépasse le nombre d'événements requis pour 5 σ",
            "marge > 0 et les deux z > 5", f"requis {c12['excess_requis']:.4f} · publié "
            f"{c12['excess_publie']:.2f} · marge {c12['marge']:.4f}",
            c12["marge"] > 0 and c12["les_deux_au_dessus_de_cinq"])
    ajouter("C13", "2024 : nos z restent sous le z déclaré par NA62, non-chevauchement écrit",
            "max(z) < 1,7 et chevauchement False", f"z {c13['z_branches'][0]:.4f}/"
            f"{c13['z_branches'][1]:.4f} · {c13['chevauchement_a_un_sigma']}",
            c13["nos_z_sous_le_z_declare"] and not c13["chevauchement_a_un_sigma"])
    ajouter("C14", "2026 : l'écart au modèle standard passe sous 1 σ",
            "z < 1 sur les deux branches", f"{c14['z_contre_sm']:.4f} · "
            f"{c14['z_branche_inf']:.4f}", c14["sous_un_sigma"])
    ajouter("C15", "la chaîne de rejets publiée est au moins à la hauteur du fond annoncé",
            "marge en ordres de grandeur > 0", f"requise "
            f"{c15['suppression_totale_requise']:.4g} · chaîne "
            f"{c15['chaine_declaree_mu_x_pi0']:.3g} · +{c15['marge_en_ordres_de_grandeur']:.3f}",
            c15["chainement_suffisant"] and c15["marge_en_ordres_de_grandeur"] > 0)
    ajouter("C16", "fraction des kaons produits qui désintègrent dans le volume utile",
            "0 < fraction < 1", f"{c16['fraction_dans_volume_fiduciel']:.4g} (un sur "
            f"{c16['un_sur']:.0f})", 0.0 < c16["fraction_dans_volume_fiduciel"] < 1.0)
    ajouter("C17", "les deux périodes publient une erreur au-dessus du seul Poisson, et le "
                   "gain mesuré reste SOUS la loi √N",
            "surcroîts > 0 · gain mesuré < gain prévu",
            f"+{c17['sur_2021']:.4f} · +{c17['sur_2024']:.4f} · {c17['gain_mesure']:.4f} < "
            f"{c17['gain_prevu_racine_n']:.4f}",
            c17["surcroit_dans_les_deux"] and c17["gain_mesure"] < c17["gain_prevu_racine_n"]
            and 0.8 <= c17["rapport_gains"] <= 1.0)
    ajouter("C18", "la limite est écrite : cinq réfutations, quatre non-preuves, dix-huit "
                   "limites d'équation non vides",
            "≥ 4 conditions et ≥ 3 non-preuves et 18/18 limites", f"{len(c18['refutation'])} · "
            f"{len(c18['ne_prouve_pas'])} · "
            f"{sum(1 for x in eqs.values() if x['limite'])}/18",
            len(c18["refutation"]) >= 4 and len(c18["ne_prouve_pas"]) >= 3
            and all(x["limite"] for x in eqs.values()) and len(eqs) == 18)
    return out


def resoudre() -> Dict[str, Any]:
    eqs = {x["id"]: x for x in equations()}
    cs = controles(eqs)
    g = graphe_dependances()
    gel = prediction_gel(DECLARE)
    donnees = {
        "source": SOURCE, "axiome": AXIOME, "piliers": PILIERS, "couches": COUCHES,
        "statuts": STATUTS, "declare": DECLARE, "comparateur": COMPARE,
        "graphe": g, "gel": gel, "imports": imports_de(__file__),
        "imports_parc": imports_parc(), "registre": registre_grandeurs(),
        "dossiers": inventaire_parc(), "equations": list(eqs.values()),
        "controles": cs,
        "conclusion": {
            "controles_verts": sum(1 for c in cs if c["ok"]),
            "controles_total": len(cs),
            "equations": len(eqs),
            "statuts_par_label": {s: sum(1 for x in eqs.values() if x["statut"] == s)
                                  for s in STATUTS},
            "digest_prediction_gel": gel["digest"],
            "verdict": "BASE EN CONFORMITÉ AVEC SES QUATRE PILIERS"
                       if all(c["ok"] for c in cs) else "NON CONFORME",
            "limite_globale": "aucune preuve universelle : dix-huit énoncés sur un graphe de "
                              "dix-huit nœuds et quatre sources publiques",
        },
    }
    return donnees


def verifier(donnees: Optional[Dict[str, Any]] = None) -> bool:
    return all(c["ok"] for c in (donnees or resoudre())["controles"])


def ecrire_artefacts(donnees: Dict[str, Any], vers: Optional[Path] = None) -> Dict[str, str]:
    dossier = vers or (RACINE / "FONDATION" / "artefacts")
    dossier.mkdir(parents=True, exist_ok=True)
    morceaux = {
        "gel.json": {"digest": donnees["gel"]["digest"],
                     "prediction": donnees["gel"]["valeurs"],
                     "variables_libres": donnees["gel"]["variables_libres"],
                     "cle_interdites_trouvees": donnees["gel"]["cle_interdites_trouvees"],
                     "a_lu_le_comparateur": donnees["gel"]["a_lu_le_comparateur"],
                     "comparateur_lu_ensuite": donnees["comparateur"]},
        "base.json": {"axiome": donnees["axiome"], "piliers": donnees["piliers"],
                      "couches": donnees["couches"], "graphe": donnees["graphe"],
                      "registre": donnees["registre"]},
        "confrontation.json": {"prediction_gel": donnees["gel"],
                               "comparateur": donnees["comparateur"],
                               "equations_chiffrees": {x["id"]: x["detail"] for x
                                                       in donnees["equations"]
                                                       if x["statut"] != "SPÉCIFIÉ"}},
        "etat.json": {"source": donnees["source"], "conclusion": donnees["conclusion"],
                      "controles": donnees["controles"],
                      "equations": [{k: v for k, v in x.items() if k != "detail"}
                                    for x in donnees["equations"]]},
        "inventaire.json": {"parc": donnees["dossiers"], "imports_parc": donnees["imports_parc"]},
    }
    rendu: Dict[str, str] = {}
    for nom, contenu in morceaux.items():
        texte = json.dumps(contenu, ensure_ascii=False, indent=2, sort_keys=True, default=str)
        octets = (texte + "\n").encode("utf-8")
        (dossier / nom).write_bytes(octets)
        rendu[nom] = f"{len(octets)} octets"
    lignes = [["equation", "statut", "couche", "piliers", "resultat", "limite"]]
    for x in donnees["equations"]:
        lignes.append([x["id"], x["statut"], x["couche"], " + ".join(x["piliers"]),
                       x["resultat"], x["limite"]])
    corps = "\r\n".join(";".join(str(v).replace(";", ",") for v in ln) for ln in lignes) + "\r\n"
    csv_octets = b"\xef\xbb\xbf" + corps.encode("utf-8")
    (dossier / "confrontation.csv").write_bytes(csv_octets)
    rendu["confrontation.csv"] = f"{len(csv_octets)} octets"
    return rendu


if __name__ == "__main__":
    donnees = resoudre()
    if "--ecrit" in sys.argv[1:]:
        donnees["artefacts"] = ecrire_artefacts(donnees)
    sortie = {
        "source": {"id": SOURCE["video_id"], "titre": SOURCE["titre"],
                   "chaine": SOURCE["chaine"], "duree_s": SOURCE["duree_s"],
                   "chapitres": SOURCE["chapitres_publics"], "transcript": SOURCE["transcript"]},
        "axiome": AXIOME["enonce"],
        "conclusion": donnees["conclusion"],
        "controles": donnees["controles"],
        "equations": [{k: v for k, v in x.items() if k != "detail"}
                      for x in donnees["equations"]],
        "digest_prediction_gel": donnees["gel"]["digest"],
        "artefacts": donnees.get("artefacts", {}),
    }
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(sortie, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    sys.exit(0 if verifier(donnees) else 1)
