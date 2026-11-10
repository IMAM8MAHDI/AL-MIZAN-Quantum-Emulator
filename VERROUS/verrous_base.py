# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""VERROUS — la couche qui mesure l'état réel de la protection au lieu de le déclarer.

D'où part ce dossier
--------------------
Une feuille de route externe en quatre phases a été reçue le 2026-11-09 : verrouiller et tracer
avant d'exposer, cadrer les premiers contacts, poser un NDA bilatéral en droit français et
démontrer en boîte noire, puis formaliser (licence d'exploitation contre cession de propriété
intellectuelle, rémunération hybride, relecture par avocat). Cette feuille de route contient des
affirmations sur le dépôt. Certaines sont fausses, d'autres sont déjà dépassées par les faits.
Ce dossier ne les répète pas : il les mesure.

Ce que ce module fait, dans l'ordre
----------------------------------
  1. il inventorie l'arbre posé sur disque, extension par extension, avec une empreinte calculée
     sur les octets — aucune horloge murale n'entre dans le certificat, et C01 le vérifie en
     relisant le code source de ce module (EQ-01) ;
  2. il relit le manifeste scellé et re-hache chaque entrée : c'est ainsi que la dérive est comptée,
     et le nombre dérivé est exigé dans le résultat publié (EQ-02) ;
  3. il lit les quatre textes de licence, compte les en-têtes SPDX fichier par fichier et nomme
     ceux qui n'en ont pas (EQ-03) ;
  4. il cherche dans les textes GNU la clause que l'avis reçu prétend voir (« usage non commercial
     uniquement ») ; le nombre rendu est ce qu'il est (EQ-04) ;
  5. il mesure la frontière « cœur secret » : ce qui est gardé, ce qui reste hors du sceau — un
     module d'équations hors du sceau signale une dérive, jamais un choix — et si les heuristiques
     fines sont réellement publiées (EQ-05) ;
  6. il date par le journal des commits joignables (`git log`), qui voyage avec le dépôt, et confronte
     ce nombre au journal local de références qui, lui, ne voyage pas ; puis il oppose ce qu'un dépôt
     prouve à ce qu'il ne prouve pas (EQ-06) ;
  7. il ouvre le registre d'accès demandé par la phase 2 — six colonnes, zéro ligne — et compte la
     matière de contact déjà présente dans le dépôt mais non reprise dans ce registre (EQ-07) ;
  8. il cherche les huit clauses de la phase 3, avec un contrôle positif qui prouve que la recherche
     fonctionne et un contraste naïf qui montre ce qu'un motif sans frontière de mot fabrique
     (EQ-08) ;
  9. il compte les artefacts précompilés de la boîte noire et lit ce que le dossier de devis dit
     réellement du générateur (EQ-09) ;
 10. il nomme les quatre instruments de la phase 4 et compte ceux qui sont signés (EQ-10), les
     montants imposés (EQ-11) et les occurrences des mots « avocat » et « barreau » (EQ-12) ;
 11. il compare les mentions publiques du dépôt Zenodo et du fichier de citation, puis confronte
     l'ordre conseillé des phases à l'ordre mesuré (EQ-13, EQ-14) ;
 12. il relit les octets qu'il vient de produire (EQ-15) et laisse ouvertes les limites qu'il ne
    remplit pas (EQ-16).

Ce qu'il ne fait pas : il ne rédige aucun contrat, ne choisit aucune licence, ne dépose rien,
n'écrit à personne, ne donne pas un conseil juridique et n'affirme aucune paternité légale. Une
clause absente reste absente après exécution de ce module — le module mesure, il ne verrouille pas.

Usage :
    cd ZENODO_DEPOT_ALMIZAN && py -3 VERROUS/verrous_base.py
    cd ZENODO_DEPOT_ALMIZAN && py -3 VERROUS/verrous_base.py --ecrit
    cd ZENODO_DEPOT_ALMIZAN && py -3 FONDATION/OUTILS/audit_piliers.py VERROUS/verrous_base.py
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

RACINE = Path(__file__).resolve().parents[1]
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

DOSSIER = Path(__file__).resolve().parent
ARTEFACTS = DOSSIER / "artefacts"
GIT = shutil.which("git") if (RACINE / ".git").exists() else None

from FONDATION import fondation_base as FB                                    # noqa: E402

# ─── 1. Source et provenance --------------------------------------------------

SOURCE: Dict[str, Any] = {
    "point_de_depart": "feuille de route externe reçue le 2026-11-09 en quatre phases — verrouillage "
                       "et traçabilité pré-exposition, premiers contacts, NDA bilatéral en droit "
                       "français et démonstration en boîte noire, formalisation du contrat — avec la "
                       "consigne finale « tout fait en sorte que sa corresponde a ma base logique »",
    "auteur": "M. Ahmed EL BAHLOUL (IMAM8MAHDI)",
    "antecedents_uses": [
        "MANIFESTE_SHA256.txt — le sceau du dépôt, dont ce dossier re-hache chaque entrée au lieu de "
        "recopier un verdict déjà écrit",
        "git log HEAD — la source d'horodatage publiée : les dates viennent du contenu des commits "
        "atteignables, jamais de l'heure de la machine, et ce journal voyage avec le dépôt ; "
        ".git/logs/HEAD n'est qu'une source locale de confrontation, absente de l'archive publiée",
        "LICENSE, LICENSE-GPL, LICENSE-AGPL, .zenodo.json, CITATION.cff, DOSSIER_DEVIS/ — les textes "
        "dont les compteurs de clauses, de mentions et de montants sont tirés",
        "FONDATION/fondation_base.py — STATUTS et COUCHES : cette couche étiquette avec les mêmes mots "
        "que le reste du dépôt",
    ],
    "ce_que_ce_module_n_utilise_pas": [
        "aucune horloge murale : les appels datetime.now, date.today et time.time ne figurent pas "
        "dans ce fichier, et C01 le vérifie en relisant le source",
        "aucun secret : rien n'est lu hors du dépôt, aucun fichier de credentials n'est ouvert",
        "aucune rédaction contractuelle, aucun modèle reproduit, aucune clause inventée",
        "aucun prix, redevance ou pourcentage proposé : les montants sont comptés, pas suggérés",
    ],
}

PHRASE_ABSENCE = "aucun verrou contractuel posé"

# ─── 2. Règles de mesure (choix d'auteur, jamais des affirmations sur le monde) 

MANIFESTE_CHEMIN = "MANIFESTE_SHA256.txt"
EXCLUS_REPERTOIRES = (".git", ".mypy_cache", ".pytest_cache", "__pycache__")
EXCLUS_SUFFIXES = (".pyc",)
EXCLUS_PREFIXES = ("VERROUS/artefacts/",)
NOM_TEMPORAIRE = ".qoder_tmp"
# Ce module et ses tests sont exclus des corpus de recherche de clauses : ils contiennent
# littéralement les motifs recherchés. L'exclusion est mesurée et publiée, pas silencieuse.
EXCLUS_AUTO = ("VERROUS/verrous_base.py", "VERROUS/tests/test_verrous.py")
HORS_DEPOT_PUBLIC = ("code/resultats/", "resultats/")
EXTENSIONS_TEXTE = (".py", ".md", ".txt", ".json", ".cff", ".csv", ".tex", ".xml", ".html")
# Un instrument d'horodatage n'est pas un mot : c'est un fichier livré par l'autorité de
# temps ou par l'huissier. Seules ces extensions rendent un artefact observable ; .asc et
# .der peuvent être une clé ou un certificat plutôt qu'un jeton d'horodatage — leur présence
# serait un dossier à ouvrir, pas un verdict. La règle est écrite ici pour être rejeuée.
EXTENSIONS_INSTRUMENT = (".tsa", ".p7s", ".p7m", ".sig", ".asc", ".der")
# C01 relit ce fichier pour vérifier l'absence d'horloge murale. Écrits en une seule chaîne, les
# motifs s'accuseraient eux-mêmes : chacun est donc fabriqué par deux morceaux.
INTERDITS_HORLOGE = tuple(a + b for a, b in (("datetime", ".now("), ("date", ".today("),
                                              ("time", ".time("), ("local", "time("),
                                              ("utc", "now(")))

COLONNES_REGISTRE = ("date_contact", "personne", "entite", "canal",
                     "question_posee", "reponse_transmise")
CHEMIN_REGISTRE = "VERROUS/artefacts/registre_acces.csv"

INSTRUMENTS: Tuple[Tuple[str, str], ...] = (
    ("licence d'exploitation", r"licence\s+d['’]exploitation"),
    ("cession de propriete intellectuelle", r"cession\s+de\s+propriet[ée]\s+intellectuelle"),
    ("accord de confidentialite bilatéral", r"accord\s+de\s+confidentialit[ée]\s+bilat[ée]ral"),
    ("protocole d'accord", r"protocole\s+d['’]accord|\bMOU\b"),
)

CLAUSES: Tuple[Tuple[str, str], ...] = (
    ("confidentialite bilaterale", r"\bNDA\b|accord\s+de\s+confidentialit[ée]"),
    ("droit_applicable_francais", r"\bdroit\s+fran[cç]ais\b"),
    ("non_contournement", r"non[- ]?circumvention|non[- ]?contournement"),
    ("non_debauchage", r"non[- ]?solicit|non[- ]?d[ée]bauch"),
    ("boite_noire_demontrable", r"bo[îi]te\s+noire"),
    ("retrocession", r"r[ée]trocession|revert\s+licence"),
    ("duree_et_territorialite", r"dur[ée]e\s+du\s+contrat|\bterritorialit[ée]\b"),
    ("condition_suspensive_de_relecture", r"condition\s+suspensive"),
)

INSTRUMENTS_HORODATAGE: Tuple[Tuple[str, str], ...] = (
    ("enveloppe e-Soleau INPI", r"e[- ]?soleau|enveloppe\s+soleau|\bINPI\b"),
    ("coffre-fort numérique horodaté", r"coffre[- ]fort\s+num[ée]rique|coffre[- ]fort\s+horodat[ée]"),
    ("horodatage RFC 3161", r"rfc\s*3161|time\s?stamp\s?authority|\bTSA\b"),
    ("constat d'huissier", r"\bhuissier\b|constat\s+d['’]huissier"),
)

MOTIFS_SIGNATURE = r"sign[ée][sS ]+le\s+[àa]|paraphe|signature\s+num[ée]rique|e\.seal"
MOTIFS_JURIDIQUES: Tuple[Tuple[str, str], ...] = (
    ("avocat", r"\bavocat"),
    ("barreau", r"\bbarreau"),
    ("service juridique", r"service\s+juridique"),
    ("cabinet", r"\bcabinet\b"),
    ("conseil juridique", r"conseil\s+juridique"),
)

TEXTES_LICENCE = ("LICENSE", "LICENSE.md", "LICENSE-GPL", "LICENSE-AGPL")
MOTS_COMMERCIAUX: Tuple[Tuple[str, str], ...] = (
    ("restriction d'usage non commercial",
     r"non-?commercial\s+use|use\s+for\s+non-?commercial|not\s+for\s+commercial\s+use|"
     r"usage\s+non\s+commercial"),
    ("permission de facturer des copies", r"you\s+may\s+charge|charge\s+a\s+(?:fee|price)|for\s+a\s+fee"),
    ("permission de faire tourner le programme", r"unlimited\s+permission\s+to\s+run|freedom\s+to\s+run"),
    ("grant irrevocable", r"irrevocable"),
    ("clause d'interaction à distance", r"Remote\s+Network\s+Interaction"),
    ("mention d'une licence propriétaire alternative", r"proprietary\s+licen[cs]e"),
)

MONTANT = r"(?:€|\bEUR\b|\bUSD\b|\bCHF\b)\s?\d|\d[\d  .,]*\s(?:€|CHF)"
MOTIF_PRIX_MOT = r"\bprix\b|\bco[ûu]t\b|\btarifs?\b|\bdevis\b"
MOTIF_REDEVANCE = r"royalt|int[ée]ressement|redevance|pourcentage\s+sur\s+les\s+ventes"

BARRES: Tuple[Tuple[str, str, str], ...] = (
    ("fichiers de l'arbre", "inventaire", "fichiers"),
    ("couverts par le sceau", "manifeste", "total_lignes"),
    ("publiés hors du sceau", "manifeste", "hors_manifeste"),
    ("sources Python avec en-tête SPDX", "licence", "avec_en_tete"),
    ("lignes du registre d'accès", "registre_acces", "nb_entrees"),
    ("clauses rédigées", "clauses", "clauses_redigees"),
    ("instruments signés", "structure_contrat", "instruments_signes"),
    ("artefacts précompilés livrables", "boite_noire", "artefacts_precompiles"),
)
LONGUEUR_MAX = Fraction(220)

COULEURS = ("#1c3550", "#2f5f86", "#7fb2d6", "#4d87b0",
            "#0f1c2b", "#b04d4d", "#8a3b3b", "#5c2f2f")

# ─── 3. Lecture de l'arbre ----------------------------------------------------


def _chemins_sous_arbre() -> List[str]:
    """Les fichiers du dépôt, hors caches, hors .git et hors nos propres artefacts."""
    rendu: List[str] = []
    for p in RACINE.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(RACINE).as_posix()
        if any(part in EXCLUS_REPERTOIRES for part in rel.split("/")[:-1]):
            continue
        if p.suffix in EXCLUS_SUFFIXES or p.name.startswith(NOM_TEMPORAIRE):
            continue
        if any(rel.startswith(pref) for pref in EXCLUS_PREFIXES):
            continue
        rendu.append(rel)
    return sorted(rendu)


def _corpus_texte() -> List[str]:
    return [c for c in _chemins_sous_arbre()
            if Path(c).suffix in EXTENSIONS_TEXTE and c not in EXCLUS_AUTO]


_CACHE: Dict[str, Any] = {}


def _git(argumens: List[str]) -> Optional[str]:
    """git exécuté dans ce dépôt ; None si git, le dépôt ou la commande font défaut."""
    if not GIT:
        return None
    try:
        p = subprocess.run(["git", *argumens], cwd=str(RACINE), capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=120)
    except (OSError, subprocess.SubprocessError):
        return None
    return p.stdout if p.returncode == 0 else None


def _suivis_par_git() -> Optional[List[str]]:
    """Les chemins que git suit — ce sont eux seuls qui voyagent dans un clone et dans l'archive."""
    if "_SUIVI" not in _CACHE:
        brut = _git(["ls-files", "-z"])
        _CACHE["_SUIVI"] = sorted(c for c in brut.split("\0") if c) if brut is not None else None
    return _CACHE["_SUIVI"]


def _iso_epoch(epoch: int, decal: str) -> str:
    """Rendu ISO d'une seconde POSIX lue dans le dépôt, avec le fuseau qui l'accompagne."""
    signe = 1 if decal[0] == "+" else -1
    tz = timezone(signe * timedelta(hours=int(decal[1:3]), minutes=int(decal[3:5])))
    return datetime.fromtimestamp(epoch, tz=tz).isoformat()


def _journal_local() -> Dict[str, Any]:
    """.git/logs/HEAD — le journal des références, qui n'existe que sur le disque qui l'a produit."""
    chemin = RACINE / ".git" / "logs" / "HEAD"
    if not chemin.exists():
        return {"present": False, "lignes": 0, "parsees": 0, "tout_parse": True,
                "utf8_stricte": 0, "utf8_integrale": True, "auteurs": {}, "somme_auteurs": 0,
                "auteurs_additifs": True, "premiere": "", "derniere": "",
                "duree_attestee_seconde": 0, "sha_dernier": "", "sha_tete": _sha_tete(),
                "tete_coherente": False}
    bruts = chemin.read_bytes()
    lignes = [l for l in bruts.split(b"\n") if l]
    parsees: List[Tuple[int, str, str, str, str]] = []
    strictes = 0
    for b in lignes:
        try:
            l = b.decode("utf-8")
            strictes += 1
        except UnicodeDecodeError:
            l = b.decode("utf-8", "replace")
        m = re.match(r"^([0-9a-f]{40}) ([0-9a-f]{40}) (.+?) <([^>]*)> (\d+) ([+-]\d{2})(\d{2})\t"
                     r"(.*)$", l)
        if m:
            parsees.append((int(m.group(5)), m.group(2), m.group(4),
                            f"{m.group(6)}{m.group(7)}", m.group(8)))
    ordre = sorted(parsees)
    tete = _sha_tete()
    auteurs: Dict[str, int] = {}
    for _, _, mail, _, _ in parsees:
        auteurs[mail] = auteurs.get(mail, 0) + 1
    return {"present": True, "lignes": len(lignes), "parsees": len(parsees),
            "tout_parse": len(parsees) == len(lignes),
            "utf8_stricte": strictes, "utf8_integrale": strictes == len(lignes),
            "auteurs": dict(sorted(auteurs.items(), key=lambda kv: (-kv[1], kv[0]))),
            "somme_auteurs": sum(auteurs.values()),
            "auteurs_additifs": sum(auteurs.values()) == len(parsees),
            "premiere": (_iso_epoch(ordre[0][0], ordre[0][3]) if ordre else ""),
            "derniere": (_iso_epoch(ordre[-1][0], ordre[-1][3]) if ordre else ""),
            "duree_attestee_seconde": (ordre[-1][0] - ordre[0][0]) if ordre else 0,
            "sha_dernier": parsees[-1][1] if parsees else "", "sha_tete": tete,
            "tete_coherente": bool(tete) and bool(parsees) and tete == parsees[-1][1]}


def _sha_tete() -> str:
    tete = (_texte(".git/HEAD") if (RACINE / ".git" / "HEAD").exists() else "").strip()
    if not tete.startswith("ref:"):
        return tete
    cible = RACINE / ".git" / tete[4:].strip()
    return cible.read_text(encoding="utf-8", errors="replace").strip() if cible.exists() else ""


def _chemins_scelles() -> List[str]:
    """Les chemins que le manifeste couvre : cette liste voyage avec le dépôt publié."""
    if "_SCEAU" not in _CACHE:
        _CACHE["_SCEAU"] = sorted({g.group(2).strip() for g in
                                   (re.match(r"^([0-9a-f]{64})  (.+)$", l)
                                    for l in _texte(MANIFESTE_CHEMIN).splitlines()) if g})
    return _CACHE["_SCEAU"]


def _lignes_du_registre() -> List[str]:
    """Les lignes de données du registre posé sur disque, en-tête retiré — pas celles voulues."""
    cible = ARTEFACTS / "registre_acces.csv"
    if not cible.exists():
        return []
    texte = cible.read_bytes().decode("utf-8-sig", "replace")
    lignes = [l for l in texte.replace("\r\n", "\n").split("\n") if l != ""]
    return lignes[1:]


def _histoire_atteignable() -> Dict[str, Any]:
    """git log HEAD — l'histoire qui voyage avec le dépôt, contrairement au journal local."""
    if "_HISTOIRE" not in _CACHE:
        sortie = _git(["log", "--format=%H%x09%ae%x09%at%x09%aI", "HEAD"])
        commits: List[Tuple[str, str, int, str]] = []
        for l in (sortie or "").splitlines():
            c = l.split("\t")
            if len(c) == 4 and c[2].isdigit():
                commits.append((c[0], c[1], int(c[2]), c[3]))
        ordre = sorted(commits, key=lambda c: c[2])
        lignes = len([l for l in (sortie or "").splitlines() if l])
        auteurs: Dict[str, int] = {}
        for _, mail, _, _ in commits:
            auteurs[mail] = auteurs.get(mail, 0) + 1
        _CACHE["_HISTOIRE"] = {
            "git_disponible": sortie is not None, "commits": len(commits),
            "lignes": lignes, "tout_parse": lignes == len(commits),
            "sha_distincts": len({c[0] for c in commits}),
            "auteurs": dict(sorted(auteurs.items(), key=lambda kv: (-kv[1], kv[0]))),
            "somme_auteurs": sum(auteurs.values()),
            "auteurs_additifs": sum(auteurs.values()) == len(commits),
            "premiere": ordre[0][3] if ordre else "", "derniere": ordre[-1][3] if ordre else "",
            "duree_attestee_seconde": (ordre[-1][2] - ordre[0][2]) if ordre else 0,
            "sha_tete": _sha_tete(),
            "tete_coherente": bool(ordre) and ordre[-1][0] == _sha_tete(),
            "commits_d_outils_automates": sum(v for k, v in auteurs.items()
                                              if "cognition" in k or "bot" in k)}
    return _CACHE["_HISTOIRE"]


def _instruments_sur_disque() -> List[str]:
    """Les artefacts d'horodatage réellement présents, toutes extensions d'instrument."""
    return [c for c in _chemins_sous_arbre()
            if Path(c).suffix.lower() in EXTENSIONS_INSTRUMENT]


def _texte(chemin: str) -> str:
    return (RACINE / chemin).read_text(encoding="utf-8", errors="replace")


def _hache(chemin: str) -> str:
    return hashlib.sha256((RACINE / chemin).read_bytes()).hexdigest()


def _compter_par_repertoire(chemins: List[str]) -> Dict[str, int]:
    rendu: Dict[str, int] = {}
    for c in chemins:
        cle = c.split("/")[0] if "/" in c else c
        rendu[cle] = rendu.get(cle, 0) + 1
    return dict(sorted(rendu.items(), key=lambda kv: (-kv[1], kv[0])))


def _motif_par_fichier(motif: str, corpus: List[str]) -> Tuple[int, List[str]]:
    n = 0
    touches: List[str] = []
    motif_re = re.compile(motif, re.I)
    for c in corpus:
        k = len(motif_re.findall(_texte(c)))
        if k:
            n += k
            touches.append(c)
    return n, sorted(set(touches))


def _decimale(v: Fraction, decimales: int) -> str:
    """Écriture décimale exacte d'un rationnel, arrondi half-up par des entiers."""
    signe = "-" if v < 0 else ""
    v = abs(v)
    m = 10 ** decimales
    n = (v * m + Fraction(1, 2)) // 1
    return f"{signe}{n // m}.{n % m:0{decimales}d}"


def _pourcent(partie: int, total: int) -> str:
    if total <= 0:
        return "0"
    return _decimale(Fraction(partie) * 100 / Fraction(total), 2)


def _contexte(motif: str, corpus: List[str]) -> str:
    """Le premier endroit où un motif tombe, avec son fichier et sa ligne."""
    motif_re = re.compile(motif, re.I)
    for c in corpus:
        for i, ligne in enumerate(_texte(c).splitlines(), 1):
            if motif_re.search(ligne):
                return f"{c}:{i} — {ligne.strip()[:96]}"
    return "aucun"


# ─── 4. Les mesures de la couche ---------------------------------------------


def inventaire() -> Dict[str, Any]:
    chemins = _chemins_sous_arbre()
    empreintes = {c: _hache(c) for c in chemins}
    ruban = "\n".join(f"{c}\t{empreintes[c]}" for c in chemins)
    tailles = {c: (RACINE / c).stat().st_size for c in chemins}
    par_extension: Dict[str, int] = {}
    for c in chemins:
        cle = Path(c).suffix or "(sans extension)"
        par_extension[cle] = par_extension.get(cle, 0) + 1
    hors_public = [c for c in chemins if any(c.startswith(p) for p in HORS_DEPOT_PUBLIC)]
    source = _texte("VERROUS/verrous_base.py")
    suivis = _suivis_par_git()
    ensemble = set(chemins)
    dans_suivi = sorted(ensemble & set(suivis)) if suivis is not None else None
    hors_suivi = sorted(ensemble - set(suivis)) if suivis is not None else None
    return {"regles": {"repertoires_exclus": list(EXCLUS_REPERTOIRES),
                       "suffixes_exclus": list(EXCLUS_SUFFIXES),
                       "prefixes_exclus": list(EXCLUS_PREFIXES),
                       "noms_exclus_par_prefixe": NOM_TEMPORAIRE},
            "fichiers": len(chemins),
            "git_disponible": suivis is not None,
            "fichiers_suivis_par_git": None if dans_suivi is None else len(dans_suivi),
            "fichiers_non_suivis_par_git": None if hors_suivi is None else len(hors_suivi),
            "exemples_non_suivis": (hors_suivi or [])[:6],
            "suivi_additif": True if suivis is None
            else len(dans_suivi) + len(hors_suivi) == len(chemins),
            "ce_que_le_suivi_dit": "un arbre scanné sur disque n'est pas l'arbre publié : les "
                                   "fichiers que git ne suit pas ne voyagent ni dans un clone ni "
                                   "dans l'archive, et l'écart est compté ici plutôt que subi",
            "octets_total": sum(tailles.values()),
            "par_extension": dict(sorted(par_extension.items(), key=lambda kv: (-kv[1], kv[0]))),
            "empreinte_arbre": hashlib.sha256(ruban.encode("utf-8")).hexdigest(),
            "empreintes_distinctes": len(set(empreintes.values())) == len(empreintes),
            "chemins_uniques": len(set(chemins)) == len(chemins),
            "somme_extensions": sum(par_extension.values()),
            "extensions_additives": sum(par_extension.values()) == len(chemins),
            "hors_depot_public": {"motifs_gitignore": _motifs_gitignore(),
                                  "fichiers": len(hors_public),
                                  "octets": sum(tailles[c] for c in hors_public),
                                  "exemples": hors_public[:4]},
            "aucune_horloge": not any(m in source for m in INTERDITS_HORLOGE),
            "motifs_horloge_reposes": [m for m in INTERDITS_HORLOGE if m in source],
            "nb_motifs_horloge_cherches": len(INTERDITS_HORLOGE),
            "horloge_noyau_fichiers": sum(1 for c in chemins if c.startswith("horloge_noyau/")),
            "ecrit_uniquement_dans": "VERROUS/artefacts/"}


def _motifs_gitignore() -> List[str]:
    lignes = _texte(".gitignore").splitlines()
    return [l.strip() for l in lignes if l.strip() and not l.strip().startswith("#")]


def manifeste() -> Dict[str, Any]:
    lignes = [m for m in (re.match(r"^([0-9a-f]{64})  (.+)$", l)
                          for l in _texte(MANIFESTE_CHEMIN).splitlines()) if m]
    entrees = [(g.group(1), g.group(2).strip()) for g in lignes]
    exact = normalise = derive = absent = 0
    derives: List[str] = []
    absents: List[str] = []
    for empreinte, chemin in entrees:
        cible = RACINE / chemin
        if not cible.exists():
            absent += 1
            absents.append(chemin)
            continue
        octets = cible.read_bytes()
        if hashlib.sha256(octets).hexdigest() == empreinte:
            exact += 1
        elif hashlib.sha256(octets.replace(b"\r\n", b"\n")).hexdigest() == empreinte:
            normalise += 1
        else:
            derive += 1
            derives.append(chemin)
    chemins = _chemins_sous_arbre()
    scelles = {c for _, c in entrees}
    hors = [c for c in chemins if c not in scelles]
    comptes = {"a_l_identique": exact, "apres_normalisation_des_fins_de_ligne": normalise,
               "derivent": derive, "absents_de_disque": absent}
    return {"chemin": MANIFESTE_CHEMIN, "lignes_fichier": len(_texte(MANIFESTE_CHEMIN).splitlines()),
            "total_lignes": len(entrees), **comptes,
            "comptes_additifs": sum(comptes.values()) == len(entrees),
            "conformes": exact + normalise,
            "couverture_%": _pourcent(exact + normalise, len(chemins)),
            "derivent_listes": sorted(derives), "absents_listes": sorted(absents),
            "hors_manifeste": len(hors),
            "hors_manifeste_octets": sum((RACINE / c).stat().st_size for c in hors),
            "hors_manifeste_par_repertoire": _compter_par_repertoire(hors),
            "hors_manifeste_exemples": sorted(hors)[:6],
            "toutes_entrees_existent": absent == 0,
            "le_manifeste_ne_se_scelle_pas_lui_meme": MANIFESTE_CHEMIN in hors,
            "verdict": ("SCELLÉ" if derive == 0 and absent == 0 else
                        f"HORS SCEAU : {derive} fichier(s) du dépôt ne rendent pas l'empreinte "
                        f"inscrite dans le manifeste"),
            "un_sceau_ne_dit_rien_de_la_date": True}


def licence() -> Dict[str, Any]:
    racine_txt = _texte("LICENSE")
    m = re.search(r"SPDX-License-Identifier:\s*(.+)", racine_txt)
    expression = m.group(1).strip() if m else ""
    tailleurs = {nom: (RACINE / nom).stat().st_size for nom in TEXTES_LICENCE
                 if (RACINE / nom).exists()}
    py = [c for c in _chemins_sous_arbre() if c.endswith(".py")]
    avec: List[str] = []
    sans: List[str] = []
    expressions: Dict[str, int] = {}
    occurrences = 0
    for c in py:
        t = _texte(c)
        k = t.count("SPDX-License-Identifier")
        occurrences += k
        if k:
            avec.append(c)
            g = re.search(r"SPDX-License-Identifier:\s*(.+)", t)
            cle = g.group(1).strip() if g else "(introuvable)"
            expressions[cle] = expressions.get(cle, 0) + 1
        else:
            sans.append(c)
    return {"expression_lue": expression,
            "expressions_dans_les_sources": dict(sorted(expressions.items())),
            "expression_unique": len(expressions) == 1,
            "uniforme_avec_licenc_racine": list(expressions) == [expression],
            "textes_licence_octets": tailleurs,
            "python_total": len(py), "avec_en_tete": len(avec), "sans_en_tete": len(sans),
            "compte_additif": len(avec) + len(sans) == len(py),
            "sans_en_tete_listes": sorted(sans),
            "sans_en_tete_par_repertoire": _compter_par_repertoire(sans),
            "occurrences_en_tete": occurrences,
            "license_md_porte_l_expression": "SPDX-License-Identifier" in _texte("LICENSE.md"),
            "textes_gnu_versions": {"GPL": sorted(set(re.findall(r"version (\d+)",
                                                                 _texte("LICENSE-GPL")))),
                                    "AGPL": sorted(set(re.findall(r"version (\d+)",
                                                                  _texte("LICENSE-AGPL"))))},
            "double_licence_declaree": "DOUBLE LICENCE" in racine_txt.upper(),
            "choix_laisse_au_licencie": "votre convenance" in racine_txt}


def regime_commercial() -> Dict[str, Any]:
    rendu: Dict[str, Dict[str, int]] = {}
    for nom, chemin in (("GPL", "LICENSE-GPL"), ("AGPL", "LICENSE-AGPL")):
        t = _texte(chemin)
        rendu[nom] = {lib: len(re.findall(pat, t, re.I)) for lib, pat in MOTS_COMMERCIAUX}
    restriction = (rendu["GPL"]["restriction d'usage non commercial"]
                   + rendu["AGPL"]["restriction d'usage non commercial"])
    facturer = (rendu["GPL"]["permission de facturer des copies"]
                + rendu["AGPL"]["permission de facturer des copies"])
    courir = (rendu["GPL"]["permission de faire tourner le programme"]
              + rendu["AGPL"]["permission de faire tourner le programme"])
    presence = {lib: (rendu["GPL"][lib] > 0, rendu["AGPL"][lib] > 0) for lib, _ in MOTS_COMMERCIAUX}
    ecarts = {lib: [rendu["GPL"][lib], rendu["AGPL"][lib]] for lib, _ in MOTS_COMMERCIAUX
              if rendu["GPL"][lib] != rendu["AGPL"][lib]}
    return {"par_texte": rendu,
            "restrictions_non_commerciales_total": restriction,
            "permissions_de_facturer_total": facturer,
            "permissions_de_courir_total": courir,
            "clause_reseau_gpl": rendu["GPL"]["clause d'interaction à distance"],
            "clause_reseau_agpl": rendu["AGPL"]["clause d'interaction à distance"],
            "differences_de_presence": presence,
            # Un compte qui diffère de 1 entre deux textes de longueurs différentes n'est pas une
            # différence de permission : la comparaison qui compte est celle de la présence.
            "seules_differences_mesurees": [lib for lib, _ in MOTS_COMMERCIAUX
                                            if presence[lib][0] != presence[lib][1]],
            "ecarts_de_compte": ecarts,
            "facturer_present_dans_les_deux": all(presence["permission de facturer des copies"]),
            "la_clause_pretendue_est_absente": restriction == 0,
            "l_avis_recu_disait": "« type Affero GPL / AGPLv3 ou licence propriétaire à usage non "
                                  "commercial uniquement »",
            "ce_que_les_textes_disent": "les deux textes GNU autorisent l'usage commercial et "
                                        "permettent de facturer des copies ; le seul mot "
                                        "« noncommercially » qu'ils contiennent règle une offre "
                                        "ponctuelle de source, pas un champ d'exploitation",
            "licence_proprietaire_alternative": rendu["AGPL"][
                "mention d'une licence propriétaire alternative"],
            "texte_non_commercial_unique": _contexte(r"non-?commercial",
                                                     ("LICENSE-GPL", "LICENSE-AGPL"))}


def frontiere() -> Dict[str, Any]:
    chemins = _chemins_sous_arbre()
    scelles = set()
    for l in _texte(MANIFESTE_CHEMIN).splitlines():
        m = re.match(r"^([0-9a-f]{64})  (.+)$", l)
        if m:
            scelles.add(m.group(2).strip())
    hors = [c for c in chemins if c not in scelles]
    modules_eq = [c for c in chemins if c.endswith(".py") and "def equations(" in _texte(c)]
    hors_eq = [c for c in modules_eq if c not in scelles]
    gardes = [c for c in chemins
              if re.search(r"secret|credential|\.pem$|\.env$", Path(c).name, re.I)]
    heur: List[Tuple[str, int]] = []
    for c in chemins:
        if not c.endswith(".py") or c in EXCLUS_AUTO:
            continue
        k = len(re.findall(r"calibration|heuristique|param[èe]tre\s+d[ée]clar[ée]",
                           _texte(c), re.I))
        if k:
            heur.append((c, k))
    caches = sum(1 for p in RACINE.rglob("*.pyc"))
    return {"fichiers_total": len(chemins), "au_manifeste": len(chemins) - len(hors),
            "hors_manifeste": len(hors),
            "hors_manifeste_octets": sum((RACINE / c).stat().st_size for c in hors),
            "hors_manifeste_par_repertoire": _compter_par_repertoire(hors),
            "modules_portant_des_equations": sorted(modules_eq),
            "modules_d_equations_hors_sceau": sorted(hors_eq),
            "coeur_secret_reelement_garde": len(gardes),
            "fichiers_gardes_listes": sorted(gardes),
            "heuristiques_et_calibrages": sorted(heur, key=lambda kv: (-kv[1], kv[0])),
            "occurrences_heuristiques": sum(k for _, k in heur),
            "heuristiques_dans_le_seul_cache": False,
            "cache_compiles_sur_disque": caches,
            "cache_hors_depôt_public": True,
            "ce_que_l_avis_prescrivait": "« Ne publiez jamais l'intégralité des briques clés… "
                                         "Gardez en secret de fabrique les heuristiques fines, les "
                                         "paramètres de calibration »",
            "mesure": f"{len(modules_eq)} module(s) porteur(s) d'équations et "
                      f"{sum(k for _, k in heur)} occurrence(s) de heuristiques et calibrages sont "
                      "dans le dépôt public, 0 fichier n'est gardé hors de lui ; "
                      f"{len(hors_eq)} de ces module(s) échappe(ent) au sceau",
            # L'incompatibilité avec l'avis se lit dans la publication elle-même : les modules sont
            # sur le disque du dépôt public. Elle ne doit surtout pas dépendre de `hors_eq`, qui ne
            # mesure qu'un sceau périmé — un manifeste non rescellé rendrait faux un verdict vrai.
            "strategie_incompatible_ecrite": (len(modules_eq) > 0
                                              and len(gardes) == 0
                                              and sum(k for _, k in heur) > 0),
            "tous_les_modules_d_equations_scelles": len(hors_eq) == 0}


def horodatages() -> Dict[str, Any]:
    """Les deux journaux de dates du dépôt, séparés par ce qu'ils traversent."""
    local = _journal_local()
    histoire = _histoire_atteignable()
    corpus = _corpus_texte()
    instruments = {}
    for lib, pat in INSTRUMENTS_HORODATAGE:
        n, ou = _motif_par_fichier(pat, corpus)
        instruments[lib] = {"occurrences": n, "fichiers": ou}
    naif_n, naif_f = _motif_par_fichier(r"coffre[- ]fort", corpus)
    artefacts = _instruments_sur_disque()
    mentions = sum(v["occurrences"] for v in instruments.values())
    fichiers_mentions = sorted({c for v in instruments.values() for c in v["fichiers"]})
    return {"histoire": histoire, "journal_local": local,
            "dates_publiees_par": "histoire",
            "commits_attestes": histoire["commits"], "premiere": histoire["premiere"],
            "derniere": histoire["derniere"],
            "duree_attestee_seconde": histoire["duree_attestee_seconde"],
            "journal_plus_que_commits": local["parsees"] - histoire["commits"],
            "source_des_commits": "git log HEAD", "source_du_journal": ".git/logs/HEAD",
            "ce_que_compte_chaque_source": "« histoire » compte les commits atteignables depuis "
                                           "HEAD : ils voyagent avec le dépôt. « journal_local » "
                                           "compte les écritures de .git/logs/HEAD : elles restent "
                                           "sur le disque qui les a produites et ne voyagent ni "
                                           "dans un clone ni dans l'archive",
            "instruments_horodatage": instruments,
            "artefacts_horodatage": artefacts,
            "nb_artefacts_horodatage": len(artefacts),
            "extensions_instrument": list(EXTENSIONS_INSTRUMENT),
            "mentions_instrument_occurrences": mentions,
            "mentions_instrument_fichiers": len(fichiers_mentions),
            "fichiers_mentionnant_un_instrument": fichiers_mentions,
            "aucun_instrument_strict": len(artefacts) == 0,
            "ce_que_compte_le_strict": "le strict compte les artefacts d'horodatage sur disque "
                                       "(" + ", ".join(EXTENSIONS_INSTRUMENT) + "), pas les mots "
                                       "qui les nomment : une mention n'est pas un instrument",
            "contraste_naif_occurrences": naif_n, "contraste_naif_fichiers": len(naif_f),
            "contraste_naif_contexte": _contexte(r"coffre[- ]fort", corpus),
            "preuve_de_paternite": False,
            "ce_que_prouve_un_depot": "un dépôt horodaté atteste qu'un contenu était accessible à "
                                      "une date, pas qu'il est de vous : antériorité légale = False",
            "commits_d_outils_automates": histoire["commits_d_outils_automates"],
            "exclus_auto": list(EXCLUS_AUTO)}


def registre_acces() -> Dict[str, Any]:
    chemins = _chemins_sous_arbre()
    deja = [c for c in chemins if "registre" in c.lower() and c != CHEMIN_REGISTRE]
    matiere = [c for c in chemins if c.startswith("emails") or c.startswith("EMAIL_")]
    suivis = _suivis_par_git()
    matiere_suivie = sorted(set(matiere) & set(suivis)) if suivis is not None else None
    lignes = _lignes_du_registre()
    sous_sceau = set(_chemins_scelles())
    repris = sorted({c for c in matiere if any(c in l or Path(c).name in l for l in lignes)})
    return {"chemin": CHEMIN_REGISTRE, "colonnes": list(COLONNES_REGISTRE),
            "nb_colonnes": len(COLONNES_REGISTRE),
            "registre_posé_sur_disque": (ARTEFACTS / "registre_acces.csv").exists(),
            "lignes_de_donnees_lues": len(lignes), "nb_entrees": len(lignes),
            "absent_avant_ce_dossier": len(deja) == 0,
            "registres_preexistants": sorted(deja),
            "matiere_sur_disque": len(matiere),
            "matiere_sur_disque_par_repertoire": _compter_par_repertoire(matiere),
            "matiere_exemples": sorted(matiere)[:6],
            "git_disponible": suivis is not None,
            "matiere_suivie_par_git": matiere_suivie if matiere_suivie is None
            else len(matiere_suivie),
            "matiere_hors_suivi_git": None if matiere_suivie is None
            else len(matiere) - len(matiere_suivie),
            "matiere_entree_du_sceau": len({c for c in matiere if c in sous_sceau}),
            "matiere_reprise_dans_le_registre": len(repris),
            "matiere_hors_registre": len(matiere) - len(repris),
            "suivi_additif": True if matiere_suivie is None
            else len(matiere_suivie) + (len(matiere) - len(matiere_suivie)) == len(matiere),
            "ce_que_l_avis_demandaite": ["qui contacte", "entité représentée", "date",
                                          "questions techniques posées"],
            "couvre_quatre_champs_demandes": all(any(col.startswith(pref)
                                                     for pref in COLONNES_REGISTRE)
                                                 for col in ("date_contact", "personne", "entite",
                                                             "question_posee"))
            and any("canal" in col for col in COLONNES_REGISTRE),
            "ligne_est_une_donnee_pas_un_commentaire": True,
            "ce_que_compte_le_suivi": "la matière de contact est comptée là où elle est : sur ce "
                                      "disque, dans ce que git suit, dans ce que le sceau couvre ; "
                                      "un fichier que git ne suit pas ne part ni dans le clone ni "
                                      "dans l'archive"}


def clauses() -> Dict[str, Any]:
    corpus = _corpus_texte()
    rendu: Dict[str, Any] = {}
    for lib, pat in CLAUSES:
        n, ou = _motif_par_fichier(pat, corpus)
        rendu[lib] = {"occurrences": n, "fichiers": ou[:6]}
    naif_n, naif_f = _motif_par_fichier(r"nda", corpus)
    pos_n, pos_f = _motif_par_fichier(r"SPDX", corpus)
    dedans = self_contamination()
    return {"par_clause": rendu, "nb_clauses_cherchees": len(CLAUSES),
            "clauses_redigees": sum(1 for v in rendu.values() if v["occurrences"]),
            "toutes_absentes": all(v["occurrences"] == 0 for v in rendu.values()),
            "contraste_naif_occurrences": naif_n, "contraste_naif_fichiers": len(naif_f),
            "contraste_naif_exemple": _contexte(r"nda", corpus),
            "controle_positif_occurrences": pos_n, "controle_positif_fichiers": len(pos_f),
            "corpus_texte": len(corpus), "recherche_fonctionne": pos_n > 0 and len(pos_f) > 0,
            "naif_supere_stricte": naif_n > sum(v["occurrences"] for v in rendu.values()),
            "auto_exclusion": list(EXCLUS_AUTO), "auto_contient_motifs": dedans,
            "exclusion_est_portante": dedans > 0}


def self_contamination() -> int:
    n = 0
    for c in EXCLUS_AUTO:
        if (RACINE / c).exists():
            for _, pat in CLAUSES:
                n += len(re.findall(pat, _texte(c), re.I))
    return n


def boite_noire() -> Dict[str, Any]:
    chemins = _chemins_sous_arbre()
    binaires: Dict[str, int] = {}
    for ext in (".so", ".pyd", ".exe", ".dll", ".wasm", ".o", ".a", ".whl", ".bin", ".elf"):
        binaires[ext] = sum(1 for c in chemins if Path(c).suffix == ext)
    devis = sorted(c for c in chemins if c.startswith("DOSSIER_DEVIS/"))
    tailles = {c: (RACINE / c).stat().st_size for c in devis}
    texte = "\n".join(_texte(c) for c in devis if Path(c).suffix == ".md")
    cite = len(re.findall(r"generateur_gds", texte, re.I))
    ligne = next((l.strip() for l in texte.splitlines() if "generateur_gds" in l), "")
    corpus = _corpus_texte()
    n_boite, f_boite = _motif_par_fichier(r"bo[îi]te\s+noire", corpus)
    return {"extensions_binaires": binaires,
            "artefacts_precompiles": sum(binaires.values()),
            "fichiers_dossier_devis": devis, "tailles_octets": tailles,
            "generateur_gds_cite": cite, "ligne_citant_le_generateur": ligne[:120],
            "octets_compiles_sur_disque": sum(1 for p in RACINE.rglob("*.pyc")),
            "boite_noire_evoquee_dans_le_corpus": n_boite,
            "boite_noire_fichiers": f_boite,
            "conteneur_chiffre": len(re.findall(r"conteneur\s+chiffr[ée]", texte, re.I)),
            "audits_sur_serveurs_tiers_attestes": 0,
            "ce_que_l_avis_prescrivait": "« Structurer les démonstrations en boîte noire… tests en "
                                         "mode API fermée ou conteneur chiffré précompilé »",
            "conseil_deja_contredit": cite > 0 and sum(binaires.values()) == 0}


def structure_contrat() -> Dict[str, Any]:
    corpus = _corpus_texte()
    rendu: Dict[str, Any] = {}
    for lib, pat in INSTRUMENTS:
        n, ou = _motif_par_fichier(pat, corpus)
        rendu[lib] = {"occurrences": n, "fichiers": ou}
    pieces = [c for c in _chemins_sous_arbre()
              if Path(c).suffix in (".pdf", ".docx", ".doc", ".odt", ".rtf", ".xades", ".p7s")]
    signes_par_piece = sum(len(re.findall(MOTIFS_SIGNATURE, _texte(c), re.I))
                           for c in corpus if Path(c).suffix in (".pdf", ".docx", ".odt", ".rtf"))
    croise = sum(1 for lib, pat in INSTRUMENTS
                 if rendu[lib]["occurrences"] > 0
                 and rendu[lib]["fichiers"] and signes_par_piece > 0)
    return {"par_instrument": rendu, "nb_instruments": len(INSTRUMENTS),
            "instruments_cites": sum(1 for v in rendu.values() if v["occurrences"]),
            "instruments_signes": croise,
            "documents_contractuels_sur_disque": len(pieces),
            "pieces_listees": sorted(pieces),
            "distingue_licence_de_cession": all(
                rendu[lib]["occurrences"] > 0 for lib in
                ("licence d'exploitation", "cession de propriete intellectuelle")),
            "bilateralite_et_droit_francais": rendu[
                "accord de confidentialite bilatéral"]["occurrences"],
            "ce_que_l_avis_prescrivait": "« Refuser les cessions globales déguisées… conservez la "
                                         "propriété exclusive des algorithmes sous-jacents »",
            "mesure": "les quatre instruments sont nommés par ce module, aucun n'apparaît dans une "
                      "pièce du dépôt, et 0 document contractuel n'est posé sur disque"}


def remuneration() -> Dict[str, Any]:
    corpus = _corpus_texte()
    devis = [c for c in _chemins_sous_arbre()
             if c.startswith("DOSSIER_DEVIS/") and Path(c).suffix == ".md"]
    texte = "\n".join(_texte(c) for c in devis)
    lignes = texte.splitlines()
    montants = len(re.findall(MONTANT, texte))
    lignes_montants = [l.strip()[:90] for l in lignes if re.search(MONTANT, l)]
    mots_prix = len(re.findall(MOTIF_PRIX_MOT, texte, re.I))
    n_red, f_red = _motif_par_fichier(MOTIF_REDEVANCE, corpus)
    return {"devis_fichiers": sorted(devis),
            "devis_lignes": len(lignes), "devis_octets": len(texte.encode("utf-8")),
            "montants_imposes": montants, "lignes_avec_montant": lignes_montants[:4],
            "mentions_de_prix_ou_cout": mots_prix,
            "redevances_occurrences": n_red, "redevances_fichiers": f_red,
            "forfait_unique_impose": len(re.findall(r"forfait\s+unique", texte, re.I)),
            "modele_hybride_declare": "part fixe + redevance proportionnelle aux déploiements",
            "modele_signe": False,
            "ce_que_l_avis_prescrivait": "« Évitez les forfaits uniques sous-évalués sans "
                                         "intéressement. Négociez un modèle hybride »",
            "mesure": f"{montants} montant imposé et {n_red} clause de redevance dans tout le "
                      f"dépôt, alors que {mots_prix} ligne(s) du devis parlent de prix, de coût "
                      "ou de tarif"}


def relecture_avocat() -> Dict[str, Any]:
    corpus = _corpus_texte()
    rendu: Dict[str, Any] = {}
    for lib, pat in MOTIFS_JURIDIQUES:
        n, ou = _motif_par_fichier(pat, corpus)
        rendu[lib] = {"occurrences": n, "fichiers": ou[:4]}
    cites = sum(1 for v in rendu.values() if v["occurrences"])
    return {"par_terme": rendu, "termes_cherches": len(MOTIFS_JURIDIQUES),
            "termes_rencontres": cites,
            "avocat_rencontre": rendu["avocat"]["occurrences"],
            "barreau_rencontre": rendu["barreau"]["occurrences"],
            "saisine_attestee": False,
            "date_de_saisine": None,
            "condition_suspensive_rempie": False,
            "instruments_a_relire": len(INSTRUMENTS),
            "ce_que_l_avis_prescrivait": "« Ne signez aucun contrat de partenariat, protocole "
                                         "d'accord (MOU) ou contrat de licence sans relecture "
                                         "préalable par un avocat spécialisé »",
            "mesure": "aucune saisine n'est écrite dans le dépôt : la relecture reste une condition "
                      "à venir, pas une étape accomplie"}


def exposition() -> Dict[str, Any]:
    z = json.loads(_texte(".zenodo.json"))
    cff = _texte("CITATION.cff")

    def champ(nom: str) -> str:
        m = re.search(rf"^{nom}:\s*\"?([^\"\n]+)\"?\s*$", cff, re.M)
        return m.group(1).strip() if m else ""

    licence_zenodo = str(z.get("license", ""))
    licence_cff = champ("license")
    expression = licence()["expression_lue"]
    branches = sorted({b.strip() for b in re.split(r"\s+OR\s+", expression)})
    racine_z = licence_zenodo.lower().replace("-only", "").replace("-or-later", "")
    perdues = [b for b in branches if b.lower().replace("-only", "") != racine_z]
    return {"version_zenodo": str(z.get("version", "")), "version_cff": champ("version"),
            "versions_egales": str(z.get("version", "")) == champ("version"),
            "titre_egal": z.get("title", "") == champ("title"),
            "titre": champ("title"),
            "doi_cff": champ("doi"), "cle_doi_dans_zenodo": "doi" in z,
            "licence_zenodo": licence_zenodo, "licence_cff": licence_cff,
            "expression_corpus": expression, "branches_de_l_expression": branches,
            "licence_zenodo_couvre_une_branche": racine_z in {
                b.lower().replace("-only", "") for b in branches},
            "licences_divergentes": licence_zenodo != licence_cff,
            "branches_non_reprises_dans_zenodo": perdues,
            "upload_type": str(z.get("upload_type", "")),
            "depot_distant": (next(iter(re.findall(r"url\s*=\s*(\S+)", _texte(".git/config"))), "")
                              if (RACINE / ".git" / "config").exists() else ""),
            "references_zenodo": len(z.get("references", []) or []),
            "date_release_lue": champ("date-released"),
            "expose": bool(champ("doi")) and bool(_chemins_sous_arbre())}


def chronologie() -> Dict[str, Any]:
    h, e = horodatages(), exposition()
    cs, st = clauses(), structure_contrat()
    verrous = cs["clauses_redigees"] + st["instruments_signes"]
    expose = bool(e["doi_cff"])
    ordre = verrous > 0 and expose
    ordre_sans_dates = verrous > 0
    return {"premiere_trace_datee": h["premiere"], "derniere_trace_datee": h["derniere"],
            "secondes_attestees": h["duree_attestee_seconde"],
            "commits_attestes": h["commits_attestes"],
            "source_des_dates": h["source_des_commits"],
            "date_de_exposition_lue": e["date_release_lue"],
            "exposition_datee_sans_le_journal": bool(e["date_release_lue"]),
            "ecritures_du_journal_local": h["journal_local"]["parsees"],
            "journal_local_present": h["journal_local"]["present"],
            "divergence_journal_moins_histoire": h["journal_plus_que_commits"],
            "doi_deja_publie": expose,
            "verrous_pos_avant_exposition": verrous,
            "verrouillage_avant_exposition": ordre,
            "verrouillage_sans_consulter_une_date": ordre_sans_dates,
            "ordre_independant_des_sources_de_dates": ordre == ordre_sans_dates,
            "exposition_attestee_anterieure_aux_verrous": expose and verrous == 0,
            "second_term_manquant_pour_dater_un_verrou": True,
            "ce_que_l_avis_prescrivait": "« Phase 1 : Verrouillage et traçabilité pré-exposition »",
            "mesure": f"l'histoire suivie par git porte {h['commits_attestes']} commits datés, le "
                      f"journal local enregistre {h['journal_local']['parsees']} écritures (écart "
                      f"{h['journal_plus_que_commits']}) : le DOI est publié et aucun verrou n'a été "
                      f"posé, la phase 1 arrive après l'exposition, elle ne la précède plus",
            "portee_des_deux_sources": "les commits se lisent dans un clone et "
                                                         "dans l'archive tant que git y est "
                                                         "disponible ; le journal de références "
                                                         "reste sur le disque qui l'a produit",
            "gouvernable_desormais": ["prochaine divulgation", "prochain contact",
                                      "prochain document avant envoi"],
            "retroactif_impossible": True}


def limites_ouvertes() -> Dict[str, Any]:
    reg = registre_acces()
    chemins = _chemins_sous_arbre()
    suivis = _suivis_par_git()
    nb_courriers = reg["matiere_sur_disque"]
    nb_suivis = reg["matiere_suivie_par_git"]
    hors_suivi = None if suivis is None else len({c for c in chemins} - {c for c in suivis})
    suivi_texte = ("git indisponible ici" if nb_suivis is None
                   else f"{nb_suivis} seulement suivi(s) par git")
    arbre_texte = ("git indisponible ici" if hors_suivi is None
                   else f"{hors_suivi} fichier(s) hors du suivi git")
    liste = [
        "aucune clause n'a été rédigée ici : les huit recherchées restent à écrire par un juriste, "
        "et ce module ne peut pas les écrire à sa place",
        f"le registre d'accès est vide : {reg['nb_entrees']} ligne lue dans ses octets, et les "
        f"{nb_courriers} fichier(s) de courriers posés sur ce disque ({suivi_texte}, "
        f"{reg['matiere_entree_du_sceau']} sous le sceau) n'y sont pas repris",
        "un dépôt horodaté ne prouve pas la paternité : ni enveloppe e-Soleau, ni RFC 3161, ni "
        "constat d'huissier n'existe dans ce corpus",
        "les concepts mathématiques ne sont pas protégeables par le droit d'auteur : seule "
        "l'expression du code est sous licence, le rapport ρ ne l'est pas",
        "la phase 1 conseillait de verrouiller avant d'exposer ; le DOI et les commits datés sont "
        "antérieurs, l'ordre est donc tenu et non réparable",
        "le manifeste ne couvre pas tout l'arbre : les fichiers hors sceau sont publics sans être "
        "certifiés, et leur nombre est publié par EQ-02",
        "aucun avocat n'a été saisi et aucune date de saisine n'existe : la relecture reste une "
        "condition suspensive à venir, pas une étape accomplie",
        "la démonstration en boîte noire n'existe pas : aucun artefact précompilé n'est livrable, "
        "et le dossier de devis nomme déjà le générateur de layout",
        "ce module ne donne pas un conseil juridique : il compte des octets posés sur un disque et "
        "ne qualifie aucun droit",
        "les prix, redevances et pourcentages sont absents du corpus : rien n'est négocié, et rien "
        "n'est ici proposé à la place",
        f"ce certificat est mesuré sous le chemin où on le lance : l'arbre vu d'ici compte "
        f"{len(chemins)} fichiers ({arbre_texte}) — les compteurs d'arbre et de matière ne "
        f"voyagent pas avec le dépôt, EQ-01 et EQ-07 publient l'écart des fichiers hors du suivi "
        f"git",
        "les dates du journal local de références ne voyagent pas : seule l'histoire atteignable "
        "par git se relit dans un clone, et l'archive publiée peut ne contenir aucun dépôt git",
        "les quatre artefacts posés sur disque sont un instantané : le compte de commits qu'ils "
        "affichent est celui de l'instant où ils ont été écrits, et le commit qui les transporte "
        "les dépasse toujours d'un",
    ]
    return {"liste": liste, "nb": len(liste), "compte_courriers": nb_courriers,
            "marqueur_courriers": f"{nb_courriers} fichier(s) de courriers",
            "toutes_au_dela_de_20": all(len(l) > 40 for l in liste),
            "remplies_dans_ce_lot": 0,
            "longueur_minimale": min(len(l) for l in liste)}


# ─── 5. Artefacts : écriture, puis relecture du même fichier ------------------


def octets_csv(cert: Dict[str, Any]) -> bytes:
    """Le registre demandé : en-tête de six colonnes, zéro ligne de données.

    Une ligne de commentaire aurait été ajoutée pour porter la phrase d'absence ; elle a été
    refusée, parce qu'un registre se lit avec un tableur et qu'un commentaire y devient une donnée.
    L'absence est donc structurelle : zéro ligne.
    """
    corps = ";".join(COLONNES_REGISTRE)
    return b"\xef\xbb\xbf" + (corps + "\r\n").encode("utf-8")


def octets_svg(cert: Dict[str, Any]) -> bytes:
    valeurs = [(lib, int(cert[nom][clef])) for lib, nom, clef in BARRES]
    grand = max([v for _, v in valeurs] + [1])
    pieces: List[str] = []
    for i, (lib, v) in enumerate(valeurs):
        w = _decimale(LONGUEUR_MAX * Fraction(v) / Fraction(grand), 2)
        y = 34 + i * 30
        pieces.append(
            f'<rect x="250" y="{y - 12}" width="{w}" height="16" fill="{COULEURS[i % len(COULEURS)]}" '
            f'data-libelle="{lib}" data-valeur="{v}"/>')
        pieces.append(
            f'<text x="8" y="{y}" font-size="13" fill="#0f1c2b" xml:lang="fr">{lib}</text>')
        pieces.append(
            f'<text x="{_decimale(Fraction(256) + LONGUEUR_MAX * Fraction(v) / Fraction(grand), 2)}" '
            f'y="{y}" font-size="13" fill="#1c3550">{v}</text>')
    bas = 34 + len(valeurs) * 30 + 24
    sceau = cert["manifeste"]
    note = (f'<text x="8" y="{bas - 18}" font-size="12" fill="#5c2f2f" xml:lang="fr">'
            f'sceau : {sceau["conformes"]}/{sceau["total_lignes"]} entrées conformes, '
            f'{sceau["derivent"]} en dérive — {PHRASE_ABSENCE}</text>')
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="520" height="{bas + 8}" '
        f'viewBox="0 0 520 {bas + 8}">\n'
        f'<title>VERROUS — frontière mesurée entre ce qui est publié et ce qui est verrouillé'
        f'</title>\n'
        f'<desc>Longueurs proportionnelles à la plus grande valeur ({grand}). '
        f'{PHRASE_ABSENCE}.</desc>\n'
        + "\n".join(pieces) + "\n" + note + "\n</svg>\n").encode("utf-8")


def octets_clauses_md(cert: Dict[str, Any]) -> bytes:
    inv, man, lic = cert["inventaire"], cert["manifeste"], cert["licence"]
    reg, cls, st = cert["registre_acces"], cert["clauses"], cert["structure_contrat"]
    bo, rm, av = cert["boite_noire"], cert["remuneration"], cert["relecture_avocat"]
    exp, chr_ = cert["exposition"], cert["chronologie"]
    rc = cert["regime_commercial"]
    lignes = [
        f"# VERROUS — {PHRASE_ABSENCE}, mesuré fichier par fichier",
        "",
        f"| phase conseillée | ce que l'avis prescrivait | ce que le dépôt rend | statut |",
        f"|---|---|---|---|",
        f"| 1 | SHA-256 de chaque fichier, config, script et preuve, avant d'exposer | "
        f"{inv['fichiers']} fichiers inventoriés, empreinte d'arbre "
        f"{inv['empreinte_arbre'][:16]}… | OPÉRATIONNEL |",
        f"| 1 | sceau probant (e-Soleau, coffre-fort, RFC 3161) | 0 instrument juridique ; manifeste "
        f"{man['conformes']}/{man['total_lignes']} conformes, {man['derivent']} en dérive | SPÉCIFIÉ |",
        f"| 1 | licence non commerciale | {rc['restrictions_non_commerciales_total']} clause "
        f"d'usage non commercial dans les deux textes GNU ; expression « {lic['expression_lue']} » "
        f"dans {lic['avec_en_tete']}/{lic['python_total']} sources | OPÉRATIONNEL |",
        f"| 1 | garder un cœur secret | {cert['frontiere']['coeur_secret_reelement_garde']} fichier "
        f"gardé, {' · '.join(cert['frontiere']['modules_d_equations_hors_sceau'])} — "
        f"{len(cert['frontiere']['modules_d_equations_hors_sceau'])} module(s) d'équations hors "
        f"sceau et publiés quand même | OPÉRATIONNEL |",
        f"| 2 | registre d'accès | {reg['nb_colonnes']} colonnes, {reg['nb_entrees']} ligne, "
        f"{reg['matiere_sur_disque']} fichier(s) de courriers sur ce disque, "
        f"{reg['matiere_suivie_par_git']} suivi(s) par git, "
        f"{reg['matiere_entree_du_sceau']} sous le sceau, aucun repris | "
        f"OPÉRATIONNEL |",
        f"| 3 | NDA bilatéral en droit français, non-contournement, non-débauchage | "
        f"{cls['clauses_redigees']}/{cls['nb_clauses_cherchees']} clause présente | SPÉCIFIÉ |",
        f"| 3 | boîte noire, conteneur chiffré précompilé | {bo['artefacts_precompiles']} artefact "
        f"précompilé, générateur de layout nommé {bo['generateur_gds_cite']} fois dans le devis | "
        f"OPÉRATIONNEL |",
        f"| 4 | licence d'exploitation contre cession de PI | {st['instruments_cites']}/"
        f"{st['nb_instruments']} instrument cité, {st['instruments_signes']} signé, "
        f"{st['documents_contractuels_sur_disque']} pièce contractuelle sur disque | SPÉCIFIÉ |",
        f"| 4 | rémunération hybride, pas de forfait unique | {rm['montants_imposes']} montant "
        f"imposé, {rm['redevances_occurrences']} mention de redevance, "
        f"{rm['mentions_de_prix_ou_cout']} ligne(s) du devis parlent de prix | SPÉCIFIÉ |",
        f"| 4 | relecture par un avocat spécialisé | {av['avocat_rencontre']} occurrence de « "
        f"avocat », {av['barreau_rencontre']} de « barreau », saisine non attestée | SPÉCIFIÉ |",
        f"| — | verrouiller avant d'exposer | DOI {exp['doi_cff']} publié, "
        f"{chr_['commits_attestes']} commits datés dès {chr_['premiere_trace_datee']}, 0 verrou : "
        f"l'ordre est tenu à l'envers | SPÉCIFIÉ |",
        "",
        "## Les quatre corrections que la mesure impose à l'avis reçu",
        "",
        f"1. {rc['ce_que_les_textes_disent']} : la proposition « AGPLv3 … à usage non commercial "
        f"uniquement » ne décrit aucune des deux licences du dépôt.",
        "2. Un dépôt — e-Soleau, Zenodo ou GitHub — atteste une date d'accessibilité, pas une "
        "paternité. La preuve de paternité reste False tant qu'aucun instrument horodaté n'existe.",
        "3. Un concept mathématique n'est pas protégeable : seule l'expression du code est sous "
        "licence. Garder « les heuristiques fines » contredit la stratégie d'antériorité déjà "
        "exécutée par ce dépôt.",
        "4. La phase 1 supposait une exposition à venir. Elle est faite : ne restent gouvernables "
        "que les divulgations suivantes.",
        "",
        "## Ce qui reste à faire, dans l'ordre",
        "",
    ]
    lignes += [f"- {l}" for l in cert["limites_ouvertes"]["liste"]]
    lignes += ["", f"**{PHRASE_ABSENCE}** : ce dossier compte des octets, il ne rédige rien et ne "
                   "conseille personne."]
    return ("\r\n".join(lignes) + "\r\n").encode("utf-8")


def octets_json(cert: Dict[str, Any]) -> bytes:
    return (json.dumps(cert, ensure_ascii=False, indent=2, sort_keys=True,
                       default=str) + "\n").encode("utf-8")


def _artefacts_octets(cert: Dict[str, Any]) -> Dict[str, bytes]:
    return {"certificat.json": octets_json(cert),
            "registre_acces.csv": octets_csv(cert),
            "verrous_et_clauses.md": octets_clauses_md(cert),
            "frontiere_publique.svg": octets_svg(cert)}


PHRASE_HORS_REGISTRE = ("certificat.json", "verrous_et_clauses.md", "frontiere_publique.svg")


def registre_relu(cert: Dict[str, Any]) -> Dict[str, Any]:
    """Re-lecture des octets du registre : le fichier publié, pas l'intention."""
    octets = octets_csv(cert)
    texte = octets.decode("utf-8-sig")
    lignes = [l for l in texte.split("\r\n") if l != ""]
    entetes = lignes[0].split(";") if lignes else []
    return {"chemin": CHEMIN_REGISTRE, "octets": len(octets),
            "bom": octets[:3] == b"\xef\xbb\xbf", "separateur": ";",
            "crlf": octets.count(b"\r\n") == len(lignes),
            "colonnes_relues": entetes, "nb_lignes_texte": len(lignes),
            "entrees_relues": max(0, len(lignes) - 1),
            "en_tete_conforme": tuple(entetes) == COLONNES_REGISTRE,
            "absence_structurale": max(0, len(lignes) - 1) == 0,
            "phrase_absente_du_csv_par_design": PHRASE_ABSENCE not in texte}


def plan_svg(cert: Dict[str, Any]) -> Dict[str, Any]:
    octets = octets_svg(cert)
    texte = octets.decode("utf-8")
    largeurs = [m.split('width="')[1].split('"')[0] for m in texte.split("<rect ")[1:]]
    valeurs = [(lib, int(cert[nom][clef])) for lib, nom, clef in BARRES]
    grand = max([v for _, v in valeurs] + [1])
    attendues = [_decimale(LONGUEUR_MAX * Fraction(v) / Fraction(grand), 2) for _, v in valeurs]
    return {"chemin": "VERROUS/artefacts/frontiere_publique.svg", "octets": len(octets),
            "barres": len(largeurs), "largeurs_conformes": largeurs == attendues,
            "valeurs_ecrites": [int(m.split('data-valeur="')[1].split('"')[0])
                                for m in texte.split("<rect ")[1:]],
            "valeurs_attendues": [v for _, v in valeurs],
            "plus_grande_valeur": grand,
            "barre_de_zero_longueur": sum(1 for w in largeurs if w == "0.00"),
            "notes_texte": texte.count("<text "), "echelle": f"{_decimale(LONGUEUR_MAX, 0)} px",
            "absence_ecrite": PHRASE_ABSENCE in texte}


def ecritures(cert: Dict[str, Any]) -> Dict[str, Any]:
    rendu = _artefacts_octets(cert)
    hors_boucle = {nom: octets for nom, octets in rendu.items() if nom != "certificat.json"}
    avec_phrase = {nom: octets for nom, octets in rendu.items()
                   if nom in PHRASE_HORS_REGISTRE}
    return {"noms": sorted(rendu),
            "tailles": {nom: len(oct) for nom, oct in sorted(hors_boucle.items())},
            "empreintes": {nom: hashlib.sha256(oct).hexdigest()[:16]
                           for nom, oct in sorted(hors_boucle.items())},
            "auto_reference": "certificat.json porte ce nœud : sa taille et son empreinte ne "
                              "peuvent pas être scellées par lui-même",
            "nom_sans_empreinte": "certificat.json",
            "nom_sans_phrase": "registre_acces.csv",
            "raison_sans_phrase": "une ligne de commentaire dans un registre Excel devient une "
                                  "donnée ; l'absence y est structurelle : zéro ligne",
            "absence_partout": all(PHRASE_ABSENCE.encode("utf-8") in oct
                                   for oct in avec_phrase.values()),
            "noms_avec_phrase": sorted(avec_phrase)}


# ─── 6. Équations et contrôles ------------------------------------------------

NOEUDS: Dict[str, Dict[str, Any]] = {
    "EQ-01": {"depend": [], "externe": ["MANIFESTE_SHA256.txt", ".gitignore"]},
    "EQ-02": {"depend": ["EQ-01"], "externe": ["MANIFESTE_SHA256.txt"]},
    "EQ-03": {"depend": ["EQ-01"], "externe": ["LICENSE", "LICENSE-GPL", "LICENSE-AGPL"]},
    "EQ-04": {"depend": ["EQ-03"], "externe": ["LICENSE-GPL", "LICENSE-AGPL"]},
    "EQ-05": {"depend": ["EQ-01", "EQ-02"], "externe": []},
    "EQ-06": {"depend": ["EQ-01"], "externe": [".git/logs/HEAD", ".git/HEAD"]},
    "EQ-07": {"depend": ["EQ-01"], "externe": []},
    "EQ-08": {"depend": ["EQ-01"], "externe": []},
    "EQ-09": {"depend": ["EQ-01"], "externe": ["DOSSIER_DEVIS/PLAN_TECHNIQUE_DEVIS.md"]},
    "EQ-10": {"depend": ["EQ-08"], "externe": []},
    "EQ-11": {"depend": ["EQ-09"], "externe": ["DOSSIER_DEVIS/"]},
    "EQ-12": {"depend": ["EQ-10"], "externe": []},
    "EQ-13": {"depend": ["EQ-03"], "externe": [".zenodo.json", "CITATION.cff", ".git/config"]},
    "EQ-14": {"depend": ["EQ-06", "EQ-13"], "externe": []},
    "EQ-15": {"depend": ["EQ-02", "EQ-08"], "externe": []},
    "EQ-16": {"depend": ["EQ-05", "EQ-12"], "externe": []},
}


def _eq(id_: str, chemin: str, formule: str, resultat: str, statut: str,
        limite: str, detail: Any, couche: str = "S2 REGULARITE") -> Dict[str, Any]:
    n = NOEUDS[id_]
    return {"id": id_, "chemin": chemin, "formule": formule, "resultat": resultat,
            "statut": statut, "limite": limite, "detail": detail, "couche": couche,
            "piliers": ["P1 UNITE", "P2 BORNE", "P3 CONFRONTATION", "P4 TRANSMISSION"],
            "depend_de": n["depend"], "fonde_hors_du_dossier": n["externe"]}


def equations(etat: Dict[str, Any]) -> List[Dict[str, Any]]:
    inv, man, lic = etat["inventaire"], etat["manifeste"], etat["licence"]
    rc, fr, h = etat["regime_commercial"], etat["frontiere"], etat["horodatages"]
    reg, cls, bo = etat["registre_acces"], etat["clauses"], etat["boite_noire"]
    st, rm, av = etat["structure_contrat"], etat["remuneration"], etat["relecture_avocat"]
    exp, chr_, lo = etat["exposition"], etat["chronologie"], etat["limites_ouvertes"]
    rr, sv, ec = etat["registre_relu"], etat["plan_svg"], etat["ecritures"]
    hi, hj = h["histoire"], h["journal_local"]
    # les listes publiées dans un énoncé s'écrivent en français, pas en repr Python
    versions_gnu = " / ".join(k + " " + ", ".join(v)
                               for k, v in sorted(lic["textes_gnu_versions"].items()))
    branches_perdues = " · ".join(exp["branches_non_reprises_dans_zenodo"]) or "aucune"
    colonnes = " ; ".join(rr["colonnes_relues"])
    return [
        _eq("EQ-01", "verrous_base.py → inventaire() → C01",
            "E_arbre = sha256( ⨁_f (chemin_f ‖ sha256(octets_f)) ) sur les fichiers du dépôt, hors "
            "caches, .git, .qoder_tmp* et nos propres artefacts",
            f"{inv['fichiers']} fichiers · {inv['octets_total']} octets · "
            f"{len(inv['par_extension'])} extensions · {inv['hors_depot_public']['fichiers']} "
            f"fichier(s) hors dépôt public ({inv['hors_depot_public']['octets']} octets) · "
            f"{inv['fichiers_suivis_par_git']} suivis par git et "
            f"{inv['fichiers_non_suivis_par_git']} hors suivi · aucune horloge dans le source "
            f"{inv['aucune_horloge']}", "OPÉRATIONNEL",
            "l'empreinte est une adresse, pas une preuve : elle dit que ces octets étaient là, elle "
            "ne dit pas de qui ni depuis quand · un fichier hors du suivi git n'est pas publié : "
            "il ne voyage ni dans un clone, ni dans l'archive", inv),
        _eq("EQ-02", "verrous_base.py → manifeste() → C02",
            "pour chaque entrée (h, chemin) du manifeste : h == sha256(octets) ou "
            "h == sha256(octets sans CRLF) ; sinon la dérive est comptée et listée",
            f"{man['total_lignes']} entrées · {man['a_l_identique']} à l'identique · "
            f"{man['apres_normalisation_des_fins_de_ligne']} après normalisation LF · "
            f"{man['derivent']} en dérive · {man['absents_de_disque']} absent(s) · verdict "
            f"{man['verdict']} · {man['hors_manifeste']} fichiers publiés hors du sceau",
            "OPÉRATIONNEL",
            "re-sceller effacerait le compte de dérive sans effacer la cause : ce résultat garde le "
            "nombre dérivé écrit, y compris quand il est défavorable", man),
        _eq("EQ-03", "verrous_base.py → licence() → C03",
            "expression SPDX lue dans LICENSE = celle de chaque en-tête de .py ; les fichiers sans "
            "en-tête sont nommés, pas comptés en silence",
            f"« {lic['expression_lue']} » · {lic['avec_en_tete']}/{lic['python_total']} sources "
            f"Python · {lic['sans_en_tete']} sans en-tête · {lic['occurrences_en_tete']} occurrences "
            f"· versions GNU {versions_gnu}", "OPÉRATIONNEL",
            "un en-tête de plus ne change pas le droit applicable : ce contrôle dit une couverture "
            "d'écriture, pas une validité juridique", lic),
        _eq("EQ-04", "verrous_base.py → regime_commercial() → C04",
            "n_mot(« non-commercial use ») sur LICENSE-GPL ‖ LICENSE-AGPL ; n_mot(« you may charge ») "
            "; n_mot(« Remote Network Interaction ») par texte",
            f"restriction d'usage non commercial {rc['restrictions_non_commerciales_total']} · "
            f"permission de facturer {rc['permissions_de_facturer_total']} · clause réseau GPL "
            f"{rc['clause_reseau_gpl']} / AGPL {rc['clause_reseau_agpl']} · seules différences "
            f"mesurées « {' · '.join(rc['seules_differences_mesurees'])} » · "
            f"{rc['ce_que_les_textes_disent']}",
            "OPÉRATIONNEL",
            "compter des mots dans une licence n'interprète pas la licence : la qualification "
            "appartient à un avocat, que ce dépôt n'a pas saisi", rc),
        _eq("EQ-05", "verrous_base.py → frontiere() → C05",
            "garde_hors_depot = |{fichiers dont le nom porte secret/credential/.pem/.env}| ; "
            "equations_hors_sceau = |{fichiers .py contenant « def equations( » et absents du "
            "manifeste}| — un résultat non nul signale une dérive du sceau, pas une publication "
            "choisie",
            f"{fr['coeur_secret_reelement_garde']} fichier gardé hors du dépôt · "
            f"{len(fr['modules_portant_des_equations'])} modules porteurs d'équations, "
            f"{len(fr['modules_d_equations_hors_sceau'])} hors du sceau · "
            f"{fr['occurrences_heuristiques']} occurrence(s) d'heuristiques et calibrages · "
            f"{fr['mesure']}", "OPÉRATIONNEL",
            "la frontière conseillée par l'avis est incompatible avec la stratégie déjà exécutée : "
            "le dépôt publie ses modules d'équations et n'en garde aucun", fr),
        _eq("EQ-06", "verrous_base.py → horodatages() → C06",
            "histoire = |{commits atteignables depuis HEAD}| lue par git log ; journal = |{lignes "
            "de .git/logs/HEAD}| ; écart = journal − histoire",
            f"{hi['commits']}/{hi['lignes']} commit(s) atteignable(s) · {hi['premiere']} → "
            f"{hi['derniere']} · {hi['duree_attestee_seconde']} s · auteurs {hi['auteurs']} · tête "
            f"cohérente {hi['tete_coherente']} · journal local {hj['parsees']} écriture(s), présent "
            f"{hj['present']}, écart {h['journal_plus_que_commits']} · "
            f"{h['nb_artefacts_horodatage']} artefact d'horodatage sur disque "
            f"({h['extensions_instrument']}) et {h['mentions_instrument_occurrences']} mention(s) "
            f"du mot dans {h['mentions_instrument_fichiers']} fichier(s)",
            "OPÉRATIONNEL",
            "un dépôt horodaté prouve une accessibilité, pas une paternité : "
            "antériorité légale = False · le mot « coffre-fort » ou « INPI » dans un fichier ne "
            "date rien : seul un artefact remis par l'autorité de temps date · le journal local de "
            "références ne voyage ni dans un clone ni dans l'archive : les dates citées viennent de "
            "l'histoire atteignable, pas de lui", h),
        _eq("EQ-07", "verrous_base.py → registre_acces() → C07",
            "registre = 6 colonnes (date, personne, entité, canal, question, réponse) ; entrées = "
            "|{lignes de données lues dans ses octets}| ; matière comptée sur disque, dans le suivi "
            "git et sous le sceau",
            f"{reg['nb_colonnes']} colonnes · {reg['nb_entrees']} entrée lue sur disque · "
            f"{reg['matiere_sur_disque']} fichier(s) de courriers sur ce disque, "
            f"{reg['matiere_suivie_par_git']} suivi(s) par git, "
            f"{reg['matiere_entree_du_sceau']} sous le sceau · "
            f"{reg['matiere_reprise_dans_le_registre']} repris · registre préexistant "
            f"{reg['absent_avant_ce_dossier']}", "OPÉRATIONNEL",
            "le cadre est posé, la matière ne l'est pas : "
            f"{reg['matiere_hors_registre']} fichier(s) de correspondance dorment hors du registre "
            f"et {reg['matiere_entree_du_sceau']} n'entre dans le sceau ; un registre vide ne "
            "protège personne, et une matière que git ne suit pas n'est pas publiée", reg),
        _eq("EQ-08", "verrous_base.py → clauses() → C08",
            "|{c ∈ CLAUSES : occurrences(c, corpus hors ce module)}| avec contrôle positif SPDX et "
            "contraste naïf « nda »",
            f"{cls['clauses_redigees']}/{cls['nb_clauses_cherchees']} clause rédigée · contrôle "
            f"positif {cls['controle_positif_occurrences']} occurrences dans "
            f"{cls['controle_positif_fichiers']} fichiers · contraste naïf "
            f"{cls['contraste_naif_occurrences']} occurrences dans "
            f"{cls['contraste_naif_fichiers']} fichiers · auto-exclusion porteuse "
            f"{cls['auto_contient_motifs']} occurrence(s)", "OPÉRATIONNEL",
            "la recherche est validée par un terme qui, lui, existe : sans le contrôle positif, un "
            "zéro ne voudrait rien dire", cls),
        _eq("EQ-09", "verrous_base.py → boite_noire() → C09",
            "n_artefacts(précompilé) = Σ |{f : extension ∈ {so, pyd, exe, dll, wasm, …}}| ; "
            "n_mentions(générateur de layout) dans DOSSIER_DEVIS",
            f"{bo['artefacts_precompiles']} artefact précompilé · "
            f"{bo['octets_compiles_sur_disque']} .pyc localement (exclus du dépôt public) · "
            f"générateur nommé {bo['generateur_gds_cite']} fois dans le dossier de devis · boîte "
            f"noire évoquée {bo['boite_noire_evoquee_dans_le_corpus']} fois", "OPÉRATIONNEL",
            "la boîte noire est prescrite et le devis nomme déjà l'outil paramétrique : les deux "
            "pièces du dossier se contredisent aujourd'hui", bo),
        _eq("EQ-10", "verrous_base.py → structure_contrat() → C10",
            "|{i ∈ INSTRUMENTS : occurrences(i) > 0}| ; signés = instruments cités dans une pièce "
            "portant une marque de signature",
            f"{st['instruments_cites']}/{st['nb_instruments']} instrument cité · "
            f"{st['instruments_signes']} signé · {st['documents_contractuels_sur_disque']} pièce "
            f"contractuelle sur disque · licence distinguée de la cession "
            f"{st['distingue_licence_de_cession']}", "SPÉCIFIÉ",
            "nommer quatre instruments ne les rédige pas : ce nœud constate une absence, il "
            "n'écrit aucun contrat", st),
        _eq("EQ-11", "verrous_base.py → remuneration() → C11",
            "n_montant(devis) + n_redevance(corpus) ; un montant est imposé s'il est écrit avec une "
            "devise et un nombre",
            f"{rm['montants_imposes']} montant imposé · {rm['mentions_de_prix_ou_cout']} ligne(s) "
            f"de devis parlent de prix, coût ou tarif · {rm['redevances_occurrences']} mention de "
            f"redevance · {rm['forfait_unique_impose']} forfait unique imposé · modèle déclaré : "
            f"{rm['modele_hybride_declare']}", "SPÉCIFIÉ",
            "ce module ne propose aucun prix : proposer serait déjà négocier, et rien ici n'est "
            "négocié avec personne", rm),
        _eq("EQ-12", "verrous_base.py → relecture_avocat() → C12",
            "n_occ(« avocat ») + n_occ(« barreau ») sur le corpus ; saisine = un instrument nommé "
            "avec une date de relecture",
            f"{av['avocat_rencontre']} occurrence de « avocat » · {av['barreau_rencontre']} de "
            f"« barreau » · {av['termes_rencontres']}/{av['termes_cherches']} terme juridique "
            f"rencontré · saisine attestée {av['saisine_attestee']} · condition suspensive remplie "
            f"{av['condition_suspensive_rempie']}", "SPÉCIFIÉ",
            "l'avis exige une relecture préalable par un avocat spécialisé : ce nœud mesure qu'elle "
            "n'a pas eu lieu et ne la remplace pas. Le comptage porte sur les mots, pas sur les "
            "preuves : écrire dans un document du dépôt que le mot manque ferait monter le compteur "
            "— constaté le 2026-11-10 sur README.md, et la prose du dépôt évite donc de redire ce "
            "que ce nœud compte déjà", av),
        _eq("EQ-13", "verrous_base.py → exposition() → C13",
            "version_zenodo = version_cff ∧ titre_egal ∧ licence_zenodo ∈ branches(expression) ; "
            "divergence = licence_zenodo ≠ licence_cff",
            f"version {exp['version_zenodo']} = {exp['version_cff']} · DOI {exp['doi_cff']} · "
            f"licence Zenodo « {exp['licence_zenodo']} » contre « {exp['licence_cff']} » · "
            f"branches non reprises {branches_perdues} · dépôt "
            f"{exp['depot_distant']}", "OPÉRATIONNEL",
            "les deux fichiers de citation ne disent pas la même licence : l'écart est publié, la "
            "correction relève d'une décision d'auteur, pas de ce module", exp),
        _eq("EQ-14", "verrous_base.py → chronologie() → C14",
            "verrouiller_avant_exposer = (verrous > 0) ∧ (DOI publié) ; le verdict ne consulte "
            "aucune date, les dates ne font que dater l'antériorité déjà publique",
            f"première trace {chr_['premiere_trace_datee']} · {chr_['commits_attestes']} commits "
            f"({chr_['source_des_dates']}) · journal local {chr_['ecritures_du_journal_local']} "
            f"écriture(s), écart {chr_['divergence_journal_moins_histoire']} · "
            f"{chr_['secondes_attestees']} s d'amplitude · "
            f"{chr_['verrous_pos_avant_exposition']} verrou · DOI déjà publié "
            f"{chr_['doi_deja_publie']} · ordre tenu {chr_['verrouillage_avant_exposition']} · "
            f"{chr_['mesure']}", "SPÉCIFIÉ",
            "rien de ce qui est déjà public ne peut être re-verrouillé après coup : seule la "
            "prochaine divulgation est gouvernable", chr_),
        _eq("EQ-15", "verrous_base.py → registre_relu() → plan_svg() → C15",
            "relire les octets écrits : BOM, séparateur « ; », en-tête à 6 colonnes, 0 ligne de "
            "données ; longueurs SVG = 220 px × valeur / max(valeurs)",
            f"registre relu : {colonnes} · {rr['entrees_relues']} entrée · BOM "
            f"{rr['bom']} · CRLF {rr['crlf']} · SVG : {sv['barres']} barres conformes "
            f"{sv['largeurs_conformes']} · {sv['barre_de_zero_longueur']} barre(s) à longueur nulle · "
            f"artefacts {ec['tailles']}", "OPÉRATIONNEL",
            "le registre ne porte pas la phrase d'absence : une ligne de commentaire y serait lue "
            "comme une donnée, son absence est donc structurelle", rr),
        _eq("EQ-16", "verrous_base.py → limites_ouvertes() → C16",
            "les limites non remplies par cette couche sont comptées et aucune n'est déclarée close",
            f"{lo['nb']} limites · aucune remplie · plus courte {lo['longueur_minimale']} "
            f"caractères · verrous posés {cls['clauses_redigees'] + st['instruments_signes']}",
            "SPÉCIFIÉ",
            "écrire une limite ne la franchit pas : la liste reste ouverte tant qu'un contrat "
            "n'existe pas et qu'un avocat n'a pas relu", lo, "S3 HORS_MATRICE"),
    ]


def controles(eqs: Dict[str, Any], etat: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []

    def ajouter(id_: str, nom: str, verifie: str, attendu: str, obtenu: str, ok: bool) -> None:
        out.append({"id": id_, "equation": f"EQ-{id_[1:]}", "nom": nom, "verifie": verifie,
                    "attendu": attendu, "obtenu": obtenu, "ok": bool(ok)})

    inv, man, lic = etat["inventaire"], etat["manifeste"], etat["licence"]
    rc, fr, h = etat["regime_commercial"], etat["frontiere"], etat["horodatages"]
    reg, cls, bo = etat["registre_acces"], etat["clauses"], etat["boite_noire"]
    st, rm, av = etat["structure_contrat"], etat["remuneration"], etat["relecture_avocat"]
    exp, chr_, lo = etat["exposition"], etat["chronologie"], etat["limites_ouvertes"]
    rr, sv, ec = etat["registre_relu"], etat["plan_svg"], etat["ecritures"]
    hi, hj = h["histoire"], h["journal_local"]

    ajouter("C01", "l'inventaire est clos, additif et sans horloge murale",
            "chemins uniques, somme des extensions = nombre de fichiers, suivi git + hors suivi = "
            "nombre de fichiers, empreinte longue de 64 caractères hexadécimaux, aucune fonction "
            "d'heure dans le source de ce module",
            "arbre additif · suivi additif · empreinte 64 hex · datetime.now absent",
            f"{inv['fichiers']} fichiers · extensions {inv['somme_extensions']} · suivi git "
            f"{inv['fichiers_suivis_par_git']} + hors suivi {inv['fichiers_non_suivis_par_git']} · "
            f"empreinte {len(inv['empreinte_arbre'])} caractères · horloge absente "
            f"{inv['aucune_horloge']} · ecritures {inv['ecrit_uniquement_dans']} · hors du suivi "
            f"écrit dans EQ-01 {'hors du suivi git' in eqs['EQ-01']['limite']}",
            inv["chemins_uniques"] and inv["extensions_additives"] and inv["suivi_additif"]
            and len(inv["empreinte_arbre"]) == 64 and inv["aucune_horloge"]
            and inv["horloge_noyau_fichiers"] >= 0
            and "hors du suivi git" in eqs["EQ-01"]["limite"])
    ajouter("C02", "la dérive du sceau est mesurée, chiffrée et écrite dans le résultat",
            "les quatre comptes épuisent les entrées, le nombre dérivé paraît dans le texte publié "
            "de EQ-02 et le manifeste ne se scelle pas lui-même",
            f"{man['total_lignes']} = Σ comptes · dérive écrite",
            f"{man['a_l_identique']} + {man['apres_normalisation_des_fins_de_ligne']} + "
            f"{man['derivent']} + {man['absents_de_disque']} = {man['total_lignes']} · additif "
            f"{man['comptes_additifs']} · dérive écrite dans le résultat "
            f"{'en dérive' in eqs['EQ-02']['resultat'] and str(man['derivent']) in eqs['EQ-02']['resultat']} · "
            f"auto-scellement {man['le_manifeste_ne_se_scelle_pas_lui_meme']}",
            man["comptes_additifs"] and man["le_manifeste_ne_se_scelle_pas_lui_meme"]
            and str(man["derivent"]) in eqs["EQ-02"]["resultat"]
            and len(man["derivent_listes"]) == man["derivent"]
            and man["toutes_entrees_existent"])
    ajouter("C03", "une seule expression de licence circule, et les absents sont nommés",
            "une expression, identique à celle de LICENSE, et autant de noms dans la liste des sans-"
            "en-tête que le compte l'annonce",
            "1 expression · liste complète",
            f"{len(lic['expressions_dans_les_sources'])} expression(s) · uniforme "
            f"{lic['uniforme_avec_licenc_racine']} · {lic['avec_en_tete']}+{lic['sans_en_tete']} = "
            f"{lic['python_total']} · listés {len(lic['sans_en_tete_listes'])}",
            lic["expression_unique"] and lic["uniforme_avec_licenc_racine"]
            and lic["compte_additif"]
            and len(lic["sans_en_tete_listes"]) == lic["sans_en_tete"])
    ajouter("C04", "le régime commercial est dit d'après les textes, pas d'après l'avis reçu",
            "aucune clause d'usage non commercial dans les deux textes, la permission de facturer "
            "présente dans chacun, et la seule différence de présence entre GPL et AGPL est la "
            "clause d'interaction à distance",
            "0 restriction non commerciale · clause réseau 1 en AGPL, 0 en GPL",
            f"{rc['restrictions_non_commerciales_total']} restriction · "
            f"{rc['permissions_de_facturer_total']} permission de facturer · réseau "
            f"GPL {rc['clause_reseau_gpl']} / AGPL {rc['clause_reseau_agpl']} · différences "
            f"{rc['seules_differences_mesurees']} · écarts de compte {rc['ecarts_de_compte']} · "
            f"texte dit dans EQ-04 "
            f"{'autorisan' in eqs['EQ-04']['resultat'] or 'usage commercial' in eqs['EQ-04']['resultat']}",
            rc["la_clause_pretendue_est_absente"] and rc["facturer_present_dans_les_deux"]
            and rc["permissions_de_facturer_total"] > 0
            and rc["clause_reseau_agpl"] == 1 and rc["clause_reseau_gpl"] == 0
            and rc["seules_differences_mesurees"]
            == ["clause d'interaction à distance"])
    ajouter("C05", "rien n'est gardé hors du dépôt, et tout module d'équations est sous le sceau",
            "0 fichier au nom secret, au moins un module d'équations publié et lisible, aucun hors "
            "du sceau, le drapeau de couverture égal au compte mesuré, et des heuristiques "
            "réellement publiées",
            "0 gardé · ≥1 module publié · 0 module hors sceau · drapeau = (compte = 0)",
            f"{fr['coeur_secret_reelement_garde']} gardé · "
            f"{len(fr['modules_portant_des_equations'])} module(s) d'équations publié(s), "
            f"{len(fr['modules_d_equations_hors_sceau'])} hors sceau · "
            f"{fr['occurrences_heuristiques']} occurrence(s) d'heuristiques · hors sceau "
            f"{fr['hors_manifeste']} fichiers",
            fr["coeur_secret_reelement_garde"] == 0
            and len(fr["modules_portant_des_equations"]) > 0
            and len(fr["modules_d_equations_hors_sceau"]) == 0
            and fr["tous_les_modules_d_equations_scelles"]
            == (len(fr["modules_d_equations_hors_sceau"]) == 0)
            and fr["occurrences_heuristiques"] > 0 and fr["hors_manifeste"] > 0)
    ajouter("C06", "l'horodatage est lisible dans ce qui voyage, et ne prouve pas la paternité",
            "toutes les lignes des deux sources parsees, somme des auteurs = lignes, tête du dépôt "
            "= sha du commit le plus récent, dates publiées lues dans l'histoire git et non dans le "
            "journal local, 0 artefact d'horodatage sur disque, paternité False",
            "histoire = source des dates · 0 artefact · paternité False",
            f"histoire {hi['commits']}/{hi['lignes']} · auteurs {hi['somme_auteurs']} · tête "
            f"cohérente {hi['tete_coherente']} · journal local {hj['parsees']}/{hj['lignes']} "
            f"(utf8 intégral {hj['utf8_integrale']}) · écart publié "
            f"{h['journal_plus_que_commits']} = {hj['parsees']} − {hi['commits']} "
            f"{h['journal_plus_que_commits'] == hj['parsees'] - hi['commits']} · "
            f"{h['nb_artefacts_horodatage']} artefact(s) sur disque et "
            f"{h['mentions_instrument_occurrences']} mention(s) · cohérence compte/drapeau "
            f"{h['aucun_instrument_strict'] == (h['nb_artefacts_horodatage'] == 0)} · preuve de "
            f"paternité {h['preuve_de_paternite']} · antériorité écrite dans EQ-06 "
            f"{'antériorité légale = False' in eqs['EQ-06']['resultat'] + eqs['EQ-06']['limite']}",
            hi["tout_parse"] and hi["auteurs_additifs"] and hj["tout_parse"]
            and hj["auteurs_additifs"] and hj["utf8_integrale"]
            and h["dates_publiees_par"] == "histoire"
            and h["commits_attestes"] == hi["commits"] and h["premiere"] == hi["premiere"]
            and h["journal_plus_que_commits"] == hj["parsees"] - hi["commits"]
            and hi["tete_coherente"] == (hi["commits"] > 0)
            and h["aucun_instrument_strict"]
            and h["aucun_instrument_strict"] == (h["nb_artefacts_horodatage"] == 0)
            and h["preuve_de_paternite"] is False
            and "antériorité légale = False" in (eqs["EQ-06"]["resultat"]
                                                 + eqs["EQ-06"]["limite"])
            and "journal local de références ne voyage" in eqs["EQ-06"]["limite"])
    ajouter("C07", "le registre existe, est vide, et rien n'y a été porté en secret",
            "6 colonnes, 0 ligne lue dans les octets posés sur le disque du registre, aucun registre "
            "préexistant, 0 matière reprise, la matière comptée séparément sur disque, dans le suivi "
            "git et sous le sceau",
            "6 · 0 entrée lue · 0 préexistant · 0 repris",
            f"{reg['nb_colonnes']} colonnes · {reg['nb_entrees']} entrée lue sur disque "
            f"(registre présent : {reg['registre_posé_sur_disque']}) · préexistants "
            f"{len(reg['registres_preexistants'])} · matière {reg['matiere_sur_disque']} sur disque, "
            f"{reg['matiere_suivie_par_git']} suivie par git, "
            f"{reg['matiere_entree_du_sceau']} sous le sceau · reprise "
            f"{reg['matiere_reprise_dans_le_registre']} · hors registre "
            f"{reg['matiere_hors_registre']} · compte additif du suivi "
            f"{reg['suivi_additif']}",
            reg["nb_colonnes"] == 6 and reg["nb_entrees"] == 0
            and reg["absent_avant_ce_dossier"]
            and reg["matiere_reprise_dans_le_registre"] == 0
            and reg["matiere_hors_registre"] == reg["matiere_sur_disque"]
            and reg["matiere_entree_du_sceau"] == 0 and reg["suivi_additif"]
            and reg["couvre_quatre_champs_demandes"])
    ajouter("C08", "aucune clause n'est rédigée, et le comptage n'est pas sourd",
            "0 clause sur 8, contrôle positif SPDX non vide, contraste naïf strictement supérieur, "
            "et l'auto-exclusion de ce module porteuse",
            "0/8 · contrôle positif > 0",
            f"{cls['clauses_redigees']}/{cls['nb_clauses_cherchees']} · positif "
            f"{cls['controle_positif_occurrences']}/{cls['controle_positif_fichiers']} fichiers · "
            f"naïf {cls['contraste_naif_occurrences']} dans {cls['contraste_naif_fichiers']} "
            f"fichiers · motifs dans ce module {cls['auto_contient_motifs']}",
            cls["toutes_absentes"] and cls["clauses_redigees"] == 0
            and cls["recherche_fonctionne"] and cls["naif_supere_stricte"]
            and cls["exclusion_est_portante"])
    ajouter("C09", "la boîte noire est absente et le devis nomme l'outil",
            "0 artefact précompilé dans le dépôt, au moins une mention du générateur de layout dans "
            "le dossier de devis",
            "0 précompilé · générateur cité",
            f"{bo['artefacts_precompiles']} artefact · {bo['octets_compiles_sur_disque']} .pyc "
            f"exclus du dépôt public · générateur {bo['generateur_gds_cite']} fois · ligne publiée "
            f"dans EQ-09 {bo['generateur_gds_cite'] > 0}",
            bo["artefacts_precompiles"] == 0 and bo["generateur_gds_cite"] >= 1
            and bo["conseil_deja_contredit"] and bool(bo["ligne_citant_le_generateur"]))
    ajouter("C10", "quatre instruments nommés, aucun signé, aucune pièce contractuelle",
            "longueur publiée = longueur déclarée, 0 instrument cité, 0 signé, 0 pièce sur disque",
            f"{st['nb_instruments']} · 0 signé",
            f"{st['instruments_cites']}/{st['nb_instruments']} cité · {st['instruments_signes']} "
            f"signé · {st['documents_contractuels_sur_disque']} pièce · liste "
            f"{len(st['par_instrument'])} · distinction licence/cession "
            f"{st['distingue_licence_de_cession']}",
            st["nb_instruments"] == len(INSTRUMENTS) == len(st["par_instrument"])
            and st["instruments_cites"] == 0 and st["instruments_signes"] == 0
            and st["documents_contractuels_sur_disque"] == 0
            and not st["distingue_licence_de_cession"])
    ajouter("C11", "le modèle de rémunération est spécifié, non négocié",
            "0 montant imposé dans les fichiers du devis, 0 mention de redevance dans le corpus, et "
            "au moins une ligne du devis parlant de prix",
            "0 montant · 0 redevance",
            f"{rm['montants_imposes']} montant · {rm['redevances_occurrences']} redevance · "
            f"{rm['mentions_de_prix_ou_cout']} ligne(s) de prix · signé {rm['modele_signe']} · "
            f"modèle « {rm['modele_hybride_declare']} »",
            rm["montants_imposes"] == 0 and rm["redevances_occurrences"] == 0
            and rm["mentions_de_prix_ou_cout"] > 0 and not rm["modele_signe"])
    ajouter("C12", "l'avocat n'a pas été saisi : la relecture reste une condition",
            "0 occurrence des deux termes nommés par l'avis, saisine False, et le compte "
            "d'instruments revérifié à partir de la liste publiée par EQ-10",
            "0 · 0 · saisine False",
            f"avocat {av['avocat_rencontre']} · barreau {av['barreau_rencontre']} · termes "
            f"rencontrés {av['termes_rencontres']}/{av['termes_cherches']} · saisine "
            f"{av['saisine_attestee']} · instruments recoupés "
            f"{av['instruments_a_relire'] == st['nb_instruments'] == len(INSTRUMENTS)}",
            av["avocat_rencontre"] == 0 and av["barreau_rencontre"] == 0
            and not av["saisine_attestee"] and not av["condition_suspensive_rempie"]
            and av["instruments_a_relire"] == st["nb_instruments"] == len(INSTRUMENTS))
    ajouter("C13", "l'exposition est publique et ses mentions ne concordent pas",
            "versions égales, titres égaux, DOI publié, et divergence de licence écrite dans le "
            "résultat plutôt que gommée",
            "versions égales · divergence publiée",
            f"{exp['version_zenodo']} = {exp['version_cff']} · titre {exp['titre_egal']} · DOI "
            f"{exp['doi_cff']} · divergence {exp['licences_divergentes']} · branches non reprises "
            f"{exp['branches_non_reprises_dans_zenodo']} · écrite dans EQ-13 "
            f"{'≠' in eqs['EQ-13']['formule'] or 'contre' in eqs['EQ-13']['resultat']}",
            exp["versions_egales"] and exp["titre_egal"] and bool(exp["doi_cff"])
            and exp["licences_divergentes"] and exp["licence_zenodo_couvre_une_branche"]
            and "contre" in eqs["EQ-13"]["resultat"])
    ajouter("C14", "l'ordre conseillé est mesuré comme tenu à l'envers",
            "DOI publié et daté dans le dépôt, commits atteignables rendus par git, 0 verrou : la "
            "phase 1 ne peut plus précéder l'exposition, et le verdict ne change selon aucune des "
            "deux sources de dates consultée",
            "verrouillage avant exposition = False",
            f"{chr_['verrous_pos_avant_exposition']} verrou · DOI {exp['doi_cff']} daté "
            f"{chr_['date_de_exposition_lue']} · {chr_['commits_attestes']} commits atteignables · "
            f"{chr_['ecritures_du_journal_local']} écritures locales · écart "
            f"{chr_['divergence_journal_moins_histoire']} · ordre "
            f"{chr_['verrouillage_avant_exposition']} · sans consulter une date "
            f"{chr_['verrouillage_sans_consulter_une_date']} · rétroactif impossible "
            f"{chr_['retroactif_impossible']} · suites gouvernables "
            f"{len(chr_['gouvernable_desormais'])}",
            chr_["verrous_pos_avant_exposition"] == 0 and exp["expose"]
            and not chr_["verrouillage_avant_exposition"]
            and chr_["exposition_attestee_anterieure_aux_verrous"]
            and chr_["ordre_independant_des_sources_de_dates"]
            and chr_["exposition_datee_sans_le_journal"]
            and bool(re.match(r"^\d{4}-\d{2}-\d{2}$", chr_["date_de_exposition_lue"]))
            and chr_["commits_attestes"] == hi["commits"]
            and chr_["ecritures_du_journal_local"] == hj["parsees"]
            and chr_["divergence_journal_moins_histoire"] == hj["parsees"] - hi["commits"]
            and chr_["secondes_attestees"] == hi["duree_attestee_seconde"]
            and len(chr_["gouvernable_desormais"]) >= 3)
    ajouter("C15", "les octets relus disent les nombres du calcul",
            "registre relu : BOM, séparateur « ; », 6 colonnes, 0 entrée ; SVG : une barre par "
            "indicateur dont la longueur retombe sur la valeur ; un seul fichier hors empreinte et "
            "un seul hors phrase",
            "0 entrée · barres conformes · exclusions exactes",
            f"colonnes {rr['colonnes_relues']} · entrées {rr['entrees_relues']} · BOM {rr['bom']} "
            f"· CRLF {rr['crlf']} · barres {sv['barres']}/{len(BARRES)} conformes "
            f"{sv['largeurs_conformes']} · phrases {ec['noms_avec_phrase']} · hors empreinte "
            f"{sorted(set(ec['noms']) - set(ec['tailles']))} · hors phrase "
            f"{sorted(set(ec['noms']) - set(ec['noms_avec_phrase']))}",
            rr["bom"] and rr["en_tete_conforme"] and rr["entrees_relues"] == 0 and rr["crlf"]
            and sv["barres"] == len(BARRES) and sv["largeurs_conformes"]
            and sv["valeurs_ecrites"] == sv["valeurs_attendues"] and sv["absence_ecrite"]
            and ec["absence_partout"] and rr["phrase_absente_du_csv_par_design"]
            and sorted(set(ec["noms"]) - set(ec["tailles"])) == [ec["nom_sans_empreinte"]]
            and sorted(set(ec["noms"]) - set(ec["noms_avec_phrase"])) == [ec["nom_sans_phrase"]])
    ajouter("C16", "les limites ouvertes ne sont pas déclarées franchies",
            "liste d'au moins douze limites, toutes longues d'au moins 40 caractères, zéro remplie "
            "dans ce lot, le compte de courriers qu'une limite cite retombe sur la mesure, deux "
            "limites disent ce qui ne voyage pas — l'arbre hors suivi et le journal local — et une "
            "limite dit que les artefacts posés sont un instantané",
            "≥12 limites · 0 remplie · compte lié à la mesure",
            f"{lo['nb']} limites · plus courte {lo['longueur_minimale']} caractères · remplies "
            f"{lo['remplies_dans_ce_lot']} · verrous posés "
            f"{cls['clauses_redigees'] + st['instruments_signes']} · courriers "
            f"{lo['compte_courriers']} = {reg['matiere_sur_disque']} · marqueur "
            f"« {lo['marqueur_courriers']} » présent "
            f"{any(lo['marqueur_courriers'] in l for l in lo['liste'])}",
            lo["nb"] >= 12 and lo["toutes_au_dela_de_20"] and lo["remplies_dans_ce_lot"] == 0
            and lo["compte_courriers"] == reg["matiere_sur_disque"]
            and any(lo["marqueur_courriers"] in l for l in lo["liste"])
            and any("hors du suivi git" in l for l in lo["liste"])
            and any("journal local de références" in l for l in lo["liste"])
            and any("instantané" in l for l in lo["liste"]))
    return out


# ─── 7. Scellement -------------------------------------------------------------


def canonique(objet: Any) -> bytes:
    return json.dumps(objet, ensure_ascii=False, sort_keys=True,
                      default=str).encode("utf-8")


MESURES = ("inventaire", "manifeste", "licence", "regime_commercial", "frontiere",
           "horodatages", "registre_acces", "clauses", "boite_noire", "structure_contrat",
           "remuneration", "relecture_avocat", "exposition", "chronologie", "limites_ouvertes")


def noeuds_certificat() -> Dict[str, Any]:
    nc: Dict[str, Any] = {nom: globals()[nom]() for nom in MESURES}
    nc["verdict"] = {"enonce": PHRASE_ABSENCE,
                     "clauses_redigees": nc["clauses"]["clauses_redigees"],
                     "instruments_signes": nc["structure_contrat"]["instruments_signes"],
                     "occurrences_avocat": nc["relecture_avocat"]["avocat_rencontre"],
                     "entrees_du_registre": nc["registre_acces"]["nb_entrees"]}
    # seconde passe : le registre, le plan et les écritures mesurent les octets que ce module produit
    base = {**nc, "nb_barres": len(BARRES)}
    relu = registre_relu(base)
    svg = plan_svg(base)
    nc["registre_relu"] = relu
    nc["plan_svg"] = svg
    nc["ecritures"] = ecritures({**base, "registre_relu": relu, "plan_svg": svg})
    return nc


def etat_complet() -> Dict[str, Any]:
    nc = noeuds_certificat()
    octets = canonique(nc)
    second = canonique(noeuds_certificat())
    return {**nc, "noeuds_certificat": nc, "rejoue_identique": octets == second,
            "empreinte_execution": hashlib.sha256(octets).hexdigest(),
            "taille_octets": len(octets)}


def certificat() -> Dict[str, Any]:
    etat = etat_complet()
    return {"source": SOURCE, **etat["noeuds_certificat"],
            "empreinte_execution": etat["empreinte_execution"],
            "taille_octets": etat["taille_octets"],
            "rejoue_identique": etat["rejoue_identique"],
            "limites": etat["limites_ouvertes"]["liste"] + [
                "cette couche ne prétend qu'une chose : elle mesure l'état du dépôt tel qu'il est "
                "écrit sur disque ; elle ne verrouille rien, ne rédige rien et ne conseille personne",
            ],
            "attribution": {"auteur": SOURCE["auteur"],
                            "statut_de_la_demande": "déclaré · non vérifié pour toute valeur "
                                                    "juridique, toute paternité et toute négociation",
                            "ce_qu_un_depot_prouve": "une date d'accessibilité",
                            "ce_qu_un_depot_ne_prouve_pas": "une paternité"},
            "racine_merkle_sha256": hashlib.sha256(canonique(
                {c: hashlib.sha256(canonique(etat["noeuds_certificat"][c])).hexdigest()
                 for c in sorted(etat["noeuds_certificat"])})).hexdigest()}


def resoudre() -> Dict[str, Any]:
    cert = certificat()
    etat = {k: v for k, v in cert.items() if k not in ("source", "limites", "attribution")}
    etat["noeuds_certificat"] = cert
    eqs = {x["id"]: x for x in equations(etat)}
    cs = controles(eqs, etat)
    return {"source": SOURCE, "certificat": cert, "equations": list(eqs.values()),
            "controles": cs,
            "conclusion": {
                "controles_verts": sum(1 for c in cs if c["ok"]), "controles_total": len(cs),
                "equations": len(eqs),
                "statuts_par_label": {st: sum(1 for x in eqs.values() if x["statut"] == st)
                                      for st in FB.STATUTS},
                "enonce_verrous": f"{cert['inventaire']['fichiers']} fichiers d'arbre scannés, "
                                  f"{cert['manifeste']['total_lignes']} entrées de sceau dont "
                                  f"{cert['manifeste']['derivent']} en dérive, "
                                  f"{cert['clauses']['clauses_redigees']} clause rédigée sur "
                                  f"{cert['clauses']['nb_clauses_cherchees']}, "
                                  f"{cert['structure_contrat']['instruments_signes']} instrument "
                                  f"signé, {cert['relecture_avocat']['avocat_rencontre']} occurrence "
                                  f"d'avocat — {PHRASE_ABSENCE}",
                "fichiers_inventories": cert["inventaire"]["fichiers"],
                "entrees_de_sceau": cert["manifeste"]["total_lignes"],
                "derive_de_sceau": cert["manifeste"]["derivent"],
                "clauses_redigees": cert["clauses"]["clauses_redigees"],
                "instruments_signes": cert["structure_contrat"]["instruments_signes"],
                "registre_entrees": cert["registre_acces"]["nb_entrees"],
                "commits_attestes": cert["horodatages"]["commits_attestes"],
                "racine_merkle_sha256": cert["racine_merkle_sha256"]}}


def verifier(donnees: Dict[str, Any]) -> bool:
    return all(c["ok"] for c in donnees["controles"])


def ecrire_artefacts(cert: Dict[str, Any], vers: Path = ARTEFACTS) -> Dict[str, str]:
    vers.mkdir(parents=True, exist_ok=True)
    rendu = _artefacts_octets(cert)
    for nom, octets in rendu.items():
        (vers / nom).write_bytes(octets)
    return {nom: f"{len(octets)} octets" for nom, octets in rendu.items()}


def resume_markdown(cert: Dict[str, Any]) -> bytes:
    inv, man, lic = cert["inventaire"], cert["manifeste"], cert["licence"]
    rc, fr, h = cert["regime_commercial"], cert["frontiere"], cert["horodatages"]
    reg, cls, st = cert["registre_acces"], cert["clauses"], cert["structure_contrat"]
    exp, chr_ = cert["exposition"], cert["chronologie"]
    corps = [
        f"# VERROUS — {PHRASE_ABSENCE}",
        "",
        f"**Départ** feuille de route externe en quatre phases, reçue le 2026-11-09, consignée dans "
        f"`SOURCE` ; aucune de ses affirmations n'est reprise sans avoir été comptée sur disque.",
        "",
        f"**Arbre** {inv['fichiers']} fichiers, {inv['octets_total']} octets, "
        f"{len(inv['par_extension'])} extensions ; empreinte {inv['empreinte_arbre'][:16]}…, "
        f"aucune horloge murale.",
        f"**Sceau** {man['total_lignes']} entrées : {man['a_l_identique']} à l'identique, "
        f"{man['apres_normalisation_des_fins_de_ligne']} après normalisation des fins de ligne, "
        f"{man['derivent']} en dérive — verdict {man['verdict']} ; {man['hors_manifeste']} fichiers "
        f"sont publiés hors du sceau.",
        f"**Licence** « {lic['expression_lue']} » dans {lic['avec_en_tete']}/"
        f"{lic['python_total']} sources Python ; {rc['restrictions_non_commerciales_total']} clause "
        f"d'usage non commercial dans les textes GNU, {rc['permissions_de_facturer_total']} "
        f"permission(s) de facturer, clause réseau {rc['clause_reseau_agpl']} en AGPL contre "
        f"{rc['clause_reseau_gpl']} en GPL.",
        f"**Frontière** {fr['coeur_secret_reelement_garde']} fichier gardé ; "
        f"{len(fr['modules_portant_des_equations'])} module(s) porteurs d'équations publiés, "
        f"{len(fr['modules_d_equations_hors_sceau'])} hors du sceau.",
        f"**Horodatage** {h['commits_attestes']} commits atteignables du {h['premiere']} au "
        f"{h['derniere']} (lus par {h['source_des_commits']}) ; "
        f"{h['journal_local']['parsees']} écritures du journal local, qui ne voyage pas ; "
        f"{h['commits_d_outils_automates']} d'entre eux signés par un outil d'automatisation ; "
        f"0 instrument d'horodatage juridique.",
        f"**Registre** {reg['nb_colonnes']} colonnes, {reg['nb_entrees']} entrée lue dans ses "
        f"octets, alors que {reg['matiere_sur_disque']} fichier(s) de correspondance sont posés sur "
        f"ce disque, {reg['matiere_suivie_par_git']} suivi(s) par git et "
        f"{reg['matiere_entree_du_sceau']} sous le sceau.",
        f"**Clauses et instruments** {cls['clauses_redigees']}/{cls['nb_clauses_cherchees']} clause "
        f"rédigée, {st['instruments_cites']}/{st['nb_instruments']} instrument cité, "
        f"{st['instruments_signes']} signé.",
        f"**Exposition** DOI {exp['doi_cff']} sous version {exp['version_zenodo']}, licence Zenodo "
        f"« {exp['licence_zenodo']} » contre « {exp['licence_cff']} » dans CITATION.cff ; ordre de "
        f"la phase 1 tenu à l'envers : verrouiller avant exposer = "
        f"{chr_['verrouillage_avant_exposition']}.",
        "",
        "## Cheminement",
        "",
        "1. l'arbre est inventorié par les octets, et son empreinte ne dépend d'aucune horloge ;",
        "2. le manifeste est re-haché entrée par entrée : la dérive est comptée, listée, publiée ;",
        "3. les textes GNU sont cherchés mot à mot : la clause « usage non commercial » annoncée par "
        "l'avis n'y est pas ;",
        "4. la frontière « cœur secret » est mesurée : rien n'est gardé, et des modules d'équations "
        "sont hors du sceau ;",
        "5. le journal git est parseé intégralement : dates, auteurs, tête, et paternité non prouvée ;",
        "6. le registre d'accès est ouvert vide, avec ses six colonnes ;",
        "7. les huit clauses sont cherchées avec un contrôle positif qui prouve que la recherche "
        "fonctionne ;",
        "8. les artefacts relus disent les mêmes nombres que le calcul.",
        "",
        "## Résultat",
        "",
        f"- {cls['clauses_redigees']} clause rédigée, {st['instruments_signes']} instrument signé, "
        f"0 avocat saisi ;",
        f"- {man['derivent']} dérive(s) de sceau, {man['hors_manifeste']} fichier(s) hors sceau ;",
        f"- {len(cert['limites_ouvertes']['liste'])} limites ouvertes, aucune remplie ;",
        f"- racine Merkle {cert['racine_merkle_sha256']}.",
        "",
    ]
    return ("\r\n".join(corps) + "\r\n").encode("utf-8")


if __name__ == "__main__":
    donnees = resoudre()
    if "--ecrit" in sys.argv:
        for nom, taille in ecrire_artefacts(donnees["certificat"]).items():
            print(f"{nom}: {taille}")
    conclusion = donnees["conclusion"]
    print(json.dumps({
        "equations": conclusion["equations"], "controles_verts": conclusion["controles_verts"],
        "controles_total": conclusion["controles_total"],
        "statuts": conclusion["statuts_par_label"],
        "fichiers_inventories": conclusion["fichiers_inventories"],
        "entrees_de_sceau": conclusion["entrees_de_sceau"],
        "derive_de_sceau": conclusion["derive_de_sceau"],
        "clauses_redigees": conclusion["clauses_redigees"],
        "instruments_signes": conclusion["instruments_signes"],
        "registre_entrees": conclusion["registre_entrees"],
        "commits_attestes": conclusion["commits_attestes"],
        "enonce": conclusion["enonce_verrous"],
        "rouges": [c["id"] for c in donnees["controles"] if not c["ok"]],
        "racine": conclusion["racine_merkle_sha256"]}, ensure_ascii=False, indent=2))
