# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""Générateur du dossier FONDATION : pages trilingues, SVG, JSON, CSV, Markdown.

`fondation_base.py` calcule ; ce fichier met en forme. Il ne pose aucune équation
de plus, ne re-arrange aucun nombre, ne convertit aucune unité : chaque valeur
imprimée en français, en anglais ou en arabe est relue dans le dictionnaire rendu
par `resoudre()`. Le moteur `ABONDANCE/moteur_page_trilingue.py` refuse ensuite
toute phrase anglaise ou arabe énonçant un chiffre absent des lignes calculées :
une traduction ne peut ni inventer un nombre ni laisser vieillir une phrase.

Formats produits dans `FONDATION/artefacts/` :
    pages/fondation[_en|_ar].html  trois pages trilingues, sans JavaScript
    pages/index[_en|_ar].html      tableau de bord de production
    figures/fondation.svg          une figure calculée (douze cases pilier × couche)
    donnees/fondation.json         le dictionnaire complet rendu au moteur
    donnees/fondation.csv          équations + contrôles, Excel français (BOM, « ; »)
    dossiers/fondation.md          dossier pédagogique markdown

Usage :
    py -3 FONDATION/generer_fondation.py

Honnêteté du contenu : la vidéo Nocturne 5pP1e69T3HQ n'a ni chapitre horodaté ni
transcript accessible. Les pages ne la citent pas, ne minutent rien, n'attribuent
aucune phrase à sa bande-son ; seul son thème est utilisé. Les comparateurs publics
(arXiv:2103.15389, arXiv:2412.12015, arXiv:2605.02415, home.cern 2024-09-25) sont
recopiés tels que le module les cite. L'axiome d'EQ-01 est POSÉ HORS MATRICE :
aucune équation ne le prouve, aucune mesure ne le confirme ni ne l'infirme, et il
ne fournit aucun nombre.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

RACINE = Path(__file__).resolve().parent
DEPOT = RACINE.parent
for _chemin in (str(RACINE), str(DEPOT / "ABONDANCE")):
    if _chemin not in sys.path:
        sys.path.insert(0, _chemin)

import fondation_base as FB                        # noqa: E402
import moteur_page_trilingue as MOTEUR             # noqa: E402

ARTEFACTS = RACINE / "artefacts"
DOI_CONCEPT = "https://doi.org/10.5281/zenodo.24028242"
DEPOT_GITHUB = "https://github.com/IMAM8MAHDI/AL-MIZAN-Quantum-Emulator"
COULEURS = {"S1": "#1f5f8b", "S2": "#166534", "S3": "#b45309"}

# ============================================================================
# Textes par équation et par langue
# ----------------------------------------------------------------------------
# Structure : {"EQ-nn": {"fr": [titre, ""], "en": [titre, ligne], "ar": [titre, ligne]}}.
# Le français ne porte que le titre : la ligne lue reste la `resultat` calculée du
# module. Les lignes anglaise et arabe sont passées au garde-fou numérique du
# moteur ; elles ne reprennent donc que des nombres tels qu'ils apparaissent dans
# cette ligne française — même notation, même décimale, aucune conversion.
# ============================================================================
EQ_TEXT: Dict[str, Dict[str, List[str]]] = {
    "EQ-01": {
        "fr": ["L'axiome posé hors matrice", ""],
        "en": ["The axiom set outside the matrix",
               "One declared source of regularity, held outside every derivation: no equation "
               "in this dossier proves it, no CERN measurement confirms or refutes it, and it "
               "supplies no number. It forbids exactly one thing — declaring the same quantity "
               "twice with two values."],
        "ar": ["المُسلَّمة موضوعة خارج المصفوفة",
               "مصدرٌ واحد مُعلَن للانتظام، موضوعٌ خارج كل اشتقاق. لا تُثبِتُه معادلةٌ في هذا "
               "الملف، ولا تُؤيِّدُه ولا تُكذِّبُه قياساتُ سيرن، ولا يمدّنا بأي عدد. يمنع أمرًا "
               "واحدًا: أن تُعلَن الكميةُ الواحدة بقيمتين."]},
    "EQ-02": {
        "fr": ["Tout nœud sans prédécesseur interne est fondé dehors", ""],
        "en": ["Every node without an internal predecessor is founded outside",
               "The chain of derivation stops on a single root, and the edges pointing outside "
               "the dossier are counted with it. Nothing here is self-founded."],
        "ar": ["كل عقدةٍ بلا سابقٍ داخلي مؤسَّسة على خارج الملف",
               "سلسلة الاشتقاق تتوقف عند جذرٍ واحد، وأضلاعُها الخارجة من الملف معدودة معه. "
               "لا شيء هنا مؤسَّس على نفسه."]},
    "EQ-03": {
        "fr": ["Le graphe est un DAG", ""],
        "en": ["The dependency graph is acyclic",
               "Acyclic, every node reachable from that root, no node citing itself. The "
               "structure rules out circular justification; it says nothing about whether the "
               "numbers are right."],
        "ar": ["المخطط الحسبي بلا دورات",
               "بلا دورات، وكل عقدة تُبلَغ من ذلك الجذر، ولا عقدة تُحيل على نفسها. البنية تنفي "
               "التدوير في الاستدلال، ولا تقول إن الأرقام صحيحة."]},
    "EQ-04": {
        "fr": ["Discipline de source et parc compté", ""],
        "en": ["Source discipline, and the dossiers counted",
               "Every number names a public source, all twelve pillar by layer cases are "
               "inhabited, and each excerpt of the channel's text is verified as a verbatim "
               "substring of the measured description. That video has no dated chapter and no "
               "accessible transcript, so this page quotes none of it and gives no timestamp."],
        "ar": ["انضباط المصدر والوحدات المعدودة",
               "كلُّ عددٍ يُسمّي مصدرًا منشورًا، والحالات الاثنتا عشرة بين الأعمدة والطبقات "
               "مأهولة، وكل مقتطف من نص القناة يُراجَع كمقطعٍ حرفي من الوصف المقيس. ذلك الفيديو "
               "لا فصول مؤرخة له ولا نصٍّ متاح، فلا اقتباس منه ولا توقيت في هذه الصفحة."]},
    "EQ-05": {
        "fr": ["Bibliothèque standard seule, ici et dans le parc", ""],
        "en": ["Standard library only, here and across the deposit",
               "Imports resolve either to the standard library or to modules of this deposit, "
               "and the same scan is run on every module of the deposit. An environment without "
               "this interpreter does not inherit the same control."],
        "ar": ["المكتبة القياسية وحدها، هنا وفي كامل المستودع",
               "الاستيراد لا يجاوز المكتبةَ القياسية لوحدات هذا المستودع، والمَسحُ نفسه يُجرى على "
               "كل وحدة من وحداته. ومن لا يملك هذا المُفسِّر لا يرث التحكمَ ذاته."]},
    "EQ-06": {
        "fr": ["Un registre, une valeur par grandeur", ""],
        "en": ["One registry, one value per quantity",
               "The registry closes on itself: as many unique names as entries, no conflicting "
               "duplicate, no empty unit. The values themselves are declared literature numbers "
               "read from the sources named below, not measurements taken here."],
        "ar": ["سجلٌّ واحد، وقيمةٌ واحدة لكل قدْر",
               "السجل مغلقٌ على نفسه: أسماء فريدة بعدد المدخلات، ولا مكرر متناقض، ولا وحدة "
               "فارغة. أما القيم فأرقام أدبيات معلَنة قُرئت من المصادر المسماة أدناه، لا قياسات "
               "أُجريت هنا."]},
    "EQ-07": {
        "fr": ["La prédiction est gelée avant la lecture du comparateur", ""],
        "en": ["The prediction is frozen before the comparator is read",
               "The prediction function receives one declared dictionary and none of the "
               "comparator keys. Its digest is unchanged when forbidden keys are injected into "
               "it, and the contamination flag rises. That is structural independence, not "
               "accuracy: the prediction may still be wrong."],
        "ar": ["التنبؤ مُجَمَّد قبل قراءة المُقارِن",
               "دالةُ التنبؤ لا تستقبل إلا القاموسَ المعلَن، ولا يصلها أيُّ مفتاحٍ من مفاتيح "
               "المقارنة. تبقى البصمة كما هي إن حُقنت مفاتيحُ ممنوعة، ويرتفع علَمُ التلوّث. ذلك "
               "استقلالٌ بنيوي لا دقة: قد يظل التنبؤ خاطئًا."]},
    "EQ-08": {
        "fr": ["Désintégrations ordinaires par désintégration rare", ""],
        "en": ["Ordinary decays per rare decay",
               "The standard model rate gives 1.19048e+10 ordinary decays for one rare decay, "
               "and the rounded count quoted by the home.cern communiqué, 9999999999, implies "
               "1e-10. That agreement is an agreement of rounding: it is written down here, not "
               "smoothed over."],
        "ar": ["التفككات الاعتيادية مقابل كل تفكك نادر",
               "يعطي معدلُ النموذج القياسي 1.19048e+10 تفككًا اعتياديًا مقابل تفككٍ نادرٍ واحد، "
               "وعددُ البلاغ المدوَّر 9999999999 يَضمر 1e-10. ذلك اتفاقُ تقريبٍ لا اتفاق قياس؛ "
               "كُتب هنا ولم يُمحَ."]},
    "EQ-09": {
        "fr": ["L'acceptance ferme sur des chiffres publiés", ""],
        "en": ["The acceptance closes on published figures",
               "Recomputing the signal count gives 10.0119 against 10.01 published, a relative "
               "gap of 0.0192, and the two acceptances give a ratio of 0.9373. Three published "
               "numbers closing on each other cannot reveal an error all three share."],
        "ar": ["القبول ينغلق على أرقام منشورة",
               "إعادةُ حساب عدد الأحداث تعطي 10.0119 مقابل 10.01 المنشور، بفارقٍ نسبي قدره "
               "0.0192، ونسبةُ القبولين 0.9373. ثلاثةُ أرقام منشورة تنغلق على بعضها لا يمكن أن "
               "تكشف خطأً يشترك فيه الثلاثة."]},
    "EQ-10": {
        "fr": ["Prédiction gelée contre l'excès publié en 2021", ""],
        "en": ["Frozen prediction against the excess published in 2021",
               "The frozen prediction is 10.0119 events; the publication reports an excess of "
               "12.97, a gap of 0.7166 σ. That is an agreement, not a discovery, and the "
               "uncertainty used is the one NA62 declares — its likelihood is not rebuilt here."],
        "ar": ["التنبؤ المجمَّد مقابل الزيادة المنشورة عام 2021",
               "التنبؤُ المجمَّد هو 10.0119 حدثًا، والنشرُ يُبلِّغ عن زيادة قدرها 12.97، أي بفارق "
               "0.7166 σ. هذا اتفاقٌ لا اكتشاف، واللاتمامُ المستعمل هو الذي تُعلنه NA62؛ لا نعيد "
               "بناء أرجحيَّتها هنا."]},
    "EQ-11": {
        "fr": ["Signification Li–Ma sur les chiffres 2021", ""],
        "en": ["Li–Ma significance on the published 2021 counts",
               "On the published counts the Li–Ma formula gives 3.9852 σ, while the p-value "
               "printed in the paper implies 3.3975 σ. Both stay under 5 σ, so the published "
               "word remains evidence, not observation. Our formula ignores the systematic "
               "uncertainty of the background and is expected to run high."],
        "ar": ["دلالة لي وما على أرقام 2021",
               "على الأعداد المنشورة تعطي صيغةُ لي وما 3.9852 σ، بينما تضمر قيمةُ p المطبوعة في "
               "المقالة 3.3975 σ. كلاهما تحت 5 σ، فتبقى الكلمة المنشورة دليلًا لا رصدًا. صيغتُنا "
               "تتغافل عن اللاتمامِ المنهجي للخلفية، فترتفع كما يُتوقَّع."]},
    "EQ-12": {
        "fr": ["Ce que cinq sigma coûtent en événements", ""],
        "en": ["What five sigma costs in events",
               "At the declared threshold of 5 σ, the published background requires 25.0624 "
               "events above it; the paper reports 33.00, a margin of 7.9376. Recomputed the "
               "same way, Li–Ma gives 6.3426 against the published 5.0690. The background used "
               "is the one the same paper announces: a coherence check, not an independent "
               "prediction."],
        "ar": ["كم يكلّف خمسةُ سيغما من الأحداث",
               "عند العتبة المعلَنة 5 σ تفوق الزيادةُ المطلوبة الخلفيةَ بـ 25.0624 حدثًا، ويُنشر "
               "33.00، بهامشٍ قدره 7.9376. وبالحساب نفسه تعطي لي وما 6.3426 مقابل 5.0690 "
               "المنشور. الخلفية المستعملة هي التي تُعلنها المقالة ذاتها: اتساقٌ داخلي لا تنبؤ "
               "مستقل."]},
    "EQ-13": {
        "fr": ["Confrontation 2024 : notre z contre le leur", ""],
        "en": ["The 2024 confrontation: our z against the published one",
               "Adding the two uncertainties in quadrature is OUR declared hypothesis, not "
               "NA62's; it puts z between 1.3340 and 1.4546 against the 1.7 they declare. The "
               "one-sigma intervals do not overlap. That is written down rather than hidden, "
               "and NA62 publishes a full likelihood treatment."],
        "ar": ["مواجهة 2024: z لدينا مقابل z لديهم",
               "جمعُ اللاتمامين تربيعيًا فرضيَّتُنا المعلَنة لا فرضية NA62؛ وهو يضع z بين 1.3340 "
               "و1.4546 مقابل 1.7 الذي يُعلنونه. فاصلا اللاتمام عند σ واحد لا يتداخلان، وهذا "
               "مكتوبٌ لا مطويّ، وNA62 تنشر معالجة أرجحية كاملة."]},
    "EQ-14": {
        "fr": ["Confrontation 2026 : l'écart se referme", ""],
        "en": ["The 2026 confrontation: the gap closes",
               "On the combined 2016-2024 numbers, BR 9.6e-11 gives z = 0.5589, lower branch "
               "0.5828, under 1 σ. Those figures come from a preprint and may move; the bound "
               "written on this equation says so."],
        "ar": ["مواجهة 2026: الفارق يضيق",
               "بالأرقام المجمَّعة من 2016 إلى 2024 يعطي BR بقيمة 9.6e-11 ما يساوي z = 0.5589، "
               "والفرع الأدنى 0.5828، أي تحت σ واحد. هذه الأرقام من مطبوعةٍ مُسبَقة وقد تتحرك، "
               "وحدُّ هذه المعادلة يقول ذلك."]},
    "EQ-15": {
        "fr": ["Budget de fond contre chaîne de rejets", ""],
        "en": ["Background budget against the published rejection chain",
               "The published background asks for a total suppression of 3.841e+11, while the "
               "rejection chain announced for muons and neutral pions reaches 1e+15, a margin of "
               "3.416 orders. These are declared orders of magnitude: which channel dominates "
               "the real background is not known here."],
        "ar": ["ميزانيةُ الخلفية مقابل سلسلة الكبت",
               "الخلفيةُ المنشورة تطلب كبتًا إجماليًا مقداره 3.841e+11، بينما تبلغ سلسلةُ الكبت "
               "المعلَنة للميونات والبيونات المحايدة 1e+15، بهامشٍ قدره 3.416 من الدرجات. هذه "
               "درجاتُ قدرٍ معلَنة، ولا نعرف أيَّ قناة تسيطر على الخلفية الحقيقية."]},
    "EQ-16": {
        "fr": ["Géométrie du faisceau : une borne inférieure simulée", ""],
        "en": ["Beam geometry: a simulated lower bound",
               "The declared beam figures give one kaon decaying in the fiducial volume per 2104 "
               "produced, at 6e+07 charged kaons per second. The status is SIMULATED: any real "
               "dead time makes the fraction larger, and the communiqué gives neither the "
               "useful time nor the beam acceptance."],
        "ar": ["هندسةُ الحزمة: حدٌّ أدنى محاكى",
               "تعطي أرقامُ الحزمة المعلَنة كاونًا واحدًا يتفكك في الحجم المؤتمَن مقابل 2104 "
               "كاونًا مُولَّدًا، بمعدل 6e+07 كاونًا موجبًا في الثانية. المرتبةُ محاكاة: كلُّ زمن "
               "ميتٍ حقيقي يزيد النسبة، ولا يعطي البلاغُ لا الزمنَ النافع ولا قبول الحزمة."]},
    "EQ-17": {
        "fr": ["Erreur de comptage contre erreur publiée", ""],
        "en": ["Counting error against the published error",
               "Both periods publish an error above pure Poisson counting, relatively 0.3774 and "
               "0.2538. The gain measured from 2021 to 2024 stays at 1.4866, below the 1.5951 "
               "the square-root law expects. That is a bundle of hints about a systematic "
               "floor, not a measurement of that floor."],
        "ar": ["خطأُ العدّ مقابل الخطأ المنشور",
               "تنشر الفترتان خطأً أعلى من عدّ بواسون وحده، بالنسبة 0.3774 ثم 0.2538. ويبقى "
               "الربحُ المقيس من 2021 إلى 2024 عند 1.4866، تحت 1.5951 التي تتوقعها قانونُ الجذر "
               "التربيعي. تلك قرينةٌ على أرضيةٍ منهجية، لا قياسُ تلك الأرضية."]},
    "EQ-18": {
        "fr": ["La limite est le produit", ""],
        "en": ["The bound is the product",
               "Five ways this base would fall, and four things it does not prove, are listed as "
               "results rather than as caveats. A dossier that writes no refutation has no "
               "bound: it has a silence."],
        "ar": ["الحَدُّ هو الناتج",
               "خمسُ حالاتٍ يسقط فيها هذا الأساس، وأربعةُ أشياءَ لا يثبتها، مكتوبةٌ كنتائج لا "
               "كتحفظات. الملفُ الذي لا يكتب دحضَه ليس له حدٌّ، بل له صمت."]},
}

# ----------------------------------------------------------------------------
# Colonne « formule » sur les pages anglaise et arabe
# ----------------------------------------------------------------------------
# La `formule` est écrite en français par le module. Elle est recopiée telle quelle
# côté français, et traduite intégralement ici — identifiants, symboles d'unités et
# nombres restant écrits tels qu'ils sont, pour que le pool numérique du moteur ne
# change pas d'une langue à l'autre. Toute formule absente de cette table, et toute
# clé de cette table sans formule correspondante, font échouer la construction.
FORMULE_TR: Dict[str, Tuple[str, str]] = {
    "AX : la régularité d'un système fini n'appartient pas à ce système": (
        "AX : the regularity of a finite system is not an element of that system",
        "AX : انتظامُ نظامٍ منتهٍ ليس عنصرًا من ذلك النظام"),
    "∀ nœud sans prédécesseur interne, une source déclarée hors du dossier": (
        "∀ node without an internal predecessor, a source declared outside the dossier",
        "∀ كل عقدةٍ بلا سابقٍ داخلي: مصدرٌ مُعلَن خارج الملف"),
    "DAG : acyclique, toutes racines atteignables, zéro auto-référence": (
        "DAG : acyclic, every root reachable, zero self-reference",
        "DAG : بلا دورات، كلُّ جذرٍ مبلَغ، ولا إحالة على الذات"),
    "chaque nombre ⇒ source publique ; douze cases pilier × couche habitées ; "
    "chaque extrait de la chaîne ⇒ sous-chaîne du texte mesuré": (
        "every number ⇒ public source ; twelve pillar × layer cases inhabited ; "
        "every excerpt of the channel ⇒ substring of the measured text",
        "كلُّ عددٍ ⇒ مصدرٌ منشور ; اثنتا عشرة حالةً بين العمود والطبقة مأهولة ; "
        "كلُّ مقتطفٍ من القناة ⇒ مقطعٌ من النص المقيس"),
    "imports ⊆ stdlib ∪ modules locaux — ici et dans tout le parc": (
        "imports ⊆ stdlib ∪ local modules — here and across the whole deposit",
        "imports ⊆ stdlib ∪ وحداتٌ محلية — هنا وفي كامل المستودع"),
    "|registre| = noms uniques · aucun doublon en conflit · unité non vide partout": (
        "|registre| = unique names · no conflicting duplicate · non-empty unit everywhere",
        "|registre| = أسماءُ فريدة · لا مكررَّ متناقض · وحدةٌ غير فارغة في كل مكان"),
    "signature(prediction) ∩ clés_comparateur = ∅ · digest stable": (
        "signature(prediction) ∩ clés_comparateur = ∅ · stable digest",
        "signature(prediction) ∩ clés_comparateur = ∅ · البصمةُ ثابتة"),
    "N_ordinaires = 1/BR − 1, intervalle par les deux branches d'incertitude": (
        "N_ordinaires = 1/BR − 1, interval from the two uncertainty branches",
        "N_ordinaires = 1/BR − 1، الفترةُ من فرعي اللاتمام"),
    "A·ε = 1/(N_K·SES) puis N = N_K·BR_sm·A·ε": (
        "A·ε = 1/(N_K·SES) then N = N_K·BR_sm·A·ε",
        "A·ε = 1/(N_K·SES) ثم N = N_K·BR_sm·A·ε"),
    "N gelé = 10,01 contre excès publié (candidates − fond)": (
        "N frozen = 10.01 against the published excess (candidates − fond)",
        "N المجمَّد = 10.01 مقابل الزيادة المنشورة (candidates − fond)"),
    "z(20 | 7,03) par Li–Ma contre z implicite de la p-value publiée": (
        "z(20 | 7.03) by Li–Ma against the implicit z of the published p-value",
        "z(20 | 7.03) بصيغة لي وما مقابل z الضمنية لقيمة p المنشورة"),
    "excès requis pour z = 5 à fond connu, contre excès publié 2024": (
        "excess required for z = 5 at a known background, against the 2024 published excess",
        "الزيادةُ المطلوبة عند z = 5 لخلفيةٍ معلومة، مقابل الزيادة المنشورة عام 2024"),
    "z = (BR_obs − BR_sm)/√(σ_obs² + σ_sm²), sur les deux branches": (
        "z = (BR_obs − BR_sm)/√(σ_obs² + σ_sm²), on both branches",
        "z = (BR_obs − BR_sm)/√(σ_obs² + σ_sm²)، على الفرعين"),
    "même formule, chiffres 2016-2024 de la mise à jour 2026": (
        "same formula, the 2016-2024 numbers of the 2026 update",
        "الصيغةُ ذاتها، أرقام 2016-2024 من تحديث 2026"),
    "suppression totale requise = N_K/fond, contre la chaîne de rejets publiée": (
        "total suppression required = N_K/fond, against the published rejection chain",
        "الكبتُ الإجمالي المطلوب = N_K/fond، مقابل سلسلة الكبت المنشورة"),
    "fraction = N_K / (secondaires/s × 6 % × 3 ans × 3,15576·10⁷ s)": (
        "fraction = N_K / (secondaires/s × 6 % × 3 years × 3,15576·10⁷ s)",
        "fraction = N_K / (secondaires/s × 6 % × 3 سنوات × 3,15576·10⁷ s)"),
    "σ_Poisson = √(s+b)/s contre erreur relative publiée, deux périodes": (
        "σ_Poisson = √(s+b)/s against the published relative error, two periods",
        "σ_Poisson = √(s+b)/s مقابل الخطأ النسبي المنشور، لفترتين"),
    "liste des réfutations internes et des non-preuves": (
        "list of internal refutations and of what is not proven",
        "لائحةُ الدحض الداخلي وما لا يُبرَهَن"),
}

# ============================================================================
# Cheminement — une chaîne de raisonnement, trois langues
# ============================================================================
CHEMINEMENT: List[Dict[str, List[str]]] = [
    {"fr": ["La source mesurée, et ses absences",
            "Le point de départ est une page YouTube mesurée octet pour octet, citée ici comme "
            "une référence bibliographique : son titre « Le CERN a Enfin Détecté un Événement "
            "que la Science Attendait depuis 40 Ans » (chaîne Nocturne, identifiant "
            "5pP1e69T3HQ, durée déclarée 8018 s). Elle ne rend que du JavaScript d'amorçage, sa "
            "description ne porte aucun chapitre horodaté, donc aucun minutage citable, et "
            "timedtext renvoie 0 octet : le transcript est tenu pour absent. Le dossier ne "
            "cite aucune phrase de la vidéo, n'en reprend aucun instant, n'en tire aucun "
            "chiffre ; il n'en retient qu'un thème, la désintégration rare K⁺ → π⁺ νν̄."],
     "en": ["The measured source, and what it lacks",
            "The starting point is a YouTube page measured byte for byte, cited here only as a "
            "bibliographic reference: its title « Le CERN a Enfin Détecté un Événement que la "
            "Science Attendait depuis 40 Ans » (Nocturne channel, id 5pP1e69T3HQ, declared "
            "length 8018 s). It serves only bootstrap JavaScript, its description carries no "
            "dated chapter and therefore no citable timestamp, and timedtext returns 0 bytes: "
            "the transcript is held to be absent. The dossier quotes no sentence of the video, "
            "reaches no instant of it and takes no number from it; it keeps one theme only, the "
            "rare decay K⁺ → π⁺ νν̄."],
     "ar": ["المصدرُ المقيس وما ينقصه",
            "نقطةُ البداية صفحةُ يوتيوب قِيست بايتً ببايت، تُذكر هنا كمرجعٍ ببليوغرافي فقط: "
            "عنوانها « Le CERN a Enfin Détecté un Événement que la Science Attendait depuis 40 "
            "Ans » (قناة Nocturne، المعرّف 5pP1e69T3HQ، المدّة المعلَنة 8018 s). لا تنشر إلا "
            "تهيئة جافاسكريبت، ولا يحمل وصفُها فصلًا مؤرَّخًا فلا لحظةَ يمكن اقتباسُها، وترجع "
            "timedtext بصفر بايت: فالنصّ المكتوب معدوم. لا يورد الملف جملةً من الفيديو ولا "
            "لحظةً منه ولا رقمًا منه، وإنما يحفظ موضوعًا واحدًا هو التفكك النادر "
            "K⁺ → π⁺ νν̄."]},
    {"fr": ["L'axiome est posé, il ne prouve rien",
            "EQ-01 énonce l'Un, posé HORS MATRICE et attribué à M. Ahmed EL BAHLOUL "
            "(IMAM8MAHDI). Le module porte explicitement `nombres_fournis_par_l_axiome = 0` : "
            "aucune équation ne dérive de l'axiome, aucune mesure du CERN ne le confirme ni ne "
            "l'infirme, et la physique de ce dossier ne suit pas une théologie. Ce que l'axiome "
            "engage est une seule contrainte vérifiable : ne pas déclarer deux fois la même "
            "grandeur avec deux valeurs."],
     "en": ["The axiom is set, and it proves nothing",
            "EQ-01 states the One, set OUTSIDE THE MATRIX and attributed to M. Ahmed EL BAHLOUL "
            "(IMAM8MAHDI). The module carries `nombres_fournis_par_l_axiome = 0` on its face: no "
            "equation derives from the axiom, no CERN measurement confirms or refutes it, and "
            "the physics here follows neither a theology nor the reverse. What the axiom commits "
            "to is one checkable constraint: never declare the same quantity twice with two "
            "values."],
     "ar": ["المُسلَّمة مقرَّرة وهي لا تُثبت شيئًا",
            "تُقرِّر EQ-01 الوحدانيةَ، موضوعةً خارج المصفوفة ومنسوبةً إلى M. Ahmed EL BAHLOUL "
            "(IMAM8MAHDI). تحمل الوحدةُ صراحةً `nombres_fournis_par_l_axiome = 0`: فلا معادلةً "
            "تشتق منها، ولا قياسٌ من سيرن يُؤكِّدها أو يُكذِّبها، ولا فيزياءَ هنا تتبع لاهوتًا "
            "ولا عكسَهما. أما ما تُلزم به فشرطٌ واحدٌ قابلٌ للتحقق: أن لا تُعلَن الكميةُ ذاتها "
            "بقيمتين."]},
    {"fr": ["Quatre piliers qui sont des contrôles",
            "Unité, Borne, Confrontation, Transmission ne sont pas des décorations : chacun est "
            "repris par des contrôles exécutés à chaque exécution, et `OUTILS/audit_piliers.py` "
            "les applique aux autres modules du dépôt. Un pilier devient exigeant quand il coûte "
            "des phrases et des échecs possibles, pas quand il est annoncé."],
     "en": ["Four pillars that are checks",
            "Unity, Bound, Confrontation and Transmission are not decoration: each is carried by "
            "controls executed on every run, and `OUTILS/audit_piliers.py` applies them to the "
            "other modules of the deposit. A pillar becomes demanding when it costs sentences "
            "and can fail, not when it is announced."],
     "ar": ["أربعةُ أعمدة هي تحققات",
            "الوحدةُ والحدُّ والمواجهةُ والنقلُ ليست زينة: يحملها تحققاتٌ تُجرى عند كل تشغيل، "
            "ويُطبِّقها `OUTILS/audit_piliers.py` على سائر وحدات المستودع. العمودُ يصير صارمًا "
            "حين يكلّف جملًا ويمكن أن يفشل، لا حين يُعلَن فحسب."]},
    {"fr": ["Le graphe s'arrête quelque part",
            "EQ-02 et EQ-03 exigent qu'un nœud sans prédécesseur interne nomme une source "
            "déclarée hors du dossier, et que le graphe reste acyclique. La chaîne de dérivation "
            "butte donc sur une source posée, jamais sur elle-même : c'est la forme opératoire "
            "de l'axiome, et elle ne dit rien de la vérité des nombres."],
     "en": ["The graph stops somewhere",
            "EQ-02 and EQ-03 require that a node without an internal predecessor name a source "
            "declared outside the dossier, and that the graph stay acyclic. The chain of "
            "derivation therefore ends on a posited source, never on itself: that is the "
            "operative shape of the axiom, and it says nothing about the truth of the numbers."],
     "ar": ["المخططُ يتوقف عند حدٍّ",
            "تطلب EQ-02 وEQ-03 أن تُسمّي كلُّ عقدةٍ بلا سابقٍ داخلي مصدرًا مُعلَنًا خارج الملف، "
            "وأن يبقى المخططُ بلا دورات. فتنتهي سلسلةُ الاشتقاق عند مصدرٍ مُقرَّر لا عند نفسها: "
            "هذا هو العملُ بالمُسلَّمة، ولا يقول شيئًا عن صدق الأرقام."]},
    {"fr": ["Une prédiction gelée avant la lecture",
            "EQ-07 gèle la prédiction sur un dictionnaire de valeurs déclarées et vérifie, par "
            "l'inspection de la signature, qu'aucune clé du comparateur n'y entre ; le drapeau "
            "de contamination se lève dès qu'on en injecte une. EQ-10 peut alors confronter "
            "10,0119 événements à l'excès publié sans avoir lu le résultat d'avance."],
     "en": ["A prediction frozen before the read",
            "EQ-07 freezes the prediction on a dictionary of declared values and checks, by "
            "inspecting the function signature, that no comparator key can enter it; the "
            "contamination flag rises as soon as one is injected. EQ-10 can then set 10.0119 "
            "events against the published excess without having read the result in advance."],
     "ar": ["تنبؤٌ جُمِّد قبل القراءة",
            "تُجمِّد EQ-07 التنبؤَ على قاموسِ قيمٍ معلَنة، وتتحقق بمعاينة توقيع الدالة أن لا "
            "مفتاحًا من مفاتيح المقارنة يدخله؛ ويرتفع علَمُ التلوّث بمجرد حقنِ أحدها. عندئذٍ "
            "تواجه EQ-10 بـ 10.0119 حدثًا الزيادةَ المنشورة، دون أن تكون قرأت النتيجة سلفًا."]},
    {"fr": ["La confrontation : 2021, 2024, 2026 et le communiqué",
            "EQ-08 à EQ-17 lisent quatre sources publiques. Le dossier écrit ce qui concorde "
            "(l'acceptance ferme, l'excès à 0,7166 σ de la prédiction gelée), ce qui ne concorde "
            "pas (les intervalles à un sigma de 2024 ne se recouvrent pas sous notre hypothèse "
            "de quadrature), et ce qui se referme (l'écart 2026 passe sous 1 σ). Aucun de ces "
            "écarts n'est présenté comme une découverte ni comme une réfutation de NA62."],
     "en": ["The confrontation: 2021, 2024, 2026 and the communiqué",
            "EQ-08 to EQ-17 read four public sources. The dossier writes what agrees (the "
            "acceptance closes, the excess sits 0.7166 σ from the frozen prediction), what does "
            "not (the 2024 one-sigma intervals do not overlap under our quadrature hypothesis), "
            "and what closes again (the 2026 gap falls under 1 σ). None of these is offered as a "
            "discovery or as a refutation of NA62."],
     "ar": ["المواجهة: 2021 و2024 و2026 والبلاغ",
            "تقرأ المعادلات من EQ-08 إلى EQ-17 أربعةَ مصادر منشورة. يكتب الملف ما يتفق (القبولُ "
            "ينغلق، والزيادةُ على بعد 0.7166 σ من التنبؤ المجمَّد)، وما لا يتفق (فاصلا اللاتمام في "
            "2024 لا يتداخلان تحت فرضية الجمع التربيعي لدينا)، وما يضيق بعد ذلك (فارق 2026 ينزل "
            "تحت σ واحد). ولا يُقدَّم شيءٌ من هذا كشفًا ولا دحضًا لـ NA62."]},
    {"fr": ["Ce que SPÉCIFIÉ et SIMULÉ veulent dire",
            "Deux équations portent SPÉCIFIÉ — l'axiome posé et la limite écrite — et une porte "
            "SIMULÉ : la fraction géométrique du faisceau, bornée inférieurement parce que le "
            "communiqué ne donne ni le temps utile ni l'acceptance du faisceau. Ces mots "
            "apparaissent dans les trois langues sur chaque page ; aucun résultat simulé n'est "
            "promu en affirmation."],
     "en": ["What SPECIFIED and SIMULATED mean here",
            "Two equations carry SPECIFIED — the posited axiom and the written bound — and one "
            "carries SIMULATED: the geometric beam fraction, bounded from below because the "
            "communiqué gives neither useful time nor beam acceptance. These words appear on "
            "every page in all three languages, and no simulated result is promoted into a "
            "claim."],
     "ar": ["ما يعنيه «محدَّد» و«محاكى»",
            "حملت معادلتان مرتبةَ محدَّد — المُسلَّمة المقرَّرة والحدُّ المكتوب — وحملت واحدةٌ "
            "مرتبةَ محاكى: نسبةُ الحزمة الهندسية، محدودةٌ من أسفل لأن البلاغ لا يعطي الزمنَ "
            "النافع ولا قبولَ الحزمة. وتظهر هذه الكلمات في الصفحات الثلاث بجميع اللغات، ولا يُرقَّى "
            "نتيجةٌ محاكاة إلى خبر."]},
    {"fr": ["Écrire sa propre réfutation",
            "EQ-18 termine le dossier par sa propre chute : cinq conditions qui l'invalident, "
            "quatre choses qu'il ne prouve pas, et dix-huit limites d'équation non vides. Un "
            "calcul fini ne fonde pas une assertion universelle ; il peut montrer que la "
            "discipline tient sur des nombres publics. C'est tout ce que ce dossier revendique."],
     "en": ["Writing one's own refutation",
            "EQ-18 closes the dossier with its own collapse: five conditions that would invalidate "
            "it, four things it does not prove, and eighteen non-empty equation bounds. A finite "
            "computation does not found a universal assertion; it can only show that a discipline "
            "holds on public numbers. That is the whole claim of this dossier."],
     "ar": ["أن يكتب المرءُ دحضَه",
            "تُختَم EQ-18 بسقوطها هي: خمسُ حالات تُبطلها، وأربعةُ أشياء لا تُبرَهَن، وثمانية "
            "عشر حدًّا للمعادلات غير خالٍ. الحسابُ المنتهي لا يؤسّس تعميمًا؛ إن يُبرهن فقط أن "
            "الانضباط ثابتٌ على أرقامٍ منشورة. هذا كله ما يدّعيه الملف."]},
]

# ============================================================================
# Grandeurs déclarées — table « matériaux »
# ----------------------------------------------------------------------------
# Les valeurs sont lues dans `declare` du dictionnaire calculé ; les noms, unités
# et équations qui s'en servent sont la description éditoriale du registre, telle
# que `SOURCES_ET_PREDECESSEURS.md` §4 la rend. La clé est contrôlée : si le module
# ajoute ou retire une grandeur déclarée, le générateur échoue plutôt que d'imprimer
# un registre périmé.
# ============================================================================
REGISTRE: Dict[str, Dict[str, Any]] = {
    "BR_sm": {
        "nom": ("BR(K⁺→π⁺νν̄), modèle standard", "BR(K⁺→π⁺νν̄), standard model",
                "‏BR لـ K⁺→π⁺νν̄ في النموذج القياسي"),
        "unite": ("1", "1", "1"),
        "eq": "EQ-08, EQ-09, EQ-10, EQ-13, EQ-14",
        "source": "Buras et al., JHEP 11 (2015) 33"},
    "dBR_sm": {
        "nom": ("incertitude théorique de BR_sm", "theory uncertainty of BR_sm",
                "عدم اليقين النظري لـ BR_sm"),
        "unite": ("1", "1", "1"),
        "eq": "EQ-08, EQ-10, EQ-13, EQ-14",
        "source": "Buras et al., JHEP 11 (2015) 33"},
    "N_K_2016_2018": {
        "nom": ("désintégrations effectives 2016-2018", "effective decays 2016-2018",
                "التفككات الفعلية 2016-2018"),
        "unite": ("désintégrations", "decays", "تفككًا"),
        "eq": "EQ-09, EQ-10, EQ-15, EQ-16",
        "source": "arXiv:2103.15389"},
    "SES_2016_2018": {
        "nom": ("sensibilité par événement 2016-2018", "single-event sensitivity 2016-2018",
                "الحساسية لكل حدث 2016-2018"),
        "unite": ("1", "1", "1"),
        "eq": "EQ-09, EQ-10",
        "source": "arXiv:2103.15389"},
    "N_K_2021_2022": {
        "nom": ("désintégrations effectives 2021-2022", "effective decays 2021-2022",
                "التفككات الفعلية 2021-2022"),
        "unite": ("désintégrations", "decays", "تفككًا"),
        "eq": "EQ-09",
        "source": "arXiv:2412.12015"},
    "SES_2021_2022": {
        "nom": ("sensibilité par événement 2021-2022", "single-event sensitivity 2021-2022",
                "الحساسية لكل حدث 2021-2022"),
        "unite": ("1", "1", "1"),
        "eq": "EQ-09",
        "source": "arXiv:2412.12015"},
    "secondaires_par_s": {
        "nom": ("secondaires incidents sur la cible", "secondary particles on target",
                "الجسيمات الثانوية على الهدف"),
        "unite": ("1/s", "1/s", "1/s"),
        "eq": "EQ-16",
        "source": "home.cern 2024-09-25"},
    "fraction_K_plus": {
        "nom": ("fraction de K⁺ dans le faisceau secondaire", "K⁺ fraction of the secondary "
                "beam", "نسبة K⁺ في الحزمة الثانوية"),
        "unite": ("1", "1", "1"),
        "eq": "EQ-16",
        "source": "home.cern 2024-09-25"},
    "annees_prises_2016_2018": {
        "nom": ("années de prise de données 2016-2018", "data-taking years 2016-2018",
                "سنوات أخذ البيانات 2016-2018"),
        "unite": ("an", "year", "سنة"),
        "eq": "EQ-16",
        "source": "arXiv:2103.15389"},
    "rejection_mu": {
        "nom": ("réjection des muons", "muon rejection", "كبت الميونات"),
        "unite": ("1", "1", "1"),
        "eq": "EQ-15",
        "source": "arXiv:2605.02415 — ordre de grandeur"},
    "rejection_pi0": {
        "nom": ("réjection des π⁰", "neutral-pion rejection", "كبت البيونات المحايدة"),
        "unite": ("1", "1", "1"),
        "eq": "EQ-15",
        "source": "arXiv:2605.02415 — ordre de grandeur"},
    "rejection_autres_canaux": {
        "nom": ("réjection des autres canaux", "rejection of the other channels",
                "كبت القنوات الأخرى"),
        "unite": ("1", "1", "1"),
        "eq": "EQ-15",
        "source": "arXiv:2605.02415 — ordre de grandeur"},
    "seuil_observation": {
        "nom": ("seuil communautaire d'observation", "community observation threshold",
                "عتبة الرصد المتعارف عليها"),
        "unite": ("sigma", "sigma", "σ"),
        "eq": "EQ-11, EQ-12",
        "source": "déclaré par la communauté"},
    "z_declare_2024": {
        "nom": ("écart déclaré par NA62 en 2024", "gap to the standard model declared by "
                "NA62 in 2024", "الفارق الذي أعلنه NA62 عام 2024"),
        "unite": ("sigma", "sigma", "σ"),
        "eq": "EQ-13",
        "source": "arXiv:2412.12015"},
}

SOURCE_FR = (
    "Point de départ mesuré : « Le CERN a Enfin Détecté un Événement que la Science Attendait "
    "depuis 40 Ans » (Nocturne, vidéo 5pP1e69T3HQ, 8018 s). La page publique ne rend que du "
    "JavaScript d'amorçage : la description ne porte aucun chapitre horodaté et timedtext "
    "renvoie 0 octet en json3, srv3 et xml — le transcript est tenu pour absent. La vidéo a "
    "fourni un sujet, la désintégration rare K⁺ → π⁺ νν̄, et une formulation ; jamais une "
    "citation, jamais un minutage, jamais un chiffre. Les nombres du dossier viennent des "
    "quatre comparateurs publics cités par le module — Collaboration NA62, arXiv:2103.15389 "
    "(JHEP 06 (2021) 093, DOI 10.1007/JHEP06(2021)093) ; Collaboration NA62, arXiv:2412.12015 "
    "(JHEP 02 (2025) 191, DOI 10.1007/JHEP02(2025)191) ; Collaboration NA62, arXiv:2605.02415 "
    "(MPP-2026-83, prépublication, peut bouger) ; communiqué home.cern du 2024-09-25, « the "
    "other 9 999 999 999 decays » — et d'une valeur théorique déclarée, BR_sm = 8.4e-11 ± "
    "1.0e-11 (Buras et al., JHEP 11 (2015) 33, arXiv:1503.02693). L'axiome d'EQ-01 est posé "
    "HORS MATRICE et attribué à M. Ahmed EL BAHLOUL (IMAM8MAHDI) : aucune équation ne le "
    "prouve, aucune mesure du CERN ne le confirme ni ne l'infirme, et il ne fournit aucun "
    "nombre. SOURCES_ET_PREDECESSEURS.md, à la racine du dossier, distingue pour chaque "
    "équation le calcul fait ici, la valeur déclarée et le simple nom de lignée.")

SOURCE_EN = (
    "Measured starting point: « Le CERN a Enfin Détecté un Événement que la Science Attendait "
    "depuis 40 Ans » (Nocturne, video 5pP1e69T3HQ, 8018 s). The public page serves only "
    "bootstrap JavaScript: its description carries no dated chapter and timedtext returns 0 "
    "bytes in json3, srv3 and xml, so the transcript is held to be absent. The video supplied a "
    "subject — the rare decay K⁺ → π⁺ νν̄ — and a wording; never a quotation, never a timestamp, "
    "never a number. The dossier's numbers come from the four public comparators the module "
    "cites — NA62, arXiv:2103.15389 (JHEP 06 (2021) 093, DOI 10.1007/JHEP06(2021)093); NA62, "
    "arXiv:2412.12015 (JHEP 02 (2025) 191, DOI 10.1007/JHEP02(2025)191); NA62, arXiv:2605.02415 "
    "(MPP-2026-83, a preprint that may move); the home.cern communiqué of 2024-09-25, « the "
    "other 9 999 999 999 decays » — and from one declared theory value, BR_sm = 8.4e-11 ± "
    "1.0e-11 (Buras et al., JHEP 11 (2015) 33, arXiv:1503.02693). The axiom of EQ-01 is set "
    "OUTSIDE THE MATRIX and attributed to M. Ahmed EL BAHLOUL (IMAM8MAHDI): no equation proves "
    "it, no CERN measurement confirms or refutes it, and it supplies no number. At the root of "
    "this dossier, SOURCES_ET_PREDECESSEURS.md separates, equation by equation, what is computed "
    "here, what is declared, and what is only a lineage name.")

SOURCE_AR = (
    "نقطةُ البداية المُقاسة: فيلم « Le CERN a Enfin Détecté un Événement que la Science "
    "Attendait depuis 40 Ans » (قناة Nocturne، الفيديو 5pP1e69T3HQ، المدة 8018 s). لا تنشر "
    "الصفحةُ العامة إلا تهيئة جافاسكريبت، ولا يحمل وصفُها فصلًا مؤرخًا، وترجع timedtext بصفر "
    "بايت في json3 وsrv3 وxml: فالترجمة النصية معدومة. أعطى الفيديو موضوعًا هو التفكك النادر "
    "K⁺ → π⁺ νν̄ وصياغةً، ولم يعطِ اقتباسًا ولا توقيتًا ولا رقمًا. أما أرقامُ الملف فتأتي من "
    "أربعة مقارنات منشورة تستشهد بها الوحدة — NA62 من arXiv:2103.15389 (‏JHEP 06 (2021) 093‏، "
    "المعرف 10.1007/JHEP06(2021)093)؛ وNA62 من arXiv:2412.12015 (‏JHEP 02 (2025) 191‏، المعرف "
    "10.1007/JHEP02(2025)191)؛ وNA62 من arXiv:2605.02415 (‏MPP-2026-83، مطبوعة مسبقة قد تتحرك)؛ "
    "وبلاغ home.cern بتاريخ 2024-09-25 « the other 9 999 999 999 decays » — ومن قيمة نظرية "
    "معلنة هي BR_sm = 8.4e-11 ± 1.0e-11 (Buras et al.‏، JHEP 11 (2015) 33‏، من arXiv:1503.02693). "
    "أما المُسلَّمة في EQ-01 فمقرَّرة خارج المصفوفة ومنسوبة إلى M. Ahmed EL BAHLOUL "
    "(IMAM8MAHDI): لا تُثبتها معادلة، ولا يُكذِّبها ولا يُؤكِّدها قياسٌ من سيرن، ولا تمدُّنا "
    "برقم. ويفرِّق SOURCES_ET_PREDECESSEURS.md في جذر الملف، لكل معادلة، بين محسوب هنا وقيمة "
    "معلَنة واسم نَسَبٍ فقط.")

LIGNE = ("Glashow, Iliopoulos et Maiani → Gaillard et Lee → Buras et al. → Li et Ma → "
         "Kahn → NA62 2021 → NA62 2024 → NA62 2026 → home.cern 2024-09-25")

COMMANDES = {
    "fr": ("# depuis la racine du dépôt\n"
           "py -3 FONDATION/fondation_base.py                 # 18 équations, 18 contrôles\n"
           "py -3 FONDATION/generer_fondation.py              # régénère pages, figure, JSON, "
           "CSV, Markdown\n"
           "py -3 -m unittest FONDATION.tests.test_fondation  # 45 tests\n"
           "py -3 FONDATION/OUTILS/audit_piliers.py FONDATION/fondation_base.py --rigide\n"
           "# hors Windows : remplacer py -3 par python3"),
    "en": ("# from the repository root\n"
           "py -3 FONDATION/fondation_base.py                 # 18 equations, 18 checks\n"
           "py -3 FONDATION/generer_fondation.py              # rebuilds pages, figure, JSON, "
           "CSV, Markdown\n"
           "py -3 -m unittest FONDATION.tests.test_fondation  # 45 tests\n"
           "py -3 FONDATION/OUTILS/audit_piliers.py FONDATION/fondation_base.py --rigide\n"
           "# off Windows: replace py -3 with python3"),
    "ar": ("# من جذر المستودع\n"
           "py -3 FONDATION/fondation_base.py                 # ‏18 معادلة و18 تحقّقًا\n"
           "py -3 FONDATION/generer_fondation.py              # يعيد بناء الصفحات والشكل وJSON "
           "وCSV وMarkdown\n"
           "py -3 -m unittest FONDATION.tests.test_fondation  # ‏45 اختبارًا\n"
           "py -3 FONDATION/OUTILS/audit_piliers.py FONDATION/fondation_base.py --rigide\n"
           "# خارج ويندوز: استبدل py -3 بـ python3"),
}

TITRE_INDEX = {"fr": "FONDATION — la base calculée",
               "en": "FONDATION — the computed base",
               "ar": "الأساس — القاعدة المحسوبة"}
DESC_INDEX = {
    "fr": "Dix-huit équations, dix-huit contrôles, une figure, un JSON, un CSV et un dossier "
          "markdown produits par le même générateur à partir de fondation_base.resoudre().",
    "en": "Eighteen equations, eighteen checks, one figure, one JSON, one CSV and one Markdown "
          "dossier, all produced by this generator from fondation_base.resoudre().",
    "ar": "ثماني عشرة معادلة وثمانية عشر تحققًا وشكلٌ واحد وملف JSON وملف CSV وملف Markdown "
          "يولّدها المولّد نفسه من fondation_base.resoudre()."}
INDEX_ENTETES = {
    "fr": ["Dossier", "Équations", "Contrôles reçus", "OPÉRATIONNEL", "SIMULÉ", "SPÉCIFIÉ",
           "Pages", "Données"],
    "en": ["Dossier", "Equations", "Checks met", "OPERATIONAL", "SIMULATED", "SPECIFIED",
           "Pages", "Data"],
    "ar": ["الملف", "المعادلات", "التحققات المستوفاة", "عامِل", "محاكى", "محدَّد",
           "الصفحات", "البيانات"],
}
PARC_ENTETES = {
    "fr": ["Dossier du parc", "Équations déclarées", "Contrôles déclarés", "Tests déclarés"],
    "en": ["Dossier in the park", "Declared equations", "Declared checks", "Declared tests"],
    "ar": ["ملفٌّ من المستودع", "معادلات معلَنة", "تحققات معلَنة", "اختبارات معلَنة"],
}
PARC_CAPTION = {
    "fr": "Comptage déclaré, relevé dans `dossiers` du dictionnaire calculé : une expression "
          "régulière sur les fichiers du dépôt. Elle mesure la déclaration, pas la justesse.",
    "en": "Declared counts, read from the `dossiers` block of the computed dictionary: a regular "
          "expression over the files of the deposit. It measures the declaration, not the "
          "correctness.",
    "ar": "عدٌّ معلَن مقروء من كتلة `dossiers` في المعجم المحسوب: تعبيرٌ نظامي على ملفات "
          "المستودع. يقيس الإعلان لا الصواب."}
CAPTION_LIVRABLES = {
    "fr": "Tout ce que le générateur écrit, et rien de plus : les pages, la figure, le JSON, le "
          "CSV Excel et le dossier markdown.",
    "en": "Everything the generator writes, and nothing more: the pages, the figure, the JSON, "
          "the Excel CSV and the Markdown dossier.",
    "ar": "كل ما يكتبه المولّد ولا شيء غيره: الصفحات والشكل وملف JSON وملف CSV لإكسل وملف "
          "Markdown."}
LIBELLES_LIVRABLE = {
    "fr": ["Pages trilingues", "Figure SVG", "Données JSON", "Données CSV", "Dossier Markdown",
           "Tableau de bord"],
    "en": ["Trilingual pages", "SVG figure", "JSON data", "CSV data", "Markdown dossier",
           "Dashboard"],
    "ar": ["صفحات ثلاث اللغات", "شكل SVG", "بيانات JSON", "بيانات CSV", "ملف Markdown",
           "لوحة الإنتاج"],
}
INDEX_REPRO = {
    "fr": "Un module calcule, ce générateur met en forme. Aucun nombre de page n'est saisi à la "
          "main : supprimer un artefact et relancer le générateur le reproduit à l'octet près.",
    "en": "One module computes, this generator formats. No page number is typed by hand: delete "
          "an artefact, re-run the generator, and it comes back byte for byte.",
    "ar": "وحدةٌ تحسب وهذا المولّد ينسّق. لا يُكتب أي رقم في الصفحة باليد: احذف المُخرَج وأعد "
          "تشغيل المولّد فيعود حرفيًا بايتً ببايت."}
INDEX_BOUTONS = {
    "fr": ["Aller à la page FONDATION", "Revenir au dépôt"],
    "en": ["Go to the FONDATION page", "Back to the deposit"],
    "ar": ["اذهب إلى صفحة الأساس", "العودة إلى الإيداع"],
}


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
        {"href": DOI_CONCEPT, "libelle": _3("DOI du dépôt", "Deposit DOI", "معرف الكائن")},
        {"href": DEPOT_GITHUB, "libelle": _3("Source sur GitHub", "Source on GitHub",
                                             "المصدر على GitHub")},
    ]


# ----------------------------------------------------------------------------
# figure calculée
# ----------------------------------------------------------------------------
def figure_fondation(donnees: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Douze cases pilier × couche, comptées dans `graphe` ; aucune valeur inventée."""
    matrice = donnees["graphe"]["matrice_pilier_couche"]
    cases = [(f"{p.split(' ')[0]} × {c.split(' ')[0]}", len(matrice[p][c]), COULEURS[c.split(' ')[0]])
             for p in donnees["piliers"] for c in donnees["couches"]]
    somme = sum(n for _, n, _ in cases)
    if somme != donnees["graphe"]["aretes"]:
        raise SystemExit(f"comptage de figure incohérent : {somme} cases vs "
                         f"{donnees['graphe']['aretes']} aretes")
    titre = _3("Douze cases pilier × couche", "Twelve pillar by layer cases",
               "اثنتا عشرة حالةً بين العمود والطبقة")
    desc = _3("Combien d'équations tiennent dans chaque case du graphe calculé par "
              "graphe_dependances() ; les douze cases sont habitées, la somme des barres est le "
              "nombre d'aretes du graphe. Les identifiants P1 à P4 et S1 à S3 sont ceux du "
              "module et restent tels quels.",
              "How many equations sit in each case of the graph computed by "
              "graphe_dependances(); all twelve cases are inhabited and the bars sum to the "
              "graph's edge count. The labels P1 to P4 and S1 to S3 are the module's own "
              "identifiers and stay as written.",
              "كم من المعادلات تسكن كل حالة من حالات المخطط الذي يحسبه graphe_dependances()؛ "
              "الحالاتُ الاثنتا عشرة مأهولة ومجموع الأعمدة يساوي عدد أضلاع المخطط. والرموز P1 "
              "إلى P4 وS1 إلى S3 معرّفات الوحدة فتبقى كما هي.")
    legende = _3(
        "Figure 1 — EQ-04 et C04 : les douze cases pilier × couche comptées dans le graphe "
        f"calculé ; les barres somment à {donnees['graphe']['aretes']} aretes. Un compte, pas "
        "une mesure.",
        "Figure 1 — EQ-04 and C04: the twelve pillar by layer cases counted in the computed "
        f"graph; the bars sum to {donnees['graphe']['aretes']} edges. A count, not a measurement.",
        "الشكل 1 — EQ-04 وC04: الحالات الاثنتا عشرة بين العمود والطبقة معدودة في المخطط "
        f"المحسوب، وتبلغ الأعمدة {donnees['graphe']['aretes']} ضلعًا. إنه عدٌّ لا قياس.")
    svg = {l: MOTEUR.figure_barres(titre[l], desc[l], cases, None, ids=("fig1-t", "fig1-d"))
           for l in MOTEUR.LANGUES}
    return [{"svg": svg, "legende": legende}]


# ----------------------------------------------------------------------------
# matériaux = registre déclaré
# ----------------------------------------------------------------------------
def materiaux(donnees: Dict[str, Any]) -> List[Dict[str, Any]]:
    declare = donnees["declare"]
    if set(declare) != set(REGISTRE):
        raise SystemExit(
            "le registre déclaré du module et sa description éditoriale ne coïncident plus : "
            f"module {sorted(declare)} vs générateur {sorted(REGISTRE)}")
    lignes: List[Dict[str, Any]] = []
    for nom, valeur in declare.items():            # ordre du dictionnaire du module
        info = REGISTRE[nom]
        lignes.append({"id": nom,
                       "nom": _3(info["nom"][0], info["nom"][1], info["nom"][2]),
                       "unite": _3(info["unite"][0], info["unite"][1], info["unite"][2]),
                       "quantite": float(valeur),
                       "equation": {"fr": info["eq"], "en": info["eq"], "ar": info["eq"]}})
    return lignes


# ----------------------------------------------------------------------------
# colonne formule traduite
# ----------------------------------------------------------------------------
def formules_traduites(donnees: Dict[str, Any], lang: str, vues: set) -> Dict[str, Any]:
    if lang == "fr":
        return donnees
    index = 0 if lang == "en" else 1
    eqs: List[Dict[str, Any]] = []
    for e in donnees["equations"]:
        if e["formule"] not in FORMULE_TR:
            raise SystemExit(f"formule sans traduction pour {lang} : {e['formule']!r}")
        vues.add(e["formule"])
        copie = dict(e)
        copie["formule"] = FORMULE_TR[e["formule"]][index]
        eqs.append(copie)
    autre = dict(donnees)
    autre["equations"] = eqs
    return autre


# ----------------------------------------------------------------------------
# spec
# ----------------------------------------------------------------------------
def spec_fondation(donnees: Dict[str, Any]) -> Dict[str, Any]:
    ch, r = _chemins("fondation"), donnees["resume"]
    d8, d10 = detail(donnees, "EQ-08"), detail(donnees, "EQ-10")
    d13, d14 = detail(donnees, "EQ-13"), detail(donnees, "EQ-14")
    return {
        "module": "fondation_base.py", "slug": "fondation", "chemins": ch,
        "theme": _3("FONDATION — une base, quatre piliers, une limite",
                    "FOUNDATION — one base, four pillars, one bound",
                    "الأساس — قاعدةٌ واحدة وأربعة أعمدة وحدٌّ واحد"),
        "description": _3(
            "Dix-huit équations posées sur une seule base et confrontées aux chiffres publics "
            "de NA62 et du communiqué CERN : une prédiction gelée avant lecture, un registre "
            "clos, une limite écrite, en français, en anglais et en arabe.",
            "Eighteen equations set on one base and confronted with the published NA62 numbers "
            "and the CERN communiqué: a prediction frozen before the read, a closed registry "
            "and a written bound, in French, English and Arabic.",
            "ثماني عشرة معادلةً مقرَّرة على أساسٍ واحد ومواجهةٌ لأرقام NA62 المنشورة وبلاغ سيرن: "
            "تنبؤٌ جُمِّد قبل القراءة، وسجلٌّ مغلق، وحدٌّ مكتوب، بالفرنسية والإنجليزية والعربية."),
        "titre_bande": _3("FONDATION — AL-MIZAN × ASTRO-Q°ODE",
                          "FOUNDATION — AL-MIZAN × ASTRO-Q°ODE",
                          "الأساس — الميزان × ASTRO-Q°ODE"),
        "eq_text": EQ_TEXT, "cheminement": CHEMINEMENT,
        "figures": figure_fondation(donnees),
        "resultats": [
            carte(("N gelé (EQ-10)", "Frozen N (EQ-10)", "N المجمَّد (EQ-10)"),
                  ("Calculé avant lecture du comparateur, puis confronté à l'excès publié.",
                   "Computed before the comparator was read, then set against the published "
                   "excess.",
                   "حُسِب قبل قراءة المقارن، ثم ووجّه مقابل الزيادة المنشورة."),
                  f"{d10['prevu']:.4f}"),
            carte(("Écart à l'excès publié 2021", "Gap to the published 2021 excess",
                   "الفارق حتى الزيادة المنشورة 2021"),
                  ("Un accord, pas une découverte ; l'incertitude est celle que NA62 déclare.",
                   "An agreement, not a discovery; the uncertainty is the one NA62 declares.",
                   "اتفاقٌ لا اكتشاف؛ واللاتمام هو الذي تُعلنه NA62."),
                  f"{d10['ecart_en_sigma']:+.4f} σ"),
            carte(("Compte ordinaire par compte rare (EQ-08)",
                   "Ordinary decays per rare decay (EQ-08)",
                   "التفككات الاعتيادية مقابل النادرة (EQ-08)"),
                  ("Le centre du modèle standard, avant toute lecture de résultat.",
                   "The standard-model centre, before any result was read.",
                   "مركزُ النموذج القياسي، قبل قراءة أي نتيجة."),
                  f"{d8['centre_modele_standard']:.6g}"),
            carte(("z 2024 sur les deux branches (EQ-13)", "z 2024 on both branches (EQ-13)",
                   "z لعام 2024 على الفرعين (EQ-13)"),
                  ("Addition en quadrature : notre hypothèse déclarée, pas la leur.",
                   "Quadrature addition: our declared hypothesis, not theirs.",
                   "الجمع التربيعي: فرضيَّتُنا المعلنة لا فرضيتهم."),
                  f"[{d13['z_branches'][0]:.4f}, {d13['z_branches'][1]:.4f}]"),
            carte(("écart déclaré par NA62 en 2024", "gap declared by NA62 for 2024",
                   "الفارق الذي أعلنه NA62 لعام 2024"),
                  ("Leur chiffre, recopié tel quel, avec nos deux z au-dessous.",
                   "Their figure, copied as it stands, with our two z below it.",
                   "رقمُهم منسوخٌ كما هو، وقيمتا z لدينا أدنى منه."),
                  f"{d13['z_declare_par_na62']}"),
            carte(("BR 2016-2024 (mise à jour 2026)", "BR 2016-2024 (2026 update)",
                   "‏BR لعامي 2016-2024 (تحديث 2026)"),
                  ("Prépublication : ces chiffres peuvent bouger, l'équation le dit.",
                   "A preprint: these numbers may move, and the equation says so.",
                   "مطبوعةٌ مسبقة: قد تتحرك هذه الأرقام، والمعادلة تقول ذلك."),
                  f"{d14['br_2016_2024']:.3g}"),
        ],
        "materiaux": materiaux(donnees),
        "caption_materiaux": _3(
            "Les quatorze grandeurs déclarées du registre : valeurs lues dans les publications "
            "nommées, recopiées par `declare` du module, jamais mesurées dans ce dépôt. La "
            "colonne d'équation indique où chacune entre en jeu.",
            "The fourteen declared quantities of the registry: values read from the publications "
            "named, copied through the module's `declare` block, never measured in this "
            "deposit. The equation column says where each one comes into play.",
            "القدرات الأربعة عشر المعلَنة في السجل: قيم مقروءة من المنشورات المسماة، منسوخة عبر "
            "كتلة `declare` في الوحدة، لم تُقس في هذا الإيداع. وعمود المعادلة يقول أين تدخل كل "
            "واحدة."),
        "sources": _3(SOURCE_FR, SOURCE_EN, SOURCE_AR),
        "fil_conducteur": LIGNE,
        "commandes": COMMANDES,
        "liens": _liens("fondation"), "index_href": "index.html",
        "index_libelle": _3("Tableau de bord du dossier", "Dashboard of this dossier",
                            "لوحة إنتاج هذا الملف"),
        "chapitres_nav": _nav(ch), "doi": DOI_CONCEPT,
    }


# ----------------------------------------------------------------------------
# tableau de bord
# ----------------------------------------------------------------------------
def page_index(lang: str, spec: Dict[str, Any], donnees: Dict[str, Any]) -> str:
    t, e = MOTEUR.T[lang], MOTEUR.ech
    lc = t["lang"]
    r, ch = donnees["resume"], spec["chemins"]
    suffixe = "" if lc == "fr" else f"_{lc}"

    def lien(href: str, txt: str, code: str = "") -> str:
        extra = f' lang="{code}"' if code else ""
        return f'<a href="{e(href)}"{extra}>{e(txt)}</a>'

    pages = " · ".join(lien(ch[l], l.upper(), l) for l in MOTEUR.LANGUES)
    data = " · ".join([lien(f"../donnees/fondation.json", "JSON"),
                       lien(f"../donnees/fondation.csv", "CSV"),
                       lien(f"../figures/fondation{suffixe}.svg", "SVG"),
                       lien("../dossiers/fondation.md", "MD")])
    lignes = [[e(_3("FONDATION — la base posée et confrontée",
                    "FOUNDATION — the base posited and confronted",
                    "الأساس — القاعدة المقرَّرة والمواجهة")[lc]),
              f"<span class=\"nb\">{r['equations']}</span>",
              f"<span class=\"nb\">{r['controles_ok']}/{r['controles_total']}</span>",
              f"<span class=\"nb\">{r['statuts'].get('OPÉRATIONNEL', 0)}</span>",
              f"<span class=\"nb\">{r['statuts'].get('SIMULÉ', 0)}</span>",
              f"<span class=\"nb\">{r['statuts'].get('SPÉCIFIÉ', 0)}</span>",
              pages, data]]
    entetes = [(INDEX_ENTETES[lc][i], "nb" if i in (1, 2, 3, 4, 5) else "") for i in range(8)]
    table = MOTEUR.tableau("dossiers", _3(
        "Une page par langue, une figure SVG autonome, un JSON, un CSV Excel et un dossier "
        "markdown, tous produits par le même générateur.",
        "One page per language, one standalone SVG figure, one JSON, one Excel CSV and one "
        "Markdown dossier, all produced by the same generator.",
        "صفحةٌ لكل لغة، وشكل SVG مستقل، وملف JSON، وملف CSV لإكسل، وملف Markdown، يولّدها جميعًا "
        "المولّد نفسه.")[lc], entetes, lignes)

    lignes_parc = [[e(nom), f"<span class=\"nb\">{v['equations']}</span>",
                    f"<span class=\"nb\">{v['controles']}</span>",
                    f"<span class=\"nb\">{v['tests']}</span>"]
                   for nom, v in donnees["dossiers"].items()]
    entetes_parc = [(PARC_ENTETES[lc][i], "nb" if i else "") for i in range(4)]
    table_parc = MOTEUR.tableau("parc", PARC_CAPTION[lc], entetes_parc, lignes_parc)

    livrables = [[e(LIBELLES_LIVRABLE[lc][i]) for i in range(6)],
                 [pages,
                  f'<a href="../figures/fondation.svg" lang="fr">FR</a> · '
                  f'<a href="../figures/fondation_en.svg" lang="en">EN</a> · '
                  f'<a href="../figures/fondation_ar.svg" lang="ar">AR</a>',
                  lien("../donnees/fondation.json", "fondation.json"),
                  lien("../donnees/fondation.csv", "fondation.csv"),
                  lien("../dossiers/fondation.md", "fondation.md"),
                  lien("index.html", "index.html"), ]]
    lignes_liv = [[livrables[0][i], livrables[1][i]] for i in range(6)]
    table_liv = MOTEUR.tableau("livrables", CAPTION_LIVRABLES[lc],
                               [(e(LIBELLES_LIVRABLE[lc][0]), ""), ("", "")], lignes_liv)

    corps = [f"<h1>{e(TITRE_INDEX[lc])}</h1>", f"<p>{e(DESC_INDEX[lc])}</p>",
             MOTEUR.badges([(f"{r['equations']} EQ", False),
                            (f"{r['controles_ok']}/{r['controles_total']} {t['controles']}",
                             True),
                            (_3("OPÉRATIONNEL", "OPERATIONAL", "عامِل")[lc] + " " +
                             str(r["statuts"].get("OPÉRATIONNEL", 0)), False),
                            (_3("SIMULÉ", "SIMULATED", "محاكى")[lc] + " " +
                             str(r["statuts"].get("SIMULÉ", 0)), False),
                            (_3("SPÉCIFIÉ", "SPECIFIED", "محدَّد")[lc] + " " +
                             str(r["statuts"].get("SPÉCIFIÉ", 0)), False)]),
             f"<p class=\"chemin\">{e(t['legende_statuts'])}</p>",
             f"<p class=\"chemin\">{e(INDEX_REPRO[lc])}</p>",
             table, table_parc, table_liv]
    boutons = (f'<a class="principal" href="{e(ch[lc])}">{e(INDEX_BOUTONS[lc][0])}</a>'
               f'<a href="{e(DOI_CONCEPT)}">{e(INDEX_BOUTONS[lc][1])}</a>')
    corps.append(f'<div class="actions">{boutons}</div>')
    corps.append(f"<h2 id=\"reproduction\">{e(t['reproduction'])}</h2>"
                 f"<pre>{e(COMMANDES[lc])}</pre>")
    nav = [("fr", "Français", "index.html"), ("en", "English", "index_en.html"),
           ("ar", "العربية", "index_ar.html")]
    queue = (f"<footer class=\"site\"><div class=\"interieur\"><p>{e(t['pied'])}</p>"
             f"<p>{e(MOTEUR.AUTEUR)} · {e(MOTEUR.LICENCE)} · {e(DOI_CONCEPT)}</p>"
             f"</div></footer>")
    chemins_index = {"fr": "index.html", "en": "index_en.html", "ar": "index_ar.html"}
    return (MOTEUR.tete(t, f"{TITRE_INDEX[lc]} — AL-MIZAN × ASTRO-Q°ODE", DESC_INDEX[lc],
                        chemins_index, chemins_index[lc])
            + "\n<body>" + MOTEUR.en_tete(t, lc, nav, spec["titre_bande"][lc])
            + "\n<main id=\"contenu\" tabindex=\"-1\">" + "".join(corps) + "</main>"
            + queue + "\n</body>\n</html>\n")


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


def resume(donnees: Dict[str, Any]) -> Dict[str, Any]:
    """Le moteur exige `resume` ; il n'est composé que de ce que la conclusion calcule."""
    c = donnees["conclusion"]
    return {"equations": c["equations"], "controles_ok": c["controles_verts"],
            "controles_total": c["controles_total"], "statuts": c["statuts_par_label"]}


def main() -> int:
    bruts = FB.resoudre()
    if not FB.verifier(bruts):
        raise SystemExit("contrôles non reçus dans fondation_base : la page n'est pas publiée")
    donnees = _titrer(dict(bruts))
    donnees["resume"] = resume(bruts)
    donnees["valeurs_declarees"] = dict(bruts["declare"])

    spec = spec_fondation(donnees)
    ecrits: List[Path] = []
    vues: set = set()
    for lang in MOTEUR.LANGUES:
        cible = ARTEFACTS / "pages" / spec["chemins"][lang]
        MOTEUR.ecrire_chemin(cible, MOTEUR.construire_page(
            spec, formules_traduites(donnees, lang, vues), lang))
        ecrits.append(cible)
    for lang in MOTEUR.LANGUES:
        figure = (ARTEFACTS / "figures"
                  / f"fondation{'' if lang == 'fr' else '_' + lang}.svg")
        MOTEUR.ecrire_svg(spec["figures"][0]["svg"][lang], figure)
        ecrits.append(figure)
    for dossier, nom, contenu in (
        ("donnees", "fondation.json", None),
        ("donnees", "fondation.csv", MOTEUR.lignes_csv_equations(donnees)),
        ("dossiers", "fondation.md", MOTEUR.markdown(donnees, spec)),
    ):
        cible = ARTEFACTS / dossier / nom
        if contenu is None:
            MOTEUR.ecrire_json(donnees, cible)
        elif isinstance(contenu, str):
            MOTEUR.ecrire_chemin(cible, contenu)
        else:
            MOTEUR.ecrire_csv(contenu, cible)
        ecrits.append(cible)
    mortes = sorted(set(FORMULE_TR) - vues)
    if mortes:
        raise SystemExit("clés de formule sans formule correspondante : " + " | ".join(mortes))
    for lang in MOTEUR.LANGUES:
        cible = ARTEFACTS / "pages" / ("index.html" if lang == "fr"
                                       else f"index_{lang}.html")
        MOTEUR.ecrire_chemin(cible, page_index(lang, spec, donnees))
        ecrits.append(cible)
    _verifier_mixte(ecrits)
    MOTEUR.ecrire_json({"version": "1.0",
                        "module": "fondation_base.py",
                        "equations": donnees["resume"]["equations"],
                        "controles_ok": donnees["resume"]["controles_ok"],
                        "controles_total": donnees["resume"]["controles_total"],
                        "statuts": donnees["resume"]["statuts"],
                        "digest_prediction_gel": donnees["conclusion"]["digest_prediction_gel"],
                        "artefacts": sorted(str(p.relative_to(RACINE)).replace("\\", "/")
                                            for p in ecrits)},
                       ARTEFACTS / "donnees" / "etat_generateur.json")
    ecrits.append(ARTEFACTS / "donnees" / "etat_generateur.json")
    print(json.dumps({"equations": donnees["resume"]["equations"],
                      "controles": f"{donnees['resume']['controles_ok']}/"
                                   f"{donnees['resume']['controles_total']}",
                      "artefacts": len(ecrits),
                      "racine": str(ARTEFACTS.relative_to(DEPOT)).replace("\\", "/")},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
