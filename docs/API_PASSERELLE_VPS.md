# Référence API — passerelle VPS Al-Mizan

Version : 0.1 — 27/10/2026
Source : [`passerelle_api_vps_mizan.py`](../passerelle_api_vps_mizan.py)

---

## 1. Conventions

| Élément | Valeur |
| :--- | :--- |
| URL locale | `http://127.0.0.1:8095` |
| URL publique | `https://www.al-mizan.world` (TLS terminé par nginx) |
| Encodage | UTF-8 |
| Corps JSON | `Content-Type: application/json` |
| Réponse JSON | `Content-Type: application/json; charset=utf-8`, `ensure_ascii=False`, indentation 2 |
| CORS | `Access-Control-Allow-Origin: *`, méthodes `GET, POST, OPTIONS` |
| Préflight | `OPTIONS` répond `{"status": "CORS_PREFLIGHT_OK"}` |
| Authentification API | `Authorization: Bearer <jeton>` — `?token=` également accepté |
| Authentification comptes | Cookie `mizan_session` (HttpOnly, `SameSite=Strict`, `Secure` derrière HTTPS, 7 jours) |
| Anti-CSRF | `Origin` autorisé **et** en-tête `X-Mizan-CSRF: 1` sur toute écriture de compte |
| Erreur type | `{"succes": false, "erreur": "<message>"}` |
| Erreur comptes | `{"succes": false, "code": "<CODE>", "erreur": "<message>"}` |

Seule la route `POST /api/v1/commande` vérifie un jeton : `MIZAN_VPS_API_KEY`, lue **exclusivement** dans l'environnement. Si la variable est absente ou vide, la route répond 401 (fermeture par défaut) et le serveur journalise un avertissement au démarrage. Aucune valeur par défaut n'est codée en dur.

Le démonstrateur multimodal (section 4.5) délivre un jeton de démonstration qui **n'authentifie aucune route**.

Les routes `/api/v1/comptes/*` et `/api/v1/admin/*` forment un espace distinct : elles s'authentifient par le cookie de session, répondent avec `Cache-Control: no-store, private` et **sans** `Access-Control-Allow-Origin: *`. Une écriture de compte sans `Origin` autorisé ou sans `X-Mizan-CSRF: 1` est refusée en 403.

> Ne pas placer de jeton dans une URL en production : il finit dans les journaux et l'historique.

---

## 2. Pages et fichiers servis (GET)

| Route | Alias | Fichier |
| :--- | :--- | :--- |
| `/` | `/index.html`, `/public`, `/accueil` | `web_cloud/portail_public_al_mizan.html` |
| `/tableau` | `/tableau-maitre`, `/tableau-sequentiel`, `/tableau-maitre-sequentiel` | `web_cloud/tableau_maitre_sequentiel.html` |
| `/livre-blanc` | `/whitepaper`, `/mzn`, `/livre_blanc` | `web_cloud/livre_blanc_almizan.html` |
| `/ponts` | `/hub-ponts`, `/ponts-synchrones`, `/hub` | `web_cloud/hub_ponts_synchrones.html` |
| `/video` | `/video-promotion`, `/al_mizan_promotion_youtube_1080p.mp4` | `web_cloud/al_mizan_promotion_youtube_1080p.mp4` |
| `/poupees` | `/cartographie`, `/poupees-russes` | `web_cloud/cartographie_poupees_1_a_27.html` |
| `/console` | `/monitoring`, `/soc`, `/cyber` | `web_cloud/monitoring_cybersecurite.html` |
| `/qubit-logique` | `/qubit_logique`, `/qubit` | `web_cloud/qubit_logique.html` |
| `/riemann` | `/hypothese-riemann`, `/oeuvre-universelle/riemann` | `web_cloud/hypothese_riemann.html` — hypothèse **non démontrée** (fr) |
| `/riemann/en` | `/hypothese-riemann/en`, `/oeuvre-universelle/riemann/en` | `web_cloud/hypothese_riemann_en.html` — *unproven* (en) |
| `/riemann/ar` | `/hypothese-riemann/ar`, `/oeuvre-universelle/riemann/ar` | `web_cloud/hypothese_riemann_ar.html` — **غير مُبرهنة** (ar, RTL) |
| `/hypothese-riemann.pdf` | `/riemann.pdf`, `/oeuvre-universelle/riemann.pdf` | `web_cloud/hypothese_riemann.pdf` — `application/pdf`, lecture seule |
| `/hypothese_riemann.png` | `/riemann.png` | `web_cloud/hypothese_riemann.png` — `image/png`, cache 7 jours |
| `/resume-lots` | `/resume_lots` | `web_cloud/resume_lots.html` — résumé des huit lots, statuts honnêtes (fr) |
| `/resume-lots/en` | — | `web_cloud/resume_lots_en.html` — public summary (en) |
| `/resume-lots/ar` | — | `web_cloud/resume_lots_ar.html` — ملخص عام (ar, RTL) |
| `/resume-lots.pdf` | `/resume_lots.pdf` | `web_cloud/resume_lots.pdf` — `application/pdf`, lecture seule |
| `/resume_lots.png` | `/resume-lots.png` | `web_cloud/resume_lots.png` — `image/png`, cache 7 jours |
| `/fondation` | `/base-universelle` | `web_cloud/fondation.html` — base posée **HORS MATRICE**, 18 EQ / 18 contrôles reçus (fr) |
| `/fondation/en` | — | `web_cloud/fondation_en.html` — mêmes revendications, traduites (en) |
| `/fondation/ar` | — | `web_cloud/fondation_ar.html` — نفس المزاعم مترجمة (ar, RTL) |
| `/fondation.json` | `/fondation/resultats.json` | `web_cloud/fondation_resultats.json` — copie verbatim (vue LF) de `FONDATION/artefacts/donnees/fondation.json`, scellée par `MANIFESTE_SHA256.txt` |
| `/chiffres-pi` | `/chiffres_pi` | `web_cloud/chiffres_pi.html` — 17 EQ / 17 contrôles sur [0 ; 10⁶[, verdict **CONTENU** ; un domaine borné, **pas** une preuve de normalité (fr) |
| `/chiffres-pi/en` | — | `web_cloud/chiffres_pi_en.html` — same bounded claim (en) |
| `/chiffres-pi/ar` | — | `web_cloud/chiffres_pi_ar.html` — الحدود ذاتها (ar, RTL) |
| `/chiffres-pi.json` | `/chiffres-pi/resultats.json` | `web_cloud/chiffres_pi_resultats.json` — copie verbatim (vue LF) de `CHIFFRES/artefacts/donnees/chiffres.json` |
| `/laboratoire` | `/horlogerie` | `web_cloud/laboratoire.html` — dossier HORLOGERIE du dépôt scellé rejoué pas à pas (15 EQ / 20 contrôles) et, en pièce jointe, le dossier QPU_DISTANT (10 EQ / 10 contrôles) : **25 EQ / 30 contrôles**, verdict `LABORATOIRE CONFORME` ; **aucune synchronisation physique** observée (fr) |
| `/laboratoire/en` | — | `web_cloud/laboratoire_en.html` — same bounded claim, *no physical synchronisation* (en) |
| `/laboratoire/ar` | — | `web_cloud/laboratoire_ar.html` — الحدود ذاتها، لا مزامنة فيزيائية (ar, RTL) |
| `/laboratoire.json` | `/laboratoire/resultats.json` | `web_cloud/laboratoire_resultats.json` — copie verbatim (vue LF) de `HORLOGERIE/artefacts/laboratoire.json` (5 contrôles, `verdict`, `portee_repere`) |
| `/laboratoire-certificats.json` | `/laboratoire/certificats.json` | `web_cloud/laboratoire_certificats.json` — copie de `HORLOGERIE/artefacts/certificats.json`, relue sans import du dépôt |
| `/laboratoire-trajectoire.svg` | — | `web_cloud/laboratoire_trajectoire.svg` — `image/svg+xml`, recopié tel quel depuis `HORLOGERIE/artefacts/trajectoire_laboratoire.svg` |
| `/laboratoire-trajectoire.csv` | — | `web_cloud/laboratoire_trajectoire.csv` — `text/csv`, CRLF et virgule décimale (format Excel français du dépôt), aucune conversion |
| `/laboratoire-stabilite.csv` | — | `web_cloud/laboratoire_stabilite.csv` — idem : stabilité simulée et stabilité propre à l'hôte |
| `/laboratoire-confrontation.csv` | — | `web_cloud/laboratoire_confrontation.csv` — idem : confrontation calcul ↔ mesure de l'hôte |
| `/laboratoire-qpu-certificat.json` | `/laboratoire/qpu-certificat.json` | `web_cloud/laboratoire_qpu_certificat.json` — certificat de l'exécution distante relue (`job dbpkmr0ou4as73ctrm80` sur `ibm_marrakesh`, 256 tirs, 600 unités, `status: Completed`) : compteurs, parité, empreintes, `racine_merkle_sha256` et `portee_et_limites`. **Aucun qubit n'est lancé ici** : le module relit et re-borne une archive déjà émise (fr/en/ar sur la page) |
| `/laboratoire-qpu-compteurs.csv` | — | `web_cloud/laboratoire_qpu_compteurs.csv` — `text/csv`, CRLF et virgule décimale : 00 → 126, 01 → 22, 11 → 108, Σ 256 (donc 10 → 0), avec le poids de paire de chaque mot |
| `/laboratoire-qpu-frontieres.csv` | — | `web_cloud/laboratoire_qpu_frontieres.csv` — les deux bornes dérivées confrontées à la parité mesurée 0,9140625 : `mediane_machine` 0,9258965 **non reçue** (−0,676 σ) et `support_reel` 0,9114310 **reçue** (+0,150 σ) |
| `/laboratoire-qpu-frontieres.svg` | — | `web_cloud/laboratoire_qpu_frontieres.svg` — `image/svg+xml`, même confrontation rendue en figure (la parité mesurée, les deux frontières, la zone de rejet) |
| `/espace-disque` | `/espace_disque` | `web_cloud/espace_disque.html` — 13 EQ / 13 contrôles sur l'espace disque mesuré du poste de développement (fr) |
| `/espace-disque/en` | — | `web_cloud/espace_disque_en.html` — same 13 equations, same limits (en) |
| `/espace-disque/ar` | — | `web_cloud/espace_disque_ar.html` — المعادلات الثلاث عشرة والحدود ذاتها (ar, RTL) |
| `/espace-disque.json` | `/espace-disque/resultats.json` | `web_cloud/espace_disque_resultats.json` — instantané mesuré (9 opérationnels, 3 simulés, 1 spécifié), lecture seule |
| `/offres` | `/tarifs` | `web_cloud/offres.html` |
| `/services` | — | `web_cloud/services.html` |
| `/statut` | `/etat-du-service` | `web_cloud/statut.html` |
| `/securite` | — | `web_cloud/securite.html` |
| `/accessibilite` | — | `web_cloud/accessibilite.html` |
| `/contact` | — | `web_cloud/contact.html` |
| `/developpeurs` | `/api-docs` | `web_cloud/developpeurs.html` |
| `/mentions-legales` | `/legal`, `/mentions` | `web_cloud/mentions_legales.html` |
| `/robots.txt` | — | `web_cloud/robots.txt` |
| `/sitemap.xml` | — | `web_cloud/sitemap.xml` |
| `/favicon.ico` | — | `web_cloud/favicon.ico` — `204` sans corps si le fichier est absent |
| `/inscription` | — | `web_cloud/compte_inscription.html` |
| `/connexion` | — | `web_cloud/compte_connexion.html` |
| `/compte` | `/compte/` | `web_cloud/compte_espace.html` |
| `/verification` | — | `web_cloud/compte_verification.html` |
| `/cgu` | — | `web_cloud/cgu.html` |
| `/confidentialite` | — | `web_cloud/confidentialite.html` |
| `/unifie` | `/panneau` | Page HTML générée en mémoire (tableau de bord des 4 démarches) |
| `/solutions-acteurs` | `/solutions-acteurs/`, `/solutions_posees_acteurs` | `web_cloud/solutions_posees_acteurs.html` — registre EQ-SA issu d'une vidéo de 109 min sans transcript : 13 équations, 13 contrôles, 12 paramètres déclarés, 13 chapitres horodatés ; **hypothèses de modèle, aucune mesure, aucune citation, aucune personne désignée** (fr) |
| `/solutions-acteurs/en` | — | `web_cloud/solutions_posees_acteurs_en.html` — same register, same equations, same numbers, declared assumptions only (en) |
| `/solutions-acteurs/ar` | — | `web_cloud/solutions_posees_acteurs_ar.html` — السجل نفسه والصيغ نفسها والأرقام نفسها؛ فرضيات معلنة لا قياس (ar, RTL) |
| `/solutions-acteurs.json` | `/solutions-acteurs/resultats.json` | `web_cloud/solutions_posees_acteurs_resultats.json` — registre EQ-SA complet : `source` (transcript absent, mesuré 0 octet sur json3/srv3/xml), `chapitres` 13, `parametres_declares` 12, `equations` 13, `controles` 13, `limites`, `resume` ; lecture seule, recalculé à chaque génération de page |
| `/securite-bornee` | `/securite-bornee/`, `/securite_bornee` | `web_cloud/securite_bornee.html` — registre EQ-SB issu d'une vidéo de 22 min 46 s sans transcript (0 chapitre public, transcript mesuré absent) : 13 équations, 13 contrôles, 13 paramètres déclarés, 6 garanties énoncées jugées comme énoncés ; **borne ce qu'une garantie peut porter, ne juge ni entreprise ni personne, aucune mesure de produit réel** (fr) |
| `/securite-bornee/en` | — | `web_cloud/securite_bornee_en.html` — same register, same equations, same numbers; the module's own statements stay in French and the page says so (en) |
| `/securite-bornee/ar` | — | `web_cloud/securite_bornee_ar.html` — السجل نفسه والصيغ نفسها والأرقام نفسها؛ فرضيات معلنة لا قياس، وعبارات السجل بالفرنسية كما يُصدرها الوحدة (ar, RTL) |
| `/securite-bornee.json` | `/securite-bornee/resultats.json` | `web_cloud/securite_bornee_resultats.json` — registre EQ-SB complet : `source`, `parametres_declares` 13, `garanties_declarees` 6, `marqueurs_absolus` 9, `mesure` (13 blocs de calculs exacts), `equations` 13, `controles` 13, `certificat` avec `racine_merkle_sha256` identique à celle du dépôt scellé, `limites` ; lecture seule, recalculé à chaque génération de page |
| `/socle-313t` | `/socle-313t/`, `/socle_313t` | `web_cloud/socle_313t.html` — registre EQ-PS du socle de 313 × 10^12 poids adressables (`reseau_poids_sparse_mizan.py`) : 9 équations, 9 contrôles, 19 paramètres déclarés, banc de non-vacuité de 8 fixtures sur 9 (EQ-PS-02 n'en porte pas, la page le dit) ; source = constante `C` scellée et échelle demandée par l'auteur, **pas une vidéo** ; capacité déclarée, majorant d'adresses nommables et poids matérialisés mesurés sont trois nombres distincts, **aucune preuve, aucune machine sous tension** (fr) |
| `/socle-313t/en` | — | `web_cloud/socle_313t_en.html` — same register, same equations, same three distinct numbers; declared capacity, upper bound of nameable addresses, measured materialised weights (en) |
| `/socle-313t/ar` | — | `web_cloud/socle_313t_ar.html` — السجل نفسه والصيغ نفسها والأرقام نفسها؛ سعة معلنة وسقف للأسماء ووزن مُاد مُقاس، وعبارات السجل الفرنسية كما يُصدرها الوحدة (ar, RTL) |
| `/socle-313t.json` | `/socle-313t/resultats.json` | `web_cloud/socle_313t_resultats.json` — rapport EQ-PS complet : `rapport` (`equations` 9 avec `forme`, `statut`, `valeur`, `chemin_controle`, `limite`, `compte` `{PASS: 9, FAIL: 0, INCONCLUSIF: 0}`, `racine` SHA-256 des neuf verdicts, `duree_observation_seconde`, `cadre` 23 champs dont `registre`, sans `cle_test` ni `echantillon`) et `mutations` (8 captées sur 8 testées) ; lecture seule, recalculé à chaque génération de page |

Les fichiers HTML sont lus à chaque requête. Aucun cache applicatif. Les six pages de compte sont renvoyées avec `Cache-Control: no-cache` et `X-Content-Type-Options: nosniff`.

Une route GET non reconnue qui ne commence pas par `/api/` renvoie `web_cloud/page_404.html` avec le code `404` ; une route API inconnue renvoie un JSON `{"succes": false, "erreur": "Route GET introuvable"}` en `404`.

**Miroir partiel, mesuré le 2026-11-14.** Les huit lignes ajoutées ici couvrent les deux registres
que ce dépôt embarque (EQ-SA et EQ-SB) ; elles sont recopiées verbatim de la table de l'atelier.
Cette copie n'est **pas** la table complète : comparée au dictionnaire `PAGES_PUBLIQUES` de la
passerelle de production (135 clés de route), 86 d'entre elles — 51 familles — n'ont pas de ligne
ici, parce que les pages correspondantes vivent du côté atelier et ne sont pas embarquées. Le contrôle
est rejouable sans réseau : lire les clés du dictionnaire, chercher chaque `` `/route` `` dans le
présent fichier et compter les absences. Ce qui est affirmé : les routes listées ci-dessus sont servies.
Ce qui ne l'est pas : que la liste soit exhaustive.

**Second relevé, mesuré le 2026-11-14 à 10:37 UTC.** Quatre lignes de plus sont ajoutées ci-dessus —
`/socle-313t`, `/socle-313t/en`, `/socle-313t/ar`, `/socle-313t.json` — et couvrent le troisième
registre que ce dépôt embarque, le socle 313T (EQ-PS) : **douze lignes descriptives pour trois
registres**, et le tableau du fichier passe de 100 à 104 lignes. Elles sont recopiées octet pour octet
de la table de l'atelier ; le contrôle est fait par diff des quatre lignes, pas par relecture.
Sous la recette énoncée au paragraphe précédent — chercher exactement `` `/route` `` dans le présent
fichier pour chaque clé de `PAGES_PUBLIQUES` — le même fichier rendait, à l'instant de HEAD
(`6c487af`, sans les quatre lignes) **91 absences en 53 familles** sur les 140 clés actuelles ; après
ajout, **86 absences en 51 familles**, les cinq clés du socle (`/socle-313t`, son alias `/socle-313t/`,
son alias `/socle_313t`, `/socle-313t/en`, `/socle-313t/ar`) passant d'absentes à couvertes par les
deux premières colonnes de la ligne canonique, et deux familles disparaissant avec elles. Le relevé
de 05:57:59 UTC (commit `618ae6a` : 135 clés, 86 absences, 51 familles) n'est donc pas contredit :
les cinq clés gagnées par la passerelle depuis cette heure sont précisément celles du socle, et les
recouvrir rend exactement les deux mêmes compteurs. La règle des familles, énoncée parce qu'elle ne se
devine pas : une clé est ramenée à sa famille en retirant un suffixe `/en`, `/ar` ou `/fr`, puis un
`/` final, puis un suffixe `.json` ; on compte ensuite les familles distinctes. Ce qui est affirmé :
ces douze lignes descriptives sont servies en production. Ce qui ne l'est pas : que la table soit
complète, ni que les 86 absences soient des routes cassées.

---

## 3. Lectures JSON (GET)

| Route | Description | Champs principaux |
| :--- | :--- | :--- |
| `/api/v1/sante` (`/sante`, `/ping`) | Santé et invariants. | `statut`, `service`, `horodatage_iso`, `invariants` |
| `/api/v1/offres` (`/api/v1/offres-services`) | Catalogue public des offres et services, source `module_offres_mizan.py`. | `catalogue.version`, `segments`, `offres`, `services`, `statut_tarifs`, `note_quotas`, `eligibilite_publique` |
| `/api/v1/statut` (`/api/v1/status`, `/api/v1/composants`) | État instantané et honnête des composants, sans historique d'uptime. | `statut_global`, `horodatage_iso`, `composants[]`, `disponibilite.mesure`, `note` |
| `/api/v1/etat` | Tenseur 12D **simulé** par le modèle interne, sans instrument. | `nature`, `avertissement`, `tenseur_12d`, `securite_physique` |
| `/api/v1/synapses` | Connectome et boucle. | `connectome.total_synapses_actives`, `boucle_infinie_permanente` |
| `/api/v1/bibliotheque?q=<sujet>` | Recherche cosinus dans la base locale. | `sujet_recherche`, `traites_trouves`, `total_traites_ram`, `latence_acces_ram_ms` |
| `/api/v1/webhooks` | Abonnements et 10 derniers événements. | `total_webhooks_inscrits`, `abonnements`, `derniers_evenements_emis` |
| `/api/v1/inventaire` (`/inventaire`, `/hub`) | Inventaire A126 ; écrit un bilan. | `acte`, `inventaire`, `symbole` |
| `/api/v1/legal` (`/api/v1/entreprise`, `/api/v1/conformite`) | Métadonnées légales. | `entreprise_conforme` |
| `/api/v1/auth/statut_session` | État du démonstrateur multimodal, jamais authentifiant. | `est_souverain` (toujours `false`), `authentifiant`, `mode`, `avertissement`, `session` sans jeton |
| `/api/v1/agent_code` (`/api/v1/agent_code/statut`, `/agent_code`) | Audit statique local du code. | Bilan de l'agent harmonisateur |
| `/api/v1/materiel/gpu` (`/api/v1/gpu`, `/api/v1/materiel`) | Contexte d'exécution matériel. | `infrastructure` |
| `/api/v1/voix` (`/api/v1/voix/statut`) | Statut du démonstrateur vocal. | `vocal.modele_charge`, `vocal.transcription_reelle_disponible`, `vocal.avertissement` |
| `/api/v1/voix/acoustique` (`/api/v1/acoustique`, `/api/v1/prosodie`) | Gabarit prosodique dérivé de l'horloge logique. | `nature`, `avertissement`, `acoustique` |
| `/api/v1/ecoute/spectre` (`/api/v1/cochlee`, `/api/v1/spectre`) | Bandes normalisées par défaut (30/55/15), sans micro. | `nature`, `avertissement`, `spectre_ecoute` |
| `/api/v1/synchronisation/totale` (`/api/v1/unification`, `/api/v1/harmonie_totale`) | Synthèse d'unification. | Rapport de l'orchestrateur |
| `/api/v1/synchronisation` (`/api/v1/sync`) | Métriques de la couche intermédiaire. | `synchronisation` |
| `/api/v1/audit/paiements` (`/api/v1/audit/transactions`) | Rapport d'audit JSON. | `audit` — 404 si le fichier est absent |
| `/api/v1/economie_islamique/statut` (`/api/v1/islamic_economy`, `/economie_islamique`) | Bilan anti-Riba/Zakat. | `economie_islamique` |
| `/api/v1/unifie` (`/unifie/donnees`) | Bilan des 4 démarches. | `bilan` |
| `/api/v1/qubit_logique` (`/api/v1/qubit-logique`, `/api/v1/qubit`) | Résultats du qubit logique `[[7,1,3]]` lus dans `resultats/qubit_logique/resume.json`. Lecture seule, sans effet de bord. | `qubit_logique.code`, `resultats`, `materiel`, `surface`, `statut`, `limites` — 404 si l'artefact est absent |

### 3.1 Comptes (GET, cookie de session)

| Route | Description | Champs principaux |
| :--- | :--- | :--- |
| `/api/v1/comptes/statut_public` (`/statistiques_publiques`) | Agrégats publics, sans donnée personnelle. | `statistiques_publiques.comptes_actifs`, `particuliers`, `entreprises`, `secteur_public`, `domaines_verifies` |
| `/api/v1/comptes/moi` | Profil du compte connecté. | `utilisateur` — 401 sans session valide |
| `/api/v1/comptes/sessions` | Sessions actives du compte, session courante signalée. | `sessions` |
| `/api/v1/comptes/export` | Export JSON des données du compte, en pièce jointe ; lecture journalisée. | `export` (profil, sessions, domaines, devis, journal), en-tête `Content-Disposition` |
| `/api/v1/comptes/devis` | Demandes de devis du compte connecté, 50 dernières. | `devis[]` (`reference`, `offre_code`, `statut`, `montant_indicatif_centimes`, `montant_propose_centimes`, `note_admin`) |
| `/api/v1/admin/devis?limite=200` | File des demandes de devis avec email et type de compte (admin). | `devis[]` — `limite` bornée à 500 |
| `/api/v1/admin/verifications?limite=200` | Demandes de vérification en attente (admin). | `verifications` — `limite` bornée à 500 |
| `/api/v1/admin/utilisateurs` | 200 derniers comptes (admin). | `utilisateurs` |
| `/api/v1/admin/journal` | 200 dernières entrées d'audit sans PII (admin). | `journal` |
| `/api/v1/admin/statistiques` | Statistiques agrégées (admin). | `statistiques` |

Le profil `utilisateur` contient : `id`, `handle`, `nom_affichage`, `type_compte`, `statut`, `email_verifie`, `verification_niveau`, `organisation`, `domaine_verifie`, `double_validation`, `cree_le`, `derniere_connexion`, `email`, `score_confiance`.

### 3.2 Qubit logique — `GET /api/v1/qubit_logique`

Route publique, en lecture seule : elle renvoie le contenu de `resultats/qubit_logique/resume.json` sans le régénérer, donc sans écriture disque. Si l'artefact n'a pas été généré, la réponse est `404` avec la commande de génération.

```bash
curl -s http://127.0.0.1:8095/api/v1/qubit_logique | head -40
```

```json
{
  "succes": true,
  "source": "resultats/qubit_logique/resume.json",
  "reproduction": "py -3 qubit_logique_mizan.py --verifier && py -3 qubit_logique_mizan.py --rapport",
  "qubit_logique": {
    "version": "1.0",
    "source": { "fichier": "qubit_logique_mizan.py", "sha256": "8c6c3d7e…" },
    "statut": {
      "code_et_preuves": "opérationnel (logiciel, calcul exact)",
      "simulation": "exacte pour le modèle de capacité de code, recoupée par Monte Carlo",
      "materiel": "modèle d'ingénierie paramétré, non mesuré",
      "qubit_physique": "non réalisé : aucun QPU, cryostat ou capteur physique",
      "reconnaissance_par_les_pairs": "non acquise : elle exige une revue externe indépendante"
    },
    "code": { "parametres": "[[7,1,3]]", "distance": 3, "paulis_verifies": 211 },
    "resultats": { "taux_exacts": [], "seuil_pseudo": 0.08108189622828846 }
  }
}
```

Champs utiles : `qubit_logique.code` (preuves), `qubit_logique.resultats` (taux exacts, coefficient quadratique, seuil, Monte Carlo, répartition par poids), `qubit_logique.materiel` (budget DAC/horloge/décohérence, décodeur), `qubit_logique.surface` (projection non simulée) et `qubit_logique.limites`. Détail des calculs : [`QUBIT_LOGIQUE.md`](QUBIT_LOGIQUE.md).

### Exemple — santé

```bash
curl -s http://127.0.0.1:8095/api/v1/sante
```

```json
{
  "statut": "OPERATIONNEL",
  "service": "Passerelle REST Légère & Webhooks VPS Al-Mizan",
  "systeme": "ASTRO-Q°ODE / AL-MIZAN",
  "horodatage_iso": "2026-10-27T00:00:00Z",
  "invariants": {
    "bride_mizan": 0.6225,
    "killswitch_cryo_mk": 45.0,
    "horloge_universelle_mhz": 135.097021,
    "partage_commercial": "50/50",
    "taux_usure_riba": "0.0%"
  },
  "symbole": "🛡️🟢 LE JUSTE MILIEU VPS"
}
```

Les valeurs exactes de `bride_mizan` et `killswitch_cryo_mk` sont définies dans [`bibliotheques/lib_almizan_extension.py`](../bibliotheques/lib_almizan_extension.py) et réexportées par [`module_ia_autonome_boucle_fermee_mizan.py`](../module_ia_autonome_boucle_fermee_mizan.py). Ne pas les recopier en dur dans un client : lire la réponse.

### Exemple — tenseur 12D

```bash
curl -s http://127.0.0.1:8095/api/v1/etat
```

Champs : `temperature_cryo_mk`, `derive_thermique_mks`, `stabilite_horloge_dt_pct`, `fidelite_quantique_bell`, `entropie_quantique`, `debit_silicium_mops`, `satisfaction_maslow`, `ratio_or_argent`, `partage_5050_pct`, `taux_usure_riba_pct`, `pression_cyber`, `harmonie_globale_mizan`.

Ces grandeurs sont produites par le modèle logiciel. Elles ne proviennent pas de capteurs physiques.

---

## 4. Écritures JSON (POST)

### 4.1 Dialogue — `POST /api/v1/interagir`

Alias : `/api/v1/dialogue`.

```json
{
  "message": "Bonjour Al-Mizan",
  "canal": "API_VPS_REST",
  "spectre_audio": null
}
```

Réponse 200 :

```json
{
  "succes": true,
  "id_interaction": "...",
  "message_utilisateur": "...",
  "reponse_ia": "...",
  "prosodie_mizan": {},
  "mode_esprit": "GOOGLE_GEMINI_... ou mode local",
  "modele_configure": "...",
  "actions_executees": [],
  "garde_fous_valides": true,
  "symbole_securite": "..."
}
```

- `message` ou `texte` requis ; sinon 400.
- Si aucune clé Gemini n'est configurée, le moteur local répond et `mode_esprit` l'indique.
- Échec interne : 503 avec `{"succes": false, "erreur": "...", "detail": "..."}`.

### 4.2 Commande proactive — `POST /api/v1/commande`

Alias : `/api/v1/action`. **Route protégée.**

```bash
curl -s -X POST http://127.0.0.1:8095/api/v1/commande \
  -H "Authorization: Bearer $MIZAN_VPS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"action":"MAINTIEN_HARMONIQUE_OPTIMAL","justification":"Contrôle périodique"}'
```

Actions acceptées (`TypeActionProactive`) :

- `REGULATION_PREEMPTIVE_THERMIQUE`
- `RECALIBRAGE_PHASE_QUANTIQUE_BELL`
- `MODULATION_CADENCE_SILICIUM`
- `REEQUILIBRAGE_RESERVES_MASLOW`
- `CONFINEMENT_PREVENTIF_FLUX_CYBER`
- `SYNCHRONISATION_PULSE_TRINITE_DT`
- `MAINTIEN_HARMONIQUE_OPTIMAL`

Sans jeton, ou si `MIZAN_VPS_API_KEY` n'est pas configurée : 401. Action inconnue : 400 avec la liste des valeurs valides.

La commande est **enregistrée**, horodatée et diffusée par webhook (`COMMANDE_EXEC`). Aucun actionneur physique n'est piloté par cette route : la réponse porte `nature: "enregistrement"` et `avertissement`.

### 4.3 Audit cyber — `POST /api/v1/cyber/auditer`

Alias : `/api/v1/cyber/scan`.

```json
{"url": "https://www.al-mizan.world"}
```

Garde anti-SSRF :

1. Schéma `http` ou `https` uniquement ; `ftp://` et les autres schémas sont refusés avant toute transformation.
2. Identifiants intégrés (`user:pass@`) refusés.
3. Port 80 ou 443 uniquement.
4. **Toutes** les adresses résolues doivent être publiques (`ipaddress.is_global`).
5. Redirections HTTP refusées (aucun rebond vers une cible interne).
6. Timeout de 6 s.

Réponse : `audit.url_auditee`, `statut_connexion`, `latence_ms`, `ssl_tls`, `en_tetes_securite`, `score_resilience_100` (plafonné à 99), `calcul_al_mizan_sans_dol`, `recommandations`.

L'analyse est heuristique et non certifiée. Le champ `note_honnetete` le rappelle dans chaque réponse.

### 4.4 Webhooks

Inscription — `POST /api/v1/webhooks/inscrire` :

```json
{
  "url_cible": "https://exemple.test/webhook",
  "evenements": ["COMMANDE_EXEC", "INTERACTION_VIVANTE"]
}
```

Réponse : `webhook.id_webhook` (`HOOK-...`), `url_cible`, `evenements`, `actif`, `date_inscription_iso`.

Événements émis par la passerelle : `INTERACTION_VIVANTE`, `COMMANDE_EXEC`, `WEBHOOK_ENTRANT_RECU`, `SOUVERAIN_CONNECTE`, `TENTATIVE_USURPATION_REFUSEE`.

Réception — `POST /webhook/recevoir` (alias `/api/v1/webhooks/entree`) :

```json
{"evenement": "PING_EXTERNE", "payload": {"source": "monitoring"}}
```

Réponse : `{"succes": true, "statut": "REÇU_ET_TRAITÉ"}`.

Signature sortante :

- En-tête `X-AlMizan-Signature`.
- Champ `signature_hmac_sha256` dans le corps.
- HMAC-SHA256 sur `json.dumps(charge_sans_signature, sort_keys=True).encode("utf-8")` avec `MIZAN_WEBHOOK_SECRET`.

Vérification côté client :

```python
import hashlib, hmac, json

def verifier(charge: dict, secret: bytes) -> bool:
    signature = charge.pop("signature_hmac_sha256", "")
    canonique = json.dumps(charge, sort_keys=True).encode("utf-8")
    attendu = hmac.new(secret, canonique, hashlib.sha256).hexdigest()
    return hmac.compare_digest(attendu, signature)
```

> Limite : l'inscription n'est pas authentifiée et l'URL cible n'est pas validée contre les adresses internes. Voir la dette technique dans [`ARCHITECTURE_ET_DEVELOPPEMENT.md`](ARCHITECTURE_ET_DEVELOPPEMENT.md#11-limites-connues-et-dette-technique).

### 4.5 Démonstrateur multimodal (ex-« session souveraine »)

**Aucune authentification.** Les trois facteurs sont déclarés par le client ; le serveur ne vérifie ni caméra, ni micro, ni signature WebAuthn. Le jeton renvoyé ne donne aucun droit et n'est accepté par aucune route protégée.

| Route | Corps | Réponse |
| :--- | :--- | :--- |
| `POST /api/v1/auth/sas_biometrique/challenge` (`/sas/challenge`) | `{}` | `id_defi`, `phrase_a_prononcer`, `sel_cryptographique`, `cree_a_epoch`, `ip_source`, `nature`, `avertissement` |
| `POST /api/v1/auth/sas_biometrique/valider` (`/sas/valider`) | voir ci-dessous | 200 + `session` (sans jeton) + `jeton_demonstration` marqué non authentifiant, ou 403 |
| `GET /api/v1/auth/statut_session` | — | `mode` `DEMONSTRATION_NON_AUTHENTIFIANTE` ou `VISITEUR_PUBLIC` ; `est_souverain` toujours `false` ; jamais de jeton |
| `POST /api/v1/auth/deconnexion` (`/sas/deconnexion`) | `{}` | `SESSION_REVOQUEE_RETOUR_PUBLIC` |

Corps de validation :

```json
{
  "id_defi": "CHALLENGE-...",
  "phrase_prononcee": "Bonjour Al-Mizan, c'est Ahmed",
  "spectre_audio_moyenne": [0.42],
  "visage_detecte": true,
  "score_vivacite_liveness": 0.9,
  "signature_materielle_passkey": "chaine-de-16-caracteres-minimum"
}
```

La démonstration exige seulement que les trois valeurs déclarées soient cohérentes entre elles. Le défi expire après 90 s. Aucune captation, aucun anti-spoofing et aucune validation cryptographique ne sont effectués : ne jamais utiliser cette route comme contrôle d'accès.

### 4.6 Économie islamique

Contrat — `POST /api/v1/economie_islamique/contrat/verifier` :

```json
{
  "type_contrat": "MUDARABA",
  "partie_a": "Investisseur",
  "partie_b": "Entrepreneur",
  "capital": 1000.0,
  "taux_interet": 0.0,
  "cle_partage": "50/50"
}
```

Un `taux_interet` non nul produit `REJETE_RIBA`. Réponse : `contrat` avec `statut_conformite_sharia`.

Zakat — `POST /api/v1/economie_islamique/zakat/prelever` :

```json
{"compte": "CITE_GALAXY_MOBILE", "solde": 1000000.0}
```

Le prélèvement est de 2,5 % au-delà du Nisab. Il s'agit d'une opération sur le grand livre logiciel, pas d'un débit bancaire.

### 4.7 Voix — `POST /api/v1/voix/transcrire`

Alias : `/api/v1/voix/stt`.

```json
{"audio_base64": "<base64>", "format": "webm"}
```

Réponse : `transcription` (bilan du démonstrateur vocal), `audio_recu` (base64 valide ou non), `transcription_reelle` (toujours `false`), `nature: "demonstration"` et `avertissement`.

Aucun moteur de reconnaissance vocale n'est chargé : le champ `texte_transcrit` reste vide et aucun enregistrement n'est conservé. Limite : 8 Mo encodés, au-delà la réponse est 413. Un base64 invalide donne `audio_recu: false` sans erreur serveur.

### 4.8 Orchestrateur unifié — `POST /api/v1/unifie/executer`

```json
{"prompt": "Explique l'harmonie du Mizan.", "webhook": null}
```

Réponse : `bilan`. La valeur `webhook` est transmise à l'orchestrateur ; ne l'utiliser qu'avec une cible de confiance.

### 4.9 Comptes — `/api/v1/comptes/*`

Toutes ces écritures exigent `Origin` autorisé et `X-Mizan-CSRF: 1`. Le cookie de session est posé par `connexion` et `connexion/2fa`.

```bash
# Inscription
curl -s -X POST http://127.0.0.1:8095/api/v1/comptes/inscription \
  -H "Content-Type: application/json" \
  -H "Origin: http://127.0.0.1:8095" \
  -H "X-Mizan-CSRF: 1" \
  -d '{
    "email": "contact@exemple.test",
    "mot_de_passe": "UnMotDePasse2026!",
    "nom_affichage": "Exemple SARL",
    "handle": "exemple-sarl",
    "type_compte": "entreprise",
    "organisation": "Exemple SARL"
  }'
```

Réponse 201 : `user_id`, `email_verifie` (`false`), message invitant à consulter l'email. Si l'envoi d'email échoue, la création est annulée et la réponse est 503 `MESSAGERIE_INDISPONIBLE`.

| Route | Corps | Effet |
| :--- | :--- | :--- |
| `POST /inscription` | `email`, `mot_de_passe`, `nom_affichage`, `handle`, `type_compte` (`particulier`, `entreprise`, `public`), `organisation` (requis pour entreprise/public) | 201 ; envoie un lien de vérification valable 24 h. |
| `POST /verification` | `token` | Active l'adresse ; renvoie `utilisateur`. |
| `POST /renvoyer-verification` | `email` | Réponse identique que le compte existe ou non ; 3 envois/heure/email. |
| `POST /connexion` | `email`, `mot_de_passe` | Pose le cookie de session, ou renvoie `deux_facteurs_requis: true` et `jeton_defi` si la double validation est active. |
| `POST /connexion/2fa` | `jeton_defi`, `code` (6 chiffres, 10 min) | Pose le cookie de session. |
| `POST /deconnexion` | `{}` | Révoque la session et efface le cookie. |
| `POST /sessions/revoquer` | `mot_de_passe` | Révoque toutes les sessions du compte (y compris la courante) ; efface le cookie. |
| `POST /double-validation` | `actif` (booléen), `mot_de_passe` | Active ou coupe la double validation par email ; 503 si la messagerie n'est pas configurée lors de l'activation. |
| `POST /reinitialisation/demander` | `email` | Réponse identique que le compte existe ou non ; lien valable 60 min. |
| `POST /reinitialisation/confirmer` | `token`, `mot_de_passe` | Réinitialise le mot de passe et révoque les sessions. |
| `POST /domaines/demander` | `domaine` | Réservé aux comptes `entreprise` et `public`. Renvoie `jeton_verification` à publier dans un enregistrement DNS TXT `_mizan-verification.<domaine>`. |
| `POST /devis` | `offre_code`, `besoins` (20 à 2000 caractères), `volume_utilisateurs` (1 à 500) | 201 ; crée une demande `recu`, avec `montant_indicatif_centimes` issu du catalogue. Aucun paiement. Refus 403 `SEGMENT_INCOMPATIBLE` si l'offre ne correspond pas au type de compte ; 400 `OFFRE_INCONNUE`, `BESOIN_INVALIDE`, `VOLUME_INVALIDE` ; 429 après 5 demandes par 24 h. |
| `POST /devis/annuler` | `devis_id` | Passe une demande `recu`, `en_revue` ou `devis_envoye` à `annule`. 409 `DEVIS_NON_ANNULABLE` au-delà. |
| `POST /supprimer` | `mot_de_passe`, `confirmation` = `SUPPRIMER` | Supprime le compte : anonymisation, sessions, jetons et demandes de devis effacés, cookie effacé. |

Règles de validation :

- Mot de passe : 12 à 128 caractères, au moins une lettre et un chiffre, ni courant ni contenant l'email local ou le handle.
- Handle : 3 à 32 caractères, minuscules, chiffres, `.`, `_`, `-`, sans séparateur aux extrémités ni séparateurs consécutifs ; les noms réservés (`admin`, `support`, `mizan`, `imam8mahdi`…) sont refusés.
- Un même email (insensible à la casse) ou un handle équivalent (séparateurs ignorés) ne peut être utilisé deux fois : 409 `COMPTE_EXISTANT`.

Limites de débit (fenêtre fixe, réponse 429 avec `Retry-After`) :

| Clé | Maximum | Fenêtre |
| :--- | :--- | :--- |
| `inscription_ip:<ip>` | 10 | 1 h |
| `connexion_ip:<ip>` | 30 | 15 min |
| `connexion_email:<email>` | 8 | 15 min |
| `renvoi_email:<email>` | 3 | 1 h |
| `reinit_ip:<ip>` | 10 | 1 h |
| `reinit_email:<email>` | 3 | 1 h |
| `defi_ip:<ip>` | 20 | 15 min |
| `domaine_ip:<ip>` | 5 | 1 h |

Les adresses IP et les emails sont hachés en HMAC-SHA256 avant stockage ; le journal d'audit ne contient aucune PII en clair. Voir [`COMPTES_ET_SECURITE.md`](COMPTES_ET_SECURITE.md) pour le modèle de données, la rétention et la formule du score de confiance.

### 4.10 Administration — `/api/v1/admin/*`

Réservé aux comptes de type `admin` (cookie de session + `X-Mizan-CSRF: 1`). Un administrateur ne peut pas suspendre son propre compte (400 `ACTION_REFUSEE`).

| Route | Corps | Effet |
| :--- | :--- | :--- |
| `POST /verifications/approuver` | `user_id`, `niveau` (`1` ou `2`), `domaine`, `note` | Passe le compte au niveau demandé ; un compte `public` est forcé au niveau 2. |
| `POST /verifications/refuser` | `user_id`, `note` | Refuse la demande de vérification. |
| `POST /utilisateurs/suspendre` | `user_id`, `note` | Suspend le compte et révoque ses sessions. |
| `POST /utilisateurs/reactiver` | `user_id` | Réactive un compte suspendu. |
| `POST /devis/statut` | `devis_id`, `statut` (`en_revue`, `devis_envoye`, `accepte`, `refuse`, `annule`), `note` (≤ 1000 caractères), `montant_propose_centimes` (optionnel) | Met à jour la demande ; `montant_propose_centimes` absent conserve la valeur existante. 400 `STATUT_INVALIDE` ou `MONTANT_INVALIDE`. |

La revue humaine reste nécessaire : l'approbation ne doit être prononcée qu'après contrôle du domaine, de l'organisation et de l'usage déclaré.

---

## 5. Codes HTTP

| Code | Usage |
| :--- | :--- |
| 200 | Succès. |
| 201 | Compte créé (inscription) ou demande de devis enregistrée. |
| 400 | Champ requis manquant, schéma/port/URL refusés, action inconnue, données de compte invalides. |
| 401 | Jeton absent sur `/api/v1/commande` ; session de compte absente, expirée ou identifiants incorrects. |
| 403 | Facteurs de démonstration déclarés incohérents ; `Origin` refusé ; `X-Mizan-CSRF` absent ; compte suspendu ; route admin sans rôle admin. |
| 404 | Route inconnue, rapport d'audit absent, compte ciblé introuvable. |
| 409 | Email ou handle déjà utilisé, domaine déjà vérifié ou déjà en attente. |
| 429 | Limite de débit atteinte ; l'en-tête `Retry-After` donne le délai en secondes. |
| 500 | Exception interne pendant un audit ou un traitement. |
| 503 | Échec du pipeline de dialogue ou service email non configuré. |

Les réponses d'erreur conservent la forme `{"succes": false, "erreur": "..."}` ; les routes de compte ajoutent un champ `code` machine.

---

## 6. Tests rapides

```bash
# Santé
curl -s http://127.0.0.1:8095/api/v1/sante

# Page publique
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8095/

# Catalogue, statut et 404 HTML
curl -s http://127.0.0.1:8095/api/v1/offres | head -20
curl -s http://127.0.0.1:8095/api/v1/statut | head -20
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8095/route-inconnue

# Devis sans session (attendu : 401)
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8095/api/v1/comptes/devis

# Dialogue
curl -s -X POST http://127.0.0.1:8095/api/v1/interagir \
  -H "Content-Type: application/json" \
  -d '{"message":"Bonjour"}'

# Commande refusée sans jeton (attendu : 401)
curl -s -o /dev/null -w "%{http_code}\n" -X POST \
  http://127.0.0.1:8095/api/v1/commande \
  -H "Content-Type: application/json" \
  -d '{"action":"MAINTIEN_HARMONIQUE_OPTIMAL"}'

# Anti-SSRF (attendu : 400)
curl -s -X POST http://127.0.0.1:8095/api/v1/cyber/auditer \
  -H "Content-Type: application/json" \
  -d '{"url":"http://127.0.0.1:8095/api/v1/sante"}'

# Pages de compte (attendu : 200)
for page in inscription connexion compte verification cgu confidentialite; do
  curl -s -o /dev/null -w "$page %{http_code}\n" "http://127.0.0.1:8095/$page"
done

# Écriture de compte sans anti-CSRF (attendu : 403)
curl -s -o /dev/null -w "%{http_code}\n" -X POST \
  http://127.0.0.1:8095/api/v1/comptes/inscription \
  -H "Content-Type: application/json" \
  -d '{"email":"test@exemple.test"}'

# Profil sans session (attendu : 401)
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8095/api/v1/comptes/moi

# Qubit logique (attendu : 200, page en français et JSON)
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8095/qubit-logique
curl -s http://127.0.0.1:8095/api/v1/qubit_logique | py -3 -c "import sys,json; d=json.load(sys.stdin); print(d['qubit_logique']['code']['distance'])"
```

Suites automatisées :

```bash
py -3 -m unittest tests.test_passerelle_api_vps -v
py -3 -m unittest tests.test_comptes_utilisateurs_mizan -v
py -3 -m unittest tests.test_comptes_http_mizan -v
py -3 -m unittest tests.test_qubit_logique_mizan -v
py -3 -m unittest tests.test_qubit_http_mizan -v
```
