# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""Textes FR/EN/AR de la page publique LABORATOIRE du site al-mizan.world.

Ce module n'arithmétise rien : il dit en trois langues ce que
`HORLOGERIE/horlogerie.py` et `HORLOGERIE/laboratoire.py` calculent. Chaque nombre
énoncé ici est repris d'une ligne calculée ; le garde-fou du moteur
(`verifier_nombres`) refuse une phrase anglaise ou arabe qui avancerait un chiffre
absent du domaine calculé.

Le dépôt scellé porte déjà ses textes français (énoncés des équations, des contrôles,
limites) : ce fichier n'en remplace aucun. Il ajoute le titre d'équation, la formule
en anglais et en arabe, la ligne de lecture, le cheminement, les légendes, les cartes
et le tableau du repère. Ce qui reste en français sur les trois pages — et pourquoi —
est dit à l'étape 10 du cheminement : les énoncés de contrôle et les lignes calculées
sont les chaînes du module scellé, et les réécrire publierait des mots qu'aucun
fichier du dépôt ne porte.
"""
from __future__ import annotations

from typing import Any, Dict, List, Sequence, Tuple


def _3(fr: str, en: str, ar: str) -> Dict[str, str]:
    return {"fr": fr, "en": en, "ar": ar}


def carte(lab: Sequence[str], note: Sequence[str], valeur: str):
    return (_3(lab[0], lab[1], lab[2]), {"fr": valeur, "en": valeur, "ar": valeur},
            _3(note[0], note[1], note[2]))


# ----------------------------------------------------------------------------
# en-tête
# ----------------------------------------------------------------------------
THEME = _3("LABORATOIRE — l'identité d'horloge jouée pas à pas",
           "LABORATORY — the clock identity played step by step",
           "المختبر — هويةُ الساعة تُؤدَّى خطوةً خطوة")

TITRE_BANDE = _3("LABORATOIRE — AL-MIZAN × ASTRO-Q°ODE",
                 "LABORATORY — AL-MIZAN × ASTRO-Q°ODE",
                 "المختبر — الميزان × ASTRO-Q°ODE")

DESCRIPTION = _3(
    "Le dossier HORLOGERIE du dépôt scellé, à l'écran : {eq} équations d'horlogerie "
    "exactes en entiers, {ctrl} contrôles reçus sur {ctrl_total}, un repère de {coord} "
    "coordonnées nommées, une trajectoire à trois axes dont la fermeture se calcule par "
    "pgcd, et une stabilité jugée par écart-type d'Allan contre un bruit déclaré. Aucune "
    "synchronisation physique n'est observée par ces calculs.",
    "The HORLOGERIE dossier of the sealed deposit, on screen: {eq} horology equations "
    "exact in integers, {ctrl} checks met out of {ctrl_total}, a frame of {coord} named "
    "coordinates, a three-axis trajectory whose closure period is computed by gcd, and a "
    "stability judged by Allan deviation against a declared noise. No physical "
    "synchronisation is observed by these calculations.",
    "ملف HORLOGERIE من الإيداع المختوم على الشاشة: {eq} معادلةً في التوقيت دقيقةً في "
    "الأعداد الصحيحة، و{ctrl} تحقُّقًا مستوفًى من {ctrl_total}، ومعْلَمًا من {coord} "
    "إحداثيةً مسماة، ومسارًا من ثلاثة محاور يُحسَب انغلاقُه بالقاسم المشترك الأعظم، "
    "واستقرارًا يُقاس بانحراف آلان مقابل ضجيجٍ مُعلَن. ولا تُلاحَظ في شيءٍ من هذا "
    "مزامنةٌ فيزيائية.")

# ----------------------------------------------------------------------------
# gel de l'équation dont le nombre dépend de la machine
# ----------------------------------------------------------------------------
EQ12_GEL = _3(
    "τ et ses cinq séries de 5 000 ticks sont mesurés sur la machine qui exécute le "
    "calcul ; le dépôt écrit « aucun horodatage » et n'y fait entrer aucun nombre d'hôte. "
    "La page publiée ne porte donc ni τ ni son rapport à la période — voir la limite de "
    "l'équation et le contrat du module.",
    "τ and its five series of 5 000 ticks are measured on the machine running the "
    "calculation; the deposit writes “no timestamp” and lets no host number in. The "
    "published page therefore carries neither τ nor its ratio to the period — see the "
    "equation's own bound and the module's contract.",
    "τ وسلاسلُه الخمس من 5 000 نبضة تُقاس على الآلة التي تنفِّذ الحساب؛ والإيداعُ يكتب "
    "«بلا ختمٍ زمني» ولا يُدخِل إليه عددًا من المضيف. فالصفحةُ المنشورة لا تحمل τ ولا "
    "نسبتَها إلى الدورة — راجِع حدَّ المعادلةِ وعقدَ الوحدة.")

C12_GEL = _3("non publié : nombre dépendant de la machine qui exécute le calcul",
             "not published: a number of the machine running the calculation",
             "غير منشور: عددٌ يعود إلى الآلة التي تنفِّذ الحساب")

# ----------------------------------------------------------------------------
# titres d'équation et lignes de lecture (FR : le titre seulement)
# ----------------------------------------------------------------------------
EQ_TEXT: Dict[str, Dict[str, tuple]] = {
    "EQ-01": {
        "fr": ("Les douze semences rationnelles", ""),
        "en": ("The twelve rational seeds",
               "Twelve declared hours, months and weeks reduce to rational day counts. "
               "The certificate proves the arithmetic of that declaration, not that the "
               "sky agrees with it."),
        "ar": ("البذورُ الاثنتا عشرة النسبية",
               "اثنتا عشرةَ ساعةً وشهرًا وأسبوعًا مُعلَنة تُرَدُّ إلى أيامٍ نسبية. "
               "والشهادةُ تُثبِت حسابَ هذا الإعلان، لا أن السماء تُوافِقه."),
    },
    "EQ-02": {
        "fr": ("dx par quatre niveaux", ""),
        "en": ("dx through four levels",
               "Four products of coefficients and seeds give dx as a fraction over 128. "
               "The two rationals are compared exactly: no tolerance is involved."),
        "ar": ("dx عبر أربعة مستويات",
               "أربعةُ حاصلاتِ ضربٍ من معاملاتٍ وبذور تُعطي dx كسرًا مقامُه 128. "
               "ويُقارَن العددان النسبيان يقينًا: فلا يدخل أيُّ هامشٍ مسموح."),
    },
    "EQ-03": {
        "fr": ("dy par quatre niveaux", ""),
        "en": ("dy through four levels",
               "The same product on the lunar seeds gives dy. The week of 168 hours is "
               "shared with the solar axis, so the ratio dy/dx is not a free parameter."),
        "ar": ("dy عبر أربعة مستويات",
               "الحاصلُ ذاتُه على البذور القمرية يُعطي dy. وأسبوعُ 168 ساعةً مشتركٌ بين "
               "محور القمر ومحور الشمس، فليست النسبة dy/dx معاملًا حرًّا."),
    },
    "EQ-04": {
        "fr": ("dz, son brut et leur rapport", ""),
        "en": ("dz, its raw form and their ratio",
               "dz is the only one of the three landing on an integer, and the raw lunar "
               "axis divided by the normalised one is exactly 144/5."),
        "ar": ("dz وخامُهما ونسبتُهما",
               "dz وحدَه من الثلاثة يستقرُّ على عددٍ صحيح، وخامُ المحور القمري على "
               "المُطبَّع منه يساوي 144/5 يقينًا."),
    },
    "EQ-05": {
        "fr": ("L'identité dt = dx + dy + dz", ""),
        "en": ("The identity dt = dx + dy + dz",
               "The closure of the three axes into the time counter holds through a "
               "cross-product of integers. It says nothing about any clock outside the "
               "arithmetic."),
        "ar": ("الهوية dt = dx + dy + dz",
               "انغلاقُ المحاور الثلاثة في عدّاد الزمن يثبت بضربٍ متصالبٍ للأعداد "
               "الصحيحة. فلا يقول شيئًا عن ساعةٍ خارج الحساب."),
    },
    "EQ-06": {
        "fr": ("Le dénominateur est minimal", ""),
        "en": ("The denominator is minimal",
               "The numerator is odd, so 2^7 is the smallest denominator dt can have. The "
               "numerator is tested odd, not prime — that is all the equation claims."),
        "ar": ("المقامُ أصغريّ",
               "البسطُ فرديٌّ، فـ2^7 أصغرُ مقامٍ يمكن أن يبلغه dt. والبسطُ يُختبَر فرديًّا "
               "لا أوَّليًّا — وهذا وحدَه ما تدّعيه المعادلة."),
    },
    "EQ-07": {
        "fr": ("La période, conséquence d'une hypothèse", ""),
        "en": ("The period, a consequence of a reading",
               "If dt were a frequency, its reciprocal would be a period of 40 digits in "
               "nanoseconds. The deposit observes no cycle counter, so this stays a "
               "specified reading, not a measurement."),
        "ar": ("الدورةُ نتيجةُ فرضيةٍ في القراءة",
               "لو كان dt تردُّدًا لكانت دورتُه عددًا من أربعين رقمًا بالنانو ثانية. "
               "والإيداعُ لا يرصد عدّادَ دورات، فتبقى هذه قراءةً مقرَّرة لا قياسًا."),
    },
    "EQ-08": {
        "fr": ("Des seuils gelés avant lecture", ""),
        "en": ("Thresholds frozen before the read",
               "Nine pairs, three thresholds and a printed seal were fixed before any "
               "comparator was read. The freeze covers the thresholds and the references, "
               "not the sky."),
        "ar": ("حدودٌ جُمِّدت قبل القراءة",
               "تسعُ مقابلاتٍ وثلاثةُ حدودٍ وختمٌ مطبوع ثُبِّتت قبل قراءة أيِّ مقارن. "
               "فالتجميدُ يشمل الحدودَ والمراجع، لا السماء."),
    },
    "EQ-09": {
        "fr": ("Soleil contre année tropique", ""),
        "en": ("Sun against the tropical year",
               "The declared solar cycle misses the mean tropical ephemeris and matches "
               "the Julian definition. A mean calendar compared to a mean ephemeris — "
               "neither is recomputed from today's sky."),
        "ar": ("الشمس مقابل السنة الاستوائية",
               "الدورةُ الشمسية المُعلَنة تُخطئ الاستوائيةَ المتوسطة وتُوافق التعريفَ "
               "اليولياني. فتقويمٌ متوسط يُقارَن بشهادةٍ متوسطة، ولا يُعاد حسابُهما من "
               "سماء اليوم."),
    },
    "EQ-10": {
        "fr": ("Lune contre douze lunaisons", ""),
        "en": ("Moon against twelve synodic months",
               "Twelve synodic months fall outside the tolerance, and a sensitivity test "
               "on the sixth decimal of the month decides whether the verdict holds."),
        "ar": ("القمر مقابل اثنتي عشرة دورةً اقترانية",
               "اثنتا عشرة دورةً اقترانية تخرج عن الهامش المسموح، ويبقى اختبارُ الحساسية "
               "على المنزلة السادسة من العُشر للشهر قائمًا."),
    },
    "EQ-11": {
        "fr": ("Terre contre trois références", ""),
        "en": ("Earth against three references",
               "None of the three earthly comparisons passes the frozen threshold. A "
               "360-day base remains a perfectly lawful computing base; the certificate "
               "only reports what it does not match."),
        "ar": ("الأرض مقابل ثلاثة مراجع",
               "لا تنجح مقارنةٌ واحدة من ثلاثٍ أرضيةٍ في الحدِّ المجمَّد. فأساسُ ثلاثمئة "
               "وستين يومًا يبقى أساسَ حسابٍ مشروعًا تمامًا؛ والشهادة لا تُبلِّغ إلا ما لا "
               "تُوافِقه."),
    },
    "EQ-12": {
        "fr": ("Le rythme d'exécution, hors scellement", ""),
        "en": ("The running pace, outside the seal",
               "Five series of 5 000 ticks measure how long the counter really takes. "
               "That number depends on the machine, the interpreter and the load, so the "
               "deposit keeps it out of the sealed bytes — see the frozen line below."),
        "ar": ("إيقاعُ التنفيذ خارج الختم",
               "خمسُ سلاسلَ من 5 000 نبضة تقيس ما يستغرقه العدّاد فعلًا. وهذا العدد يتوقّف "
               "على الآلة والمُفسِّر والحِمل، فأبقاه الإيداعُ خارج المختومات — راجِع السطر "
               "المُجمَّد أدناه."),
    },
    "EQ-13": {
        "fr": ("Quatre énoncés du même nombre", ""),
        "en": ("Four statements of one number",
               "The living library, LA TABLE and the sealed act A136 write the same "
               "rational bit for bit. The confrontation covers what the deposit writes; it "
               "does not make the number physical."),
        "ar": ("أربعةُ تصريحاتٍ لعددٍ واحد",
               "المكتبةُ الحيّة وLA TABLE والفعلُ A136 المختوم يكتبون النسبةَ نفسها بتّةً "
               "بتّة. فالمواجهةُ تشمل ما يكتبه الإيداع، ولا تجعل العددَ فيزيائيًّا."),
    },
    "EQ-14": {
        "fr": ("Un certificat qui se relit sans le dépôt", ""),
        "en": ("A certificate read without the deposit",
               "A second verifier recomputes the root from the file alone, without a "
               "single import from the module that produced it, and refuses a mutated "
               "field. It proves the file reads: it proves no physics."),
        "ar": ("شهادةٌ تُعاد قراءتُها بلا الإيداع",
               "مُتحقِّقٌ ثانٍ يُعيد حساب الجذر من الملف وحده دون استيراد سطرٍ واحد من "
               "الوحدة التي أنتجته، ويرفض حقلًا مُبَدَّلًا. فيُثبِت أن الملف يُقرأ، ولا "
               "يُثبِت فيزياء."),
    },
    "EQ-15": {
        "fr": ("La cohérence interne des sources", ""),
        "en": ("The internal coherence of the sources",
               "Twelve synodic months equal twelve times the mean month, and every "
               "fraction of the file matches the decimal it cites. This is a citation "
               "check — the guard that caught the error of 2026-11-09."),
        "ar": ("تلاؤمُ المصادر ذاتيًّا",
               "اثنتا عشرة دورةً اقترانية تساوي اثنتي عشرة مرةً الشهرَ المتوسط، وكلُّ كسرٍ "
               "في الملف يُطابق العشرية التي يستشهد بها. وهذا تحقُّقُ استشهاد — وهو الذي "
               "أمسك خطأَ 2026-11-09."),
    },
}

# ----------------------------------------------------------------------------
# formules : le français est comparé au dépôt, l'anglais et l'arabe ne déplacent
# ni un chiffre ni un symbole
# ----------------------------------------------------------------------------
FORMULE_FR: Dict[str, str] = {
    "EQ-01": "A, M, S ∈ ℚ par astre, et A/24 donne les jours déclarés",
    "EQ-02": "dx = (5/2·8766/12)·(3/2·(1461/2)/168)·(3/2·168/24)·(24/60)",
    "EQ-03": "dy = (5/2·8496/12)·(3/2·708/168)·(3/2·168/24)·(24/60)",
    "EQ-04": ("dz = 216 000·250·5/2 ; dz_brut = (300·8640/12)·(50·720/144)·(30·144/24)"
              "·(24/60)"),
    "EQ-05": "dt = dx + dy + dz",
    "EQ-06": ("den(dt) = 2^7 et num(dt) impair ⇒ fraction réduite et dénominateur "
              "minimal"),
    "EQ-07": "si dt est une fréquence : 1/dt = 128·10^9/17 292 418 731 ns",
    "EQ-08": ("seuils gelés avant lecture : ≤ 60 s/an · ≤ 3 600 s/an · au-delà HORS "
              "TOLÉRANCE"),
    "EQ-09": "Soleil 365,25 j contre année tropique 365,2422 j",
    "EQ-10": "Lune 354 j contre douze lunaisons 354,36708 j",
    "EQ-11": "Terre 360 j contre les trois références disponibles",
    "EQ-12": "τ = T/N sur consommer_tick(), cinq séries de cinq mille ticks",
    "EQ-13": "lib_temporelle ≡ lib_informe ≡ acte A136 scellé ≡ certificat",
    "EQ-14": ("un certificat se relit sans exécuter le dépôt : racine = SHA-256 des six "
              "empreintes"),
    "EQ-15": ("lunaisons_12 = 12 × lunaison, et chaque fraction du fichier est la "
              "décimale citée"),
}

FORMULE_TR: Dict[str, Tuple[str, str]] = {
    "EQ-01": ("A, M, S ∈ ℚ per body, and A/24 gives the declared days",
              "A وM وS ∈ ℚ لكلِّ جرمٍ، وA/24 يعطي الأيامَ المُعلَنة"),
    "EQ-02": ("dx = (5/2·8766/12)·(3/2·(1461/2)/168)·(3/2·168/24)·(24/60)",
              "dx = (5/2·8766/12)·(3/2·(1461/2)/168)·(3/2·168/24)·(24/60)"),
    "EQ-03": ("dy = (5/2·8496/12)·(3/2·708/168)·(3/2·168/24)·(24/60)",
              "dy = (5/2·8496/12)·(3/2·708/168)·(3/2·168/24)·(24/60)"),
    "EQ-04": ("dz = 216 000·250·5/2 ; dz_brut = (300·8640/12)·(50·720/144)·(30·144/24)"
              "·(24/60)",
              "dz = 216 000·250·5/2 ; dz_brut = (300·8640/12)·(50·720/144)·(30·144/24)"
              "·(24/60)"),
    "EQ-05": ("dt = dx + dy + dz", "dt = dx + dy + dz"),
    "EQ-06": ("den(dt) = 2^7 and num(dt) odd ⇒ reduced fraction and minimal denominator",
              "den(dt) = 2^7 والبسطُ فرديٌّ ⇒ الكسرُ مُختزَلٌ والمقامُ أصغريّ"),
    "EQ-07": ("if dt is a frequency: 1/dt = 128·10^9/17 292 418 731 ns",
              "إن كان dt تردُّدًا: 1/dt = 128·10^9/17 292 418 731 ns"),
    "EQ-08": ("thresholds frozen before the read: ≤ 60 s/yr · ≤ 3 600 s/yr · beyond, "
              "OUT OF TOLERANCE",
              "حدودٌ جُمِّدت قبل القراءة: ≤ 60 ث/سنة · ≤ 3 600 ث/سنة · وما جاوزَها خارج "
              "التحمُّل"),
    "EQ-09": ("Sun 365,25 d against the tropical year 365,2422 d",
              "الشمس 365,25 يومًا مقابل السنة الاستوائية 365,2422 يومًا"),
    "EQ-10": ("Moon 354 d against twelve synodic months 354,36708 d",
              "القمر 354 يومًا مقابل اثنتي عشرة دورةً اقترانية 354,36708 يومًا"),
    "EQ-11": ("Earth 360 d against the three available references",
              "الأرض 360 يومًا مقابل المراجع الثلاثة المتوافرة"),
    "EQ-12": ("τ = T/N on consommer_tick(), five series of five thousand ticks",
              "τ = T/N على consommer_tick()، خمسُ سلاسلَ من خمسة آلاف نبضة"),
    "EQ-13": ("lib_temporelle ≡ lib_informe ≡ sealed act A136 ≡ certificate",
              "lib_temporelle ≡ lib_informe ≡ الفعلُ A136 المختوم ≡ الشهادة"),
    "EQ-14": ("a certificate is re-read without running the deposit: root = SHA-256 of "
              "the six seals",
              "شهادةٌ تُعاد قراءتُها بلا تشغيل الإيداع: الجذرُ = SHA-256 للأختام الستة"),
    "EQ-15": ("lunaisons_12 = 12 × lunaison, and every fraction of the file is the "
              "decimal it cites",
              "lunaisons_12 = 12 × lunaison، وكلُّ كسرٍ في الملف هو العشريةُ التي يستشهد "
              "بها"),
}


def formules_traduites(donnees: Dict[str, Any], lang: str, vues: set) -> Dict[str, Any]:
    """Version « lang » du dictionnaire de calcul : la formule change, rien d'autre.

    La formule française est d'abord comparée à `FORMULE_FR` : si le dépôt scellé en
    change un mot, la traduction ne suit pas silencieusement, le générateur s'arrête.
    """
    if lang == "fr":
        return donnees
    index = 0 if lang == "en" else 1
    eqs: List[Dict[str, Any]] = []
    for e in donnees["equations"]:
        cle = e["id"]
        if cle not in FORMULE_TR:
            raise SystemExit(f"formule sans traduction pour {lang} : {cle}")
        if FORMULE_FR[cle] != e["formule"]:
            raise SystemExit(f"{cle} : la formule du dépôt a changé — {e['formule']!r}")
        vues.add(cle)
        copie = dict(e)
        copie["formule"] = FORMULE_TR[cle][index]
        eqs.append(copie)
    autre = dict(donnees)
    autre["equations"] = eqs
    return autre


# ----------------------------------------------------------------------------
# cheminement
# ----------------------------------------------------------------------------
CHEMINEMENT: List[Dict[str, tuple]] = [
    {
        "fr": ("Ce que la page publie, et d'où cela vient",
               "Chaque valeur affichée sort d'un fichier du dépôt `ZENODO_DEPOT_ALMIZAN`, "
               "vérifié au SHA-256 contre `MANIFESTE_SHA256.txt` avant lecture. Les JSON, "
               "CSV et SVG servis à côté des pages sont ces mêmes fichiers, copiés octet "
               "pour octet : ce que le visiteur lit en données est ce que porte l'archive "
               "du DOI."),
        "en": ("What the page publishes, and where it comes from",
               "Every displayed value leaves a file of the `ZENODO_DEPOT_ALMIZAN` deposit, "
               "checked against `MANIFESTE_SHA256.txt` by SHA-256 before it is read. The "
               "JSON, CSV and SVG served beside the pages are those same files, copied "
               "byte for byte: the data a visitor reads is what the DOI archive carries."),
        "ar": ("ما تنشره الصفحة ومن أين يأتي",
               "كلُّ قيمةٍ ظاهرة تخرج من ملفٍ في إيداع `ZENODO_DEPOT_ALMIZAN` يُتحقَّق منه "
               "بـ SHA-256 مقابل `MANIFESTE_SHA256.txt` قبل قراءته. وملفات JSON وCSV وSVG "
               "المقدَّمة بجوار الصفحات هي تلك الملفات ذاتها منسوخةً بتّةً بتّة: فبياناتُ ما "
               "يقرأه الزائر هي ما تحمله أرشيفُ المعرِّف."),
    },
    {
        "fr": ("Un compteur, pas une horloge du ciel",
               "Le module avance trois compteurs d'espace et un compteur de temps de dx, "
               "dy, dz et dt. À chaque pas, x + y + z − k·dt rend un résidu entier, et ce "
               "résidu vaut 0 : c'est l'identité, jouée. Rien n'est synchronisé avec un "
               "temps physique, et le module l'écrit dans chacune de ses sorties."),
        "en": ("A counter, not a clock of the sky",
               "The module advances three space counters and one time counter by dx, dy, "
               "dz and dt. At every step x + y + z − k·dt returns an integer residue, and "
               "that residue is 0: the identity, played. Nothing is synchronised with any "
               "physical time, and the module says so in each of its outputs."),
        "ar": ("عدّادٌ لا ساعةُ سماء",
               "تقدِّم الوحدةُ ثلاثةَ عدّاداتِ مكانٍ وعدّادَ زمانٍ بمقدار dx وdy وdz وdt. "
               "فيُعطي x + y + z − k·dt عند كلِّ خطوةٍ باقيًا صحيحًا، وهذا الباقي يساوي "
               "صفرًا: فهي الهوية مُؤدّاة. ولا يتزامن شيءٌ مع زمنٍ فيزيائي، والوحدةُ تقول "
               "ذلك في كلِّ مخرجاتها."),
    },
    {
        "fr": ("La fermeture se calcule, elle ne s'observe pas sur la figure",
               "La période d'un axe est dt divisé par le pgcd du pas de cet axe et de dt ; "
               "la fermeture commune est le ppcm des trois périodes. La figure ne montre "
               "qu'un préfixe de la trajectoire : ce qu'elle dessine est une fraction du "
               "cycle, pas le cycle entier."),
        "en": ("The closure is computed, not seen on the figure",
               "An axis period is dt divided by the gcd of that axis's step and dt; the "
               "common closure is the lcm of the three periods. The figure shows only a "
               "prefix of the trajectory: what it draws is a fraction of the cycle, not "
               "the whole cycle."),
        "ar": ("الانغلاقُ يُحسَب ولا يُرى في الشكل",
               "دورةُ المحور هي dt على القاسم المشترك الأعظم لخطوة ذلك المحور وdt؛ "
               "والانغلاقُ المشترك هو المضاعف المشترك الأصغر للدورات الثلاث. والشكلُ لا "
               "يُظهر إلا طليعةَ المسار: فمرسومُه جزءٌ من الدورة لا الدورةُ كلُّها."),
    },
    {
        "fr": ("Un repère de quatorze coordonnées nommées",
               "Quatorze nombres, chacun pris tel quel dans le dépôt scellé ou mesuré sur "
               "l'hôte. C'est un système de coordonnées défini par convention de listing : "
               "rien ici ne revendique quatorze dimensions physiques. Le contrôle L03 porte "
               "le compte, le contrôle L05 l'origine de chaque ligne."),
        "en": ("A frame of fourteen named coordinates",
               "Fourteen numbers, each taken as it stands from the sealed deposit or "
               "measured on the host. This is a coordinate system defined by a listing "
               "convention: nothing here claims fourteen physical dimensions. Check L03 "
               "carries the count and check L05 the source of each line."),
        "ar": ("معْلَمٌ من أربعَ عشرةَ إحداثيةً مسماة",
               "أربعةَ عشرَ عددًا، كلٌّ منها مأخوذٌ كما هو من الإيداع المختوم أو مقاسٌ على "
               "المضيف. فهذا نظامُ إحداثياتٍ يُحدَّد بعُرف الجرد: فلا يدّعي شيءٌ هنا أربعة "
               "عشر بُعدًا فيزيائيًّا. والتحقُّقُ L03 يحمل العدَّ، وL05 مصدرَ كلِّ سطر."),
    },
    {
        "fr": ("La stabilité d'abord sur une série simulée",
               "Un bruit d'amplitude déclarée est injecté à dessein dans une série de "
               "4 000 fenêtres, puis l'écart-type d'Allan est calculé sur ces fenêtres. "
               "L'instrument doit retrouver l'amplitude qu'il a lui-même déclarée : sinon "
               "c'est son instrument qui est faux, pas le ciel qui est stable."),
        "en": ("Stability first on a simulated series",
               "A noise of declared amplitude is deliberately injected into a series of "
               "4 000 windows, and the Allan deviation is computed over those windows. The "
               "instrument must recover the amplitude it declared itself: otherwise it is "
               "the instrument that is wrong, not the sky that is steady."),
        "ar": ("الاستقرارُ أولًا على سلسلةٍ محاكاة",
               "يُحقَن ضجيجٌ بسَّعةٍ مُعلَنة عمدًا في سلسلةٍ من 4 000 نافذة، ثم يُحسَب "
               "انحراف آلان على تلك النوافذ. وعلى الأداة أن تستعيد السَّعة التي أعلنتها هي: "
               "وإلا فالأداةُ هي الخاطئة، لا السماءُ هي المستقرة."),
    },
    {
        "fr": ("La même formule sur une machine réelle ne caractérise que la machine",
               "Rejouer le calcul sur des ticks comptés ne dit rien de l'horloge du dépôt : "
               "cela dit ce que vaut l'hôte à cet instant. Le dépôt exclut donc ce nombre "
               "de ses octets scellés, et la page publiée le gèle : la ligne de lecture en "
               "porte la règle, jamais la valeur."),
        "en": ("The same formula on a real machine characterises only that machine",
               "Rerunning the calculation on counted ticks says nothing about the "
               "deposit's clock: it says what the host is worth at that moment. The "
               "deposit therefore keeps that number out of its sealed bytes, and the "
               "published page freezes it — the reading line carries the rule, never the "
               "value."),
        "ar": ("الصيغةُ ذاتها على آلةٍ حقيقية لا تصف إلا تلك الآلة",
               "إعادةُ الحساب على نبضاتٍ معدودة لا تقول شيئًا عن ساعة الإيداع: إنما تقول ما "
               "يساويه المضيفُ في تلك اللحظة. فلذلك يُخرج الإيداعُ هذا العددَ من مختوماته، "
               "وتُجمِّده الصفحةُ المنشورة: فسطرُ القراءة يحمل القاعدةَ لا القيمة."),
    },
    {
        "fr": ("Une confrontation astronomique dont le verdict est défavorable",
               "Six comparaisons à une éphéméride mesurée : aucune ne tombe sous les 60 "
               "secondes par an. En revanche 365,25 j est exactement l'année julienne et "
               "354 j exactement l'année lunaire civile. La page publie le verdict "
               "défavorable tel quel : ce sont des calendriers, pas des mesures."),
        "en": ("An astronomical confrontation with an unfavourable verdict",
               "Six comparisons against measured ephemerides: none falls under 60 seconds "
               "a year. Yet 365.25 days is exactly the Julian year and 354 exactly the "
               "civil lunar year. The page publishes the unfavourable verdict as it is: "
               "these are calendars, not measurements."),
        "ar": ("مواجهةٌ فلكيةٌ حكمُها غيرُ صالح",
               "ستُّ مواجهاتٍ مع شهاداتٍ مقيسة: فلا تنخفض واحدةٌ منها دون ستين ثانيةً في "
               "السنة. ومع ذلك فـ365.25 يومًا هي السنةُ اليوليانية يقينًا، و354 هي السنةُ "
               "القمرية المدنية يقينًا. وتنشر الصفحةُ الحكمَ غير الصالح كما هو: فتلك تقاويمُ "
               "لا قياسات."),
    },
    {
        "fr": ("Un second vérificateur qui n'importe pas le dépôt",
               "`verifier_certificats.py` relit le fichier et recalcule la racine sans "
               "importer une seule ligne du module qui l'a produit, puis refuse un champ "
               "muté. Cette garde est ce qui distingue un scellement d'une habitude."),
        "en": ("A second verifier that does not import the deposit",
               "`verifier_certificats.py` re-reads the file and recomputes the root "
               "without importing a single line from the module that produced it, then "
               "refuses a mutated field. That guard is what separates a seal from a habit."),
        "ar": ("مُتحقِّقٌ ثانٍ لا يستورد الإيداع",
               "يعيد `verifier_certificats.py` قراءةَ الملف ويُعيد حساب الجذر دون استيراد "
               "سطرٍ واحد من الوحدة التي أنتجته، ثم يرفض حقلًا مُبَدَّلًا. وهذه الحراسةُ هي "
               "ما يفصل الختمَ عن العادة."),
    },
    {
        "fr": ("Ce que rien ici ne revendique",
               "Aucune prévision astronomique, aucune dimension physique nouvelle, aucun "
               "horodatage dans les octets scellés, aucune preuve que le compteur tienne "
               "quelque chose du ciel. Les limites sont écrites dans le fichier et "
               "reproduites sur la page, pas dans une note à part."),
        "en": ("What nothing here claims",
               "No astronomical prediction, no new physical dimension, no timestamp inside "
               "the sealed bytes, no proof that the counter holds anything of the sky. The "
               "limits are written in the file and reproduced on the page, not in a side "
               "note."),
        "ar": ("ما لا يدّعيه شيءٌ هنا",
               "لا تنبُّؤَ فلكي، ولا بُعدًا فيزيائيًّا جديدًا، ولا ختمًا زمنيًّا داخل "
               "المختومات، ولا برهانَ أن العدّاد يمسك شيئًا من السماء. والحدودُ مكتوبةٌ في "
               "الملف ومُعادةٌ على الصفحة، لا في هامشٍ جانبي."),
    },
    {
        "fr": ("La langue des énoncés et des lignes calculées",
               "Les formules, les titres d'équation, les lignes de lecture, le cheminement, "
               "les légendes et les cartes existent en trois langues. Les vingt énoncés de "
               "contrôle et les lignes calculées, eux, restent en français : ce sont les "
               "chaînes que le module scellé produit et que le manifeste protège. Une page "
               "anglaise ou arabe qui les réécrirait affirmerait des mots qu'aucun fichier "
               "du dépôt ne porte."),
        "en": ("The language of the statements and the computed lines",
               "The formulas, equation titles, reading lines, reasoning, captions and "
               "cards exist in three languages. The twenty control statements and the "
               "computed lines stay in French: they are the strings the sealed module "
               "writes and the manifest protects. An English or Arabic page rewriting them "
               "would assert words no file of the deposit carries."),
        "ar": ("لغةُ العباراتِ والأسطرِ المحسوبة",
               "الصيغُ وعناوينُ المعادلات وأسطرُ القراءة ومسارُ الاستدلال والتعليقاتُ "
               "والبطاقات موجودةٌ بثلاث لغات. أمّا عباراتُ التحقق العشرين والأسطرُ "
               "المحسوبةُ فتبقى بالفرنسية: فهي النصوصُ التي تكتبها الوحدةُ المختومة ويحميها "
               "البيان. ولو أعادت كتابةَها صفحةٌ إنجليزيةٌ أو عربيةٌ لثبّتت كلماتٍ لا "
               "يحملها أيُّ ملفٍ في الإيداع."),
    },
]

# ----------------------------------------------------------------------------
# sources, fil conducteur, commandes
# ----------------------------------------------------------------------------
FIL_CONDUCTEUR = ("Semences déclarées du dépôt → produit de quatre niveaux → "
                  "identité dt = dx + dy + dz → période sous hypothèse de lecture → "
                  "confrontation à six éphémérides → vérificateur autonome")

SOURCES = _3(
    "Le dossier naît d'une vidéo publique (Adem B10, « AI Proved His 18-Year-Old "
    "Conjecture. He Hasn't Understood It Yet. », 593 s, huit chapitres horodatés), sondée "
    "le 2026-11-09T15:32:44Z. Aucun transcript n'a été obtenu : aucune phrase, aucune "
    "citation et aucun nombre ne lui est donc attribué. Les repères extérieurs cités sont "
    "l'Union astronomique internationale, la NASA Glenn Research Center, l'Explanatory "
    "Supplement to the Astronomical Almanac et Wikipédia pour l'année tropique, chacun "
    "repris avec sa source nommée.",
    "The dossier grows out of one public video (Adem B10, “AI Proved His 18-Year-Old "
    "Conjecture. He Hasn't Understood It Yet.”, 593 s, eight timestamped chapters), probed "
    "on 2026-11-09T15:32:44Z. No transcript was obtained, so no sentence, no quotation and "
    "no number is attributed to it. The external references cited are the International "
    "Astronomical Union, NASA Glenn Research Center, the Explanatory Supplement to the "
    "Astronomical Almanac and Wikipedia for the tropical year, each taken with its named "
    "source.",
    "ينشأ هذا الملف من فيديو عامٍّ واحد (Adem B10، «AI Proved His 18-Year-Old Conjecture. "
    "He Hasn't Understood It Yet»، 593 ثانية، وثمانية فصولٍ مؤرَّخة)، رُصِد في "
    "2026-11-09T15:32:44Z. ولم يُحصَل نصُّ كلام، فلا تُنسَب إليه عبارةٌ ولا اقتباسٌ ولا عدد. "
    "واما المراجع الخارجية المذكورة فهي الاتحاد الفلكي الدولي، ومركز ناسا غلين، والملحق "
    "الشارح للقائمة الفلكية، وويكيبيديا للسنة الاستوائية — كلٌّ بمصدره المسمّى.",
)

COMMANDES = _3(
    "cd ZENODO_DEPOT_ALMIZAN\n"
    "py -3 HORLOGERIE/horlogerie.py                      # 15 équations, 15 contrôles\n"
    "py -3 HORLOGERIE/verifier_certificats.py            # relit le certificat sans le dépôt\n"
    "py -3 HORLOGERIE/laboratoire.py --pas 4096          # trajectoire, repère, stabilité\n"
    "py -3 HORLOGERIE/laboratoire.py --en-direct --secondes 20 --ticks 50000\n"
    "cd HORLOGERIE && py -3 -m unittest tests.test_horlogerie tests.test_laboratoire\n"
    "py -3 -m OUTILS.sceller_manifeste --verifier        # re-hache chaque entrée scellée",
    "cd ZENODO_DEPOT_ALMIZAN\n"
    "py -3 HORLOGERIE/horlogerie.py                      # 15 equations, 15 checks\n"
    "py -3 HORLOGERIE/verifier_certificats.py            # re-reads the certificate alone\n"
    "py -3 HORLOGERIE/laboratoire.py --pas 4096          # trajectory, frame, stability\n"
    "py -3 HORLOGERIE/laboratoire.py --en-direct --secondes 20 --ticks 50000\n"
    "cd HORLOGERIE && py -3 -m unittest tests.test_horlogerie tests.test_laboratoire\n"
    "py -3 -m OUTILS.sceller_manifeste --verifier        # re-hashes every sealed entry",
    "cd ZENODO_DEPOT_ALMIZAN\n"
    "py -3 HORLOGERIE/horlogerie.py                      # 15 معادلة و15 تحقُّقًا\n"
    "py -3 HORLOGERIE/verifier_certificats.py            # يعيد قراءة الشهادة وحدها\n"
    "py -3 HORLOGERIE/laboratoire.py --pas 4096          # المسار والمعلَم والاستقرار\n"
    "py -3 HORLOGERIE/laboratoire.py --en-direct --secondes 20 --ticks 50000\n"
    "cd HORLOGERIE && py -3 -m unittest tests.test_horlogerie tests.test_laboratoire\n"
    "py -3 -m OUTILS.sceller_manifeste --verifier        # يُعيد تجزئة كل مدخل موقَّع",
)

# ----------------------------------------------------------------------------
# figures
# ----------------------------------------------------------------------------
FIG_ECARTS_TITRE = _3("Écart maximal par cycle déclaré, en secondes par an",
                      "Largest gap per declared cycle, in seconds a year",
                      "أقصى فارقٍ لكلِّ دورةٍ مُعلَنة، بالثانية في السنة")

FIG_ECARTS_DESC = _3(
    "Trois barres : le plus grand écart annuel retenu pour le Soleil, la Lune et la Terre "
    "contre les éphémérides publiées. Toutes trois dépassent le seuil gelé de 60 secondes "
    "par an ; à cette échelle le seuil tient sur un cheveu et n'est pas tracé.",
    "Three bars: the largest annual gap kept for the Sun, the Moon and the Earth against "
    "the published ephemerides. All three exceed the threshold frozen at 60 seconds a "
    "year; at this scale the threshold is a hair wide, so it is not drawn.",
    "ثلاثةُ أعمدة: أكبرُ فارقٍ سنويٍّ المحتفَظ به للشمس والقمر والأرض مقابل الشهادات "
    "المنشورة. وكلُّها يتجاوز الحدَّ المجمَّد عند 60 ثانيةً في السنة؛ وعلى هذا المقياس لا "
    "يُرسم الحدُّ لدقّته.",
)

FIG_ECARTS_SERIES: Dict[str, Tuple[str, str, str]] = {
    "Soleil": ("Soleil → année tropique", "Sun → tropical year",
               "الشمس ← السنة الاستوائية"),
    "Lune": ("Lune → douze lunaisons", "Moon → twelve synodic months",
             "القمر ← اثنتا عشرة دورةً اقترانية"),
    "Terre": ("Terre → pire des trois", "Earth → worst of three",
              "الأرض ← أسوأُ الثلاثة"),
}

FIG_ECARTS_LEGENDE = _3(
    "Le plus grand écart retenu par cycle, en secondes par an : {soleil} pour le Soleil, "
    "{lune} pour la Lune, {terre} pour la Terre. Le seuil gelé est à {seuil} s/an, et "
    "aucun des trois ne le tient.",
    "The largest gap kept per cycle, in seconds a year: {soleil} for the Sun, {lune} for "
    "the Moon, {terre} for the Earth. The frozen threshold is {seuil} s a year, and not "
    "one of the three holds.",
    "أكبرُ فارقٍ محتفَظ به لكلِّ دورة، بالثانية في السنة: {soleil} للشمس و{lune} للقمر "
    "و{terre} للأرض. والحدُّ المجمَّد عند {seuil} ث/سنة، ولا واحدَ من الثلاثة يُمسكه.",
)

FIG_STAB_TITRE = _3("L'instrument retrouve-t-il le bruit qu'il déclare ?",
                    "Does the instrument recover the noise it declares?",
                    "هل تستعيد الأداةُ الضجيجَ الذي تُعلنه؟")

FIG_STAB_DESC = _3(
    "Deux barres et une limite : l'amplitude de bruit injectée à dessein dans la série, "
    "puis l'écart-type d'Allan mesuré sur cette même série. La ligne pointillée est la "
    "borne haute de l'accord, calculée avant la mesure.",
    "Two bars and one limit: the noise amplitude deliberately injected into the series, "
    "then the Allan deviation measured on that same series. The dashed line is the upper "
    "bound of the agreement, computed before the measure.",
    "عمودان وحدٌّ: سَّعةُ الضجيج المحقون عمدًا في السلسلة، ثم انحرافُ آلان المقيس على "
    "السلسلة ذاتها. والخطُّ المتقطّع هو الحدُّ الأعلى للاتفاق، المحسوبُ قبل القياس.",
)

FIG_STAB_SERIES: Dict[str, Tuple[str, str, str]] = {
    "eps": ("bruit injecté ε", "injected noise ε", "الضجيجُ المحقون ε"),
    "adev": ("écart-type d'Allan mesuré", "Allan deviation measured",
             "انحرافُ آلان المقيس"),
}

FIG_STAB_LEGENDE = _3(
    "Bruit injecté {eps} ; écart-type d'Allan mesuré {adev} ; accord exigé entre {basse} "
    "et {haute}. L'instrument retrouve l'amplitude qu'il déclare.",
    "Injected noise {eps} ; Allan deviation measured {adev} ; agreement required between "
    "{basse} and {haute}. The instrument recovers the amplitude it declares.",
    "ضجيجٌ محقونٌ {eps}؛ وانحرافُ آلان المقيس {adev}؛ والاتفاقُ مطلوبٌ بين {basse} و{haute}. "
    "فالأداةُ تستعيد السَّعة التي تُعلنها.",
)

IMG_TRAJECTOIRE_ALT = _3(
    "Trajectoire à trois axes produite par le dépôt : {pas} pas sur une fermeture commune "
    "de {fermeture} pas.",
    "Three-axis trajectory produced by the deposit: {pas} steps over a common closure of "
    "{fermeture} steps.",
    "مسارٌ من ثلاثة محاور أنتجه الإيداع: {pas} خطوةً في انغلاقٍ مشتركٍ من {fermeture} "
    "خطوة.",
)

IMG_LEGENDE = _3(
    "Le tracé du dépôt lui-même, servi octet pour octet depuis `HORLOGERIE/artefacts/` : "
    "{pas} pas d'une fermeture calculée à {fermeture} pas, soit {tours} tours de la "
    "trajectoire complète. La figure ci-dessus, elle, est dessinée par le moteur de pages.",
    "The deposit's own plot, served byte for byte from `HORLOGERIE/artefacts/`: {pas} "
    "steps of a closure computed at {fermeture} steps, that is {tours} turns of the whole "
    "trajectory. The figure above, by contrast, is drawn by the page engine.",
    "مخطَّطُ الإيداع نفسه، مُقدَّمًا بتّةً بتّة من `HORLOGERIE/artefacts/`: {pas} خطوةً من "
    "انغلاقٍ محسوبٍ عند {fermeture} خطوة، أي {tours} دورةً من المسار الكامل. أمّا الشكلُ "
    "أعلاه فيرسمه محرِّكُ الصفحات.",
)

CAPTION_MATIERAUX = _3(
    "Les quatorze coordonnées du repère, dans l'ordre du fichier scellé. La colonne de "
    "quantité recopie la valeur telle que le dépôt l'écrit — y compris les deux valeurs "
    "non produites, que le dépôt écrit en français faute de nombre d'hôte ; la colonne "
    "d'équation renvoie à la ligne de cette page qui la produit. Les formulations "
    "complètes et le statut de chaque coordonnée — opérationnel, spécifié ou simulé — sont "
    "dans `laboratoire_resultats.json`, copié octet pour octet de l'artefact scellé.",
    "The fourteen coordinates of the frame, in the order of the sealed file. The quantity "
    "column copies the value as the deposit writes it — including the two values left "
    "unproduced, which the deposit writes in French for want of a host number; the "
    "equation column points back to the line of this page that produces it. The full "
    "wordings and the status of every coordinate — operational, specified or simulated — "
    "are in `laboratoire_resultats.json`, copied byte for byte from the sealed artefact.",
    "الإحداثياتُ الأربعَ عشرةَ للمعْلَم بترتيب الملف المختوم. وعمودُ الكمية ينسخ القيمة كما "
    "يكتبها الإيداع — بما في ذلك القيمتَان غيرُ المُنتَجَتَين، اللتان يكتبهما بالفرنسية "
    "لعَدَدٍ من المضيف؛ ويعودُ عمودُ المعادلة إلى سطر هذه الصفحة الذي يُنتِجها. والصيغُ "
    "الكاملة ومرتبةُ كلِّ إحداثية — عاملةٌ أو مقرَّرةٌ أو محاكاة — في "
    "`laboratoire_resultats.json` المنسوخ بتّةً بتّة من المُخرَج المختوم.",
)

NOTE_HOTE = _3(
    "Ce que l'hôte mesure vraiment n'est pas sur cette page : il dépend de la machine qui "
    "exécute. La production publie néanmoins le nombre d'horloge qu'elle dérive elle-même, "
    "à l'adresse `/api/v1/synchronisation/totale` — lecture publique, sans clé.",
    "What the host actually measures is not on this page: it belongs to the machine "
    "running the calculation. Production nevertheless publishes the clock number it "
    "derives itself, at `/api/v1/synchronisation/totale` — a public read, no key.",
    "ما يقيسه المضيفُ فعلًا ليس في هذه الصفحة: إنه للآلة التي تنفِّذ. ومع ذلك تنشر "
    "البيئةُ الحيّة عددَ الساعة الذي تشتقّه بنفسها على `/api/v1/synchronisation/totale` — "
    "قراءةٌ عامّة بلا مفتاح.",
)

# ----------------------------------------------------------------------------
# cartes : valeurs reprises telles quelles du calcul, notes traduites
# ----------------------------------------------------------------------------
def cartes(v: Dict[str, str]) -> List[Any]:
    """Dix cartes. `v` porte les chaînes déjà écrites par les modules du dépôt."""
    def n(trio: Sequence[str]) -> List[str]:
        return [trio[i].format(**v) for i in range(3)]

    return [
        carte(("l'identité dt en entiers", "dt as integers, in the identity",
               "الهوية dt في الأعداد الصحيحة"),
              n(("dx + dy + dz rendu sans arrondi : la fraction est celle que quatre "
                 "produits d'entiers produisent, et la fermeture tombe au pas "
                 "{fermeture}.",
                 "dx + dy + dz returned with no rounding: the fraction is the one four "
                 "products of integers produce, and the closure falls at step "
                 "{fermeture}.",
                 "يُعيد dx + dy + dz بلا تقريب: فالنسبةُ هي التي تُنتجها أربعةُ حاصلاتِ "
                 "ضربٍ للأعداد الصحيحة، ويقع الانغلاقُ عند الخطوة {fermeture}.")),
              v["dt"]),
        carte(("fermeture commune des trois axes", "common closure of the three axes",
               "الانغلاقُ المشترك للمحاور الثلاثة"),
              n(("le ppcm des trois périodes d'axes, en pas de compteur. C'est un nombre de "
                 "pas, ni un temps ni une fréquence.",
                 "the lcm of the three axis periods, in counter steps. It is a step count, "
                 "neither a time nor a frequency.",
                 "المضاعفُ المشترك الأصغر لدورات المحاور الثلاثة، بخطوات العدّاد. فهو عددُ "
                 "خطواتٍ لا زمنٌ ولا تردُّد.")),
              v["fermeture"]),
        carte(("résidu maximal sur la trajectoire", "largest residue on the trajectory",
               "أقصى باقٍ على المسار"),
              n(("{residu} en valeur absolue au maximum, sur les {pas} pas dessinés : "
                 "l'identité x + y + z − k·dt est tenue à chaque pas.",
                 "{residu} at the largest absolute value, over the {pas} drawn steps: the "
                 "identity x + y + z − k·dt holds at every step.",
                 "{residu} في أقصى قيمةٍ مطلقة، على {pas} خطوةً مرسومة: فالهويةُ "
                 "x + y + z − k·dt ثابتةٌ عند كلِّ خطوة.")),
              v["residu"]),
        carte(("bruit injecté dans la série", "noise injected into the series",
               "الضجيجُ المحقون في السلسلة"),
              n(("amplitude déclarée avant la mesure, injectée à dessein dans les "
                 "{fenetres} fenêtres simulées : l'épreuve de l'instrument, pas du ciel.",
                 "amplitude declared before the measure, deliberately injected into the "
                 "{fenetres} simulated windows: the instrument's test, not the sky's.",
                 "سَّعةٌ مُعلَنة قبل القياس، تُحقَن عمدًا في {fenetres} نافذةٍ محاكاة: فهي "
                 "اختبارُ الأداة لا اختبارُ السماء.")),
              v["eps"]),
        carte(("écart-type d'Allan mesuré", "Allan deviation measured",
               "انحرافُ آلان المقيس"),
              n(("calculé sur la même série, il devait tomber dans [{basse} ; {haute}] : "
                 "l'instrument retrouve l'amplitude qu'il a lui-même déclarée.",
                 "computed on that same series, it had to fall in [{basse} ; {haute}]: the "
                 "instrument recovers the amplitude it declared itself.",
                 "يُحسَب على السلسلة ذاتها وكان عليه أن يقع في [{basse} ؛ {haute}]: "
                 "فتستعيد الأداةُ السَّعةَ التي أعلنتها هي.")),
              v["adev"]),
        carte(("Soleil, pire écart retenu", "Sun, largest gap kept",
               "الشمس، أكبرُ فارقٍ محتفَظ به"),
              n(("secondes par an contre l'année tropique moyenne ; le seuil gelé est à "
                 "{seuil} s/an et le verdict publié est {verdict_soleil}.",
                 "seconds a year against the mean tropical year; the frozen threshold is "
                 "{seuil} s a year and the published verdict is {verdict_soleil}.",
                 "بالثانية في السنة مقابل السنة الاستوائية المتوسطة؛ والحدُّ المجمَّد عند "
                 "{seuil} ث/سنة والحكمُ المنشور هو {verdict_soleil}.")),
              v["soleil"]),
        carte(("Lune, pire écart retenu", "Moon, largest gap kept",
               "القمر، أكبرُ فارقٍ محتفَظ به"),
              n(("secondes par an contre douze lunaisons ; {verdict_lune}, et la variante "
                 "du mois synodique ne change pas le verdict.",
                 "seconds a year against twelve synodic months; {verdict_lune}, and the "
                 "synodic-month variant does not change the verdict.",
                 "بالثانية في السنة مقابل اثنتي عشرة دورةً اقترانية؛ {verdict_lune}، "
                 "والتنوُّعُ في الشهر الاقتراني لا يغيّر الحكم.")),
              v["lune"]),
        carte(("Terre, pire écart retenu", "Earth, largest gap kept",
               "الأرض، أكبرُ فارقٍ محتفَظ به"),
              n(("secondes par an, sur {face} références disponibles, toutes {verdict_terre} "
                 "au seuil gelé.",
                 "seconds a year, over {face} available references, all {verdict_terre} at "
                 "the frozen threshold.",
                 "بالثانية في السنة، على {face} مراجعَ متوافرة، وكلُّها {verdict_terre} عند "
                 "الحدِّ المجمَّد.")),
              v["terre"]),
        carte(("coordonnées du repère", "coordinates of the frame",
               "إحداثياتُ المعْلَم"),
              n(("nombres nommés, chacun repris du dépôt scellé ou mesuré sur l'hôte : "
                 "{coord} entrées, dont deux laissées à produire. Le compte est tenu par "
                 "le contrôle L03.",
                 "named numbers, each taken from the sealed deposit or measured on the "
                 "host: {coord} entries, two of them left to be produced. Check L03 keeps "
                 "the count.",
                 "أعدادٌ مسماة، كلٌّ منها من الإيداع المختوم أو مقيسٌ على المضيف: {coord} "
                 "مدخلًا، منها اثنان يُترَكان للإنتاج. والعدَّ يضبطه التحقُّقُ L03.")),
              v["coord"]),
        carte(("contrôles reçus", "checks met", "التحقُّقاتُ المستوفاة"),
              n(("quinze du certificat d'horlogerie et cinq du laboratoire, tous verts au "
                 "moment où la page est écrite : {ctrl} sur {ctrl_total}.",
                 "fifteen from the horology certificate and five from the laboratory, all "
                 "green as the page is written: {ctrl} of {ctrl_total}.",
                 "خمسةَ عشرَ من شهادة التوقيت وخمسةً من المختبر، كلها ناجحةٌ عند كتابة "
                 "الصفحة: {ctrl} من {ctrl_total}.")),
              v["controles"]),
    ]


# ----------------------------------------------------------------------------
# coordonnée → équation de la page, rôle, unité, statut
# ----------------------------------------------------------------------------
COORD_EQ: Dict[str, str] = {
    "t": "EQ-05", "x": "EQ-02", "y": "EQ-03", "z": "EQ-04", "z_brut": "EQ-04",
    "1 / dt": "EQ-07", "annee_julienne": "EQ-09", "annee_tropique": "EQ-09",
    "annee_tropique_2000": "EQ-09", "lunaison": "EQ-10", "lunaisons_12": "EQ-15",
    "annee_lunaire_civile": "EQ-10", "tau": "EQ-12", "tau / (1 / dt)": "EQ-12",
}

COORD_ROLE: Dict[str, Tuple[str, str, str]] = {
    "t": ("temps du scénario", "scenario time", "زمنُ السيناريو"),
    "x": ("axe 1", "axis 1", "المحور 1"),
    "y": ("axe 2", "axis 2", "المحور 2"),
    "z": ("axe 3", "axis 3", "المحور 3"),
    "z_brut": ("variante non normalisée du même axe, facteur 144/5",
               "un-normalised variant of the same axis, factor 144/5",
               "صيغةٌ غير مُطبَّعة من المحور ذاتِه، بعامل 144/5"),
    "1 / dt": ("période si dt était une fréquence", "period if dt were a frequency",
               "الدورةُ إن كان dt تردُّدًا"),
    "annee_julienne": ("céleste cité", "celestial body cited", "مرجعٌ سماويٌّ مذكور"),
    "annee_tropique": ("céleste cité", "celestial body cited", "مرجعٌ سماويٌّ مذكور"),
    "annee_tropique_2000": ("céleste cité", "celestial body cited", "مرجعٌ سماويٌّ مذكور"),
    "lunaison": ("céleste cité", "celestial body cited", "مرجعٌ سماويٌّ مذكور"),
    "lunaisons_12": ("céleste cité", "celestial body cited", "مرجعٌ سماويٌّ مذكور"),
    "annee_lunaire_civile": ("céleste cité", "celestial body cited", "مرجعٌ سماويٌّ مذكور"),
    "tau": ("rythme réel d'un tick", "real pace of one tick", "إيقاعُ النبضة الواحد فعلًا"),
    "tau / (1 / dt)": ("précision du mesuré contre le spécifié",
                       "accuracy of the measured against the specified",
                       "دقّةُ المقيس مقابل المقرَّر"),
}

UNITE_TR = {
    "comptes": _3("comptes", "counts", "حسابات"),
    "ns": _3("ns", "ns", "نانو ثانية"),
    "jours": _3("jours", "days", "يوم"),
    "ns/tick": _3("ns/pas", "ns/tick", "نانو ثانية/نبضة"),
    "sans unité": _3("sans unité", "dimensionless", "بلا بُعد"),
}

STATUT_COORD_TR = {
    "opérationnel": _3("opérationnel", "operational", "عامِل"),
    "spécifié": _3("spécifié", "specified", "محدَّد"),
    "simulé": _3("simulé", "simulated", "محاكى"),
    "mesuré": _3("mesuré", "measured", "مقيس"),
}


def materiaux(repere: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Le repère à quatorze coordonnées, tel que `laboratoire.reperes()` le rend.

    Une coordonnée dont le nom n'aurait ni rôle ni équation d'attache ferait publier un
    nombre sans provenance : le générateur s'arrête plutôt que d'en afficher un.
    """
    lignes: List[Dict[str, Any]] = []
    for c in repere:
        nom = c["nom"]
        if nom not in COORD_ROLE or nom not in COORD_EQ:
            raise SystemExit(f"coordonnée du repère sans texte de page : {nom!r}")
        if c["unite"] not in UNITE_TR or c["statut"] not in STATUT_COORD_TR:
            raise SystemExit(f"coordonnée {nom!r} avec une unité ou un statut que le "
                             "moteur de page ne traduit pas")
        eq = COORD_EQ[nom]
        lignes.append({"id": nom,
                       "nom": _3(*COORD_ROLE[nom]),
                       "quantite": _3(c["valeur"], c["valeur"], c["valeur"]),
                       "unite": UNITE_TR[c["unite"]],
                       "equation": _3(eq, eq, eq)})
    if len(lignes) != 14:
        raise SystemExit(f"le tableau du repère publierait {len(lignes)} coordonnées")
    return lignes


# ----------------------------------------------------------------------------
# équations et contrôles effectivement affichés
# ----------------------------------------------------------------------------
def table_eq_text() -> Dict[str, Dict[str, tuple]]:
    """EQ-12 est gelée : ni τ ni son rapport, sur aucune des trois langues."""
    table = {k: dict(v) for k, v in EQ_TEXT.items()}
    table["EQ-12"] = {
        "fr": (EQ_TEXT["EQ-12"]["fr"][0], EQ12_GEL["fr"]),
        "en": (EQ_TEXT["EQ-12"]["en"][0], EQ12_GEL["en"]),
        "ar": (EQ_TEXT["EQ-12"]["ar"][0], EQ12_GEL["ar"]),
    }
    return table


def gele_controles(controles: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """C12 est la seule ligne dont `obtenu` porte un nombre d'hôte : elle est gelée."""
    out: List[Dict[str, Any]] = []
    for c in controles:
        copie = dict(c)
        if copie["id"] == "C12":
            copie["obtenu"] = C12_GEL["fr"]
        out.append(copie)
    return out


__all__ = ["_3", "carte", "THEME", "TITRE_BANDE", "DESCRIPTION", "EQ_TEXT", "FORMULE_FR",
           "FORMULE_TR", "formules_traduites", "CHEMINEMENT", "FIL_CONDUCTEUR", "SOURCES",
           "COMMANDES", "CAPTION_MATIERAUX", "NOTE_HOTE", "FIG_ECARTS_TITRE",
           "FIG_ECARTS_DESC", "FIG_ECARTS_SERIES", "FIG_ECARTS_LEGENDE", "FIG_STAB_TITRE",
           "FIG_STAB_DESC", "FIG_STAB_SERIES", "FIG_STAB_LEGENDE", "IMG_TRAJECTOIRE_ALT",
           "IMG_LEGENDE", "COORD_EQ", "COORD_ROLE", "UNITE_TR", "STATUT_COORD_TR",
           "materiaux", "cartes", "EQ12_GEL", "C12_GEL", "table_eq_text",
           "gele_controles"]
