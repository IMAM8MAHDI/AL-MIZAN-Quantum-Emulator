# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""Pages publiques FONDATION et CHIFFRES pour al-mizan.world, depuis le dépôt scellé.

Le dépôt `ZENODO_DEPOT_ALMIZAN` calcule et publie ; ce fichier met en forme pour le
site. Il n'ajoute aucune équation, ne re-arrange aucun nombre et ne convertit aucune
unité : les valeurs proviennent des modules du dépôt, reluqués contre
`MANIFESTE_SHA256.txt` avant usage. Les artefacts JSON, CSV et Markdown sont copiés
octet pour octet, donc ce que le site sert en données est exactement ce que l'archive
du DOI porte.

Le moteur `ABONDANCE/moteur_page_trilingue.py` est réutilité tel quel ; seule la
bloc « chemins » change, pour pointer les routes du site au lieu des fichiers du
dossier. Le garde-fou numérique du moteur refuse toute phrase anglaise ou arabe
énonçant un chiffre absent des lignes calculées.

Sorties, toutes en LF :
    web_cloud/fondation[_en|_ar].html        trois pages, 18 équations, NA62
    web_cloud/chiffres_pi[_en|_ar].html      trois pages, 17 équations, π-e-√2
    web_cloud/laboratoire[_en|_ar].html      trois pages, 15 équations, repère et trajectoire
    web_cloud/fondation_resultats.json       copie verbatim de FONDATION/artefacts/donnees
    web_cloud/chiffres_pi_resultats.json     copie verbatim de CHIFFRES/artefacts/donnees
    web_cloud/laboratoire_{resultats,certificats}.json  copies des artefacts HORLOGERIE
    web_cloud/laboratoire_trajectoire.svg            tracé du dépôt, recopié tel quel
    web_cloud/laboratoire_{trajectoire,stabilite,confrontation}.csv  idem, en CRLF Excel

Usage :
    py -3 pages_depot/generer_pages_site.py

Le dépôt n'est pas une dépendance du VPS : la passerelle sert des fichiers statiques
et aucun générateur ne tourne en production.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

RACINE = Path(__file__).resolve().parent.parent            # ASTRO-Q°ODE_SYSTEME
DEPOT = Path(os.environ.get("AL_MIZAN_DEPOT")
             or (RACINE.parent / "ZENODO_DEPOT_ALMIZAN"))
if not (DEPOT / "FONDATION" / "fondation_base.py").is_file():
    # depuis l'archive publiée, pages_depot/ est à la racine du dépôt : aucun voisin
    # n'est requis, et `git clone` puis `py -3 pages_depot/generer_pages_site.py` suffit.
    DEPOT = RACINE
WEB = RACINE / "web_cloud"
SITE = "https://www.al-mizan.world"
DOI_CONCEPT = "https://doi.org/10.5281/zenodo.24028242"
ARCHIVE_PUBLIEE = "10.5281/zenodo.24105422"
DEPOT_GITHUB = "https://github.com/IMAM8MAHDI/AL-MIZAN-Quantum-Emulator"

for _d in (str(DEPOT / "FONDATION"), str(DEPOT / "ABONDANCE"), str(RACINE / "pages_depot")):
    if _d not in sys.path:
        sys.path.insert(0, _d)

import moteur_page_trilingue as MOTEUR                      # noqa: E402
import generer_fondation as GF                              # noqa: E402


def _3(fr: str, en: str, ar: str) -> Dict[str, str]:
    return {"fr": fr, "en": en, "ar": ar}


def _vue_git(corps: bytes) -> bytes:
    """Le manifeste scelle le blob, soit les octets sans CR : `core.autocrlf=true`
    rend le dossier de travail en CRLF, la comparaison doit se faire sur la même vue."""
    return corps.replace(b"\r\n", b"\n")


def _sha(chemin: Path) -> str:
    return hashlib.sha256(_vue_git(chemin.read_bytes())).hexdigest()


def _manifeste() -> Dict[str, str]:
    """`MANIFESTE_SHA256.txt` du dépôt : {chemin posix: sha256 du blob}."""
    table: Dict[str, str] = {}
    for ligne in (DEPOT / "MANIFESTE_SHA256.txt").read_text(encoding="utf-8").splitlines():
        if "  " in ligne:
            sha, _, chemin = ligne.partition("  ")
            table[chemin.strip()] = sha.strip()
    return table


class Sceau:
    """Pointe d'entrée unique : chaque fichier du dépôt utilisé est vérifié au SHA-256."""

    def __init__(self) -> None:
        self.table = _manifeste()
        self.utilises: Dict[str, str] = {}

    def chemin(self, *parties: str) -> Path:
        cible = DEPOT.joinpath(*parties)
        cle = "/".join(parties)
        attendu = self.table.get(cle)
        if attendu is None:
            raise SystemExit(f"{cle} : absent du MANIFESTE_SHA256.txt du dépôt")
        obtenu = _sha(cible)
        if obtenu != attendu:
            raise SystemExit(f"{cle} : dérive entre le disque et le manifeste scellé "
                             f"({obtenu[:16]}… vs {attendu[:16]}…)")
        self.utilises[cle] = obtenu
        return cible


def _rebaser(spec: Dict[str, Any], base: str, liens: List[Dict[str, Any]]) -> Dict[str, str]:
    """Chemins du site dans le <head>, la nav de langue et le bouton « accueil »."""
    ch = {"fr": f"{SITE}{base}", "en": f"{SITE}{base}/en", "ar": f"{SITE}{base}/ar"}
    spec["chemins"] = ch
    spec["chapitres_nav"] = [("fr", "Français", ch["fr"]), ("en", "English", ch["en"]),
                             ("ar", "العربية", ch["ar"])]
    spec["liens"] = liens
    spec["index_href"] = f"{SITE}/"
    spec["index_libelle"] = _3("Accueil du site", "Site home", "الصفحة الرئيسية للموقع")
    return ch


def _fuite_none(texte: str) -> List[str]:
    """Un `str(None)` rendu se voit en tête du contenu d'un élément ou dans une valeur d'attribut.

    Le mot « None » d'une phrase anglaise (« None of these is offered as a discovery ») n'est
    pas une fuite : la recherche porte sur les positions de rendu, pas sur le mot.
    """
    corps = re.sub(r'<span class="lecture">.*?</span>', "", texte, flags=re.S)
    return re.findall(r'>\s*None\b|=\s*"\s*None\b', corps)


def _page(spec: Dict[str, Any], donnees: Dict[str, Any], vues: set,
          lang: str, cible: Path, traduire) -> Path:
    texte = MOTEUR.construire_page(spec, traduire(donnees, lang, vues), lang)
    fuite = _fuite_none(texte)
    if fuite:
        raise SystemExit(f"{cible.name} : un « None » de rendu fuite dans la page "
                         f"({len(fuite)} position(s), premier : {fuite[0]!r})")
    cible.write_text(texte, encoding="utf-8", newline="\n")
    return cible


# ============================================================================
# FONDATION : le spec scellé, rebasé sur les routes du site
# ============================================================================
def fondation(sceau: Sceau, ecrits: List[Path]) -> Dict[str, Any]:
    sys.path.insert(0, str(DEPOT / "FONDATION"))
    FB = __import__("fondation_base")
    sceau.chemin("FONDATION", "fondation_base.py")
    sceau.chemin("FONDATION", "generer_fondation.py")
    sceau.chemin("ABONDANCE", "moteur_page_trilingue.py")

    bruts = FB.resoudre()
    if not FB.verifier(bruts):
        raise SystemExit("contrôles non reçus dans fondation_base : la page n'est pas publiée")
    donnees = GF._titrer(dict(bruts))
    donnees["resume"] = GF.resume(bruts)
    donnees["valeurs_declarees"] = dict(bruts["declare"])

    spec = GF.spec_fondation(donnees)
    _rebaser(spec, "/fondation", [
        {"href": f"{SITE}/fondation.json",
         "libelle": _3("JSON calculé (18 équations)", "Computed JSON (18 equations)",
                       "JSON المحسوب (١٨ معادلة)")},
        {"href": f"{SITE}/chiffres-pi",
         "libelle": _3("La confrontation chiffrée : CHIFFRES",
                       "The digit confrontation: CHIFFRES", "المواجهةُ بالأرقام: الخانات")},
        {"href": DOI_CONCEPT, "libelle": _3("DOI du dépôt", "Deposit DOI", "معرف الكائن")},
        {"href": DEPOT_GITHUB, "libelle": _3("Source sur GitHub", "Source on GitHub",
                                             "المصدر على GitHub")},
    ])

    vues: set = set()
    for lang in MOTEUR.LANGUES:
        cible = WEB / ("fondation.html" if lang == "fr" else f"fondation_{lang}.html")
        ecrits.append(_page(spec, donnees, vues, lang, cible, GF.formules_traduites))
    mortes = sorted(set(GF.FORMULE_TR) - vues)
    if mortes:
        raise SystemExit("clés de formule sans formule correspondante : " + " | ".join(mortes))

    source = sceau.chemin("FONDATION", "artefacts", "donnees", "fondation.json")
    # Copie verbatim, mais dans la vue scellée : le dépôt est en CRLF sur disque (`core.autocrlf`).
    (WEB / "fondation_resultats.json").write_bytes(_vue_git(source.read_bytes()))
    ecrits.append(WEB / "fondation_resultats.json")
    return {"equations": donnees["resume"]["equations"],
            "controles": f"{donnees['resume']['controles_ok']}/{donnees['resume']['controles_total']}"}


# ============================================================================
# CHIFFRES : les textes vivent dans le dépôt scellé ; le site ne change que les chemins
# ============================================================================
def chiffres(sceau: Sceau, ecrits: List[Path]) -> Dict[str, Any]:
    """Aucune phrase n'est redite ici : `CHIFFRES/generer_pages.py` les porte déjà.

    Le dépôt est vérifié au SHA-256 contre `MANIFESTE_SHA256.txt` avant lecture, les dix-sept
    lignes françaises sont confrontées à `artefacts/etat.json`, et le site n'ajoute que la base
    des URL : ce que le visiteur lit est octet pour octet le contenu de l'archive du DOI.
    """
    for part in (("CHIFFRES", "chiffres_pi.py"), ("CHIFFRES", "generer_chiffres.py"),
                 ("CHIFFRES", "generer_pages.py"), ("ABONDANCE", "moteur_page_trilingue.py")):
        sceau.chemin(*part)
    sys.path.insert(0, str(DEPOT / "CHIFFRES"))
    GP = __import__("generer_pages")

    chemin_json = sceau.chemin("CHIFFRES", "artefacts", "donnees", "chiffres.json")
    chemin_etat = sceau.chemin("CHIFFRES", "artefacts", "etat.json")
    donnees = json.loads(chemin_json.read_text(encoding="utf-8"))
    etat = json.loads(chemin_etat.read_text(encoding="utf-8"))

    lignes = {e["id"]: e["resultat"] for e in donnees["equations"]}
    scellees = {e["id"]: e["resultat"] for e in etat["equations"]}
    derives = [f"{cle} : site {lignes.get(cle)!r} vs artefact {scellees.get(cle)!r}"
               for cle in sorted(set(lignes) | set(scellees))
               if lignes.get(cle) != scellees.get(cle)]
    if derives:
        raise SystemExit("le site ne publie pas le domaine scellé : " + " | ".join(derives[:3]))
    non_recus = [c["id"] for c in etat["controles"] if not c["ok"]]
    if non_recus:
        raise SystemExit("des contrôles du dépôt ne sont pas reçus : " + " ".join(non_recus))
    domaine = donnees["resume"]["domaine"]
    if int(domaine["n"]) != 1_000_000:
        raise SystemExit(f"le site publierait un autre domaine : {domaine['n']}")

    spec = GP.spec_chiffres(donnees)
    _rebaser(spec, "/chiffres-pi", [
        {"href": f"{SITE}/chiffres-pi.json",
         "libelle": _3("JSON calculé (17 équations, 17 contrôles)",
                       "Computed JSON (17 equations, 17 controls)",
                       "JSON المحسوب (١٧ معادلة و١٧ مراقَبة)")},
        {"href": f"{SITE}/fondation",
         "libelle": _3("La base posée : FONDATION", "The posited base: FONDATION",
                       "الأساس المقرَّر: FONDATION")},
        {"href": DOI_CONCEPT, "libelle": _3("DOI du dépôt", "Deposit DOI", "معرف الكائن")},
        {"href": DEPOT_GITHUB, "libelle": _3("Source sur GitHub", "Source on GitHub",
                                             "المصدر على GitHub")},
    ])

    vues: set = set()
    for lang in MOTEUR.LANGUES:
        cible = WEB / ("chiffres_pi.html" if lang == "fr" else f"chiffres_pi_{lang}.html")
        ecrits.append(_page(spec, donnees, vues, lang, cible, GP.formules_traduites))
    mortes = sorted(set(GP.FORMULE_TR) - vues)
    if mortes:
        raise SystemExit("clés de formule sans formule correspondante : " + " | ".join(mortes))

    (WEB / "chiffres_pi_resultats.json").write_bytes(_vue_git(chemin_json.read_bytes()))
    ecrits.append(WEB / "chiffres_pi_resultats.json")
    t = donnees["resume"]
    return {"equations": t["equations"],
            "controles": f"{t['controles_ok']}/{t['controles_total']}",
            "domaine": domaine["n"], "verdict": t["verdict_global"]}


# ============================================================================
# LABORATOIRE : le dossier HORLOGERIE du dépôt scellé, joué pas à pas
# ============================================================================
COULEUR_SIGNALÉ = "#1f5f8b"
COULEUR_HORS_TOLERANCE = "#b45309"
IDX = {lang: i for i, lang in enumerate(MOTEUR.LANGUES)}   # les trios (fr, en, ar)


def _valeur_brute(x: Any) -> str:
    """Un nombre de contrôle rendu tel que le module l'écrit, liste comprise."""
    if isinstance(x, bool):
        return "vrai" if x else "faux"
    if isinstance(x, (list, tuple)):
        return " · ".join(_valeur_brute(i) for i in x)
    if isinstance(x, float):
        return repr(x)
    return str(x)


def _fuite_hote(ecrits: List[Path], mesure: Dict[str, Any]) -> None:
    """τ dépend de la machine : aucune de ses écritures ne doit atteindre un fichier du lot.

    Le gel d'EQ-12 et de C12 est la mesure prise à la source ; ce contrôle vérifie le
    résultat, car une ligne calculée réintroduite plus tard par le dépôt passerait sinon.
    Sont seuls visés les quatre τ et leur rapport à la période : `periode_hypothetique_ns`
    n'est pas un nombre d'hôte mais la période spécifiée, que le certificat scellé porte.
    """
    signatures = {f"{mesure[k]:.1f}" for k in ("tau_mediane_ns", "tau_eam_ns", "tau_min_ns",
                                               "tau_max_ns")}
    signatures |= {repr(mesure[k]) for k in ("tau_mediane_ns", "tau_eam_ns", "tau_min_ns",
                                             "tau_max_ns", "ratio_tau_sur_periode")}
    signatures |= {f"{mesure['ratio_tau_sur_periode']:.4f}"}
    signatures = {s for s in signatures if len(s) >= 5 and any(c.isdigit() for c in s)}
    for cible in ecrits:
        texte = cible.read_text(encoding="utf-8", errors="replace")
        for sig in sorted(signatures):
            if re.search(r"(?<![\d.,a-f])" + re.escape(sig) + r"(?![\da-f])", texte):
                raise SystemExit(f"{cible.name} : une valeur de l'hôte ({sig}) est publiée "
                                 "alors qu'EQ-12 et C12 sont gelées")


def laboratoire(sceau: Sceau, ecrits: List[Path]) -> Dict[str, Any]:
    """Rien n'est calculé de neuf ici : le site met en forme le dossier HORLOGERIE.

    Le certificat et le laboratoire sont recalculés puis confrontés aux artefacts scellés —
    ce qui ne coïncide pas arrête la génération. Deux lignes sont gelées avant affichage
    parce que leur nombre dépend de la machine qui exécute : EQ-12 (τ mesuré) et C12 (ses
    cinq séries). Aucune valeur d'hôte n'atteint une page ; `_fuite_hote` le vérifie.
    """
    for part in (("HORLOGERIE", "horlogerie.py"), ("HORLOGERIE", "laboratoire.py"),
                 ("HORLOGERIE", "calibrer_horloge_almizan.py"),
                 ("HORLOGERIE", "verifier_certificats.py"),
                 ("ABONDANCE", "moteur_page_trilingue.py")):
        sceau.chemin(*part)
    PL = __import__("pages_laboratoire")

    if str(DEPOT) not in sys.path:
        sys.path.insert(0, str(DEPOT))
    LAB = __import__("HORLOGERIE.laboratoire", fromlist=["laboratoire"])
    H = LAB.HOR

    bruts = H.resoudre()
    if not H.verifier(bruts):
        raise SystemExit("contrôles du certificat d'horlogerie non reçus : la page n'est pas publiée")
    cert, mesure = bruts["certificat"], bruts["mesure"]

    chemin_cert = sceau.chemin("HORLOGERIE", "artefacts", "certificats.json")
    if H.octets_certificat(cert) != _vue_git(chemin_cert.read_bytes()):
        raise SystemExit("le certificat recalculé n'est pas l'artefact scellé : rien n'est publié")

    lab = LAB.laboratoire(pas=4096, pas_horloge=4000, bruit=1e-3, graine=20261109)
    chemin_lab = sceau.chemin("HORLOGERIE", "artefacts", "laboratoire.json")
    scelle = json.loads(_vue_git(chemin_lab.read_bytes()).decode("utf-8"))
    derives = [cle for cle in sorted(set(scelle) | set(lab))
               if cle != "mesure_hote_ecrite"
               and json.dumps(scelle.get(cle), sort_keys=True, ensure_ascii=False)
               != json.dumps(lab.get(cle), sort_keys=True, ensure_ascii=False)]
    if derives:
        raise SystemExit("le laboratoire rejoué ne rend pas l'artefact scellé : "
                         + " | ".join(derives[:3]))
    if lab["verdict"] != "LABORATOIRE CONFORME":
        raise SystemExit(f"le laboratoire ne se dit pas conforme : {lab['verdict']}")
    if lab["controles_verts"] != lab["nombre_controles"]:
        raise SystemExit(f"contrôles du laboratoire non reçus : "
                         f"{lab['controles_verts']}/{lab['nombre_controles']}")

    # ── ce que la page affiche : le domaine calculé, moins les deux lignes d'hôte ──
    eqs = []
    for e in bruts["equations"]:
        copie = dict(e)
        if copie["id"] == "EQ-12":
            copie["resultat"] = PL.EQ12_GEL["fr"]
            copie["detail"] = {"gel": PL.EQ12_GEL["fr"]}
        eqs.append(copie)
    controles = PL.gele_controles(bruts["controles"]) + [
        {"id": c["id"], "nom": c["enonce"], "attendu": _valeur_brute(c["attendu"]),
         "obtenu": _valeur_brute(c["obtenu"]), "ok": bool(c["vrai"])} for c in lab["controles"]]
    recus = sum(1 for c in controles if c["ok"])
    if recus != len(controles):
        raise SystemExit(f"{len(controles) - recus} contrôle(s) sur {len(controles)} "
                         "seraient publiés en rouge")

    astro, par = cert["astronomie"], cert["astronomie"]["par_cycle"]
    r, fermet = cert["rationnels"], lab["trajectoire"]["fermeture"]
    stab, bande = lab["stabilite_simulee"], lab["stabilite_simulee"]["bande"]
    pas, fermeture = lab["trajectoire"]["pas"], fermet["periode_commune"]
    v = {
        "dt": f"{r['dt']['numerateur']}/{r['dt']['denominateur']}",
        "fermeture": str(fermeture),
        "residu": str(lab["trajectoire"]["residu_max_absolu"]),
        "eps": repr(stab["eps_injecte"]),
        "adev": repr(stab["adev_mesure"]),
        "soleil": repr(par["Soleil"]["ecart_max_s"]),
        "lune": repr(par["Lune"]["ecart_max_s"]),
        "terre": repr(par["Terre"]["ecart_max_s"]),
        "coord": str(len(lab["repere"])),
        "controles": f"{recus}/{len(controles)}",
        "pas": str(pas),
        "fenetres": str(stab["pas"]),
        "basse": repr(bande["borne_basse"]),
        "haute": repr(bande["borne_haute"]),
        "seuil": str(astro["seuils"]["conforme_s_par_an"]),
        "face": str(par["Terre"]["paires"]),
        "verdict_soleil": par["Soleil"]["verdict"],
        "verdict_lune": par["Lune"]["verdict"],
        "verdict_terre": par["Terre"]["verdict"],
        "ctrl": str(recus), "ctrl_total": str(len(controles)),
        "eq": str(len(eqs)),
        "tours": f"{pas / fermeture:.3e}",
    }

    def fmt(trio: Dict[str, str]) -> Dict[str, str]:
        return _3(*[trio[lang].format(**v) for lang in MOTEUR.LANGUES])

    donnees = {
        "source": bruts["source"],
        "equations": eqs,
        "controles": controles,
        "resume": {"equations": len(eqs), "controles_ok": recus, "controles_total": len(controles),
                   "statuts": bruts["conclusion"]["statuts_par_label"]},
        "valeurs_declarees": {},
    }

    # ── trois figures : deux dessinées par le moteur, une recopiée du dépôt ──
    serie_ecarts = {lang: [(PL.FIG_ECARTS_SERIES[a][IDX[lang]], float(par[a]["ecart_max_s"]),
                           COULEUR_SIGNALÉ if par[a]["verdict"] == "ÉCART SIGNALÉ"
                           else COULEUR_HORS_TOLERANCE)
                           for a in ("Soleil", "Lune", "Terre")] for lang in MOTEUR.LANGUES}
    serie_stab = {lang: [(PL.FIG_STAB_SERIES["eps"][IDX[lang]], float(stab["eps_injecte"]),
                          COULEUR_SIGNALÉ),
                         (PL.FIG_STAB_SERIES["adev"][IDX[lang]], float(stab["adev_mesure"]),
                          COULEUR_HORS_TOLERANCE)] for lang in MOTEUR.LANGUES}
    figures = [
        {"svg": {lang: MOTEUR.figure_barres(PL.FIG_ECARTS_TITRE[lang], PL.FIG_ECARTS_DESC[lang],
                                           serie_ecarts[lang], None, ids=("fig1-t", "fig1-d"))
                 for lang in MOTEUR.LANGUES},
         "legende": fmt(PL.FIG_ECARTS_LEGENDE)},
        {"svg": {lang: MOTEUR.figure_barres(PL.FIG_STAB_TITRE[lang], PL.FIG_STAB_DESC[lang],
                                            serie_stab[lang], float(bande["borne_haute"]),
                                            ids=("fig2-t", "fig2-d"))
                 for lang in MOTEUR.LANGUES},
         "legende": fmt(PL.FIG_STAB_LEGENDE)},
        {"svg": {lang: (f"<img src='{SITE}/laboratoire-trajectoire.svg' width='1160' height='390' "
                        f"loading='lazy' decoding='async' "
                        f"style='max-width:100%;height:auto' "
                        f"alt=\"{MOTEUR.ech(fmt(PL.IMG_TRAJECTOIRE_ALT)[lang])}\">")
                 for lang in MOTEUR.LANGUES},
         "legende": fmt(PL.IMG_LEGENDE)},
    ]

    spec = {
        "module": "HORLOGERIE/horlogerie.py + HORLOGERIE/laboratoire.py",
        "slug": "laboratoire", "theme": PL.THEME, "titre_bande": PL.TITRE_BANDE,
        "description": fmt(PL.DESCRIPTION), "eq_text": PL.table_eq_text(),
        "cheminement": PL.CHEMINEMENT, "figures": figures,
        "resultats": PL.cartes(v),
        "materiaux": PL.materiaux(lab["repere"]),
        "caption_materiaux": PL.CAPTION_MATIERAUX,
        "sources": _3(*[f"{PL.SOURCES[lang]} {PL.NOTE_HOTE[lang]}" for lang in MOTEUR.LANGUES]),
        "fil_conducteur": PL.FIL_CONDUCTEUR, "commandes": PL.COMMANDES, "doi": DOI_CONCEPT,
    }
    _rebaser(spec, "/laboratoire", [
        {"href": f"{SITE}/laboratoire.json",
         "libelle": _3(f"JSON du laboratoire ({len(eqs)} équations, {len(controles)} contrôles)",
                       f"Laboratory JSON ({len(eqs)} equations, {len(controles)} checks)",
                       f"JSON المختبر ({len(eqs)} معادلة و{len(controles)} تحقُّقًا)")},
        {"href": f"{SITE}/laboratoire-certificats.json",
         "libelle": _3("Certificat d'horlogerie scellé", "Sealed horology certificate",
                       "شهادةُ التوقيت المختومة")},
        {"href": f"{SITE}/fondation",
         "libelle": _3("La base posée : FONDATION", "The posited base: FONDATION",
                       "الأساس المقرَّر: FONDATION")},
        {"href": f"{SITE}/chiffres-pi",
         "libelle": _3("La confrontation chiffrée : CHIFFRES",
                       "The digit confrontation: CHIFFRES", "المواجهةُ بالأرقام: الخانات")},
        {"href": DOI_CONCEPT, "libelle": _3("DOI du dépôt", "Deposit DOI", "معرف الكائن")},
        {"href": DEPOT_GITHUB, "libelle": _3("Source sur GitHub", "Source on GitHub",
                                             "المصدر على GitHub")},
    ])

    vues: set = set()
    avant = len(ecrits)
    for lang in MOTEUR.LANGUES:
        cible = WEB / ("laboratoire.html" if lang == "fr" else f"laboratoire_{lang}.html")
        ecrits.append(_page(spec, donnees, vues, lang, cible, PL.formules_traduites))
    mortes = sorted(set(PL.FORMULE_TR) - vues)
    if mortes:
        raise SystemExit("clés de formule sans formule correspondante : " + " | ".join(mortes))

    # ── les données : les fichiers scellés eux-mêmes, recopiés ──
    copies = [("HORLOGERIE", "artefacts", "laboratoire.json"),
              ("HORLOGERIE", "artefacts", "certificats.json"),
              ("HORLOGERIE", "artefacts", "trajectoire_laboratoire.svg"),
              ("HORLOGERIE", "artefacts", "trajectoire_laboratoire.csv"),
              ("HORLOGERIE", "artefacts", "stabilite_laboratoire.csv"),
              ("HORLOGERIE", "artefacts", "confrontation_astronomique.csv")]
    destinations = ["laboratoire_resultats.json", "laboratoire_certificats.json",
                    "laboratoire_trajectoire.svg", "laboratoire_trajectoire.csv",
                    "laboratoire_stabilite.csv", "laboratoire_confrontation.csv"]
    for part, nom in zip(copies, destinations):
        source = sceau.chemin(*part)
        brut = _vue_git(source.read_bytes()) if Path(nom).suffix == ".json" else source.read_bytes()
        (WEB / nom).write_bytes(brut)
        ecrits.append(WEB / nom)

    _fuite_hote(ecrits[avant:], mesure)
    return {"equations": len(eqs), "controles": f"{recus}/{len(controles)}",
            "coordonnees": len(lab["repere"]), "verdict": lab["verdict"],
            "racine_merkle": cert["racine_merkle_sha256"][:16] + "…"}


# ============================================================================
# contrôles de forme avant d'écrire le lot
# ============================================================================
def verifier(ecrits: List[Path]) -> None:
    for cible in ecrits:
        brut = cible.read_bytes()
        if cible.suffix in (".html", ".json", ".md") and b"\r" in brut:
            raise SystemExit(f"{cible.name} : des CR se sont glissés dans le fichier")
        if cible.suffix != ".html":
            continue
        texte = brut.decode("utf-8")
        for motif in ('href="../', 'href="fondation', 'href="index.html', 'href="chiffres_pi'):
            if motif in texte:
                raise SystemExit(f"{cible.name} : lien relatif encore présent — {motif}")
        if 'rel="canonical"' not in texte:
            raise SystemExit(f"{cible.name} : pas de canonical")
        if texte.count('rel="alternate"') != 4:
            raise SystemExit(f"{cible.name} : {texte.count('rel=\"alternate\"')} alternates, "
                             " attendu 4 (trois langues + x-default)")
    selection = [p for p in ecrits if p.suffix == ".html"]
    for page in selection:
        if page.name.endswith("_ar.html") and 'dir="rtl"' not in page.read_text(encoding="utf-8"):
            raise SystemExit(f"{page.name} : la page arabe n'est pas en RTL")


def main() -> int:
    for dossier in (WEB,):
        if not dossier.is_dir():
            raise SystemExit(f"destinataire absent : {dossier}")
    sceau = Sceau()
    ecrits: List[Path] = []
    recu = {"fondation": fondation(sceau, ecrits), "chiffres": chiffres(sceau, ecrits),
            "laboratoire": laboratoire(sceau, ecrits)}
    verifier(ecrits)
    sortie = {
        "archive_publiee": ARCHIVE_PUBLIEE,
        "controle_par_dossier": recu,
        "fichiers_du_depot_verifies": len(sceau.utilises),
        "ecrits": [{"chemin": str(p.relative_to(RACINE)).replace("\\", "/"),
                    "octets": p.stat().st_size,
                    "sha256": _sha(p)} for p in ecrits],
    }
    print(json.dumps(sortie, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
