# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""Tests du dossier GUERRE — les comptes sont re-mesurés, pas recopiés.

Six exigences, dans l'ordre :
    1. chaque nombre publié est re-mesuré ICI à partir des octets bruts du snapshot, par une écriture
       différente : le SHA-256 vient d'une lecture par blocs (et non d'un `read_bytes`), les
       pourcentages et les longueurs de barres viennent d'une division entière à arrondi half-up (et
       non d'un `Fraction` sur le quotient), le rho de rang vient de `1 − 6·Σd²/(n(n²−1))` (et non de
       `statistics.correlation`), les médianes sont prises à la main sur une liste triée (et non de
       `statistics.median`), et le tri de masse est un tri stable à deux passes ;
    2. les règles de comptage sont éprouvées sur des jeux étrangers au dépôt : un plan fabriqué à
       partir de compteurs fictifs rend des barres proportionnelles non nulles, le compteur de
       mentions compte ce qu'on lui donne, et le rho vaut exactement 1, −1 et 0,9 sur trois jeux ;
    3. les quatre artefacts sont écrits dans un répertoire temporaire, relus par `csv.reader` et par
       regex, puis comparés au certificat : les tailles et les empreintes scellées retombent sur les
       octets présents, et un nombre mué sur disque ne passe plus la relecture ;
    4. non-vacuité : seize mutations en mémoire, une par contrôle, chacune exigeant un message
       d'obtenu différent — la grille n'est pas décorative et ne rougit pas deux fois ;
    5. les verdicts défavorables restent écrits : l'énoncé de l'auteur reste réfuté, l'absolue tombe
       par les deux côtés, l'émulateur reste hors sujet, la protection reste inexécutable, le
       transcript reste absent, les dix limites restent ouvertes — et la phrase d'auteur ne devient
       jamais une loi dans les octets publiés ;
    6. structure et langage : seize nœuds plus deux, racine Merkle recalculée, imports de la
       bibliothèque standard seule, et les quatre signaux d'appel de l'émulateur absents des deux
       sources du dossier — y compris de ce fichier de tests.

Bibliothèque standard seule.
    cd ZENODO_DEPOT_ALMIZAN && py -3 -m unittest GUERRE.tests.test_guerre -v
"""

import ast
import copy
import csv
import hashlib
import io
import json
import re
import sys
import unittest
from fractions import Fraction
from pathlib import Path
from tempfile import TemporaryDirectory

RACINE_DEPOT = Path(__file__).resolve().parents[2]
if str(RACINE_DEPOT) not in sys.path:
    sys.path.insert(0, str(RACINE_DEPOT))

from FONDATION import fondation_base as FB                       # noqa: E402
from GUERRE import guerre_base as G                               # noqa: E402

HORS_NOEUDS = frozenset({"source", "empreinte_execution", "taille_octets", "rejoue_identique",
                         "limites", "attribution", "racine_merkle_sha256"})


# ─── la voie indépendante : rien de ce qui est publié n'est accepté sur parole --


def canon(objet):
    return json.dumps(objet, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")


def sans_la_liste(objet):
    """Retire la liste des interdits où qu'elle soit : le seul endroit où un interdit a le droit
    d'apparaître est l'énoncé de l'interdiction. La présence de la liste est contrôlée avant."""
    if isinstance(objet, dict):
        return {k: sans_la_liste(v) for k, v in objet.items() if k != "liste_des_phrases_interdites"}
    if isinstance(objet, list):
        return [sans_la_liste(v) for v in objet]
    return objet


def etat_de(cert):
    """Re-construit l'état exactement comme `resoudre()` le fait, depuis un certificat donné."""
    etat = {k: v for k, v in cert.items() if k not in ("source", "limites", "attribution")}
    etat["noeuds_certificat"] = cert
    return etat


def grille_de(cert):
    etat = etat_de(cert)
    eqs = {x["id"]: x for x in G.equations(etat)}
    return {c["id"]: c for c in G.controles(eqs, etat)}


def racine_depuis(noeuds):
    return hashlib.sha256(canon({c: hashlib.sha256(canon(noeuds[c])).hexdigest()
                                 for c in sorted(noeuds)})).hexdigest()


def q_dec(v, decimales):
    """Half-up par entiers sur un Fraction : même contrat que `_decimale`, autre écriture."""
    signe = "-" if v < 0 else ""
    v = abs(v)
    m = 10 ** decimales
    e = (v.numerator * 2 * m + v.denominator) // (v.denominator * 2)
    return f"{signe}{e // m}.{e % m:0{decimales}d}"


def pct_entier(haut, total, decimales=2):
    """Pourcentage half-up sans Fraction : division entière pure."""
    m = 10 ** decimales
    e = (2 * haut * 100 * m + total) // (2 * total)
    return f"{e // m}.{e % m:0{decimales}d}"


def largeur_barre(valeur, grand):
    """220 × v / grand en arithmétique entière : autre chemin que le `Fraction` du module."""
    m = 100
    e = (2 * 220 * valeur * m + grand) // (2 * grand)
    return f"{e // m}.{e % m:02d}"


def mediane(vals):
    v = sorted(vals)
    n = len(v)
    if n == 0:
        return None
    return v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2.0


def rangs(valeurs, cles):
    n = len(valeurs)
    ordre = list(range(n))
    ordre.sort(key=lambda i: cles[i])       # départage : code ISO
    ordre.sort(key=lambda i: valeurs[i])    # tri stable : le rang 1 est le plus petit
    r = [0] * n
    for pos, i in enumerate(ordre):
        r[i] = pos + 1
    return r


def spearman_exact(paires):
    """rho = 1 − 6·Σd²/(n(n²−1)) : la formule des rangs, pas une covariance de `statistics`."""
    rx = rangs([p[0] for p in paires], [p[2] for p in paires])
    ry = rangs([p[1] for p in paires], [p[2] for p in paires])
    d = sum((a - b) ** 2 for a, b in zip(rx, ry))
    n = len(paires)
    return Fraction(1) - Fraction(6 * d, n * (n * n - 1))


def est_nb(r, cle):
    v = r.get(cle)
    return type(v) is int or type(v) is float


def tri_par_masse(lignes):
    """Deux passes stables (ISO croissant, puis masse décroissante) : même règle, autre code."""
    pas = sorted(lignes, key=lambda r: r["iso3"])
    return sorted(pas, key=lambda r: -r[CLE_MASSE])


def tri_par_revenu(lignes):
    pas = sorted(lignes, key=lambda r: r["iso3"])
    return sorted(pas, key=lambda r: r[CLE_REVENU])


def effort_de(r):
    if est_nb(r, CLE_PART) and est_nb(r, CLE_RECETTES) and r[CLE_RECETTES] > 0:
        return 100.0 * r[CLE_PART] / r[CLE_RECETTES]
    return None


CLE_MASSE = "depense_militaire_usd_courants"
CLE_REVENU = "pib_par_habitant_usd_courants"
CLE_PART = "depense_part_du_pib_pct"
CLE_RECETTES = "recettes_publiques_part_du_pib_pct"
CLE_DETTES = "dette_publique_part_du_pib_pct"
TOUTES_CLES = [c for c, _ in G.CHAMPS]

BRUT = (RACINE_DEPOT / G.CHEMIN_TRESOR).read_bytes()
SNAP = json.loads(BRUT.decode("utf-8"))
LIG = SNAP["lignes"]
BRUT_VIDEO = (RACINE_DEPOT / G.CHEMIN_CHAPITRES).read_bytes()
VIDEO = json.loads(BRUT_VIDEO.decode("utf-8"))

COMPARABLES = [r for r in LIG if est_nb(r, CLE_MASSE) and est_nb(r, CLE_REVENU)]
AYANT_PART = [r for r in LIG if est_nb(r, CLE_PART) and est_nb(r, CLE_REVENU)]
EFFORTS = [r for r in LIG if effort_de(r) is not None]
TRIEES = tri_par_masse(COMPARABLES)
ORDRE_REVENU = tri_par_revenu(AYANT_PART)
MEDIANE_REVENU = mediane([r[CLE_REVENU] for r in COMPARABLES])
TOTAL_DOLLARS = 0.0
for _r in TRIEES:
    TOTAL_DOLLARS = TOTAL_DOLLARS + _r[CLE_MASSE]
HAUT_DIX = 0.0
for _r in TRIEES[:G.SEUIL_TOP]:
    HAUT_DIX = HAUT_DIX + _r[CLE_MASSE]

CERT = G.certificat()
EQS = {x["id"]: x for x in G.equations(etat_de(CERT))}
CS = grille_de(CERT)
NOEUDS = {k: v for k, v in CERT.items() if k not in HORS_NOEUDS}
RACINE = CERT["racine_merkle_sha256"]


# ─── 1. la source, la couverture, les masses -----------------------------------

class TestReDerivationSourceEtCouverture(unittest.TestCase):
    def test_le_sha256_du_snapshot_vient_d_une_lecture_par_blocs(self):
        h = hashlib.sha256()
        with open(RACINE_DEPOT / G.CHEMIN_TRESOR, "rb") as f:
            while True:
                bloc = f.read(4096)
                if not bloc:
                    break
                h.update(bloc)
        self.assertEqual(h.hexdigest(), CERT["source_tresor"]["sha256"])
        self.assertEqual(len(BRUT), CERT["source_tresor"]["octets"])
        self.assertGreater(len(BRUT), 50_000)

    def test_les_entites_hors_agregats_retombent_sur_le_decompte(self):
        s = CERT["source_tresor"]
        self.assertEqual(SNAP["entites_declarees"] - SNAP["agregats_exclus"],
                         SNAP["entites_hors_agregats"])
        self.assertEqual(s["entites_hors_agregats"], s["lignes"])
        self.assertEqual(s["lignes"], len(LIG))
        codes = [r["iso3"] for r in LIG]
        self.assertEqual(codes, sorted(codes), "le snapshot n'est plus dans l'ordre ISO")
        self.assertEqual(len(set(codes)), len(codes), "un code ISO en double")

    def test_les_six_empreintes_brutes_sont_celles_de_l_indicateur_annonce(self):
        s = CERT["source_tresor"]
        self.assertEqual(sorted(s["empreintes_brutes"]), sorted(TOUTES_CLES))
        self.assertEqual({k: v["indicateur"] for k, v in SNAP["indicateurs"].items()},
                         dict(G.CHAMPS))
        for cle in TOUTES_CLES:
            self.assertEqual(s["empreintes_brutes"][cle], SNAP["indicateurs"][cle]["sha256_brut"], cle)
            self.assertRegex(s["empreintes_brutes"][cle], r"^[0-9a-f]{64}$", cle)
            self.assertGreater(SNAP["indicateurs"][cle]["octets_bruts"], 1000, cle)
        self.assertEqual(len({SNAP["indicateurs"][c]["sha256_brut"] for c in TOUTES_CLES}), 6,
                         "deux indicateurs empreints identiques")

    def test_la_couverture_est_recomptee_indicateur_par_indicateur(self):
        cov = CERT["couverture"]
        recompte = {cle: sum(1 for r in LIG if est_nb(r, cle)) for cle in TOUTES_CLES}
        self.assertEqual(cov["par_indicateur"], recompte)
        self.assertEqual(cov["comparables"], len(COMPARABLES))
        self.assertEqual(cov["avec_recettes"], recompte[CLE_RECETTES])
        self.assertEqual(cov["avec_dette"], recompte[CLE_DETTES])
        self.assertEqual(cov["avec_effort_fiscal"], len(EFFORTS))
        muets = [r["iso3"] for r in LIG if not any(est_nb(r, c) for c in TOUTES_CLES)]
        self.assertEqual(cov["codes_sans_aucune_valeur"], muets)
        self.assertEqual(cov["sans_aucune_valeur"], len(muets))

    def test_le_ratio_exploitable_est_une_division_entiere_half_up(self):
        cov = CERT["couverture"]
        self.assertEqual(cov["ratio_exploitable_pct"], pct_entier(len(COMPARABLES), len(LIG)))
        self.assertEqual(cov["indicateur_le_plus_muet"],
                         min(TOUTES_CLES, key=lambda c: (cov["par_indicateur"][c],
                                                         TOUTES_CLES.index(c))))
        self.assertLess(cov["comparables"], cov["lignes"])
        self.assertGreater(cov["comparables"], 100)

    def test_absence_n_est_pas_zero_et_c_est_la_regle_publiee(self):
        cov = CERT["couverture"]
        self.assertIn("n'est pas un État sans armée", cov["absence_n_est_pas_zero"])
        non_publiees = sum(1 for r in LIG if not est_nb(r, CLE_MASSE))
        self.assertGreater(non_publiees, 0)
        self.assertEqual(non_publiees + cov["par_indicateur"][CLE_MASSE], len(LIG))


class TestReDerivationMasses(unittest.TestCase):
    def test_total_et_top_dix_recalcules_en_dollars(self):
        m = CERT["masses"]
        self.assertEqual(m["effectif"], len(COMPARABLES))
        self.assertEqual(int(round(TOTAL_DOLLARS)), m["total_dollars_arrondis"])
        self.assertEqual(int(round(HAUT_DIX)), m["top_dix_dollars_arrondis"])
        self.assertEqual(m["total_mds"], q_dec(Fraction(float(TOTAL_DOLLARS / 1e9)), 1))
        self.assertEqual(m["top_dix_mds"], q_dec(Fraction(float(HAUT_DIX / 1e9)), 1))

    def test_le_top_dix_pour_cent_vient_d_une_division_entiere(self):
        m = CERT["masses"]
        self.assertEqual(m["top_dix_pct"],
                         pct_entier(m["top_dix_dollars_arrondis"], m["total_dollars_arrondis"]))
        self.assertEqual(m["top_dix_pct"],
                         pct_entier(int(round(HAUT_DIX)), int(round(TOTAL_DOLLARS))))

    def test_le_tri_de_tete_et_la_mediane_sont_les_miennes(self):
        m = CERT["masses"]
        self.assertEqual([x["iso3"] for x in m["tops"]], [r["iso3"] for r in TRIEES[:15]])
        self.assertEqual(m["premier"].split()[0], TRIEES[0]["iso3"])
        self.assertEqual(m["mediane_mds"],
                         q_dec(Fraction(float(mediane([r[CLE_MASSE] for r in COMPARABLES]) / 1e9)), 3))
        self.assertEqual(m["tops"][0]["mds"], q_dec(Fraction(float(TRIEES[0][CLE_MASSE] / 1e9)), 3))
        self.assertEqual(m["tops"][0]["pib_h"], q_dec(Fraction(float(TRIEES[0][CLE_REVENU])), 0))
        self.assertEqual([x["rang"] for x in m["tops"]], list(range(1, 16)))

    def test_les_franchissements_de_seuil_sont_decroissants_et_recomptes(self):
        m = CERT["masses"]
        attendu = {f">= {int(s / 1e9)} Md$": sum(1 for r in TRIEES if r[CLE_MASSE] >= s)
                   for s in G.SEUIL_MASSES}
        self.assertEqual(m["seuils"], attendu)
        self.assertLessEqual(attendu[">= 100 Md$"], attendu[">= 10 Md$"])
        self.assertLessEqual(attendu[">= 10 Md$"], attendu[">= 1 Md$"])

    def test_les_depenses_exactement_nulles_sont_nommees(self):
        m = CERT["masses"]
        nuls = sorted(r["iso3"] for r in COMPARABLES if r[CLE_MASSE] == 0)
        self.assertEqual(m["zero_mesures"], nuls)
        self.assertEqual(m["nb_zero"], len(nuls))
        self.assertGreaterEqual(len(nuls), 1)


# ─── 2. rangs, quintiles, effort fiscal ---------------------------------------

class TestReDerivationCorrelations(unittest.TestCase):
    def test_rho_revenu_part_vient_de_la_forme_des_rangs(self):
        cr = CERT["charge_relative"]
        paires = [(r[CLE_REVENU], r[CLE_PART], r["iso3"]) for r in AYANT_PART]
        self.assertEqual(cr["effectif"], len(paires))
        exact = spearman_exact(paires)
        self.assertEqual(q_dec(exact, 4), cr["spearman_revenu_part"])
        self.assertLess(abs(float(exact) - float(cr["spearman_revenu_part"])), 5e-5)
        self.assertEqual(cr["seuil_de_platitude"], q_dec(Fraction(float(G.SEUIL_CHARGE_PLATE)), 2))

    def test_rho_revenu_masse_vient_de_la_meme_forme_sur_la_masse(self):
        ca = CERT["capacite_absolue"]
        paires = [(r[CLE_REVENU], r[CLE_MASSE], r["iso3"]) for r in COMPARABLES]
        self.assertEqual(ca["effectif"], len(paires))
        self.assertEqual(q_dec(spearman_exact(paires), 4), ca["spearman_revenu_masse"])
        self.assertEqual(ca["mediane_revenu"], q_dec(Fraction(float(MEDIANE_REVENU)), 0))
        self.assertGreater(float(ca["spearman_revenu_masse"]),
                           float(CERT["charge_relative"]["spearman_revenu_part"]))

    def test_rho_revenu_effort_calculable_sans_statistics(self):
        tr = CERT["tresorerie"]
        paires = [(r[CLE_REVENU], effort_de(r), r["iso3"]) for r in EFFORTS]
        self.assertEqual(tr["effectif"], len(EFFORTS))
        self.assertEqual(q_dec(spearman_exact(paires), 4), tr["spearman_revenu_effort"])
        self.assertEqual(tr["mediane_pct"],
                         q_dec(Fraction(float(mediane([effort_de(r) for r in EFFORTS]))), 2))
        self.assertEqual(tr["seuil_massif_pct"], q_dec(Fraction(float(G.SEUIL_EFFORT_MASSIF)), 2))
        massifs = [r["iso3"] for r in EFFORTS if effort_de(r) >= G.SEUIL_EFFORT_MASSIF]
        self.assertEqual(sorted(tr["codes_massifs"]), sorted(massifs),
                         "la liste des efforts massifs ne retombe pas")
        bas = [r["iso3"] for r in EFFORTS if effort_de(r) >= G.SEUIL_EFFORT_MASSIF
               and r[CLE_REVENU] < 5000]
        self.assertEqual(sorted(tr["massifs_et_sous_cinq_mille"]), sorted(bas))
        self.assertGreaterEqual(len(bas), 1, "aucun État pauvre à effort massif : mesure creuse")
        dettes = [r[CLE_DETTES] for r in LIG if est_nb(r, CLE_DETTES)]
        self.assertEqual(tr["dette_effectif"], len(dettes))
        self.assertEqual(tr["dette_mediane_pct"], q_dec(Fraction(float(mediane(dettes))), 2))

    def test_le_haut_du_tableau_d_effort_est_tri_comme_moi(self):
        tr = CERT["tresorerie"]
        tete = sorted(sorted(EFFORTS, key=lambda r: r["iso3"]), key=lambda r: -effort_de(r))
        self.assertEqual([x["iso3"] for x in tr["haut_du_tableau"]], [r["iso3"] for r in tete[:10]])
        for publie, r in zip(tr["haut_du_tableau"], tete[:10]):
            self.assertEqual(publie["effort_pct"], q_dec(Fraction(float(effort_de(r))), 1), r["iso3"])
            self.assertGreaterEqual(effort_de(r), effort_de(tete[tete.index(r) + 1])
                                    if tete.index(r) + 1 < len(tete) else 0.0)

    def test_les_cinq_quintiles_courent_l_effectif_et_retombent(self):
        cr = CERT["charge_relative"]
        n = len(ORDRE_REVENU) // 5
        attendu = []
        for i in range(5):
            bloc = ORDRE_REVENU[i * n:(i + 1) * n] if i < 4 else ORDRE_REVENU[4 * n:]
            acc = 0.0
            for r in bloc:
                acc = acc + r[CLE_PART]
            attendu.append({"n": len(bloc),
                            "part_moyenne_pct": q_dec(Fraction(acc) / len(bloc), 2),
                            "intervalle_pib_h":
                                f"{q_dec(Fraction(float(bloc[0][CLE_REVENU])), 0)}"
                                f" → {q_dec(Fraction(float(bloc[-1][CLE_REVENU])), 0)}"})
        self.assertEqual(len(cr["quintiles"]), 5)
        self.assertEqual([q["n"] for q in cr["quintiles"]], [a["n"] for a in attendu])
        self.assertEqual([q["part_moyenne_pct"] for q in cr["quintiles"]],
                         [a["part_moyenne_pct"] for a in attendu])
        self.assertEqual([q["intervalle_pib_h"] for q in cr["quintiles"]],
                         [a["intervalle_pib_h"] for a in attendu])
        self.assertEqual(sum(q["n"] for q in cr["quintiles"]), cr["effectif"])
        moy = [float(q["part_moyenne_pct"]) for q in cr["quintiles"]]
        self.assertEqual(cr["ecart_max_min_pct"],
                         q_dec(Fraction(max(moy)) - Fraction(min(moy)), 2))
        self.assertEqual(cr["rang_du_quintile_le_plus_lourd"], moy.index(max(moy)) + 1)
        self.assertEqual(cr["quintile_le_plus_lourd"],
                         cr["quintiles"][moy.index(max(moy))]["intervalle_pib_h"])
        self.assertTrue(cr["la_charge_ne_croit_pas_avec_le_revenu"])

    def test_l_extreme_mesure_est_bien_le_maximum_et_son_rang(self):
        ex = CERT["extreme_mesure"]
        attendu_rang = [r["iso3"] for r in ORDRE_REVENU].index(ex["iso3"]) + 1
        self.assertEqual(ex["rang_revenu"], attendu_rang)
        parts = [r[CLE_PART] for r in AYANT_PART]
        self.assertEqual(ex["part_pct"], q_dec(Fraction(float(max(parts))), 2))
        self.assertTrue(ex["est_le_maximum_mesure"])
        med = mediane(parts)
        self.assertEqual(ex["mediane_part_pct"], q_dec(Fraction(float(med)), 2))
        self.assertEqual(ex["rapport_a_la_mediane"],
                         q_dec(Fraction(float(max(parts))) / Fraction(float(med)), 2))
        self.assertEqual(len(ex["suivants"]), 7)
        self.assertGreater(float(ex["rapport_a_la_mediane"]), 1)


# ─── 3. falsification, riches désarmés, belligérants ---------------------------

class TestReDerivationFalsification(unittest.TestCase):
    def test_les_contre_exemples_sous_la_mediane_sont_les_miens(self):
        f = CERT["falsification"]
        miens = [r for r in COMPARABLES if r[CLE_REVENU] < MEDIANE_REVENU
                 and r[CLE_MASSE] >= G.SEUIL_MASSES[0]]
        self.assertEqual(f["effectif"], len(miens))
        self.assertEqual(f["population_sous_mediane"],
                         sum(1 for r in COMPARABLES if r[CLE_REVENU] < MEDIANE_REVENU))
        self.assertEqual(sorted(x["iso3"] for x in f["pauvres_armes"]),
                         sorted(r["iso3"] for r in miens))
        self.assertEqual(f["mediane_revenu"], q_dec(Fraction(float(MEDIANE_REVENU)), 0))
        plus_pauvre = min(miens, key=lambda r: (r[CLE_REVENU], r["iso3"]))
        self.assertEqual(f["plus_pauvre_arms"]["iso3"], plus_pauvre["iso3"])
        self.assertEqual(f["plus_pauvre_arms"]["pib_h"],
                         q_dec(Fraction(float(plus_pauvre[CLE_REVENU])), 0))
        self.assertEqual([float(x["pib_h"]) for x in f["pauvres_armes"]],
                         sorted(float(x["pib_h"]) for x in f["pauvres_armes"]))

    def test_le_seuil_de_dix_milliards_et_la_forme_absolue(self):
        f = CERT["falsification"]
        gros = [r["iso3"] for r in COMPARABLES if r[CLE_REVENU] < MEDIANE_REVENU
                and r[CLE_MASSE] >= G.SEUIL_MASSES[1]]
        self.assertEqual(sorted(f["au_dessus_de_dix_mds"]), sorted(gros))
        self.assertGreater(f["effectif"], 0, "la réfutation doit rester mesurée")
        self.assertTrue(f["l_absolue_est_refutee"])
        self.assertEqual(f["enonce_teste"], "sans richesse pas de guerre")

    def test_les_riches_desarmes_sont_recomptes_des_deux_cotes(self):
        rs = CERT["riches_sans_armee"]
        nuls = sorted((r for r in COMPARABLES if r[CLE_MASSE] == 0), key=lambda r: r["iso3"])
        self.assertEqual(rs["zero"], len(nuls))
        self.assertEqual([x["iso3"] for x in rs["liste"]], [r["iso3"] for r in nuls])
        self.assertTrue(rs["tous_au_dessus_de_la_mediane"])
        self.assertEqual(rs["mediane_revenu"], q_dec(Fraction(float(MEDIANE_REVENU)), 0))
        riche = max(nuls, key=lambda r: r[CLE_REVENU])
        self.assertEqual(rs["le_plus_riche"]["iso3"], riche["iso3"])
        self.assertEqual(rs["le_plus_riche"]["pib_h"], q_dec(Fraction(float(riche[CLE_REVENU])), 0))
        self.assertTrue(rs["l_implication_tombe_a_l_envers"])

    def test_la_table_declaree_ne_convertit_aucune_absence_en_zero(self):
        bd = CERT["belligerants_declares"]
        par_iso = {r["iso3"]: r for r in LIG}
        mesures, absents = [], []
        for d in G.BELLIGERANTS_DECLARES:
            (mesures if est_nb(par_iso.get(d["iso3"], {}), CLE_REVENU) else absents).append(d["iso3"])
        self.assertEqual(bd["nb"], len(G.BELLIGERANTS_DECLARES))
        self.assertEqual(bd["revenus_mesures"], len(mesures))
        self.assertEqual(bd["codes_sans_revenu"], absents)
        self.assertEqual(bd["revenus_absents"], len(absents))
        self.assertTrue(bd["chaque_ligne_est_mesuree_ou_dite_absente"])
        self.assertEqual(bd["part_revenus_mesures_pct"], pct_entier(len(mesures), bd["nb"]))
        self.assertEqual(bd["statut_du_fait"], "déclaré · non vérifié")
        self.assertFalse(bd["base_de_conflits_jointe"])
        for d in bd["details"]:
            ligne = par_iso.get(d["iso3"], {})
            attendu = (q_dec(Fraction(float(ligne[CLE_REVENU])), 0)
                       if est_nb(ligne, CLE_REVENU) else "—")
            self.assertEqual(d["revenu_mesure_pib_h"], attendu, d["iso3"])
            e = effort_de(ligne)
            self.assertEqual(d["effort_fiscal_pct"],
                             q_dec(Fraction(float(e)), 1) if e is not None else "—", d["iso3"])
        self.assertGreaterEqual(bd["revenus_absents"], 1,
                                "aucune absence : la règle d'absence ne serait pas éprouvée")

    def test_le_verdict_rend_compte_sans_adoucir(self):
        ve, f, rs = CERT["verdict"], CERT["falsification"], CERT["riches_sans_armee"]
        self.assertEqual(ve["contre_exemples_mesures"], f["effectif"])
        self.assertEqual(ve["riches_sans_armee_mesures"], rs["zero"])
        self.assertEqual(ve["statut_de_l_enonce_original"], "réfuté par la mesure")
        self.assertIn("non prouvé", ve["statut_de_l_enonce_borne"])
        self.assertEqual(ve["enonce_original"],
                         "il faut etre riche pour faire la guerre = sans richesse pas de guerre")
        self.assertIn(ve["enonce_original"], G.SOURCE["point_de_depart"])
        self.assertEqual(ve["aucune_guerre_datee"], G.PHRASE_ABSENCE)
        self.assertEqual(ve["effort_fiscal_median_pct"], CERT["tresorerie"]["mediane_pct"])


# ─── 4. la vidéo : des minutages, rien d'autre ---------------------------------

class TestReDerivationVideo(unittest.TestCase):
    def test_les_chapitres_sont_croissants_et_dans_la_duree(self):
        cv = CERT["chapitres_video"]
        ch = VIDEO["chapitres"]
        self.assertEqual(cv["nombre"], len(ch))
        secondes = [x["debut_s"] for x in ch]
        self.assertEqual(secondes, sorted(set(secondes)), "horodatages non strictement croissants")
        self.assertLessEqual(secondes[-1], VIDEO["duree_s"])
        self.assertTrue(cv["strictement_croissants"] and cv["sous_la_duree"])
        self.assertEqual(cv["duree_s"], VIDEO["duree_s"])

    def test_chaque_minutage_ecrit_correspond_a_sa_chaine(self):
        for x in VIDEO["chapitres"]:
            h, m, s = [int(p) for p in x["debut"].split(":")]
            self.assertEqual(x["debut_s"], 3600 * h + 60 * m + s, x["debut"])

    def test_le_transcript_reste_a_zero_octet_et_zero_citation(self):
        cv = CERT["chapitres_video"]
        mesures = VIDEO["transcript"]["mesures"]
        self.assertEqual(cv["transcript_etat"], VIDEO["transcript"]["etat"])
        self.assertEqual(len(cv["sondes"]), len(mesures))
        self.assertEqual(cv["transcript_octets"], sum(int(m.rpartition("=")[2]) for m in mesures))
        self.assertEqual(cv["transcript_octets"], 0)
        self.assertEqual(cv["nb_sondes"], 3)
        self.assertEqual(cv["citations_du_transcript"], 0)
        self.assertEqual(cv["nb_chapitres_cites"], len(G.CHAPITRES_CITES))
        for cite in cv["chapitres_cites"]:
            self.assertIn(cite["debut"], [x["debut"] for x in VIDEO["chapitres"]])
        self.assertGreaterEqual(len(cv["avertissements"]), 1)
        self.assertEqual(cv["octets"], len(BRUT_VIDEO))
        self.assertEqual(cv["sha256"], hashlib.sha256(BRUT_VIDEO).hexdigest())
        self.assertEqual(cv["id"], VIDEO["source"]["id"])
        self.assertEqual(cv["chaine"], VIDEO["auteur"])


# ─── 5. règles étrangères au dépôt ---------------------------------------------

class TestLoisSurJeuxEtrangers(unittest.TestCase):
    def test_decimale_half_up_sur_des_rationnels_pris_a_la_main(self):
        self.assertEqual(G._decimale(Fraction(1, 3), 4), "0.3333")
        self.assertEqual(G._decimale(Fraction(2, 3), 4), "0.6667")
        self.assertEqual(G._decimale(Fraction(1, 8), 2), "0.13")
        self.assertEqual(G._decimale(Fraction(-1, 8), 2), "-0.13")
        for v in (Fraction(1, 7), Fraction(22, 7), Fraction(-5, 16), Fraction(0), Fraction(3)):
            for d in (0, 1, 2, 4, 5):
                self.assertEqual(G._decimale(v, d), q_dec(v, d), f"{v} à {d}")

    def test_le_rho_vaut_exactement_un_moins_un_et_neuf_dixiemes(self):
        self.assertEqual(G._spearman([(1.0, 2.0, "a"), (2.0, 4.0, "b"), (3.0, 6.0, "c"),
                                      (4.0, 8.0, "d")]), "1.0000")
        self.assertEqual(G._spearman([(1.0, 8.0, "a"), (2.0, 6.0, "b"), (3.0, 4.0, "c"),
                                      (4.0, 2.0, "d")]), "-1.0000")
        self.assertEqual(G._spearman([(1.0, 1.0, "a"), (2.0, 2.0, "b"), (3.0, 3.0, "c"),
                                      (4.0, 5.0, "d"), (5.0, 4.0, "e")]), "0.9000")

    def test_les_rangs_dependagent_par_code_iso_et_non_par_l_entree(self):
        self.assertEqual(G._rangs([3.0, 1.0, 2.0], ["c", "a", "b"]), [3, 1, 2])
        self.assertEqual(G._rangs([5.0, 5.0, 1.0], ["zz", "aa", "bb"]), [3, 2, 1])
        self.assertEqual(rangs([5.0, 5.0, 1.0], ["zz", "aa", "bb"]),
                         G._rangs([5.0, 5.0, 1.0], ["zz", "aa", "bb"]))

    def test_l_effort_fiscal_rejette_le_denominateur_null(self):
        self.assertIsNone(G._effort({"depense_part_du_pib_pct": 3.0}))
        self.assertIsNone(G._effort({"depense_part_du_pib_pct": 3.0,
                                     "recettes_publiques_part_du_pib_pct": 0.0}))
        self.assertEqual(G._effort({"depense_part_du_pib_pct": 4.0,
                                    "recettes_publiques_part_du_pib_pct": 20.0}), 20.0)
        self.assertEqual(G._nombre(None), "—")
        self.assertEqual(G._nombre(0), q_dec(Fraction(0), 2))

    def test_un_plan_factice_non_nul_garde_ses_barres_proportionnelles(self):
        factice = {"couverture": {"comparables": 40, "avec_recettes": 25, "avec_dette": 30},
                   "falsification": {"effectif": 7}, "riches_sans_armee": {"zero": 3},
                   "chapitres_video": {"nombre": 49},
                   "instruments_protection": {"artefacts_executifs": 0},
                   "limites_ouvertes": {"nb": 5},
                   "verdict": {"contre_exemples_mesures": 7, "riches_sans_armee_mesures": 3}}
        svg = G.octets_svg(factice).decode("utf-8")
        corps = svg.split("<rect ")[1:]
        valeurs = [int(m.split('data-valeur="')[1].split('"')[0]) for m in corps]
        largeurs = [m.split('width="')[1].split('"')[0] for m in corps]
        self.assertEqual(valeurs, [40, 7, 3, 25, 30, 49, 0, 5])
        self.assertEqual(len(largeurs), len(G.BARRES))
        self.assertEqual(largeurs[5], "220.00", "la plus grande barre doit occuper la pleine largeur")
        self.assertEqual(largeurs[6], "0.00", "une grandeur nulle doit rendre une barre nulle")
        self.assertEqual(largeurs, [largeur_barre(v, max(valeurs)) for v in valeurs])
        self.assertIn(G.PHRASE_ABSENCE, svg)

    def test_le_compteur_de_mentions_compte_reelement(self):
        self.assertEqual(G._motif_par_fichier("zzz_impossible_zzz", ["GUERRE/guerre_base.py"]),
                         (0, []))
        n, ou = G._motif_par_fichier("tresor", ["GUERRE/guerre_base.py"])
        self.assertGreater(n, 0)
        self.assertEqual(ou, ["GUERRE/guerre_base.py"])

    def test_le_plan_reel_ne_tient_pas_sur_des_zeros(self):
        pl = CERT["plan_tresor"]
        attendu = [CERT["couverture"]["comparables"], CERT["falsification"]["effectif"],
                   CERT["riches_sans_armee"]["zero"], CERT["couverture"]["avec_recettes"],
                   CERT["couverture"]["avec_dette"], CERT["chapitres_video"]["nombre"],
                   CERT["instruments_protection"]["artefacts_executifs"],
                   CERT["limites_ouvertes"]["nb"]]
        self.assertEqual(pl["valeurs_attendues"], attendu)
        self.assertEqual(pl["valeurs_ecrites"], attendu)
        self.assertEqual(pl["plus_grande_valeur"], max(attendu + [1]))
        self.assertGreater(pl["valeurs_attendues"][0], 100)
        self.assertEqual(pl["barres"], 8)


# ─── 6. les octets publiés se relisent ----------------------------------------

class TestArtefactsSurDisque(unittest.TestCase):
    def setUp(self):
        self._td = TemporaryDirectory(prefix="guerre-artefacts-")
        self.vers = Path(self._td.name)
        self.ecrit = G.ecrire_artefacts(CERT, self.vers)

    def tearDown(self):
        self._td.cleanup()

    def test_les_quatre_artefacts_sont_ecrits_octet_par_octet(self):
        self.assertEqual(sorted(self.ecrit), sorted(G.NOMS_ARTEFACTS))
        attendus = G._artefacts_octets(CERT)
        for nom, taille in self.ecrit.items():
            octets = (self.vers / nom).read_bytes()
            self.assertEqual(octets, attendus[nom], nom)
            self.assertEqual(taille, f"{len(octets)} octets", nom)
            self.assertGreater(len(octets), 200, nom)
        self.assertEqual(sorted(self.ecrit), sorted(CERT["ecritures"]["noms"]))

    def test_le_certificat_scelle_les_trois_autres_octets(self):
        ec = CERT["ecritures"]
        for nom in ec["empreintes"]:
            octets = (self.vers / nom).read_bytes()
            self.assertEqual(ec["tailles"][nom], len(octets), nom)
            self.assertEqual(ec["empreintes"][nom], hashlib.sha256(octets).hexdigest()[:16], nom)
        self.assertNotIn("certificat.json", ec["tailles"], "auto-référence mesurée : mensonge")
        self.assertEqual(sorted(set(G.NOMS_ARTEFACTS) - set(ec["tailles"])),
                         [ec["nom_sans_empreinte"]])
        self.assertEqual(sorted(set(G.NOMS_ARTEFACTS) - set(ec["noms_avec_phrase"])),
                         [ec["nom_sans_phrase"]])

    def test_le_registre_relu_a_une_ligne_par_pays_comparable(self):
        octets = (self.vers / "tresor_et_guerre.csv").read_bytes()
        lignes = list(csv.reader(io.StringIO(octets.decode("utf-8-sig")), delimiter=";"))
        self.assertEqual(octets[:3], b"\xef\xbb\xbf")
        self.assertEqual(octets.count(b"\n"), octets.count(b"\r\n"))
        self.assertEqual(octets.count(b"\r\n"), len(lignes))
        self.assertEqual(lignes[0], list(G.COLONNES_TRESOR))
        corps = lignes[1:]
        self.assertEqual(len(corps), len(COMPARABLES))
        self.assertEqual([l[0] for l in corps], [r["iso3"] for r in TRIEES])
        self.assertEqual([l[2] for l in corps],
                         [q_dec(Fraction(float(r[CLE_MASSE])), 2) for r in TRIEES])
        self.assertEqual([int(l[8]) for l in corps], list(range(1, len(corps) + 1)))
        masses = [float(l[2]) for l in corps]
        self.assertEqual(masses, sorted(masses, reverse=True), "le rang de dépense n'est pas trié")
        sous = sum(1 for l in corps if l[9] == "oui")
        self.assertEqual(sous, CERT["falsification"]["population_sous_mediane"])
        self.assertEqual(sous, sum(1 for r in COMPARABLES if r[CLE_REVENU] < MEDIANE_REVENU))
        self.assertEqual(sum(1 for l in corps if l[9] not in ("oui", "non")), 0)
        efforts = sum(1 for l in corps if l[7] != "—")
        self.assertEqual(efforts, sum(1 for r in COMPARABLES if effort_de(r) is not None))
        for l in corps:
            self.assertEqual(len(l), len(G.COLONNES_TRESOR), l[0])
            self.assertNotIn(";", l[1], l[1])
        self.assertNotIn(G.PHRASE_ABSENCE.encode("utf-8"), octets,
                         "une ligne de commentaire serait lue comme une donnée")
        self.assertEqual(len(octets), CERT["plan_tresor"]["octets_registre"])

    def test_le_plan_relu_porte_huit_barres_nommees_et_chiffrees(self):
        texte = (self.vers / "frontiere_tresor.svg").read_text(encoding="utf-8")
        corps = texte.split("<rect ")[1:]
        self.assertEqual(len(corps), len(G.BARRES))
        self.assertEqual([m.split('data-libelle="')[1].split('"')[0] for m in corps],
                         [lib for lib, _, _ in G.BARRES])
        valeurs = [int(m.split('data-valeur="')[1].split('"')[0]) for m in corps]
        self.assertEqual(valeurs, CERT["plan_tresor"]["valeurs_ecrites"])
        self.assertEqual(valeurs, CERT["plan_tresor"]["valeurs_attendues"])
        largeurs = [m.split('width="')[1].split('"')[0] for m in corps]
        self.assertEqual(largeurs, [largeur_barre(v, max(valeurs)) for v in valeurs])
        self.assertEqual(texte.count("<text "), 2 * len(G.BARRES) + 1)
        self.assertIn(G.PHRASE_ABSENCE, texte)
        self.assertIn(G.PHRASE_VERIFIEE, texte)
        self.assertEqual(len(texte.encode("utf-8")), CERT["plan_tresor"]["octets"])

    def test_le_md_relu_rend_l_enonce_sans_le_eriger_en_loi(self):
        lignes = (self.vers / "guerre_et_tresor.md").read_text(encoding="utf-8").splitlines()
        self.assertEqual(sum(1 for l in lignes if l.startswith("- ")),
                         3 + CERT["limites_ouvertes"]["nb"])
        tableau = [l for l in lignes if l.startswith("|")]
        self.assertEqual(len(tableau), 7)
        for l in tableau:
            self.assertEqual(len([c for c in l.strip("|").split("|")]), 3, l)
        for l in lignes:
            if "sans richesse pas de guerre" in l:
                self.assertTrue("réfut" in l or "testée" in l, l)
        self.assertIn("## Limites ouvertes", lignes)
        self.assertIn(G.PHRASE_ABSENCE, lignes[-1])
        self.assertIn(G.PHRASE_VERIFIEE, lignes[-1])

    def test_le_json_relu_se_recharge_a_l_identique(self):
        relu = json.loads((self.vers / "certificat.json").read_bytes().decode("utf-8"))
        self.assertEqual(sorted(relu), sorted(CERT))
        for cle in NOEUDS:
            self.assertEqual(canon(relu[cle]), canon(CERT[cle]), cle)
        self.assertEqual(relu["racine_merkle_sha256"], RACINE)
        self.assertTrue(relu["rejoue_identique"])

    def test_un_nombre_mue_sur_disque_ne_passe_plus_la_relecture(self):
        chemin = self.vers / "frontiere_tresor.svg"
        avant = chemin.read_bytes()
        premiere = CERT["plan_tresor"]["valeurs_ecrites"][0]
        mue = avant.decode("utf-8").replace(f'data-valeur="{premiere}"',
                                            f'data-valeur="{premiere + 1}"', 1)
        self.assertNotEqual(mue, avant.decode("utf-8"), "rien à muer : relecture verte pour rien")
        chemin.write_bytes(mue.encode("utf-8"))
        relu = [int(m.split('data-valeur="')[1].split('"')[0])
                for m in chemin.read_text(encoding="utf-8").split("<rect ")[1:]]
        self.assertNotEqual(relu, CERT["plan_tresor"]["valeurs_ecrites"])
        for nom in G.NOMS_ARTEFACTS:
            if nom != "frontiere_tresor.svg":
                self.assertEqual((self.vers / nom).read_bytes(),
                                 G._artefacts_octets(CERT)[nom], nom)

    def test_ecrire_deux_fois_ne_deplace_rien(self):
        premier = {n: (self.vers / n).read_bytes() for n in G.NOMS_ARTEFACTS}
        G.ecrire_artefacts(CERT, self.vers)
        for n, octets in premier.items():
            self.assertEqual((self.vers / n).read_bytes(), octets, n)


# ─── 7. non-vacuité : une mutation par contrôle --------------------------------

class TestChaqueControlePeutRougir(unittest.TestCase):
    MUTATIONS = {
        "C01": ("source_tresor", "lignes", 999),
        "C02": ("couverture", "ratio_exploitable_pct", "99.99"),
        "C03": ("masses", "top_dix_pct", "77.00"),
        "C04": ("charge_relative", "la_charge_ne_croit_pas_avec_le_revenu", False),
        "C05": ("capacite_absolue", "spearman_revenu_masse", "0.0000"),
        "C06": ("falsification", "l_absolue_est_refutee", False),
        "C07": ("extreme_mesure", "est_le_maximum_mesure", False),
        "C08": ("riches_sans_armee", "tous_au_dessus_de_la_mediane", False),
        "C09": ("tresorerie", "massifs", 0),
        "C10": ("verdict", "contre_exemples_mesures", 99),
        "C11": ("belligerants_declares", "statut_du_fait", "prouvé par le dépôt"),
        "C12": ("emulateur_hors_sujet", "apport_de_l_emulateur_dans_ce_dossier", 3),
        "C13": ("instruments_protection", "artefacts_executifs", 1),
        "C14": ("chapitres_video", "citations_du_transcript", 1),
        "C15": ("plan_tresor", "largeurs_conformes", False),
        "C16": ("limites_ouvertes", "remplies_dans_ce_lot", 1),
    }

    def test_tous_les_controles_sont_verts_avant_mutation(self):
        self.assertEqual([c for c, v in CS.items() if not v["ok"]], [])
        self.assertEqual(len(CS), len(G.NOEUDS))
        self.assertEqual(sorted(CS), [f"C{i:02d}" for i in range(1, 17)])
        self.assertEqual(len(NOEUDS), len(G.MESURES) + 2)

    def test_chaque_mutation_fait_rougir_un_seul_controle(self):
        for id_, (noeud, cle, valeur) in sorted(self.MUTATIONS.items()):
            with self.subTest(controle=id_):
                mue = copy.deepcopy(CERT)
                self.assertIn(cle, mue[noeud], f"{noeud} ne porte pas {cle}")
                mue[noeud][cle] = valeur
                rendu = grille_de(mue)
                rouges = sorted(c for c, v in rendu.items() if not v["ok"])
                self.assertEqual(rouges, [id_], rendu[id_]["obtenu"])

    def test_chaque_mutation_change_le_message_d_obtenu(self):
        """Un contrôle qui rougit sans changer de message ne lit pas le nœud mué."""
        for id_, (noeud, cle, valeur) in sorted(self.MUTATIONS.items()):
            with self.subTest(controle=id_):
                mue = copy.deepcopy(CERT)
                mue[noeud][cle] = valeur
                self.assertNotEqual(grille_de(mue)[id_]["obtenu"], CS[id_]["obtenu"])

    def test_la_grille_de_l_auditeur_est_reecrite_ici_et_tombe_juste(self):
        born = sum(1 for e in EQS.values() if len(str(e["limite"]).strip()) >= 40)
        chemins = sum(1 for e in EQS.values() if "→" in str(e["chemin"]))
        statuts = sum(1 for e in EQS.values() if e["statut"] in FB.STATUTS)
        couches = sum(1 for e in EQS.values() if e["couche"] in FB.COUCHES)
        self.assertEqual((born, chemins, statuts, couches), (16, 16, 16, 16))
        self.assertEqual([e["id"] for e in EQS.values()], [f"EQ-{i:02d}" for i in range(1, 17)])
        self.assertEqual(sorted(e["id"] for e in EQS.values()),
                         sorted(CS[c]["equation"] for c in CS))
        for c in CS.values():
            self.assertTrue(c["attendu"] and c["obtenu"] and c["verifie"] and c["nom"], c["id"])
        for e in EQS.values():
            self.assertEqual(e["piliers"], ["P1 UNITE", "P2 BORNE", "P3 CONFRONTATION",
                                            "P4 TRANSMISSION"], e["id"])

    def test_changer_un_noeud_change_la_racine(self):
        self.assertEqual(racine_depuis(NOEUDS), RACINE)
        self.assertEqual(CERT["taille_octets"], len(canon(NOEUDS)))
        self.assertEqual(CERT["empreinte_execution"], hashlib.sha256(canon(NOEUDS)).hexdigest())
        mue = copy.deepcopy(NOEUDS)
        mue["verdict"]["contre_exemples_mesures"] = 10 ** 6
        self.assertNotEqual(racine_depuis(mue), RACINE)
        for cle in ("limites", "attribution", "source"):
            self.assertNotIn(cle, NOEUDS, f"{cle} ne doit pas entrer dans la racine")
        self.assertRegex(RACINE, r"^[0-9a-f]{64}$")


# ─── 8. ce qui ne sert pas est compté quand même -------------------------------

class TestHorsSujetEtNonProtege(unittest.TestCase):
    def test_l_emulateur_n_entre_pas_dans_ce_dossier(self):
        em = CERT["emulateur_hors_sujet"]
        brut = (RACINE_DEPOT / G.CHEMIN_EMULATEUR).read_bytes()
        texte = brut.decode("utf-8", "replace")
        self.assertEqual(em["octets"], len(texte.encode("utf-8")))
        self.assertEqual(em["sha256"], hashlib.sha256(brut).hexdigest())
        self.assertEqual(em["sous_commandes"],
                         len(set(re.findall(r"^def (cmd_\w+)", texte, re.M))))
        for terme in G.FINANCE_HORS_EMULATEUR:
            self.assertEqual(em["mentions_de_finance"][terme], texte.lower().count(terme.lower()),
                             terme)
        self.assertTrue(em["aucune_grandeur_de_finance"])
        self.assertTrue(em["jamais_appel"])
        self.assertEqual(em["apport_de_l_emulateur_dans_ce_dossier"], 0)
        self.assertIn("classique", em["declaration_lue"])
        self.assertGreater(em["corpus_hors_ce_module"], 100)

    def test_la_protection_reste_un_mot(self):
        ip = CERT["instruments_protection"]
        executifs = [c for c in G._chemins_sous_arbre()
                     if Path(c).suffix.lower() in G.EXTENSIONS_EXECUTIVES]
        self.assertEqual(ip["chemins_executifs"], executifs)
        self.assertEqual(ip["artefacts_executifs"], len(executifs))
        self.assertEqual(ip["personnes_protegeables_par_ce_depot"], 0)
        self.assertTrue(ip["le_texte_ne_protege_pas"])
        self.assertEqual(ip["mentions_total"], sum(v["occurrences"] for v in ip["mentions"].values()))
        self.assertGreater(ip["mentions_total"], 0, "corpus sans mot : mesure creuse")
        self.assertEqual(ip["statut_de_la_demande"],
                         "déclaré · non vérifié et non exécutable par ce dépôt")

    def test_le_corpus_auto_exclut_le_module_et_ses_tests(self):
        corpus = G._corpus_texte()
        self.assertEqual(len(corpus), len(set(corpus)))
        for c in G.EXCLUS_AUTO:
            self.assertNotIn(c, corpus, c)
            self.assertTrue((RACINE_DEPOT / c).exists(), f"exclusion fantôme : {c}")
        self.assertEqual(sorted(G.EXCLUS_AUTO),
                         ["GUERRE/guerre_base.py", "GUERRE/tests/test_guerre.py"])
        dossier = CERT["emulateur_hors_sujet"]["fichiers_de_ce_dossier_scrutes"]
        self.assertIn("GUERRE/tests/test_guerre.py", dossier,
                      "le dossier doit se compter lui-même, tests compris")
        self.assertIn("GUERRE/guerre_base.py", dossier)

    def test_aucun_signal_d_appel_n_est_ecrit_dans_les_sources_du_dossier(self):
        sources = [c for c in G._chemins_sous_arbre()
                   if c.startswith("GUERRE/") and Path(c).suffix == ".py"]
        self.assertGreaterEqual(len(sources), 2)
        for chemin in sources:
            texte = (RACINE_DEPOT / chemin).read_text(encoding="utf-8")
            for signal in G.SIGNAUX_APPEL_EMULATEUR:
                self.assertNotIn(signal, texte, f"{signal} lu dans {chemin}")

    def test_le_module_n_importe_que_la_bibliotheque_standard(self):
        texte = (RACINE_DEPOT / "GUERRE/guerre_base.py").read_text(encoding="utf-8")
        racines = set()
        for n in ast.walk(ast.parse(texte)):
            if isinstance(n, ast.Import):
                racines |= {a.name.split(".")[0] for a in n.names}
            elif isinstance(n, ast.ImportFrom) and n.module and n.level == 0:
                racines.add(n.module.split(".")[0])
        self.assertEqual(sorted(racines), ["FONDATION", "__future__", "fractions", "hashlib",
                                           "json", "pathlib", "re", "statistics", "sys", "typing"])
        self.assertIn('if __name__ == "__main__":', texte)
        self.assertTrue(G.verifier({"controles": list(CS.values())}))


# ─── 9. limites, bornes et phrases qui ne doivent pas apparaître ---------------

class TestLimitesEtLangage(unittest.TestCase):
    def test_les_dix_limites_restent_ouvertes_et_longues(self):
        lo = CERT["limites_ouvertes"]
        self.assertEqual(lo["nb"], len(lo["liste"]))
        self.assertGreaterEqual(lo["nb"], 8)
        self.assertEqual(lo["remplies_dans_ce_lot"], 0)
        for l in lo["liste"]:
            self.assertGreaterEqual(len(l), 40, l)
        self.assertTrue(any(G.PHRASE_ABSENCE in l for l in lo["liste"]))
        self.assertEqual(lo["seuil_platitude_declare"],
                         q_dec(Fraction(float(G.SEUIL_CHARGE_PLATE)), 2))
        self.assertEqual(lo["seuil_effort_declare"],
                         q_dec(Fraction(float(G.SEUIL_EFFORT_MASSIF)), 2))
        self.assertEqual(lo["la_quatrieme_absence"], "aucune protection promise")
        self.assertEqual(len(CERT["limites"]), lo["nb"] + 1)

    def test_les_deux_seuils_sont_dits_choix_d_auteur(self):
        self.assertIn("choix d'auteur", CERT["charge_relative"]["regle"])
        self.assertIn("choix d'auteur", CERT["limites_ouvertes"]["liste"][-1])
        self.assertIn("contestés", CERT["limites_ouvertes"]["liste"][-1])

    def test_un_interdit_n_apparait_que_comme_interdit(self):
        rendu = G._artefacts_octets(CERT)
        self.assertEqual(sorted(rendu), sorted(G.NOMS_ARTEFACTS))
        for nom in ("tresor_et_guerre.csv", "guerre_et_tresor.md", "frontiere_tresor.svg"):
            texte = rendu[nom].decode("utf-8")
            for p in G.INTERDITS:
                self.assertNotIn(p, texte, f"{p} dans {nom}")
        relu = json.loads(rendu["certificat.json"].decode("utf-8"))
        brut = canon(relu).decode("utf-8")
        self.assertEqual(sorted(relu["ecritures"]["liste_des_phrases_interdites"]),
                         sorted(G.INTERDITS))
        self.assertIn("sans richesse pas de guerre est une loi", brut,
                      "la liste des interdits n'est plus publiée : la règle serait invisible")
        filtre = sans_la_liste(relu)
        for p in G.INTERDITS:
            self.assertNotIn(p, canon(filtre).decode("utf-8"),
                             f"{p} ailleurs que dans la liste des interdits")
        for e in EQS.values():
            t = canon(sans_la_liste(e)).decode("utf-8")
            for p in G.INTERDITS:
                self.assertNotIn(p, t, f"{p} dans {e['id']}")
        self.assertTrue(CERT["ecritures"]["interdits_hors_des_octets"])
        self.assertIn("certificat", CERT["ecritures"]["ou_la_liste_est_lisible"])

    def test_la_refutation_et_l_absence_sont_ecrites_cote_a_cote(self):
        md = G._artefacts_octets(CERT)["guerre_et_tresor.md"].decode("utf-8")
        self.assertIn("réfuté", md)
        self.assertIn("sans richesse pas de guerre", md)
        self.assertNotIn("sans richesse pas de guerre est une loi", md)
        self.assertIn("ne prédit aucun conflit", md)
        self.assertIn(G.PHRASE_VERIFIEE, md)
        self.assertIn(G.PHRASE_ABSENCE, md)

    def test_les_noeuds_externes_declares_existent_sur_disque(self):
        chemins = set()
        for n in G.NOEUDS.values():
            chemins |= set(n["externe"])
        self.assertGreaterEqual(len(chemins), 3)
        for c in sorted(chemins):
            self.assertTrue((RACINE_DEPOT / c).exists(), c)
        self.assertEqual(len(G.NOEUDS), 16)
        for i, n in G.NOEUDS.items():
            for x in n["depend"]:
                self.assertIn(x, G.NOEUDS, f"{i} dépend de {x} qui n'existe pas")
                self.assertLess(x, i, f"{i} dépend d'un nœud postérieur")

    def test_resoudre_tombe_juste_de_bout_en_bout(self):
        donnees = G.resoudre()
        self.assertEqual(donnees["conclusion"]["controles_verts"], 16)
        self.assertEqual(donnees["conclusion"]["controles_total"], 16)
        self.assertEqual(donnees["conclusion"]["equations"], 16)
        self.assertEqual(donnees["conclusion"]["limites_ouvertes"], 10)
        self.assertEqual(donnees["conclusion"]["racine_merkle_sha256"], RACINE)
        self.assertTrue(G.verifier(donnees))
        self.assertEqual(donnees["conclusion"]["statuts_par_label"]["OPÉRATIONNEL"], 14)
        self.assertEqual(donnees["conclusion"]["statuts_par_label"]["SPÉCIFIÉ"], 2)
        self.assertEqual(sum(donnees["conclusion"]["statuts_par_label"].values()), 16)


if __name__ == "__main__":
    unittest.main(verbosity=2)
