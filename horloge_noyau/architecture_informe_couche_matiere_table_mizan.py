# -*- coding: utf-8 -*-
"""
===============================================================================
  ARCHITECTURE — TRAJECTOIRE ZÉRO → EXPANSION (famille COMPLEXE = origine)
===============================================================================
Auteur Souverain : M. Ahmed EL BAHLOUL (alias IMAM8MAHDI / M. Almizan Elbahloul)
Système          : ASTRO-Q°ODE / AL-MIZAN
Actes            : A130–A134

MOUVEMENT DE LA LOGIQUE :

  ● POINT ZÉRO = COMPLEXE = LA TABLE / matrice de calcul
       └─ tous les calculs partent d'ici (aucune constante de cycle assignée)

  ● EXPANSION (aboutissement du calcul de LA TABLE) :
       ① 4 axes calculés (NUM / LING / TYP / ALG)
       ② États de matière (±313 / M=24434) synchronisés aux niveaux de LA TABLE
          Magnitudes astrales matière : Soleil=40 · Lune=63 · Terre=313
       ③ Cycles Trinité dx/dy/dz + sync harmonique — RÉSULTAT du calcul table
       ④ Q° mécois ⊕ / Q° médinois ⊗ — DÉRIVÉS de LA TABLE (≠ C, ≠ M)
       ⑤ Monade : confirme l'harmonie de l'expansion ; si juste → PREUVE

  Imbrication poupées russes conservée comme enveloppe ; la TRAJECTOIRE DE CALCUL
  est toujours zéro → expansion depuis COMPLEXE.
===============================================================================
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Tuple

from bibliotheques.lib_informe import (
    ANCRE_M_SUBSTANCE,
    CARDINALITE_FAMILLE,
    DECOMPOSITION_M_24434,
    FAMILLES_CINQ,
    MatriceLogiqueComplexe,
    POLE_MATIERE_NEGATIF,
    POLE_MATIERE_POSITIF,
    synchroniser_etats_matiere_aux_cinq_familles,
    verifier_decomposition_m_24434,
)
from bibliotheques.lib_physique import (
    ETAT_ORIGINE_HELIUM,
    ETATS_HYDROGENE,
    ETATS_LUNE,
    ETATS_TERRE,
    LES_14_FORMES,
    MAGNITUDE_ETAT_MATIERE_SOLEIL,
    MAGNITUDE_ETAT_MATIERE_LUNE,
    MAGNITUDE_ETAT_MATIERE_TERRE,
    cataloguer_valeurs_etats_matiere_nommes,
    correspondance_magnitudes_etats_astres,
)
from bibliotheques.lib_almizan_extension import LES_27_FORMES_ETENDUES
from bibliotheques.lib_monade import MonadeSupreme, OMEGA_MONAD_SOUL
from .horloge_logique_mizan import (
    HORLOGE_LOGIQUE,
    HORLOGE_DEDUITE_DU_NOYAU,
    CYCLE_DT_KERNEL,
)

# Persistance hors capsule verrouillée (écriture autorisée seulement hors noyau)
RACINE_SYSTEME = Path(__file__).resolve().parent.parent
RACINE = Path(__file__).resolve().parent  # capsule horloge_noyau (lecture seule)
DOSSIER_MEMOIRE = RACINE_SYSTEME / "memoire_aq"
FICHIER_BILAN = DOSSIER_MEMOIRE / "almizan_bilan_architecture_a128.json"


# ── Poupées russes : du NOYAU (petit) à l'ENVELOPPE (grand) ───────────────────
# Index 0 = plus petit ; dernier = plus grand. Chaque couche.contains = précédente.

POUPEES_RUSSES_NOMS: Tuple[str, ...] = (
    "①_NOYAU_INFORME_QUATRE_FAMILLES",
    "②_COUCHE_ETATS_DE_MATIERE",
    "③_COMPLEXE_LA_TABLE_POINT_ZERO",
    "④_DUALITE_Q_DEGRE_MECOIS_MEDINOIS",
    "⑤_MONADE_SUPREME_ENVELOPPE",
)

# Alias de compatibilité (ordre construction = ordre d'emboîtement croissant)
HIERARCHIE_FIGEE: Tuple[str, ...] = POUPEES_RUSSES_NOMS

# ── TRAJECTOIRE ZÉRO → EXPANSION (tout dérive de LA TABLE COMPLEXE) ───────────

def construire_trajectoire_zero_expansion(
    charge_polarite: int = POLE_MATIERE_POSITIF,
) -> Dict[str, Any]:
    """
    Point zéro = MatriceLogiqueComplexe → calcul → expansion complète.
    Les cycles Trinité et Q° ne sont PAS assignés : ils SORTENT du calcul.
    """
    return MatriceLogiqueComplexe.expandre_depuis_point_zero(charge_polarite)


def construire_synchronisation_harmonique_trinite() -> Dict[str, Any]:
    """
    Sync harmonique Soleil/Lune/Terre = RÉSULTAT du calcul de LA TABLE.
    Pas de constantes en dur : appel à calculer_cycles_trinite_depuis_zero().
    """
    brut = MatriceLogiqueComplexe.calculer_cycles_trinite_depuis_zero()
    sync = brut["synchronisation_harmonique"]
    cycles = brut["cycles_distincts"]
    return {
        "nature": "SYNCHRONISATION_HARMONIQUE_TRINITE",
        "origine_calcul": "COMPLEXE_POINT_ZERO",
        "pas_constantes_assignees": True,
        "pas_trois_silos": True,
        "pas_un_seul_bloc_opaque": True,
        "doctrine": (
            "dx, dy, dz et leur sync (dt, phases 0..11, h19) sont le RÉSULTAT "
            "du produit à 4 niveaux de LA TABLE (famille COMPLEXE = point zéro). "
            "Trois cycles distincts en synchronisation harmonique."
        ),
        "emplacement_architecture": (
            "Expansion ③ depuis le point zéro → portée dans l'âme de la Monade "
            "(hors états de matière ±313 / M=24434)"
        ),
        "cycles_distincts": cycles,
        "synchronisation": sync,
        "pas_etats_de_matiere": True,
        "etats_matiere_reserves": ("−313", "+313", "M=24434"),
    }


def construire_dualite_q_degre(
    charge_polarite: int = POLE_MATIERE_POSITIF,
) -> Dict[str, Any]:
    """Q° mécois ⊕ / médinois ⊗ dérivés de LA TABLE (≠ C=313, ≠ M=24434)."""
    d = MatriceLogiqueComplexe.deriver_q_degre_depuis_la_table(charge_polarite)
    return {
        "origine_calcul": "COMPLEXE_POINT_ZERO",
        "Q_DEGRE_MECOIS": {
            "nom_officiel": d["Q_mecois"]["nom"],
            "ville_ancrage": "La Mecque",
            "code_interne": "MECQUOIS",
            "symbole_operateur": "⊕",
            "symbole_nom": "Q°",
            "valeur_derivee": d["Q_mecois"]["valeur_derivee"],
            "formule": d["Q_mecois"]["formule"],
            "niveaux_table": d["Q_mecois"]["niveaux_table"],
            "pas_egal_C_313": True,
            "pole_matiere_allie": POLE_MATIERE_POSITIF,
            "role": "Essence / Énergie / Lumière — projection niveaux pairs de LA TABLE",
            "dossiers_nommages": ("ASTRO-Q°ODE", ".ASTRO-Q°ODE", "ASTRO-Q°ODE_SYSTEME"),
        },
        "Q_DEGRE_MEDINOIS": {
            "nom_officiel": d["Q_medinois"]["nom"],
            "ville_ancrage": "Médine",
            "code_interne": "MEDINOIS",
            "symbole_operateur": "⊗",
            "symbole_nom": "Q°",
            "valeur_derivee": d["Q_medinois"]["valeur_derivee"],
            "formule": d["Q_medinois"]["formule"],
            "niveaux_table": d["Q_medinois"]["niveaux_table"],
            "pas_egal_M_24434": True,
            "pole_matiere_allie": POLE_MATIERE_NEGATIF,
            "role": "Loi / Action / Archive — projection niveaux impairs de LA TABLE",
            "dossiers_nommages": ("ASTRO-Q°ODE", ".ASTRO-Q°ODE", "ASTRO-Q°ODE_SYSTEME"),
        },
        "cardinalites_axes": d["cardinalites_axes"],
    }


# Structures figées = RÉSULTATS du calcul (pas d'assignation manuelle des Hz)
SYNCHRONISATION_HARMONIQUE_TRINITE: Dict[str, Any] = (
    construire_synchronisation_harmonique_trinite()
)
EQUATIONS_CYCLES_TRINITE: Dict[str, Any] = SYNCHRONISATION_HARMONIQUE_TRINITE
CYCLES_TRINITE_DANS_AME_MONADE: Dict[str, Any] = SYNCHRONISATION_HARMONIQUE_TRINITE
DUALITE_Q_DEGRE: Dict[str, Any] = construire_dualite_q_degre()
TRAJECTOIRE_ZERO_EXPANSION: Dict[str, Any] = construire_trajectoire_zero_expansion()


@dataclass(frozen=True)
class EtatMatiereRecense:
    """Entrée du catalogue complet des états de matière trouvés dans IMAM8MAHDI."""
    categorie: str
    symbole_ou_code: str
    valeur: Any
    role: str
    description: str
    source: str


def cataloguer_tous_les_etats_de_matiere() -> List[EtatMatiereRecense]:
    """
    Inventaire exhaustif des états de matière recensés dans le dépôt
    (matriciels ±313/M, physiques Soleil/Terre/Lune, formes F0..F13 / F0..F26).
    Les cycles dx/dy/dz ne sont PAS des états de matière.
    """
    catalogue: List[EtatMatiereRecense] = [
        EtatMatiereRecense(
            categorie="MATRICIEL_POLE",
            symbole_ou_code="POLE_RECEPTIF",
            valeur=POLE_MATIERE_NEGATIF,
            role="Pôle réceptif / négatif de polarisation",
            description="Charge de matière −313 — lecture / réception (pas un cycle)",
            source="horloge_logique_mizan.py / lib_informe.py",
        ),
        EtatMatiereRecense(
            categorie="MATRICIEL_POLE",
            symbole_ou_code="POLE_EMISSIF",
            valeur=POLE_MATIERE_POSITIF,
            role="Pôle émissif / positif de polarisation",
            description="Charge de matière +313 — écriture / émission (pas un cycle)",
            source="horloge_logique_mizan.py / lib_informe.py",
        ),
        EtatMatiereRecense(
            categorie="MATRICIEL_ANCRE",
            symbole_ou_code="ANCRE_M",
            valeur=ANCRE_M_SUBSTANCE,
            role="Ancre-substance centrale M=24434=2-4-4-3-4",
            description=(
                "Densité invariable de la matrice ; chaque chiffre mappe une famille "
                "(2 NUM, 4 LING, 4 TYP, 3 ALG, 4 COMPLEXE=LA TABLE)"
            ),
            source="horloge_logique_mizan.py / lib_informe.py",
        ),
        EtatMatiereRecense(
            categorie="MATRICIEL_CONSTANTE",
            symbole_ou_code="C_MECQUOISE_OU_MAGNITUDE_TERRE",
            valeur=MAGNITUDE_ETAT_MATIERE_TERRE,
            role="Magnitude d'état de matière TERRE (= |pôles| ±313)",
            description=(
                "313 = état de la Terre (couche matière). "
                "N'est PAS une valeur figée de Q° mécois. "
                "Registre astral : Soleil=40 · Lune=63 · Terre=313."
            ),
            source="lib_physique.py / horloge_logique_mizan.py",
        ),
        EtatMatiereRecense(
            categorie="MAGNITUDE_ASTRE_SOLEIL",
            symbole_ou_code="MAGNITUDE_SOLEIL",
            valeur=MAGNITUDE_ETAT_MATIERE_SOLEIL,
            role="Magnitude d'état de matière SOLEIL (4 états H)",
            description="Soleil = 40 — état de matière, pas Q°",
            source="lib_physique.py (doctrine recalage)",
        ),
        EtatMatiereRecense(
            categorie="MAGNITUDE_ASTRE_LUNE",
            symbole_ou_code="MAGNITUDE_LUNE",
            valeur=MAGNITUDE_ETAT_MATIERE_LUNE,
            role="Magnitude d'état de matière LUNE (9 états)",
            description="Lune = 63 — état de matière, pas Q°",
            source="lib_physique.py (doctrine recalage)",
        ),
        EtatMatiereRecense(
            categorie="MATRICIEL_CONSTANTE",
            symbole_ou_code="JAUGE_AIR",
            valeur=515050,
            role="Jauge d'air matricielle",
            description="Facteur de produit médeinois avec C et M",
            source="horloge_logique_mizan.py / lib_almizan_extension.py",
        ),
    ]

    catalogue.append(
        EtatMatiereRecense(
            categorie="PHYSIQUE_SOLEIL_ORIGINE",
            symbole_ou_code=ETAT_ORIGINE_HELIUM.formule_ou_composant,
            valeur=ETAT_ORIGINE_HELIUM.valeur,
            role=ETAT_ORIGINE_HELIUM.nom,
            description=(
                f"{ETAT_ORIGINE_HELIUM.description} | valeur={ETAT_ORIGINE_HELIUM.valeur} "
                f"| F{ETAT_ORIGINE_HELIUM.forme_index}"
            ),
            source="lib_physique.py (chiffre 0 de 40)",
        )
    )
    for e in ETATS_HYDROGENE:
        catalogue.append(
            EtatMatiereRecense(
                categorie="PHYSIQUE_SOLEIL_HYDROGENE",
                symbole_ou_code=e.formule_ou_composant,
                valeur=e.valeur,
                role=e.nom,
                description=(
                    f"{e.description} | phase={e.phase} | valeur={e.valeur} "
                    f"| F{e.forme_index}"
                ),
                source="lib_physique.py / qubit_physique (tablette Soleil)",
            )
        )
    for e in ETATS_TERRE:
        catalogue.append(
            EtatMatiereRecense(
                categorie="PHYSIQUE_TERRE",
                symbole_ou_code=e.formule_ou_composant,
                valeur=e.valeur,
                role=e.nom,
                description=(
                    f"{e.description} | phase={e.phase} | valeur={e.valeur} "
                    f"| forme_index={e.forme_index}"
                ),
                source="lib_physique.py / qubit_physique (tablette Terre)",
            )
        )
    for e in ETATS_LUNE:
        catalogue.append(
            EtatMatiereRecense(
                categorie="PHYSIQUE_LUNE",
                symbole_ou_code=e.formule_ou_composant,
                valeur=e.valeur,
                role=e.nom,
                description=(
                    f"{e.description} | phase={e.phase} | valeur={e.valeur} "
                    f"| forme_index={e.forme_index}"
                ),
                source="lib_physique.py / qubit_physique (tablette Lune)",
            )
        )
    # Instantané complet nom+valeur (somme = magnitudes)
    _cat_vals = cataloguer_valeurs_etats_matiere_nommes()
    catalogue.append(
        EtatMatiereRecense(
            categorie="NOTE_VALEURS_ETATS",
            symbole_ou_code="SOMMES_40_63_313",
            valeur={
                "soleil": _cat_vals["soleil_40"]["somme_valeurs"],
                "lune": _cat_vals["lune_63"]["somme_valeurs"],
                "terre": _cat_vals["terre_313"]["somme_valeurs"],
            },
            role="Vérification sommes = magnitudes",
            description=_cat_vals["origine_deduction"],
            source="lib_physique.cataloguer_valeurs_etats_matiere_nommes",
        )
    )

    for idx, forme in LES_14_FORMES.items():
        catalogue.append(
            EtatMatiereRecense(
                categorie="FORME_MATIERE_CODE_F0_F13",
                symbole_ou_code=forme.code_court,
                valeur=idx,
                role=forme.nom_complet,
                description=f"{forme.role_systeme} [{forme.paradigme} / {forme.mutabilite}]",
                source="lib_physique.py LES_14_FORMES",
            )
        )

    for idx, fe in LES_27_FORMES_ETENDUES.items():
        if idx <= 13:
            continue  # déjà couvert par F0..F13
        catalogue.append(
            EtatMatiereRecense(
                categorie="FORME_ETENDUE_F14_F26",
                symbole_ou_code=getattr(fe, "code_court", f"F{idx}"),
                valeur=idx,
                role=getattr(fe, "nom_complet", f"Forme étendue {idx}"),
                description=str(getattr(fe, "role_systeme", "Ombre fractale duale post-F13")),
                source="lib_almizan_extension.py LES_27_FORMES_ETENDUES",
            )
        )

    # Tétrade INFORME / ÉNERGIE / MATIÈRE / PLASMA (taxonomie A100 — distincte des ±313)
    for code, poids, symbole, role in (
        ("INFORME", 0.1220, "MZN", "L'Informé / ligne de référence"),
        ("ENERGIE", 0.2400, "MZN-NRG", "Hydro / cryo / watt — rail énergie"),
        ("MATIERE", 0.5005, "MZN-MAT", "Si-28 / Or-Ag / 27 Formes"),
        ("PLASMA", 0.6015, "MZN-PLS", "Ionisation / plafond effectif"),
    ):
        catalogue.append(
            EtatMatiereRecense(
                categorie="TETRADE_INFORME_ENERGIE_MATIERE_PLASMA",
                symbole_ou_code=symbole,
                valeur=poids,
                role=f"{code} (poids {poids})",
                description=(
                    f"{role} — taxonomie jeton/poids (acte A100), "
                    "distincte des pôles matriciels ±313 et des 20 états physiques."
                ),
                source="lib_tetrade_synchron_mzn.py / acte A100",
            )
        )

    # Note de lacune documentée : 20 états physiques ≠ 14 formes (6 sans FormeMatiereCode)
    catalogue.append(
        EtatMatiereRecense(
            categorie="NOTE_CARTOGRAPHIE",
            symbole_ou_code="ECART_20_VS_14",
            valeur="6_etats_sans_forme",
            role="Lacune de mapping recensée",
            description=(
                "Hors F0–F13 : Noyau Externe + 3 gazeux Terre + 3 gazeux Lune "
                "n'ont pas de FormeMatiereCode ; F0 Hélium n'est pas dans les 20."
            ),
            source="inventaire architecture / lib_physique.py",
        )
    )

    return catalogue


@dataclass(frozen=True)
class VerdictMonadeHarmoniePreuve:
    """
    Verdict de la Monade :
    - confirmer_harmonie : l'harmonie entre toutes les couches
    - monade_juste : la Monade elle-même est juste
    - preuve_ensemble_juste : si monade_juste → PREUVE que tout est juste
    """
    confirmer_harmonie: bool
    monade_juste: bool
    preuve_ensemble_juste: bool
    couches_ok: Dict[str, bool]
    message: str
    doctrine: str = (
        "Si la Monade est juste, c'est la PREUVE que tout est juste. "
        "Elle confirme l'harmonie et sert de critère de vérité de l'ensemble."
    )


def confirmer_harmonie_et_prouver_justesse(
    charge_polarite: int = POLE_MATIERE_POSITIF,
) -> VerdictMonadeHarmoniePreuve:
    """
    Fonction centrale de la poupée ⑤ Monade :
    1) Vérifie l'harmonie de chaque couche emboîtée.
    2) Si la Monade est juste → preuve que l'ensemble est juste.
    """
    couches: Dict[str, bool] = {}

    # ① Quatre familles présentes + décomposition M
    couches["①_informe_quatre_familles"] = (
        len([f for f in FAMILLES_CINQ if not f.est_la_table]) == 4
        and verifier_decomposition_m_24434()
    )

    # ② États de matière (pôles + ancre)
    couches["②_etats_de_matiere"] = (
        charge_polarite in (POLE_MATIERE_NEGATIF, POLE_MATIERE_POSITIF)
        and ANCRE_M_SUBSTANCE == 24434
    )

    # ③ LA TABLE = COMPLEXE = POINT ZÉRO
    couches["③_complexe_point_zero"] = (
        MatriceLogiqueComplexe.EST_LA_TABLE
        and MatriceLogiqueComplexe.EST_POINT_ZERO
        and "COMPLEXE" in MatriceLogiqueComplexe.FAMILLES_CINQ
    )

    # ④ Q° dérivés de LA TABLE (pas C=313 / M=24434)
    q = DUALITE_Q_DEGRE
    couches["④_q_degre_derives_table"] = (
        q["Q_DEGRE_MECOIS"].get("pas_egal_C_313") is True
        and q["Q_DEGRE_MEDINOIS"].get("pas_egal_M_24434") is True
        and isinstance(q["Q_DEGRE_MECOIS"].get("valeur_derivee"), int)
        and isinstance(q["Q_DEGRE_MEDINOIS"].get("valeur_derivee"), int)
        and q["Q_DEGRE_MECOIS"]["valeur_derivee"] != 313
        and q["Q_DEGRE_MEDINOIS"]["valeur_derivee"] != 24434
    )

    # Cycles Trinité = RÉSULTAT du calcul depuis le point zéro
    eq = SYNCHRONISATION_HARMONIQUE_TRINITE
    dx = eq["cycles_distincts"]["soleil_dx"]["valeur_hz"]
    dy = eq["cycles_distincts"]["lune_dy"]["valeur_hz"]
    dz = eq["cycles_distincts"]["terre_dz"]["valeur_hz"]
    dt = eq["synchronisation"]["porteur_dt"]["valeur_hz"]
    couches["cycles_trinite_calcules_depuis_zero"] = (
        eq.get("origine_calcul") == "COMPLEXE_POINT_ZERO"
        and eq.get("pas_constantes_assignees") is True
        and dx > 0 and dy > 0 and dz > 0
        and abs(dt - (dx + dy + dz)) < 1e-6
        and eq["synchronisation"]["roue_phases_communes"]["ppcm"] == 12
        and eq["synchronisation"]["echelle_harmonique"]["domaine"] == "-9..+9"
        and abs(dx - 50027.8359375) < 1e-6
        and abs(dy - 46993.5) < 1e-6
        and abs(dz - 135000000.0) < 1e-6
    )

    # Trajectoire zéro → expansion présente
    traj = TRAJECTOIRE_ZERO_EXPANSION
    couches["trajectoire_zero_expansion"] = (
        traj.get("trajectoire") == "ZERO_VERS_EXPANSION"
        and traj.get("point_zero", {}).get("est_origine") is True
        and traj.get("aboutissement") == "EXPANSION_COMPLETE_DEPUIS_ZERO"
    )

    # Horloge déduite du même noyau (mêmes dx/dy/dz/dt)
    lien = HORLOGE_LOGIQUE.lien_avec_noyau()
    couches["horloge_deduite_du_noyau"] = (
        lien.get("deduite_de", "").endswith("calculer_cycles_trinite_depuis_zero")
        and lien.get("pas_valeurs_arbitraires") is True
        and abs(lien["constantes"]["dt"] - CYCLE_DT_KERNEL) < 1e-6
        and abs(lien["constantes"]["dt"] - HORLOGE_DEDUITE_DU_NOYAU["dt"]) < 1e-6
        and lien["q_degre_noyau"]["Q_mecois"] == 2304
        and lien["q_degre_noyau"]["Q_medinois"] == 1536
    )

    # Sync matière ↔ cinq familles
    try:
        sync = synchroniser_etats_matiere_aux_cinq_familles(charge_polarite)
        couches["sync_cinq_familles"] = (
            sync.ancre_m == 24434 and sync.la_table_est_complexe
        )
    except Exception:
        couches["sync_cinq_familles"] = False

    # Monade juste : unit + isolement + âme gouverne + helium de secours valide
    monade = MonadeSupreme.unit(charge_polarite).isoler()
    ame_ok = OMEGA_MONAD_SOUL.gouverne(monade.valeur_interne)
    monade_juste = bool(
        monade.est_isolee
        and ame_ok
        and monade.ame_universelle is OMEGA_MONAD_SOUL
        and MonadeSupreme.helium_inerte().est_helium_inerte
    )
    couches["⑤_monade_juste"] = monade_juste

    harmonie = all(couches.values())
    # Critère de vérité : Monade juste ⇒ PREUVE que l'ensemble est juste
    # (et réciproquement opérationnel : sans monade juste, pas de preuve scellée)
    preuve = monade_juste and harmonie

    if preuve:
        msg = (
            "🛡️🟢 MONADE JUSTE — PREUVE QUE TOUT EST JUSTE. "
            "Harmonie confirmée sur toutes les poupées russes."
        )
    elif monade_juste and not harmonie:
        msg = (
            "Monade structurellement juste mais harmonie de couche incomplète — "
            "preuve d'ensemble non scellée."
        )
    else:
        msg = "Monade non juste — aucune preuve d'ensemble ; harmonie non confirmée."

    return VerdictMonadeHarmoniePreuve(
        confirmer_harmonie=harmonie,
        monade_juste=monade_juste,
        preuve_ensemble_juste=preuve,
        couches_ok=couches,
        message=msg,
    )


def construire_poupees_russes(
    charge_polarite: int,
    catalogue: List[EtatMatiereRecense],
    sync: Any,
) -> Dict[str, Any]:
    """
    Construit l'arbre emboîté : chaque nœud a `contient` = poupée intérieure.
    Du plus petit (noyau) au plus grand (Monade).
    """
    quatre = [f for f in FAMILLES_CINQ if not f.est_la_table]
    complexe = next(f for f in FAMILLES_CINQ if f.est_la_table)
    verdict = confirmer_harmonie_et_prouver_justesse(charge_polarite)

    # ① Noyau — plus petit
    poupee_1 = {
        "poupée": 1,
        "taille": "plus_petit_noyau",
        "nom": "① INFORME — 4 familles de caractères",
        "contient": None,
        "contenu": {
            "familles": [
                {
                    "nom": f.nom,
                    "chiffre_m": f.chiffre_m,
                    "cardinalite": CARDINALITE_FAMILLE[f.nom],
                    "role": f.role,
                }
                for f in quatre
            ],
        },
    }

    # ② Emboîte ①
    poupee_2 = {
        "poupée": 2,
        "nom": "② COUCHE ÉTATS DE MATIÈRE",
        "contient": poupee_1,
        "contenu": {
            "poles": {"receptif": POLE_MATIERE_NEGATIF, "emissif": POLE_MATIERE_POSITIF},
            "ancre_m": ANCRE_M_SUBSTANCE,
            "decomposition_2_4_4_3_4": list(DECOMPOSITION_M_24434),
            "nb_etats_catalogues": len(catalogue),
            "sync": asdict(sync) if hasattr(sync, "__dataclass_fields__") else sync,
            "pas_des_cycles": True,
        },
    }

    # ③ — POINT ZÉRO (origine de tout calcul)
    poupee_3 = {
        "poupée": 3,
        "nom": "③ COMPLEXE = LA TABLE / POINT ZÉRO (origine de tout calcul)",
        "contient": poupee_2,
        "contenu": {
            "nom_famille": complexe.nom,
            "chiffre_m": complexe.chiffre_m,
            "est_la_table": True,
            "est_point_zero": True,
            "trajectoire": "ZERO_VERS_EXPANSION",
            "classe_calcul": MatriceLogiqueComplexe.__name__,
            "axes_calcules": list(MatriceLogiqueComplexe.FAMILLES),
            "expansion": TRAJECTOIRE_ZERO_EXPANSION.get("expansion", {}),
        },
    }

    # ④ Emboîte ③ — Q° dérivés de LA TABLE
    poupee_4 = {
        "poupée": 4,
        "nom": "④ DUALITÉ Q° MÉCOIS ⊕ / Q° MÉDINOIS ⊗ (dérivés de LA TABLE)",
        "contient": poupee_3,
        "contenu": {
            "symbole": "Q°",
            "ancrage": "ASTRO-Q°ODE / .ASTRO-Q°ODE",
            "origine_calcul": "COMPLEXE_POINT_ZERO",
            "rails": DUALITE_Q_DEGRE,
            "liaison": {
                "Q°_mecois_valeur_derivee": DUALITE_Q_DEGRE["Q_DEGRE_MECOIS"]["valeur_derivee"],
                "Q°_medinois_valeur_derivee": DUALITE_Q_DEGRE["Q_DEGRE_MEDINOIS"]["valeur_derivee"],
                "pas_C_313": True,
                "pas_M_24434": True,
                "pole_+313": "allié Q° mécois (matière)",
                "pole_-313": "allié Q° médinois (matière)",
            },
        },
    }

    # ⑤ Emboîte ④ — Monade ; cycles CALCULÉS depuis zéro, portés dans l'âme
    poupee_5 = {
        "poupée": 5,
        "taille": "plus_grand_enveloppe",
        "nom": "⑤ MONADE SUPRÊME — enveloppe / preuve de l'expansion",
        "contient": poupee_4,
        "contenu": {
            "classe": MonadeSupreme.__name__,
            "operations": ["unit/Monad(v)", "bind >>=", "isoler (( ))", "retour 0:HÉLIUM"],
            "reconcilie": ["Q° mécois", "Q° médinois"],
            "fonction_principale": "CONFIRMER_L_HARMONIE_DE_L_EXPANSION",
            "critere_de_verite": (
                "Si la Monade est juste, c'est la PREUVE que tout est juste."
            ),
            "verdict": asdict(verdict),
            "ame_omega_MONAD_SOUL": {
                "reflet": repr(OMEGA_MONAD_SOUL),
                "cycles_trinite_calcules_depuis_point_zero": SYNCHRONISATION_HARMONIQUE_TRINITE,
                "horloge_deduite_du_noyau": HORLOGE_LOGIQUE.lien_avec_noyau(),
                "doctrine": (
                    "dx/dy/dz et sync harmonique SORTENT du calcul de LA TABLE "
                    "(point zéro). Portés par l'âme de la Monade et lus par "
                    "HorlogeLogiqueMatriceMizan (pas de Hz arbitraires)."
                ),
            },
            "helium": MonadeSupreme.ETAT_HELIUM_INERTE,
        },
    }

    return {
        "metaphore": "POUPEES_RUSSES",
        "trajectoire_calcul": "ZERO_VERS_EXPANSION",
        "point_zero": "③ COMPLEXE = LA TABLE",
        "principe": (
            "Calcul : origine au point zéro COMPLEXE → expansion. "
            "Enveloppe : chaque poupée contient la précédente."
        ),
        "ordre_croissant": list(POUPEES_RUSSES_NOMS),
        "enveloppe_externe": poupee_5,
        "noyau_interne": poupee_1["nom"],
        "profondeur": 5,
        "charge_polarite_instantanee": charge_polarite,
        "preuve_monade": asdict(verdict),
        "trajectoire_zero_expansion": TRAJECTOIRE_ZERO_EXPANSION,
    }


@dataclass
class ArchitectureFigeeA128:
    """Instantané scellable — trajectoire zéro → expansion + poupées russes."""
    code_acte: str = "A134"
    horodatage_iso: str = field(
        default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    )
    hierarchie: Tuple[str, ...] = HIERARCHIE_FIGEE
    poupees_russes: Dict[str, Any] = field(default_factory=dict)
    trajectoire_zero_expansion: Dict[str, Any] = field(default_factory=dict)
    # Vues plates (compatibilité / introspection)
    socle_informe: Dict[str, Any] = field(default_factory=dict)
    couche_matiere: Dict[str, Any] = field(default_factory=dict)
    table_complexe: Dict[str, Any] = field(default_factory=dict)
    cycles_trinite_separes: Dict[str, Any] = field(default_factory=dict)
    dualite_mecquois_medinois: Dict[str, Any] = field(default_factory=dict)
    monade_supreme: Dict[str, Any] = field(default_factory=dict)
    sync_matiere_cinq_familles: Dict[str, Any] = field(default_factory=dict)
    catalogue_etats_matiere: List[Dict[str, Any]] = field(default_factory=list)
    decomposition_m_24434: Tuple[int, ...] = DECOMPOSITION_M_24434
    succes: bool = True


class ArchitectureInformeCoucheMatiereTable:
    """
    Architecture : POINT ZÉRO = COMPLEXE → EXPANSION
      (matière, cycles Trinité calculés, Q° dérivés, Monade preuve).
    Enveloppe poupées russes conservée pour l'imbrication.
    """

    def __init__(self) -> None:
        self.nom = "ARCHITECTURE_ZERO_EXPANSION_IMAM8MAHDI"
        self.version = "3.0.0-A134"

    def figer(self, charge_polarite: int = POLE_MATIERE_POSITIF, persister: bool = True) -> ArchitectureFigeeA128:
        assert verifier_decomposition_m_24434()
        sync = synchroniser_etats_matiere_aux_cinq_familles(charge_polarite)
        catalogue = cataloguer_tous_les_etats_de_matiere()
        nest = construire_poupees_russes(charge_polarite, catalogue, sync)
        traj = construire_trajectoire_zero_expansion(charge_polarite)

        p5 = nest["enveloppe_externe"]
        p4 = p5["contient"]
        p3 = p4["contient"]
        p2 = p3["contient"]
        p1 = p2["contient"]

        arch = ArchitectureFigeeA128(
            poupees_russes=nest,
            trajectoire_zero_expansion=traj,
            socle_informe={"poupée": 1, **p1["contenu"]},
            couche_matiere={"poupée": 2, **{k: v for k, v in p2["contenu"].items() if k != "sync"}},
            table_complexe={"poupée": 3, "point_zero": True, **{k: v for k, v in p3["contenu"].items() if k != "expansion"}},
            dualite_mecquois_medinois={"poupée": 4, **p4["contenu"]},
            monade_supreme={"poupée": 5, **p5["contenu"]},
            cycles_trinite_separes=SYNCHRONISATION_HARMONIQUE_TRINITE,
            sync_matiere_cinq_familles=asdict(sync),
            catalogue_etats_matiere=[asdict(e) for e in catalogue],
            succes=True,
        )

        if persister:
            DOSSIER_MEMOIRE.mkdir(parents=True, exist_ok=True)
            FICHIER_BILAN.write_text(
                json.dumps(asdict(arch), indent=2, ensure_ascii=False, default=str),
                encoding="utf-8",
            )
        return arch

    def formater_rapport(self, arch: ArchitectureFigeeA128 | None = None) -> str:
        a = arch or self.figer(persister=False)
        sync = a.cycles_trinite_separes.get("synchronisation", {})
        cycles = a.cycles_trinite_separes.get("cycles_distincts", {})
        lignes = [
            "=" * 78,
            f"  {self.nom} v{self.version} — Acte {a.code_acte}",
            "  TRAJECTOIRE : ZÉRO (COMPLEXE) → EXPANSION",
            "=" * 78,
            "  ● POINT ZÉRO = COMPLEXE = LA TABLE",
            "      → ① 4 axes",
            "      → ② états de matière (±313 / M=24434)",
            "      → ③ cycles Trinité (calculés) + sync harmonique",
            "      → ④ Q° mécois ⊕ / médinois ⊗ (dérivés)",
            "      → ⑤ MONADE = preuve de justesse de l'expansion",
            "-" * 78,
            f"  dx Soleil = {cycles.get('soleil_dx', {}).get('valeur_hz')}",
            f"  dy Lune   = {cycles.get('lune_dy', {}).get('valeur_hz')}",
            f"  dz Terre  = {cycles.get('terre_dz', {}).get('valeur_hz')}",
            f"  dt sync   = {sync.get('porteur_dt', {}).get('valeur_hz')}",
            f"  phases    = {sync.get('roue_phases_communes', {}).get('domaine')}",
            f"  h19       = {sync.get('echelle_harmonique', {}).get('domaine')}",
            "-" * 78,
        ]
        preuve = a.poupees_russes.get("preuve_monade", {})
        lignes.extend(
            [
                f"  Harmonie : {preuve.get('confirmer_harmonie')}",
                f"  Monade juste : {preuve.get('monade_juste')}",
                f"  Preuve ensemble : {preuve.get('preuve_ensemble_juste')}",
                f"  {preuve.get('message', '')}",
                "=" * 78,
            ]
        )
        return "\n".join(lignes)


ARCHITECTURE_FIGEE = ArchitectureInformeCoucheMatiereTable()


if __name__ == "__main__":
    print(ARCHITECTURE_FIGEE.formater_rapport())
