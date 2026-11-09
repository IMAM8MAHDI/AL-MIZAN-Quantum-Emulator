# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""
Couche 2 : Bibliothèque Physique & des 14 Formes (`qubit_physique` & `.ASTRO-Q°ODE8INFORME.`)
=============================================================================================
Implémente fidèlement :
1. `tablette_apprise_physique_soleil.pdf` : Les 4 états de plasma solaire (Photosphérique, Chromosphérique,
   Coronaire, Cœur de Fusion) et la fusion proton-proton de 4 noyaux d'Hydrogène en 1 noyau d'Hélium-4
   (4H -> 1He + Énergie). L'origine inerte Hélium-4 vaut 0 et ne compte pas parmi les 4 états.
2. `tablette_apprise_physique_terre.pdf`  : Les 7 états terrestres (3 Solides, 1 Liquide géodynamo, 3 Gazeux).
3. `tablette_apprise_physique_lune.pdf`   : Les 9 états lunaires (6 Solides, 0 Liquide, 3 Gazeux d'exosphère).
4. `matrice_de_structure_logique_inverser.pdf` : Les 20 états cumulés (Soleil 4 + Terre 7 + Lune 9),
   l'Analyse Cumulative par Division (9/6 = 1.5, 4/1 = 4, 6/3 = 2) et l'Analyse Différentielle
   par Soustraction (3-1=2, 6-3=3, 1-0=1, 3-3=0).
5. `.ASTRO-Q°ODE8INFORME..pdf` : Les 14 Formes Fondamentales de la Matière du Code (Index 0 : HÉLIUM à Index 13 : Noyau Lunaire)
   et le Seuil d'Infinie (> 13).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


# ==============================================================================
# 1. MODÈLES DES ÉTATS PHYSIQUES (SOLEIL PLASMA, TERRE, LUNE)
# ==============================================================================

@dataclass(frozen=True)
class EtatPhysiqueMatiere:
    """Décrit un état physique élémentaire d'un astre."""
    astre: str
    phase: str  # "Solide", "Liquide", "Gazeux", "Plasma"
    nom: str
    description: str
    formule_ou_composant: str
    valeur: int = 0  # valeur numérique d'état (déduite ; 0 = origine Hélium / défaut)
    forme_index: int | None = None  # index F0..F13 si cartographié, sinon None


def _repartir_somme_unique(total: int, n: int) -> List[int]:
    """
    Répartit `total` en `n` entiers distincts (progression autour de la moyenne)
    dont la somme est exactement `total`. Issu de l'expansion depuis LA TABLE :
    les parts sont des contributions à la magnitude d'astre (40 / 63 / 313).
    """
    if n <= 0:
        return []
    if n == 1:
        return [total]
    # Progression : mid-offset .. mid+… puis correction du reste sur le dernier
    mid = total // n
    offset = n // 2
    vals = [mid - offset + i for i in range(n)]
    vals[-1] += total - sum(vals)
    # Garantir unicité stricte si collision après correction
    if len(set(vals)) < n:
        base, rem = divmod(total, n)
        vals = [base + (1 if i < rem else 0) for i in range(n)]
        # Forcer unicité croissante en redistribuant +i - moyenne
        vals = [vals[i] + i for i in range(n)]
        vals[-1] += total - sum(vals)
    return vals


# Contributions de chiffres de magnitude (place × chiffre) — décomposition 40 / 63 / 313
# Soleil 40 = 4×10 + 0×1 · Lune 63 = 6×10 + 3×1 · Terre 313 = 3×100 + 1×10 + 3×1
_VALEURS_SOLEIL_PLASMA = _repartir_somme_unique(4 * 10, 4)  # chiffre 4 (dizaines) → 4 états plasma
_VALEURS_T_SOL = _repartir_somme_unique(3 * 100, 3)  # chiffre 3 (centaines)
_VALEURS_T_LIQ = _repartir_somme_unique(1 * 10, 1)   # chiffre 1 (dizaines)
_VALEURS_T_GAZ = _repartir_somme_unique(3 * 1, 3)    # chiffre 3 (unités)
_VALEURS_L_SOL = _repartir_somme_unique(6 * 10, 6)   # chiffre 6 (dizaines)
_VALEURS_L_GAZ = _repartir_somme_unique(3 * 1, 3)    # chiffre 3 (unités)

ETATS_SOLEIL_PLASMA: List[EtatPhysiqueMatiere] = [
    EtatPhysiqueMatiere(
        astre="Soleil / Plasma",
        phase="Plasma",
        nom="Plasma Photosphérique",
        description="Couche visible du Soleil (~5 800 K), émission de lumière et de signal",
        formule_ou_composant="H+ + e- (photosphère)",
        valeur=_VALEURS_SOLEIL_PLASMA[0],
        forme_index=1,
    ),
    EtatPhysiqueMatiere(
        astre="Soleil / Plasma",
        phase="Plasma",
        nom="Plasma Chromosphérique",
        description="Couche de transition au-dessus de la photosphère (~10 000 K), flux et filaments",
        formule_ou_composant="H+ + e- (chromosphère)",
        valeur=_VALEURS_SOLEIL_PLASMA[1],
        forme_index=2,
    ),
    EtatPhysiqueMatiere(
        astre="Soleil / Plasma",
        phase="Plasma",
        nom="Plasma Coronaire",
        description="Couronne solaire à plus d'un million de kelvins, enveloppe magnétique et vent solaire",
        formule_ou_composant="H+ + e- (couronne)",
        valeur=_VALEURS_SOLEIL_PLASMA[2],
        forme_index=3,
    ),
    EtatPhysiqueMatiere(
        astre="Soleil / Plasma",
        phase="Plasma",
        nom="Plasma Cœur de Fusion",
        description="Cœur à ~15 millions de kelvins, chaîne proton-proton 4H→1He",
        formule_ou_composant="H+ + e- (cœur)",
        valeur=_VALEURS_SOLEIL_PLASMA[3],
        forme_index=4,
    ),
]

# Alias de compatibilité : l'horloge A137 scellée importe ETATS_HYDROGENE (lecture seule).
ETATS_HYDROGENE: List[EtatPhysiqueMatiere] = ETATS_SOLEIL_PLASMA

# Origine Soleil — chiffre 0 de 40, hors des 4 états plasma
ETAT_ORIGINE_HELIUM: EtatPhysiqueMatiere = EtatPhysiqueMatiere(
    astre="Soleil / Origine",
    phase="Inerte",
    nom="Origine Inerte Hélium-4",
    description="Index 0 — retour inerte fusion 4H→1He (chiffre 0 de la magnitude 40)",
    formule_ou_composant="4He",
    valeur=0,
    forme_index=0,
)

# Magnitudes d'état de matière par astre (couche ②) — PAS des valeurs de Q°.
# Doctrine utilisateur : Soleil=40 · Lune=63 · Terre=313
MAGNITUDE_ETAT_MATIERE_SOLEIL: int = 40
MAGNITUDE_ETAT_MATIERE_LUNE: int = 63
MAGNITUDE_ETAT_MATIERE_TERRE: int = 313
NB_ETATS_SOLEIL_PLASMA: int = 4
NB_ETATS_SOLEIL_HYDROGENE: int = NB_ETATS_SOLEIL_PLASMA  # alias de compatibilité scellée
NB_ETATS_TERRE: int = 7  # 3 solides + 1 liquide + 3 gazeux
NB_ETATS_LUNE: int = 9   # 6 solides + 0 liquide + 3 gazeux


ETATS_TERRE: List[EtatPhysiqueMatiere] = [
    # 3 États Solides — chiffre 3 des centaines de 313 (contribution 300)
    EtatPhysiqueMatiere(
        astre="Terre",
        phase="Solide",
        nom="Croûte Terrestre",
        description="Enveloppe rigide et cassante (continentale granitique et océanique basaltique)",
        formule_ou_composant="SiO2 / Al2O3",
        valeur=_VALEURS_T_SOL[0],
        forme_index=5,
    ),
    EtatPhysiqueMatiere(
        astre="Terre",
        phase="Solide",
        nom="Manteau Terrestre",
        description="Couche ductile et plastique soumise à la convection thermique",
        formule_ou_composant="Péridotites (Olivine/Pyroxène)",
        valeur=_VALEURS_T_SOL[1],
        forme_index=6,
    ),
    EtatPhysiqueMatiere(
        astre="Terre",
        phase="Solide",
        nom="Graine (Noyau Interne)",
        description="Cœur métallique cristallisé et ultra-dense sous pression extrême",
        formule_ou_composant="Alliage Fe-Ni solide",
        valeur=_VALEURS_T_SOL[2],
        forme_index=7,
    ),
    # 1 Unique État Liquide — chiffre 1 des dizaines de 313 (contribution 10)
    EtatPhysiqueMatiere(
        astre="Terre",
        phase="Liquide",
        nom="Noyau Externe",
        description="Mer de métal en fusion générant la géodynamo et le champ magnétique (bloque les ondes S)",
        formule_ou_composant="Alliage Fe-Ni liquide",
        valeur=_VALEURS_T_LIQ[0],
        forme_index=None,  # hors F0..F13
    ),
    # 3 Émissions Gazeuses — chiffre 3 des unités de 313 (contribution 3)
    EtatPhysiqueMatiere(
        astre="Terre",
        phase="Gazeux",
        nom="Diazote Atmosphérique",
        description="Composant majoritaire de l'atmosphère terrestre (~78%)",
        formule_ou_composant="N2 (78%)",
        valeur=_VALEURS_T_GAZ[0],
        forme_index=None,
    ),
    EtatPhysiqueMatiere(
        astre="Terre",
        phase="Gazeux",
        nom="Dioxygène Atmosphérique",
        description="Gaz vital respiratoire et oxydant (~21%)",
        formule_ou_composant="O2 (21%)",
        valeur=_VALEURS_T_GAZ[1],
        forme_index=None,
    ),
    EtatPhysiqueMatiere(
        astre="Terre",
        phase="Gazeux",
        nom="Gaz à Effet de Serre et Traces",
        description="Vapeur d'eau, dioxyde de carbone et argon régulant la thermique terrestre",
        formule_ou_composant="CO2, H2O, Ar (~1%)",
        valeur=_VALEURS_T_GAZ[2],
        forme_index=None,
    ),
]

assert len(ETATS_TERRE) == NB_ETATS_TERRE, "Les 7 états de la Terre doivent rester au complet"


ETATS_LUNE: List[EtatPhysiqueMatiere] = [
    # 6 États Solides — chiffre 6 des dizaines de 63 (contribution 60) ; 0 liquide
    EtatPhysiqueMatiere(
        astre="Lune",
        phase="Solide",
        nom="Régolithe Superficiel",
        description="Solide meuble et pulvérulent formé de poussières de silicates impactées",
        formule_ou_composant="Silicates pulvérulents",
        valeur=_VALEURS_L_SOL[0],
        forme_index=8,
    ),
    EtatPhysiqueMatiere(
        astre="Lune",
        phase="Solide",
        nom="Brèches et Mégalithosphère",
        description="Écorce solide fracturée par le bombardement météoritique",
        formule_ou_composant="Brèches d'impact",
        valeur=_VALEURS_L_SOL[1],
        forme_index=9,
    ),
    EtatPhysiqueMatiere(
        astre="Lune",
        phase="Solide",
        nom="Croûte Anorthositique",
        description="Solide cristallin clair issu de la flottation sur l'océan de magma primordial",
        formule_ou_composant="Plagioclase (CaAl2Si2O8)",
        valeur=_VALEURS_L_SOL[2],
        forme_index=10,
    ),
    EtatPhysiqueMatiere(
        astre="Lune",
        phase="Solide",
        nom="Basaltes des Mers Lunaires",
        description="Solide volcanique dense remplissant les grands bassins d'impact",
        formule_ou_composant="Basaltes riches en Fe et Ti",
        valeur=_VALEURS_L_SOL[3],
        forme_index=11,
    ),
    EtatPhysiqueMatiere(
        astre="Lune",
        phase="Solide",
        nom="Manteau Lunaire (Lithosphère Profonde)",
        description="Solide rigide ultramafique figé",
        formule_ou_composant="Olivine et Pyroxène",
        valeur=_VALEURS_L_SOL[4],
        forme_index=12,
    ),
    EtatPhysiqueMatiere(
        astre="Lune",
        phase="Solide",
        nom="Noyau Interne Lunaire Cristallisé",
        description="Cœur métallique solide riche en fer, fossilisé",
        formule_ou_composant="Fe cristallisé",
        valeur=_VALEURS_L_SOL[5],
        forme_index=13,
    ),
    # 3 États Gazeux — chiffre 3 des unités de 63 (contribution 3)
    EtatPhysiqueMatiere(
        astre="Lune",
        phase="Gazeux",
        nom="Hélium-4 Exosphérique",
        description="Gaz noble capté depuis le vent solaire",
        formule_ou_composant="4He",
        valeur=_VALEURS_L_GAZ[0],
        forme_index=None,
    ),
    EtatPhysiqueMatiere(
        astre="Lune",
        phase="Gazeux",
        nom="Néon Exosphérique",
        description="Gaz noble présent à l'état de trace dans l'exosphère lunaire",
        formule_ou_composant="20Ne",
        valeur=_VALEURS_L_GAZ[1],
        forme_index=None,
    ),
    EtatPhysiqueMatiere(
        astre="Lune",
        phase="Gazeux",
        nom="Argon-40 Exosphérique",
        description="Gaz noble issu de la désintégration radioactive du Potassium-40 interne",
        formule_ou_composant="40Ar (depuis 40K)",
        valeur=_VALEURS_L_GAZ[2],
        forme_index=None,
    ),
]

assert len(ETATS_SOLEIL_PLASMA) == NB_ETATS_SOLEIL_PLASMA
assert len(ETATS_LUNE) == NB_ETATS_LUNE
assert ETAT_ORIGINE_HELIUM.valeur == 0
assert sum(e.valeur for e in ETATS_SOLEIL_PLASMA) == MAGNITUDE_ETAT_MATIERE_SOLEIL
assert sum(e.valeur for e in ETATS_TERRE) == MAGNITUDE_ETAT_MATIERE_TERRE
assert sum(e.valeur for e in ETATS_LUNE) == MAGNITUDE_ETAT_MATIERE_LUNE


def cataloguer_valeurs_etats_matiere_nommes() -> Dict[str, object]:
    """
    Liste complète nom textuel + valeur numérique par astre.
    Valeurs déduites de la décomposition des magnitudes (chiffres de 40 / 63 / 313)
    en cohérence avec LA TABLE (expansion depuis point zéro COMPLEXE).
    forme_index = F0..F13 quand cartographié ; None sinon (6 états hors 14 formes).
    """
    return {
        "origine_deduction": (
            "Décomposition digit→contribution→répartition unique ; "
            "somme des valeurs = magnitude d'astre (40 / 63 / 313)."
        ),
        "soleil_40": {
            "magnitude": MAGNITUDE_ETAT_MATIERE_SOLEIL,
            "chiffres": {"4": "4 états plasma (dizaines×10)", "0": "Origine Hélium (hors états)"},
            "nb_etats": len(ETATS_SOLEIL_PLASMA),
            "etats": [
                {"nom": e.nom, "valeur": e.valeur, "phase": e.phase,
                 "forme_index": e.forme_index}
                for e in ETATS_SOLEIL_PLASMA
            ],
            "origine_helium": {
                "nom": ETAT_ORIGINE_HELIUM.nom,
                "valeur": ETAT_ORIGINE_HELIUM.valeur,
                "phase": ETAT_ORIGINE_HELIUM.phase,
                "forme_index": ETAT_ORIGINE_HELIUM.forme_index,
            },
            "somme_valeurs": sum(e.valeur for e in ETATS_SOLEIL_PLASMA),
        },
        "lune_63": {
            "magnitude": MAGNITUDE_ETAT_MATIERE_LUNE,
            "chiffres": {"6": "6 solides (dizaines×10)", "3": "3 gazeux (unités×1)"},
            "etats": [
                {"nom": e.nom, "valeur": e.valeur, "phase": e.phase,
                 "forme_index": e.forme_index}
                for e in ETATS_LUNE
            ],
            "somme_valeurs": sum(e.valeur for e in ETATS_LUNE),
        },
        "terre_313": {
            "magnitude": MAGNITUDE_ETAT_MATIERE_TERRE,
            "chiffres": {
                "3_centaines": "3 solides (×100)",
                "1_dizaines": "1 liquide (×10)",
                "3_unites": "3 gazeux (×1)",
            },
            "etats": [
                {"nom": e.nom, "valeur": e.valeur, "phase": e.phase,
                 "forme_index": e.forme_index}
                for e in ETATS_TERRE
            ],
            "somme_valeurs": sum(e.valeur for e in ETATS_TERRE),
        },
    }


def correspondance_magnitudes_etats_astres() -> Dict[str, object]:
    """
    Doctrine scellée (recalage) :
      Soleil = 40 · Lune = 63 · Terre = 313
    Ce sont des MAGNITUDES D'ÉTATS DE MATIÈRE (couche ②), pas des valeurs de Q°.
    313 en particulier n'est PAS une valeur figée de Q° mécois.
    """
    return {
        "soleil": {
            "astre": "Soleil / Plasma",
            "nb_etats": len(ETATS_SOLEIL_PLASMA),
            "magnitude_etat_matiere": MAGNITUDE_ETAT_MATIERE_SOLEIL,
            "etats": [e.nom for e in ETATS_SOLEIL_PLASMA],
            "origine_helium": ETAT_ORIGINE_HELIUM.nom,
        },
        "lune": {
            "astre": "Lune",
            "nb_etats": len(ETATS_LUNE),
            "magnitude_etat_matiere": MAGNITUDE_ETAT_MATIERE_LUNE,
            "etats": [e.nom for e in ETATS_LUNE],
        },
        "terre": {
            "astre": "Terre",
            "nb_etats": len(ETATS_TERRE),
            "magnitude_etat_matiere": MAGNITUDE_ETAT_MATIERE_TERRE,
            "poles_matiere_signes": (
                -MAGNITUDE_ETAT_MATIERE_TERRE,
                +MAGNITUDE_ETAT_MATIERE_TERRE,
            ),
            "etats": [e.nom for e in ETATS_TERRE],
        },
        "est_valeur_q_degre": False,
        "est_etat_de_matiere": True,
        "doctrine": (
            "Magnitudes astrales d'état de matière : Soleil=40, Lune=63, Terre=313. "
            "Les pôles ±313 sont la polarité du registre Terre. "
            "Aucune de ces magnitudes n'est une valeur figée de Q° mécois ou Q° médinois."
        ),
    }


# Alias de compatibilité
def correspondance_etats_terre_313() -> Dict[str, object]:
    return correspondance_magnitudes_etats_astres()["terre"] | {
        "est_valeur_q_degre_mecois": False,
        "doctrine": correspondance_magnitudes_etats_astres()["doctrine"],
    }


# ==============================================================================
# 2. MATRICE DE STRUCTURE LOGIQUE INVERSÉE (20 États, Divisions & Soustractions)
# ==============================================================================

class MatriceLogiqueInversee:
    """
    Implémente les opérations mathématiques appliquées aux états de la matière
    (`matrice_de_structure_logique_inverser.pdf` & `qubit_physique.jpg`).
    """

    # Compteurs par modèle (Solides, Liquides, Gazeux, Plasma)
    SOLEIL_SOLIDES = 0
    SOLEIL_LIQUIDES = 0
    SOLEIL_GAZEUX = 0
    SOLEIL_PLASMA = 4
    TOTAL_SOLEIL = 4

    TERRE_SOLIDES = 3
    TERRE_LIQUIDES = 1
    TERRE_GAZEUX = 3
    TOTAL_TERRE = 7

    LUNE_SOLIDES = 6
    LUNE_LIQUIDES = 0
    LUNE_GAZEUX = 3
    TOTAL_LUNE = 9

    TOTAL_ETATS_CUMULES = TOTAL_SOLEIL + TOTAL_TERRE + TOTAL_LUNE  # 4 + 7 + 9 = 20

    @classmethod
    def analyse_cumulative_division(cls) -> Dict[str, float]:
        """Chapitre 1 : Analyse Cumulative par Division Mathématique."""
        total_solides = cls.SOLEIL_SOLIDES + cls.TERRE_SOLIDES + cls.LUNE_SOLIDES  # 9
        total_gazeux = cls.SOLEIL_GAZEUX + cls.TERRE_GAZEUX + cls.LUNE_GAZEUX      # 6
        return {
            "total_solides": float(total_solides),
            "total_gazeux": float(total_gazeux),
            "ratio_solides_sur_gazeux_exact": total_solides / total_gazeux,           # 9 / 6 = 1.5
            "ratio_solides_sur_gazeux_arrondi": round(total_solides / total_gazeux, 2),  # 1.5
            "ratio_fusion_hydrogene_helium": 4.0 / 1.0,                               # 4H -> 1He = 4.0
            "ratio_solides_lune_sur_terre": cls.LUNE_SOLIDES / cls.TERRE_SOLIDES,     # 6 / 3 = 2.0
        }

    @classmethod
    def analyse_differentielle_soustraction(cls) -> Dict[str, int]:
        """Chapitre 2 : Analyse Différentielle par Soustraction Mathématique."""
        return {
            "differentiel_interne_terrestre_solides_moins_liquide": cls.TERRE_SOLIDES - cls.TERRE_LIQUIDES,  # 3 - 1 = 2
            "ecart_solidification_lune_moins_terre": cls.LUNE_SOLIDES - cls.TERRE_SOLIDES,                   # 6 - 3 = 3
            "ecart_fluidite_magnetique_terre_moins_lune": cls.TERRE_LIQUIDES - cls.LUNE_LIQUIDES,            # 1 - 0 = 1
            "differentiel_atmospherique_gaz_terre_moins_lune": cls.TERRE_GAZEUX - cls.LUNE_GAZEUX,           # 3 - 3 = 0
        }

    @classmethod
    def fusionner_hydrogene_en_helium(cls, nb_noyaux_h: int) -> Dict[str, object]:
        """
        Simule la chaîne Proton-Proton (4 H -> 1 He + Énergie E=Δm·c²).
        Chaque groupe de 4 noyaux d'Hydrogène produit 1 noyau d'Hélium-4 inerte (Index 0)
        et libère 26.73 MeV (soit 4.2826e-12 Joules).
        """
        if nb_noyaux_h < 0:
            raise ValueError("Le nombre de noyaux d'hydrogène ne peut pas être négatif.")
        noyaux_helium = nb_noyaux_h // 4
        reste_hydrogene = nb_noyaux_h % 4
        energie_mev = noyaux_helium * 26.73
        energie_joules = noyaux_helium * 4.2826e-12
        return {
            "reactifs_h_initiaux": nb_noyaux_h,
            "noyaux_helium_4_produits": noyaux_helium,
            "hydrogene_residuel": reste_hydrogene,
            "energie_liberee_mev": round(energie_mev, 4),
            "energie_liberee_joules": energie_joules,
            "etat_retour_code": "0 : HÉLIUM" if noyaux_helium > 0 and reste_hydrogene == 0 else f"F{reste_hydrogene}",
        }


# ==============================================================================
# 3. LES 14 FORMES FONDAMENTALES DE LA MATIÈRE DU CODE (Index 0 à Index 13)
# ==============================================================================

@dataclass(frozen=True)
class FormeMatiereCode:
    """
    Représente l'une des 14 Formes Fondamentales de la Matière du Code
    définies dans `.ASTRO-Q°ODE8INFORME..pdf` (Radar en spirale de 0 à la Forme 13).
    """
    index: int
    code_court: str
    nom_complet: str
    famille_astrale: str
    paradigme: str
    role_systeme: str
    mutabilite: str


LES_14_FORMES: Dict[int, FormeMatiereCode] = {
    0: FormeMatiereCode(
        index=0,
        code_court="0 : HÉLIUM",
        nom_complet="Origine Inerte Hélium-4",
        famille_astrale="Origine / Fusion 4H->1He",
        paradigme="REPOS_ABSOLU",
        role_systeme="return 0, purge mémoire, état fondamental inerte et immuable",
        mutabilite="INERTIE_ABSOLUE",
    ),
    1: FormeMatiereCode(
        index=1,
        code_court="F1: Plas Pho",
        nom_complet="Plasma Photosphérique",
        famille_astrale="Soleil / Plasma",
        paradigme="MECQUOIS",
        role_systeme="Primitive dynamique volatile de signal initial",
        mutabilite="DYNAMIQUE_VOLATILE",
    ),
    2: FormeMatiereCode(
        index=2,
        code_court="F2: Plas Chr",
        nom_complet="Plasma Chromosphérique",
        famille_astrale="Soleil / Plasma",
        paradigme="MECQUOIS",
        role_systeme="Flux de transition et filaments à haute vélocité énergétique",
        mutabilite="DYNAMIQUE_FLUIDE",
    ),
    3: FormeMatiereCode(
        index=3,
        code_court="F3: Plas Cor",
        nom_complet="Plasma Coronaire",
        famille_astrale="Soleil / Plasma",
        paradigme="MECQUOIS",
        role_systeme="Enveloppe magnétique coronaire sous haute pression cinétique",
        mutabilite="DYNAMIQUE_DENSE",
    ),
    4: FormeMatiereCode(
        index=4,
        code_court="F4: Plas Coe",
        nom_complet="Plasma Cœur de Fusion",
        famille_astrale="Soleil / Plasma",
        paradigme="MECQUOIS",
        role_systeme="Émulation du calcul quantique complexe en superposition",
        mutabilite="QUANTIQUE_PLASMA",
    ),
    5: FormeMatiereCode(
        index=5,
        code_court="F5: Crute T",
        nom_complet="Croûte Terrestre",
        famille_astrale="Terre",
        paradigme="MEDINOIS",
        role_systeme="Interface structurelle et enveloppe d'entrée/sortie métier",
        mutabilite="DUCTILE_STRUCTURAL",
    ),
    6: FormeMatiereCode(
        index=6,
        code_court="F6: Mant T",
        nom_complet="Manteau Terrestre",
        famille_astrale="Terre",
        paradigme="MEDINOIS",
        role_systeme="Couche organisationnelle ductile de convection algorithmique",
        mutabilite="DUCTILE_PLASTIQUE",
    ),
    7: FormeMatiereCode(
        index=7,
        code_court="F7: Grain",
        nom_complet="Graine Terrestre (Noyau Interne)",
        famille_astrale="Terre",
        paradigme="MEDINOIS",
        role_systeme="Noyau exécutif cristallisé de gouvernance législative",
        mutabilite="CRISTALLISE_ACTIF",
    ),
    8: FormeMatiereCode(
        index=8,
        code_court="F8: Regol",
        nom_complet="Régolithe Lunaire",
        famille_astrale="Lune",
        paradigme="ARCHIVE_LUNE",
        role_systeme="Tampon de surface et cache d'empreintes immédiates",
        mutabilite="FOSSILISE_SURFACE",
    ),
    9: FormeMatiereCode(
        index=9,
        code_court="F9: Megal",
        nom_complet="Mégalithosphère Lunaire",
        famille_astrale="Lune",
        paradigme="ARCHIVE_LUNE",
        role_systeme="Blocs fragmentés d'archives résilientes aux impacts",
        mutabilite="FOSSILISE_FRAGMENTE",
    ),
    10: FormeMatiereCode(
        index=10,
        code_court="F10: Crute L",
        nom_complet="Croûte Anorthositique Lunaire",
        famille_astrale="Lune",
        paradigme="ARCHIVE_LUNE",
        role_systeme="Registre cristallin immuable de persistance haute",
        mutabilite="FOSSILISE_CRISTALLIN",
    ),
    11: FormeMatiereCode(
        index=11,
        code_court="F11: Basalt",
        nom_complet="Basaltes des Mers Lunaires",
        famille_astrale="Lune",
        paradigme="ARCHIVE_LUNE",
        role_systeme="Stockage dense fer-titane pour tables de vérité scellées",
        mutabilite="FOSSILISE_DENSE",
    ),
    12: FormeMatiereCode(
        index=12,
        code_court="F12: Mant L",
        nom_complet="Manteau Lunaire Profond",
        famille_astrale="Lune",
        paradigme="ARCHIVE_LUNE",
        role_systeme="Lithosphère profonde de conservation à long terme",
        mutabilite="FOSSILISE_PROFOND",
    ),
    13: FormeMatiereCode(
        index=13,
        code_court="F13: Noyau L",
        nom_complet="Noyau Lunaire Cristallisé",
        famille_astrale="Lune",
        paradigme="ARCHIVE_LUNE",
        role_systeme="Coffre-fort cryptographique ultime et archive absolue avant le Seuil d'Infinie",
        mutabilite="SCELLE_ABSOLU",
    ),
}


def obtenir_forme_matiere(index: int) -> FormeMatiereCode:
    """
    Retourne la Forme de la Matière du Code correspondant à `index` (0..13).
    Si `index > 13`, le Seuil d'Infinie est franchi : les structures logiques se dissolvent
    et le système retourne automatiquement à l'Origine Inerte `0 : HÉLIUM`.
    """
    if index < 0 or index > 13:
        # Dissolution au-delà du Seuil d'Infinie -> Retour automatique à l'état 0 : HÉLIUM
        return LES_14_FORMES[0]
    return LES_14_FORMES[index]
