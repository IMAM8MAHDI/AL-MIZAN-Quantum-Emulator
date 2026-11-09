# KIT DE DIFFUSION — AL-MIZAN : 3 profils, 3 messages

**Point d'ancrage commun** : DOI 10.5281/zenodo.24028242 (DOI de concept :
il résout toujours vers la dernière version déposée, jamais vers une archive
périmée) +
`github.com/IMAM8MAHDI/AL-MIZAN-Quantum-Emulator` +
`RESUME_ACADEMIQUE.md` + `WHITE_PAPER_ALMIZAN.md`

---

## PROFIL 1 — Chercheurs chronobiologie / biophysique

**Cibles** : laboratoires chronobiologie, sommeil, chronothérapie
(cancer), VFC — type INSERM, instituts du sommeil, équipes PhysioNet.

**Message à adapter** :

> Objet : Filtrage exact de signaux circadiens — collaboration sur données réelles
>
> Bonjour,
>
> J'ai développé un moteur d'analyse de rythmes en arithmétique exacte
> (autocorrélation + convergents de fractions continues) qui traduit
> chaque signal périodique en "fraction de synchronie" puis en score de
> stabilité harmonique (SAM, 0-100). Sur signaux synthétiques, il détecte
> les désynchronisations circadiennes avec confiance forte.
>
> Je cherche à confronter le modèle à de vraies séries (actimétrie,
> mélatonine, VFC). L'ensemble est ouvert (AGPL), scellé SHA-256,
> documenté : DOI 10.5281/zenodo.24028242. Seriez-vous intéressé·e par
> un test sur vos cohortes ou un échange technique ?
>
> Cordialement,

---

## PROFIL 2 — Développeurs santé numérique / MedTech

**Cibles** : ingénieurs traitement du signal ECG/EEG, startups MedTech,
équipes wearables, développeurs d'aide au diagnostic.

**Message à adapter** :

> Objet : Interface clinique 3 champs sur algèbre certifiée — open source
>
> Bonjour,
>
> Notre module `medecin_simple.py` montre comment masquer une algèbre
> complète (intervalles, fractions continues, formes quadratiques)
> derrière une interface épurée : {score, couleur, action}. Zéro
> dépendance, pur Python, embarquable edge. Chaque artefact publié porte
> une empreinte SHA-256 : cela donne l'**intégrité et la
> reproductibilité** d'une version précise — ce n'est **pas** une
> conformité réglementaire (marquage CE, MDR, IEC 62304 : rien de tout
> cela n'est engagé ici).
>
> Le code est AGPL sur GitHub (AL-MIZAN-Quantum-Emulator), avec un white
> paper technique complet (interop HL7 FHIR, PhysioNet/WFDB, extensions
> matérielles). Heureux d'échanger si une de ces briques vous sert.

---

## PROFIL 3 — Mathématiciens expérimentaux

**Cibles** : théorie des nombres computationnelle, formes quadratiques,
arithmétique expérimentale — MathOverflow, revues exp. math., séminaires.

**Message à adapter** (cf. QUESTION_MATHSE.md déjà prête) :

> Objet : Signature carrée et normes quadratiques dans un système fini —
> structure connue ?
>
> Bonjour,
>
> En analysant un système paramétrique fini, j'ai vérifié par calcul
> exact (rationnel) : (i) une signature « partie puissante » sur les
> constantes dérivées (dx = 27·487², dy = 27·59², dt = 3⁷·7·1129559),
> (ii) deux relations entières tombant exactement sur les graines
> calendaires : 8766² = 12·dx et 8496² = 768·dy (8766 = 18·487 heures),
> (iii) le facteur premier 1129559 représenté **de façon unique** par
> x² + 7y², soit 884² + 7·223², avec 1129559 ≡ 4 (mod 7).
>
> Rejeu : `python code/conjecture_point_carre.py` imprime les six
> contrôles et leur sceau. Certificats : DOI 10.5281/zenodo.24028242.
> (i) et (ii) ont-ils un nom dans la littérature ? (iii) semble classique
> — la référence exacte m'intéresse.

**Variante — dossier CHIFFRES** (mêmes cibles, autre question) :

> Objet : 108 cellules pré-déclarées sur π, e et √2 — structure connue ?
>
> Bonjour,
>
> `CHIFFRES/chiffres_pi.py` produit π, e et √2 par **deux voies
> indépendantes** (Chudnovsky 1989 contre Machin 1706 pour π ; Σ 1/k! pour
> e ; encadrement entier pour √2), annonce 108 cellules de test avant de
> lire les chiffres, puis les confronte sur n = 10⁶ : une exclusion contre
> 0,108 attendues, p globale 0,2047 — verdict CONTENU. Rien ici ne prétend
> prouver la normalité de π : le domaine est fini et déclaré, et le dernier
> chapitre de la vidéo d'amorce (« A pattern nobody has proven ») est pris
> au mot.
>
> Rejeu : `cd CHIFFRES && py -3 chiffres_pi.py` (domaine court, 17/17
> contrôles). L'audit des quatre piliers pour tout le dépôt :
> `py -3 FONDATION/OUTILS/audit_piliers.py --tous --rigide`.
> Ces fréquences par longueur ont-elles un nom dans la littérature
> (runs, mots distincts, auto-localisation du numéro à sa propre place) ?

---

## Règles d'envoi

1. **Jamais de spam** — un message personnalisé par destinataire.
2. **Toujours la clause honnête** — « modèle expérimental, cherche
   validation sur données réelles ».
3. **DOI d'abord** — c'est la carte d'identité ; le code suit.
4. **Une semaine par vague** — 5 messages ciblés plutôt que 50 généraux.
