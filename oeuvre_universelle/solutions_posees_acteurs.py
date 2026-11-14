# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""Solutions posées par les acteurs de « L'AFTER » : équations et contrôles exécutables.

Source du parcours : « L'AFTER : Jensen Huang viré, Anthropic surpuissant, Musk contre
Breton ! », Silicon Carne (YouTube, 99d88_rcjak, 6 540 s). La vidéo fournit treize
chapitres horodatés et AUCUNE transcription accessible (timedtext : 0 octet sur json3,
srv3 et xml, mesuré le 2026-11-13). Elle donne donc des thèmes et des horodatages, jamais
des citations : aucun propos, aucun chiffre n'est affirmé « dit dans la vidéo ».

Ce que fait le module : chaque chapitre nomme un problème et les acteurs nomment une
solution (plan de succession, retour du fondateur, dual-class ou nationalisation,
arbitrage recherche/IPO, automatisation de tableur, régime de preuve, simulation d'un
univers, correction de la polarisation, partage du travail, consentement local, monnaie
de réserve, capacité de l'État). Une solution sans coût calculable n'est pas une
solution : chacune est posée en équation, résolue en arithmétique exacte
(``fractions.Fraction``) ou par dénombrement fini, puis contrôlée par une SECONDE route
indépendante — boucle contre forme fermée, dénombrement de chemins contre puissance de
matrice, deux énumérations de coalitions, algèbre contre bissection, permutations contre
programmation dynamique, comptage individuel contre formule de Bayes, trois formules de
Gini, récurrence contre algèbre, force brute contre DP.

Statuts : OPÉRATIONNEL = identité ou dénombrement fini démontré ici ; SIMULÉ = modèle à
paramètres déclarés, le nombre dépend d'une hypothèse écrite dans ce fichier ; SPÉCIFIÉ =
grandeur externe datée, non mesurée dans ce dépôt. Aucune donnée d'entreprise, aucune
mesure, aucune prévision n'est produite.

Usage :
    py -3 oeuvre_universelle/solutions_posees_acteurs.py
    py -3 oeuvre_universelle/solutions_posees_acteurs.py --rapport
"""

from __future__ import annotations

import itertools
import json
import math
import sys
from datetime import datetime, timezone
from fractions import Fraction as Q
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

RACINE = Path(__file__).resolve().parents[1]
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

import reseau_poids_sparse_mizan as socle  # noqa: E402

FICHIER = "solutions_posees_acteurs.py"
STATUTS = ("OPÉRATIONNEL", "SIMULÉ", "SPÉCIFIÉ")

# ── 1. Source : chapitres verbatim, transcript mesuré absent ────────────────

SOURCE: Dict[str, object] = {
    "titre": "L'AFTER : Jensen Huang viré, Anthropic surpuissant, Musk contre Breton !",
    "chaine": "Silicon Carne",
    "video_id": "99d88_rcjak",
    "url": "https://www.youtube.com/watch?v=99d88_rcjak",
    "duree_s": 6540,
    "chapitres_publics": 13,
    "transcript": "absent — timedtext 0 octet sur json3, srv3 et xml (mesuré 2026-11-13)",
    "avertissements": [
        "aucun en-tête de chapitres dans la description : horodatages pris dans toute la description",
        "les chapitres sont des thèmes, pas des citations ; aucun propos n'est attribué à la vidéo",
    ],
}

CHAPITRES: Tuple[Tuple[str, int, str], ...] = (
    ("00:00", 0, "— Sommaire"),
    ("03:03", 183, "— Jensen Huang viré de Nvidia : chute ou assassinat ?"),
    ("11:05", 665, "— Jensen Huang peut-il revenir comme Steve Jobs ?"),
    ("19:50", 1190, "— Nvidia sans Jensen : nationalisation ou empire familial ?"),
    ("30:44", 1844, "— Claude Fable : soigner le cancer ou vendre l'IPO ?"),
    ("42:34", 2554, "— Claude Sheets : l'IA prend d'assaut vos tableurs"),
    ("52:40", 3160, "— Création IA : naviguer quand la tech devient coupable"),
    ("01:04:40", 3880, "— L'ère des démiurges : créer des univers entiers"),
    ("01:14:30", 4470, "— L'IA polarise tout : retour au vivant, règne du 1%"),
    ("01:23:27", 5007, "— La fin du travail : mythe ou vraie menace ?"),
    ("01:36:19", 5779, "— Backlash anti-data centers : peur ou haine économique ?"),
    ("01:39:25", 5965, "— Breton vs Musk : l'Europe humiliée en Afrique"),
    ("01:45:15", 6315, "— La France se fissure : émeutes et État défaillant"),
)

ANCRAGE_CHAPITRE: Dict[str, int] = {f"EQ-{i:02d}": i for i in range(1, 13)}
ANCRAGE_CHAPITRE["EQ-13"] = 0  # la synthèse porte sur les douze, pas sur un chapitre


def chapitres_ancres() -> List[Dict[str, object]]:
    sorts = []
    for eq in sorted(ANCRAGE_CHAPITRE):
        debut, debut_s, titre = CHAPITRES[ANCRAGE_CHAPITRE[eq]]
        sorts.append({"equation": eq, "debut": debut, "debut_s": debut_s, "titre": titre})
    return sorts


# ── 2. Paramètres DÉCLARÉS : aucun n'est une donnée d'entreprise ────────────

PARAMETRES: Tuple[Dict[str, str], ...] = (
    {"id": "P_SORTIE", "grandeur": "probabilité annuelle de départ du dirigeant",
     "valeur": "0,03", "nature": "hypothèse de modèle"},
    {"id": "M_RETOUR", "grandeur": "matrice de transition en place / dehors / revenu",
     "valeur": "lignes 85/10/5, 0/75/25, 30/0/70 en %", "nature": "hypothèse de modèle"},
    {"id": "JEUX_VOTE", "grandeur": "jeux de vote pondéré étudiés",
     "valeur": "[51 ; 48, 48, 4] et [60 ; 50, 49, 2]", "nature": "structures fictiles"},
    {"id": "RD_IPO", "grandeur": "coût, rente, taux et durée de la recherche",
     "valeur": "400 M$, 140 M$/an, 5 %, 10 ans", "nature": "hypothèse de modèle"},
    {"id": "FEUILLE", "grandeur": "graphe de dépendances de tableur",
     "valeur": "7 cellules, 11 arcs", "nature": "objet de démonstration"},
    {"id": "SIGNAL", "grandeur": "population, prévalence, sensibilité, spécificité",
     "valeur": "10^6 · 12 000 · 0,90 · 0,95", "nature": "hypothèse de modèle"},
    {"id": "GINI", "grandeur": "part du centile supérieur",
     "valeur": "20 % pour 1 % de la population", "nature": "hypothèse de modèle"},
    {"id": "TACHES", "grandeur": "grille de tâches",
     "valeur": "60 tâches de lourdeur 1..60 ; propension 0,8 pour 1..30, 0,2 pour 31..60",
     "nature": "hypothèse de modèle"},
    {"id": "DATA_CENTRE", "grandeur": "site, eau, emplois, fiscalité, nuisance",
     "valeur": "120 MW · 2 L/kWh · 400 emplois · 18 M$/an · 0,18 M$/MW",
     "nature": "hypothèse de modèle"},
    {"id": "RESERVE", "grandeur": "parts de réserve et croissance mondiale",
     "valeur": "20 % → 25 % en 10 ans, croissance 4 %/an", "nature": "ordres de grandeur externes"},
    {"id": "DETTE", "grandeur": "r, g, dette initiale, cible, horizon",
     "valeur": "3 % · 1,5 % · 110 % · 100 % · 12 ans", "nature": "hypothèse de modèle"},
    {"id": "BUDGET", "grandeur": "budget commun aux douze solutions",
     "valeur": "1 000 GWh", "nature": "hypothèse de modèle"},
)


def _n(valeur: object) -> str:
    """Forme comparable d'une valeur : point décimal, décimales superflues retirées.

    Le contrat du registre exige des champs textuels. Les scalaires, les listes et les
    dictionnaires rendent donc toujours par une chaîne, jamais par la repr Python d'un
    Fraction — un dictionnaire devient « cle=valeur; cle=valeur ».
    """
    if isinstance(valeur, Q):
        return f"{float(valeur):.9f}".rstrip("0").rstrip(".")
    if isinstance(valeur, bool):
        return str(valeur)
    if isinstance(valeur, float):
        return f"{valeur:.9f}".rstrip("0").rstrip(".")
    if isinstance(valeur, dict):
        return "; ".join(f"{cle}={_n(v)}" for cle, v in valeur.items())
    if isinstance(valeur, (list, tuple)):
        return "[" + ", ".join(_n(x) for x in valeur) + "]"
    return str(valeur)


# ── 3. I — Dépendance à un dirigeant (03:03) ───────────────────────────────

P_SORTIE = Q(3, 100)
HORIZON_MANDAT = 20


def survie_dirigeant(p: Q = P_SORTIE, n: int = HORIZON_MANDAT) -> Q:
    """S(n) = (1 − p)^n."""
    return (1 - p) ** n


def somme_survie_boucle(p: Q = P_SORTIE, n: int = HORIZON_MANDAT) -> Q:
    """Σ_{k=0}^{n−1} (1 − p)^k terme à terme : la route lente."""
    total, terme = Q(0), Q(1)
    for _ in range(n):
        total += terme
        terme *= (1 - p)
    return total


def esperance_mandat(p: Q = P_SORTIE, n: int = HORIZON_MANDAT) -> Q:
    """Même somme en forme fermée : (1 − (1 − p)^n)/p."""
    return (1 - (1 - p) ** n) / p


# ── 4. II — Le retour du fondateur (11:05) ─────────────────────────────────

M_RETOUR: Tuple[Tuple[Q, ...], ...] = (
    (Q(85, 100), Q(10, 100), Q(5, 100)),
    (Q(0), Q(75, 100), Q(25, 100)),
    (Q(30, 100), Q(0), Q(70, 100)),
)
HORIZON_RETOUR = 5


def produit_matrices(a, b):
    n = len(a)
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(n)) for j in range(n))
                 for i in range(n))


def puissance_matrice(m, n: int):
    r = tuple(tuple(Q(int(i == j)) for j in range(len(m))) for i in range(len(m)))
    for _ in range(n):
        r = produit_matrices(r, m)
    return r


def prob_retour_par_chemins(m=M_RETOUR, n: int = HORIZON_RETOUR, etat_cible: int = 2) -> Q:
    """Dénombrement des 3^n chemins, sans algèbre linéaire."""
    total = Q(0)
    for chemin in itertools.product(range(len(m)), repeat=n):
        precedent, poids = 0, Q(1)
        for courant in chemin:
            poids *= m[precedent][courant]
            if poids == 0:
                break
            precedent = courant
        else:
            if precedent == etat_cible:
                total += poids
    return total


def prob_retour_par_matrice(m=M_RETOUR, n: int = HORIZON_RETOUR, etat_cible: int = 2) -> Q:
    return puissance_matrice(m, n)[0][etat_cible]


# ── 5. III — Qui contrôle sans les voix ? (19:50) ──────────────────────────

JEUX_VOTE: Dict[str, Tuple[int, Tuple[int, ...]]] = {
    "dual_class_etat": (51, (48, 48, 4)),
    "adherent_inutile": (60, (50, 49, 2)),
}


def swings_par_coalitions(quota: int, poids: Sequence[int]) -> List[int]:
    """Route 1 : parcourir les 2^n coalitions et tester la criticité de chaque membre."""
    n = len(poids)
    bruts = [0] * n
    for masque in range(1 << n):
        total = sum(poids[i] for i in range(n) if masque >> i & 1)
        if total >= quota:
            for i in range(n):
                if masque >> i & 1 and total - poids[i] < quota:
                    bruts[i] += 1
    return bruts


def swings_par_retrait(quota: int, poids: Sequence[int]) -> List[int]:
    """Route 2 : pour chaque joueur, énumérer les coalitions des AUTRES."""
    bruts = []
    for i, p_i in enumerate(poids):
        autres = [poids[j] for j in range(len(poids)) if j != i]
        critiques = 0
        for k in range(len(autres) + 1):
            for sous in itertools.combinations(autres, k):
                total = sum(sous)
                if total < quota <= total + p_i:
                    critiques += 1
        bruts.append(critiques)
    return bruts


def index_banzhaf(quota: int, poids: Sequence[int]) -> List[Q]:
    bruts = swings_par_retrait(quota, poids)
    total = sum(bruts)
    return [Q(b, total) if total else Q(0) for b in bruts]


# ── 6. IV — Soigner le cancer ou vendre l'IPO (30:44) ──────────────────────

COUT_RD = Q(400_000_000)
RENTE_RD = Q(140_000_000)
TAUX_ACTUARIEL = Q(5, 100)
DUREE_RD = 10


def somme_annuite(r: Q = TAUX_ACTUARIEL, n: int = DUREE_RD) -> Q:
    return sum(Q(1) / (1 + r) ** t for t in range(1, n + 1))


def annuite_fermee(r: Q = TAUX_ACTUARIEL, n: int = DUREE_RD) -> Q:
    return (1 - (1 + r) ** (-n)) / r


def utilite_actuarielle(p: Q, cout: Q = COUT_RD, rente: Q = RENTE_RD,
                        r: Q = TAUX_ACTUARIEL, n: int = DUREE_RD) -> Q:
    return p * rente * annuite_fermee(r, n) - cout


def seuil_indifference(cout: Q = COUT_RD, rente: Q = RENTE_RD,
                       r: Q = TAUX_ACTUARIEL, n: int = DUREE_RD) -> Q:
    """p* explicite : l'espérance de la recherche égale exactement son coût."""
    return cout / (rente * annuite_fermee(r, n))


def racine_bissection(f, borne_basse: float, borne_haute: float,
                      tolerance: float = 1e-15, pas: int = 200) -> float:
    a, b = borne_basse, borne_haute
    fa = f(a)
    for _ in range(pas):
        m = (a + b) / 2.0
        fm = f(m)
        if (fa > 0) == (fm > 0):
            a, fa = m, fm
        else:
            b = m
        if b - a < tolerance:
            break
    return (a + b) / 2.0


def seuil_indifference_par_bissection() -> float:
    pente = float(RENTE_RD * annuite_fermee())
    constante = float(-COUT_RD)
    return racine_bissection(lambda x: pente * x + constante, 0.0, 1.0)


# ── 7. V — Le tableur est un graphe (42:34) ────────────────────────────────

FEUILLE: Dict[str, Tuple[str, ...]] = {
    "A1": (), "A2": (),
    "B1": ("A1", "A2"),
    "B2": ("A1", "B1"),
    "C1": ("A2", "B1"),
    "C2": ("B1", "B2"),
    "D1": ("C1", "C2", "B2"),
}


def ordre_valide(perm: Sequence[str], feuille: Dict[str, Tuple[str, ...]] = FEUILLE) -> bool:
    vues = set()
    for cell in perm:
        if any(pre not in vues for pre in feuille[cell]):
            return False
        vues.add(cell)
    return True


def extensions_par_permutations(feuille: Dict[str, Tuple[str, ...]] = FEUILLE) -> int:
    cellules = list(feuille)
    return sum(1 for p in itertools.permutations(cellules) if ordre_valide(p))


def extensions_par_dp(feuille: Dict[str, Tuple[str, ...]] = FEUILLE) -> int:
    """Route 2 : sur chaque sous-ensemble S, le dernier évalué doit être maximal dans S."""
    cellules = list(feuille)
    n = len(cellules)
    position = {c: i for i, c in enumerate(cellules)}
    predecesseurs = [sum(1 << position[p] for p in feuille[c]) for c in cellules]
    etat = [0] * (1 << n)
    etat[0] = 1
    for sous in range(1, 1 << n):
        total = 0
        for i in range(n):
            if sous >> i & 1 and not (sous & ~(1 << i)) & predecesseurs[i]:
                total += etat[sous & ~(1 << i)]
        etat[sous] = total
    return etat[(1 << n) - 1]


def descendance(celle: str, feuille: Dict[str, Tuple[str, ...]] = FEUILLE) -> frozenset:
    enfants: Dict[str, List[str]] = {c: [] for c in feuille}
    for c, pres in feuille.items():
        for p in pres:
            enfants[p].append(c)
    vus, pile = set(), list(enfants[celle])
    while pile:
        x = pile.pop()
        if x not in vus:
            vus.add(x)
            pile.extend(enfants[x])
    return frozenset(vus)


def rayon_correction(feuille: Dict[str, Tuple[str, ...]] = FEUILLE) -> Dict[str, int]:
    """Une formule fausse sur une cellule corrompt la cellule et ses descendantes."""
    return {c: 1 + len(descendance(c, feuille)) for c in feuille}


# ── 8. VI — Naviguer quand la tech devient coupable (52:40) ────────────────

POPULATION = 1_000_000
INFRACTIONS = 12_000
SENSIBILITE = Q(90, 100)
SPECIFICITE = Q(95, 100)


def comptes_signalement(population: int = POPULATION, infractions: int = INFRACTIONS,
                        sensibilite: Q = SENSIBILITE, specificite: Q = SPECIFICITE
                        ) -> Tuple[int, int, int]:
    vp = int(Q(infractions) * sensibilite)
    fp = int(Q(population - infractions) * (1 - specificite))
    return vp, fp, infractions - vp


def vpn_par_formule(population: int = POPULATION, infractions: int = INFRACTIONS,
                    sensibilite: Q = SENSIBILITE, specificite: Q = SPECIFICITE) -> Q:
    vp, fp, _ = comptes_signalement(population, infractions, sensibilite, specificite)
    return Q(vp, vp + fp)


def vpn_par_denombrement(population: int = POPULATION, infractions: int = INFRACTIONS,
                         sensibilite: Q = SENSIBILITE, specificite: Q = SPECIFICITE) -> Q:
    """Même nombre sans formule : on itère sur la population finie et on compte."""
    vp_attendus, fp_attendus, _ = comptes_signalement(population, infractions,
                                                      sensibilite, specificite)
    vp = fp = 0
    for i in range(population):
        reel = i < infractions
        signale = i < vp_attendus or infractions <= i < infractions + fp_attendus
        if reel and signale:
            vp += 1
        elif signale:
            fp += 1
    if (vp, fp) != (vp_attendus, fp_attendus):
        raise AssertionError("dénombrement incohérent avec les comptes déclarés")
    return Q(vp, vp + fp)


def part_manquee(sensibilite: Q = SENSIBILITE) -> Q:
    return 1 - sensibilite


# ── 9. VII — Créer des univers entiers (01:04:40) ──────────────────────────

def enumeration_etats(alphabet: int, variables: int) -> int:
    return sum(1 for _ in itertools.product(range(alphabet), repeat=variables))


def espace_etats(alphabet: int, variables: int) -> int:
    return alphabet ** variables


def variables_max_boucle(capacite: int, alphabet: int) -> int:
    """Combien de variables de base `alphabet` tiennent dans `capacite` adresses."""
    n, total = 0, 1
    while total * alphabet <= capacite:
        total *= alphabet
        n += 1
    return n


def variables_max_log(capacite: int, alphabet: int) -> int:
    """Seconde route : estimation flottante de log, redressée par deux comparaisons exactes."""
    n = int(math.log(capacite) / math.log(alphabet))
    while alphabet ** (n + 1) <= capacite:
        n += 1
    while alphabet ** n > capacite:
        n -= 1
    return n


# ── 10. VIII — Le règne du 1 % (01:14:30) ─────────────────────────────────

PART_CENTILE = Q(1, 100)
RICHESSE_CENTILE = Q(1, 5)
INDIVIDUS_RICHES, INDIVIDUS_POPULAIRES = 100, 9900


def population_a_deux_classes(part: Q = RICHESSE_CENTILE) -> List[int]:
    """10 000 individus entiers dont le centile supérieur détient exactement `part`."""
    y_pauvre = 4
    y_riche = round(y_pauvre * INDIVIDUS_POPULAIRES * part / ((1 - part) * INDIVIDUS_RICHES))
    total = INDIVIDUS_RICHES * y_riche + INDIVIDUS_POPULAIRES * y_pauvre
    if Q(INDIVIDUS_RICHES * y_riche, total) != part:
        raise AssertionError("population construite hors de la part déclarée")
    return [y_riche] * INDIVIDUS_RICHES + [y_pauvre] * INDIVIDUS_POPULAIRES


def gini_par_rangs(valeurs: Sequence[int]) -> Q:
    n = len(valeurs)
    triees = sorted(valeurs)
    total = sum(triees)
    ponderation = sum((i + 1) * x for i, x in enumerate(triees))
    return Q(2 * ponderation, n * total) - Q(n + 1, n)


def gini_lorenz(valeurs: Sequence[int]) -> Q:
    """Aire trapézoïdale sous la courbe de Lorenz : largeur 1/n, hauteur moyenne (Y_i + Y_i−1)/2."""
    n = len(valeurs)
    triees = sorted(valeurs)
    total = sum(triees)
    aire, cumul = Q(0), 0
    for x in triees:
        aire += Q(1, n) * Q(2 * cumul + x, 2 * total)
        cumul += x
    return 1 - 2 * aire


def gini_deux_classes(part_pop: Q = PART_CENTILE, part_riche: Q = RICHESSE_CENTILE) -> Q:
    y1 = part_riche / part_pop
    y2 = (1 - part_riche) / (1 - part_pop)
    return part_pop * (1 - part_pop) * abs(y1 - y2)


# ── 11. IX — La fin du travail est une somme de tâches (01:23:27) ──────────

PROPENSION_LEGERE = Q(8, 10)
PROPENSION_LOURDE = Q(2, 10)
SEUIL_LOURDEUR = 30
TACHES: Tuple[Tuple[int, Q], ...] = tuple(
    (lourdeur, PROPENSION_LEGERE if lourdeur <= SEUIL_LOURDEUR else PROPENSION_LOURDE)
    for lourdeur in range(1, 61)
)


def deplacement_par_taches(taches: Sequence[Tuple[int, Q]] = TACHES) -> Q:
    """Route 1 : la somme se fait tâche par tâche, dans l'ordre de lourdeur."""
    charge = sum(Q(l) * a for l, a in taches)
    masse = sum(l for l, _ in taches)
    return charge / Q(masse)


def deplacement_par_groupes(taches: Sequence[Tuple[int, Q]] = TACHES) -> Q:
    """Route 2 : regrouper les propensions identiques avant de multiplier."""
    groupes: Dict[Q, int] = {}
    for l, a in taches:
        groupes[a] = groupes.get(a, 0) + l
    masse = sum(groupes.values())
    return sum(Q(l) * a for a, l in groupes.items()) / Q(masse)


def deplacement_binaire(taches: Sequence[Tuple[int, Q]] = TACHES) -> Q:
    """Si l'on remplace la propension par un verdict (a ≥ 1/2 → 1, sinon 0), on compte."""
    masse = sum(l for l, _ in taches)
    automatique = sum(l for l, a in taches if a >= Q(1, 2))
    return Q(automatique, masse)


def moyenne_non_ponderee(taches: Sequence[Tuple[int, Q]] = TACHES) -> Q:
    """Ce que rend « x % des métiers » : la moyenne des propensions, sans la lourdeur."""
    return sum(a for _, a in taches) / len(taches)


# ── 12. X — Le compte local d'un data center (01:36:19) ────────────────────

PUISSANCE_MW = Q(120)
LITRES_PAR_KWH = Q(2, 1000)
HEURES_JOUR = Q(24)
EMPLOIS_LOCAUX = 400
FISCALITE_AN = Q(18_000_000)
PART_SALARIE_LOCALE = Q(60, 100)
NUISANCE_PAR_MW = Q(180_000)


def eau_jour_voie_kwh(puissance_mw: Q = PUISSANCE_MW, l_par_kwh: Q = LITRES_PAR_KWH,
                      heures: Q = HEURES_JOUR) -> Q:
    return puissance_mw * 1000 * heures * l_par_kwh


def eau_jour_voie_mwh(puissance_mw: Q = PUISSANCE_MW, l_par_kwh: Q = LITRES_PAR_KWH,
                      heures: Q = HEURES_JOUR) -> Q:
    return puissance_mw * heures * (l_par_kwh * 1000)


def solde_local(salaire: Q, emplois: int = EMPLOIS_LOCAUX, fiscalite: Q = FISCALITE_AN,
                part_locale: Q = PART_SALARIE_LOCALE, puissance_mw: Q = PUISSANCE_MW,
                nuisance_par_mw: Q = NUISANCE_PAR_MW) -> Q:
    """Masse salariale locale + fiscalité − nuisance : la ligne qu'un conseil municipal lit."""
    return emplois * salaire * part_locale + fiscalite - puissance_mw * nuisance_par_mw


def salaire_seuil(emplois: int = EMPLOIS_LOCAUX, fiscalite: Q = FISCALITE_AN,
                  part_locale: Q = PART_SALARIE_LOCALE, puissance_mw: Q = PUISSANCE_MW,
                  nuisance_par_mw: Q = NUISANCE_PAR_MW) -> Q:
    return (puissance_mw * nuisance_par_mw - fiscalite) / (emplois * part_locale)


def salaire_seuil_par_bissection() -> float:
    pente = float(EMPLOIS_LOCAUX * PART_SALARIE_LOCALE)
    constante = float(FISCALITE_AN - PUISSANCE_MW * NUISANCE_PAR_MW)
    return racine_bissection(lambda w: pente * w + constante, 0.0, 1_000_000.0)


# ── 13. XI — Breton, Musk et la contrainte de Triffin (01:39:25) ───────────

CROISSANCE_RESERVES = Q(4, 100)
PART_INITIALE = Q(20, 100)
PART_CIBLE = Q(25, 100)
HORIZON_RESERVE = 10


def part_recur(s0: Q, deficit_constant: Q, g: Q = CROISSANCE_RESERVES,
               n: int = HORIZON_RESERVE) -> Q:
    """s_{t+1} = (s_t + d)/(1 + g) : la part ne monte que si l'émetteur émet."""
    s = s0
    for _ in range(n):
        s = (s + deficit_constant) / (1 + g)
    return s


def deficit_requis(s0: Q = PART_INITIALE, cible: Q = PART_CIBLE,
                   g: Q = CROISSANCE_RESERVES, n: int = HORIZON_RESERVE) -> Q:
    num = cible * (1 + g) ** n - s0
    den = ((1 + g) ** n - 1) / g if g else Q(n)
    return num / den


def trajectoire_equilibre(s0: Q = PART_INITIALE, g: Q = CROISSANCE_RESERVES,
                          n: int = HORIZON_RESERVE) -> Q:
    """Émission strictement égale au besoin du monde : la part ne bouge pas."""
    s = s0
    for _ in range(n):
        s = (s + s * g) / (1 + g)
    return s


# ── 14. XII — Capacité de l'État : la dette (01:45:15) ─────────────────────

TAUX_REEL = Q(3, 100)
CROISSANCE_PIB = Q(15, 1000)
DETTE_INITIALE = Q(110, 100)
DETTE_CIBLE = Q(100, 100)
HORIZON_DETTE = 12


def facteur_portage(r: Q = TAUX_REEL, g: Q = CROISSANCE_PIB) -> Q:
    """x = (1 + r)/(1 + g) : ce que la dette devient en un an sans solde primaire."""
    return (1 + r) / (1 + g)


def dette_recur(d0: Q, solde: Q, n: int, x: Q) -> Q:
    d = d0
    for _ in range(n):
        d = x * d - solde
    return d


def solde_primaire_requis(d0: Q = DETTE_INITIALE, cible: Q = DETTE_CIBLE,
                          n: int = HORIZON_DETTE, x: Q = None) -> Q:
    x = facteur_portage() if x is None else x
    return (d0 * x ** n - cible) / sum(x ** k for k in range(n))


def solde_primaire_stationnaire(d: Q, r: Q = TAUX_REEL, g: Q = CROISSANCE_PIB) -> Q:
    """Le solde qui fige la dette sous la même récurrence : pb = d·(x − 1) = d·(r − g)/(1 + g)."""
    return d * (r - g) / (1 + g)


# ── 15. XIII — Le portefeuille sous budget commun ──────────────────────────

# (solution, coût en GWh, couverture en millièmes) — toutes déclarées.
SOLUTIONS_PORTFEUILLE: Tuple[Tuple[str, int, int], ...] = (
    ("S01 plan de succession contractualisé", 40, 120),
    ("S02 droit de retour du fondateur", 25, 70),
    ("S03 constitution de vote bornée", 60, 210),
    ("S04 budget de recherche à seuil d'indifférence", 320, 260),
    ("S05 vérification des formules générées", 90, 150),
    ("S06 régime de preuve et d'assurance contenu", 140, 130),
    ("S07 socle d'adressage de poids 313 T", 480, 240),
    ("S08 fiscalité du capital", 210, 190),
    ("S09 partage du temps de travail", 130, 160),
    ("S10 accord local à bénéfice garanti", 70, 110),
    ("S11 union des marchés de capitaux", 390, 200),
    ("S12 règle de solde primaire pluriannuelle", 150, 170),
)
BUDGET_GWH = 1000


def _bilan(indices: Sequence[int], solutions: Sequence[Tuple[str, int, int]]
           ) -> Tuple[int, int]:
    return (sum(solutions[i][2] for i in indices), sum(solutions[i][1] for i in indices))


def optimum_brut(solutions: Sequence[Tuple[str, int, int]] = SOLUTIONS_PORTFEUILLE,
                 budget: int = BUDGET_GWH) -> Tuple[int, Tuple[int, ...]]:
    """Route 1 : énumérer les 2^12 = 4 096 sous-ensembles."""
    meilleur, choisis = -1, tuple()
    n = len(solutions)
    for masque in range(1 << n):
        indices = tuple(i for i in range(n) if masque >> i & 1)
        couverture, cout = _bilan(indices, solutions)
        if cout <= budget and couverture > meilleur:
            meilleur, choisis = couverture, indices
    return meilleur, choisis


def optimum_dp(solutions: Sequence[Tuple[str, int, int]] = SOLUTIONS_PORTFEUILLE,
               budget: int = BUDGET_GWH) -> Tuple[int, Tuple[int, ...]]:
    """Route 2 : programmation dynamique sur la grille de budget, sans énumération."""
    valeur = [0] * (budget + 1)
    trace: List[List[int]] = [[] for _ in range(budget + 1)]
    for index, (_, cout, couverture) in enumerate(solutions):
        for b in range(budget, cout - 1, -1):
            candidate = valeur[b - cout] + couverture
            if candidate > valeur[b]:
                valeur[b] = candidate
                trace[b] = trace[b - cout] + [index]
    meilleur = max(valeur)
    choix = next(trace[b] for b in range(budget + 1) if valeur[b] == meilleur)
    return meilleur, tuple(sorted(choix))


# ── 16. Registre des équations ─────────────────────────────────────────────

def _eq(id_: str, fonction: str, titre: str, formule: str, derivation: str,
        statut: str, resultat: object, detail: Dict[str, object],
        liens: Sequence[str] = ()) -> Dict[str, object]:
    numero = id_.split("-")[1]
    return {"id": id_, "titre": titre, "registre": f"EQ-SA-{numero}",
            "chemin": f"{FICHIER} → {fonction}() → C{numero}",
            "formule": formule, "resultat": _n(resultat), "statut": statut,
            "derivation": derivation, "detail": detail, "liens": list(liens),
            "chapitre": CHAPITRES[ANCRAGE_CHAPITRE[id_]][2],
            "debut_s": CHAPITRES[ANCRAGE_CHAPITRE[id_]][1]}


def registre_equations() -> List[Dict[str, object]]:
    p_etoile = seuil_indifference()
    extensions_perm = extensions_par_permutations()
    vp, fp, manques = comptes_signalement()
    population = population_a_deux_classes()
    portage = facteur_portage()
    pb = solde_primaire_requis(x=portage)
    brut, pris_brut = optimum_brut()
    dp, pris_dp = optimum_dp()
    s_boucle = variables_max_boucle(socle.CAPACITE_POIDS, 2)

    return [
        _eq("EQ-01", "survie_dirigeant",
            "Départ du dirigeant : la survie d'un mandat est géométrique",
            "S(n) = (1 − p)^n ; E[T ; n] = Σ_{k=0}^{n−1} (1 − p)^k = (1 − (1 − p)^n)/p",
            "Si la probabilité de départ ne dépend pas de l'ancienneté, la loi de survie est "
            "géométrique et la durée moyenne du mandat est la somme des survies. Le contrôle "
            "confronte la boucle terme à terme à la forme fermée, en rationnels exacts.",
            "OPÉRATIONNEL",
            {"S_20": survie_dirigeant(), "E_mandat": esperance_mandat()},
            {"p": str(P_SORTIE), "horizon": HORIZON_MANDAT,
             "par_boucle": str(somme_survie_boucle()), "par_forme_fermee": str(esperance_mandat()),
             "plafond_theorique_1_sur_p": str(1 / P_SORTIE)},
            ["EQ-BSC-03", "EQ-02"]),
        _eq("EQ-02", "prob_retour_par_chemins",
            "Retour du fondateur : marche à trois états, deux compteurs",
            "P(revenu en n) = (M^n)[en place, revenu], M à lignes sommant 1",
            "On ne revient pas de nulle part : on revient d'un état « dehors ». La probabilité se "
            "calcule par puissance de matrice ET par énumération des 3^n chemins pondérés ; les "
            "deux voies rendent le même rationnel, ce qui prouve l'implémentation, pas le scénario.",
            "SIMULÉ",
            {"P_retour_5_ans": prob_retour_par_matrice()},
            {"horizon": HORIZON_RETOUR, "chemins": 3 ** HORIZON_RETOUR,
             "par_chemins": str(prob_retour_par_chemins()),
             "par_matrice": str(prob_retour_par_matrice()),
             "depuis_dehors": str(puissance_matrice(M_RETOUR, HORIZON_RETOUR)[1][2]),
             "sommes_lignes": [float(sum(ligne)) for ligne in M_RETOUR]},
            ["EQ-01"]),
        _eq("EQ-03", "swings_par_retrait",
            "Nationalisation ou empire familial : le pouvoir n'est pas la part du capital",
            "β_i = #{S ⊆ N∖{i} : v(S) = 0 et v(S ∪ {i}) = 1} / Σ_j β_j",
            "Ce qui compte dans un vote pondéré n'est pas le pourcentage détenu mais le nombre de "
            "coalitions où le retrait d'un membre fait perdre. Deux énumérations indépendantes "
            "(toutes les coalitions, puis les coalitions des autres) sont rejouées sur deux jeux : "
            "le poids 4 de [51 ; 48, 48, 4] vaut un tiers du pouvoir, le poids 2 de [60 ; 50, 49, 2] "
            "ne vaut rien.",
            "OPÉRATIONNEL",
            {"banzhaf": {nom: [str(x) for x in index_banzhaf(q, p)]
                         for nom, (q, p) in JEUX_VOTE.items()}},
            {"jeux": {nom: {"quota": q, "poids": list(p),
                            "swings_coalitions": swings_par_coalitions(q, p),
                            "swings_retrait": swings_par_retrait(q, p),
                            "index": [str(x) for x in index_banzhaf(q, p)]}
                      for nom, (q, p) in JEUX_VOTE.items()},
             "poids_des_joueurs": {nom: [round(w / sum(p) * 100, 2) for w in p]
                                   for nom, (_, p) in JEUX_VOTE.items()}},
            ["EQ-RB-13", "EQ-13"]),
        _eq("EQ-04", "seuil_indifference",
            "Soigner le cancer ou vendre l'IPO : une probabilité d'indifférence",
            "U(p) = p·A·(1 − (1 + r)^−n)/r − C ; p* = C / (A·annuité)",
            "L'arbitrage posé par le chapitre est une racine, pas une préférence. Le seuil sort de "
            "l'algèbre et se retrouve par bissection sur U ; l'annuité en forme fermée se retrouve "
            "par la somme des dix termes actualisés, et l'utilité calculée en p* retombe "
            "exactement à zéro. En dessous de p*, le financement de la "
            "recherche est un acte de foi, pas un calcul.",
            "SIMULÉ",
            {"p_etoile": p_etoile, "annuite": annuite_fermee()},
            {"cout": str(COUT_RD), "rente": str(RENTE_RD), "taux": str(TAUX_ACTUARIEL),
             "duree": DUREE_RD, "annuite_somme": str(somme_annuite()),
             "annuite_fermee": str(annuite_fermee()),
             "p_algebrique": float(p_etoile),
             "p_bissection": seuil_indifference_par_bissection(),
             "utilite_a_p_etoile": str(utilite_actuarielle(p_etoile))},
            ["EQ-BSC-03", "EQ-PS-06"]),
        _eq("EQ-05", "extensions_par_dp",
            "Le tableur est un graphe : le nombre d'ordres d'évaluation se compte",
            "e(P) = # extensions linéaires du poset des dépendances ; rayon(c) = 1 + |descendantes(c)|",
            "Une formule générée ne se vérifie pas à l'œil : elle se réévalue dans un ordre valide. "
            "Le nombre d'ordres valides d'une feuille de sept cellules est compté deux fois — force "
            "brute sur les 5 040 permutations, puis programmation dynamique sur les sous-ensembles "
            "— et le rayon de corruption est calculé par fermeture transitive.",
            "OPÉRATIONNEL",
            {"ordres_valides": extensions_perm, "rayon_maximal": max(rayon_correction().values())},
            {"cellules": len(FEUILLE), "arcs": sum(len(v) for v in FEUILLE.values()),
             "permutations_totales": math.factorial(len(FEUILLE)),
             "par_permutations": extensions_perm, "par_dp": extensions_par_dp(),
             "rayons": rayon_correction()},
            ["EQ-07", "EQ-PS-01"]),
        _eq("EQ-06", "vpn_par_denombrement",
            "Responsabilité : un détecteur à 95 % de spécificité accuse surtout des innocents",
            "PPV = k·se / (k·se + (N − k)·(1 − sp)) ; rappel = se",
            "« Naviguer quand la tech devient coupable » : le régime de preuve a une valeur "
            "prédictive et elle se calcule. Le nombre sort de Bayes et se retrouve en comptant les "
            "10^6 individus un par un. Sur une prévalence de 1,2 %, un détecteur à 0,90/0,95 "
            "signale environ quatre innocents pour un coupable.",
            "SIMULÉ",
            {"ppv": vpn_par_denombrement(), "faux_pour_un_vrai": Q(fp, vp)},
            {"population": POPULATION, "infractions": INFRACTIONS,
             "sensibilite": str(SENSIBILITE), "specificite": str(SPECIFICITE),
             "vrais_positifs": vp, "faux_positifs": fp, "manques": manques,
             "par_formule": str(vpn_par_formule()),
             "par_denombrement": str(vpn_par_denombrement()),
             "part_manquee": str(part_manquee())},
            ["EQ-BSC-02", "EQ-BSC-04"]),
        _eq("EQ-07", "variables_max_boucle",
            "Créer un univers entier : 48 variables binaires dans les 313 T du socle",
            "|Ω| = V^S ; S_max = ⌊log_V(C)⌋ avec C = 313 000 000 000 000",
            "« L'ère des démiurges » a un coût combinatoire mesurable. Douze variables binaires "
            "font 4 096 états, dénombrés un par un et non décrétés ; le socle d'adressage du dépôt "
            "nomme 2^48 configurations et pas une de plus si chaque variable est binaire. La "
            "barrière n'est pas la mémoire, c'est l'exposant.",
            "OPÉRATIONNEL",
            {"S_max": s_boucle, "etats_2_12": espace_etats(2, 12),
             "capacite_socle": socle.CAPACITE_POIDS},
            {"enumeration_2_12": enumeration_etats(2, 12), "formule_2_12": espace_etats(2, 12),
             "enumeration_3_8": enumeration_etats(3, 8), "formule_3_8": espace_etats(3, 8),
             "S_par_boucle": s_boucle, "S_par_log": variables_max_log(socle.CAPACITE_POIDS, 2),
             "capacite_socle": socle.CAPACITE_POIDS,
             "nommables_par_la_matrice": socle.adresses_nommables(),
             "dense_bf16_octets": socle.DENSE_BF16_OCTETS},
            ["EQ-PS-01", "EQ-PS-06"]),
        _eq("EQ-08", "gini_par_rangs",
            "Le règne du 1 % est un nombre : trois formules, un seul Gini",
            "G = (2·Σ i·x_i)/(n·Σ x_i) − (n+1)/n = 1 − 2·aire(Lorenz) = p(1−p)·|y₁ − y₂|",
            "« L'IA polarise tout » se tient ou tombe par identité. Sur une population de 10 000 "
            "individus entiers dont le centile détient exactement un cinquième de la richesse, le "
            "Gini est calculé par les rangs, par l'aire sous Lorenz et par la formule à deux "
            "classes. Les trois routes sont rationnelles et rendent 19/100.",
            "OPÉRATIONNEL",
            {"gini": gini_par_rangs(population)},
            {"n": len(population), "part_pop": str(PART_CENTILE), "part_riche": str(RICHESSE_CENTILE),
             "par_rangs": str(gini_par_rangs(population)),
             "par_lorenz": str(gini_lorenz(population)),
             "par_deux_classes": str(gini_deux_classes()),
             "richesse_individuelle": [population[0], population[-1]]},
            ["EQ-09"]),
        _eq("EQ-09", "deplacement_par_taches",
            "La fin du travail est une somme pondérée, pas une moyenne de métiers",
            "D = Σ_t L_t·a_t / Σ_t L_t ; le comptage binaire prend L_t si a_t ≥ 1/2, sinon 0",
            "« Mythe ou vraie menace » : la réponse dépend de la lourdeur des tâches, pas de leur "
            "nombre. La somme se calcule tâche par tâche, puis en regroupant les propensions "
            "identiques — les deux voies rendent le même rationnel. Le verdict binaire (« cette "
            "tâche est-elle automatisable ? ») et la moyenne non pondérée des mêmes propensions "
            "rendent deux autres nombres : c'est exactement l'écart qu'autorise la formulation "
            "« x % des métiers disparaissent ».",
            "SIMULÉ",
            {"deplacement": deplacement_par_taches(),
             "moyenne_non_ponderee": moyenne_non_ponderee()},
            {"taches": len(TACHES), "par_taches": str(deplacement_par_taches()),
             "par_groupes": str(deplacement_par_groupes()),
             "binaire": str(deplacement_binaire()),
             "non_pondere": str(moyenne_non_ponderee())},
            ["EQ-08"]),
        _eq("EQ-10", "salaire_seuil",
            "Le backlash est une soustraction : à quel salaire local le site devient acceptable",
            "B(w) = E·φ·w + F − P·ν ; w* = (P·ν − F)/(E·φ) ; eau = P·24·10³·ℓ",
            "« Peur ou haine économique » : le compte local est linéaire dans le salaire offert. Le "
            "seuil sort de l'algèbre et se retrouve par bissection sur B ; l'eau journalière sort "
            "de la voie kWh et de la voie MWh, qui doivent rendre le même litre par une autre "
            "décomposition des unités.",
            "SIMULÉ",
            {"salaire_seuil": salaire_seuil(), "eau_jour_litres": eau_jour_voie_kwh()},
            {"puissance_mw": str(PUISSANCE_MW), "emplois": EMPLOIS_LOCAUX,
             "fiscalite": str(FISCALITE_AN), "part_locale": str(PART_SALARIE_LOCALE),
             "nuisance_par_mw": str(NUISANCE_PAR_MW),
             "eau_voie_kwh": str(eau_jour_voie_kwh()), "eau_voie_mwh": str(eau_jour_voie_mwh()),
             "w_algebrique": float(salaire_seuil()), "w_bissection": salaire_seuil_par_bissection(),
             "solde_au_seuil": str(solde_local(salaire_seuil()))},
            ["EQ-ITh-01", "EQ-RB-12"]),
        _eq("EQ-11", "deficit_requis",
            "Triffin : une part de réserve ne monte que si l'émetteur émet",
            "s_{t+1} = (s_t + d)/(1 + g) ; d = (s_n(1 + g)^n − s_0)·g / ((1 + g)^n − 1)",
            "« L'Europe humiliée » a un test arithmétique. La récurrence menée dix ans avec le "
            "déficit que l'algèbre exige tombe exactement sur la part cible ; avec l'émission "
            "d'équilibre d_t = s_t·g, la part ne bouge pas d'une unité. C'est une contrainte, pas "
            "une opinion sur Musk ou Breton.",
            "SPÉCIFIÉ",
            {"deficit_requis": deficit_requis(),
             "part_apres_10_ans": part_recur(PART_INITIALE, deficit_requis())},
            {"part_initiale": str(PART_INITIALE), "part_cible": str(PART_CIBLE),
             "croissance": str(CROISSANCE_RESERVES), "horizon": HORIZON_RESERVE,
             "d_algebrique": str(deficit_requis()),
             "s_par_recurrence": str(part_recur(PART_INITIALE, deficit_requis())),
             "s_equilibre": str(trajectoire_equilibre())},
            ["EQ-12"]),
        _eq("EQ-12", "solde_primaire_requis",
            "État défaillant : le solde primaire qui ramène la dette, et celui qui la fige",
            "d_{t+1} = x·d_t − pb, x = (1 + r)/(1 + g) ; pb = (d₀xⁿ − d_n)/Σ_{k<n} x^k ; "
            "pb_stationnaire = d₀·(r − g)/(1 + g)",
            "« Émeutes et État défaillant » se lit dans la dynamique de la dette : le solde requis "
            "sort d'une somme géométrique et se vérifie en rejouant les douze années pas à pas. "
            "Autre identité, celle que les programmes n'écrivent jamais : à pb = d(r − g)/(1 + g), "
            "la dette est stationnaire exactement — le solde ne fait que payer le portage.",
            "OPÉRATIONNEL",
            {"solde_requis": pb, "dette_apres_12_ans": dette_recur(DETTE_INITIALE, pb, HORIZON_DETTE, portage)},
            {"r": str(TAUX_REEL), "g": str(CROISSANCE_PIB), "portage": str(portage),
             "d0": str(DETTE_INITIALE), "cible": str(DETTE_CIBLE), "horizon": HORIZON_DETTE,
             "pb_algebrique": str(pb),
             "pb_stationnaire": str(solde_primaire_stationnaire(DETTE_INITIALE)),
             "d_avec_pb_requis": str(dette_recur(DETTE_INITIALE, pb, HORIZON_DETTE, portage)),
             "d_stationnaire_10_ans": str(dette_recur(DETTE_INITIALE,
                                                      solde_primaire_stationnaire(DETTE_INITIALE),
                                                      10, portage))},
            ["EQ-11"]),
        _eq("EQ-13", "optimum_brut",
            "Portefeuille : douze solutions, un budget, un optimum calculé deux fois",
            "max Σ c_i·x_i sous Σ k_i·x_i ≤ B, x ∈ {0, 1}^12",
            "Toutes les solutions ci-dessus consomment la même ressource rare. L'optimum du "
            "portefeuille est calculé par énumération des 4 096 sous-ensembles puis par "
            "programmation dynamique sur la grille de budget : la valeur doit coïncider, et "
            "chacune des deux routes doit rendre un panier dont le coût tient dans le budget.",
            "SIMULÉ",
            {"couverture_optimale": brut,
             "cout_panier": _bilan(pris_brut, SOLUTIONS_PORTFEUILLE)[1]},
            {"solutions": len(SOLUTIONS_PORTFEUILLE), "budget_gwh": BUDGET_GWH,
             "sous_ensembles": 2 ** len(SOLUTIONS_PORTFEUILLE),
             "brut": {"couverture": brut, "cout": _bilan(pris_brut, SOLUTIONS_PORTFEUILLE)[1],
                      "choix": [SOLUTIONS_PORTFEUILLE[i][0] for i in pris_brut]},
             "dp": {"couverture": dp, "cout": _bilan(pris_dp, SOLUTIONS_PORTFEUILLE)[1],
                    "choix": [SOLUTIONS_PORTFEUILLE[i][0] for i in pris_dp]}},
            ["EQ-RB-13", "EQ-03"]),
    ]


# ── 17. Contrôles : un attendu dérivé par une autre route que l'obtenu ─────

def controles() -> List[Dict[str, object]]:
    cs: List[Dict[str, object]] = []

    def ctrl(id_: str, nom: str, attendu, obtenu) -> None:
        cs.append({"id": id_, "nom": nom, "attendu": _n(attendu), "obtenu": _n(obtenu),
                   "ok": attendu == obtenu})

    def bilan_de_route(choix: Sequence[int], couverture: int) -> List[object]:
        couverture_panier, cout_panier = _bilan(choix, SOLUTIONS_PORTFEUILLE)
        return [couverture, cout_panier <= BUDGET_GWH, couverture_panier == couverture]

    ctrl("C01", "somme terme à terme == forme fermée (rationnel exact)",
         somme_survie_boucle(), esperance_mandat())
    ctrl("C02", "3^5 chemins pondérés == (M^5)[0,2]",
         prob_retour_par_chemins(), prob_retour_par_matrice())
    ctrl("C03", "deux énumérations de coalitions concordent sur les deux jeux",
         [swings_par_coalitions(q, p) for q, p in JEUX_VOTE.values()],
         [swings_par_retrait(q, p) for q, p in JEUX_VOTE.values()])
    ctrl("C04", "p* algébrique == racine de U ; annuité boucle == fermée ; U(p*) == 0 exactement",
         [round(float(seuil_indifference()), 12), somme_annuite(), Q(0)],
         [round(seuil_indifference_par_bissection(), 12), annuite_fermee(),
          utilite_actuarielle(seuil_indifference())])
    ctrl("C05", "extensions linéaires : permutations == programmation dynamique",
         extensions_par_permutations(), extensions_par_dp())
    ctrl("C06", "valeur prédictive : formule de Bayes == dénombrement des 10^6",
         vpn_par_formule(), vpn_par_denombrement())
    ctrl("C07", "espaces d'états énumérés == puissances ; S_max boucle == log corrigé",
         [enumeration_etats(2, 12), enumeration_etats(3, 8),
          variables_max_boucle(socle.CAPACITE_POIDS, 2)],
         [espace_etats(2, 12), espace_etats(3, 8),
          variables_max_log(socle.CAPACITE_POIDS, 2)])
    ctrl("C08", "Gini : rangs et aire de Lorenz == formule à deux classes",
         [gini_par_rangs(population_a_deux_classes()), gini_lorenz(population_a_deux_classes())],
         [gini_deux_classes(), gini_deux_classes()])
    ctrl("C09", "déplacement : somme par tâche == regroupement par propension",
         deplacement_par_taches(), deplacement_par_groupes())
    ctrl("C10", "eau : voie kWh == voie MWh ; salaire seuil : algèbre == bissection",
         [eau_jour_voie_kwh(), round(float(salaire_seuil()), 6)],
         [eau_jour_voie_mwh(), round(salaire_seuil_par_bissection(), 6)])
    ctrl("C11", "récurrence 10 ans == cible ; émission d'équilibre == part inchangée",
         [part_recur(PART_INITIALE, deficit_requis()), trajectoire_equilibre()],
         [PART_CIBLE, PART_INITIALE])
    ctrl("C12", "pb de la somme géométrique rejoué : d₁₂ == cible ; pb stationnaire : d == d₀",
         [dette_recur(DETTE_INITIALE, solde_primaire_requis(), HORIZON_DETTE, facteur_portage()),
          dette_recur(DETTE_INITIALE, solde_primaire_stationnaire(DETTE_INITIALE), 10,
                      facteur_portage())],
         [DETTE_CIBLE, DETTE_INITIALE])
    ctrl("C13", "optimum : force brute == DP en valeur, panier sous budget et valeur atteinte",
         bilan_de_route(optimum_brut()[1], optimum_brut()[0]),
         bilan_de_route(optimum_dp()[1], optimum_dp()[0]))
    return cs


# ── 18. Limites ────────────────────────────────────────────────────────────

def limites() -> Dict[str, str]:
    return {
        "source": "Aucune transcription accessible : aucun propos n'est tiré de la vidéo. Les "
                  "treize chapitres ne fournissent que des thèmes horodatés ; les équations "
                  "formalisent les problèmes nommés, elles ne rapportent aucune phrase d'un acteur.",
        "parametres": "Toutes les grandeurs d'entrée sont déclarées dans PARAMETRES. Aucune n'est "
                      "une donnée d'entreprise, un cours, une statistique officielle ou une mesure. "
                      "Les remplacer change les nombres, jamais les identités contrôlées.",
        "EQ-01": "La probabilité de départ sans mémoire est une idéalisation : un mandat a une "
                 "mémoire (âge, santé, conseil). Le nombre borne un ordre de grandeur, il ne "
                 "prédit aucun départ.",
        "EQ-02": "La matrice à trois états est une hypothèse. L'accord des deux voies prouve "
                 "l'implémentation, pas les taux.",
        "EQ-03": "Les deux jeux sont fictifs : la structure du capital de Nvidia n'est pas rejouée. "
                 "Ce qui est démontré est le paradoxe du poids critique.",
        "EQ-04": "Coût, rente, taux et durée sont déclarés ; l'utilité attendue ne valorise pas une "
                 "vie soignée. p* est un test de cohérence, pas un conseil d'investissement.",
        "EQ-05": "La feuille de sept cellules est un jouet : la valeur est l'accord de deux "
                 "compteurs d'extensions linéaires, pas une promesse sur les tableurs réels.",
        "EQ-06": "Prévalence, sensibilité, spécificité sont déclarées. La population de 10^6 est "
                 "un modèle construit par index, pas un contentieux ni une base réelle.",
        "EQ-07": "Les nombres du socle sont relus sur reseau_poids_sparse_mizan.py, pas "
                 "réévalués ici. Un univers physique n'est pas une grille de variables binaires : "
                 "l'exposant est une borne d'architecture, pas une thèse.",
        "EQ-08": "La population est à deux classes par construction : le Gini obtenu ne mesure "
                 "aucun pays, aucune entreprise, aucune industrie.",
        "EQ-09": "La grille de 60 tâches est déclarée sans source statistique. Ce qui reste "
                 "portable est la méthode — pondérer par la lourdeur — pas le pourcentage.",
        "EQ-10": "Les coefficients locaux sont déclarés : aucun site réel n'est évalué, aucune "
                 "opposition n'est qualifiée de juste ou d'injuste.",
        "EQ-11": "Parts de réserve et croissance sont des ordres de grandeur externes non rejoués "
                 "(statut SPÉCIFIÉ). Seule la récurrence est démontrée, rien n'est prédit sur "
                 "l'euro.",
        "EQ-12": "r, g, dette initiale et cible sont déclarés ; le modèle est linéaire et sans "
                 "incertitude. Il ne prévoit aucune trajectoire française.",
        "EQ-13": "Coûts en GWh et couvertures en millièmes sont arbitraires et déclarés : "
                 "l'optimum prouve l'accord force brute / DP, pas la supériorité d'une solution.",
        "general": "Aucune preuve économique, juridique ou politique n'est produite. Le module "
                   "exécute des identités sur des hypothèses écrites et les nomme équation par "
                   "équation.",
    }


# ── 19. Assemblage ─────────────────────────────────────────────────────────

def resoudre() -> Dict[str, object]:
    equations = registre_equations()
    cs = controles()
    return {
        "version": "1.0",
        "horodatage_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "module": FICHIER,
        "domaine": "solutions_posees_par_les_acteurs_ia",
        "registre": "EQ-SA",
        "source": SOURCE,
        "chapitres": [{"debut": d, "debut_s": s, "titre": t} for d, s, t in CHAPITRES],
        "chapitres_ancres": chapitres_ancres(),
        "parametres_declares": list(PARAMETRES),
        "equations": equations,
        "controles": cs,
        "limites": limites(),
        "liens": {"socle_313T": "reseau_poids_sparse_mizan.py",
                  "capacite_poids": socle.CAPACITE_POIDS,
                  "plafond_materialise": socle.PLAFOND_MATERIALISES},
        "resume": {"equations": len(equations),
                   "controles_ok": sum(1 for c in cs if c["ok"]),
                   "controles_total": len(cs),
                   "statuts": {s: sum(1 for e in equations if e["statut"] == s) for s in STATUTS}},
    }


def verifier(donnees: Dict[str, object]) -> bool:
    return all(c["ok"] for c in donnees["controles"])


def ecrire_rapport(chemin: Path = None) -> Path:
    cible = Path(chemin) if chemin else (RACINE / "resultats" / "solutions_posees_acteurs.json")
    cible.parent.mkdir(parents=True, exist_ok=True)
    cible.write_text(json.dumps(resoudre(), ensure_ascii=False, indent=2), encoding="utf-8")
    return cible


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    rendu = resoudre()
    for c in rendu["controles"]:
        print(f"{'OK' if c['ok'] else 'KO'} {c['id']} attendu={c['attendu'][:56]:<56} "
              f"obtenu={c['obtenu'][:56]}")
    print(json.dumps({"resume": rendu["resume"]}, ensure_ascii=False, indent=2))
    if "--rapport" in sys.argv:
        print("rapport :", ecrire_rapport())
    raise SystemExit(0 if verifier(rendu) else 1)
