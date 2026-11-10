# -*- coding: utf-8 -*-
"""
Critère exécutable d'un accord numérique : dérivation, ou coïncidence ?

Ce module ne prouve rien sur le monde. Il donne une procédure re-exécutable pour
statuer sur un nombre sorti d'une forme fermée et annoncé en accord avec une
référence mesurée : le test porte-t-il sur le bon objet, l'écart est-il réel, de
quoi la forme a-t-elle besoin comme intrants, combien de formes du même gabarit
tombent dans la même fenêtre, et la revendication dit-elle ce qui l'éliminerait.
Il s'applique à une revendication extérieure lue dans un document daté, et il
s'applique à nos propres nombres avant toute publication.

Cible testée (document extérieur, cité, non adopté)
    A. D. Wissner-Gross, "Chain Theory — a Compendium of Preliminary Findings",
    working draft, page de titre datée du 23 octobre 2026, 754 pages,
    3 676 297 octets, SHA-256
    cdd99bf011bd908fc226591d7c69a62c08985dd30e126cf0b26c43b7cc5abbc9.
    Passage verbatim :
      "Chain Theory yields an exact candidate for it, the algebraic number
      (79 + 48*sqrt(2) + 42*sqrt(3) + 3*sqrt(6))/31104, a weighted count over
      the 172 measurement records of a single entangled pair, small enough to
      check by hand. [...] Its inverse is 137.035 999 189 566 ... . [...]
      Its 2022 recommendation for the inverse is 137.035 999 177, with a
      standard deviation of 21 in the last two digits. The Chain Theory-derived
      number agrees with the CODATA recommendation in its first ten significant
      digits and lies 0.60 standard deviations from it."
      "Mine differs in the one respect that matters: the number is a theorem of
      a stated axiom, its definitions and a few stated readings of them, checked
      in Lean rather than fitted, and only its identification with alpha(0) is
      conjectured."
      "The experimental measurements still disagree with one another by more
      than their stated uncertainties, so this comparison is not yet decisive."

Six équations, six contrôles exécutés
    EQ-DSI-01  Reproduction de la forme fermée (le test porte-t-il sur le bon objet ?)
    EQ-DSI-02  Écart normalisé z contre une référence externe, datée, non fabriquée
    EQ-DSI-03  Compte d'intrants : de quoi la formulation publiée a-t-elle besoin ?
    EQ-DSI-04  Recensement des coïncidences du même gabarit (denominateur libre / fixe)
    EQ-DSI-05  Classement de l'accord : combien de formes tombent plus près ?
    EQ-DSI-06  Falsifiabilité engagée : la revendication nomme-t-elle ce qui la tuerait ?

Limites assumées
    - Le module ne juge pas la physique : il ne dit pas si la théorie est vraie.
    - Il ne juge pas l'auteur : il ne dit pas d'où viennent ses coefficients.
    - Le compte d'intrants porte sur la formulation publiée, pas sur la preuve
      Lean, qui n'est pas rejouée ici.
    - Les bornes du recensement (a_max, n_max) sont un choix déclaré ; changer de
      borne change le nombre de coïncidences, et le module le mesure.
    - Arithmétique en double précision ; la parité avec Decimal(60) est contrôlée
      sur un espace restreint, pas sur l'espace complet.

Console : accents remplacés si le terminal ne les accepte pas ; sortie JSON en UTF-8.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import time
from decimal import ROUND_HALF_UP, Decimal, getcontext

RACINE_DEUX = math.sqrt(2.0)
RACINE_TROIS = math.sqrt(3.0)
RACINE_SIX = math.sqrt(6.0)

# Fenêtre « dix chiffres significatifs » sur une grandeur d'ordre 137 : le dernier
# chiffre retenu est celui des unités de 1e-8, donc ±5e-8.
FENETRE_DIX_CHIFFRES = 5e-8

# ─────────────────────────────────────────────────────────────────────────────
# Référence externe DÉCLARÉE (reprise du document source ; un tiers doit la
# revérifier auprès du CODATA. Elle n'est jamais calculée par ce module.)
# ─────────────────────────────────────────────────────────────────────────────
REFERENCE = {
    "grandeur": "inverse de la constante de structure fine alpha(0), limite Thomson",
    "valeur": 137.035999177,
    "ecart_type": 2.1e-8,
    "source": "recommandation CODATA 2022, telle que citée dans le compendium",
    "date_reference": "2022",
    "date_constat_local": "2026-11-10",
}

FORME_DECLAREE = {
    "a": 79, "b": 48, "c": 42, "d": 3,
    "n": 31104,
    "inverse_publie": 137.035999189566,
    "z_annonce": 0.60,
    "provenance": "Chain Theory Compendium, draft du 2026-10-23, SHA-256 cdd99bf0...5abbc9",
}

# Inventaire des intrants de la formulation publiée.
#   DERIVE  : la quantité se déduit des axiomes énoncés
#   DECLARE : la quantité apparaît comme donnée dans le texte public
#   COMPTE  : la quantité vient d'un dénombrement d'objets ou de mesures
#   EXTERNE : la quantité vient d'une mesure hors du système formel
INTRANTS_DECLARES = [
    {"nom": "sqrt(2), sqrt(3), sqrt(6)", "etat": "DERIVE",
     "justification": "nombres algébriques : aucune donnée physique n'est nécessaire"},
    {"nom": "entiers 79, 48, 42, 3", "etat": "DECLARE",
     "justification": "le texte public les énonce sous cette forme ; la dérivation "
                      "Lean n'est pas rejouée ici"},
    {"nom": "denominateur 31104", "etat": "DECLARE",
     "justification": "idem ; c'est le degré de liberté qui décide du gabarit_search"},
    {"nom": "172 enregistrements de mesure", "etat": "COMPTE",
     "justification": "dénombrement d'un tableau de mesures, non déduit d'un axiome seul"},
    {"nom": "identification du lien au photon", "etat": "DECLARE",
     "justification": "qualifiée de conjecture par l'auteur lui-même"},
    {"nom": "valeur et écart_type CODATA", "etat": "EXTERNE",
     "justification": "indispensables à la comparaison, étrangers à la dérivation"},
]

ENGAGEMENT = {
    "regle_de_rejet": "si les nouvelles mesures s'accordent entre elles à précision "
                      "améliorée, soit elles convergent vers la valeur dérivée, soit "
                      "l'éliminent",
    "gain_de_precision_annonce": 10.0,
    "date_engagement": "2026-10-23",
    "seuil_de_rejet": 3.0,
}

FENETRES_SIGMA = (0.30, 0.60, 1.00, 2.00, 3.00, 5.00, 10.00)


# ─────────────────────────────────────────────────────────────────────────────
# Primitives numériques
# ─────────────────────────────────────────────────────────────────────────────
def somme_algebrique(a: int, b: int, c: int, d: int) -> float:
    return a + b * RACINE_DEUX + c * RACINE_TROIS + d * RACINE_SIX


def inverse_forme(a: int, b: int, c: int, d: int, n: int) -> float:
    """1/alpha pour alpha = (a + b*sqrt2 + c*sqrt3 + d*sqrt6)/n."""
    return n / somme_algebrique(a, b, c, d)


def inverse_forme_decimal(a: int, b: int, c: int, d: int, n: int, chiffres: int = 50) -> Decimal:
    getcontext().prec = chiffres
    return (Decimal(n) / (Decimal(a) + Decimal(b) * Decimal(2).sqrt()
                          + Decimal(c) * Decimal(3).sqrt()
                          + Decimal(d) * Decimal(6).sqrt()))


def _cle(a: int, b: int, c: int, d: int, n: int):
    g = math.gcd(math.gcd(math.gcd(math.gcd(a, b), c), d), n)
    return (a // g, b // g, c // g, d // g, n // g)


# ─────────────────────────────────────────────────────────────────────────────
# Le balayage unique : une passe, deux modes, toutes les fenêtres
# ─────────────────────────────────────────────────────────────────────────────
def balayer(a_max: int, n_max: int, seuil_large: float = 10.0) -> dict:
    """Parcourt l'espace des formes (a + b*sqrt2 + c*sqrt3 + d*sqrt6)/n avec
    0 <= a, b, c, d <= a_max et enregistre, pour chaque numérateur, l'écart à la
    référence dans les deux modes de dénominateur.

    Mode « libre » : n = arrondi(T * L) avec 1 <= n <= n_max. C'est l'espace
    d'une recherche aveugle sur la forme complète, dénominateur compris.
    Mode « fixe » : n = FORME_DECLAREE["n"]. Le dénominateur n'est plus un degré
    de liberté ; c'est le gabarit tel qu'il est publié.

    seuil_large est exprimé en multiples de FENETRE_DIX_CHIFFRES pour que le
    recensement le plus large reste inclus dans la mémoire conservée.
    """
    t_ref = REFERENCE["valeur"]
    n_fixe = FORME_DECLAREE["n"]
    limite = seuil_large * FENETRE_DIX_CHIFFRES

    rencontres_libre = []
    rencontre_fixe = []
    espace = 0
    pas_de_six = [d * RACINE_SIX for d in range(a_max + 1)]
    pas_de_trois = [c * RACINE_TROIS for c in range(a_max + 1)]
    bornes = range(a_max + 1)
    arrondir = math.floor
    valeur_absolue = abs

    for a in bornes:
        for b in bornes:
            x = a + b * RACINE_DEUX
            for c in bornes:
                base = x + pas_de_trois[c]
                for d in bornes:
                    L = base + pas_de_six[d]
                    if L <= 0.0:
                        continue
                    espace += 1
                    n = int(arrondir(t_ref * L + 0.5))
                    if 1 <= n <= n_max:
                        v = n / L
                        e = valeur_absolue(v - t_ref)
                        if e <= limite:
                            rencontres_libre.append((a, b, c, d, n, v, e))
                    v = n_fixe / L
                    e2 = valeur_absolue(v - t_ref)
                    if e2 <= limite:
                        rencontre_fixe.append((a, b, c, d, n_fixe, v, e2))

    rencontres_libre.sort(key=lambda t: t[6])
    rencontre_fixe.sort(key=lambda t: t[6])
    return {
        "a_max": a_max, "n_max": n_max, "n_fixe": n_fixe,
        "fenetre_balayage_sigma": round(limite / REFERENCE["ecart_type"], 3),
        "espace_parcore": espace,
        "libre": rencontres_libre,
        "fixe": rencontre_fixe,
    }


def dans_fenetre(rencontres, sigma: float, k: float) -> list:
    w = k * sigma
    return [t for t in rencontres if t[6] <= w]


def distinctes(rencontres) -> int:
    return len({_cle(t[0], t[1], t[2], t[3], t[4]) for t in rencontres})


# ─────────────────────────────────────────────────────────────────────────────
# EQ-DSI-01 — Reproduction
# ─────────────────────────────────────────────────────────────────────────────
def eq_dsi_01() -> dict:
    f = FORME_DECLAREE
    recalcule = inverse_forme(f["a"], f["b"], f["c"], f["d"], f["n"])
    ecart = abs(recalcule - f["inverse_publie"])
    ok = ecart <= 1e-9
    return {
        "id": "EQ-DSI-01",
        "titre": "Reproduction de la forme fermée déclarée",
        "enonce": "1/alpha = n / (a + b*sqrt2 + c*sqrt3 + d*sqrt6) reproduit les "
                  "chiffres publiés à 1e-9 près",
        "entrees": {k: f[k] for k in ("a", "b", "c", "d", "n")},
        "resultat": {
            "inverse_recalcule": recalcule,
            "inverse_publie": f["inverse_publie"],
            "ecart_absolu": ecart,
            "tolerance": 1e-9,
        },
        "controle": "ecart_absolu <= 1e-9",
        "statut_controle": "PASS" if ok else "FAIL",
        "statut_epistemique": "MESURE",
        "chemin_controle": "eq_dsi_01 -> inverse_forme -> ecart_absolu",
    }


# ─────────────────────────────────────────────────────────────────────────────
# EQ-DSI-02 — Écart normalisé contre référence datée
# ─────────────────────────────────────────────────────────────────────────────
def eq_dsi_02() -> dict:
    f = FORME_DECLAREE
    v = inverse_forme(f["a"], f["b"], f["c"], f["d"], f["n"])
    z = (v - REFERENCE["valeur"]) / REFERENCE["ecart_type"]
    zd = float((inverse_forme_decimal(f["a"], f["b"], f["c"], f["d"], f["n"])
                - Decimal(str(REFERENCE["valeur"]))) / Decimal(str(REFERENCE["ecart_type"])))
    ecart_calcule = abs(z - zd)
    ok = ecart_calcule <= 1e-4
    return {
        "id": "EQ-DSI-02",
        "titre": "Ecart normalise a la reference externe",
        "enonce": "z = (v_derive - v_reference) / sigma_reference, la reference etant "
                  "externe, datee et non calculee par ce module ; le z annonce doit "
                  "sortir du meme calcul",
        "entrees": {"valeur_derivee": v, "reference": REFERENCE["valeur"],
                    "sigma": REFERENCE["ecart_type"], "date": REFERENCE["date_reference"]},
        "resultat": {
            "z_double_precision": z,
            "z_decimal_50_chiffres": zd,
            "ecart_entre_les_deux_calculs": ecart_calcule,
            "z_annonce_dans_le_document": f["z_annonce"],
            "ecart_a_l_annonce": abs(z - f["z_annonce"]),
            "accord_une_sigma": abs(z) <= 1.0,
            "accord_dix_chiffres_significatifs": abs(v - REFERENCE["valeur"]) <= FENETRE_DIX_CHIFFRES,
        },
        "controle": "abs(z_double - z_decimal) <= 1e-4",
        "statut_controle": "PASS" if ok else "FAIL",
        "statut_epistemique": "MESURE",
        "chemin_controle": "eq_dsi_02 -> inverse_forme / inverse_forme_decimal -> z",
    }


# ─────────────────────────────────────────────────────────────────────────────
# EQ-DSI-03 — Compte d'intrants
# ─────────────────────────────────────────────────────────────────────────────
ETATS_INTRANTS = ("DERIVE", "DECLARE", "COMPTE", "EXTERNE")


def eq_dsi_03() -> dict:
    comptes = {e: 0 for e in ETATS_INTRANTS}
    hors_protocole = 0
    for item in INTRANTS_DECLARES:
        etat = item.get("etat")
        if etat not in comptes or not (item.get("justification") or "").strip():
            hors_protocole += 1
            continue
        comptes[etat] += 1
    libres = comptes["DECLARE"] + comptes["COMPTE"]
    ok = (hors_protocole == 0 and sum(comptes.values()) == len(INTRANTS_DECLARES))
    return {
        "id": "EQ-DSI-03",
        "titre": "Compte des intrants de la formulation publiee",
        "enonce": "une forme fermee est « sans intrant » au sens fort si chaque "
                  "quantite qui la compose est DERIVEE ; DECLARE et COMPTE sont "
                  "comptes a part, EXTERNE sert a la comparaison",
        "entrees": {"inventaire": INTRANTS_DECLARES},
        "resultat": {
            "total_inventorie": len(INTRANTS_DECLARES),
            "derive": comptes["DERIVE"],
            "declare": comptes["DECLARE"],
            "compte": comptes["COMPTE"],
            "externe": comptes["EXTERNE"],
            "intrants_non_decharges": libres,
            "verdict_sur_la_revendication": ("ETABLI" if libres == 0
                                             else "NON ETABLI SUR LE TEXTE PUBLIC"),
        },
        "controle": "toute entree de l'inventaire porte un etat de l'ensemble "
                    "{DERIVE, DECLARE, COMPTE, EXTERNE} et une justification non vide ; "
                    "la somme des comptes rend au total inventorie",
        "statut_controle": "PASS" if ok else "FAIL",
        "statut_epistemique": "MESURE",
        "chemin_controle": "eq_dsi_03 -> INTRANTS_DECLARES -> comptes",
        "note": "Le controle porte sur la formulation publiee. Une preuve formelle "
                "rejouable dechargeant 79, 48, 42, 3 et 31104 ferait passer le statut "
                "a ETABLI ; ce module ne peut pas la rejouer a sa place, et ne "
                "conclut donc ni a une derivation sans intrant, ni a un ajustement.",
    }


# ─────────────────────────────────────────────────────────────────────────────
# EQ-DSI-04 — Recensement des coïncidences
# ─────────────────────────────────────────────────────────────────────────────
def eq_dsi_04(balayage: dict) -> dict:
    f = FORME_DECLAREE
    sigma = REFERENCE["ecart_type"]
    cle = (f["a"], f["b"], f["c"], f["d"], f["n"])
    libre = {}
    fixe = {}
    for k in FENETRES_SIGMA:
        rl = dans_fenetre(balayage["libre"], sigma, k)
        rf = dans_fenetre(balayage["fixe"], sigma, k)
        libre[str(k)] = {"tuples": len(rl), "valeurs_distinctes": distinctes(rl)}
        fixe[str(k)] = {"tuples": len(rf), "valeurs_distinctes": distinctes(rf)}
    dans_libre = any(t[:5] == cle for t in balayage["libre"])
    dans_fixe = any(t[:5] == cle for t in balayage["fixe"])
    dix_libre = [t for t in balayage["libre"] if t[6] <= FENETRE_DIX_CHIFFRES]
    dix_fixe = [t for t in balayage["fixe"] if t[6] <= FENETRE_DIX_CHIFFRES]
    series = [libre[str(k)]["tuples"] for k in FENETRES_SIGMA]
    monotone = all(series[i] <= series[i + 1] for i in range(len(series) - 1))
    fenetre_dix_coherente = (len(dix_libre) >= libre["1.0"]["tuples"]
                             and len(dix_libre) <= libre["3.0"]["tuples"])
    ok = dans_libre and dans_fixe and monotone and series[0] >= 1 and fenetre_dix_coherente
    return {
        "id": "EQ-DSI-04",
        "titre": "Recensement des coïncidences du même gabarit",
        "enonce": "denombrer, parmi toutes les formes (a + b*sqrt2 + c*sqrt3 + d*sqrt6)/n "
                  "a coefficients bornes par a_max, celles dont l'inverse tombe dans la "
                  "fenetre k*sigma de la reference, a denominateur libre et a denominateur "
                  "fixe a la valeur publiee",
        "entrees": {"a_max": balayage["a_max"], "n_max": balayage["n_max"],
                    "denominateur_fixe": balayage["n_fixe"], "fenetres_sigma": list(FENETRES_SIGMA)},
        "resultat": {
            "espace_parcore": balayage["espace_parcore"],
            "denominateur_libre": libre,
            "denominateur_fixe": fixe,
            "fenetre_dix_chiffres_significatifs": {
                "largeur_absolue": FENETRE_DIX_CHIFFRES,
                "equivalent_en_sigma": FENETRE_DIX_CHIFFRES / sigma,
                "denominateur_libre": {"tuples": len(dix_libre),
                                       "valeurs_distinctes": distinctes(dix_libre)},
                "denominateur_fixe": {"tuples": len(dix_fixe),
                                      "valeurs_distinctes": distinctes(dix_fixe)},
            },
            "forme_declaree_dans_le_recensement_libre": dans_libre,
            "forme_declaree_dans_le_recensement_fixe": dans_fixe,
            "compte_croissant_avec_la_fenetre": monotone,
        },
        "controle": "la forme declaree est membre du recensement dans les deux modes ; "
                    "le compte est non nul meme a 0.30 sigma (les meilleures rencontres "
                    "du gabarit sont plus serrees que l'accord revendique) ; le compte "
                    "ne decroît pas quand la fenetre s'ouvre ; la fenetre « dix chiffres "
                    "significatifs » (5e-8, soit 2.38 sigma) encadre les comptes 1 et 3 sigma",
        "statut_controle": "PASS" if ok else "FAIL",
        "statut_epistemique": "MESURE",
        "chemin_controle": "eq_dsi_04 -> balayer -> dans_fenetre -> distinctes",
        "interpretation": "le compte n'est pas une accusation : c'est la taille de "
                          "l'espace dans lequel un accord au meme niveau peut apparaitre "
                          "sans aucune theorie. Un accord n'est une evidence que relative "
                          "a l'espace declare, et l'espace doit exclure tout degre de "
                          "liberte qui n'est pas lui-meme derive.",
    }


# ─────────────────────────────────────────────────────────────────────────────
# EQ-DSI-05 — Classement de l'accord
# ─────────────────────────────────────────────────────────────────────────────
def eq_dsi_05(balayage: dict) -> dict:
    f = FORME_DECLAREE
    sigma = REFERENCE["ecart_type"]
    cible = (f["a"], f["b"], f["c"], f["d"], f["n"])
    un_sigma = dans_fenetre(balayage["libre"], sigma, 1.0)
    autres_denominateurs = [t for t in un_sigma if t[4] != f["n"]]
    rang = next((i + 1 for i, t in enumerate(un_sigma) if t[:5] == cible), None)
    z_cible = (inverse_forme(*cible) - REFERENCE["valeur"]) / sigma
    # Un recensement vide est un resultat, pas une exception : les bornes declarees
    # peuvent simplement etre trop strictes pour contenir quoi que ce soit.
    meilleur = un_sigma[0] if un_sigma else None
    z_meilleur = (meilleur[6] / sigma) if meilleur else None
    ok = (rang is not None and 1 <= rang <= len(un_sigma)
          and z_meilleur is not None and z_meilleur <= abs(z_cible) + 1e-12)
    return {
        "id": "EQ-DSI-05",
        "titre": "Classement de l'accord revendique parmi les formes du gabarit",
        "enonce": "combien de formes du meme gabarit, a denominateur libre, tombent plus "
                  "pres de la reference que la forme revendiquee",
        "entrees": {"a_max": balayage["a_max"], "n_max": balayage["n_max"], "fenetre": "1 sigma"},
        "resultat": {
            "formes_dans_un_sigma": len(un_sigma),
            "rang_de_la_forme_declaree": rang,
            "z_de_la_forme_declaree": z_cible,
            "z_de_la_meilleure_coincidence": z_meilleur,
            "formes_mieux_alignees": (rang - 1) if rang else None,
            "rapport_meilleure_sur_declaree": (z_meilleur / abs(z_cible))
                                              if (z_meilleur is not None and z_cible) else None,
            "meilleure_coincidence": ({"coefficients": list(meilleur[:4]),
                                       "denominateur": meilleur[4],
                                       "inverse": meilleur[5]} if meilleur else None),
            "formes_dans_un_sigma_sans_le_denominateur_publie": len(autres_denominateurs),
        },
        "controle": "rang dans [1, N] et meilleur |z| recense <= |z| revendique",
        "statut_controle": "PASS" if ok else "FAIL",
        "statut_epistemique": "MESURE",
        "chemin_controle": "eq_dsi_05 -> balayer -> dans_fenetre(1 sigma) -> rang",
    }


# ─────────────────────────────────────────────────────────────────────────────
# EQ-DSI-06 — Falsifiabilité engagée
# ─────────────────────────────────────────────────────────────────────────────
def eq_dsi_06() -> dict:
    f = FORME_DECLAREE
    z = abs((inverse_forme(f["a"], f["b"], f["c"], f["d"], f["n"])
             - REFERENCE["valeur"]) / REFERENCE["ecart_type"])
    gain = ENGAGEMENT["gain_de_precision_annonce"]
    seuil = ENGAGEMENT["seuil_de_rejet"]
    z_futur = z * gain
    discriminante = z_futur >= seuil
    ok = (bool(ENGAGEMENT["regle_de_rejet"])
          and ENGAGEMENT["date_engagement"] <= REFERENCE["date_constat_local"]
          and discriminante)
    return {
        "id": "EQ-DSI-06",
        "titre": "Falsifiabilite engagee avant mesure",
        "enonce": "une valeur derivée est engagee si le texte publie nomme une regle de "
                  "rejet, si cette regle est anterieure a la mesure nouvelle, et si la "
                  "precision annoncee rend le z actuel decisif ou non concluant",
        "entrees": {"z_actuel": z, "gain_de_precision_annonce": gain,
                    "seuil_de_rejet": seuil, "date_engagement": ENGAGEMENT["date_engagement"]},
        "resultat": {
            "z_attendu_a_la_nouvelle_precision": z_futur,
            "l_accor_actuel_devient_decisif": discriminante,
            "regle_de_rejet_nommee": bool(ENGAGEMENT["regle_de_rejet"]),
            "engagement_antrieur_au_constat": ENGAGEMENT["date_engagement"] <= REFERENCE["date_constat_local"],
            "limite_constatee": "les mesures existantes divergent deja au-dela de leurs "
                                "incertitudes annoncees : le module enregistre cet "
                                "empechement a conclure, il n'en fait pas un verdict",
        },
        "controle": "regle non vide + date d'engagement <= date de constat + z_futur >= seuil",
        "statut_controle": "PASS" if ok else "FAIL",
        "statut_epistemique": "MESURE",
        "chemin_controle": "eq_dsi_06 -> ENGAGEMENT -> z_futur",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Contrôle de parité : double précision == Decimal(60) sur un espace restreint
# ─────────────────────────────────────────────────────────────────────────────
def controle_parete_decimal(a_max: int = 20, n_max: int = 31104, k: float = 20.0) -> dict:
    """Le recensement en double precision doit rendre exactement le meme compte qu'un
    recalcul en Decimal(60) sur un espace petit mais non vide.

    La fenetre est elargie a 20 sigma : en 1 sigma l'espace a_max=20 ne contient
    aucune rencontre, et un controle qui compare deux zeros ne prouve rien.
    """
    getcontext().prec = 60
    d2, d3, d6 = Decimal(2).sqrt(), Decimal(3).sqrt(), Decimal(6).sqrt()
    t_ref = Decimal(str(REFERENCE["valeur"]))
    sig = Decimal(str(REFERENCE["ecart_type"]))
    w = Decimal(str(k)) * sig
    n_fixe = FORME_DECLAREE["n"]
    compte_libre = 0
    compte_fixe = 0
    for a in range(a_max + 1):
        for b in range(a_max + 1):
            for c in range(a_max + 1):
                for d in range(a_max + 1):
                    L = Decimal(a) + Decimal(b) * d2 + Decimal(c) * d3 + Decimal(d) * d6
                    if L <= 0:
                        continue
                    n = int((t_ref * L).to_integral_value(rounding=ROUND_HALF_UP))
                    if 1 <= n <= n_max and abs(Decimal(n) / L - t_ref) <= w:
                        compte_libre += 1
                    if abs(Decimal(n_fixe) / L - t_ref) <= w:
                        compte_fixe += 1
    # Le balayage conserve tout ce qui tombe a 10 x la fenetre « dix chiffres »,
    # soit 23.8 sigma : la fenetre de controle doit rester a l'interieur.
    if k > 20.0:
        raise ValueError("fenetre de controle trop large pour le balayage conserve")
    bal = balayer(a_max, n_max)
    double_libre = len(dans_fenetre(bal["libre"], REFERENCE["ecart_type"], k))
    double_fixe = len(dans_fenetre(bal["fixe"], REFERENCE["ecart_type"], k))
    non_vide = (compte_libre + compte_fixe) > 0
    ok = (compte_libre == double_libre) and (compte_fixe == double_fixe) and non_vide
    return {
        "controle": "double precision == Decimal(60) sur l'espace restreint, et cet "
                    "espace doit contenir au moins une rencontre",
        "a_max": a_max, "fenetre_sigma": k,
        "libre_decimal": compte_libre, "libre_double": double_libre,
        "fixe_decimal": compte_fixe, "fixe_double": double_fixe,
        "espace_restreint_non_vide": non_vide,
        "statut": "PASS" if ok else "FAIL",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Rapport
# ─────────────────────────────────────────────────────────────────────────────
def construire_rapport(a_max: int = 79, n_max: int = 31104,
                       avec_parete: bool = True, avec_balayage: bool = True) -> dict:
    t0 = time.time()
    equations = [eq_dsi_01(), eq_dsi_02(), eq_dsi_03()]
    if avec_balayage:
        bal = balayer(a_max, n_max)
        equations.append(eq_dsi_04(bal))
        equations.append(eq_dsi_05(bal))
    else:
        for id_, titre in (("EQ-DSI-04", "Recensement des coïncidences du même gabarit"),
                           ("EQ-DSI-05", "Classement de l'accord revendique parmi les formes du gabarit")):
            equations.append({"id": id_, "titre": titre,
                              "enonce": "balayage demande explicitement",
                              "entrees": {}, "resultat": {},
                              "controle": "NON_EVALUE (option --sans-balayage)",
                              "statut_controle": "NON_EVALUE",
                              "statut_epistemique": "SPÉCIFIÉ",
                              "chemin_controle": "%s -> balayer (non execute)" % id_.lower().replace("-", "_")})
    equations.append(eq_dsi_06())
    par = controle_parete_decimal() if avec_parete else {"statut": "NON_EVALUE"}
    statuts = [eq["statut_controle"] for eq in equations] + [par.get("statut", "NON_EVALUE")]
    bilan = {"pass": statuts.count("PASS"), "fail": statuts.count("FAIL"),
             "non_evalue": statuts.count("NON_EVALUE"), "total": len(statuts)}
    duree = time.time() - t0
    return {
        "titre": "Critere executable d'un accord numerique : derivation ou coincidence",
        "version": "1.0.0",
        "genere_le_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "cible": {
            "document": "Chain Theory Compendium (working draft)",
            "auteur_declare": "A. D. Wissner-Gross",
            "date_document": "2026-10-23",
            "sha256_document": "cdd99bf011bd908fc226591d7c69a62c08985dd30e126cf0b26c43b7cc5abbc9",
            "octets_document": 3676297,
            "pages": 754,
        },
        "reference": REFERENCE,
        "bornes_recensement": {"a_max": a_max, "n_max": n_max,
                               "fenetre_dix_chiffres": FENETRE_DIX_CHIFFRES},
        "equations": equations,
        "controle_parete_decimal": par,
        "bilan": bilan,
        "duree_seconde": round(duree, 3),
        "ce_que_ce_module_ne_dit_pas": [
            "il ne dit pas si la theorie testee est vraie ou fausse",
            "il ne dit pas d'ou viennent les coefficients de l'auteur teste",
            "il ne prouve pas que l'accord est une coincidence : il donne la taille "
            "de l'espace ou un tel accord peut apparaitre",
            "il ne remplace pas la preuve formelle annoncee par l'auteur",
            "il n'evalue aucune affirmation de nos propres publications : aucune ne "
            "donne une forme fermee ajustee sur une constante mesuree",
        ],
    }


def json_canonical(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def empreinte_rapport(rapport: dict) -> str:
    """Corps du rapport hors horodatage et duree : deux executions du meme binaire
    sur la meme machine doivent rendre la meme empreinte."""
    corps = {k: v for k, v in rapport.items() if k not in ("genere_le_utc", "duree_seconde")}
    return hashlib.sha256(json_canonical(corps).encode("utf-8")).hexdigest()


def _ascii(texte: str) -> str:
    table = {"a": "á", "A": "Á", "e": "é", "E": "É", "i": "í", "I": "Í",
             "o": "ó", "O": "Ó", "u": "ú", "U": "Ú", "c": "ç", "C": "Ç"}
    for cible, source in table.items():
        texte = texte.replace(source, cible)
    return texte


def imprimer(rapport: dict, flot=None) -> None:
    out = flot or sys.stdout
    e = _ascii
    out.write("=" * 88 + "\n")
    out.write(e("CRITERE EXECUTABLE D'UN ACCORD NUMERIQUE -- DERIVATION OU COINCIDENCE") + "\n")
    out.write("=" * 88 + "\n")
    out.write(e("cible     : %s, %s, %s\n") % (e(rapport["cible"]["document"]),
                                               e(rapport["cible"]["auteur_declare"]),
                                               rapport["cible"]["date_document"]))
    out.write(e("sha256    : %s\n") % rapport["cible"]["sha256_document"])
    ref = rapport["reference"]
    out.write(e("reference : %s = %.9f +/- %.1e (%s)\n") % (e(ref["grandeur"]), ref["valeur"],
                                                            ref["ecart_type"], e(ref["source"])))
    b = rapport["bornes_recensement"]
    out.write(e("bornes    : a_max=%d  n_max=%d\n") % (b["a_max"], b["n_max"]))
    out.write("-" * 88 + "\n")
    for eq in rapport["equations"]:
        out.write("%-10s %-58s %-12s %s\n" % (eq["id"], e(eq["titre"])[:58],
                                              eq["statut_controle"], e(eq["statut_epistemique"])))
        out.write("   controle : %s\n" % e(eq["controle"]))
        out.write("   resultat : %s\n" % e(json_canonical(eq["resultat"]))[:520])
    par = rapport["controle_parete_decimal"]
    out.write("-" * 88 + "\n")
    out.write(e("parite double/Decimal : %s\n") % par.get("statut"))
    if par.get("statut") != "NON_EVALUE":
        out.write("   %s\n" % json_canonical({k: v for k, v in par.items()
                                             if k != "controle"})[:300])
    bilan = rapport["bilan"]
    out.write(e("bilan     : %d PASS / %d FAIL / %d NON_EVALUE sur %d controles\n") % (
        bilan["pass"], bilan["fail"], bilan["non_evalue"], bilan["total"]))
    out.write(e("duree     : %.3f s\n") % rapport["duree_seconde"])
    out.write(e("empreinte : %s\n") % empreinte_rapport(rapport))
    out.write(e("limites   :\n"))
    for l in rapport["ce_que_ce_module_ne_dit_pas"]:
        out.write("   - %s\n" % e(l))
    out.write("=" * 88 + "\n")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Critere executable d'un accord numerique")
    ap.add_argument("--a-max", type=int, default=79,
                    help="borne des coefficients a, b, c, d (defaut 79 : le gabarit publie)")
    ap.add_argument("--n-max", type=int, default=31104,
                    help="borne du denominateur en mode libre (defaut 31104)")
    ap.add_argument("--sans-parete", action="store_true",
                    help="ne pas executer le controle de parite Decimal (plus rapide)")
    ap.add_argument("--sans-balayage", action="store_true",
                    help="ne pas executer le recensement (EQ-DSI-04 et 05 en NON_EVALUE)")
    ap.add_argument("--json", action="store_true", help="rendre le rapport en JSON canonical")
    ap.add_argument("--sortie", help="ecrire le rapport JSON canonical dans ce fichier")
    args = ap.parse_args(argv)

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    rapport = construire_rapport(args.a_max, args.n_max,
                                 avec_parete=not args.sans_parete,
                                 avec_balayage=not args.sans_balayage)
    if args.sortie:
        with open(args.sortie, "w", encoding="utf-8", newline="\n") as f:
            f.write(json_canonical(rapport))
    if args.json:
        sys.stdout.write(json_canonical(rapport) + "\n")
    else:
        imprimer(rapport)
    return 0 if rapport["bilan"]["fail"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
