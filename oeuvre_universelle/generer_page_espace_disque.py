# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""Génère les pages trilingues (FR/EN/AR) du problème d'espace disque.

Honnêteté : le sujet est un problème d'exploitation d'un poste de développement,
mesuré puis résolu par équations numérotées et contrôles indépendants. Aucun
chiffre n'est présenté comme une mesure certifiée du parc complet ; la source
est l'instantané scellé du collecteur, dont l'empreinte SHA-256 est affichée.

Usage :
    py -3 oeuvre_universelle/generer_page_espace_disque.py
"""

from __future__ import annotations

import html
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from oeuvre_universelle.espace_disque import resoudre, verifier
else:
    from .espace_disque import resoudre, verifier

RACINE = Path(__file__).resolve().parent.parent
WEB_CLOUD = RACINE / "web_cloud"
RESULTATS = RACINE / "resultats" / "oeuvre_universelle"

LANGUES = ("fr", "en", "ar")
CHEMINS = {
    "fr": "/espace-disque",
    "en": "/espace-disque/en",
    "ar": "/espace-disque/ar",
}
PAGES = {
    "fr": WEB_CLOUD / "espace_disque.html",
    "en": WEB_CLOUD / "espace_disque_en.html",
    "ar": WEB_CLOUD / "espace_disque_ar.html",
}
DONNEES_JSON = WEB_CLOUD / "espace_disque_resultats.json"
ARCHIVE_JSON = RESULTATS / "espace_disque_page.json"

AUTEUR = "M. Ahmed EL BAHLOUL (IMAM8MAHDI)"
SITE = "https://www.al-mizan.world"
DATE_JOUR = date.today().isoformat()

GO = 1024**3


def _ech(v: Any) -> str:
    return html.escape(str(v), quote=True)


_CLE = re.compile(r"\{([a-z][a-z0-9_]*)\}")


def _fmt(texte: Any, val: Dict[str, str]) -> str:
    """Remplace les marqueurs {cle} connus ; les accolades accidentelles restent littérales."""
    return _CLE.sub(lambda m: val.get(m.group(1), m.group(0)), str(texte))


def _cles_inconnues(*textes: Any) -> set:
    trouves = set()
    pile = list(textes)
    while pile:
        x = pile.pop()
        if isinstance(x, str):
            trouves |= {m.group(1) for m in _CLE.finditer(x)}
        elif isinstance(x, dict):
            pile.extend(x.values())
        elif isinstance(x, (list, tuple)):
            pile.extend(x)
    return trouves


def _controler_cles(val: Dict[str, str]) -> None:
    """Un gabarit du générateur qui appelle une clé absente écrirait un trou dans la page."""
    inconnues = set()
    for langue in T.values():
        inconnues |= _cles_inconnues(langue)
    for par_langue in EQ_TEXT.values():
        inconnues |= _cles_inconnues(par_langue)
    manquant = sorted(inconnues - set(val))
    if manquant:
        raise RuntimeError(f"Gabarits référenceurs des clés absentes de _valeurs : {manquant}")


def _go(octets: Any) -> str:
    return f"{float(octets) / GO:.3f}"


# Un horizon en jours se lit avec son unité ; l'infini, lui, doit être dit, pas affiché.
_HORIZON = {
    "fr": ("jours", "non borné — aucune copie sur la fenêtre de 24 h"),
    "en": ("days", "unbounded — no copy inside the 24 h window"),
    "ar": ("يومًا", "غير محدود — لا نسخة ضمن نافذة 24 ساعة"),
}


def _horizon(v: Any, lang: str) -> str:
    unite, quand_infini = _HORIZON[lang]
    if isinstance(v, float) and (v != v or abs(v) == float("inf")):
        return quand_infini
    return f"{v:.2f} {unite}"


def _json_sur(obj: Any) -> Any:
    """json.dumps écrit « Infinity », que JSON.parse du navigateur refuse (RFC 8259).

    Une projection non bornée se publie donc en null, avec la note qui le dit : le
    module, lui, continue de renvoyer le float infini que ses tests attendent.
    """
    if isinstance(obj, float) and (obj != obj or abs(obj) == float("inf")):
        return None
    if isinstance(obj, dict):
        return {k: _json_sur(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_sur(v) for v in obj]
    return obj


def _carte(donnees: Dict[str, Any], eq_id: str) -> Dict[str, Any]:
    for eq in donnees["equations"]:
        if eq["id"] == eq_id:
            return eq["detail"]
    raise KeyError(eq_id)


def _valeurs(donnees: Dict[str, Any], lang: str = "fr") -> Dict[str, str]:
    r = donnees["resume"]
    mes = donnees["mesures"]
    inst = mes["volumes"]["instantane"]
    vol = donnees["source"]
    classes = json.loads(Path(vol["instantane"]).read_text(encoding="utf-8"))["depot"]["octets_par_classe"]
    retention = mes["retention"]
    return {
        "ok": str(r["controles_ok"]),
        "total": str(r["controles_total"]),
        "eq": str(r["equations"]),
        "date": DATE_JOUR,
        "auteur": _ech(AUTEUR),
        "libre": f"{r['libre_go']:.3f}",
        "occupation": f"{100 * r['occupation']:.1f}",
        "recuperable": f"{r['recuperable_go']:.3f}",
        "deficit": f"{r['deficit_go']:.3f}",
        "horizon": _horizon(r["jours_avant_saturation"], lang),
        "copies": f"{r['copies_historiques']:,}".replace(",", "\u202f"),
        "archives_go": _go(mes["copies"].get("archives_octets", classes.get("_archives", 0))),
        "seuil": f"{_go(donnees['invariants']['rho_marge'] * inst['total_octets'])}",
        "capacite": f"{_go(inst['total_octets'])}",
        "empreinte": donnees["source"].get("empreinte", ""),
        "collecteur": "outils/collecter_instantane_espace_disque.py",
        "regle": retention["regle"],
        "gardees": str(retention["gardees_n"]),
    }


# ============================================================================
# FIGURE SVG — partition du dépôt et solde avant/après, recalculée depuis les données
# ============================================================================

def _figure(donnees: Dict[str, Any], lang: str) -> str:
    inst = json.loads(Path(donnees["source"]["instantane"]).read_text(encoding="utf-8"))
    classes = inst["depot"]["octets_par_classe"]
    depot = inst["depot"]["octets_total"]
    vol = inst["volumes"]["C:"]
    r = donnees["resume"]
    f = FIG[lang]
    lbl = CLASSES_LBL[lang]

    couleurs = {
        "copie_de_soie": "#b45309",
        "autre": "#1f5f8b",
        "temporaire_qoder": "#7c3aed",
        "journal": "#0e7490",
        "cache_python": "#4b5563",
        "archive": "#94a3b8",
        "git": "#166534",
    }
    ordre = sorted(classes, key=lambda k: -classes[k])
    x0, y0, w, h = 60, 46, 880, 42
    largeur = lambda o: max(1.0, w * float(o) / depot)  # noqa: E731
    parts, x = [], x0
    for nom in ordre:
        lw = largeur(classes[nom])
        col = couleurs.get(nom, "#94a3b8")
        parts.append(
            f"<rect x='{x:.2f}' y='{y0}' width='{lw:.2f}' height='{h}' fill='{col}'>"
            f"<title>{_ech(lbl.get(nom, nom))} · {_go(classes[nom])} Go · "
            f"{100 * classes[nom] / depot:.2f} {f['part']}</title></rect>"
        )
        if lw > 52:
            parts.append(
                f"<text x='{x + lw / 2:.1f}' y='{y0 + h + 18}' text-anchor='middle' "
                f"class='lbl'>{_ech(lbl.get(nom, nom))}</text>"
            )
            parts.append(
                f"<text x='{x + lw / 2:.1f}' y='{y0 + h + 34}' text-anchor='middle' "
                f"class='num'>{_go(classes[nom])} Go</text>"
            )
        x += lw

    total_v = float(vol["total_octets"])
    libre_avant = float(vol["libre_octets"])
    r_go = r["recuperable_go"] * GO
    seuil = 0.10 * total_v
    libre_apres = libre_avant + r_go

    # deux barres : solde libre mesuré, puis projection L' = L + R
    def _barre(y: int, couleur: str, fraction: float, libelle: str) -> str:
        bw = max(1.0, w * fraction)
        texte = f"{libelle} ({100 * fraction:.1f} %)"
        if bw > 0.72 * w:      # barre presque pleine : libelle a l'interieur, en blanc
            return (
                f"<rect x='{x0}' y='{y}' width='{w}' height='22' fill='#e2e8ef'/>"
                f"<rect x='{x0}' y='{y}' width='{bw:.2f}' height='22' fill='{couleur}'/>"
                f"<text x='{x0 + 6}' y='{y + 16}' class='sur'>{_ech(texte)}</text>"
            )
        return (
            f"<rect x='{x0}' y='{y}' width='{w}' height='22' fill='#e2e8ef'/>"
            f"<rect x='{x0}' y='{y}' width='{bw:.2f}' height='22' fill='{couleur}'/>"
            f"<text x='{x0 + bw + 8:.2f}' y='{y + 16}' class='lbl'>{_ech(texte)}</text>"
        )

    solde = [
        f"<text x='20' y='176' class='tit'>{_ech(f['solde'])}</text>",
        _barre(190, "#0e7490", libre_avant / total_v,
               f"{f['avant']} : {_go(libre_avant)} Go"),
        _barre(224, "#166534", libre_apres / total_v,
               f"{f['apres']} : {_go(libre_apres)} Go"),
        f"<line x1='{x0 + w * seuil / total_v:.2f}' y1='184' x2='{x0 + w * seuil / total_v:.2f}' y2='252' "
        f"stroke='#b45309' stroke-width='2' stroke-dasharray='5 4'/>",
        f"<text x='{x0 + w * seuil / total_v + 6:.2f}' y='270' class='lbl'>{_ech(f['seuil'])} "
        f"({_go(seuil)} Go)</text>",
    ]

    legende = "".join(
        f"<rect x='{20 + i * 210}' y='292' width='13' height='13' fill='{couleurs.get(n, '#94a3b8')}'/>"
        f"<text x='{40 + i * 210}' y='303' class='lbl'>{_ech(lbl.get(n, n))}</text>"
        for i, n in enumerate(ordre[:6])
    )

    return f"""<svg role="img" aria-labelledby="titredisque" viewBox="0 0 1000 330" xmlns="http://www.w3.org/2000/svg">
<title id="titredisque">{_ech(f['titre'])}</title>
<style>
.lbl{{font:12px 'Segoe UI',Arial,sans-serif;fill:#33475a}}
.num{{font:600 12px 'Segoe UI',Arial,sans-serif;fill:#10263a}}
.tit{{font:600 13px 'Segoe UI',Arial,sans-serif;fill:#10263a}}
.sur{{font:600 12px 'Segoe UI',Arial,sans-serif;fill:#ffffff}}
</style>
<text x="20" y="34" class="tit">{_ech(f['depot'])} · {_go(depot)} Go / {_go(total_v)} Go · {inst["depot"]["fichiers"]:,} {_ech(f['fichiers'])}</text>
{''.join(parts)}
{''.join(solde)}
<text x="20" y="140" class="num">{_ech(f['cloture'].format(s=_go(sum(classes.values()))))}</text>
{''.join(legende)}
</svg>"""


# ============================================================================
# TEXTES
# ============================================================================

T: Dict[str, Dict[str, Any]] = {
    "fr": {
        "lang": "fr", "dir": "ltr", "locale": "fr_FR",
        "titre": "Espace disque : treize équations et leurs contrôles | AL-MIZAN",
        "description": "Le problème d'espace disque d'un poste de développement, posé en treize équations numérotées, "
                       "contrôlé par des routes de mesure indépendantes, et la libération qui en découle.",
        "og_titre": "Espace disque : treize équations et leurs contrôles",
        "nav": ["Accueil", "Œuvre universelle", "Observateur triniter", "Portefeuille", "Développeurs"],
        "pied": "AL-MIZAN.WORLD — œuvre de {auteur}. Calculs reproductibles sur le poste de développement, "
                "aucune mesure certifiée du parc.",
        "h1": "Problème d'espace disque, posé en équations",
        "lead": "Un volume {capacite} Go saturé à {occupation} % par des copies que le système produisait "
                "lui-même. Treize équations, treize contrôles indépendants, une libération chiffrée.",
        "badge_calc": "Calculs reproductibles",
        "badge_ctrl": "Contrôles {ok}/{total}",
        "badge_hon": "Aucune preuve revendiquée",
        "warn_titre": "Cadre.",
        "warn_corps": "Il s'agit d'un problème d'exploitation d'un poste de développement, pas d'une découverte. "
                      "Chaque chiffre vient d'un instantané scellé (empreinte SHA-256) et d'une route de mesure "
                      "indépendante ; les projections supposent cadence et taille constantes.",
        "s_source": "Source et témoin",
        "p_source": "Instantané du {date} produit par {collecteur}, empreinte SHA-256 "
                    "<code>{empreinte}</code>. {copies} copies historiques étaient dénombrées au moment de la pose.",
        "s_table": "Les treize équations",
        "p_table": "Chaque équation porte son chemin <code>module → fonction → contrôle</code> et un statut : "
                   "opérationnel (identité ou relevé reproductible), simulé (projection sous convention), "
                   "spécifié (choix de doctrine).",
        "th_id": "ID", "th_equation": "Objet", "th_formule": "Formule",
        "th_resultat": "Résultat", "th_statut": "Statut",
        "s_detail": "Lecture équation par équation",
        "s_controles": "Contrôles numériques",
        "p_controles": "Un contrôle ne recopie pas la valeur affichée : il la retrouve par une autre route "
                       "(seconde API de volume, second dénombrement, re-stat live, ordre d'association, "
                       "clôture de partition, deux prédicats d'appartenance).",
        "th_controle": "Contrôle", "th_attendu": "Attendu", "th_obtenu": "Obtenu", "th_etat": "État",
        "ok_label": "conforme", "ko_label": "échec",
        "s_figure": "Figure",
        "fig_legende": "Partition des classes du dépôt, puis solde libre mesuré et projection L' = L + R "
                       "(EQ-11), la règle de rétention restant à appliquer. "
                       "Largeurs recalculées depuis l'instantané, aucune donnée saisie à la main.",
        "s_mizan": "Ce que le calcul change",
        "p_mizan": "Sous la règle « {regle} », {recuperable} Go sont récupérables et {gardees} copies restent "
                   "disponibles pour restaurer. Le déficit de {deficit} Go vis-à-vis du seuil ρ = 0,10 devient "
                   "un solde de {libre} Go libres, puis un gain net après compression des archives. "
                   "Horizon projeté vers la saturation : {horizon}, coupé par un plafond durable "
                   "posé dans le module de sauvegarde lui-même.",
        "s_repro": "Reproductibilité",
        "p_repro": "Le module imprime le JSON complet et sort en 1 si un contrôle échoue ; le générateur refuse "
                    "d'écrire les pages tant que les contrôles ne sont pas tous conformes.",
        "s_limites": "Limites",
        "actions_json": "Résultats (JSON)", "actions_oeuvre": "Œuvre universelle",
        "note_langue": "Formules, tableaux et blocs de code restent en LTR, y compris sur la page arabe.",
        "statuts": {"OPÉRATIONNEL": "opérationnel", "SIMULÉ": "simulé", "SPÉCIFIÉ": "spécifié"},
        "objets": {
            "EQ-01": "Occupation du volume", "EQ-02": "Témoin scellé",
            "EQ-03": "Clôture de la partition", "EQ-04": "Poids de la copie de soi",
            "EQ-05": "Dénombrement des copies", "EQ-06": "Facteur de duplication",
            "EQ-07": "Masse du journal", "EQ-08": "Projection de saturation",
            "EQ-09": "Espace récupérable", "EQ-10": "Marge de sécurité",
            "EQ-11": "Solde après libération", "EQ-12": "Rendement de la libération",
            "EQ-13": "Secteurs scellés",
        },
    },
    "en": {
        "lang": "en", "dir": "ltr", "locale": "en_GB",
        "titre": "Disk space: thirteen equations and their checks | AL-MIZAN",
        "description": "A development workstation's disk-space problem, stated as thirteen numbered equations, "
                       "checked through independent measurement routes, and the reclaim that follows.",
        "og_titre": "Disk space: thirteen equations and their checks",
        "nav": ["Home", "Universal work", "Trinary observer", "Portfolio", "Developers"],
        "pied": "AL-MIZAN.WORLD — work by {auteur}. Reproducible computations on one development workstation, "
                "no certified fleet measurement.",
        "h1": "The disk-space problem, stated in equations",
        "lead": "A {capacite} GiB volume {occupation} % full, filled by copies the system was making of itself. "
                "Thirteen equations, thirteen independent checks, one quantified reclaim.",
        "badge_calc": "Reproducible computations",
        "badge_ctrl": "Checks {ok}/{total}",
        "badge_hon": "No proof claimed",
        "warn_titre": "Scope.",
        "warn_corps": "This is the operation of one development workstation, not a discovery. Every figure comes "
                      "from a sealed snapshot (SHA-256 fingerprint) and an independent measurement route; "
                      "projections assume a constant rate and constant copy size.",
        "s_source": "Source and witness",
        "p_source": "Snapshot of {date} produced by {collecteur}, SHA-256 fingerprint "
                    "<code>{empreinte}</code>. {copies} historical copies were counted when the equations were posed.",
        "s_table": "The thirteen equations",
        "p_table": "Each equation carries its <code>module → function → check</code> path and a status: "
                   "operational (reproducible identity or reading), simulated (projection under a stated "
                   "convention), specified (a doctrine choice).",
        "th_id": "ID", "th_equation": "Object", "th_formule": "Formula",
        "th_resultat": "Result", "th_statut": "Status",
        "s_detail": "Equation by equation",
        "s_controles": "Numeric checks",
        "p_controles": "A check never copies the displayed value: it recovers it by another route "
                       "(second volume API, second enumeration, live re-stat, association order, "
                       "partition closure, two membership predicates).",
        "th_controle": "Check", "th_attendu": "Expected", "th_obtenu": "Obtained", "th_etat": "State",
        "ok_label": "match", "ko_label": "failure",
        "s_figure": "Figure",
        "fig_legende": "Classes of the repository, then the measured free balance and the projection L' = L + R "
                       "(EQ-11), the retention rule still being pending application. "
                       "Widths recomputed from the snapshot; nothing typed by hand.",
        "s_mizan": "What the computation changes",
        "p_mizan": "Under the rule “{regle}”, {recuperable} GiB are reclaimable and {gardees} copies stay "
                   "available for restoration. The {deficit} GiB shortfall against the ρ = 0.10 threshold "
                   "becomes {libre} GiB free, then a net gain after archive compression. Projected runway "
                   "to saturation: {horizon}, cut by a durable ceiling placed inside the "
                   "back-up module itself.",
        "s_repro": "Reproducibility",
        "p_repro": "The module prints the full JSON and exits 1 if any check fails; the generator refuses to "
                   "write the pages while any check is red.",
        "s_limites": "Limits",
        "actions_json": "Results (JSON)", "actions_oeuvre": "Universal work",
        "note_langue": "Formulas, tables and code blocks stay LTR, including on the Arabic page.",
        "statuts": {"OPÉRATIONNEL": "operational", "SIMULÉ": "simulated", "SPÉCIFIÉ": "specified"},
        "objets": {
            "EQ-01": "Volume occupancy", "EQ-02": "Sealed witness",
            "EQ-03": "Partition closure", "EQ-04": "Weight of the self-copy",
            "EQ-05": "Counting the copies", "EQ-06": "Duplication factor",
            "EQ-07": "Journal mass", "EQ-08": "Saturation projection",
            "EQ-09": "Reclaimable space", "EQ-10": "Safety margin",
            "EQ-11": "Balance after reclaim", "EQ-12": "Reclaim yield",
            "EQ-13": "Sealed sectors",
        },
    },
    "ar": {
        "lang": "ar", "dir": "rtl", "locale": "ar_SA",
        "titre": "مساحة القرص: ثلاث عشرة معادلة وضوابطها | AL-MIZAN",
        "description": "مسألة مساحة القرص في جهاز تطوير، موضوعة في ثلاث عشرة معادلة مرقّمة، "
                       "بضوابط عبر مسارات قياس مستقلة، والتحرير الناتج عنها.",
        "og_titre": "مساحة القرص: ثلاث عشرة معادلة وضوابطها",
        "nav": ["الرئيسية", "الأعمال الكونية", "المراقب الثلاثي", "المحفظة", "المطورون"],
        "pied": "AL-MIZAN.WORLD — أعمال {auteur}. حسابات قابلة لإعادة الإنتاج على جهاز تطوير واحد، "
                "وليست قياسًا معتمدًا لأسطول أجهزة.",
        "h1": "مسألة مساحة القرص، موضوعة بالمعادلات",
        "lead": "وحدة سعتها {capacite} جيبي ممتلئة بنسبة {occupation} %، ملأتها نسخٌ كان النظام "
                "يُنشئها عن نفسه. ثلاث عشرة معادلة، وثلاثة عشر ضبطًا مستقلًا، وتحرير مُقنَّن للمساحة.",
        "badge_calc": "حسابات قابلة لإعادة الإنتاج",
        "badge_ctrl": "الضوابط {ok}/{total}",
        "badge_hon": "لا ادّعاءَ proof",
        "warn_titre": "الإطار.",
        "warn_corps": "الأمر يتصل بتشغيل جهاز تطوير واحد لا باكتشاف. كل رقم يأتي من لقطة موقّعة "
                      "(بصمة SHA-256) ومن مسار قياس مستقل؛ أما الإسقاطات نفترض ثبات المعدل وحجم النسخ.",
        "s_source": "المصدر والشاهد",
        "p_source": "لقطة {date} أنتجها {collecteur}، البصمة <code>{empreinte}</code>. "
                    "كان {copies} نسخة تاريخية معدودة عند وضع المعادلات.",
        "s_table": "المعادلات الثلاث عشرة",
        "p_table": "كل معادلة تحمل مسارها <code>module → function → check</code> وحالتها: "
                   " تشغيلي (مطابقة أو قراءة قابلة لإعادة الإنتاج)، محاكى (إسقاط وفق اصطلاح مصرّح)، "
                   "أو مُحدَّد (خيار في المذهب).",
        "th_id": "المعرّف", "th_equation": "الموضوع", "th_formule": "الصيغة",
        "th_resultat": "الناتج", "th_statut": "الحالة",
        "s_detail": "قراءة معادلة بمعادلة",
        "s_controles": "الضوابط الرقمية",
        "p_controles": "لا ينسخ الضبطُ القيمةَ المعروضة، بل يستعيدها من مسار آخر: "
                       "ثانية واجهات قياس الحجم، وجرد ثانٍ، وإعادة قياس حيّة، وترتيب الجمع، "
                       "وانغلاق التجزئة، ومحرّكا عضوية.",
        "th_controle": "الضبط", "th_attendu": "المتوقع", "th_obtenu": "المحصل", "th_etat": "الحالة",
        "ok_label": "مطابق", "ko_label": "فاشل",
        "s_figure": "الشكل",
        "fig_legende": "تصنيفات المستودع والرصيد الحر قبل/بعد تطبيق قاعدة الاحتفاظ. "
                       "الأعراض محسوبة من اللقطة، ولا إدخال يدوي.",
        "s_mizan": "ما يغيّره الحساب",
        "p_mizan": "وفق القاعدة «{regle}»، يحرَّر {recuperable} جيبي وتبقى {gardees} نسخ للاستعادة. "
                   "عجزُ {deficit} جيبي إزاء عتبة ρ = 0.10 يصبح {libre} جيبي متاحة، ثم ربحًا صافيًا "
                   "بعد ضغط الأرشيف. أفقُ الامتلاء المتوقع: {horizon}، يقطعُه سقفٌ دائم وُضع داخل "
                   "وحدة النسخ نفسها.",
        "s_repro": "القابلية لإعادة الإنتاج",
        "p_repro": "تطبع الوحدة JSON كاملًا وتخرج بـ 1 إذا فشل أي ضبط، ويأبى المولّد كتابة الصفحات "
                   "ما دام أي ضبط غير مطابق.",
        "s_limites": "الحدود",
        "actions_json": "النتائج (JSON)", "actions_oeuvre": "الأعمال الكونية",
        "note_langue": "تبقى الصيغ والجداول والأكواد LTR حتى في الصفحة العربية.",
        "statuts": {"OPÉRATIONNEL": "تشغيلي", "SIMULÉ": "محاكى", "SPÉCIFIÉ": "محدَّد"},
        "objets": {
            "EQ-01": "إشغال الوحدة", "EQ-02": "الشاهد الموقّع",
            "EQ-03": "انغلاق التجزئة", "EQ-04": "وزن نسخة الذات",
            "EQ-05": "عدّ النسخ", "EQ-06": "معامل التكرار",
            "EQ-07": "كتلة السجل", "EQ-08": "إسقاط الامتلاء",
            "EQ-09": "المساحة القابلة للتحرير", "EQ-10": "هامش الأمان",
            "EQ-11": "الرصيد بعد التحرير", "EQ-12": "عائد التحرير",
            "EQ-13": "القطاعات الموقّعة",
        },
    },
}

EQ_TEXT: Dict[str, Dict[str, tuple]] = {
    "EQ-01": {
        "fr": ("Le volume et son occupation",
               "Relever total, utilisé et libre du volume C: par shutil.disk_usage, puis les comparer à une "
               "seconde API (Win32_LogicalDisk via PowerShell).",
               "Deux interfaces du même système de fichiers rendent les mêmes octets à l'octet près : "
               "l'occupation {occupation} % n'est pas un artefact d'une seule fonction."),
        "en": ("The volume and its occupancy",
               "Read total, used and free bytes of drive C: with shutil.disk_usage, then compare with a "
               "second API (Win32_LogicalDisk through PowerShell).",
               "Two interfaces of the same file system return the same bytes exactly: the {occupation} % "
               "occupancy is not an artefact of one function."),
        "ar": ("الوحدة ونسبة إشغالها",
               "قراءة المساحة الكلية والمستخدمة والمتاحة من shutil.disk_usage ثم مقارنتها بواجهة ثانية "
               "(Win32_LogicalDisk عبر PowerShell).",
               "واجهتان لنظام الملفات نفسه تعطيان نفس عدد البايتات؛ إذن نسبة {occupation} % ليست أثرًا "
               "لدالة واحدة."),
    },
    "EQ-02": {
        "fr": ("Un témoin scellé, pas une moyenne flottante",
               "Rejouer le scellement du collecteur : SHA-256 du JSON canonique sans sa propre clé.",
               "L'empreinte est recalculée à partir des octets de l'instantané et retombe sur la valeur "
               "publiée : tous les chiffres de la page sont rattachés à un témoin daté."),
        "en": ("A sealed witness, not a floating average",
               "Replay the collector's sealing: SHA-256 of the canonical JSON without its own key.",
               "The fingerprint is recomputed from the snapshot's bytes and lands on the published value: "
               "every figure on the page is tied to a dated witness."),
        "ar": ("شاهدٌ موقّع لا متوسطٌ طافٍ",
               "إعادة إنتاج ختم الجامع: SHA-256 لـ JSON القانوني دون مفتاحه نفسه.",
               "تُحسب البصمة من بايتات اللقطة وتطابق القيمة المنشورة، فكل رقم في الصفحة مرتبط بشاهد مؤرَّخ."),
    },
    "EQ-03": {
        "fr": ("La partition se ferme",
               "Sommer les classes d'octets et les niveaux 1 du dépôt, puis comparer à l'annonce du parcours.",
               "Deux découpages indépendants du même arbre rendent la somme exacte : la classe qui accuse "
               "est bien la classe qui pèse."),
        "en": ("The partition closes",
               "Sum the byte classes and the first-level buckets of the repository, then compare with the "
               "walk's own tally.",
               "Two independent cuts of the same tree return the exact sum: the class that reports the blame "
               "is the class that weighs."),
        "ar": ("التجزئة تُغلق",
               "جمع فئات البايتات والمستوى الأول من المستودع ثم مقارنتهما بمجموع الجولة نفسه.",
               "تقسيمان مستقلان لنفس الشجرة يعطيان المجموع التام: الفئة التي تُشار إليها هي الفئة الأثقل."),
    },
    "EQ-04": {
        "fr": ("Le poids de la copie de soi",
               "Fractionner le dépôt par classes, normaliser par le total du dépôt, et retrouver la classe "
               "dominante par le second découpage.",
               "La copie de soi représente la majeure partie du dépôt : le problème n'est pas le contenu "
               "de l'auteur, c'est l'oubli d'une règle de rétention."),
        "en": ("The weight of the self-copy",
               "Split the repository by classes, normalise by the repository total, and recover the dominant "
               "class through the second cut.",
               "The self-copy accounts for most of the repository: the problem is not the author's content, "
               "it is a missing retention rule."),
        "ar": ("وزن نسخة الذات",
               "تجزئة المستودع إلى فئات وتطبيعه على مجموعه ثم استخراج الفئة الغالبة بالتجزئة الثانية.",
               "نسخة الذات تستأثر بأكبر جزء من المستودع: المشكلة ليست في محتوى المؤلف بل في غياب قاعدة احتفاظ."),
    },
    "EQ-05": {
        "fr": ("Compter les copies une par une",
               "Énumérer les dossiers d'historique, retenir ceux dont le nom est un instant UTC, et fermer le "
               "répertoire par une seconde API d'énumération.",
               "Le compte n'est pas déduit d'un âge ou d'une taille : chaque copie est un nom, chaque nom est "
               "un instant, et les entrées hors format sont comptées à part (archives)."),
        "en": ("Counting the copies one by one",
               "Enumerate the history folders, keep those whose name is a UTC instant, and close the directory "
               "with a second enumeration API.",
               "The count is not inferred from age or size: each copy is a name, each name an instant, and "
               "non-conforming entries (archives) are counted separately."),
        "ar": ("عَدّ النسخ نسخةً نسخة",
               "سرد مجلدات التاريخ والاحتفاظ بأسماء هي لحظات UTC، ثم إغلاق الدليل بواجهة سرد ثانية.",
               "العدد ليس مستنتجًا من عمر أو حجم: كل نسخة اسم، وكل اسم لحظة، والداخل الخارج عن الصيغة "
               "(الأرشيف) يُعدّ على حدة."),
    },
    "EQ-06": {
        "fr": ("Le facteur de duplication",
               "Un seul parcours groupé : taille de chaque copie, moyenne, puis N × s̄ confronté à la somme directe.",
               "Les copies sont des duplicata quasi complets de la même copie courante : c'est ce qui rend "
               "l'archivage si rentable."),
        "en": ("The duplication factor",
               "One grouped walk: size of each copy, the mean, then N × s̄ confronted with the direct sum.",
               "The copies are near-complete duplicates of the same current copy: that is what makes archiving "
               "so profitable."),
        "ar": ("معامل التكرار",
               "جولة مجمعة واحدة: حجم كل نسخة ومتوسطها، ثم N × s̄ مقابل المجموع المباشر.",
               "النسخ شبه مطابقة كاملة لنفس النسخة الجارية؛ وهذا ما يجعل الأرشيف مربحًا."),
    },
    "EQ-07": {
        "fr": ("La masse du journal append-only",
               "Re-statuer en direct le plus lourd des journaux et le comparer à l'instantané, puis diviser par "
               "le nombre de lignes.",
               "Le journal est deuxième en masse : il est instrumenté, pas supprimé — la doctrine « journal "
               "append-only » interdit d'en effacer les traces."),
        "en": ("The mass of the append-only journal",
               "Re-stat the heaviest journal live, compare it with the snapshot, then divide by its line count.",
               "The journal ranks second by mass: it is instrumented, not deleted — the append-only doctrine "
               "forbids erasing its traces."),
        "ar": ("كتلة السجل ذي الإلحاق فقط",
               "إعادة قياس أثقل سجل مباشرة ومقارنته باللقطة ثم قسمته على عدد الأسطر.",
               "السجل ثاني الكتلة: يُرقَّب ولا يُحذف، فمذهب «إلحاق فقط» يمنع محو أثره."),
    },
    "EQ-08": {
        "fr": ("La projection qui a fait peur",
               "Cadence mesurée sur la fenêtre de 24 h × taille moyenne, en deux ordres d'association ; horizon "
               "de 30 jours en masse.",
               "Le chiffre est une projection sous convention (cadence et taille de copie constantes), pas une "
               "prévision certifiée. Aucune copie dans la fenêtre de 24 h rend l'horizon non borné ; c'est le "
               "plafond posé dans le module de sauvegarde qui a interrompu la croissance."),
        "en": ("The projection that alarmed",
               "Rate measured over the 24 h window × mean size, in two association orders; 30-day horizon as mass.",
               "The figure is a projection under a stated convention (constant rate, constant copy size), not a "
               "certified forecast. With no copy inside the 24 h window the runway is unbounded; the ceiling "
               "placed in the back-up module is what interrupted the growth."),
        "ar": ("الإسقاط الذي أيقظ القلق",
               "معدل مُقاس على نافذة 24 ساعة × الحجم المتوسط، بترتيبي جمع؛ وأفق ثلاثين يومًا ككتلة.",
               "الرقم إسقاطٌ وفق اصطلاح مصرَّح به (معدل ثابت وحجم نسخة ثابت) لا توقّع معتمد. وغيابُ أي نسخة "
               "ضمن نافذة 24 ساعة يترك الأفق غير محدود؛ والسقف الموضوع داخل وحدة النسخ هو ما أوقف النمو."),
    },
    "EQ-09": {
        "fr": ("Ce qui est récupérable, et rien d'autre",
               "R = caches + temporaires + Σ(copies hors rétention), la rétention étant la règle énoncée.",
               "Le périmètre est borné par la règle, pas par l'appétit : {gardees} copies restent disponibles "
               "pour restaurer, et les secteurs scellés de l'auteur ne sont pas touchés."),
        "en": ("What is reclaimable, and nothing else",
               "R = caches + temporaries + Σ(copies outside retention), retention being the stated rule.",
               "The perimeter is bounded by a rule, not by appetite: {gardees} copies stay available for "
               "restoration, and the author's sealed sectors are untouched."),
        "ar": ("ما يصحّ تحريره لا غير",
               "R = المخابئ + المؤقتات + Σ(النسخ الخارجة عن الاحتفاظ)، وقاعدة الاحتفاظ مصرَّح بها.",
               "النطاق ترسمه قاعدة لا شهية: تبقى {gardees} نسخ متاحة للاستعادة، والقطاعات الموقّعة للمؤلف لا "
               "تُمسّ."),
    },
    "EQ-10": {
        "fr": ("La marge de sécurité est un choix",
               "L_seuil = ρ·T avec ρ = 0,10 ; déficit Δ = max(0, L_seuil − L), vérifié par la seconde API.",
               "ρ = 0,10 est une convention d'exploitation, pas un théorème : Windows ne garantit rien à ce "
               "seuil. Elle est déclarée pour que le déficit soit calculable, pas pour être vraie."),
        "en": ("The safety margin is a choice",
               "L_threshold = ρ·T with ρ = 0.10; shortfall Δ = max(0, L_threshold − L), verified by the second API.",
               "ρ = 0.10 is an operating convention, not a theorem: Windows guarantees nothing at that threshold. "
               "It is declared so the shortfall is computable, not because it is true."),
        "ar": ("هامش الأمان خيار",
               "L_عتبة = ρ·T بـ ρ = 0.10؛ والعجز Δ = max(0, L_عتبة − L) محقَّق بالواجهة الثانية.",
               "قيمة ρ اصطلاحُ تشغيل لا نظرية؛ ويندوز لا يضمن شيئًا عند هذه العتبة. صُرّح بها ليُحسب العجز، لا "
               "لأنها صادقة."),
    },
    "EQ-11": {
        "fr": ("Le solde après libération",
               "L' = L + R, puis verdict contre le seuil ρ·T.",
               "La libération est jugée sur une addition, pas sur une impression : le solde passe au-dessus du "
               "seuil, avec une marge qui n'exige aucune suppression de contenu."),
        "en": ("The balance after reclaim",
               "L' = L + R, then a verdict against the threshold ρ·T.",
               "The reclaim is judged by an addition, not by a feeling: the balance crosses the threshold with a "
               "margin that requires no content deletion."),
        "ar": ("الرصيد بعد التحرير",
               "L' = L + R ثم الحكم مقابل العتبة ρ·T.",
               "يُقيَّم التحرير بجمع لا بانطباع: يتجاوز الرصيد العتبة بهامش لا يستلزم حذف أي محتوى."),
    },
    "EQ-12": {
        "fr": ("Le rendement de la libération",
               "η = R / T, la masse libérée rapportée au volume.",
               "Rien n'est supprimé par le module : il borne l'espace que la politique de rétention autorise à "
               "libérer. La compression change ce rendement, pas le périmètre."),
        "en": ("The yield of the reclaim",
               "η = R / T, the reclaimed mass against the volume.",
               "The module deletes nothing: it bounds the space the retention policy allows to be freed. "
               "Compression changes the yield, not the perimeter."),
        "ar": ("عائد التحرير",
               "η = R / T، أي الكتلة المحرَّرة نسبةً إلى الوحدة.",
               "لا تحذف الوحدة شيئًا: إنما تحدّ المساحة التي يسمح بها مذهب الاحتفاظ. الضغط يغيّر العائد لا النطاق."),
    },
    "EQ-13": {
        "fr": ("Les secteurs scellés restent intacts",
               "Deux prédicats indépendants d'appartenance à une classe nettoyable, appliqués aux fichiers du "
               "manifeste d'antériorité.",
               "Aucun fichier scellé ne tombe dans une catégorie nettoyable, et les deux prédicats le disent "
               "chacun de leur côté : la libération ne peut pas manger l'antériorité."),
        "en": ("The sealed sectors stay intact",
               "Two independent membership predicates for cleanable classes, applied to the files of the "
               "anteriority manifest.",
               "No sealed file falls into a cleanable class, and both predicates say so from their own side: the "
               "reclaim cannot eat into anteriority."),
        "ar": ("القطاعات الموقّعة تبقى سليمة",
               "محرّكان مستقلان للعضوية في فئة قابلة للتنظيف، مطبَّقان على ملفات قائمة الأسبقية.",
               "لا يقع أي ملف موقّع في فئة قابلة للتنظيف، وكلا المحرّكين يقول ذلك من جهته: لا يستطيع التحرير أن "
               "يأكل الأسبقية."),
    },
}

CLASSES_LBL: Dict[str, Dict[str, str]] = {
    "fr": {"copie_de_soie": "copie de soi", "autre": "autre", "temporaire_qoder": "temporaires .qoder",
           "journal": "journaux", "cache_python": "caches Python", "archive": "archives", "git": "git"},
    "en": {"copie_de_soie": "self-copy", "autre": "other", "temporaire_qoder": ".qoder temp files",
           "journal": "journals", "cache_python": "Python caches", "archive": "archives", "git": "git"},
    "ar": {"copie_de_soie": "نسخة الذات", "autre": "أخرى", "temporaire_qoder": "ملفات ‏.qoder‏ المؤقتة",
           "journal": "السجلات", "cache_python": "مخازن Python", "archive": "الأرشيف", "git": "git"},
}

FIG: Dict[str, Dict[str, str]] = {
    "fr": {"titre": "Partition du dépôt et solde libre du volume",
           "depot": "Dépôt IMAM8MAHDI", "solde": "Volume C: — solde libre",
           "avant": "libre mesuré", "apres": "projection L' = L + R",
           "seuil": "seuil ρ = 0,10 · T", "cloture": "Σ classes = {s} Go (clôture de partition, EQ-03)",
           "part": "% du dépôt", "fichiers": "fichiers"},
    "en": {"titre": "Repository partition and volume free balance",
           "depot": "IMAM8MAHDI repository", "solde": "Volume C: — free balance",
           "avant": "free measured", "apres": "projection L' = L + R",
           "seuil": "threshold ρ = 0.10 · T", "cloture": "Σ classes = {s} GiB (partition closure, EQ-03)",
           "part": "% of repository", "fichiers": "files"},
    "ar": {"titre": "تقسيم المستودع والرصيد المتاح للحجم",
           "depot": "مستودع IMAM8MAHDI", "solde": "الحجم C: — الرصيد المتاح",
           "avant": "قبل", "apres": "بعد الاحتفاظ والأرشفة",
           "seuil": "العتبة ρ = 0,10 · T", "cloture": "Σ الفئات = {s} غيبيبا (انغلاق التقسيم، EQ-03)",
           "part": "٪ من المستودع", "fichiers": "ملفًا"},
}

CSS = """
:root{--encre:#10263a;--bleu:#1f5f8b;--pale:#f5f7fa;--or:#b45309;--gris:#5b6b7a;}
*{box-sizing:border-box}
body{margin:0;font-family:Georgia,'Times New Roman',serif;color:var(--encre);
     background:#fbfcfd;line-height:1.62;font-size:17px}
html[dir="rtl"] body{font-family:'Segoe UI',Tahoma,'Traditional Arabic',Arial,sans-serif}
header.site{background:#0f2438;color:#eef4f9;padding:14px 22px;display:flex;flex-wrap:wrap;
     gap:14px;align-items:center;justify-content:space-between;font-family:'Segoe UI',Arial,sans-serif}
header.site a{color:#dce9f4;text-decoration:none;margin-left:16px;font-size:14px}
header.site .marque{font-weight:700;letter-spacing:.06em;font-size:15px}
header.site nav .langues{margin-left:14px;padding-left:12px;border-left:1px solid #34506a}
header.site nav .langues a{margin-left:6px;padding:2px 7px;border:1px solid #34506a;border-radius:5px;font-size:12.5px}
header.site nav .langues a.on{background:#dce9f4;color:#0f2438;border-color:#dce9f4;font-weight:700}
html[dir="rtl"] header.site nav .langues{margin-left:0;padding-left:0;border-left:0;margin-right:14px;
     padding-right:12px;border-right:1px solid #34506a}
html[dir="rtl"] .formule,html[dir="rtl"] table,html[dir="rtl"] pre,html[dir="rtl"] code,
html[dir="rtl"] figure,html[dir="rtl"] svg{direction:ltr;text-align:left}
main{max-width:1120px;margin:0 auto;padding:30px 22px 60px}
h1{font-size:32px;line-height:1.2;margin:10px 0 6px}
h2{font-size:23px;margin-top:44px;border-bottom:1px solid #d7e0e8;padding-bottom:6px}
h3{font-size:18px;margin:0 0 6px}
p.lead{font-size:19px;color:#33475a}
code{font-family:Consolas,monospace;font-size:.92em;background:#f4f6f8;padding:1px 5px;border-radius:4px}
.badges{margin:14px 0 6px}
.badges span{display:inline-block;font-family:'Segoe UI',Arial,sans-serif;font-size:12.5px;
     margin:0 8px 8px 0;padding:4px 10px;border-radius:20px;border:1px solid #cfdbe6;
     background:#eef4f9;color:#1f5f8b}
.badges .or{background:#fdf3e7;border-color:#ecc79a;color:#8a4b06}
.avertissement{margin:18px 0;padding:14px 16px;border-left:4px solid var(--or);
     background:#fdf8f2;font-size:15.5px;color:#4a3a28}
html[dir="rtl"] .avertissement{border-left:0;border-right:4px solid var(--or)}
.tableau{overflow-x:auto}
table{width:100%;border-collapse:collapse;font-size:14.5px;margin:14px 0}
th,td{text-align:left;padding:9px 10px;border-bottom:1px solid #e2e9ef;vertical-align:top}
html[dir="rtl"] th,html[dir="rtl"] td{text-align:right}
th{font-family:'Segoe UI',Arial,sans-serif;font-size:12.5px;text-transform:uppercase;
   letter-spacing:.05em;color:#5b6b7a;background:#f5f7fa}
tbody tr:hover{background:#f8fbfd}
td.id{white-space:nowrap;font-weight:700;color:#0f3d5c}
.formule{display:block;font-family:Consolas,monospace;font-size:13.5px;color:#1f4e6b;background:#f4f8fb;
     padding:10px 12px;border-radius:6px;overflow-x:auto;white-space:pre-wrap;overflow-wrap:anywhere}
code,.carte .res,.carte .lecture,.carte .chemin{overflow-wrap:anywhere}
.grille{display:grid;grid-template-columns:repeat(2,1fr);gap:16px;margin-top:18px}
.carte{border:1px solid #dde6ed;border-radius:10px;padding:16px 18px;background:#fff}
.carte .entete{display:flex;justify-content:space-between;align-items:center;
     font-family:'Segoe UI',Arial,sans-serif;font-size:12.5px;color:#5b6b7a;margin-bottom:8px}
.carte .equation{font-size:15px;color:#33475a;margin:0 0 10px}
.carte .res{font-size:15px;margin:10px 0 0;padding:8px 10px;background:#f4f8fb;border-radius:6px}
.carte .lecture{font-size:15px;color:#3c4f61;margin:10px 0 0}
.carte .chemin{font-family:Consolas,monospace;font-size:12.5px;color:#5b6b7a;margin:8px 0 0}
.statut{display:inline-block;font-family:'Segoe UI',Arial,sans-serif;font-size:11.5px;
     padding:2px 9px;border-radius:20px;border:1px solid #cfdbe6;background:#eef4f9;color:#1f5f8b;
     white-space:nowrap}
.statut.o{background:#eaf6ef;border-color:#bfe0cb;color:#1e6b3a}
.statut.s{background:#fdf3e7;border-color:#ecc79a;color:#8a4b06}
.statut.p{background:#f0eefc;border-color:#cfc6f2;color:#4b3a9a}
.statut.ok{background:#eaf6ef;border-color:#bfe0cb;color:#1e6b3a}
.statut.ko{background:#fdecea;border-color:#f3b4ad;color:#9b1c1c}
figure{margin:20px 0;padding:10px;border:1px solid #dde6ed;border-radius:10px;background:#fff}
figure svg{width:100%;height:auto;display:block}
figcaption{font-size:14px;color:#5b6b7a;margin-top:8px}
ul{margin:10px 0 0;padding-left:20px}
html[dir="rtl"] ul{padding-left:0;padding-right:20px}
li{margin:6px 0}
pre{background:#f6f8fa;border:1px solid #d7e0e8;border-radius:8px;padding:14px;overflow-x:auto;font-size:13.5px}
.actions{margin-top:26px;display:flex;flex-wrap:wrap;gap:10px}
.actions a{font-family:'Segoe UI',Arial,sans-serif;font-size:14px;text-decoration:none;
     padding:9px 16px;border-radius:8px;border:1px solid #1f5f8b;color:#1f5f8b}
.actions a.principal{background:#1f5f8b;color:#fff}
.note-langue{font-size:13.5px;color:#5b6b7a;margin-top:10px}
footer.site{background:#0f2438;color:#c9d9e6;padding:18px 22px;font-size:13.5px;
     font-family:'Segoe UI',Arial,sans-serif;text-align:center}
footer.site a{color:#dce9f4}
@media (max-width:900px){.grille{grid-template-columns:1fr}}
"""


def _nav(lang: str) -> str:
    t = T[lang]
    liens = (
        ("/", t["nav"][0]),
        ("/oeuvre-universelle", t["nav"][1]),
        ("/observateur-triniter", t["nav"][2]),
        ("/portefeuille", t["nav"][3]),
        ("/developpeurs", t["nav"][4]),
    )
    corps = "".join(f"<a href='{h}'>{_ech(libelle)}</a>" for h, libelle in liens)
    langues = "".join(
        f"<a class='langue{' on' if code == lang else ''}' href='{CHEMINS[code]}' "
        f"hreflang='{code}' lang='{code}'>{libelle}</a>"
        for code, libelle in (("fr", "FR"), ("en", "EN"), ("ar", "العربية"))
    )
    return (
        "<header class='site'><div class='marque'>AL-MIZAN.WORLD</div><nav>"
        f"{corps}<span class='langues'>{langues}</span></nav></header>"
    )


def _pied(lang: str) -> str:
    return f"<footer class='site'>{T[lang]['pied'].format(auteur=_ech(AUTEUR))}</footer>"


def _classe_statut(statut: str) -> str:
    return {"OPÉRATIONNEL": "o", "SIMULÉ": "s", "SPÉCIFIÉ": "p"}.get(statut, "")


def _table(donnees: Dict[str, Any], lang: str, val: Dict[str, str]) -> str:
    t = T[lang]
    lignes = []
    for eq in donnees["equations"]:
        lignes.append(
            "<tr>"
            f"<td class='id'><a href='#{eq['id'].lower()}'>{eq['id']}</a></td>"
            f"<td>{_ech(t['objets'][eq['id']])}</td>"
            f"<td><span class='formule'>{_ech(eq['formule'])}</span></td>"
            f"<td>{_ech(_fmt(eq['resultat'], val))}</td>"
            f"<td><span class='statut {_classe_statut(eq['statut'])}'>"
            f"{_ech(t['statuts'][eq['statut']])}</span></td>"
            "</tr>"
        )
    return (
        "<div class='tableau'><table><thead><tr>"
        f"<th>{t['th_id']}</th><th>{t['th_equation']}</th><th>{t['th_formule']}</th>"
        f"<th>{t['th_resultat']}</th><th>{t['th_statut']}</th>"
        "</tr></thead><tbody>" + "".join(lignes) + "</tbody></table></div>"
    )


def _table_controles(donnees: Dict[str, Any], lang: str) -> str:
    t = T[lang]
    lignes = []
    for c in donnees["controles"]:
        etat = t["ok_label"] if c["ok"] else t["ko_label"]
        cls = "ok" if c["ok"] else "ko"
        lignes.append(
            "<tr>"
            f"<td class='id'>{_ech(c['id'])}</td>"
            f"<td>{_ech(c['nom'])}</td>"
            f"<td><span class='formule'>{_ech(c['attendu'])}</span></td>"
            f"<td><span class='formule'>{_ech(c['obtenu'])}</span></td>"
            f"<td><span class='statut {cls}'>{_ech(etat)}</span></td>"
            "</tr>"
        )
    return (
        "<div class='tableau'><table><thead><tr>"
        f"<th>{t['th_controle']}</th><th>{t['th_equation']}</th><th>{t['th_attendu']}</th>"
        f"<th>{t['th_obtenu']}</th><th>{t['th_etat']}</th>"
        "</tr></thead><tbody>" + "".join(lignes) + "</tbody></table></div>"
    )


def _cartes(donnees: Dict[str, Any], lang: str, val: Dict[str, str]) -> str:
    blocs = []
    for eq in donnees["equations"]:
        titre, pose, lecture = EQ_TEXT[eq["id"]][lang]
        t = T[lang]
        statut = t["statuts"][eq["statut"]]
        blocs.append(
            f"<article class='carte' id='{eq['id'].lower()}'>"
            f"<div class='entete'><span class='id'>{eq['id']}</span>"
            f"<span>{_ech(t['objets'][eq['id']])}</span></div>"
            f"<h3>{_ech(titre)}</h3>"
            f"<p class='equation'>{_ech(pose)}</p>"
            f"<div class='formule'>{_ech(eq['formule'])}</div>"
            f"<p class='res'><strong>{t['th_resultat']} :</strong> {_ech(_fmt(eq['resultat'], val))}</p>"
            f"<p class='lecture'>{_ech(_fmt(lecture, val))}</p>"
            f"<p class='chemin'>{_ech(eq['chemin'])}</p>"
            f"<span class='statut {_classe_statut(eq['statut'])}'>{_ech(statut)}</span>"
            "</article>"
        )
    return "<div class='grille'>" + "".join(blocs) + "</div>"


def _corps(donnees: Dict[str, Any], svg: str, lang: str, val: Dict[str, str]) -> str:
    t = T[lang]
    limites = "".join(f"<li>{_ech(_fmt(x, val))}</li>" for x in donnees["limites"])
    return f"""
<h1>{_fmt(t['h1'], val)}</h1>
<p class="lead">{_fmt(t['lead'], val)}</p>
<div class="badges">
  <span>{t['badge_calc']}</span>
  <span>{_fmt(t['badge_ctrl'], val)}</span>
  <span class="or">{t['badge_hon']}</span>
</div>

<div class="avertissement">
  <strong>{t['warn_titre']}</strong> {t['warn_corps']}
</div>

<h2 id="source">{t['s_source']}</h2>
<p>{_fmt(t['p_source'], val)}</p>

<h2 id="table">{t['s_table']}</h2>
<p>{t['p_table']}</p>
{_table(donnees, lang, val)}

<h2 id="detail">{t['s_detail']}</h2>
{_cartes(donnees, lang, val)}

<h2 id="controles">{t['s_controles']}</h2>
<p>{t['p_controles']}</p>
{_table_controles(donnees, lang)}

<h2 id="figure">{t['s_figure']}</h2>
<figure>{svg}<figcaption>{t['fig_legende']}</figcaption></figure>

<h2 id="conclusion">{t['s_mizan']}</h2>
<p>{_fmt(t['p_mizan'], val)}</p>

<h2 id="reproductibilite">{t['s_repro']}</h2>
<pre>py -3 outils/collecter_instantane_espace_disque.py
py -3 oeuvre_universelle/espace_disque.py
py -3 outils/archiver_copies_de_soie.py
py -3 -m unittest tests.test_espace_disque -v</pre>
<p>{t['p_repro']}</p>

<h2 id="limites">{t['s_limites']}</h2>
<ul>{limites}</ul>

<div class="actions">
  <a class="principal" href="/espace-disque.json">{t['actions_json']}</a>
  <a href="/oeuvre-universelle">{t['actions_oeuvre']}</a>
</div>
<p class="note-langue">{t['note_langue']}</p>
"""


def _html(donnees: Dict[str, Any], svg: str, lang: str, val: Dict[str, str]) -> str:
    t = T[lang]
    alternates = "".join(
        f"<link rel='alternate' hreflang='{code}' href='{SITE}{CHEMINS[code]}'>\n"
        for code in LANGUES
    )
    return f"""<!DOCTYPE html>
<html lang="{t['lang']}" dir="{t['dir']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_ech(t['titre'])}</title>
<meta name="description" content="{_ech(t['description'])}">
<link rel="canonical" href="{SITE}{CHEMINS[lang]}">
{alternates}<link rel="alternate" hreflang="x-default" href="{SITE}/espace-disque">
<meta property="og:title" content="{_ech(t['og_titre'])}">
<meta property="og:description" content="{_ech(t['description'])}">
<meta property="og:type" content="article">
<meta property="og:locale" content="{t['locale']}">
<style>{CSS}</style>
</head>
<body>
{_nav(lang)}
<main>
{_corps(donnees, svg, lang, val)}
</main>
{_pied(lang)}
</body>
</html>
"""


def generer() -> Dict[str, Any]:
    donnees = resoudre()
    if not verifier(donnees):
        echoues = [c["id"] for c in donnees["controles"] if not c["ok"]]
        raise RuntimeError(f"Contrôles numériques en échec : {echoues}")
    donnees["source"]["empreinte"] = donnees["invariants"]["empreinte_instantane"]
    val = _valeurs(donnees)
    _controler_cles(val)

    WEB_CLOUD.mkdir(parents=True, exist_ok=True)
    RESULTATS.mkdir(parents=True, exist_ok=True)
    for lang in LANGUES:
        PAGES[lang].write_text(_html(donnees, _figure(donnees, lang), lang, _valeurs(donnees, lang)),
                               encoding="utf-8", newline="\n")
    publiees = _json_sur(donnees)
    publiees["limites"] = list(publiees["limites"]) + [
        "Le JSON publié rend une valeur non finie en null (RFC 8259) : resoudre() la renvoie en float infini.",
    ]
    charge = json.dumps(publiees, ensure_ascii=False, indent=2, default=str, allow_nan=False)
    DONNEES_JSON.write_text(charge, encoding="utf-8", newline="\n")
    ARCHIVE_JSON.write_text(charge, encoding="utf-8", newline="\n")
    return {
        "pages": {lang: {"chemin": str(PAGES[lang]), "octets": PAGES[lang].stat().st_size}
                  for lang in LANGUES},
        "json": str(DONNEES_JSON),
        "controles": f"{donnees['resume']['controles_ok']}/{donnees['resume']['controles_total']}",
        "equations": len(donnees["equations"]),
        "valeurs": val,
    }


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print(json.dumps(generer(), ensure_ascii=False, indent=2))
