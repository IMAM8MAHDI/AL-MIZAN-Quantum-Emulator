# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""CONSTRUCTION — la couche qui descend le théorème de CONTINUITE jusqu'à l'atelier.

D'où part ce dossier
--------------------
`CONTINUITE/continuite_base.py` a démontré, sans mesure, que la chaîne x_k = MIZAN·ρ^k, avec
ρ = (249/400)^(1/12), sort du domaine déclaré D = [61/500 ; 249/400] au pas 42 et que son clampage
n'admet qu'un seul point fixe, 61/500. Ce résultat était resté un nombre. Cette couche lui donne
une cote, une tolérance, une masse, un outil et une réfutation.

Ce que ce module fait, dans l'ordre
-----------------------------------
  1. il relit les semences et le rapport ρ chez CONTINUITE, puis ré-encadre ρ par bissection
     entière jusqu'à quinze décimales — celle du théorème n'est pas suffisante pour coter un plan
     (EQ-01, EQ-13) ;
  2. il écrit la pile de quarante-trois plateaux carrés emboîtés : à chaque cran, la cote est LE
     multiple unique de 0,01 mm tombé dans l'intervalle rationnel du cran — aucune arrondi
     flottant n'entre dans une cote (EQ-02, EQ-03) ;
  3. il déclare la tolérance relative ε_a = 1/1000 (choix d'auteur) et montre que l'erreur
     cumulative du pile est exactement ε_a : les tolérances s'additionnent au prorata des cotes,
     le budget d'erreur ne grossit pas (EQ-04) ;
  4. il calcule le facteur de cascade 1/(1−ρ²) = 13,1645… en rationnels encadrés : la matière
     totale de la pile infinie est bornée, et les 43 crans retenus en laissent 6,9 % dehors
     (EQ-05) ;
  5. il produit une nomenclature (CSV), un plan coté (SVG) et des prédictions réfutables (MD),
     puis relit ses propres fichiers pour vérifier que ce qui est écrit est ce qui a été calculé
     (EQ-06, EQ-07, EQ-11) ;
  6. il dit l'échelle humaine en deux faits contradictoires : toutes les cotes tiennent dans le
     geste, la masse totale ne se porte pas (EQ-08) ; il classe chaque cran derrière un outil
     d'atelier déclaré et en déduit qu'aucun vide, aucune salle blanche n'est requis (EQ-09,
     EQ-10) ;
  7. il compte les prototypes construits — zéro — et écrit cette absence dans les quatre
     artefacts (EQ-12) ; il relie la cascade au catalogue scellé des 27 formes (EQ-14), se rejoue
     à l'octet près (EQ-15) et laisse ouvertes les limites qu'il ne remplit pas (EQ-16).

Ce qu'il ne fait pas : il n'affirme aucune propriété d'aucun objet réel, ne certifie aucun outil,
ne convertit pas ρ en loi physique, n'a rien usiné ni rien mesuré, et ne touche pas à
`horloge_noyau/`.

Usage :
    cd ZENODO_DEPOT_ALMIZAN && py -3 CONSTRUCTION/construction_base.py
    cd ZENODO_DEPOT_ALMIZAN && py -3 CONSTRUCTION/construction_base.py --ecrit
    cd ZENODO_DEPOT_ALMIZAN && py -3 FONDATION/OUTILS/audit_piliers.py CONSTRUCTION/construction_base.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from decimal import Decimal, getcontext
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

RACINE = Path(__file__).resolve().parents[1]
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

DOSSIER = Path(__file__).resolve().parent
ARTEFACTS = DOSSIER / "artefacts"
PROTOTYPES = DOSSIER / "prototypes"
PRECISION = 60

from CONTINUITE import continuite_base as CONT                                # noqa: E402
from FONDATION import fondation_base as FB                                    # noqa: E402
from bibliotheques import lib_almizan_extension as EXT                        # noqa: E402

# ─── 1. Source et provenance --------------------------------------------------

SOURCE: Dict[str, Any] = {
    "point_de_depart": "demande d'auteur 2026-11-09 : « developper les outils applicatifs réels "
                       "avec la creation de designs et de plans de construction materiel engin et "
                       "tout ce qui peut etre produit à l'echelle de l'humanite »",
    "auteur": "M. Ahmed EL BAHLOUL (IMAM8MAHDI)",
    "antecedents_uses": [
        "CONTINUITE/continuite_base.py — le théorème dont cette couche tire les cotes : ρ, le pas "
        "42 et le point fixe 61/500 y sont démontrés, ils ne sont pas recopiés ici",
        "bibliotheques/lib_almizan_extension.py — MIZAN = 249/400, LIGNE_REF = 61/500 et le "
        "catalogue scellé des 27 formes étendues",
        "ABONDANCE/moteur_page_trilingue.py — l'unique fabriquant des pages publiées : ce dossier "
        "écrit des plans, pas des pages",
    ],
    "ce_que_ce_module_n_utilise_pas": [
        "aucune mesure d'objet réel : aucun pied à coulisse, aucune balance, aucune machine n'est "
        "intervenu dans ce dossier",
        "aucun flottant dans les verdicts : les cotes viennent d'une bissection entière, les "
        "bornes sont des fractions",
        "aucune vidéo, aucun transcript, aucune citation parlée",
        "aucune certification d'outil, de matériau ou de fournisseur : les outils sont des noms "
        "déclarés, pas des machines vérifiées",
    ],
}

PHRASE_ABSENCE = "aucun prototype construit"

# ─── 2. Déclarations de conception (choix d'auteur, jamais des mesures) -------

CADRE_MM = Fraction(1000)          # un cran de tête de 622,5 mm : le mètre comme cadre
PAS_AFFICHAGE = Fraction(1, 100)    # 0,01 mm : la résolution que le plan s'oblige à tenir
EPS_TOL = Fraction(1, 1000)         # tolérance relative ε_a : 1 µm par mm — déclaré (EQ-04)
EPAISSEUR_MM = Fraction(8)          # épaisseur unique des plateaux — déclaré
MASSE_VOL_KG_MM3 = Fraction(157, 20) / Fraction(10 ** 6)   # acier : 7,85 kg/dm³ — déclaré
ECHELLE_PLAN = Fraction(1, 10)      # le SVG est coté au 1/10
NB_CRANS = 43                        # crans 0 à 42 : le 42ᵉ est le dernier avant le clampage
DEC_THEOREME = 5                     # encadrement publié par CONTINUITE
DEC_PLANS = 15                       # encadrement nécessaire pour coter le plan
PORTEE_MM = Fraction(700)            # allonge d'une main — déclaré
SAISIE_MIN_MM = Fraction(100)        # ce qu'un pouce et un index saisissent — déclaré
PORTAGE_UN_KG = Fraction(25)         # porté par une personne — déclaré

OUTILS: List[Tuple[str, Fraction, Fraction]] = [
    ("scie à ruban", Fraction(1, 2), Fraction(1, 4)),
    ("dégauchisseuse-rabot", Fraction(1, 10), Fraction(1, 2)),
    ("fraiseuse verticale", Fraction(2, 100), Fraction(1)),
    ("rectifieuse", Fraction(5, 1000), Fraction(2)),
]

COULEURS = ("#0f1c2b", "#1c3550", "#2f5f86", "#4d87b0", "#7fb2d6")

# ─── 3. Arithmétique exacte : rien ne passe par un flottant -------------------


def _decimale(v: Fraction, decimales: int) -> str:
    """Écriture décimale exacte d'un rationnel, arrondi half-up par des entiers."""
    signe = "-" if v < 0 else ""
    v = abs(v)
    m = 10 ** decimales
    n = (v * m + Fraction(1, 2)) // 1
    return f"{signe}{n // m}.{n % m:0{decimales}d}"


def _fraction(texte: str) -> Fraction:
    a, _, b = texte.partition("/")
    return Fraction(int(a), int(b)) if b else Fraction(a)


def _graine(nom: str) -> Fraction:
    """La semence rationnelle telle que CONTINUITE l'écrit : importée, jamais recopiée ici."""
    return next(v for n, v, _ in CONT.FICHES_SEMENCES if n == nom)


MIZAN = _graine("MIZAN")
LIGNE_REF = _graine("LIGNE_REF")


def _rho_entiers(decimales: int) -> Tuple[int, int, int]:
    """(a, a+1, 10^n) avec (a/10^n)^12 < 249/400 ≤ ((a+1)/10^n)^12 — entiers uniquement.

    (a/10^n)^12 < 249/400 équivaut à a^12·400 < 249·10^(12n) : la bissection ne compare que des
    entiers, aucun logarithme ni racine n'entre dans les bornes."""
    m = 10 ** decimales
    cible = 249 * m ** 12
    bas, haut = 0, m
    while bas + 1 < haut:
        milieu = (bas + haut) // 2
        if pow(milieu, 12) * 400 < cible:
            bas = milieu
        else:
            haut = milieu
    return bas, haut, m


def rho_encadre(decimales: int) -> Tuple[Fraction, Fraction]:
    """Les deux bornes rationnelles de ρ au dixième de 10^-decimales."""
    bas, haut, m = _rho_entiers(decimales)
    return Fraction(bas, m), Fraction(haut, m)


def _tick_le_plus_proche(v: Fraction) -> Fraction:
    """Le multiple de 0,01 mm le plus proche de v (demi-écart vers le haut), par des entiers."""
    return (v / PAS_AFFICHAGE + Fraction(1, 2)) // 1 * PAS_AFFICHAGE


def _tick_unique(bas: Fraction, haut: Fraction) -> Optional[Fraction]:
    """La cote que l'intervalle désigne sans ambiguïté : les deux bouts arrondis au même tick."""
    b, h = _tick_le_plus_proche(bas), _tick_le_plus_proche(haut)
    return b if b == h else None


def _intervalle_cran(k: int, bas_rho: Fraction, haut_rho: Fraction,
                     c_min: Fraction) -> Tuple[Fraction, Fraction, Optional[Fraction]]:
    """(borne basse, borne haute, cote cotable) du cran k — la même écriture partout."""
    b = max(c_min, CADRE_MM * MIZAN * bas_rho ** k)
    h = max(c_min, CADRE_MM * MIZAN * haut_rho ** k)
    return b, h, _tick_unique(b, h)


_CONT: Dict[str, Any] = {}


def continuite_cert() -> Dict[str, Any]:
    """Le certificat de CONTINUITE, lu une seule fois : sa déterminisation est prouvée là-bas."""
    if "cert" not in _CONT:
        _CONT["cert"] = CONT.certificat()
    return _CONT["cert"]


# ─── 4. Les mesures de la couche ---------------------------------------------


def semences() -> Dict[str, Any]:
    mizan, ref = MIZAN, LIGNE_REF
    pub = continuite_cert()["rho"]
    b5, h5, m5 = _rho_entiers(DEC_THEOREME)
    b15, h15, m15 = _rho_entiers(DEC_PLANS)
    return {
        "domaine_D": {"borne_basse": f"{ref.numerator}/{ref.denominator}",
                      "borne_haute": f"{mizan.numerator}/{mizan.denominator}"},
        "rho_publie_par_continuite": {"inferieur": pub["inferieur"],
                                      "superieur": pub["superieur"]},
        "encadrement_theoreme": {"decimales": DEC_THEOREME,
                                 "inferieur": f"{b5}/{m5}", "superieur": f"{h5}/{m5}",
                                 "largeur": f"1/{m5}"},
        "encadrement_plans": {"decimales": DEC_PLANS,
                              "inferieur": f"{b15}/{m15}", "superieur": f"{h15}/{m15}",
                              "largeur": f"1/{m15}"},
        "concorde_avec_continuite": (f"{b5}/{m5}" == pub["inferieur"]
                                     and f"{h5}/{m5}" == pub["superieur"]),
        "cadre_mm": f"{CADRE_MM.numerator}/{CADRE_MM.denominator}",
        "eps_a_declaree": f"{EPS_TOL.numerator}/{EPS_TOL.denominator}",
        "cote_clampee_mm": _decimale(CADRE_MM * ref, 2),
    }


def crans() -> Dict[str, Any]:
    """Les 43 plateaux : cote, bornes, tolérance, masse — tout en fractions exactes."""
    bas_rho, haut_rho = rho_encadre(DEC_PLANS)
    c_min = CADRE_MM * LIGNE_REF
    # la position du clamp n'est pas recalculée ici : elle est lue dans la preuve entière de
    # CONTINUITE (sortie_de_D = « MIZAN·ρ^k < LIGNE_REF », comparé par des entiers seuls)
    sortie = {r["k"]: bool(r["sortie_de_D"]) for r in continuite_cert()["chaine"]["table"]}
    table: List[Dict[str, Any]] = []
    indeterminees = 0
    surface = Fraction(0)
    for k in range(NB_CRANS):
        b, h, c = _intervalle_cran(k, bas_rho, haut_rho, c_min)
        ambigue = c is None
        if ambigue:
            indeterminees += 1
            c = _tick_le_plus_proche((b + h) / 2)    # à défaut : le tick du milieu de la plage
        t = c * EPS_TOL
        masse = c * c * EPAISSEUR_MM * MASSE_VOL_KG_MM3
        surface += c * c
        table.append({
            "cran": k,
            "cote_mm": _decimale(c, 2),
            "borne_basse_mm": _decimale(b, 6),
            "borne_haute_mm": _decimale(h, 6),
            "largeur_mm": _decimale(h - b, 12),
            "clamp": sortie.get(k, False),
            "indeterminee": ambigue,
            "tolerance_mm": _decimale(t, 5),
            "masse_kg": _decimale(masse, 3),
            "cote_exacte": c,
            "tolerance_exacte": t,
            "masse_exacte": masse,
        })
    un_sur_rho = (Fraction(1) / haut_rho, Fraction(1) / bas_rho)   # (basse, haute) de 1/ρ
    # les cotes écrites sont des ticks : chacune porte ± un demi-tick. La plage acceptée pour le
    # rapport de deux ticks consécutifs est donc 1/ρ élargi de r·(d/a + d/b) — sinon la
    # quantification du plan elle-même ferait sortir les 42 rapports, et le clamp deviendrait
    # invisible dans ce qu'il est censé isoler.
    demi_tick = PAS_AFFICHAGE / 2
    rapports: List[Dict[str, Any]] = []
    for k in range(1, NB_CRANS):
        a, b = table[k - 1]["cote_exacte"], table[k]["cote_exacte"]
        r = a / b
        marge = r * (demi_tick / a + demi_tick / b)
        bande = (un_sur_rho[0] - marge, un_sur_rho[1] + marge)
        dans = bande[0] <= r <= bande[1]
        ecart = Fraction(0) if dans else min(abs(r - bande[0]), abs(r - bande[1]))
        rapports.append({"k": k, "rapport": _decimale(r, 6),
                         "plage_acceptee": f"{_decimale(bande[0], 6)}–{_decimale(bande[1], 6)}",
                         "marge_de_quantification": _decimale(marge, 8),
                         "dans_la_plage_de_1_sur_rho": bool(dans),
                         "ecart_a_la_plage": _decimale(ecart, 6)})
    hors = [x["k"] for x in rapports if not x["dans_la_plage_de_1_sur_rho"]]
    return {
        "nb_crans": NB_CRANS,
        "table": table,
        "cotes_indeterminees": indeterminees,
        "premier_clampe": [x["cran"] for x in table if x["clamp"]][:1],
        "surface_total_mm2": _decimale(surface, 1),
        "masse_totale_kg": _decimale(sum(x["masse_exacte"] for x in table), 3),
        "invariance": {"nom": "1/ρ", "inferieur": _decimale(un_sur_rho[0], 6),
                       "superieur": _decimale(un_sur_rho[1], 6)},
        "rapports_consecutifs": rapports,
        "rapports_hors_plage": hors,
        "reglage_de_la_plage": "la plage est 1/ρ élargi du demi-tick porté par chacune des deux "
                               "cotes : c'est la quantification du plan, pas ρ, qui fixe cette "
                               "marge",
        "ecart_max_a_la_plage": _decimale(max(
            (_fraction(x["ecart_a_la_plage"]) for x in rapports), default=Fraction(0)), 6),
    }


def cascade() -> Dict[str, Any]:
    """Le facteur 1/(1−ρ²) encadré, et ce que la troncature au cran 42 laisse dehors."""
    bas_rho, haut_rho = rho_encadre(DEC_PLANS)
    f_bas = 1 / (1 - bas_rho ** 2)             # ρ croissant, le facteur aussi
    f_haut = 1 / (1 - haut_rho ** 2)
    p_bas = sum(bas_rho ** (2 * j) for j in range(NB_CRANS))
    p_haut = sum(haut_rho ** (2 * j) for j in range(NB_CRANS))
    r_bas, r_haut = f_bas - p_bas, f_haut - p_haut
    return {
        "formule": "facteur = Σ ρ^(2j) = 1/(1−ρ²) pour la pile infinie, aire au carré de la cote",
        "monotone": "les trois grandeurs sont croissantes en ρ : les bornes se prennent aux "
                    "bornes de l'encadrement, dans le même ordre",
        "facteur_infini": {"inferieur": _decimale(f_bas, 4), "superieur": _decimale(f_haut, 4),
                           "largeur": _decimale(f_haut - f_bas, 10)},
        "facteur_43_crans": {"inferieur": _decimale(p_bas, 4),
                             "superieur": _decimale(p_haut, 4)},
        "reste_de_la_troncature": {"inferieur": _decimale(r_bas, 4),
                                   "superieur": _decimale(r_haut, 4)},
        "part_hors_des_43_crans": _decimale(r_bas / f_bas * 100, 2),
        "identite_partielle": bool(p_bas + r_bas == f_bas and p_haut + r_haut == f_haut),
        "encadrement_valide": bool(f_bas < f_haut and p_bas < p_haut and r_bas > 0
                                   and p_bas < f_bas and r_bas < f_bas),
        "aire_tete_mm2": _decimale(Fraction(6225, 10) ** 2, 1),
    }


def outil_pour(tolerance: Fraction) -> Optional[Tuple[str, Fraction, Fraction]]:
    """Le plus grossier des outils déclarés dont la capacité tient sous la tolérance."""
    for nom, capacite, heures in OUTILS:
        if capacite <= tolerance:
            return nom, capacite, heures
    return None


def outillage() -> Dict[str, Any]:
    tables = crans()["table"]
    rangs: Dict[str, int] = {}
    par_cran: List[Dict[str, Any]] = []
    hors_ligne = 0
    tol = [x["tolerance_exacte"] for x in tables]
    for x in tables:
        choix = outil_pour(x["tolerance_exacte"])
        if choix is None:
            hors_ligne += 1
            nom = "aucun outil déclaré"
        else:
            nom = choix[0]
        rangs[nom] = rangs.get(nom, 0) + 1
        par_cran.append({"cran": x["cran"], "tolerance_mm": x["tolerance_mm"],
                         "outil_declare": nom})
    return {"ladder": [{"outil": n, "capacite_mm": _decimale(c, 3),
                        "heures": _decimale(h, 2)} for n, c, h in OUTILS],
            "repartition": rangs, "hors_ligne": hors_ligne,
            "outils_utilises": len(rangs), "par_cran": par_cran,
            "le_plus_fin_mm": _decimale(min(tol), 5),
            "le_plus_large_mm": _decimale(max(tol), 5)}


def cout() -> Dict[str, Any]:
    tables = crans()["table"]
    par_cran: List[Dict[str, Any]] = []
    total = Fraction(0)
    for x in tables:
        choix = outil_pour(x["tolerance_exacte"])
        heures = choix[2] if choix else Fraction(0)
        total += heures
        par_cran.append({"cran": x["cran"], "heures_declarees": _decimale(heures, 2)})
    return {"total_heures": _decimale(total, 2),
            "moyenne_par_cran": _decimale(total / NB_CRANS, 4),
            "par_cran": par_cran, "total_exact": total,
            "somme_des_lignes": sum(_fraction(p["heures_declarees"]) for p in par_cran)}


def echelle_humaine() -> Dict[str, Any]:
    tables = crans()["table"]
    cotes = [_fraction(x["cote_mm"]) for x in tables]
    masses = [_fraction(x["masse_kg"]) for x in tables]
    return {"cote_max_mm": _decimale(max(cotes), 2), "cote_min_mm": _decimale(min(cotes), 2),
            "portee_declaree_mm": _decimale(PORTEE_MM, 0),
            "saisie_min_declaree_mm": _decimale(SAISIE_MIN_MM, 0),
            "toutes_dans_le_geste": max(cotes) <= PORTEE_MM and min(cotes) >= SAISIE_MIN_MM,
            "masse_tete_kg": _decimale(max(masses), 3),
            "masse_totale_kg": _decimale(sum(masses), 3),
            "portage_un_kg": _decimale(PORTAGE_UN_KG, 0),
            "tete_portable_par_un": max(masses) <= PORTAGE_UN_KG,
            "pile_portable_par_un": sum(masses) <= PORTAGE_UN_KG,
            "crans_portables_seuls": sum(1 for m in masses if m <= PORTAGE_UN_KG),
            "nb_crans": len(tables)}


def predictions() -> Dict[str, Any]:
    """Ce qui serait faux si l'objet était construit et mésuré — la partie réfutable."""
    tables = crans()["table"]
    ca, cr = cascade(), crans()
    tete, fin = tables[0], tables[-1]
    hauteur_pile = sum(x["cote_exacte"] for x in tables)
    liste = [
        {"id": "P1", "grandeur": "cote usinée du cran 0", "unite": "mm",
         "prevue": f"{tete['cote_mm']} ± {tete['tolerance_mm']}",
         "instrument": "pied à coulisse 0,01 mm",
         "refutation": "une mesure hors de l'intervalle réfute le plan de ce cran",
         "mesure": None},
        {"id": "P2", "grandeur": "rapport de deux cotes consécutives avant le clampage",
         "unite": "sans",
         "prevue": f"entre {cr['invariance']['inferieur']} et "
                   f"{cr['invariance']['superieur']}",
         "instrument": "pied à coulisse 0,01 mm sur deux plateaux",
         "refutation": "un rapport stablement hors de cette plage réfute la contraction dans "
                       "l'objet, pas seulement dans le calcul",
         "mesure": None},
        {"id": "P3", "grandeur": "masse du cran 0", "unite": "kg",
         "prevue": f"{tete['masse_kg']} ± 0,5 %",
         "instrument": "balance d'atelier",
         "refutation": "une masse hors de la bande réfute l'épaisseur ou l'acier déclarés",
         "mesure": None},
        {"id": "P4", "grandeur": "cote des crans au-delà du 42ᵉ", "unite": "mm",
         "prevue": f"{fin['cote_mm']} exactement (clamp)",
         "instrument": "règle",
         "refutation": "un plateau qui continue de rétrécir au-delà du 42ᵉ cran réfute la "
                       "déclaration de domaine, pas le calcul",
         "mesure": None},
        {"id": "P5", "grandeur": "cumul des tolérances des 43 plateaux", "unite": "mm",
         "prevue": f"= {_decimale(sum(x['tolerance_exacte'] for x in tables), 3)}, soit ε_a fois "
                   f"la hauteur nominale {_decimale(hauteur_pile, 2)} mm",
         "instrument": "compareur",
         "refutation": "un cumul d'erreurs supérieur à ε_a fois la hauteur nominale réfute le "
                       "budget d'erreur déclaré",
         "mesure": None},
        {"id": "P6", "grandeur": "matière laissée dehors par la troncature aux 43 crans",
         "unite": "%",
         "prevue": f"{ca['part_hors_des_43_crans']} % de la pile infinie",
         "instrument": "balance d'atelier",
         "refutation": "une masse des 43 crans qui atteindrait la limite théorique montre que "
                       "la troncature est mal comptée",
         "mesure": None},
    ]
    instruments = sorted({p["instrument"] for p in liste})
    return {"liste": liste, "nb": len(liste),
            "aucune_mesure_effectuee": all(p["mesure"] is None for p in liste),
            "instruments": instruments,
            "au_moins_un_à_main": any("pied à coulisse" in p["instrument"] for p in liste),
            "champs_attendus": ["id", "grandeur", "unite", "prevue", "instrument",
                                "refutation", "mesure"]}


def prototypes() -> Dict[str, Any]:
    vues = sorted(p.relative_to(RACINE).as_posix() for p in PROTOTYPES.rglob("*")
                  if p.is_file()) if PROTOTYPES.exists() else []
    return {"repertoire": PROTOTYPES.relative_to(RACINE).as_posix(),
            "repertoire_existe": PROTOTYPES.exists(), "fichiers": vues,
            "nb_prototypes": len(vues),
            "enonce": "aucun prototype construit : la couche décrit ce qu'il faudrait usiner, "
                      "elle n'a usiné ni mésuré aucun objet"}


def sensibilite() -> Dict[str, Any]:
    """Le même calcul avec l'encadrement du théorème (5 décimales) puis celui du plan (15)."""
    c_min = CADRE_MM * LIGNE_REF
    rendu: Dict[str, Any] = {}
    for nom, dec in (("theoreme_5_decimales", DEC_THEOREME), ("plans_15_decimales", DEC_PLANS)):
        bas_rho, haut_rho = rho_encadre(dec)
        inde, premier = 0, None
        for k in range(NB_CRANS):
            b, h, c = _intervalle_cran(k, bas_rho, haut_rho, c_min)
            if c is None:
                inde += 1
                if premier is None:
                    premier = k
        rendu[nom] = {"crans_indetermines": inde, "premier_cran_indetermine": premier,
                      "largeur_encadrement": _decimale(haut_rho - bas_rho, dec)}
    rendu["ecart"] = (rendu["theoreme_5_decimales"]["crans_indetermines"]
                      - rendu["plans_15_decimales"]["crans_indetermines"])
    rendu["enonce"] = ("l'encadrement publié par le théorème ne suffit pas pour coter un plan : "
                       "c'est le nombre de crans rendus indéterminés qui le dit")
    return rendu


DEMI_DERNIER_CHIFFRE = Fraction(5, 10 ** 9)   # le catalogue écrit ses échelles à 8 décimales


def borne_propagee_ecriture() -> Fraction:
    """Ce que l'arrondi de stockage seul peut faire dériver un rapport de deux échelles.

    |ê_{k+1}/ê_k − e_{k+1}/e_k| ≤ δ·(1/LIGNE_REF + MIZAN/LIGNE_REF²) avec δ la moitié du dernier
    chiffre écrit : aucune échelle du catalogue n'est sous LIGNE_REF et aucune ne dépasse MIZAN."""
    return DEMI_DERNIER_CHIFFRE * (1 / LIGNE_REF + MIZAN / LIGNE_REF ** 2)


def lien_catalogue() -> Dict[str, Any]:
    cat = continuite_cert()["catalogue"]
    bas_rho, haut_rho = rho_encadre(DEC_PLANS)
    min_c = Fraction(cat["rapports_consecutifs_min"])
    max_c = Fraction(cat["rapports_consecutifs_max"])
    borne = borne_propagee_ecriture()
    hors = max(Fraction(0), bas_rho - min_c, max_c - haut_rho)
    return {"rapports_catalogue": {"min": cat["rapports_consecutifs_min"],
                                   "max": cat["rapports_consecutifs_max"]},
            "rho_exact_continuite": cat["rho_exact"],
            "derive_maximale": cat["derive_maximale"],
            "demi_dernier_chiffre": f"{DEMI_DERNIER_CHIFFRE.numerator}/"
                                    f"{DEMI_DERNIER_CHIFFRE.denominator}",
            "borne_propagee": _decimale(borne, 12),
            "ecart_hors_borne_plan": _decimale(hors, 12),
            "catalogue_sous_la_borne_ecriture": bool(hors <= borne),
            "part_de_la_borne": _decimale(hors / borne * 100, 2),
            "plan_plus_fin_que_ecriture": bool((haut_rho - bas_rho) < borne),
            "rapport_des_finesses": _decimale(borne / (haut_rho - bas_rho), 0),
            "nb_formes_catalogue": len(EXT.LES_27_FORMES_ETENDUES),
            "invariance_plan": _decimale(Fraction(1) / bas_rho, 6)}


def limites_ouvertes() -> Dict[str, Any]:
    liste = [
        "aucun prototype : rien n'a été usiné, par conséquent aucune des six prédictions n'a "
        "été ni confirmée ni réfutée",
        "les capacités d'outil (0,5 mm à 0,005 mm) sont des ordres de grandeur déclarés : "
        "aucune machine du commerce n'a été mesurée ici",
        "la tolérance relative ε_a = 1/1000 est un choix d'auteur : le dépôt ne contient "
        "aucun instrument qui l'ait vérifiée",
        "le clampage au-delà du cran 42 est une déclaration de domaine, pas une propriété des "
        "plaques : la nature n'est pas engagée",
        "le facteur 13,1645 ne vaut que pour une similitude d'aire au carré de la cote : une "
        "autre géométrie donne un autre facteur",
    ]
    return {"liste": liste, "nb": len(liste), "remplies_dans_ce_lot": 0,
            "toutes_au_dela_de_20": all(len(l) > 20 for l in liste)}


# ─── 5. Artefacts : écriture, puis relecture du même fichier ------------------

COLONNES = ["cran", "cote_nominale_mm", "resolution_plan_mm", "borne_basse_mm",
            "borne_haute_mm", "largeur_encadrement_mm", "clamp", "tolerance_mm",
            "outil_declare", "heures_declarees", "masse_kg", "statut_construction",
            "predicat_associe"]


def _lignes_nomenclature(cert: Dict[str, Any]) -> List[List[str]]:
    t = cert["crans"]["table"]
    ou = {x["cran"]: x["outil_declare"] for x in cert["outillage"]["par_cran"]}
    he = {x["cran"]: x["heures_declarees"] for x in cert["cout"]["par_cran"]}
    lignes = [COLONNES]
    for x in t:
        lignes.append([str(x["cran"]), x["cote_mm"], _decimale(PAS_AFFICHAGE, 2),
                       x["borne_basse_mm"], x["borne_haute_mm"], x["largeur_mm"],
                       "OUI" if x["clamp"] else "NON", x["tolerance_mm"],
                       ou.get(x["cran"], ""), he.get(x["cran"], ""), x["masse_kg"],
                       PHRASE_ABSENCE,
                       "P1" if x["cran"] == 0 else ("P4" if x["clamp"] else "P2")])
    lignes.append(["total", "", "", "", "", "", "", "", "", cert["cout"]["total_heures"],
                   cert["crans"]["masse_totale_kg"], PHRASE_ABSENCE, "P6"])
    return lignes


def octets_csv(cert: Dict[str, Any]) -> bytes:
    corps = "\r\n".join(";".join(c.replace(".", ",") for c in ligne)
                        for ligne in _lignes_nomenclature(cert))
    return b"\xef\xbb\xbf" + (corps + "\r\n").encode("utf-8")


def octets_svg(cert: Dict[str, Any]) -> bytes:
    t = cert["crans"]["table"]
    bord, pas_texte = 20, 5
    cotes = [_fraction(x["cote_mm"]) for x in t]
    dessin = max(cotes) * ECHELLE_PLAN
    largeur = _decimale(dessin + 2 * bord, 2)
    hauteur = _decimale(dessin + 3 * bord + pas_texte * len(t), 2)
    pieces: List[str] = []
    for i, x in enumerate(t):
        c = _decimale(_fraction(x["cote_mm"]) * ECHELLE_PLAN, 2)
        pieces.append(
            f'<rect x="{bord}" y="{bord}" width="{c}" height="{c}" fill="none" '
            f'stroke="{COULEURS[i % len(COULEURS)]}" stroke-width="0.4" '
            f'data-cran="{x["cran"]}" data-cote-mm="{x["cote_mm"]}"/>')
    depart = dessin + 2 * bord
    cotations = "".join(
        f'<text x="{bord}" y="{_decimale(depart + pas_texte * i, 2)}">'
        f'cran {x["cran"]} : {x["cote_mm"]} mm ± {x["tolerance_mm"]} — {PHRASE_ABSENCE}'
        f'</text>'
        for i, x in enumerate(t))
    tete, fin = t[0], t[-1]
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{largeur}" height="{hauteur}" '
        f'viewBox="0 0 {largeur} {hauteur}">\n'
        f'<title>CONSTRUCTION — pile de {NB_CRANS} plateaux carrés emboîtés, échelle '
        f'1:{int(1 / ECHELLE_PLAN)}</title>\n'
        f'<desc>Cote du premier plateau : {tete["cote_mm"]} mm. Cote clampee : '
        f'{fin["cote_mm"]} mm. {PHRASE_ABSENCE}.</desc>\n'
        + "\n".join(pieces) + "\n" + cotations + "\n</svg>\n").encode("utf-8")


def octets_predictions_md(cert: Dict[str, Any]) -> bytes:
    p = cert["predictions"]
    lignes = [
        f"# CONSTRUCTION — {p['nb']} prédictions réfutables, {PHRASE_ABSENCE}",
        "",
        f"- Cote du cran 0 : **{cert['crans']['table'][0]['cote_mm']} mm** ; cran 42 : "
        f"**{cert['crans']['table'][-1]['cote_mm']} mm**.",
        f"- Facteur de cascade 1/(1−ρ²) : "
        f"**{cert['cascade']['facteur_infini']['inferieur']} à "
        f"{cert['cascade']['facteur_infini']['superieur']}** ; les {NB_CRANS} crans en laissent "
        f"dehors **{cert['cascade']['part_hors_des_43_crans']} %**.",
        f"- Masse des {NB_CRANS} crans : **{cert['crans']['masse_totale_kg']} kg** pour un cadre "
        f"de {PORTEE_MM} mm de portée.",
        "",
        "| id | grandeur | unité | prévu | instrument | ce qui la réfuterait | mesure |",
        "|---|---|---|---|---|---|---|",
    ]
    for x in p["liste"]:
        lignes.append(f"| {x['id']} | {x['grandeur']} | {x['unite']} | {x['prevue']} | "
                      f"{x['instrument']} | {x['refutation']} | "
                      f"{'aucune' if x['mesure'] is None else x['mesure']} |")
    lignes += ["", "## Limites ouvertes", ""]
    lignes += [f"- {l}" for l in cert["limites_ouvertes"]["liste"]]
    lignes += ["", f"**{PHRASE_ABSENCE}** : aucune ligne de ce tableau n'a été remplie par une "
                   "mesure, et ce dossier ne prétend rien d'aucun objet réel."]
    return ("\r\n".join(lignes) + "\r\n").encode("utf-8")


def octets_json(cert: Dict[str, Any]) -> bytes:
    return (json.dumps(cert, ensure_ascii=False, indent=2, sort_keys=True,
                       default=str) + "\n").encode("utf-8")


def _artefacts_octets(cert: Dict[str, Any]) -> Dict[str, bytes]:
    return {"certificat.json": octets_json(cert),
            "nomenclature_crans.csv": octets_csv(cert),
            "plan_emboitement.svg": octets_svg(cert),
            "predictions_falsifiables.md": octets_predictions_md(cert)}


def nomenclature(cert: Dict[str, Any]) -> Dict[str, Any]:
    """Re-lecture des octets du CSV : l'instrument, c'est le fichier que le dossier écrit."""
    octets = octets_csv(cert)
    texte = octets.decode("utf-8-sig")
    lignes = [l.split(";") for l in texte.split("\r\n") if l]
    par_cran = {l[0]: l for l in lignes[1:-1]}
    total = lignes[-1]
    masses = sum(_fraction(l[10].replace(",", ".")) for l in lignes[1:-1])
    heures = sum(_fraction(l[9].replace(",", ".")) for l in lignes[1:-1])
    t = cert["crans"]["table"]
    coincide = (len(par_cran) == NB_CRANS
                and all(_fraction(par_cran[str(x["cran"])][1].replace(",", "."))
                        == _fraction(x["cote_mm"]) for x in t))
    return {"chemin": "CONSTRUCTION/artefacts/nomenclature_crans.csv",
            "octets": len(octets), "lignes": len(lignes), "colonnes": len(lignes[0]),
            "bom": octets[:3] == b"\xef\xbb\xbf", "separateur": ";",
            "crlf": octets.count(b"\r\n") == len(lignes),
            "crans_relus": len(par_cran), "cotes_identiques_au_calcul": coincide,
            "masse_reluee_kg": _decimale(masses, 3), "heures_relues": _decimale(heures, 2),
            "total_declare": total[9] + ";" + total[10],
            "absence_ecrite": all(l[11].replace("\ufeff", "") == PHRASE_ABSENCE
                                  for l in lignes[1:])}


def plans(cert: Dict[str, Any]) -> Dict[str, Any]:
    octets = octets_svg(cert)
    texte = octets.decode("utf-8")
    largeurs = [m.split('width="')[1].split('"')[0]
                for m in texte.split("<rect ")[1:]]
    attendues = [_decimale(_fraction(x["cote_mm"]) * ECHELLE_PLAN, 2)
                 for x in cert["crans"]["table"]]
    return {"chemin": "CONSTRUCTION/artefacts/plan_emboitement.svg",
            "octets": len(octets), "rectangles": len(largeurs),
            "largeurs_conformes": largeurs == attendues,
            "largeur_attendue_premiere": attendues[0],
            "largeur_relevee_premiere": largeurs[0] if largeurs else "",
            "echelle": f"1:{int(1 / ECHELLE_PLAN)}",
            "cotes_escrites": texte.count("mm ±"),
            "absence_ecrite": PHRASE_ABSENCE in texte}


def ecritures(cert: Dict[str, Any]) -> Dict[str, Any]:
    rendu = {nom: octets for nom, octets in _artefacts_octets(cert).items()}
    # certificat.json contient ce nœud : sa taille et son empreinte ne peuvent pas être scellées
    # par lui-même. Les mesurer ici écrirait un nombre que le fichier publié ne vérifie pas.
    hors_boucle = {nom: octets for nom, octets in rendu.items() if nom != "certificat.json"}
    return {"noms": sorted(rendu),
            "tailles": {nom: len(oct) for nom, oct in sorted(hors_boucle.items())},
            "empreintes": {nom: hashlib.sha256(oct).hexdigest()[:16]
                           for nom, oct in sorted(hors_boucle.items())},
            "auto_reference": "certificat.json porte ce nœud : sa taille sur disque n'est pas "
                              "mesurée ici, seul ce qui l'entoure l'est",
            "absence_partout": all(PHRASE_ABSENCE.encode("utf-8") in oct
                                   for oct in rendu.values()),
            "nom_sans_empreinte": "certificat.json"}


# ─── 6. Équations et contrôles ------------------------------------------------

NOEUDS: Dict[str, Dict[str, Any]] = {
    "EQ-01": {"depend": [], "externe": ["CONTINUITE/continuite_base.py"]},
    "EQ-02": {"depend": ["EQ-01"], "externe": []},
    "EQ-03": {"depend": ["EQ-02"], "externe": ["bibliotheques/lib_almizan_extension.py"]},
    "EQ-04": {"depend": ["EQ-02"], "externe": []},
    "EQ-05": {"depend": ["EQ-01"], "externe": []},
    "EQ-06": {"depend": ["EQ-02"], "externe": []},
    "EQ-07": {"depend": ["EQ-06"], "externe": []},
    "EQ-08": {"depend": ["EQ-02"], "externe": []},
    "EQ-09": {"depend": ["EQ-04"], "externe": []},
    "EQ-10": {"depend": ["EQ-09"], "externe": []},
    "EQ-11": {"depend": ["EQ-02", "EQ-05"], "externe": []},
    "EQ-12": {"depend": ["EQ-06", "EQ-07"], "externe": []},
    "EQ-13": {"depend": ["EQ-01", "EQ-02"], "externe": []},
    "EQ-14": {"depend": ["EQ-01"], "externe": ["CONTINUITE/continuite_base.py"]},
    "EQ-15": {"depend": [], "externe": []},
    "EQ-16": {"depend": ["EQ-11", "EQ-12"], "externe": []},
}


def _eq(id_: str, chemin: str, formule: str, resultat: str, statut: str,
        limite: str, detail: Any, couche: str = "S2 REGULARITE") -> Dict[str, Any]:
    n = NOEUDS[id_]
    return {"id": id_, "chemin": chemin, "formule": formule, "resultat": resultat,
            "statut": statut, "limite": limite, "detail": detail, "couche": couche,
            "piliers": ["P1 UNITE", "P2 BORNE", "P3 CONFRONTATION", "P4 TRANSMISSION"],
            "depend_de": n["depend"], "fonde_hors_du_dossier": n["externe"]}


def equations(etat: Dict[str, Any]) -> List[Dict[str, Any]]:
    se, cr, ca = etat["semences"], etat["crans"], etat["cascade"]
    ou, co, eh = etat["outillage"], etat["cout"], etat["echelle_humaine"]
    pr, pro, sen = etat["predictions"], etat["prototypes"], etat["sensibilite"]
    li, lo = etat["lien_catalogue"], etat["limites_ouvertes"]
    no, pl, ec = etat["nomenclature"], etat["plans"], etat["ecritures"]
    return [
        _eq("EQ-01", "construction_base.py → semences() → C01",
            "ρ = (249/400)^(1/12), encadré par bissection entière à 5 puis à 15 décimales",
            f"5 déc {se['encadrement_theoreme']['inferieur']}–"
            f"{se['encadrement_theoreme']['superieur']} · 15 déc "
            f"{se['encadrement_plans']['inferieur']}–{se['encadrement_plans']['superieur']} · "
            f"concorde CONTINUITE {se['concorde_avec_continuite']}", "OPÉRATIONNEL",
            "l'encadrement prouve une plage, pas une valeur : la cote imprimée est le tick "
            "unique de 0,01 mm tombé dans cette plage, et rien de plus", se),
        _eq("EQ-02", "construction_base.py → crans() → C02",
            "cote_k = max(1000·LIGNE_REF, 1000·MIZAN·ρ^k), cote écrite au multiple unique de "
            "0,01 mm de l'intervalle",
            f"{cr['nb_crans']} crans · {cr['cotes_indeterminees']} cote(s) indéterminée(s) · "
            f"cran 0 {cr['table'][0]['cote_mm']} mm · clamp dès le cran "
            f"{cr['premier_clampe']} · masse {cr['masse_totale_kg']} kg", "OPÉRATIONNEL",
            "le plan ne cote que ce que l'encadrement détermine : si deux ticks tombent dans "
            "la plage, la cote est marquée indéterminée au lieu d'être devinée", cr),
        _eq("EQ-03", "construction_base.py → crans() → C03",
            "le dernier cran libre est le 42ᵉ : au-delà, la cote est la borne basse déclarée, "
            "122,00 mm ; le rapport cesse d'être 1/ρ",
            f"rapport cran 0/cran 1 = {cr['rapports_consecutifs'][0]['rapport']} · 1/ρ ∈ "
            f"[{cr['invariance']['inferieur']} ; {cr['invariance']['superieur']}] · crans "
            f"clampeés {sum(1 for x in cr['table'] if x['clamp'])} · rapports hors plage "
            f"{cr['rapports_hors_plage']} · écart max {cr['ecart_max_a_la_plage']}",
            "SIMULÉ",
            "le clampage vient de la déclaration du domaine D dans lib_almizan_extension.py : "
            "ce n'est pas une propriété des plaques, c'est la règle du jeu écrite par l'auteur",
            cr),
        _eq("EQ-04", "construction_base.py → crans() → C04",
            "tolérance T_k = cote_k × ε_a avec ε_a = 1/1000 déclarée ; l'erreur cumulative de "
            "la pile vaut ε_a fois sa cote, pas davantage",
            f"T_0 {cr['table'][0]['tolerance_mm']} mm · T_42 "
            f"{cr['table'][-1]['tolerance_mm']} mm · ε_a {se['eps_a_declaree']} · "
            f"plus large {ou['le_plus_large_mm']} mm · plus fin {ou['le_plus_fin_mm']} mm",
            "SPÉCIFIÉ",
            "aucun instrument n'a vérifié ε_a : le budget d'erreur est une promesse d'auteur "
            "que la P1 et la P5 peuvent réfuter", {"eps_a": se["eps_a_declaree"],
                                                   "tol": [x["tolerance_mm"] for x in cr["table"]]}),
        _eq("EQ-05", "construction_base.py → cascade() → C05",
            "facteur de matière = Σ ρ^(2j) = 1/(1−ρ²) pour la pile infinie, encadré en "
            "rationnels",
            f"facteur {ca['facteur_infini']['inferieur']}–{ca['facteur_infini']['superieur']} · "
            f"43 crans {ca['facteur_43_crans']['inferieur']}–"
            f"{ca['facteur_43_crans']['superieur']} · hors troncature "
            f"{ca['part_hors_des_43_crans']} %", "SIMULÉ",
            "le facteur ne vaut que pour une similitude d'aire au carré de la cote : changer la "
            "géométrie du plateau change le facteur, pas ρ", ca),
        _eq("EQ-06", "construction_base.py → nomenclature() → C06",
            "nomenclature = 43 lignes + un total, relue dans les octets que ce module écrit",
            f"{no['crans_relus']} crans relus sur {no['lignes']} lignes · {no['colonnes']} "
            f"colonnes · BOM {no['bom']} · cotes identiques au "
            f"calcul {no['cotes_identiques_au_calcul']} · masse relue {no['masse_reluee_kg']} kg",
            "OPÉRATIONNEL",
            "le CSV est l'objet publié : le vérifier, c'est le relire tel qu'il sera lu, pas "
            "telle qu'on l'a calculé", no),
        _eq("EQ-07", "construction_base.py → plans() → C07",
            "largeur SVG = cote × échelle 1:10, recollée dans le fichier puis redécoupée",
            f"{pl['rectangles']} rectangles · conformes {pl['largeurs_conformes']} · "
            f"{pl['cotes_escrites']} cotes écrites sur {cr['nb_crans']} crans · échelle "
            f"{pl['echelle']} · {pl['octets']} octets", "OPÉRATIONNEL",
            "le plan n'est pas une image décorative : ses largeurs sont les cotes, et un rect "
            "qui ne retombe pas sur la cote rend le contrôle rouge", pl),
        _eq("EQ-08", "construction_base.py → echelle_humaine() → C08",
            "deux faits mesurés ensemble : toutes les cotes tiennent dans le geste, la masse "
            "totale ne se porte pas",
            f"cotes {eh['cote_min_mm']}–{eh['cote_max_mm']} mm pour une portée de "
            f"{eh['portee_declaree_mm']} mm · {eh['toutes_dans_le_geste']} · cran 0 "
            f"{eh['masse_tete_kg']} kg ({eh['tete_portable_par_un']}) · pile "
            f"{eh['masse_totale_kg']} kg ({eh['pile_portable_par_un']})", "OPÉRATIONNEL",
            "la portée et le portage sont déclarés en millimètres et en kilogrammes par "
            "l'auteur : aucun corps humain n'a été mesuré", eh),
        _eq("EQ-09", "construction_base.py → outil_pour() → outillage() → C09",
            "outil(k) = rang le plus grossier dont la capacité déclarée tient sous T_k",
            f"ladder {len(ou['ladder'])} outils · répartition {ou['repartition']} · "
            f"hors ligne {ou['hors_ligne']} · plus fin requis {ou['le_plus_fin_mm']} mm",
            "SPÉCIFIÉ",
            "les capacités sont des ordres de grandeur d'atelier déclarés : ce contrôle ne "
            "certifie aucune machine et n'a consulté aucun catalogue fournisseur", ou),
        _eq("EQ-10", "construction_base.py → outil_pour() → cout() → C10",
            "heures = Σ heures(outil(k)) ; le total est la somme des lignes, pas un nombre écrit",
            f"total {co['total_heures']} h pour {NB_CRANS} crans · moyenne "
            f"{co['moyenne_par_cran']} h · somme des lignes "
            f"{_decimale(co['somme_des_lignes'], 2)} h", "SPÉCIFIÉ",
            "les temps unitaires sont déclarés par outil : ils ne sortent d'aucun chantier et "
            "ne constituent pas un devis", co),
        _eq("EQ-11", "construction_base.py → predictions() → C11",
            "prédiction = grandeur + unité + bande + instrument + condition de réfutation, "
            "avec une mesure vide",
            f"{pr['nb']} prédictions · aucune mesure {pr['aucune_mesure_effectuee']} · "
            f"instruments {pr['instruments']} · au moins un à main {pr['au_moins_un_à_main']}",
            "SPÉCIFIÉ",
            "une prédiction n'est pas un résultat : tant que la colonne mesure est vide, "
            "rien de ce dossier n'est confirmé, et rien n'est non plus réfuté", pr),
        _eq("EQ-12", "construction_base.py → prototypes() → C12",
            "compter les prototypes sur disque et exiger la phrase d'absence dans les quatre "
            "artefacts",
            f"{pro['nb_prototypes']} prototype(s) · répertoire {pro['repertoire']} "
            f"({'existe' if pro['repertoire_existe'] else 'absent'}) · phrase partout "
            f"{ec['absence_partout']} · {ec['tailles']}", "OPÉRATIONNEL",
            "zéro prototype n'est pas un succès : c'est la raison pour laquelle la colonne "
            "mesure de EQ-11 reste vide", {**pro, "ecritures": ec}),
        _eq("EQ-13", "construction_base.py → sensibilite() → C13",
            "crans indéterminés selon la finesse de l'encadrement de ρ : 5 décimales contre 15",
            f"5 déc {sen['theoreme_5_decimales']['crans_indetermines']} indéterminés "
            f"(dès le cran {sen['theoreme_5_decimales']['premier_cran_indetermine']}) · "
            f"15 déc {sen['plans_15_decimales']['crans_indetermines']} · écart {sen['ecart']}",
            "OPÉRATIONNEL",
            "c'est l'instrument qu'on mesure ici, pas l'objet : la même cote change de statut "
            "selon la plage de ρ qu'on accepte d'utiliser", sen),
        _eq("EQ-14", "construction_base.py → lien_catalogue() → C14",
            "les rapports consécutifs du catalogue scellé restent à ρ moins la borne propagée "
            "de son seul arrondi d'écriture ; la plage du plan est plus fine que cette borne",
            f"catalogue {li['rapports_catalogue']['min'][:12]}–"
            f"{li['rapports_catalogue']['max'][:12]} · plage plans "
            f"{se['encadrement_plans']['inferieur']}–{se['encadrement_plans']['superieur']} · "
            f"hors borne {li['ecart_hors_borne_plan']} · propagée {li['borne_propagee']} · "
            f"dedans {li['catalogue_sous_la_borne_ecriture']} ({li['part_de_la_borne']} % de "
            f"la borne) · dérive max {li['derive_maximale']}", "OPÉRATIONNEL",
            "le catalogue est stocké arrondi : sa dérive est un défaut d'écriture du fichier, "
            "pas une divergence de la géométrie ; ce contrôle compare deux finesses de "
            "représentation, il ne dit rien d'un plateau usiné", li),
        _eq("EQ-15", "construction_base.py → noeuds_certificat() → C15",
            "deux exécutions des mêmes nœuds rendent le même octet",
            f"{etat['rejoue_identique']} · {etat['empreinte_execution'][:16]}…",
            "OPÉRATIONNEL",
            "le rejeu ne prouve que la déterminisme du calcul : il ne dit rien de la vérité "
            "des déclarations", {"empreinte": etat["empreinte_execution"],
                                 "identique": etat["rejoue_identique"]}),
        _eq("EQ-16", "construction_base.py → limites_ouvertes() → C16",
            "les limites que cette couche n'a pas remplies sont comptées et aucune n'est "
            "déclarée close",
            f"{lo['nb']} limites · remplies dans ce lot "
            f"{lo['remplies_dans_ce_lot']} · prototypes {pro['nb_prototypes']}", "OPÉRATIONNEL",
            "écrire une limite ne la franchit pas : la liste reste ouverte tant qu'un objet "
            "n'a pas été usiné et mesuré", lo, "S3 HORS_MATRICE"),
    ]


def controles(eqs: Dict[str, Any], etat: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []

    def ajouter(id_: str, nom: str, verifie: str, attendu: str, obtenu: str, ok: bool) -> None:
        out.append({"id": id_, "equation": f"EQ-{id_[1:]}", "nom": nom, "verifie": verifie,
                    "attendu": attendu, "obtenu": obtenu, "ok": bool(ok)})

    se, cr, ca = etat["semences"], etat["crans"], etat["cascade"]
    ou, co, eh = etat["outillage"], etat["cout"], etat["echelle_humaine"]
    pr, pro, sen = etat["predictions"], etat["prototypes"], etat["sensibilite"]
    li, lo = etat["lien_catalogue"], etat["limites_ouvertes"]
    no, pl, ec = etat["nomenclature"], etat["plans"], etat["ecritures"]
    n_star = continuite_cert()["chaine"]["pas_de_sortie"]
    # la concordance est re-tissée ici à partir des deux chaînes publiées de part et d'autre : si
    # l'une bouge sans l'autre, le contrôle rougit — la valeur booléenne seule ne suffit pas.
    ajouter("C01", "ρ est le rapport du théorème, pas un nombre inventé ici",
            "l'encadrement à 5 décimales redit celui de CONTINUITE et ρ < 1",
            f"{se['rho_publie_par_continuite']}",
            f"5 déc {se['encadrement_theoreme']['inferieur']}–"
            f"{se['encadrement_theoreme']['superieur']} · concordance "
            f"{se['concorde_avec_continuite']}",
            se["concorde_avec_continuite"]
            and se["encadrement_theoreme"]["inferieur"]
            == se["rho_publie_par_continuite"]["inferieur"]
            and se["encadrement_theoreme"]["superieur"]
            == se["rho_publie_par_continuite"]["superieur"]
            and _fraction(se["encadrement_plans"]["superieur"]) < 1)
    ajouter("C02", "chaque cote imprimée est déterminée par son encadrement",
            "zéro cote indéterminée sur 43 crans",
            f"{cr['nb_crans']} ticks uniques", f"{cr['cotes_indeterminees']} indéterminée(s) · "
            f"{cr['nb_crans']} crans cotés",
            cr["cotes_indeterminees"] == 0 and cr["nb_crans"] == NB_CRANS)
    ajouter("C03", "le clampage tombe exactement au pas démontré par CONTINUITE",
            f"le premier cran clampe est {n_star}, le théorème dit {n_star}, et le seul rapport "
            f"qui quitte la plage de 1/ρ est le sien",
            f"{n_star}",
            f"premier clampe {cr['premier_clampe']} · nombre de crans clampeés "
            f"{sum(1 for x in cr['table'] if x['clamp'])} · théorème {n_star} · rapports hors "
            f"plage {cr['rapports_hors_plage']}",
            cr["premier_clampe"] == [n_star] and n_star == 42
            and sum(1 for x in cr["table"] if x["clamp"]) == 1
            and cr["rapports_hors_plage"] == [n_star])
    ajouter("C04", "le budget d'erreur de la pile reste à ε_a fois la cote",
            "T_k = cote_k/1000 sur les 43 crans et ε_a sous 1/100",
            "43/43 égalités",
            f"écarts nuls {all(_fraction(x['tolerance_mm']) ==
                               _fraction(x['cote_mm']) * EPS_TOL for x in cr['table'])} · "
            f"ε_a {se['eps_a_declaree']}",
            all(_fraction(x["tolerance_mm"]) == _fraction(x["cote_mm"]) * EPS_TOL
                for x in cr["table"]))
    ajouter("C05", "le facteur de cascade est encadré et la troncature laisse un reste",
            "inférieur ≤ partiel ≤ supérieur, reste strictement positif et somme redite depuis "
            "les chaînes publiées",
            "encadrement valide",
            f"{ca['facteur_infini']['inferieur']} ≤ {ca['facteur_43_crans']['inferieur']} ≤ "
            f"{ca['facteur_infini']['superieur']} · reste hors 43 crans "
            f"{ca['part_hors_des_43_crans']} % · partiel+reste = "
            f"{_decimale(_fraction(ca['facteur_43_crans']['inferieur'])
                         + _fraction(ca['reste_de_la_troncature']['inferieur']), 4)}",
            ca["encadrement_valide"]
            and _fraction(ca["facteur_43_crans"]["inferieur"])
            + _fraction(ca["reste_de_la_troncature"]["inferieur"])
            == _fraction(ca["facteur_infini"]["inferieur"])
            and _fraction(ca["reste_de_la_troncature"]["inferieur"]) > 0
            and _fraction(ca["facteur_43_crans"]["inferieur"])
            <= _fraction(ca["facteur_infini"]["superieur"]))
    ajouter("C06", "la nomenclature relue vaut le calcul",
            "43 lignes + total, cotes égales au calcul, BOM et CRLF",
            f"{NB_CRANS} crans relus",
            f"{no['crans_relus']} · {no['colonnes']} colonnes · BOM {no['bom']} · "
            f"CRLF {no['crlf']} · cotes {no['cotes_identiques_au_calcul']}",
            no["crans_relus"] == NB_CRANS and no["bom"] and no["crlf"]
            and no["cotes_identiques_au_calcul"] and no["absence_ecrite"])
    ajouter("C07", "les largeurs du SVG sont les cotes à l'échelle",
            "un rectangle par cran, largeurs égales aux cotes multipliées par 1/10",
            f"{NB_CRANS} rectangles conformes",
            f"{pl['rectangles']} rectangles · conformes {pl['largeurs_conformes']} · "
            f"{pl['cotes_escrites']} cotes écrites · échelle {pl['echelle']}",
            pl["rectangles"] == NB_CRANS and pl["largeurs_conformes"]
            and pl["cotes_escrites"] == NB_CRANS and pl["absence_ecrite"])
    ajouter("C08", "l'échelle humaine est dite avec ses deux moitiés",
            "cotes dans la portée, et masse totale écrite telle quelle même hors portage",
            "geste OUI, portage Non",
            f"{eh['cote_min_mm']}–{eh['cote_max_mm']} mm dans {eh['portee_declaree_mm']} mm "
            f"({eh['toutes_dans_le_geste']}) · {eh['masse_totale_kg']} kg pour un portage de "
            f"{eh['portage_un_kg']} kg ({eh['pile_portable_par_un']})",
            eh["toutes_dans_le_geste"] and not eh["pile_portable_par_un"]
            and eh["tete_portable_par_un"])
    ajouter("C09", "tout cran tombe derrière un outil déclaré",
            "zéro cran hors de l'échelle d'outils",
            "0 hors ligne",
            f"répartition {ou['repartition']} · hors ligne {ou['hors_ligne']} · plus fin "
            f"{ou['le_plus_fin_mm']} mm",
            ou["hors_ligne"] == 0 and ou["outils_utilises"] >= 1)
    ajouter("C10", "le total d'heures est la somme des lignes",
            "total calculé = somme des 43 lignes",
            f"{co['total_heures']} h",
            f"{_decimale(co['somme_des_lignes'], 2)} h relues · total déclaré "
            f"{co['total_heures']} h",
            _decimale(co["somme_des_lignes"], 2) == co["total_heures"])
    mesures_vides = all(p["mesure"] in (None, "") for p in pr["liste"])
    ajouter("C11", "les prédictions sont réfutables et non encore mesurées",
            "six lignes complètes, aucune mesure, un instrument à main",
            "6/6 · mesures vides",
            f"{pr['nb']} prédictions · toutes les six clés "
            f"{all(all(p[k] for k in ('id', 'grandeur', 'unite', 'prevue', 'instrument',
                                      'refutation')) for p in pr['liste'])} · colonne mesure "
            f"re-vide ici {mesures_vides} · aucune mesure {pr['aucune_mesure_effectuee']}",
            pr["nb"] == 6 and mesures_vides and pr["aucune_mesure_effectuee"]
            and pr["au_moins_un_à_main"]
            and all(all(p[k] for k in ("id", "grandeur", "unite", "prevue", "instrument",
                                       "refutation")) for p in pr["liste"]))
    ajouter("C12", "aucun prototype n'existe et c'est écrit partout",
            "zéro fichier de prototype, la phrase dans les quatre artefacts, et le seul fichier "
            "hors sceau est celui qui porte ce nœud",
            "0 prototype · phrase 4/4",
            f"{pro['nb_prototypes']} prototype(s) · absence écrite partout "
            f"{ec['absence_partout']} · artefacts {ec['noms']} · non scellés "
            f"{sorted(set(ec['noms']) - set(ec['tailles']))}",
            pro["nb_prototypes"] == 0 and ec["absence_partout"] and len(ec["noms"]) == 4
            and sorted(set(ec["noms"]) - set(ec["tailles"])) == [ec["nom_sans_empreinte"]])
    ajouter("C13", "la finesse de l'encadrement change le statut des cotes",
            "l'encadrement du théorème laisse des crans indéterminés, celui du plan non",
            "5 déc > 0 et 15 déc = 0",
            f"{sen['theoreme_5_decimales']['crans_indetermines']} indéterminés à 5 décimales · "
            f"{sen['plans_15_decimales']['crans_indetermines']} à 15 · écart {sen['ecart']}",
            sen["theoreme_5_decimales"]["crans_indetermines"] > 0
            and sen["plans_15_decimales"]["crans_indetermines"] == 0)
    ajouter("C14", "le catalogue scellé et le plan parlent du même rapport",
            "les rapports du catalogue restent sous la borne propagée de leur arrondi "
            "d'écriture, et la plage du plan est plus fine qu'elle",
            f"écart ≤ {li['borne_propagee']} et finesse du plan inférieure",
            f"hors borne {li['ecart_hors_borne_plan']} · sous seuil "
            f"{li['catalogue_sous_la_borne_ecriture']} ({li['part_de_la_borne']} % de la "
            f"borne) · plus fin {li['plan_plus_fin_que_ecriture']} "
            f"({li['rapport_des_finesses']}×) · {li['nb_formes_catalogue']} formes",
            li["catalogue_sous_la_borne_ecriture"] and li["plan_plus_fin_que_ecriture"])
    ajouter("C15", "deux exécutions produisent la même empreinte",
            "l'empreinte des nœuds est identique sur deux appels",
            f"{etat['taille_octets']} octets reproductibles",
            f"identique {etat['rejoue_identique']} · {etat['empreinte_execution'][:16]}…",
            etat["rejoue_identique"])
    ajouter("C16", "les limites ouvertes ne sont pas déclarées franchies",
            "liste non vide et zéro remplie dans ce lot",
            f"{lo['nb']} limites, 0 remplie",
            f"{lo['nb']:,} lignes · toutes longues {lo['toutes_au_dela_de_20']} · remplies "
            f"{lo['remplies_dans_ce_lot']} · prototypes {pro['nb_prototypes']}",
            lo["nb"] >= 5 and lo["remplies_dans_ce_lot"] == 0
            and lo["toutes_au_dela_de_20"])
    return out


# ─── 7. Scellement -------------------------------------------------------------


def canonique(objet: Any) -> bytes:
    return json.dumps(objet, ensure_ascii=False, sort_keys=True,
                      default=str).encode("utf-8")


MESURES = ("semences", "crans", "cascade", "outillage", "cout", "echelle_humaine",
           "predictions", "prototypes", "sensibilite", "lien_catalogue", "limites_ouvertes")


def noeuds_certificat() -> Dict[str, Any]:
    nc: Dict[str, Any] = {nom: globals()[nom]() for nom in MESURES}
    # seconde passe : nomenclature, plans et écritures mesurent les octets que ce module produit
    base = {**nc, "nb_crans": NB_CRANS}
    nomen = nomenclature(base)
    plans_nc = plans(base)
    nc["nomenclature"] = nomen
    nc["plans"] = plans_nc
    nc["ecritures"] = ecritures({**base, "nomenclature": nomen, "plans": plans_nc})
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
                "la couche ne prétend qu'une chose : à partir du rapport démontré dans "
                "CONTINUITE, on peut écrire des cotes, des tolérances et une nomenclature "
                "cohérentes — pas qu'un objet construit sera conforme",
            ],
            "attribution": {"auteur": SOURCE["auteur"],
                            "statut_de_la_demande": "déclaré · non vérifié pour tout objet "
                                                    "réel, tout outil et toute portée hors "
                                                    "du dépôt"},
            "racine_merkle_sha256": hashlib.sha256(canonique(
                {c: hashlib.sha256(canonique(etat["noeuds_certificat"][c])).hexdigest()
                 for c in sorted(etat["noeuds_certificat"])})).hexdigest()}


def resoudre() -> Dict[str, Any]:
    cert = certificat()
    etat = {k: cert[k] for k in cert if k not in ("source", "limites", "attribution")}
    etat["noeuds_certificat"] = cert
    eqs = {x["id"]: x for x in equations(etat)}
    cs = controles(eqs, etat)
    return {"source": SOURCE, "certificat": cert, "equations": list(eqs.values()),
            "controles": cs,
            "conclusion": {
                "controles_verts": sum(1 for c in cs if c["ok"]), "controles_total": len(cs),
                "equations": len(eqs),
                "statuts_par_label": {st: sum(1 for x in eqs.values() if x["statut"] == st)
                                      for st in ("OPÉRATIONNEL", "SIMULÉ", "SPÉCIFIÉ")},
                "enonce_construction": f"pile de {NB_CRANS} plateaux carrés, cote de tête "
                                       f"{cert['crans']['table'][0]['cote_mm']} mm, clampée à "
                                       f"{cert['crans']['table'][-1]['cote_mm']} mm au cran 42, "
                                       f"tolérance relative 1/1000, facteur de matière "
                                       f"1/(1−ρ²), {PHRASE_ABSENCE}",
                "nb_crans": NB_CRANS,
                "masse_totale_kg": cert["crans"]["masse_totale_kg"],
                "facteur_cascade": cert["cascade"]["facteur_infini"],
                "prototypes_construits": cert["prototypes"]["nb_prototypes"],
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
    cr, ca, eh = cert["crans"], cert["cascade"], cert["echelle_humaine"]
    corps = [
        f"# CONSTRUCTION — {PHRASE_ABSENCE}, mais coté",
        "",
        f"**Départ** ρ = (249/400)^(1/12), démontré dans CONTINUITE ; cadre 1 000 mm ; "
        f"tolérance relative ε_a = 1/1000 (déclarée).",
        "",
        f"**La pile** {NB_CRANS} plateaux carrés emboîtés, de {cr['table'][0]['cote_mm']} mm "
        f"à {cr['table'][-1]['cote_mm']} mm ; le clampage commence au cran 42, exactement le "
        f"pas du théorème.",
        f"**Matière** facteur 1/(1−ρ²) = {ca['facteur_infini']['inferieur']}–"
        f"{ca['facteur_infini']['superieur']} ; les {NB_CRANS} crans en laissent dehors "
        f"{ca['part_hors_des_43_crans']} %.",
        f"**Masse** {cr['masse_totale_kg']} kg ; le plateau de tête fait "
        f"{eh['masse_tete_kg']} kg, la pile entière ne se porte pas.",
        f"**Outils** {cert['outillage']['repartition']} — aucun vide, aucune salle blanche.",
        f"**Temps déclaré** {cert['cout']['total_heures']} h d'atelier pour les "
        f"{NB_CRANS} crans.",
        "",
        "## Cheminement",
        "",
        "1. ρ est ré-encadré par bissection entière, à 5 puis à 15 décimales ;",
        "2. la cote de chaque cran est le multiple unique de 0,01 mm de l'intervalle — pas un "
        "flottant ;",
        "3. la tolérance suit la cote, donc l'erreur cumulative de la pile reste à ε_a fois sa "
        "taille ;",
        "4. la somme des aires en ρ^(2k) converge : 13,1645 fois le plateau de tête ;",
        "5. le CSV et le SVG sont relus après écriture : le plan dit ce que le calcul a dit ;",
        "6. six prédictions portent un instrument et une condition de réfutation ; la colonne "
        "mesure est vide.",
        "",
        "## Résultat",
        "",
        f"- {cert['prototypes']['nb_prototypes']} prototype construit ;",
        f"- {len(cert['limites_ouvertes']['liste'])} limites ouvertes, aucune remplie ;",
        f"- racine Merkle {cert['racine_merkle_sha256']}.",
        "",
    ]
    return ("\r\n".join(corps) + "\r\n").encode("utf-8")


if __name__ == "__main__":
    getcontext().prec = PRECISION
    donnees = resoudre()
    if "--ecrit" in sys.argv:
        for nom, taille in ecrire_artefacts(donnees["certificat"]).items():
            print(f"{nom}: {taille}")
    conclusion = donnees["conclusion"]
    print(json.dumps({
        "equations": conclusion["equations"], "controles_verts": conclusion["controles_verts"],
        "controles_total": conclusion["controles_total"],
        "statuts": conclusion["statuts_par_label"], "nb_crans": conclusion["nb_crans"],
        "masse_totale_kg": conclusion["masse_totale_kg"],
        "facteur_cascade": conclusion["facteur_cascade"],
        "prototypes": conclusion["prototypes_construits"],
        "enonce": conclusion["enonce_construction"],
        "rouges": [c["id"] for c in donnees["controles"] if not c["ok"]],
        "racine": conclusion["racine_merkle_sha256"]}, ensure_ascii=False, indent=2))
