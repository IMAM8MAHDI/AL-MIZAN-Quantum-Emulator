# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""Générateur du dossier ABONDANCE : équations → pages trilingues, SVG, JSON, CSV, Markdown.

Trois modules calculent (electricite_abondance.py, eau_abondance.py,
agriculture_abondance.py) ; ce fichier ne calcule rien de neuf : il met en forme
les dictionnaires rendus, et refuse de publier une page dont un contrôle manque
ou dont une traduction énonce un nombre que le calcul ne produit pas.

Formats produits dans `ABONDANCE/artefacts/` :
    pages/<slug>[_en|_ar].html   neuf pages trilingues, sans JavaScript
    pages/index.html             tableau de bord de production
    figures/<slug>.svg           une figure par dossier, en plus de l'inline
    donnees/<slug>.json          le dictionnaire complet du module
    donnees/<slug>.csv           équations + contrôles, Excel français (BOM, « ; »)
    dossiers/<slug>.md           dossier pédagogique markdown
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

RACINE = Path(__file__).resolve().parent
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

import agriculture_abondance as AGRI          # noqa: E402
import eau_abondance as EAU                   # noqa: E402
import electricite_abondance as ELEC          # noqa: E402
import moteur_page_trilingue as MOTEUR        # noqa: E402

ARTEFACTS = RACINE / "artefacts"
DOI_CONCEPT = "https://doi.org/10.5281/zenodo.24028242"
COULEURS = {"1f5f8b": "#1f5f8b", "or": "#b45309", "vert": "#166534", "gris": "#64748b"}

# ============================================================================
# ÉLECTRICITÉ — textes par équation et par langue
# ============================================================================
ELEC_TEXT: Dict[str, Dict[str, List[str]]] = {
    "EQ-01": {
        "fr": ["La charge se compte en électrons", ""],
        "en": ["Charge is a count of electrons",
               "Two 1 C charges 1 m apart push with 8.9876 × 10^9 N, and 1 C is "
               "6.2415 × 10^18 electrons: the force law is a counting law."],
        "ar": ["الشحنة عَدٌّ للإلكرتونات",
               "شحنتان قدر كل منهما 1 C على بُعد 1 m تتدافعان بقوة 8.9876 × 10^9 N، "
               "والكولوم الواحد يعادل 6.2415 × 10^18 إلكرتونًا."]},
    "EQ-02": {
        "fr": ["Le condensateur : champ et énergie stockée", ""],
        "en": ["The capacitor: field and stored energy",
               "One square metre at 1 mm gap gives 0.000000008854 F, and charging it to "
               "1 kV stores 0.0044 J — the energy lives in the field, not in the metal."],
        "ar": ["المُكثِّف: المجال والطاقة المخزَّنة",
               "متر مربّع بغرفة 1 mm يعطي 0.000000008854 F، وشحنه إلى 1 kV يخزِّن 0.0044 J."]},
    "EQ-03": {
        "fr": ["Résistance et vitesse de dérive", ""],
        "en": ["Resistance and drift speed",
               "One kilometre under 10 mm² costs 1.680 Ω in copper and 2.650 Ω in "
               "aluminium, while the electrons drift at 0.3671 mm/s."],
        "ar": ["المقاومة وسرعة الانجراح",
               "كيلومتر تحت 10 mm² يكلّف 1.680 Ω في النحاس و2.650 Ω في الألومنيوم، "
               "بينما تنجرح الإلكرتونات بسرعة 0.3671 mm/s."]},
    "EQ-04": {
        "fr": ["Puissance : trois écritures d'une même grandeur", ""],
        "en": ["Power: three spellings of one quantity",
               "230 V across 10 A is 2 300.0 W, and P = UI = I²R = U²/R agree to "
               "0.00e+00 W — the kilowatt-hour is then exactly 3.6 MJ."],
        "ar": ["القدرة: ثلاث كتابات لنفس المقدار",
               "230 V على 10 A تعطي 2 300.0 W، والصيغ الثلاث تتفق عند 0.00e+00 W."]},
    "EQ-05": {
        "fr": ["Kirchhoff résolu en rationnels", ""],
        "en": ["Kirchhoff solved in rationals",
               "The loop current is 0.005455 A and both balances close at exactly 0 — "
               "no rounding is borrowed to make the node work."],
        "ar": ["حل كيرشوف بالكسور النسبية",
               "تيار الحلقة 0.005455 A والميزانان ينغلقان على الصفر تمامًا دون أي تقريب."]},
    "EQ-06": {
        "fr": ["Le champ d'un fil, défini au dixième chiffre", ""],
        "en": ["A wire's field, defined to the digit",
               "B(1 A, 1 m) = 2.00000000109 × 10^-7 T, a relative gap of 5.44 × 10^-10 "
               "from the old defining value of 2·10⁻⁷."],
        "ar": ["مجال سلك موصول إلى رقمه التعريفي",
               "B(1 A, 1 m) = 2.00000000109 × 10^-7 T بفارق نسبي 5.44 × 10^-10 عن 2·10⁻⁷."]},
    "EQ-07": {
        "fr": ["Faraday : l'alternateur né du mouvement", ""],
        "en": ["Faraday: the alternator born of motion",
               "100 turns at 50 Hz give a 314.16 V peak and a 222.14 V rms — one "
               "rotating coil, no electronics."],
        "ar": ["فاراداي: المولِّد وُلد من الحركة",
               "100 لَفٌّ عند 50 Hz يعطي قمة 314.16 V وقيمة فعّالة 222.14 V."]},
    "EQ-08": {
        "fr": ["Inductance : l'énergie du champ magnétique", ""],
        "en": ["Inductance: energy held in the magnetic field",
               "L = 0.000314159 H stores 0.000628 J, and the magnetic density beats the "
               "electric one by u_B/u_E = 1.42 × 10^1."],
        "ar": ["المحاثة: طاقة المجال المغناطيسي",
               "L = 0.000314159 H يخزِّن 0.000628 J، وكثافة المجال المغناطيسي تتجاوز "
               "الكهربائية بنسبة u_B/u_E = 1.42 × 10^1."]},
    "EQ-09": {
        "fr": ["Maxwell : la lumière était déjà électrique", ""],
        "en": ["Maxwell: light was already electrical",
               "c = 1/√(μ₀ε₀) gives 2.997924580 × 10^8 m/s and an impedance of "
               "376.7303 Ω — optics falls out of two circuit constants."],
        "ar": ["ماكسويل: الضوء كان كهربائيًا سلفًا",
               "c = 1/√(μ₀ε₀) يعطي 2.997924580 × 10^8 m/s ومعاوقة 376.7303 Ω."]},
    "EQ-10": {
        "fr": ["Le facteur de puissance : ce qu'on paie et ce qui travaille", ""],
        "en": ["Power factor: what is billed and what works",
               "325 V peak is 229.81 V rms; at cos φ = 0.500000 only 1149.05 W of the "
               "2298.10 VA actually heats or turns."],
        "ar": ["معامل القدرة: ما يُدفَع وما ينجز العمل",
               "325 V قمة تساوي 229.81 V فعّالة، وعند cos φ = 0.500000 يعمل "
               "1149.05 W فقط من 2298.10 VA."]},
    "EQ-11": {
        "fr": ["Le triphasé : trois courants, une somme nulle", ""],
        "en": ["Three-phase: three currents, one zero sum",
               "√3 = 1.732050807569, the phasor sum closes at 3.1e-16, and 230 V per "
               "phase becomes 398.37 V between lines."],
        "ar": ["الثلاثي الأطوار: ثلاثة تيارات ومجموع صفر",
               "√3 = 1.732050807569 ومجموع المتجهات ينغلق عند 3.1e-16، و230 V لكل طور "
               "تصبح 398.37 V بين الخطوط."]},
    "EQ-12": {
        "fr": ["Le transformateur ne crée rien : il échange", ""],
        "en": ["A transformer trades, it does not create",
               "20 kV down to 400 V delivers I₂ = 1000.00 A at 97.37 % efficiency with "
               "the declared losses — apparent power is conserved."],
        "ar": ["المحوِّل يتبادل ولا يخلق",
               "من 20 kV إلى 400 V يعطي I₂ = 1000.00 A بكفاءة 97.37 % مع الفقد المعلَن."]},
    "EQ-13": {
        "fr": ["Haute tension : le facteur 10^6 sur les pertes", ""],
        "en": ["High voltage: a factor of 10^6 on losses",
               "Carrying 1 GW at 400 V would burn 3.12 × 10^11 W in the lines; at 400 kV "
               "the same copper burns 3.12 × 10^5 W."],
        "ar": ["الجهد العالي: عامل 10^6 على الفقد",
               "نقل 1 GW عند 400 V يحرق 3.12 × 10^11 W في الخطوط، وعند 400 kV يحرق "
               "3.12 × 10^5 W فقط."]},
    "EQ-14": {
        "fr": ["Chute d'eau : la puissance déjà écrite dans la gravité", ""],
        "en": ["Falling water: power already written in gravity",
               "100 m, 10 m³/s at η = 0,90 gives 8.83 MW and 0.2724 kWh per cubic metre."],
        "ar": ["السقوط المائي: قدرة مكتوبة سلفًا في الجاذبية",
               "100 m و10 m³/s عند η = 0,90 تعطي 8.83 MW و0.2724 kWh لكل متر مكعّب."]},
    "EQ-15": {
        "fr": ["Betz : la limite se dérive, elle ne se négocie pas", ""],
        "en": ["Betz: the ceiling is derived, not negotiated",
               "C_P = 4a(1−a)² peaks at a* = 1/3 with 16/27 = 0.592592593 of the wind's "
               "power — no blade design goes past it."],
        "ar": ["بيتس: السقف يُستنتَج ولا يُفاوَض عليه",
               "C_P = 4a(1−a)² تبلغ ذروتها عند a* = 1/3 فتلتقط 16/27 = 0.592592593 من قدرة الريح."]},
    "EQ-16": {
        "fr": ["Carnot : la chaleur a un plafond politique", ""],
        "en": ["Carnot: heat has a hard ceiling",
               "Between 800 K and 300 K the bound is 62.50 %, and the best declared "
               "machine sits at 97.6 % of that bound."],
        "ar": ["كارنو: للحرية سقف",
               "بين 800 K و300 K الحد هو 62.50 %، وأفضل آلة معلَنة تبلغ 97.6 % من هذا الحد."]},
    "EQ-17": {
        "fr": ["Le seuil du semi-conducteur : qui paie les photons", ""],
        "en": ["The semiconductor threshold pays for photons",
               "Silicon's 1,12 eV gap cuts at 1107.0 nm, and a photon at 2E_g wastes 50 % "
               "of its energy as heat."],
        "ar": ["عتبة أشباه الموصلات تدفع ثمن الفوتونات",
               "فجوة السيليكون 1,12 eV تقطع عند 1107.0 nm، وفوتون عند 2E_g يهدر 50 % من طاقته."]},
    "EQ-18": {
        "fr": ["Stocker : la matière ne ment pas sur sa densité", ""],
        "en": ["Storage: matter does not lie about its density",
               "LiFePO₄ active material holds 586 Wh/kg, hydrogen LHV 33.33 kWh/kg, and "
               "100 m of water only 0.272 Wh/kg."],
        "ar": ["التخزين: المادة لا تكذب في كثافتها",
               "LiFePO₄ النشط يحمل 586 Wh/kg، و H₂ LHV 33.33 kWh/kg، و100 m من الماء "
               "0.272 Wh/kg فقط."]},
    "EQ-19": {
        "fr": ["Supraconductivité : zéro, mais à quel prix", ""],
        "en": ["Superconductivity: zero, but at what price",
               "NbTi gives Δ = 1.399 meV and a recomputed ratio of 3.530, while one "
               "kilometre of copper at 50 A still burns 4200.00 W when it is warm."],
        "ar": ["التوصيل الفائق: صفر، لكن بأي ثمن",
               "NbTi يعطي Δ = 1.399 meV ونسبة معاد حسابها 3.530، بينما كيلومتر من النحاس "
               "عند 50 A يحرق 4200.00 W وهو دافئ."]},
    "EQ-20": {
        "fr": ["Le budget solaire de la Terre", ""],
        "en": ["Earth's solar budget",
               "Φ = 1361.17 W/m² outside the atmosphere, the disc intercepts "
               "1.736 × 10^17 W, i.e. 9135× the declared world consumption."],
        "ar": ["ميزانية الأرض الشمسية",
               "Φ = 1361.17 W/m² خارج الغلاف، والقرص يعترض 1.736 × 10^17 W أي 9135× من "
               "الاستهلاك العالمي المعلَن."]},
    "EQ-21": {
        "fr": ["Quatre ponts de lecture, chacun avec sa limite", ""],
        "en": ["Four reading bridges, each with its limit",
               "Sealing, clock, fault tolerance and register — four analogies declared as "
               "reading aids, never as measurements."],
        "ar": ["أربعة جسور للقراءة، لكل منها حدّه",
               "الختم والساعة والتسامح مع العطل والسجل: أربعة تشبيهات مُعلَنة كأدوات قراءة "
               "لا كقياسات."]},
}

ELEC_CHEMINEMENT: List[Dict[str, List[str]]] = [
    {"fr": ["Thalès et le frottement",
            "un morceau d'ambre frotté attire la poussière : la première fois, une "
            "propriété de la matière est isolée, nommée, et non expliquée par un mythe."],
     "en": ["Thales and the rubbed amber",
            "Rubbed amber draws dust: for the first time a property of matter is isolated, "
            "named, and not explained by a myth."],
     "ar": ["طاليس والكهرمان المدلوك",
            "الكهرمان المدلوك يجذب الغبار: هنا لأول مرة تُعزَل خاصية للمادة وتُسمَّى "
            "ولا تُفسَّر بأسطورة."]},
    {"fr": ["De Gilbert à Coulomb : compter la force",
            "Gilbert sépare l'électrique du magnétique ; von Guericke fabrique une machine "
            "à sphère ; Franklin donne un nom (positif, négatif) ; Coulomb pèse la force "
            "avec une balance de torsion."],
     "en": ["From Gilbert to Coulomb: counting the force",
            "Gilbert separates electricity from magnetism; von Guericke builds a sphere "
            "machine; Franklin names positive and negative; Coulomb weighs the force with "
            "a torsion balance."],
     "ar": ["من جيلبرت إلى كولوم: عَدُّ القوة",
            "جيلبرت فصل الكهربائية عن المغناطيسية، وفون غويريكي صنع آلة الكروية، وفرانكلين "
            "سمّى الموجب والسالب، وكولوم وزن القوة بميزان الالتواء."]},
    {"fr": ["Ampère, Ohm, Faraday : le circuit devient grandeur",
            "Le courant devient une intensité mesurable, la tension une résistance, "
            "l'induction une tension qui naît du mouvement. L'électricité cesse d'être "
            "un spectacle de salon."],
     "en": ["Ampère, Ohm, Faraday: the circuit becomes a quantity",
            "Current becomes a measurable intensity, voltage a resistance, induction a "
            "voltage born of motion. Electricity stops being a salon trick."],
     "ar": ["أمبير وأوم وفاراداي: الدائرة تصبح مقدارًا",
            "يصير التيار شدة قابلة للقياس، والجهد مقاومة، والحثّ جهدًا يولد من الحركة."]},
    {"fr": ["Maxwell, Tesla, Steinmetz : la fréquence et le réseau",
            "Maxwell enferme la lumière dans deux constantes ; Tesla et Steinmetz donnent "
            "le polyphase et le calcul en nombres complexes. Un réseau à 50 Hz est une "
            "équation qui tourne."],
     "en": ["Maxwell, Tesla, Steinmetz: frequency and grid",
            "Maxwell traps light in two constants; Tesla and Steinmetz deliver polyphase "
            "and complex arithmetic. A 50 Hz grid is an equation that turns."],
     "ar": ["ماكسويل وتيسلا وشطاينمِتس: التردد والشبكة",
            "ماكسويل حبس الضوء في ثابتين، وتيسلا وشطاينمِتس أعطيا الأطوار الثلاثة والحساب "
            "بالمركّبات. شبكة بـ 50 Hz هي معادلة تدور."]},
    {"fr": ["Betz, Carnot, Shockley : les plafonds d'abord",
            "Avant de promettre une machine, on pose la limite : 16/27 pour le vent, "
            "1 − T_froid/T_source pour la chaleur, le seuil du semi-conducteur pour la "
            "lumière. Le reste est de l'ingénierie."],
     "en": ["Betz, Carnot, Shockley: ceilings first",
            "Before promising a machine, set the limit: 16/27 for wind, "
            "1 − T_froid/T_source for heat, the semiconductor threshold for light. "
            "The rest is engineering."],
     "ar": ["بيتس وكارنو وشوكلي: السقوف أولًا",
            "قبل وعد أي آلة يُقرَّر الحد: 16/27 للريح، و 1 − T_froid/T_source للحرارة، "
            "وعتبة أشباه الموصلات للضوء. والباقي هندسة."]},
]

# ============================================================================
# EAU — textes par équation et par langue
# ============================================================================
EAU_TEXT: Dict[str, Dict[str, List[str]]] = {
    "EQ-01": {
        "fr": ["Toute l'eau, puis la part douce", ""],
        "en": ["All the water, then the sweet share",
               "Sweet water is 35.90 × 10⁶ km³ out of 1386.00 × 10⁶ km³, and only "
               "0.03 % of that stock renews: 2991 years to refresh all of it."],
        "ar": ["كل الماء، ثم النصيب العذب",
               "الماء العذب 35.90 × 10⁶ km³ من 1386.00 × 10⁶ km³، ولا يتجدد إلا 0.03 % منه: "
               "2991 سنة لتجديد المخزون كله."]},
    "EQ-02": {
        "fr": ["L'hydrostatique : chaque mètre compte", ""],
        "en": ["Hydrostatics: every metre counts",
               "At 10 m the pressure is 97.772 kPa, 1.965 atm absolute; at 100 m at sea "
               "it is 1005.2 kPa, and ρgH gives 980 665.0000 J per cubic metre."],
        "ar": ["علم السكون المائي: كل متر يحسب",
               "عند 10 m الضغط 97.772 kPa أي 1.965 atm مطلقة، وعند 100 m في البحر "
               "1005.2 kPa، ويعطي ρgH مقدار 980 665.0000 J لكل متر مكعّب."]},
    "EQ-03": {
        "fr": ["Archimède : la glace dit la densité", ""],
        "en": ["Archimedes: ice states the density",
               "An iceberg floats 89.46 % submerged and 10.54 % above; a 50 000 t hull "
               "displaces 4.878 × 10^4 m³."],
        "ar": ["أرخميدس: الثلج يقول الكثافة",
               "الجبل الجليدي يطفو مغمورًا 89.46 % وبارزًا 10.54 %، وسفينة بـ 50 000 t "
               "تزحزح 4.878 × 10^4 m³."]},
    "EQ-04": {
        "fr": ["Continuité : ce qui entre sort, plus vite ou plus lentement", ""],
        "en": ["Continuity: what enters leaves, faster or slower",
               "10 m³/s through 10 m² runs at 1.0 m/s and through 0,5 m² at 20.0 m/s — "
               "the residual is 0.00e+00."],
        "ar": ["الاستمرارية: ما يدخل يخرج أسرع أو أبطأ",
               "10 m³/s عبر 10 m² يجري بـ 1.0 m/s وعبر 0,5 m² بـ 20.0 m/s، والباقي 0.00e+00."]},
    "EQ-05": {
        "fr": ["Bernoulli : la hauteur transformée en vitesse", ""],
        "en": ["Bernoulli: height converted into speed",
               "10 m gives 14.005 m/s and 100 m gives 44.29 m/s, with a slope of "
               "9.806650 m/s² — gravity unchanged."],
        "ar": ["برنولي: الارتفاع يتحول سرعة",
               "10 m تعطي 14.005 m/s و100 m تعطي 44.29 m/s بميل 9.806650 m/s²."]},
    "EQ-06": {
        "fr": ["Pomper : le prix en kWh du mètre cube", ""],
        "en": ["Pumping: the price of a cubic metre in kWh",
               "50 m at η 0,65 costs 0.2089 kWh/m³ and 8.7 kW on average for "
               "1000 m³/day — still 0.26× of the desalination bound of EQ-08."],
        "ar": ["الضخ: سعر المتر المكعب بالكيلوواط الساعي",
               "50 m عند η 0,65 تكلّف 0.2089 kWh/m³ و8.7 kW في المتوسط لضخ "
               "1000 m³/يوم، أي 0.26× من حد EQ-08."]},
    "EQ-07": {
        "fr": ["van 't Hoff : la pression osmotique", ""],
        "en": ["van 't Hoff: osmotic pressure",
               "At 35 g/kg the ideal pressure is 30.44 bar — 29.69 bar through the molar "
               "route and about 27.1 bar real — a head equal to a 302.8 m column."],
        "ar": ["فانت هوف: الضغط الأسموزي",
               "عند 35 g/kg يكون الضغط المثالي 30.44 bar — أي 29.69 bar من المسار المولي "
               "ونحو 27.1 bar فعلي — بما يعادل عمودًا من 302.8 m."]},
    "EQ-08": {
        "fr": ["Le travail minimum du dessalement", ""],
        "en": ["The minimum work of desalination",
               "With x_eau = 0.978877 the thermodynamic floor is 0.8136 kWh/m³, and the "
               "declared reverse-osmosis plant uses 3.0 kWh/m³, i.e. 3.69× the floor."],
        "ar": ["العمل الأدنى لتحلية الماء",
               "عند x_eau = 0.978877 يكون الحد الثيرموديناميكي 0.8136 kWh/m³، "
               "والتناضح العكسي المعلَن يستهلك 3.0 kWh/m³ أي 3.69× الحد."]},
    "EQ-09": {
        "fr": ["Bilan salin : la saumure est comptée", ""],
        "en": ["A salt balance: the brine is counted",
               "At Y = 0,45 the brine reaches 63.6 g/kg, 1.82× the feed, and "
               "1.22 m³ are rejected per m³ produced, with a residual of 0.00e+00."],
        "ar": ["ميزان الملح: المحلول المركَّز معدود",
               "عند Y = 0,45 يبلغ المركَّز 63.6 g/kg أي 1.82× من التغذية، ويُرفض "
               "1.22 m³ لكل m³ منتج، والباقي 0.00e+00."]},
    "EQ-10": {
        "fr": ["Deux lois pour une vapeur", ""],
        "en": ["Two laws for one vapour",
               "At 25 °C Magnus gives 31.617 hPa and Clausius 31.002 hPa, a 1.95 % gap; "
               "evaporating 1 m³ costs 676.3 kWh."],
        "ar": ["قانونان لبخار واحد",
               "عند 25 °C يعطي ماغنوس 31.617 hPa وكلازيوس 31.002 hPa بفارق 1.95 %، "
               "وتبخير 1 m³ يكلّف 676.3 kWh."]},
    "EQ-11": {
        "fr": ["Le cycle global ferme ses deux colonnes", ""],
        "en": ["The global cycle closes both columns",
               "119 000 = 72 000 + 47 000 km³/an over the land, 799 mm/an on emerged "
               "land against 1029 mm/an on the planet."],
        "ar": ["الدورة الكلية تغلق عموديها",
               "119 000 = 72 000 + 47 000 km³/ سنة على اليابسة، و799 mm/ سنة على الأرض "
               "الظاهرة مقابل 1029 mm/ سنة على الكوكب."]},
    "EQ-12": {
        "fr": ["L'eau dans l'assiette", ""],
        "en": ["Water on the plate",
               "Beef to tomato differs by 60×, and a declared diet takes about "
               "2201 L/day against 150 L/day at the tap."],
        "ar": ["الماء في الطبق",
               "الفرق بين اللحم والطماطم 60×، والنظام الغذائي المعلَن يأخذ نحو 2201 L/ يوم "
               "مقابل 150 L/ يوم من الصنبور."]},
    "EQ-13": {
        "fr": ["Salinité et conductivité : le pont de l'instrument", ""],
        "en": ["Salinity and conductivity: the instrument bridge",
               "35 g/kg reads 54.7 dS/m, that is 5.47 S/m, while the drinking threshold "
               "sits at 1.56 dS/m."],
        "ar": ["الملوحة والتوصيل: جسر الآلة",
               "35 g/kg تقرأ 54.7 dS/m أي 5.47 S/m، بينما عتبة الشرب عند 1.56 dS/m."]},
    "EQ-14": {
        "fr": ["Stocker l'eau, c'est stocker la même formule qu'en électricité", ""],
        "en": ["Storing water uses the same formula as electricity",
               "One km³ under 100 m is 272.4 GWh — 0.2724 TWh — draining in 8 h at "
               "34.1 GW, and only 0.272 Wh/kg of water."],
        "ar": ["تخزين الماء الصيغة نفسها المستعملة في الكهرباء",
               "km³ واحد تحت 100 m يساوي 272.4 GWh أي 0.2724 TWh، يفرَّغ في 8 h بقوة "
               "34.1 GW، وبمقدار 0.272 Wh/kg من الماء."]},
    "EQ-15": {
        "fr": ["Quatre ponts de lecture, chacun borné", ""],
        "en": ["Four reading bridges, each bounded",
               "Bound, cycles, redundancy and hydrological debt: four declared readings, "
               "each with an explicit limit."],
        "ar": ["أربعة جسور للقراءة، كل منها محدود",
               "الحد والدورات والتكرار والدين المائي: أربع قراءات معلَنة لكل منها حد صريح."]},
}

EAU_CHEMINEMENT: List[Dict[str, List[str]]] = [
    {"fr": ["Thalès, et l'eau comme principe",
            "L'élève de Thalès, Anaximandre, fait de l'eau le principe de toute chose : "
            "une erreur, mais la première tentative de expliquer le monde sans mythe."],
     "en": ["Thales, and water as first principle",
            "Thales' student Anaximander made water the principle of all things: wrong, "
            "but the first attempt to explain the world without a myth."],
     "ar": ["طاليس والماء مبدأ",
            "جعل أناكسيمندر، تلميذ طاليس، الماء مبدأ كل شيء: خطأ، لكنه أول محاولة لتفسير "
            "العالم بلا أسطورة."]},
    {"fr": ["Archimède, Pascal, Bernoulli : la pression devient nombre",
            "La poussée, puis le baromètre de von Guericke, puis l'écoulement : "
            "l'hydrostatique et l'hydrodynamique deviennent mesurables avant l'industrie."],
     "en": ["Archimedes, Pascal, Bernoulli: pressure becomes a number",
            "Buoyancy, then von Guericke's barometer, then flow: hydrostatics and "
            "hydrodynamics become measurable before industry does."],
     "ar": ["أرخميدس وباسكال وبرنولي: الضغط يصير عددًا",
            "الدفعة ثم بارومتر فون غويريكي ثم الجريان: يصير علم السكون والحركة المائيين "
            "قابلين للقياس قبل الصناعة."]},
    {"fr": ["van 't Hoff : la pression osmotique, avant les membranes",
            "π = i·c·R·T est une formule de 1886. Elle pose la borne que l'osmose inverse "
            "mettra un siècle à approcher."],
     "en": ["van 't Hoff: osmotic pressure before the membranes",
            "π = i·c·R·T dates from 1886. It sets the floor that reverse osmosis would "
            "take a century to approach."],
     "ar": ["فانت هوف: الضغط الأسموزي قبل الأغشية",
            "π = i·c·R·T من سنة 1886. وهي تقرَّر الحد الذي لن تقترب منه التناضح العكسي إلا "
            "بعد قرن."]},
    {"fr": ["Second principe : le plancher du dessalement",
            "Extraire de l'eau douce de la mer coûte au minimum un travail de mélange "
            "inversé : 0.8136 kWh/m³. Toute promesse en dessous est une erreur de compte."],
     "en": ["Second law: the floor under desalination",
            "Pulling fresh water out of the sea costs at least the reversed work of "
            "mixing: 0.8136 kWh/m³. Any promise below it is a bookkeeping error."],
     "ar": ["القانون الثاني: أرضية التحلية",
            "استخراج الماء العذب من البحر يكلّف على الأقل عملًا عكسيًا للمزج مقداره "
            "0.8136 kWh/m³. وكل وعد أقل من ذلك خطأ في الحساب."]},
    {"fr": ["Fermer le cycle, puis compter l'assiette",
            "Le cycle terrestre ne doit rien laisser de côté : les colonnes se ferment "
            "d'elles-mêmes. Ensuite l'eau virtuelle place le robinet dans l'agriculture."],
     "en": ["Close the cycle, then count the plate",
            "The land cycle must leave nothing out: the columns close by themselves. "
            "Then virtual water puts the tap inside agriculture."],
     "ar": ["إغلاق الدورة ثم عَدُّ الطبق",
            "يجب ألا تترك دورة اليابسة شيئًا: ينغلق العمودان بنفسهما. ثم يضع الماء الافتراضي "
            "الصنبور داخل الزراعة."]},
]

# ============================================================================
# AGRICULTURE — textes par équation et par langue
# ============================================================================
AGRI_TEXT: Dict[str, Dict[str, List[str]]] = {
    "EQ-01": {
        "fr": ["La photosynthèse est un bilan de masse", ""],
        "en": ["Photosynthesis is a mass balance",
               "372.144 g of reactants give 372.144 g of products, and fixing one gram of "
               "biomass costs 1.466 g of CO2 — the balance closes at 0."],
        "ar": ["البناء الضوئي ميزان كتلة",
               "372.144 g من المتفاعلات تعطي 372.144 g من الناتجات، وإنتاج غرام واحد من "
               "الكتلة الحيوية يكلّف 1.466 g من CO2، والميزان ينغلق على 0."]},
    "EQ-02": {
        "fr": ["Le prix du CO2 fixé : 4 photons au moins", ""],
        "en": ["The price of fixed CO2: at least four photons",
               "680 nm light is 1.8233 eV, one einstein is 175.92 kJ/mol, and the ceiling "
               "is 68.0 % at 4 photons but 32.0 % at the 8,5 actually measured."],
        "ar": ["ثمن CO2 المثبَّت: أربعة فوتونات على الأقل",
               "ضوء 680 nm يساوي 1.8233 eV، والإينشتاين 175.92 kJ/mol، والسقف 68.0 % عند "
               "4 فوتونات لكنه 32.0 % عند 8,5 المُقاس فعلًا."]},
    "EQ-03": {
        "fr": ["Intégrer le spectre : combien de photons utilisables", ""],
        "en": ["Integrating the spectrum: how many usable photons",
               "The 400–700 nm band carries 36.6 % of the energy, the full spectrum gives "
               "1.673 µmol/J, and outside the atmosphere the light is about 1673 µmol/m²/s."],
        "ar": ["تكامل الطيف: كم من الفوتونات قابل للاستعمال",
               "يحمل نطاق 400–700 nm نحو 36.6 % من الطاقة، ويعطي الطيف كله 1.673 µmol/J، "
               "وتبلغ الإضاءة خارج الغلاف نحو 1673 µmol/m²/s."]},
    "EQ-04": {
        "fr": ["Le rayonnement disponible contre l'assiette disponible", ""],
        "en": ["Available radiation against the food demand",
               "The band delivers 43.7 ZJ/an over cultivable land against 0.026 ZJ/an "
               "demanded: even at 0.5 % conversion that is 8.5× the need."],
        "ar": ["الإشعاع المتاح مقابل الطلب الغذائي",
               "يبلغ النطاق 43.7 ZJ/ سنة على الأرض القابلة للزراعة مقابل 0.026 ZJ/ سنة "
               "مطلوبة: وحتى عند تحويل 0.5 % ذلك يعادل 8.5× الحاجة."]},
    "EQ-05": {
        "fr": ["Monteith : le rendement borné par la lumière", ""],
        "en": ["Monteith: yield bounded by light",
               "The quantum ceiling is 20.08 g/MJ PAR, and the declared C4 and C3 "
               "efficiencies reach 33.2 % and 16.6 % of it."],
        "ar": ["مونتايث: المحصول محدود بالضوء",
               "السقف الكمّي 20.08 g/MJ PAR، وتبلغ الكفاءات المعلَنة C4 و C3 منه 33.2 % و 16.6 %."]},
    "EQ-06": {
        "fr": ["C3, C4, CAM : Rubisco et la photorespiration", ""],
        "en": ["C3, C4, CAM: Rubisco and photorespiration",
               "Rubisco's specificity is declared at 85, C4 doubles ε (2.00×), and "
               "photorespiration costs 52.9 % of the photons in a C3 leaf."],
        "ar": ["C3 و C4 و CAM: روبيسكو والتنفس الضوئي",
               "خصوصية روبيسكو معلَنة عند 85، و C4 تضعف ε (2.00×)، ويكلّف التنفس الضوئي "
               "52.9 % من الفوتونات في ورقة C3."]},
    "EQ-07": {
        "fr": ["Liebig : le baril ne se remplit pas à la planche haute", ""],
        "en": ["Liebig: the barrel fills at its lowest stave",
               "With phosphorus limiting the yield is 1.40 t/ha, doubling it gives 2.45, "
               "doubling it again changes nothing, and only full boards reach 3.50."],
        "ar": ["ليبيغ: البرميل يمتلئ عند أخفض لوح",
               "عندما يحدّ الفسفور يكون المحصول 1.40 t/ha، ومضاعفته تعطي 2.45، ومضاعفته "
               "مرة أخرى لا تغيّر شيئًا، ولا يبلغ 3.50 إلا إذا امتلأت كل الألواح."]},
    "EQ-08": {
        "fr": ["Haber-Bosch : l'azote que l'on achète", ""],
        "en": ["Haber-Bosch: nitrogen that has to be bought",
               "NH3 is 82.25 % nitrogen and 31 GJ/t means 37.7 MJ per kg N: 73.68 kg N/ha "
               "of 120 applied is a 61.4 % recovery, i.e. 359 kWh per tonne of wheat."],
        "ar": ["هابر-بوش: الآزوت الذي يُشترى",
               "NH3 آزوته 82.25 % و 31 GJ/t يعني 37.7 MJ لكل kg من N: 73.68 kg N/ha من "
               "120 مطبَّقة أي استرجاع 61.4 %، أي 359 kWh لكل طن من القمح."]},
    "EQ-09": {
        "fr": ["L'évapotranspiration : le même litre que le dossier EAU", ""],
        "en": ["Evapotranspiration: the same litre as the water dossier",
               "A net radiation of 100 W/m² evaporates 3.549 mm/day, and a 500 mm wheat "
               "season needs 5000 m³/ha, that is 1428.57 L/kg."],
        "ar": ["النتح التبخري: نفس اللتر في ملف الماء",
               "إشعاع صافٍ بـ 100 W/m² يبخر 3.549 mm/ يوم، وموسم قمح بـ 500 mm يحتاج "
               "5000 m³/ha أي 1428.57 L/kg."]},
    "EQ-10": {
        "fr": ["Irriguer : le kWh/m³ hérité du dossier EAU", ""],
        "en": ["Irrigating: the kWh/m³ inherited from the water dossier",
               "At 0.2089 kWh/m³, drip costs 4.178 GJ/ha against 6.267 GJ/ha for surface "
               "flooding — irrigation is 0.92 of the nitrogen bill."],
        "ar": ["الري: kWh/m³ الموروث من ملف الماء",
               "عند 0.2089 kWh/m³ يكلّف التنقيط 4.178 GJ/ha مقابل 6.267 GJ/ha للسطحية، "
               "فيساوي الري 0.92 من فاتورة الآزوت."]},
    "EQ-11": {
        "fr": ["Eau virtuelle : deux chemins, un même chiffre", ""],
        "en": ["Virtual water: two roads, one figure",
               "Derived from the field the wheat is 1428.57 L/kg against the declared "
               "1500 L/kg, a 4.8 % gap, and the green/blue/grey shares close."],
        "ar": ["الماء الافتراضي: طريقان ورقم واحد",
               "المشتق من الحقل يعطي للقمح 1428.57 L/kg مقابل 1500 L/kg المعلَن بفارق "
               "4.8 %، وتنتهي نسب الأخضر والأزرق والرمادي إلى الميزان."]},
    "EQ-12": {
        "fr": ["Δ13C : la plante enregistre son eau", ""],
        "en": ["Δ13C: the plant records its own water use",
               "A measured 19.5‰ gives ci/ca = 0.6681, and at constant Δ, going from "
               "300 to 420 ppm raises water-use efficiency by 40.0 %."],
        "ar": ["Δ13C: النبتة تسجل ماءها",
               "قيمة مقاسة بـ 19.5‰ تعطي ci/ca = 0.6681، وعند Δ ثابت ينقل الانتقال من 300 "
               "إلى 420 ppm كفاءة الماء إلى +40.0 %."]},
    "EQ-13": {
        "fr": ["Ce qu'un hectare nourrit", ""],
        "en": ["What one hectare feeds",
               "Wheat carries 15.53 persons/ha and maize 47.62, a ratio of 3.07 — the "
               "difference is the declared yield, not the soil."],
        "ar": ["ما يُطعمه هكتار",
               "يحمل القمح 15.53 شخصًا/ha والذرة 47.62 بنسبة 3.07؛ الفرق في المحصول المعلَن "
               "لا في التربة."]},
    "EQ-14": {
        "fr": ["La surface pour nourrir le monde, bornée", ""],
        "en": ["The area needed to feed the world, bounded",
               "8 billion on cereals alone would take 515 Mha of the 1400 Mha cultivable "
               "(2.7× margin); with 25 % of calories from animals it becomes 1159 Mha."],
        "ar": ["المساحة لإطعام العالم، بحدودها",
               "8 مليارات على الحبوب وحدها تأخذ 515 Mha من 1400 Mha الصالحة للزراعة "
               "(هامش 2.7×)، ومع 25 % من السعرات حيوانية تصبح 1159 Mha."]},
    "EQ-15": {
        "fr": ["Le sol est un stock, l'érosion un débit", ""],
        "en": ["Soil is a stock, erosion a flow",
               "A 30 cm horizon weighs 3900 t/ha; at 10 t/ha/an the erosion runs at 20× "
               "the formation rate, leaving 390 years before the horizon is gone."],
        "ar": ["التربة مخزون والانجراف دفق",
               "أفق بعمق 30 cm يزن 3900 t/ha؛ وعند 10 t/ha/ سنة يجري الانجراف بمعدل 20× "
               "التكوّن، فلا يبقى من الأفق إلا 390 سنة."]},
    "EQ-16": {
        "fr": ["La lumière achetée : du DLI au kilogramme", ""],
        "en": ["Bought light: from DLI to the kilogram",
               "A DLI of 15 mol/m²/jour has a photon minimum of 0.7330 kWh and a system "
               "cost of 1.4881 kWh (93 W/m²), i.e. 13.58 kWh per kg of tomato."],
        "ar": ["الضوء المشترى: من DLI إلى الكيلوغرام",
               "DLI بـ 15 mol/m²/ يوم له حدّ فوتوني من 0.7330 kWh وكلفة نظام 1.4881 kWh "
               "(93 W/m²) أي 13.58 kWh لكل kg من الطماطم."]},
    "EQ-17": {
        "fr": ["Les matériaux, dimensionnés par les équations", ""],
        "en": ["Materials, sized by the equations",
               "Eight materials come out of the previous equations: 276.00 kg/ha of "
               "polyethylene film and 666.67 kg/ha of hydrogel for a 20 mm buffer."],
        "ar": ["المواد المقدَّرة بالمعادلات",
               "ثماني مواد تخرج من المعادلات السابقة: 276.00 kg/ha من فيلم البولي إيثيلين "
               "و666.67 kg/ha من الهلام الماصّ لوسادة من 20 mm."]},
    "EQ-18": {
        "fr": ["Quatre ponts de lecture, chacun borné", ""],
        "en": ["Four reading bridges, each bounded",
               "The quantum ceiling cannot be negotiated, the agronomic clock is "
               "biological, redundancy is not a coding theorem, and the debts are "
               "declared — four readings, each with its limit."],
        "ar": ["أربعة جسور للقراءة، كل منها محدود",
               "لا يُفاوَض على السقف الكمّي، والساعة الزراعية بيولوجية، والتكرار ليس مبرهنة "
               "ترميز، والديون معلَنة — أربع قراءات لكل منها حدّها."]},
}

AGRI_CHEMINEMENT: List[Dict[str, List[str]]] = [
    {"fr": ["Du photon à la feuille",
            "Rien d'agricole ne se comprend sans la lumière : un einstein à 680 nm vaut "
            "175.92 kJ/mol et le nombre de photons par CO2 fixé est une obligation "
            "thermodynamique, pas un réglage."],
     "en": ["From photon to leaf",
            "Nothing agricultural is understood without light: one einstein at 680 nm is "
            "175.92 kJ/mol, and the photon count per CO2 fixed is a thermodynamic "
            "obligation, not a tuning knob."],
     "ar": ["من الفوتون إلى الورقة",
            "لا يُفهم شيء زراعي بلا ضوء: الإينشتاين عند 680 nm يساوي 175.92 kJ/mol، وعدد "
            "الفوتونات لكل CO2 مثبَّت التزام ثيرموديناميكي لا ضبط."]},
    {"fr": ["De la feuille au champ : Monteith et Liebig",
            "Le rendement d'un couvert est le produit ε·fAPAR·PAR tant qu'aucun facteur "
            "ne manque ; dès qu'un facteur manque, c'est lui qui décide."],
     "en": ["From leaf to field: Monteith and Liebig",
            "A crop's yield is ε·fAPAR·PAR as long as nothing is missing; the moment one "
            "factor is missing, that factor decides."],
     "ar": ["من الورقة إلى الحقل: مونتايث وليبيغ",
            "محصول الغطاء هو ε·fAPAR·PAR ما دام شيء غير ناقص؛ فإذا نقص عامل واحد فهو الذي "
            "يقرّر."]},
    {"fr": ["De l'azote du vent à l'ammoniac de Bosch",
            "L'air est gratuit, la fixation ne l'est pas : 31 GJ par tonne de NH3, "
            "d'où 37.7 MJ par kg d'azote. C'est le prix de sortie de la faim saisonnière."],
     "en": ["From nitrogen in the air to Bosch's ammonia",
            "Air is free, fixing it is not: 31 GJ per tonne of NH3, hence 37.7 MJ per kg "
            "of nitrogen. That is the price of leaving seasonal hunger."],
     "ar": ["من آزوت الهواء إلى نشادر بوش",
            "الهواء مجاني والتثبيت ليس كذلك: 31 GJ لكل طن من NH3، أي 37.7 MJ لكل kg من "
            "الآزوت. هذا ثمن الخروج من الجوع الموسمي."]},
    {"fr": ["L'eau entre par la physique : les deux dossiers se touchent",
            "L'évapotranspiration redonne le litre du dossier EAU, et le kilowattheure de "
            "pompage vient de la même identité ρgH/η. Aucun chiffre agricole n'est saisi "
            "à la main."],
     "en": ["Water enters through physics: the two dossiers touch",
            "Evapotranspiration returns the water dossier's litre, and the pumping "
            "kilowatt-hour comes from the same ρgH/η identity. No agricultural figure is "
            "typed by hand."],
     "ar": ["يدخل الماء من الفيزياء: يلمس الملفان بعضهما",
            "يعيد النتح التبخري لتر ملف الماء، ويجيء كيلوواط الساعة المضخ من الهوية نفسها "
            "ρgH/η، فلا يُكتب أي رقم زراعي باليد."]},
    {"fr": ["Le sol et l'eau comme dettes, pas comme charges",
            "Un horizon de 30 cm s'use à 10 t/ha/an alors qu'il se forme vingt fois plus "
            "lentement : la ferme écrit une dette, et la comptabilité se voit."],
     "en": ["Soil and water as debts, not as costs",
            "A 30 cm horizon wears at 10 t/ha/an while it forms twenty times slower: the "
            "farm is writing a debt, and the ledger shows it."],
     "ar": ["التربة والماء ديون لا نفقات",
            "يُستهلك أفق 30 cm بمعدل 10 t/ha/ سنة بينما يتكوّن أبطأ عشرين مرة: فالمزرعة "
            "تكتب دينًا، والدفتر يظهره."]},
]

# ----------------------------------------------------------------------------
# Figures : chaque valeur est relue dans le dictionnaire calculé
# ----------------------------------------------------------------------------
def detail(donnees: Dict[str, Any], eq_id: str) -> Dict[str, Any]:
    for e in donnees["equations"]:
        if e["id"] == eq_id:
            return e["detail"]
    raise KeyError(f"{eq_id} absent")


def carte(lab: Sequence[str], note: Sequence[str], valeur: str):
    return ({"fr": lab[0], "en": lab[1], "ar": lab[2]},
            {"fr": valeur, "en": valeur, "ar": valeur},
            {"fr": note[0], "en": note[1], "ar": note[2]})


# Colonne « équation source » des matériaux : le module écrit parfois un
# identifiant (EQ-nn), parfois une raison en français. La raison est traduite
# ici ; toute autre valeur inconnue fait échouer la construction.
EQUATION_SOURCE: Dict[str, Tuple[str, str]] = {
    "géométrie × densité déclarée": ("geometry × declared density",
                                      "الهندسة × الكثافة المعلَنة"),
    "EQ-09 (1 mm = 10 m³/ha)": ("EQ-09 (1 mm = 10 m³/ha)",
                                "EQ-09 (1 مم = 10 م³/هكتار)"),
    "stock P4 — surface BET déclarée": ("pillar P4 stock — declared BET surface",
                                        "رصيد العمود P4 — مساحة BET المعلَنة"),
    "stoichiométrie P2O5": ("P2O5 stoichiometry", "ستوكيوميتريا P2O5"),
    "stoichiométrie K2O": ("K2O stoichiometry", "ستوكيوميتريا K2O"),
    "EQ-16 (annualisé, photopériode 16 h)": ("EQ-16 (annualised, 16 h photoperiod)",
                                             "EQ-16 (مُسنْترة، فترة ضوئية 16 h)"),
}
EQ_VUES: set = set()


def _eq_source(cle: str) -> Dict[str, str]:
    if cle.startswith("EQ-") and len(cle) == 5 and cle[3:].isdigit():
        return {"fr": cle, "en": cle, "ar": cle}
    if cle not in EQUATION_SOURCE:
        raise KeyError(f"équation source de matériau sans traduction : {cle!r}")
    EQ_VUES.add(cle)
    en, ar = EQUATION_SOURCE[cle]
    return {"fr": cle, "en": en, "ar": ar}


def mat(ident: str, nom: Sequence[str], unite: Sequence[str],
        quantite: float, equation: str) -> Dict[str, Any]:
    return {"id": ident,
            "nom": {"fr": nom[0], "en": nom[1], "ar": nom[2]},
            "unite": {"fr": unite[0], "en": unite[1], "ar": unite[2]},
            "quantite": quantite, "equation": _eq_source(equation)}


# ----------------------------------------------------------------------------
# Libellés de figures : la clé vient du module, les trois langues sont obligatoires
# ----------------------------------------------------------------------------
LIBELLES: Dict[str, Tuple[str, str, str]] = {
    "vapeur supercritique": ("Vapeur supercritique", "Supercritical steam", "بخار فوق حرج"),
    "cycle combine gaz": ("Cycle combiné gaz", "Gas combined cycle", "دورة غازية مركّبة"),
    "diesel automobile": ("Diesel automobile", "Car diesel engine", "ديزل السيارات"),
    "solaire thermodynamique": ("Solaire thermodynamique", "Concentrated solar power",
                                "طاقة شمسية حرارية"),
    "LiFePO4 materiau actif (theorique)": ("LiFePO₄, matière active", "LiFePO₄, active material",
                                           "LiFePO₄ المادة الفعّالة"),
    "cellule Li-ion (declaree)": ("Cellule Li-ion déclarée", "Li-ion cell (declared)",
                                  "خلية ليثيوم معلَنة"),
    "graphite materiau actif (theorique)": ("Graphite, matière active",
                                            "Graphite, active material",
                                            "غرافيت المادة الفعّالة"),
    "accumulateur plomb (declare)": ("Plomb-acide (déclaré)", "Lead-acid (declared)",
                                     "رصاص-حمض (معلَن)"),
    "supercondensateur (declare)": ("Supercondensateur (déclaré)", "Supercapacitor (declared)",
                                    "مكثّاق فائق (معلَن)"),
    "stockage gravitaire 100 m": ("Eau portée à 100 m", "Water lifted to 100 m",
                                  "ماء مرفوع إلى 100 m"),
    "evap_ocean": ("Évaporation des océans", "Ocean evaporation", "تبخر المحيطات"),
    "precip_ocean": ("Précipitations sur les océans", "Rain over the oceans",
                     "هطول على المحيطات"),
    "precip_terre": ("Précipitations sur les terres", "Rain over the land", "هطول على اليابس"),
    "evap_terre": ("Évaporation des terres", "Land evaporation", "تبخر اليابس"),
    "ruissellement": ("Ruissellement vers la mer", "Runoff to the sea", "جريان إلى البحر"),
    "pompage": ("Pompage", "Pumping", "ضخّ"),
    "osmose inverse declaree": ("Osmose inverse déclarée", "Declared reverse osmosis",
                               "تناضح عكسي معلَن"),
    "borne de separation": ("Borne de séparation des sels", "Salt-separation bound",
                           "حدّ فصل الأملاح"),
    "lumiere": ("Lumière", "Light", "الضوء"),
    "azote": ("Azote", "Nitrogen", "الآزوت"),
    "phosphore": ("Phosphore", "Phosphorus", "الفوسفور"),
    "potasse": ("Potasse", "Potash", "البوتاس"),
    "eau": ("Eau", "Water", "الماء"),
    "depart": ("Départ, phosphore limitant", "Start, phosphorus limiting",
               "البداية: الفوسفور محدود"),
    "P x2": ("Phosphore ×2", "Phosphorus ×2", "فوسفور ×2"),
    "P x4": ("Phosphore ×4", "Phosphorus ×4", "فوسفور ×4"),
    "P x4 eau x2": ("Phosphore ×4 et eau ×2", "Phosphorus ×4 and water ×2",
                    "فوسفور ×4 وماء ×2"),
    "planches pleines": ("Toutes les planches à 1", "Every plank at 1", "كل الألواح عند 1"),
    "C4 sur PAR": ("C4 rapporté au PAR", "C4 against PAR", "C4 نسبة إلى PAR"),
    "C3 sur PAR": ("C3 rapporté au PAR", "C3 against PAR", "C3 نسبة إلى PAR"),
    "plafond 8.5": ("Plafond mesuré à 8,5 photons", "Ceiling measured at 8.5 photons",
                    "السقف المقاس عند 8.5 فوتون"),
    "ble 3.5": ("Blé 3.5 t/ha", "Wheat 3.5 t/ha", "قمح 3.5 t/ha"),
    "mais 10": ("Maïs 10 t/ha", "Maize 10 t/ha", "ذرة 10 t/ha"),
    "ble monde": ("Blé mondial 2.5 t/ha", "World wheat 2.5 t/ha", "قمح عالمي 2.5 t/ha"),
}
CLE_PLANCHES = {"lumière": "lumiere", "azote": "azote", "phosphore": "phosphore",
                "potasse": "potasse", "eau": "eau"}
CLE_ETATS = {"départ (P limitant)": "depart", "P ×2": "P x2", "P ×4": "P x4",
             "P ×4 et eau ×2": "P x4 eau x2", "toutes les planches ≥ 1": "planches pleines"}
AXES: Dict[str, Tuple[str, str, str]] = {
    "betz_x": ("a = vitesse aval / vitesse amont", "a = wake speed / wind speed",
               "a = سرعة الواجهة / سرعة الرياح"),
    "cp": ("C_P", "C_P", "C_P"),
}


def lib(cle: str, lang: str) -> str:
    if cle not in LIBELLES:
        raise KeyError(f"libellé de figure sans traduction : {cle}")
    return dict(zip(MOTEUR.LANGUES, LIBELLES[cle]))[lang]


def axe(cle: str, lang: str) -> str:
    return dict(zip(MOTEUR.LANGUES, AXES[cle]))[lang]


def _3(fr: str, en: str, ar: str) -> Dict[str, str]:
    return {"fr": fr, "en": en, "ar": ar}


def figures_elec(donnees: Dict[str, Any]) -> List[Dict[str, Any]]:
    d15 = detail(donnees, "EQ-15")
    d16 = detail(donnees, "EQ-16")
    wh = detail(donnees, "EQ-18")["Wh_par_kg"]
    cp = lambda a: 4.0 * a * (1.0 - a) ** 2          # noqa: E731 — la formule de EQ-15
    points = [(n / 200.0, cp(n / 200.0)) for n in range(201)]
    sommet = f"16/27 = {d15['seize_sur_vingt_sept']:.4f}"
    rendus = sorted(d16["rendements_declares"].items(), key=lambda kv: -kv[1])
    stockage = ["LiFePO4 materiau actif (theorique)", "cellule Li-ion (declaree)",
                "graphite materiau actif (theorique)", "accumulateur plomb (declare)",
                "supercondensateur (declare)", "stockage gravitaire 100 m"]
    titre1 = _3("C_P(a) = 4a(1−a)² : la limite de Betz",
                "C_P(a) = 4a(1−a)²: the Betz limit", "C_P(a) = 4a(1−a)²: حدّ بيتز")
    desc1 = _3("Coefficient de puissance d'un rotor idéal selon le glissement a = vitesse "
               "aval sur vitesse amont ; le sommet est 16/27 pour a = 1/3. Aucune hélice ne "
               "peut mieux : c'est un compte, pas un réglage.",
               "Power coefficient of an ideal rotor against the slip a = wake speed over wind "
               "speed; the peak is 16/27 at a = 1/3. No rotor does better: it is a count, "
               "not a tuning.",
               "معامل القدرة لدوّار مثالي حسب الانزلاق a = سرعة الواجهة على سرعة الرياح؛ "
               "القمة 16/27 عند a = 1/3. لا مروحة تفعل أفضل: إنه عدٌّ لا ضبط.")
    legende1 = _3("Figure 1 — EQ-15 : la formule de Betz échantillonnée de a = 0 à a = 1 ; le "
                  "sommet marqué est la valeur calculée, pas une visée d'ingénieur.",
                  "Figure 1 — EQ-15: the Betz formula sampled from a = 0 to a = 1; the marked "
                  "peak is the computed value, not an engineering target.",
                  "الشكل 1 — EQ-15: صيغة بيتز مأخوذة من a = 0 إلى a = 1؛ والقمة المشار إليها "
                  "قيمة محسوبة لا هدف هندسي.")
    titre2 = _3("Rendements thermiques déclarés sous le plafond de Carnot",
                "Declared thermal efficiencies under the Carnot ceiling",
                "كفاءات حرارية معلَنة تحت سقف كارنو")
    desc2 = _3("Quatre rendements de littérature entre 800 K et 300 K, face au plafond de "
               "Carnot calculé dans EQ-16. La ligne rouge est une limite, pas un objectif.",
               "Four literature efficiencies between 800 K and 300 K against the Carnot "
               "ceiling computed in EQ-16. The red line is a bound, not a target.",
               "أربع كفاءات من الأدبيات بين 800 K و300 K أمام سقف كارنو المحسوب في EQ-16. "
               "الخط الأحمر حدٌّ لا هدف.")
    legende2 = _3("Figure 2 — EQ-16 : le plafond 1 − T_froid/T_source = 62.50 % borne les "
                  "quatre rendements déclarés ; le meilleur atteint 97.6 % du plafond.",
                  "Figure 2 — EQ-16: the ceiling 1 − T_froid/T_source = 62.50 % bounds the "
                  "four declared efficiencies; the best reaches 97.6 % of it.",
                  "الشكل 2 — EQ-16: السقف 1 − T_froid/T_source = 62.50 % يحدّ الكفاءات "
                  "الأربع؛ وأفضلها يبلغ 97.6 % منه.")
    titre3 = _3("Stockage Wh par kg : électrochimique et gravitaire",
                "Storage in Wh per kg: electrochemical and gravitational",
                "التخزين بالـWh لكل kg: كهروكيميائي وثقالي")
    desc3 = _3("Six densités d'énergie lues dans EQ-18. Essence et hydrogène sont hors "
               "d'échelle et restent dans le tableau : l'échelle linéaire est la limite de "
               "cette figure.",
               "Six energy densities read from EQ-18. Petrol and hydrogen fall outside the "
               "scale and stay in the table: the linear scale is this figure's limit.",
               "كثافات طاقة ست مقروءة من EQ-18. البنزين والهيدروجين خارج المقياس ويبقيان في "
               "الجدول: فالمقياس الخطي حدّ هذا الشكل.")
    legende3 = _3("Figure 3 — EQ-18 : un mètre cube d'eau porté à 100 m vaut 0.272 Wh/kg, et "
                  "c'est exactement le chiffre du dossier EAU.",
                  "Figure 3 — EQ-18: one cubic metre of water lifted to 100 m is 0.272 Wh/kg, "
                  "and that is precisely the water dossier's number.",
                  "الشكل 3 — EQ-18: متر مكعّب من الماء يُرفع إلى 100 m يساوي 0.272 Wh/kg، وهو "
                  "رقم ملف الماء نفسه بالضبط.")
    svg1 = {l: MOTEUR.figure_courbe(
        titre1[l], desc1[l], points, (axe("betz_x", l), axe("cp", l)),
        [(d15["a_max_bissection"], d15["cp_max"], sommet)], ids=("fig1-t", "fig1-d"))
        for l in MOTEUR.LANGUES}
    svg2 = {l: MOTEUR.figure_barres(
        titre2[l], desc2[l],
        [(lib(cle, l), d16["rendements_declares"][cle] * 100.0, COULEURS["1f5f8b"])
         for cle, _ in rendus],
        d16["eta_carnot"] * 100.0, ids=("fig2-t", "fig2-d")) for l in MOTEUR.LANGUES}
    svg3 = {l: MOTEUR.figure_barres(
        titre3[l], desc3[l],
        [(lib(cle, l), wh[cle],
          COULEURS["or"] if "gravitaire" in cle else COULEURS["1f5f8b"]) for cle in stockage],
        None, ids=("fig3-t", "fig3-d")) for l in MOTEUR.LANGUES}
    return [{"svg": svg1, "legende": legende1},
            {"svg": svg2, "legende": legende2},
            {"svg": svg3, "legende": legende3}]


def figures_eau(donnees: Dict[str, Any]) -> List[Dict[str, Any]]:
    d11 = detail(donnees, "EQ-11")
    d6 = detail(donnees, "EQ-06")
    d9 = detail(donnees, "EQ-09")
    ordre = ["evap_ocean", "precip_ocean", "precip_terre", "evap_terre", "ruissellement"]
    flux = d11["km3_par_an"]
    titre1 = _3("Cycle de l'eau : km³ par an, bilan fermé",
                "Water cycle: km³ per year, closed balance",
                "دورة الماء: km³ في السنة، ميزان مغلق")
    desc1 = _3("Les cinq flux d'EQ-11. Le solde des terres et celui des océans valent 0.0 : "
               "la table est fermée par construction, et l'écart avec la table courante est "
               "revendiqué dans le module.",
               "The five flows of EQ-11. The land balance and the ocean balance are 0.0: the "
               "table is closed by construction, and its gap with the usual table is claimed "
               "in the module.",
               "التدفقات الخمسة في EQ-11. رصيد اليابس ورصيد المحيط يساويان 0.0: فالجدول مغلق "
               "بالبناء، والفرق عن الجدول المتداول مُصرَّح به في الوحدة.")
    legende1 = _3("Figure 1 — EQ-11 : 119 000 = 72 000 + 47 000 km³/an sur les terres ; le "
                  "volume n'est pas une ressource, c'est un débit de renouvellement.",
                  "Figure 1 — EQ-11: 119 000 = 72 000 + 47 000 km³/an over the land; the "
                  "volume is not a resource, it is a renewal rate.",
                  "الشكل 1 — EQ-11: على اليابسة 119 000 = 72 000 + 47 000 km³/سنة؛ فالحجم ليس "
                  "موردًا بل معدّل تجدّد.")
    titre2 = _3("kWh par m³ : la borne et ce que dépensent les ouvrages",
                "kWh per m³: the bound and what the works spend",
                "kWh لكل m³: الحدّ وما تصرفه المنشآت")
    desc2 = _3("Quatre hauteurs de pompage calculées par ρgH/η, l'osmose inverse déclarée et "
               "la borne de EQ-08 en ligne rouge : 0.8136 kWh/m³ est un minimum absolu, pas "
               "un devis d'usine.",
               "Four pumping heads computed by ρgH/η, the declared reverse osmosis, and the "
               "EQ-08 bound drawn as a red line: 0.8136 kWh/m³ is an absolute minimum, not a "
               "plant quote.",
               "أربعة ارتفاعات ضخّ محسوبة بـρgH/η، والتناضح العكسي المعلَن، وحدّ EQ-08 خطًا "
               "أحمر: 0.8136 kWh/m³ دنيا مطلقة لا تقدير مصنع.")
    legende2 = _3("Figure 2 — EQ-06 et EQ-08 : pomper 50 m coûte 0.2089 kWh/m³, cinq fois "
                  "moins que la borne de séparation ; les deux chiffres viennent des mêmes "
                  "identités ρgH et R·T·ln(1/x).",
                  "Figure 2 — EQ-06 and EQ-08: pumping 50 m costs 0.2089 kWh/m³, five times "
                  "below the separation bound; both numbers come from the same identities "
                  "ρgH and R·T·ln(1/x).",
                  "الشكل 2 — EQ-06 وEQ-08: ضخّ 50 m يكلّف 0.2089 kWh/m³، أي خمس حدّ الفصل؛ "
                  "والرقمان من الهويتين نفسيهما ρgH وR·T·ln(1/x).")
    titre3 = _3("Saumure produite selon la récupération, en g/kg",
                "Brine produced against recovery, in g/kg",
                "المحلول الملحي المنتَج حسب الاستخراج، بـg/kg")
    desc3 = _3("Le bilan de masse d'EQ-09 : la concentration monte plus vite que la "
               "récupération, et le modèle linéaire s'arrête vers Y ≈ 0.6, où gypse et "
               "calcaire précipitent.",
               "The mass balance of EQ-09: concentration rises faster than recovery, and the "
               "linear model stops near Y ≈ 0.6, where gypsum and calcite precipitate.",
               "ميزان الكتلة في EQ-09: التركيز يصعد أسرع من الاستخراج، والنموذج الخطي يتوقف "
               "قرب Y ≈ 0.6 حيث يترسّب الجبس والحجر الجيري.")
    legende3 = _3("Figure 3 — EQ-09 : à Y = 0.45 la saumure sort à 63.6 g/kg, soit 1.82× "
                  "l'eau de mer, et 1.22 m³ sont rejetés par m³ produit.",
                  "Figure 3 — EQ-09: at Y = 0.45 the brine leaves at 63.6 g/kg, that is 1.82× "
                  "seawater, and 1.22 m³ is rejected per m³ produced.",
                  "الشكل 3 — EQ-09: عند Y = 0.45 يخرج المحلول بـ63.6 g/kg أي 1.82 مرة ماء "
                  "البحر، ويُرفَض 1.22 m³ لكل m³ مُنتَج.")
    svg1 = {l: MOTEUR.figure_barres(
        titre1[l], desc1[l],
        [(lib(k, l), flux[k], COULEURS["1f5f8b"]) for k in ordre], None,
        ids=("fig1-t", "fig1-d")) for l in MOTEUR.LANGUES}
    svg2 = {l: MOTEUR.figure_barres(
        titre2[l], desc2[l],
        [(f"{lib('pompage', l)} {int(r['H_m'])} m", r["kWh_par_m3_rendement"],
          COULEURS["1f5f8b"]) for r in d6["table"]]
        + [(lib("osmose inverse declaree", l),
            float(donnees["valeurs_declarees"]["SEC_osmose_inverse_kWh_m3"]), COULEURS["or"]),
           (lib("borne de separation", l), donnees["resume"]["travail_minimum_kWh_m3"],
            COULEURS["gris"])],
        None, ids=("fig2-t", "fig2-d")) for l in MOTEUR.LANGUES}
    svg3 = {l: MOTEUR.figure_barres(
        titre3[l], desc3[l],
        [(f"Y = {r['Y']:.2f}", r["saumure_g_kg"],
          COULEURS["or"] if r["Y"] > 0.6 else COULEURS["1f5f8b"]) for r in d9["table"]],
        d9["c_feed_g_kg"], ids=("fig3-t", "fig3-d")) for l in MOTEUR.LANGUES}
    return [{"svg": svg1, "legende": legende1},
            {"svg": svg2, "legende": legende2},
            {"svg": svg3, "legende": legende3}]


def figures_agri(donnees: Dict[str, Any]) -> List[Dict[str, Any]]:
    d7 = detail(donnees, "EQ-07")
    d5 = detail(donnees, "EQ-05")
    d13 = detail(donnees, "EQ-13")
    planches = [(CLE_PLANCHES[k], v) for k, v in d7["planches"].items()]
    serie = [(CLE_ETATS[s["etat"]], s["rendement_t_ha"]) for s in d7["serie"]]
    titre1 = _3("Baril de Liebig : cinq planches, un seul remplissage",
                "Liebig barrel: five planks, one fill level",
                "برميل ليبيغ: خمسة ألواح ومستوى تعبئة واحد")
    desc1 = _3("Les cinq facteurs d'EQ-07 rapportés à leur valeur optimale. Le remplissage "
               "est décidé par la planche la plus courte — ici le phosphore — et non par la "
               "moyenne.",
               "The five factors of EQ-07 referred to their optimum value. The fill is set by "
               "the shortest plank — here phosphorus — not by the average.",
               "العوامل الخمسة في EQ-07 نسبة إلى قيمتها المثلى. مستوى التعبئة تقرّره أقصر لوح "
               "— هنا الفوسفور — لا المتوسط.")
    legende1 = _3("Figure 1 — EQ-07 : loi du minimum. Une seule planche borne le baril ; "
                  "c'est aussi le pilier P3 du dossier, la tolérance à la panne passe par les "
                  "planches hautes, pas par la moyenne.",
                  "Figure 1 — EQ-07: the law of the minimum. One plank alone bounds the "
                  "barrel; this is also pillar P3 of the dossier — fault tolerance comes from "
                  "the tall planks, not the average.",
                  "الشكل 1 — EQ-07: قانون الحد الأدنى. لوح واحد وحده يحدّ البرميل؛ وهو أيضًا "
                  "الركن P3 من الملف، فالتحمّل يأتي من الألواح الطويلة لا من المتوسط.")
    titre2 = _3("Rendement t/ha quand on répare les planches une à une",
                "Yield in t/ha as the planks are repaired one by one",
                "المحصول بـt/ha عند ترميم الألواح واحدًا بعد واحد")
    desc2 = _3("La série d'EQ-07 : doubler le phosphore au-delà de l'optimum ne change rien, "
               "et le gain suivant vient de l'eau. La ligne est le plafond de la variété "
               "déclarée, 3.5 t/ha.",
               "The EQ-07 series: doubling phosphorus past its optimum changes nothing, and "
               "the next gain comes from water. The line is the declared variety's ceiling, "
               "3.5 t/ha.",
               "سلسلة EQ-07: مضاعفة الفوسفور بعد مثلاه لا تغيّر شيئًا، والمكسب التالي من "
               "الماء. الخط هو سقف الصنف المعلَن، 3.5 t/ha.")
    legende2 = _3("Figure 2 — EQ-07 : P ×2 donne 2.45 t/ha, P ×4 ne donne rien de plus, puis "
                  "l'eau ×2 ouvre 2.80 t/ha. Le test est exact, ce n'est pas une opinion.",
                  "Figure 2 — EQ-07: P ×2 gives 2.45 t/ha, P ×4 adds nothing, then water ×2 "
                  "opens 2.80 t/ha. The test is exact; it is not an opinion.",
                  "الشكل 2 — EQ-07: مضاعفة الفوسفور تعطي 2.45 t/ha، ومضاعفته أربعًا لا تضيف "
                  "شيئًا، ثم مضاعفة الماء تفتح 2.80 t/ha. الاختبار دقيق لا رأي.")
    titre3 = _3("Grammes de biomasse par MJ de PAR : l'écart au plafond",
                "Grams of biomass per MJ of PAR: the gap to the ceiling",
                "غرامات كتلة حيوية لكل MJ من PAR: الفرق عن السقف")
    desc3 = _3("EQ-05 : les efficacités 6.67 et 3.33 g/MJ PAR contre le plafond "
               "thermodynamique de 42.67 g/MJ à 4 photons, tracé en rouge. Le plafond ne "
               "promet aucune récolte.",
               "EQ-05: the efficiencies 6.67 and 3.33 g/MJ PAR against the thermodynamic "
               "ceiling of 42.67 g/MJ at 4 photons, drawn in red. The ceiling promises no "
               "harvest.",
               "EQ-05: الكفاءتان 6.67 و3.33 g/MJ PAR أمام السقف الثيرموديناميكي 42.67 g/MJ عند "
               "4 فوتونات، مرسومًا بالأحمر. السقف لا يعد بحصاد.")
    legende3 = _3("Figure 3 — EQ-05 : nous sommes à 15.6 % et 33.2 % du plafond quantique. "
                  "Toute promesse agricole au-dessus de 20 g/MJ PAR est une erreur de compte.",
                  "Figure 3 — EQ-05: we sit at 15.6 % and 33.2 % of the quantum ceiling. Any "
                  "farm promise above 20 g/MJ PAR is a counting error.",
                  "الشكل 3 — EQ-05: نحن عند 15.6 % و33.2 % من السقف الكمّي. كل وعد زراعي فوق "
                  "20 g/MJ PAR خطأ في العدّ.")
    titre4 = _3("Personnes nourries par hectare et par an, en calories",
                "Persons fed per hectare per year, in calories",
                "أشخاص يُغذَّون لكل هكتار في السنة، بالسعرات")
    desc4 = _3("EQ-13 : le rapport maïs/blé vient des deux rendements déclarés, pas d'une "
               "opinion ; la troisième barre rappelle que la moyenne mondiale est plus basse.",
               "EQ-13: the maize-to-wheat ratio comes from the two declared yields, not from "
               "an opinion; the third bar recalls that the world average is lower.",
               "EQ-13: نسبة الذرة إلى القمح تجيء من المحصولين المعلَنين لا من رأي؛ واللوح "
               "الثالث يذكّر بأن المتوسط العالمي أدنى.")
    legende4 = _3("Figure 4 — EQ-13 : 15.53 personnes/ha pour le blé, 47.62 pour le maïs sur "
                  "les mêmes bonnes terres irriguées ; le ratio 3.07 est une conséquence "
                  "arithmétique.",
                  "Figure 4 — EQ-13: 15.53 persons/ha for wheat, 47.62 for maize on the same "
                  "good irrigated land; the 3.07 ratio is an arithmetic consequence.",
                  "الشكل 4 — EQ-13: 15.53 شخص/ha للقمح و47.62 للذرة على الأرض المروية الجيدة "
                  "نفسها؛ والنسبة 3.07 نتيجة حسابية.")
    svg1 = {l: MOTEUR.figure_baril(
        titre1[l], desc1[l], [(lib(k, l), v) for k, v in planches], 1.0,
        ids=("fig1-t", "fig1-d")) for l in MOTEUR.LANGUES}
    svg2 = {l: MOTEUR.figure_barres(
        titre2[l], desc2[l],
        [(lib(k, l), v,
          COULEURS["or"] if v >= d7["rendement_max_t_ha"] - 1e-9 else COULEURS["1f5f8b"])
         for k, v in serie],
        d7["rendement_max_t_ha"], ids=("fig2-t", "fig2-d")) for l in MOTEUR.LANGUES}
    svg3 = {l: MOTEUR.figure_barres(
        titre3[l], desc3[l],
        [(lib("C4 sur PAR", l), d5["eps_C4_rapporte_au_PAR"], COULEURS["vert"]),
         (lib("C3 sur PAR", l), d5["eps_C3_rapporte_au_PAR"], COULEURS["1f5f8b"]),
         (lib("plafond 8.5", l), d5["plafond_a_8_5_photons_g_par_MJ_PAR"], COULEURS["gris"])],
        d5["plafond_theorique_g_par_MJ_PAR"], ids=("fig3-t", "fig3-d"))
        for l in MOTEUR.LANGUES}
    svg4 = {l: MOTEUR.figure_barres(
        titre4[l], desc4[l],
        [(lib("ble 3.5", l), d13["ble"]["personnes_par_ha"], COULEURS["1f5f8b"]),
         (lib("mais 10", l), d13["mais"]["personnes_par_ha"], COULEURS["vert"]),
         (lib("ble monde", l), d13["personnes_par_ha_monde_reel_ble_2t5"], COULEURS["or"])],
        None, ids=("fig4-t", "fig4-d")) for l in MOTEUR.LANGUES}
    return [{"svg": svg1, "legende": legende1},
            {"svg": svg2, "legende": legende2},
            {"svg": svg3, "legende": legende3},
            {"svg": svg4, "legende": legende4}]


# ----------------------------------------------------------------------------
# Matériaux : les quantités sont dimensionnées par les équations, pas saisies
# ----------------------------------------------------------------------------
def materiaux_elec(donnees: Dict[str, Any]) -> List[Dict[str, Any]]:
    m = donnees["materiaux_declares"]
    wh = detail(donnees, "EQ-18")["Wh_par_kg"]
    return [
        mat("M-CUIEC", ("cuivre IEC (résistivité)", "IEC copper (resistivity)", "نحاس IEC (مقاومية نوعية)"),
            ("Ω·m", "Ω·m", "Ω·m"), m["resistivites_ohm_m"]["cuivre IEC"], "EQ-03"),
        mat("M-AL", ("aluminium (résistivité)", "aluminium (resistivity)", "ألومنيوم (مقاومية نوعية)"),
            ("Ω·m", "Ω·m", "Ω·m"), m["resistivites_ohm_m"]["aluminium"], "EQ-03"),
        mat("M-SI", ("silicum, bande interdite", "silicon band gap", "فجوة السيليكون"),
            ("eV", "eV", "eV"), m["bandes_gap_eV"]["Si"], "EQ-17"),
        mat("M-GAAS", ("arséniure de gallium", "gallium arsenide", "زرنيخيد الغاليوم"),
            ("eV", "eV", "eV"), m["bandes_gap_eV"]["GaAs"], "EQ-17"),
        mat("M-LFP", ("cathode LiFePO₄, matière active", "LiFePO₄ cathode, active material", "مهبط LiFePO₄ المادة الفعّالة"),
            ("Wh/kg", "Wh/kg", "Wh/kg"), wh["LiFePO4 materiau actif (theorique)"], "EQ-18"),
        mat("M-H2", ("dihydrogene, pouvoir calorifique bas", "hydrogen, lower heating value", "الهيدروجين، قيمة وقود دنيا"),
            ("Wh/kg", "Wh/kg", "Wh/kg"), wh["dihydrogene LHV"], "EQ-18"),
        mat("M-YBCO", ("YBCO, température critique", "YBCO critical temperature", "حرارة حرجة لـ YBCO"),
            ("K", "K", "K"), m["supraconducteurs"]["YBCO Tc K"], "EQ-19"),
        mat("M-NBTI", ("NbTi, température critique", "NbTi critical temperature", "حرارة حرجة لـ NbTi"),
            ("K", "K", "K"), m["supraconducteurs"]["NbTi Tc K"], "EQ-19"),
        mat("M-BETZ", ("vitesse aval optimale (Betz)", "optimal wake speed (Betz)", "سرعة الواجهة المثلى (بيتز)"),
            ("fraction de a", "fraction of a", "كسر من a"),
            detail(donnees, "EQ-15")["a_max_bissection"], "EQ-15"),
    ]


def materiaux_eau(donnees: Dict[str, Any]) -> List[Dict[str, Any]]:
    v, d7, d9 = donnees["valeurs_declarees"], detail(donnees, "EQ-07"), detail(donnees, "EQ-09")
    return [
        mat("M-NACL", ("sel de l'eau d'alimentation", "salt in the feed water", "ملح ماء التغذية"),
            ("g/kg", "g/kg", "g/kg"), d9["c_feed_g_kg"], "EQ-09"),
        mat("M-I", ("facteur de van 't Hoff effectif (NaCl)", "effective van 't Hoff factor (NaCl)", "عامل فانت هوف الفعّال (NaCl)"),
            ("osmoles/formule", "osmoles per formula", "أ اسموز/صيغة"), d7["i_effectif_declare"], "EQ-07"),
        mat("M-RO", ("osmose inverse, énergie spécifique déclarée", "reverse osmosis, declared specific energy", "التناضح العكسي، طاقة نوعية معلَنة"),
            ("kWh/m³", "kWh/m³", "kWh/m³"), float(v["SEC_osmose_inverse_kWh_m3"]), "EQ-08"),
        mat("M-Y", ("récupération pratique de la ligne", "practical line recovery", "نسبة الاستخراج العملية"),
            ("fraction", "fraction", "كسر"), float(v["recuperation_RO"]), "EQ-09"),
        mat("M-BAR", ("pression d'usine déclarée", "declared plant pressure", "ضغط المصنع المعلَن"),
            ("bar", "bar", "bar"), float(v["pression_usine_RO_bar"]), "EQ-07"),
        mat("M-COLONNE", ("colonne d'eau équivalente à π", "water column equivalent to π", "عمود ماء يعادل π"),
            ("m", "m", "m"), d7["hauteur_equivalente_m"], "EQ-07"),
        mat("M-L", ("chaleur latente de vaporisation", "latent heat of vaporisation", "حرارة التبخر الكامنة"),
            ("J/kg", "J/kg", "J/kg"), float(v["chaleur_latente_J_kg"]), "EQ-10"),
        mat("M-FUITES", ("fuites réseau déclarées", "declared network leaks", "تسرب الشبكة المعلَن"),
            ("fraction", "fraction", "كسر"), float(v["fuites_reseau_pct"]), "EQ-12"),
        mat("M-POT", ("seuil de potabilité en sel", "salinity potability threshold", "عتبة الملوحة للشرب"),
            ("g/kg", "g/kg", "g/kg"), detail(donnees, "EQ-13")["seuil_potable_g_kg"], "EQ-13"),
    ]


def materiaux_agri(donnees: Dict[str, Any]) -> List[Dict[str, Any]]:
    tabelles = {m["materiau"]: m for m in detail(donnees, "EQ-17")["materiaux"]}
    noms = [
        ("azote ammoniacal (Haber-Bosch, catalyseur fer)", "anhydrous ammonia (Haber-Bosch, iron catalyst)", "نشادر لا مائي (هابر-بوش، حفّاز حديد)"),
        ("film de paillage polyéthylène, 30 µm", "polyethylene mulch film, 30 µm", "غطاء بولي إيثيلين 30 µm"),
        ("hydrogel absorbant (SAP) pour tamponner 20 mm", "water-absorbing gel (SAP) buffering 20 mm", "هلام ماص للماء (SAP) لخبز 20 mm"),
        ("biochar, 10 t/ha à 60 % de carbone", "biochar, 10 t/ha at 60 % carbon", "فحم حيوي 10 t/ha بنسبة كربون 60 %"),
        ("minerai phosphaté (30 % P2O5) pour 25 kg P/ha", "phosphate ore (30 % P2O5) for 25 kg P/ha", "خام فوسفات (30 % P2O5) لـ25 kg P/ha"),
        ("potasse KCl (60 % K2O) pour 30 kg K/ha", "potash KCl (60 % K2O) for 30 kg K/ha", "بوتاس KCl (60 % K2O) لـ30 kg K/ha"),
        ("LED 660 nm (AlGaInP) pour un DLI de 15 mol", "660 nm LED (AlGaInP) for a 15 mol daily dose", "مصباح LED 660 nm (AlGaInP) لجرعة 15 mol"),
        ("eau prélevée en goutte-à-goutte", "water drawn by drip irrigation", "ماء مسحوب بالري بالتنقيط"),
    ]
    unites = [
        ("kg NH3/an", "kg NH3/yr", "كغ نشادر/سنة"),
        ("kg/ha", "kg/ha", "كغ/ها"),
        ("kg/ha en eau douce", "kg/ha in fresh water", "كغ/ها في ماء عذب"),
        ("kg/ha", "kg/ha", "كغ/ها"),
        ("kg/ha", "kg/ha", "كغ/ها"),
        ("kg/ha", "kg/ha", "كغ/ها"),
        ("kW installés/ha", "installed kW/ha", "kW مركّب/ها"),
        ("m³/ha", "m³/ha", "m³/ها"),
    ]
    out = []
    for (cle, _), nom, unite in zip(tabelles.items(), noms, unites):
        m = tabelles[cle]
        out.append(mat(f"M-{len(out) + 1:02d}", nom, unite, float(m["quantite_par_ha"]), m["equation"]))
    return out


# ----------------------------------------------------------------------------
# Spécifications des trois pages
# ----------------------------------------------------------------------------
COMMANDES = {
    "fr": ("# depuis la racine du dépôt\n"
           "py -3 ABONDANCE/electricite_abondance.py     # 21 équations, 21 contrôles\n"
           "py -3 ABONDANCE/eau_abondance.py            # 15 équations, 15 contrôles\n"
           "py -3 ABONDANCE/agriculture_abondance.py    # 18 équations, 18 contrôles\n"
           "py -3 ABONDANCE/generer_abondance.py        # régénère pages, figures, JSON, CSV, Markdown\n"
           "# hors Windows : remplacer py -3 par python3"),
    "en": ("# from the repository root\n"
           "py -3 ABONDANCE/electricite_abondance.py     # 21 equations, 21 checks\n"
           "py -3 ABONDANCE/eau_abondance.py            # 15 equations, 15 checks\n"
           "py -3 ABONDANCE/agriculture_abondance.py    # 18 equations, 18 checks\n"
           "py -3 ABONDANCE/generer_abondance.py        # rebuilds pages, figures, JSON, CSV, Markdown\n"
           "# off Windows: replace py -3 with python3"),
    "ar": ("# من جذر المستودع\n"
           "py -3 ABONDANCE/electricite_abondance.py     # 21 معادلة و21 تحقّق\n"
           "py -3 ABONDANCE/eau_abondance.py            # 15 معادلة و15 تحقّق\n"
           "py -3 ABONDANCE/agriculture_abondance.py    # 18 معادلة و18 تحقّق\n"
           "py -3 ABONDANCE/generer_abondance.py        # يعيد بناء الصفحات والأشكال وJSON وCSV وMarkdown\n"
           "# خارج ويندوز: استبدل py -3 بـ python3"),
}

SOURCE_ELEC_FR = (
    "Point de départ : « Électricité : tout s'éclaire ! » (Déclics, ARTE ; chaîne ARTE, "
    "vidéo cFx7Cm-c2nA, 1565 s, scénario Pierre Lergenmüller, France 2020, 26 mn). La "
    "page publique de la vidéo ne publie aucun chapitre et ses sous-titres renvoient 0 "
    "octet en json3, srv3 et xml : la vidéo a fourni une méthode et des thèmes, jamais "
    "une citation ni un chiffre. Les prédécesseurs nommés sont ceux des lois utilisées ; "
    "pour chaque équation, SOURCES_ET_PREDECESSEURS.md, à la racine du dossier, distingue "
    "la loi calculée et contrôlée ici, la valeur déclarée de littérature et le nom de lignée.")
SOURCE_EAU_FR = (
    "Ce dossier ne part pas d'une table de chiffres mais des mêmes constantes : l'eau "
    "reçoit ρgH du dossier ÉLECTRICITÉ et rend le kWh/m³ de pompage que l'agriculture "
    "utilisera. Prédécesseurs nommés : Thalès (l'eau comme principe), Archimède "
    "(poussée), Pascal (pression transmise), Bernoulli (énergie du mouvement), Darcy "
    "(écoulement en milieu poreux), van 't Hoff et Pfeffer (osmose), Gibbs (travail de "
    "mélange), Loeb et Sourirajan (membrane asymétrique pour le dessalement) ; leurs "
    "performances restent des valeurs déclarées, non mesurées ici. Darcy, Pfeffer, Loeb et "
    "Sourirajan ne portent aucune équation de ce dossier : noms de lignée, comme le détaille "
    "SOURCES_ET_PREDECESSEURS.md à la racine.")
SOURCE_AGRI_FR = (
    "La vidéo d'origine est une vidéo d'électricité : elle ne fournit AUCUNE donnée "
    "agricole. L'agriculture est notre extension, construite avec le même patron, et "
    "elle repose sur les prédécesseurs nommés suivants : Thalès et Anaximandre, puis "
    "Théophraste ; Boussingault et Liebig (loi du minimum), Blackman (facteur limitant), "
    "Calvin (cycle du carbone), Haber et Bosch (ammoniac), Monteith (Ray Use Efficiency), "
    "Allan (eau virtuelle) et Hoekstra (empreinte eau), van 't Hoff et Pfeffer (osmose). "
    "Thalès, Anaximandre et Théophraste y sont des noms de lignée : aucune des dix-huit "
    "équations ne repose sur eux, et SOURCES_ET_PREDECESSEURS.md, à la racine du dossier, "
    "classe chaque équation en loi calculée, valeur déclarée ou nom de lignée.")

LIGNE_ELEC = ("Coulomb → Volta → Ampère → Ohm → Faraday → Lenz → Henry → Joule → "
             "Kirchhoff → Maxwell → J. J. Thomson → W. Thomson (Kelvin) → Tesla → "
             "Steinmetz → Planck → Onnes → BCS → Betz → Carnot → Shockley–Queisser")
LIGNE_EAU = ("Thalès → Archimède → Pascal → Torricelli → Bernoulli → Darcy → van 't Hoff "
             "→ Pfeffer → Clausius et Clapeyron → Magnus → Alduchov et Eskridge → Raoult "
             "→ Gibbs → Loeb → Sourirajan")
LIGNE_AGR = ("Planck → Stefan → Boltzmann → Boussingault → Liebig → Blackman → Calvin "
             "→ Benson → Farquhar → Haber → Bosch → Monteith → Allan → Hoekstra "
             "→ van 't Hoff → Pfeffer")


def _chemins(slug: str) -> Dict[str, str]:
    return {"fr": f"{slug}.html", "en": f"{slug}_en.html", "ar": f"{slug}_ar.html"}


def _nav(chemins: Dict[str, str]) -> List[Sequence[str]]:
    return [("fr", "Français", chemins["fr"]), ("en", "English", chemins["en"]),
            ("ar", "العربية", chemins["ar"])]


def _liens(slug: str) -> List[Dict[str, Any]]:
    dep = "../donnees/"
    return [
        {"href": f"{dep}{slug}.json", "libelle": {"fr": "JSON calculé", "en": "Computed JSON",
                                                  "ar": "JSON المحسوب"}},
        {"href": f"{dep}{slug}.csv", "libelle": {"fr": "CSV Excel", "en": "Excel CSV",
                                                  "ar": "CSV لإكسل"}},
        {"href": f"../dossiers/{slug}.md", "libelle": {"fr": "Dossier markdown",
                                                       "en": "Markdown dossier",
                                                       "ar": "ملف Markdown"}},
        {"href": DOI_CONCEPT, "libelle": {"fr": "DOI du dépôt", "en": "Deposit DOI",
                                          "ar": "معرف الكائن"}},
        {"href": "https://github.com/IMAM8MAHDI/AL-MIZAN-Quantum-Emulator",
         "libelle": {"fr": "Source sur GitHub", "en": "Source on GitHub",
                     "ar": "المصدر على GitHub"}},
    ]


def spec_elec(donnees: Dict[str, Any]) -> Dict[str, Any]:
    ch, r = _chemins("electricite"), donnees["resume"]
    return {
        "module": "electricite_abondance.py", "slug": "electricite", "chemins": ch,
        "theme": {"fr": "ÉLECTRICITÉ & ABONDANCE ÉNERGÉTIQUE",
                  "en": "ELECTRICITY AND ENERGY ABUNDANCE",
                  "ar": "الكهرباء ووفرة الطاقة"},
        "description": {
            "fr": "21 équations de l'électricité, du coulomb au panneau solaire, chacune "
                  "calculée, contrôlée et traduite en anglais et en arabe.",
            "en": "Twenty-one equations of electricity, from the coulomb to the solar "
                  "panel, each computed, checked, and translated into English and Arabic.",
            "ar": "إحدى وعشرون معادلة للكهرباء، من الكولوم إلى اللوح الشمسي، كلٌّ منها "
                  "محسوب ومُتحقَّق منه ومترجَم إلى الإنجليزية والعربية."},
        "titre_bande": {"fr": "ABONDANCE — AL-MIZAN × ASTRO-Q°ODE",
                        "en": "ABUNDANCE — AL-MIZAN × ASTRO-Q°ODE",
                        "ar": "الوفرة — الميزان × ASTRO-Q°ODE"},
        "eq_text": ELEC_TEXT, "cheminement": ELEC_CHEMINEMENT,
        "figures": figures_elec(donnees),
        "resultats": [
            carte(("Limite de Betz C_P,max", "Betz limit C_P,max", "حدّ بيتز C_P,max"),
                  ("16/27 : une hélice idéale ne capture pas plus, quelle que soit sa taille.",
                   "16/27: an ideal rotor captures no more, whatever its size.",
                   "16/27: المرونة المثالية لا تقتطف أكثر، مهما كان حجمها."),
                  MOTEUR._fmt(r["betz_max"])),
            carte(("Carnot 800 K / 300 K", "Carnot 800 K / 300 K", "كارنو 800 K / 300 K"),
                  ("Le plafond thermique : 62.50 % de la chaleur devient travail.",
                   "The thermal ceiling: 62.50 % of the heat becomes work.",
                   "السقف الحراري: 62.50 % من الحرارة يتحوّل شغلًا."),
                  f"{r['carnot_800_300_K'] * 100:.2f} %"),
            carte(("Seuil du silicium", "Silicon threshold", "عتبة السيليكون"),
                  ("Au-delà de cette longueur d'onde le photon ne produit rien.",
                   "Beyond this wavelength the photon produces nothing.",
                   "فوق هذا الطول الموجي لا ينتج الفوتون شيئًا."),
                  f"{r['seuil_Si_nm']:.1f} nm"),
            carte(("Pertes d'une ligne de 1 GW à 400 kV", "Losses of a 1 GW line at 400 kV",
                   "فقد خط 1 GW عند 400 kV"),
                  ("Contre 3.12 × 10^11 W à 400 V : six ordres de grandeur.",
                   "Against 3.12 × 10^11 W at 400 V: six orders of magnitude.",
                   "مقابل 3.12 × 10^11 W عند 400 V: ست درجات من المقدار."),
                  "3.12 × 10^5 W"),
            carte(("Puissance solaire interceptée par la Terre",
                   "Solar power intercepted by the Earth", "القدرة الشمسية التي تعترضها الأرض"),
                  ("9 135 fois la consommation déclarée : le flux ne manque pas.",
                   "9 135 times the declared consumption: the flow is not the shortage.",
                   "9 135 مرة الاستهلاك المعلَن: التدفق ليس هو النقص."),
                  "1.74 × 10^17 W"),
            carte(("Surface pour 20 TW à 22 %", "Area for 20 TW at 22 %", "مساحة 20 TW عند 22 %"),
                  ("0.04 % des terres émergées : la contrainte est le câblage, pas la lumière.",
                   "0.04 % of emerged land: the constraint is wiring, not sunlight.",
                   "0.04 % من اليابس: القيد في الأسلاك لا في الضوء."),
                  f"{r['surface_utile_km2_pour_20TW']:.0f} km²"),
        ],
        "materiaux": materiaux_elec(donnees),
        "caption_materiaux": {
            "fr": "Matériaux et constantes déclarés dont se servent les équations : "
                  "valeurs de littérature, non mesurées dans ce dépôt.",
            "en": "Declared materials and constants that the equations use: literature "
                  "values, not measured in this deposit.",
            "ar": "مواد وثوابت معلَنة تستعملها المعادلات: قيم من الأدبيات لم تُقس في هذا "
                  "الإيداع."},
        "sources": {"fr": SOURCE_ELEC_FR,
                    "en": "Starting point: « Électricité : tout s'éclaire ! » (Déclics, "
                          "ARTE; video cFx7Cm-c2nA, 1565 s, written by Pierre Lergenmüller, "
                          "France 2020, 26 min). The public page publishes no chapters and "
                          "its captions return 0 bytes in json3, srv3 and xml: the video "
                          "supplied a method and themes, never a quotation or a number. The "
                          "predecessors named here own the laws used; for each equation, "
                          "SOURCES_ET_PREDECESSEURS.md, at the root of this dossier, separates "
                          "a law computed and checked here, a declared literature value and a "
                          "lineage-only name.",
                    "ar": "نقطة البداية: «Électricité : tout s'éclaire !» (Déclics، قناة "
                          "ARTE، الفيديو cFx7Cm-c2nA، 1565 s، كتابة Pierre Lergenmüller، "
                          "فرنسا 2020، 26 دقيقة). لا تنشر الصفحة أي فصول وترجع ترجمة "
                          "الفيديو 0 بايت بصيغ json3 وsrv3 وxml: فقد أعطى الفيديو طريقة "
                          "ومواضيع، لا اقتباسًا ولا رقمًا. والسابقون المسمّون هنا أصحاب "
                          "القوانين المستعملة؛ ولكل معادلة، يفرّق ملف "
                          "SOURCES_ET_PREDECESSEURS.md، في جذر هذا الملف، بين قانون يُحسب "
                          "ويُتحقَّق منه هنا، وقيمة معلَنة من الأدبيات، واسم نسب فقط."},
        "fil_conducteur": LIGNE_ELEC,
        "commandes": COMMANDES,
        "liens": _liens("electricite"), "index_href": "index.html",
        "index_libelle": {"fr": "Tableau de bord des trois dossiers",
                          "en": "Dashboard of the three dossiers",
                          "ar": "لوحة الملفات الثلاثة"},
        "chapitres_nav": _nav(ch), "doi": DOI_CONCEPT,
    }


def spec_eau(donnees: Dict[str, Any]) -> Dict[str, Any]:
    ch, r = _chemins("eau"), donnees["resume"]
    return {
        "module": "eau_abondance.py", "slug": "eau", "chemins": ch,
        "theme": {"fr": "EAU — ABONDANCE, DESSALEMENT ET CYCLE",
                  "en": "WATER — ABUNDANCE, DESALINATION AND CYCLE",
                  "ar": "الماء — الوفرة وإزالة الملوحة والدورة"},
        "description": {
            "fr": "15 équations de l'eau : pression, poussée, osmose, dessalement et "
                  "cycle planétaire, avec la borne thermodynamique du kWh/m³.",
            "en": "Fifteen equations of water: pressure, buoyancy, osmosis, desalination "
                  "and the planetary cycle, with the thermodynamic bound in kWh/m³.",
            "ar": "خمس عشرة معادلة للماء: الضغط والطفاحة والتناضح وإزالة الملوحة والدورة "
                  "الكوكبية، مع الحدّ الثيرموديناميكي بـkWh/m³."},
        "titre_bande": {"fr": "ABONDANCE — AL-MIZAN × ASTRO-Q°ODE",
                        "en": "ABUNDANCE — AL-MIZAN × ASTRO-Q°ODE",
                        "ar": "الوفرة — الميزان × ASTRO-Q°ODE"},
        "eq_text": EAU_TEXT, "cheminement": EAU_CHEMINEMENT,
        "figures": figures_eau(donnees),
        "resultats": [
            carte(("Borne thermodynamique du sel", "Thermodynamic bound on salt",
                   "الحدّ الثيرموديناميكي للأملاح"),
                  ("En dessous de ce chiffre, séparer l'eau du sel est impossible.",
                   "Below this number, separating water from salt is impossible.",
                   "تحت هذا الرقم لا يمكن فصل الماء عن الملح."),
                  f"{r['travail_minimum_kWh_m3']:.4f} kWh/m³"),
            carte(("Pression osmotique de l'eau de mer", "Osmotic pressure of seawater",
                   "الضغط الأسموزي لماء البحر"),
                  ("Idéale, calculée par R·T·c ; réelle, corrigée par i = 1.78.",
                   "Ideal, computed by R·T·c; real, corrected by i = 1.78.",
                   "مثالية محسوبة بـR·T·c، وواقعية مصحّحة بـi = 1.78."),
                  f"{r['pression_osmotique_ideale_bar']:.2f} bar"),
            carte(("Pompage sous 50 m", "Pumping under 50 m", "الضخّ تحت 50 m"),
                  ("Le chiffre repris mot pour mot par le dossier agriculture.",
                   "The number the agriculture dossier takes word for word.",
                   "الرقم الذي يأخذه ملف الزراعة حرفيًا."),
                  f"{r['pompage_50m_kWh_m3']:.4f} kWh/m³"),
            carte(("Un km³ d'eau stocké sous 100 m", "One km³ of water stored under 100 m",
                   "كيلومتر مكعّب من الماء تحت 100 m"),
                  ("Identique au calcul du dossier ÉLECTRICITÉ : 0.00 écart.",
                   "Identical to the electricity dossier's computation: 0.00 gap.",
                   "مطابق لحساب ملف الكهرباء: الفرق 0.00."),
                  f"{r['energie_1km3_sous_100m_GWh']:.1f} GWh"),
            carte(("Précipitations sur les terres", "Rain over the land", "هطول على اليابس"),
                  ("Le volume renouvelable, pas le stock : c'est là que l'agriculture puise.",
                   "The renewable flow, not the stock: this is where farming draws.",
                   "التدفق المتجدّد لا المخزون: من هنا تسحب الزراعة."),
                  f"{r['precipitations_terre_mm_par_an']:.0f} mm/an"),
            carte(("Eau virtuelle d'un régime déclaré", "Virtual water of a declared diet",
                   "ماء افتراضي لنظام غذائي معلَن"),
                  ("Quinze fois le robinet : la vraie consommation est agricole.",
                   "Fifteen times the tap: the real consumption is agricultural.",
                   "خمسة عشر مرة الحنفية: الاستهلاك الحقيقي زراعي."),
                  f"{r['eau_virtuelle_L_par_personne_par_jour']:.0f} L/j"),
        ],
        "materiaux": materiaux_eau(donnees),
        "caption_materiaux": {
            "fr": "Valeurs déclarées et grandeurs calculées qui entrent dans les équations : "
                  "les premières sont de littérature, les secondes sont contrôlées.",
            "en": "Declared values and computed quantities used by the equations: the first "
                  "come from literature, the second are checked.",
            "ar": "قيم معلَنة ومقادير محسوبة تدخل في المعادلات: الأولى من الأدبيات والثانية "
                  "مُتحقَّق منها."},
        "sources": {"fr": SOURCE_EAU_FR,
                    "en": "This dossier starts from constants, not from a table of numbers: "
                          "water receives ρgH from the electricity dossier and returns the "
                          "pumping kWh/m³ that agriculture will spend. Predecessors named: "
                          "Thales (water as first principle), Archimedes (buoyancy), Pascal "
                          "(transmitted pressure), Bernoulli (energy of motion), Darcy "
                          "(flow through rock), van 't Hoff and Pfeffer (osmotic pressure "
                          "and osmometry), Gibbs (mixing work), Loeb and Sourirajan "
                          "(asymmetric membrane for desalination); their performances stay "
                          "declared figures, not measured here. Darcy, Pfeffer, Loeb and "
                          "Sourirajan carry no equation in this dossier: lineage-only names, "
                          "as SOURCES_ET_PREDECESSEURS.md at the root spells out.",
                    "ar": "لا يبدأ هذا الملف من جدول أرقام بل من ثوابت: يأخذ الماء ρgH من "
                          "ملف الكهرباء ويعيد kWh/m³ الضخّ الذي ستصرفه الزراعة. والسابقون: "
                          "طاليس (الماء مبدأً)، وأرشميدس (الطفاحة)، وباسكال (الضغط المنقول)، "
                          "وبيرنولي (طاقة الحركة)، ودارسي (الجريان في الصخر)، وفانت هوف "
                          "وفيفر (الضغط الأسموزي وقياسه)، وجيبس (شغل الخلط)، ولوب "
                          "وسوريراجان (الغشاء غير المتماثل للتحلية)؛ وأداء هؤلاء قيم "
                          "معلَنة لا مقاسة هنا. ودارسي وفيفر ولوب وسوريراجان لا يحملون أي "
                          "معادلة في هذا الملف: أسماء نسب فقط، كما يفرّق ملف "
                          "SOURCES_ET_PREDECESSEURS.md في جذر الملفات."},
        "fil_conducteur": LIGNE_EAU,
        "commandes": COMMANDES,
        "liens": _liens("eau"), "index_href": "index.html",
        "index_libelle": {"fr": "Tableau de bord des trois dossiers",
                          "en": "Dashboard of the three dossiers",
                          "ar": "لوحة الملفات الثلاثة"},
        "chapitres_nav": _nav(ch), "doi": DOI_CONCEPT,
    }


def spec_agri(donnees: Dict[str, Any]) -> Dict[str, Any]:
    ch, r = _chemins("agriculture"), donnees["resume"]
    return {
        "module": "agriculture_abondance.py", "slug": "agriculture", "chemins": ch,
        "theme": {"fr": "AGRICULTURE — DU PHOTON À L'ASSIETTE",
                  "en": "AGRICULTURE — FROM PHOTON TO PLATE",
                  "ar": "الزراعة — من الفوتون إلى الطبق"},
        "description": {
            "fr": "18 équations agricoles : photons, loi du minimum, azote de Haber, eau, "
                  "sol et matériaux — l'extension de la vidéo d'électricité.",
            "en": "Eighteen agricultural equations: photons, the minimum law, Haber "
                  "nitrogen, water, soil and materials — the extension of the electricity "
                  "video.",
            "ar": "ثماني عشرة معادلة زراعية: فوتونات، قانون الحد الأدنى، آزوت هابر، ماء "
                  "وتربة ومواد — امتداد فيديو الكهرباء."},
        "titre_bande": {"fr": "ABONDANCE — AL-MIZAN × ASTRO-Q°ODE",
                        "en": "ABUNDANCE — AL-MIZAN × ASTRO-Q°ODE",
                        "ar": "الوفرة — الميزان × ASTRO-Q°ODE"},
        "eq_text": AGRI_TEXT, "cheminement": AGRI_CHEMINEMENT,
        "figures": figures_agri(donnees),
        "resultats": [
            carte(("Plafond quantique à 8,5 photons", "Quantum ceiling at 8.5 photons",
                   "سقف كمّي عند 8.5 فوتون"),
                  ("Au-dessus de ce chiffre, la promesse agricole est une erreur de compte.",
                   "Above this number, a farm promise is a counting error.",
                   "فوق هذا الرقم يكون الوعد الزراعي خطأً في العدّ."),
                  f"{r['plafond_quantique_g_par_MJ_PAR']:.2f} g/MJ PAR"),
            carte(("Un einstein à 680 nm", "One einstein at 680 nm", "إينشتاين عند 680 nm"),
                  ("Le prix en kJ de la mole de photons : le compte des 4 photons.",
                   "The price in kJ of a mole of photons: the four-photon count.",
                   "ثمن المول من الفوتونات بالkJ: عدّ الفوتونات الأربع."),
                  f"{r['einstein_680nm_kJ']:.2f} kJ/mol"),
            carte(("Azote du vent à l'ammoniac", "Nitrogen from air to ammonia",
                   "الآزوت من الهواء إلى النشادر"),
                  ("Le prix de sortie de la faim saisonnière, en énergie.",
                   "The price of leaving seasonal hunger, in energy.",
                   "ثمن الخروج من الجوع الموسمي، بالطاقة."),
                  f"{r['MJ_par_kg_N_haber']:.2f} MJ/kg N"),
            carte(("Litres par kg de blé", "Litres per kg of wheat", "لتر لكل kg قمح"),
                  ("Dérivé de l'évapotranspiration, à 4.8 % du chiffre déclaré.",
                   "Derived from evapotranspiration, 4.8 % from the declared figure.",
                   "مشتق من النتح التبخري، بفارق 4.8 % عن الرقم المعلَن."),
                  f"{r['litres_par_kg_ble_derive']:.2f} L/kg"),
            carte(("Personnes par hectare de blé", "Persons per hectare of wheat",
                   "أشخاص لكل ها قمح"),
                  ("En calories, sur les bonnes terres irriguées déclarées.",
                   "In calories, on the declared good irrigated land.",
                   "بالسعرات، على الأرض المروية الجيدة المعلَنة."),
                  f"{r['personnes_par_ha_ble']:.2f}"),
            carte(("Céréales pour 8 milliards", "Cereals for eight billion",
                   "حبوب لثمانية مليارات"),
                  ("Sur 1400 Mha de cultivable déclaré : 2.7 fois la surface nécessaire.",
                   "Against 1400 Mha of declared arable land: 2.7 times the needed area.",
                   "مقابل 1400 Mha من الأرض الصالحة للزراعة المعلَنة: 2.7 مرة المساحة اللازمة."),
                  f"{r['surface_monde_Mha']:.0f} Mha"),
            carte(("Sol avant disparition", "Soil before loss", "التربة قبل الزوال"),
                  ("À 10 t/ha/an contre une formation vingt fois plus lente.",
                   "At 10 t/ha/an against a formation twenty times slower.",
                   "بمعدل 10 t/ha/سنة مقابل تكوين أبطأ عشرين مرة."),
                  f"{r['annees_de_sol_reste']:.0f} ans"),
            carte(("Tomate sous LED, lumière seule", "LED tomato, light alone",
                   "طماطم تحت LED، الضوء وحده"),
                  ("Le kWh/kg sans le climatiseur ni la construction.",
                   "The kWh/kg without air conditioning or construction.",
                   "kWh/kg دون التكييف أو البناء."),
                  f"{r['kWh_par_kg_tomate_led']:.2f} kWh/kg"),
        ],
        "materiaux": materiaux_agri(donnees),
        "caption_materiaux": {
            "fr": "Huit matériaux dimensionnés par les équations du dossier pour un hectare "
                  "de blé : les quantités sont calculées, les propriétés sont déclarées.",
            "en": "Eight materials sized by the dossier's equations for one hectare of "
                  "wheat: the quantities are computed, the properties are declared.",
            "ar": "ثماني مواد مقدَّرة بمعادلات الملف لهكتار واحد من القمح: الكميات محسوبة "
                  "والخواص معلَنة."},
        "sources": {"fr": SOURCE_AGRI_FR,
                    "en": "The source video is about electricity: it supplies NO agricultural "
                          "data — no yield, no photosynthesis value, no material is taken "
                          "from it. Agriculture is our own extension, built with the same "
                          "patron, and it stands on named predecessors: Thales and "
                          "Anaximander, then Theophrastus on plants; Boussingault and Liebig "
                          "for the law of the minimum; Blackman on limiting factors; Calvin "
                          "on the carbon cycle; Haber and Bosch on ammonia; Monteith on "
                          "radiation use efficiency; Allan on virtual water and Hoekstra on "
                          "the water footprint; van 't Hoff and Pfeffer on osmosis. Thales, "
                          "Anaximander and Theophrastus are lineage-only names here: none of "
                          "the eighteen equations rests on them, and "
                          "SOURCES_ET_PREDECESSEURS.md, at the root of this dossier, sorts "
                          "every equation into computed law, declared value or lineage name.",
                    "ar": "الفيديو المصدر كهربائي: لا يقدّم أي بيانات زراعية — لا محصول ولا "
                          "قيمة بناء ضوئي ولا مادة مأخوذة منه. فالزراعة امتدادنا الخاص، "
                          "مبنيًا بالنمط نفسه، وتستند إلى سابقين مسمّين: طاليس وأنافكسيمندر، "
                          "ثم ثيوفراستوس في النبات، وبوسينغو وليبيغ لقانون الحد الأدنى، "
                          "وبلاكمان للعامل المحدود، وكالفن لدورة الكربون، وهابر وبوش للنشادر، "
                          "ومونتايث لكفاءة استخدام الإشعاع، وألان للماء الافتراضي وهوكسترا "
                          "لبصمة الماء، وفانت هوف وفيفر للأسموزة. وطاليس وأنافكسيمندر "
                          "وثيوفراستوس أسماء نسب فقط: لا معادلة من الثماني عشرة تستند إليهم، "
                          "وملف SOURCES_ET_PREDECESSEURS.md، في جذر هذا الملف، يفرز كل معادلة "
                          "بين قانون محسوب وقيمة معلَنة واسم نسب."},
        "fil_conducteur": LIGNE_AGR,
        "commandes": COMMANDES,
        "liens": _liens("agriculture"), "index_href": "index.html",
        "index_libelle": {"fr": "Tableau de bord des trois dossiers",
                          "en": "Dashboard of the three dossiers",
                          "ar": "لوحة الملفات الثلاثة"},
        "chapitres_nav": _nav(ch), "doi": DOI_CONCEPT,
    }


# ----------------------------------------------------------------------------
# Tableau de bord
# ----------------------------------------------------------------------------
TITRE_INDEX = {"fr": "ABONDANCE — trois dossiers calculés",
               "en": "ABUNDANCE — three computed dossiers",
               "ar": "الوفرة — ثلاثة ملفات محسوبة"}
DESC_INDEX = {
    "fr": "Électricité, eau, agriculture : 54 équations, 54 contrôles, neuf pages "
          "trilingues, figures SVG, JSON, CSV et Markdown calculés par les modules.",
    "en": "Electricity, water, agriculture: fifty-four equations, fifty-four checks, nine "
          "trilingual pages, SVG figures, JSON, CSV and Markdown computed by the modules.",
    "ar": "كهرباء وماء وزراعة: 54 معادلة و54 تحقّقًا وتسع صفحات ثلاثية وأشكال SVG وملفات "
          "JSON وCSV وMarkdown تحسبها الوحدات."}


LIBELLES_DOSSIER = {
    "electricite": {"fr": "Électricité", "en": "Electricity", "ar": "الكهرباء"},
    "eau": {"fr": "Eau", "en": "Water", "ar": "الماء"},
    "agriculture": {"fr": "Agriculture", "en": "Agriculture", "ar": "الزراعة"},
}
INDEX_ENTETES = {
    "fr": ["Dossier", "Équations", "Contrôles reçus", "OPÉRATIONNEL", "SIMULÉ",
           "SPÉCIFIÉ", "Pages", "Données"],
    "en": ["Dossier", "Equations", "Checks met", "OPERATIONAL", "SIMULATED",
           "SPECIFIED", "Pages", "Data"],
    "ar": ["الملف", "المعادلات", "التحققات المستوفاة", "عامل", "محاكى", "محدَّد",
           "الصفحات", "البيانات"],
}
INDEX_BOUTONS = {
    "fr": ["Aller au dossier Électricité", "Aller au dossier Eau",
           "Aller au dossier Agriculture", "Revenir au dépôt"],
    "en": ["Go to the electricity dossier", "Go to the water dossier",
           "Go to the agriculture dossier", "Back to the deposit"],
    "ar": ["اذهب إلى ملف الكهرباء", "اذهب إلى ملف الماء", "اذهب إلى ملف الزراعة",
           "العودة إلى الإيداع"],
}
INDEX_REPRO = {
    "fr": "Trois modules calculent, ce générateur met en forme. Aucun nombre de page "
          "n'est saisi à la main : supprimer un artefact et relancer le générateur le "
          "reproduit à l'octet près.",
    "en": "Three modules compute, this generator formats. No page number is typed by "
          "hand: delete an artefact, re-run the generator, and it comes back byte for "
          "byte.",
    "ar": "ثلاث وحدات تحسب وهذا المولّد ينسّق. لا يُكتب أي رقم في الصفحة باليد: احذف "
          "المُخرَج وأعد تشغيل المولّد فيعود حرفيًا بايت ببايت."}


def page_index(lang: str, paquets: List[Tuple[Dict[str, Any], Dict[str, Any]]]) -> str:
    t = MOTEUR.T[lang]
    e = MOTEUR.ech
    lang_code = t["lang"]
    lignes = []
    for spec, donnees in paquets:
        r, slug = donnees["resume"], spec["slug"]
        ch = spec["chemins"]
        pages = " · ".join(f'<a href="{e(ch[l])}" lang="{l}">{l.upper()}</a>'
                           for l in MOTEUR.LANGUES)
        suffixe = "" if lang_code == "fr" else f"_{lang_code}"
        data = (f'<a href="../donnees/{e(slug)}.json">JSON</a> · '
                f'<a href="../donnees/{e(slug)}.csv">CSV</a> · '
                f'<a href="../figures/{e(slug)}{e(suffixe)}.svg">SVG</a> · '
                f'<a href="../dossiers/{e(slug)}.md">MD</a>')
        lignes.append([e(LIBELLES_DOSSIER[slug][lang_code]),
                       f"<span class=\"nb\">{r['equations']}</span>",
                       f"<span class=\"nb\">{r['controles_ok']}/{r['controles_total']}</span>",
                       f"<span class=\"nb\">{r['statuts'].get('OPÉRATIONNEL', 0)}</span>",
                       f"<span class=\"nb\">{r['statuts'].get('SIMULÉ', 0)}</span>",
                       f"<span class=\"nb\">{r['statuts'].get('SPÉCIFIÉ', 0)}</span>",
                       pages, data])
    entetes = [(INDEX_ENTETES[lang_code][i], "nb" if i in (1, 2, 3, 4, 5) else "")
               for i in range(8)]
    table = MOTEUR.tableau(
        "dossiers",
        ("Neuf pages, trois figures SVG autonomes, trois JSON, trois CSV Excel et trois "
         "dossiers markdown produits par le même générateur."
         if lang_code == "fr" else
         "Nine pages, three standalone SVG figures, three JSON, three Excel CSV and three "
         "Markdown dossiers, all produced by the same generator."
         if lang_code == "en" else
         "تسع صفحات وثلاثة أشكال SVG مستقلة وثلاثة ملفات JSON وثلاثة CSV لإكسل وثلاثة "
         "ملفات Markdown، كل ذلك يولده المولّد نفسه."),
        entetes, lignes)
    total_eq = sum(d["resume"]["equations"] for _, d in paquets)
    total_ctrl = sum(d["resume"]["controles_total"] for _, d in paquets)
    ok_ctrl = sum(d["resume"]["controles_ok"] for _, d in paquets)
    corps = [f"<h1>{e(TITRE_INDEX[lang_code])}</h1>", f"<p>{e(DESC_INDEX[lang_code])}</p>",
             MOTEUR.badges([(f"{total_eq} EQ", False),
                            (f"{ok_ctrl}/{total_ctrl} {t['controles']}", True)])]
    if lang_code != "fr":
        corps.append(f"<p class=\"chemin\">{e(INDEX_REPRO[lang_code])}</p>")
    else:
        corps.append(f"<p class=\"chemin\">{e(INDEX_REPRO['fr'])}</p>")
    corps.append(table)
    boutons = "".join(
        f'<a class="{"principal" if i < 3 else ""}" href="{e(paquets[i][0]["chemins"][lang_code] if i < 3 else DOI_CONCEPT)}">'
        f'{e(INDEX_BOUTONS[lang_code][i])}</a>' for i in range(4))
    corps.append(f'<div class="actions">{boutons}</div>')
    corps.append(f"<h2 id=\"reproduction\">{e(t['reproduction'])}</h2>"
                 f"<pre>{e(COMMANDES[lang_code])}</pre>")
    nav = [("fr", "Français", f"index.html"), ("en", "English", "index_en.html"),
           ("ar", "العربية", "index_ar.html")]
    queue = (f"<footer class=\"site\"><div class=\"interieur\"><p>{e(t['pied'])}</p>"
             f"<p>{e(MOTEUR.AUTEUR)} · {e(MOTEUR.LICENCE)} · {e(DOI_CONCEPT)}</p>"
             f"</div></footer>")
    return (MOTEUR.tete(t, f"{TITRE_INDEX[lang_code]} — AL-MIZAN × ASTRO-Q°ODE",
                        DESC_INDEX[lang_code],
                        {"fr": "index.html", "en": "index_en.html", "ar": "index_ar.html"},
                        f"index{'' if lang_code == 'fr' else '_' + lang_code}.html")
            + "\n<body>" + MOTEUR.en_tete(t, lang_code, nav,
                                          {"fr": "ABONDANCE — AL-MIZAN × ASTRO-Q°ODE",
                                           "en": "ABUNDANCE — AL-MIZAN × ASTRO-Q°ODE",
                                           "ar": "الوفرة — الميزان × ASTRO-Q°ODE"}[lang_code])
            + "\n<main id=\"contenu\" tabindex=\"-1\">" + "".join(corps) + "</main>"
            + queue + "\n</body>\n</html>\n")


# ----------------------------------------------------------------------------
# colonne « formule » sur les pages anglaise et arabe
# ----------------------------------------------------------------------------
# Le module écrit « partie symbolique ; qualification ». La partie symbolique,
# ses identifiants et ses symboles d'unités sont recopiés tels quels (ce sont
# des noms du code) ; la qualification, elle, est traduite ci-dessous. Toute
# qualification nouvelle non listée fait échouer la construction plutôt que
# d'imprimer du français sur une page arabe.
FORMULE_SYMBOLIQUE = frozenset({
    "1 kW·h = 3,6 MJ",
    "C = ε₀S/d ;  W = ½CU² = ½QU = ½ε₀E²·(Sd)",
    "F = P·S",
    "F/ℓ = μ₀I₁I₂/(2πd)",
    "P = UI·cos φ ;  S² = P² + Q²",
    "P = e·Q",
    "P_océan + R = ET_océan",
    "V_douce = Σ V_compartiments",
    "W = ½LI² ;  u_B = B²/(2μ₀) ;  u_E = ½ε₀E²",
    "WPE = φ·E_photon/Pélec",
    "WUE ∝ ca·(1 − ci/ca)",
    "Z₀ = √(μ₀/ε₀) = μ₀c ;  E/B = c",
    "a* = 1/3 ;  C_P,max = 16/27",
    "d ln e/dT = L/(R_v·T²)",
    "k = 1/(4πε₀) = μ₀c²/4π ;  1 C = 1/e",
    "v = Q/A",
    "v = √(2gh)",
    "Φ = B·S·cos(ωt) ;  ℰ_rms = N·B·S·ω/√2",
    "σ = 1/ρ ;  v_dérive = I/(n·e·S)",
    "φ = ∫M_λλ/(hc)dλ",
})

# Tête de formule (partie avant le premier « ; », formule entière quand il n'y en
# a pas) : mêmes règles, mêmes tables. Une clé qui ne rencontre aucune formule
# fait échouer la construction, donc pas de traduction orpheline ni de clé périmée.
FORMULE_TETE: Dict[str, Tuple[str, str]] = {
    "ΣI(nœud) = 0": ("ΣI(node) = 0", "ΣI(العقدة) = 0"),
    "P_pertes = (P/U)²·R  ⇒  pertes ∝ 1/U²": (
        "P_pertes = (P/U)²·R  ⇒  losses ∝ 1/U²",
        "P_pertes = (P/U)²·R  ⇒  الفقد ∝ 1/U²"),
    "e = U·capacité (Wh/kg)": ("e = U·capacity (Wh/kg)", "e = U × السعة (Wh/kg)"),
    "2Δ(0)/(k_B·T_c) ≈ 3,53 (déclaré)": (
        "2Δ(0)/(k_B·T_c) ≈ 3.53 (declared)",
        "2Δ(0)/(k_B·T_c) ≈ 3.53 (مُعلَن)"),
    "P1 ↔ contrôle · P2 ↔ 50 Hz · P3 ↔ redondance N-1 · P4 ↔ comptage": (
        "P1 ↔ control · P2 ↔ 50 Hz · P3 ↔ N-1 redundancy · P4 ↔ metering",
        "P1 ↔ التحكّم · P2 ↔ 50 Hz · P3 ↔ تكرار N-1 · P4 ↔ العدّ"),
    "Q = A·v constant": ("Q = A·v constant", "Q = A·v ثابتة"),
    "e = ρ·g·H/η (par m³)": ("e = ρ·g·H/η (per m³)", "e = ρ·g·H/η (لكل م³)"),
    "w_min = R·T·ln(1/x_eau) par mole d'eau douce extraite": (
        "w_min = R·T·ln(1/x_eau) per mole of fresh water extracted",
        "w_min = R·T·ln(1/x_eau) لكل مول من الماء العذب المُستخرَج"),
    "P1 ↔ borne · P2 ↔ cycles · P3 ↔ redondance · P4 ↔ dette hydrologique": (
        "P1 ↔ boundary · P2 ↔ cycles · P3 ↔ redundancy · P4 ↔ hydrological debt",
        "P1 ↔ الحدّ · P2 ↔ الدورات · P3 ↔ التكرار · P4 ↔ الدَّين الهيدرولوجي"),
    "E = N_A·hc/λ par einstein": ("E = N_A·hc/λ per einstein",
                                  "E = N_A·hc/λ لكل أينشتاين"),
    "M_λ(T) intégrée sur 400–700 nm": ("M_λ(T) integrated over 400–700 nm",
                                       "M_λ(T) مُكامَلة على 400–700 nm"),
    "Rubisco : v_C/v_O = 85 · C4 = pompe à CO2 devant Rubisco": (
        "Rubisco : v_C/v_O = 85 · C4 = CO2 pump ahead of Rubisco",
        "Rubisco : v_C/v_O = 85 · وC4 مضخّة CO2 أمام Rubisco"),
    "NH3 = 82,25 % d'azote": ("NH3 = 82.25 % nitrogen", "NH3 = 82.25 % من النيتروجين"),
    "e = kWh/m³ du dossier EAU (ρgH/η à 50 m) × volume prélevé": (
        "e = kWh/m³ from the WATER dossier (ρgH/η at 50 m) × volume withdrawn",
        "e = kWh/m³ من ملف الماء (ρgH/η عند 50 m) × الحجم المسحوب"),
    "L/kg dérivé (EQ-09) contre L/kg déclaré (dossier EAU EQ-12)": (
        "L/kg derived (EQ-09) versus L/kg declared (WATER dossier EQ-12)",
        "L/kg مشتق (EQ-09) مقابل L/kg معلَن (ملف الماء EQ-12)"),
    "personnes/ha = (t/ha)·(kcal/t) / (2100 kcal/j × 365)": (
        "persons/ha = (t/ha)·(kcal/t) / (2100 kcal/j × 365)",
        "الأفراد/هكتار = (t/ha)·(kcal/t) / (2100 kcal/j × 365)"),
    "quantité/ha = f(EQ-08, EQ-09, EQ-10, EQ-16) avec facteurs stoechiométriques exacts": (
        "quantity/ha = f(EQ-08, EQ-09, EQ-10, EQ-16) with exact stoichiometric factors",
        "الكمية/هكتار = f(EQ-08, EQ-09, EQ-10, EQ-16) بمعاملات متوازنة دقيقة"),
    "P1 ↔ plafond · P2 ↔ photopériode et siècles de sol · P3 ↔ planche la plus basse "
    "· P4 ↔ dettes": (
        "P1 ↔ ceiling · P2 ↔ photoperiod and soil centuries · P3 ↔ lowest plank "
        "· P4 ↔ debts",
        "P1 ↔ السقف · P2 ↔ الفترة الضوئية وقرون التربة · P3 ↔ أخفض لوحة · P4 ↔ الدُّيُون"),
}

FORMULE_GLOSE: Dict[str, Tuple[str, str]] = {
    "1 mm sur 1 ha = 10 m³": ("1 mm spread over 1 ha = 10 m³",
                              "1 مم على مساحة 1 هكتار تساوي 10 م³"),
    "31 GJ/t NH3 ⇒ 37,7 MJ par kg N": ("31 GJ/t NH3 ⇒ 37.7 MJ per kg of N",
                                       "31 GJ/t من NH3 ⇒ 37.7 MJ لكل kg من النيتروجين"),
    "4 photons/CO2 au minimum, 8,5 mesurés": ("at least 4 photons per CO2, 8.5 measured",
                                              "4 فوتونات لكل CO2 على الأقل، و8.5 هو المُقاس"),
    "I₂/I₁ = N₁/N₂ ;  S = UI conservée": ("I₂/I₁ = N₁/N₂ ;  S = UI is conserved",
                                          "I₂/I₁ = N₁/N₂ ;  والقدرة الظاهرية S = UI محفوظة"),
    "P interceptée = Φ·πR⊕² ;  S = P/(η·Φ)": ("P intercepted = Φ·πR⊕² ;  S = P/(η·Φ)",
                                              "P المعترَضة = Φ·πR⊕² ;  S = P/(η·Φ)"),
    "R = 0 ⇒ pertes ohmiques nulles": ("R = 0 ⇒ ohmic losses vanish",
                                       "R = 0 ⇒ تنعدم الفقد الأومية"),
    "Wh = J/3600 ;  gravitaire = g·h": ("Wh = J/3600 ;  and gravity = g·h",
                                        "Wh = J/3600 ;  والجاذبية = g·h"),
    "bilan salin fermé": ("closed salt balance", "ميزان ملحي مغلق"),
    "c en osmoles par m³": ("c in osmoles per m³", "c بوحدة الأسمول لكل م³"),
    "demande = N·(kcal/j)·365·4184": ("demand = N·(kcal/j)·365·4184",
                                      "الطلب = N·(kcal/j)·365·4184"),
    "dette = débit d'érosion − taux de formation": (
        "debt = erosion rate − soil formation rate",
        "الدَّين = معدل التعرية − معدل تكوّن التربة"),
    "doubler un facteur non limitant ne change rien": (
        "doubling a non-limiting factor changes nothing",
        "مضاعفة عامل غير حاسم لا تغيّر شيئًا"),
    "e = ρ·g·H (par m³)": ("e = ρ·g·H (per m³)", "e = ρ·g·H (لكل م³)"),
    "même membre que le dossier électricité": ("same term as in the electricity dossier",
                                               "الحدّ نفسه الوارد في ملف الكهرباء"),
    "mᵢ en kg par personne et par an": ("mᵢ in kg per person per year",
                                        "mᵢ بالكيلوغرام لكل شخص في السنة"),
    "part immergée = ρ_objet/ρ_fluide": ("submerged fraction = ρ_objet/ρ_fluide",
                                         "الجزء الغاطس = ρ_objet/ρ_fluide"),
    "perte = (E_photon − E_g)/E_photon": ("loss = (E_photon − E_g)/E_photon",
                                          "الفقد = (E_photon − E_g)/E_photon"),
    "rejet = T_froid/T_source": ("reject = T_froid/T_source", "المرفوض = T_froid/T_source"),
    "élevage = surface × indice de conversion": (
        "livestock = area × feed conversion ratio",
        "الإنتاج الحيواني = المساحة × معامل التحويل الغذائي"),
    "équilibre atome par atome": ("balance atom by atom", "توازن ذرّة بذرّة"),
    "Σ phasores = 0 ;  P = √3·U_L·I_L·cos φ": ("Σ phasors = 0 ;  P = √3·U_L·I_L·cos φ",
                                               "Σ المتجهات الدورانية = 0 ;  P = √3·U_L·I_L·cos φ"),
    "ΣU(maille) = 0 ;  résolution en rationnels": ("ΣU(loop) = 0 ;  solved in rationals",
                                                   "ΣU(الحلقة) = 0 ;  والحل بالأعداد النسبية"),
    "ε ≤ plafond EQ-02": ("ε ≤ ceiling of EQ-02", "ε ≤ سقف EQ-02"),
}


def _formules(donnees: Dict[str, Any], lang: str,
              vues_t: set, vues_q: set) -> Dict[str, Any]:
    """Copie des équations dont la colonne formule reste lisible dans `lang`."""
    if lang == "fr":
        return donnees
    index = 0 if lang == "en" else 1
    eqs: List[Dict[str, Any]] = []
    for e in donnees["equations"]:
        tete, sep, qual = e["formule"].partition(" ; ")
        cle_q = qual.strip()
        cle_t = tete if sep else e["formule"]
        if cle_t in FORMULE_TETE:
            vues_t.add(cle_t)
            tete_r = FORMULE_TETE[cle_t][index]
        else:
            tete_r = tete if sep else e["formule"]
        if not sep:
            eqs.append(e if cle_t not in FORMULE_TETE else _avec_formule(e, tete_r))
            continue
        if cle_q in FORMULE_SYMBOLIQUE:
            eqs.append(_avec_formule(e, f"{tete_r} ; {cle_q}"))
            continue
        if cle_q not in FORMULE_GLOSE:
            raise KeyError(f"qualifiant de formule sans traduction pour {lang} : {qual!r}")
        vues_q.add(cle_q)
        eqs.append(_avec_formule(e, f"{tete_r} ; {FORMULE_GLOSE[cle_q][index]}"))
    autre = dict(donnees)
    autre["equations"] = eqs
    return autre


def _avec_formule(eq: Dict[str, Any], formule: str) -> Dict[str, Any]:
    if eq["formule"] == formule:
        return eq
    copie = dict(eq)
    copie["formule"] = formule
    return copie


# ----------------------------------------------------------------------------
# écriture
# ----------------------------------------------------------------------------
def _titrer(donnees: Dict[str, Any], textes: Dict[str, Dict[str, List[str]]]) -> Dict[str, Any]:
    """Étiquette les équations pour le CSV et le Markdown : titre français seulement."""
    for eq in donnees["equations"]:
        eq["_titre_fr"] = textes[eq["id"]]["fr"][0]
    return donnees


MODULES = {"electricite": ELEC, "eau": EAU, "agriculture": AGRI}
TEXTES = {"electricite": ELEC_TEXT, "eau": EAU_TEXT, "agriculture": AGRI_TEXT}
SPECIFICATIONS = {"electricite": spec_elec, "eau": spec_eau, "agriculture": spec_agri}


MOT_MIXTE = re.compile(r'[\u0621-\u064a\u064f-\u0652]{4,}[A-Za-z]{4,}')


def _verifier_mixte(ecrits: List[Path]) -> None:
    """Un mot arabe translittéré de moitié en latin ne passe pas la publication."""
    fautifs = [f"{p.name} : {m.group(0)}" for p in ecrits if "_ar." in p.name
               for m in MOT_MIXTE.finditer(p.read_text(encoding="utf-8"))]
    if fautifs:
        raise SystemExit("mots arabes mêlés de latin : " + " | ".join(fautifs[:8]))


def main() -> int:
    donnees: Dict[str, Any] = {}
    vues_t: set = set()
    vues_q: set = set()
    for slug, module in MODULES.items():
        d = _titrer(module.resoudre(), TEXTES[slug])
        if not module.verifier(d):
            raise SystemExit(f"contrôles non reçus dans {slug} : la page n'est pas publiée")
        donnees[slug] = d
    ecrits: List[Path] = []
    paquets = []
    for slug in ("electricite", "eau", "agriculture"):
        spec, d = SPECIFICATIONS[slug](donnees[slug]), donnees[slug]
        paquets.append((spec, d))
        for lang in MOTEUR.LANGUES:
            cible = ARTEFACTS / "pages" / spec["chemins"][lang]
            MOTEUR.ecrire_chemin(cible, MOTEUR.construire_page(
                spec, _formules(d, lang, vues_t, vues_q), lang))
            ecrits.append(cible)
        for lang in MOTEUR.LANGUES:
            figure = ARTEFACTS / "figures" / f"{slug}{'' if lang == 'fr' else '_' + lang}.svg"
            MOTEUR.ecrire_svg(spec["figures"][0]["svg"][lang], figure)
            ecrits.append(figure)
        for dossier, nom, contenu in (
            ("donnees", f"{slug}.json", None),
            ("donnees", f"{slug}.csv", MOTEUR.lignes_csv_equations(d)),
            ("dossiers", f"{slug}.md", MOTEUR.markdown(d, spec)),
        ):
            cible = ARTEFACTS / dossier / nom
            if contenu is None:
                MOTEUR.ecrire_json(d, cible)
            elif isinstance(contenu, str):
                MOTEUR.ecrire_chemin(cible, contenu)
            else:
                MOTEUR.ecrire_csv(contenu, cible)
            ecrits.append(cible)
    mortes = ((set(FORMULE_TETE) - vues_t) | (set(FORMULE_GLOSE) - vues_q)
              | (set(EQUATION_SOURCE) - EQ_VUES))
    if mortes:
        raise SystemExit("clés de formule sans formule correspondante : "
                         + " | ".join(sorted(mortes)))
    for lang in MOTEUR.LANGUES:
        cible = ARTEFACTS / "pages" / ("index.html" if lang == "fr" else f"index_{lang}.html")
        MOTEUR.ecrire_chemin(cible, page_index(lang, paquets))
        ecrits.append(cible)
    _verifier_mixte(ecrits)
    MOTEUR.ecrire_json({"version": "1.0",
                        "equations": sum(d["resume"]["equations"] for d in donnees.values()),
                        "controles_ok": sum(d["resume"]["controles_ok"] for d in donnees.values()),
                        "controles_total": sum(d["resume"]["controles_total"] for d in donnees.values()),
                        "artefacts": sorted(str(p.relative_to(RACINE)).replace("\\", "/")
                                            for p in ecrits)},
                       ARTEFACTS / "donnees" / "etat.json")
    print(json.dumps({"equations": sum(d["resume"]["equations"] for d in donnees.values()),
                      "controles": f"{sum(d['resume']['controles_ok'] for d in donnees.values())}"
                                   f"/{sum(d['resume']['controles_total'] for d in donnees.values())}",
                      "artefacts": len(ecrits) + 1,
                      "racine": str(ARTEFACTS.relative_to(RACINE.parent))},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())

