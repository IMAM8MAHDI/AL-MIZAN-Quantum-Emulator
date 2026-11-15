# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""Accomplissement des 313 000 000 000 000 poids visés — registre EQ-TLU.

Le socle `reseau_poids_sparse_mizan.py` dit une chose que ce module reprécise :
l'espace vaut 313 × 10^12 emplacements et 175 509 d'entre eux sont écrits par le
registre. « Accomplir les 313 T de poids visés » a trois sens séparés, traités
séparément ici :

    accompli comme VOLUME    — stocker 3,13e14 nombres : 626 To en bf16, 2 504 To en
                               float64. Cette machine n'en offre que quelques dizaines
                               de gigaoctets : la marge est mesurée à chaque exécution
                               (`mesures_machine()`, EQ-TLU-06) et tourne autour de
                               1,9e4 x sur disque et 2,8e6 x en RAM. Ce module ne
                               l'affirme pas : il le refuse et donne la marge.
    accompli comme STRUCTURE — chaque adresse de [0, 313T) a un nom, chaque nom a une
                               adresse : les radices (313, 10, 10, ..., 10) ont pour
                               produit EXACTEMENT 313T, et la couverture n'est plus un
                               échantillon mais une partition vérifiée.
    accompli comme FONCTION  — un poids est défini pour chaque adresse, calculable en
                               O(1) sans stockage : `poids(i)`. Le réseau dense n'est
                               pas mémorisé, il est lu à la volée. Deux tirages
                               chronométrés bornent le débit (EQ-TLU-07) ; le temps
                               d'énumération qui en est extrapolé se compte en siècles,
                               jamais en secondes, et n'a jamais été couru.

Ce qui est réellement matérialisé : une grille d'ancrage de 313 000 poids, exactement
10^-9 de la capacité, soit 1,565 fois le plafond publié du socle (200 000) et 1,78 fois
ce que le registre écrivait (175 509), avec une racine de Merkle recomputée deux fois
à l'identique.

Un contrôle ne recopie pas la valeur affichée : il la retrouve par une autre route.
C02 décompose par Horner puis confronte à la conversion décimale de Python ; C03
mesure la partition par trois identités entières distinctes ; C04 confronte deux
implémentations indépendantes du quantile χ² et exige un statistic encadré (ni biaisé
ni sospeusement parfait) ; C07 débite deux tailles différentes et requiert qu'elles
se recouvrent. Le banc de fixtures attaque les contrôles à rebours : une normale qui
rouge sous mutation prouve que l'instrument lit quelque chose.

Dans l'atelier de production, ce module n'écrit rien dans l'espace scellé par le
manifeste d'antériorité du site : il n'est nommé dans aucun de ses globs, ne modifie
ni le socle ni ses pages, et son certificat tombe sous `resultats/`, déjà exclu.
Dans ce dépôt le scellement est celui de `FONDATION/OUTILS/sceller_manifeste.py`,
pris sur les blobs git : le module et sa suite de tests y entrent donc, et leur
empreinte déplace le sceau ; le certificat, lui, n'y est pas commité, parce qu'il
porte les grandeurs de la machine qui l'émet. L'écriture reste bornée à
`resultats/accomplissement_313t/`.
"""

import hashlib
import json
import math
import shutil
import sys
import time
import tracemalloc
from array import array
from fractions import Fraction as Q
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple

RACINE = Path(__file__).resolve().parent
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

import reseau_poids_sparse_mizan as socle                           # noqa: E402

VERSION = "1.0"
AUTEUR = "M. Ahmed El Bahloul (IMAM8MAHDI)"

CONSTANTE_C: int = socle.CONSTANTE_C            # 313, scellé dans bibliotheques/lib_physique.py
ECHELLE: int = socle.ECHELLE                    # 10^12, l'échelle demandée par l'auteur
CAPACITE: int = socle.CAPACITE_POIDS            # 313 000 000 000 000
DENSE_BF16_OCTETS: int = socle.DENSE_BF16_OCTETS
DENSE_FLOAT64_OCTETS: int = 8 * CAPACITE
UNITE_HACHAGE: int = 2 ** 64 - 1                # max d'un BLAKE2b-64 lu en grand endian

# Les radices qui ferment exactement le cardinal : une de 313, douze de 10.
RADICES: Tuple[int, ...] = (CONSTANTE_C,) + (10,) * 12
# La boîte exhaustive reprend le même code avec trois radices de 10 seulement.
RADICES_EXHAUSTIVES: Tuple[int, ...] = (CONSTANTE_C,) + (10,) * 3
PAS_GRILLE = 10 ** 9                            # les neuf derniers chiffres à zéro
CHIFFRES_ANCRE = 3                              # 313 x 10^3 = 313 000 ancres

CONFIANCE_SUP = 1.0 - 1e-6                      # seuil haut :attrape un biais grossier
CONFIANCE_INF = 1e-6                            # seuil bas : attrape un statistic éteint

STATUTS = ("PASS", "FAIL", "INCONCLUSIF")
SENS = ("volume", "structure", "fonction")

DESSINS_LOI = 20_000                            # tirages déterministes pour la loi de poids
CONTROLE_INTERNE = 2_000                        # pointes confrontées à la conversion décimale
DEBIT_PETIT = 50_000
DEBIT_GRAND = 150_000
ECHANTILLON_DISTINCTS_GRILLE = 50_000


class NomInvalide(ValueError):
    """Adresse ou chiffre hors de la boîte : la bijection n'est pas définie ailleurs."""


# ────────────────────────────────────────────────────────────────────────────
# 1. Arithmétique des bases mixtes — réécrite ici, pas importée du socle
# ────────────────────────────────────────────────────────────────────────────

def produit(radices: Sequence[int]) -> int:
    r = 1
    for n in radices:
        r *= int(n)
    return r


def pas_positionnels(radices: Sequence[int]) -> List[int]:
    """poids[k] = produit des radices d'indice > k : le pas du rang k."""
    poids = [1] * len(radices)
    for k in range(len(radices) - 2, -1, -1):
        poids[k] = poids[k + 1] * int(radices[k + 1])
    return poids


def nommer(i: int, radices: Sequence[int] = RADICES) -> Tuple[int, ...]:
    """Adresse -> chiffres, du plus significatif au moins significatif."""
    m = produit(radices)
    if not 0 <= i < m:
        raise NomInvalide(f"adresse {i} hors de [0, {m})")
    pas, reste, chiffres = pas_positionnels(radices), int(i), []
    for k in range(len(radices)):
        chiffres.append(reste // pas[k])
        reste %= pas[k]
    return tuple(chiffres)


def slot(chiffres: Sequence[int], radices: Sequence[int] = RADICES) -> int:
    """Chiffres -> adresse par Horner. Inverse de `nommer` sur la boîte."""
    if len(chiffres) != len(radices):
        raise NomInvalide(f"{len(chiffres)} chiffres pour {len(radices)} radices")
    v = 0
    for k, (c, r) in enumerate(zip(chiffres, radices)):
        if not 0 <= int(c) < int(r):
            raise NomInvalide(f"chiffre {k} = {c} hors radix {r}")
        v = v * int(r) + int(c)
    return v


def nom_canonique(chiffres: Sequence[int]) -> bytes:
    """Séparateur 0x1f : deux noms distincts ne peuvent pas produire les mêmes octets."""
    return b"\x1f".join(str(int(c)).encode("ascii") for c in chiffres)


def nommer_par_str(i: int) -> Tuple[int, ...]:
    """Seconde route : la conversion décimale de Python, pas ma décomposition."""
    if not 0 <= i < CAPACITE:
        raise NomInvalide(f"adresse {i} hors de [0, {CAPACITE})")
    haut, bas = divmod(int(i), ECHELLE)
    return (haut,) + tuple(int(x) for x in f"{bas:012d}")


def factoriser(n: int) -> List[Tuple[int, int]]:
    """Division d'essai écrite ici : le socle a la sienne, la confrontation fait contrôle."""
    f, d, reste = [], 2, int(n)
    while d * d <= reste:
        if reste % d == 0:
            e = 0
            while reste % d == 0:
                reste //= d
                e += 1
            f.append((d, e))
        d += 1 if d == 2 else 2
    if reste > 1:
        f.append((reste, 1))
    return f


def est_premier_6k(n: int) -> bool:
    """Test en 6k±1, indépendant de la division d'essai ci-dessus et de celui du socle."""
    if n < 2:
        return False
    for p in (2, 3):
        if n % p == 0:
            return n == p
    d = 5
    while d * d <= n:
        if n % d == 0 or n % (d + 2) == 0:
            return False
        d += 6
    return True


def quantile_normale(p: float) -> float:
    """z tel que P(Z <= z) = p, par bissection sur la CDF normale centrée réduite."""
    if not 0.0 < p < 1.0:
        raise ValueError("p doit être dans ]0, 1[")
    lo, hi = -12.0, 12.0
    for _ in range(120):
        mid = 0.5 * (lo + hi)
        if 0.5 * (1.0 + math.erf(mid / math.sqrt(2.0))) < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def seuil_chi2(ddl: int, p: float) -> float:
    """Wilson-Hilferty réimplémentée ici, pour être confrontée à celle du socle."""
    if ddl < 1:
        raise ValueError("ddl >= 1")
    z = quantile_normale(p)
    return ddl * (1.0 - 2.0 / (9.0 * ddl) + z * math.sqrt(2.0 / (9.0 * ddl))) ** 3


def statistic_chi2(effectifs: Sequence[int], attendu: float) -> float:
    return sum((int(o) - attendu) ** 2 / attendu for o in effectifs)


# ────────────────────────────────────────────────────────────────────────────
# 2. La loi de poids : 313 T adresses, zéro stockage
# ────────────────────────────────────────────────────────────────────────────

def hacher(i: int) -> int:
    return int.from_bytes(
        hashlib.blake2b(nom_canonique(nommer(i)), digest_size=8).digest(), "big")


def poids(i: int) -> float:
    """w(i) dans [0, 1] : O(1), sans table, sans graine, reproductible octet pour octet.

    C'est le seul sens où « les 313 T poids » puissent exister sur cette machine :
    non pas stockés, mais définis pour chaque adresse et lus à la volée.
    """
    return hacher(i) / float(UNITE_HACHAGE)


def adresses_dessin(n: int, pas: Optional[int] = None) -> List[int]:
    """Suite déterministe, jamais un tirage aléatoire : le statistic de C04 est rejeuable."""
    pas = pas if pas is not None else max(1, CAPACITE // (n or 1))
    return [min(CAPACITE - 1, k * pas + 7) for k in range(n)]


# ────────────────────────────────────────────────────────────────────────────
# 3. Ce que la machine tient réellement
# ────────────────────────────────────────────────────────────────────────────

def _mesurer_ram() -> Dict[str, object]:
    """GlobalMemoryStatusEx par ctypes : dépendance standard uniquement, lecture seule."""
    import ctypes

    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [
            ("dwLength", ctypes.c_uint32), ("dwMemoryLoad", ctypes.c_uint32),
            ("ullTotalPhys", ctypes.c_uint64), ("ullAvailPhys", ctypes.c_uint64),
            ("ullTotalPageFile", ctypes.c_uint64), ("ullAvailPageFile", ctypes.c_uint64),
            ("ullTotalVirtual", ctypes.c_uint64), ("ullAvailVirtual", ctypes.c_uint64),
            ("ullAvailExtendedVirtual", ctypes.c_uint64),
        ]

    m = MEMORYSTATUSEX()
    m.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):
        return {"disponible": False, "total_octets": 0, "libre_octets": 0, "charge_pct": 0}
    return {"disponible": True, "total_octets": int(m.ullTotalPhys),
            "libre_octets": int(m.ullAvailPhys), "charge_pct": int(m.dwMemoryLoad)}


def mesures_machine() -> Dict[str, object]:
    disque = shutil.disk_usage(str(RACINE))
    ram = _mesurer_ram()
    libre = int(disque.free)
    teneur = 8                                  # un float64 nu, sans objet Python
    tenants = int(ram["libre_octets"]) // teneur if ram["disponible"] else 0
    return {
        "disque_total_octets": int(disque.total),
        "disque_libre_octets": libre,
        "dense_bf16_octets": DENSE_BF16_OCTETS,
        "dense_float64_octets": DENSE_FLOAT64_OCTETS,
        "marge_bf16_sur_disque": DENSE_BF16_OCTETS / libre if libre else None,
        "marge_float64_sur_disque": DENSE_FLOAT64_OCTETS / libre if libre else None,
        "ram": ram,
        "teneur_par_slot_octets": teneur,
        "slots_tenants_en_ram": tenants,
        "marge_ram": CAPACITE / tenants if tenants else None,
    }


def mesurer_debit(n_petit: int = DEBIT_PETIT, n_grand: int = DEBIT_GRAND) -> Dict[str, object]:
    """Deux mesures de débit, pas une : l'extrapolation n'est honnête que si elle se recoupe."""
    rendus: Dict[int, Dict[str, object]] = {}
    for n in (n_petit, n_grand):
        t0 = time.perf_counter()
        s = 0.0
        for i in adresses_dessin(n):
            s += poids(i)
        d = time.perf_counter() - t0
        rendus[n] = {"seconde": d, "debit": n / d if d else 0.0, "somme": s}
    bas, haut = rendus[n_petit]["debit"], rendus[n_grand]["debit"]
    retenu = min(bas, haut)
    t = CAPACITE / retenu if retenu else None
    return {"par_taille": rendus, "debit_retenu": retenu,
            "rapport_debits": (haut / bas) if bas else None,
            "temps_enumere_seconde": t,
            "temps_enumere_annees": (t / 31_557_600.0) if t else None,
            "seconde_annee": 31_557_600.0}


# ────────────────────────────────────────────────────────────────────────────
# 4. Grille d'ancrage matérialisée
# ────────────────────────────────────────────────────────────────────────────

def racine_merkle(feuilles: bytearray) -> str:
    """Arbre bâti sur un bloc contigu de digests de 32 octets, feuilles ordonnées par adresse.

    Le manifeste de l'atelier trie ses empreintes ; ici l'ordre est celui de l'adresse,
    parce que c'est lui qui porte la sémantique du registre. La divergence est déclarée.
    Quand un niveau compte un nombre impair de feuilles, la dernière est dupliquée.
    """
    if len(feuilles) % 32:
        raise ValueError("bloc de feuilles multiples de 32 octets")
    if not feuilles:
        return hashlib.sha256(b"").hexdigest()
    niveau = feuilles
    while len(niveau) > 32:
        if len(niveau) % 64:
            niveau = niveau + niveau[-32:]
        suivant = bytearray()
        for k in range(0, len(niveau), 64):
            suivant += hashlib.sha256(bytes(niveau[k:k + 64])).digest()
        niveau = suivant
    return niveau.hex()


def grille_ancrage(chiffres_significatifs: int = CHIFFRES_ANCRE,
                   recalculer: bool = True) -> Dict[str, object]:
    """Les adresses dont les derniers chiffres sont nuls, avec leurs poids réels.

    Le pas est dérivé du nombre de chiffres conservés : 10^(12 - k), donc k = 3 rend
    la grille publiée de 313 000 ancres et k = 2 une grille dix fois moindre que les
    tests utilisent pour la même arithmétique à moindre coût.
    Taille exacte par trois routes : division entière de la capacité par le pas,
    produit des radices tronquées, et dénombrement de l'itération.
    """
    if not 1 <= chiffres_significatifs <= 12:
        raise ValueError("un à douze chiffres significatifs")
    pas = 10 ** (12 - chiffres_significatifs)
    divisible = (CAPACITE % pas == 0)
    par_division = CAPACITE // pas
    par_produit = produit(RADICES[:1 + chiffres_significatifs])
    t0 = time.perf_counter()
    tracemalloc.start()
    adresses = array("Q")
    poids_tab = array("d")
    feuilles = bytearray()
    for c in range(CONSTANTE_C):
        base = c * ECHELLE
        for tete in range(10 ** chiffres_significatifs):
            i = base + tete * pas
            w = poids(i)
            adresses.append(i)
            poids_tab.append(w)
            feuilles += hashlib.sha256(f"{i}|{w!r}".encode("ascii")).digest()
    pic, _ = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    duree = time.perf_counter() - t0
    n = len(adresses)
    n_ech = min(ECHANTILLON_DISTINCTS_GRILLE, n)
    croissant = all(adresses[k] < adresses[k + 1] for k in range(n - 1))
    rendu: Dict[str, object] = {
        "chiffres_significatifs": chiffres_significatifs,
        "pas": pas,
        "divisible_exactement": divisible,
        "taille_par_division": int(par_division),
        "taille_par_produit": int(par_produit),
        "taille_denomeree": n,
        "occupation": Q(par_division, CAPACITE) if divisible else None,
        "adresses_strictement_croissantes": croissant,
        "toutes_dans_capacite": bool(n and adresses[-1] < CAPACITE),
        "poids_dans_zero_un": bool(min(poids_tab) >= 0.0 and max(poids_tab) <= 1.0),
        "poids_min": min(poids_tab),
        "poids_max": max(poids_tab),
        "poids_distincts_sur_echantillon": (
            len(set(poids_tab[:n_ech])) == n_ech),
        "taille_echantillon_distincts": n_ech,
        "octets_table_poids": len(poids_tab) * poids_tab.itemsize,
        "octets_table_adresses": len(adresses) * adresses.itemsize,
        "octets_bloc_feuilles": len(feuilles),
        "pic_tracemalloc_octets": int(pic),
        "teneur_par_ancre_octets": round(pic / n, 3) if n else None,
        "racine_merkle": racine_merkle(feuilles),
        "racine_simple": hashlib.sha256(bytes(feuilles)).hexdigest(),
        "debit_grille_par_seconde": round(n / duree, 1) if duree else None,
        "duree_seconde": round(duree, 4),
    }
    if recalculer:
        autre = grille_ancrage(chiffres_significatifs, recalculer=False)
        rendu["racine_reproduite"] = autre["racine_merkle"] == rendu["racine_merkle"]
        rendu["racine_simple_reproduite"] = autre["racine_simple"] == rendu["racine_simple"]
    return rendu


# ────────────────────────────────────────────────────────────────────────────
# 5. Observations
# ────────────────────────────────────────────────────────────────────────────

def bijectif_exhaustif() -> Dict[str, object]:
    """Les deux sens de la bijection, énumérés entièrement sur la boîte réduite."""
    m = produit(RADICES_EXHAUSTIVES)
    retours = sum(1 for i in range(m)
                  if slot(nommer(i, RADICES_EXHAUSTIVES), RADICES_EXHAUSTIVES) == i)
    noms, hors_boite = 0, 0
    for c in range(RADICES_EXHAUSTIVES[0]):
        for a in range(10):
            for b in range(10):
                for d in range(10):
                    nom = (c, a, b, d)
                    s = slot(nom, RADICES_EXHAUSTIVES)
                    if nommer(s, RADICES_EXHAUSTIVES) == nom and 0 <= s < m:
                        noms += 1
                    else:
                        hors_boite += 1
    return {"radices": RADICES_EXHAUSTIVES, "taille_boite": m,
            "retours_identiques": retours, "noms_inverses": noms, "hors_boite": hors_boite}


def controles_interfaces() -> Dict[str, object]:
    """Pointes réelles, puis confrontation Horner / conversion décimale de Python."""
    pointes = [0, 1, 9, 10, 99, 100, ECHELLE - 1, ECHELLE, ECHELLE + 1,
               CAPACITE // 2, CAPACITE - CONSTANTE_C, CAPACITE - 1]
    draws = adresses_dessin(CONTROLE_INTERNE)
    refus = 0
    for i in (CAPACITE, CAPACITE + 1, -1):
        try:
            nommer(i)
        except NomInvalide:
            refus += 1
    refus_chiffre = 0
    for nom in ((CONSTANTE_C, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
                (0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)):
        try:
            slot(nom)
        except NomInvalide:
            refus_chiffre += 1
    return {"pointes": pointes,
            "pointes_identiques": sum(1 for i in pointes if nommer(i) == nommer_par_str(i)),
            "pointes_retour": sum(1 for i in pointes if slot(nommer(i)) == i),
            "pointes_deuxieme_route": sum(1 for i in pointes if slot(nommer_par_str(i)) == i),
            "interne_testees": CONTROLE_INTERNE,
            "interne_conformes": sum(1 for i in draws
                                     if nommer(i) == nommer_par_str(i) and slot(nommer(i)) == i),
            "hors_boite_refuses": refus, "chiffres_hors_radix_refuses": refus_chiffre}


def partition_fibres() -> Dict[str, object]:
    """Les 313 fibres de 10^12 : trois mesures entières indépendantes du recouvrement."""
    debut = [c * ECHELLE for c in range(CONSTANTE_C)]
    fin = [d + ECHELLE for d in debut]
    contiguous = sum(1 for k in range(CONSTANTE_C - 1) if fin[k] == debut[k + 1])
    somme = sum(f - d for f, d in zip(fin, debut))
    telescope = fin[-1] - debut[0]
    produit_constant = CONSTANTE_C * ECHELLE
    ancres_ok = sum(1 for c in range(CONSTANTE_C)
                    if nommer(debut[c])[0] == c and nommer(fin[c] - 1)[0] == c)
    return {"fibres": CONSTANTE_C, "contiguite_verifiee": contiguous,
            "debut": debut[0], "fin": fin[-1], "somme_mesures": somme,
            "telescope": telescope, "produit_constant": produit_constant,
            "recouvre_capacite": (somme == CAPACITE and telescope == CAPACITE
                                  and produit_constant == CAPACITE),
            "fibres_ancres": ancres_ok}


def loi_poids(n: int = DESSINS_LOI) -> Dict[str, object]:
    """Support, stabilité, avalanche et uniformité encadrée de la loi sur 20 000 adresses."""
    draws = adresses_dessin(n)
    w = [poids(i) for i in draws]
    w2 = [poids(i) for i in draws]
    suivants = sum(1 for i in draws
                   if poids(i + 1 if i + 1 < CAPACITE else 0) != poids(i))
    buckets = [0] * CONSTANTE_C
    for x in w:
        buckets[min(CONSTANTE_C - 1, int(x * CONSTANTE_C))] += 1
    attendu = n / float(CONSTANTE_C)
    stat = statistic_chi2(buckets, attendu)
    ddl = CONSTANTE_C - 1
    haut, bas = seuil_chi2(ddl, CONFIANCE_SUP), seuil_chi2(ddl, CONFIANCE_INF)
    return {"dessins": n, "cases": CONSTANTE_C, "ddl": ddl,
            "dans_support": sum(1 for x in w if 0.0 <= x <= 1.0),
            "stables": sum(1 for a, b in zip(w, w2) if a == b),
            "distincts": len(set(w)), "suivants_distincts": suivants,
            "case_min": min(buckets), "case_max": max(buckets),
            "chi2": round(stat, 4), "attendu_par_case": round(attendu, 4),
            "borne_haute": round(haut, 4), "borne_basse": round(bas, 4),
            "seuil_socle_haut": round(socle.seuil_chi2(ddl, CONFIANCE_SUP), 4),
            "seuil_socle_bas": round(socle.seuil_chi2(ddl, CONFIANCE_INF), 4),
            "ecart_haut_relatif": abs(haut - socle.seuil_chi2(ddl, CONFIANCE_SUP)) / haut,
            "ddl2_wilson_hilferty": round(seuil_chi2(2, 0.99), 6),
            "ddl2_formule_exacte": round(-2.0 * math.log(1.0 - 0.99), 6)}


def nommables_registre() -> Dict[str, object]:
    """Ce que le registre nomme aujourd'hui, lu dans le socle, ratio recalculé en exact."""
    axes = socle.axes_registre()
    plan = socle.plan_de_crissance(axes)
    nommables = socle.adresses_nommables(axes)
    regroupement = (axes["entrees"] * axes["strates"]) * (axes["colonnes"] * axes["symboles"]) \
        * axes["tranches"]
    ratio_exact = Q(nommables, CAPACITE)
    return {"axes": axes, "nommables": nommables,
            "regroupement_alternatif": regroupement,
            "ratio_exact": ratio_exact, "ratio_flottant": float(ratio_exact),
            "ratio_socle": plan["ratio_espace_nomme"],
            "facteur_manquant": plan["facteur_manquant"],
            "entrees_pour_egaliser": plan["entrees_pour_egaliser"],
            "tranches_pour_egaliser": plan["tranches_pour_egaliser"],
            "materialises_socle_publie": 175_509,
            "plafond_socle": socle.PLAFOND_MATERIALISES}


def observer(loom: int = DESSINS_LOI, avec_grille: bool = True) -> Dict[str, object]:
    t0 = time.perf_counter()
    obs: Dict[str, object] = {
        "capacite": CAPACITE, "constante_c": CONSTANTE_C, "echelle": ECHELLE,
        "radices": RADICES, "produit_radices": produit(RADICES),
        "exhaustif": bijectif_exhaustif(),
        "interfaces": controles_interfaces(),
        "partition": partition_fibres(),
        "loi": loi_poids(loom),
        "nommables": nommables_registre(),
        "machine": mesures_machine(),
        "debit": mesurer_debit(),
        "capacite_socle": socle.CAPACITE_POIDS,
        "dense_socle": socle.DENSE_BF16_OCTETS,
    }
    obs["grille"] = grille_ancrage() if avec_grille else None
    obs["duree_observation"] = round(time.perf_counter() - t0, 4)
    return obs


# ────────────────────────────────────────────────────────────────────────────
# 6. Registre EQ-TLU : équations, formes, contrôles
# ────────────────────────────────────────────────────────────────────────────
# Convention reprise du socle : chemin = "<fichier>.py -> <fonction>() -> Cnn", le
# Cnn final est l'identifiant du contrôle. Chaque contrôle retrouve la valeur affichée
# par une route qu'il écrit lui-même, jamais en relisant `obs` tel quel.

def eq_tlu_01(o: Dict[str, object], mut: Optional[str] = None) -> Tuple[str, Dict[str, object], str]:
    """Le cardinal visé se ferme exactement sur les radices (313, 10^12)."""
    radices = RADICES if mut != "radix_faussee" else (CONSTANTE_C,) + (10,) * 11
    p = produit(radices)
    f = factoriser(CAPACITE)
    produit_fact = 1
    for base, expo in f:
        produit_fact *= base ** expo
    ok = (p == CAPACITE and produit_fact == CAPACITE and est_premier_6k(CONSTANTE_C)
          and [b for b, _ in f] == sorted(b for b, _ in f)
          and o["capacite"] == o["capacite_socle"] and len(radices) == 13
          and radices[0] == CONSTANTE_C)
    return ("PASS" if ok else "FAIL",
            {"produit_radices": p, "factorisation": f, "produit_factorisation": produit_fact,
             "constante_c_premier": est_premier_6k(CONSTANTE_C), "radices": list(radices),
             "nb_radices": len(radices), "capacite_socle": o["capacite_socle"]},
            "accomplissement_313t_mizan.py → eq_tlu_01() → C01")


def eq_tlu_02(o: Dict[str, object], mut: Optional[str] = None) -> Tuple[str, Dict[str, object], str]:
    """Nommer et décoder sont bijectifs : exhaustif sur une boîte, croisé sur la vraie."""
    e, i = o["exhaustif"], o["interfaces"]
    total = e["taille_boite"]
    décalage = 1 if mut == "retour_tronque" else 0
    retours = e["retours_identiques"] - décalage
    inverses = e["noms_inverses"] - décalage
    ok = (retours == total and inverses == total and e["hors_boite"] == 0
          and i["pointes_identiques"] == len(i["pointes"])
          and i["pointes_retour"] == len(i["pointes"])
          and i["pointes_deuxieme_route"] == len(i["pointes"])
          and i["interne_conformes"] == i["interne_testees"]
          and i["hors_boite_refuses"] == 3 and i["chiffres_hors_radix_refuses"] == 2)
    return ("PASS" if ok else "FAIL",
            {"boite_exhaustive": total, "retours_identiques": retours,
             "noms_inverses_verifies": inverses, "hors_boite": e["hors_boite"],
             "pointes": len(i["pointes"]), "pointes_identiques": i["pointes_identiques"],
             "pointes_deuxieme_route": i["pointes_deuxieme_route"],
             "interne": i["interne_testees"], "interne_conformes": i["interne_conformes"],
             "hors_boite_refuses": i["hors_boite_refuses"],
             "chiffres_hors_radix_refuses": i["chiffres_hors_radix_refuses"],
             "route_independante": "divmod + format 012d (Python) contre Horner (ici)"},
            "accomplissement_313t_mizan.py → eq_tlu_02() → C02")


def eq_tlu_03(o: Dict[str, object], mut: Optional[str] = None) -> Tuple[str, Dict[str, object], str]:
    """Les 313 fibres de 10^12 partitionnent [0, 313T) : trois identités entières."""
    p = o["partition"]
    somme = p["somme_mesures"] - (1 if mut == "mesure_gonflee" else 0)
    ok = (somme == CAPACITE and p["telescope"] == CAPACITE
          and p["produit_constant"] == CAPACITE
          and p["contiguite_verifiee"] == p["fibres"] - 1
          and p["debut"] == 0 and p["fin"] == CAPACITE
          and p["fibres_ancres"] == p["fibres"])
    return ("PASS" if ok else "FAIL",
            {"fibres": p["fibres"], "somme_des_mesures": somme, "telescope": p["telescope"],
             "produit_constant": p["produit_constant"],
             "contiguite_verifiee": p["contiguite_verifiee"],
             "debut": p["debut"], "fin": p["fin"], "fibres_ancres": p["fibres_ancres"]},
            "accomplissement_313t_mizan.py → eq_tlu_03() → C03")


def eq_tlu_04(o: Dict[str, object], mut: Optional[str] = None) -> Tuple[str, Dict[str, object], str]:
    """La loi de poids est totale, stable et non constante ; uniformité encadrée à 1e-6."""
    l = o["loi"]
    stat = 0.0 if mut == "loi_platee" else l["chi2"]
    distincts = 1 if mut == "loi_platee" else l["distincts"]
    ok = (l["dans_support"] == l["dessins"] and l["stables"] == l["dessins"]
          and distincts == l["dessins"] and l["suivants_distincts"] == l["dessins"]
          and l["borne_basse"] < stat < l["borne_haute"]
          and l["ecart_haut_relatif"] < 1e-9
          and abs(l["ddl2_wilson_hilferty"] - l["ddl2_formule_exacte"])
          / l["ddl2_formule_exacte"] < 1e-2
          and l["attendu_par_case"] >= 5.0)
    return ("PASS" if ok else "FAIL",
            {"dessins": l["dessins"], "cases": l["cases"], "ddl": l["ddl"],
             "dans_support": l["dans_support"], "stables": l["stables"],
             "distincts": distincts, "suivants_distincts": l["suivants_distincts"],
             "chi2": stat, "attendu_par_case": l["attendu_par_case"],
             "case_min": l["case_min"], "case_max": l["case_max"],
             "borne_basse": l["borne_basse"], "borne_haute": l["borne_haute"],
             "seuil_socle_haut": l["seuil_socle_haut"],
             "ecart_seuil_relatif": round(l["ecart_haut_relatif"], 15),
             "ddl2_wilson_hilferty": l["ddl2_wilson_hilferty"],
             "ddl2_formule_exacte": l["ddl2_formule_exacte"]},
            "accomplissement_313t_mizan.py → eq_tlu_04() → C04")


def eq_tlu_05(o: Dict[str, object], mut: Optional[str] = None) -> Tuple[str, Dict[str, object], str]:
    """Ce que le registre nomme est un sous-ensemble strict du cardinal : ratio exact."""
    n = o["nommables"]
    nommables = CAPACITE if mut == "nommables_surlevalues" else n["nommables"]
    ratio = Q(nommables, CAPACITE)
    ok = (n["regroupement_alternatif"] == n["nommables"] and nommables < CAPACITE
          and abs(n["ratio_flottant"] - n["ratio_socle"]) < 1e-12
          and ratio < 1 and n["facteur_manquant"] > 1
          and n["materialises_socle_publie"] < n["plafond_socle"]
          and ratio * CAPACITE == nommables
          and n["tranches_pour_egaliser"] > n["axes"]["tranches"])
    return ("PASS" if ok else "FAIL",
            {"axes": n["axes"], "adresses_nommables": nommables,
             "regroupement_alternatif": n["regroupement_alternatif"],
             "ratio_exact": str(ratio), "ratio_decimal": float(ratio),
             "ratio_socle": n["ratio_socle"],
             "facteur_manquant": round(n["facteur_manquant"], 6),
             "entrees_pour_egaliser": n["entrees_pour_egaliser"],
             "tranches_pour_egaliser": n["tranches_pour_egaliser"],
             "materialises_socle": n["materialises_socle_publie"],
             "plafond_socle": n["plafond_socle"]},
            "accomplissement_313t_mizan.py → eq_tlu_05() → C05")


def eq_tlu_06(o: Dict[str, object], mut: Optional[str] = None) -> Tuple[str, Dict[str, object], str]:
    """Le volume dense est mesuré, pas imaginé : c'est ce que la machine refuse."""
    m = o["machine"]
    dense = o["dense_socle"] // 10 if mut == "dense_divise_par_dix" else o["dense_socle"]
    libre = m["disque_libre_octets"]
    marge = dense / libre if libre else None
    tenants = m["slots_tenants_en_ram"]
    ok = (2 * CAPACITE == dense and o["dense_socle"] == DENSE_BF16_OCTETS
          and DENSE_FLOAT64_OCTETS == 8 * CAPACITE and libre > 0 and marge is not None
          and marge > 1.0 and m["ram"]["disponible"] and 0 < tenants < CAPACITE
          and m["marge_ram"] > 1.0)
    return ("PASS" if ok else "FAIL",
            {"dense_bf16_octets": dense, "dense_float64_octets": DENSE_FLOAT64_OCTETS,
             "disque_libre_octets": libre, "disque_total_octets": m["disque_total_octets"],
             "marge_bf16_sur_disque": round(marge, 1) if marge else None,
             "marge_float64_sur_disque": round(DENSE_FLOAT64_OCTETS / libre, 1) if libre else None,
             "ram_libre_octets": m["ram"]["libre_octets"],
             "ram_charge_pct": m["ram"]["charge_pct"],
             "slots_tenants_en_ram": tenants,
             "marge_ram": round(m["marge_ram"], 1) if m["marge_ram"] else None,
             "accompli_comme_volume": False},
            "accomplissement_313t_mizan.py → eq_tlu_06() → C06")


def eq_tlu_07(o: Dict[str, object], mut: Optional[str] = None) -> Tuple[str, Dict[str, object], str]:
    """Énumérer les 313 T une seule fois dépasse la durée de vie de la machine : débit mesuré."""
    d = o["debit"]
    retenu = 1e18 if mut == "debit_invente" else d["debit_retenu"]
    rapport = d["rapport_debits"]
    t = CAPACITE / retenu if retenu else None
    annees = t / d["seconde_annee"] if t else None
    ok = (rapport is not None and 0.5 <= rapport <= 2.0 and retenu > 0 and t is not None
          and annees is not None and annees > 1.0
          and d["par_taille"][DEBIT_PETIT]["somme"] > 0.0
          and len(d["par_taille"]) == 2)
    return ("PASS" if ok else "FAIL",
            {"debit_petit": round(d["par_taille"][DEBIT_PETIT]["debit"], 1),
             "debit_grand": round(d["par_taille"][DEBIT_GRAND]["debit"], 1),
             "rapport_debits": round(rapport, 4) if rapport else None,
             "debit_retenu": round(retenu, 1), "tailles": [DEBIT_PETIT, DEBIT_GRAND],
             "temps_enumere_seconde": round(t, 1) if t else None,
             "temps_enumere_annees": round(annees, 2) if annees else None,
             "extrapolation_mesuree_pas_enumeree": True},
            "accomplissement_313t_mizan.py → eq_tlu_07() → C07")


def eq_tlu_08(o: Dict[str, object], mut: Optional[str] = None) -> Tuple[str, Dict[str, object], str]:
    """La grille d'ancrage est matérialisée, comptée par trois routes et hachée deux fois."""
    g = o["grille"]
    chemin = "accomplissement_313t_mizan.py → eq_tlu_08() → C08"
    if g is None:
        return ("INCONCLUSIF", {"grille": "absente de l'observation (--sans-grille)"}, chemin)
    taille = g["taille_denomeree"] + (1 if mut == "grille_comptee_faussee" else 0)
    plafond = o["nommables"]["plafond_socle"]
    ok = (g["divisible_exactement"] and g["taille_par_division"] == g["taille_par_produit"]
          and taille == g["taille_par_division"]
          and Q(taille, CAPACITE) == Q(1, 10 ** 9)
          and g["adresses_strictement_croissantes"] and g["toutes_dans_capacite"]
          and g["poids_dans_zero_un"] and g["poids_distincts_sur_echantillon"]
          and len(g["racine_merkle"]) == 64 and len(g["racine_simple"]) == 64
          and g["racine_reproduite"] and g["racine_simple_reproduite"]
          and taille > plafond)
    return ("PASS" if ok else "FAIL",
            {"taille_par_division": g["taille_par_division"],
             "taille_par_produit": g["taille_par_produit"], "taille_denomeree": taille,
             "pas": g["pas"], "chiffres_significatifs": g["chiffres_significatifs"],
             "occupation_exacte": str(Q(taille, CAPACITE)),
             "occupation_decimale": float(Q(taille, CAPACITE)),
             "racine_merkle": g["racine_merkle"], "racine_simple": g["racine_simple"],
             "racine_reproduite": g["racine_reproduite"],
             "racine_simple_reproduite": g["racine_simple_reproduite"],
             "pic_memoire_octets": g["pic_tracemalloc_octets"],
             "teneur_par_ancre_octets": g["teneur_par_ancre_octets"],
             "poids_min": g["poids_min"], "poids_max": g["poids_max"],
             "debit_grille_par_seconde": g["debit_grille_par_seconde"],
             "plafond_socle": plafond, "au_dessus_du_plafond_du_socle": taille > plafond},
            chemin)


def eq_tlu_09(o: Dict[str, object], mut: Optional[str] = None) -> Tuple[str, Dict[str, object], str]:
    """Le mot « accompli » a trois sens : volume refusé sur mesure, structure et fonction tiennent."""
    p, g, n = o["partition"], o["grille"], o["nommables"]
    clos = (produit(RADICES) == CAPACITE and p["recouvre_capacite"]
            and o["exhaustif"]["retours_identiques"] == o["exhaustif"]["taille_boite"])
    couvert = p["fibres"] == CONSTANTE_C and p["fibres_ancres"] == CONSTANTE_C
    rempli = (g is not None and g["occupation"] == Q(1, 10 ** 9)
              and g["taille_denomeree"] == CAPACITE // PAS_GRILLE)
    if mut == "volume_declare_accompli":
        sens = {"volume": "accompli", "structure": "accompli", "fonction": "accompli"}
        rempli = False
    else:
        sens = {"volume": "non accompli — hors de portée mesurée",
                "structure": "accompli — partition vérifiée",
                "fonction": "accompli — loi totale O(1) sans stockage"}
    ok = clos and couvert and rempli and sens["volume"].startswith("non accompli")
    return ("PASS" if ok else "FAIL",
            {"sens": sens, "clos": clos, "couvert": couvert, "rempli": rempli,
             "capacite": CAPACITE, "fibres": p["fibres"],
             "grille_ancee": (g["taille_denomeree"] if g else None),
             "occupation_ancee": str(Q(1, 10 ** 9)),
             "nommables_par_le_registre": n["nommables"],
             "formule": "313 x 10^12 = 313 fibres ; 313 x 10^3 ancres = 10^-9 de la capacite"},
            "accomplissement_313t_mizan.py → eq_tlu_09() → C09")


EQUATIONS: Tuple[Tuple[str, str, str, Callable], ...] = (
    ("EQ-TLU-01", "Fermeture exacte du cardinal vise",
     "produit(313, 10 x12) = 313 000 000 000 000", eq_tlu_01),
    ("EQ-TLU-02", "Bijection adresse <-> nom",
     "exhaustif sur 313 000 + croise a la conversion decimale", eq_tlu_02),
    ("EQ-TLU-03", "Partition en 313 fibres",
     "somme = telescope = 313 x 10^12 = capacite", eq_tlu_03),
    ("EQ-TLU-04", "Loi de poids totale",
     "w(i) dans [0,1], stable, distincte, borne_basse < chi2(312) < borne_haute", eq_tlu_04),
    ("EQ-TLU-05", "Ce que le registre nomme",
     "produit(axes du registre charge) < capacite, ratio exact en Fraction", eq_tlu_05),
    ("EQ-TLU-06", "Volume dense refuse",
     "626 To bf16 / disque libre > 1 et RAM < capacite", eq_tlu_06),
    ("EQ-TLU-07", "Enumeration hors duree de vie",
     "313T / debit mesure > 1 an, deux tailles cohérentes", eq_tlu_07),
    ("EQ-TLU-08", "Grille d'ancrage materialisee",
     "313 000 = 10^-9, racine hachee deux fois a l'identique", eq_tlu_08),
    ("EQ-TLU-09", "Triple sens d'accompli",
     "structure et fonction tiennent, volume est refuse", eq_tlu_09),
)

CONTROLES = {identifiant: controle for identifiant, _t, _f, controle in EQUATIONS}


def limites() -> Dict[str, str]:
    return {
        "EQ-TLU-01": "Fermer le cardinal sur les radices (313, 10^12) est une écriture du même "
                    "nombre, pas une capacité nouvelle : le produit redonne exactement ce que le "
                    "socle avait déclaré. Ce qui change est l'accès — une adresse devient nommable "
                    "par décomposition de base, sans hachage et sans registre.",
        "EQ-TLU-02": "L'exhaustivité porte sur une boîte de 313 × 10^3 = 313 000 adresses, non sur "
                    "les 3,13×10^14 : le code est le même (fonctions paramétrées par les radices), "
                    "la taille est bornée par le temps. Sur la vraie échelle, douze pointes et 2 000 "
                    "adresses intérieures sont confrontées à la conversion décimale de Python.",
        "EQ-TLU-03": "Le recouvrement est vérifié sur les 313 intervalles par arithmétique entière : "
                    "cela prouve l'absence de trou et de chevauchement, pas que chaque intervalle "
                    "contienne de l'information.",
        "EQ-TLU-04": "La loi est une convention de remplissage déterministe (BLAKE2b-64 sur le nom), "
                    "pas un poids appris : rien n'a été entraîné ici. L'encadrement du χ² est choisi "
                    "à 1e-6 de chaque côté — il attrape un biais grossier ou un statistic éteint, pas "
                    "une dérive à 1 %. Le seuil vient de Wilson-Hilferty, exacte à ~0,15 % près sur "
                    "2 degrés de liberté, ce que le contrôle vérifie contre la forme close -2 ln(1-p).",
        "EQ-TLU-05": "Le produit des axes est un majorant d'adresses nommables recalculé sur le "
                    "tableau maître chargé : il est donc auto-référent et bouge dès qu'une strate "
                    "est ajoutée ou qu'une ligne est réécrite — 396 594 148 860 sur 470 × 42 le "
                    "14/11/2026 à 21:19:36Z, 440 618 966 788 sur 482 × 43 à 21:58:24Z. Deux "
                    "quintuplets peuvent hacher sur le même slot : le ratio ne dit rien de la "
                    "qualité du contenu, seulement de l'étendue nommée.",
        "EQ-TLU-06": "Les 626 To et les 2 504 To sont de l'arithmétique ; le disque libre, la RAM "
                    "libre et les marges sont des relevés de CETTE machine à cette heure, nommés "
                    "dans le seul JSON de service et jamais sur les pages, et ils changent d'une "
                    "exécution à "
                    "l'autre : la marge est une borne locale datée, pas une loi. Un serveur à 1 Po "
                    "ne rendrait pas l'énumération possible pour autant : le facteur bloquant "
                    "devient alors le débit, traité en EQ-TLU-07.",
        "EQ-TLU-07": "Le temps d'énumération est une extrapolation à partir de deux mesures de débit "
                    "(50 000 et 150 000 adresses), pas une course des 313 T. Elle néglige entrées/"
                    "sorties, parallélisme et coût du stockage : elle borne le problème, ne le résout "
                    "pas.",
        "EQ-TLU-08": "Les 313 000 ancres sont réelles, en mémoire, hachées — et disparaissent à la fin "
                    "du processus : ce certificat atteste d'une écriture, pas d'un poids persistant. "
                    "La racine ordonne les feuilles par adresse, contrairement au manifeste d'atelier "
                    "qui trie les siennes.",
        "EQ-TLU-09": "Ce module ne prétend pas avoir rempli 313 T de poids. Il affirme trois choses "
                    "distinctes et étiquetées : l'espace est clos (structure), la loi est totale "
                    "(fonction), le volume est refusé (mesure). Qui ne retient que le mot « accompli » "
                    "aura lu une phrase qui n'existe pas ici.",
    }


def evaluer(obs: Dict[str, object], mut: Optional[str] = None) -> Dict[str, object]:
    rendu: List[Dict[str, object]] = []
    for identifiant, titre, forme, controle in EQUATIONS:
        statut, valeur, chemin = controle(obs, mut)
        rendu.append({"id": identifiant, "titre": titre, "forme": forme, "statut": statut,
                      "valeur": valeur, "chemin_controle": chemin, "limite": limites()[identifiant]})
    compte = {s: sum(1 for c in rendu if c["statut"] == s) for s in STATUTS}
    return {"equations": rendu, "compte": compte,
            "racine": hashlib.sha256(
                "\n".join(f"{c['id']}|{c['statut']}" for c in rendu).encode("utf-8")).hexdigest()}


def cadre_de(obs: Dict[str, object], rapport: Dict[str, object]) -> Dict[str, object]:
    m, g, n, d = obs["machine"], obs["grille"], obs["nommables"], obs["debit"]
    return {
        "module": "accomplissement_313t_mizan.py", "version": VERSION, "auteur": AUTEUR,
        "registre": "EQ-TLU", "capacite_poids": CAPACITE, "constante_c": CONSTANTE_C,
        "echelle": ECHELLE, "radices": list(RADICES), "produit_radices": obs["produit_radices"],
        "dense_bf16_octets": DENSE_BF16_OCTETS, "dense_float64_octets": DENSE_FLOAT64_OCTETS,
        "disque_libre_octets": m["disque_libre_octets"],
        "ram_libre_octets": m["ram"]["libre_octets"],
        "marge_dense_sur_disque": round(m["marge_bf16_sur_disque"], 1),
        "slots_tenants_en_ram": m["slots_tenants_en_ram"],
        "marge_ram": round(m["marge_ram"], 1) if m["marge_ram"] else None,
        "debit_retenu_par_seconde": round(d["debit_retenu"], 1),
        "temps_enumere_annees": round(d["temps_enumere_annees"], 2),
        "adresses_nommables": n["nommables"], "ratio_nommables": str(n["ratio_exact"]),
        "grille_ancee": g["taille_denomeree"] if g else None,
        "occupation_ancee": str(g["occupation"]) if g else None,
        "racine_grille": g["racine_merkle"] if g else None,
        "racine_grille_reproduite": g["racine_reproduite"] if g else None,
        "accompli": {"volume": False, "structure": True, "fonction": True},
        "module_socle": "reseau_poids_sparse_mizan.py",
        "plafond_materialises_socle": socle.PLAFOND_MATERIALISES,
        "statuts_equations": rapport["compte"], "racine_verdicts": rapport["racine"],
        "duree_observation_seconde": obs["duree_observation"],
    }


def controler(echantillons: int = DESSINS_LOI, avec_grille: bool = True) -> Dict[str, object]:
    obs = observer(loom=echantillons, avec_grille=avec_grille)
    rapport = evaluer(obs)
    rapport["cadre"] = cadre_de(obs, rapport)
    return rapport


# ────────────────────────────────────────────────────────────────────────────
# 7. Banc de mutations : un contrôle qui ne rouge jamais ne contrôle rien
# ────────────────────────────────────────────────────────────────────────────

MUTATIONS: Dict[str, str] = {
    "EQ-TLU-01": "radix_faussee",
    "EQ-TLU-02": "retour_tronque",
    "EQ-TLU-03": "mesure_gonflee",
    "EQ-TLU-04": "loi_platee",
    "EQ-TLU-05": "nommables_surlevalues",
    "EQ-TLU-06": "dense_divise_par_dix",
    "EQ-TLU-07": "debit_invente",
    "EQ-TLU-08": "grille_comptee_faussee",
    "EQ-TLU-09": "volume_declare_accompli",
}


def verifier_mutations(obs: Optional[Dict[str, object]] = None) -> Dict[str, object]:
    obs = obs or observer()
    resultats = {}
    for identifiant, mut in MUTATIONS.items():
        normal = CONTROLES[identifiant](obs, None)[0]
        mute = CONTROLES[identifiant](obs, mut)[0]
        resultats[identifiant] = {"normal": normal, "mute": mute,
                                  "capte": normal == "PASS" and mute != "PASS"}
    # Le drapeau « rejouee » doit vouloir dire quelque chose : la racine des verdicts est
    # recalculée ici par une seconde route (le banc itère MUTATIONS et appelle CONTROLES,
    # là où `evaluer` itère EQUATIONS et formatte les tuples complets). Si le banc omettait
    # une équation, en doublait une ou lisait un verdict différent, la racine divergerait.
    # Ce n'est pas une seconde exécution du module : c'est une seconde dérivation, sur la
    # même observation, des mêmes verdicts.
    racine_banc = hashlib.sha256(
        "\n".join(f"{k}|{v['normal']}" for k, v in resultats.items()).encode("utf-8")).hexdigest()
    return {"par_equation": resultats,
            "captees": sum(1 for v in resultats.values() if v["capte"]),
            "testees": len(resultats),
            "racine_verdicts_du_banc": racine_banc,
            "observation_rejouee": racine_banc == evaluer(obs)["racine"]}


# ────────────────────────────────────────────────────────────────────────────
# 8. Certificat
# ────────────────────────────────────────────────────────────────────────────

DOSSIER_CERTIFICAT = RACINE / "resultats" / "accomplissement_313t"


def ecrire_certificat(repertoire: Optional[Path] = None,
                      echantillons: int = DESSINS_LOI) -> Dict[str, object]:
    """Le certificat porte les mesures ; la racine ne couvre que les verdicts EQ-TLU.

    Aucun horodatage n'entre dans la racine : le document change d'heure sans que le
    digest des verdicts bouge, et la racine du registre ne dépend pas de ce fichier.
    """
    repertoire = Path(repertoire or DOSSIER_CERTIFICAT)
    repertoire.mkdir(parents=True, exist_ok=True)
    rapport = controler(echantillons=echantillons)
    mutations = verifier_mutations()
    document = {
        "version": 1, "registre": "EQ-TLU", "module": "accomplissement_313t_mizan.py",
        "horodatage_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "cadre": rapport["cadre"], "equations": rapport["equations"],
        "compte": rapport["compte"], "racine_verdicts": rapport["racine"],
        "limites": limites(), "mutations": mutations,
        "recette": "py -3 -B accomplissement_313t_mizan.py --controler --json",
        "racine_hors_certificat": True,
    }
    chemin = repertoire / "certificat.json"
    chemin.write_text(json.dumps(document, ensure_ascii=False, indent=2, default=str) + "\n",
                      encoding="utf-8", newline="\n")
    octets = chemin.read_bytes()
    return {"chemin": str(chemin), "octets": len(octets),
            "sha256": hashlib.sha256(octets).hexdigest(),
            "racine_verdicts": rapport["racine"], "compte": rapport["compte"],
            "captees": mutations["captees"], "testees": mutations["testees"]}


# ────────────────────────────────────────────────────────────────────────────
# 9. CLI
# ────────────────────────────────────────────────────────────────────────────

def _affiche(objet: object) -> None:
    print(json.dumps(objet, ensure_ascii=False, indent=2, default=str))


def main(argv: Sequence[str]) -> int:
    if "--nommer" in argv:
        i = int(argv[argv.index("--nommer") + 1])
        _affiche({"adresse": i, "nom": list(nommer(i)), "route_python": list(nommer_par_str(i)),
                  "nom_canonique": nom_canonique(nommer(i)).decode("ascii", "replace"),
                  "poids": poids(i), "capacite": CAPACITE})
        return 0
    if "--poids" in argv:
        i = int(argv[argv.index("--poids") + 1])
        _affiche({"adresse": i, "poids": poids(i), "grille": i % PAS_GRILLE == 0})
        return 0
    if "--mutations" in argv:
        r = verifier_mutations()
        _affiche(r)
        return 0 if r["captees"] == r["testees"] else 1
    if "--certificat" in argv:
        r = ecrire_certificat()
        _affiche(r)
        return 0 if (r["compte"]["FAIL"] == 0 and r["compte"]["INCONCLUSIF"] == 0
                     and r["captees"] == r["testees"]) else 1
    echantillons = DESSINS_LOI
    if "--echantillons" in argv:
        echantillons = int(argv[argv.index("--echantillons") + 1])
    if "--controler" in argv:
        rapport = controler(echantillons=echantillons, avec_grille="--sans-grille" not in argv)
        if "--json" in argv:
            _affiche(rapport)
        else:
            c = rapport["cadre"]
            print(f"{c['capacite_poids']:,} poids adressables ".replace(",", " ")
                  + f"| {c['grille_ancee']:,} ancres matérialisées ".replace(",", " ")
                  + f"| occupation {c['occupation_ancee']}")
            for eq in rapport["equations"]:
                print(f"{eq['statut']:<12} {eq['id']} {eq['titre']}")
            print("compte :", rapport["compte"], "racine :", rapport["racine"][:16])
        return 0 if rapport["compte"]["FAIL"] == 0 and rapport["compte"]["INCONCLUSIF"] == 0 else 1
    _affiche({"module": "accomplissement_313t_mizan.py", "version": VERSION, "auteur": AUTEUR,
              "registre": "EQ-TLU", "capacite_poids": CAPACITE, "radices": list(RADICES),
              "dense_bf16_octets": DENSE_BF16_OCTETS,
              "sens_accomplis": {"volume": "non — hors de portée mesurée",
                                 "structure": "oui — partition vérifiée",
                                 "fonction": "oui — loi totale sans stockage"},
              "usage": ["--controler [--echantillons N] [--sans-grille] [--json]",
                        "--nommer 312999999999999", "--poids 0", "--mutations", "--certificat"]})
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
