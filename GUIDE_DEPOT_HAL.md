# GUIDE DE DÉPÔT SUR HAL (Archive Ouverte)

## 📋 Étape 1 : Accéder à HAL

**URL :** https://hal.science/

1. Cliquez sur **"Se connecter"** (en haut à droite)
2. Connectez-vous avec votre compte HAL ou créez-en un
   - Vous pouvez utiliser votre email : elbahloulahmed505@gmail.com
   - Ou vous connecter via ORCID/Recherche&Référentiel

---

## 📝 Étape 2 : Initier le dépôt

1. Une fois connecté, cliquez sur **"Déposer"** dans le menu principal
2. Sélectionnez **"Déposer un document"**
3. Choisissez le type : **"Logiciel"** (Software)

---

## 📄 Étape 3 : Remplir les métadonnées

### Section "Identification"

**Titre principal :**
```
AL-MIZAN : Émulateur quantique pur Python avec certificats mathématiques scellés pour les problèmes du millénaire
```

**Titre secondaire (anglais) :**
```
AL-MIZAN: A Pure-Python Quantum Emulator with Sealed Mathematical Certificates for Millennium Problems
```

**Type de document :** Logiciel

**Statut du document :** Publié

---

### Section "Auteurs"

**Auteur 1 :**
- Nom : EL BAHLOUL
- Prénom : Ahmed
- Civilité : M.
- Email : elbahloulahmed505@gmail.com
- Affiliation : IMAM8MAHDI Research Initiative, Valence, France
- Rôle : Auteur principal

**Auteur 2 (optionnel - assistance IA) :**
- Nom : Devin
- Organisation : Cognition AI
- Rôle : Assistance IA (SWE-2)
- Note : Mentionner dans les commentaires que c'est une IA

---

### Section "Résumés"

**Résumé français :**
```
AL-MIZAN est un émulateur quantique complet implémenté en Python pur sans dépendances externes, unifiant la simulation par vecteur d'état, l'évolution par matrice densité, la correction d'erreurs quantiques (code Steane [[7,1,3]]), l'extrapolation à bruit nul (ZNE) et la génération de layout GDSII pédagogique. Au-delà de la simulation quantique, le paquetage fournit des certificats mathématiques scellés SHA-256 pour des vérifications bornées de problèmes du millénaire : la Conjecture du Point Carré (PC-1..PC-5 prouvées par exhaustion), le théorème de Turing sur la bande de Riemann ≤100 (29 zéros certifiés par arithmétique d'intervalles), et la vérification BSD sur des courbes elliptiques nommées. L'architecture maintient des contraintes d'honnêteté strictes — chaque artefact porte sa borne de calcul, et aucun problème ouvert du millénaire n'est revendiqué comme résolu.
```

**Résumé anglais :**
```
AL-MIZAN is a complete quantum emulator implemented in pure Python with zero external dependencies, unifying state vector simulation, density matrix evolution, quantum error correction (Steane [[7,1,3]] code), zero-noise extrapolation (ZNE), and pedagogical GDSII layout generation. Beyond quantum simulation, the package provides sealed SHA-256 mathematical certificates for bounded verifications of millennium problems: the Point Square Conjecture (PC-1..PC-5 proven by exhaustion), Turing's theorem on the Riemann strip ≤100 (29 zeros certified via interval arithmetic), and BSD verification on named elliptic curves. The architecture maintains strict honesty constraints—every artifact carries its computational bound, and no open millennium problem is claimed as solved.
```

---

### Section "Mots-clés"

**Mots-clés français :**
- émulateur quantique
- Python
- correction d'erreurs quantiques
- hypothèse de Riemann
- conjecture BSD
- certificats mathématiques
- simulation quantique
- OpenQASM
- code Steane
- extrapolation à bruit nul

**Keywords anglais :**
- quantum emulator
- Python
- quantum error correction
- Riemann hypothesis
- BSD conjecture
- mathematical certificates
- quantum simulation
- OpenQASM
- Steane code
- zero-noise extrapolation

---

### Section "Domaines"

Sélectionnez :
- **Informatique** → Calcul formel
- **Mathématiques** → Physique mathématique
- **Physique** → Mécanique quantique

---

### Section "Langue"

**Langue du document :** Français
**Autres langues :** Anglais

---

### Section "Licence"

**Licence :** AGPL-3.0 (GNU Affero General Public License v3.0)

Si HAL ne propose pas AGPL-3.0 dans la liste, choisissez :
- "Autre licence ouverte" et précisez : "AGPL-3.0"

---

### Section "Déclaration IA" (IMPORTANT)

**Case à cocher :** "Ce document a été généré ou assisté par IA"

**Texte à ajouter dans les commentaires/notes :**
```
Ce logiciel a été développé avec l'assistance d'IA générative (Devin SWE-2, Cognition AI) pour la génération de code, les tests et la documentation. L'auteur humain (M. Ahmed EL BAHLOUL) a révisé, validé et dirigé tous les résultats, et a pris les décisions de conception fondamentales incluant la doctrine Al-Mizan, les règles du noyau scellé, l'architecture des certificats mathématiques et les contraintes d'honnêteté. Tout le code généré par IA a été inspecté manuellement et intégré sous supervision humaine.
```

---

### Section "Relations"

**Version révisée de :**
- ASTRO-Q°ODE_SYSTEME
- DOI : 10.5281/zenodo.23554838

**DOI associé :**
- 10.5281/zenodo.24028243

**URL du dépôt GitHub :**
- https://github.com/IMAM8MAHDI/AL-MIZAN-Quantum-Emulator

---

## 📁 Étape 4 : Télécharger les fichiers

**Fichiers à uploader :**

1. **ZENODO_DEPOT_ALMIZAN.zip** (archive complète)
   - Chemin : `C:\Users\Administrateur\Desktop\IMAM8MAHDI\ZENODO_DEPOT_ALMIZAN.zip`
   - Taille : ~1.6 GB
   - Description : "Archive complète du dépôt GitHub contenant code source, tests, documentation et métadonnées"

2. **paper.md** (optionnel - article scientifique)
   - Chemin : `C:\Users\Administrateur\Desktop\IMAM8MAHDI\ZENODO_DEPOT_ALMIZAN\paper.md`
   - Description : "Article scientifique au format JOSS (Journal of Open Source Software)"

3. **METADONNEES_HAL.md** (optionnel - documentation)
   - Chemin : `C:\Users\Administrateur\Desktop\IMAM8MAHDI\ZENODO_DEPOT_ALMIZAN\METADONNEES_HAL.md`
   - Description : "Métadonnées complètes du dépôt HAL"

---

## ✅ Étape 5 : Vérification et soumission

1. **Relisez toutes les métadonnées**
2. **Vérifiez que la déclaration IA est bien présente**
3. **Confirmez la licence AGPL-3.0**
4. **Cliquez sur "Déposer" ou "Soumettre"**

---

## 📧 Étape 6 : Après soumission

- HAL va vérifier votre dépôt (généralement 24-48h)
- Vous recevrez un email de confirmation
- Un **identifiant HAL** sera attribué (ex: hal-01234567)
- Le document sera accessible publiquement sur https://hal.science/

---

## ⚠️ Points d'attention

1. **Déclaration IA obligatoire** — Ne pas oublier de cocher la case et d'ajouter le texte
2. **Licence** — Bien spécifier AGPL-3.0
3. **Fichiers** — L'archive ZIP est volumineuse (~1.6 GB), assurez-vous d'avoir une bonne connexion
4. **Métadonnées** — Remplir tous les champs obligatoires (marqués d'un *)
5. **Résumés** — Les deux langues (français + anglais) sont recommandées

---

## 🔗 Liens utiles

- **HAL :** https://hal.science/
- **Aide HAL :** https://help.scientific-commons.org/
- **Licence AGPL-3.0 :** https://www.gnu.org/licenses/agpl-3.0.fr.html
- **Dépôt GitHub :** https://github.com/IMAM8MAHDI/AL-MIZAN-Quantum-Emulator
- **DOI Zenodo :** https://doi.org/10.5281/zenodo.24028243

---

## 📞 Support

Si vous rencontrez des problèmes :
- Email HAL : hal@inist.fr
- Documentation : https://www.ccsemi.fr/fr/aide

---

**Prêt à déposer ?** Suivez les étapes 1 à 6 ci-dessus. Le fichier METADONNEES_HAL.md contient toutes les informations en format copier-coller.
