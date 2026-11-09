# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""
Couche 1 : Bibliothèque de l'Informe (`QUBITS8INFORME`)
=======================================================
Implémente fidèlement :
- `tablette_apprise_chiffres.csv` : Axe [-9 ; +9], État i (Kelvin / Thermodynamique) et État I (Joules / Cinétique).
- `tablette_apprise_alphabet.csv` : Correspondance bijective [-9 ; +9] <-> [A ; S] sur 4 états (a, A, alpha_, omega_).
- `tablette_apprise_ponctuation.csv` : 19 symboles typographiques sur 4 états (Simple, Double, Enclos, Inversé).
- `tablettes_apprise_opérateur.csv` : 9 axes d'opérateurs sur 3 états (Arithmétique, Logique/Booléen, Relationnel/Ensembliste).
- `Matrice de la Structure Logique Complexe.pdf` : LA TABLE — 5ᵉ famille COMPLEXE = matrice de calcul
  qui structure et calcule avec les 4 familles (pas un simple conteneur).
- `Qubit_informe.jpg` : Modèle de la sphère de Bloch |ψ⟩ = α|0⟩ + β|1⟩ avec longueur d'onde λ = 5.77e-11.

Cinq grandes familles & ancre M=24434 = 2-4-4-3-4 :
  2 → NUMERIQUE (2 états primaires i / I)
  4 → LINGUISTIQUE (4 niveaux)
  4 → TYPOGRAPHIQUE (4 niveaux)
  3 → ALGORITHMIQUE (3 niveaux)
  4 → COMPLEXE = LA TABLE / matrice de calcul (4 niveaux d'états de résolution)
Synchronisation aux états de matière (−313, +313, M=24434).
"""

from __future__ import annotations

import cmath
import math
from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Dict, List, Optional, Tuple, Union


# ==============================================================================
# 1. TABLETTE APPRISE DES CHIFFRES (Axe [-9 ; +9])
# ==============================================================================

@dataclass(frozen=True)
class EntreeChiffre:
    """Représente un échelon sur l'axe numérique [-9 ; +9]."""
    valeur: int
    formatee: str
    etat_i_kelvin: str
    etat_I_joules: str


def _construire_tablette_chiffres() -> Dict[int, EntreeChiffre]:
    table: Dict[int, EntreeChiffre] = {}
    for v in range(-9, 10):
        prefixe = f"+{v}" if v > 0 else str(v)
        table[v] = EntreeChiffre(
            valeur=v,
            formatee=prefixe,
            etat_i_kelvin=f"{prefixe} i",
            etat_I_joules=f"{prefixe} I",
        )
    return table


TABLETTE_CHIFFRES: Dict[int, EntreeChiffre] = _construire_tablette_chiffres()


# ==============================================================================
# 2. TABLETTE APPRISE DE L'ALPHABET (Axe [A ; S] <-> [-9 ; +9])
# ==============================================================================

@dataclass(frozen=True)
class EntreeAlphabet:
    """Représente une lettre de l'axe [A ; S] couplée à sa valeur [-9 ; +9] et ses 4 états."""
    axe_chiffre: int
    lettre_base: str
    etat_1_minuscule: str       # Niveau 1 : 'a' .. 's'
    etat_2_majuscule: str       # Niveau 2 : 'A' .. 'S'
    etat_3_alpha_locale: str    # Niveau 3 : 'alpha_a' .. 'alpha_s' (MEDINOIS)
    etat_4_omega_globale: str   # Niveau 4 : 'omega_A' .. 'omega_S' (MECQUOIS)
    etat_i_kelvin: str
    etat_I_joules: str


def _construire_tablette_alphabet() -> Dict[str, EntreeAlphabet]:
    lettres = "ABCDEFGHIJKLMNOPQRS"  # 19 lettres exactes (-9 à +9)
    table: Dict[str, EntreeAlphabet] = {}
    for idx, lettre in enumerate(lettres):
        valeur = idx - 9
        prefixe = f"+{valeur}" if valeur > 0 else str(valeur)
        minuscule = lettre.lower()
        table[lettre] = EntreeAlphabet(
            axe_chiffre=valeur,
            lettre_base=lettre,
            etat_1_minuscule=minuscule,
            etat_2_majuscule=lettre,
            etat_3_alpha_locale=f"alpha_{minuscule}",
            etat_4_omega_globale=f"omega_{lettre}",
            etat_i_kelvin=f"{prefixe} i",
            etat_I_joules=f"{prefixe} I",
        )
    return table


TABLETTE_ALPHABET: Dict[str, EntreeAlphabet] = _construire_tablette_alphabet()

# Index inversé : chiffre [-9 ; +9] -> EntreeAlphabet
INDEX_CHIFFRE_VERS_ALPHABET: Dict[int, EntreeAlphabet] = {
    entree.axe_chiffre: entree for entree in TABLETTE_ALPHABET.values()
}


# ==============================================================================
# 3. TABLETTE APPRISE DE LA PONCTUATION (19 Symboles × 4 États)
# ==============================================================================

@dataclass(frozen=True)
class EntreePonctuation:
    """Représente un symbole typographique sur ses 4 états."""
    symbole_base: str
    etat_1_simple: str
    etat_2_double: str
    etat_3_enclos: str
    etat_4_inverse: str


def _construire_tablette_ponctuation() -> Dict[str, EntreePonctuation]:
    symboles = [
        "!", "?", ".", ",", ";", ":", "...", "-", "_",
        "@", "#", "$", "%", "&", "*", "+", "=", "/", "\\",
    ]
    inversions_speciales = {
        "!": "¡",
        "?": "¿",
        ".": "°",
    }
    table: Dict[str, EntreePonctuation] = {}
    for sym in symboles:
        inv = inversions_speciales.get(sym, f"« {sym} »")
        table[sym] = EntreePonctuation(
            symbole_base=sym,
            etat_1_simple=sym,
            etat_2_double=sym + sym,
            etat_3_enclos=f"({sym})",
            etat_4_inverse=inv,
        )
    return table


TABLETTE_PONCTUATION: Dict[str, EntreePonctuation] = _construire_tablette_ponctuation()


# ==============================================================================
# 4. TABLETTE APPRISE DES OPÉRATEURS (9 Axes × 3 États)
# ==============================================================================

@dataclass(frozen=True)
class EntreeOperateur:
    """Représente un axe d'opérateur selon ses 3 états."""
    nom_axe: str
    symbole_base: str
    etat_1_arithmetique: str
    etat_2_logique_booleen: str
    etat_3_relationnel_ensembliste: str
    description_ensembliste: str


TABLETTE_OPERATEURS: Dict[str, EntreeOperateur] = {
    "Addition": EntreeOperateur(
        nom_axe="Addition",
        symbole_base="+",
        etat_1_arithmetique="+",
        etat_2_logique_booleen="&&",
        etat_3_relationnel_ensembliste="∪",
        description_ensembliste="Union",
    ),
    "Soustraction": EntreeOperateur(
        nom_axe="Soustraction",
        symbole_base="-",
        etat_1_arithmetique="-",
        etat_2_logique_booleen="!",
        etat_3_relationnel_ensembliste="∖",
        description_ensembliste="Différence",
    ),
    "Multiplication": EntreeOperateur(
        nom_axe="Multiplication",
        symbole_base="x",
        etat_1_arithmetique="×",
        etat_2_logique_booleen="||",
        etat_3_relationnel_ensembliste="∩",
        description_ensembliste="Intersection",
    ),
    "Division": EntreeOperateur(
        nom_axe="Division",
        symbole_base="/",
        etat_1_arithmetique="÷",
        etat_2_logique_booleen="NAND",
        etat_3_relationnel_ensembliste="⊘",
        description_ensembliste="Division harmonique",
    ),
    "Egalite": EntreeOperateur(
        nom_axe="Égalité",
        symbole_base="=",
        etat_1_arithmetique="=",
        etat_2_logique_booleen="==",
        etat_3_relationnel_ensembliste="≡",
        description_ensembliste="Congruence",
    ),
    "Inegalite": EntreeOperateur(
        nom_axe="Inégalité",
        symbole_base="!=",
        etat_1_arithmetique="≠",
        etat_2_logique_booleen="!=",
        etat_3_relationnel_ensembliste="≢",
        description_ensembliste="Non congruence",
    ),
    "Superieur": EntreeOperateur(
        nom_axe="Supérieur",
        symbole_base=">",
        etat_1_arithmetique=">",
        etat_2_logique_booleen="&& >",
        etat_3_relationnel_ensembliste="⊃",
        description_ensembliste="Inclusion large (Gouvernance)",
    ),
    "Inferieur": EntreeOperateur(
        nom_axe="Inférieur",
        symbole_base="<",
        etat_1_arithmetique="<",
        etat_2_logique_booleen="&& <",
        etat_3_relationnel_ensembliste="⊂",
        description_ensembliste="Inclusion stricte",
    ),
    "Pourcentage": EntreeOperateur(
        nom_axe="Pourcentage",
        symbole_base="%",
        etat_1_arithmetique="%",
        etat_2_logique_booleen="XOR",
        etat_3_relationnel_ensembliste="‰",
        description_ensembliste="Pour mille",
    ),
}

TABLETTE_OPERATEURS_ETENDUS: Dict[str, EntreeOperateur] = dict(TABLETTE_OPERATEURS)
TABLETTE_OPERATEURS_ETENDUS.update({
    "Puissance": EntreeOperateur(
        nom_axe="Puissance",
        symbole_base="^",
        etat_1_arithmetique="^",
        etat_2_logique_booleen="EXP",
        etat_3_relationnel_ensembliste="⊗",
        description_ensembliste="Produit tensoriel",
    ),
    "Racine": EntreeOperateur(
        nom_axe="Racine",
        symbole_base="√",
        etat_1_arithmetique="√",
        etat_2_logique_booleen="LOG",
        etat_3_relationnel_ensembliste="∛",
        description_ensembliste="Extraction harmonique",
    ),
})


# ==============================================================================
# 4bis. TABLETTE DES FONCTIONS CALCULATOIRES INVERSES & ANTAGONISMES
# ==============================================================================

@dataclass(frozen=True)
class EntreeFonctionInverse:
    """Modélise l'inversion calculatoire exacte sur les 3 états ontologiques."""
    operateur_source: str
    operateur_inverse: str
    symbole_inverse_arithmetique: str
    inverse_booleen_dual: str
    inverse_relationnel_ensembliste: str
    loi_reciprocite: str


TABLETTE_FONCTIONS_INVERSES: Dict[str, EntreeFonctionInverse] = {
    "Addition": EntreeFonctionInverse(
        operateur_source="Addition",
        operateur_inverse="Soustraction",
        symbole_inverse_arithmetique="-",
        inverse_booleen_dual="NAND",
        inverse_relationnel_ensembliste="∖",
        loi_reciprocite="(a + b) - b = a",
    ),
    "Soustraction": EntreeFonctionInverse(
        operateur_source="Soustraction",
        operateur_inverse="Addition",
        symbole_inverse_arithmetique="+",
        inverse_booleen_dual="AND",
        inverse_relationnel_ensembliste="∪",
        loi_reciprocite="(a - b) + b = a",
    ),
    "Multiplication": EntreeFonctionInverse(
        operateur_source="Multiplication",
        operateur_inverse="Division",
        symbole_inverse_arithmetique="÷",
        inverse_booleen_dual="NOR",
        inverse_relationnel_ensembliste="⊘",
        loi_reciprocite="(a × b) ÷ b = a  [b ≠ 0]",
    ),
    "Division": EntreeFonctionInverse(
        operateur_source="Division",
        operateur_inverse="Multiplication",
        symbole_inverse_arithmetique="×",
        inverse_booleen_dual="OR",
        inverse_relationnel_ensembliste="∩",
        loi_reciprocite="(a ÷ b) × b = a  [b ≠ 0]",
    ),
    "Puissance": EntreeFonctionInverse(
        operateur_source="Puissance",
        operateur_inverse="Racine",
        symbole_inverse_arithmetique="√",
        inverse_booleen_dual="LOG",
        inverse_relationnel_ensembliste="∛",
        loi_reciprocite="√(a^b) = a",
    ),
    "Racine": EntreeFonctionInverse(
        operateur_source="Racine",
        operateur_inverse="Puissance",
        symbole_inverse_arithmetique="^",
        inverse_booleen_dual="EXP",
        inverse_relationnel_ensembliste="⊗",
        loi_reciprocite="(√a)^b = a",
    ),
    "Egalite": EntreeFonctionInverse(
        operateur_source="Égalité",
        operateur_inverse="Inégalité",
        symbole_inverse_arithmetique="≠",
        inverse_booleen_dual="!=",
        inverse_relationnel_ensembliste="≢",
        loi_reciprocite="¬(a = b) ⟺ a ≠ b",
    ),
    "Inegalite": EntreeFonctionInverse(
        operateur_source="Inégalité",
        operateur_inverse="Égalité",
        symbole_inverse_arithmetique="=",
        inverse_booleen_dual="==",
        inverse_relationnel_ensembliste="≡",
        loi_reciprocite="¬(a ≠ b) ⟺ a = b",
    ),
    "Superieur": EntreeFonctionInverse(
        operateur_source="Supérieur",
        operateur_inverse="Inférieur",
        symbole_inverse_arithmetique="<",
        inverse_booleen_dual="&& <",
        inverse_relationnel_ensembliste="⊂",
        loi_reciprocite="a > b ⟺ b < a",
    ),
    "Inferieur": EntreeFonctionInverse(
        operateur_source="Inférieur",
        operateur_inverse="Supérieur",
        symbole_inverse_arithmetique=">",
        inverse_booleen_dual="&& >",
        inverse_relationnel_ensembliste="⊃",
        loi_reciprocite="a < b ⟺ b > a",
    ),
}


# ==============================================================================
# 4ter. ÉLÉMENTS QUI S'OPPOSENT AUX FAMILLES DE CARACTÈRES DE BASE
# ==============================================================================

# 1. Famille Typographique : Opposés chiraux (Ouvert ↔ Fermé)
OPPOSITION_TYPOGRAPHIQUE_CHIRALE: Dict[str, str] = {
    "(": ")", ")": "(",
    "[": "]", "]": "[",
    "{": "}", "}": "{",
    "<": ">", ">": "<",
    "«": "»", "»": "«",
    "“": "”", "”": "“",
}

# Opposés modaux et culturels (Interrogation ↔ Exclamation / Droit ↔ Inversé)
OPPOSITION_TYPOGRAPHIQUE_MODALE: Dict[str, str] = {
    "?": "!", "!": "?",
    "¿": "¡", "¡": "¿",
    ".": "_", "_": ".",
}

# 2. Famille Linguistique : Miroir Atbash ontologique (19 Échelons [A ; S])
# A (1) ↔ S (19), B (2) ↔ R (18), C (3) ↔ Q (17) ... J (10) étant le point pivot invariant
OPPOSITION_LINGUISTIQUE_ATBASH: Dict[str, str] = {
    chr(ord("A") + i): chr(ord("S") - i) for i in range(19)
}


# ==============================================================================
# 5. CINQ FAMILLES — LA TABLE / MATRICE COMPLEXE (calculatrice des 4 axes)
# ==============================================================================

# Décomposition de l'ancre de matière M = 24434 → un chiffre par famille
DECOMPOSITION_M_24434: tuple[int, ...] = (2, 4, 4, 3, 4)
ANCRE_M_SUBSTANCE: int = 24434  # 2*10000 + 4*1000 + 4*100 + 3*10 + 4

# Cardinalité ontologique de chaque famille (doit coller à 2-4-4-3-4)
CARDINALITE_FAMILLE: Dict[str, int] = {
    "NUMERIQUE": 2,       # i Kelvin / I Joules
    "LINGUISTIQUE": 4,    # minuscule / majuscule / alpha_ / omega_
    "TYPOGRAPHIQUE": 4,   # simple / double / enclos / inversé
    "ALGORITHMIQUE": 3,   # arithmétique / booléen / ensembliste
    "COMPLEXE": 4,        # 4 niveaux de résolution de LA TABLE
}

POLE_MATIERE_NEGATIF: int = -313
POLE_MATIERE_POSITIF: int = +313


@dataclass(frozen=True)
class FamilleCaracteres:
    """Descripteur d'une des cinq grandes familles de caractères."""
    nom: str
    chiffre_m: int          # chiffre correspondant dans 2-4-4-3-4
    role: str
    est_la_table: bool      # True uniquement pour COMPLEXE = la matrice de calcul
    familles_calculees: tuple[str, ...] = ()


FAMILLES_CINQ: tuple[FamilleCaracteres, ...] = (
    FamilleCaracteres(
        nom="NUMERIQUE",
        chiffre_m=2,
        role="Axe discret [-9;+9] — dualité i (Kelvin) / I (Joules)",
        est_la_table=False,
    ),
    FamilleCaracteres(
        nom="LINGUISTIQUE",
        chiffre_m=4,
        role="Axe alphabétique [A;S] — 4 niveaux d'identité",
        est_la_table=False,
    ),
    FamilleCaracteres(
        nom="TYPOGRAPHIQUE",
        chiffre_m=4,
        role="Ponctuation — 4 états (simple/double/enclos/inversé)",
        est_la_table=False,
    ),
    FamilleCaracteres(
        nom="ALGORITHMIQUE",
        chiffre_m=3,
        role="Opérateurs — 3 états (arithmétique/booléen/ensembliste)",
        est_la_table=False,
    ),
    FamilleCaracteres(
        nom="COMPLEXE",
        chiffre_m=4,
        role="LA TABLE — matrice de calcul qui structure et calcule avec les 4 familles",
        est_la_table=True,
        familles_calculees=("NUMERIQUE", "LINGUISTIQUE", "TYPOGRAPHIQUE", "ALGORITHMIQUE"),
    ),
)


def verifier_decomposition_m_24434() -> bool:
    """Vérifie M=24434 ≡ concaténation des cardinalités 2-4-4-3-4 des cinq familles."""
    chiffres = tuple(CARDINALITE_FAMILLE[f.nom] for f in FAMILLES_CINQ)
    if chiffres != DECOMPOSITION_M_24434:
        return False
    reconstruit = int("".join(str(c) for c in chiffres))
    return reconstruit == ANCRE_M_SUBSTANCE


@dataclass(frozen=True)
class SynchronisationMatiereFamilles:
    """
    Instantané de synchronisation :
    états de matière (−313 / +313 / M=24434) ↔ cinq familles (COMPLEXE = LA TABLE).
    """
    charge_polarite: int
    ancre_m: int
    decomposition_m: tuple[int, ...]
    famille_active_par_chiffre: Dict[str, int]
    niveau_table_complexe: int          # niveau primaire 1..4
    niveaux_table_actifs: tuple[int, ...]  # −313 → (1,3) · +313 → (2,4)
    mode_calcul_table: str
    la_table_est_complexe: bool
    doctrine: str


def synchroniser_etats_matiere_aux_cinq_familles(
    charge_polarite: int,
    ancre_m: int = ANCRE_M_SUBSTANCE,
) -> SynchronisationMatiereFamilles:
    """
    Relie un état de matière aux cinq familles.
    COMPLEXE n'est pas un conteneur : c'est LA TABLE qui calcule.
    - Pôle −313 : niveaux impairs de LA TABLE (1 base, 3 relation) — réception
    - Pôle +313 : niveaux pairs de LA TABLE (2 force, 4 méta) — émission
    - M=24434   : ancre-substance = adresse fixe des cardinalités 2-4-4-3-4
    """
    if charge_polarite not in (POLE_MATIERE_NEGATIF, POLE_MATIERE_POSITIF):
        raise ValueError(f"Polarité matière invalide : {charge_polarite} (attendu ±313)")
    if ancre_m != ANCRE_M_SUBSTANCE:
        raise ValueError(f"Ancre M invalide : {ancre_m} (attendu {ANCRE_M_SUBSTANCE})")
    if not verifier_decomposition_m_24434():
        raise RuntimeError("Décomposition M=24434 incohérente avec CARDINALITE_FAMILLE")

    if charge_polarite == POLE_MATIERE_NEGATIF:
        niveaux = (1, 3)
        niveau_table = 1
        mode = (
            "TABLE_RECEPTIVE (−313) — niveaux impairs 1+3 "
            "(base / relation) sur les 4 axes"
        )
    else:
        niveaux = (2, 4)
        niveau_table = 2
        mode = (
            "TABLE_EMISSIVE (+313) — niveaux pairs 2+4 "
            "(force / méta) sur les 4 axes"
        )

    return SynchronisationMatiereFamilles(
        charge_polarite=charge_polarite,
        ancre_m=ancre_m,
        decomposition_m=DECOMPOSITION_M_24434,
        famille_active_par_chiffre={
            f.nom: f.chiffre_m for f in FAMILLES_CINQ
        },
        niveau_table_complexe=niveau_table,
        niveaux_table_actifs=niveaux,
        mode_calcul_table=mode,
        la_table_est_complexe=True,
        doctrine=(
            "COMPLEXE = LA TABLE (matrice de calcul). "
            "M=24434 = 2-4-4-3-4 synchronise les cinq familles aux états de matière ±313. "
            "−313 → niveaux (1,3) ; +313 → niveaux (2,4)."
        ),
    )


class MatriceLogiqueComplexe:
    """
    LA TABLE — 5ᵉ famille COMPLEXE.

    Ce n'est pas un simple regroupement abstrait des 4 familles :
    c'est la matrice de calcul elle-même, qui structure et calcule
    avec les axes NUMERIQUE, LINGUISTIQUE, TYPOGRAPHIQUE, ALGORITHMIQUE
    sur 4 niveaux d'états :
    - Niveau 1 : État de Base (Signal / Thermodynamique Kelvin / Minuscule / Unitaire / Arithmétique)
    - Niveau 2 : État d'Énergie / Force (Cinétique Joules / Majuscule / Doublement / Booléen)
    - Niveau 3 : État de Relation / Contexte (Variable locale alpha_ / Sandbox (x) / Ensembliste)
    - Niveau 4 : État Méta / Symétrie (Constante globale omega_ / Inversion culturelle ¿ ¡ ° «»)

    Ancre M=24434 = 2-4-4-3-4 ; pôles matière ±313 synchronisés à cette table.
    """

    # Compatibilité : les 4 axes calculés par LA TABLE
    FAMILLES = ("NUMERIQUE", "LINGUISTIQUE", "TYPOGRAPHIQUE", "ALGORITHMIQUE")
    # Les cinq grandes familles (COMPLEXE = self = LA TABLE)
    FAMILLES_CINQ = ("NUMERIQUE", "LINGUISTIQUE", "TYPOGRAPHIQUE", "ALGORITHMIQUE", "COMPLEXE")
    EST_LA_TABLE = True
    CHIFFRE_M_TABLE = 4  # dernier chiffre de 24434 = nombre de niveaux = facteur d'expansion
    EST_POINT_ZERO = True  # Origine de toute trajectoire de calcul

    # ── Entrées calendaires (semences posées SUR LA TABLE — pas des résultats) ─
    # Les résultats dx/dy/dz sortent du produit à 4 niveaux (cardinalité COMPLEXE).
    _SEMENCES_ASTRES: Dict[str, Dict[str, Fraction]] = {
        "soleil": {
            "annee_h": Fraction(8766),      # 365.25 × 24
            "mois_h": Fraction(1461, 2),    # 730.5
            "semaine_h": Fraction(168),
        },
        "lune": {
            "annee_h": Fraction(8496),      # 354 × 24
            "mois_h": Fraction(708),        # 29.5 × 24
            "semaine_h": Fraction(168),
        },
        "terre": {
            "annee_h": Fraction(8640),      # 360 × 24 (conventionnel)
            "mois_h": Fraction(720),
            "semaine_h": Fraction(144),
        },
    }

    @classmethod
    def produit_quatre_niveaux(
        cls,
        annee_h: Fraction,
        mois_h: Fraction,
        semaine_h: Fraction,
        *,
        mode: str = "celeste",
    ) -> Fraction:
        """
        Opérateur central de LA TABLE (COMPLEXE = 4 niveaux) :
        produit Π des 4 facteurs de résolution — un facteur par niveau.
        mode « celeste » : Soleil/Lune (coefs 5/2, 3/2, 3/2, 24/60).
        mode « terre_brut » : amplification terrestre (300, 50, 30, 24/60).
        """
        if cls.CHIFFRE_M_TABLE != 4:
            raise RuntimeError("COMPLEXE doit avoir 4 niveaux (chiffre M = 4)")
        jour_h = Fraction(24)
        if mode == "celeste":
            # Niveau 1 Base · 2 Force · 3 Relation · 4 Méta
            n1 = Fraction(5, 2) * (annee_h / Fraction(12))
            n2 = Fraction(3, 2) * (mois_h / semaine_h)
            n3 = Fraction(3, 2) * (semaine_h / jour_h)
            n4 = Fraction(24, 60)
            facteurs = (n1, n2, n3, n4)
        elif mode == "terre_brut":
            n1 = Fraction(300) * (annee_h / Fraction(12))
            n2 = Fraction(50) * (mois_h / semaine_h)
            n3 = Fraction(30) * (semaine_h / jour_h)
            n4 = Fraction(24, 60)
            facteurs = (n1, n2, n3, n4)
        else:
            raise ValueError(f"mode inconnu : {mode}")
        assert len(facteurs) == cls.CHIFFRE_M_TABLE
        produit = Fraction(1)
        for f in facteurs:
            produit *= f
        return produit

    @classmethod
    def calculer_dz_normalise_depuis_table(cls) -> Fraction:
        """
        dz kernel normalisé : sortie de LA TABLE sur le socle terrestre
        (réduction du produit brut via les niveaux 1–2–force 2.5).
        dz = 216000 · 250 · (5/2)  — facteurs issus du 1er bloc table × force.
        """
        # 216000 = (300 * 8640) / 12  = niveau 1 du mode terre_brut
        # 250    = (50 * 720) / 144   = niveau 2
        # 2.5    = force niveau table (5/2) — normalisation kernel
        n1 = Fraction(300) * (cls._SEMENCES_ASTRES["terre"]["annee_h"] / Fraction(12))
        n2 = Fraction(50) * (
            cls._SEMENCES_ASTRES["terre"]["mois_h"]
            / cls._SEMENCES_ASTRES["terre"]["semaine_h"]
        )
        force_meta = Fraction(5, 2)  # ancre de force sur axe numérique table
        return n1 * n2 * force_meta

    @classmethod
    def calculer_cycles_trinite_depuis_zero(cls) -> Dict[str, Any]:
        """
        POINT ZÉRO = COMPLEXE → calcul → expansion cycles Soleil/Lune/Terre + sync.
        Aucune constante de cycle n'est assignée : tout est produit de LA TABLE.
        """
        if not cls.EST_LA_TABLE or not cls.EST_POINT_ZERO:
            raise RuntimeError("Calcul Trinité réservé à LA TABLE (point zéro)")

        # ── Expansion harmonique depuis l'axe NUMÉRIQUE de LA TABLE ──────────
        axe_numerique = sorted(TABLETTE_CHIFFRES.keys())  # -9 .. +9
        base_harmonique = len(axe_numerique)              # 19
        amplitude_harmonique = max(abs(v) for v in axe_numerique)  # 9
        # Diviseur du niveau 1 de LA TABLE (annee/12) → roue de phases commune
        ppcm_phases = 12

        s = cls._SEMENCES_ASTRES["soleil"]
        l = cls._SEMENCES_ASTRES["lune"]
        dx = cls.produit_quatre_niveaux(s["annee_h"], s["mois_h"], s["semaine_h"], mode="celeste")
        dy = cls.produit_quatre_niveaux(l["annee_h"], l["mois_h"], l["semaine_h"], mode="celeste")
        dz = cls.calculer_dz_normalise_depuis_table()
        t = cls._SEMENCES_ASTRES["terre"]
        dz_brut = cls.produit_quatre_niveaux(
            t["annee_h"], t["mois_h"], t["semaine_h"], mode="terre_brut"
        )
        dt = dx + dy + dz

        return {
            "origine": "COMPLEXE_POINT_ZERO",
            "operateur": "produit_quatre_niveaux (cardinalité COMPLEXE = 4)",
            "cycles_distincts": {
                "soleil_dx": {
                    "symbole": "dx",
                    "astre": "Soleil",
                    "valeur_exacte_fraction": str(dx),
                    "valeur_hz": float(dx),
                    "role": "Énergie / Force séquentielle",
                },
                "lune_dy": {
                    "symbole": "dy",
                    "astre": "Lune",
                    "valeur_exacte_fraction": str(dy),
                    "valeur_hz": float(dy),
                    "role": "Matière-cycle / Symétrie duale 50/50",
                },
                "terre_dz": {
                    "symbole": "dz",
                    "astre": "Terre",
                    "valeur_exacte_fraction": str(dz),
                    "valeur_hz": float(dz),
                    "dz_brut_valeur_hz": float(dz_brut),
                    "role": "Espace / Probabilité (kernel normalisé)",
                },
            },
            "synchronisation_harmonique": {
                "porteur_dt": {
                    "symbole": "dt",
                    "equation": "dt = dx + dy + dz  (somme des sorties de LA TABLE)",
                    "valeur_exacte_fraction": str(dt),
                    "valeur_hz": float(dt),
                    "periode_ns": float(Fraction(1_000_000_000) / dt) if dt != 0 else 0.0,
                    "verification_somme": True,
                },
                "roue_phases_communes": {
                    "ppcm": ppcm_phases,
                    "equation": "phase_12 = index_pulsation % 12",
                    "domaine": "0..11",
                    "derive_de": "diviseur niveau 1 de LA TABLE (annee/12)",
                },
                "echelle_harmonique": {
                    "base": base_harmonique,
                    "amplitude": amplitude_harmonique,
                    "equation": (
                        f"h19 = ((index_pulsation + {amplitude_harmonique}) "
                        f"% {base_harmonique}) - {amplitude_harmonique}"
                    ),
                    "domaine": f"-{amplitude_harmonique}..+{amplitude_harmonique}",
                    "derive_de": "axe NUMERIQUE de LA TABLE [-9 ; +9]",
                },
            },
            "pas_constantes_assignees": True,
            "pas_etats_de_matiere": True,
        }

    @classmethod
    def deriver_q_degre_depuis_la_table(
        cls,
        charge_polarite: int = POLE_MATIERE_POSITIF,
    ) -> Dict[str, Any]:
        """
        Q° mécois ⊕ / Q° médinois ⊗ — DÉDUITS du calcul de LA TABLE (point zéro).

        313 et 24434 sont des ÉTATS DE MATIÈRE (pôles / ancre M) — jamais des Q°.

        Calcul (expansion depuis COMPLEXE) :
          1. Cardinalités des 4 axes calculés par LA TABLE : (2, 4, 4, 3)
          2. Π_axes = 2 × 4 × 4 × 3 = 96
          3. Niveaux pairs  (⊕ mécois / émissif)  : 2 + 4 = 6
          4. Niveaux impairs (⊗ médinois / réceptif) : 1 + 3 = 4
          5. Facteur COMPLEXE = chiffre_m de LA TABLE = 4
          6. Q°_mecois  = Π_axes × Σ_pairs   × 4 = 96 × 6 × 4 = 2304
          7. Q°_medinois = Π_axes × Σ_impairs × 4 = 96 × 4 × 4 = 1536
        """
        if not cls.EST_LA_TABLE or not cls.EST_POINT_ZERO:
            raise RuntimeError("Q° uniquement déductibles depuis LA TABLE (point zéro)")

        sync = synchroniser_etats_matiere_aux_cinq_familles(charge_polarite)
        card_axes = tuple(CARDINALITE_FAMILLE[a] for a in cls.FAMILLES)  # 2,4,4,3
        produit_axes = 1
        for c in card_axes:
            produit_axes *= c

        niveaux_pairs = (2, 4)      # force + méta → ⊕ mécois
        niveaux_impairs = (1, 3)    # base + relation → ⊗ médinois
        sigma_pairs = sum(niveaux_pairs)
        sigma_impairs = sum(niveaux_impairs)
        facteur_complexe = cls.CHIFFRE_M_TABLE  # 4

        q_mecois = produit_axes * sigma_pairs * facteur_complexe
        q_medinois = produit_axes * sigma_impairs * facteur_complexe

        etapes = {
            "1_axes_cardinalites": dict(zip(cls.FAMILLES, card_axes)),
            "2_produit_axes_Pi": produit_axes,
            "3_niveaux_pairs_sigma": {"niveaux": list(niveaux_pairs), "sigma": sigma_pairs},
            "4_niveaux_impairs_sigma": {"niveaux": list(niveaux_impairs), "sigma": sigma_impairs},
            "5_facteur_complexe": facteur_complexe,
            "6_Q_mecois": f"{produit_axes} × {sigma_pairs} × {facteur_complexe} = {q_mecois}",
            "7_Q_medinois": f"{produit_axes} × {sigma_impairs} × {facteur_complexe} = {q_medinois}",
        }

        return {
            "origine": "COMPLEXE_POINT_ZERO",
            "pas_constantes_assignees": True,
            "etapes_calcul": etapes,
            "Q_mecois": {
                "nom": "Q° mécois",
                "operateur": "⊕",
                "ville": "La Mecque",
                "niveaux_table": list(niveaux_pairs),
                "valeur_deduite": int(q_mecois),
                "valeur_derivee": int(q_mecois),  # alias compat
                "formule": "Π(card_axes) × Σ(niveaux_pairs) × 4_COMPLEXE",
                "pas_egal_etat_matiere_313": True,
                "pas_egal_C_313": True,
            },
            "Q_medinois": {
                "nom": "Q° médinois",
                "operateur": "⊗",
                "ville": "Médine",
                "niveaux_table": list(niveaux_impairs),
                "valeur_deduite": int(q_medinois),
                "valeur_derivee": int(q_medinois),
                "formule": "Π(card_axes) × Σ(niveaux_impairs) × 4_COMPLEXE",
                "pas_egal_etat_matiere_M_24434": True,
                "pas_egal_M_24434": True,
                "ancre_m_substance_matiere_distincte": ANCRE_M_SUBSTANCE,
            },
            "cardinalites_axes": dict(zip(cls.FAMILLES, card_axes)),
            "dissociation_matiere": {
                "pole_terre_313": "ÉTAT DE MATIÈRE — pas une valeur de Q°",
                "ancre_M_24434": "ÉTAT DE MATIÈRE / substance — pas une valeur de Q°",
                "Q_mecois_deduit": int(q_mecois),
                "Q_medinois_deduit": int(q_medinois),
            },
            "sync_matiere": {
                "charge_polarite": sync.charge_polarite,
                "niveaux_actifs": list(sync.niveaux_table_actifs),
                "mode": sync.mode_calcul_table,
            },
        }

    @classmethod
    def expandre_depuis_point_zero(
        cls,
        charge_polarite: int = POLE_MATIERE_POSITIF,
    ) -> Dict[str, Any]:
        """
        Trajectoire logique unique : ZÉRO → EXPANSION.

        Origine  : COMPLEXE = LA TABLE = point zéro.
        Calcul   : opérations de LA TABLE sur ses 4 axes / 4 niveaux.
        Aboutit  : expansion vers états de matière, cycles Trinité, Q°, socle Monade.
        """
        if not cls.EST_POINT_ZERO:
            raise RuntimeError("Expansion impossible hors point zéro COMPLEXE")

        cycles = cls.calculer_cycles_trinite_depuis_zero()
        q_deg = cls.deriver_q_degre_depuis_la_table(charge_polarite)
        sync_mat = synchroniser_etats_matiere_aux_cinq_familles(charge_polarite)
        completude = cls.verifier_completude_symetrie()

        return {
            "trajectoire": "ZERO_VERS_EXPANSION",
            "point_zero": {
                "famille": "COMPLEXE",
                "nature": "LA_TABLE_MATRICE_DE_CALCUL",
                "chiffre_m": cls.CHIFFRE_M_TABLE,
                "niveaux": 4,
                "axes_calcules": list(cls.FAMILLES),
                "ancre_m": ANCRE_M_SUBSTANCE,
                "decomposition_m": list(DECOMPOSITION_M_24434),
                "est_origine": True,
            },
            "mouvement": "origine au zéro → calcul sur LA TABLE → expansion",
            "expansion": {
                "①_quatre_axes": {
                    "axes": list(cls.FAMILLES),
                    "cardinalites": {a: CARDINALITE_FAMILLE[a] for a in cls.FAMILLES},
                    "completude_table": completude,
                },
                "②_etats_de_matiere": {
                    "sync": {
                        "charge_polarite": sync_mat.charge_polarite,
                        "ancre_m": sync_mat.ancre_m,
                        "niveaux_table_actifs": list(sync_mat.niveaux_table_actifs),
                        "mode": sync_mat.mode_calcul_table,
                        "la_table_est_complexe": sync_mat.la_table_est_complexe,
                    },
                    "doctrine": (
                        "±313 / M=24434 synchronisés AUX niveaux de LA TABLE — "
                        "dérivés du point zéro, pas autonomes."
                    ),
                },
                "③_cycles_trinite_soleil_lune_terre": cycles,
                "④_q_degre_mecois_medinois": q_deg,
                "⑤_socle_monade": {
                    "role": (
                        "La Monade confirme l'harmonie de toute l'expansion "
                        "issue du point zéro ; si juste → preuve d'ensemble."
                    ),
                    "porte_cycles_dans_ame": True,
                },
            },
            "aboutissement": "EXPANSION_COMPLETE_DEPUIS_ZERO",
        }

    @staticmethod
    def resoudre_chiffre(valeur: int, niveau: int = 1) -> str:
        """Résout un entier de [-9 ; +9] au niveau demandé (1: Kelvin 'i', 2: Joules 'I')."""
        if valeur not in TABLETTE_CHIFFRES:
            raise ValueError(f"Valeur {valeur} hors de l'axe discret [-9 ; +9].")
        entree = TABLETTE_CHIFFRES[valeur]
        if niveau == 1:
            return entree.etat_i_kelvin
        if niveau == 2:
            return entree.etat_I_joules
        if niveau == 3:
            return INDEX_CHIFFRE_VERS_ALPHABET[valeur].etat_3_alpha_locale
        if niveau == 4:
            return INDEX_CHIFFRE_VERS_ALPHABET[valeur].etat_4_omega_globale
        raise ValueError(f"Niveau {niveau} invalide (attendu: 1..4).")

    @staticmethod
    def resoudre_lettre(lettre: str, niveau: int = 1) -> str:
        """Résout une lettre de [A ; S] selon le niveau (1: a, 2: A, 3: alpha_a, 4: omega_A)."""
        cle = lettre.upper()
        if cle not in TABLETTE_ALPHABET:
            raise ValueError(f"Lettre '{lettre}' hors du domaine ontologique [A ; S].")
        entree = TABLETTE_ALPHABET[cle]
        if niveau == 1:
            return entree.etat_1_minuscule
        if niveau == 2:
            return entree.etat_2_majuscule
        if niveau == 3:
            return entree.etat_3_alpha_locale
        if niveau == 4:
            return entree.etat_4_omega_globale
        raise ValueError(f"Niveau {niveau} invalide (attendu: 1..4).")

    @staticmethod
    def chiffre_depuis_identifiant(identifiant: str) -> Optional[int]:
        """Retrouve la coordonnée [-9 ; +9] associée à un identifiant alpha_x ou omega_X."""
        if identifiant.startswith("alpha_") and len(identifiant) == 7:
            lettre = identifiant[-1].upper()
            if lettre in TABLETTE_ALPHABET:
                return TABLETTE_ALPHABET[lettre].axe_chiffre
        elif identifiant.startswith("omega_") and len(identifiant) == 7:
            lettre = identifiant[-1].upper()
            if lettre in TABLETTE_ALPHABET:
                return TABLETTE_ALPHABET[lettre].axe_chiffre
        elif len(identifiant) == 1 and identifiant.upper() in TABLETTE_ALPHABET:
            return TABLETTE_ALPHABET[identifiant.upper()].axe_chiffre
        return None

    @staticmethod
    def resoudre_ponctuation(symbole: str, niveau: int = 1) -> str:
        """Résout un symbole de ponctuation sur ses 4 états."""
        if symbole not in TABLETTE_PONCTUATION:
            raise ValueError(f"Symbole '{symbole}' absent de la tablette de ponctuation.")
        entree = TABLETTE_PONCTUATION[symbole]
        if niveau == 1:
            return entree.etat_1_simple
        if niveau == 2:
            return entree.etat_2_double
        if niveau == 3:
            return entree.etat_3_enclos
        if niveau == 4:
            return entree.etat_4_inverse
        raise ValueError(f"Niveau {niveau} invalide (attendu: 1..4).")

    @staticmethod
    def resoudre_operateur(axe_ou_symbole: str, niveau: int = 1) -> str:
        """Résout un opérateur selon son niveau (1: Arithmétique, 2: Booléen, 3: Ensembliste)."""
        cible: Optional[EntreeOperateur] = None
        for cle, entree in TABLETTE_OPERATEURS.items():
            if axe_ou_symbole in (
                cle,
                entree.nom_axe,
                entree.symbole_base,
                entree.etat_1_arithmetique,
                entree.etat_2_logique_booleen,
                entree.etat_3_relationnel_ensembliste,
            ):
                cible = entree
                break
        if cible is None:
            raise ValueError(f"Opérateur '{axe_ou_symbole}' inconnu dans la tablette.")
        if niveau == 1:
            return cible.etat_1_arithmetique
        if niveau == 2:
            return cible.etat_2_logique_booleen
        if niveau in (3, 4):
            return cible.etat_3_relationnel_ensembliste
        raise ValueError(f"Niveau {niveau} invalide (attendu: 1..4).")

    @classmethod
    def resoudre_fonction_inverse(cls, axe_ou_symbole: str, niveau: int = 1) -> str:
        """
        Résout la fonction calculatoire inverse d'un opérateur sur ses 3 niveaux :
        - Niveau 1 : Inverse arithmétique (+ ↔ -, × ↔ ÷, ^ ↔ √)
        - Niveau 2 : Dual booléen (AND ↔ NAND, OR ↔ NOR, == ↔ !=)
        - Niveau 3/4 : Inverse relationnel / ensembliste (∪ ↔ ∖, ∩ ↔ ⊘, ≡ ↔ ≢, ⊃ ↔ ⊂)
        """
        cible: Optional[EntreeFonctionInverse] = None
        # 1. Recherche par correspondance exacte sur la source
        for cle, entree in TABLETTE_FONCTIONS_INVERSES.items():
            if axe_ou_symbole.lower() in (cle.lower(), entree.operateur_source.lower()):
                cible = entree
                break

        # 2. Recherche par symbole ou opérateur inverse si non trouvé
        if cible is None:
            for cle, entree in TABLETTE_FONCTIONS_INVERSES.items():
                if axe_ou_symbole.lower() in (
                    entree.operateur_inverse.lower(),
                    entree.symbole_inverse_arithmetique.lower(),
                ):
                    cible = entree
                    break
        if cible is None:
            # Fallback vers résolution par opérateur standard
            for cle, op in TABLETTE_OPERATEURS.items():
                if axe_ou_symbole in (cle, op.nom_axe, op.symbole_base, op.etat_1_arithmetique):
                    if cle in TABLETTE_FONCTIONS_INVERSES:
                        cible = TABLETTE_FONCTIONS_INVERSES[cle]
                        break

        if cible is None:
            raise ValueError(f"Opérateur calculatoire '{axe_ou_symbole}' sans inverse enregistré.")

        if niveau == 1:
            return cible.symbole_inverse_arithmetique
        if niveau == 2:
            return cible.inverse_booleen_dual
        if niveau in (3, 4):
            return cible.inverse_relationnel_ensembliste
        raise ValueError(f"Niveau {niveau} invalide (attendu: 1..4).")

    @classmethod
    def resoudre_oppose_numerique(cls, valeur: int, mode: str = "additif") -> float | int:
        """
        Résout l'élément opposé d'un nombre du socle [-9 ; +9] :
        - mode 'additif' (miroir de parité P) : -x (ex: +7 → -7)
        - mode 'multiplicatif' (symétrie macro/micro M) : 1/x pour x ≠ 0
        """
        if valeur not in TABLETTE_CHIFFRES:
            raise ValueError(f"Valeur {valeur} hors de l'axe [-9 ; +9].")
        if mode == "additif":
            return -valeur
        if mode == "multiplicatif":
            if valeur == 0:
                raise ZeroDivisionError("L'élément 0 (point d'unisson) n'admet pas d'inverse multiplicatif fini.")
            return round(1.0 / float(valeur), 6)
        raise ValueError(f"Mode d'opposition numérique '{mode}' inconnu ('additif' ou 'multiplicatif').")

    @classmethod
    def resoudre_oppose_linguistique(cls, lettre_ou_identifiant: str, mode: str = "atbash") -> str:
        """
        Résout l'élément opposé pour la famille linguistique :
        - mode 'atbash' : Inversion miroir sur les 19 échelons [A ; S] (A ↔ S, B ↔ R ... J pivot)
        - mode 'casse' : Inversion minuscule ↔ majuscule (polarité de force)
        - mode 'portee' : Inversion variable locale alpha_x ↔ constante globale omega_X
        """
        txt = lettre_ou_identifiant.strip()
        if mode == "atbash":
            lettre = txt[-1].upper()
            if lettre not in OPPOSITION_LINGUISTIQUE_ATBASH:
                raise ValueError(f"Caractère '{lettre}' hors de l'ensemble ontologique [A ; S].")
            opp = OPPOSITION_LINGUISTIQUE_ATBASH[lettre]
            if txt.startswith("alpha_"):
                return f"alpha_{opp.lower()}"
            if txt.startswith("omega_"):
                return f"omega_{opp}"
            return opp if txt.isupper() else opp.lower()

        if mode == "casse":
            return txt.lower() if txt.isupper() else txt.upper()

        if mode == "portee":
            if txt.startswith("alpha_"):
                return f"omega_{txt[6:].upper()}"
            if txt.startswith("omega_"):
                return f"alpha_{txt[6:].lower()}"
            if txt.islower():
                return f"omega_{txt.upper()}"
            return f"alpha_{txt.lower()}"

        raise ValueError(f"Mode d'opposition linguistique '{mode}' inconnu.")

    @classmethod
    def resoudre_oppose_typographique(cls, symbole: str) -> str:
        """
        Résout l'élément opposé pour la famille typographique :
        - Chiralité ouvrante ↔ fermante : ( ↔ ), [ ↔ ], « ↔ »
        - Modalité interrogation ↔ certitude : ? ↔ !
        - Inversion culturelle : ¿ ↔ ¡
        """
        s = symbole.strip()
        if s in OPPOSITION_TYPOGRAPHIQUE_CHIRALE:
            return OPPOSITION_TYPOGRAPHIQUE_CHIRALE[s]
        if s in OPPOSITION_TYPOGRAPHIQUE_MODALE:
            return OPPOSITION_TYPOGRAPHIQUE_MODALE[s]
        # Inversion de ponctuation standard
        if s in TABLETTE_PONCTUATION:
            return TABLETTE_PONCTUATION[s].etat_4_inverse
        raise ValueError(f"Symbole typographique '{symbole}' sans opposé défini.")

    @classmethod
    def calculer_sur_table(
        cls,
        famille_axe: str,
        symbole_ou_valeur: Union[str, int],
        niveau: int = 1,
        charge_polarite: int = POLE_MATIERE_POSITIF,
    ) -> Dict[str, object]:
        """
        Opération de LA TABLE (famille COMPLEXE) :
        calcule / résout un symbole d'une des 4 familles sous un pôle de matière.
        """
        if famille_axe not in cls.FAMILLES:
            raise ValueError(f"Axe '{famille_axe}' hors des 4 familles calculées par LA TABLE")
        if niveau not in (1, 2, 3, 4):
            raise ValueError(f"Niveau de table invalide : {niveau}")
        sync = synchroniser_etats_matiere_aux_cinq_familles(charge_polarite)

        if famille_axe == "NUMERIQUE":
            resultat = cls.resoudre_chiffre(int(symbole_ou_valeur), niveau=min(niveau, 2) if niveau <= 2 else niveau)
        elif famille_axe == "LINGUISTIQUE":
            resultat = cls.resoudre_lettre(str(symbole_ou_valeur), niveau=niveau)
        elif famille_axe == "TYPOGRAPHIQUE":
            resultat = cls.resoudre_ponctuation(str(symbole_ou_valeur), niveau=niveau)
        else:  # ALGORITHMIQUE — 3 niveaux max
            resultat = cls.resoudre_operateur(str(symbole_ou_valeur), niveau=min(niveau, 3))

        return {
            "la_table": "COMPLEXE",
            "est_matrice_de_calcul": True,
            "axe_calcule": famille_axe,
            "entree": symbole_ou_valeur,
            "niveau_demande": niveau,
            "resultat": resultat,
            "sync_matiere": {
                "charge_polarite": sync.charge_polarite,
                "ancre_m": sync.ancre_m,
                "decomposition_m": list(sync.decomposition_m),
                "mode_calcul_table": sync.mode_calcul_table,
                "niveau_table_complexe": sync.niveau_table_complexe,
            },
        }

    @classmethod
    def verifier_completude_symetrie(cls) -> Dict[str, bool]:
        """Vérifie que la structure est rigoureusement complète et symétrique."""
        operateurs_inversibles = all(k in TABLETTE_FONCTIONS_INVERSES for k in ["Addition", "Soustraction", "Multiplication", "Division"])
        atbash_symetrique = all(OPPOSITION_LINGUISTIQUE_ATBASH[OPPOSITION_LINGUISTIQUE_ATBASH[c]] == c for c in OPPOSITION_LINGUISTIQUE_ATBASH)
        chiralite_symetrique = all(OPPOSITION_TYPOGRAPHIQUE_CHIRALE[OPPOSITION_TYPOGRAPHIQUE_CHIRALE[s]] == s for s in OPPOSITION_TYPOGRAPHIQUE_CHIRALE)
        parite_numerique = all(-(-x) == x for x in TABLETTE_CHIFFRES)
        cinq_familles_m = verifier_decomposition_m_24434()
        table_est_complexe = cls.EST_LA_TABLE and "COMPLEXE" in cls.FAMILLES_CINQ

        return {
            "operateurs_calculatoires_inverses_complets": operateurs_inversibles,
            "symetrie_atbash_linguistique_validee": atbash_symetrique,
            "chiralite_typographique_opposee_validee": chiralite_symetrique,
            "parite_miroir_numerique_validee": parite_numerique,
            "cinq_familles_decomposition_m_24434": cinq_familles_m,
            "complexe_est_la_table_de_calcul": table_est_complexe,
            "matrice_socle_parfaitement_fermee": (
                operateurs_inversibles
                and atbash_symetrique
                and chiralite_symetrique
                and parite_numerique
                and cinq_familles_m
                and table_est_complexe
            ),
        }

    @classmethod
    def exporter_resume_complet(cls) -> Dict[str, object]:
        """Exporte LA TABLE (matrice COMPLEXE) et les 4 axes qu'elle calcule."""
        return {
            "cinquieme_famille_complexe": {
                "nom": "COMPLEXE",
                "nature": "LA_TABLE_MATRICE_DE_CALCUL",
                "pas_un_simple_conteneur": True,
                "chiffre_m": cls.CHIFFRE_M_TABLE,
                "decomposition_m_24434": list(DECOMPOSITION_M_24434),
                "axes_calcules": list(cls.FAMILLES),
                "niveaux_resolution": 4,
            },
            "axe_numerique": [
                {
                    "valeur": e.valeur,
                    "niveau_1_kelvin": e.etat_i_kelvin,
                    "niveau_2_joules": e.etat_I_joules,
                }
                for e in TABLETTE_CHIFFRES.values()
            ],
            "axe_linguistique": [
                {
                    "chiffre": e.axe_chiffre,
                    "lettre": e.lettre_base,
                    "niveau_1": e.etat_1_minuscule,
                    "niveau_2": e.etat_2_majuscule,
                    "niveau_3": e.etat_3_alpha_locale,
                    "niveau_4": e.etat_4_omega_globale,
                }
                for e in TABLETTE_ALPHABET.values()
            ],
            "axe_typographique": [
                {
                    "base": e.symbole_base,
                    "niveau_1_simple": e.etat_1_simple,
                    "niveau_2_double": e.etat_2_double,
                    "niveau_3_enclos": e.etat_3_enclos,
                    "niveau_4_inverse": e.etat_4_inverse,
                }
                for e in TABLETTE_PONCTUATION.values()
            ],
            "axe_algorithmique": [
                {
                    "axe": e.nom_axe,
                    "base": e.symbole_base,
                    "niveau_1_arithmetique": e.etat_1_arithmetique,
                    "niveau_2_booleen": e.etat_2_logique_booleen,
                    "niveau_3_ensembliste": e.etat_3_relationnel_ensembliste,
                }
                for e in TABLETTE_OPERATEURS.values()
            ],
        }


# Valeurs officielles de Q° — DÉDUITES une fois depuis LA TABLE (pas 313 / 24434)
_Q_OFFICIEL = MatriceLogiqueComplexe.deriver_q_degre_depuis_la_table(POLE_MATIERE_POSITIF)
Q_DEGRE_MECOIS: int = int(_Q_OFFICIEL["Q_mecois"]["valeur_deduite"])       # 2304
Q_DEGRE_MEDINOIS: int = int(_Q_OFFICIEL["Q_medinois"]["valeur_deduite"])   # 1536
assert Q_DEGRE_MECOIS == 2304 and Q_DEGRE_MEDINOIS == 1536
assert Q_DEGRE_MECOIS != 313 and Q_DEGRE_MEDINOIS != 24434
assert Q_DEGRE_MECOIS != ANCRE_M_SUBSTANCE and Q_DEGRE_MEDINOIS != abs(POLE_MATIERE_POSITIF)


# ==============================================================================
# 6. SPHÈRE QUANTIQUE DE BLOCH (`Qubit_informe.jpg`)
# ==============================================================================

class QubitInforme:
    """
    Modélise le Qubit Informe sur la sphère de Bloch :
        |ψ⟩ = α|0⟩ + β|1⟩  avec |α|² + |β|² = 1
    Constante d'onde associée dans QUBITS8INFORME : λ = 5.77e-11 m.
    Permet de projeter n'importe quel signal thermique [-9 ; +9] i sur la sphère de Bloch.
    """

    LAMBDA_INFORME: float = 5.77e-11

    def __init__(self, alpha: complex = 1.0 + 0.0j, beta: complex = 0.0 + 0.0j) -> None:
        norme = math.sqrt(abs(alpha) ** 2 + abs(beta) ** 2)
        if norme == 0:
            self.alpha = 1.0 + 0.0j
            self.beta = 0.0 + 0.0j
        else:
            self.alpha = alpha / norme
            self.beta = beta / norme

    @classmethod
    def depuis_echelon_thermique(cls, echelon: int, phase_joules: float = 0.0) -> "QubitInforme":
        """
        Construit un état |ψ⟩ à partir d'un échelon [-9 ; +9] (Kelvin) et d'une phase (Joules).
        -9 i -> |1⟩ pur (pôle sud thermique)
         0 i -> superposition équilibrée (|0⟩ + |1⟩)/√2 (équateur J / Hélium)
        +9 i -> |0⟩ pur (pôle nord thermique)
        """
        borne = max(-9.0, min(9.0, float(echelon)))
        # Angle polaire theta dans [0, pi] : +9 -> 0, 0 -> pi/2, -9 -> pi
        theta = (9.0 - borne) * (math.pi / 18.0)
        phi = phase_joules * (math.pi / 9.0)
        alpha = complex(math.cos(theta / 2.0), 0.0)
        beta = cmath.rect(math.sin(theta / 2.0), phi)
        return cls(alpha=alpha, beta=beta)

    @property
    def probabilite_0(self) -> float:
        return round(abs(self.alpha) ** 2, 6)

    @property
    def probabilite_1(self) -> float:
        return round(abs(self.beta) ** 2, 6)

    @property
    def est_superpose(self) -> bool:
        return 0.001 < self.probabilite_0 < 0.999

    def coordonnees_bloch(self) -> Tuple[float, float, float]:
        """Retourne le vecteur (x, y, z) sur la sphère unité de Bloch."""
        x = 2.0 * (self.alpha.conjugate() * self.beta).real
        y = 2.0 * (self.alpha.conjugate() * self.beta).imag
        z = abs(self.alpha) ** 2 - abs(self.beta) ** 2
        return (round(x, 6), round(y, 6), round(z, 6))

    def representation_ket(self) -> str:
        return (
            f"|ψ⟩ = ({self.alpha.real:+.4f}{self.alpha.imag:+.4f}j)|0⟩ "
            f"+ ({self.beta.real:+.4f}{self.beta.imag:+.4f}j)|1⟩ "
            f"[λ={self.LAMBDA_INFORME:.2e} m]"
        )
