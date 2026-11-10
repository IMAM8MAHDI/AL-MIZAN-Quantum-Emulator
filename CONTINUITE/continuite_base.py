# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""CONTINUITE — la couche qui énonce et vérifie le théorème de continuité continuelle.

Ce que le dépôt contenait déjà, et d'où part ce dossier
-------------------------------------------------------
Une seule auto-similarité est réellement écrite dans le corpus : dans
`bibliotheques/lib_almizan_extension.py`, l'« octave duale » emboîte les formes sur le rapport
`0.6225^(k/12)` (docstring de `FormeEtendueAlmizan`, `_construire_27_formes`). Le mot « fractale »
apparaît comme vocabulaire ; aucun calcul de dimension de Hausdorff, aucun ensemble de Mandelbrot,
aucun itéré de Julia n'existe dans le dépôt. Ce dossier ne corrige pas le mot : il calcule le
rapport qui est déjà là, et il le dit.

Le second antécédent est `ABONDANCE/eau_abondance.py → continuite()` (EQ-04 de ce dossier-là) :
la conservation du débit à travers des sections discontinues. C'est le seul énoncé de continuité
formalisé du parc avant cette couche.

Troisième antécédent, et c'est le motif du lot : `certificats/plan_global.py` marque d'une croix
les lignes « borne a priori → régularité globale » et « passage borne uniforme → régularité » —
le goulot. Et `horloge_noyau/horloge_logique_mizan.py` affirme `continuité_sans_arret = True`
sans le dériver (capsule en lecture seule : ce dossier ne l'écrit pas, il la lit).

Ce que ce module fait, dans l'ordre
-----------------------------------
  1. il importe les semences au lieu de les recopier, puis les écrit en rationnels exacts (EQ-01) ;
  2. il construit le rapport de contraction ρ comme la seule racine douzième utile, et l'encadre
     par des comparaisons d'entiers — pas par un flottant (EQ-02) ;
  3. il vérifie que le catalogue scellé des 27 formes est bien une suite géométrique de rapport ρ,
     et que l'octave duale n'est que l'octave publique multipliée par une constante (EQ-03, EQ-04) ;
  4. il énonce le théorème : la chaîne déclarée descend, ne perd rien (télescopage exact), et
     s'absorbe en un nombre borné de pas sur un unique point fixe du domaine (EQ-05 à EQ-10) ;
  5. il branche la couche sur le graphe réel des dossiers du dépôt (EQ-11) et sur l'antécédent de
     l'eau (EQ-12) ;
  6. il écrit ce que la couche ne remplit pas : les croix du plan global restent des croix (EQ-13),
     la bande ε reste une déclaration (EQ-14), et le module se re-joue à l'octet près (EQ-15).

Ce qu'il ne fait pas : il ne prétend pas que la connaissance continue dans la nature, ne convertit
pas un rapport de contraction en loi physique, ne touche pas à `horloge_noyau/`, et ne remplit
aucune des six échelles ouvertes des problèmes du millénaire.

Usage :
    cd ZENODO_DEPOT_ALMIZAN && py -3 CONTINUITE/continuite_base.py
    cd ZENODO_DEPOT_ALMIZAN && py -3 CONTINUITE/continuite_base.py --ecrit
    cd ZENODO_DEPOT_ALMIZAN && py -3 FONDATION/OUTILS/audit_piliers.py CONTINUITE/continuite_base.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from decimal import Decimal, getcontext
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Tuple

RACINE = Path(__file__).resolve().parents[1]
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

DOSSIER = Path(__file__).resolve().parent
ARTEFACTS = DOSSIER / "artefacts"
PRECISION = 60

from bibliotheques import lib_almizan_extension as EXT                      # noqa: E402
from FONDATION import fondation_base as FB                                  # noqa: E402

# ─── 1. Source et provenance --------------------------------------------------

SOURCE: Dict[str, Any] = {
    "point_de_depart": "demande d'auteur 2026-11-09 : « rajouter une couche ... poser les "
                       "équations pour la théorisation de théorème nouveau dans une "
                       "continuité continuelle ... montrer le cheminement, le résultat »",
    "auteur": "M. Ahmed EL BAHLOUL (IMAM8MAHDI)",
    "antecedents_uses": [
        "bibliotheques/lib_almizan_extension.py — octave duale d'échelle 0.6225^(k/12) : "
        "la seule auto-similarité écrite du corpus",
        "ABONDANCE/eau_abondance.py → continuite() — conservation du débit, EQ-04/C04",
        "certificats/plan_global.py — lignes « ✗ GONGOULOT » : les sauts non remplis",
        "horloge_noyau/horloge_logique_mizan.py — `continuité_sans_arret = True` posé sans "
        "dérivation (capsule lue, jamais écrite)",
    ],
    "ce_que_ce_module_n_utilise_pas": [
        "aucune vidéo : ni transcript, ni chiffre, ni phrase citée d'une bande-son",
        "aucun flottant pour conclure : les verdicts sortent de comparaisons d'entiers",
        "aucune dimension de Hausdorff, aucun Mandelbrot, aucun itéré de Julia : le dépôt n'en "
        "contient pas et ce module n'en invente pas",
    ],
}

# ─── 2. Semences : importées, puis écrites en rationnels ----------------------

FICHES_SEMENCES: List[Tuple[str, Fraction, str]] = [
    ("MIZAN", Fraction(249, 400), "bibliotheques/lib_almizan_extension.py:57"),
    ("LIGNE_REF", Fraction(61, 500), "bibliotheques/lib_almizan_extension.py:58"),
    ("EPSILON", Fraction(21, 1000), "bibliotheques/lib_almizan_extension.py:59"),
    ("PLAFOND_EFFECTIF", Fraction(1203, 2000), "bibliotheques/lib_almizan_extension.py:60"),
    ("COMBLE_CIBLE", Fraction(2322, 4000), "bibliotheques/lib_almizan_extension.py:61"),
]

PUISSANCE_OCTAVE = 12          # douze pas par octave : le k/12 du catalogue
PAS_PAR_OCTAVE = 13            # treize formes publiées, treize duales, une origine


def semences() -> Dict[str, Any]:
    """Les constantes telles que le module les lit dans la source scellée, en rationnels."""
    lues = {"MIZAN": EXT.MIZAN, "LIGNE_REF": EXT.LIGNE_REF, "EPSILON": EXT.EPSILON,
            "PLAFOND_EFFECTIF": EXT.PLAFOND_EFFECTIF, "COMBLE_CIBLE": EXT.COMBLE_CIBLE}
    rationnels = {nom: valeur for nom, valeur, _ in FICHES_SEMENCES}
    ecarts = {nom: abs(lues[nom] - float(rationnels[nom])) for nom in rationnels}
    domaine = (rationnels["LIGNE_REF"], rationnels["MIZAN"])
    return {
        "lues_flottantes": lues,
        "rationnels": {nom: f"{v.numerator}/{v.denominator}" for nom, v in rationnels.items()},
        "exactitude_float": {"tous_egaux": all(e == 0.0 for e in ecarts.values()),
                             "ecarts": ecarts},
        "domaine_D": {"borne_basse": str(domaine[0]), "borne_haute": str(domaine[1]),
                      "largeur": f"{(domaine[1] - domaine[0]).numerator}/"
                                 f"{(domaine[1] - domaine[0]).denominator}",
                      "non_vide": domaine[0] < domaine[1],
                      "definition": "clamp_domaine_mizan, "
                                    "bibliotheques/lib_almizan_extension.py:97-99"},
        "espece": {"pas_par_octave": PAS_PAR_OCTAVE, "puissance": PUISSANCE_OCTAVE,
                   "noeuds_catalogue": len(EXT.LES_27_FORMES_ETENDUES)},
    }


# ─── 3. ρ : racine douzième encadrée par des entiers -------------------------

def _dixiemes(n: int) -> Tuple[int, int]:
    """Plus grand a tel que (a/10^n)^12 < MIZAN, et son successeur — entiers uniquement."""
    m = 10 ** n
    cible_gauche = 249 * m ** 12                 # MIZAN·10^(12n), avec num/den 249/400
    bas, haut = 0, m
    while bas + 1 < haut:
        milieu = (bas + haut) // 2
        if milieu ** 12 * 400 < cible_gauche:
            bas = milieu
        else:
            haut = milieu
    return bas, haut


def encadrement_rho(decimales: int = 5) -> Dict[str, Any]:
    """ρ = 0,6225^(1/12) encadré à 10^-decimales près, par comparaison de douzièmes puissances."""
    a, b = _dixiemes(decimales)
    m = 10 ** decimales
    bas, haut = Fraction(a, m), Fraction(b, m)
    return {
        "decimales": decimales,
        "inferieur": f"{a}/{m}", "superieur": f"{b}/{m}",
        "largeur_encadrement": f"1/{m}",
        "preuve": {
            "rho_superieur_a_bas": 249 * m ** 12 > a ** 12 * 400 if False
            else a ** 12 * 400 < 249 * m ** 12,
            "rho_inferieur_ou_egal_a_haut": b ** 12 * 400 >= 249 * m ** 12,
            "chiffres_gauche": len(str(a ** 12 * 400)),
            "chiffres_droite": len(str(249 * m ** 12)),
        },
        "conclusion": {"rho_strictement_inferieur_a_un": haut <= 1,
                       "rho_strictement_superieur_a_zero": bas > 0,
                       "contraction": bool(bas < haut and haut < 1)},
        "bornes": {"bas": bas, "haut": haut},
    }


def chaine_m(Z: int) -> Dict[str, Any]:
    """x_k = MIZAN·ρ^k = (249/400)^((12+k)/12), comparé à LIGNE_REF par des entiers seuls."""
    R = Fraction(61, 500)
    M = Fraction(249, 400)

    def compar(k: int) -> Dict[str, Any]:
        # x_k < R  ⟺  M^(12+k) < R^12  ⟺  249^(12+k)·500^12 < 400^(12+k)·61^12
        gauche = 249 ** (PUISSANCE_OCTAVE + k) * 500 ** 12
        droite = 400 ** (PUISSANCE_OCTAVE + k) * 61 ** 12
        return {"k": k, "sortie_de_D": gauche < droite,
                "gauche": gauche, "droite": droite,
                "ecart_signe": -1 if gauche < droite else (0 if gauche == droite else 1)}

    premier = next(k for k in range(0, 4096) if compar(k)["sortie_de_D"])
    table = [compar(k) for k in range(0, min(Z, 4096))]
    getcontext().prec = PRECISION
    D = Decimal(249) / Decimal(400)
    rho = D ** (Decimal(1) / Decimal(12))
    valeurs = {k: float(D * rho ** k) for k in range(0, min(Z, 4096))}
    # Sens et positivité conclus par entiers : x_k^12 / x_{k+1}^12 = 400/249 > 1.
    ordre = {"rapport_12puissances": "400/249",
             "strictement_decroissante": 400 > 249,
             "stricte": (lambda: all(
                 249 ** (12 + k) * 400 ** (13 + k) > 249 ** (13 + k) * 400 ** (12 + k)
                 for k in range(0, min(Z, 64))))(),
             "positive_partout": 249 > 0 and 400 > 0,
             "enonce": "x_k^12 = (249/400)^(12+k), donc x_k/x_{k+1} = (400/249)^(1/12) > 1 "
                       "puisque 400 > 249 : la décroissance est une comparaison d'entiers"}
    return {"rapport_par_pas": "ρ = (249/400)^(1/12)",
            "ordre_entier": ordre,
            "valeur_decimale_rho": str(+rho),
            "pas_de_sortie": premier,
            "voisinage": {"k_avant": compar(premier - 1), "k_premier": compar(premier),
                          "k_apres": compar(premier + 1)},
            "table": [{k: v for k, v in c.items() if k not in ("gauche", "droite")}
                      for c in table],
            "valeurs_flottantes_indicatives": valeurs,
            "bornes_D": {"haute": f"{M.numerator}/{M.denominator}",
                         "basse": f"{R.numerator}/{R.denominator}"},
            "semences_rationnelles": {nom: f"{v.numerator}/{v.denominator}"
                                      for nom, v, _ in FICHES_SEMENCES}}


def pas_absorption(d: Fraction) -> int:
    """Nombre de pas de T(x)=max(LIGNE_REF, ρx) pour absorber le départ d : entiers seuls.

    ρ^j·d ≤ R ⟺ (ρ^j·d)^12 ≤ R^12 ⟺ MIZAN^j · num(d)^12 · 500^12 ≤ 400^j · den(d)^12 · 61^12.
    """
    for j in range(0, 4096):
        gauche = 249 ** j * d.numerator ** 12 * 500 ** 12
        droite = 400 ** j * d.denominator ** 12 * 61 ** 12
        if gauche <= droite:
            return j
    raise RuntimeError("absorption non atteinte sur le domaine déclaré")


def point_fixe() -> Dict[str, Any]:
    """T(x) = max(LIGNE_REF, ρ·x) sur D : un seul point fixe, atteint en nombre borné de pas."""
    R, M = Fraction(61, 500), Fraction(249, 400)
    rho = encadrement_rho(5)
    catalogue = EXT.LES_27_FORMES_ETENDUES
    departs: List[Tuple[str, Fraction]] = []
    for idx, forme in sorted(catalogue.items()):
        d = Fraction(str(forme.image_fonction_d))
        departs.append((f"F{idx}", d))
    absorptions = {nom: pas_absorption(d) for nom, d in departs}
    dans_D = [nom for nom, d in departs if not (R <= d <= M)]
    suite = [R] + [M * Fraction(str(rho["bornes"]["haut"])) ** k for k in range(1, 5)]
    grille = [R + (M - R) * k / 64 for k in range(65)]
    fixes = [x for x in grille
             if max(R, min(M, x * Fraction(96126, 100000))) == x
             or max(R, min(M, x * Fraction(96127, 100000))) == x]
    return {
        "enonce": "sur D = [61/500 ; 249/400], T(x) = max(61/500, ρ·x) n'a qu'un point fixe, "
                  "x = 61/500, et toute orbite de D l'atteint en au plus 42 pas",
        "preuve unicite": "ρ < 1 donc ρ·x < x pour tout x > 0 : aucun intérieur de D n'est fixe ; "
                          "le maximum de la borne basse absorbe le reste, et ρ·(61/500) < 61/500",
        "rho_pour_unicite": {"bas": rho["inferieur"], "haut": rho["superieur"]},
        "point_fixe": f"{R.numerator}/{R.denominator}",
        "appartient_D": R >= Fraction(61, 500) and R <= M,
        "depts_hors_D": dans_D,
        "absorption_maximale": max(absorptions.values()),
        "absorption_minimale": min(absorptions.values()),
        "absorptions_par_noeud": absorptions,
        "candidats_fixes_sur_grille": [str(x) for x in fixes][:8],
        "suite_testee": [str(x) for x in suite],
    }


def _dec(v: Fraction) -> Decimal:
    getcontext().prec = PRECISION
    return Decimal(v.numerator) / Decimal(v.denominator)


def queue(n: int) -> Dict[str, Any]:
    """Σ_{k≥n} ρ^k = ρ^n/(1−ρ), encadré par des rationnels issus de l'encadrement de ρ."""
    rho = encadrement_rho(5)
    bas, haut = rho["bornes"]["bas"], rho["bornes"]["haut"]
    un = Fraction(1)
    borne_haute = haut ** n / (un - haut)
    borne_basse = bas ** n / (un - bas)
    getcontext().prec = PRECISION
    D = Decimal(249) / Decimal(400)
    r = D ** (Decimal(1) / Decimal(12))
    valeur = r ** n / (1 - r)
    return {"n": n, "formule": "ρ^n/(1−ρ)",
            "borne_basse": f"{borne_basse.numerator}/{borne_basse.denominator}",
            "borne_haute": f"{borne_haute.numerator}/{borne_haute.denominator}",
            "valeur_decimal": str(+valeur),
            "encadrement_valide": bool(_dec(borne_basse) < valeur < _dec(borne_haute)),
            "largeur_encadrement": str(+(_dec(borne_haute) - _dec(borne_basse))),
            "somme_totale": {"formule": "1/(1−ρ)",
                             "basse": str(un / (un - bas)),
                             "haute": str(un / (un - haut))}}


def telescage(N: int) -> Dict[str, Any]:
    """Σ (x_{k−1} − x_k) = x_0 − x_N : la chaîne ne crée et ne perd rien en route."""
    getcontext().prec = PRECISION
    D = Decimal(249) / Decimal(400)
    rho = D ** (Decimal(1) / Decimal(12))
    x = [D * rho ** k for k in range(N + 1)]
    somme = sum(x[k - 1] - x[k] for k in range(1, N + 1))
    difference = x[0] - x[N]
    sauts = [x[k - 1] - x[k] for k in range(1, N + 1)]
    M, R = Fraction(249, 400), Fraction(61, 500)
    return {"N": N,
            "somme_des_sauts": str(+somme), "difference_des_bords": str(+difference),
            "ecart_absolu": str(+(somme - difference)),
            "identique": bool(abs(somme - difference) < Decimal(10) ** -(PRECISION - 8)),
            "saut_max": str(+max(sauts)), "saut_min": str(+min(sauts)),
            "span_declare": f"{(M - R).numerator}/{(M - R).denominator}",
            "span_decimal": str(+(Decimal(M.numerator) / M.denominator
                                   - Decimal(61) / Decimal(500))),
            "perte_cumulee": str(+(x[0] - x[N]))}


def catalogue_contraction() -> Dict[str, Any]:
    """Le catalogue scellé est-il une suite géométrique de rapport ρ ? Dérive maximale mesurée."""
    getcontext().prec = PRECISION
    D = Decimal(249) / Decimal(400)
    rho = D ** (Decimal(1) / Decimal(12))
    # Facteur dual : LIGNE_REF/MIZAN = (61/500)/(249/400) = 244/1245 = 1220/6225 ≈ 0,1959839357.
    dual = Fraction(61, 500) / Fraction(249, 400)
    facteur_dual = Decimal(dual.numerator) / Decimal(dual.denominator)
    catalogue = EXT.LES_27_FORMES_ETENDUES
    derives: Dict[str, Decimal] = {}
    rapports: List[Decimal] = []
    for octave, idxs in (("OCTAVE_1_LUMIERE", range(1, 14)),
                         ("OCTAVE_2_DUALE_OMBRE", range(14, 27))):
        echelles = [Decimal(str(catalogue[i].echelle_mizan)) for i in idxs]
        for k, value in enumerate(echelles):
            exact = (rho ** k) if octave.endswith("LUMIERE") else (rho ** k) * facteur_dual
            derives[f"{octave}#{k}"] = abs(value - exact)
        rapports += [echelles[k + 1] / echelles[k] for k in range(len(echelles) - 1)]
    duales = [Decimal(str(catalogue[i].echelle_mizan)) for i in range(14, 27)]
    publiques = [Decimal(str(catalogue[i].echelle_mizan)) for i in range(1, 14)]
    quotients = [duales[k] / publiques[k] for k in range(13)]
    return {"rapports_consecutifs_min": str(+min(rapports)),
            "rapports_consecutifs_max": str(+max(rapports)),
            "rho_exact": str(+rho),
            "derive_maximale": str(+max(derives.values())),
            "derives": {k: str(+v) for k, v in sorted(derives.items())},
            "facteur_dual_declare": f"{EXT.LIGNE_REF}/{EXT.MIZAN}",
            "facteur_dual_fraction": f"{dual.numerator}/{dual.denominator}",
            "facteur_dual_decimal": str(+facteur_dual),
            "quotients_dual_sur_public_min": str(+min(quotients)),
            "quotients_dual_sur_public_max": str(+max(quotients)),
            "nb_noeuds_testes": len(derives)}


def graphe_couche() -> Dict[str, Any]:
    """Le graphe réel des dossiers qui portent des équations, lu dans la base intégrée."""
    modules = list(FB.MODULES_PRINCIPAUX)
    presences = {m: any((RACINE / d / m).exists() for d in FB.DOSSIERS_EQUATIONS)
                 for m in modules}
    inventaire = FB.inventaire_parc()
    imports = FB.imports_parc()
    equitations = sum(v["equations"] for v in inventaire.values())
    return {"modules_declares": modules, "modules_absents": [m for m, ok in presences.items()
                                                             if not ok],
            "dossiers_comptes": sorted(inventaire),
            "equations_comptees": equitations,
            "controles_comptes": sum(v["controles"] for v in inventaire.values()),
            "tests_comptes": sum(v["tests"] for v in inventaire.values()),
            "tiers_par_dossier": {d: v["tiers"] for d, v in imports.items() if v["tiers"]},
            "racines_fondees_dehors": FB.graphe_dependances()["racines_fondees_dehors"]}


def antecedent_eau() -> Dict[str, Any]:
    """Re-dérive en rationnels l'unique énoncé de continuité déjà formalisé du parc.

    Les valeurs ne sont pas recopiées ici : elles sont lues dans le dictionnaire renvoyé par
    `ABONDANCE/eau_abondance.py → continuite()` (debit_m3_s, sections_m2), puis recalculées en
    rationnels exacts. La leçon de forme est la suivante : la continuité s'énonce
    « S_i·v_i = Q pour toute section i », et non « Σ S_i·v_i = Q » — la somme, sur trois
    sections, vaut 3·Q.
    """
    from ABONDANCE import eau_abondance as EAU
    lu = EAU.continuite()
    debit = Fraction(str(lu["debit_m3_s"]))
    sections = [Fraction(str(s)) for s in lu["sections_m2"]]
    vitesses = [debit / s for s in sections]
    produits = [s * v for s, v in zip(sections, vitesses)]
    somme = sum(produits)
    return {"source_lue": "ABONDANCE/eau_abondance.py → continuite()",
            "equation": "Q = S_i · v_i pour chaque section i, avec v_i = Q / S_i",
            "debit": f"{debit.numerator}/{debit.denominator}",
            "sections": [f"{s.numerator}/{s.denominator}" for s in sections],
            "vitesses": [f"{v.numerator}/{v.denominator}" for v in vitesses],
            "produits": [f"{p.numerator}/{p.denominator}" for p in produits],
            "identique_al_debit": all(p == debit for p in produits),
            "somme_des_produits": f"{somme.numerator}/{somme.denominator}",
            "somme_est_triple_debit": somme == 3 * debit,
            "pigee_formelle": "Σ S_i·v_i = Q est faux : la somme vaut 3·Q sur trois sections ; "
                              "le contrôle porte produit par produit",
            "registre_dossier": "EQ-04/C04 de ABONDANCE/eau_abondance.py",
            "ce_que_ca_ne_prouve_pas": "trois sections et un débit déclarés par ABONDANCE : "
                                       "c'est leur exemple, pas un écoulement réel"}


def ecarts_ouverts() -> Dict[str, Any]:
    """Compte les croix du plan global : ce que la couche laisse ouvertes, sans les effacer."""
    chemin = RACINE / "certificats" / "plan_global.py"
    texte = chemin.read_text(encoding="utf-8", errors="replace")
    croix = [ligne.strip() for ligne in texte.splitlines() if "✗" in ligne]
    coches = sum(ligne.count("✓") for ligne in texte.splitlines())
    mi = sum(ligne.count("◐") for ligne in texte.splitlines())
    return {"fichier": "certificats/plan_global.py",
            "lignes_a_croix": len(croix),
            "exemples": [c[:96] for c in croix[:4]],
            "coches": coches, "demi_coches": mi,
            "goulots": sum(1 for c in croix if "GONGOULOT" in c.upper() or "GONGOULOT" in c),
            "que_dit_ce_dossier": "la continuité continuelle de cette couche est une propriété "
                                  "d'une chaîne déclarée sur un domaine fini ; aucune de ces "
                                  "croix n'est devenue une coche"}


def bande_epsilon() -> Dict[str, Any]:
    """La bande ε : trois rationnels déclarés, un rapport, aucune mesure."""
    M, R = Fraction(249, 400), Fraction(61, 500)
    EPS, P, C = Fraction(21, 1000), Fraction(1203, 2000), Fraction(2322, 4000)
    span = M - R
    getcontext().prec = PRECISION
    return {"epsilon": f"{EPS.numerator}/{EPS.denominator}",
            "plafond": f"{P.numerator}/{P.denominator}",
            "comble": f"{C.numerator}/{C.denominator}",
            "chaine_des_deux_eps": bool(M - EPS == P and P - EPS == C),
            "rapport_epsilon_sur_span": str(+(Decimal(EPS.numerator) / EPS.denominator
                                               / (Decimal(M.numerator) / M.denominator
                                                   - Decimal(R.numerator) / R.denominator))),
            "span": f"{span.numerator}/{span.denominator}",
            "statut_de_la_bande": "déclarée par l'auteur dans lib_almizan_extension.py ; "
                                  "aucun instrument du dépôt ne la mesure"}


# ─── 4. Équations et contrôles -------------------------------------------------

NOEUDS: Dict[str, Dict[str, Any]] = {
    "EQ-01": {"depend": [], "externe": ["bibliotheques/lib_almizan_extension.py (scellé)"]},
    "EQ-02": {"depend": ["EQ-01"], "externe": []},
    "EQ-03": {"depend": ["EQ-02"], "externe": ["catalogue LES_27_FORMES_ETENDUES"]},
    "EQ-04": {"depend": ["EQ-03"], "externe": ["docstring FormeEtendueAlmizan"]},
    "EQ-05": {"depend": ["EQ-02"], "externe": []},
    "EQ-06": {"depend": ["EQ-05"], "externe": []},
    "EQ-07": {"depend": ["EQ-05", "EQ-01"], "externe": []},
    "EQ-08": {"depend": ["EQ-05", "EQ-02"], "externe": []},
    "EQ-09": {"depend": ["EQ-07"], "externe": ["clamp_domaine_mizan"]},
    "EQ-10": {"depend": ["EQ-09"], "externe": ["catalogue LES_27_FORMES_ETENDUES"]},
    "EQ-11": {"depend": ["EQ-01"], "externe": ["FONDATION/fondation_base.py"]},
    "EQ-12": {"depend": ["EQ-06"], "externe": ["ABONDANCE/eau_abondance.py"]},
    "EQ-13": {"depend": ["EQ-09"], "externe": ["certificats/plan_global.py",
                                               "horloge_noyau/horloge_logique_mizan.py"]},
    "EQ-14": {"depend": ["EQ-01"], "externe": ["lib_almizan_extension.py:60-61"]},
    "EQ-15": {"depend": ["EQ-02", "EQ-07", "EQ-09"], "externe": []},
}

N_PAS_TELESCOPE = 42          # la longueur de chaîne déclarée : le pas de bascule lui-même


def _eq(id_: str, chemin: str, formule: str, resultat: str, statut: str,
        limite: str, detail: Any) -> Dict[str, Any]:
    n = NOEUDS[id_]
    return {"id": id_, "chemin": chemin, "formule": formule, "resultat": resultat,
            "statut": statut, "limite": limite, "detail": detail,
            "couche": "S2 REGULARITE",
            "piliers": ["P1 UNITE", "P2 BORNE", "P3 CONFRONTATION", "P4 TRANSMISSION"],
            "depend_de": n["depend"], "fonde_hors_du_dossier": n["externe"]}


def equations(etat: Dict[str, Any]) -> List[Dict[str, Any]]:
    s, rho, ch, pf, q, te, cat = (etat["semences"], etat["rho"], etat["chaine"],
                                  etat["point_fixe"], etat["queue"], etat["telescage"],
                                  etat["catalogue"])
    g, ea, eo, be = (etat["graphe"], etat["antecedent_eau"], etat["ecarts_ouverts"],
                     etat["bande_epsilon"])
    return [
        _eq("EQ-01", "continuite_base.py → semences() → C01",
            "D = [61/500 ; 249/400] ⊂ ℚ, ε = 21/1000, semences importées et non recopiées",
            f"rationnels {s['rationnels']} · domaines non vide {s['domaine_D']['non_vide']} · "
            f"largeur {s['domaine_D']['largeur']}", "OPÉRATIONNEL",
            "les cinq nombres viennent d'une ligne précise du dépôt (fichier:ligne citée) ; le "
            "contrôle prouve qu'ils sont exactement ces rationnels, pas qu'ils décrivent une "
            "grandeur physique", s),
        _eq("EQ-02", "continuite_base.py → encadrement_rho() → C02",
            "ρ = (249/400)^(1/12), donc ρ^12 = 249/400 et 0 < ρ < 1",
            f"{rho['inferieur']} < ρ ≤ {rho['superieur']} · largeur {rho['largeur_encadrement']} · "
            f"chiffres comparés {rho['preuve']['chiffres_gauche']} contre "
            f"{rho['preuve']['chiffres_droite']}", "OPÉRATIONNEL",
            "l'encadrement est obtenu par recherche dichotome sur des douzièmes puissances "
            "entières : aucun flottant n'intervient dans la conclusion", rho),
        _eq("EQ-03", "continuite_base.py → catalogue_contraction() → C03",
            "échelle publique e_k = ρ^k pour k = 0..12, rapport consécutif constant",
            f"rapports mesurés dans [{cat['rapports_consecutifs_min']} ; "
            f"{cat['rapports_consecutifs_max']}] · ρ = {cat['rho_exact']} · dérive maximale vs "
            f"catalogue {cat['derive_maximale']}", "OPÉRATIONNEL",
            "le catalogue est stocké arrondi à 8 décimales : la dérive constatée est un défaut "
            "d'écriture du catalogue, pas une violation de la loi ; c'est la seule auto-similarité "
            "effectivement présente dans le dépôt", cat),
        _eq("EQ-04", "continuite_base.py → catalogue_contraction() → C04",
            "octave duale d_k = (61/500 ÷ 249/400)·e_k = (244/1245)·ρ^k, phase +π",
            f"quotient dual/public mesuré dans [{cat['quotients_dual_sur_public_min']} ; "
            f"{cat['quotients_dual_sur_public_max']}] · constante déclarée "
            f"{cat['facteur_dual_declare']}", "OPÉRATIONNEL",
            "le facteur 244/1245 est exactement le rapport 0.122/0.6225 écrit dans la source : "
            "rien n'est ajouté pour rendre les deux octaves semblables", cat),
        _eq("EQ-05", "continuite_base.py → chaine_m() → C05",
            "x_k = MIZAN·ρ^k = (249/400)^((12+k)/12) : décroissante, minorée par 0",
            f"rapport par pas {ch['rapport_par_pas']} · x_0 = {ch['bornes_D']['haute']} · "
            f"minorée de 0 et strictement décroissante sur 0 ≤ k ≤ 42", "OPÉRATIONNEL",
            "la décroissance se lit sur ρ < 1 (EQ-02) : la minoration par 0 est celle du domaine, "
            "pas une propriété de la nature", ch),
        _eq("EQ-06", "continuite_base.py → telescage() → C06",
            "Σ_{k=1..N}(x_{k−1} − x_k) = x_0 − x_N, identité télescopique exacte",
            f"somme {te['somme_des_sauts']} · différence des bords {te['difference_des_bords']} · "
            f"écart {te['ecart_absolu']} · span déclaré {te['span_declare']}", "OPÉRATIONNEL",
            "le calcul est mené en décimal à 60 chiffres sur N = 42 pas : l'identité est algébrique "
            "et ne prouve pas qu'une quantité réelle se conserve, elle prouve que la chaîne "
            "déclarée n'invente ni ne perd de valeur en route", te),
        _eq("EQ-07", "continuite_base.py → chaine_m() → C07",
            "n* = min{ k : MIZAN·ρ^k < LIGNE_REF } — le pas de bascule hors du domaine",
            f"n* = {ch['pas_de_sortie']} · x_41 = {ch['voisinage']['k_premier']['k']} refusé, "
            f"x_{ch['pas_de_sortie']} = {ch['voisinage']['k_premier']['ecart_signe']} retenu "
            f"(signe de la comparaison entière)", "OPÉRATIONNEL",
            "42 pas est un compte de pas d'une application déclarée sur un intervalle déclaré ; "
            "ce n'est ni une durée, ni une demi-vie, ni une portée temporelle du savoir", ch),
        _eq("EQ-08", "continuite_base.py → queue() → C08",
            "Σ_{k≥n} ρ^k = ρ^n/(1−ρ), encadré à partir de l'encadrement de ρ",
            f"à n = {q['n']} : [{q['borne_basse'][:28]}… ; {q['borne_haute'][:28]}…] · "
            f"valeur {q['valeur_decimal'][:24]} · somme totale 1/(1−ρ) = {q['somme_totale']['basse'][:18]}…",
            "OPÉRATIONNEL",
            "l'encadrement rationnel est hérité de la largeur 10^-5 de l'encadrement de ρ : "
            "augmenter les décimales resserre la borne, cela ne change pas la loi", q),
        _eq("EQ-09", "continuite_base.py → point_fixe() → C09",
            "T(x) = max(61/500, ρ·x) sur D : unique point fixe x = 61/500",
            f"point fixe {pf['point_fixe']} · candidats fixes sur la grille "
            f"{pf['candidats_fixes_sur_grille'] or 'aucun autre'} · ρ ∈ [{pf['rho_pour_unicite']['bas']} ; "
            f"{pf['rho_pour_unicite']['haut']}]", "OPÉRATIONNEL",
            "l'unicité tient parce que ρ < 1 et que le clamp est pris sur la borne basse : "
            "changer la définition du clamp change le théorème, c'est une conséquence du "
            "domaine déclaré par l'auteur, pas une nécessité logique", pf),
        _eq("EQ-10", "continuite_base.py → point_fixe() → C10",
            "pas d'absorption j(d) = min{ j : ρ^j·d ≤ 61/500 }, pour les 27 nœuds déclarés",
            f"absorption maximale {pf['absorption_maximale']} · minimale "
            f"{pf['absorption_minimale']} · nœuds testés {len(pf['absorptions_par_noeud'])}",
            "OPÉRATIONNEL",
            "les départs sont les valeurs `image_fonction_d` du catalogue, donc arrondies à six "
            "décimales : un départ non représentable dans D est signalé, jamais corrigé en "
            "silence", pf),
        _eq("EQ-11", "continuite_base.py → graphe_couche() → C11",
            "couche = graphe des dossiers à équations : modules déclarés, imports, comptes",
            f"{g['modules_declares'] and len(g['modules_declares'])} modules porteurs · "
            f"{g['equations_comptees']} équations · {g['controles_comptes']} contrôles · "
            f"{g['tests_comptes']} tests · tiers {g['tiers_par_dossier'] or 'aucun'}",
            "OPÉRATIONNEL",
            "un graphe de dépendances entre fichiers est une propriété du dépôt, pas de la "
            "connaissance : « continuité » ici veut dire que chaque équation est atteignable "
            "depuis une semence écrite hors de son dossier", g),
        _eq("EQ-12", "continuite_base.py → antecedent_eau() → C12",
            "S_i · v_i = Q pour chaque section i, v_i = Q/S_i (lu dans ABONDANCE, re-dérivé ici)",
            f"Q = {ea['debit']} · sections {ea['sections']} · vitesses {ea['vitesses']} · "
            f"produits {ea['produits']} · somme {ea['somme_des_produits']} = 3Q "
            f"{ea['somme_est_triple_debit']}", "OPÉRATIONNEL",
            "c'est l'exemple posé par ABONDANCE (trois sections, un débit déclaré) : la couche le "
            "re-dérive en rationnels et n'en tire aucune généralité sur les fluides", ea),
        _eq("EQ-13", "continuite_base.py → ecarts_ouverts() → C13",
            "les sauts non remplis du plan global restent non remplis après cette couche",
            f"{eo['lignes_a_croix']} lignes à croix · {eo['coches']} coches · "
            f"{eo['demi_coches']} demi-coches · exemples {eo['exemples'][:1]}", "SPÉCIFIÉ",
            "cette équation ne comble aucun des goulots ouverts : elle interdit qu'ils passent "
            "silencieusement de ✗ à ✓ quand une couche nouvelle ajoute le mot « continuité »", eo),
        _eq("EQ-14", "continuite_base.py → bande_epsilon() → C14",
            "MIZAN − ε = PLAFOND_EFFECTIF ; PLAFOND_EFFECTIF − ε = COMBLE_CIBLE ; ε = 21/1000",
            f"chaîne des deux ε {be['chaine_des_deux_eps']} · span {be['span']} · "
            f"ε/span = {be['rapport_epsilon_sur_span']}", "SPÉCIFIÉ",
            "les deux ε sont des paramètres de conception déclarés dans le fichier source : "
            "aucun instrument du dépôt ne les mesure, et le rapport ε/span n'a pas d'unité "
            "physique", be),
        _eq("EQ-15", "continuite_base.py → resoudre() → C15",
            "déterminisme : deux exécutions produisent les mêmes octets, hors mesure d'hôte",
            f"empreinte stable {etat['empreinte_execution']} · aucune valeur d'hôte dans les "
            f"octets scellés", "OPÉRATIONNEL",
            "la re-jouabilité est testée sur la machine de l'auteur : elle prouve l'absence "
            "d'aléa et de dépendance au matériel dans le calcul, pas l'exactitude des semences",
            {"empreinte": etat["empreinte_execution"], "rejoue": etat["rejoue_identique"]}),
    ]


def controles(eqs: Dict[str, Any], etat: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []

    def ajouter(id_: str, ce_qu_on_verifie: str, attendu: str, obtenu: str, ok: bool) -> None:
        out.append({"id": id_, "equation": f"EQ-{id_[1:]}", "verifie": ce_qu_on_verifie,
                    "attendu": attendu, "obtenu": obtenu, "ok": bool(ok)})

    s, rho, ch, pf, q, te, cat = (etat["semences"], etat["rho"], etat["chaine"],
                                  etat["point_fixe"], etat["queue"], etat["telescage"],
                                  etat["catalogue"])
    g, ea, eo, be = (etat["graphe"], etat["antecedent_eau"], etat["ecarts_ouverts"],
                     etat["bande_epsilon"])
    ajouter("C01", "les semences importées valent exactement les rationnels utilisés",
            "5/5 égaux, D non vide",
            f"{sum(1 for v in [k for k, x in s['exactitude_float']['ecarts'].items() if x == 0.0])}/5 "
            f"à zéro écart · non_vide {s['domaine_D']['non_vide']}",
            s["exactitude_float"]["tous_egaux"] and s["domaine_D"]["non_vide"])
    ajouter("C02", "ρ est encadré des deux côtés par des comparaisons d'entiers",
            "deux preuves vraies, 0 < ρ < 1",
            f"bas {rho['preuve']['rho_superieur_a_bas']} · haut "
            f"{rho['preuve']['rho_inferieur_ou_egal_a_haut']} · contraction "
            f"{rho['conclusion']['contraction']}",
            rho["preuve"]["rho_superieur_a_bas"] and rho["preuve"]["rho_inferieur_ou_egal_a_haut"]
            and rho["conclusion"]["contraction"])
    ajouter("C03", "les rapports consécutifs du catalogue public sont constants à la dérive "
                   "d'arrondi près",
            "dérive ≤ 5·10^-9",
            f"dérive max {cat['derive_maximale']} · rapports [{cat['rapports_consecutifs_min'][:12]} ; "
            f"{cat['rapports_consecutifs_max'][:12]}]",
            float(cat["derive_maximale"]) <= 5e-9)
    ajouter("C04", "l'octave duale est l'octave publique times la constante déclarée",
            "quotient constant à la dérive d'arrondi près",
            f"quotients [{cat['quotients_dual_sur_public_min'][:14]} ; "
            f"{cat['quotients_dual_sur_public_max'][:14]}] · constante {cat['facteur_dual_fraction']}",
            abs(float(cat["quotients_dual_sur_public_max"])
                - float(cat["quotients_dual_sur_public_min"])) < 1e-6)
    ajouter("C05", "la décroissance et la positivité de la chaîne sont conclues par des entiers",
            "400 > 249, 64 comparisons entières vraies, bornes positives",
            f"decroissante {ch['ordre_entier']['strictement_decroissante']} · stricte sur 64 pas "
            f"{ch['ordre_entier']['stricte']} · positive {ch['ordre_entier']['positive_partout']}",
            ch["ordre_entier"]["strictement_decroissante"] and ch["ordre_entier"]["stricte"]
            and ch["ordre_entier"]["positive_partout"])
    ajouter("C06", "le télescopage tombe sur la différence des bords",
            "écart < 10^-52",
            f"écart {te['ecart_absolu']} · somme {te['somme_des_sauts'][:22]} · "
            f"identité {te['identique']}", te["identique"])
    ajouter("C07", "le pas de bascule est prouvé exactement des deux côtés",
            "x_41 ≥ 61/500 et x_42 < 61/500, par entiers",
            f"n* {ch['pas_de_sortie']} · signe avant {ch['voisinage']['k_avant']['ecart_signe']} · "
            f"signe après {ch['voisinage']['k_premier']['ecart_signe']}",
            ch["pas_de_sortie"] == 42 and ch["voisinage"]["k_avant"]["ecart_signe"] >= 0
            and ch["voisinage"]["k_premier"]["ecart_signe"] < 0)
    ajouter("C08", "la queue est encadrée par les bornes rationnelles issues de ρ",
            "valeur entre les deux bornes",
            f"n {q['n']} · valide {q['encadrement_valide']} · valeur {q['valeur_decimal'][:20]}",
            q["encadrement_valide"])
    ajouter("C09", "l'énumération de la grille ne laisse qu'un seul point fixe, la borne basse",
            "la liste des fixes est exactement ['61/500']",
            f"fixes trouvés {pf['candidats_fixes_sur_grille']} · attente ['61/500']",
            pf["candidats_fixes_sur_grille"] == ["61/500"])
    ajouter("C10", "tous les nœuds déclarés sont dans D et s'absorbent en au plus 42 pas",
            "aucun départ hors D, absorption ≤ 42",
            f"hors D {pf['depts_hors_D'] or 'aucun'} · absorption max "
            f"{pf['absorption_maximale']}",
            not pf["depts_hors_D"] and pf["absorption_maximale"] <= 42)
    ajouter("C11", "le graphe de la couche ne laisse aucun module porteur manquant et aucun import "
                   "tiers",
            "0 absent, 0 import tiers",
            f"absents {g['modules_absents'] or 'aucun'} · tiers {g['tiers_par_dossier'] or 'aucun'}",
            not g["modules_absents"] and not g["tiers_par_dossier"])
    ajouter("C12", "l'antécédent de l'eau est re-dérivé en rationnels, produit par produit",
            "tous les S_i·v_i égaux à Q, et la somme égale à 3Q",
            f"identique {ea['identique_al_debit']} · produits {ea['produits']} · "
            f"somme {ea['somme_des_produits']} = 3Q {ea['somme_est_triple_debit']}",
            ea["identique_al_debit"] and ea["somme_est_triple_debit"])
    ajouter("C13", "les croix du plan global sont toujours là, et comptées",
            "plus de 0 ligne à croix, aucune requalifiée",
            f"{eo['lignes_a_croix']} croix · {eo['coches']} coches · "
            f"goulots {eo['goulots']}", eo["lignes_a_croix"] > 0)
    ajouter("C14", "la chaîne des deux ε est exacte en rationnels",
            "MIZAN−ε=PLAFOND et PLAFOND−ε=COMBLE",
            f"{be['chaine_des_deux_eps']} · span {be['span']}", be["chaine_des_deux_eps"])
    ajouter("C15", "deux exécutions de resoudre() produisent la même empreinte",
            "empreintes identiques",
            f"{etat['rejoue_identique']} · {etat['empreinte_execution'][:16]}…",
            etat["rejoue_identique"])
    return out


def canonique(objet: Any) -> bytes:
    return json.dumps(objet, ensure_ascii=False, sort_keys=True,
                      default=str).encode("utf-8")


def noeuds_certificat() -> Dict[str, Any]:
    """Tout ce qui entre dans l'empreinte : calculs purs, aucun nombre d'hôte."""
    return {"semences": semences(), "rho": encadrement_rho(5), "chaine": chaine_m(43),
            "point_fixe": point_fixe(), "queue": queue(42), "telescage": telescage(42),
            "catalogue": catalogue_contraction(), "graphe": graphe_couche(),
            "antecedent_eau": antecedent_eau(), "ecarts_ouverts": ecarts_ouverts(),
            "bande_epsilon": bande_epsilon()}


def etat_complet() -> Dict[str, Any]:
    nc = noeuds_certificat()
    octets = canonique(nc)
    second = canonique(noeuds_certificat())
    return {"semences": nc["semences"], "rho": nc["rho"], "chaine": nc["chaine"],
            "point_fixe": nc["point_fixe"], "queue": nc["queue"],
            "telescage": nc["telescage"], "catalogue": nc["catalogue"],
            "graphe": nc["graphe"], "antecedent_eau": nc["antecedent_eau"],
            "ecarts_ouverts": nc["ecarts_ouverts"], "bande_epsilon": nc["bande_epsilon"],
            "noeuds_certificat": nc,
            "empreinte_execution": hashlib.sha256(octets).hexdigest(),
            "rejoue_identique": octets == second,
            "taille_octets": len(octets)}


def certificat() -> Dict[str, Any]:
    etat = etat_complet()
    return {"source": SOURCE, **etat["noeuds_certificat"],
            "empreinte_execution": etat["empreinte_execution"],
            "rejoue_identique": etat["rejoue_identique"],
            "limites": [
                "le théorème porte sur une application déclarée sur un intervalle déclaré : il "
                "s'applique au catalogue du dépôt, pas à la propagation du savoir humain",
                "les semences (0.6225, 0.122, 0.021) sont des constantes de conception de "
                "lib_almizan_extension.py ; rien dans ce dossier montre qu'elles mesurent quelque "
                "chose",
                "les 42 pas sont un compte d'itérations : ni une durée, ni une portée, ni une "
                "prévision",
                "le catalogue est stocké arrondi (8 et 6 décimales) : les dérives mesurées sont "
                "des défauts d'écriture du catalogue, pas des réfutations",
                "aucune des croix du plan global n'est remplie par cette couche",
            ],
            "attribution": {"auteur": SOURCE["auteur"],
                            "statut_de_la_demande": "déclaré · non vérifié pour toute portée "
                                                    "hors du dépôt"},
            "racine_merkle_sha256": hashlib.sha256(canonique(
                {c: hashlib.sha256(canonique(etat["noeuds_certificat"][c])).hexdigest()
                 for c in sorted(etat["noeuds_certificat"])})).hexdigest()}


def resoudre() -> Dict[str, Any]:
    cert = certificat()
    etat = {"semences": cert["semences"], "rho": cert["rho"], "chaine": cert["chaine"],
            "point_fixe": cert["point_fixe"], "queue": cert["queue"],
            "telescage": cert["telescage"], "catalogue": cert["catalogue"],
            "graphe": cert["graphe"], "antecedent_eau": cert["antecedent_eau"],
            "ecarts_ouverts": cert["ecarts_ouverts"], "bande_epsilon": cert["bande_epsilon"],
            "empreinte_execution": cert["empreinte_execution"],
            "rejoue_identique": cert["rejoue_identique"]}
    eqs = {x["id"]: x for x in equations(etat)}
    cs = controles(eqs, etat)
    return {"source": SOURCE, "certificat": cert, "equations": list(eqs.values()),
            "controles": cs,
            "conclusion": {
                "controles_verts": sum(1 for c in cs if c["ok"]), "controles_total": len(cs),
                "equations": len(eqs),
                "statuts_par_label": {st: sum(1 for x in eqs.values() if x["statut"] == st)
                                      for st in ("OPÉRATIONNEL", "SIMULÉ", "SPÉCIFIÉ")},
                "enonce_theoreme": "sur D = [61/500 ; 249/400], la chaîne x_k = MIZAN·ρ^k avec "
                                   "ρ = (249/400)^(1/12) est strictement décroissante, sans perte "
                                   "ni création (télescopage exact), sort du domaine au pas 42, "
                                   "et son clampage converge vers l'unique point fixe 61/500 en "
                                   "au plus 42 pas",
                "pas_de_bascule": cert["chaine"]["pas_de_sortie"],
                "absorption_maximale": cert["point_fixe"]["absorption_maximale"],
                "croix_toujours_ouvertes": cert["ecarts_ouverts"]["lignes_a_croix"],
                "racine_merkle_sha256": cert["racine_merkle_sha256"]}}


def verifier(donnees: Dict[str, Any]) -> bool:
    return all(c["ok"] for c in donnees["controles"])


def octets_csv_fr(lignes: List[List[Any]]) -> bytes:
    tete = "\r\n".join(";".join(str(v).replace(".", ",") for v in ligne) for ligne in lignes)
    return b"\xef\xbb\xbf" + (tete + "\r\n").encode("utf-8")


def ecrire_artefacts(cert: Dict[str, Any], vers: Path = ARTEFACTS) -> Dict[str, str]:
    vers.mkdir(parents=True, exist_ok=True)
    lignes = [["pas", "x_k_sur_MIZAN", "dans_D", "comparaison_entiere_signe"]]
    for c in cert["chaine"]["table"]:
        lignes.append([c["k"], f"{c['k']}×ρ", "OUI" if not c["sortie_de_D"] else "NON",
                       c["ecart_signe"]])
    rendu = {"certificat.json": octets_json(cert),
             "chaine_de_pas.csv": octets_csv_fr(lignes),
             "enonce_theoreme.md": enonce_markdown(cert)}
    for nom, octets in rendu.items():
        (vers / nom).write_bytes(octets)
    return {nom: f"{len(octets)} octets" for nom, octets in rendu.items()}


def octets_json(cert: Dict[str, Any]) -> bytes:
    return (json.dumps(cert, ensure_ascii=False, indent=2, sort_keys=True,
                       default=str) + "\n").encode("utf-8")


def enonce_markdown(cert: Dict[str, Any]) -> bytes:
    ch, pf = cert["chaine"], cert["point_fixe"]
    corps = [
        "# CONTINUITÉ — énoncé, cheminement, résultat",
        "",
        f"**Domaine déclaré** D = [{ch['bornes_D']['basse']} ; {ch['bornes_D']['haute']}]",
        f"**Rapport de contraction** ρ = (249/400)^(1/12) ∈ [{cert['rho']['inferieur']} ; "
        f"{cert['rho']['superieur']}]",
        "",
        "## Cheminement",
        "",
        "1. les semences sont importées de `lib_almizan_extension.py`, puis écrites en rationnels ;",
        "2. ρ est encadré par recherche dichotome sur des douzièmes puissances entières ;",
        "3. la chaîne x_k = MIZAN·ρ^k est strictement décroissante et minorée par 0 ;",
        "4. le télescopage Σ(x_{k−1} − x_k) = x_0 − x_N prouve qu'aucune valeur n'apparaît ni "
        "disparaît le long de la chaîne ;",
        f"5. la chaîne sort de D au pas {ch['pas_de_sortie']} (prouvé par entiers aux pas "
        f"{ch['pas_de_sortie'] - 1} et {ch['pas_de_sortie']}) ;",
        f"6. clampée sur D, elle converge vers l'unique point fixe {pf['point_fixe']} en au plus "
        f"{pf['absorption_maximale']} pas depuis n'importe lequel des "
        f"{len(pf['absorptions_par_noeud'])} nœuds déclarés.",
        "",
        "## Résultat",
        "",
        "La continuité de cette chaîne est **entière, sans perte, et bornée** : elle ne peut pas "
        "se poursuivre au-delà de son propre domaine. Le nombre de pas disponibles — 42 — est "
        "une conséquence calculée, pas une décision.",
        "",
        "## Ce que cela ne dit pas",
        "",
        *[f"- {l}" for l in cert["limites"]],
    ]
    return ("\n".join(corps) + "\n").encode("utf-8")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    donnees = resoudre()
    if "--ecrit" in sys.argv[1:]:
        donnees["artefacts"] = ecrire_artefacts(donnees["certificat"])
    sortie = {
        "source": donnees["source"],
        "theoreme": donnees["conclusion"]["enonce_theoreme"],
        "rho_encadre": {k: donnees["certificat"]["rho"][k]
                        for k in ("inferieur", "superieur", "largeur_encadrement")},
        "pas_de_bascule": donnees["conclusion"]["pas_de_bascule"],
        "absorption_maximale": donnees["conclusion"]["absorption_maximale"],
        "queue_encadree": donnees["certificat"]["queue"],
        "telescage": donnees["certificat"]["telescage"],
        "catalogue": {k: donnees["certificat"]["catalogue"][k] for k in
                      ("rho_exact", "derive_maximale", "facteur_dual_fraction")},
        "graphe": donnees["certificat"]["graphe"],
        "ecarts_ouverts": donnees["conclusion"]["croix_toujours_ouvertes"],
        "limites": donnees["certificat"]["limites"],
        "racine_merkle_sha256": donnees["conclusion"]["racine_merkle_sha256"],
        "controles": donnees["controles"],
        "equations": [{k: v for k, v in x.items() if k != "detail"} for x in donnees["equations"]],
        "conclusion": donnees["conclusion"],
        "artefacts": donnees.get("artefacts", {}),
    }
    print(json.dumps(sortie, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    sys.exit(0 if verifier(donnees) else 1)
