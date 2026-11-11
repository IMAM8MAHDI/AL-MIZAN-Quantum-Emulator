# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""QPU_DISTANT — ce qu'un processeur quantique distant a réellement rendu.

Dossier du dépôt scellé portant une exécution observée sur du matériel qui n'est pas
celui de l'auteur : le job `dbpkmr0ou4as73ctrm80`, soumis le 2026-11-10T16:50:52Z sur
`ibm_marrakesh` (156 fils, 256 tirs, programme `sampler`), archive téléchargée depuis le
tableau de bord du fournisseur. Le dépôt d'AL-MIZAN continue de déclarer
`qubit_physique_local = False` : rien ici ne s'exécute sur un qubit tenu par l'auteur,
et ce dossier ne prétend pas corriger cette déclaration — il la borde, en disant ce
qu'une machine distante rend sur une paire de Bell.

Ce que le module recalcule, avec la seule bibliothèque standard et à partir des fichiers
publiés dans `sources/` :

  1. les empreintes (membres de l'archive, bloc QPY décompressé, fichiers publiés) ;
  2. les compteurs, en dépaquetant le `BitArray` du résultat — format `.npy` lu à la main ;
  3. la parité mesurée, son écart-type de tirage, et le test exact de l'asymétrie 01/10 ;
  4. la parité idéale, en simulant le circuit transpilé sur son support en arithmétique
     complexe (deux qubits, ni qiskit ni numpy) ;
  5. deux enveloppes de bruit **tenues séparées** : la médiane machine scellée et la
     somme porte par porte des erreurs réelles du support. Elles ne coïncident pas, et
     l'observation tombe entre les deux : la médiane aurait falsifié ce tirage,
     l'enveloppe exacte le reçoit. Les verdicts sont donc rendus l'un après l'autre.

Ce qu'il ne fait pas : il ne re-soumet rien, n'appelle aucun réseau, n'écrit rien hors de
`artefacts/`, ne publie aucun identifiant de compte (le champ `user_id` est remplacé par
le préfixe SHA-256 en douze rangs de lui-même, `sources/portes_transpilees.json` en porte
la règle) et ne conclut rien sur AL-MIZAN à partir d'un tirage de 256 coups.

Usage :
    py -3 QPU_DISTANT/qpu_distant_base.py             # 10 équations, 10 contrôles, rc 0 ou 1
    py -3 QPU_DISTANT/qpu_distant_base.py --ecrit     # + certificat.json, CSV et SVG
    py -3 QPU_DISTANT/qpu_distant_base.py --json      # rapport complet en JSON
"""
from __future__ import annotations

import ast
import base64
import hashlib
import json
import math
import sys
import zlib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

DOSSIER = Path(__file__).resolve().parent
SOURCES = DOSSIER / "sources"
ARTEFACTS = DOSSIER / "artefacts"

F_INFOS = "info_netoyee.json"
F_RESULT = "result.json"
F_REGISTRE = "portes_transpilees.json"
F_CALIBRAGE = "calibration_ibm_marrakesh_2026-11-10T1647Z.json"
F_SUPPORT = "support_ibm_marrakesh_0-1_2026-11-10T2057Z.json"
F_EMPREINTES = "EMPREINTES.json"

PUBLIES = (F_INFOS, F_RESULT, F_REGISTRE, F_CALIBRAGE, F_SUPPORT)

# Coûts de bruit lus dans le calibrage machine, par nom de porte (chemin dans le JSON).
CLE_CALIBRAGE = {"sx": ("erreur_1q", "sx"), "x": ("erreur_1q", "x"), "cz": ("erreur_2q",),
                 "measure": ("erreur_lecture",), "reset": ("erreur_lecture",)}
# Portes sans coût déclaré : virtuelles ou purement classiques dans ce budget.
SANS_ERREUR = {"rz", "id", "barrier", "delay", "global_phase"}
HORS_UNITAIRE = {"measure", "barrier", "delay", "reset", "id"}
TOLERANCE_NUMERIQUE = 1e-12


# ----------------------------------------------------------------------------
# lecture des sources publiées
# ----------------------------------------------------------------------------
def _sha(brut: bytes) -> str:
    return hashlib.sha256(brut).hexdigest()


def _octets(nom: str) -> bytes:
    return (SOURCES / nom).read_bytes()


def _json(nom: str) -> Any:
    return json.loads(_octets(nom).decode("utf-8"))


def debase_zlib(chaine: str) -> bytes:
    return zlib.decompress(base64.b64decode(chaine))


def empreintes_des_sources() -> Dict[str, Any]:
    """`EMPREINTES.json` recontrôlé sur les octets réellement présents à côté du module."""
    table = _json(F_EMPREINTES)["fichiers"]
    rendu: Dict[str, Any] = {}
    for nom in sorted(table):
        brut = _octets(nom)
        obtenu = _sha(brut)
        rendu[nom] = {"octets": len(brut), "sha256": obtenu,
                      "attendu": table[nom]["sha256"],
                      "ok": obtenu == table[nom]["sha256"] and len(brut) == table[nom]["octets"]}
    rendu["hors_table"] = sorted({p.name for p in SOURCES.iterdir() if p.is_file()}
                                 - set(table) - {F_EMPREINTES})
    return rendu


def infos() -> Dict[str, Any]:
    return _json(F_INFOS)


def registre() -> Dict[str, Any]:
    return _json(F_REGISTRE)


def calibrage() -> Dict[str, Any]:
    return _json(F_CALIBRAGE)


def sonde_support() -> Dict[str, Any]:
    return _json(F_SUPPORT)


def bloc_qpy() -> bytes:
    """Le circuit transpilé, décompressé du porteur JSON — sans qiskit."""
    return debase_zlib(infos()["params"]["pubs"][0][0]["__value__"])


def npy(brut: bytes) -> Tuple[str, List[int], List[int]]:
    """(descr, forme, valeurs) d'un tableau `.npy` v1 en petits entiers non signés."""
    if brut[:6] != b"\x93NUMPY":
        raise ValueError("signature .npy absente")
    if brut[6] != 1:
        raise ValueError(f"version .npy non lue : {brut[6]}")
    taille_en_tete = int.from_bytes(brut[8:10], "little")
    entete = ast.literal_eval(brut[10:10 + taille_en_tete].decode("latin-1"))
    descr, forme = entete["descr"], list(entete["shape"])
    if descr != "|u1":
        raise ValueError(f"descr non supporté : {descr}")
    corps = brut[10 + taille_en_tete:]
    if entete["fortran_order"] or len(corps) != (math.prod(forme) if forme else 0):
        raise ValueError("tableau discontinue ou de longueur incohérente")
    return descr, forme, list(corps)


def lecture_compteurs() -> Dict[str, Any]:
    """Les compteurs, recalculés à partir du `BitArray` publié verbatim."""
    donnees = _json(F_RESULT)["__value__"]["pub_results"][0]["__value__"]["data"]["__value__"]
    champ = donnees["field_names"][0]
    entree = donnees["fields"][champ]["__value__"]
    bits = int(entree["num_bits"])
    descr, forme, valeurs = npy(debase_zlib(entree["array"]["__value__"]))
    compte: Dict[str, int] = {}
    for valeur in valeurs:
        cle = f"{int(valeur):0{bits}b}"
        compte[cle] = compte.get(cle, 0) + 1
    tirs_declares = infos()["params"]["pubs"][0][2]
    return {"champ": champ, "num_bits": bits, "descr": descr, "forme": forme,
            "tirages": len(valeurs), "tirs_declares": tirs_declares,
            "compte": dict(sorted(compte.items())),
            "sha256_membre_result": _sha(_octets(F_RESULT))}


def parite_mesuree(compte: Dict[str, int]) -> Dict[str, Any]:
    tirages = sum(compte.values())
    pair = sum(v for k, v in compte.items() if k.count("1") % 2 == 0)
    impair = tirages - pair
    p = pair / tirages
    sigma = math.sqrt(max(p * (1.0 - p), 0.0) / tirages)
    return {"evenement": "nombre de 1 pair sur le registre", "tirages": tirages,
            "tirages_pairs": pair, "tirages_impairs": impair,
            "p_mesuree": p, "sigma_tirage": sigma,
            "intervalle_1sigma": [p - sigma, p + sigma],
            "p_exacte": f"{pair}/{tirages}"}


def test_asymetrie(compte: Dict[str, int]) -> Dict[str, Any]:
    """Comparaison exacte des deux issues impaires, conditionnée à leur effectif total.

    Sous l'hypothèse nulle « les deux mots de poids un sont équiprobables », le compte de
    `01` suit une loi binomiale(n_impairs, 1/2) : la valeur p bilatérale est l'exact
    2·(1/2)^n dès qu'une des deux cellules est vide. Aucun tirage au sort, aucune
    approximation normale.
    """
    a, b = compte.get("01", 0), compte.get("10", 0)
    n = a + b
    if n == 0:
        return {"01": a, "10": b, "effectif": 0, "valeur_p": None,
                "conclusion": "aucun tirage impair : le test est sans objet"}
    k = min(a, b)
    unilaterale = sum(math.comb(n, i) for i in range(k + 1)) / (2.0 ** n)
    valeur_p = min(1.0, 2.0 * unilaterale)
    return {"01": a, "10": b, "effectif": n, "cellule_minimale": k,
            "hypothese_nulle": "les deux mots de poids un sont équiprobables",
            "loi": f"Binom({n}, 1/2) calculée en entiers",
            "valeur_p": valeur_p,
            "conclusion": ("asymétrie non imputable au seul tirage" if valeur_p < 0.05
                           else "asymétrie compatible avec le tirage")}


def support_touche(portes: Sequence[Dict[str, Any]]) -> List[int]:
    return sorted({q for g in portes for q in g["qubits"]})


def simuler(portes: Sequence[Dict[str, Any]], support: Sequence[int]) -> Dict[str, Any]:
    """Amplitudes exactes du circuit restreint à son support, en `complex` pur.

    Convention Qiskit reproduite : qubit 0 = bit de poids faible, `rz(θ)` diagonal
    (e^{-iθ/2}, e^{+iθ/2}), `sx` = (1/2)·[[1+i, 1-i], [1-i, 1+i]], `cz` = diag(1,1,1,-1).
    Une porte hors de cette table arrête le calcul plutôt que de le poursuivre en ignorant
    une opération.
    """
    filtres = {q: i for i, q in enumerate(support)}
    dim = 1 << len(support)
    psi: List[complex] = [0j] * dim
    psi[0] = 1 + 0j
    appliquees = 0
    for g in portes:
        nom = g["nom"]
        if nom in HORS_UNITAIRE:
            continue
        indices = [filtres[q] for q in g["qubits"]]
        if nom == "cz":
            i0, i1 = indices
            for x in range(dim):
                if (x >> i0) & 1 and (x >> i1) & 1:
                    psi[x] *= -1
        elif nom == "rz":
            theta = float(g["parametres"][0])
            tour = [(math.cos(-theta / 2.0) + 1j * math.sin(-theta / 2.0)),
                    (math.cos(theta / 2.0) + 1j * math.sin(theta / 2.0))]
            i0 = indices[0]
            for x in range(dim):
                psi[x] *= tour[(x >> i0) & 1]
        elif nom in ("sx", "x"):
            if nom == "x":
                mat = [complex(0), complex(1), complex(1), complex(0)]
            else:
                mat = [0.5 + 0.5j, 0.5 - 0.5j, 0.5 - 0.5j, 0.5 + 0.5j]
            i0 = indices[0]
            for x in range(dim):
                if (x >> i0) & 1:
                    continue
                y = x | (1 << i0)
                a, b = psi[x], psi[y]
                psi[x] = mat[0] * a + mat[1] * b
                psi[y] = mat[2] * a + mat[3] * b
        else:
            raise ValueError(f"porte hors du simulateur standard : {nom}")
        appliquees += 1
    probs = [abs(a) ** 2 for a in psi]
    normale = sum(probs)
    pair = sum(v for i, v in enumerate(probs) if bin(i).count("1") % 2 == 0)
    return {"qubits_actifs": len(support), "dimensions": dim,
            "operations_unitaires": appliquees,
            "distribution": [round(v, 12) for v in probs],
            "norme": normale, "p_pair_calculee": pair,
            "bruit_numerique": abs(pair - round(pair, 12))}


# ----------------------------------------------------------------------------
# les deux enveloppes, jamais fusionnées
# ----------------------------------------------------------------------------
def mediane(calibrage_: Dict[str, Any], chemin: Tuple[str, ...]) -> float:
    table: Any = calibrage_
    for cle in chemin:
        table = table[cle]
    return float(table["mediane"])


def compte_portes(portes: Sequence[Dict[str, Any]]) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for g in portes:
        out[g["nom"]] = out.get(g["nom"], 0) + 1
    return dict(sorted(out.items()))


def enveloppe_mediane(portes: Sequence[Dict[str, Any]],
                      calibrage_: Dict[str, Any]) -> Dict[str, Any]:
    """Σ ε sur les médiannes de la machine entière : répond à « un circuit typique »."""
    somme = 0.0
    detail: Dict[str, Any] = {}
    for g in portes:
        cle = CLE_CALIBRAGE.get(g["nom"])
        if not cle:
            continue
        eps = mediane(calibrage_, cle)
        somme += eps
        entree = detail.setdefault(g["nom"], {"erreur": eps, "n": 0, "contribution": 0.0})
        entree["n"] += 1
        entree["contribution"] += eps
    return {"source": F_CALIBRAGE, "regle": "borne = 1 − 2·Σ ε (inégalité triangulaire)",
            "somme_eps": somme, "delta_enveloppe": 2.0 * somme,
            "borne_basse": 1.0 - 2.0 * somme, "detail": detail}


def enveloppe_support(portes: Sequence[Dict[str, Any]], support: Dict[str, Any],
                      calibrage_: Dict[str, Any]) -> Dict[str, Any]:
    """Σ ε porte par porte avec les erreurs des qubits réellement occupés."""
    qubits, aretes = support["qubits"], support["aretes"]
    somme, detail, repli = 0.0, {}, {}
    for g in portes:
        nom, indices = g["nom"], g["qubits"]
        if nom in SANS_ERREUR:
            valeur, source = 0.0, "virtuelle"
        elif len(indices) == 2:
            cle = f"{min(indices)}-{max(indices)}"
            arete = aretes.get(cle) or aretes.get(f"{max(indices)}-{min(indices)}")
            if arete:
                valeur, source = float(arete["erreur"]), f"{arete['porte']}[{cle}]"
            else:
                valeur = mediane(calibrage_, CLE_CALIBRAGE[nom]) if nom in CLE_CALIBRAGE else 0.0
                source = "repli mediane"
                repli[cle] = valeur
        else:
            entree = qubits.get(str(indices[0]), {})
            if nom in entree and entree[nom] is not None:
                valeur, source = float(entree[nom]), f"{nom}[{indices[0]}]"
            elif nom in CLE_CALIBRAGE:
                valeur = mediane(calibrage_, CLE_CALIBRAGE[nom])
                source = "repli mediane"
                repli[f"{nom}[{indices[0]}]"] = valeur
            else:
                valeur, source = 0.0, "non comptee"
        cle_detail = f"{nom}[{','.join(map(str, indices))}]"
        ligne = detail.setdefault(cle_detail, {"erreur": valeur, "source": source,
                                               "n": 0, "contribution": 0.0})
        ligne["n"] += 1
        ligne["contribution"] += valeur
        somme += valeur
    return {"source": F_SUPPORT, "regle": "borne = 1 − 2·Σ ε sur le support",
            "somme_eps": somme, "delta_enveloppe": 2.0 * somme,
            "borne_basse": 1.0 - 2.0 * somme, "detail": detail,
            "repli_mediane": repli, "empreinte_support": support["empreinte_support"],
            "horodatage_support_utc": support["horodatage_utc"]}


def empreinte_parc_recalculee(calibrage_: Dict[str, Any]) -> str:
    corps = json.dumps({k: v for k, v in calibrage_.items() if k != "empreinte_parc"},
                       sort_keys=True, ensure_ascii=False)
    return _sha(corps.encode("utf-8"))


def empreinte_support_recalculee(support: Dict[str, Any]) -> str:
    corps = json.dumps({k: v for k, v in support.items()
                        if k not in ("horodatage_utc", "empreinte_support")},
                       sort_keys=True, ensure_ascii=False)
    return _sha(corps.encode("utf-8"))


def duree_execution() -> Dict[str, Any]:
    """La fenêtre d'exécution, lue dans les spans du résultat publié."""
    donnees = _json(F_RESULT)["__value__"]["metadata"]["execution"]["execution_spans"]
    span = donnees["__value__"]["spans"][0]["__value__"]
    debut = datetime.fromisoformat(span["start"]["__value__"])
    fin = datetime.fromisoformat(span["stop"]["__value__"])
    return {"debut_utc": span["start"]["__value__"], "fin_utc": span["stop"]["__value__"],
            "duree_observee_s": (fin - debut).total_seconds(),
            "duree_estimee_s": infos()["estimated_running_time_seconds"],
            "portee": "fenêtre d'exécution déclarée par le fournisseur, attente de file exclue"}


# ----------------------------------------------------------------------------
# certificat
# ----------------------------------------------------------------------------
def _merkle(hashes: Sequence[str]) -> str:
    if not hashes:
        return _sha(b"")
    niveau = list(hashes)
    while len(niveau) > 1:
        suivant = []
        for i in range(0, len(niveau), 2):
            droit = niveau[i + 1] if i + 1 < len(niveau) else niveau[i]
            suivant.append(_sha((niveau[i] + droit).encode("utf-8")))
        niveau = suivant
    return niveau[0]


def mesurer() -> Dict[str, Any]:
    """Tous les nombres du dossier, recalculés une fois pour toutes."""
    reg = registre()
    portes = reg["portes"]
    support = sonde_support()
    calibrage_ = calibrage()
    touches = support_touche(portes)
    compte = lecture_compteurs()
    par = parite_mesuree(compte["compte"])
    simu = simuler(portes, touches)
    e1 = enveloppe_mediane(portes, calibrage_)
    e2 = enveloppe_support(portes, support, calibrage_)
    qpy_brut = bloc_qpy()
    return {
        "registre": reg, "portes": portes, "support": support, "calibrage": calibrage_,
        "support_physique": touches, "compte_portes": compte_portes(portes),
        "lecture": compte, "compteurs": compte["compte"], "parite": par,
        "asymetrie": test_asymetrie(compte["compte"]), "simulation": simu,
        "enveloppe_mediane": e1, "enveloppe_support": e2,
        "duree": duree_execution(),
        "empreintes": {
            "sha256_zip_atteste": reg["archive"]["sha256_zip"],
            "sha256_bloc_qpy_recalcule": _sha(qpy_brut),
            "sha256_bloc_qpy_registre": reg["archive"]["sha256_bloc_qpy"],
            "octets_bloc_qpy_recalcules": len(qpy_brut),
            "sha256_membre_result_registre": reg["redaction"]["sha256_membre_result"],
            "sha256_info_netoyee": _sha(_octets(F_INFOS)),
            "empreinte_parc_declaree": calibrage_["empreinte_parc"],
            "empreinte_parc_recalculee": empreinte_parc_recalculee(calibrage_),
            "empreinte_support_declaree": support["empreinte_support"],
            "empreinte_support_recalculee": empreinte_support_recalculee(support),
        },
        "verdicts": {
            "mediane_machine": {
                "borne_basse": e1["borne_basse"],
                "recue": par["p_mesuree"] >= e1["borne_basse"],
                "recue_a_3sigma": par["p_mesuree"] >= e1["borne_basse"] - 3.0 * par["sigma_tirage"],
                "ecart_en_sigma": (par["p_mesuree"] - e1["borne_basse"]) / par["sigma_tirage"]},
            "support_reel": {
                "borne_basse": e2["borne_basse"],
                "recue": par["p_mesuree"] >= e2["borne_basse"],
                "ecart_en_sigma": (par["p_mesuree"] - e2["borne_basse"]) / par["sigma_tirage"]},
        },
        "empreintes_des_sources": empreintes_des_sources(),
    }


NOEUDS = {
    "EQ-01": {"depend": [], "externe": "archive du fournisseur, téléchargée puis scellée"},
    "EQ-02": {"depend": ["EQ-01"], "externe": "qiskit (qpy.load) pour la seule extraction du registre"},
    "EQ-03": {"depend": ["EQ-01"], "externe": "format .npy de numpy, lu à la main"},
    "EQ-04": {"depend": ["EQ-03"], "externe": None},
    "EQ-05": {"depend": ["EQ-04"], "externe": None},
    "EQ-06": {"depend": ["EQ-02"], "externe": None},
    "EQ-07": {"depend": ["EQ-04"], "externe": "calibrage public du parc ibm_marrakesh"},
    "EQ-08": {"depend": ["EQ-04"], "externe": "sonde du support 0-1, lecture seule du target"},
    "EQ-09": {"depend": ["EQ-07", "EQ-08"], "externe": None},
    "EQ-10": {"depend": ["EQ-01"], "externe": "horodatages du fournisseur"},
}


def _eq(id_: str, chemin: str, formule: str, resultat: str, statut: str,
        limite: str, detail: Any) -> Dict[str, Any]:
    n = NOEUDS[id_]
    return {"id": id_, "chemin": chemin, "formule": formule, "resultat": resultat,
            "statut": statut, "limite": limite, "detail": detail,
            "couche": "S2 REGULARITE",
            "piliers": ["P1 UNITE", "P2 BORNE", "P3 CONFRONTATION", "P4 TRANSMISSION"],
            "depend_de": n["depend"], "fonde_hors_du_dossier": n["externe"]}


def equations(m: Dict[str, Any]) -> List[Dict[str, Any]]:
    e = m["empreintes"]
    reg, par, simu = m["registre"], m["parite"], m["simulation"]
    e1, e2 = m["enveloppe_mediane"], m["enveloppe_support"]
    v1, v2 = m["verdicts"]["mediane_machine"], m["verdicts"]["support_reel"]
    asym, duree = m["asymetrie"], m["duree"]
    ch = "QPU_DISTANT/qpu_distant_base.py → "
    return [
        _eq("EQ-01", ch + "mesurer() → empreintes",
            "SHA-256(info) · SHA-256(result) · SHA-256(bloc QPY décompressé)",
            f"result {e['sha256_membre_result_registre'][:16]}… · "
            f"QPY {e['sha256_bloc_qpy_recalcule'][:16]}… sur "
            f"{e['octets_bloc_qpy_recalcules']} octets · zip "
            f"{e['sha256_zip_atteste'][:16]}…", "OPÉRATIONNEL",
            "l'archive d'origine n'est pas publiée : elle porte un identifiant de compte. "
            "Son SHA-256 reste attesté par le registre scellé, non reproductible ici.",
            {"zip_atteste": e["sha256_zip_atteste"],
             "qpy_reproductible": e["sha256_bloc_qpy_recalcule"] == e["sha256_bloc_qpy_registre"]}),
        _eq("EQ-02", ch + "registre() → support_touche()",
            "12 opérations sur un registre de 156 fils, support effectif {0, 1}",
            f"{m['compte_portes']} · profondeur {reg['circuit']['profondeur']} · "
            f"{reg['circuit']['qubits_registre']} fils · {len(m['support_physique'])} actifs",
            "SPÉCIFIÉ",
            "le registre de portes vient de `qpy.load` (qiskit), exécuté une fois hors du "
            "dépôt : ici il n'est ni regénéré ni contesté, seulement lié au bloc QPY par "
            "son empreinte.",
            {"fichier": F_REGISTRE, "phase": reg["circuit"]["global_phase"]}),
        _eq("EQ-03", ch + "lecture_compteurs() → npy()",
            "BitArray → compte |00⟩, |01⟩, |10⟩, |11⟩",
            f"{m['compteurs']} sur {m['lecture']['tirages']} tirages "
            f"(déclarés {m['lecture']['tirs_declares']})", "OPÉRATIONNEL",
            "le tableau est dépaqueté à la main : aucun octet du résultat n'est repris "
            "d'un calcul antérieur.", {"descr": m["lecture"]["descr"],
                                       "forme": m["lecture"]["forme"]}),
        _eq("EQ-04", ch + "parite_mesuree()",
            "p = n(pair)/N · σ = √(p(1−p)/N)",
            f"p = {par['p_mesuree']} ({par['p_exacte']}) · σ = {par['sigma_tirage']}",
            "OPÉRATIONNEL",
            "σ est l'écart-type de tirage d'une proportion : il ne dit rien du bruit "
            "corrélé ni des erreurs de lecture systématisées.", par),
        _eq("EQ-05", ch + "test_asymetrie()",
            "H0 : les deux mots de poids un sont équiprobables · test bilatéral exact",
            f"|01⟩ {asym['01']} contre |10⟩ {asym['10']} sur {asym['effectif']} · "
            f"p = {asym['valeur_p']}", "OPÉRATIONNEL",
            "le test porte sur la répartition entre les deux issues impaires, pas sur la "
            "parité : les enveloppes, elles, ne bornent que la parité.", asym),
        _eq("EQ-06", ch + "simuler()",
            "|ψ⟩ sur le support · pz(pair) = Σ |⟨x|ψ⟩|² sur x de poids pair",
            f"p_pair = {simu['p_pair_calculee']} · distribution {simu['distribution']} · "
            f"norme {simu['norme']} · {simu['operations_unitaires']} portes unitaires",
            "SIMULÉ",
            "simulation exacte d'un circuit de deux qubits en arithmétique flottante : "
            "elle établit la prédiction testée, elle n'exécute rien.", simu),
        _eq("EQ-07", ch + "enveloppe_mediane()",
            "borne = 1 − 2·Σ ε_médiane",
            f"Σ ε = {e1['somme_eps']} · borne = {e1['borne_basse']} · reçue "
            f"{v1['recue']} · écart {v1['ecart_en_sigma']} σ", "SPÉCIFIÉ",
            "les médiannes décrivent la machine entière, pas la paire de qubits occupée : "
            "c'est une borne de circuit typique, pas de CE circuit.",
            {"detail": e1["detail"], "recue_a_3sigma": v1["recue_a_3sigma"]}),
        _eq("EQ-08", ch + "enveloppe_support()",
            "borne = 1 − 2·Σ ε_support",
            f"Σ ε = {e2['somme_eps']} · borne = {e2['borne_basse']} · reçue "
            f"{v2['recue']} · écart {v2['ecart_en_sigma']} σ · repli "
            f"{len(e2['repli_mediane'])}", "SPÉCIFIÉ",
            "chaque porte est facturée à l'erreur mesurée du qubit qu'elle occupe ; la "
            "règle d'addition reste une inégalité triangulaire, pas une simulation du "
            "bruit corrélé.", {"detail": e2["detail"],
                               "empreinte_support": e2["empreinte_support"]}),
        _eq("EQ-09", ch + "verdicts",
            "1 − 2·Σ ε_support < p < 1 − 2·Σ ε_médiane",
            f"{e2['borne_basse']} < {par['p_mesuree']} < {e1['borne_basse']} · écart entre "
            f"bornes {e1['borne_basse'] - e2['borne_basse']} soit "
            f"{(e1['borne_basse'] - e2['borne_basse']) / par['sigma_tirage']:.3f} σ",
            "OPÉRATIONNEL",
            "une seule exécution tranche entre deux enveloppes : elle ne valide pas la "
            "médiane machine comme modèle de ce circuit, elle montre seulement qu'elle "
            "l'aurait falsifiée ici.", {"verdicts": m["verdicts"]}),
        _eq("EQ-10", ch + "duree_execution()",
            "fenêtre d'exécution · coût · localité",
            f"{duree['duree_observee_s']} s observés contre {duree['duree_estimee_s']} s "
            f"estimés · {reg['job']['cout_units']} units · "
            f"qubit_physique_local = False", "OPÉRATIONNEL",
            "la fenêtre publiée par le fournisseur couvre l'exécution, pas l'attente dans "
            "la file ; le coût est celui porté par l'archive.", duree),
    ]


def controles(m: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    eqs = {x["id"]: x for x in equations(m)}

    def ajouter(id_: str, nom: str, attendu: Any, obtenu: Any, ok: bool) -> None:
        out.append({"id": id_, "nom": nom, "attendu": str(attendu), "obtenu": str(obtenu),
                    "ok": bool(ok), "limite": eqs["EQ-" + id_[1:]]["limite"]})

    empreintes = m["empreintes_des_sources"]
    lignes = [n for n, v in empreintes.items() if isinstance(v, dict) and v["ok"]]
    ajouter("C01", "les fichiers publiés correspondent à leur empreinte scellée",
            f"{len(PUBLIES)}/{len(PUBLIES)}", f"{len(lignes)}/{len(PUBLIES)}",
            len(lignes) == len(PUBLIES) and not empreintes["hors_table"])
    e = m["empreintes"]
    ajouter("C02", "result.json publié est le membre verbatim de l'archive",
            e["sha256_membre_result_registre"][:24], m["lecture"]["sha256_membre_result"][:24],
            e["sha256_membre_result_registre"] == m["lecture"]["sha256_membre_result"])
    ajouter("C03", "le bloc QPY reproduit depuis info_netoyée porte l'empreinte du registre",
            e["sha256_bloc_qpy_registre"][:24], e["sha256_bloc_qpy_recalcule"][:24],
            e["sha256_bloc_qpy_registre"] == e["sha256_bloc_qpy_recalcule"])
    occurrences = sum(_octets(n).decode("utf-8", "replace").count("IBMid") for n in PUBLIES)
    ajouter("C04", "aucun identifiant de compte ne subsiste dans les fichiers publiés",
            0, occurrences, occurrences == 0)
    ajouter("C05", "tirs déclarés = somme des compteurs = longueur du tableau",
            m["lecture"]["tirs_declares"],
            f"{sum(m['compteurs'].values())} · {m['lecture']['tirages']}",
            m["lecture"]["tirs_declares"] == sum(m["compteurs"].values())
            == m["lecture"]["tirages"])
    ajouter("C06", "largeur du registre mesuré = nombre de bits du BitArray",
            m["registre"]["circuit"]["clbits"], m["lecture"]["num_bits"],
            m["registre"]["circuit"]["clbits"] == m["lecture"]["num_bits"])
    releve = m["compte_portes"]
    ajouter("C07", "multiset des portes et leur compte total",
            f"{m['registre']['circuit']['operations']} opérations", str(releve),
            sum(releve.values()) == m["registre"]["circuit"]["operations"]
            and releve == {"cz": 1, "measure": 2, "rz": 6, "sx": 3})
    simu = m["simulation"]
    ajouter("C08", "la simulation rend la distribution de Bell attendue",
            "[0.5, 0.0, 0.0, 0.5]", f"{simu['distribution']} à {TOLERANCE_NUMERIQUE:g}",
            simu["distribution"] == [0.5, 0.0, 0.0, 0.5]
            and abs(simu["p_pair_calculee"] - 1.0) < TOLERANCE_NUMERIQUE
            and abs(simu["norme"] - 1.0) < TOLERANCE_NUMERIQUE)
    ajouter("C09", "les empreintes internes du calibrage et de la sonde se recalculent",
            f"{e['empreinte_parc_declaree'][:16]}… · {e['empreinte_support_declaree'][:16]}…",
            f"{e['empreinte_parc_recalculee'][:16]}… · {e['empreinte_support_recalculee'][:16]}…",
            e["empreinte_parc_declaree"] == e["empreinte_parc_recalculee"]
            and e["empreinte_support_declaree"] == e["empreinte_support_recalculee"])
    v1, v2, p = (m["verdicts"]["mediane_machine"], m["verdicts"]["support_reel"],
                 m["parite"]["p_mesuree"])
    ajouter("C10", "les deux enveloppes rendent des verdicts distincts et ordonnés",
            "support reçu · médiane non reçue",
            f"{v2['recue']} · {v1['recue']} · {m['enveloppe_support']['borne_basse']:.6f} "
            f"< {p:.6f} < {m['enveloppe_mediane']['borne_basse']:.6f}",
            v2["recue"] and not v1["recue"]
            and m["enveloppe_support"]["borne_basse"] < p < m["enveloppe_mediane"]["borne_basse"])
    return out


def certificat(m: Dict[str, Any]) -> Dict[str, Any]:
    eqs = equations(m)
    noeuds = [{**x, "resultat": None, "detail": None, "limite": None} for x in eqs]
    corps = {
        "dossier": "QPU_DISTANT",
        "job": {"id": m["registre"]["job"]["id"], "backend": m["registre"]["job"]["backend"],
                "status": m["registre"]["job"]["status"],
                "cree_le_utc": m["registre"]["job"]["cree_le_utc"],
                "cout_units": m["registre"]["job"]["cout_units"],
                "programme": m["registre"]["job"]["programme"],
                "tirs": m["registre"]["job"]["tirs"],
                "titulaire": m["registre"]["redaction"]["remplace_par"] + " : "
                            + m["registre"]["redaction"]["empreinte_compte_sha256_12"]},
        "circuit": m["registre"]["circuit"],
        "support_physique": m["support_physique"],
        "compte_portes": m["compte_portes"],
        "compteurs": m["compteurs"],
        "parite": m["parite"],
        "asymetrie": m["asymetrie"],
        "parite_ideale_simulee": m["simulation"],
        "enveloppe_mediane": m["enveloppe_mediane"],
        "enveloppe_support": m["enveloppe_support"],
        "verdicts": m["verdicts"],
        "duree": m["duree"],
        "empreintes": m["empreintes"],
        "horodatages_des_sources": {
            "calibrage_utc": m["calibrage"]["horodatage_utc"],
            "support_utc": m["support"]["horodatage_utc"],
            "machine": m["calibrage"]["machine"], "num_qubits_parc": m["calibrage"]["num_qubits"]},
        "portee_et_limites": {
            "qubit_physique_local": False,
            "executions_locales": 0,
            "reseau_appelle_par_ce_module": False,
            "ecritures_hors_artefacts": 0,
            "predictions_al_mizan_testees": 0,
            "enonces": [
                "Un seul job, une seule paire de qubits, 256 tirs : aucune généralisation "
                "n'est établie par ce dossier.",
                "Les deux enveloppes sont des bornes, pas des modèles de bruit : leurs "
                "verdicts sont rendus séparément et ne sont jamais fusionnés.",
                "Le registre de portes transpilées est extrait avec qiskit hors du dépôt ; "
                "il est lié à l'archive par l'empreinte du bloc QPY, recalculée ici.",
                "Ce tirage ne teste aucune équation d'AL-MIZAN : il borne ce qu'une "
                "exécution quantique distante autorise à écrire."]},
        "equations": noeuds,
    }
    corps["racine_merkle_sha256"] = _merkle(
        [_sha(json.dumps(x, sort_keys=True, ensure_ascii=False).encode("utf-8")) for x in noeuds])
    return corps


def verifier(donnees: Dict[str, Any]) -> bool:
    return all(c["ok"] for c in donnees["controles"])


def octets_certificat(cert: Dict[str, Any]) -> bytes:
    return (json.dumps(cert, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def octets_compteurs(m: Dict[str, Any]) -> bytes:
    """Le format Excel français du dépôt : BOM, « ; », CRLF, virgule décimale."""
    lignes = [["mot", "occurrences", "poids_de_paire"]]
    for mot, n in m["compteurs"].items():
        lignes.append([mot, n, "pair" if mot.count("1") % 2 == 0 else "impair"])
    lignes.append(["Σ", sum(m["compteurs"].values()), "—"])
    corps = "\r\n".join(";".join(str(v).replace(".", ",") for v in ligne) for ligne in lignes)
    return b"\xef\xbb\xbf" + (corps + "\r\n").encode("utf-8")


def octets_frontieres(m: Dict[str, Any]) -> bytes:
    e1, e2 = m["enveloppe_mediane"], m["enveloppe_support"]
    lignes = [["enveloppe", "source", "somme_eps", "borne_basse", "p_mesuree",
               "recue", "ecart_en_sigma"]]
    for nom, e, v in (("mediane_machine", e1, m["verdicts"]["mediane_machine"]),
                      ("support_reel", e2, m["verdicts"]["support_reel"])):
        lignes.append([nom, e["source"], e["somme_eps"], e["borne_basse"],
                       m["parite"]["p_mesuree"], "vrai" if v["recue"] else "faux",
                       v["ecart_en_sigma"]])
    corps = "\r\n".join(";".join(str(v).replace(".", ",") for v in ligne) for ligne in lignes)
    return b"\xef\xbb\xbf" + (corps + "\r\n").encode("utf-8")


def octets_svg(m: Dict[str, Any]) -> bytes:
    """Trois barres, aucun mot en langue : p mesurée et les deux bornes."""
    p = m["parite"]["p_mesuree"]
    b1, b2 = m["enveloppe_mediane"]["borne_basse"], m["enveloppe_support"]["borne_basse"]
    bas, haut = 0.88, 0.94
    largeur, hauteur, marge = 900, 360, 56

    def y(v: float) -> float:
        return hauteur - marge - (v - bas) / (haut - bas) * (hauteur - 2 * marge)

    barres = [("p", p, "#1f5f8b"), ("1-2\u03a3\u03b5 sup", b2, "#0f7b52"),
              ("1-2\u03a3\u03b5 med", b1, "#b45309")]
    corps_svg = []
    for i, (etiq, v, couleur) in enumerate(barres):
        x = marge + 60 + i * 240
        corps_svg.append(
            f"<rect x='{x}' y='{y(v):.2f}' width='150' height='{hauteur - marge - y(v):.2f}' "
            f"fill='{couleur}'/>"
            f"<text x='{x + 75}' y='{y(v) - 10:.2f}' text-anchor='middle' font-size='22' "
            f"fill='#10263a'>{v:.6f}</text>"
            f"<text x='{x + 75}' y='{hauteur - 22}' text-anchor='middle' font-size='20' "
            f"fill='#10263a'>{etiq}</text>")
    for v in (0.88, 0.90, 0.92, 0.94):
        corps_svg.append(f"<line x1='{marge}' y1='{y(v):.2f}' x2='{largeur - 20}' "
                         f"y2='{y(v):.2f}' stroke='#c9d4de'/>"
                         f"<text x='{marge - 8}' y='{y(v) + 6:.2f}' text-anchor='end' "
                         f"font-size='16' fill='#5b6b7a'>{v:.2f}</text>")
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{largeur}' height='{hauteur}' "
            f"viewBox='0 0 {largeur} {hauteur}' role='img' "
            f"aria-label='p mesure et deux bornes d enveloppe'>"
            f"<rect width='{largeur}' height='{hauteur}' fill='#ffffff'/>"
            + "".join(corps_svg) + f"</svg>\n").encode("utf-8")


def ecrire_artefacts(m: Dict[str, Any], vers: Path = ARTEFACTS) -> Dict[str, Any]:
    (vers / "figures").mkdir(parents=True, exist_ok=True)
    rendu: Dict[str, Any] = {}
    ecritures = [("certificat.json", octets_certificat(certificat(m))),
                 ("compteurs.csv", octets_compteurs(m)),
                 ("frontieres.csv", octets_frontieres(m)),
                 ("figures/frontieres.svg", octets_svg(m))]
    for nom, octets in ecritures:
        (vers / nom).write_bytes(octets)
        rendu[nom] = {"octets": len(octets), "sha256": _sha(octets)}
    return rendu


def resoudre() -> Dict[str, Any]:
    m = mesurer()
    eqs = {x["id"]: x for x in equations(m)}
    cs = controles(m)
    cert = certificat(m)
    return {"source": {"dossier": "QPU_DISTANT", "fournisseur": "IBM Quantum",
                       "machine": m["registre"]["job"]["backend"],
                       "job": m["registre"]["job"]["id"],
                       "archive_attestee": m["empreintes"]["sha256_zip_atteste"],
                       "publices": list(PUBLIES)},
            "mesure": m, "certificat": cert,
            "equations": list(eqs.values()), "controles": cs,
            "conclusion": {
                "controles_verts": sum(1 for c in cs if c["ok"]), "controles_total": len(cs),
                "equations": len(eqs),
                "statuts_par_label": {st: sum(1 for x in eqs.values() if x["statut"] == st)
                                      for st in ("OPÉRATIONNEL", "SIMULÉ", "SPÉCIFIÉ")},
                "verdict_paires": "PAIRE DE BELL OBSERVÉE — parité 234/256",
                "verdict_enveloppes": {k: v["recue"] for k, v in m["verdicts"].items()},
                "racine_merkle_sha256": cert["racine_merkle_sha256"]}}


def principal() -> int:
    donnees = resoudre()
    if "--ecrit" in sys.argv[1:]:
        donnees["artefacts"] = ecrire_artefacts(donnees["mesure"])
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if "--json" in sys.argv[1:]:
        sortie = {"source": donnees["source"], "conclusion": donnees["conclusion"],
                  "equations": [{k: e[k] for k in ("id", "formule", "resultat", "statut")}
                                for e in donnees["equations"]],
                  "controles": [{k: c[k] for k in ("id", "nom", "attendu", "obtenu", "ok")}
                                for c in donnees["controles"]]}
        if "artefacts" in donnees:
            sortie["artefacts"] = donnees["artefacts"]
        print(json.dumps(sortie, ensure_ascii=False, indent=1))
    else:
        for c in donnees["controles"]:
            print(f"{'OK  ' if c['ok'] else 'ECHEC'} {c['id']} {c['nom']} :: "
                  f"attendu {c['attendu']} / obtenu {c['obtenu']}")
        con = donnees["conclusion"]
        print(f"CONTROLES {con['controles_verts']}/{con['controles_total']} · "
              f"EQUATIONS {con['equations']} · RACINE {con['racine_merkle_sha256'][:16]}…")
    return 0 if verifier(donnees) else 1


if __name__ == "__main__":
    raise SystemExit(principal())
