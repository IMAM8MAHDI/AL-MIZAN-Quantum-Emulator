# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""HORLOGERIE — certificats exacts de l'horloge du kernel, et ce qu'ils ne disent pas.

Point de départ du lot : « AI Proved His 18-Year-Old Conjecture. He Hasn't Understood It
Yet. », Adem B10, 593 s, identifiant YouTube `qa8IsnneG0c`. La page watch ne rend que du
JavaScript d'amorçage et timedtext répond sans contenu : le transcript est tenu pour absent.
La vidéo fournit huit titres horodatés, recopiés mot pour mot dans `SOURCE`, et rien de plus :
aucun chiffre, aucune phrase, aucun résultat de ce dossier ne vient d'elle. Ce qui en vient est
une décision de forme — un certificat doit se lire SANS faire confiance à celui qui l'a produit
— et cette décision est prise ici, pas citée.

Le dossier répond à une objection précise, adressée à AL-MIZAN le 2026-11-09 :

    « dx + dy + dz = dt est arithmétiquement exact, mais 365,25 / 354 / 360 jours ne sont pas
      des périodes astronomiques mesurées ; et écrire dt ≈ 135 097 021,3359375 Hz suppose une
      période de 7,4 ns que la machine ne respecte pas. »

Ce que fait ce module, dans l'ordre :

  1. il certifie l'arithmétique — les quatre nombres, en entiers, à partir des seules semences
     déclarées par le dépôt, sans jamais se servir d'un flottant pour conclure (EQ-01 à EQ-06) ;
  2. il écrit la conséquence numérique de l'hypothèse « hertz », en décimale exacte (EQ-07) ;
  3. il gèle trois seuils AVANT de lire le ciel, puis confronte les trois cycles déclarés aux
     éphémérides publiques ; le verdict est rendu tel quel, y compris quand il est défavorable
     (EQ-08 à EQ-11) ;
  4. il mesure le rythme réel d'un tick sur la machine hôte (EQ-12) ;
  5. il recolle le certificat aux trois endroits du dépôt qui énoncent ces nombres, puis au
     vérificateur autonome qui les relit sans rien importer du dépôt (EQ-13, EQ-14).

Ce qu'il ne fait pas : il ne décrète pas qu'AL-MIZAN prévoit une fréquence d'horloge, ne
convertit pas une convention de calendrier en période mesurée, ne retouche pas la capsule
`horloge_noyau/` (lecture seule) et n'attribue aucune portée universelle au temps mesuré.

Usage :
    py -3 HORLOGERIE/horlogerie.py                 # 15 équations, 15 contrôles, rc=0 ou 1
    py -3 HORLOGERIE/horlogerie.py --ecrit         # + certificats.json et le CSV français
    py -3 HORLOGERIE/verifier_certificats.py       # relit le certificat, zéro import du dépôt
    py -3 HORLOGERIE/calibrer_horloge_almizan.py --ticks 10000 --series 7
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import sys
from decimal import Decimal, getcontext
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List

RACINE = Path(__file__).resolve().parents[1]
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

DOSSIER = Path(__file__).resolve().parent
ARTEFACTS = DOSSIER / "artefacts"
CERTIFICAT = ARTEFACTS / "certificats.json"
CSV_ASTRO = ARTEFACTS / "confrontation_astronomique.csv"
VERIFICATEUR = DOSSIER / "verifier_certificats.py"
ACTE_A134 = (RACINE / "horloge_noyau" / "actes"
             / "almizan_acte_a134_zero_expansion_matrice_complexe.json")
ACTE_A136 = (RACINE / "horloge_noyau" / "actes"
             / "almizan_acte_a136_horloge_deduite_du_noyau.json")

PRECISION = 40          # rangs décimaux de la période : fixés, pas laissés au contexte par défaut

SOURCE: Dict[str, Any] = {
    "titre": "AI Proved His 18-Year-Old Conjecture. He Hasn't Understood It Yet.",
    "chaine": "Adem B10",
    "video_id": "qa8IsnneG0c",
    "url": "https://www.youtube.com/watch?v=qa8IsnneG0c",
    "duree_s": 593,
    "chapitres_publics": 8,
    "chapitres_verbatims": [
        {"debut": "0:00", "titre": "\"I believe the proof is correct\""},
        {"debut": "1:08", "titre": "Cups, looks and a quantum computer"},
        {"debut": "2:15", "titre": "The dial and the switch that matters"},
        {"debut": "3:23", "titre": "The 2019 proof that failed"},
        {"debut": "3:58", "titre": "Reason one: the Lean certificate"},
        {"debut": "5:12", "titre": "Reason two: the humans"},
        {"debut": "6:12", "titre": "Is quantum supremacy dead?"},
        {"debut": "8:58", "titre": "How Aaronson feels"},
    ],
    "transcript": "absent (timedtext : 0 octet en json3, srv3 et xml)",
    "mesure_le": "2026-11-09T15:32:44Z",
    "outils": "scripts/extraire_chapitres_youtube.py "
              "(Skill extraire-chapitres-youtube-sans-transcript)",
    "avertissements_sonde": [
        "aucun en-tete de chapitres : horodatages pris dans toute la description",
        "timedtext repond sans contenu : le transcript est tenu pour absent",
    ],
    "sonde_transcript_octets": {"json3": 0, "srv3": 0, "xml": 0},
    "ce_que_la_video_n_a_pas_fourni": [
        "aucun transcript : donc aucune citation, aucune phrase attribuée à la bande-son",
        "aucun nombre : ni borne, ni délai, ni taux de réussite d'une preuve automatique",
        "aucune mention d'AL-MIZAN, que la vidéo ne nomme pas",
    ],
    "principe_repris_ici": "séparer celui qui produit la preuve de celui qui la vérifie : le "
                           "certificat s'écrit avec le dépôt et se relit sans lui. C'est une "
                           "décision de ce dossier, pas une citation de la vidéo.",
}

# ─── 1. Les semences déclarées du dépôt ---------------------------------------

SEMENCES: Dict[str, Dict[str, str]] = {
    "soleil": {"annee_h": "8766", "mois_h": "1461/2", "semaine_h": "168"},
    "lune": {"annee_h": "8496", "mois_h": "708", "semaine_h": "168"},
    "terre": {"annee_h": "8640", "mois_h": "720", "semaine_h": "144"},
}
NIVEAUX: Dict[str, List[str]] = {
    "celeste": ["5/2", "3/2", "3/2", "24/60"],
    "terre_brut": ["300", "50", "30", "24/60"],
    "terre_normalise": ["216000", "250", "5/2"],
}
FORMULES: Dict[str, str] = {
    "celeste": "(c1·A/12) · (c2·M/S) · (c3·S/24) · c4, avec A l'année en heures, M le mois, "
               "S la semaine",
    "terre_brut": "même produit sur les semences de la Terre, coefficients 300 · 50 · 30 · 24/60",
    "terre_normalise": "216 000 · 250 · 5/2 — les deux premiers niveaux du brut, puis l'ancre "
                       "de force 5/2 sur l'axe numérique de LA TABLE",
    "somme": "dt = dx + dy + dz",
}


def F(x: Any) -> Fraction:
    """Un rationnel exact depuis une chaîne « n » ou « n/d », un entier ou un Fraction."""
    return x if isinstance(x, Fraction) else Fraction(str(x))


def D(x: str) -> Fraction:
    """Une décimale citée à la française (« 365,25 ») ramenée au rationnel exact."""
    return Fraction(str(x).replace(",", "."))


def semences() -> Dict[str, Dict[str, Fraction]]:
    return {astre: {nom: F(v) for nom, v in clefs.items()}
            for astre, clefs in SEMENCES.items()}


def produit_quatre_niveaux(annee_h: Fraction, mois_h: Fraction, semaine_h: Fraction,
                           coefficients: List[str]) -> Fraction:
    c1, c2, c3, c4 = (F(c) for c in coefficients)
    return (c1 * annee_h / 12) * (c2 * mois_h / semaine_h) * (c3 * semaine_h / 24) * c4


def rationnaux() -> Dict[str, Fraction]:
    s = semences()
    dx = produit_quatre_niveaux(s["soleil"]["annee_h"], s["soleil"]["mois_h"],
                                s["soleil"]["semaine_h"], NIVEAUX["celeste"])
    dy = produit_quatre_niveaux(s["lune"]["annee_h"], s["lune"]["mois_h"],
                                s["lune"]["semaine_h"], NIVEAUX["celeste"])
    dz = F(NIVEAUX["terre_normalise"][0]) * F(NIVEAUX["terre_normalise"][1]) \
        * F(NIVEAUX["terre_normalise"][2])
    dz_brut = produit_quatre_niveaux(s["terre"]["annee_h"], s["terre"]["mois_h"],
                                     s["terre"]["semaine_h"], NIVEAUX["terre_brut"])
    return {"dx": dx, "dy": dy, "dz": dz, "dz_brut": dz_brut, "dt": dx + dy + dz}


# ─── 2. Ciel public, seuils gelés avant toute lecture -------------------------

SEUILS: Dict[str, Any] = {
    "conforme_s_par_an": 60,
    "signale_s_par_an": 3600,
    "gele_le": "2026-11-09T15:32:44Z",
    "enonce": "CONFORME si |écart| ≤ 60 s par an ; ÉCART SIGNALÉ si 60 < |écart| ≤ 3 600 s ; "
              "HORS TOLÉRANCE au-delà",
    "justification": "une période invoquée pour régler une horloge doit suivre le calendrier "
                     "qu'elle prétend décrire à la minute près sur un an ; sous 60 s par an "
                     "l'écart ne se voit pas, au-delà d'une heure par an il se voit dans la "
                     "saison",
    "correction_apportee": "2026-11-09 : la fraction de lunaisons_12 était écrite 8884173/25000 "
                           "(= 355,36692 d), ce que ne donnait pas sa propre source « 12 × "
                           "29,53059 ». Elle est réécrite 8859177/25000 (= 354,36708 d) et "
                           "l'identité 12 × lunaison = lunaisons_12 est devenue un contrôle, "
                           "C15 côté production et V16 côté vérificateur : une référence citée "
                           "depuis une autre ne peut plus se tromper silencieusement",
}

REFERENCES: List[Dict[str, str]] = [
    {"id": "annee_julienne", "jours": "1461/4", "decite": "365,25", "nature": "définition exacte",
     "source": "Union astronomique internationale, Résolution B2 (2009) : l'année julienne vaut "
               "365,25 jours exactement, soit 31 557 600 s"},
    {"id": "annee_tropique", "jours": "1826211/5000", "decite": "365,2422", "nature": "éphéméride mesurée",
     "source": "NASA Glenn Research Center, Planetary Fact Sheet — Earth : 365,2422 jours "
               "(moyenne tropique)"},
    {"id": "annee_tropique_2000", "jours": "36524219/100000", "decite": "365,24219", "nature": "éphéméride mesurée",
     "source": "Wikipedia, Tropical year : 365,24219 ephemeris days à l'équinoxe J2000"},
    {"id": "lunaison", "jours": "2953059/100000", "decite": "29,53059", "nature": "éphéméride mesurée",
     "source": "Explanatory Supplement to the Astronomical Almanac — mois synodique moyen "
               "29,53059 d"},
    {"id": "lunaisons_12", "jours": "8859177/25000", "decite": "354,36708", "nature": "éphéméride mesurée",
     "source": "12 × mois synodique moyen (ligne précédente) = 354,36708 d"},
    {"id": "annee_lunaire_civile", "jours": "354", "decite": "354", "nature": "convention de calendrier",
     "source": "année lunaire de douze mois de 29 ou 30 jours — 354 jours, convention civile"},
]

CYCLES_DECLARES: List[Dict[str, str]] = [
    {"id": "Soleil", "jours": "1461/4", "heures": "8766", "constant": "dx",
     "attendu": "365,25 j est l'année julienne (définition de l'UAI), pas l'année tropique "
                "(mesure)"},
    {"id": "Lune", "jours": "354", "heures": "8496", "constant": "dy",
     "attendu": "354 j est l'année lunaire civile (12 × 29,5), pas douze lunaisons moyennes"},
    {"id": "Terre", "jours": "360", "heures": "8640", "constant": "dz",
     "attendu": "360 j n'est la période de rien : c'est une base de calcul"},
]

# Les neuf paires sont écrites AVANT tout calcul, et gelées avec les seuils par empreinte.
PAIRES: List[Dict[str, str]] = [
    {"cycle": "Soleil", "reference": "annee_julienne"},
    {"cycle": "Soleil", "reference": "annee_tropique"},
    {"cycle": "Soleil", "reference": "annee_tropique_2000"},
    {"cycle": "Lune", "reference": "annee_lunaire_civile"},
    {"cycle": "Lune", "reference": "lunaisons_12"},
    {"cycle": "Lune", "reference": "annee_tropique"},
    {"cycle": "Terre", "reference": "annee_julienne"},
    {"cycle": "Terre", "reference": "annee_tropique"},
    {"cycle": "Terre", "reference": "lunaisons_12"},
]

VERDICTS = ("CONFORME", "ÉCART SIGNALÉ", "HORS TOLÉRANCE")
PIRE = {v: i for i, v in enumerate(VERDICTS)}


def verdict(ecart_s: Fraction) -> str:
    a = abs(ecart_s)
    if a <= F(SEUILS["conforme_s_par_an"]):
        return "CONFORME"
    if a <= F(SEUILS["signale_s_par_an"]):
        return "ÉCART SIGNALÉ"
    return "HORS TOLÉRANCE"


def canonique(objet: Any) -> bytes:
    return json.dumps(objet, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def sensibilite() -> Dict[str, Any]:
    """La conclusion survit-elle au doute sur la sixième décimale de la lunaison ?"""
    variante = F("29530588/1000000")          # 29,530588 d : autre valeur publiée
    ecart = (F("354") - 12 * variante) * 86400
    return {"question": "et si le mois synodique valait 29,530588 d au lieu de 29,53059 d",
            "lunaison_alternee": "29530588/1000000",
            "ecart_s_par_an": f"{ecart.numerator}/{ecart.denominator}",
            "verdict": verdict(ecart),
            "conclusion": "le verdict ne change pas : le seuil est franchi par plus de deux "
                          "ordres de grandeur, la sixième décimale n'y peut rien"}


def coherence_des_sources() -> Dict[str, Any]:
    """Les références qui se citent entre elles doivent se recouper en entiers.

    « lunaisons_12 » n'est pas une mesure indépendante : son énoncé dit 12 × mois synodique.
    Cette identité est le seul endroit du dossier où une référence dépend d'une autre ; si elle
    bouge, le contrôle tombe au lieu de déplacer un écart sans que rien ne le signale.
    """
    refs = {r["id"]: F(r["jours"]) for r in REFERENCES}
    testes = [
        {"enonce": "lunaisons_12 = 12 × lunaison",
         "gauche": f"{refs['lunaisons_12'].numerator}/{refs['lunaisons_12'].denominator}",
         "droite": f"{(12 * refs['lunaison']).numerator}/"
                   f"{(12 * refs['lunaison']).denominator}",
         "vraie": refs["lunaisons_12"] == 12 * refs["lunaison"]},
        {"enonce": "pour chaque référence, la fraction du fichier est la décimale citée",
         "gauche": " · ".join(f"{r['id']}={refs[r['id']]}" for r in REFERENCES),
         "droite": " · ".join(f"{r['id']}={D(r['decite'])}" for r in REFERENCES),
         "vraie": all(refs[r["id"]] == D(r["decite"]) for r in REFERENCES)},
    ]
    return {"identites": testes, "fausses": [x["enonce"] for x in testes if not x["vraie"]],
            "portee": "une identité entre deux lignes citées du même dossier ; elle ne dit rien "
                      "du ciel, elle dit que la citation est cohérente avec sa source"}


def confrontation() -> Dict[str, Any]:
    refs = {r["id"]: r for r in REFERENCES}
    resultats = []
    for p in PAIRES:
        cycle = next(c for c in CYCLES_DECLARES if c["id"] == p["cycle"])
        ref = refs[p["reference"]]
        ecart = (F(cycle["jours"]) - F(ref["jours"])) * 86400
        resultats.append({"cycle": p["cycle"], "reference": p["reference"],
                          "nature_reference": ref["nature"], "source_reference": ref["source"],
                          "declare_jours": cycle["jours"], "reference_jours": ref["jours"],
                          "ecart_s_par_an": f"{ecart.numerator}/{ecart.denominator}",
                          "ecart_s_arrondi": round(float(ecart), 3),
                          "verdict": verdict(ecart)})
    par_cycle: Dict[str, Dict[str, Any]] = {}
    for cycle in CYCLES_DECLARES:
        siennes = [x for x in resultats if x["cycle"] == cycle["id"]]
        pire = max(siennes, key=lambda x: PIRE[x["verdict"]])
        mesurées = [x for x in siennes if x["nature_reference"] == "éphéméride mesurée"]
        par_cycle[cycle["id"]] = {
            "constante": cycle["constant"], "jours": cycle["jours"], "heures": cycle["heures"],
            "attendu": cycle["attendu"], "verdict": pire["verdict"],
            "face_a": pire["reference"], "paires": len(siennes),
            "ephemerides_mesurees": len(mesurées),
            "verdict_sur_ephemeride": max((x["verdict"] for x in mesurées),
                                          key=lambda v: PIRE[v], default="aucune"),
            "ecart_max_s": max(abs(x["ecart_s_arrondi"]) for x in mesurées) if mesurées else 0.0,
        }
    gel = hashlib.sha256(canonique({"seuils": SEUILS, "references": REFERENCES,
                                    "cycles": CYCLES_DECLARES, "paires": PAIRES})).hexdigest()
    return {"seuils": SEUILS, "references": REFERENCES, "cycles_declares": CYCLES_DECLARES,
            "paires": PAIRES, "resultats": resultats, "par_cycle": par_cycle,
            "coherence_des_sources": coherence_des_sources(),
            "empreinte_du_gel": gel, "sensibilite": sensibilite(),
            "conclusion": "sur les six comparaisons à une éphéméride MESURÉE, aucune ne tombe "
                          "sous les 60 s par an : aucun des trois cycles déclarés ne reproduit "
                          "la période astronomique qu'il nomme. En revanche 365,25 j est "
                          "exactement l'année julienne définie par l'UAI et 354 j exactement "
                          "l'année lunaire civile : ce sont des calendriers, pas des mesures."}


def periode_ns() -> Dict[str, Any]:
    getcontext().prec = PRECISION
    dt = rationnaux()["dt"]
    return {"hypothese": "dt serait une fréquence en s⁻¹ — c'est ainsi que les actes A134 et "
                         "A136 l'écrivent (« Hz »)",
            "fraction": f"{dt.denominator * 10 ** 9}/{dt.numerator}",
            "valeur_ns": str(Decimal(dt.denominator * 10 ** 9) / Decimal(dt.numerator)),
            "flottant": float(F(dt.denominator * 10 ** 9) / dt.numerator),
            "statut": "conséquence arithmétique d'une hypothèse de lecture : le dépôt n'observe "
                      "aucun compteur de cycles par seconde"}


def sources_du_depot(cert: Dict[str, Any]) -> Dict[str, Any]:
    """Ce que le dépôt pose lui-même sur la table — trois endroits, un seul nombre."""
    from bibliotheques import lib_informe, lib_temporelle as LT

    table = lib_informe.MatriceLogiqueComplexe.calculer_cycles_trinite_depuis_zero()
    clefs = {"dx": table["cycles_distincts"]["soleil_dx"],
             "dy": table["cycles_distincts"]["lune_dy"],
             "dz": table["cycles_distincts"]["terre_dz"],
             "dt": table["synchronisation_harmonique"]["porteur_dt"]}
    a136 = json.loads(ACTE_A136.read_text(encoding="utf-8"))["constantes_deduites"]
    a134 = json.loads(ACTE_A134.read_text(encoding="utf-8"))["expansion"]["3_cycles_trinite"]
    return {
        "lib_temporelle": {"CLOCK_DX_SOLEIL": LT.CLOCK_DX_SOLEIL,
                           "CLOCK_DY_LUNE": LT.CLOCK_DY_LUNE, "CLOCK_DZ_TERRE": LT.CLOCK_DZ_TERRE,
                           "CLOCK_DZ_TERRE_BRUT": LT.CLOCK_DZ_TERRE_BRUT,
                           "CLOCK_DT_KERNEL": LT.CLOCK_DT_KERNEL},
        "lib_informe": {k: {"fraction": v["valeur_exacte_fraction"], "valeur": v["valeur_hz"],
                            "periode_ns": v.get("periode_ns")} for k, v in clefs.items()},
        "acte_a136_scelle": dict(a136),
        "acte_a134_scelle": {k: v for k, v in a134.items() if isinstance(v, str)},
        "concordance": float(cert["rationnels"]["dt"]["flottant"]) == LT.CLOCK_DT_KERNEL
                       == a136["dt_kernel"] == clefs["dt"]["valeur_hz"],
    }


def mesure_rythme() -> Dict[str, Any]:
    from HORLOGERIE.calibrer_horloge_almizan import mesurer

    m = mesurer(ticks=5_000, series=5)
    periode = periode_ns()["flottant"]
    return {
        "tau_mediane_ns": m["mediane_ns"], "tau_min_ns": m["minimum_ns"],
        "tau_max_ns": m["maximum_ns"], "tau_eam_ns": m["ecart_absolu_median_ns"],
        "serie_de": m["ticks_par_serie"], "series": m["series"],
        "periode_hypothetique_ns": periode,
        "ratio_tau_sur_periode": m["mediane_ns"] / periode,
        "condition": "la lecture hertz tombe dès que τ > 2 × la période de 1/dt",
        "verdict_mesure": "LECTURE HERTZ RÉFUTÉE SUR CETTE MACHINE"
                          if m["mediane_ns"] > 2 * periode else
                          "LECTURE HERTZ NON RÉFUTÉE PAR CETTE MESURE",
        "hote": m["hote"], "formule": m["formule"], "portee": m["portee"],
    }


# ─── 3. Le certificat : déterministe, aucune mesure, aucun nombre d'hôte -------

def corps_certificat() -> Dict[str, Any]:
    r = rationnaux()
    rationnels = {nom: {"numerateur": f.numerator, "denominateur": f.denominator,
                        "flottant": repr(float(f)),
                        "reduit": math.gcd(f.numerator, f.denominator) == 1}
                  for nom, f in r.items()}
    dt, dx, dy, dz, brut = r["dt"], r["dx"], r["dy"], r["dz"], r["dz_brut"]
    somme = dx + dy + dz
    identites = [
        {"id": "somme", "enonce": "dt = dx + dy + dz",
         "second_membre": f"{somme.numerator}/{somme.denominator}",
         "produit_croise": f"{dt.numerator}×{somme.denominator} = {somme.numerator}×"
                           f"{dt.denominator} = {dt.numerator * somme.denominator}",
         "vraie": dt == somme},
        {"id": "normalisation", "enonce": "dz_brut = dz × 144/5",
         "rapport_brut_sur_normalise": f"{(brut / dz).numerator}/{(brut / dz).denominator}",
         "vraie": dz * Fraction(144, 5) == brut},
        {"id": "denominateur", "enonce": "128·dt est un entier impair : 2^7 est le plus petit "
                                         "dénominateur possible",
         "numerateur": dt.numerator, "denominateur": dt.denominator,
         "puissance_de_deux": int(math.log2(dt.denominator)),
         "numerateur_impair": dt.numerator % 2 == 1,
         "vraie": dt.denominator == 2 ** 7 and dt.numerator % 2 == 1},
    ]
    unites = {
        "lectures_rencontrees": [
            {"lieu": "horloge_noyau/actes/almizan_acte_a134_zero_expansion_matrice_complexe.json",
             "forme_verbatim": "dx_soleil ≈ 50027.8359375 Hz · dt = dx + dy + dz ≈ "
                               "135097021.3359375 Hz",
             "portee": "déclaration d'un acte scellé, lu en lecture seule : ce dossier ne "
                       "modifie pas la capsule horloge_noyau/"},
            {"lieu": "bibliotheques/lib_informe.py → porteur_dt.periode_ns",
             "forme_verbatim": repr(periode_ns()["flottant"]),
             "portee": "arithmétique 1/dt en nanosecondes : un nombre dérivé, pas une mesure"},
            {"lieu": "resultats/run_cycle_solaire_lunaire_terrestre_*.json → pulsation_dt_hz",
             "forme_verbatim": "135097021.3359375",
             "portee": "un champ nommé « hz » rempli par la constante du noyau, non par un "
                       "compteur de cycles par seconde"},
        ],
        "condition_de_refutation": "la lecture hertz tombe dès que le temps mesuré d'un tick "
                                   "dépasse 2 × la période ci-dessus ; la mesure est produite "
                                   "par calibrer_horloge_almizan.py, hors scellement",
        "lecture_retenue": "cycle logique",
        "enonce_retenu": "dt = 17 292 418 731/128 est un BUDGET DE COMPTES adimensionnel. Son "
                         "rythme d'exécution est une mesure dépendante de la machine ; sa "
                         "valeur est un rationnel exact qui ne dépend de rien.",
        "pourquoi_pas_hz": "une constante physique ne change pas du simple au double d'un "
                           "ordinateur à l'autre ; le temps par tick, si. La quantité qui porte "
                           "le nom de l'horloge n'est donc pas la cadence de la machine.",
    }
    return {"derivation": {"semences": SEMENCES, "niveaux": NIVEAUX, "formules": FORMULES},
            "rationnels": rationnels, "identites": identites, "periode": periode_ns(),
            "astronomie": confrontation(), "unites": unites}


def certificat() -> Dict[str, Any]:
    corps = corps_certificat()
    empreintes = {cle: hashlib.sha256(canonique(v)).hexdigest() for cle, v in corps.items()}
    return {"version": 1, "dossier": "HORLOGERIE",
            "objet": "certificat arithmétique de l'horloge du kernel AL-MIZAN, et portée de sa "
                     "lecture en unités de temps",
            "mode_emploi": "py -3 HORLOGERIE/verifier_certificats.py — se relit sans exécuter "
                           "une ligne du dépôt",
            "englobe": sorted(empreintes),
            **corps,
            "empreintes_souche": empreintes,
            "racine_merkle_sha256": hashlib.sha256(canonique(empreintes)).hexdigest(),
            "limites": [
                "le certificat porte l'arithmétique des nombres déclarés, jamais leur valeur de "
                "prévision : rien ici n'affirme qu'AL-MIZAN prédit une période astronomique",
                "les semences (8766 h, 8496 h, 8640 h) viennent du dépôt ; le certificat montre "
                "qu'elles produisent exactement les constantes publiées, pas qu'elles sont vraies",
                "les références astronomiques sont des valeurs publiques moyennes, citées avec "
                "leur source ; elles ne sont pas recalculées depuis une éphéméride du jour",
                "le rythme d'exécution est absent de ce fichier : il dépend de la machine et "
                "sort à part, hors scellement",
            ],
            "attribution": SOURCE}


# ─── 4. Équations et contrôles -------------------------------------------------

NOEUDS: Dict[str, Dict[str, Any]] = {
    "EQ-01": {"depend": [], "externe": ["bibliotheques/lib_temporelle.py",
                                        "horloge_noyau/ (lecture seule)"]},
    "EQ-02": {"depend": ["EQ-01"], "externe": []},
    "EQ-03": {"depend": ["EQ-01"], "externe": []},
    "EQ-04": {"depend": ["EQ-01"], "externe": []},
    "EQ-05": {"depend": ["EQ-02", "EQ-03", "EQ-04"], "externe": []},
    "EQ-06": {"depend": ["EQ-05"], "externe": []},
    "EQ-07": {"depend": ["EQ-05"], "externe": []},
    "EQ-08": {"depend": [], "externe": ["le choix de l'expérimentateur : trois seuils, une fois"]},
    "EQ-09": {"depend": ["EQ-08", "EQ-01"], "externe": ["NASA GRC", "UAI 2009", "Wikipedia"]},
    "EQ-10": {"depend": ["EQ-08", "EQ-01"],
              "externe": ["Explanatory Supplement to the Astronomical Almanac"]},
    "EQ-11": {"depend": ["EQ-08", "EQ-01"], "externe": ["NASA GRC", "UAI 2009"]},
    "EQ-12": {"depend": [], "externe": ["la machine hôte : time.perf_counter_ns"]},
    "EQ-13": {"depend": ["EQ-05", "EQ-07"],
              "externe": ["bibliotheques/lib_informe.py", "acte A136 scellé"]},
    "EQ-14": {"depend": ["EQ-13"], "externe": ["HORLOGERIE/verifier_certificats.py"]},
    "EQ-15": {"depend": ["EQ-08"],
              "externe": ["UAI 2009", "NASA GRC",
                          "Explanatory Supplement to the Astronomical Almanac"]},
}


def _eq(id_: str, chemin: str, formule: str, resultat: str, statut: str,
        limite: str, detail: Any) -> Dict[str, Any]:
    n = NOEUDS[id_]
    return {"id": id_, "chemin": chemin, "formule": formule, "resultat": resultat,
            "statut": statut, "limite": limite, "detail": detail,
            "couche": "S2 REGULARITE", "piliers": ["P1 UNITE", "P2 BORNE", "P3 CONFRONTATION",
                                                   "P4 TRANSMISSION"],
            "depend_de": n["depend"], "fonde_hors_du_dossier": n["externe"]}


def trouver(astro: Dict[str, Any], cycle: str, reference: str) -> Dict[str, Any]:
    return next(x for x in astro["resultats"]
                if x["cycle"] == cycle and x["reference"] == reference)


def equations(cert: Dict[str, Any], mesure: Dict[str, Any]) -> List[Dict[str, Any]]:
    r, ids = cert["rationnels"], {i["id"]: i for i in cert["identites"]}
    astro, par = cert["astronomie"], cert["astronomie"]["par_cycle"]
    s = semences()
    co = astro["coherence_des_sources"]
    return [
        _eq("EQ-01", "horlogerie.py → semences() → C01",
            "A, M, S ∈ ℚ par astre, et A/24 donne les jours déclarés",
            " · ".join(f"{a} {s[a]['annee_h']} h = {s[a]['annee_h'] / 24} j "
                       f"(mois {s[a]['mois_h']} h, semaine {s[a]['semaine_h']} h)"
                       for a in ("soleil", "lune", "terre")),
            "OPÉRATIONNEL",
            "les douze nombres d'entrée sont la déclaration du dépôt : le certificat ne dit pas "
            "qu'ils décrivent le ciel, il dit exactement ce qu'ils calculent", cert["derivation"]),
        _eq("EQ-02", "horlogerie.py → produit_quatre_niveaux() → C02",
            "dx = (5/2·8766/12)·(3/2·(1461/2)/168)·(3/2·168/24)·(24/60)",
            f"dx = {r['dx']['numerateur']}/{r['dx']['denominateur']} = {r['dx']['flottant']} · "
            f"réduite {r['dx']['reduit']}", "OPÉRATIONNEL",
            "égalité de deux rationnels : aucune tolérance n'intervient, et aucun flottant ne "
            "sert à conclure", r["dx"]),
        _eq("EQ-03", "horlogerie.py → produit_quatre_niveaux() → C03",
            "dy = (5/2·8496/12)·(3/2·708/168)·(3/2·168/24)·(24/60)",
            f"dy = {r['dy']['numerateur']}/{r['dy']['denominateur']} = {r['dy']['flottant']} · "
            f"réduite {r['dy']['reduit']}", "OPÉRATIONNEL",
            "la semaine de 168 h est commune au Soleil et à la Lune : le rapport dy/dx ne "
            "dépend donc que des mois et des années déclarés", r["dy"]),
        _eq("EQ-04", "horlogerie.py → rationnaux() → C04",
            "dz = 216 000·250·5/2 ; dz_brut = (300·8640/12)·(50·720/144)·(30·144/24)·(24/60)",
            f"dz = {r['dz']['numerateur']} · dz_brut = {r['dz_brut']['numerateur']} · rapport "
            f"{ids['normalisation']['rapport_brut_sur_normalise']}", "OPÉRATIONNEL",
            "dz est le seul des trois à tomber sur un entier : c'est de là que vient le poids "
            "du budget dans dt, et non d'une mesure", r["dz"]),
        _eq("EQ-05", "horlogerie.py → rationnaux() → C05",
            "dt = dx + dy + dz",
            f"{ids['somme']['second_membre']} = {r['dt']['flottant']} · produit croisé "
            f"{ids['somme']['produit_croise']} · vraie {ids['somme']['vraie']}", "OPÉRATIONNEL",
            "l'identité se vérifie par produit croisé d'entiers ; elle ne dit rien de la nature "
            "physique des trois termes additionnés", ids["somme"]),
        _eq("EQ-06", "horlogerie.py → corps_certificat() → C06",
            "den(dt) = 2^7 et num(dt) impair ⇒ fraction réduite et dénominateur minimal",
            f"num = {r['dt']['numerateur']} · den = {r['dt']['denominateur']} = "
            f"2^{ids['denominateur']['puissance_de_deux']} · impair "
            f"{ids['denominateur']['numerateur_impair']}", "OPÉRATIONNEL",
            "le numérateur n'est pas testé premier, seulement impair : c'est ce qu'il faut et "
            "ce qu'il suffit pour borner le dénominateur", ids["denominateur"]),
        _eq("EQ-07", "horlogerie.py → periode_ns() → C07",
            "si dt est une fréquence : 1/dt = 128·10^9/17 292 418 731 ns",
            f"{cert['periode']['valeur_ns'][:22]} ns sur {len(cert['periode']['valeur_ns'].replace('.', ''))} rangs",
            "SPÉCIFIÉ",
            "ce nombre est la conséquence d'une hypothèse de lecture, pas une mesure : le dépôt "
            "n'observe aucun compteur de cycles par seconde", cert["periode"]),
        _eq("EQ-08", "horlogerie.py → confrontation() → C08",
            "seuils gelés avant lecture : ≤ 60 s/an · ≤ 3 600 s/an · au-delà HORS TOLÉRANCE",
            f"gel {astro['seuils']['gele_le']} · empreinte {astro['empreinte_du_gel'][:16]}… · "
            f"{len(astro['paires'])} paires écrites à l'avance sur {len(astro['references'])} "
            f"références", "SPÉCIFIÉ",
            "le gel porte sur les seuils, les références et les paires — pas sur l'interprétation "
            "du ciel : trois nombres choisis ici, une fois, et publiés avec le verdict",
            astro["seuils"]),
        _eq("EQ-09", "horlogerie.py → confrontation() → C09",
            "Soleil 365,25 j contre année tropique 365,2422 j",
            f"écart {trouver(astro, 'Soleil', 'annee_tropique')['ecart_s_arrondi']} s/an · "
            f"{par['Soleil']['verdict']} (pire des trois) · CONFORME contre l'année julienne",
            "OPÉRATIONNEL",
            "l'écart compare un calendrier moyen à une éphéméride moyenne : il ne prononce rien "
            "sur l'équinoxe d'une année donnée", par["Soleil"]),
        _eq("EQ-10", "horlogerie.py → confrontation() → C10",
            "Lune 354 j contre douze lunaisons 354,36708 j",
            f"écart {trouver(astro, 'Lune', 'lunaisons_12')['ecart_s_arrondi']} s/an · "
            f"{par['Lune']['verdict']} · sous la variante 29,530588 d : "
            f"{astro['sensibilite']['verdict']}", "OPÉRATIONNEL",
            "la sensibilité teste la sixième décimale du mois synodique : si le verdict en "
            "dépendait, il faudrait le taire plutôt que l'afficher", astro["sensibilite"]),
        _eq("EQ-11", "horlogerie.py → confrontation() → C11",
            "Terre 360 j contre les trois références disponibles",
            f"{par['Terre']['verdict']} face à {par['Terre']['face_a']} · "
            f"{par['Terre']['paires']} comparaisons, écart maximal retenu "
            f"{par['Terre']['ecart_max_s']} s/an", "OPÉRATIONNEL",
            "360 jours reste une base de calcul parfaitement licite ; ce que le certificat "
            "refuse, c'est de la faire passer pour une mesure du ciel", par["Terre"]),
        _eq("EQ-12", "calibrer_horloge_almizan.py → mesurer() → C12",
            "τ = T/N sur consommer_tick(), cinq séries de cinq mille ticks",
            f"τ = {mesure['tau_mediane_ns']:.1f} ns/tick (écart absolu médian "
            f"{mesure['tau_eam_ns']:.1f}) · période hypothétique "
            f"{mesure['periode_hypothetique_ns']:.4f} ns · rapport "
            f"{mesure['ratio_tau_sur_periode']:.0f} × · {mesure['verdict_mesure']}",
            "OPÉRATIONNEL",
            "mesure dépendante de la machine, de l'interpréteur et de la charge : elle est "
            "exclue du certificat scellé et ne vaut que pour l'hôte qui l'a produite", mesure),
        _eq("EQ-13", "horlogerie.py → sources_du_depot() → C13",
            "lib_temporelle ≡ lib_informe ≡ acte A136 scellé ≡ certificat",
            f"quatre énoncés du même nombre, identiques bit à bit : {r['dt']['flottant']} · "
            f"{r['dt']['numerateur']}/{r['dt']['denominateur']}", "OPÉRATIONNEL",
            "la confrontation porte sur ce que le dépôt ÉCRIT : elle ne rend pas le nombre vrai, "
            "elle montre qu'il n'existe pas deux versions de l'horloge", cert["rationnels"]),
        _eq("EQ-14", "verifier_certificats.py → verifier() → C14",
            "un certificat se relit sans exécuter le dépôt : racine = SHA-256 des six empreintes",
            f"{len(cert['englobe'])} sous-certificats · racine "
            f"{cert['racine_merkle_sha256'][:16]}… · relu par {VERIFICATEUR.name} sans un seul "
            f"import du dépôt", "OPÉRATIONNEL",
            "le vérificateur ne prouve aucune physique : il prouve que le fichier se relit sans "
            "aucune confiance dans ce module", cert["empreintes_souche"]),
        _eq("EQ-15", "horlogerie.py → coherence_des_sources() → C15",
            "lunaisons_12 = 12 × lunaison, et chaque fraction du fichier est la décimale citée",
            f"identités : {len(co['identites'])} · références : "
            f"{len(astro['references'])} · fausses {co['fausses'] or 'aucune'}",
            "OPÉRATIONNEL",
            "c'est cette garde qui a attrapé l'erreur du 2026-11-09 : lunaisons_12 valait "
            "355,36692 là où sa source écrit 354,36708 ; elle ne valide pas le ciel, elle "
            "interdit à une valeur citée de dériver silencieusement de sa propre source", co),
    ]


def controles(eqs: Dict[str, Dict[str, Any]], cert: Dict[str, Any],
              mesure: Dict[str, Any]) -> List[Dict[str, Any]]:
    from HORLOGERIE import verifier_certificats as VC

    out: List[Dict[str, Any]] = []

    def ajouter(id_: str, nom: str, attendu: str, obtenu: str, ok: bool) -> None:
        out.append({"id": id_, "nom": nom, "attendu": attendu, "obtenu": obtenu, "ok": bool(ok),
                    "limite": eqs[id_.replace("C", "EQ-")]["limite"]})

    s = semences()
    r = rationnaux()
    ids = {i["id"]: i for i in cert["identites"]}
    astro = cert["astronomie"]
    ajouter("C01", "les douze semences sont rationnelles et rendent 365,25 · 354 · 360 jours",
            "1461/4 · 354 · 360",
            " · ".join(str(s[a]["annee_h"] / 24) for a in ("soleil", "lune", "terre")),
            s["soleil"]["annee_h"] / 24 == F("1461/4") and s["lune"]["annee_h"] / 24 == 354
            and s["terre"]["annee_h"] / 24 == 360)
    ajouter("C02", "dx tombe exactement sur 6 403 563/128", "6403563/128",
            f"{r['dx'].numerator}/{r['dx'].denominator}",
            (r["dx"].numerator, r["dx"].denominator) == (6_403_563, 128)
            and float(r["dx"]) == 50_027.8359375)
    ajouter("C03", "dy tombe exactement sur 93 987/2", "93987/2",
            f"{r['dy'].numerator}/{r['dy'].denominator}",
            (r["dy"].numerator, r["dy"].denominator) == (93_987, 2) and float(r["dy"]) == 46_993.5)
    ajouter("C04", "dz est entier et le rapport brut sur normalisé vaut 144/5", "135000000 · 144/5",
            f"{r['dz'].numerator} · {ids['normalisation']['rapport_brut_sur_normalise']}",
            r["dz"].denominator == 1 and ids["normalisation"]["vraie"])
    ajouter("C05", "l'identité dt = dx + dy + dz tient en entiers", "vraie · 135097021.3359375",
            f"{ids['somme']['vraie']} · {float(r['dt'])!r}",
            ids["somme"]["vraie"] and float(r["dt"]) == 135_097_021.3359375)
    ajouter("C06", "den(dt) = 2^7 et num(dt) impair", "128 · impair",
            f"{ids['denominateur']['denominateur']} · {ids['denominateur']['numerateur_impair']}",
            ids["denominateur"]["vraie"])
    p = cert["periode"]
    ajouter("C07", "la période est rendue en décimale exacte sur 40 rangs, sans arrondi masqué",
            "40 rangs · 7,4020877…",
            f"{len(p['valeur_ns'].replace('.', ''))} rangs · {p['valeur_ns'][:9]}…",
            p["valeur_ns"].startswith("7.4020877")
            and len(p["valeur_ns"].replace(".", "")) == PRECISION
            and F(p["fraction"]) * r["dt"] == 10 ** 9)
    ajouter("C08", "neuf paires gelées, trois seuils, une empreinte de 64 hexadécimales",
            "9 paires · 64 hex", f"{len(astro['resultats'])} paires · "
            f"{len(astro['empreinte_du_gel'])} hex",
            len(astro["resultats"]) == len(PAIRES) == 9 and len(astro["empreinte_du_gel"]) == 64)
    soleil = [x for x in astro["resultats"] if x["cycle"] == "Soleil"]
    ajouter("C09", "l'écart Soleil-tropique vaut 673,92 s/an et le verdict suit le seuil gelé",
            "673,92 s · ÉCART SIGNALÉ · CONFORME contre l'année julienne",
            f"{trouver(astro, 'Soleil', 'annee_tropique')['ecart_s_arrondi']} s · "
            f"{astro['par_cycle']['Soleil']['verdict']} · "
            f"{trouver(astro, 'Soleil', 'annee_julienne')['verdict']}",
            abs(trouver(astro, "Soleil", "annee_tropique")["ecart_s_arrondi"] - 673.92) < 5e-3
            and trouver(astro, "Soleil", "annee_tropique")["verdict"] == "ÉCART SIGNALÉ"
            and all(x["verdict"] == "CONFORME" for x in soleil
                    if x["reference"] == "annee_julienne"))
    lune = [x for x in astro["resultats"] if x["cycle"] == "Lune"]
    mesu = [x for x in lune if x["nature_reference"] == "éphéméride mesurée"]
    ajouter("C10", "les douze lunaisons dépassent la tolérance d'une heure, et la variante du "
                   "mois ne change rien",
            "HORS TOLÉRANCE · HORS TOLÉRANCE",
            f"{trouver(astro, 'Lune', 'lunaisons_12')['verdict']} · "
            f"{astro['sensibilite']['verdict']}",
            len(mesu) == 2 and all(x["verdict"] == "HORS TOLÉRANCE" for x in mesu)
            and astro["sensibilite"]["verdict"] == "HORS TOLÉRANCE")
    terre = [x for x in astro["resultats"] if x["cycle"] == "Terre"]
    ajouter("C11", "aucune des trois confrontations de la Terre ne passe sous l'heure",
            "3/3 hors tolérance",
            f"{sum(1 for x in terre if x['verdict'] == 'HORS TOLÉRANCE')}/{len(terre)}",
            len(terre) == 3 and all(x["verdict"] == "HORS TOLÉRANCE" for x in terre))
    ajouter("C12", "la médiane tombe entre le minimum et le maximum des cinq séries",
            "min ≤ médiane ≤ max",
            f"{mesure['tau_min_ns']:.1f} ≤ {mesure['tau_mediane_ns']:.1f} ≤ "
            f"{mesure['tau_max_ns']:.1f}",
            mesure["tau_min_ns"] <= mesure["tau_mediane_ns"] <= mesure["tau_max_ns"]
            and mesure["tau_mediane_ns"] > 0 and mesure["series"] == 5)
    depot = sources_du_depot(cert)
    ajouter("C13", "la bibliothèque, LA TABLE et l'acte A136 scellé rendent le même nombre",
            "les quatre concordants",
            f"{depot['lib_temporelle']['CLOCK_DT_KERNEL']!r} · "
            f"{depot['lib_informe']['dt']['valeur']!r} · "
            f"{depot['acte_a136_scelle']['dt_kernel']!r}",
            depot["concordance"]
            and depot["lib_informe"]["dt"]["fraction"] == f"{r['dt'].numerator}/"
                                                          f"{r['dt'].denominator}")
    rendu = VC.verifier(cert)
    muet = copy.deepcopy(cert)
    muet["rationnels"]["dx"]["numerateur"] += 1
    echo = [x["id"] for x in VC.verifier(muet) if not x["ok"]]
    ajouter("C14", "le vérificateur autonome donne PASS sur le certificat et FAIL sur une copie "
                   "dont un numérateur est déplacé de 1",
            "16/16 PASS · mutation refusée",
            f"{sum(1 for x in rendu if x['ok'])}/{len(rendu)} PASS · mutation "
            f"{echo or 'ACCEPTÉE (garde morte)'}",
            all(x["ok"] for x in rendu) and bool(echo))
    co = astro["coherence_des_sources"]
    ajouter("C15", "douze lunaisons valent douze fois le mois synodique, et chaque "
                   "fraction du fichier est la décimale citée par sa source",
            "2 identités vraies · aucune fausse",
            f"{sum(1 for x in co['identites'] if x['vraie'])}/2 · fausses "
            f"{co['fausses'] or 'aucune'} · lunaisons_12 "
            f"{co['identites'][0]['gauche']}",
            all(x["vraie"] for x in co["identites"]) and not co["fausses"])
    return out


def verifier(donnees: Dict[str, Any]) -> bool:
    return all(c["ok"] for c in donnees["controles"])


def octets_certificat(cert: Dict[str, Any]) -> bytes:
    return (json.dumps(cert, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def octets_csv_astro(astro: Dict[str, Any]) -> bytes:
    """Le format Excel français du dépôt : BOM, « ; », CRLF, virgule décimale."""
    lignes = [["cycle", "reference", "nature", "declare_jours", "reference_jours",
               "ecart_s_an", "verdict"]]
    for x in astro["resultats"]:
        lignes.append([x["cycle"], x["reference"], x["nature_reference"],
                       float(F(x["declare_jours"])), float(F(x["reference_jours"])),
                       float(F(x["ecart_s_par_an"])), x["verdict"]])
    corps = "\r\n".join(";".join(str(v).replace(".", ",") for v in ligne) for ligne in lignes)
    return b"\xef\xbb\xbf" + (corps + "\r\n").encode("utf-8")


def ecrire_artefacts(cert: Dict[str, Any], vers: Path = ARTEFACTS) -> Dict[str, str]:
    vers.mkdir(parents=True, exist_ok=True)
    rendu: Dict[str, str] = {}
    for nom, octets in (("certificats.json", octets_certificat(cert)),
                        ("confrontation_astronomique.csv", octets_csv_astro(cert["astronomie"]))):
        (vers / nom).write_bytes(octets)
        rendu[nom] = f"{len(octets)} octets"
    return rendu


def resoudre() -> Dict[str, Any]:
    cert = certificat()
    mesure = mesure_rythme()
    eqs = {x["id"]: x for x in equations(cert, mesure)}
    cs = controles(eqs, cert, mesure)
    return {"source": SOURCE, "certificat": cert, "mesure": mesure, "depot": sources_du_depot(cert),
            "equations": list(eqs.values()), "controles": cs,
            "conclusion": {
                "controles_verts": sum(1 for c in cs if c["ok"]), "controles_total": len(cs),
                "equations": len(eqs),
                "statuts_par_label": {st: sum(1 for x in eqs.values() if x["statut"] == st)
                                      for st in ("OPÉRATIONNEL", "SIMULÉ", "SPÉCIFIÉ")},
                "verdict_identite": "EXACTE EN ENTIERS — 17 292 418 731/128",
                "verdict_astronomique": {k: v["verdict"] for k, v in
                                         cert["astronomie"]["par_cycle"].items()},
                "verdict_unite": mesure["verdict_mesure"],
                "racine_merkle_sha256": cert["racine_merkle_sha256"]}}


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    donnees = resoudre()
    if "--ecrit" in sys.argv[1:]:
        donnees["artefacts"] = ecrire_artefacts(donnees["certificat"])
    sortie = {
        "source": {"id": SOURCE["video_id"], "titre": SOURCE["titre"],
                   "chaine": SOURCE["chaine"], "duree_s": SOURCE["duree_s"],
                   "chapitres": SOURCE["chapitres_verbatims"], "transcript": SOURCE["transcript"]},
        "identite": donnees["certificat"]["identites"],
        "periode_hypothetique_ns": donnees["certificat"]["periode"]["valeur_ns"],
        "astronomie": donnees["certificat"]["astronomie"]["par_cycle"],
        "conclusion_astronomique": donnees["certificat"]["astronomie"]["conclusion"],
        "unite_retenue": donnees["certificat"]["unites"]["enonce_retenu"],
        "mesure_rythme": donnees["mesure"],
        "racine_merkle_sha256": donnees["certificat"]["racine_merkle_sha256"],
        "controles": donnees["controles"],
        "equations": [{k: v for k, v in x.items() if k != "detail"}
                      for x in donnees["equations"]],
        "conclusion": donnees["conclusion"],
        "artefacts": donnees.get("artefacts", {}),
    }
    print(json.dumps(sortie, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    sys.exit(0 if verifier(donnees) else 1)
