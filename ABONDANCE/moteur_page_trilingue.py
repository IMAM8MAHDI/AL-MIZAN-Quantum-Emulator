# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""Moteur de pages trilingues (fr/en/ar) pour le dossier ABONDANCE.

Le moteur ne connaît aucune équation : il reçoit un spec (titre, chemins,
textes par langue, figures) et le dictionnaire rendu par un module
`*_abondance.py`, et il assemble la page HTML, le CSV Excel-français, le
Markdown et le SVG. Un seul patron, trois langues, zéro JavaScript.

Garde-fils : `verifier_nombres` refuse toute phrase d'une langue qui énonce un
nombre absent de la ligne calculée française. Une traduction ne peut donc pas
inventer ni laisser vieillir un chiffre.
"""
from __future__ import annotations

import csv
import html
import io
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

LANGUES: Tuple[str, ...] = ("fr", "en", "ar")
AUTEUR = "M. Ahmed EL BAHLOUL (IMAM8MAHDI)"
LICENCE = "GPL-3.0-only OR AGPL-3.0-only"

CODE_LANGUE = {"fr": "fr-FR", "en": "en-GB", "ar": "ar-SA"}

# ----------------------------------------------------------------------------
# Chaînes d'interface, par langue
# ----------------------------------------------------------------------------
T: Dict[str, Dict[str, str]] = {
    "fr": {
        "lang": "fr", "dir": "ltr", "locale": "fr_FR",
        "saut": "Aller au contenu",
        "nav": "Langue", "nav_site": "Sommaire du dossier",
        "equations": "Équations posées",
        "controles": "Contrôles numériques",
        "cheminement": "Cheminement",
        "materiaux": "Matériaux et valeurs déclarées",
        "reproduction": "Reproduire le calcul",
        "resultats": "Résultats clés",
        "statuts": "Statuts",
        "sources": "Sources et prédécesseurs",
        "col_id": "ID", "col_titre": "Titre", "col_formule": "Formule",
        "col_ligne": "Ligne calculée", "col_statut": "Statut",
        "col_controle": "Contrôle", "col_attendu": "Attendu", "col_obtenu": "Obtenu",
        "col_ok": "État", "ok": "reçu", "ko": "manquant",
        "col_matiere": "Matériau", "col_quantite": "Quantité",
        "col_equation": "Équation source",
        "caption_eq": "Équations du dossier, chacune suivie du chemin module → fonction → "
                      "contrôle. La colonne formule recopie la notation du module : les "
                      "identifiants qu'elle porte (noms de variables, symboles d'unités) "
                      "restent écrits tels quels ; seules les qualifications en français "
                      "sont traduites sur les pages anglaise et arabe.",
        "caption_ctrl": "Contrôles exécutés par le module ; la page n'est publiée que s'ils "
                        "passent tous. Les intitulés sont ceux du code source : identifiants, "
                        "ils ne sont pas traduits.",
        "caption_resultats": "Quelques valeurs lues directement dans le JSON calculé.",
        "pied": "Document calculé, non écrit à la main : régénérer le module régénère la page.",
        "legende_statuts": "OPÉRATIONNEL = calculé et contrôlé ici ; SIMULÉ = modèle à valeurs déclarées ; SPÉCIFIÉ = cadre posé, mesure à faire.",
    },
    "en": {
        "lang": "en", "dir": "ltr", "locale": "en_GB",
        "saut": "Skip to content",
        "nav": "Language", "nav_site": "Series contents",
        "equations": "Equations set out",
        "controles": "Numerical checks",
        "cheminement": "Line of reasoning",
        "materiaux": "Materials and declared values",
        "reproduction": "Reproduce the calculation",
        "resultats": "Key results",
        "statuts": "Statuses",
        "sources": "Sources and predecessors",
        "col_id": "ID", "col_titre": "Title", "col_formule": "Formula",
        "col_ligne": "Computed line", "col_statut": "Status",
        "col_controle": "Check", "col_attendu": "Expected", "col_obtenu": "Obtained",
        "col_ok": "State", "ok": "met", "ko": "missing",
        "col_matiere": "Material", "col_quantite": "Quantity",
        "col_equation": "Source equation",
        "caption_eq": "Series equations, each followed by the module → function → check path. "
                      "Paths and module names are source identifiers and stay as written. The "
                      "formula column reproduces the module's own notation: the identifiers it "
                      "carries (variable names, unit symbols) are kept exactly as written, and "
                      "only the French qualifiers after the semicolon are translated.",
        "caption_ctrl": "Checks run by the module; the page is published only when all of them "
                        "pass. The names are the source code's own: they are identifiers, "
                        "so they are not translated. What each one verifies is stated, in "
                        "this language, in the reading line of the equation it belongs to.",
        "caption_resultats": "Values read straight from the computed JSON.",
        "pied": "A computed document, not a hand-written one: re-run the module and the page reappears.",
        "legende_statuts": "OPERATIONAL = computed and checked here; SIMULATED = model with declared inputs; SPECIFIED = framework set, measurement pending.",
    },
    "ar": {
        "lang": "ar", "dir": "rtl", "locale": "ar_SA",
        "saut": "الانتقال إلى المحتوى",
        "nav": "اللغة", "nav_site": "فهرس السلسلة",
        "equations": "المعادلات المُقَرَّرة",
        "controles": "التحققات العددية",
        "cheminement": "مسار الاستدلال",
        "materiaux": "المواد والقيم المُعلَنة",
        "reproduction": "إعادة الحساب",
        "resultats": "النتائج الأساسية",
        "statuts": "المراتب",
        "sources": "المصادر والسابقون",
        "col_id": "م", "col_titre": "العنوان", "col_formule": "الصيغة",
        "col_ligne": "السطر المحسوب", "col_statut": "المرتبة",
        "col_controle": "التحقق", "col_attendu": "المتوقع", "col_obtenu": "المُحصَّل",
        "col_ok": "الحالة", "ok": "مستوفى", "ko": "ناقص",
        "col_matiere": "المادة", "col_quantite": "الكمية",
        "col_equation": "المعادلة المصدر",
        "caption_eq": "معادلات السلسلة، يتبع كلًّا منها المسار من الوحدة إلى الدالة إلى التحقق. "
                      "وأسماء الوحدات والمسارات معرّفات شيفرة فتبقى كما هي. وعمود الصيغة ينسخ "
                      "تدوين الوحدة كما هو: فأسماء المتغيرات ورموز الوحدات تبقى مكتوبة كما هي، "
                      "ولا تُترجَم سوى التعليقات الفرنسية التي تأتي بعد الفاصلة المنقوطة.",
        "caption_ctrl": "التحققات التي تجريها الوحدة؛ لا تُنشَر الصفحة إلا إذا نجحت كلها. "
                        "والأسماء هي أسماء الشيفرة المصدرية: فهي معرّفات فلا تُترجَم. "
                        "وأما ما يثبته كلُّ فحص فقد جاء بعبارة هذه اللغة في سطر القراءة "
                        "الملحَق بمعادلته.",
        "caption_resultats": "قيم مقروءة مباشرة من ملف JSON المحسوب.",
        "pied": "وثيقة محسوبة لا مكتوبة باليد: أعد تشغيل الوحدة تُعاد الصفحة.",
        "legende_statuts": "عامل = محسوب ومُتحقَّق منه هنا؛ محاكى = نموذج بقيم معلَنة؛ محدَّد = إطار مقرر والقياسُ باقٍ.",
    },
}

STATUT_CLASSE = {"OPÉRATIONNEL": "o", "SIMULÉ": "s", "SPÉCIFIÉ": "p"}
STATUT_LIBELLE = {
    "fr": {"OPÉRATIONNEL": "OPÉRATIONNEL", "SIMULÉ": "SIMULÉ", "SPÉCIFIÉ": "SPÉCIFIÉ"},
    "en": {"OPÉRATIONNEL": "OPERATIONAL", "SIMULÉ": "SIMULATED", "SPÉCIFIÉ": "SPECIFIED"},
    "ar": {"OPÉRATIONNEL": "عامِل", "SIMULÉ": "محاكى", "SPÉCIFIÉ": "محدَّد"},
}

CSS = """
:root{--encre:#10263a;--bleu:#1f5f8b;--pale:#f5f7fa;--or:#b45309;--gris:#5b6b7a;--cible:#0f3d5c}
*{box-sizing:border-box}
body{margin:0;font-family:Georgia,'Times New Roman',serif;color:var(--encre);
background:#fbfcfd;line-height:1.62;font-size:17px}
html[dir="rtl"] body{font-family:'Segoe UI',Tahoma,'Traditional Arabic',Arial,sans-serif}
html[dir="rtl"] .formule,html[dir="rtl"] .nb,html[dir="rtl"] table,html[dir="rtl"] pre,
html[dir="rtl"] code{direction:ltr;text-align:left}
html[dir="rtl"] td.titre,html[dir="rtl"] td.lecture{text-align:right}
a{color:var(--cible)}
header.site{background:#0f2438;color:#f2f6fa;padding:14px 22px}
header.site .bande{max-width:1120px;margin:0 auto;display:flex;flex-wrap:wrap;
align-items:center;justify-content:space-between;gap:12px}
header.site strong{font-size:19px;letter-spacing:.2px}
header.site a{color:#e8f1f8;text-decoration:none}
header.site nav{display:flex;flex-wrap:wrap;gap:4px}
header.site nav .langues{display:flex;flex-wrap:wrap;gap:4px}
header.site nav .langues a{padding:7px 12px;border:1px solid #47688a;border-radius:6px;min-height:30px}
header.site nav .langues a.on{background:#fdf3e7;color:#0f2438;border-color:#fdf3e7;font-weight:700}
header.site :focus-visible{outline:3px solid #fdf3e7;outline-offset:2px}
:focus-visible{outline:3px solid var(--or);outline-offset:2px}
.saut a{position:absolute;left:-9999px;top:auto;background:#fdf3e7;color:#0f2438;
padding:10px 14px;border-radius:6px;min-height:30px}
.saut a:focus{left:12px;top:12px;z-index:9}
main{max-width:1120px;margin:0 auto;padding:30px 22px 60px}
main p{max-width:38em}
h1{font-size:33px;line-height:1.2;margin:6px 0 10px}
h2{font-size:25px;margin:34px 0 10px;border-bottom:2px solid #dbe6ef;padding-bottom:6px}
h3{font-size:20px;margin:22px 0 8px}
.badges{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0 4px}
.badges span{border:1px solid #cfdce7;background:var(--pale);border-radius:20px;
padding:6px 13px;font-size:14px;min-height:30px;display:inline-flex;align-items:center}
.badges .or{border-color:var(--or);color:#7a3c07;background:#fff7ed}
.formule{display:block;font-family:Consolas,Menlo,monospace;font-size:13.5px;color:#1f4e6b;
background:#f4f8fb;padding:10px 12px;border-radius:6px;overflow-x:auto}
.chemin{font-family:Consolas,Menlo,monospace;font-size:12px;color:var(--gris);white-space:nowrap}
.calcul{display:block;direction:ltr;text-align:left;font-family:Consolas,Menlo,monospace;
font-size:12.5px;color:#1f4e6b;background:#f4f8fb;padding:8px 10px;border-radius:6px;
margin-top:6px;white-space:normal}
.tableau{overflow-x:auto}
pre{background:#0f2438;color:#eaf2f8;padding:14px 16px;border-radius:8px;
overflow-x:auto;font-size:13.5px}
table{width:100%;border-collapse:collapse;font-size:14.5px;margin:14px 0}
caption{caption-side:top;text-align:left;font-size:13.5px;color:var(--gris);padding:0 0 8px}
html[dir="rtl"] caption{text-align:right}
th,td{text-align:left;padding:9px 10px;border-bottom:1px solid #e2e9ef;vertical-align:top}
html[dir="rtl"] th,html[dir="rtl"] td{text-align:right}
html[dir="rtl"] td.nb,html[dir="rtl"] th.nb{text-align:left}
th{background:#eef4f9;color:#0f2438}
td.id{white-space:nowrap;font-weight:700;color:var(--cible)}
.statut{display:inline-block;font-size:12.5px;font-weight:700;letter-spacing:.3px;
padding:4px 10px;border-radius:20px;border:1px solid;min-height:26px}
.statut.o{color:#14532d;border-color:#86efac;background:#f0fdf4}
.statut.s{color:#7c2d12;border-color:#fdba74;background:#fff7ed}
.statut.p{color:#334155;border-color:#cbd5e1;background:#f8fafc}
.grille{display:grid;grid-template-columns:repeat(2,1fr);gap:16px;margin-top:18px}
.carte{border:1px solid #dbe6ef;border-radius:10px;padding:14px 16px;background:#fff}
.carte h3{margin:0 0 6px;font-size:18px}
.carte .gros{font-size:26px;font-weight:700;color:var(--cible)}
html[dir="rtl"] .carte .gros{direction:ltr;text-align:left}
.etape{border-left:4px solid var(--bleu);padding:4px 0 4px 16px;margin:0 0 18px}
html[dir="rtl"] .etape{border-left:0;border-right:4px solid var(--bleu);padding:4px 16px 4px 0}
.etape h3{margin:0 0 4px;font-size:19px}
figure{margin:22px 0;padding:0}
figcaption{font-size:13.5px;color:var(--gris);margin-top:8px}
footer.site{border-top:2px solid #dbe6ef;margin-top:40px;padding:22px;color:var(--gris);font-size:14px}
footer.site .interieur{max-width:1120px;margin:0 auto}
.actions{display:flex;flex-wrap:wrap;gap:10px;margin:20px 0}
.actions a{display:inline-flex;align-items:center;justify-content:center;min-height:44px;
padding:10px 16px;border:1px solid var(--cible);border-radius:8px;text-decoration:none;font-weight:700}
.actions a.principal{background:var(--cible);color:#fff}
.sommaire{display:flex;flex-wrap:wrap;gap:8px;margin:20px 0 8px}
.sommaire a{display:inline-flex;align-items:center;min-height:30px;padding:6px 12px;
border:1px solid #cfdce7;border-radius:8px;text-decoration:none;font-size:14.5px}
ul{margin:10px 0 10px 22px;padding:0}
html[dir="rtl"] ul{margin:10px 22px 10px 0}
@media (max-width:900px){.grille{grid-template-columns:1fr}h1{font-size:28px}}
"""


# ----------------------------------------------------------------------------
# Utilitaires
# ----------------------------------------------------------------------------
def ech(v: Any) -> str:
    return html.escape(str(v), quote=True)


def _norm(x: str) -> str:
    """Chiffres normalisés : insécables, espaces fines, séparateurs milliers."""
    return (x.replace("\u202f", "").replace("\u00a0", "")
             .replace("\u2009", "").replace(" ", ""))


def _eclater(brut: str) -> List[str]:
    """« 0.866, 29.914 » et « √2 16.6573 » sont deux nombres, pas un seul « 216.6573 »."""
    morceaux: List[str] = []
    for morceau in re.split(r"[.,]\s+", brut):
        morceaux.extend(re.split(r"\s+(?=\d*[.,]\d)", morceau))
    return [m for m in morceaux if m]


def nombres(texte: str) -> List[str]:
    """Nombre écrits dans un texte, virgule décimale acceptée, séparés de milliers ôtés."""
    out: List[str] = []
    for brut in re.findall(r"\d[\d\s.,\u202f\u00a0]*", texte):
        for morceau in _eclater(brut):
            tok = _norm(morceau)
            if not tok or tok in (",", "."):
                continue
            if tok.count(",") == 1 and tok.count(".") == 0:
                tok = tok.replace(",", ".")
            elif tok.count(",") == 1 and tok.count(".") == 1 and tok.index(",") < tok.index("."):
                tok = tok.replace(",", "")
            elif tok.count(",") > 1 and tok.count(".") == 0:
                tok = (tok.replace(",", ".") if len(tok.split(",")[-1]) != 3
                       else tok.replace(",", ""))
            out.append(tok.rstrip(".,"))
    return out


def pool_nombres(*textes: str) -> set:
    """Ensemble des valeurs numériques rendues par les lignes calculées (FR)."""
    vals: set = set()
    for t in textes:
        for n in nombres(t):
            try:
                vals.add(round(float(n), 10))
            except ValueError:
                continue
    return vals


def verifier_nombres(phrase: str, pool: set) -> List[str]:
    """Nombres énoncés dans `phrase` qui ne figurent pas dans `pool`."""
    manquants: List[str] = []
    for n in nombres(phrase):
        try:
            v = round(float(n), 10)
        except ValueError:
            continue
        if v in pool:
            continue
        if not any(abs(v - p) <= max(1e-9, abs(p) * 1e-6) for p in pool):
            manquants.append(n)
    return manquants


# ----------------------------------------------------------------------------
# primitives HTML
# ----------------------------------------------------------------------------
def _alternates(chemins: Dict[str, str], base: str) -> str:
    lignes = [f"<link rel=\"alternate\" hreflang=\"{l}\" href=\"{base}{chemins[l]}\">"
              for l in LANGUES]
    lignes.append(f"<link rel=\"alternate\" hreflang=\"x-default\" href=\"{base}{chemins['fr']}\">")
    return "\n".join(lignes)


def tete(t: Dict[str, str], titre: str, description: str,
         chemins: Dict[str, str], canonique: str, base: str = "") -> str:
    direction = f' dir="{t["dir"]}"' if t["dir"] != "ltr" else ""
    return f"""<!DOCTYPE html>
<html lang="{t['lang']}"{direction}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{ech(titre)}</title>
<meta name="description" content="{ech(description)}">
<link rel="canonical" href="{base}{canonique}">
<meta property="og:url" content="{base}{canonique}">
{_alternates(chemins, base)}
<meta property="og:title" content="{ech(titre)}">
<meta property="og:description" content="{ech(description)}">
<meta property="og:type" content="article">
<meta property="og:locale" content="{t['locale']}">
<style>{CSS}</style>
</head>"""


def en_tete(t: Dict[str, str], courant: str, chapitres: Sequence[Sequence[str]],
            titre_bande: str) -> str:
    liens = []
    for item in chapitres:
        code, libelle = item[0], item[1]
        href = item[2] if len(item) > 2 else code
        on = ' class="on" aria-current="page"' if code == courant else ""
        liens.append(f'<a href="{ech(href)}"{on} lang="{code}">{ech(libelle)}</a>')
    nav = (f'<nav aria-label="{ech(t["nav"])}"><span class="langues">'
           + "".join(liens) + "</span></nav>")
    return f"""<div class="saut"><a href="#contenu">{ech(t["saut"])}</a></div>
<header class="site"><div class="bande">
<strong>{ech(titre_bande)}</strong>
{nav}
</div></header>"""


def badges(items: Iterable[Tuple[str, bool]]) -> str:
    return ('<div class="badges">' + "".join(
        f'<span class="{"or" if or_ else ""}">{ech(txt)}</span>' for txt, or_ in items
    ) + "</div>")


def tableau(nom: str, caption: str, entetes: Sequence[Tuple[str, str]],
            lignes: Sequence[Sequence[str]]) -> str:
    th = "".join(f'<th scope="col"{c}>{e}</th>' for e, c in entetes)
    corps = []
    for ligne in lignes:
        cellules = []
        for i, valeur in enumerate(ligne):
            cls = entetes[i][1]
            if i == 0:
                cls = "id"
                scope = ' scope="row"'
            else:
                scope = ""
            cellules.append(f'<td class="{cls}"{scope}>{valeur}</td>')
        corps.append("<tr>" + "".join(cellules) + "</tr>")
    return (f"<div class=\"tableau\"><table id=\"{nom}\"><caption>{ech(caption)}</caption>"
            f"<thead><tr>{th}</tr></thead><tbody>{''.join(corps)}</tbody></table></div>")


# ----------------------------------------------------------------------------
# figures SVG calculées
# ----------------------------------------------------------------------------
def _svg(largeur: int, hauteur: int, titre: str, description: str,
         corps: str, ids: Tuple[str, str]) -> str:
    return (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {largeur} {hauteur}'"
            f" width='100%' role='img' aria-labelledby='{ids[0]} {ids[1]}'>"
            f"<title id='{ids[0]}'>{ech(titre)}</title>"
            f"<desc id='{ids[1]}'>{ech(description)}</desc>{corps}</svg>")


def figure_barres(titre: str, description: str, serie: Sequence[Tuple[str, float, str]],
                  plafond: float | None = None, ids: Tuple[str, str] = ("fig-t", "fig-d"),
                  largeur: int = 1120, etiq_largeur: int = 320) -> str:
    """Barres horizontales proportionnelles ; `plafond` trace la limite théorique."""
    haut = 96 + 54 * len(serie) + 46
    valeurs = [v for _, v, _ in serie] + ([plafond] if plafond is not None else [])
    emin, emax = 0.0, max(valeurs)
    emin = min(emin, min(valeurs))
    zone_l = largeur - etiq_largeur - 150
    if emax - emin <= 0:
        emax = emin + 1.0
    echelle = lambda v: etiq_largeur + (v - emin) / (emax - emin) * zone_l  # noqa: E731
    pieces = [f"<rect x='0' y='0' width='{largeur}' height='{haut}' fill='#ffffff'/>"]
    y = 60
    for nom, val, couleur in serie:
        x0, x1 = echelle(emin), echelle(val)
        if x1 < x0:
            x0, x1 = x1, x0
        pieces.append(
            f"<rect x='{x0:.1f}' y='{y}' width='{max(x1 - x0, 1.5):.1f}' height='30'"
            f" fill='{couleur or '#1f5f8b'}' opacity='0.85' rx='4'/>")
        pieces.append(f"<text x='{etiq_largeur - 14}' y='{y + 21}' text-anchor='end'"
                      f" font-family='Segoe UI,Arial' font-size='15' fill='#10263a'>{ech(nom)}</text>")
        pieces.append(f"<text x='{largeur - 138}' y='{y + 21}' font-family='Segoe UI,Arial'"
                      f" font-size='15' fill='#0f3d5c'>{ech(_fmt(val))}</text>")
        y += 54
    if plafond is not None:
        xp = echelle(plafond)
        pieces.append(f"<line x1='{xp:.1f}' y1='46' x2='{xp:.1f}' y2='{y - 18}'"
                      f" stroke='#b45309' stroke-width='2' stroke-dasharray='7 5'/>")
        pieces.append(f"<text x='{xp + 8:.1f}' y='40' font-family='Segoe UI,Arial'"
                      f" font-size='14' fill='#b45309'>{ech(_fmt(plafond))}</text>")
    pieces.append(f"<line x1='{etiq_largeur}' y1='46' x2='{etiq_largeur}' y2='{y - 18}'"
                  f" stroke='#5b6b7a' stroke-width='1.4'/>")
    return _svg(largeur, haut, titre, description, "".join(pieces), ids)


def figure_baril(titre: str, description: str, planches: Sequence[Tuple[str, float]],
                 plafond: float, ids: Tuple[str, str] = ("fig-t", "fig-d"),
                 largeur: int = 1120) -> str:
    """Baril de Liebig : chaque planche à sa hauteur, le remplissage au min."""
    haut, bas = 460, 400
    n = max(len(planches), 1)
    marge_l, marge_r = 90, 190
    zone_l = largeur - marge_l - marge_r
    large_b = zone_l / (2 * n - 1)
    scale = lambda v: (v / max(plafond, 1e-12)) * (haut - 120)  # noqa: E731
    pieces = [f"<rect x='0' y='0' width='{largeur}' height='{haut + 90}' fill='#ffffff'/>"]
    h_min = min(v for _, v in planches)
    y_remplissage = bas - scale(h_min)
    pieces.append(f"<rect x='{marge_l}' y='{y_remplissage:.1f}' width='{zone_l:.1f}'"
                  f" height='{scale(h_min):.1f}' fill='#1f5f8b' opacity='0.22'/>")
    for i, (nom, val) in enumerate(planches):
        x = marge_l + i * 2 * large_b
        h = scale(val)
        pieces.append(f"<rect x='{x:.1f}' y='{bas - h:.1f}' width='{large_b * 0.78:.1f}'"
                      f" height='{h:.1f}' fill='#1f5f8b' opacity='0.85' rx='3'/>")
        pieces.append(f"<text x='{x + large_b * 0.39:.1f}' y='{bas + 26}' text-anchor='middle'"
                      f" font-family='Segoe UI,Arial' font-size='14' fill='#10263a'>{ech(nom)}</text>")
        pieces.append(f"<text x='{x + large_b * 0.39:.1f}' y='{bas - h - 10:.1f}'"
                      f" text-anchor='middle' font-family='Segoe UI,Arial' font-size='14'"
                      f" fill='#0f3d5c'>{ech(_fmt(val))}</text>")
    pieces.append(f"<line x1='{marge_l - 20}' y1='{y_remplissage:.1f}'"
                  f" x2='{largeur - marge_r + 60}' y2='{y_remplissage:.1f}'"
                  f" stroke='#b45309' stroke-width='2' stroke-dasharray='7 5'/>")
    pieces.append(f"<text x='{largeur - marge_r + 66}' y='{y_remplissage + 5:.1f}'"
                  f" font-family='Segoe UI,Arial' font-size='15' fill='#b45309'>"
                  f"{ech(_fmt(h_min))}</text>")
    pieces.append(f"<line x1='{marge_l - 20}' y1='{bas}' x2='{largeur - 40}' y2='{bas}'"
                  f" stroke='#5b6b7a' stroke-width='1.6'/>")
    return _svg(largeur, haut + 90, titre, description, "".join(pieces), ids)


def figure_courbe(titre: str, description: str, points: Sequence[Tuple[float, float]],
                  axes: Tuple[str, str], marqueurs: Sequence[Tuple[float, float, str]] = (),
                  ids: Tuple[str, str] = ("fig-t", "fig-d"),
                  largeur: int = 1120, hauteur: int = 430) -> str:
    """Courbe en L : x et y réels, axe ordonnées à droite, marqueurs annotés."""
    gauche, droite, bas_y, haut_y = 110, largeur - 60, hauteur - 60, 40
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys + [m[1] for m in marqueurs]), max(ys + [m[1] for m in marqueurs])
    if xmax - xmin <= 0:
        xmax = xmin + 1.0
    if ymax - ymin <= 0:
        ymax = ymin + 1.0
    sx = lambda v: gauche + (v - xmin) / (xmax - xmin) * (droite - gauche)  # noqa: E731
    sy = lambda v: bas_y - (v - ymin) / (ymax - ymin) * (bas_y - haut_y)    # noqa: E731
    pieces = [f"<rect x='0' y='0' width='{largeur}' height='{hauteur}' fill='#ffffff'/>"]
    for k in range(5):
        yy = haut_y + k * (bas_y - haut_y) / 4
        val = ymax - k * (ymax - ymin) / 4
        pieces.append(f"<line x1='{gauche}' y1='{yy:.1f}' x2='{droite}' y2='{yy:.1f}'"
                      f" stroke='#e2e9ef' stroke-width='1'/>")
        pieces.append(f"<text x='{gauche - 10}' y='{yy + 5:.1f}' text-anchor='end'"
                      f" font-family='Segoe UI,Arial' font-size='12' fill='#33475a'>"
                      f"{ech(_fmt(val))}</text>")
    chemin = " ".join(("M" if i == 0 else "L") + f"{sx(x):.1f} {sy(y):.1f}"
                      for i, (x, y) in enumerate(points))
    pieces.append(f"<path d='{chemin}' fill='none' stroke='#1f5f8b' stroke-width='2.4'/>")
    for x, y, nom in marqueurs:
        pieces.append(f"<circle cx='{sx(x):.1f}' cy='{sy(y):.1f}' r='6' fill='#ffffff'"
                      f" stroke='#0f3d5c' stroke-width='2.2'/>")
        pieces.append(f"<text x='{sx(x):.1f}' y='{sy(y) - 14:.1f}' text-anchor='middle'"
                      f" font-family='Segoe UI,Arial' font-size='13' fill='#0f3d5c'>"
                      f"{ech(nom)}</text>")
    pieces.append(f"<line x1='{gauche}' y1='{bas_y}' x2='{droite}' y2='{bas_y}'"
                  f" stroke='#5b6b7a' stroke-width='1.6'/>")
    pieces.append(f"<line x1='{gauche}' y1='{haut_y}' x2='{gauche}' y2='{bas_y}'"
                  f" stroke='#5b6b7a' stroke-width='1.6'/>")
    pieces.append(f"<text x='{(gauche + droite) / 2:.1f}' y='{hauteur - 18}'"
                  f" text-anchor='middle' font-family='Segoe UI,Arial' font-size='13'"
                  f" fill='#33475a'>{ech(axes[0])}</text>")
    return _svg(largeur, hauteur, titre, description, "".join(pieces), ids)


def _fmt(v: float) -> str:
    if v == 0:
        return "0"
    a = abs(v)
    if a >= 1e6 or a < 1e-3:
        return f"{v:.3e}"
    if a >= 100:
        return f"{v:,.0f}".replace(",", "\u202f")
    if a >= 1:
        return f"{v:.2f}".rstrip("0").rstrip(".")
    return f"{v:.4g}"


# ----------------------------------------------------------------------------
# écritures hors HTML
# ----------------------------------------------------------------------------
def ecrire_chemin(chemin: Path, texte: str) -> None:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(texte, encoding="utf-8", newline="\n")


def ecrire_svg(seul: str, chemin: Path) -> None:
    """SVG autonome : le même inline, avec l'attribut xmlns déjà présent."""
    ecrire_chemin(chemin, seul)


def ecrire_json(donnees: Dict[str, Any], chemin: Path) -> None:
    ecrire_chemin(chemin, json.dumps(donnees, ensure_ascii=False, indent=2, default=str))


def ecrire_csv(lignes: Sequence[Sequence[Any]], chemin: Path) -> None:
    """Excel français : BOM UTF-8 et séparateur point-virgule."""
    tampon = io.StringIO(newline="")
    ecrivain = csv.writer(tampon, delimiter=";", lineterminator="\r\n", quoting=csv.QUOTE_MINIMAL)
    for ligne in lignes:
        ecrivain.writerow(ligne)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text("\ufeff" + tampon.getvalue(), encoding="utf-8", newline="")


def _ligne_equation(e: Dict[str, Any]) -> Dict[str, Any]:
    return {"id": e["id"], "chemin": e["chemin"], "formule": e["formule"],
            "resultat": e["resultat"], "statut": e["statut"]}


def lignes_csv_equations(donnees: Dict[str, Any]) -> List[List[Any]]:
    entete = ["ID", "Titre", "Formule", "Ligne calculee", "Statut",
              "Chemin module -> fonction -> controle"]
    lignes = [entete]
    for e in donnees["equations"]:
        lignes.append([e["id"], e.get("_titre_fr", ""), e["formule"], e["resultat"],
                       e["statut"], e["chemin"]])
    lignes.append([])
    lignes.append(["CONTROLES", "Nom", "Attendu", "Obtenu", "Recoit", ""])
    for c in donnees["controles"]:
        lignes.append([c["id"], c["nom"], c["attendu"], c["obtenu"],
                       "OUI" if c["ok"] else "NON", ""])
    return lignes


def markdown(donnees: Dict[str, Any], spec: Dict[str, Any]) -> str:
    t = T["fr"]
    out: List[str] = [f"# {spec['theme']['fr']}", ""]
    out += [f"**Auteur** : {AUTEUR}  ",
            f"**Licence** : {LICENCE}  ",
            f"**Module** : `{spec['module']}` — "
            f"{donnees['resume']['equations']} équations, "
            f"{donnees['resume']['controles_ok']}/{donnees['resume']['controles_total']} "
            "contrôles reçus.", ""]
    out += ["## Chemin", ""]
    for etape in spec["cheminement"]:
        out += [f"### {etape['fr'][0]}", etape["fr"][1], ""]
    out += ["## Équations", ""]
    for e in donnees["equations"]:
        titre = e.get("_titre_fr", e["id"])
        out += [f"### {e['id']} — {titre}", "", f"`{e['formule']}`", "",
                f"> {e['resultat']}", "",
                f"*Statut* : {e['statut']} · *chemin* : `{e['chemin']}`", ""]
    out += ["## Contrôles numériques", "", "| ID | Contrôle | Attendu | Obtenu | État |",
            "|---|---|---|---|---|"]
    for c in donnees["controles"]:
        out += [f"| {c['id']} | {c['nom']} | {c['attendu']} | {c['obtenu']} | "
                f"{'reçu' if c['ok'] else 'manquant'} |"]
    out += ["", "## Source", "", "```",
            json.dumps(donnees["source"], ensure_ascii=False, indent=2, default=str), "```", ""]
    out += ["## Valeurs déclarées", "", "```",
            json.dumps(donnees.get("valeurs_declarees", donnees.get("materiaux_declares", {})),
                       ensure_ascii=False, indent=2, default=str),
            "```", ""]
    out += [f"> {t['pied']}", ""]
    return "\n".join(out)


# ----------------------------------------------------------------------------
# assemblage d'une page
# ----------------------------------------------------------------------------
def cle_eq(e: Dict[str, Any]) -> str:
    """Clé des tables de textes quand une page réunit deux modules.

    `EQ-01` désigne alors deux équations : la table est indexée par
    « DOSSIER/EQ-01 », et la page affiche le dossier sous l'identifiant. Une ligne
    qui ne porte pas de dossier garde l'identifiant seul — les pages mono-module
    restent inchangées.
    """
    return f"{e['dossier']}/{e['id']}" if e.get("dossier") else e["id"]


def marque_dossier(e: Dict[str, Any]) -> str:
    """Le dossier d'une ligne, sous son identifiant : `.chemin` est déjà le style d'une
    trace, il n'a pas besoin d'une seconde classe pour dire d'où vient la ligne."""
    d = e.get("dossier")
    return "" if not d else f"<br><span class=\"chemin\">{ech(d)}</span>"


def construire_page(spec: Dict[str, Any], donnees: Dict[str, Any], lang: str) -> str:
    t = T[lang]
    pool = pool_nombres(
        *[f"{e['formule']} {e['resultat']} {json.dumps(e['detail'], ensure_ascii=False, default=str)}"
          for e in donnees["equations"]],
        *[f"{c['attendu']} {c['obtenu']}" for c in donnees["controles"]],
        json.dumps(donnees.get("resume", {}), ensure_ascii=False, default=str),
        json.dumps(donnees.get("valeurs_declarees", {}), ensure_ascii=False, default=str),
        json.dumps(donnees.get("materiaux_declares", {}), ensure_ascii=False, default=str),
        json.dumps(donnees.get("invariants", {}), ensure_ascii=False, default=str),
    )
    textes_eq = spec["eq_text"]

    def eq_texte(e: Dict[str, Any], champ: int) -> str:
        trio = textes_eq[cle_eq(e)][lang]
        if champ == 0:
            return trio[0]
        if lang == "fr":
            return trio[1] if len(trio) > 1 and trio[1] else ""
        return trio[1]

    manquants: List[str] = []
    for e in donnees["equations"]:
        cle_txt = cle_eq(e)
        if cle_txt not in textes_eq:
            manquants.append(cle_txt + " (absent)")
            continue
        for code in ("en", "ar"):
            hors = verifier_nombres(textes_eq[cle_txt][code][1], pool)
            if hors:
                manquants.append(f"{cle_txt}[{code}] :" + ",".join(hors))
    if manquants:
        raise ValueError("textes hors pool numérique : " + " ; ".join(manquants))

    statuts = donnees["resume"]["statuts"]
    lib_s = lambda cle: STATUT_LIBELLE[lang].get(cle, cle)  # noqa: E731
    titre = spec["theme"][lang]
    description = spec["description"][lang]
    chemins = spec["chemins"]
    canonique = chemins[lang]

    Sommaire = "".join(
        f'<a href="#{an}">{ech(lib)}</a>' for an, lib in (
            ("cheminement", t["cheminement"]), ("equations", t["equations"]),
            ("controles", t["controles"]), ("resultats", t["resultats"]),
            ("materiaux", t["materiaux"]), ("sources", t["sources"]),
            ("reproduction", t["reproduction"])))
    tete_page = (f"<h1>{ech(titre)}</h1>"
                 f"<p>{ech(description)}</p>"
                 + badges([
                     (f"{donnees['resume']['equations']} EQ", False),
                     (f"{donnees['resume']['controles_ok']}/"
                      f"{donnees['resume']['controles_total']} {t['controles']}", True),
                     (f"{lib_s('OPÉRATIONNEL')} {statuts.get('OPÉRATIONNEL', 0)}", False),
                     (f"{lib_s('SIMULÉ')} {statuts.get('SIMULÉ', 0)}", False),
                     (f"{lib_s('SPÉCIFIÉ')} {statuts.get('SPÉCIFIÉ', 0)}", False),
                 ])
                 + f"<p class=\"chemin\">{ech(t['legende_statuts'])}</p>"
                 + f'<nav aria-label="{ech(t["nav_site"])}" class="sommaire">{Sommaire}</nav>')

    corps: List[str] = [tete_page]

    if spec.get("figures"):
        for fig in spec["figures"]:
            svg = fig["svg"][lang] if isinstance(fig["svg"], dict) else fig["svg"]
            corps.append(f"<figure>{svg}"
                         f"<figcaption>{ech(fig['legende'][lang])}</figcaption></figure>")

    corps.append(f"<h2 id=\"cheminement\">{ech(t['cheminement'])}</h2>")
    for etape in spec["cheminement"]:
        corps.append(f"<div class=\"etape\"><h3>{ech(etape[lang][0])}</h3>"
                     f"<p>{ech(etape[lang][1])}</p></div>")

    lignes_eq = []
    for e in donnees["equations"]:
        titre_eq = eq_texte(e, 0)
        ligne = e["resultat"] if lang == "fr" else eq_texte(e, 1)
        # Les nombres d'une ligne calculée ne se traduisent pas : sans eux, une page sur trois
        # seule porte la valeur vérifiable.
        calcul = ("" if lang == "fr"
                  else f"<br><span class=\"calcul\">{ech(e['resultat'])}</span>")
        cellule = (f"<span class=\"lecture\">{ech(ligne)}</span>{calcul}"
                   f"<br><span class=\"chemin\">{ech(e['chemin'])}</span>")
        if lang != "fr" and ech(e["resultat"]) not in cellule:
            raise ValueError(f"{cle_eq(e)} : ligne calculée absente de la page «{lang}»")
        lignes_eq.append([
            ech(e["id"]) + marque_dossier(e),
            f"<span class=\"titre\">{ech(titre_eq)}</span>",
            f"<span class=\"formule\">{ech(e['formule'])}</span>",
            cellule,
            f"<span class=\"statut {STATUT_CLASSE[e['statut']]}\">{ech(lib_s(e['statut']))}</span>",
        ])
    corps.append(f"<h2 id=\"equations\">{ech(t['equations'])}</h2>" + tableau(
        "eq", t["caption_eq"],
        [(t["col_id"], ""), (t["col_titre"], ""), (t["col_formule"], "formule"),
         (t["col_ligne"], ""), (t["col_statut"], "")], lignes_eq))

    lignes_ctrl = []
    for c in donnees["controles"]:
        lignes_ctrl.append([ech(c["id"]) + marque_dossier(c),
                            f"<span class=\"titre\">{ech(c['nom'])}</span>",
                            f"<span class=\"nb\">{ech(c['attendu'])}</span>",
                            f"<span class=\"nb\">{ech(c['obtenu'])}</span>",
                            f"<span class=\"statut {'o' if c['ok'] else 'p'}\">"
                            f"{ech(t['ok'] if c['ok'] else t['ko'])}</span>"])
    corps.append(f"<h2 id=\"controles\">{ech(t['controles'])}</h2>" + tableau(
        "ctrl", t["caption_ctrl"],
        [(t["col_id"], ""), (t["col_controle"], ""), (t["col_attendu"], "nb"),
         (t["col_obtenu"], "nb"), (t["col_ok"], "")], lignes_ctrl))

    if spec.get("resultats"):
        cartes = "".join(
            f"<div class=\"carte\"><div class=\"gros\">{ech(v[lang])}</div>"
            f"<h3>{ech(lab[lang])}</h3><p>{ech(not_[lang])}</p></div>"
            for lab, v, not_ in spec["resultats"])
        corps.append(f"<h2 id=\"resultats\">{ech(t['resultats'])}</h2>"
                     f"<p>{ech(t['caption_resultats'])}</p>"
                     f"<div class=\"grille\">{cartes}</div>")

    if spec.get("materiaux"):
        lignes_m = []
        for m in spec["materiaux"]:
            q = m["quantite"]
            q = q[lang] if isinstance(q, dict) else _fmt(float(q))
            eq_src = m["equation"]
            eq_src = eq_src[lang] if isinstance(eq_src, dict) else eq_src
            lignes_m.append([ech(m["id"]),
                             f"<span class=\"titre\">{ech(m['nom'][lang])}</span>",
                             f"<span class=\"nb\">{ech(q)} {ech(m['unite'][lang])}</span>",
                             f"<span class=\"nb\">{ech(eq_src)}</span>"])
        corps.append(f"<h2 id=\"materiaux\">{ech(t['materiaux'])}</h2>" + tableau(
            "mat", spec["caption_materiaux"][lang],
            [(t["col_id"], ""), (t["col_matiere"], ""), (t["col_quantite"], "nb"),
             (t["col_equation"], "nb")], lignes_m))

    predecesseurs = [p.strip() for p in re.split("→|->", spec["fil_conducteur"]) if p.strip()]
    liste = "".join(f"<li>{ech(p)}</li>" for p in predecesseurs)
    corps.append(f"<h2 id=\"sources\">{ech(t['sources'])}</h2>"
                 f"<p>{ech(spec['sources'][lang])}</p>"
                 f"<ul>{liste}</ul>")

    corps.append(f"<h2 id=\"reproduction\">{ech(t['reproduction'])}</h2>"
                 f"<pre>{ech(spec['commandes'][lang])}</pre>")

    actions = "".join(
        f"<a class=\"principal\" href=\"{ech(spec['index_href'])}\">{ech(spec['index_libelle'][lang])}</a>"
        + "".join(f"<a href=\"{ech(l['href'])}\">{ech(l['libelle'][lang])}</a>"
                  for l in spec.get("liens", [])))
    corps.append(f"<div class=\"actions\">{actions}</div>")

    nav_bas = en_tete(t, lang, spec["chapitres_nav"], spec["titre_bande"][lang])
    queue = (f"<footer class=\"site\"><div class=\"interieur\">"
             f"<p>{ech(t['pied'])}</p>"
             f"<p>{ech(AUTEUR)} · {ech(LICENCE)} · {ech(spec['doi'])}</p>"
             f"</div></footer>")
    return (tete(t, f"{titre} — AL-MIZAN × ASTRO-Q°ODE", description, chemins, canonique)
            + "\n<body>" + nav_bas
            + "\n<main id=\"contenu\" tabindex=\"-1\">" + "".join(corps) + "</main>"
            + queue + "\n</body>\n</html>\n")


__all__ = ["LANGUES", "AUTEUR", "LICENCE", "T", "CSS", "ech", "nombres",
           "verifier_nombres", "figure_barres", "figure_baril", "figure_courbe",
           "construire_page", "ecrire_chemin", "ecrire_json", "ecrire_csv",
           "ecrire_svg", "markdown", "lignes_csv_equations", "_fmt",
           "cle_eq", "marque_dossier"]
