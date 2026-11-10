# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""Espace disque : équations d'occupation, de duplication et de récupération.

Le problème est mesuré, pas narré. Le volume système est à saturation et la
masse est localisable : un instantané unique
(`outils/collecter_instantane_espace_disque.py`, empreint) donne la répartition,
et ce module ne fait que combiner ces relevés par des routes indépendantes :
seconde API de volume, second dénombrement, re-stat de journal, identité
algébrique, partitions croisées.

Chaque contrôle retrouve sa valeur autrement que l'équation qui l'affiche.
Aucun octet n'est supprimé ici : le module calcule ce qui est récupérable, le
risque attaché à chaque catégorie et la marge qui resterait. La mise en œuvre
est une décision distincte, bornée par EQ-13 : rien de scellé ne doit être
touchable.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

RACINE_SYSTEME = Path(__file__).resolve().parents[1]
RACINE_DEPOT = RACINE_SYSTEME.parent
CHEMIN_INSTANTANE = RACINE_SYSTEME / "resultats" / "oeuvre_universelle" / "espace_disque_instantane.json"
CHEMIN_MANIFESTE = RACINE_SYSTEME / "resultats" / "oeuvre_universelle" / "manifeste_anteriorite.json"
COPIE_SOI = RACINE_DEPOT / "_AL_MIZAN_COPIE_SOI"
DIR_HISTORIQUE = COPIE_SOI / "historique"
DIR_ARCHIVES = DIR_HISTORIQUE / "_archives"
DIR_COURANTE = COPIE_SOI / "courante"

GO = 1024 ** 3
RHO_MARGE = 0.10          # convention : 10 % du volume reste libre
HORIZON_JOURS = 30.0
FENETRE_JOURS = 1.0       # fenêtre de mesure du taux de copies
GARDE_FRAIS = 5           # copies les plus récentes conservées, en plus de l'ancre quotidienne
ANCRES_JOURS = 30         # fenêtre de l'ancre quotidienne, alignée sur conscience_logique/sauvegarde_soi.py
MAX_STAMPS = 48           # plafond dur du nombre de snapshots conservés
MAX_OCTETS_COPIES = 2 * GO  # plafond dur du volume conservé dans historique/
CATEGORIES_RECUPERABLES = ("cache_python", "temporaire_qoder", "historiques_hors_retention")

SOURCE = {
    "type": "mesure locale sur le poste de développement, volume C:",
    "instantane": str(CHEMIN_INSTANTANE),
    "collecteur": "outils/collecter_instantane_espace_disque.py",
    "manifeste": str(CHEMIN_MANIFESTE),
    "transversale": "aucune transcription externe ; 0 source vidéo",
}

STATUTS = {
    "OPÉRATIONNEL": "identité ou relevé reproductible sur ce poste",
    "SIMULÉ": "projection sous convention déclarée (taux constant, rho fixe)",
    "SPÉCIFIÉ": "choix de doctrine non démontré, exposé comme tel",
}


def _iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _eq(id_: str, chemin: str, formule: str, resultat: str, statut: str,
        detail: Any) -> Dict[str, Any]:
    return {"id": id_, "chemin": chemin, "formule": formule, "resultat": resultat,
            "statut": statut, "detail": detail}


def _c(id_: str, nom: str, attendu: Any, obtenu: Any, tol: Any = 0.0) -> Dict[str, Any]:
    return {"id": id_, "nom": nom, "attendu": _s(attendu), "obtenu": _s(obtenu),
            "ok": _egal(attendu, obtenu, tol)}


def _s(v: Any) -> str:
    """Rendu texte comparable : meme format des deux cotes de chaque controle."""
    if isinstance(v, bool):
        return "vrai" if v else "faux"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        return "infini" if v == float("inf") else f"{v:.6f}"
    if isinstance(v, list):
        return " | ".join(_s(x) for x in v) if v else "aucun element"
    return str(v)


def _egal(a: Any, b: Any, tol: Any = 0.0) -> bool:
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return False
        tols = tol if isinstance(tol, list) else [tol] * len(a)
        return all(_egal(x, y, z) for x, y, z in zip(a, b, tols))
    if isinstance(a, (int, float)) and not isinstance(a, bool) \
            and isinstance(b, (int, float)) and not isinstance(b, bool):
        # inf - inf = nan : la difference ne decide pas de deux infinis egaux, et une
        # tolerance infinie (1e-9 * inf) accepterait n'importe quoi. L'egalite stricte
        # tranche d'abord ; une tolerance non finie ne peut plus que la confirmer.
        if a == b:
            return True
        if abs(tol) == float("inf"):
            return False
        return abs(a - b) <= tol
    return a == b


def _go(octets: float) -> str:
    return f"{octets / GO:.3f} Go"


def _j(v: float) -> str:
    """Rendu texte d'un horizon en jours.

    Une cadence nulle rend J = +infini : « inf » dans une page publiée serait un reste
    de formatage, pas une affirmation. Le texte dit ici ce que l'infini veut dire.
    """
    return "infini, aucune copie sur la fenêtre de 24 h" if v == float("inf") else f"{v:.2f} j"


# ---------------------------------------------------------------------------
# ROUTES DE MESURE
# ---------------------------------------------------------------------------

def mesurer_volume_python() -> Dict[str, int]:
    t, u, f = shutil.disk_usage("C:/")
    return {"total": t, "utilise": u, "libre": f}


def mesurer_volume_wmi() -> Dict[str, Any]:
    """Seconde API (Win32_LogicalDisk via PowerShell) : route indépendante de shutil."""
    cmd = [
        "powershell", "-NoProfile", "-Command",
        "$d = Get-CimInstance Win32_LogicalDisk -Filter \"DeviceID='C:'\"; $d.Size; $d.FreeSpace",
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except Exception as exc:
        return {"erreur": type(exc).__name__}
    nbrs = [int(x) for x in (r.stdout or "").split() if x.strip().isdigit()]
    if len(nbrs) < 2:
        return {"erreur": f"sortie_inattendue_rc{r.returncode}"}
    return {"total": nbrs[0], "libre": nbrs[1], "utilise": nbrs[0] - nbrs[1]}


def charger_instantane() -> Dict[str, Any]:
    if not CHEMIN_INSTANTANE.exists():
        raise FileNotFoundError(
            f"instantané absent : lancer outils/collecter_instantane_espace_disque.py ({CHEMIN_INSTANTANE})"
        )
    return json.loads(CHEMIN_INSTANTANE.read_text(encoding="utf-8"))


def empreinte_instantane(donnees: Dict[str, Any]) -> str:
    """Rejoue le scellement du collecteur : canonique, sans la propre empreinte."""
    corps = {k: v for k, v in donnees.items() if k != "empreinte_snapshot_sha256"}
    texte = json.dumps(corps, ensure_ascii=False, indent=2, sort_keys=True)
    return hashlib.sha256(texte.encode("utf-8")).hexdigest()


def fractions_occupation(inst: Dict[str, Any]) -> Dict[str, Any]:
    """Fractions internes au dépôt : chaque partition est normalisée par S_dépôt."""
    s_depot = inst["depot"]["octets_total"]
    tot = inst["volumes"]["C:"]["total_octets"]
    f_classe = {k: v / s_depot for k, v in inst["depot"]["octets_par_classe"].items()}
    f_niveau1 = {k: v / s_depot for k, v in inst["depot"]["octets_par_niveau1"].items()}
    return {"total_volume": tot, "octets_depot": s_depot,
            "part_du_volume": s_depot / tot,
            "classes": f_classe, "niveau1": f_niveau1,
            "somme_classes": sum(f_classe.values()), "somme_niveau1": sum(f_niveau1.values())}


def denombrer_historiques() -> Dict[str, Any]:
    """Dénombrement exact : une copie = un nom qui est un instant UTC ; le reste est compté à part."""
    repertoires: List[str] = []
    if DIR_HISTORIQUE.is_dir():
        with os.scandir(DIR_HISTORIQUE) as it:
            repertoires = sorted(e.name for e in it if e.is_dir(follow_symlinks=False))
    noms = [n for n in repertoires if _est_stamp(n)]
    hors = [n for n in repertoires if not _est_stamp(n)]
    par_courant = sorted(p.name for p in DIR_HISTORIQUE.iterdir()
                         if p.is_dir() and not p.is_symlink()) if DIR_HISTORIQUE.is_dir() else []
    parse = [datetime.strptime(n, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc) for n in noms]
    seuil = datetime.now(timezone.utc) - timedelta(days=FENETRE_JOURS)
    arch_o, arch_f = taille_arbre(DIR_ARCHIVES) if DIR_ARCHIVES.is_dir() else (0, 0)
    return {
        "repertoire": str(DIR_HISTORIQUE),
        "noms": noms,
        "total": len(noms),
        "uniques": len(set(noms)),
        "repertoires_n": len(repertoires),
        "hors_format": hors,
        "hors_format_n": len(hors),
        "route_independente_n": len(par_courant),
        "valides_par_syntaxe": sum(
            1 for n in noms
            if len(n) == 16 and n[8] == "T" and n[15] == "Z"
            and n[:8].isdigit() and n[9:15].isdigit()
        ),
        "jours_utc": sorted({n[:8] for n in noms}),
        "premier": parse[0].strftime("%Y-%m-%dT%H:%M:%SZ") if parse else None,
        "dernier": parse[-1].strftime("%Y-%m-%dT%H:%M:%SZ") if parse else None,
        "span_jours": (parse[-1] - parse[0]).total_seconds() / 86400.0 if len(parse) > 1 else 0.0,
        "dans_fenetre_24h": sum(1 for p in parse if p >= seuil),
        "archives": {"present": DIR_ARCHIVES.is_dir(), "octets": arch_o, "fichiers": arch_f},
    }


def _est_stamp(nom: str) -> bool:
    """Un dossier d'historique n'est une copie que si son nom est un instant UTC."""
    if len(nom) != 16 or not nom.endswith("Z"):
        return False
    try:
        datetime.strptime(nom, "%Y%m%dT%H%M%SZ")
    except ValueError:
        return False
    return True


def taille_arbre(racine: Path) -> Tuple[int, int]:
    """(octets, fichiers) par parcours propre, sans suivre les liens."""
    octets = fichiers = 0
    pile = [racine]
    while pile:
        dossier = pile.pop()
        try:
            entrees = list(os.scandir(dossier))
        except OSError:
            continue
        for e in entrees:
            try:
                if e.is_symlink():
                    continue
                if e.is_dir(follow_symlinks=False):
                    pile.append(Path(e.path))
                elif e.is_file(follow_symlinks=False):
                    octets += e.stat().st_size
                    fichiers += 1
            except OSError:
                continue
    return octets, fichiers


def mesurer_copies() -> Dict[str, Any]:
    """Un seul parcours groupé : taille de chaque historique, puis agrégats."""
    par_stamp: List[Dict[str, Any]] = []
    hors_format: List[str] = []
    if DIR_HISTORIQUE.is_dir():
        with os.scandir(DIR_HISTORIQUE) as it:
            for e in sorted(it, key=lambda x: x.name):
                if not e.is_dir(follow_symlinks=False):
                    continue
                if _est_stamp(e.name):
                    o, f = taille_arbre(DIR_HISTORIQUE / e.name)
                    par_stamp.append({"stamp": e.name, "octets": o, "fichiers": f})
                else:
                    hors_format.append(e.name)
    o_cour, f_cour = taille_arbre(DIR_COURANTE) if DIR_COURANTE.is_dir() else (0, 0)
    s_hist = sum(s["octets"] for s in par_stamp)
    arch_o, arch_f = taille_arbre(DIR_ARCHIVES) if DIR_ARCHIVES.is_dir() else (0, 0)
    return {
        "courante_octets": o_cour,
        "courante_fichiers": f_cour,
        "historiques": par_stamp,
        "historiques_octets": s_hist,
        "historiques_fichiers": sum(s["fichiers"] for s in par_stamp),
        "total_octets": o_cour + s_hist,
        "hors_format": hors_format,
        "archives_octets": arch_o,
        "archives_fichiers": arch_f,
        "total_avec_archives_octets": o_cour + s_hist + arch_o,
    }


def politique_retention(cop: Dict[str, Any], hist: Dict[str, Any]) -> Dict[str, Any]:
    """Garde la copie courante, une ancre par jour UTC sur ANCRES_JOURS, les K plus récentes,
    sous plafond dur de MAX_STAMPS copies et MAX_OCTETS_COPIES octets.

    Règle identique à `conscience_logique/sauvegarde_soi.py -> appliquer_retention_historique`,
    posée ici comme convention de calcul avant toute suppression.
    """
    tailles = {s["stamp"]: s["octets"] for s in cop["historiques"]}
    noms = [n for n in hist["noms"] if _est_stamp(n)]
    maintenant = datetime.now(timezone.utc)
    seuil = maintenant - timedelta(days=ANCRES_JOURS)
    ancres: List[str] = []
    vus: set = set()
    for n in reversed(noms):
        t = datetime.strptime(n, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
        if t < seuil:
            break
        jour = n[:8]
        if jour in vus:
            continue
        vus.add(jour)
        ancres.append(n)
    garde = set(ancres)
    if GARDE_FRAIS:
        garde |= set(noms[-GARDE_FRAIS:])
    conserves = sorted(garde)
    vagues: List[str] = [n for n in noms if n not in garde]
    while conserves and (
        len(conserves) > MAX_STAMPS
        or sum(tailles.get(n, 0) for n in conserves) > MAX_OCTETS_COPIES
    ):
        vagues.append(conserves.pop(0))
    hors = [n for n in noms if n not in set(conserves)]
    return {
        "regle": (
            f"courante + 1 ancre par jour UTC sur {ANCRES_JOURS} j ({len(vus)} jours) "
            f"+ {GARDE_FRAIS} plus récentes, plafonnée à {MAX_STAMPS} copies et "
            f"{MAX_OCTETS_COPIES / GO:.0f} Go"
        ),
        "jours_ancres": len(vus),
        "gardees": conserves,
        "gardees_n": len(conserves),
        "gardees_octets": sum(tailles.get(n, 0) for n in conserves),
        "hors_retention": hors,
        "hors_retention_n": len(hors),
        "hors_retention_octets": sum(tailles.get(n, 0) for n in hors),
    }


def recontroler_journal(inst: Dict[str, Any]) -> Dict[str, Any]:
    """Re-stat live du plus lourd des journaux append-only, par deux routes indépendantes.

    Le journal grossit en continu (~5 Mo/j, EQ-07) : l'instantané du collecteur est
    daté, la lecture est postérieure. Egaliser les deux décomptes serait une assertion
    sur une horloge, pas sur une identité. Le comptage live est donc refait sur un même
    tampon figé par deux routes qui ne partagent rien (itérateur de lignes vs dénombrement
    des sauts ; taille vs somme des longueurs de lignes), et la dérive
    instantané → live est publiée comme donnée, avec la seule propriété réellement
    vérifiable sur un append-only : la croissance monotone.
    """
    jr = inst.get("journaux") or []
    if not jr:
        return {"erreur": "journal_absent_de_l_instantane"}
    j0 = max(jr, key=lambda j: j["octets"])
    p = Path(j0["chemin"])
    if not p.is_file():
        return {"erreur": "journal_ilisible", "chemin": str(p)}
    with p.open("rb") as f:
        data = f.read()
    lignes_iterateur = sum(1 for _ in io.BytesIO(data))
    lignes_sauts = data.count(b"\n") + (1 if data and not data.endswith(b"\n") else 0)
    octets_sommes = sum(len(b) for b in data.splitlines(True))
    age_j = max((time.time() - p.stat().st_ctime) / 86400.0, 1e-6)
    return {
        "chemin": str(p),
        "instantane": {"octets": j0["octets"], "lignes": j0["lignes"]},
        "live": {"octets": len(data), "lignes": lignes_iterateur},
        "live_seconde_route": {"octets": octets_sommes, "lignes": lignes_sauts},
        "octets_par_ligne_live": len(data) / lignes_iterateur if lignes_iterateur else 0.0,
        "octets_par_jour_live": len(data) / age_j,
        "age_jours_live": age_j,
        "drift_octets": len(data) - j0["octets"],
        "drift_lignes": lignes_iterateur - j0["lignes"],
    }


def projection_saturation(copies_par_jour: float, taille_moyenne: float, libre: int) -> Dict[str, Any]:
    conso_j = copies_par_jour * taille_moyenne
    return {
        "conso_par_jour": conso_j,
        "jours_avant_saturation": libre / conso_j if conso_j > 0 else float("inf"),
        "jours_avant_saturation_ordre_inverse": (libre / taille_moyenne) / copies_par_jour
        if (copies_par_jour > 0 and taille_moyenne > 0) else float("inf"),
        "masse_horizon": conso_j * HORIZON_JOURS,
        "masse_horizon_factorisee": copies_par_jour * (taille_moyenne * HORIZON_JOURS),
    }


def categories_recuperables(inst: Dict[str, Any], retention: Dict[str, Any]) -> Dict[str, int]:
    classes = inst["depot"]["octets_par_classe"]
    return {
        "cache_python": int(classes.get("cache_python", 0)),
        "temporaire_qoder": int(classes.get("temporaire_qoder", 0)),
        "historiques_hors_retention": int(retention["hors_retention_octets"]),
    }


def marge_securite(total: int, libre: int) -> Dict[str, float]:
    seuil = RHO_MARGE * total
    return {"seuil": seuil, "deficit": max(0.0, seuil - libre), "rho": RHO_MARGE}


def solde_apres(libre: int, r: float) -> int:
    return libre + r


def rendement(r: float, total: float) -> float:
    return r / total if total else 0.0


def secteurs_scelles() -> Dict[str, Any]:
    """Deux prédicats indépendants d'appartenance à une catégorie nettoyable."""
    if not CHEMIN_MANIFESTE.exists():
        return {"erreur": "manifeste_absent", "chemin": str(CHEMIN_MANIFESTE)}
    man = json.loads(CHEMIN_MANIFESTE.read_text(encoding="utf-8"))
    chemins = [str(e["chemin"]).replace("\\", "/") for e in man.get("fichiers", [])]

    # Route 1 : le classificateur du collecteur, appliqué aux chemins du manifeste.
    if str(RACINE_SYSTEME / "outils") not in sys.path:
        sys.path.insert(0, str(RACINE_SYSTEME / "outils"))
    import collecter_instantane_espace_disque as coll

    classes_touchees = {"cache_python", "temporaire_qoder", "copie_de_soie"}
    par_classe = [f"{c} -> {coll.classe_de(c)}" for c in chemins
                  if coll.classe_de(c) in classes_touchees]

    # Route 2 : règle géométrique de préfixe, sans import du collecteur.
    racines_nettoyables = ("_AL_MIZAN_COPIE_SOI/", "__pycache__/", ".qoder/", "memoire_aq/")
    par_prefixe = [c for c in chemins
                   if c.startswith(racines_nettoyables)
                   or any(f"/{r}" in f"/{c}" for r in racines_nettoyables)]
    return {
        "manifeste": str(CHEMIN_MANIFESTE),
        "nb_fichiers_manifeste": len(chemins),
        "racine_merkle_sha256": man.get("racine_merkle_sha256"),
        "genere_le_utc": man.get("genere_le_utc"),
        "par_classe": par_classe,
        "par_prefixe": par_prefixe,
        "racines_testees": list(racines_nettoyables),
    }


# ---------------------------------------------------------------------------
# ASSEMBLAGE
# ---------------------------------------------------------------------------

def resoudre(instantane: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    inst = instantane or charger_instantane()
    dep = inst["depot"]
    vol = inst["volumes"]["C:"]
    eqs: List[Dict[str, Any]] = []
    controles: List[Dict[str, Any]] = []

    t, u, l = vol["total_octets"], vol["utilise_octets"], vol["libre_octets"]

    # EQ-01 — conservation du volume
    py = mesurer_volume_python()
    wmi = mesurer_volume_wmi()
    eqs.append(_eq(
        "EQ-01", "espace_disque.py → mesurer_volume_python() → C01",
        "T = U + L",
        f"T={_go(t)}, U={_go(u)}, L={_go(l)} ({100 * u / t:.1f} % utilisé)",
        "OPÉRATIONNEL",
        {"instantane": {"T": t, "U": u, "L": l}, "shutil_live": py, "wmi_live": wmi},
    ))
    if "erreur" in wmi:
        controles.append(_c("C01", "seconde API de volume injoignable", "wmi_injoignable", str(wmi["erreur"])))
    else:
        controles.append(_c(
            "C01", "PowerShell Win32_LogicalDisk retrouve T et L de shutil",
            [wmi["total"], wmi["libre"]], [py["total"], py["libre"]], tol=[GO // 10, GO // 10],
        ))

    # EQ-02 — empreinte de l'instantané, témoin rejouable
    e_lue = inst.get("empreinte_snapshot_sha256", "")
    e_calculee = empreinte_instantane(inst)
    genere = datetime.strptime(inst["genere_le_utc"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    age_min = (datetime.now(timezone.utc) - genere).total_seconds() / 60.0
    eqs.append(_eq(
        "EQ-02", "espace_disque.py → empreinte_instantane() → C02",
        "E = SHA-256(canonique(instantané) sans E)",
        f"{e_lue} (instantané du {inst['genere_le_utc']}, vieux de {age_min:.1f} min)",
        "OPÉRATIONNEL",
        {"genere_le_utc": inst["genere_le_utc"], "duree_collecte_s": inst["duree_collecte_s"],
         "bornes": inst["bornes"]},
    ))
    controles.append(_c("C02", "re-hachage du fichier rejoue l'empreinte scellée", e_lue, e_calculee))

    # EQ-03 — fermeture des deux partitions du dépôt
    somme_classes = sum(dep["octets_par_classe"].values())
    somme_niveau1 = sum(dep["octets_par_niveau1"].values())
    eqs.append(_eq(
        "EQ-03", "espace_disque.py → charger_instantane() → C03",
        "S_dépôt = Σ_classes S_classe = Σ_niveau1 S_i",
        f"Σ_classes={_go(somme_classes)}, Σ_niveau1={_go(somme_niveau1)}, "
        f"annonce={_go(dep['octets_total'])} sur {dep['fichiers']} fichiers",
        "OPÉRATIONNEL",
        {"classes": dep["octets_par_classe"],
         "niveau1_top": dict(sorted(dep["octets_par_niveau1"].items(), key=lambda kv: -kv[1])[:6])},
    ))
    controles.append(_c("C03", "deux partitions indépendantes du même parcours saturent le total",
                        somme_classes, somme_niveau1))

    # EQ-04 — fractions d'occupation normalisées
    fr = fractions_occupation(inst)
    dom_classe = max(fr["classes"].items(), key=lambda kv: kv[1])
    eqs.append(_eq(
        "EQ-04", "espace_disque.py → fractions_occupation() → C04",
        "f_i = S_i / S_dépôt ; Σ_i f_i = 1 sur une partition couvrante",
        f"classe dominante {dom_classe[0]} = {100 * dom_classe[1]:.2f} % du dépôt "
        f"({_go(dom_classe[1] * fr['octets_depot'])}) ; dépôt = {100 * fr['part_du_volume']:.2f} % du volume C:",
        "OPÉRATIONNEL",
        {"fractions_classes": dict(sorted(fr["classes"].items(), key=lambda kv: -kv[1])),
         "fractions_niveau1_top": dict(sorted(fr["niveau1"].items(), key=lambda kv: -kv[1])[:6]),
         "max_classe": [dom_classe[0], dom_classe[1]],
         "max_niveau1": max(fr["niveau1"].items(), key=lambda kv: kv[1]),
         "normalisateur": "octets_total du dépôt, pas le volume : les deux partitions ne couvrent que le dépôt",
         "remarque": "un maximum de classe et un maximum de répertoire de premier niveau ne sont pas la "
                     "même grandeur : une classe rassemble plusieurs répertoires, la concordance de leurs "
                     "maxima dépend de l'état du dépôt, pas d'une identité"},
    ))
    controles.append(_c(
        "C04", "Σ f_i = 1 sur les deux partitions ; la fraction dominante rend l'octet de sa classe",
        [fr["somme_classes"], fr["somme_niveau1"], max(dep["octets_par_classe"].values())],
        [1.0, 1.0, dom_classe[1] * fr["octets_depot"]], tol=[1e-9, 1e-9, 1.0],
    ))

    # EQ-05 — dénombrement des copies historiques
    hist = denombrer_historiques()
    eqs.append(_eq(
        "EQ-05", "espace_disque.py → denombrer_historiques() → C05",
        "N = |historique| ; chaque nom est un instant UTC unique",
        f"N={hist['total']} copies ({hist['uniques']} uniques) sur {len(hist['jours_utc'])} jours UTC, "
        f"du {hist['premier']} au {hist['dernier']} ({hist['span_jours']:.2f} j)",
        "OPÉRATIONNEL",
        {"repertoire": hist["repertoire"], "total_live": hist["total"],
         "repertoires_total": hist["repertoires_n"], "hors_format": hist["hors_format"],
         "total_instantane": inst["copie_de_soie"]["historiques"],
         "derive_live_minus_instantane": hist["total"] - inst["copie_de_soie"]["historiques"],
         "jours_utc": hist["jours_utc"], "archives": hist["archives"]},
    ))
    controles.append(_c(
        "C05", "dénombrement autonome : clôture du répertoire, unicité, tri, second prédicat d'horodatage",
        [hist["route_independente_n"] - hist["hors_format_n"], hist["total"], True, hist["total"]],
        [hist["repertoires_n"] - hist["hors_format_n"], hist["uniques"],
         hist["noms"] == sorted(hist["noms"]), hist["valides_par_syntaxe"]],
    ))

    # EQ-06 — facteur de duplication des copies de soi
    cop = mesurer_copies()
    n_hist = len(cop["historiques"])
    s_moyen = (cop["historiques_octets"] / n_hist) if n_hist else 0.0
    duplication = cop["total_octets"] / max(1, cop["courante_octets"])
    eqs.append(_eq(
        "EQ-06", "espace_disque.py → mesurer_copies() → C06",
        "D = (courante + Σ historiques) / courante ; s̄ = Σ historiques / N",
        f"D = {duplication:.3f} pour {n_hist} historiques de s̄ = {_go(s_moyen)} "
        f"(courante {_go(cop['courante_octets'])}, total copies {_go(cop['total_octets'])}, "
        f"archives {_go(cop['archives_octets'])})",
        "OPÉRATIONNEL",
        {"courante_octets": cop["courante_octets"], "historiques_octets": cop["historiques_octets"],
         "historiques_fichiers": cop["historiques_fichiers"],
         "archives_octets": cop["archives_octets"], "hors_format": cop["hors_format"],
         "par_stamp_extremes": cop["historiques"][:2] + cop["historiques"][-2:]},
    ))
    controles.append(_c(
        "C06", "N × s̄ retrouvé par la somme directe des stamps, puis clôture stamps+courante+archives",
        [s_moyen * n_hist, cop["historiques_octets"] + cop["courante_octets"] + cop["archives_octets"]],
        [float(cop["historiques_octets"]), float(cop["total_avec_archives_octets"])],
        tol=1.0,
    ))

    # EQ-07 — masse et densité du journal append-only dominant
    jr = recontroler_journal(inst)
    eqs.append(_eq(
        "EQ-07", "espace_disque.py → recontroler_journal() → C07",
        "μ_j = octets_j / lignes_j ; φ_j = octets_j / âge_j ; lignes = #{sauts} + fin sans saut",
        ("journal absent" if "erreur" in jr else
         f"{_go(jr['live']['octets'])} en {jr['live']['lignes']} lignes : μ = {jr['octets_par_ligne_live']:.2f} o/ligne, "
         f"φ = {jr['octets_par_jour_live'] / 1e6:.2f} Mo/j sur {jr['age_jours_live']:.2f} j ; "
         f"dérive depuis l'instantané du collecteur : +{jr['drift_octets']} o / +{jr['drift_lignes']} lignes"),
        "OPÉRATIONNEL",
        jr,
    ))
    if "erreur" in jr:
        controles.append(_c("C07", "journal non re-contrôlable", "re-stat impossible", jr["erreur"]))
    else:
        o_j = jr["live"]["octets"]
        controles.append(_c(
            "C07", "double comptage du meme tampon (sauts vs iterateur, somme des lignes vs taille), "
                   "identites mu·L = O et phi·t = O, croissance append-only vs instantane",
            [jr["live_seconde_route"]["lignes"], jr["live_seconde_route"]["octets"],
             jr["octets_par_ligne_live"] * jr["live"]["lignes"],
             jr["octets_par_jour_live"] * jr["age_jours_live"], True],
            [jr["live"]["lignes"], o_j, o_j, o_j,
             jr["live"]["octets"] >= jr["instantane"]["octets"]
             and jr["live"]["lignes"] >= jr["instantane"]["lignes"]],
            tol=[0.0, 0.0, 1e-9 * max(1.0, o_j), 1e-9 * max(1.0, o_j), 0.0],
        ))

    # EQ-08 — cadence des copies et projection à horizon
    r_span = (hist["total"] / hist["span_jours"]) if hist["span_jours"] > 0 else 0.0
    r_fenetre = hist["dans_fenetre_24h"] / FENETRE_JOURS
    proj = projection_saturation(r_fenetre, s_moyen, l)       # cadence récente : cas le plus défavorable
    proj_span = projection_saturation(r_span, s_moyen, l)     # cadence moyenne depuis la première copie
    eqs.append(_eq(
        "EQ-08", "espace_disque.py → projection_saturation() → C08",
        "r = N_fenêtre / Δt_fenêtre ; φ = r·s̄ ; J = L / φ",
        f"r_fenêtre = {r_fenetre:.1f} copies/j sur {FENETRE_JOURS:.0f} j "
        f"({hist['dans_fenetre_24h']} copies) contre r_span = {r_span:.1f}/j sur {hist['span_jours']:.2f} j "
        f"→ φ = {_go(proj['conso_par_jour'])}/j ; J = {_j(proj['jours_avant_saturation'])} "
        f"(J_span = {_j(proj_span['jours_avant_saturation'])}) ; "
        f"+{_go(proj['masse_horizon'])} à {HORIZON_JOURS:.0f} j",
        "SIMULÉ",
        {"copies_par_jour_fenetre": r_fenetre, "copies_par_jour_span": r_span,
         "fenetre_jours": FENETRE_JOURS, "projection_fenetre": dict(proj),
         "projection_span": dict(proj_span), "taille_moyenne_stamp": s_moyen,
         "hypothese": "cadence et taille moyennes constantes ; la cadence récente domine largement la moyenne"},
    ))
    controles.append(_c(
        "C08", "J = L/(r·s̄) = (L/s̄)/r et masse = r·(s̄·30) sur les deux cadences",
        [proj["jours_avant_saturation"], proj_span["jours_avant_saturation"],
         proj["masse_horizon"], proj_span["masse_horizon"]],
        [proj["jours_avant_saturation_ordre_inverse"], proj_span["jours_avant_saturation_ordre_inverse"],
         proj["masse_horizon_factorisee"], proj_span["masse_horizon_factorisee"]],
        tol=[1e-9 * max(1.0, proj["jours_avant_saturation"]),
             1e-9 * max(1.0, proj_span["jours_avant_saturation"]),
             1e-9 * max(1.0, proj["masse_horizon"]),
             1e-9 * max(1.0, proj_span["masse_horizon"])],
    ))

    # EQ-09 — récupérable par catégorie sous politique de rétention
    retention = politique_retention(cop, hist)
    cat = categories_recuperables(inst, retention)
    R = sum(cat.values())
    eqs.append(_eq(
        "EQ-09", "espace_disque.py → categories_recuperables() → C09",
        f"R = caches + temporaires + Σ(stamps hors rétention) ; rétention : {retention['regle']}",
        f"R = {_go(R)} (caches {_go(cat['cache_python'])}, temporaires {_go(cat['temporaire_qoder'])}, "
        f"{retention['hors_retention_n']} historiques hors rétention {_go(cat['historiques_hors_retention'])})",
        "SIMULÉ",
        {"categories": cat, "regle": retention["regle"],
         "gardees_n": retention["gardees_n"], "jours_ancres": retention["jours_ancres"],
         "gardees_octets": retention["gardees_octets"]},
    ))
    controles.append(_c(
        "C09", "partition des copies : gardées + courante + hors rétention = total mesuré",
        retention["gardees_octets"] + cop["courante_octets"] + retention["hors_retention_octets"],
        cop["total_octets"],
    ))

    # EQ-10 — marge de sécurité
    ms = marge_securite(t, l)
    ms_live = marge_securite(py["total"], py["libre"])
    ms_wmi = marge_securite(wmi["total"], wmi["libre"]) if "erreur" not in wmi else None
    eqs.append(_eq(
        "EQ-10", "espace_disque.py → marge_securite() → C10",
        f"L_seuil = ρ·T avec ρ = {RHO_MARGE} ; Δ = max(0, L_seuil − L)",
        f"L_seuil = {_go(ms['seuil'])} ; déficit Δ = {_go(ms['deficit'])} à l'instantané, "
        f"{_go(ms_live['deficit'])} à la lecture en cours",
        "SPÉCIFIÉ",
        {"rho": RHO_MARGE, "libre_actuel": l, "total": t,
         "live": {"total": py["total"], "libre": py["libre"], "deficit": ms_live["deficit"]},
         "derive_de_linstantane_au_live": ms_live["deficit"] - ms["deficit"],
         "commentaire": "ρ = 0,10 est une convention d'exploitation, pas un théorème ; le Δ de "
                        "l'instantané et le Δ lu en direct ne sont pas la même quantité : l'un est "
                        "daté, l'autre court pendant la mesure"},
    ))
    if ms_wmi is None:
        controles.append(_c("C10", "seconde API de volume injoignable", "wmi_injoignable",
                            str(wmi.get("erreur", "absente"))))
    else:
        controles.append(_c(
            "C10", "déficit de la marge retrouvé par la seconde API, sur la même lecture en cours",
            ms_live["deficit"], ms_wmi["deficit"], tol=GO / 5,
        ))

    # EQ-11 — solde après libération
    apres = solde_apres(l, R)
    eqs.append(_eq(
        "EQ-11", "espace_disque.py → solde_apres() → C11",
        "L' = L + R ; verdict = (L' ≥ L_seuil) ⟺ (R ≥ Δ)",
        f"L' = {_go(apres)} ; seuil {_go(ms['seuil'])} → "
        f"{'SUFFISANT' if apres >= ms['seuil'] else 'INSUFFISANT'} ; occupation {100 * (1 - apres / t):.1f} %",
        "SIMULÉ",
        {"L": l, "R": int(R), "L_prime": int(apres), "seuil": int(ms["seuil"]),
         "occupation_apres": 1 - apres / t},
    ))
    controles.append(_c(
        "C11", "L' − R = L (identité) et (L' ≥ seuil) ⟺ (R ≥ Δ) (cohérence logique)",
        [int(apres - R), True], [l, (apres >= ms["seuil"]) == (R >= ms["deficit"])],
    ))

    # EQ-12 — rendement rapporté au volume
    eta = rendement(R, t)
    eqs.append(_eq(
        "EQ-12", "espace_disque.py → rendement() → C12",
        "η = R / T",
        f"η = {eta:.5f} ({100 * eta:.2f} % du volume C: récupérable ; "
        f"{100 * R / max(1, dep['octets_total']):.1f} % du dépôt)",
        "OPÉRATIONNEL",
        {"R": int(R), "T": t, "S_depot": dep["octets_total"], "eta": eta},
    ))
    controles.append(_c("C12", "η·T = R et 0 ≤ η ≤ 1", [eta * t, 0.0 <= eta <= 1.0],
                        [float(R), True], tol=[max(1.0, 1e-9 * t), 0.0]))

    # EQ-13 — invariant de non-perte du patrimoine scellé
    sc = secteurs_scelles()
    eqs.append(_eq(
        "EQ-13", "espace_disque.py → secteurs_scelles() → C13",
        "∀ f ∈ manifeste d'antériorité : f n'appartient à aucune catégorie nettoyable",
        ("manifeste absent" if "erreur" in sc else
         f"{sc['nb_fichiers_manifeste']} fichiers scellés (racine Merkle {str(sc['racine_merkle_sha256'])[:16]}…) : "
         f"{len(sc['par_classe'])} nettoyables selon le collecteur, {len(sc['par_prefixe'])} selon la règle de préfixe"),
        "OPÉRATIONNEL",
        sc,
    ))
    if "erreur" in sc:
        controles.append(_c("C13", "manifeste indisponible : invariant non contrôlé",
                            "manifeste_absent", sc["erreur"]))
    else:
        controles.append(_c(
            "C13", "les deux prédicats d'appartenance concordent et donnent 0",
            [sc["par_classe"], sc["par_prefixe"]], [[], []],
        ))

    resume = {
        "equations": len(eqs),
        "controles_ok": sum(1 for c in controles if c["ok"]),
        "controles_total": len(controles),
        "statuts": {s: sum(1 for e in eqs if e["statut"] == s) for s in STATUTS},
        "libre_go": round(l / GO, 3),
        "occupation": round(u / t, 4),
        "recuperable_go": round(R / GO, 3),
        "deficit_go": round(ms["deficit"] / GO, 3),
        "copies_historiques": n_hist,
        "hors_retention_n": retention["hors_retention_n"],
        "jours_avant_saturation": round(proj["jours_avant_saturation"], 2),
    }
    return {
        "version": "1.0",
        "genere_le_utc": _iso(),
        "source": SOURCE,
        "invariants": {
            "GO": GO, "rho_marge": RHO_MARGE, "horizon_jours": HORIZON_JOURS,
            "fenetre_jours": FENETRE_JOURS, "garde_frais": GARDE_FRAIS,
            "empreinte_instantane": e_calculee,
        },
        "equations": eqs,
        "controles": controles,
        "resume": resume,
        "mesures": {
            "volumes": {"instantane": vol, "python_live": py, "wmi_live": wmi},
            "copies": {"courante_octets": cop["courante_octets"],
                       "historiques_n": n_hist,
                       "historiques_octets": cop["historiques_octets"],
                       "archives_octets": cop["archives_octets"],
                       "archives_fichiers": cop["archives_fichiers"],
                       "total_octets": cop["total_octets"],
                       "taille_moyenne": s_moyen,
                       "duplication": duplication},
            "retention": {k: v for k, v in retention.items() if k != "hors_retention"},
            "journal_append_only": jr,
            "recuperable_par_categorie": cat,
            "scelle": sc,
        },
        "limites": [
            "Chiffres d'un poste unique, à un instant unique : l'instantané est le témoin, pas une moyenne.",
            "EQ-08 suppose cadence et taille constantes ; le service perpétuel qui produit les copies peut changer de cycle.",
            "EQ-09 est une borne supérieure sous convention de rétention (courante + 1 ancre par jour UTC + 5 plus récentes) : ce n'est pas la mesure de ce qui sera supprimé.",
            "ρ = 0,10 est un choix d'exploitation ; la politique d'allocation de Windows ne garantit rien à ce seuil.",
            "C04 comparait jadis le maximum de la partition par classe au maximum de la partition par "
            "répertoire de premier niveau : les deux maxima coïncidaient parce qu'un seul répertoire dominait "
            "le dépôt. Cette égalité ne relève d'aucune identité ; le contrôle compare désormais la "
            "fraction dominante à l'octet de sa classe, remis par la normalisation.",
            "Le plafond posé dans conscience_logique/sauvegarde_soi.py ne supprime que les stamps figurant dans "
            "_archives/manifeste_couverture.json, écrit par l'archiver après vérification octet par octet : une "
            "copie hors rétention mais non archivée est gardée et signalée, jamais jetée.",
            "C10 ne compare plus l'instantané au direct : les deux lectures live (shutil puis PowerShell) portent "
            "sur le même déficit. Le décalage entre le Δ daté et le Δ en cours, publié dans EQ-10, est la "
            "consommation réelle pendant l'âge de l'instantané, pas une erreur de formule.",
            "C07 ne compare plus l'instantané du collecteur au recompté live : le journal d'actes grossit en "
            "continu (~5 Mo/j), l'égalité daté↔direct dépendait de l'horloge et a échoué à +2,9 % sur 50 minutes. "
            "Le comptage live est refait par deux routes indépendantes sur un même tampon figé (itérateur de "
            "lignes contre dénombrement des sauts, taille contre somme des longueurs), et la seule propriété "
            "append-only vérifiable — la croissance monotone — est assertée. La dérive daté→direct est publiée "
            "dans EQ-07, aucune tolérance n'a été élargie.",
            "Rien n'est supprimé par ce module : la libération est une étape distincte, avec manifeste des stamps retirés et feu vert de l'auteur.",
            f"Hors périmètre : vibe_videos, AMAL_CONSOLIDE et vibe_videos_doublons totalisent "
            f"{(dep['octets_par_niveau1'].get('vibe_videos', 0) + dep['octets_par_niveau1'].get('AMAL_CONSOLIDE', 0) + dep['octets_par_niveau1'].get('vibe_videos_doublons', 0)) / GO:.2f} Go "
            "de contenu de l'auteur, non scellé, à trancher par lui — non comptés dans R.",
        ],
    }


def verifier(donnees: Optional[Dict[str, Any]] = None) -> bool:
    donnees = donnees or resoudre()
    return all(c["ok"] for c in donnees["controles"])


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    _sortie = resoudre()
    print(json.dumps(_sortie, ensure_ascii=False, indent=2, default=str))
    raise SystemExit(0 if verifier(_sortie) else 1)
