# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""SURETE — ce qu'une garantie de sécurité peut porter, et à quelle condition elle est tenable.

D'où part ce dossier
--------------------
Le 2026-11-13, la sonde du Skill `extraire-chapitres-youtube-sans-transcript` a lu le titre
public d'une vidéo de franceinfo : « Panne chez Microsoft : "L'informatique ne sera jamais
sécurisée à 100%" ». Vingt-deux minutes quarante-six de bande-son, **zéro chapitre horodaté,
zéro octet de transcript** (json3, srv3 et xml). De cette source il ne peut être tiré **aucune
citation** et **aucun chiffre** : ni ce que la personne interrogée a dit, ni ce qu'une panne a
coûté, ni ce qu'un produit contient. Le titre, lui, est une donnée publique vérifiable par
oEmbed, et il énonce une proposition précise — une borne sur ce que la sécurité informatique
peut promettre.

Ce dossier ne discute pas cette proposition : il la formalise. La question n'est pas « qui a
raison de la prononcer », elle est « quelles garanties sont du côté de ce qui se décide, et
lesquelles sont du côté de ce qui ne se décide pas ». Cette frontière est un résultat standard
de la théorie de la calculabilité, pas une opinion.

Ce que ce module fait, dans l'ordre
-----------------------------------
  1. il exhibe deux machines dont les langages diffèrent sur la propriété « aucune chaîne
     acceptée n'atteint l'état critique » : la propriété est donc non triviale, et le théorème
     de Rice déclare indécidable l'ensemble des programmes qui la vérifient (EQ-01) ;
  2. il énumère réellement un domaine fini d'états — 131 071, mot vide compris — et confronte ce
     compte à la forme fermée 2^17 − 1 : la vérification exhaustive existe, c'est sa taille qui
     pose (EQ-02) ;
  3. il calcule les défauts exploitables attendus de trois surfaces de confiance à partir de
     deux paramètres déclarés, par produit direct et par somme en mille tronçons, et retrouve
     e^−N par sa définition de limite (EQ-03) ;
  4. il déroule une chaîne de correctif en heures, par multiplication puis en comptant
     effectivement des pas d'une heure entre deux instants (EQ-04) ;
  5. il additionne des intervalles dont l'un n'a pas de borne supérieure et montre ce que cette
     addition produit : un minorant, jamais un majorant (EQ-05) ;
  6. il derive une chaîne de N couches d'un modèle à cause commune — fuite = s + (1−s)·a^N —
     et ferme le compte des quatre issues par une probabilité exactement égale à un (EQ-06) ;
  7. il montre sur quarante rangs rationnels exacts que le plancher de fuite ne s'annule pour
     aucun nombre fini de couches, et vérifie sa pente en logarithme (EQ-07) ;
  8. il convertit une disponibilité en temps perdu par deux routes exactes, et rappelle qu'une
     disponibilité n'est pas une sécurité (EQ-08) ;
  9. il pose un critère **décidable sur un énoncé** : une garantie est tenable si elle porte une
     borne chiffrée non nulle et une procédure publique re-jouable en temps borné ; il l'applique
     à six garanties écrites ici, dont trois sont les siennes (EQ-09) ;
 10. il compte ce dont un tiers a besoin pour rejouer ce dossier : imports hors bibliothèque
     standard, fichiers extérieurs lus, accès réseau — mesurés sur l'arbre syntaxique du fichier
     lui-même (EQ-10) ;
 11. il confronte l'instantané consigné du registre d'équations à lui-même : la somme des
     comptes module à module égale le total publié, le nombre d'entrées égale le nombre de
     modules annoncés (EQ-11) ;
 12. il divise les 313 000 000 000 000 poids du socle par le plancher de vitesse déclaré : une
     capacité d'adressage n'est pas un délai de cassage (EQ-12) ;
 13. il retourne le critère contre lui-même : treize limites écrites, zéro marqueur d'absolu
     dans les résultats publiés, racine de Merkle stable entre deux exécutions (EQ-13).

Ce qu'il ne fait pas
--------------------
Il ne nomme aucune entreprise, aucune équipe, aucun produit, aucune personne : le critère d'EQ-09
porte sur des **garanties**, et les six énoncés sur lesquels il s'exerce sont écrits ici, sans
attribution. Il ne conclut l'obsolescence de rien du tout : il rend décidable le fait qu'une
promesse soit ou non du côté de ce qui peut être attesté — et il y comprend les nôtres. Il ne
mesure aucun système réel : les surfaces de confiance, les durées de correctif, les densités de
défauts, la probabilité de couche, le coefficient de cause commune et les MTBF/MTTR sont des
**paramètres déclarés**, nommés dans `PARAMETRES` avec leur statut. Un calcul n'est pas une
mesure, et aucun domaine fini vérifié ne dit rien de son complément.

Usage :
    cd ZENODO_DEPOT_ALMIZAN && py -3 SURETE/surete_bornee_base.py
    cd ZENODO_DEPOT_ALMIZAN && py -3 SURETE/surete_bornee_base.py --json
    cd ZENODO_DEPOT_ALMIZAN && py -3 SURETE/surete_bornee_base.py --ecrit
    cd ZENODO_DEPOT_ALMIZAN && py -3 FONDATION/OUTILS/audit_piliers.py SURETE/surete_bornee_base.py
"""

from __future__ import annotations

import ast
import hashlib
import json
import math
import sys
import time
from datetime import datetime, timedelta, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional

DOSSIER = Path(__file__).resolve().parent
ARTEFACTS = DOSSIER / "artefacts"
F_CERTIFICAT = "certificat.json"

VERSION = "1.0.0"

# ─── Source : ce qui a été mesuré publiquement, et rien d'autre ───────────────────────────
SOURCE: Dict[str, Any] = {
    "titre": "Panne chez Microsoft : \u201cL\u2019informatique ne sera jamais s\u00e9curis\u00e9e \u00e0 100%\u201d "
             "(Damien Bancal)",
    "chaine": "franceinfo",
    "video_id": "AcoshabaQyg",
    "url": "https://www.youtube.com/watch?v=AcoshabaQyg",
    "duree_s": 1366,
    "chapitres_publics": 0,
    "transcript": "absent (timedtext : 0 octet en json3, srv3 et xml)",
    "mesure_le": "2026-11-13T23:44:50Z",
    "outils": "scripts/extraire_chapitres_youtube.py "
              "(Skill extraire-chapitres-youtube-sans-transcript), oEmbed pour le titre",
    "avertissements_sonde": [
        "aucun en-tete de chapitres : horodatages pris dans toute la description",
        "aucun chapitre horodate dans la description",
        "timedtext repond sans contenu : le transcript est tenu pour absent",
    ],
    "sonde_transcript_octets": {"json3": 0, "srv3": 0, "xml": 0},
    "ce_que_le_titre_fournit": "une proposition sur la borne de ce qu'une securite informatique "
                               "peut promettre : c'est le theme de ce dossier",
    "ce_que_la_video_n_a_pas_fourni": [
        "aucune citation : sans transcript, aucune phrase n'est attribuable a la bande-son",
        "aucun chiffre : ni cout de panne, ni effectif, ni duree ne vient d'ici",
        "aucune attribution de ce dossier a la personne nommee dans le titre",
    ],
}

STATUTS: Dict[str, str] = {
    "OPÉRATIONNEL": "calcul exact reproductible, contrôle attaché",
    "SIMULÉ": "scénario ou valeur déclarée, explicité comme tel",
    "SPÉCIFIÉ": "posé ou structurant, non évalué par ce dossier",
}

COUCHES: Dict[str, str] = {
    "S1 MESURABLE": "les nombres : comptes, taux, intervalles",
    "S2 REGULARITE": "les lois et les identités : ce qui se calcule sans mesure",
    "S3 HORS_MATRICE": "la borne de ce qui est décidable : posée, non démontrée ici",
}

# ─── Paramètres déclarés : toute valeur qui n'est pas une mesure est nommée ici ───────────
PARAMETRES: Dict[str, Any] = {
    "profondeur_enumeree": 16,
    "plancher_etats_par_s": 20_000,
    "socle_poids": 313_000_000_000_000,
    "socle_facteur": 313,
    "socle_puissance": 10 ** 12,
    "annee_s": 31_557_600,
    "tcb_lignes": {"petite": 10_000, "moyenne": 10_000_000, "grande": 1_000_000_000},
    "densite_defauts_par_ligne": "1/1000",
    "fraction_exploitable": "1/10",
    "troncons_poisson": 1_000,
    "bornes_fenetre_connue_h": ["360", "720"],
    "chaine_correctif_jours": {"divulgation_a_publication": 7, "preparation_et_tests": 5,
                               "deploiement": 3},
    "correctifs_par_an": 40,
    "p_couche": "1/5",
    "beta_cause_commune": "1/10",
    "mtbf_h": 8_760,
    "mttr_h": 2,
    "heures_par_an": 8_760,
    "tolerance_relative": 1.0e-5,
    "registre_consigne": {
        "mesure_le": "2026-11-14",
        "provenance": "DECLARATION/artefacts/certificat.json, recopié comme instantané pour que "
                      "ce module reste exécutable hors du dépôt",
        "modules_porteurs": 15,
        "total_parc": 232,
        "equations_par_module": {
            "ABONDANCE/agriculture_abondance.py": 18,
            "ABONDANCE/eau_abondance.py": 15,
            "ABONDANCE/electricite_abondance.py": 21,
            "CHIFFRES/chiffres_pi.py": 17,
            "CONSTRUCTION/construction_base.py": 16,
            "CONTINUITE/continuite_base.py": 15,
            "DECLARATION/declaration_base.py": 16,
            "FONDATION/fondation_base.py": 18,
            "GOULETS/goulets_base.py": 10,
            "GUERRE/guerre_base.py": 16,
            "HORLOGERIE/horlogerie.py": 15,
            "QPU_DISTANT/qpu_distant_base.py": 10,
            "REDACTION/redaction_mizan.py": 16,
            "SURETE/surete_bornee_base.py": 13,
            "VERROUS/verrous_base.py": 16,
        },
    },
}

# Six garanties écrites ici, aucune attribuée. `borne` est la probabilité de fuite que l'énoncé
# laisse subsister quand il en énonce une ; 0 = il prétend la supprimer.
GARANTIES_DECLAREES: List[Dict[str, Any]] = [
    {"id": "G1", "enonce": "ce système est sécurisé à cent pour cent", "borne": "0",
     "procedure_publique": False},
    {"id": "G2", "enonce": "il ne subsiste dans ce code aucun chemin exploitable", "borne": "0",
     "procedure_publique": False},
    {"id": "G3", "enonce": "la couverture de verification est complete", "borne": "0",
     "procedure_publique": False},
    {"id": "G4", "enonce": "la fuite est bornée par le plancher s de la chaîne de couches",
     "borne": "1/50", "procedure_publique": True},
    {"id": "G5", "enonce": "les 131 071 états du domaine déclaré ont été énumérés sans "
                           "contredit", "borne": "1/1000", "procedure_publique": True},
    {"id": "G6", "enonce": "le certificat de ce dossier se rejoue hors ligne par une commande",
     "borne": "1/100", "procedure_publique": True},
]

# Par où une prétention absolue se trahit dans un résultat publié.
MARQUEURS_ABSOLUS = ("100 %", "infaillible", "invuln", "aucune faille", "complete", "garanti a",
                     "zero risque", "sûre", "certain")

NOEUDS: Dict[str, Dict[str, Any]] = {
    "EQ-01": {"depend": [], "externe": "Rice, Classes of recursively enumerable sets and their "
                                       "decision problems, 1953 — énoncé standard, redémontré nulle part ici"},
    "EQ-02": {"depend": ["EQ-01"], "externe": "énumération exécutée sur cet hôte ; vitesse et "
                                              "durée consignées dans `detail`"},
    "EQ-03": {"depend": ["EQ-02"], "externe": None},
    "EQ-04": {"depend": ["EQ-03"], "externe": None},
    "EQ-05": {"depend": ["EQ-04"], "externe": None},
    "EQ-06": {"depend": ["EQ-05"], "externe": None},
    "EQ-07": {"depend": ["EQ-06"], "externe": None},
    "EQ-08": {"depend": ["EQ-07"], "externe": None},
    "EQ-09": {"depend": ["EQ-01", "EQ-07"], "externe": "les six énoncés sont écrits dans ce "
                                                       "fichier, sans attribution"},
    "EQ-10": {"depend": ["EQ-09"], "externe": "arbre syntaxique de ce fichier, lu à l'exécution"},
    "EQ-11": {"depend": ["EQ-10"], "externe": "instantané consigné de "
                                              "DECLARATION/artefacts/certificat.json"},
    "EQ-12": {"depend": ["EQ-02"], "externe": "socle de poids adressables déclaré par "
                                              "reseau_poids_sparse_mizan.py, recopié en paramètre"},
    "EQ-13": {"depend": ["EQ-09", "EQ-10"], "externe": None},
}


# ─── 1. Indécidabilité : deux machines, une propriété non triviale ────────────────────────
def mots_boules(K: int) -> List[str]:
    """Tous les mots binaires de longueur au plus K, mot vide compris, par parcours en largeur."""
    mots = [""]
    frontiere = [""]
    for _ in range(K):
        frontiere = [p + b for p in frontiere for b in ("0", "1")]
        mots += frontiere
    return mots


def machine_vide(mot: str) -> bool:
    return False


def machine_totale(mot: str) -> bool:
    return True


def rice() -> Dict[str, Any]:
    """« Aucune chaîne acceptée n'atteint l'état critique » : ni always, ni never."""
    K = int(PARAMETRES["profondeur_enumeree"])
    domaine = mots_boules(K)
    critique = "0" * K
    acceptes_vide = [m for m in domaine if machine_vide(m)]
    acceptes_totale = [m for m in domaine if machine_totale(m)]
    sur_vide = critique not in acceptes_vide
    sur_totale = critique not in acceptes_totale
    return {"K": K, "domaine": len(domaine), "forme_ferree": 2 ** (K + 1) - 1,
            "critique": critique, "acceptes_vide": len(acceptes_vide),
            "acceptes_totale": len(acceptes_totale), "propriete_sur_vide": sur_vide,
            "propriete_sur_totale": sur_totale, "non_triviale": sur_vide != sur_totale,
            "enonce_propriete": "aucune chaine acceptee n'atteint l'etat critique"}


# ─── 2. Énumération réelle d'un domaine fini ─────────────────────────────────────────────
def enumeration() -> Dict[str, Any]:
    """Énumère le domaine et mesure le temps réel ; seul le compte entre dans un résultat."""
    K = int(PARAMETRES["profondeur_enumeree"])
    depart = time.perf_counter()
    domaine = mots_boules(K)
    duree = time.perf_counter() - depart
    vitesse = len(domaine) / duree if duree > 0 else float("inf")
    plancher = int(PARAMETRES["plancher_etats_par_s"])
    return {"etats": len(domaine), "duree_s": duree, "vitesses_par_s": vitesse,
            "dizaine_vitesse": int(10 ** math.floor(math.log10(vitesse))),
            "plancher": plancher, "au_dessus_du_plancher": vitesse >= plancher,
            "cout_domaine_s": len(domaine) / plancher}


# ─── 3. Défauts exploitables attendus d'une surface de confiance ──────────────────────────
def defauts_tcb() -> Dict[str, Any]:
    d = Fraction(PARAMETRES["densite_defauts_par_ligne"])
    f = Fraction(PARAMETRES["fraction_exploitable"])
    n_troncons = int(PARAMETRES["troncons_poisson"])
    scenarios: Dict[str, Any] = {}
    for nom, L in PARAMETRES["tcb_lignes"].items():
        N = Fraction(L) * d * f
        par_troncons = sum(Fraction(L, n_troncons) * d * f for _ in range(n_troncons))
        scenarios[nom] = {"lignes": L, "attendus": N, "attendus_flottant": float(N),
                          "somme_de_troncons": par_troncons, "coherent": par_troncons == N,
                          "moins_log10_P0": float(N) * math.log10(math.e)}
    N_petit = scenarios["petite"]["attendus_flottant"]
    n = 10 ** 6
    par_limite = (1.0 - N_petit / n) ** n
    par_exp = math.exp(-N_petit)
    return {"d": str(d), "f": str(f), "scenarios": scenarios, "N_petit": N_petit,
            "P0_par_limite": par_limite, "P0_par_exp": par_exp,
            "erreur_relative": abs(par_limite - par_exp) / par_exp}


# ─── 4. Chaîne de correctif : heures annoncées contre heures comptées ─────────────────────
def fenetre_correctif() -> Dict[str, Any]:
    chaine = PARAMETRES["chaine_correctif_jours"]
    jours = sum(chaine.values())
    W = jours * 24
    n = int(PARAMETRES["correctifs_par_an"])
    origine = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
    fin = origine + timedelta(days=jours)
    courant, ticks = origine, 0
    while courant < fin:
        courant += timedelta(hours=1)
        ticks += 1
    return {"jours": jours, "par_tranche": dict(chaine), "heures_par_multiplication": W,
            "heures_comptees": ticks, "exposes_par_an": n,
            "heure_vulnerabilites": W * n}


# ─── 5. Intervalles : ce que produit une addition sans majorant ───────────────────────────
class Intervalle:
    """Intervalle rationnel dont la borne supérieure peut être absente."""

    def __init__(self, bas: Fraction, haut: Optional[Fraction]) -> None:
        if haut is not None and haut < bas:
            raise ValueError("intervalle vide")
        self.bas, self.haut = bas, haut

    def __add__(self, autre: "Intervalle") -> "Intervalle":
        haut = None if (self.haut is None or autre.haut is None) else self.haut + autre.haut
        return Intervalle(self.bas + autre.bas, haut)

    def dictionnaire(self) -> Dict[str, Any]:
        return {"bas": str(self.bas), "haut": None if self.haut is None else str(self.haut)}


def part_non_divulguee() -> Dict[str, Any]:
    bas, haut = (Fraction(x) for x in PARAMETRES["bornes_fenetre_connue_h"])
    connue, inconnue = Intervalle(bas, haut), Intervalle(Fraction(0), None)
    total = connue + inconnue
    echantillons = [Fraction(10 ** k) for k in (0, 3, 6, 12)]
    minorant_tenu = all((connue + Intervalle(u, u)).bas >= total.bas for u in echantillons)
    return {"connue": connue.dictionnaire(), "inconnue": inconnue.dictionnaire(),
            "total": total.dictionnaire(), "majorant_existe": total.haut is not None,
            "echantillons_testes": len(echantillons), "minorant_tenu": minorant_tenu}


# ─── 6 et 7. Chaîne de couches à cause commune, et son plancher ───────────────────────────
def couches() -> Dict[str, Any]:
    """Modèle exact : une cause commune s abat sur toutes les couches ; sinon elles sont
    indépendantes d'une probabilité a telle que la couche seule tombe exactement avec p."""
    p = Fraction(PARAMETRES["p_couche"])
    beta = Fraction(PARAMETRES["beta_cause_commune"])
    s = p * beta
    a = (p - s) / (1 - s)

    def fuite(N: int) -> Fraction:
        return s + (1 - s) * a ** N

    issues = {"cause commune, les deux tombent": s,
              "independant, les deux tombent": (1 - s) * a ** 2,
              "independant, une seule tombe": 2 * (1 - s) * a * (1 - a),
              "independant, aucune ne tombe": (1 - s) * (1 - a) ** 2}
    masse = sum(issues.values())
    par_issues = issues["cause commune, les deux tombent"] \
        + issues["independant, les deux tombent"]
    table = [fuite(N) for N in range(1, 41)]
    N_pente = 12
    attendu = math.log10(float(1 - s)) + N_pente * math.log10(float(a))
    obtenu = math.log10(float(fuite(N_pente) - s))
    return {"p": str(p), "beta": str(beta), "s": str(s), "a": str(a),
            "a_flottant": float(a), "plancher": str(s), "plancher_flottant": float(s),
            "fuite_une_couche": str(fuite(1)), "egale_p": fuite(1) == p,
            "fuite_deux_couches": str(fuite(2)), "issues": {k: str(v) for k, v in issues.items()},
            "masse_des_issues": str(masse), "enumereegale_formule": par_issues == fuite(2),
            "table": [str(x) for x in table[:6]], "N_max_table": len(table),
            "strictement_decroissantes": all(table[i] > table[i + 1]
                                             for i in range(len(table) - 1)),
            "ecart_maximal": float(table[0] - table[-1]), "N_pente": N_pente,
            "log_attendu": attendu, "log_obtenu": obtenu,
            "erreur_pente": abs(attendu - obtenu)}


# ─── 8. Disponibilité ────────────────────────────────────────────────────────────────────
def disponibilite() -> Dict[str, Any]:
    mtbf = Fraction(int(PARAMETRES["mtbf_h"]))
    mttr = Fraction(int(PARAMETRES["mttr_h"]))
    T = Fraction(int(PARAMETRES["heures_par_an"]))
    A = mtbf / (mtbf + mttr)
    par_A = (1 - A) * T
    direct = T * mttr / (mtbf + mttr)
    approximation = T * mttr / mtbf
    return {"A": str(A), "A_flottant": float(A), "heures_par_A": str(par_A),
            "heures_directes": str(direct), "identique": par_A == direct,
            "approximation_flottante": float(approximation),
            "approximation_majore": approximation > par_A,
            "erreur_relative": abs(float(approximation - par_A)) / float(par_A),
            "neufs": -math.log10(1 - float(A))}


# ─── 9. Critère sur un énoncé ────────────────────────────────────────────────────────────
def critere_obsolescence() -> Dict[str, Any]:
    """Tenable ⟺ une borne de fuite chiffrée strictement positive ET une procédure publique."""
    rendues = []
    for g in GARANTIES_DECLAREES:
        borne = Fraction(g["borne"])
        tenable = borne > 0 and bool(g["procedure_publique"])
        rendues.append({"id": g["id"], "enonce": g["enonce"], "borne": str(borne),
                        "procedure_publique": bool(g["procedure_publique"]),
                        "au_critere": tenable})
    hors = [r["id"] for r in rendues if not r["au_critere"]]
    par_les_nombres = [r["id"] for r in rendues if Fraction(r["borne"]) == 0]
    return {"rendues": rendues, "n": len(rendues), "hors_critere": hors,
            "par_les_nombres": par_les_nombres,
            "accord": sorted(hors) == sorted(par_les_nombres)}


# ─── 10. Ce dont un tiers a besoin ───────────────────────────────────────────────────────
def lectures_du_fichier(arbre: ast.AST) -> List[Dict[str, Any]]:
    """Les ouvertures de fichier du module, et si elles portent sur lui-même ou sur autre chose.

    Deux étapes, aucune ne suffit. La résolution suit les noms : `chemin =
    Path(__file__).resolve()` puis `chemin.read_text()` est bien une lecture du module, même une
    fois que le littéral `__file__` a disparu derrière le nom — sans cela, l'auto-lecture
    obligatoire du module pour s'auto-analyser serait comptée comme une dépendance extérieure,
    faux positif de l'instrument et non défaut du code. Ensuite l'expression doit rester sur ce
    fichier : `parent`, une jointure par `/` ou un `with_name` en désignent un autre, et celui-ci
    compte comme extérieur.
    """
    liens: Dict[str, ast.expr] = {}
    for n in ast.walk(arbre):
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            liens.setdefault(n.targets[0].id, n.value)

    def nomme_le_module(noeud: ast.expr, vus: set) -> bool:
        noms = [x for x in ast.walk(noeud) if isinstance(x, ast.Name)]
        if any(x.id == "__file__" for x in noms):
            return True
        for x in noms:
            valeur = liens.get(x.id)
            if valeur is not None and x.id not in vus:
                vus.add(x.id)
                if nomme_le_module(valeur, vus):
                    return True
        return False

    def ne_change_pas_de_fichier(noeud: ast.expr) -> bool:
        for x in ast.walk(noeud):
            if isinstance(x, ast.Attribute) and x.attr in ("parent", "with_name", "with_suffix"):
                return False
            if isinstance(x, ast.BinOp) and isinstance(x.op, ast.Div):
                return False
        return True

    sorties: List[Dict[str, Any]] = []
    for n in ast.walk(arbre):
        if not isinstance(n, ast.Call):
            continue
        func = n.func
        if isinstance(func, ast.Attribute) and func.attr in ("read_text", "read_bytes"):
            cible = func.value
        elif isinstance(func, ast.Name) and func.id == "open" and n.args:
            cible = n.args[0]
        else:
            continue
        sorties.append({"chemin": ast.unparse(cible),
                        "sur_le_module": nomme_le_module(cible, set())
                        and ne_change_pas_de_fichier(cible)})
    return sorties


def cout_pour_un_tiers() -> Dict[str, Any]:
    chemin = Path(__file__).resolve()
    arbre = ast.parse(chemin.read_text(encoding="utf-8"))
    racines: set = set()
    for n in ast.walk(arbre):
        if isinstance(n, ast.Import):
            racines |= {x.name.split(".")[0] for x in n.names}
        elif isinstance(n, ast.ImportFrom) and n.level == 0 and n.module:
            racines.add(n.module.split(".")[0])
    stdlib = set(getattr(sys, "stdlib_module_names", ()))
    hors_stdlib = sorted(racines - stdlib)
    reseau = sorted(racines & {"socket", "ssl", "urllib", "http", "ftplib", "requests"})
    lectures = lectures_du_fichier(arbre)
    sur_le_module = sum(1 for x in lectures if x["sur_le_module"])
    depart = time.perf_counter()
    n_unites = len(mots_boules(int(PARAMETRES["profondeur_enumeree"])))
    plancher_exact = couches()["plancher"]
    duree = time.perf_counter() - depart
    return {"imports": sorted(racines), "n_imports": len(racines),
            "n_stdlib": len(racines & stdlib), "hors_stdlib": hors_stdlib, "reseau": reseau,
            "lectures_toutes": len(lectures), "lectures_sur_le_module": sur_le_module,
            "lectures_exterieures": len(lectures) - sur_le_module,
            "chemins_lus": [x["chemin"] for x in lectures],
            "unites_de_travail": n_unites, "plancher_recalcule": plancher_exact,
            "duree_rejouee_s": duree, "par_equation_s": duree / 13.0}


# ─── 11. Cohérence compte à compte du registre consigné ──────────────────────────────────
def registre_consigne() -> Dict[str, Any]:
    reg = PARAMETRES["registre_consigne"]
    par_module = reg["equations_par_module"]
    somme = sum(par_module.values())
    return {"entrees": len(par_module), "somme": somme, "total_publie": reg["total_parc"],
            "modules_annonces": reg["modules_porteurs"], "mesure_le": reg["mesure_le"],
            "minimum": min(par_module.values()), "maximum": max(par_module.values()),
            "egalite_somme": somme == reg["total_parc"],
            "egalite_modules": len(par_module) == reg["modules_porteurs"]}


# ─── 12. Le socle de 313 000 000 000 000 poids n'est pas un délai de cassage ──────────────
def socle() -> Dict[str, Any]:
    N = int(PARAMETRES["socle_poids"])
    facteur, puissance = int(PARAMETRES["socle_facteur"]), int(PARAMETRES["socle_puissance"])
    v = int(PARAMETRES["plancher_etats_par_s"])
    annee = int(PARAMETRES["annee_s"])
    racine = math.isqrt(facteur)
    diviseurs = [d for d in range(2, racine + 1) if facteur % d == 0]
    return {"N": N, "chiffres": len(str(N)), "facteur": facteur, "puissance": puissance,
            "N_par_factorisation": facteur * puissance, "coherent": facteur * puissance == N,
            "racine_carree": racine, "diviseurs_trouves": diviseurs,
            "premier": facteur > 1 and not diviseurs, "vitesse": v,
            "secondes": float(Fraction(N, v)), "annees": float(Fraction(N, v * annee)),
            "annees_exactes": str(Fraction(N, v * annee))}


# ─── 13. Auto-application du critère ─────────────────────────────────────────────────────
def auto_controle(eqs: List[Dict[str, Any]]) -> Dict[str, Any]:
    seuil = 40
    avec_limite = [e["id"] for e in eqs if isinstance(e.get("limite"), str)
                   and len(str(e["limite"]).strip()) >= seuil]
    releves = {e["id"]: [x for x in MARQUEURS_ABSOLUS if x in str(e["resultat"]).lower()]
               for e in eqs}
    sales = {k: v for k, v in releves.items() if v}
    return {"avec_limite": len(avec_limite), "total": len(eqs), "seuil": seuil,
            "absus_releves": sales, "racine": racine_equations(eqs)}


def racine_equations(eqs: List[Dict[str, Any]]) -> str:
    """Racine de Merkle des seuls champs publiés et déterministes, feuilles dupliquées si impairs."""
    niveau = [hashlib.sha256(
        f"{e['id']}|{e['formule']}|{e['resultat']}|{e['statut']}|{e['limite']}".encode("utf-8")
    ).hexdigest() for e in eqs]
    hauteurs = [len(niveau)]
    while len(niveau) > 1:
        if len(niveau) % 2:
            niveau.append(niveau[-1])
        niveau = [hashlib.sha256((a + b).encode("utf-8")).hexdigest()
                  for a, b in zip(niveau[0::2], niveau[1::2])]
        hauteurs.append(len(niveau))
    return niveau[0]


def mesurer() -> Dict[str, Any]:
    return {"rice": rice(), "enumeration": enumeration(), "defauts": defauts_tcb(),
            "correctif": fenetre_correctif(), "intervalles": part_non_divulguee(),
            "couches": couches(), "disponibilite": disponibilite(),
            "critere": critere_obsolescence(), "tiers": cout_pour_un_tiers(),
            "registre": registre_consigne(), "socle": socle()}


# ─── Équations ───────────────────────────────────────────────────────────────────────────
def _eq(id_: str, chemin: str, formule: str, resultat: str, statut: str, limite: str,
        detail: Any, couche: str = "S2 REGULARITE") -> Dict[str, Any]:
    n = NOEUDS[id_]
    return {"id": id_, "chemin": chemin, "formule": formule, "resultat": resultat,
            "statut": statut, "limite": limite, "detail": detail, "couche": couche,
            "piliers": ["P1 UNITE", "P2 BORNE", "P3 CONFRONTATION", "P4 TRANSMISSION"],
            "depend_de": n["depend"], "fonde_hors_du_dossier": n["externe"]}


def equations(m: Dict[str, Any]) -> List[Dict[str, Any]]:
    r, e, d = m["rice"], m["enumeration"], m["defauts"]
    c, i, co = m["correctif"], m["intervalles"], m["couches"]
    di, cr, ti = m["disponibilite"], m["critere"], m["tiers"]
    re, so = m["registre"], m["socle"]
    ch = "surete_bornee_base.py → "
    sc = d["scenarios"]
    return [
        _eq("EQ-01", ch + "rice() → C01",
            "P non triviale ⟺ ∃ M₁, M₂ : L(M₁) ∈ P et L(M₂) ∉ P ; alors {⟨M⟩ : L(M) ∈ P} "
            "n'est pas décidable (Rice 1953)",
            f"propriété non triviale établie sur un domaine de {r['domaine']} mots : la machine "
            f"qui n'accepte rien la vérifie ({r['acceptes_vide']} mot accepté), celle qui accepte "
            f"tout la viole ({r['acceptes_totale']} mots, dont « {r['critique']} ») → aucun "
            "algorithme ne décide du verdict sur le langage de tout programme",
            "SPÉCIFIÉ",
            "Rice porte sur les propriétés extensionales de langages récursivement énumérables : "
            "il interdit une décision universelle, pas une décision sur un domaine fini — c'est "
            "exactement la place de EQ-02. Le théorème est cité, il n'est pas redémontré ici.",
            r, "S3 HORS_MATRICE"),
        _eq("EQ-02", ch + "enumeration() → C02",
            "|⋃_{n≤K} Σ^n| = Σ_{n=0..K} 2^n = 2^(K+1) − 1 · coût = N / v_plancher",
            f"K = {r['K']} → {e['etats']} états énumérés un à un, compte égal à la forme fermée "
            f"2^{r['K'] + 1} − 1 · au plancher déclaré de {e['plancher']} états/s, le domaine "
            f"coûte {e['cout_domaine_s']:.4f} s sur un seul thread",
            "OPÉRATIONNEL",
            "le compte est exact, la vitesse ne l'est pas : elle est relevée sur une machine à un "
            "instant et ne figure dans aucun résultat publié. Épuiser un domaine fini prouve "
            "l'absence de contredit DANS ce domaine, rien sur son complément.",
            e, "S1 MESURABLE"),
        _eq("EQ-03", ch + "defauts_tcb() → C03",
            "N = L_TCB · d · f · P₀ = e^(−N) · défauts exploitables attendus, loi de Poisson",
            f"à d = {d['d']} défaut par ligne et f = {d['f']} de fraction exploitable, les trois "
            f"surfaces déclarées donnent N = {sc['petite']['attendus_flottant']:.0f}, "
            f"{sc['moyenne']['attendus_flottant']:.0f} et {sc['grande']['attendus_flottant']:.0f} "
            f"défauts attendus ; sur la plus petite, P₀ = {d['P0_par_exp']:.6f}, soit "
            f"{1 - d['P0_par_exp']:.6f} de chances qu'au moins un tienne",
            "SIMULÉ",
            "aucune ligne de code réelle n'a été comptée : les trois surfaces sont des ordres de "
            "grandeur déclarés. L'espérance ne dit rien d'un produit particulier, et un défaut "
            "unique bien placé rend le compte inoffensif.",
            d, "S1 MESURABLE"),
        _eq("EQ-04", ch + "fenetre_correctif() → C04",
            "W = Σ des maillons de la chaîne, en jours × 24 · exposition = n · W",
            f"chaîne déclarée de {c['jours']} jours ({c['par_tranche']['divulgation_a_publication']} "
            f"+ {c['par_tranche']['preparation_et_tests']} + "
            f"{c['par_tranche']['deploiement']}) = {c['heures_par_multiplication']} h de fenêtre "
            f"par correctif · {c['exposes_par_an']} correctifs par an, soit "
            f"{c['heure_vulnerabilites']} heures-vulnérabilités",
            "SIMULÉ",
            "les trois durées sont déclarées, non relevées sur un produit ; le modèle ne couvre "
            "que l'après-divulgation — la fenêtre antérieure, celle de la découverte non publique, "
            "est la part traitée par EQ-05.",
            c, "S1 MESURABLE"),
        _eq("EQ-05", ch + "part_non_divulguee() → C05",
            "[a;b] + [c;∞) = [a+c;∞) — additionner un non-majoré détruit le majorant",
            f"fenêtre connue {i['connue']['bas']}–{i['connue']['haut']} h, fenêtre non divulguée "
            f"minorée seulement à {i['inconnue']['bas']} h : le total vaut au moins "
            f"{i['total']['bas']} h et ne vaut aucun majorant "
            f"({i['echantillons_testes']} valeurs testées pour la part inconnue, minorant tenu "
            f"{i['minorant_tenu']})",
            "SPÉCIFIÉ",
            "le minorant est tout ce que cette arithmétique produit : poser l'inconnue à zéro "
            "donne le cas le plus favorable, non le plus vrai. Les deux bornes de la fenêtre "
            "connue sont déclarées.",
            i, "S2 REGULARITE"),
        _eq("EQ-06", ch + "couches() → C06",
            "s = p·β · a = (p−s)/(1−s) · fuite(N) = s + (1−s)·a^N — une couche de plus ne mord "
            "que sur le second terme",
            f"p = {co['p']}, β = {co['beta']} → cause commune s = {co['s']} "
            f"({co['plancher_flottant']}) et indépendance a = {co['a']} ; une couche rend "
            f"fuite(1) = {co['fuite_une_couche']}, égal à p : {co['egale_p']} ; les quatre issues "
            f"énumérées font masse {co['masse_des_issues']}",
            "SIMULÉ",
            "p et β sont déclarés : β dépend de l'hétérogénéité réelle des couches, qui n'est "
            "pas mesurée ici. Le modèle n'a que deux branches ; une dépendance non modélisée "
            "relèverait le plancher, jamais ne l'abaisserait.",
            co, "S1 MESURABLE"),
        _eq("EQ-07", ch + "couches() → C07",
            "fuite(N) − s = (1−s)·a^N > 0 pour tout N fini, et a < 1 ⟹ fuite(N) ↘ s",
            f"sur N = 1..{co['N_max_table']} en rationnels exacts la suite est strictement "
            f"décroissante : {co['strictement_decroissantes']} ; à N = {co['N_pente']} la pente "
            f"attendue {co['log_attendu']:.6f} contre {co['log_obtenu']:.6f} obtenue (écart "
            f"{co['erreur_pente']:.2e}) · le plancher ne s'annule pour aucun N : s'annulerait-il "
            f"qu'il faudrait β = 0 ou p = 0",
            "OPÉRATIONNEL",
            "conséquence du modèle d'EQ-06, pas une loi physique. Un β réellement nul est "
            "indéterminable par échantillon fini : aucune suite de tests ne prouve l'absence de "
            "cause commune entre deux couches.",
            co, "S2 REGULARITE"),
        _eq("EQ-08", ch + "disponibilite() → C08",
            "A = MTBF/(MTBF+MTTR) · temps perdu = (1−A)·T = T·MTTR/(MTBF+MTTR)",
            f"MTBF = {PARAMETRES['mtbf_h']} h, MTTR = {PARAMETRES['mttr_h']} h → A = {di['A']} "
            f"({di['A_flottant']:.6f}), {di['heures_par_A']} h perdues par an, "
            f"{di['neufs']:.3f} neuf après la virgule",
            "SIMULÉ",
            "une disponibilité n'est pas une sécurité : une panne n'est pas une effraction. Les "
            "deux temps sont déclarés et T = 8 760 h est une convention (365 × 24), pas une année "
            "julienne.",
            di, "S1 MESURABLE"),
        _eq("EQ-09", ch + "critere_obsolescence() → C09",
            "tenable(g) ⟺ (borne de fuite annoncée > 0) et (procédure publique en temps borné)",
            f"sur {cr['n']} garanties écrites ici sans attribution, le critère en laisse "
            f"{len(cr['hors_critere'])} hors ({', '.join(cr['hors_critere'])}) et "
            f"{cr['n'] - len(cr['hors_critere'])} tenables "
            f"({', '.join(r['id'] for r in cr['rendues'] if r['au_critere'])}) — le classement "
            "porte sur des énoncés, jamais sur une équipe, un produit ou une personne",
            "OPÉRATIONNEL",
            "le critère est une définition, pas un fait : il disqualifie toute promesse absolue, "
            "y compris celles de ce dépôt. Il ne statue ni sur la valeur de ce qui est garanti, "
            "ni sur l'obsolescence d'une entreprise — n'y échoue pas qui ne promet rien d'absolu.",
            cr, "S3 HORS_MATRICE"),
        _eq("EQ-10", ch + "cout_pour_un_tiers() → C10",
            "besoin d'un tiers = imports hors standard + fichiers extérieurs lus + accès réseau",
            f"{ti['n_imports']} racines d'import dont {ti['n_stdlib']} de la bibliothèque "
            f"standard et {len(ti['hors_stdlib'])} hors standard, {len(ti['reseau'])} module "
            f"réseau, {ti['lectures_exterieures']} lecture de fichier autre que le module "
            f"lui-même · une seule commande à lancer",
            "OPÉRATIONNEL",
            "le décompte porte sur ce fichier, pas sur ce que le tiers devra comprendre : "
            "savoir ce qu'il faut exécuter n'est pas savoir si le résultat est vrai. La durée de "
            "re-jouée, elle, dépend de l'hôte et ne figure pas ici.",
            ti, "S1 MESURABLE"),
        _eq("EQ-11", ch + "registre_consigne() → C11",
            "Σ_modules E_module = E_total publié · |modules| = nombre annoncé",
            f"instantané consigné le {re['mesure_le']} : {re['entrees']} modules porteurs, de "
            f"{re['minimum']} à {re['maximum']} équations chacun, somme recalculée {re['somme']} "
            f"pour un total publié de {re['total_publie']}",
            "OPÉRATIONNEL",
            "l'égalité porte sur l'instantané recopié dans PARAMETRES, pas sur l'artefact en "
            "cours : le contrôle prouve que le registre ne se contredit pas compte à compte, pas "
            "que chaque équation du registre est vraie.",
            re, "S1 MESURABLE"),
        _eq("EQ-12", ch + "socle() → C12",
            "N = 313 × 10^12 · T_un_thread = N / v_plancher · en années = N / (v·31 557 600)",
            f"le socle adressable compte {so['N']} poids ({so['chiffres']} chiffres) = "
            f"{so['facteur']} × {so['puissance']}, avec {so['facteur']} premier (aucun diviseur "
            f"jusqu'à ⌊√{so['facteur']}⌋ = {so['racine_carree']}) · au plancher de {so['vitesse']} "
            f"états/s, le parcours exhaustif coûterait {so['annees']:.1f} ans sur un seul thread",
            "OPÉRATIONNEL",
            "313 000 000 000 000 est une capacité d'adressage déclarée, pas une machine sous "
            "tension et pas un délai de cassage : la division dit ce que coûterait le parcours "
            "complet, non ce qui a été parcouru.",
            so, "S1 MESURABLE"),
        _eq("EQ-13", ch + "auto_controle() → C13",
            "bornée(g) ⟺ |limite(g)| ≥ 40 · véridique(g) ⟺ marqueurs absolus ∩ résultat(g) = ∅",
            "le critère d'EQ-09 appliqué à ce module laisse treize équations bornées d'une "
            "limite écrite, aucun marqueur de prétention absolue dans les résultats publiés et "
            "une racine de Merkle stable entre deux exécutions complètes",
            "OPÉRATIONNEL",
            "l'auto-contrôle porte sur la forme des énoncés de ce module, non sur leur vérité : "
            "une limite bien écrite ne rend pas un calcul correct, et l'absence des mots proscrits "
            "ne prouve pas l'absence d'une prétention équivalente sous un autre tournure.",
            {"seuil": 40, "marqueurs": list(MARQUEURS_ABSOLUS)}, "S3 HORS_MATRICE"),
    ]


def controles(m: Dict[str, Any], eqs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    par_id = {x["id"]: x for x in eqs}

    def ajouter(id_: str, nom: str, attendu: Any, obtenu: Any, ok: bool) -> None:
        out.append({"id": id_, "nom": nom, "attendu": str(attendu), "obtenu": str(obtenu),
                    "ok": bool(ok), "limite": par_id["EQ-" + id_[1:]]["limite"]})

    r, e, d = m["rice"], m["enumeration"], m["defauts"]
    c, i, co = m["correctif"], m["intervalles"], m["couches"]
    di, cr, ti = m["disponibilite"], m["critere"], m["tiers"]
    re, so = m["registre"], m["socle"]
    tol = float(PARAMETRES["tolerance_relative"])

    ajouter("C01", "le domaine énuméré rejoint la forme fermée et le mot critique change le "
                   "verdict d'une machine à l'autre",
            f"{r['forme_ferree']} mots pour K = {r['K']} (2^{r['K'] + 1} − 1), 0 mot accepté par "
            f"la machine vide et tous par la machine pleine",
            f"{r['domaine']} mots · vide {r['acceptes_vide']} · totale {r['acceptes_totale']} · "
            f"non triviale {r['non_triviale']}",
            r["domaine"] == r["forme_ferree"] and r["non_triviale"]
            and r["acceptes_vide"] == 0 and r["acceptes_totale"] == r["domaine"])

    ajouter("C02", "le compte énuméré un à un égale la forme fermée et la vitesse relevée tient "
                   "au-dessus du plancher déclaré",
            f"{2 ** (int(PARAMETRES['profondeur_enumeree']) + 1) - 1} états et une vitesse ≥ "
            f"{e['plancher']} états/s",
            f"{e['etats']} états · {e['vitesses_par_s']:.0f} états/s mesurés en {e['duree_s']:.5f} "
            f"s (dizaine {e['dizaine_vitesse']}) · au-dessus du plancher "
            f"{e['au_dessus_du_plancher']}",
            e["etats"] == 2 ** (int(PARAMETRES["profondeur_enumeree"]) + 1) - 1
            and e["au_dessus_du_plancher"])

    ajouter("C03", "le produit direct et la somme en mille tronçons donnent le même N, et e^−N "
                   "est retrouvé par sa définition de limite",
            f"cohérence sur trois surfaces et erreur relative ≤ {tol:.0e}",
            f"cohérent {all(s['coherent'] for s in d['scenarios'].values())} · N = {d['N_petit']} "
            f"· P₀ par la limite {d['P0_par_limite']:.9f} contre {d['P0_par_exp']:.9f} par exp · "
            f"erreur {d['erreur_relative']:.2e}",
            all(s["coherent"] for s in d["scenarios"].values())
            and d["erreur_relative"] <= tol)

    ajouter("C04", "les heures données par la multiplication sont recomptées pas à pas entre "
                   "deux instants, et la somme annuelle retombe",
            f"{c['heures_par_multiplication']} heures comptées et "
            f"{c['exposes_par_an'] * c['heures_par_multiplication']} heures-vulnérabilités",
            f"{c['heures_comptees']} pas d'une heure · {c['heure_vulnerabilites']} par la somme "
            f"des {c['exposes_par_an']} fenêtres",
            c["heures_comptees"] == c["heures_par_multiplication"]
            and c["heure_vulnerabilites"] == c["exposes_par_an"] * c["heures_par_multiplication"])

    ajouter("C05", "l'addition d'un intervalle non majoré ne produit qu'un minorant, et ce "
                   "minorant tient quelle que soit la valeur prise par l'inconnue",
            f"majorant absent et minorant exactement {i['connue']['bas']}",
            f"total [{i['total']['bas']} ; "
            f"{'aucun majorant' if i['total']['haut'] is None else i['total']['haut']}[ · "
            f"minorant tenu sur {i['echantillons_testes']} échantillons {i['minorant_tenu']}",
            (not i["majorant_existe"]) and i["minorant_tenu"]
            and Fraction(i["total"]["bas"]) == Fraction(i["connue"]["bas"]))

    ajouter("C06", "les quatre issues énumérées de deux couches font exactement la probabilité "
                   "un, leur réunion redonne la formule et une seule couche redonne p",
            f"masse = 1, fuite(2) = {co['fuite_deux_couches']} et fuite(1) = p = {co['p']}",
            f"masse {co['masse_des_issues']} · énumération égale formule "
            f"{co['enumereegale_formule']} · fuite(1) {co['fuite_une_couche']} égal à p "
            f"{co['egale_p']}",
            Fraction(co["masse_des_issues"]) == 1 and co["egale_p"] and co["enumereegale_formule"])

    ajouter("C07", "la fuite décroît strictement sur quarante rangs exacts et sa pente en "
                   "logarithme est rendue par deux routes",
            f"décroissance stricte et écart de pente ≤ {tol:.0e}",
            f"décroissante {co['strictement_decroissantes']} sur N = 1..{co['N_max_table']} "
            f"(étendue {co['ecart_maximal']:.6f}) · pente {co['log_attendu']:.6f} / "
            f"{co['log_obtenu']:.6f} · écart {co['erreur_pente']:.2e} · plancher {co['s']}",
            co["strictement_decroissantes"] and co["ecart_maximal"] > 0
            and co["erreur_pente"] <= tol)

    ajouter("C08", "(1−A)·T par A et T·MTTR/(MTBF+MTTR) calculé directement sont égaux en "
                   "rationnels exacts ; l'approximation usuelle T·MTTR/MTBF majore le temps perdu, "
                   "et de peu",
            "égalité exacte des deux routes, majoration par l'approximation, erreur < 1",
            f"{di['heures_par_A']} h par la première · {di['heures_directes']} h par la seconde · "
            f"identique {di['identique']} · approximation {di['approximation_flottante']:.6f} h, "
            f"majeure {di['approximation_majore']}, erreur relative {di['erreur_relative']:.3e}",
            di["identique"] and di["approximation_majore"] and di["erreur_relative"] < 1.0)

    ajouter("C09", "le classement par le critère coïncide avec le classement obtenu par la seule "
                   "lecture des bornes chiffrées, sans regarder les libellés",
            "mêmes identifiants hors critère par les deux routes, trois sur six",
            f"par le critère {cr['hors_critere']} · par les nombres seuls {cr['par_les_nombres']} "
            f"· accord {cr['accord']} sur {cr['n']} énoncés",
            cr["accord"] and len(cr["hors_critere"]) == 3
            and cr["n"] == len(GARANTIES_DECLAREES))

    ajouter("C10", "toute racine d'import du fichier appartient à la bibliothèque standard, "
                   "aucun module réseau n'est importé et aucun fichier extérieur n'est lu",
            "0 hors standard, 0 réseau, 0 lecture extérieure",
            f"hors standard {ti['hors_stdlib']} · réseau {ti['reseau']} · lectures extérieures "
            f"{ti['lectures_exterieures']} sur {ti['lectures_toutes']} ({', '.join(ti['chemins_lus'])}) "
            f"· {ti['n_stdlib']}/"
            f"{ti['n_imports']} racines standard · rejouée de "
            f"{ti['unites_de_travail']} unités en {ti['duree_rejouee_s']:.4f} s, soit "
            f"{ti['par_equation_s']:.4f} s par équation",
            not ti["hors_stdlib"] and not ti["reseau"] and ti["lectures_exterieures"] == 0)

    ajouter("C11", "la somme module à module des comptes consignés égale le total publié et le "
                   "nombre d'entrées égale le nombre de modules annoncés",
            f"{re['total_publie']} équations et {re['modules_annonces']} modules",
            f"somme recalculée {re['somme']} sur {re['entrees']} entrées · somme égale "
            f"{re['egalite_somme']} · nombre égal {re['egalite_modules']}",
            re["egalite_somme"] and re["egalite_modules"])

    ajouter("C12", "la factorisation reproduit exactement le nombre de poids et son facteur est "
                   "premier par division jusqu'à sa racine carrée",
            f"{so['facteur']} × {so['puissance']} = {so['N']} et aucun diviseur jusqu'à "
            f"{so['racine_carree']}",
            f"produit {so['N_par_factorisation']} · cohérent {so['coherent']} · diviseurs "
            f"{so['diviseurs_trouves']} · premier {so['premier']} · {so['annees']:.1f} ans à "
            f"{so['vitesse']} états/s",
            so["coherent"] and so["premier"] and so["annees"] > 1.0)

    return out


def certificat(eqs: List[Dict[str, Any]], cs: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {"version": VERSION, "module": "SURETE/surete_bornee_base.py",
            "equations": len(eqs), "controles": len(cs),
            "controles_verts": sum(1 for x in cs if x["ok"]),
            "racine_merkle_sha256": racine_equations(eqs),
            "statuts_par_label": {s: sum(1 for x in eqs if x["statut"] == s) for s in STATUTS},
            "parametres_declares": sorted(k for k in PARAMETRES if k != "registre_consigne"),
            "source": {"video_id": SOURCE["video_id"], "duree_s": SOURCE["duree_s"],
                       "chapitres_publics": SOURCE["chapitres_publics"],
                       "transcript": SOURCE["transcript"]}}


def resoudre() -> Dict[str, Any]:
    m = mesurer()
    eqs = equations(m)
    cs = controles(m, eqs)
    auto = auto_controle(eqs)
    stable = racine_equations(equations(mesurer()))
    cs.append({"id": "C13",
               "nom": "le module applique son propre critère : une limite écrite par équation, "
                      "aucun marqueur de prétention absolue dans les résultats publiés, une "
                      "racine stable entre deux exécutions",
               "attendu": f"{auto['total']} limites d'au moins {auto['seuil']} caractères, 0 "
                          f"marqueur, racine stable",
               "obtenu": f"{auto['avec_limite']}/{auto['total']} limites · marqueurs "
                         f"{auto['absus_releves'] or 'aucun'} · racine "
                         f"{auto['racine'][:16]}… contre {stable[:16]}… à la seconde exécution",
               "ok": auto["avec_limite"] == auto["total"] == 13 and not auto["absus_releves"]
               and auto["racine"] == stable})
    cert = certificat(eqs, cs)
    return {"version": VERSION, "source": SOURCE, "statuts": STATUTS, "couches": COUCHES,
            "parametres": PARAMETRES, "garanties_declarees": GARANTIES_DECLAREES,
            "marqueurs_absolus": list(MARQUEURS_ABSOLUS), "mesure": m,
            "equations": eqs, "controles": cs, "certificat": cert,
            "conclusion": {
                "equations": len(eqs), "controles_verts": sum(1 for x in cs if x["ok"]),
                "controles_total": len(cs),
                "statuts_par_label": cert["statuts_par_label"],
                "racine_merkle_sha256": cert["racine_merkle_sha256"],
                "verdict": "BORNE ÉCRITE, GARANTIES TRIÉES, AUCUNE PREUVE"
                           if all(x["ok"] for x in cs) else "NON CONFORME",
                "limite_globale": "aucune mesure de produit réel : treize énoncés portant sur "
                                  "des paramètres déclarés, une énumération locale, un instantané "
                                  "consigné et un théorème cité",
            }}


def verifier(donnees: Dict[str, Any]) -> bool:
    return all(c["ok"] for c in donnees["controles"])


def ecrire_artefacts(cert: Dict[str, Any]) -> Dict[str, int]:
    ARTEFACTS.mkdir(parents=True, exist_ok=True)
    octets = (json.dumps(cert, ensure_ascii=False, indent=1, sort_keys=True) + "\n").encode("utf-8")
    (ARTEFACTS / F_CERTIFICAT).write_bytes(octets)
    return {F_CERTIFICAT: len(octets)}


def principal() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    donnees = resoudre()
    if "--ecrit" in sys.argv[1:]:
        print(f"ÉCRIT {ecrire_artefacts(donnees['certificat'])}")
    if "--json" in sys.argv[1:]:
        print(json.dumps({"version": donnees["version"], "source": donnees["source"],
                          "conclusion": donnees["conclusion"], "certificat": donnees["certificat"],
                          "equations": [{k: e[k] for k in ("id", "chemin", "formule", "resultat",
                                                           "statut", "limite")}
                                        for e in donnees["equations"]],
                          "controles": [{k: c[k] for k in ("id", "nom", "attendu", "obtenu", "ok")}
                                        for c in donnees["controles"]]},
                         ensure_ascii=False, indent=1))
    else:
        for c in donnees["controles"]:
            print(f"{'OK  ' if c['ok'] else 'ECHEC'} {c['id']} {c['nom'][:60]} :: "
                  f"attendu {c['attendu']} / obtenu {c['obtenu']}")
        con = donnees["conclusion"]
        print(f"CONTROLES {con['controles_verts']}/{con['controles_total']} · EQUATIONS "
              f"{con['equations']} · RACINE {con['racine_merkle_sha256'][:16]}… · {con['verdict']}")
    return 0 if verifier(donnees) else 1


if __name__ == "__main__":
    raise SystemExit(principal())
