# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""GOULETS — ce qui borne réellement une chaîne de publication, mesuré.

La demande adressée au dépôt était : « étudier et poser les équations pour résoudre les
goulots d'étranglement et être inarrêtable ». Le mot « inarrêtable » n'a pas de définition
falsifiable et n'est donc pas repris. Il est remplacé par quatre bornes, chacune mesurée ou
déclarée à une date consignée, chacune accompagnée de la condition qui la rompt :

  1. la borne de **durée** : 900 s par vidéo, seuil que le fournisseur attache à la levée
     d'un verrou ; la plus longue vidéo publiée mesure 30 s ;
  2. la borne de **quota** : 10 000 unités par jour et 100 appels d'expédition, soit
     99 publications par jour au coût déclaré de 101 unités ;
  3. la borne **effectivement observée** : 10 publications sur un seul jour, avec un refus
     enregistré ce même jour — et un jour de refus à zéro publication, qui défait l'hypothèse
     d'un simple compteur journalier ;
  4. la borne **matérielle** : l'espace libre de l'hôte de production, converti en nombre de
     vidéos du gabarit moyen du stock.

Le taux d'emploi de la borne 3 par la cadence réellement tenue (borne mesurée 2) est de
13,5 % : la file n'est pas du côté de la plateforme. Ce dossier le mesure, il ne le démontre
pas pour les jours à venir, et n'avance aucune recette d'audience — le rapport
vues-publication y est consigné comme un fait, sans interprétation.

Ce que le module recalcule, avec la seule bibliothèque standard et à partir des six
instantanés publiés dans `sources/` :

  1. les empreintes SHA-256 des six instantanés, contre la table scellée à côté d'eux ;
  2. la cadence λ = N/E sur deux calendriers distincts — jours UTC et jours du Pacifique,
     ce dernier étant recalculé ici par la règle américaine du changement d'heure, sans
     dépendre d'une base tzdata installée sur la machine ;
  3. les durées, la capacité en unités et le plafond effectif, en rapprochant le journal des
     refus du nombre de vidéos réellement publiées le même jour ;
  4. le taux d'emploi contre les deux plafonds, la couverture du stock par l'espace libre,
     et l'horizon de publication sous cadence constante (projection, étiquetée comme telle).

Ce qu'il ne fait pas : il n'appelle aucun réseau, ne relève aucun compte, ne publie rien,
n'écrit rien hors de `artefacts/`, et ne contient aucun jeton — les instantanés ne portent
que des compteurs publics, des durées, des identifiants de fichiers et des dates.

Usage :
    py -3 GOULETS/goulets_base.py             # 10 équations, 10 contrôles, rc 0 ou 1
    py -3 GOULETS/goulets_base.py --ecrit     # + certificat.json, CSV et SVG
    py -3 GOULETS/goulets_base.py --json      # rapport complet en JSON
"""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Sequence

DOSSIER = Path(__file__).resolve().parent
SOURCES = DOSSIER / "sources"
ARTEFACTS = DOSSIER / "artefacts"

# Aucun de ces noms ne porte de date : le nom entre dans MANIFESTE_SHA256.txt, et le sceau
# d'AL-MIZAN ne doit porter aucune date (contrôlée par DECLARATION C04). La prise de chaque
# instantané reste consignée à l'intérieur du fichier, champ mesure_le_utc.
F_YOUTUBE = "youtube.json"
F_QUOTAS = "quotas_declares.json"
F_DISQUE = "disque.json"
F_STOCK = "backlog_local.json"
F_VIDEO = "video_source.json"
F_PLAFOND = "plafond_chaine.json"
F_EMPREINTES = "EMPREINTES.json"

PUBLIES = (F_YOUTUBE, F_QUOTAS, F_DISQUE, F_STOCK, F_VIDEO, F_PLAFOND)

# Le seuil de durée que le fournisseur attache à la levée du verrou, en secondes.
SEUIL_DUREE_DECLARE_S = 900.0
# Une publication complète au sens du barème : créer, régler les métadonnées, poser la vignette.
COMPOSANTS_PUBLICATION = ("videos.insert", "videos.update", "thumbnails.set")
HEURE_D_ETE = timedelta(hours=-7)
HEURE_D_HIVER = timedelta(hours=-8)


# ----------------------------------------------------------------------------
# lecture des instantanés publiés
# ----------------------------------------------------------------------------
def _sha(brut: bytes) -> str:
    return hashlib.sha256(brut).hexdigest()


def _octets(nom: str) -> bytes:
    return (SOURCES / nom).read_bytes()


def _json(nom: str) -> Any:
    return json.loads(_octets(nom).decode("utf-8"))


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
    rendu["racine_declaree"] = _json(F_EMPREINTES)["racine_sha256"]
    rendu["racine_recalculee"] = _sha(
        "".join(f"{k}{v['sha256']}" for k, v in sorted(table.items())).encode("utf-8"))
    return rendu


def youtube() -> Dict[str, Any]:
    return _json(F_YOUTUBE)


def quotas() -> Dict[str, Any]:
    return _json(F_QUOTAS)


def disque() -> Dict[str, Any]:
    return _json(F_DISQUE)


def stock() -> Dict[str, Any]:
    return _json(F_STOCK)


def video_source() -> Dict[str, Any]:
    return _json(F_VIDEO)


def journal_plafond() -> Dict[str, Any]:
    return _json(F_PLAFOND)


# ----------------------------------------------------------------------------
# le jour du Pacifique, recalculé ici et non importé d'une base tzdata
# ----------------------------------------------------------------------------
def _nieme_dimanche(annee: int, mois: int, n: int) -> date:
    """Le `n`-ième dimanche du mois — la règle américaine s'exprime en dimanches, pas en dates."""
    premier = date(annee, mois, 1)
    return premier + timedelta(days=(6 - premier.weekday()) % 7, weeks=n - 1)


def decalage_pacifique(instant_utc: datetime) -> timedelta:
    """UTC-7 entre le 2e dimanche de mars 02:00 et le 1er dimanche de novembre 02:00, sinon UTC-8.

    Les bornes sont écrites en UTC (10:00 et 09:00) parce que le changement d'heure se
    décrète à 02:00 heure locale, pas à 02:00 UTC.
    """
    a = instant_utc.year
    debut = datetime.combine(_nieme_dimanche(a, 3, 2), time(10), tzinfo=timezone.utc)
    fin = datetime.combine(_nieme_dimanche(a, 11, 1), time(9), tzinfo=timezone.utc)
    return HEURE_D_ETE if debut <= instant_utc < fin else HEURE_D_HIVER


def instants_des_publications() -> List[datetime]:
    out = []
    for p in youtube()["publications"]:
        i = datetime.fromisoformat(p["publie_le_utc"].replace("Z", "+00:00"))
        out.append(i if i.tzinfo else i.replace(tzinfo=timezone.utc))
    return sorted(out)


# ----------------------------------------------------------------------------
# cadence, durées, plafonds
# ----------------------------------------------------------------------------
def cadence() -> Dict[str, Any]:
    instants = instants_des_publications()
    jours_utc = Counter(i.date().isoformat() for i in instants)
    jours_pt = Counter((i + decalage_pacifique(i)).date().isoformat() for i in instants)
    premiere, derniere = instants[0], instants[-1]
    emprise_utc = (derniere.date() - premiere.date()).days + 1
    emprise_pt = (((derniere + decalage_pacifique(derniere)).date())
                  - ((premiere + decalage_pacifique(premiere)).date())).days + 1
    n = len(instants)
    return {"publiees": n,
            "premiere_utc": premiere.isoformat(), "derniere_utc": derniere.isoformat(),
            "jours_utc": dict(sorted(jours_utc.items())),
            "jours_pacifique": dict(sorted(jours_pt.items())),
            "jours_actifs_utc": len(jours_utc), "jours_actifs_pacifique": len(jours_pt),
            "emprise_jours_utc": emprise_utc, "emprise_jours_pacifique": emprise_pt,
            "lambda_par_jour_utc": n / emprise_utc,
            "lambda_par_jour_pacifique": n / emprise_pt,
            "devoir": len(jours_utc) / emprise_utc,
            "pic_utc": max(jours_utc.values()), "pic_pacifique": max(jours_pt.values()),
            "identiques": sorted(jours_utc.items()) == sorted(jours_pt.items())}


def durees() -> Dict[str, Any]:
    pub = [p for p in youtube()["publications"] if p.get("secondes") is not None]
    s = [float(p["secondes"]) for p in pub]
    return {"comptees": len(s), "total_s": round(sum(s), 3),
            "moyenne_s": sum(s) / len(s), "max_s": max(s), "min_s": min(s),
            "seuil_declare_s": SEUIL_DUREE_DECLARE_S,
            "marge_avant_seuil_s": SEUIL_DUREE_DECLARE_S - max(s),
            "franchissement_du_seuil": max(s) > SEUIL_DUREE_DECLARE_S,
            "verrou_fournisseur": youtube()["chaine"]["longUploadsStatus"]}


def capacite_declaree() -> Dict[str, Any]:
    q = quotas()
    couts = q["couts_unites_par_appel"]
    components = {c: couts[c] for c in COMPOSANTS_PUBLICATION}
    cout = sum(components.values())
    reserve = q["reserve_unites_par_jour"]
    capacite_unites = int(reserve // cout)
    plafond_appels = q["plafonds_appels_par_jour"]["videos.insert"]
    return {"composants": components, "cout_par_publication": cout,
            "reserve_unites_par_jour": reserve, "capacite_en_unites": capacite_unites,
            "plafond_appels_par_jour": plafond_appels,
            "capacite_declaree_par_jour": min(capacite_unites, plafond_appels),
            "citation": q["citation_verbatim"], "reinitialisation": q["reinitialisation"]}


def plafond_constate() -> Dict[str, Any]:
    j = journal_plafond()
    par_jour = j["par_jour_pacifique"]
    jours_refus = sorted({d for d, v in par_jour.items() if v["raisons"]})
    avec_publication = {d: v["publiees_ce_jour"] for d, v in par_jour.items()
                        if v["publiees_ce_jour"] > 0}
    jours_sans_publication = [d for d in jours_refus if par_jour[d]["publiees_ce_jour"] == 0]
    reasons = sorted({r for v in par_jour.values() for r in v["raisons"]})
    return {"jours_avec_refus": jours_refus,
            "raisons_rencontrees": {r: j["jours_par_raison"].get(r, []) for r in reasons},
            "max_publiees_un_jour": max(avec_publication.values()),
            "jour_du_max": max(avec_publication, key=lambda d: (avec_publication[d], d)),
            "suites_publiees_par_jour": [avec_publication[d] for d in sorted(avec_publication)],
            "jours_refus_sans_publication": jours_sans_publication,
            "loi_temporele_etablie": False,
            "citation_raison": j["citation_raison"]}


def emploi(cad: Dict[str, Any], cap: Dict[str, Any], plaf: Dict[str, Any]) -> Dict[str, Any]:
    lam = cad["lambda_par_jour_pacifique"]
    b_eff, b_doc = plaf["max_publiees_un_jour"], cap["capacite_declaree_par_jour"]
    return {"lambda_par_jour": lam, "borne_effective_par_jour": b_eff,
            "borne_declaree_par_jour": b_doc,
            "taux_emploi_effectif": lam / b_eff, "taux_emploi_declare": lam / b_doc,
            "rapport_des_deux_bornes": b_doc / b_eff,
            "marges_jours_par_jour": {"effective": b_eff - lam, "declaree": b_doc - lam},
            "aucune_borne_atteinte": lam < min(b_eff, b_doc)}


def audience() -> Dict[str, Any]:
    st = youtube()["statistiques"]
    vues, videos = int(st["viewCount"]), int(st["videoCount"])
    return {"vues": vues, "abonnes": int(st["subscriberCount"]), "videos": videos,
            "vues_par_publication": vues / videos, "abonnes_masques": st.get(
                "hiddenSubscriberCount") is True}


def inventaire_stock() -> Dict[str, Any]:
    lignes = stock()["fichiers"]
    octets = sum(l["octets"] for l in lignes)
    lues = [l for l in lignes if l.get("secondes") is not None]
    secondes = sum(float(l["secondes"]) for l in lues)
    par_dossier: Dict[str, Dict[str, Any]] = {}
    for l in lignes:
        d = par_dossier.setdefault(l["dossier"], {"fichiers": 0, "octets": 0, "secondes": 0.0})
        d["fichiers"] += 1
        d["octets"] += l["octets"]
        d["secondes"] += float(l["secondes"] or 0.0)
    for d in par_dossier.values():
        d["secondes"] = round(d["secondes"], 3)
    n = len(lignes)
    return {"fichiers": n, "octets": octets, "secondes": round(secondes, 3),
            "durees_non_lues": len(lignes) - len(lues),
            "gabarit_moyen_octets": octets / n, "dossiers": par_dossier,
            "doublons": par_dossier.get("vibe_videos_doublons", {"fichiers": 0, "octets": 0})}


def marge_disque(inv: Dict[str, Any]) -> Dict[str, Any]:
    d = disque()
    libre, total = int(d["octets_libres"]), int(d["octets_totaux"])
    gabarit = inv["gabarit_moyen_octets"]
    return {"octets_libres": libre, "octets_totaux": total,
            "part_libre": libre / total, "appel_reussi": bool(d["appel_reussi"]),
            "gabarit_moyen_octets": gabarit,
            "videos_du_gabarit_acceptees": int(libre // gabarit),
            "stock_deja_ecrit": inv["fichiers"],
            "le_stock_tient": inv["fichiers"] <= int(libre // gabarit)}


def horizon(cad: Dict[str, Any], inv: Dict[str, Any], plaf: Dict[str, Any]) -> Dict[str, Any]:
    n = inv["fichiers"]
    lam, b = cad["lambda_par_jour_pacifique"], plaf["max_publiees_un_jour"]
    return {"fichiers_a_publier": n, "jours_a_cadence_tenue": n / lam,
            "jours_au_plafond_effectif": n / b, "plafond_effectif_par_jour": b,
            "hypothese": "projection linéaire : la cadence observée et le plafond mesuré "
                         "tenus constants, sans hypothèse sur la production à venir"}


def chapitres_source() -> Dict[str, Any]:
    v = video_source()
    t = [float(x["debut_s"]) for x in v["chapitres"]]
    return {"titre": v["titre"], "auteur": v["auteur"], "duree_s": v["duree_s"],
            "chapitres": len(v["chapitres"]), "croissants": all(b > a for a, b in zip(t, t[1:])),
            "dernier_dans_la_duree": t[-1] <= v["duree_s"],
            "transcript": "non sondé", "avertissement": v["avertissement"]}


# ----------------------------------------------------------------------------
# agrégat de mesure
# ----------------------------------------------------------------------------
def _merkle(hashes: Sequence[str]) -> str:
    if not hashes:
        return hashlib.sha256(b"").hexdigest()
    niveau = list(hashes)
    while len(niveau) > 1:
        if len(niveau) % 2:
            niveau.append(niveau[-1])
        niveau = [hashlib.sha256((a + b).encode("utf-8")).hexdigest()
                  for a, b in zip(niveau[0::2], niveau[1::2])]
    return niveau[0]


def mesurer() -> Dict[str, Any]:
    cad, cap, plaf = cadence(), capacite_declaree(), plafond_constate()
    inv = inventaire_stock()
    return {"empreintes_des_sources": empreintes_des_sources(),
            "chaine": youtube()["chaine"], "statistiques": youtube()["statistiques"],
            "cadence": cad, "durees": durees(), "capacite": cap, "plafond": plaf,
            "emploi": emploi(cad, cap, plaf), "audience": audience(),
            "stock": inv, "disque": marge_disque(inv),
            "horizon": horizon(cad, inv, plaf), "video": chapitres_source(),
            "horodatages": {p: _json(p)["mesure_le_utc"] for p in PUBLIES}}


NOEUDS = {
    "EQ-01": {"depend": [], "externe": "six instantanés consigné hors du dépôt, puis écrits ici"},
    "EQ-02": {"depend": ["EQ-01"], "externe": "playlist d'expédition lue en lecture seule"},
    "EQ-03": {"depend": ["EQ-02"], "externe": "règle américaine du changement d'heure, "
                                               "recalculée sans tzdata"},
    "EQ-04": {"depend": ["EQ-01"], "externe": "durées lues dans les boîtes mvhd des fichiers"},
    "EQ-05": {"depend": ["EQ-01"], "externe": "barème de coûts publié par le fournisseur"},
    "EQ-06": {"depend": ["EQ-01", "EQ-03"], "externe": "journal local de l'opérateur, "
                                                       "horodaté localement"},
    "EQ-07": {"depend": ["EQ-02", "EQ-05", "EQ-06"], "externe": None},
    "EQ-08": {"depend": ["EQ-01"], "externe": "compteurs publics de la chaîne"},
    "EQ-09": {"depend": ["EQ-01"], "externe": "stat() de l'hôte de production"},
    "EQ-10": {"depend": ["EQ-02", "EQ-09"], "externe": None},
}


def _eq(id_: str, chemin: str, formule: str, resultat: str, statut: str,
        limite: str, detail: Any) -> Dict[str, Any]:
    n = NOEUDS[id_]
    return {"id": id_, "chemin": chemin, "formule": formule, "resultat": resultat,
            "statut": statut, "limite": limite, "detail": detail,
            "couche": "S1 MESURABLE",
            "piliers": ["P1 UNITE", "P2 BORNE", "P3 CONFRONTATION", "P4 TRANSMISSION"],
            "depend_de": n["depend"], "fonde_hors_du_dossier": n["externe"]}


def equations(m: Dict[str, Any]) -> List[Dict[str, Any]]:
    cad, d4, cap = m["cadence"], m["durees"], m["capacite"]
    plaf, emp, aud = m["plafond"], m["emploi"], m["audience"]
    inv, dis, hor = m["stock"], m["disque"], m["horizon"]
    e = m["empreintes_des_sources"]
    ch = "GOULETS/goulets_base.py → "
    return [
        _eq("EQ-01", ch + "empreintes_des_sources()",
            "SHA-256(instantané) pour les six fichiers · racine = SHA-256(nom+empreinte triés)",
            f"{sum(1 for v in e.values() if isinstance(v, dict) and v['ok'])}/{len(PUBLIES)} "
            f"conformes · racine {e['racine_recalculee'][:16]}…", "OPÉRATIONNEL",
            "l'empreinte atteste que l'octet lu est celui qui a été consigné à la date dite ; "
            "elle ne dit pas que la mesure était juste le jour de sa prise.",
            {"racine_declaree": e["racine_declaree"],
             "coincide": e["racine_declaree"] == e["racine_recalculee"],
             "hors_table": e["hors_table"]}),
        _eq("EQ-02", ch + "cadence()",
            "λ = N/E · devoir = J_actifs/E",
            f"λ = {cad['publiees']}/{cad['emprise_jours_pacifique']} = "
            f"{cad['lambda_par_jour_pacifique']:.6f} /jour · devoir "
            f"{cad['devoir']:.6f} ({cad['jours_actifs_utc']} jours actifs sur "
            f"{cad['emprise_jours_utc']})", "OPÉRATIONNEL",
            "λ est une moyenne sur l'emprise de la chaîne, pas une cadence tenue : le devoir "
            "de {0:.4f} dit que {1} jours sur {2} seulement ont porté une publication. "
            "Aucune valeur future n'en est déduite.".format(
                cad["devoir"], cad["jours_actifs_utc"], cad["emprise_jours_utc"]),
            {"premiere_utc": cad["premiere_utc"], "derniere_utc": cad["derniere_utc"],
             "lambda_utc": cad["lambda_par_jour_utc"]}),
        _eq("EQ-03", ch + "decalage_pacifique() → cadence()",
            "jour_pacifique = date(instant + δ(instant)) · δ = −7h en été, −8h en hiver",
            f"{cad['jours_pacifique']} en jours du Pacifique contre {cad['jours_utc']} en "
            f"jours UTC · mêmes comptes, libellés décalés : {not cad['identiques']}",
            "OPÉRATIONNEL",
            "le fournisseur déclare sa réinitialisation « at midnight Pacific Time » : un "
            "décompte en jours UTC attribue donc des publications au mauvais jour. La règle "
            "de δ est recalculée ici, sans base tzdata, et ne vaut que pour le fuseau "
            "américain du Pacifique.",
            {"identiques": cad["identiques"],
             "ecart": sorted(set(cad["jours_utc"]) ^ set(cad["jours_pacifique"]))}),
        _eq("EQ-04", ch + "durees()",
            "max(d) vs S_declare · verrou = longUploadsStatus",
            f"max {d4['max_s']} s · moyenne {d4['moyenne_s']:.3f} s sur {d4['comptees']} · "
            f"seuil {d4['seuil_declare_s']} s · marge {d4['marge_avant_seuil_s']} s · verrou "
            f"« {d4['verrou_fournisseur']} »", "OPÉRATIONNEL",
            "le seuil de 900 s est la borne que le fournisseur attache à la levée du verrou, "
            "pas une capacité mesurée d'expédition : aucune vidéo plus longue n'a été tentée, "
            "donc la hauteur réelle du plafond de durée reste non éprouvée.",
            {"franchissement": d4["franchissement_du_seuil"], "min_s": d4["min_s"],
             "total_s": d4["total_s"]}),
        _eq("EQ-05", ch + "capacite_declaree()",
            "c = Σ coûts · capacité = min(⌊R/c⌋, plafond d'appels)",
            f"c = {cap['cout_par_publication']} unités "
            f"({cap['composants']}) · ⌊{cap['reserve_unites_par_jour']}/{cap['cout_par_publication']}"
            f"⌋ = {cap['capacite_en_unites']} · appels {cap['plafond_appels_par_jour']} · "
            f"capacité déclarée {cap['capacite_declaree_par_jour']}/jour", "SPÉCIFIÉ",
            "entièrement issu du barème publié par le fournisseur : le quota réellement "
            "alloué à CE projet n'est pas lu par le dépôt, qui ne mesure ici qu'une "
            "conséquence arithmétique d'une table déclarée.",
            {"citation": cap["citation"], "reinitialisation": cap["reinitialisation"]}),
        _eq("EQ-06", ch + "plafond_constate()",
            "plafond_effectif = max_jour(publiées) sur les jours portant un refus",
            f"{plaf['max_publiees_un_jour']} publiées le {plaf['jour_du_max']} avec refus ce "
            f"jour-là · suite {plaf['suites_publiees_par_jour']} · refus à zéro publication "
            f"le {plaf['jours_refus_sans_publication']}", "OPÉRATIONNEL",
            "un refus est enregistré un jour où aucune vidéo n'a été publiée : la loi "
            "temporelle du plafond n'est donc PAS un compteur qui se remet à zéro à minuit, "
            "et le dépôt ne l'établit pas. Seule la valeur instantanée "
            f"({plaf['max_publiees_un_jour']}/jour) est mesurée, sur {len(plaf['jours_avec_refus'])} "
            "jours de journal.",
            {"jours_avec_refus": plaf["jours_avec_refus"],
             "loi_temporele_etablie": plaf["loi_temporele_etablie"],
             "raisons": plaf["raisons_rencontrees"]}),
        _eq("EQ-07", ch + "emploi()",
            "ρ = λ / borne",
            f"ρ_effectif = {emp['taux_emploi_effectif']:.6f} (λ = "
            f"{emp['lambda_par_jour']:.6f} / {emp['borne_effective_par_jour']}) · ρ_declare = "
            f"{emp['taux_emploi_declare']:.6f} / {emp['borne_declaree_par_jour']} · les deux "
            f"bornes diffèrent d'un facteur {emp['rapport_des_deux_bornes']}", "OPÉRATIONNEL",
            "ρ mesure l'emploi d'une capacité, il n'établit pas que la capacité suivante "
            "sera atteignable : la borne effective est un maximum observé, pas un droit, et "
            "le rapport de 9,9 est celui d'une table déclarée à un fait observé.",
            {"aucune_borne_atteinte": emp["aucune_borne_atteinte"],
             "marges": emp["marges_jours_par_jour"]}),
        _eq("EQ-08", ch + "audience()",
            "vues / publications · abonnés",
            f"{aud['vues']} vues pour {aud['videos']} vidéos = "
            f"{aud['vues_par_publication']:.6f} vue par publication · {aud['abonnes']} abonné",
            "OPÉRATIONNEL",
            "compteurs publics à une date, sans décomposition par origine ni par durée de "
            "visionnage : ce rapport ne dit rien de ce qui le produirait, et aucune recette "
            "d'audience n'est avancée dans ce dossier.",
            {"abonnes_masques": aud["abonnes_masques"],
             "borne_goulot": "la diffusion n'est pas la mise en ligne"}),
        _eq("EQ-09", ch + "inventaire_stock() → marge_disque()",
            "marge = ⌊octets_libres / (Σoctets / n)⌋",
            f"stock {inv['fichiers']} fichiers · {inv['octets']} o · {inv['secondes']} s · "
            f"gabarit moyen {inv['gabarit_moyen_octets']:.3f} o · libre "
            f"{dis['octets_libres']} o ({dis['part_libre']:.6f} du volume) → "
            f"{dis['videos_du_gabarit_acceptees']} vidéos", "OPÉRATIONNEL",
            "instantané propre à l'hôte de production : un autre poste rend un autre chiffre. "
            "Le stock est déjà écrit, donc la marge compte ce que l'on peut AJOUTER, et les "
            "vidéos publiées ne libèrent pas l'espace local.",
            {"dossiers": inv["dossiers"], "durees_non_lues": inv["durees_non_lues"],
             "le_stock_tient": dis["le_stock_tient"]}),
        _eq("EQ-10", ch + "horizon()",
            "jours = n / λ · jours = n / borne_effective",
            f"{hor['fichiers_a_publier']} fichiers : {hor['jours_a_cadence_tenue']:.3f} jours "
            f"à la cadence tenue contre {hor['jours_au_plafond_effectif']:.3f} jour(s) au "
            f"plafond observé · {hor['hypothese']}", "SIMULÉ",
            "projection linéaire de deux nombres mesurés : elle suppose λ constant et le "
            "plafond non abaissé, et ne prédit rien. L'écart entre les deux durées est "
            "exactement le rapport des deux rythmes, pas une découverte sur la chaîne.",
            {"rapport_rythmes": hor["jours_a_cadence_tenue"]
                                / hor["jours_au_plafond_effectif"],
             "plafond_effectif_par_jour": hor["plafond_effectif_par_jour"]}),
    ]


def controles(m: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []

    def ajouter(id_: str, nom: str, attendu: Any, obtenu: Any, ok: bool) -> None:
        # C0n contrôle EQ-0n : le nom de contrôle est la chaîne continue que P1 exige,
        # l'équation contrôlée s'en déduit, aucune table de correspondance à maintenir.
        eq = {x["id"]: x for x in equations(m)}["EQ-" + id_[1:]]
        out.append({"id": id_, "nom": nom, "attendu": str(attendu), "obtenu": str(obtenu),
                    "ok": bool(ok), "limite": eq["limite"]})

    cad, d4, cap = m["cadence"], m["durees"], m["capacite"]
    plaf, emp, aud = m["plafond"], m["emploi"], m["audience"]
    inv, dis = m["stock"], m["disque"]

    e = m["empreintes_des_sources"]
    conformes = [n for n, v in e.items() if isinstance(v, dict) and v["ok"]]
    ajouter("C01", "les six instantanés correspondent à l'empreinte scellée, rien hors table",
            f"{len(PUBLIES)}/{len(PUBLIES)}", f"{len(conformes)}/{len(PUBLIES)}",
            len(conformes) == len(PUBLIES) and not e["hors_table"]
            and e["racine_declaree"] == e["racine_recalculee"])
    n = cad["publiees"]
    ajouter("C02", "les deux histogrammes somment au compte de vidéos déclaré par la chaîne",
            f"{n} = {m['statistiques']['videoCount']}",
            f"{sum(cad['jours_utc'].values())} UTC · {sum(cad['jours_pacifique'].values())} PT"
            f" · chaîne {m['statistiques']['videoCount']}",
            sum(cad["jours_utc"].values()) == sum(cad["jours_pacifique"].values()) == n
            == int(m["statistiques"]["videoCount"]))
    ajouter("C03", "mêmes comptes quotidiens en UTC et en Pacifique, libellés décalés",
            "comptes identiques, jours distincts",
            f"{sorted(cad['jours_utc'].values())} vs {sorted(cad['jours_pacifique'].values())} "
            f"· jours différents {sorted(set(cad['jours_utc']) ^ set(cad['jours_pacifique']))} "
            f"· tables identiques {cad['identiques']}",
            sorted(cad["jours_utc"].values()) == sorted(cad["jours_pacifique"].values())
            and not cad["identiques"] and cad["pic_utc"] == cad["pic_pacifique"])
    ajouter("C04", "toutes les durées sont lues, sous le seuil déclaré, verrou levé",
            f"≤ {d4['seuil_declare_s']} s · verrou « allowed »",
            f"{d4['comptees']}/{n} · max {d4['max_s']} s · « {d4['verrou_fournisseur']} »",
            d4["comptees"] == n and not d4["franchissement_du_seuil"]
            and d4["verrou_fournisseur"] == "allowed" and d4["min_s"] > 0)
    ajouter("C05", "le coût déclaré d'une publication et la capacité qui en découle",
            "101 unités · ⌊10 000/101⌋ ≤ 100 appels",
            f"{cap['cout_par_publication']} unités · {cap['capacite_en_unites']} par unités · "
            f"{cap['plafond_appels_par_jour']} par appels",
            cap["cout_par_publication"] == sum(cap["composants"].values())
            and cap["capacite_en_unites"] == cap["reserve_unites_par_jour"]
            // cap["cout_par_publication"]
            and cap["capacite_declaree_par_jour"] == min(cap["capacite_en_unites"],
                                                         cap["plafond_appels_par_jour"]))
    ajouter("C06", "le plafond effectif est atteint un jour de refus et un refus existe à zéro "
                   "publication",
            f"max {plaf['max_publiees_un_jour']} avec refus · ≥ 1 jour à 0",
            f"{plaf['jour_du_max']} = {plaf['max_publiees_un_jour']} · zéro publication le "
            f"{plaf['jours_refus_sans_publication']}",
            plaf["max_publiees_un_jour"] == cad["pic_pacifique"]
            and plaf["jours_refus_sans_publication"]
            and plaf["max_publiees_un_jour"] < cap["capacite_declaree_par_jour"])
    ajouter("C07", "les deux taux d'emploi restent strictement sous 1 et se distinguent",
            "ρ_effectif < 1 · ρ_declare < 1 · ρ_effectif > ρ_declare",
            f"{emp['taux_emploi_effectif']:.6f} · {emp['taux_emploi_declare']:.6f} · "
            f"rapport {emp['rapport_des_deux_bornes']}",
            emp["aucune_borne_atteinte"]
            and emp["taux_emploi_effectif"] > emp["taux_emploi_declare"]
            and abs(emp["taux_emploi_effectif"]
                    - emp["lambda_par_jour"] / emp["borne_effective_par_jour"]) < 1e-12)
    ajouter("C08", "les compteurs publics se laissent diviser et l'un au moins est brut",
            "vues ≥ publications · rapport recalculé",
            f"{aud['vues']} ≥ {aud['videos']} · {aud['vues_par_publication']:.6f} · "
            f"{aud['abonnes']} abonné",
            aud["vues"] >= aud["videos"]
            and abs(aud["vues_par_publication"] - aud["vues"] / aud["videos"]) < 1e-12
            and aud["abonnes"] >= 1)
    lignes = stock()["fichiers"]
    ajouter("C09", "le stock se recalcule ligne à ligne, sans durée perdue",
            f"{inv['fichiers']} fichiers · 0 durée non lue",
            f"{len(lignes)} lignes · {sum(l['octets'] for l in lignes)} o · "
            f"{inv['durees_non_lues']} non lues",
            len(lignes) == inv["fichiers"] and inv["durees_non_lues"] == 0
            and sum(l["octets"] for l in lignes) == inv["octets"]
            and all(l.get("secondes") and l["secondes"] > 0 for l in lignes))
    hor = m["horizon"]
    ajouter("C10", "l'espace libre accepte le stock et la marge excède ce qui est déjà écrit",
            f"marge {dis['videos_du_gabarit_acceptees']} ≥ stock {inv['fichiers']}",
            f"{dis['videos_du_gabarit_acceptees']} ≥ {inv['fichiers']} · "
            f"libre {dis['octets_libres']} o · appel "
            f"{dis['appel_reussi']} · {hor['jours_au_plafond_effectif']:.3f} j au plafond",
            dis["appel_reussi"] and dis["octets_libres"] > 0
            and dis["videos_du_gabarit_acceptees"] >= inv["fichiers"]
            and hor["jours_au_plafond_effectif"] <= hor["jours_a_cadence_tenue"])
    return out


def certificat(m: Dict[str, Any]) -> Dict[str, Any]:
    eqs = equations(m)
    noeuds = [{**x, "resultat": None, "detail": None, "limite": None} for x in eqs]
    corps = {
        "dossier": "GOULETS",
        "sujet": "bornes mesurées d'une chaîne de publication vidéo",
        "demande_originelle": "étudier et poser les équations pour résoudre les goulots "
                              "d'étranglement et être inarrêtable",
        "requalification": "« inarrêtable » n'a pas de définition falsifiable : le dossier "
                           "pose quatre bornes datées, chacune avec la condition qui la rompt, "
                           "et n'affirme aucune impossibilité d'arrêter la chaîne",
        "chaine": {"id": m["chaine"]["id"], "titre": m["chaine"]["titre"],
                   "creee_le_utc": m["chaine"]["creee_le_utc"],
                   "longUploadsStatus": m["chaine"]["longUploadsStatus"]},
        "statistiques": m["statistiques"],
        "cadence": m["cadence"], "durees": m["durees"], "capacite_declaree": m["capacite"],
        "plafond_constate": m["plafond"], "emploi": m["emploi"], "audience": m["audience"],
        "stock": m["stock"], "disque": m["disque"], "horizon": m["horizon"],
        "video_source": m["video"],
        "horodatages_des_sources": m["horodatages"],
        "empreintes": {k: v for k, v in m["empreintes_des_sources"].items()},
        "portee_et_limites": {
            "reseau_appelle_par_ce_module": False,
            "ecritures_hors_artefacts": 0,
            "jetons_consignes": 0,
            "predictions_al_mizan_testees": 0,
            "enonces": [
                "Quatre bornes, quatre natures : la durée est mesurée contre un seuil déclaré, "
                "la capacité en unités vient d'un barème publié, le plafond de 10 par jour est "
                "un fait observé, la marge de disque est propre à cet hôte.",
                "Le plafond effectif (10/jour) est 9,9 fois plus bas que le plafond que le "
                "barème laisse calculer (99/jour) : la table publiée ne décrit pas la "
                "contrainte qui borne réellement cette chaîne.",
                "Un refus est consigné un jour sans aucune publication : la loi temporelle du "
                "plafond n'est pas établie par ces données, et le dossier ne l'invente pas.",
                "La cadence tenue (1,3529/jour) n'approche aucune des bornes : la contrainte "
                "mesurée est en amont de la plateforme, dans la production et la décision de "
                "publier — ce dossier ne mesure pas la première.",
                "Aucune recette d'audience, aucune promesse de croissance : le rapport "
                "vues-publication est consigné comme un compteur, sans interprétation.",
                "Le stock et la marge de disque sont des instantanés d'une machine : ils ne "
                "sont pas reproductibles sur une autre et ne prétendent pas l'être."]},
        "equations": noeuds,
    }
    corps["racine_merkle_sha256"] = _merkle(
        [_sha(json.dumps(x, sort_keys=True, ensure_ascii=False).encode("utf-8")) for x in noeuds])
    return corps


def verifier(donnees: Dict[str, Any]) -> bool:
    return all(c["ok"] for c in donnees["controles"])


def octets_certificat(cert: Dict[str, Any]) -> bytes:
    return (json.dumps(cert, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def octets_cadence(m: Dict[str, Any]) -> bytes:
    """Le format Excel français du dépôt : BOM, « ; », CRLF, virgule décimale."""
    cad, plaf = m["cadence"], m["plafond"]
    jours = sorted(set(cad["jours_utc"]) | set(cad["jours_pacifique"])
                   | set(plaf["jours_avec_refus"]))
    lignes = [["jour_utc_ou_pacifique", "publiees_jour_utc", "publiees_jour_pacifique",
               "refus_enregistre"]]
    for j in jours:
        lignes.append([j, cad["jours_utc"].get(j, 0), cad["jours_pacifique"].get(j, 0),
                       "vrai" if j in plaf["jours_avec_refus"] else "faux"])
    lignes.append(["Σ", cad["publiees"], cad["publiees"], len(plaf["jours_avec_refus"])])
    corps = "\r\n".join(";".join(str(v).replace(".", ",") for v in ligne) for ligne in lignes)
    return b"\xef\xbb\xbf" + (corps + "\r\n").encode("utf-8")


def octets_bornes(m: Dict[str, Any]) -> bytes:
    cap, plaf, emp, dis, inv = (m["capacite"], m["plafond"], m["emploi"], m["disque"],
                                m["stock"])
    cad, d4 = m["cadence"], m["durees"]
    lignes = [["borne", "valeur", "unite", "source", "cadre", "rompee_si"]]
    lignes += [
        ["duree", d4["seuil_declare_s"], "secondes", "déclaré", "seuil attaché au verrou",
         f"une vidéo publiée dépasse {d4['seuil_declare_s']:.0f} secondes"],
        ["duree_publiée_max", d4["max_s"], "secondes", "mesuré", "fait",
         "un instantané de chaîne plus récent rend un autre maximum"],
        ["capacite_unites", cap["capacite_declaree_par_jour"], "publications/jour", "déclaré",
         "barème publié", "le fournisseur modifie son barème ou son allocation projet"],
        ["plafond_effectif", plaf["max_publiees_un_jour"], "publications/jour", "mesuré",
         "fait", "un jour publie davantage sans refus, ou le plafond est relevé"],
        ["cadence_tenue", round(emp["lambda_par_jour"], 6), "publications/jour", "mesuré",
         "moyenne d'emprise", "la cadence observée change de valeur"],
        ["taux_emploi_effectif", round(emp["taux_emploi_effectif"], 6), "sans unité", "mesuré",
         "rapport", "le numérateur ou le dénominateur bouge"],
        ["marge_disque", dis["videos_du_gabarit_acceptees"], "vidéos", "mesuré",
         "instantané d'hôte", "l'espace libre descend sous un gabarit moyen"],
        ["stock_en_attente", inv["fichiers"], "fichiers", "mesuré", "instantané d'hôte",
         "le dossier change de contenu"],
    ]
    corps = "\r\n".join(";".join(str(v).replace(".", ",") for v in ligne) for ligne in lignes)
    return b"\xef\xbb\xbf" + (corps + "\r\n").encode("utf-8")


def octets_svg(m: Dict[str, Any]) -> bytes:
    """Trois barres, aucun mot en langue naturelle : les trois bornes quotidiennes réelles.

    La marge de disque est exclue de la figure : elle se compte en vidéos, les trois autres
    en publications par jour. Les mettre sur la même ordonnée exigerait de diviser l'une
    d'elles par un facteur choisi — ce que le tracé n'aurait pas pu dire. Elle reste dans
    `bornes.csv` et dans le certificat.
    """
    cap, plaf, emp = m["capacite"], m["plafond"], m["emploi"]
    series = [(f"{cap['capacite_declaree_par_jour']:.0f}/j",
               float(cap["capacite_declaree_par_jour"]), "#b45309"),
              (f"{plaf['max_publiees_un_jour']:.0f}/j",
               float(plaf["max_publiees_un_jour"]), "#1f5f8b"),
              (f"{emp['lambda_par_jour']:.2f}/j", emp["lambda_par_jour"], "#0f7b52")]
    largeur, hauteur, marge = 900, 360, 56
    grand = max(v for _, v, _ in series)
    corps = []
    for i, (etiq, v, couleur) in enumerate(series):
        x = marge + 90 + i * 260
        h = (hauteur - 2 * marge) * v / grand
        y = hauteur - marge - h
        corps.append(
            f"<rect x='{x}' y='{y:.2f}' width='150' height='{h:.2f}' fill='{couleur}'/>"
            f"<text x='{x + 75}' y='{y - 10:.2f}' text-anchor='middle' font-size='22' "
            f"fill='#10263a'>{v:.2f}</text>"
            f"<text x='{x + 75}' y='{hauteur - 22}' text-anchor='middle' font-size='20' "
            f"fill='#10263a'>{etiq}</text>")
    for v in (0.25, 0.5, 0.75, 1.0):
        y = hauteur - marge - (hauteur - 2 * marge) * v
        corps.append(f"<line x1='{marge}' y1='{y:.2f}' x2='{largeur - 20}' y2='{y:.2f}' "
                     f"stroke='#c9d4de'/>"
                     f"<text x='{marge - 8}' y='{y + 6:.2f}' text-anchor='end' font-size='16' "
                     f"fill='#5b6b7a'>{v * grand:.2f}</text>")
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{largeur}' height='{hauteur}' "
            f"viewBox='0 0 {largeur} {hauteur}' role='img' "
            f"aria-label='trois bornes par jour sur une echelle commune'>"
            f"<rect width='{largeur}' height='{hauteur}' fill='#ffffff'/>"
            + "".join(corps) + f"</svg>\n").encode("utf-8")


def ecrire_artefacts(m: Dict[str, Any], vers: Path = ARTEFACTS) -> Dict[str, Any]:
    (vers / "figures").mkdir(parents=True, exist_ok=True)
    rendu: Dict[str, Any] = {}
    for nom, octets in (("certificat.json", octets_certificat(certificat(m))),
                        ("cadence.csv", octets_cadence(m)),
                        ("bornes.csv", octets_bornes(m)),
                        ("figures/bornes.svg", octets_svg(m))):
        (vers / nom).write_bytes(octets)
        rendu[nom] = {"octets": len(octets), "sha256": _sha(octets)}
    return rendu


def resoudre() -> Dict[str, Any]:
    m = mesurer()
    eqs = {x["id"]: x for x in equations(m)}
    cs = controles(m)
    cert = certificat(m)
    return {"source": {"dossier": "GOULETS", "supports": "YouTube Data API v3 (lecture seule) "
                                                         "+ journal local de l'opérateur",
                       "chaine": m["chaine"]["id"], "mesures_utc": list(m["horodatages"].values()),
                       "publices": list(PUBLIES)},
            "mesure": m, "certificat": cert,
            "equations": list(eqs.values()), "controles": cs,
            "conclusion": {
                "controles_verts": sum(1 for c in cs if c["ok"]), "controles_total": len(cs),
                "equations": len(eqs),
                "statuts_par_label": {st: sum(1 for x in eqs.values() if x["statut"] == st)
                                      for st in ("OPÉRATIONNEL", "SIMULÉ", "SPÉCIFIÉ")},
                "verdict_bornes": (f"AUCUNE BORNE ATTEINTE — cadence "
                                   f"{m['emploi']['lambda_par_jour']:.4f}/jour contre plafond "
                                   f"{m['emploi']['borne_effective_par_jour']}/jour"),
                "bornes_par_jour": {"declaree": m["capacite"]["capacite_declaree_par_jour"],
                                    "effective": m["plafond"]["max_publiees_un_jour"],
                                    "tenue": m["emploi"]["lambda_par_jour"]},
                "goulots_non_plateformes": {
                    "production_en_amont": "non mesurée par ce dossier",
                    "diffusion": f"{m['audience']['vues_par_publication']:.4f} vues par "
                                 f"publication, {m['audience']['abonnes']} abonné"},
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
