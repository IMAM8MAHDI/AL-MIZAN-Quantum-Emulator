# GUIDE D'UTILISATION DU FICHIER HAL_DEPOSIT.xml

## 📄 Fichier créé

**HAL_DEPOSIT.xml** — Fichier XML complet au format SWORD (Simple Web-service Offering Repository Deposit) contenant toutes les métadonnées pour le dépôt HAL.

**Chemin :** `C:\Users\Administrateur\Desktop\IMAM8MAHDI\ZENODO_DEPOT_ALMIZAN\HAL_DEPOSIT.xml`

---

## 🎯 Deux méthodes de dépôt

### Méthode 1 : Dépôt manuel (recommandé)

Utilisez le XML comme référence pour remplir le formulaire HAL en ligne.

**Étapes :**

1. Ouvrez le fichier `HAL_DEPOSIT.xml` dans un éditeur de texte ou navigateur
2. Allez sur https://hal.science/
3. Connectez-vous et cliquez sur "Déposer"
4. Remplissez chaque champ en copiant les valeurs depuis le XML :
   - `<title>` → Titre du document
   - `<author>` → Auteurs
   - `<summary>` → Résumés FR/EN
   - `<category term="...">` → Mots-clés
   - `<hal:domain>` → Domaines scientifiques
   - `<dcterms:license>` → Licence
   - `<hal:ai-disclosure>` → Déclaration IA
   - etc.

**Avantages :**
- Contrôle total sur chaque champ
- Vérification visuelle avant soumission
- Pas besoin de credentials API

---

### Méthode 2 : Dépôt automatique via API SWORD

Pour les utilisateurs avancés avec accès API HAL.

**Prérequis :**
- Compte HAL avec login/mot de passe
- Ou token d'authentification HAL
- Python 3.10+ installé

**Script Python de dépôt automatique :**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de dépôt automatique HAL via API SWORD
"""

import requests
from pathlib import Path
import base64

# ============================================
# CONFIGURATION
# ============================================

HAL_API_URL = "https://api.archives-ouvertes.fr/sword/hal/"
HAL_USERNAME = "elbahloulahmed505@gmail.com"  # Remplacez par votre login HAL
HAL_PASSWORD = "VOTRE_MOT_DE_PASSE_HAL"        # Remplacez par votre mot de passe

XML_FILE = "HAL_DEPOSIT.xml"
ZIP_FILE = "ZENODO_DEPOT_ALMIZAN.zip"

# ============================================
# AUTHENTIFICATION
# ============================================

def get_auth_header():
    """Génère l'en-tête d'authentification Basic"""
    credentials = f"{HAL_USERNAME}:{HAL_PASSWORD}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return {"Authorization": f"Basic {encoded}"}

# ============================================
# DÉPÔT DU XML (MÉTADONNÉES)
# ============================================

def deposit_metadata():
    """Dépose le fichier XML des métadonnées"""
    print("📤 Dépôt des métadonnées XML...")
    
    headers = get_auth_header()
    headers["Content-Type"] = "application/atom+xml;type=entry"
    headers["Content-Length"] = str(Path(XML_FILE).stat().st_size)
    
    with open(XML_FILE, "rb") as f:
        xml_content = f.read()
    
    response = requests.post(
        HAL_API_URL,
        headers=headers,
        data=xml_content
    )
    
    if response.status_code == 201:
        print("✅ Métadonnées déposées avec succès")
        print(f"📄 Réponse HAL : {response.text}")
        return response.headers.get("Location")
    else:
        print(f"❌ Erreur {response.status_code}")
        print(response.text)
        return None

# ============================================
# UPLOAD DU FICHIER ZIP
# ============================================

def upload_package(entry_url):
    """Upload le fichier ZIP vers l'entrée HAL"""
    if not entry_url:
        print("❌ Pas d'URL d'entrée, abandon")
        return
    
    print(f"📦 Upload du fichier ZIP vers {entry_url}...")
    
    headers = get_auth_header()
    headers["Content-Type"] = "application/zip"
    headers["Content-Disposition"] = f'attachment; filename="{ZIP_FILE}"'
    
    with open(ZIP_FILE, "rb") as f:
        zip_content = f.read()
    
    headers["Content-Length"] = str(len(zip_content))
    
    # URL de dépôt du contenu (media-resource)
    content_url = entry_url + "/edit-media"
    
    response = requests.post(
        content_url,
        headers=headers,
        data=zip_content
    )
    
    if response.status_code in [200, 201]:
        print("✅ Fichier ZIP uploadé avec succès")
        print(f"📄 Réponse HAL : {response.text}")
    else:
        print(f"❌ Erreur {response.status_code}")
        print(response.text)

# ============================================
# FLUX PRINCIPAL
# ============================================

def main():
    print("=" * 60)
    print("DÉPÔT AUTOMATIQUE HAL - AL-MIZAN")
    print("=" * 60)
    
    # Vérifier que les fichiers existent
    if not Path(XML_FILE).exists():
        print(f"❌ Fichier {XML_FILE} introuvable")
        return
    
    if not Path(ZIP_FILE).exists():
        print(f"❌ Fichier {ZIP_FILE} introuvable")
        return
    
    print(f"✓ Fichier XML : {XML_FILE} ({Path(XML_FILE).stat().st_size} bytes)")
    print(f"✓ Fichier ZIP : {ZIP_FILE} ({Path(ZIP_FILE).stat().st_size / 1e9:.2f} GB)")
    print()
    
    # Étape 1 : Déposer les métadonnées
    entry_url = deposit_metadata()
    
    if entry_url:
        print()
        # Étape 2 : Upload du fichier
        upload_package(entry_url)
    
    print()
    print("=" * 60)
    print("DÉPÔT TERMINÉ")
    print("=" * 60)
    print()
    print("📋 Prochaines étapes :")
    print("1. Connectez-vous à https://hal.science/")
    print("2. Vérifiez votre dépôt dans 'Mes documents'")
    print("3. Attendez la validation HAL (24-48h)")
    print()

if __name__ == "__main__":
    main()
```

**Utilisation :**

```bash
# 1. Installez les dépendances
pip install requests

# 2. Éditez le script avec vos credentials HAL
# HAL_USERNAME = "votre_email"
# HAL_PASSWORD = "votre_mot_de_passe"

# 3. Lancez le dépôt
python depot_hal_sword.py
```

**⚠️ Sécurité :**
- Ne jamais committer vos credentials HAL dans Git
- Utilisez des variables d'environnement si possible :
  ```python
  import os
  HAL_USERNAME = os.getenv("HAL_USERNAME")
  HAL_PASSWORD = os.getenv("HAL_PASSWORD")
  ```

---

## 📋 Structure du fichier XML

Le fichier `HAL_DEPOSIT.xml` contient les sections suivantes :

| Section | Balises XML | Contenu |
|---------|-------------|---------|
| **Titres** | `<title>` | Titre FR et EN |
| **Auteurs** | `<author>` | EL BAHLOUL + Devin (IA) |
| **Résumés** | `<summary>` | Résumé FR et EN |
| **Mots-clés** | `<category>` | 10 mots-clés FR + 10 EN |
| **Domaines** | `<hal:domain>` | Informatique, Maths, Physique |
| **Identifiants** | `<id>`, `<link>` | GitHub URL, DOI Zenodo |
| **Dates** | `<published>`, `<updated>` | 7 novembre 2026 |
| **Type** | `<dcterms:type>` | Software / LOGICIEL |
| **Version** | `<dcterms:hasVersion>` | 1.0.0 |
| **Langues** | `<dcterms:language>` | FR, EN |
| **Licence** | `<rights>`, `<dcterms:license>` | AGPL-3.0 |
| **Déclaration IA** | `<hal:ai-assistance>`, `<hal:ai-disclosure>` | Obligatoire |
| **Relations** | `<dcterms:isVersionOf>`, `<dcterms:relation>` | DOI Zenodo liés |
| **Formats** | `<dcterms:format>` | ZIP, Markdown, BibTeX |
| **Références** | `<dcterms:references>` | Bibliographie (Turing, Steane, etc.) |

---

## ✅ Vérification avant dépôt

Avant de soumettre, vérifiez :

- [ ] Titre FR et EN corrects
- [ ] Auteurs complets (EL BAHLOUL + mention IA)
- [ ] Résumés FR et EN présents
- [ ] Mots-clés pertinents (10 FR + 10 EN)
- [ ] Domaines scientifiques sélectionnés
- [ ] Licence AGPL-3.0 spécifiée
- [ ] **Déclaration IA présente** (obligatoire)
- [ ] DOI Zenodo mentionné (10.5281/zenodo.24028243)
- [ ] URL GitHub correcte
- [ ] Fichier ZIP prêt (~1.6 GB)

---

## 🔗 Liens utiles

- **HAL :** https://hal.science/
- **API HAL SWORD :** https://api.archives-ouvertes.fr/docs/sword/
- **Documentation SWORD :** http://swordapp.org/
- **Schéma XML HAL :** https://www.archives-ouvertes.fr/hal-00385423/document
- **Dépôt GitHub :** https://github.com/IMAM8MAHDI/AL-MIZAN-Quantum-Emulator
- **DOI Zenodo :** https://doi.org/10.5281/zenodo.24028243

---

## 📞 Support

**Problèmes techniques :**
- HAL Support : hal@inist.fr
- Documentation : https://www.ccsemi.fr/fr/aide

**API SWORD :**
- Documentation : https://api.archives-ouvertes.fr/docs/sword/
- Exemples : https://github.com/CCSDForge/hal-sword-examples

---

**Prêt à déposer ?** 

➡️ **Méthode recommandée :** Utilisez le XML comme référence pour le dépôt manuel sur https://hal.science/

➡️ **Méthode avancée :** Utilisez le script Python avec vos credentials HAL
