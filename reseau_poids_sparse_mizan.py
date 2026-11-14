# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""Socle de 313 000 000 000 000 poids adressables — réseau de poids sparse haché.

Auteur : M. Ahmed El Bahloul (IMAM8MAHDI).

Ce module ne matérielise pas 3,13×10^14 nombres : il rend cet espace adressable. Un poids
y est désigné par le quintuplet (entrée, strate, colonne, symbole, tranche), réduit modulo
``CAPACITE_POIDS`` par BLAKE2b-64. Seules les adresses effectivement écrites tiennent en
mémoire, sous un plafond compté ; le reste de l'espace est adressable et vide, ce que
EQ-PS-05 mesure au lieu de le cacher.

Le cardinal n'est pas tombé du ciel : 313 est la magnitude matière Terre scellée du projet
(``lib_physique.MAGNITUDE_ETAT_MATIERE_TERRE``, ``lib_informe.POLE_MATIERE_POSITIF``, et
``lib_bloc_synchron_mzn.CONSTANTE_C`` dans l'atelier de production), et 10^12 est l'échelle
fixée par la demande de l'auteur. Les trois attestations rendent le même entier (313,
vérifié) ; dans ce dépôt la valeur est lue sur ``lib_physique``, parce que le grand livre
MZN reste hors du corpus public : il porte l'état civil de l'auteur et deux adresses de
portefeuille nominatives, et le verrou C11 de ``VERROUS/`` compte dans tout le corpus une
clause rémunératoire qu'il n'admet qu'à zéro occurrence. Le détail est dans
``README_DEPOT.md``, section « Copies depuis la production ».
Le densement n'est pas possible ici : 3,13×10^14 poids en bf16 feraient 626 To pour 32,5 Go
libres (consigné au tableau maître, strate S38).

Trois chiffres, jamais confondus :
    CAPACITE_POIDS      313 000 000 000 000 emplacements adressables   — spécifié
    adresses_nommables  produit des axes mesurés du registre           — opérationnel
    materialises        écritures réellement tenues en mémoire         — mesuré
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import subprocess
import sys
import time
import tracemalloc
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple

RACINE = Path(__file__).resolve().parent
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

import tokenizer_mizan as tk                                        # noqa: E402
from module_tableau_maitre_mizan import REGISTRE_TABLEAU_MAITRE     # noqa: E402
from bibliotheques.lib_physique import MAGNITUDE_ETAT_MATIERE_TERRE as CONSTANTE_C  # noqa: E402

VERSION = "1.0"
AUTEUR = "M. Ahmed El Bahloul (IMAM8MAHDI)"

ECHELLE = 10 ** 12
CAPACITE_POIDS: int = CONSTANTE_C * ECHELLE          # 313 000 000 000 000
ESPACE_HACHAGE: int = 2 ** 64                        # 18 446 744 073 709 551 616
NB_SYMBOLES: int = tk.TAILLE_VOCAB                   # 259 : 3 spéciaux + 256 octets
FENETRE_POSITIONS: int = 64                          # largeur d'une tranche, en symboles
PLAFOND_MATERIALISES: int = 200_000                  # écritures gardées en mémoire, comptées
SEPARATEUR = b"\x1f"                                 # absent de tout champ ascii d'index

COLONNES_REGISTRE: Tuple[str, ...] = (
    "SEQ", "STRATE", "CODE", "FAMILLE_LOGIQUE", "ELEMENT", "ROLE_DESCRIPTION",
    "INTERACTION_MATIERE", "CYCLE_TERRE", "CYCLE_LUNE", "CYCLE_SOLEIL",
    "COUCHE_QUANTIQUE_BIO", "VALEUR_SCELLEE", "SOURCE",
)
NB_COLONNES: int = len(COLONNES_REGISTRE)            # 13

STATUTS = ("PASS", "FAIL", "INCONCLUSIF")
DENSE_BF16_OCTETS: int = 2 * CAPACITE_POIDS         # 626 000 000 000 000 o


class PlafondMaterialise(RuntimeError):
    """Écriture refusée au-delà de PLAFOND_MATERIALISES : le socle est borné, pas extensible."""


def _champ(valeur: object, nom: str, minimum: int = 0, maximum: Optional[int] = None) -> int:
    n = int(valeur)
    if n < minimum:
        raise ValueError(f"{nom} = {n}, attendu >= {minimum}")
    if maximum is not None and n >= maximum:
        raise ValueError(f"{nom} = {n}, attendu < {maximum}")
    return n


# ────────────────────────────────────────────────────────────────────────────
# 1. Arithmétique du cardinal — recalculée, jamais recopiée
# ────────────────────────────────────────────────────────────────────────────

def est_premier(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def factorisation(n: int) -> List[Tuple[int, int]]:
    facteurs: List[Tuple[int, int]] = []
    d, reste = 2, n
    while d * d <= reste:
        if reste % d == 0:
            e = 0
            while reste % d == 0:
                reste //= d
                e += 1
            facteurs.append((d, e))
        d += 1 if d == 2 else 2
    if reste > 1:
        facteurs.append((reste, 1))
    return facteurs


def produit_facteurs(facteurs: Sequence[Tuple[int, int]]) -> int:
    r = 1
    for p, e in facteurs:
        r *= p ** e
    return r


def quantile_normale(p: float) -> float:
    """z tel que P(Z <= z) = p, par bissection sur la CDF normale centrée réduite."""
    if not 0.0 < p < 1.0:
        raise ValueError("p doit être dans ]0, 1[")
    lo, hi = -12.0, 12.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if 0.5 * (1.0 + math.erf(mid / math.sqrt(2.0))) < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def seuil_chi2(ddl: int, p: float = 0.99) -> float:
    """Quantile du χ² par Wilson-Hilferty — la formule est dans le code, pas dans un tableau."""
    z = quantile_normale(p)
    return ddl * (1.0 - 2.0 / (9.0 * ddl) + z * math.sqrt(2.0 / (9.0 * ddl))) ** 3


def borne_anniversaire(n: int, module: int) -> float:
    """Espérance du nombre de collisions pour n tirages dans un espace de taille `module`."""
    if n < 2:
        return 0.0
    return n * (n - 1) / (2.0 * module)


# ────────────────────────────────────────────────────────────────────────────
# 2. Adressage
# ────────────────────────────────────────────────────────────────────────────

def cle(entree: int, strate: int, colonne: int, symbole: int, tranche: int) -> bytes:
    """Quintuplet -> octets canoniques, séparateur invisible : aucune clé ambiguë."""
    champs = (
        _champ(entree, "entree", minimum=1),
        _champ(strate, "strate"),
        _champ(colonne, "colonne", maximum=NB_COLONNES),
        _champ(symbole, "symbole", maximum=NB_SYMBOLES),
        _champ(tranche, "tranche"),
    )
    return SEPARATEUR.join(str(x).encode("ascii") for x in champs)


def adresser(cle_brute: bytes, module: int = CAPACITE_POIDS) -> int:
    """BLAKE2b-64 puis réduction modulo `module` : déterministe, sans graine à garder."""
    return int.from_bytes(hashlib.blake2b(cle_brute, digest_size=8).digest(), "big") % module


def slot_de(entree: int, strate: int, colonne: int, symbole: int, tranche: int,
            module: int = CAPACITE_POIDS) -> int:
    return adresser(cle(entree, strate, colonne, symbole, tranche), module)


def decompiler(i: int, axes: Dict[str, int]) -> Tuple[int, int, int, int, int]:
    """Entier -> quintuplet par bases mixtes : deux i distincts donnent deux clés distinctes."""
    return (
        1 + i % axes["entrees"],
        (i // axes["entrees"]) % axes["strates"],
        (i // (axes["entrees"] * axes["strates"])) % axes["colonnes"],
        (i // (axes["entrees"] * axes["strates"] * axes["colonnes"])) % axes["symboles"],
        i // (axes["entrees"] * axes["strates"] * axes["colonnes"] * axes["symboles"]),
    )


# ────────────────────────────────────────────────────────────────────────────
# 3. Le réseau sparse : ce qui est écrit, et rien d'autre
# ────────────────────────────────────────────────────────────────────────────

class ReseauPoidsSparse:
    """Table slot -> poids, plafonnée, à empreinte déterministe."""

    def __init__(self, capacite: int = CAPACITE_POIDS, plafond: int = PLAFOND_MATERIALISES):
        self.capacite = capacite
        self.plafond = plafond
        self.poids: Dict[int, float] = {}
        self.ecritures_refusees = 0

    def ecrire(self, slot: int, valeur: float) -> bool:
        if slot in self.poids:
            self.poids[slot] = valeur
            return False
        if len(self.poids) >= self.plafond:
            self.ecritures_refusees += 1
            raise PlafondMaterialise(
                f"PLAFOND_MATERIALISES atteint ({self.plafond}) : écriture refusée au slot {slot}")
        self.poids[slot] = valeur
        return True

    def lire(self, slot: int) -> Optional[float]:
        return self.poids.get(slot)

    @property
    def materialises(self) -> int:
        return len(self.poids)

    @property
    def occupation(self) -> float:
        return self.materialises / self.capacite

    def empreinte(self) -> str:
        corps = "\n".join(f"{s}|{self.poids[s]:.12f}" for s in sorted(self.poids))
        return hashlib.sha256(corps.encode("utf-8")).hexdigest()


def valeur_poids(ids: Sequence[int], symbole: int, tranche: int) -> float:
    """Poids = fréquence du symbole dans la fenêtre `tranche`, bornée dans [0, 1]."""
    debut = tranche * FENETRE_POSITIONS
    fenetre = ids[debut:debut + FENETRE_POSITIONS]
    if not fenetre:
        return 0.0
    return fenetre.count(symbole) / float(len(fenetre))


def indice_strate(nom: str) -> int:
    lst = _liste_strates()
    return lst.index(nom) if nom in lst else 0


_STRATES: Optional[List[str]] = None


def _liste_strates() -> List[str]:
    global _STRATES
    if _STRATES is None:
        _STRATES = sorted({l.get("STRATE", "") for l in REGISTRE_TABLEAU_MAITRE.lignes
                          if l.get("STRATE")})
    return _STRATES


def texte_cellule(ligne: Dict[str, str], champ: str) -> str:
    for cle_ligne, valeur in ligne.items():
        if cle_ligne and cle_ligne.strip() == champ:
            return valeur or ""
    return ""


def materialiser_registre(reseau: Optional[ReseauPoidsSparse] = None
                          ) -> Tuple[ReseauPoidsSparse, Dict[str, object]]:
    """Écrit chaque (entrée, strate, colonne, symbole, tranche) rencontré dans le registre."""
    reseau = reseau or ReseauPoidsSparse()
    rencontre = ecritures = 0
    arrete = False
    t0 = time.perf_counter()
    for ligne in REGISTRE_TABLEAU_MAITRE.lignes:
        try:
            entree = int(str(ligne.get("SEQ", "")).strip())
        except ValueError:
            continue
        if entree < 1:
            continue
        strate = indice_strate(ligne.get("STRATE", ""))
        for colonne, nom in enumerate(COLONNES_REGISTRE):
            ids = tk.encoder(texte_cellule(ligne, nom), avec_bords=False)
            if not ids:
                continue
            for tranche in range(1 + (len(ids) - 1) // FENETRE_POSITIONS):
                symboles = set(ids[tranche * FENETRE_POSITIONS:(tranche + 1) * FENETRE_POSITIONS])
                for symbole in symboles:
                    v = valeur_poids(ids, symbole, tranche)
                    if v <= 0.0:
                        continue
                    rencontre += 1
                    try:
                        if reseau.ecrire(slot_de(entree, strate, colonne, symbole, tranche), v):
                            ecritures += 1
                    except PlafondMaterialise:
                        arrete = True
                        break
                if arrete:
                    break
            if arrete:
                break
        if arrete:
            break
    return reseau, {"rencontres": rencontre, "ecritures": ecritures,
                    "arrete_au_plafond": arrete,
                    "duree_seconde": round(time.perf_counter() - t0, 4),
                    "materialises": reseau.materialises, "empreinte": reseau.empreinte()}


def axes_registre() -> Dict[str, int]:
    """Les cinq axes du quintuplet, mesurés sur le registre chargé."""
    total_positions = 0
    for ligne in REGISTRE_TABLEAU_MAITRE.lignes:
        for nom in COLONNES_REGISTRE:
            total_positions += len(tk.encoder(texte_cellule(ligne, nom), avec_bords=False))
    return {
        "entrees": REGISTRE_TABLEAU_MAITRE.total_entrees(),
        "strates": len(_liste_strates()),
        "colonnes": NB_COLONNES,
        "symboles": NB_SYMBOLES,
        "tranches": max(1, math.ceil(total_positions / FENETRE_POSITIONS)),
        "positions_total": total_positions,
    }


def adresses_nommables(axes: Optional[Dict[str, int]] = None) -> int:
    a = axes or axes_registre()
    return a["entrees"] * a["strates"] * a["colonnes"] * a["symboles"] * a["tranches"]


def plan_de_crissance(axes: Optional[Dict[str, int]] = None) -> Dict[str, object]:
    """Ce qui manque pour que la matrice puisse nommer tout l'espace des 313T poids."""
    a = axes or axes_registre()
    nommables = adresses_nommables(a)
    par_entree = a["strates"] * a["colonnes"] * a["symboles"] * a["tranches"]
    par_tranche = a["entrees"] * a["strates"] * a["colonnes"] * a["symboles"]
    return {
        "adresses_nommables": nommables,
        "ratio_espace_nomme": nommables / CAPACITE_POIDS,
        "facteur_manquant": CAPACITE_POIDS / nommables if nommables else None,
        "entrees_pour_egaliser": math.ceil(CAPACITE_POIDS / par_entree) if par_entree else None,
        "tranches_pour_egaliser": math.ceil(CAPACITE_POIDS / par_tranche) if par_tranche else None,
        "entrees_actuelles": a["entrees"],
        "entrees_a_ecrire": (max(0, math.ceil(CAPACITE_POIDS / par_entree) - a["entrees"])
                             if par_entree else None),
    }


# ────────────────────────────────────────────────────────────────────────────
# 4. Usage : comparer deux questions se fait dans cet espace
# ────────────────────────────────────────────────────────────────────────────

def nettoyer(texte: str) -> str:
    return " ".join(str(texte or "").casefold().split())


def indices_question(question: str, strate: int = 0, colonne: int = 0) -> Dict[int, float]:
    ids = tk.encoder(nettoyer(question), avec_bords=False)
    sparse: Dict[int, float] = {}
    for tranche in range(1 + (len(ids) - 1) // FENETRE_POSITIONS) if ids else range(0):
        for symbole in set(ids[tranche * FENETRE_POSITIONS:(tranche + 1) * FENETRE_POSITIONS]):
            v = valeur_poids(ids, symbole, tranche)
            if v > 0.0:
                sparse[adresser(cle(1, strate, colonne, symbole, tranche))] = v
    return sparse


def recouvrement(q1: str, q2: str) -> Dict[str, object]:
    a, b = indices_question(q1), indices_question(q2)
    if not a or not b:
        return {"similarite": 0.0, "slots_communs": 0, "slots_a": len(a), "slots_b": len(b)}
    communs = set(a) & set(b)
    scalaire = sum(a[s] * b[s] for s in communs)
    norme = math.sqrt(sum(v * v for v in a.values())) * math.sqrt(sum(v * v for v in b.values()))
    return {"similarite": scalaire / norme if norme else 0.0, "slots_communs": len(communs),
            "slots_a": len(a), "slots_b": len(b)}


# ────────────────────────────────────────────────────────────────────────────
# 5. Observation une fois, neuf contrôles
# ────────────────────────────────────────────────────────────────────────────

Observation = Dict[str, object]

DOSSIERS_IGNORES = {".qoder", "__pycache__", ".git", "_AL_MIZAN_COPIE_SOI", "node_modules",
                    ".venv", "venv", "dist", "build"}
EXTENSIONS_POIDS = {".pt", ".safetensors", ".bin", ".gguf", ".ckpt", ".onnx", ".npy", ".npz"}


def inventaire_poids_sur_disque() -> List[str]:
    """Extensions de poids sous le dépôt, hors copies de travail. Ce module n'en lit aucune."""
    trouves: List[str] = []
    for racine, dossiers, fichiers in os.walk(RACINE):
        dossiers[:] = [d for d in dossiers if d.lower() not in DOSSIERS_IGNORES]
        for nom in fichiers:
            if Path(nom).suffix.lower() in EXTENSIONS_POIDS:
                chemin = Path(racine) / nom
                trouves.append(str(chemin.relative_to(RACINE)).replace("\\", "/"))
    return sorted(trouves)


def question_disjointe(reference: str, longueur: int = 12) -> str:
    """Caractères dont aucun octet UTF-8 n'apparaît dans `reference` : recouvrement nul garanti."""
    ids = set(tk.encoder(nettoyer(reference), avec_bords=False))
    candidats = [chr(o) for o in range(0x21, 0x7F)
                 if o + tk.DECALAGE_OCTET not in ids and o != 0x7C]
    return "".join(candidats[:longueur])


def observer(echantillons: int = 200_000, croiser_processus: bool = True) -> Observation:
    t0 = time.perf_counter()
    axes = axes_registre()
    nommables = adresses_nommables(axes)
    cle_test = cle(1, 0, 0, 7, 3)
    slots = [adresser(cle_test) for _ in range(4)]

    cles = [cle(*decompiler(i, axes)) for i in range(echantillons)]
    adresses = [adresser(c) for c in cles]
    buckets = [0] * 256
    for s in adresses:
        buckets[s * 256 // CAPACITE_POIDS] += 1
    attendu = echantillons / 256.0
    chi2 = sum((b - attendu) ** 2 / attendu for b in buckets)
    t_hache = time.perf_counter()

    collisions_reelles = len(adresses) - len(set(adresses))
    sous_espace = 10 ** 6
    adresses_petites = [adresser(c, sous_espace) for c in cles]
    collisions_sous = len(adresses_petites) - len(set(adresses_petites))

    tiers = None
    if croiser_processus:
        try:
            rendu = subprocess.run(
                [sys.executable, "-B", str(RACINE / "reseau_poids_sparse_mizan.py"),
                 "--slot", "1|0|0|7|3"], capture_output=True, timeout=90,
                stdin=subprocess.DEVNULL)
            tiers = (json.loads(rendu.stdout.decode("utf-8").strip())
                     if rendu.returncode == 0 else
                     {"erreur": f"rc {rendu.returncode}: {rendu.stderr.decode('utf-8')[:120]}"})
        except Exception as exc:
            tiers = {"erreur": f"{type(exc).__name__}: {exc}"}

    n_mem = min(50_000, echantillons)
    r_mem = ReseauPoidsSparse(plafond=n_mem + 10)
    tracemalloc.start()
    for i in range(n_mem):
        r_mem.ecrire(adresses[i], 0.5)
    pic = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()

    reseau, etat_materialisation = materialiser_registre()

    q_a = "combien de paramètres dans le réseau de zéro"
    q_b = "la lune a-t-elle une magnitude scellée"
    q_vide = question_disjointe(q_a)

    return {
        "capacite": CAPACITE_POIDS, "espace_hachage": ESPACE_HACHAGE,
        "axes": axes, "adresses_nommables": nommables,
        "chantillon": echantillons, "cles": cles, "adresses": adresses,
        "buckets": buckets, "chi2": chi2,
        "collisions_reelles": collisions_reelles,
        "collisions_sous_espace": collisions_sous, "sous_espace": sous_espace,
        "collisions_attendues": borne_anniversaire(echantillons, CAPACITE_POIDS),
        "collisions_attendues_sous": borne_anniversaire(echantillons, sous_espace),
        "slots_stables": slots, "empreinte_tiers": tiers,
        "memoire": {"slots_mesures": n_mem, "octets_par_slot": pic / n_mem,
                    "pic_octets": pic, "dense_bf16_octets": DENSE_BF16_OCTETS},
        "reseau": reseau, "materialisation": etat_materialisation,
        "recouvrement": recouvrement(q_a, q_b),
        "recouvrement_bis": recouvrement(q_a, q_a),
        "question_hors_corpus": recouvrement(q_vide, q_a),
        "debit_hachage": echantillons / max(1e-9, t_hache - t0),
        "poids_sur_disque": inventaire_poids_sur_disque(),
        "cle_test": "|".join(str(x) for x in (1, 0, 0, 7, 3)),
        "duree_observation": round(time.perf_counter() - t0, 4),
    }


def eq_ps_01(obs: Observation) -> Tuple[str, object, str]:
    f = factorisation(CAPACITE_POIDS)
    bon = (produit_facteurs(f) == CAPACITE_POIDS and est_premier(CONSTANTE_C)
           and CONSTANTE_C in [p for p, _ in f] and CAPACITE_POIDS == CONSTANTE_C * ECHELLE
           and ECHELLE == 10 ** 12 and CAPACITE_POIDS < ESPACE_HACHAGE
           and int(obs["capacite"]) == CAPACITE_POIDS)
    return ("PASS" if bon else "FAIL"), \
        {"capacite": CAPACITE_POIDS, "facteurs": f, "constante_c": CONSTANTE_C,
         "echelle": ECHELLE, "c_est_premier": est_premier(CONSTANTE_C),
         "ratio_espace_hachage": ESPACE_HACHAGE / CAPACITE_POIDS}, \
        "factorisation() + est_premier() + produit_facteurs() recalculés sur CAPACITE_POIDS"


def eq_ps_02(obs: Observation) -> Tuple[str, object, str]:
    n = int(obs["chantillon"])
    attendues = borne_anniversaire(n, CAPACITE_POIDS)
    constatees = int(obs["collisions_reelles"])
    cles_distinctes = len(set(obs["cles"])) == n
    borne_haute = max(4.0, attendues * 8.0)
    return ("PASS" if (constatees <= borne_haute and cles_distinctes) else "FAIL"), \
        {"echantillon": n, "cles_distinctes_verifiees": cles_distinctes,
         "collisions_constatees": constatees, "collisions_attendues": attendues,
         "borne_haute": borne_haute}, "borne_anniversaire(n, C) comparée au comptage, clés distinctes"


def eq_ps_03(obs: Observation) -> Tuple[str, object, str]:
    ddl = len(obs["buckets"]) - 1
    chi2 = float(obs["chi2"])
    seuil = seuil_chi2(ddl)
    ecart_max = max(abs(b - int(obs["chantillon"]) / 256.0) for b in obs["buckets"])
    return ("PASS" if chi2 < seuil else "FAIL"), \
        {"chi2_observed": round(chi2, 3), "seuil_99": round(seuil, 3), "ddl": ddl,
         "ecart_max_paquet": round(ecart_max, 2), "echantillon": int(obs["chantillon"])}, \
        "256 paquets + χ² recalculé, seuil Wilson-Hilferty produit par le module"


def eq_ps_04(obs: Observation) -> Tuple[str, object, str]:
    slots = [int(s) for s in obs["slots_stables"]]
    tiers = obs["empreinte_tiers"]
    dans_processus = len(set(slots)) == 1
    Second = isinstance(tiers, dict) and "slot" in tiers
    stable = dans_processus and Second and int(tiers["slot"]) == slots[0] \
        and int(tiers["capacite"]) == CAPACITE_POIDS
    return ("PASS" if stable else "FAIL"), \
        {"slot": slots[0], "rejoue_quatre_fois_local": dans_processus,
         "seconde_instance": tiers}, \
        "subprocess py -3 -B reseau_poids_sparse_mizan.py --slot, comparé au slot local"


def eq_ps_05(obs: Observation) -> Tuple[str, object, str]:
    reseau: ReseauPoidsSparse = obs["reseau"]
    m = obs["memoire"]
    materialises = reseau.materialises
    teneur = float(m["octets_par_slot"]) * materialises
    ok = (materialises > 0 and 0 < materialises <= PLAFOND_MATERIALISES
          and teneur < 256 * 1024 * 1024 and DENSE_BF16_OCTETS == 2 * CAPACITE_POIDS)
    return ("PASS" if ok else "FAIL"), \
        {"materialises": materialises, "capacite": CAPACITE_POIDS,
         "occupation": materialises / CAPACITE_POIDS, "octets_par_slot": m["octets_par_slot"],
         "teneur_octets": teneur, "dense_bf16_octets": DENSE_BF16_OCTETS,
         "arrete_au_plafond": obs["materialisation"]["arrete_au_plafond"],
         "rencontres": obs["materialisation"]["rencontres"]}, \
        "tracemalloc sur 50 000 écritures + comptage du réseau réellement matérialisé"


def eq_ps_06(obs: Observation) -> Tuple[str, object, str]:
    axes = obs["axes"]
    nommables = int(obs["adresses_nommables"])
    produit = (axes["entrees"] * axes["strates"] * axes["colonnes"]
               * axes["symboles"] * axes["tranches"])
    plan = plan_de_crissance(axes)
    facteur = plan["facteur_manquant"]
    ok = (produit == nommables and axes["colonnes"] == NB_COLONNES
          and axes["symboles"] == NB_SYMBOLES and axes["entrees"] > 0
          and axes["tranches"] > 0 and nommables < CAPACITE_POIDS)
    return ("PASS" if ok else "FAIL"), \
        {"axes": axes, "adresses_nommables": nommables,
         "ratio_espace_nomme": plan["ratio_espace_nomme"],
         "facteur_manquant": round(facteur, 4) if facteur is not None else "INFINI",
         "entrees_pour_egaliser": plan["entrees_pour_egaliser"],
         "tranches_pour_egaliser": plan["tranches_pour_egaliser"]}, \
        "axes_registre() lu sur le CSV, produit recalculé, plan_de_crissance() dérivé"


def eq_ps_07(obs: Observation) -> Tuple[str, object, str]:
    r = ReseauPoidsSparse(plafond=10)
    refuses = 0
    for i in range(64):
        try:
            r.ecrire(adresser(cle(1, 0, 0, i % NB_SYMBOLES, i)), 1.0)
        except PlafondMaterialise:
            refuses += 1
    ok = (r.materialises == 10 and refuses == 54 and r.ecritures_refusees == 54
          and not obs.get("poids_lus_par_ce_module", True) is True)
    return ("PASS" if ok else "FAIL"), \
        {"plafond": r.plafond, "materialises_apres_64_tentatives": r.materialises,
         "ecritures_refusees": r.ecritures_refusees,
         "poids_sur_disque_inventories": len(obs["poids_sur_disque"]),
         "poids_lus_par_ce_module": obs.get("poids_lus_par_ce_module")}, \
        "64 écritures dans un réseau à plafond 10 + drapeau de lecture de poids externe"


def eq_ps_08(obs: Observation) -> Tuple[str, object, str]:
    rec, rec_bis, hors = obs["recouvrement"], obs["recouvrement_bis"], obs["question_hors_corpus"]
    t = float(rec["similarite"])
    t_bis = float(rec_bis["similarite"])
    ok = (abs(t_bis - 1.0) < 1e-9 and 0.0 <= t <= 1.0 and int(rec["slots_a"]) > 0
          and int(hors["slots_communs"]) == 0 and int(hors["slots_a"]) > 0
          and int(hors["slots_b"]) > 0)
    return ("PASS" if ok else "FAIL"), \
        {"similarite_question_sur_meme_question": t_bis,
         "similarite_deux_questions": round(t, 6), "slots_communs": rec["slots_communs"],
         "slots_a": rec["slots_a"], "slots_b": rec["slots_b"],
         "recouvrement_hors_corpus": hors["slots_communs"]}, \
        "recouvrement() rejoué sur (q,q) et sur une question sans symbole commun"


def eq_ps_09(obs: Observation) -> Tuple[str, object, str]:
    debit = float(obs["debit_hachage"])
    sous = int(obs["collisions_sous_espace"])
    attendues = float(obs["collisions_attendues_sous"])
    ok = debit > 50_000 and sous > 0 and abs(sous - attendues) < max(50.0, attendues * 0.35)
    return ("PASS" if ok else "FAIL"), \
        {"hachages_par_seconde": round(debit, 1), "sous_espace": obs["sous_espace"],
         "collisions_constatees_sous_espace": sous,
         "collisions_attendues_sous_espace": round(attendues, 1)}, \
        "débit mesuré + comptage dans un sous-espace à 10^6 où les collisions sont attendues"


EQUATIONS: Tuple[Tuple[str, str, str, Callable[[Observation], Tuple[str, object, str]]], ...] = (
    ("EQ-PS-01", "Cardinal exact de l'espace", "313 x 10^12 = 313 000 000 000 000 < 2^64", eq_ps_01),
    ("EQ-PS-02", "Bornage des collisions", "collisions <= max(4 ; 8 n(n-1)/2C)", eq_ps_02),
    ("EQ-PS-03", "Uniformité de l'adressage", "chi2(255 ddl) < seuil 99 % calcule", eq_ps_03),
    ("EQ-PS-04", "Stabilite entre processus", "slot(sous-processus) == slot(local)", eq_ps_04),
    ("EQ-PS-05", "Materialisation plafonnee", "0 < materialises <= 200000 et teneur < 256 Mo", eq_ps_05),
    ("EQ-PS-06", "Ce que la matrice nomme", "produit des axes measures < capacite", eq_ps_06),
    ("EQ-PS-07", "Plafond ferme, aucun poids lu", "10 gardes et 54 refuses sur 64 tentatives", eq_ps_07),
    ("EQ-PS-08", "Le socle sert a comparer", "recouvrement(q,q) = 1 et hors-corpus = 0", eq_ps_08),
    ("EQ-PS-09", "Non-vacuite du compteur", "debit > 5e4/s et collisions > 0 dans 10^6", eq_ps_09),
)

CONTROLES = {identifiant: controle for identifiant, _t, _f, controle in EQUATIONS}


def limites() -> Dict[str, str]:
    return {
        "EQ-PS-01": "Le cardinal est une déclaration d'architecte : 313 est scellé dans le projet, "
                    "10^12 est l'échelle demandée par l'auteur. Rien dans cette équation ne dit que "
                    "ces emplacements contiennent de l'information.",
        "EQ-PS-02": "Le comptage porte sur 2×10^5 clés dans un espace de 3,13×10^14 : l'espérance de "
                    "collision y est de l'ordre de 10^-4, donc ce contrôle prouve l'absence de bug "
                    "d'adressage, pas la qualité statistique du hachage à pleine charge. EQ-PS-09 "
                    "fait le travail lourd dans un sous-espace.",
        "EQ-PS-03": "Le seuil χ² est produit par l'approximation de Wilson-Hilferty implémentée ici, "
                    "non par un tableau statistique : elle est exacte à quelques unités près pour 255 "
                    "degrés de liberté. Le contrôle porte sur un échantillon, pas sur l'espace entier.",
        "EQ-PS-04": "La seconde instance tourne sur la même machine, avec le même fichier et la même "
                    "bibliothèque de hachage : elle prouve l'absence d'état caché (graine, dictionnaire, "
                    "pid), pas la stabilité après un changement de version de CPython.",
        "EQ-PS-05": "La teneur est mesurée sur un dictionnaire Python de floats : le socle ne "
                    "matérialise pas un espace clairsemé de 3,13×10^14 entrées. Le contrôle dit où est "
                    "le plafond et ce qui tient dessous.",
        "EQ-PS-06": "Le produit des axes est un majorant d'adresses nommables, pas un décompte "
                    "d'adresses distinctes : deux quintuplets différents peuvent hacher sur le même "
                    "slot, et toutes les combinaisons n'ont pas de sens métier.",
        "EQ-PS-07": "L'inventaire des fichiers de poids ne balaie que les extensions connues sous ce "
                    "dépôt, hors copies de travail : un poids importé ailleurs ne serait pas vu. Ce "
                    "contrôle affirme que ce module n'en lit aucun, pas qu'aucun n'existe.",
        "EQ-PS-08": "Le recouvrement est un cosinus sur fréquences fenêtrées : c'est une mesure "
                    "lexicale. Une question juste mais hors registre peut recouvrir fort, et le socle "
                    "ne tranche pas la véracité — c'est le rôle du moteur déterministe.",
        "EQ-PS-09": "Le sous-espace 10^6 est un banc d'essai du compteur de collisions, pas une "
                    "version réduite du socle : ses chiffres n'ont pas vocation à être publiés comme "
                    "une propriété de l'espace de 313T.",
    }


def evaluer(obs: Observation) -> Dict[str, object]:
    rendu: List[Dict[str, object]] = []
    for identifiant, titre, forme, controle in EQUATIONS:
        statut, valeur, chemin = controle(obs)
        rendu.append({"id": identifiant, "titre": titre, "forme": forme, "statut": statut,
                      "valeur": valeur, "chemin_controle": chemin, "limite": limites()[identifiant]})
    compte = {s: sum(1 for c in rendu if c["statut"] == s) for s in STATUTS}
    return {"equations": rendu, "compte": compte,
            "racine": hashlib.sha256(
                "\n".join(f"{c['id']}|{c['statut']}" for c in rendu).encode("utf-8")).hexdigest(),
            "duree_observation_seconde": obs["duree_observation"]}


def controler(echantillons: int = 200_000, croiser_processus: bool = True) -> Dict[str, object]:
    obs = observer(echantillons=echantillons, croiser_processus=croiser_processus)
    obs["poids_lus_par_ce_module"] = False
    rapport = evaluer(obs)
    cadre = {"module": "reseau_poids_sparse_mizan.py", "version": VERSION, "auteur": AUTEUR,
             "capacite_poids": CAPACITE_POIDS, "constante_c": CONSTANTE_C, "echelle": ECHELLE,
             "espace_hachage": ESPACE_HACHAGE, "dense_bf16_octets": DENSE_BF16_OCTETS,
             "colonnes": NB_COLONNES, "symboles": NB_SYMBOLES,
             "fenetre_positions": FENETRE_POSITIONS, "plafond_materialises": PLAFOND_MATERIALISES,
             "axes": obs["axes"], "adresses_nommables": obs["adresses_nommables"],
             "materialises": obs["reseau"].materialises,
             "occupation": obs["reseau"].occupation,
             "empreinte_reseau": obs["reseau"].empreinte(),
             "plan_de_crissance": plan_de_crissance(obs["axes"]),
             "ecritures_refusees": obs["reseau"].ecritures_refusees,
             "octets_par_slot": obs["memoire"]["octets_par_slot"],
             "debit_hachage_par_seconde": round(obs["debit_hachage"], 1),
             "poids_sur_disque_inventories": len(obs["poids_sur_disque"])}
    rapport["cadre"] = cadre
    return rapport


# ────────────────────────────────────────────────────────────────────────────
# 6. Banc de mutations : un contrôle qui ne rouge jamais ne contrôle rien
# ────────────────────────────────────────────────────────────────────────────

def _mut_capacite_trompeuse(o: Observation) -> Observation:
    n = dict(o)
    n["capacite"] = CONSTANTE_C * 10 ** 11
    return n


def _mut_adressage_biase(o: Observation) -> Observation:
    n = dict(o)
    paquets = [0] * 256
    paquets[0] = int(o["chantillon"])
    attendu = int(o["chantillon"]) / 256.0
    n["buckets"] = paquets
    n["chi2"] = sum((b - attendu) ** 2 / attendu for b in paquets)
    return n


def _mut_sans_seconde_instance(o: Observation) -> Observation:
    n = dict(o)
    n["empreinte_tiers"] = {"erreur": "SUBPROCESS_ABSENT"}
    return n


def _mut_reseau_vide(o: Observation) -> Observation:
    n = dict(o)
    n["reseau"] = ReseauPoidsSparse()
    n["materialisation"] = dict(o["materialisation"], rencontres=0, arrete_au_plafond=False)
    return n


def _mut_axes_reduits(o: Observation) -> Observation:
    n = dict(o)
    axes = dict(o["axes"], entrees=0)
    n["axes"] = axes
    n["adresses_nommables"] = 0
    return n


def _mut_poids_importes(o: Observation) -> Observation:
    n = dict(o)
    n["poids_lus_par_ce_module"] = True
    return n


def _mut_similarite_inventee(o: Observation) -> Observation:
    n = dict(o)
    n["recouvrement_bis"] = dict(o["recouvrement_bis"], similarite=0.77)
    return n


def _mut_compteur_endormi(o: Observation) -> Observation:
    n = dict(o)
    n["debit_hachage"] = 10.0
    n["collisions_sous_espace"] = 0
    return n


MUTATIONS: Dict[str, Callable[[Observation], Observation]] = {
    "EQ-PS-01": _mut_capacite_trompeuse,
    "EQ-PS-03": _mut_adressage_biase,
    "EQ-PS-04": _mut_sans_seconde_instance,
    "EQ-PS-05": _mut_reseau_vide,
    "EQ-PS-06": _mut_axes_reduits,
    "EQ-PS-07": _mut_poids_importes,
    "EQ-PS-08": _mut_similarite_inventee,
    "EQ-PS-09": _mut_compteur_endormi,
}


def verifier_mutations(obs: Optional[Observation] = None) -> Dict[str, object]:
    rejouee = obs is None
    # La fixture part de la même observation que --controler : une mutation testée sur une
    # normale déjà FAIL ne prouve rien. À 20 000 échantillons, EQ-PS-03 est à la lisière
    # du seuil (χ² 311,9 pour 310,5 mesuré le 2026-11-13) et EQ-PS-04 faute de second
    # processus : la normale n'y est pas stable.
    obs = obs or observer()
    obs = dict(obs)
    obs.setdefault("poids_lus_par_ce_module", False)
    resultats = {}
    for identifiant, mut in MUTATIONS.items():
        normal = CONTROLES[identifiant](obs)[0]
        mute = CONTROLES[identifiant](mut(obs))[0]
        resultats[identifiant] = {"normal": normal, "mute": mute,
                                  "capte": normal == "PASS" and mute != "PASS"}
    return {"par_equation": resultats,
            "captees": sum(1 for v in resultats.values() if v["capte"]),
            "testees": len(resultats), "observation_rejouee": rejouee}


# ────────────────────────────────────────────────────────────────────────────
# 7. CLI
# ────────────────────────────────────────────────────────────────────────────

def _affiche(objet: object) -> None:
    print(json.dumps(objet, ensure_ascii=False, indent=2, default=str))


def main(argv: Sequence[str]) -> int:
    if "--slot" in argv:
        e, s, c, y, t = (int(x) for x in argv[argv.index("--slot") + 1].split("|"))
        _affiche({"slot": slot_de(e, s, c, y, t), "capacite": CAPACITE_POIDS,
                  "cle": argv[argv.index("--slot") + 1]})
        return 0
    if "--questions" in argv:
        a, b = argv[argv.index("--questions") + 1].split("||")
        _affiche(recouvrement(a, b))
        return 0
    if "--mutations" in argv:
        rapport = verifier_mutations()
        _affiche(rapport)
        return 0 if rapport["captees"] == rapport["testees"] else 1
    echantillons = 200_000
    if "--echantillons" in argv:
        echantillons = int(argv[argv.index("--echantillons") + 1])
    if "--controler" in argv:
        rapport = controler(echantillons=echantillons,
                            croiser_processus="--sans-processus" not in argv)
        if "--json" in argv:
            _affiche(rapport)
        else:
            c = rapport["cadre"]
            print(f"{c['capacite_poids']:,} poids adressables ".replace(",", " ")
                  + f"| {c['materialises']:,} matérialisés ".replace(",", " ")
                  + f"| {c['adresses_nommables']:,} nommables par la matrice".replace(",", " "))
            for eq in rapport["equations"]:
                print(f"{eq['statut']:<12} {eq['id']} {eq['titre']}")
            print("compte :", rapport["compte"], "racine :", rapport["racine"][:16])
        return 0 if rapport["compte"]["FAIL"] == 0 and rapport["compte"]["INCONCLUSIF"] == 0 else 1
    _affiche({"module": "reseau_poids_sparse_mizan.py", "version": VERSION, "auteur": AUTEUR,
              "capacite_poids": CAPACITE_POIDS, "dense_bf16_octets": DENSE_BF16_OCTETS,
              "usage": ["--controler [--echantillons N] [--json] [--sans-processus]",
                        "--slot 1|0|0|7|3", "--questions \"a||b\"", "--mutations"]})
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
