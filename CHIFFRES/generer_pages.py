# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""Générateur des pages trilingues du dossier CHIFFRES.

`chiffres_pi.py` calcule ; ce fichier met en forme. Aucune équation n'est ajoutée ici,
aucun nombre n'y est recomposé : chaque valeur imprimée en français, en anglais ou en
arabe est relue dans le dictionnaire rendu par `resoudre()` sur le domaine publié
(`N_PAGE = 1 000 000`). Le moteur `ABONDANCE/moteur_page_trilingue.py` refuse ensuite
toute phrase anglaise ou arabe énonçant un chiffre absent des lignes calculées.

Le générateur compare en outre ses dix-sept lignes françaises à celles de
`artefacts/etat.json` : si le domaine scellé et la page divergeaient, la page n'est
pas publiée.

Formats produits dans `CHIFFRES/artefacts/` :
    pages/chiffres[_en|_ar].html   trois pages, sans JavaScript
    figures/chiffres[_en|_ar].svg  une figure calculée (χ²(9) par constante, plafond déclaré)
    donnees/chiffres.json          le dictionnaire complet rendu au moteur
    donnees/chiffres.csv           équations + contrôles, Excel français (BOM, « ; »)
    donnees/etat_generateur.json   compteurs et liste des artefacts écrits
    dossiers/chiffres.md           dossier markdown

Honnêteté du contenu : la vidéo Euclidea M90ZAVojI30 ne rend pas de transcript (timedtext
0 octet). Ses dix chapitres horodatés sont repris tels quels, avec leur titre anglais et
leur `debut` ; aucune phrase ne lui est attribuée, aucun chiffre n'en vient. Le dossier
ne prouve la normalité d'aucune constante : il confronte des lois calculées à des mesures
sur un domaine fini déclaré avant la mesure.

Usage :
    py -3 CHIFFRES/generer_pages.py
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Sequence

RACINE = Path(__file__).resolve().parent
DEPOT = RACINE.parent
for _chemin in (str(RACINE), str(DEPOT / "ABONDANCE")):
    if _chemin not in sys.path:
        sys.path.insert(0, _chemin)

import chiffres_pi as CP                       # noqa: E402
import generer_chiffres as GEN                 # noqa: E402
import moteur_page_trilingue as MOTEUR         # noqa: E402

ARTEFACTS = RACINE / "artefacts"
DOI_CONCEPT = "https://doi.org/10.5281/zenodo.24028242"
DEPOT_GITHUB = "https://github.com/IMAM8MAHDI/AL-MIZAN-Quantum-Emulator"
N_PAGE = 1_000_000
COULEURS = {"pi": "#1f5f8b", "e": "#166534", "racine2": "#b45309"}

# ============================================================================
# Textes par équation et par langue
# ----------------------------------------------------------------------------
# Structure : {"EQ-nn": {"fr": [titre, ""], "en": [titre, ligne], "ar": [titre, ligne]}}.
# Le français ne porte que le titre : la ligne lue reste la `resultat` calculée du
# module. Les lignes anglaise et arabe sont passées au garde-fou numérique du moteur :
# elles ne reprennent que des nombres tels qu'ils apparaissent dans les lignes
# calculées du domaine publié — même notation, même décimale, aucune conversion.
# ============================================================================
EQ_TEXT: Dict[str, Dict[str, List[str]]] = {
    "EQ-01": {
        "fr": ["π certifié par splitting binaire de Chudnovsky", ""],
        "en": ["π certified by Chudnovsky's binary splitting",
               "One integer certificate, no rounding: the enclosure is computed at both "
               "bounds, so the chain holds 1000000 certified decimals taken from 71434 terms, "
               "and 40 guard digits remain free once the width of the enclosure is subtracted."],
        "ar": ["π مُصدَّق عليه بالتجزئة الثنائية لشدنوفسكي",
               "شهادةٌ صحيحة واحدة بلا تقريب: تُحسب الإحاطة عند الطرفين، فتعطي السلسلةُ "
               "1000000 خانةٍ عشريةٍ مُصدَّقٍ عليها من 71434 حدًّا، ويبقى 40 خانةً احتياطيةً "
               "حرةً بعد طرح سعة الإحاطة."]},
    "EQ-02": {
        "fr": ["Seconde voie pour π : la formule de Machin", ""],
        "en": ["A second path for π: Machin's formula",
               "The independent rational path meets the first one digit for digit over 500 "
               "digits, and the first disagreement is None — the generator does not drift from "
               "one decimal to the next."],
        "ar": ["طريقٌ ثانية لـ π: صيغة ماشان",
               "تلتقي الطريقُ المستقلة الثانية بالطريقِ الأولى خانةً بخانة على 500 خانة، وأولُ "
               "اختلاق بينهما هو None — أي أن المولّد لا ينحرف من خانةٍ إلى التي تليها."]},
    "EQ-03": {
        "fr": ["e certifié par la série des inverses de factorielles", ""],
        "en": ["e certified by the series of inverse factorials",
               "The tail is bounded by an integer inequality: 1000000 certified decimals with "
               "m = 205029, and the identity Q = m! is verified again in integers — True."],
        "ar": ["e مُصدَّقٌ عليه بسلسلة مقلوبات المضروب",
               "يُحَدُّ الذيلُ بمتراجحةٍ صحيحة: 1000000 خانةٍ عشريةٍ مُصدَّقٍ عليها حيث "
               "m = 205029، ويُتحقَّق من المساواة Q = m! من جديد في الأعداد الصحيحة، وهي True."]},
    "EQ-04": {
        "fr": ["√2 par une seule inégalité entière", ""],
        "en": ["√2 by a single integer inequality",
               "No series is borrowed: w = ⌊√2·10ⁿ⌋ is put to the test w² ≤ 2·10²ⁿ < (w+1)², "
               "which gives 1000000 decimals with preuve True, and Newton's path on fixed "
               "integers answers True as well."],
        "ar": ["√2 بمتراجحةٍ صحيحةٍ واحدة",
               "لا تُستعار أيُّ سلسلة: يُمحَّص w = ⌊√2·10ⁿ⌋ بالمتراجحة w² ≤ 2·10²ⁿ < (w+1)²، "
               "فتعطي 1000000 خانةٍ عشريةً والإثبات True، وطريقُ نيوتن على الأعداد الصحيحة "
               "الثابتة يعطي True كذلك."]},
    "EQ-05": {
        "fr": ["Une convention d'indexage, assumée et écrite", ""],
        "en": ["An indexing convention, assumed and written down",
               "Position 1 is the first decimal, and that digit of π is 1. Under this "
               "convention 16470 is self-localised — True — while the other convention shifts "
               "every position by exactly 1."],
        "ar": ["اصطلاحٌ للترقيم، مفترضٌ ومكتوب",
               "الموضعُ 1 هو أولُ خانةٍ عشرية، ورقمُ π في ذلك الموضع هو 1. وبموجب هذا الاصطلاح "
               "يكون 16470 متموضعًا في ذاته — True — بينما يُزحزح الاصطلاحُ الآخر كلَّ موضعٍ "
               "بمقدار 1 بالضبط."]},
    "EQ-06": {
        "fr": ["H0 posée, et 108 cellules closes avant la mesure", ""],
        "en": ["H0 set, and 108 cells closed before the read",
               "The null model declares the decimals independent and uniform on {0,…,9}; the "
               "rejection threshold is ALPHA = 0.001, that is z beyond 3.290527, and the whole "
               "grid holds 108 cells, which expect 0.108 exclusion."],
        "ar": ["الفرضية الصفرية H0 و 108 خليةً مُغلقةً قبل القراءة",
               "يُعلن النموذجُ الصفرية أن الخانات مستقلةٌ ومتماثلةٌ على {0,…,9}، وحدُّ الرفض هو "
               "ALPHA = 0.001 أي z يتجاوز 3.290527، والشبكةُ كلُّها تحمل 108 خليةً تنتظر "
               "0.108 استبعادًا."]},
    "EQ-07": {
        "fr": ["Dix chiffres comptés, un χ² lu dans un intervalle", ""],
        "en": ["Ten digits counted, one χ² read inside an interval",
               "Over the ten digit classes the statistic is 5.5091 for π, 9.5057 for e and "
               "16.6573 for √2, all three inside [0.866, 29.914]. Staying inside bounds a "
               "rejection; it never proves uniformity."],
        "ar": ["عشرُ خاناتٍ معدودة، وكي² تُقرأ داخل مجال",
               "على فئاتِ الخانات العشر تبلغ الإحصاءُ 5.5091 لـ π و 9.5057 لـ e و 16.6573 لـ √2، "
               "وهي جميعًا داخل المجال من 0.866 إلى 29.914. البقاءُ داخل الحدود يحدّ من الرفض، "
               "ولا يُثبت التماثل أبدًا."]},
    "EQ-08": {
        "fr": ["Une régularité exacte : 9/10, classe après classe", ""],
        "en": ["One exact regularity: 9/10, class after class",
               "In exact fractions, for every class k = 1..20 the expected count of "
               "self-localised positions is 9/10 — nine candidates per ten, times one tenth. "
               "The identity belongs to the model, not to the digits of π."],
        "ar": ["انتظامٌ تام: 9/10، فئةً بعد فئة",
               "بكسورٍ تامة، لكلِّ فئة k = 1..20 يكون العددُ المتوقع للمواضع المتموضعةِ في ذاتها "
               "هو 9/10 — تسعةُ مرشحين من عشرة مضروبةً في عُشر. هذه المطابقةُ ملكُ النموذج لا "
               "خاناتِ π."]},
    "EQ-09": {
        "fr": ["Les positions qui s'écrivent à leur propre place", ""],
        "en": ["Positions that write themselves at their own place",
               "The first of them is 1, and inside the published chain π keeps 3 such positions, "
               "16470 among them. The count is read off the digits the module produced, never "
               "off a screenshot."],
        "ar": ["مواضعَ تكتبُ نفسها في موضعها",
               "أولُها الموضعُ 1، ويحتفظ π داخل السلسلة المنشورة بـ 3 من هذه المواضع، منها "
               "16470. العددُ مقروءٌ من الخانات التي ولّدتها الوحدة، لا من لقطةِ شاشة."]},
    "EQ-10": {
        "fr": ["Comptes par classe de longueur, sous loi de Poisson", ""],
        "en": ["Counts per length class, under a Poisson law",
               "For each class the obtained count is compared with the Poisson interval declared "
               "for it before the read; every class of π stays inside its own interval."],
        "ar": ["أعدادٌ بحسب فئات الأطوال تحت قانون بواسون",
               "يُقارن العددُ المحصول عليه في كلِّ فئةٍ بمجال بواسون المعلَن لها قبل القراءة، "
               "وكلُّ فئةٍ من فئات π يبقى داخل مجالها الخاص."]},
    "EQ-11": {
        "fr": ["Une courbe cumulative, un seuil de Bonferroni", ""],
        "en": ["A cumulative curve, a Bonferroni threshold",
               "The running total is read on 10 declared points; the largest |z| against the "
               "analytic curve is 1.842, below the Bonferroni threshold of 4.149 that the "
               "multiplicity of those 10 points alone requires."],
        "ar": ["منحنًى تراكميٌّ وحدُّ بونفيروني",
               "يُقرأ المجموعُ الجاري على 10 نقاطٍ معلَنة، وأكبرُ قيمةٍ لـ |z| مقابل المنحنى "
               "التحليلي هي 1.842، أي أدنى من حدّ بونفيروني 4.149 الذي تقتضيه تعدديةُ تلك النقاط "
               "العشر وحدها."]},
    "EQ-12": {
        "fr": ["Trois voies de comptage sur une graine déclarée", ""],
        "en": ["Three counting paths on a declared seed",
               "Analytic, Monte-Carlo and direct sweep are run again on the declared domain "
               "n_sim = 100000: the simulation gives 4.650 with an uncertainty of 2.102 against "
               "the analytic 4.500. The draw tests the chain of expectations, not the digits."],
        "ar": ["ثلاثةُ مساراتٍ للعدّ على بذرةٍ معلَنة",
               "أُعيد تشغيلُ التحليل ومونت كارلو والمسحَ المباشر على المجال المعلَن "
               "n_sim = 100000: تعطي المحاكاةُ 4.650 بتماميةِ 2.102 مقابل التحليلي 4.500. "
               "القرعةُ تختبر سلسلةَ التوقعات لا الخانات."]},
    "EQ-13": {
        "fr": ["Runs de chiffres identiques, compte sur compte", ""],
        "en": ["Runs of identical digits, count against count",
               "The observed number of runs of each length is set beside the expectation of the "
               "independent model, from a run of 1 digit up to a run of 7, on the chain of "
               "1000000 decimals. Coincidence here measures the domain, nothing more."],
        "ar": ["سلاسلُ خاناتٍ متماثلة، عددٌ مقابل عدد",
               "يوضع العددُ المرصود لكلِّ طولٍ من سلاسل التكرار إلى جانب توقعِ النموذج المستقل، "
               "من سلسلةٍ من 1 خانةٍ إلى سلسلةٍ من 7، على سلسلةِ 1000000 خانةٍ عشرية. التطابقُ "
               "هنا يقيس المجالَ لا أكثر."]},
    "EQ-14": {
        "fr": ["Occulence : tout mot court apparaît, sur ce domaine", ""],
        "en": ["Occupancy: every short word shows up, on this domain",
               "π returns 10 distinct blocks out of 10 at k = 1 and 631548 out of the 632119 "
               "expected at k = 6. Counting what a finite window contains says nothing about "
               "what lies beyond it."],
        "ar": ["الإشغال: كلُّ كلمةٍ قصيرة تظهر، داخل هذا المجال",
               "يعطي π العددَ 10 من 10 كتلةً متمايزة عند k = 1، ثم 631548 من 632119 المتوقعة عند "
               "k = 6. عدُّ ما يحويه مجالٌ منتهٍ لا يقول شيئًا عمّا وراءه."]},
    "EQ-15": {
        "fr": ["Cinq sondes déclarées, lues avant tout commentaire", ""],
        "en": ["Five declared probes, read before any comment",
               "On π the five declared probes answer 12345 at 49702, 54321 at 64224, 00000 at "
               "17534 and 999999 at 762, while 0123456789 is still None inside the domain. No "
               "probe was chosen after seeing the digits."],
        "ar": ["خمسةُ مجساتٍ معلَنة، تُقرأ قبل أيّ تعليق",
               "على π تُجيب المجساتُ الخمسة المعلَنة هكذا: 12345 عند 49702، و 54321 عند 64224، و "
               "00000 عند 17534، و 999999 عند 762، بينما تبقى 0123456789 بلا ظهورٍ أي None داخل "
               "المجال. لم يُخترَ أيُّ مجسٍّ بعد رؤية الخانات."]},
    "EQ-16": {
        "fr": ["Une déiance sommée sur les trois constantes", ""],
        "en": ["A deviance pooled over the three constants",
               "The pooled deviance is G² = 21.036 on 18 degrees of freedom, inside "
               "[4.33, 44.61], so the verdict is CONTENU. An interval is a bound on rejection, "
               "not a certificate of normality."],
        "ar": ["انحرافٌ مجموعٌ على الثوابت الثلاثة",
               "الانحرافُ المجموع هو G² = 21.036 على 18 درجةَ حرية، داخل المجال من 4.33 إلى "
               "44.61، فالحكمُ هو CONTENU. المجالُ حدٌّ للرفض، لا شهادةٌ بالطبيعية"]},
    "EQ-17": {
        "fr": ["Un verdict borné : CONTENU, et rien de plus", ""],
        "en": ["A bounded verdict: CONTENU, and nothing more",
               "One cell is excluded out of 108 against 0.11 expected, with a global p of "
               "0.2047, so the domain is CONTENU. A failure here would have proved nothing; "
               "this agreement proves nothing either."],
        "ar": ["حكمٌ محدود: CONTENU، ولا شيء أكثر",
               "استُبعدت خليةٌ واحدة من 108 مقابل المتوقع 0.11، والقيمةُ العامةُ لـ p هي 0.2047، "
               "فالمجالُ إذن CONTENU. كان الفشلُ هنا لن يُثبت شيئًا، وهذا الاتفاقُ لا يُثبت "
               "شيئًا هو أيضًا."]},
}

# ============================================================================
# Colonne « formule » : seuls les qualificatifs français sont traduits.
# Les identifiants (λ_k, KMAX, MT19937, Wilson–Hilferty) restent tels quels.
# ============================================================================
FORMULE_TR: Dict[str, Dict[str, str]] = {
    "π = 426880·√10005 / Σ(−1)ᵏ(6k)!(A+Bk)/((3k)!(k!)³C³), splitting binaire": {
        "en": "π = 426880·√10005 / Σ(−1)ᵏ(6k)!(A+Bk)/((3k)!(k!)³C³), binary splitting",
        "ar": "π = 426880·√10005 / Σ(−1)ᵏ(6k)!(A+Bk)/((3k)!(k!)³C³)، بالتجزئة الثنائية"},
    "π = 16·arccot 5 − 4·arccot 239 (Machin 1706), bornes alternées": {
        "en": "π = 16·arccot 5 − 4·arccot 239 (Machin 1706), alternating bounds",
        "ar": "π = 16·arccot 5 − 4·arccot 239 (‏Machin 1706)، بحدودٍ متناوبة"},
    "e = Σ 1/k!, queue < 1/(m·m!) avec m·m! > 10^(n+40)": {
        "en": "e = Σ 1/k!, tail < 1/(m·m!) with m·m! > 10^(n+40)",
        "ar": "e = Σ 1/k!، بذيلٍ أصغر من 1/(m·m!) حيث m·m! > 10^(n+40)"},
    "w = ⌊√2·10ⁿ⌋ éprouvé par w² ≤ 2·10²ⁿ < (w+1)²": {
        "en": "w = ⌊√2·10ⁿ⌋ put to the test by w² ≤ 2·10²ⁿ < (w+1)²",
        "ar": "w = ⌊√2·10ⁿ⌋ يُمحَّص بـ w² ≤ 2·10²ⁿ < (w+1)²"},
    "position 1 = première décimale ; l'autre convention décale de 1": {
        "en": "position 1 = first decimal ; the other convention shifts by 1",
        "ar": "الموضع 1 = أول خانة عشرية ؛ الاصطلاحُ الآخر يُزحزح بمقدار 1"},
    "H0 : décimales i.i.d. uniformes sur {0,…,9}": {
        "en": "H0 : i.i.d. decimals, uniform on {0,…,9}",
        "ar": "H0 : خاناتٌ مستقلةٌ متماثلة التوزيع على {0,…,9}"},
    "E[compte] = n/10, σ = √(0,09n), χ²(9) : 9 ± √18, intervalle Wilson–Hilferty": {
        "en": "E[count] = n/10, σ = √(0.09n), χ²(9) : 9 ± √18, Wilson–Hilferty interval",
        "ar": "E[compte] = n/10، σ = √(0.09n)، χ²(9) : 9 ± √18، مجال Wilson–Hilferty"},
    "λ_k = 9·10^(k−1) · 10^(−k) = 9/10": {
        "en": "λ_k = 9·10^(k−1) · 10^(−k) = 9/10",
        "ar": "λ_k = 9·10^(k−1) · 10^(−k) = 9/10"},
    "p tel que la lecture en p redonne p": {
        "en": "p such that reading at p returns p",
        "ar": "p بحيث تُعيد القراءةُ عند p نفسَ p"},
    "compte par classe de longueur, Poisson(λ_k) indépendante du nombre de chiffres": {
        "en": "count per length class, Poisson(λ_k) independent of the number of digits",
        "ar": "عدٌّ بحسب فئة الطول، Poisson(λ_k) مستقلٌّ عن عدد الخانات"},
    "E[N(x)] = Σ_{k'<k}λ_k' + (x − 10^(k−1) + 1)·10^(−k)": {
        "en": "E[N(x)] = Σ_{k'<k}λ_k' + (x − 10^(k−1) + 1)·10^(−k)",
        "ar": "E[N(x)] = Σ_{k'<k}λ_k' + (x − 10^(k−1) + 1)·10^(−k)"},
    "analytique / Monte-Carlo (MT19937, graine déclarée) / balayage direct": {
        "en": "analytic / Monte-Carlo (MT19937, declared seed) / direct sweep",
        "ar": "تحليلي / مونت كارلو (‏MT19937 ببذرةٍ معلَنة) / مسحٌ مباشر"},
    "E[run de longueur r] = (n−r−1)·0,81·10^(−(r−1)) + 1,8·10^(−(r−1))": {
        "en": "E[run of length r] = (n−r−1)·0.81·10^(−(r−1)) + 1.8·10^(−(r−1))",
        "ar": "E[run of length r] = (n−r−1)·0.81·10^(−(r−1)) + 1.8·10^(−(r−1))"},
    "E[k-présentes] = 10^k·(1 − (1 − 10^(−k))^m)": {
        "en": "E[k present] = 10^k·(1 − (1 − 10^(−k))^m)",
        "ar": "E[k présent] = 10^k·(1 − (1 − 10^(−k))^m)"},
    "T ~ géométrique(10^(−L)) ; u = P(T ≤ t) doit suivre une uniforme": {
        "en": "T ~ geometric(10^(−L)) ; u = P(T ≤ t) must follow a uniform law",
        "ar": "T ~ هندسية(10^(−L)) ؛ يجب أن تتبع u = P(T ≤ t) قانونًا منتظمًا"},
    "G² = 2Σ[x·ln(x/λ) + λ − x] ~ χ²(3·KMAX)": {
        "en": "G² = 2Σ[x·ln(x/λ) + λ − x] ~ χ²(3·KMAX)",
        "ar": "G² = 2Σ[x·ln(x/λ) + λ − x] ~ χ²(3·KMAX)"},
    "rejet si p < 0.001 ; global : Poisson(α·cellules) sur le nombre d'exclusions": {
        "en": "reject if p < 0.001 ; global : Poisson(α·cells) on the number of exclusions",
        "ar": "الرفضُ إذا p < 0.001 ؛ وعلى المستوى العام Poisson(α·cellules) في عدد الاستبعادات"},
}

# ============================================================================
# Cheminement — six étapes, mêmes nombres que les lignes calculées
# ============================================================================
CHEMINEMENT: List[Dict[str, List[str]]] = [
    {"fr": ["La source mesurée, et ce qu'elle ne donne pas",
            "Le point de départ est une page YouTube mesurée octet pour octet, citée comme une "
            "référence bibliographique : « What Is Actually Hiding in the Digits of Pi? » "
            "(chaîne Euclidea, identifiant M90ZAVojI30, durée déclarée 854 s). Elle rend dix "
            "chapitres horodatés, mais timedtext renvoie 0 octet en json3, srv3 et xml : le "
            "transcript est tenu pour absent. Le dossier n'en tire aucune citation, aucun "
            "chiffre, aucune méthode ; il en retient dix thèmes, chacun rattaché à une "
            "équation."],
     "en": ["The measured source, and what it does not give",
            "The starting point is a YouTube page measured byte for byte, cited as a "
            "bibliographic reference: “What Is Actually Hiding in the Digits of Pi?” (Euclidea "
            "channel, id M90ZAVojI30, declared length 854 s). It serves ten dated chapters, but "
            "timedtext returns 0 bytes in json3, srv3 and xml: the transcript is held to be "
            "absent. The dossier takes no quotation, no number and no method from it; it keeps "
            "ten themes, each attached to one equation."],
     "ar": ["المصدرُ المقيس وما لا يعطيه",
            "نقطةُ البداية صفحةُ يوتيوب قِيست بايتً ببايت، تُذكر كمرجعٍ ببليوغرافي: « What Is "
            "Actually Hiding in the Digits of Pi? » (قناة Euclidea، المعرّف M90ZAVojI30، المدّة "
            "المعلَنة 854 s). تنشر الصفحةُ عشرةَ فصولٍ مؤرَّخة، لكن timedtext ترجع بصفر بايت في "
            "json3 و srv3 و xml: فالنصّ المكتوب معدوم. لا يأخذ الملفُ منها اقتباسًا ولا رقمًا ولا "
            "طريقة، وإنما يحفظ عشرةَ مواضيع، كلُّ واحدةٍ منها مربوطةٌ بمعادلة."]},
    {"fr": ["Le domaine est clos avant la mesure",
            "n = 1000000 chiffres par constante, KMAX = 6 classes, RMAX = 7 longueurs de runs, "
            "ALPHA = 0.001, GRAINE = 20261109, PAS_CUMUL = 10, cinq sondes de recherche : tout "
            "est écrit dans le module avant que la moindre décimale ne soit produite. Les 108 "
            "cellules de la confrontation sont énumérées par `predire(n)`, qui ne lit aucun "
            "chiffre."],
     "en": ["The domain is closed before the read",
            "n = 1000000 digits per constant, KMAX = 6 classes, RMAX = 7 run lengths, "
            "ALPHA = 0.001, GRAINE = 20261109, PAS_CUMUL = 10, five search probes: every one of "
            "these is written in the module before a single decimal is produced. The 108 cells "
            "of the confrontation are enumerated by `predire(n)`, which reads no digit at all."],
     "ar": ["المجالُ مُغلَقٌ قبل القراءة",
            "n = 1000000 خانةٍ لكلِّ ثابتة، و KMAX = 6 فئات، و RMAX = 7 أطوالٍ للسلاسل، و "
            "ALPHA = 0.001، و GRAINE = 20261109، و PAS_CUMUL = 10، خمسةُ مجسات بحث: كلُّ ذلك "
            "مكتوبٌ في الوحدة قبل إنتاج أيِّ خانةٍ عشرية. والخلايا الـ 108 للمواجهة تُعدِّدُها "
            "الدالةُ `predire(n)` التي لا تقرأ أيَّ خانة."]},
    {"fr": ["Les décimales viennent d'un certificat, pas d'un arrondi",
            "Chaque voie principale rend un encadrement exact aux deux bornes et vérifie que "
            "les deux bornes ont la même partie entière à l'échelle demandée : les chiffres sont "
            "forcés. Le module porte même une correction consignée — la constante d'ancre de √2 "
            "avait été recopiée fausse, divergeant au 38ᵉ chiffre ; rien ne la confrontait, "
            "désormais C01 le fait."],
     "en": ["The decimals come from a certificate, not from rounding",
            "Each main path computes an exact enclosure at both bounds and checks that the two "
            "bounds share the same integer part at the requested scale: the digits are forced. "
            "The module even records one real correction — the anchor constant for √2 had been "
            "copied wrong, diverging at the 38th digit, and nothing confronted it; C01 does now."],
     "ar": ["الخاناتُ تأتي من شهادةٍ لا من تقريب",
            "تحسبُ كلُّ طريقٍ رئيسية إحاطةً تامةً عند الطرفين وتتأكد أن الطرفين لهما الجزءُ "
            "الصحيحُ نفسُه على المقياس المطلوب: فتُفرَض الخاناتُ فرضًا. ويحمل الملفُ حتى تصحيحًا "
            "موثَّقًا — فقد كانت ثابتةُ الإرساء الخاصة بـ √2 منسوخةً خطأً، وتنفصل عند الخانة الـ "
            "38، ولم يكن شيءٌ يواجهها، أما الآن فيفعل C01 ذلك."]},
    {"fr": ["Deux voies indépendantes se recoupent",
            "Chudnovsky contre Machin pour π, la série des factorielles contre la somme terme à "
            "terme pour e, la racine carrée entière contre Newton pour √2. L'accord chiffre à "
            "chiffre atteste que le générateur ne dérive pas ; il n'ajoute rien de neuf sur les "
            "constantes elles-mêmes."],
     "en": ["Two independent paths are crossed",
            "Chudnovsky against Machin for π, the factorial series against the term-by-term sum "
            "for e, the integer square root against Newton for √2. Agreement digit for digit "
            "testifies that the generator does not drift; it adds nothing new about the "
            "constants themselves."],
     "ar": ["طريقان مستقلان يتقاطعان",
            "شدنوفسكي مقابل ماشان لـ π، وسلسلةُ المضروب مقابل الجمع حدًّا حدًّا لـ e، والجذرُ "
            "التربيعي الصحيح مقابل نيوتن لـ √2. الاتفاقُ خانةً بخانة يشهد أن المولّد لا ينحرف، "
            "ولا يضيف شيئًا جديدًا عن الثوابت ذاتها."]},
    {"fr": ["La confrontation borne le rejet, elle ne prouve pas",
            "108 cellules, un seuil bilatère de 0.001 déclaré d'avance, une déiance sommée sur "
            "18 degrés de liberté et un verdict global Poisson sur le nombre d'exclusions. Une "
            "cellule est exclue sur 108, là où 0.108 étaient attendues, p = 0.2047 : CONTENU. Ce "
            "résultat ne dit pas que π est normal ; il dit que, sur ce domaine, rien ne force à "
            "le traiter autrement qu'une suite uniforme."],
     "en": ["The confrontation bounds rejection, it does not prove",
            "108 cells, a two-sided threshold of 0.001 declared in advance, a deviance pooled "
            "over 18 degrees of freedom and a global Poisson verdict on the number of "
            "exclusions. One cell is excluded out of 108 where 0.108 were expected, with "
            "p = 0.2047: CONTENU. This does not say π is normal; on this domain it says nothing "
            "forces us to treat it as anything but a uniform sequence."],
     "ar": ["المواجهةُ تُحدُّ من الرفض ولا تُثبت",
            "108 خليةً، وحدٌّ ثنائيٌّ مقداره 0.001 معلَنٌ مسبقًا، وانحرافٌ مجموعٌ على 18 درجةَ "
            "حرية، وحكمٌ عام بواسوني على عدد الاستبعادات. استُبعدت خليةٌ واحدة من 108 حيث كانت "
            "المتوقعةُ 0.108، بـ p = 0.2047: فالنتيجة CONTENU. لا يقول هذا إن π عددٌ طبيعي "
            "التوزيع، بل يقول إن شيئًا على هذا المجال لا يُجبرنا على معاملته بغير معاملة سلسلة "
            "منتظمة."]},
    {"fr": ["La limite est écrite dans le module",
            "`EQ-17` ne porte pas la mention « preuve » : le statut de tout ce dossier est une "
            "confrontation sur domaine fini. La normalité simple de π, e et √2 reste ouverte "
            "depuis Borel 1909 ; aucune des lignes calculées ici ne s'avance au-delà du domaine "
            "déclaré, et le dernier chapitre de la vidéo, « A pattern nobody has proven », est "
            "pris au mot."],
     "en": ["The bound is written in the module",
            "`EQ-17` carries no word “proof”: the status of this whole dossier is a "
            "confrontation over a finite domain. Simple normality of π, e and √2 has remained "
            "open since Borel 1909; not one computed line here steps outside the declared "
            "domain, and the last chapter of the video, “A pattern nobody has proven”, is taken "
            "at its word."],
     "ar": ["الحَدُّ مكتوبٌ في الوحدة",
            "لا تحمل المعادلةُ `EQ-17` لفظَ «برهان»: فمقامُ هذا الملف كلِّه مواجهةٌ على مجالٍ "
            "منتهٍ. طبيعيةُ π وe و√2 ما زالت مسألةً مفتوحة منذ Borel عام 1909، ولا سطرٌ محسوبٌ "
            "هنا يتجاوز المجالَ المعلَن، والفصلُ الأخير من الفيديو « A pattern nobody has proven » "
            "يُؤخَذ على وجهه."]},
]

# ============================================================================
# Valeurs déclarées (matériaux du dossier)
# ============================================================================
DECLAREES: List[Dict[str, Any]] = [
    {"id": "n", "nom": ("Domaine publié", "Published domain", "المجال المنشور"),
     "unite": ("chiffres par constante", "digits per constant", "خانةً لكل ثابت"),
     "valeur": float(N_PAGE), "equation": "EQ-01, EQ-03, EQ-04"},
    {"id": "GARDE", "nom": ("Chiffres de garde", "Guard digits", "خاناتٌ احتياطية"),
     "unite": ("chiffres", "digits", "خانة"),
     "valeur": float(GEN.GARDE), "equation": "EQ-01, EQ-03"},
    {"id": "A_CHUD", "nom": ("Constante A de Chudnovsky", "Chudnovsky constant A",
                             "ثابت شدنوفسكي A"),
     "unite": ("entier déclaré", "declared integer", "عددٌ صحيح معلَن"),
     "valeur": float(GEN.A_CHUD), "equation": "EQ-01"},
    {"id": "B_CHUD", "nom": ("Constante B de Chudnovsky", "Chudnovsky constant B",
                             "ثابت شدنوفسكي B"),
     "unite": ("entier déclaré", "declared integer", "عددٌ صحيح معلَن"),
     "valeur": float(GEN.B_CHUD), "equation": "EQ-01"},
    {"id": "C_CHUD", "nom": ("Constante C de Chudnovsky", "Chudnovsky constant C",
                             "ثابت شدنوفسكي C"),
     "unite": ("entier déclaré", "declared integer", "عددٌ صحيح معلَن"),
     "valeur": float(GEN.C_CHUD), "equation": "EQ-01"},
    {"id": "LONGUEUR_ANCRE", "nom": ("Ancre publiée recoupée", "Crossed published anchor",
                                     "مرساةٌ منشورة مُقابلة"),
     "unite": ("décimales citées", "cited decimals", "خانةً مُستشهَدًا بها"),
     "valeur": float(CP.LONGUEUR_ANCRE), "equation": "EQ-01, C01"},
    {"id": "ALPHA", "nom": ("Seuil bilatère de rejet", "Two-sided rejection threshold",
                            "حدُّ الرفض الثنائي"),
     "unite": ("probabilité", "probability", "احتمال"),
     "valeur": float(CP.ALPHA), "equation": "EQ-06, EQ-17"},
    {"id": "Z_SEUIL", "nom": ("z correspondant", "matching z", "قيمة z الموافقة"),
     "unite": ("écarts-types", "standard deviations", "انحرافٌ معياري"),
     "valeur": float(CP.Z_SEUIL), "equation": "EQ-06"},
    {"id": "KMAX", "nom": ("Classes de positions", "Position classes", "فئات المواضع"),
     "unite": ("classes", "classes", "فئات"),
     "valeur": float(CP.KMAX), "equation": "EQ-08, EQ-10, EQ-16"},
    {"id": "RMAX", "nom": ("Longueurs de runs", "Run lengths", "أطوال السلاسل"),
     "unite": ("longueurs", "lengths", "أطوال"),
     "valeur": float(CP.RMAX), "equation": "EQ-13"},
    {"id": "PAS_CUMUL", "nom": ("Points de la courbe cumulative", "Cumulative curve points",
                                "نقاط المنحنى التراكمي"),
     "unite": ("points déclarés", "declared points", "نقاطٌ معلنة"),
     "valeur": float(CP.PAS_CUMUL), "equation": "EQ-11"},
    {"id": "GRAINE", "nom": ("Graine MT19937", "MT19937 seed", "بذرة MT19937"),
     "unite": ("identifiant de tirage", "draw identifier", "معرّف القرعة"),
     "valeur": float(CP.GRAINE), "equation": "EQ-12"},
    {"id": "n_sim", "nom": ("Domaine du calibrage", "Calibration domain", "مجال المعايرة"),
     "unite": ("répétitions", "repetitions", "تكرارات"),
     "valeur": float(CP.N_SIM), "equation": "EQ-12"},
    {"id": "repiliques", "nom": ("Répliques par domaine", "Replicates per domain",
                                 "نسخٌ لكل مجال"),
     "unite": ("répliques", "replicates", "نسخ"),
     "valeur": float(CP.REPILIQUES), "equation": "EQ-12"},
    {"id": "LIMITE_POISSON_EXACT", "nom": ("Bascule Poisson / normale",
                                           "Poisson-to-normal switch", "بديل بواسون / الطبيعي"),
     "unite": ("valeur de λ", "value of λ", "قيمة λ"),
     "valeur": float(CP.LIMITE_POISSON_EXACT), "equation": "EQ-06, EQ-10"},
    {"id": "KAPPA_BANDE", "nom": ("Bande haute sur κ", "Upper band on κ", "النطاق الأعلى لـ κ"),
     "unite": ("rapport de variances", "variance ratio", "نسبة التباينات"),
     "valeur": float(CP.KAPPA_BANDE[1]), "equation": "EQ-14"},
    {"id": "BANDE_RAPPORT", "nom": ("Bande du rapport d'écarts-types",
                                    "Spread-ratio band", "نطاق نسبة الانحرافات"),
     "unite": ("rapport", "ratio", "نسبة"),
     "valeur": float(CP.BANDE_RAPPORT[1]), "equation": "EQ-12"},
    {"id": "MIN_LAMBDA_RAPPORT", "nom": ("λ minimal pour un rapport",
                                         "Minimum λ for a ratio", "أدنى λ بالنسبة"),
     "unite": ("valeur de λ", "value of λ", "قيمة λ"),
     "valeur": float(CP.MIN_LAMBDA_RAPPORT), "equation": "EQ-12"},
]

# ----------------------------------------------------------------------------
# Sources, lignée, commandes
# ----------------------------------------------------------------------------
CHAPITRES = ("0:00 Five digits at position 16470 · 1:33 Where position one is · "
             "2:57 Ninety thousand candidates · 4:17 Zero point nine every time · "
             "5:37 Matches by length · 7:03 The running total · 8:22 Three ways to count · "
             "9:39 The same search in e and root two · 11:02 Every short string shows up · "
             "12:46 A pattern nobody has proven")

SOURCE_FR = (
    "Point de départ mesuré : « What Is Actually Hiding in the Digits of Pi? » (Euclidea, "
    "vidéo M90ZAVojI30, 854 s), mesurée avec le script de lecture des chapitres ; les dix "
    "chapitres sont repris tels quels — " + CHAPITRES + ". La page ne rend aucun transcript "
    "(timedtext 0 octet) : aucune phrase de la vidéo n'est citée, aucun chiffre n'en vient, "
    "et le titre « Five digits at position 16470 » n'est pas la source du chiffre 16470, que "
    "C09 recalcule dans les décimales produites ici. Les deux voies de génération viennent de "
    "la littérature et sont déclarées comme telles : Chudnovsky et Chudnovsky (1989) pour "
    "π = 426880·√10005 / Σ(−1)ᵏ(6k)!(A+Bk)/((3k)!(k!)³C³), Machin (1706) pour la seconde voie "
    "de π, Euler (1748) pour e = Σ 1/k!, et l'inégalité entière w² ≤ 2·10²ⁿ < (w+1)² pour √2. "
    "Les outils statistiques sont eux aussi publics : Pearson pour le χ², Wilson et Hilferty "
    "(1931) pour l'intervalle en racine cubique, Bonferroni (1936) et Cetoni (1925) pour la "
    "correction multiple, Poisson pour les petits comptes, Fisher (1932) pour le test G, "
    "Metropolis, Ulam et von Neumann (1949) pour le Monte-Carlo. Noms de lignée pure, sans "
    "aucune équation qui repose sur eux : Borel (1909), Sierpiński (1917), Champernowne "
    "(1933), Copeland et Erdős (1937), Wall (1949), Bailey, Borwein et Plouffe (1995) — "
    "aucune de nos deux voies n'utilise la formule BBP. Ce qui est calculé ici, et seulement "
    "ici : les certificats entiers, les 108 cellules fermées avant mesure, les trois voies de "
    "comptage, la déiance sommée et le verdict borné.")

SOURCE_EN = (
    "Measured starting point: “What Is Actually Hiding in the Digits of Pi?” (Euclidea, video "
    "M90ZAVojI30, 854 s), read with the chapter-extraction script; the ten chapters are "
    "reproduced as they stand — " + CHAPITRES + ". The page serves no transcript (timedtext, "
    "0 bytes): no sentence of the video is quoted, no number comes from it, and the title "
    "“Five digits at position 16470” is not the source of the figure 16470, which C09 recomputes "
    "from the decimals produced here. Both generating paths come from the literature and are "
    "declared as such: Chudnovsky and Chudnovsky (1989) for π = 426880·√10005 / "
    "Σ(−1)ᵏ(6k)!(A+Bk)/((3k)!(k!)³C³), Machin (1706) for the second path of π, Euler (1748) for "
    "e = Σ 1/k!, and the integer inequality w² ≤ 2·10²ⁿ < (w+1)² for √2. The statistical tools "
    "are public too: Pearson for χ², Wilson and Hilferty (1931) for the cube-root interval, "
    "Bonferroni (1936) and Cetoni (1925) for the multiplicity correction, Poisson for small "
    "counts, Fisher (1932) for the G test, Metropolis, Ulam and von Neumann (1949) for "
    "Monte-Carlo. Pure lineage names, on which no equation rests: Borel (1909), Sierpiński "
    "(1917), Champernowne (1933), Copeland and Erdős (1937), Wall (1949), Bailey, Borwein and "
    "Plouffe (1995) — neither of our two paths uses the BBP formula. What is computed here, and "
    "only here: the integer certificates, the 108 cells closed before the read, the three "
    "counting paths, the pooled deviance and the bounded verdict.")

SOURCE_AR = (
    "نقطةُ البداية المقاسة: فيلم « What Is Actually Hiding in the Digits of Pi? » (قناة "
    "Euclidea، الفيديو M90ZAVojI30، المدة 854 s)، قُرئ بأداة استخراج الفصول، والفصولُ العشرة "
    "منسوخةٌ كما هي — " + CHAPITRES + ". لا تنشر الصفحةُ أيَّ نصٍّ مكتوب (‏timedtext بصفر بايت): "
    "فلا تُقتبس جملةٌ من الفيديو ولا يأتي منه رقمٌ، وعنوانُ فصل « Five digits at position "
    "16470 » ليس مصدرَ العدد 16470 الذي يعيد C09 حسابه من الخانات المولَّدة هنا. أما مسارا "
    "التوليد فأصلُهما الأدبيّ ومُعلَنان كذلك: Chudnovsky و Chudnovsky عام 1989 من أجل "
    "π = 426880·√10005 / Σ(−1)ᵏ(6k)!(A+Bk)/((3k)!(k!)³C³)، و Machin عام 1706 للمسار الثاني من π، "
    "و Euler عام 1748 لـ e = Σ 1/k!، والمتراجحةُ الصحيحة w² ≤ 2·10²ⁿ < (w+1)² لـ √2. وأدواتُ "
    "الإحصاء منشورةٌ هي الأخرى: Pearson لـ χ²، و Wilson و Hilferty عام 1931 لمجال الجذر التكعيبي، "
    "و Bonferroni عام 1936 و Cetoni عام 1925 لتصحيح التعدد، و Poisson للأعداد الصغيرة، و Fisher "
    "عام 1932 لاختبار G، و Metropolis و Ulam و von Neumann عام 1949 لمونت كارلو. وأسماءُ نسبةٍ "
    "محضة لا تستند عليها معادلة: Borel عام 1909، و Sierpiński عام 1917، و Champernowne عام 1933، "
    "و Copeland و Erdős عام 1937، و Wall عام 1949، و Bailey و Borwein و Plouffe عام 1995 — فأيٌّ "
    "من مساري لا يستعمل صيغة BBP. وما يُحسَب هنا هو وحده: الشهاداتُ الصحيحة، والخلايا الـ 108 "
    "المغلقةُ قبل القراءة، ومساراتُ العدّ الثلاثة، والانحرافُ المجموع، والحكمُ المحدود.")

LIGNE = ("Chudnovsky et Chudnovsky 1989 → Machin 1706 → Euler 1748 → Hippase (irrationalité de √2) "
         "→ Poisson 1837 → Pearson 1900 → Wilson et Hilferty 1931 → Bonferroni 1936 → "
         "Metropolis, Ulam, von Neumann 1949 → Euclidea M90ZAVojI30 (dix thèmes horodatés)")

COMMANDES = {
    "fr": ("# depuis la racine du dépôt\n"
           "py -3 CHIFFRES/chiffres_pi.py 1000000 --ecrit     # 17 équations, 17 contrôles, "
           "artefacts\n"
           "py -3 CHIFFRES/generer_pages.py                   # régénère pages, figure, JSON, "
           "CSV, Markdown\n"
           "py -3 -m unittest CHIFFRES.tests.test_chiffres     # 30 tests\n"
           "py -3 FONDATION/OUTILS/audit_piliers.py CHIFFRES/chiffres_pi.py --rigide\n"
           "# hors Windows : remplacer py -3 par python3"),
    "en": ("# from the repository root\n"
           "py -3 CHIFFRES/chiffres_pi.py 1000000 --ecrit     # 17 equations, 17 checks, "
           "artefacts\n"
           "py -3 CHIFFRES/generer_pages.py                   # rebuilds pages, figure, JSON, "
           "CSV, Markdown\n"
           "py -3 -m unittest CHIFFRES.tests.test_chiffres     # 30 tests\n"
           "py -3 FONDATION/OUTILS/audit_piliers.py CHIFFRES/chiffres_pi.py --rigide\n"
           "# off Windows: replace py -3 with python3"),
    "ar": ("# من جذر المستودع\n"
           "py -3 CHIFFRES/chiffres_pi.py 1000000 --ecrit     # 17 معادلةً و 17 تحقُّقًا "
           "والمخرجات\n"
           "py -3 CHIFFRES/generer_pages.py                   # يعيد توليد الصفحات والشكل و JSON "
           "و CSV و Markdown\n"
           "py -3 -m unittest CHIFFRES.tests.test_chiffres     # 30 اختبارًا\n"
           "py -3 FONDATION/OUTILS/audit_piliers.py CHIFFRES/chiffres_pi.py --rigide\n"
           "# خارج ويندوز: استبدل py -3 بـ python3"),
}

FONDATION_HREF = "../../../FONDATION/artefacts/pages/fondation.html"
INDEX_LIBELLE = {"fr": "Voir la page FONDATION du même dépôt",
                 "en": "See the FONDATION page of the same deposit",
                 "ar": "اطّلع على صفحة الأساس في الإيداع نفسه"}


# ----------------------------------------------------------------------------
# utilitaires locaux
# ----------------------------------------------------------------------------
def detail(donnees: Dict[str, Any], eq_id: str) -> Dict[str, Any]:
    for e in donnees["equations"]:
        if e["id"] == eq_id:
            return e["detail"]
    raise KeyError(f"{eq_id} absent")


def _3(fr: str, en: str, ar: str) -> Dict[str, str]:
    return {"fr": fr, "en": en, "ar": ar}


def carte(lab: Sequence[str], note: Sequence[str], valeur: str):
    return (_3(lab[0], lab[1], lab[2]), {"fr": valeur, "en": valeur, "ar": valeur},
            _3(note[0], note[1], note[2]))


def _chemins(slug: str) -> Dict[str, str]:
    return {"fr": f"{slug}.html", "en": f"{slug}_en.html", "ar": f"{slug}_ar.html"}


def _nav(chemins: Dict[str, str]) -> List[Sequence[str]]:
    return [("fr", "Français", chemins["fr"]), ("en", "English", chemins["en"]),
            ("ar", "العربية", chemins["ar"])]


def _liens(slug: str) -> List[Dict[str, Any]]:
    dep = "../donnees/"
    return [
        {"href": f"{dep}{slug}.json", "libelle": _3("JSON calculé", "Computed JSON",
                                                    "JSON المحسوب")},
        {"href": f"{dep}{slug}.csv", "libelle": _3("CSV Excel", "Excel CSV", "CSV لإكسل")},
        {"href": f"../dossiers/{slug}.md", "libelle": _3("Dossier markdown",
                                                         "Markdown dossier", "ملف Markdown")},
        {"href": "../etat.json", "libelle": _3("État du domaine", "Domain state",
                                               "حالة المجال")},
        {"href": "../confrontation.json", "libelle": _3("108 cellules confrontées",
                                                        "108 confronted cells",
                                                        "108 خليةً مواجهَة")},
        {"href": DOI_CONCEPT, "libelle": _3("DOI du dépôt", "Deposit DOI", "معرف الكائن")},
        {"href": DEPOT_GITHUB, "libelle": _3("Source sur GitHub", "Source on GitHub",
                                             "المصدر على GitHub")},
    ]


# ----------------------------------------------------------------------------
# figure calculée
# ----------------------------------------------------------------------------
def figure_chiffres(donnees: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Trois χ²(9) mesurés, un plafond déclaré : la figure ne dessine que des calculs."""
    d7 = detail(donnees, "EQ-07")
    bas, haut = CP.chi2_intervalle(9, CP.ALPHA)
    serie = [(CP.LIBELLES[c], float(d7[c]["chi2"]), COULEURS[c]) for c in CP.CONSTANTES]
    for _, v, _ in serie:
        if not bas <= v <= haut:
            raise SystemExit(f"un χ² de la figure sort de l'intervalle annoncé : {v}")
    titre = _3("χ²(9) des dix chiffres, plafond déclaré",
               "χ²(9) of the ten digits, with the declared ceiling",
               "χ²(9) للخانات العشر مع السقف المعلَن")
    desc = _3("Une barre par constante : la statistique calculée sur les dix classes de "
              f"chiffres, {CP.LIBELLES['pi']}, {CP.LIBELLES['e']} et {CP.LIBELLES['racine2']}. "
              "Le trait pointillé est la borne haute de l'intervalle Wilson–Hilferty déclaré "
              "par le module, pas une mesure. Aucun label n'est traduit dans le dessin.",
              "One bar per constant: the statistic computed over the ten digit classes for "
              f"{CP.LIBELLES['pi']}, {CP.LIBELLES['e']} and {CP.LIBELLES['racine2']}. The dashed "
              "line is the upper bound of the Wilson–Hilferty interval declared by the module, "
              "not a measurement. No label inside the drawing is translated.",
              "عمودٌ لكل ثابت: الإحصاءُ المحسوب على فئات الخانات العشر للرموز "
              f"{CP.LIBELLES['pi']} و{CP.LIBELLES['e']} و{CP.LIBELLES['racine2']}. والخطُّ المنقّط "
              "هو الحدُّ الأعلى لمجال Wilson–Hilferty الذي أعلنه المولّد، لا قياس. ولا تُترجَم أيُّ "
              "تسمية داخل الرسم.")
    legende = _3(
        "Figure 1 — EQ-07 et C07 : les trois χ²(9) calculés sur le domaine publié, sous le "
        f"plafond déclaré {haut:.3f}. Aucune barre ne le touche ; ce n'est pas une preuve "
        "d'uniformité, c'est une absence de rejet sur ce domaine.",
        "Figure 1 — EQ-07 and C07: the three χ²(9) computed on the published domain, under the "
        f"declared ceiling {haut:.3f}. No bar touches it; that is not proof of uniformity, it is "
        "an absence of rejection on this domain.",
        "الشكل 1 — EQ-07 وC07: قيم χ²(9) المحسوبة على المجال المنشور، تحت سقفٍ معلَن قدره "
        f"{haut:.3f}. لا يلمس أيُّ عمود ذلك السقف؛ وليس هذا برهانَ تماثل، بل هو عدمُ رفضٍ على "
        "هذا المجال.")
    svg = {l: MOTEUR.figure_barres(titre[l], desc[l], serie, haut, ids=("fig1-t", "fig1-d"))
           for l in MOTEUR.LANGUES}
    return [{"svg": svg, "legende": legende}]


# ----------------------------------------------------------------------------
# matériaux = valeurs déclarées
# ----------------------------------------------------------------------------
def materiaux() -> List[Dict[str, Any]]:
    lignes: List[Dict[str, Any]] = []
    for info in DECLAREES:
        lignes.append({"id": info["id"],
                       "nom": _3(info["nom"][0], info["nom"][1], info["nom"][2]),
                       "unite": _3(info["unite"][0], info["unite"][1], info["unite"][2]),
                       "quantite": float(info["valeur"]),
                       "equation": {"fr": info["equation"], "en": info["equation"],
                                    "ar": info["equation"]}})
    return lignes


# ----------------------------------------------------------------------------
# colonne formule traduite
# ----------------------------------------------------------------------------
def formules_traduites(donnees: Dict[str, Any], lang: str, vues: set) -> Dict[str, Any]:
    if lang == "fr":
        return donnees
    eqs: List[Dict[str, Any]] = []
    for e in donnees["equations"]:
        if e["formule"] not in FORMULE_TR:
            raise SystemExit(f"formule sans traduction pour {lang} : {e['formule']!r}")
        vues.add(e["formule"])
        copie = dict(e)
        copie["formule"] = FORMULE_TR[e["formule"]][lang]
        eqs.append(copie)
    autre = dict(donnees)
    autre["equations"] = eqs
    return autre


# ----------------------------------------------------------------------------
# spec
# ----------------------------------------------------------------------------
def spec_chiffres(donnees: Dict[str, Any]) -> Dict[str, Any]:
    ch = _chemins("chiffres")
    conf = donnees["confrontation"]
    d1 = detail(donnees, "EQ-01")
    dev = conf["deviance_auto_local"]
    return {
        "module": "chiffres_pi.py", "slug": "chiffres", "chemins": ch,
        "theme": _3("CHIFFRES — 108 cellules fermées avant la mesure",
                    "DIGITS — 108 cells closed before the read",
                    "الخانات — 108 خليةً مُغلَقةً قبل القراءة"),
        "description": _3(
            "Dix-sept équations sur π, e et √2 : les décimales viennent d'un certificat entier, "
            "deux voies indépendantes se recoupent, et cent huit cellules statistiques sont "
            "écrites avant toute mesure, puis confrontées sur un domaine fini — en français, en "
            "anglais et en arabe.",
            "Seventeen equations on π, e and √2: the decimals come from an integer certificate, "
            "two independent paths are crossed against each other, and one hundred eight "
            "statistical cells are written before any measurement, then confronted on a finite "
            "domain — in French, English and Arabic.",
            "سبعَ عشرةَ معادلةً على π وe و√2: الخاناتُ تأتي من شهادةٍ صحيحة، ويتقاطع مسارٌ "
            "مستقلان، ومئةٌ وثماني خليةٍ إحصائية تُكتب قبل أي قياس ثم تواجه على مجالٍ منتهٍ — "
            "بالفرنسية والإنجليزية والعربية."),
        "titre_bande": _3("CHIFFRES — AL-MIZAN × ASTRO-Q°ODE",
                          "DIGITS — AL-MIZAN × ASTRO-Q°ODE",
                          "الخانات — الميزان × ASTRO-Q°ODE"),
        "eq_text": EQ_TEXT, "cheminement": CHEMINEMENT,
        "figures": figure_chiffres(donnees),
        "resultats": [
            carte(("Cellules fermées avant mesure (EQ-06)", "Cells closed before the read (EQ-06)",
                   "خلايا مُغلَقة قبل القراءة (EQ-06)"),
                  ("Énumérées par `predire(n)`, qui ne lit aucun chiffre.",
                   "Enumerated by `predire(n)`, which reads no digit.",
                   "تُعدِّدها `predire(n)` التي لا تقرأ أيَّ خانة."),
                  f"{conf['nombre_cellules']}"),
            carte(("Cellules exclues / attendues (EQ-17)", "Excluded / expected cells (EQ-17)",
                   "الخلايا المستبعدة / المتوقعة (EQ-17)"),
                  ("Le compte des exclusions suit une loi de Poisson déclarée.",
                   "The count of exclusions follows a declared Poisson law.",
                   "عددُ الاستبعادات يتبع قانون بواسون المعلَن."),
                  f"{conf['nombre_exclues']} / {conf['exclues_attendues']}"),
            carte(("p globale (EQ-17)", "Global p (EQ-17)", "القيمة العامة لـ p (EQ-17)"),
                  ("Une cellule sur cent huit : dans la bande, hors preuve.",
                   "One cell in one hundred eight: inside the band, outside any proof.",
                   "خليةٌ من مئةٍ وثمانٍ: داخل النطاق، خارج أي برهان."),
                  f"{conf['p_globale']:.4f}"),
            carte(("Verdict global du domaine", "Global verdict of the domain",
                   "الحكمُ العام على المجال"),
                  ("« CONTENU » : le domaine fini n'a rien rejeté, rien n'est établi au-delà.",
                   "“CONTENU”: the finite domain rejected nothing; nothing is established beyond it.",
                   "«CONTENU»: لم يرفض المجالُ المنتهي شيئًا، ولا يثبت شيءٌ وراءه."),
                  f"{conf['verdict_global']}"),
            carte(("Déiance auto-localisée (EQ-16)", "Self-localisation deviance (EQ-16)",
                   "انحرافُ التموضع الذاتي (EQ-16)"),
                  (f"Somme sur {dev['df']} degrés de liberté, dans l'intervalle χ² déclaré.",
                   "Pooled over {0} degrees of freedom, inside the declared χ² interval."
                   .format(dev["df"]),
                   "مجموعٌ على {0} درجةِ حرية، داخل مجال χ² المعلَن.".format(dev["df"])),
                  f"{dev['g2']:.3f}"),
            carte(("Termes de Chudnovsky pour π (EQ-01)", "Chudnovsky terms for π (EQ-01)",
                   "حدود شدنوفسكي لـ π (EQ-01)"),
                  ("Chaque terme donne environ quatorze chiffres ; le compte vient du module.",
                   "Each term yields about fourteen digits; the count comes from the module.",
                   "يمنح كلُّ حدٍّ نحو أربع عشرة خانة؛ والعددُ من الوحدة."),
                  f"{d1['termes']}"),
        ],
        "materiaux": materiaux(),
        "caption_materiaux": _3(
            "Dix-huit valeurs déclarées avant calcul : domaine, gardes, entiers de l'identité de "
            "Chudnovsky, seuils statistiques et graine du tirage. Elles viennent des publications "
            "nommées ou du module lui-même ; aucune n'est mesurée dans ce dépôt, et la colonne "
            "d'équation dit où chacune entre en jeu.",
            "Eighteen values declared before any computation: domain, guards, the integers of "
            "Chudnovsky's identity, the statistical thresholds and the seed of the draw. They "
            "come from the publications named or from the module itself; none is measured in this "
            "deposit, and the equation column says where each one comes into play.",
            "ثماني عشرةَ قيمةً معلَنةً قبل أي حساب: المجال، والحراسات، والأعدادُ الصحيحة في هوية "
            "شدنوفسكي، وحدودُ الإحصاء، وبذرةُ القرعة. تأتي من المنشورات المسماة أو من الوحدة "
            "نفسها، ولم تُقس أيٌّ منها في هذا الإيداع، وعمودُ المعادلة يقول أين تدخل كلُّ واحدة."),
        "sources": _3(SOURCE_FR, SOURCE_EN, SOURCE_AR),
        "fil_conducteur": LIGNE,
        "commandes": COMMANDES,
        "liens": _liens("chiffres"), "index_href": FONDATION_HREF,
        "index_libelle": INDEX_LIBELLE,
        "chapitres_nav": _nav(ch), "doi": DOI_CONCEPT,
    }


# ----------------------------------------------------------------------------
# garde-fous locaux
# ----------------------------------------------------------------------------
MOT_MIXTE = re.compile(r"[\u0621-\u064a\u064f-\u0652]{4,}[A-Za-z]{4,}")


def _verifier_mixte(ecrits: List[Path]) -> None:
    """Un mot arabe translittéré de moitié en latin ne passe pas la publication."""
    fautifs = [f"{p.name} : {m.group(0)}" for p in ecrits if "_ar." in p.name
               for m in MOT_MIXTE.finditer(p.read_text(encoding="utf-8"))]
    if fautifs:
        raise SystemExit("mots arabes mêlés de latin : " + " | ".join(fautifs[:8]))


def _titrer(donnees: Dict[str, Any]) -> Dict[str, Any]:
    """Étiquette les équations pour le CSV et le Markdown : titre français seulement."""
    for eq in donnees["equations"]:
        eq["_titre_fr"] = EQ_TEXT[eq["id"]]["fr"][0]
    return donnees


def _coherence_artefacts(donnees: Dict[str, Any]) -> None:
    """La page publie le domaine scellé : les lignes françaises sont comparées à etat.json."""
    chemin = ARTEFACTS / "etat.json"
    if not chemin.is_file():
        return
    scelle = json.loads(chemin.read_text(encoding="utf-8"))
    index = {e["id"]: e["resultat"] for e in scelle["equations"]}
    derives = [f"{e['id']} : page {e['resultat']!r} vs artefact {index.get(e['id'])!r}"
               for e in donnees["equations"] if index.get(e["id"]) != e["resultat"]]
    if derives:
        raise SystemExit("la page et l'artefact scellé ne publient pas le même domaine : "
                         + " | ".join(derives[:4]))


def resume(donnees: Dict[str, Any]) -> Dict[str, Any]:
    statuts = Counter(e["statut"] for e in donnees["equations"])
    return {"equations": len(donnees["equations"]),
            "controles_ok": sum(1 for c in donnees["controles"] if c["ok"]),
            "controles_total": len(donnees["controles"]),
            "statuts": dict(statuts),
            "domaine": donnees["domaine"],
            "verdict_global": donnees["confrontation"]["verdict_global"]}


def _sans_chaines(donnees: Dict[str, Any]) -> Dict[str, Any]:
    copie = dict(donnees)
    copie["certificats"] = {c: {k: v for k, v in donnees["certificats"][c].items()
                                if k != "chiffres"}
                            for c in donnees["certificats"]}
    return copie


def main() -> int:
    donnees = CP.resoudre(N_PAGE, CP.N_SIM, CP.N_SIM2, CP.REPILIQUES, CP.REPILIQUES2)
    if not CP.verifier(donnees):
        raise SystemExit("contrôles non reçus dans chiffres_pi : la page n'est pas publiée")
    _coherence_artefacts(donnees)
    donnees["resume"] = resume(donnees)
    donnees["source"] = {"module": "chiffres_pi.py", "video": donnees["video"],
                         "domaine": donnees["domaine"],
                         "outils": {"generation": "generer_chiffres.py",
                                    "confrontation": "chiffres_pi.py"}}
    donnees["valeurs_declarees"] = {d["id"]: d["valeur"] for d in DECLAREES}
    donnees = _titrer(donnees)

    spec = spec_chiffres(donnees)
    ecrits: List[Path] = []
    vues: set = set()
    for lang in MOTEUR.LANGUES:
        cible = ARTEFACTS / "pages" / spec["chemins"][lang]
        MOTEUR.ecrire_chemin(cible, MOTEUR.construire_page(
            spec, formules_traduites(donnees, lang, vues), lang))
        ecrits.append(cible)
    for lang in MOTEUR.LANGUES:
        figure = (ARTEFACTS / "figures"
                  / f"chiffres{'' if lang == 'fr' else '_' + lang}.svg")
        MOTEUR.ecrire_svg(spec["figures"][0]["svg"][lang], figure)
        ecrits.append(figure)
    for dossier, nom, contenu in (
        ("donnees", "chiffres.json", None),
        ("donnees", "chiffres.csv", MOTEUR.lignes_csv_equations(donnees)),
        ("dossiers", "chiffres.md", MOTEUR.markdown(_sans_chaines(donnees), spec)),
    ):
        cible = ARTEFACTS / dossier / nom
        if contenu is None:
            MOTEUR.ecrire_json(_sans_chaines(donnees), cible)
        elif isinstance(contenu, str):
            MOTEUR.ecrire_chemin(cible, contenu)
        else:
            MOTEUR.ecrire_csv(contenu, cible)
        ecrits.append(cible)
    mortes = sorted(set(FORMULE_TR) - vues)
    if mortes:
        raise SystemExit("clés de formule sans formule correspondante : " + " | ".join(mortes))
    _verifier_mixte(ecrits)
    MOTEUR.ecrire_json({"version": "1.0",
                        "module": "chiffres_pi.py",
                        "equations": donnees["resume"]["equations"],
                        "controles_ok": donnees["resume"]["controles_ok"],
                        "controles_total": donnees["resume"]["controles_total"],
                        "statuts": donnees["resume"]["statuts"],
                        "verdict_global": donnees["resume"]["verdict_global"],
                        "domaine": donnees["domaine"],
                        "artefacts": sorted(str(p.relative_to(RACINE)).replace("\\", "/")
                                            for p in ecrits)},
                       ARTEFACTS / "donnees" / "etat_generateur.json")
    ecrits.append(ARTEFACTS / "donnees" / "etat_generateur.json")
    print(json.dumps({"equations": donnees["resume"]["equations"],
                      "controles": f"{donnees['resume']['controles_ok']}/"
                                   f"{donnees['resume']['controles_total']}",
                      "verdict": donnees["resume"]["verdict_global"],
                      "artefacts": len(ecrits),
                      "racine": str(ARTEFACTS.relative_to(DEPOT)).replace("\\", "/")},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
