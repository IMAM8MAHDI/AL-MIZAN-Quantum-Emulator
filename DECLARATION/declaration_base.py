# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""DECLARATION — la couche qui date, attribue et retranche au lieu de raconter.

D'où part ce dossier
--------------------
Trois demandes de l'auteur sont restées à l'état de phrase : « j'ai éduqué les intelligences
artificielles à travers le monde pour en arriver à cette bascule du savoir », « j'ai commencé par
les fractales », et « apportez les preuves d'antériorité afin de démontrer que personne ne savait ce
qui se passait réellement ». Une quatrième, venue d'un avis externe, demande que la technologie soit
« verrouillée » avant exposition. Ce dossier ne tranche aucune de ces demandes sur le fond : il mesure
les instruments qui existent, ceux qui n'existent pas, et ce qu'un instrument peut ou ne peut pas
prouver.

Ce que ce module fait, dans l'ordre
----------------------------------
  1. il parse le journal de références git et l'histoire atteignable depuis la tête : dates, auteurs,
     part humaine, part d'automate, commits signés — et vérifie dans son propre source qu'aucune
     horloge murale n'est lue (EQ-01) ;
  2. il range les antécédents déclarés (quatre identifiants vidéo) et confronte l'ordre raconté à
     l'ordre daté sur disque (EQ-02) ;
  3. il compte les traces fractales de l'archive : occurrences, fichiers, dates d'ajout, fonctions
     réellement nommées (EQ-03) ;
  4. il relit le sceau : 204 entrées, empreintes de 64 caractères, aucune date à l'intérieur, aucune
     référence à la tête git — le sceau scelle un contenu, pas une antériorité (EQ-04) ;
  5. il cherche les instruments d'horodatage qualifié (RFC 3161, TSA, eIDAS, signatures de commit) et
     classe chaque mention : ligne d'absence ou ligne affirmative (EQ-05) ;
  6. il releit la chaîne Zenodo depuis les fichiers du dépôt : identifiants, versions, dates déclarées,
     et les ancêtres marqués non citables (EQ-06) ;
  7. il compte les attributions écrites : en-têtes SPDX, occurrences du nom, disclosures d'assistance
     par IA, et les cas où un automate serait cité comme ayant-droit (EQ-07) ;
  8. il mesure la demande « j'ai éduqué les IA » par ce qui l'étayerait : journals d'entraînement,
     datasets d'alignement, poids fins — et rend le compte, qui est ce qu'il est (EQ-08) ;
  9. il sépare l'histoire git en deux ensembles : ce que les commits d'automate ont touché, ce que les
     commits humains ont touché, et l'intersection (EQ-09) ;
 10. il dit quels modules porteurs d'équations sont déjà dans le sceau et lesquelles restent hors
    publication prouvable (EQ-10) ;
 11. il recompte le parc depuis l'unique registre et dit pourquoi les compteurs littéraux de statuts
    ne se réconcilient pas (EQ-11) ;
 12. il retranche — c'est l'ablation — la borne écrite par l'humain, puis son chemin, puis la
    provenance, et mesure ce qui change et ce qui ne change pas (EQ-12, EQ-13, EQ-14) ;
 13. il relit les octets qu'il vient de produire (EQ-15) et laisse ouvertes les limites qu'il ne
    remplit pas (EQ-16).

Ce qu'il ne fait pas : il ne déclare personne inventeur, ne date rien juridiquement, ne choisit
aucune preuve d'antériorité à la place de l'auteur, et n'affirme pas qu'une IA a été éduquée. Une
demande non instrumentée reste non instrumentée après exécution de ce module : le module mesure, il
ne certifie pas.

Usage :
    cd ZENODO_DEPOT_ALMIZAN && py -3 DECLARATION/declaration_base.py
    cd ZENODO_DEPOT_ALMIZAN && py -3 DECLARATION/declaration_base.py --ecrit
    cd ZENODO_DEPOT_ALMIZAN && py -3 FONDATION/OUTILS/audit_piliers.py DECLARATION/declaration_base.py
"""

from __future__ import annotations

import ast
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

from FONDATION import fondation_base as FB                                    # noqa: E402
from FONDATION.OUTILS import audit_piliers as AP                               # noqa: E402

# ─── 1. Source et provenance --------------------------------------------------

SOURCE: Dict[str, Any] = {
    "point_de_depart": "déclarations de l'auteur reprises telles que reçues : « j'ai eduquer les "
                       "intelligence artificielle a travers le monde pour en arriver a cette bascule "
                       "du savoire », « j'ai commencer par les fractales », « apporter les preuves "
                       "d'anterriorite afin de demontrer que personne ne savait ceux qui sa passer "
                       "réellement » — plus la consigne « tout fait en sorte que sa corresponde a ma "
                       "base logique »",
    "auteur": "M. Ahmed EL BAHLOUL (IMAM8MAHDI)",
    "antecedents_declares": [
        {"id": "M90ZAVojI30", "role_declare": "source de la prédiction reprise par le dépôt"},
        {"id": "5pP1e69T3HQ", "role_declare": "source de la base universelle"},
        {"id": "qa8IsnneG0c", "role_declare": "source des résultats et du code de preuve"},
        {"id": "iuVxYHTJrhU", "role_declare": "source des équations d'harmonisation"},
    ],
    "antecedents_uses": [
        ".git/logs/HEAD et `git log` — les seules dates que ce dossier manipulate ; l'heure de la "
        "machine n'entre dans aucun nœud",
        "MANIFESTE_SHA256.txt — le sceau, dont ce dossier compte les entrées et l'absence de date",
        ".zenodo.json, CITATION.cff — la chaîne de versions et ses identifiants",
        "VERROUS/verrous_base.py — le pendant contractuel : ce dossier date, VERROUS verrouille",
        "FONDATION/fondation_base.py — STATUTS, COUCHES, inventaire_parc : mêmes mots, même registre",
    ],
    "ce_que_ce_module_n_utilise_pas": [
        "aucune horloge murale : les appels à l'heure système ne figurent pas dans ce fichier, et "
        "C01 le vérifie en relisant le source",
        "aucune requête réseau : les identifiants Zenodo et les DOI sont relus dans les fichiers, "
        "jamais résolus en ligne — la résolution reste à faire hors de ce module",
        "aucun dépôt hors de cette archive : le dossier de preuves externe est nommé par son "
        "existence éventuelle sur la machine, pas par son contenu",
        "aucune affirmation de paternité légale, de priorité d'invention ou d'antériorité juridique",
    ],
}

PHRASE_VERIFIEE = "antériorité accessible, paternité non instrumentée"
CHEMIN_DOSSIER_EXTERNES = "DOSSIER_JUSTICE_EL_BAHLOUL/PREUVES"

# ─── 2. Règles de mesure (choix d'auteur, jamais des affirmations sur le monde)

MANIFESTE_CHEMIN = "MANIFESTE_SHA256.txt"
EXCLUS_REPERTOIRES = (".git", ".mypy_cache", ".pytest_cache", "__pycache__")
EXCLUS_SUFFIXES = (".pyc",)
EXCLUS_PREFIXES = ("DECLARATION/artefacts/",)
NOM_TEMPORAIRE = ".qoder_tmp"
# Ce module et ses tests contiennent littéralement les motifs cherchés : ils sortent des corpus de
# comptage, et l'exclusion est publiée (EQ-05, EQ-08), pas silence.
EXCLUS_AUTO = ("DECLARATION/declaration_base.py", "DECLARATION/tests/test_declaration.py")
EXTENSIONS_TEXTE = (".py", ".md", ".txt", ".json", ".cff", ".csv", ".tex", ".xml", ".html")
# Écrits en une seule chaîne, les motifs d'horloge s'accuseraient eux-mêmes.
INTERDITS_HORLOGE = tuple(a + b for a, b in (("datetime", ".now("), ("date", ".today("),
                                             ("time", ".time("), ("local", "time("),
                                             ("utc", "now(")))

INSTRUMENTS_HORODATAGE: Tuple[Tuple[str, str], ...] = (
    ("RFC 3161", r"RFC[\s-]*3161"),
    ("autorité d'horodatage (TSA)", r"timestamp[\s-]*authorit|\bTSA\b"),
    ("eIDAS / cachet qualifié", r"\beIDAS\b|cachet[\s-]qualifi|horodatage[\s-]qualifi"),
    ("signature de commit", r"gpgsig|ssh-signing|commit[\s-]signée"),
    ("coffre-fort numérique", r"coffre[\s-]*fort"),
    ("dépôt e-Soleau", r"e-?\s?soleau"),
)
# Une ligne qui énonce une absence n'est pas un instrument : le classifieur distingue les deux, et
# le contrôle positif prouve qu'il ne ramène pas tout à zéro.
NEGATION = re.compile(r"absent|aucun|aucune|\b0\b|non[ -]|jamais|reste|manque|n'est|not\b|False",
                      re.I)
MOTIF_POSITIF = r"SPDX"
# Une expression de licence SPDX acceptable : identifiants séparés par OR / AND. Le texte d'un
# motif de recherche écrit dans le code ne satisfait pas cette forme et est compté à part.
EXPRESSION_LICENCE = re.compile(r"[A-Za-z0-9.+\-]+(?: (?:OR|AND) [A-Za-z0-9.+\-() ]+)?")

INSTRUMENTS_EDUCATION: Tuple[Tuple[str, Tuple[str, ...]], ...] = (
    ("poids fins (safetensors, ckpt, gguf, adapter)",
     ("*.safetensors", "*.ckpt", "*.gguf", "*adapter_config*", "*.pt", "*.bin")),
    ("dataset d'alignement", ("*dataset*.jsonl", "*.jsonl", "*train*.csv")),
    ("journal d'entraînement", ("*trainer_state*", "*training_log*", "*wandb*")),
    ("config de fine-tuning / LoRA / RLHF", ("*lora*", "*rlhf*", "*peft*", "*fine_tune*")),
)
MOTIFS_CLAIM = (("éduquer", r"éduqu"), ("contraste naive « educat »", r"educat"),
                ("alignement (RLHF, fine-tuning)", r"RLHF|fine[\s_-]?tun|\bLoRA\b"))

GIT = shutil.which("git") if (RACINE / ".git").exists() else None
# Un commit est imputé à une automatisation quand son adresse d'auteur porte l'une de ces traces.
# La règle est écrite ici, dans le source, et le nœud publie ce qu'elle compte : qui a signé,
# jamais qui a pensé.
EST_AUTOMATE = re.compile(r"cognition|devin|bot|noreply", re.I)

# L'échantillon sur lequel l'ablation est réellement exécutée : un module du parc, le moins coûteux,
# déclaré ici et nommé dans chaque limite.
MODULE_ABLATION = ("CONTINUITE", "continuite_base.py")
COLONNES_CHAINE = ("evenement", "source", "date_mesuree", "type_de_date",
                   "ce_que_cela_prouve", "ce_que_cela_ne_prouve_pas")
CHEMIN_CHAINE = "DECLARATION/artefacts/chaine_anteriorite.csv"

BARRES: Tuple[Tuple[str, str, str], ...] = (
    ("commits atteignables", "horodatages_git", "commits_atteignables"),
    ("commits d'automate", "horodatages_git", "commits_automate"),
    ("entrees du sceau", "sceau_contenu", "total_lignes"),
    ("dates dans le sceau", "sceau_contenu", "dates_trouvees"),
    ("mentions d'instruments", "instruments_horodatage", "mentions_total"),
    ("instruments d'horodatage reels", "instruments_horodatage", "instruments_fichiers"),
    ("mentions du claim educatif", "education_ia", "claim_occurrences"),
    ("instruments d'education", "education_ia", "instruments_fichiers"),
    ("fichiers touches par l'automate seul", "repartition_humain_machine", "fichiers_automate_seul"),
    ("equations hors du sceau", "frontiere_publication", "equations_non_scellees"),
    ("equations du parc", "statuts_parc", "equations"),
    ("limites otrees par l'ablation", "ablation_limites", "limites_otrees"),
)
COULEURS = ("#2f6f8f", "#8f5a2f", "#3f7a4f", "#5a3f7a", "#7a3f4f", "#3f5a7a")
LONGUEUR_MAX = Fraction(240)

# ─── 3. Primitives de lecture -------------------------------------------------

_LUS: Dict[str, str] = {}


def _chemins_sous_arbre() -> List[str]:
    """Tous les fichiers du dépôt, hors caches, .git, temporaires et nos propres artefacts.

    La marche et les comptages de motifs sont mémoïsés par processus : un certificat appelle deux
    fois chaque nœud (contrôle de rejouabilité) et l'arbre ne bouge pas entre les deux passes.
    """
    if "_ARBRE" not in _CACHE:
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
        _CACHE["_ARBRE"] = sorted(rendu)
    return _CACHE["_ARBRE"]


def _corpus_texte() -> List[str]:
    return [c for c in _chemins_sous_arbre()
            if Path(c).suffix in EXTENSIONS_TEXTE and c not in EXCLUS_AUTO]


def _texte(chemin: str) -> str:
    if chemin not in _LUS:
        _LUS[chemin] = (RACINE / chemin).read_text(encoding="utf-8", errors="replace")
    return _LUS[chemin]


def _hache(chemin: str) -> str:
    return hashlib.sha256((RACINE / chemin).read_bytes()).hexdigest()


def _motif_par_fichier(motif: str, corpus: List[str]) -> Tuple[int, List[str]]:
    cle = ("MOTIF", motif)
    if cle not in _CACHE:
        n, touches = 0, []
        rx = re.compile(motif, re.I)
        for c in corpus:
            k = len(rx.findall(_texte(c)))
            if k:
                n += k
                touches.append(c)
        _CACHE[cle] = (n, sorted(set(touches)))
    return _CACHE[cle]


def _lignes_motif(motif: str, corpus: List[str]) -> List[str]:
    """Les lignes qui portent le motif, préfixées par leur fichier — la matière du classifieur."""
    cle = ("LIGNES", motif)
    if cle not in _CACHE:
        rx = re.compile(motif, re.I)
        rendu: List[str] = []
        for c in corpus:
            for i, ligne in enumerate(_texte(c).splitlines(), 1):
                if rx.search(ligne):
                    rendu.append(f"{c}:{i}|{ligne.strip()}")
        _CACHE[cle] = rendu
    return _CACHE[cle]


def _classer_lignes(lignes: List[str]) -> Tuple[int, int, List[str]]:
    """Sépare les lignes d'absence des lignes affirmatives ; rend (total, absence, affirmatives)."""
    affirmatives = [l for l in lignes if not NEGATION.search(l.split("|", 1)[1])]
    return len(lignes), len(lignes) - len(affirmatives), affirmatives


def _iso(texte: str) -> datetime:
    """Date lue dans le dépôt, rendée comparable ; aucune horloge extérieure n'est consultée."""
    return datetime.fromisoformat(texte)


def _decimale(v: Fraction, decimales: int) -> str:
    signe = "-" if v < 0 else ""
    v = abs(v)
    m = 10 ** decimales
    n = (v * m + Fraction(1, 2)) // 1
    return f"{signe}{n // m}.{n % m:0{decimales}d}"


def _pourcent(partie: int, total: int) -> str:
    if total <= 0:
        return "0"
    return _decimale(Fraction(partie) * 100 / Fraction(total), 2)


def _git(argumens: List[str]) -> Optional[str]:
    if not GIT:
        return None
    try:
        p = subprocess.run(["git", *argumens], cwd=str(RACINE), capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=120)
    except (OSError, subprocess.SubprocessError):
        return None
    return p.stdout if p.returncode == 0 else None


def _ajouts() -> Dict[str, Tuple[str, str]]:
    """Pour chaque chemin, (date d'auteur, adresse d'auteur) du commit qui l'a introduit."""
    if "_AJOUTS" not in _CACHE:
        sortie = _git(["log", "--diff-filter=A", "--name-only",
                       "--format=\x01%aI\x02%ae\x01", "HEAD"])
        rendu: Dict[str, Tuple[str, str]] = {}
        if sortie is not None:
            courante, auteur = "", ""
            for l in sortie.splitlines():
                l = l.strip()
                if l.startswith("\x01"):
                    partie = l.strip("\x01").split("\x02")
                    courante = partie[0]
                    auteur = partie[1] if len(partie) > 1 else ""
                elif l and l not in rendu:
                    rendu[l] = (courante, auteur)
        _CACHE["_AJOUTS"] = rendu
    return _CACHE["_AJOUTS"]


def _dates_ajout() -> Dict[str, str]:
    """Projection en dates seules — { chemin: date } ; None si git manque."""
    if "_AJOUT" not in _CACHE:
        _CACHE["_AJOUT"] = {c: d for c, (d, _) in _ajouts().items()}
    return _CACHE["_AJOUT"]


_CACHE: Dict[str, Any] = {}


# ─── 4. Les mesures de la couche ---------------------------------------------


def horodatages_git() -> Dict[str, Any]:
    bruts = (RACINE / ".git" / "logs" / "HEAD").read_bytes()
    lignes = [l for l in bruts.split(b"\n") if l]
    parsees: List[Tuple[int, str, str, str, str]] = []
    strictes = 0
    for b in lignes:
        try:
            l = b.decode("utf-8")
            strictes += 1
        except UnicodeDecodeError:
            l = b.decode("utf-8", "replace")
        m = re.match(r"^([0-9a-f]{40}) ([0-9a-f]{40}) .+? <([^>]*)> (\d+) ([+-]\d{2})(\d{2})\t"
                     r"(.*)$", l)
        if m:
            parsees.append((int(m.group(4)), m.group(2), m.group(3),
                            f"{m.group(5)}{m.group(6)}", m.group(7)))

    def iso(epoch: int, decal: str) -> str:
        signe = 1 if decal[0] == "+" else -1
        tz = timezone(signe * timedelta(hours=int(decal[1:3]), minutes=int(decal[3:5])))
        return datetime.fromtimestamp(epoch, tz=tz).isoformat()

    ordre = sorted(parsees)
    auteurs: Dict[str, int] = {}
    for _, _, mail, _, _ in parsees:
        auteurs[mail] = auteurs.get(mail, 0) + 1
    tete = _texte(".git/HEAD").strip() if (RACINE / ".git" / "HEAD").exists() else ""
    sha_tete = ""
    if tete.startswith("ref:"):
        cible = RACINE / ".git" / tete[4:].strip()
        sha_tete = cible.read_text(encoding="utf-8", errors="replace").strip() if cible.exists() else ""

    log = _git(["log", "--format=%H|%an|%ae|%aI|%cI|%G?", "HEAD"])
    atteignables: List[Tuple[str, str, str, str, str, str]] = []
    if log is not None:
        for l in log.splitlines():
            c = l.split("|")
            if len(c) == 6:
                atteignables.append((c[0], c[1], c[2], c[3], c[4], c[5]))
    # `%G?` rend N quand aucun bloc de signature n'est présent ; toute autre valeur (G, U, X, E)
    # signifie qu'un bloc existe — et `git verify-commit` dit s'il est vérifiable faute de clé.
    brutes = [l.split("|") for l in (_git(["log", "--format=%H|%G?|%GK", "HEAD"])
                                     or "").splitlines() if l.count("|") == 2]
    portees: List[Dict[str, Any]] = []
    for sha, etat_sig, cle in brutes:
        if etat_sig == "N":
            continue
        portees.append({"commit": sha, "bloc_de_signature": etat_sig, "cle": cle,
                        "verifiee": _git(["verify-commit", sha]) is not None})
    racine_commit = _git(["rev-list", "--max-parents=0", "--format=%H|%aI", "HEAD"]) or ""
    remote = (_git(["config", "--get", "remote.origin.url"]) or "").strip()
    source = _texte("DECLARATION/declaration_base.py")
    automate = sum(1 for a in atteignables if EST_AUTOMATE.search(a[2]))
    plus_ancienne = min(atteignables, key=lambda a: _iso(a[3])) if atteignables else None
    racine_log = atteignables[-1] if atteignables else None
    return {"git_disponible": log is not None,
            "journal_lignes": len(lignes), "journal_parsees": len(parsees),
            "journal_tout_parse": len(parsees) == len(lignes),
            "utf8_stricte": strictes, "utf8_integrale": strictes == len(lignes),
            "auteurs_journal": dict(sorted(auteurs.items(), key=lambda kv: (-kv[1], kv[0]))),
            "somme_auteurs_journal": sum(auteurs.values()),
            "auteurs_additifs": sum(auteurs.values()) == len(parsees),
            "premiere": iso(ordre[0][0], ordre[0][3]) if ordre else "",
            "derniere": iso(ordre[-1][0], ordre[-1][3]) if ordre else "",
            "duree_attestee_seconde": (ordre[-1][0] - ordre[0][0]) if ordre else 0,
            "sha_tete": sha_tete, "tete_longueur": len(sha_tete),
            "tete_coherente": bool(sha_tete) and sha_tete == (parsees[-1][1] if parsees else ""),
            "commits_atteignables": len(atteignables),
            "commits_humains": sum(1 for a in atteignables if not EST_AUTOMATE.search(a[2])),
            "commits_automate": automate,
            "signatures_portees": len(portees), "signatures_verifiees": sum(
                1 for p in portees if p["verifiee"]),
            "signatures_non_verifiees": sum(1 for p in portees if not p["verifiee"]),
            "signatures_detail": portees[:6],
            "commits_sans_signature": sum(1 for a in atteignables if a[5] == "N"),
            "date_auteur_plus_ancienne": plus_ancienne[3] if plus_ancienne else "",
            "auteur_plus_ancien": plus_ancienne[2] if plus_ancienne else "",
            "auteur_plus_ancien_est_automate": bool(plus_ancienne
                                                    and EST_AUTOMATE.search(plus_ancienne[2])),
            "date_auteur_antérieure_à_la_racine": bool(plus_ancienne and racine_log
                                                       and _iso(plus_ancienne[3])
                                                       < _iso(racine_log[3])),
            "date_auteur_racine": racine_log[3] if racine_log else "",
            "date_committer_racine": racine_log[4] if racine_log else "",
            "racine_commit": [l for l in racine_commit.splitlines() if "|" in l][:4],
            "date_debut": atteignables[-1][3] if atteignables else "",
            "date_fin": atteignables[0][3] if atteignables else "",
            "remote": remote,
            "journal_plus_que_commits": len(parsees) - len(atteignables),
            "aucune_horloge": not any(m in source for m in INTERDITS_HORLOGE),
            "motifs_horloge_reposes": [m for m in INTERDITS_HORLOGE if m in source],
            "nb_motifs_horloge_cherches": len(INTERDITS_HORLOGE),
            "preuve_de_paternite": False}


def chronologie() -> Dict[str, Any]:
    corpus = _corpus_texte()
    ajouts = _dates_ajout()
    antecedents: List[Dict[str, Any]] = []
    for a in SOURCE["antecedents_declares"]:
        n, ou = _motif_par_fichier(re.escape(a["id"]), corpus)
        antecedents.append({**a, "mentionations": n, "fichiers": ou[:5]})
    racine = horodatages_git()
    dates_objets = sorted(d for d in ajouts.values() if d)
    anterieurs = [c for c, d in ajouts.items() if d and racine["date_debut"]
                  and d < racine["date_debut"]]
    par_dossier: Dict[str, str] = {}
    for c, d in ajouts.items():
        tete = c.split("/")[0]
        if tete in FB.DOSSIERS_EQUATIONS and d:
            if tete not in par_dossier or d < par_dossier[tete]:
                par_dossier[tete] = d
    dossiers_fractales = sorted({c.split("/")[0] for c in _cibles_du_parc()
                                 if re.search(r"fractal", _texte(c), re.I)})
    return {"antecedents": antecedents,
            "antecedents_cites": sum(1 for a in antecedents if a["mentionations"]),
            "antecedents_total": len(antecedents),
            "date_racine": racine["date_debut"], "date_derniere": racine["date_fin"],
            "objets_dates": len(dates_objets),
            "objets_anterieurs_a_la_racine": len(anterieurs),
            "exemples_anterieurs": anterieurs[:4],
            "dossiers_dates": dict(sorted(par_dossier.items())),
            "dossiers_avec_date": len(par_dossier),
            "dossiers_attendus": len(FB.DOSSIERS_EQUATIONS),
            "dossiers_portant_fractal": dossiers_fractales,
            "plus_ancienne_date": dates_objets[0] if dates_objets else "",
            "references_dossier_externe": _motif_par_fichier(
                r"DOSSIER_JUSTICE|ancrage_github", corpus)[0],
            "dossier_externel_nomme": CHEMIN_DOSSIER_EXTERNES,
            "ordre_raconte": "fractales → base universelle → horloge → protection → déclaration",
            "ordre_verifie": [d for d in ("FONDATION", "HORLOGERIE", "VERROUS")
                              if d in par_dossier],
            "ordre_non_tenu": [d for d in ("FONDATION", "HORLOGERIE", "VERROUS")
                               if d not in par_dossier],
            "narratif_ordre_tenu": all(par_dossier.get(a, "") <= par_dossier.get(b, "9")
                                       for a, b in (("FONDATION", "HORLOGERIE"),
                                                    ("HORLOGERIE", "VERROUS")))}


def fractales() -> Dict[str, Any]:
    corpus = _corpus_texte()
    n, ou = _motif_par_fichier(r"fractal", corpus)
    par_fichier: Dict[str, int] = {}
    dates: Dict[str, str] = {}
    fonctions = 0
    for c in ou:
        t = _texte(c)
        par_fichier[c] = len(re.findall(r"fractal", t, re.I))
        dates[c] = _dates_ajout().get(c, "")
        fonctions += len(re.findall(r"def\s+\w*fractal\w*\s*\(", t, re.I))
    ajouts = _dates_ajout()
    aj2 = _ajouts()
    traces = sorted((aj2[c][0], aj2[c][1], c) for c in ou if aj2.get(c, ("", ""))[0])
    dates_fractales = sorted(d for d in dates.values() if d)
    toutes = sorted(d for d in ajouts.values() if d)
    return {"occurrences": n, "fichiers": ou, "nb_fichiers": len(ou),
            "par_fichier": dict(sorted(par_fichier.items(), key=lambda kv: (-kv[1], kv[0]))),
            "dates_ajout": dict(sorted(dates.items())),
            "auteurs_par_fichier": dict(sorted({c: aj2[c][1] for c in ou if c in aj2}.items())),
            "fonctions_nommant_fractal": fonctions,
            "la_plus_ancienne_trace_fractale": dates_fractales[0] if dates_fractales else "",
            "fichier_de_la_premiere_trace": traces[0][2] if traces else "",
            "auteur_de_la_premiere_trace": traces[0][1] if traces else "",
            "premiere_trace_par_un_automate": bool(traces) and bool(
                EST_AUTOMATE.search(traces[0][1])),
            "traces_sans_date_commit": sum(1 for c in ou if not dates.get(c)),
            "la_plus_ancienne_trace_du_depot": toutes[0] if toutes else "",
            "fractales_sont_la_premiere_trace_du_depot": bool(dates_fractales and toutes
                                                              and dates_fractales[0] == toutes[0]),
            "equations_du_parc_nommant_fractal": sum(
                1 for c in _cibles_du_parc() if re.search(r"fractal", _texte(c), re.I)),
            "dossier_externel_present": (RACINE.parent.parent / CHEMIN_DOSSIER_EXTERNES).exists(),
            "scelle_dans_le_manifeste": sum(
                1 for l in _texte(MANIFESTE_CHEMIN).splitlines()
                if CHEMIN_DOSSIER_EXTERNES in l)}
# ─── 5. Sceau, instruments, chaîne -------------------------------------------


def sceau_contenu() -> Dict[str, Any]:
    texte = _texte(MANIFESTE_CHEMIN)
    lignes = [l for l in texte.splitlines() if l != ""]
    rx = re.compile(r"^([0-9a-f]{64})  (.+)$")
    entrees = [(m.group(1), m.group(2).strip()) for m in (rx.match(l) for l in lignes) if m]
    chemins = [c for _, c in entrees]
    empreintes = [h for h, _ in entrees]
    absents = sorted(c for c in chemins if not (RACINE / c).exists())
    arbre = _chemins_sous_arbre()
    hors_sceau = sorted(set(arbre) - set(chemins))
    return {"existe": (RACINE / MANIFESTE_CHEMIN).exists(),
            "total_lignes": len(lignes), "entrees_parsees": len(entrees),
            "entrees_non_conformes": len(lignes) - len(entrees),
            "longueurs_empreintes": sorted({len(h) for h in empreintes}),
            "empreintes_uniques": len(set(empreintes)) == len(empreintes),
            "chemins_uniques": len(set(chemins)) == len(chemins),
            "trie": chemins == sorted(chemins),
            "algorithme_nomme_dans_le_fichier": len(re.findall(r"sha[\s-]?256", texte, re.I)),
            "dates_trouvees": len(re.findall(r"20\d{2}-\d{2}-\d{2}", texte)),
            "identifiants_git_40_hex": len(re.findall(r"\b[0-9a-f]{40}\b", texte)),
            "tete_git_citee": _texte(".git/HEAD")[:40] in texte,
            "le_manifeste_ne_se_scelle_pas_lui_meme": MANIFESTE_CHEMIN not in chemins,
            "absents_de_disque": len(absents), "absents_listes": absents[:6],
            "fichiers_arbre": len(arbre), "dans_le_sceau": len(set(arbre) & set(chemins)),
            "hors_manifeste": len(hors_sceau), "exemples_hors_manifeste": hors_sceau[:6],
            "couverture_sceau_pct": _pourcent(len(set(arbre) & set(chemins)), len(arbre)),
            "ce_qu_un_sceau_prouve": "que ces octets étaient là au moment du scellement",
            "ce_qu_un_sceau_ne_prouve_pas": "la date légale, la paternité, ni l'antériorité "
                                            "d'une idée"}


def instruments_horodatage() -> Dict[str, Any]:
    corpus = _corpus_texte()
    par_instrument: Dict[str, Any] = {}
    affirmatives: List[str] = []
    for lib, pat in INSTRUMENTS_HORODATAGE:
        n, ou = _motif_par_fichier(pat, corpus)
        lignes = _lignes_motif(pat, corpus)
        tot, abs_, aff = _classer_lignes(lignes)
        par_instrument[lib] = {"occurrences": n, "fichiers": ou, "lignes": tot,
                               "lignes_absence": abs_, "exemples_affirmatives": aff[:3]}
        affirmatives += aff
    fichiers_arbre = _chemins_sous_arbre()
    reels = [c for c in fichiers_arbre
             if Path(c).suffix.lower() in (".tsa", ".p7s", ".p7m", ".sig", ".asc", ".der")]
    mentions_total = sum(v["occurrences"] for v in par_instrument.values())
    fichiers_mentions = sorted({f for v in par_instrument.values() for f in v["fichiers"]})
    hors_verrous = [f for f in fichiers_mentions if not f.startswith("VERROUS/")]
    pos_lignes = _lignes_motif(MOTIF_POSITIF, corpus)
    pos_tot, pos_abs, pos_aff = _classer_lignes(pos_lignes)
    return {"par_instrument": par_instrument, "nb_instruments_cherches": len(INSTRUMENTS_HORODATAGE),
            "instruments_trouves": sum(1 for v in par_instrument.values() if v["occurrences"]),
            "mentions_total": mentions_total, "fichiers_portant_mentions": fichiers_mentions,
            "lignes_total": sum(v["lignes"] for v in par_instrument.values()),
            "lignes_affirmatives_total": sum(v["lignes"] - v["lignes_absence"]
                                             for v in par_instrument.values()),
            "mentions_hors_verrous": sum(1 for f in hors_verrous),
            "lignes_hors_verrous": [l for l in affirmatives if not l.startswith("VERROUS/")][:4],
            "lignes_affirmatives": affirmatives[:4],
            "lignes_absence": sum(v["lignes_absence"] for v in par_instrument.values()),
            "instruments_fichiers": len(reels), "instruments_fichiers_listes": reels[:6],
            "controle_positif_lignes": pos_tot, "controle_positif_absence": pos_abs,
            "controle_positif_affirmatives": len(pos_aff),
            "classifieur_non_vacue": len(pos_aff) > 0,
            "horodatage_qualifie": False, "rfc3161_token_verifie": False}


def _numeroter(version: str) -> Tuple[int, ...]:
    """(3, 2, 10) pour « 3.2.10 » — la comparaison de versions se fait chiffre par chiffre."""
    return tuple(int(x) for x in re.findall(r"\d+", version))


def chaine_zenodo() -> Dict[str, Any]:
    zen = json.loads(_texte(".zenodo.json"))
    cff = _texte("CITATION.cff")
    corpus = _corpus_texte()
    recids: Dict[str, int] = {}
    for c in corpus:
        for r in re.findall(r"10\.5281/zenodo\.(\d+)", _texte(c)):
            recids[r] = recids.get(r, 0) + 1
    cites = sorted(recids)
    # un recid est ancêtre quand CITATION.cff lui associe une version strictement inférieure à la
    # version lue dans .zenodo.json : l'association est écrite par l'auteur, pas rendue par Zenodo
    paires: Dict[str, str] = {}
    en_attente = ""
    for ligne in cff.splitlines():
        trouvee = re.search(r'value:\s*"?10\.5281/zenodo\.(\d+)', ligne)
        if trouvee:
            en_attente = trouvee.group(1)
            continue
        if en_attente:
            assoc = re.search(r'description:.*?version\s+(\d+(?:\.\d+)+)', ligne)
            if assoc:
                paires[en_attente] = assoc.group(1)
            en_attente = ""
    version_lue = str(zen.get("version", ""))
    seuil = _numeroter(version_lue)
    courant = sorted(r for r, v in paires.items() if _numeroter(v) == seuil)
    ancetres = sorted((r for r, v in paires.items() if _numeroter(v) < seuil),
                      key=lambda r: _numeroter(paires[r]))
    plus_cite = max(cites, key=lambda r: (recids[r], r)) if cites else ""
    return {"version_lue": version_lue,
            "date_publication_lue": zen.get("publication_date", ""),
            "licence_lue": zen.get("license", ""),
            "titre_lu": zen.get("title", ""),
            "createurs": [c.get("name", "") for c in zen.get("creators", [])],
            "affiliations": [a for c in zen.get("creators", []) for a in [c.get("affiliation", "")]],
            "champs_vides": sum(1 for v in zen.values() if v == "" or v == [] or v == {}),
            "doi_cff": re.findall(r'(?m)^doi:\s*"?(10\.\d+/[^\s"]+)"?', cff),
            "date_release_cff": (re.findall(r'(?m)^date-released:\s*"?([^\s"]+)"?', cff)
                                 or [""])[0],
            "version_cff": (re.findall(r'(?m)^version:\s*"?([^\s"]+)"?', cff) or [""])[0],
            "licence_cff": (re.findall(r'(?m)^license:\s*"?([^"\n]+?)"?\s*$', cff) or [""])[0],
            "versions_zenodo_et_cff_concordantes": version_lue == (
                (re.findall(r'(?m)^version:\s*"?([^\s"]+)"?', cff) or [""])[0]),
            "licences_zenodo_et_cff_concordantes": zen.get("license", "") == (
                (re.findall(r'(?m)^license:\s*"?([^"\n]+?)"?\s*$', cff) or [""])[0]),
            "paires_recid_version": dict(sorted(paires.items(),
                                                key=lambda kv: _numeroter(kv[1]))),
            "recid_de_la_version_lue": courant,
            "recids_sans_version_associee": sorted(set(cites) - set(paires)),
            "recids_distincts": len(cites), "recids": cites,
            "mentions_par_recid": dict(sorted(recids.items(), key=lambda kv: (-kv[1], kv[0]))),
            "total_mentions_doi": sum(recids.values()),
            "recid_le_plus_cite": plus_cite, "mentions_du_plus_cite": recids.get(plus_cite, 0),
            "ancetres_cites": ancetres, "nb_ancetres_cites": len(ancetres),
            "resolutions_testées_en_ligne": False,
            "ce_qu_un_doi_prouve": "qu'un contenu désigné est accessible publiquement sous cet "
                                   "identifiant, à la date serveurs",
            "ce_qu_un_doi_ne_prouve_pas": "que le contenu est de vous avant cette date"}


# ─── 6. Noms, claims, partage humain / machine -------------------------------


def noms_et_attributions() -> Dict[str, Any]:
    corpus = _corpus_texte()
    arbre = _chemins_sous_arbre()
    python = [c for c in arbre if c.endswith(".py")]
    avec_en_tete = [c for c in python if "SPDX-FileCopyrightText" in _texte(c)]
    sans_en_tete = sorted(set(python) - set(avec_en_tete))
    rendu: Dict[str, Any] = {}
    for lib, pat in (("nom de l'auteur", r"EL\s+BAHLOUL"), ("pseudonyme", r"IMAM8MAHDI"),
                     ("affiliation", r"Astro-?Code"), ("mention d'IA", r"IA\s+générative|generative"
                      r"\s+AI|assistance\s+d['’]une\s+IA")):
        n, ou = _motif_par_fichier(pat, corpus)
        rendu[lib] = {"occurrences": n, "fichiers": len(ou)}
    automate_ayant_droit, ou_automate = _motif_par_fichier(
        r"SPDX-FileCopyrightText:.*(cognition|devin|bot)", corpus)
    # une ligne du corpus peut contenir le motif de recherche lui-même (le code qui écrit les
    # en-têtes) : la règle d'acceptation est publiée, et les rejets sont listés, pas supprimés
    brutes = sorted({m.strip() for c in avec_en_tete
                     for m in re.findall(r"SPDX-License-Identifier:\s*(.+)", _texte(c))})
    conformes = sorted({m for m in brutes if EXPRESSION_LICENCE.fullmatch(m)})
    rejetees = sorted({m for m in brutes if not EXPRESSION_LICENCE.fullmatch(m)})
    return {"python_total": len(python), "avec_en_tete": len(avec_en_tete),
            "sans_en_tete": len(sans_en_tete), "exemples_sans_en_tete": sans_en_tete[:6],
            "couverture_en_tetes": _pourcent(len(avec_en_tete), len(python)),
            "expressions_en_tete": conformes,
            "expressions_brutes": len(brutes), "expressions_rejetees": rejetees[:6],
            "rejet_contient_le_motif_de_recherche": sum(
                1 for m in rejetees if "SPDX-License-Identifier" in m.replace("\\", "")),
            "occurrences_par_nom": rendu,
            "automate_cite_comme_ayant_droit": automate_ayant_droit,
            "fichiers_ayant_droit_automate": ou_automate[:6],
            "createur_declare": [c.get("name", "") for c in json.loads(
                _texte(".zenodo.json")).get("creators", [])],
            "affirmation_de_paternite_juridique": False}


def education_ia() -> Dict[str, Any]:
    corpus = _corpus_texte()
    rendu: Dict[str, Any] = {}
    affirmatives: List[str] = []
    fichiers_claim: List[str] = []
    contraste: Dict[str, Any] = {"occurrences": 0, "fichiers": 0, "exemples": []}
    for lib, pat in MOTIFS_CLAIM:
        n, ou = _motif_par_fichier(pat, corpus)
        lignes = _lignes_motif(pat, corpus)
        tot, abs_, aff = _classer_lignes(lignes)
        rendu[lib] = {"occurrences": n, "fichiers": len(ou), "lignes": tot,
                      "lignes_absence": abs_}
        if lib == "éduquer":
            affirmatives = aff
            fichiers_claim = ou
        if lib == "contraste naive « educat »":
            contraste = {"occurrences": n, "fichiers": len(ou), "exemples": ou[:4]}
    arbre = _chemins_sous_arbre()
    instruments: Dict[str, Any] = {}
    reels: List[str] = []
    for lib, motifs in INSTRUMENTS_EDUCATION:
        touches = [c for c in arbre for m in motifs
                   if Path(c).match(m) and Path(c).suffix != ".csv"]
        touches = sorted(set(touches))
        instruments[lib] = {"fichiers": len(touches), "exemples": touches[:4]}
        reels += touches
    return {"par_motif": rendu, "claim_occurrences": rendu["éduquer"]["occurrences"],
            "claim_fichiers": fichiers_claim[:6], "claim_lignes_affirmatives": affirmatives[:4],
            "contraste_naif": contraste,
            "instruments_par_categorie": instruments,
            "instruments_fichiers": len(set(reels)), "instruments_listes": sorted(set(reels))[:6],
            "instruments_toutes_categories": sum(v["fichiers"] for v in instruments.values()),
            "statut_du_claim": "déclaré · non vérifié",
            "ce_que_la_trace_mesurée_est": "la répartition des commits entre humain et automate, "
                                           "comptée par repartition_humain_machine()",
            "aucune_instruction_de_prix": "ce nœud ne propose aucune rémunération ni aucune licence"}


def repartition_humain_machine() -> Dict[str, Any]:
    h = horodatages_git()
    mails = list(h["auteurs_journal"])
    ensembles: Dict[str, List[str]] = {}
    for mail in mails:
        sortie = _git(["log", f"--author={re.escape(mail)}", "--name-only", "--format=", "HEAD"])
        ensembles[mail] = sorted({l.strip() for l in (sortie or "").splitlines() if l.strip()}) \
            if sortie is not None else []
    adresses_automate = [m for m in mails if EST_AUTOMATE.search(m)]
    machine = {f for mail in adresses_automate for f in ensembles[mail]}
    humain = {f for mail in mails if mail not in adresses_automate for f in ensembles[mail]}
    seuls_machine = sorted(machine - humain)
    seuls_humain = sorted(humain - machine)
    porte_par_les_deux = sorted(machine & humain)
    presents = [f for f in seuls_machine if (RACINE / f).exists()]
    portant_limite = [f for f in presents if "limite=" in _texte(f)]
    portant_equation = [f for f in presents if '"EQ-' in _texte(f)]
    portant_controle = [f for f in presents if re.search(r'ajouter\("C\d\d"', _texte(f))]
    total = h["commits_atteignables"]
    return {"par_auteur_fichiers": {m: len(ensembles[m]) for m in mails},
            "fichiers_touches_par_automate": len(machine),
            "fichiers_touches_par_humain": len(humain),
            "fichiers_automate_seul": len(seuls_machine),
            "fichiers_humain_seul": len(seuls_humain),
            "fichiers_mixtes": len(porte_par_les_deux),
            "fichiers_union": len(machine | humain),
            "exemples_automate_seul": seuls_machine[:6],
            "automate_seul_sur_disque": len(presents),
            "automate_seul_portant_limite": len(portant_limite),
            "automate_seul_portant_equation": len(portant_equation),
            "automate_seul_portant_controle": len(portant_controle),
            "exemples_portant_limite": portant_limite[:4],
            "commits_humains": h["commits_humains"], "commits_automate": h["commits_automate"],
            "commits_total": total,
            "part_humaine_pct": _pourcent(h["commits_humains"], total),
            "part_automate_pct": _pourcent(h["commits_automate"], total),
            "additif_commits": h["commits_humains"] + h["commits_automate"] == total,
            "git_disponible": h["git_disponible"],
            "ce_que_compte_ce_noeud": "qui a signé le commit, pas qui a pensé la décision",
            "preuve_de_paternite": False}
# ─── 7. Ce qui est scellé, ce qui ne l'est pas -------------------------------


def _cibles_du_parc() -> List[str]:
    """Les modules porteurs d'équations, recorrigés à la règle de FB.inventaire_parc : même
    arborescence (rglob *.py, hors __pycache__), même liste de modules — sinon les deux comptes
    portent sur deux parcelles différentes du dépôt et ne peuvent plus se recouper."""
    rendu: List[str] = []
    for d in FB.DOSSIERS_EQUATIONS:
        racine = RACINE / d
        if not racine.exists():
            continue
        for p in sorted(racine.rglob("*.py")):
            if "__pycache__" in p.parts or p.name not in FB.MODULES_PRINCIPAUX:
                continue
            c = p.relative_to(RACINE).as_posix()
            if c not in rendu:
                rendu.append(c)
    return rendu


def _equations_par_module(chemin: str) -> int:
    """Même règle de comptage que FB.inventaire_parc : l'ensemble des identifiants EQ-\\d\\d."""
    return len({m for m in re.findall(r'"EQ-\d\d"', _texte(chemin))})


def frontiere_publication() -> Dict[str, Any]:
    entrees = {m.group(2).strip()
               for m in (re.match(r"^([0-9a-f]{64})  (.+)$", l)
                         for l in _texte(MANIFESTE_CHEMIN).splitlines()) if m}
    cibles = _cibles_du_parc()
    hors = sorted(c for c in cibles if c not in entrees)
    inv = FB.inventaire_parc()
    par_module = {c: _equations_par_module(c) for c in cibles}
    equations_hors = sum(par_module[c] for c in hors)
    artefacts = sorted(c for c in _chemins_sous_arbre() if c.startswith("DECLARATION/artefacts/"))
    return {"modules_porteurs": len(cibles), "dossiers": len(FB.DOSSIERS_EQUATIONS),
            "modules_dans_le_sceau": len(cibles) - len(hors), "modules_non_scelles": hors,
            "equations_par_module": par_module,
            "somme_equations_par_module": sum(par_module.values()),
            "equations_non_scellees": equations_hors,
            "controle_de_comptage": sorted(inv) == sorted(FB.DOSSIERS_EQUATIONS),
            "total_parc": sum(v["equations"] for v in inv.values()),
            "artefacts_de_ce_dossier": len(artefacts),
            "artefacts_dans_le_sceau": sum(1 for a in artefacts if a in entrees),
            "coeur_secret_garde": 0,
            "ce_que_publier_veut_dire": "une équation non scellée est lisible sur ce disque, pas "
                                        "encore démontrable comme publiée : la charnière est le "
                                        "commit, pas l'écriture du fichier"}


def statuts_parc() -> Dict[str, Any]:
    inv = FB.inventaire_parc()
    par_dossier = {d: {"equations": v["equations"], "controles": v["controles"],
                       "tests": v["tests"], "modules": v["modules"]} for d, v in inv.items()}
    litteraux: Dict[str, Any] = {}
    reconcilies = 0
    for c in _cibles_du_parc():
        t = _texte(c)
        compte = {s: len(re.findall(f'"{re.escape(s)}"', t)) for s in FB.STATUTS}
        eq = _equations_par_module(c)
        somme = sum(compte.values())
        litteraux[c] = {"equations": eq, **compte, "somme": somme, "reconcilie": somme == eq}
        reconcilies += 1 if somme == eq else 0
    echantillon = _echantillon()
    eqs_s, cs_s = echantillon["eqs"], echantillon["cs"]
    repartis: Dict[str, int] = {}
    for e in eqs_s:
        repartis[e["statut"]] = repartis.get(e["statut"], 0) + 1
    return {"par_dossier": par_dossier, "dossiers": len(par_dossier),
            "equations": sum(v["equations"] for v in par_dossier.values()),
            "controles": sum(v["controles"] for v in par_dossier.values()),
            "tests": sum(v["tests"] for v in par_dossier.values()),
            "modules": sum(len(v["modules"]) for v in par_dossier.values()),
            "additif_par_dossier": sum(v["equations"] for v in par_dossier.values())
            == sum(l["equations"] for l in litteraux.values()),
            "litteraux_par_module": litteraux,
            "modules_reconcilies": reconcilies,
            "echantillon_nomme": echantillon["nom"],
            "echantillon_equations": len(eqs_s),
            "echantillon_statuts": dict(sorted(repartis.items())),
            "echantillon_additif": sum(repartis.values()) == len(eqs_s),
            "echantillon_controles": len(cs_s),
            "echantillon_verts": sum(1 for c in cs_s if c["ok"]),
            "statuts_cherches": list(FB.STATUTS)}


# ─── 8. Ablations -------------------------------------------------------------


CLE_NON_NOEUDS = ("source", "limites", "attribution", "empreinte_execution", "taille_octets",
                  "rejoue_identique", "racine_merkle_sha256")


def _echantillon() -> Dict[str, Any]:
    """Le module sur lequel les ablations sont réellement exécutées, chargé une seule fois.

    `etat` est reconstruit exactement comme le fait `resoudre()` du module sondé : les nœuds au
    premier niveau, plus le certificat complet sous `noeuds_certificat`. La racine Merkle, elle, ne
    se calcule que sur `noeuds` — le certificat débarrassé de ses clés d'exécution et d'attribution.
    """
    if "_ECHANTILLON" not in _CACHE:
        d, m = MODULE_ABLATION
        module = AP.charger(RACINE / d / m)
        cert = module.certificat()
        etat = {k: v for k, v in cert.items() if k not in ("source", "limites", "attribution")}
        etat["noeuds_certificat"] = cert
        eqs = {x["id"]: x for x in module.equations(etat)}
        _CACHE["_ECHANTILLON"] = {
            "nom": f"{d}/{m}", "module": module, "cert": cert, "etat": etat,
            "eqs": list(eqs.values()), "cs": module.controles(eqs, etat),
            "noeuds": {k: v for k, v in cert.items() if k not in CLE_NON_NOEUDS}}
    return _CACHE["_ECHANTILLON"]


def _regles(eqs: List[Dict[str, Any]], cs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Les quatre comptes de l'auditeur, recalculés sur une liste d'équations donnée."""
    born = [e["id"] for e in eqs if isinstance(e.get("limite"), str)
            and len(e["limite"].strip()) >= AP.MIN_LIMITE]
    sans_chemin = [e["id"] for e in eqs
                   if not isinstance(e.get("chemin"), str) or "→" not in e["chemin"]]
    inconnus = [e["id"] for e in eqs if e.get("statut") not in FB.STATUTS]
    vides = [c["id"] for c in cs if not str(c.get("attendu", "")).strip()
             or not str(c.get("obtenu", "")).strip()]
    rouges = [c["id"] for c in cs if not c.get("ok")]
    return {"born": len(born), "non_born": len(eqs) - len(born), "non_born_ids": sorted(
        e["id"] for e in eqs if e["id"] not in born),
            "sans_chemin": len(sans_chemin), "sans_chemin_ids": sans_chemin[:4],
            "statuts_inconnus": len(inconnus), "controles_vides": len(vides),
            "controles_rouges": len(rouges), "controles_verts": len(cs) - len(rouges),
            "p2_tient": len(born) == len(eqs), "p3_tient": not (sans_chemin or inconnus
                                                                or vides or rouges)}


def ablation_limites() -> Dict[str, Any]:
    import copy
    s = _echantillon()
    nom, module, eqs, cs = s["nom"], s["module"], s["eqs"], s["cs"]
    avant = _regles(eqs, cs)
    ottees = copy.deepcopy(eqs)
    for e in ottees:
        e["limite"] = ""
    apres = _regles(ottees, cs)
    sans_limite_avant = [{k: v for k, v in e.items() if k != "limite"} for e in eqs]
    sans_limite_apres = [{k: v for k, v in e.items() if k != "limite"} for e in ottees]
    nombres = module.canonique(sans_limite_avant) == module.canonique(sans_limite_apres)
    longueurs = sorted(len(e["limite"]) for e in eqs)
    return {"module": nom, "equations": len(eqs), "controles": len(cs),
            "born_avant": avant["born"], "born_apres": apres["born"],
            "limites_otrees": avant["born"] - apres["born"],
            "non_born_avant": avant["non_born"], "non_born_apres": apres["non_born"],
            "p2_avant": avant["p2_tient"], "p2_apres": apres["p2_tient"],
            "seuil": AP.MIN_LIMITE, "longueurs_min_max": [longueurs[0], longueurs[-1]],
            "nombres_inchanges_par_otage": nombres,
            "controles_toujours_verts": apres["controles_verts"],
            "enonce": "retrancher la borne écrite par l'humain ne change aucun nombre : cela "
                      "change seulement ce que ces nombres ont le droit de dire"}


def ablation_chemins() -> Dict[str, Any]:
    import copy
    s = _echantillon()
    nom, module, etat, eqs, cs = s["nom"], s["module"], s["etat"], s["eqs"], s["cs"]
    avant = _regles(eqs, cs)
    mutilees = copy.deepcopy(eqs)
    for e in mutilees:
        e["chemin"] = ""
        e["statut"] = "STATUT_INVENTE"
    apres = _regles(mutilees, cs)
    cs_apres = module.controles({e["id"]: e for e in mutilees}, etat)
    return {"module": nom, "equations": len(eqs),
            "sans_chemin_avant": avant["sans_chemin"], "sans_chemin_apres": apres["sans_chemin"],
            "statuts_inconnus_avant": avant["statuts_inconnus"],
            "statuts_inconnus_apres": apres["statuts_inconnus"],
            "p3_avant": avant["p3_tient"], "p3_apres": apres["p3_tient"],
            "controles_module_verts_avant": avant["controles_verts"],
            "controles_module_verts_apres": sum(1 for c in cs_apres if c["ok"]),
            "controles_module_total": len(cs_apres),
            "auditeur_rouge_apres": not apres["p3_tient"],
            "nombres_inchanges": module.canonique(
                [{k: v for k, v in e.items() if k not in ("chemin", "statut")} for e in eqs])
            == module.canonique([{k: v for k, v in e.items() if k not in ("chemin", "statut")}
                                 for e in mutilees]),
            "enonce": "les contrôles du module restent verts quand le chemin et le statut "
                      "disparaissent : seule la grille de l'auditeur voit la trace effacée"}


def _racine_de(module: Any, noeuds: Dict[str, Any]) -> str:
    return hashlib.sha256(module.canonique(
        {c: hashlib.sha256(module.canonique(noeuds[c])).hexdigest()
         for c in sorted(noeuds)})).hexdigest()


def ablation_provenance() -> Dict[str, Any]:
    import copy
    # Les fonctions qui ne font qu'afficher le bloc SOURCE sont classées « rendu » ; toute autre
    # lecture est classée « mesure » — y compris discipline_sources(), qui compte réellement SOURCE.
    RENDU = {"certificat", "resoudre", "resume_markdown", "regles_markdown", "octets_clauses_md",
             "(module/garde)", "(module)"}
    par_module: Dict[str, Any] = {}
    total_presentation = total_mesure = 0
    lectures_de_mesure: List[str] = []
    for c in _cibles_du_parc():
        arbre = ast.parse(_texte(c), filename=c)
        lu: List[Tuple[str, str]] = []

        class Visite(ast.NodeVisitor):
            def __init__(self, nom_fonction: str):
                self.nom_fonction = nom_fonction

            def _note(self, cible: str) -> None:
                if self.nom_fonction != "(definition)":
                    lu.append((self.nom_fonction, cible))

            def visit_Subscript(self, n: ast.Subscript) -> None:
                if isinstance(n.value, ast.Name) and n.value.id == "SOURCE":
                    self._note(getattr(n.slice, "value", "?"))
                self.generic_visit(n)

            def visit_Attribute(self, n: ast.Attribute) -> None:
                if isinstance(n.value, ast.Name) and n.value.id == "SOURCE":
                    self._note(n.attr)
                self.generic_visit(n)

            def visit_Name(self, n: ast.Name) -> None:
                if n.id == "SOURCE":
                    self._note("(reference-nue)")
                self.generic_visit(n)

        for no in ast.iter_child_nodes(arbre):
            if isinstance(no, ast.FunctionDef):
                Visite(no.name).visit(no)
            elif isinstance(no, ast.AnnAssign) and isinstance(no.target, ast.Name) \
                    and no.target.id == "SOURCE":
                Visite("(definition)").visit(no)
            elif isinstance(no, ast.If):
                Visite("(module/garde)").visit(no)
            else:
                Visite("(module)").visit(no)
        dans_presentation = [x for x in lu if x[0] in RENDU]
        ailleurs = sorted({f for f, _ in lu if f not in RENDU})
        par_module[c] = {"lectures": len(lu), "presentation": len(dans_presentation),
                         "fonctions_de_mesure": ailleurs,
                         "fonctions_citees": sorted({f for f, _ in lu})}
        total_presentation += len(dans_presentation)
        total_mesure += len(lu) - len(dans_presentation)
        for f in ailleurs:
            lectures_de_mesure.append(f"{c} → {f}")

    s = _echantillon()
    nom, module, cert = s["nom"], s["module"], s["cert"]
    noeuds = s["noeuds"]
    racine_avant = _racine_de(module, noeuds)
    formule_reproduite = racine_avant == cert["racine_merkle_sha256"]
    noeuds_sans_attrib = copy.deepcopy(noeuds)
    retire = [k for k in ("source", "attribution") if noeuds_sans_attrib.pop(k, None) is not None]
    racine_apres_retrait = _racine_de(module, noeuds_sans_attrib)
    cle_test = sorted(noeuds.keys())[0]
    noeuds_fausses = copy.deepcopy(noeuds)
    noeuds_fausses[cle_test] = {"nombre_injecte": 12345}
    racine_apres_nombre = _racine_de(module, noeuds_fausses)
    racine_certificat_complet = _racine_de(module, cert)
    attribue = {c: v for c, v in par_module.items() if v["fonctions_de_mesure"]}
    return {"par_module": par_module, "modules_audites": len(par_module),
            "lectures_presentation": total_presentation, "lectures_hors_presentation": total_mesure,
            "fonctions_lisant_la_provenance": sorted({f for v in par_module.values()
                                                      for f in v["fonctions_citees"]}),
            "modules_avec_lecture_de_mesure": sorted(attribue),
            "enonces_de_lecture_de_mesure": lectures_de_mesure[:6],
            "module_echantillon": nom,
            "racine_formule_reproduite": formule_reproduite,
            "racine_avant": racine_avant, "racine_apres_retrait_attribution": racine_apres_retrait,
            "attribution_dans_la_racine": racine_apres_retrait != racine_avant,
            "cles_attribution_dans_les_noeuds": retire,
            "racine_apres_nombre_injecte": racine_apres_nombre,
            "racine_sensible_aux_nombres": racine_apres_nombre != racine_avant,
            "cle_injectee": cle_test,
            "racine_certificat_complet": racine_certificat_complet,
            "certificat_complet_hors_racine": racine_certificat_complet != racine_avant,
            "noeuds_exclus_du_scellement": sorted(set(cert) - set(noeuds)),
            "enonce": "l'attribution n'entre pas dans la racine Merkle du certificat : elle n'est "
                      "rendue probante que par le sceau du fichier qui la porte"}


def limites_ouvertes() -> Dict[str, Any]:
    h, s, i, e = horodatages_git(), sceau_contenu(), instruments_horodatage(), education_ia()
    ch, zp, fr = chronologie(), chaine_zenodo(), fractales()
    cle = h["signatures_detail"][0]["cle"] if h["signatures_detail"] else "aucune clé relevée"
    liste = [
        "aucun instrument d'horodatage qualifié (RFC 3161, TSA, eIDAS, cachet) n'est dans "
        f"l'archive : {i['instruments_fichiers']} fichier — ce dossier ne peut pas en produire un",
        f"{h['signatures_portees']} commit sur {h['commits_atteignables']} porte un bloc gpgsig "
        f"(clé {cle}) et {h['signatures_verifiees']} est vérifiée : faute de clé publique au "
        "trousseau, aucun commit ne rend ce dépôt probant par signature",
        f"le sceau ne porte aucune date : {s['dates_trouvees']} date dans {s['total_lignes']} "
        "entrées — dater un contenu demande un tiers de confiance, pas un hash",
        f"aucune trace d'éducation des IA dans l'archive : {e['instruments_fichiers']} instrument "
        "(poids fins, dataset, journal, config) — la demande reste déclarée",
        f"le dossier de preuves externe est cité {ch['references_dossier_externe']} fois dans "
        f"l'archive et n'y est pas scellé : sa valeur probante ne se transmet pas avec le ZIP",
        f"{ch['antecedents_cites']}/{ch['antecedents_total']} antécédents vidéo sont nommés dans "
        "l'archive ; aucun n'y porte de date mesurable",
        f"la résolution en ligne des {zp['recids_distincts']} identifiants Zenodo comptés n'est pas "
        "faite ici : ce module ne fait aucune requête réseau",
        f"{s['hors_manifeste']} fichiers de l'archive sont hors du sceau, dont "
        f"{frontiere_publication()['equations_non_scellees']} équations de modules non scellés",
        f"la date d'auteur la plus ancienne ({h['date_auteur_plus_ancienne']}) est signée "
        f"{h['auteur_plus_ancien'] or 'auteur inconnu'} et la première trace fractale "
        f"({fr['la_plus_ancienne_trace_fractale'] or 'aucune'}) "
        f"{fr['auteur_de_la_premiere_trace'] or 'auteur inconnu'} : la plus vieille date du dépôt "
        "n'attribue pas l'idée à un humain",
        f"le classifieur statue ligne à ligne : {i['lignes_affirmatives_total']} lignes affirmatives "
        "sur les mentions d'horodatage, dont des clés de fichiers qui nomment l'instrument sans "
        "l'employer — le mot compte, il ne prouve pas",
    ]
    return {"liste": liste, "nb_limites": len(liste),
            "remplies": 0, "non_remplies": sum(1 for _ in liste),
            "aucune_limite_remplie_en_execuant_le_module": True,
            "toutes_au_moins_quarante": all(len(l) >= AP.MIN_LIMITE for l in liste),
            "plus_courte": min(len(l) for l in liste)}
# ─── 9. Octets publiés --------------------------------------------------------


def _cell(v: Any) -> str:
    s = str(v)
    for separe in (";", "\r\n", "\n", "\r", "\t"):
        s = s.replace(separe, " ")
    return " ".join(s.split()).strip()


def _lignes_chaine(cert: Dict[str, Any]) -> List[List[str]]:
    """La chaîne d'antériorité : une ligne par instrument daté ou non daté, avec ce qu'il prouve."""
    h, s = cert["horodatages_git"], cert["sceau_contenu"]
    ch, fr = cert["chronologie"], cert["fractales"]
    ed, zp = cert["education_ia"], cert["chaine_zenodo"]
    i, rm = cert["instruments_horodatage"], cert["repartition_humain_machine"]
    rows: List[List[str]] = [
        ["racine du depot git", ".git + git rev-list --max-parents=0", h["date_debut"] or "absent",
         "declaree par l'horloge cliente", "le depot commence ici", "rien de ce qui precede"],
        ["dernier commit atteignable", "git log", h["date_fin"] or "absent",
         "declaree par l'horloge cliente", "le depot etait a cet etat", "la date de publication"],
        ["plage du journal de références", ".git/logs/HEAD",
         f"{ch['date_racine']} -> {ch['date_derniere']}" if ch["date_racine"] else "absent",
         "encaissee par git", f"{h['journal_parsees']} operations locales datees",
         "une paternite"],
        ["sceau SHA-256 du depot", MANIFESTE_CHEMIN, "aucune date dans le fichier",
         "empreinte de contenu", f"{s['total_lignes']} entrees, {s['dates_trouvees']} date",
         "une date, ni une paternite"],
        ["tete git liee au sceau", MANIFESTE_CHEMIN, "non liee",
         "absence mesuree", f"{s['identifiants_git_40_hex']} identifiant de commit dans le sceau",
         "le lien entre version publiee et octets scelles"],
        ["enregistrement Zenodo lu", ".zenodo.json", zp["date_publication_lue"],
         "declare par l'auteur dans le depot", f"version {zp['version_lue']}, licence "
         f"{zp['licence_lue']}", "la date serveurs de Zenodo, qui se verifie en ligne"],
        ["citation lue", "CITATION.cff", zp["date_release_cff"], "declare par l'auteur",
         f"{zp['recids_distincts']} identifiants Zenodo distincts cites",
         "que chaque identifiant resout"],
        ["dernier commit de l'archive", ".git/HEAD", h["sha_tete"], "encaisse par git",
         f"{rm['commits_total']} commits dont {rm['commits_automate']} d'automate",
         "qui a decide"],
        ["instruments d'horodatage qualifie", "archive complete", "aucun",
         "denombrement de fichiers", f"{i['instruments_fichiers']} fichier d'instrument, "
         f"{i['mentions_total']} mentions textuelles", "une valeur probante"],
        ["trace fractale la plus ancienne de l'archive", ", ".join(fr["fichiers"])[:60],
         fr["la_plus_ancienne_trace_fractale"] or "absent", "date du commit d'ajout",
         f"{fr['occurrences']} occurrences dans {fr['nb_fichiers']} fichiers",
         "que les fractales soient le point de depart de l'auteur"],
        ["claim d'education des IA", "archive complete", "aucune date",
         "denombrement d'instruments", f"{ed['claim_occurrences']} mention du verbe, "
         f"{ed['instruments_fichiers']} instrument d'entrainement", "le claim lui-meme"],
    ]
    for d, date in sorted(ch["dossiers_dates"].items()):
        rows.append([f"dossier {d}", "git log --diff-filter=A", date, "date du commit d'ajout",
                     "le dossier est entre dans l'archive a cette date",
                     "la date de la premiere idee qu'il contient"])
    for c, n in sorted(fr["par_fichier"].items()):
        rows.append([f"fichier nommant fractal : {c}", "fractales()", fr["dates_ajout"].get(c, ""),
                     "date du commit d'ajout", f"{n} occurrences", "l'anteriorite du fractalisme"])
    for a in ch["antecedents"]:
        rows.append([f"antecedent video {a['id']}", "SOURCE + corpus du depot",
                     "aucune date mesurable dans l'archive", "mention textuelle",
                     f"{a['mentionations']} mention(s) dans l'archive",
                     "la date de publication de la video"])
    return rows


def octets_csv(cert: Dict[str, Any]) -> bytes:
    lignes = [list(COLONNES_CHAINE)] + [[_cell(x) for x in r] for r in _lignes_chaine(cert)]
    corps = "\r\n".join(";".join(r) for r in lignes) + "\r\n"
    return b"\xef\xbb\xbf" + corps.encode("utf-8")


def octets_svg(cert: Dict[str, Any]) -> bytes:
    valeurs = [(lib, int(cert[nom][clef])) for lib, nom, clef in BARRES]
    grand = max([v for _, v in valeurs] + [1])
    pieces: List[str] = []
    for i, (lib, v) in enumerate(valeurs):
        w = _decimale(LONGUEUR_MAX * Fraction(v) / Fraction(grand), 2)
        y = 34 + i * 30
        pieces.append(f'<rect x="250" y="{y - 12}" width="{w}" height="16" '
                      f'fill="{COULEURS[i % len(COULEURS)]}" data-libelle="{lib}" '
                      f'data-valeur="{v}"/>')
        pieces.append(f'<text x="8" y="{y}" font-size="13" fill="#0f1c2b" xml:lang="fr">'
                      f'{lib}</text>')
        xp = _decimale(Fraction(256) + LONGUEUR_MAX * Fraction(v) / Fraction(grand), 2)
        pieces.append(f'<text x="{xp}" y="{y}" font-size="13" fill="#1c3550">{v}</text>')
    bas = 34 + len(valeurs) * 30 + 26
    s, i = cert["sceau_contenu"], cert["instruments_horodatage"]
    note = (f'<text x="8" y="{bas - 18}" font-size="12" fill="#5c2f2f" xml:lang="fr">'
            f'{s["total_lignes"]} entrees de sceau, {s["dates_trouvees"]} date a l\'interieur, '
            f'{i["instruments_fichiers"]} instrument d\'horodatage reel — {PHRASE_VERIFIEE}</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="520" height="{bas + 8}" '
            f'viewBox="0 0 520 {bas + 8}">\n'
            f'<title>DECLARATION — ce que chaque instrument date et ce qu\'il ne date pas</title>\n'
            f'<desc>Longueurs proportionnelles a la plus grande valeur ({grand}). '
            f'{PHRASE_VERIFIEE}.</desc>\n' + "\n".join(pieces) + "\n" + note +
            "\n</svg>\n").encode("utf-8")


def octets_declaration_md(cert: Dict[str, Any]) -> bytes:
    h, s, i = cert["horodatages_git"], cert["sceau_contenu"], cert["instruments_horodatage"]
    ch, fr, ed = cert["chronologie"], cert["fractales"], cert["education_ia"]
    zn = cert["chaine_zenodo"]
    rm, fp = cert["repartition_humain_machine"], cert["frontiere_publication"]
    al, ac, ap = cert["ablation_limites"], cert["ablation_chemins"], cert["ablation_provenance"]
    lo = cert["limites_ouvertes"]
    lignes = [
        f"# DECLARATION — {PHRASE_VERIFIEE}",
        "",
        "**Départ** quatre déclarations de l'auteur et une consigne d'avis externe, consignées dans "
        "`SOURCE` ; aucune n'est reprise comme preuve, toutes sont comptées.",
        "",
        "| demande de l'auteur | instrument qui l'étayerait | mesuré | statut |",
        "|---|---|---|---|",
        f"| preuves d'antériorité | sceau SHA-256 du dépôt | {s['total_lignes']} entrées, "
        f"{s['dates_trouvees']} date à l'intérieur, {s['identifiants_git_40_hex']} identifiant de "
        f"commit | OPÉRATIONNEL |",
        f"| antériorité par un tiers | RFC 3161 / TSA / eIDAS / coffre-fort / e-Soleau | "
        f"{i['instruments_fichiers']} instrument sur disque, {i['mentions_total']} mentions "
        f"textuelles dont {i['lignes_absence']} lignes d'absence | OPÉRATIONNEL |",
        f"| dépôt public horodaté | commits git, blocs de signature | {h['signatures_portees']}/"
        f"{h['commits_atteignables']} portent gpgsig, {h['signatures_verifiees']} vérifiée(s) "
        f"faute de clé publique, du {h['date_debut']} au {h['date_fin']} | OPÉRATIONNEL |",
        f"| « j'ai commencé par les fractales » | trace fractale datée dans l'archive | "
        f"{fr['occurrences']} occurrences, {fr['nb_fichiers']} fichiers, première trace fractale "
        f"{fr['la_plus_ancienne_trace_fractale'] or 'aucune'} contre {fr['la_plus_ancienne_trace_du_depot']} "
        f"pour le dépôt ; première trace fractale = plus ancienne du dépôt : "
        f"{fr['fractales_sont_la_premiere_trace_du_depot']} | OPÉRATIONNEL |",
        f"| « j'ai éduqué les IA » | poids fins, dataset d'alignement, journal d'entraînement | "
        f"{ed['instruments_fichiers']} instrument, {ed['claim_occurrences']} mention du verbe dans "
        f"l'archive | SIMULÉ — déclaratif |",
        f"| mérite contre l'automate | partage mesuré des commits et des fichiers | "
        f"{rm['commits_humains']} commits humains / {rm['commits_automate']} d'automate "
        f"({rm['part_humaine_pct']} % / {rm['part_automate_pct']} %) ; "
        f"{rm['fichiers_automate_seul']} fichiers touchés par l'automate seul, dont "
        f"{rm['automate_seul_portant_limite']} portant une borne écrite | OPÉRATIONNEL |",
        f"| chaîne de publication | Zenodo et CITATION.cff relus | version {zn['version_lue']}, "
        f"{zn['recids_distincts']} identifiants distincts, {zn['total_mentions_doi']} mentions de DOI, "
        f"résolution en ligne non testée ici | OPÉRATIONNEL |",
        f"| équations publiables | sceau par module | {fp['modules_dans_le_sceau']}/"
        f"{fp['modules_porteurs']} modules dans le sceau, {fp['equations_non_scellees']} équations "
        f"hors publication prouvable | OPÉRATIONNEL |",
        "",
        "## Les trois ablations exécutées",
        "",
        f"1. **Retrancher la borne.** Sur `{al['module']}`, {al['limites_otrees']} limites d'au "
        f"moins {al['seuil']} caractères effacées : P2 passe de tenu {al['p2_avant']} à tenu "
        f"{al['p2_apres']}, et les nombres rendus sont inchangés : {al['nombres_inchanges_par_otage']}. "
        f"Un nombre sans borne n'est pas plus faux — il ne borne plus rien.",
        f"2. **Retrancher le chemin et le statut.** Sur `{ac['module']}`, "
        f"{ac['sans_chemin_apres']} équations sans chemin et {ac['statuts_inconnus_apres']} statuts "
        f"inconnus : les {ac['controles_module_verts_apres']}/{ac['controles_module_total']} "
        f"contrôles du module restent verts, la grille de l'auditeur rouge "
        f"({ac['auditeur_rouge_apres']}). Ce que l'automate produit ne se déclare pas lui-même.",
        f"3. **Retrancher la provenance.** {ap['lectures_presentation']} lectures du bloc SOURCE "
        f"se font dans les fonctions de rendu, {ap['lectures_hors_presentation']} dans des fonctions "
        f"de mesure ({', '.join(ap['modules_avec_lecture_de_mesure']) or 'aucun module'}). "
        f"Effacer l'attribution ne change pas la racine Merkle : "
        f"{ap['attribution_dans_la_racine']} ; y injecter un nombre la change : "
        f"{ap['racine_sensible_aux_nombres']}.",
        "",
        "## Ce que la mesure corrige dans la demande",
        "",
        "1. Un dépôt — Zenodo, GitHub, un sceau SHA-256 — atteste une **date d'accessibilité** d'un "
        "contenu, pas une paternité ni une priorité d'invention. Une idée, un concept ou une "
        "fractale ne se déposent pas : seule leur expression se diffuse et se date.",
        "2. L'ordre demandé (« verrouiller avant d'exposer ») est déjà tenu à l'envers par les "
        "faits : l'exposition est publique depuis le premier dépôt. Ce dossier date cette exposition "
        "au lieu de la nier.",
        "3. L'ablation ne montre pas que l'automate ne produit rien : elle montre que ce qu'il "
        "produit reste vérifiable et borné par des règles écrites ailleurs, et que ces règles, une "
        "fois retirées, laissent les mêmes nombres dire n'importe quoi.",
        "",
        "## Limites ouvertes",
        "",
    ]
    lignes += [f"- {l}" for l in lo["liste"]]
    lignes += ["", f"**{PHRASE_VERIFIEE}** : ce dossier date et retranche ; il ne certifie personne.",
               ""]
    return ("\r\n".join(lignes) + "\r\n").encode("utf-8")


def octets_json(cert: Dict[str, Any]) -> bytes:
    return (json.dumps(cert, ensure_ascii=False, indent=2, sort_keys=True,
                       default=str) + "\n").encode("utf-8")


def _artefacts_octets(cert: Dict[str, Any]) -> Dict[str, bytes]:
    return {"certificat.json": octets_json(cert),
            "chaine_anteriorite.csv": octets_csv(cert),
            "declaration_et_ablations.md": octets_declaration_md(cert),
            "frontiere_anteriorite.svg": octets_svg(cert)}


PHRASE_HORS_CHAINE = ("certificat.json", "declaration_et_ablations.md", "frontiere_anteriorite.svg")


def chaine_relu(cert: Dict[str, Any]) -> Dict[str, Any]:
    octets = octets_csv(cert)
    texte = octets.decode("utf-8-sig")
    lignes = [l for l in texte.split("\r\n") if l != ""]
    entetes = lignes[0].split(";") if lignes else []
    largeurs = sorted({len(l.split(";")) for l in lignes})
    return {"chemin": CHEMIN_CHAINE, "octets": len(octets),
            "bom": octets[:3] == b"\xef\xbb\xbf", "separateur": ";",
            "crlf": octets.count(b"\r\n") == len(lignes),
            "colonnes_relues": entetes, "en_tete_conforme": tuple(entetes) == COLONNES_CHAINE,
            "nb_lignes_texte": len(lignes), "lignes_de_donnees": max(0, len(lignes) - 1),
            "largeurs_de_colonnes": largeurs, "largeur_unique": len(largeurs) == 1,
            "aucun_separateur_dans_une_cellule": all(";" not in c for l in lignes
                                                     for c in l.split(";")),
            "dates_dans_le_sceau_relues": sum(1 for l in lignes[1:]
                                              if l.startswith("sceau") and "aucune date" in l),
            "phrase_absente_du_csv_par_design": PHRASE_VERIFIEE not in texte}


def plan_svg(cert: Dict[str, Any]) -> Dict[str, Any]:
    octets = octets_svg(cert)
    texte = octets.decode("utf-8")
    largeurs = [m.split('width="')[1].split('"')[0] for m in texte.split("<rect ")[1:]]
    valeurs = [(lib, int(cert[nom][clef])) for lib, nom, clef in BARRES]
    grand = max([v for _, v in valeurs] + [1])
    attendues = [_decimale(LONGUEUR_MAX * Fraction(v) / Fraction(grand), 2) for _, v in valeurs]
    return {"chemin": "DECLARATION/artefacts/frontiere_anteriorite.svg", "octets": len(octets),
            "barres": len(largeurs), "largeurs_conformes": largeurs == attendues,
            "valeurs_ecrites": [int(m.split('data-valeur="')[1].split('"')[0])
                                for m in texte.split("<rect ")[1:]],
            "valeurs_attendues": [v for _, v in valeurs],
            "plus_grande_valeur": grand,
            "barre_de_zero_longueur": sum(1 for w in largeurs if w == "0.00"),
            "notes_texte": texte.count("<text "),
            "absence_ecrite": PHRASE_VERIFIEE in texte}


def ecritures(cert: Dict[str, Any]) -> Dict[str, Any]:
    rendu = _artefacts_octets(cert)
    hors_boucle = {nom: octets for nom, octets in rendu.items() if nom != "certificat.json"}
    avec_phrase = {nom: octets for nom, octets in rendu.items() if nom in PHRASE_HORS_CHAINE}
    return {"noms": sorted(rendu),
            "tailles": {nom: len(oct) for nom, oct in sorted(hors_boucle.items())},
            "empreintes": {nom: hashlib.sha256(oct).hexdigest()[:16]
                           for nom, oct in sorted(hors_boucle.items())},
            "auto_reference": "certificat.json porte ce nœud : sa taille et son empreinte ne "
                              "peuvent pas être scellées par lui-même",
            "nom_sans_empreinte": "certificat.json", "nom_sans_phrase": "chaine_anteriorite.csv",
            "raison_sans_phrase": "une chaîne d'antériorité se lit dans un tableur : la phrase de "
                                  "verdict y deviendrait une donnée datée comme les autres",
            "absence_partout": all(PHRASE_VERIFIEE.encode("utf-8") in oct
                                   for oct in avec_phrase.values()),
            "noms_avec_phrase": sorted(avec_phrase)}
# ─── 10. Équations, contrôles, certificat -------------------------------------

NOEUDS: Dict[str, Dict[str, Any]] = {
    "EQ-01": {"depend": [], "externe": [".git/logs/HEAD", ".git/HEAD",
                                         "DECLARATION/declaration_base.py"]},
    "EQ-02": {"depend": ["EQ-01"], "externe": [".git"]},
    "EQ-03": {"depend": ["EQ-02"], "externe": ["MANIFESTE_SHA256.txt"]},
    "EQ-04": {"depend": [], "externe": ["MANIFESTE_SHA256.txt", ".git/HEAD"]},
    "EQ-05": {"depend": ["EQ-04"], "externe": []},
    "EQ-06": {"depend": [], "externe": [".zenodo.json", "CITATION.cff"]},
    "EQ-07": {"depend": [], "externe": ["LICENSE", "LICENSE-GPL", "LICENSE-AGPL"]},
    "EQ-08": {"depend": ["EQ-07"], "externe": []},
    "EQ-09": {"depend": ["EQ-01"], "externe": [".git"]},
    "EQ-10": {"depend": ["EQ-04"], "externe": ["FONDATION/fondation_base.py",
                                               "MANIFESTE_SHA256.txt"]},
    "EQ-11": {"depend": ["EQ-10"], "externe": ["FONDATION/fondation_base.py",
                                               "CONTINUITE/continuite_base.py"]},
    "EQ-12": {"depend": ["EQ-11"], "externe": ["CONTINUITE/continuite_base.py",
                                               "FONDATION/OUTILS/audit_piliers.py"]},
    "EQ-13": {"depend": ["EQ-12"], "externe": ["CONTINUITE/continuite_base.py"]},
    "EQ-14": {"depend": ["EQ-04", "EQ-13"], "externe": ["CONTINUITE/continuite_base.py"]},
    "EQ-15": {"depend": ["EQ-01", "EQ-04"], "externe": []},
    "EQ-16": {"depend": ["EQ-05", "EQ-08", "EQ-10"], "externe": []},
}


def _eq(id_: str, chemin: str, formule: str, resultat: str, statut: str,
        limite: str, detail: Any, couche: str = "S1 MESURABLE") -> Dict[str, Any]:
    n = NOEUDS[id_]
    return {"id": id_, "chemin": chemin, "formule": formule, "resultat": resultat,
            "statut": statut, "limite": limite, "detail": detail, "couche": couche,
            "piliers": ["P1 UNITE", "P2 BORNE", "P3 CONFRONTATION", "P4 TRANSMISSION"],
            "depend_de": n["depend"], "fonde_hors_du_dossier": n["externe"]}


def equations(etat: Dict[str, Any]) -> List[Dict[str, Any]]:
    h = etat["horodatages_git"]
    ch, fr, s = etat["chronologie"], etat["fractales"], etat["sceau_contenu"]
    i, zp, n_ = etat["instruments_horodatage"], etat["chaine_zenodo"], etat["noms_et_attributions"]
    ed, rm = etat["education_ia"], etat["repartition_humain_machine"]
    fp, st = etat["frontiere_publication"], etat["statuts_parc"]
    al, ac, ap = etat["ablation_limites"], etat["ablation_chemins"], etat["ablation_provenance"]
    rr, sv, ec = etat["chaine_relu"], etat["plan_svg"], etat["ecritures"]
    lo = etat["limites_ouvertes"]
    # les listes publiées dans un énoncé s'écrivent en français, pas en repr Python
    dossiers_dates = " · ".join(f"{d} {d_[:10]}" for d, d_ in sorted(ch["dossiers_dates"].items()))
    instruments = " · ".join(f"{k} {v['occurrences']}" for k, v in sorted(
        i["par_instrument"].items(), key=lambda kv: -kv[1]["occurrences"]))
    categories = " · ".join(f"{k.split(' (')[0]} {v['fichiers']}" for k, v in sorted(
        ed["instruments_par_categorie"].items()))
    statuts = " · ".join(f"{k} {v}" for k, v in sorted(st["echantillon_statuts"].items()))
    expressions = " / ".join(n_["expressions_en_tete"]) or "aucune"
    par_nom = n_["occurrences_par_nom"]
    nom_auteur, pseudonyme = par_nom["nom de l'auteur"], par_nom["pseudonyme"]
    affiliation, mention_ia = par_nom["affiliation"], par_nom["mention d'IA"]
    tailles = " · ".join(f"{k} {v} octets" for k, v in sorted(ec["tailles"].items()))
    hors_sceau = " · ".join(fp["modules_non_scelles"]) or "aucun"
    return [
        _eq("EQ-01", "declaration_base.py → horodatages_git() → C01",
            "J = { (n, n′, auteur, t, Δ) } lus octet à octet dans .git/logs/HEAD ; C = commits "
            "atteignables par `git log HEAD` ; la couche exige Σ_a J_a = |J| et |J| ≥ |C|",
            f"{h['journal_lignes']} lignes de journal · {h['journal_parsees']} parsées "
            f"(intégralement {h['journal_tout_parse']}) · {h['commits_atteignables']} commits "
            f"atteignables · {len(h['auteurs_journal'])} auteur(s) additifs "
            f"{h['auteurs_additifs']} · {h['signatures_portees']} bloc(s) de signature porté(s), "
            f"{h['signatures_verifiees']} vérifiée(s), {h['signatures_non_verifiees']} non "
            f"vérifiable(s) · du {h['date_debut']} au {h['date_fin']} · tête {h['sha_tete'][:12]}… "
            f"longue de {h['tete_longueur']} · date d'auteur la plus ancienne "
            f"{h['date_auteur_plus_ancienne']} signée par {h['auteur_plus_ancien']} "
            f"(automate : {h['auteur_plus_ancien_est_automate']}), antérieure à la date d'auteur de "
            f"la racine ({h['date_auteur_racine']}) : {h['date_auteur_antérieure_à_la_racine']} · "
            f"horloge murale dans ce source : {h['nb_motifs_horloge_cherches']} motifs, "
            f"{len(h['motifs_horloge_reposes'])} reposé",
            "OPÉRATIONNEL",
            "les dates sont celles qu'a déclarées l'horloge de la machine qui a écrit le commit : "
            "aucun tiers (TSA, RFC 3161, eIDAS) ne les atteste ici, et le journal mesure qui a "
            f"signé, pas qui a pensé — preuve_de_paternite = {h['preuve_de_paternite']}. Un bloc "
            "gpgsig présent ne signifie pas signature reconnue : la vérification échoue faute de "
            "clé publique dans le trousseau, et une date d'auteur antérieure à la racine vient "
            "d'un remaniement d'historique, pas d'une antériorité", h),
        _eq("EQ-02", "declaration_base.py → chronologie() → C02",
            "pour chaque objet introduit par un commit d'ajout : a(objet) = date du commit ; "
            "D = { dossiers du registre : min a } ; l'ordre raconté est tenu si a(FONDATION) ≤ "
            "a(HORLOGERIE) ≤ a(VERROUS)",
            f"{ch['objets_dates']} objets datés · la plus ancienne date {ch['plus_ancienne_date']} · "
            f"{ch['objets_anterieurs_a_la_racine']} objet(s) daté(s) avant la racine du dépôt · "
            f"{ch['dossiers_avec_date']}/{ch['dossiers_attendus']} dossiers datés ({dossiers_dates})"
            f" · antécédents vidéo cités {ch['antecedents_cites']}/{ch['antecedents_total']} · "
            f"dossiers portant « fractal » : "
            f"{' · '.join(ch['dossiers_portant_fractal']) or 'aucun'} · ordre raconté « "
            f"{ch['ordre_raconte']} » tenu par les dates : {ch['narratif_ordre_tenu']}",
            "OPÉRATIONNEL",
            "une date de commit ne date pas l'idée : elle date son entrée dans cette archive. Un "
            "ordre raconté peut être vrai dans la tête de l'auteur et faux dans le dépôt — le nœud "
            "publie les deux et ne tranche pas", ch),
        _eq("EQ-03", "declaration_base.py → fractales() → C03",
            "F = corpus (hors ce module et ses tests) ; o = nombre d'occurrences de « fractal » ; "
            "f(c) = date du commit qui introduit c ; la demande « j'ai commencé par les fractales » "
            "serait étayée si min f(F_rain) = min f(corpus)",
            f"{fr['occurrences']} occurrences dans {fr['nb_fichiers']} fichier(s) · "
            f"{fr['fonctions_nommant_fractal']} fonction(s) du dépôt nommant fractal · "
            f"{fr['equations_du_parc_nommant_fractal']} module(s) d'équations en portent le mot · "
            f"première trace fractale {fr['la_plus_ancienne_trace_fractale'] or 'aucune'} contre "
            f"{fr['la_plus_ancienne_trace_du_depot']} pour l'objet le plus ancien du dépôt · "
            f"égalité = {fr['fractales_sont_la_premiere_trace_du_depot']} · dossier de preuves "
            f"externe présent sur la machine : {fr['dossier_externel_present']}, scellé "
            f"{fr['scelle_dans_le_manifeste']} fois",
            "OPÉRATIONNEL",
            "compter le mot ne fonde pas l'antériorité du fractalisme : le dépôt ne peut être que "
            "postérieur à l'idée, et un dossier externe non scellé ne voyage pas avec l'archive",
            fr),
        _eq("EQ-04", "declaration_base.py → sceau_contenu() → C04",
            "S = { (e, c) } lignes de MANIFESTE_SHA256.txt avec e longue de 64 hex ; la couche "
            "exige e injectif, c injectif, trié, S ∌ S, et relit dans S toute date et tout "
            "identifiant de commit",
            f"{s['total_lignes']} entrées · {s['entrees_parsees']} conformes, "
            f"{s['entrees_non_conformes']} non conformes · empreintes de "
            f"{'/'.join(str(x) for x in s['longueurs_empreintes'])} caractères · uniques "
            f"{s['empreintes_uniques']} · triées {s['trie']} · {s['dates_trouvees']} date et "
            f"{s['identifiants_git_40_hex']} identifiant de commit à l'intérieur · "
            f"{s['absents_de_disque']} entrée(s) absente(s) de disque · {s['dans_le_sceau']}/"
            f"{s['fichiers_arbre']} fichiers de l'arbre scellés ({s['couverture_sceau_pct']} %), "
            f"{s['hors_manifeste']} hors sceau · le manifeste ne se scelle pas lui-même : "
            f"{s['le_manifeste_ne_se_scelle_pas_lui_meme']}",
            "OPÉRATIONNEL",
            "un sceau SHA-256 prouve que ces octets étaient là au moment du scellement ; il ne "
            "porte ni date légale ni paternité, et ne lie pas le contenu scellé à une tête git", s),
        _eq("EQ-05", "declaration_base.py → instruments_horodatage() → C05",
            "pour chaque instrument k de INSTRUMENTS_HORODATAGE : m_k = occurrences dans le corpus, "
            "L_k = lignes portées, L_k = A_k (affirmatives) + N_k (négation) ; un contrôle positif "
            "(SPDX) prouve que le classifieur rend autre chose que zéro",
            f"{i['nb_instruments_cherches']} instruments cherchés · {i['instruments_trouves']} "
            f"mentionné(s) · {i['mentions_total']} mentions ({instruments}) · {i['lignes_total']} "
            f"lignes dont {i['lignes_absence']} d'absence et {i['lignes_affirmatives_total']} "
            f"affirmatives · {i['instruments_fichiers']} fichier d'instrument réel sur disque "
            f"({' · '.join(i['instruments_fichiers_listes']) or 'aucun'}) · contrôle positif : "
            f"{i['controle_positif_lignes']} lignes SPDX, {i['controle_positif_affirmatives']} "
            f"affirmatives, classifieur non vide {i['classifieur_non_vacue']}",
            "OPÉRATIONNEL",
            "une mention textuelle n'est pas un instrument : ce nœud compte des lignes et des "
            "extensions de fichiers, il ne vérifie la validité d'aucun jeton d'horodatage et n'en "
            "produit aucun", i),
        _eq("EQ-06", "declaration_base.py → chaine_zenodo() → C06",
            "V = version lue dans .zenodo.json ; R = { identifiants 10.5281/zenodo.NNNN du corpus } "
            "avec n_r = occurrences ; un recid est ancêtre si CITATION.cff lui associe une version "
            "strictement inférieure à V (comparée chiffre à chiffre) ; aucune résolution réseau "
            "n'est tentée",
            f"version lue {zp['version_lue']} · date de publication lue "
            f"{zp['date_publication_lue']} · licence lue {zp['licence_lue']} · createur "
            f"{' / '.join(zp['createurs'])} · {zp['recids_distincts']} identifiants distincts pour "
            f"{zp['total_mentions_doi']} mentions · le plus cité {zp['recid_le_plus_cite']} "
            f"({zp['mentions_du_plus_cite']} fois) · {zp['nb_ancetres_cites']} ancêtre(s) associé"
            f"(s) à une version inférieure ({' · '.join(zp['ancetres_cites']) or 'aucun'}) · "
            f"{len(zp['recids_sans_version_associee'])} identifiant(s) sans version associée · "
            f"CITATION.cff version {zp['version_cff']} du {zp['date_release_cff']}, licence "
            f"« {zp['licence_cff']} », concordance des versions "
            f"{zp['versions_zenodo_et_cff_concordantes']}, des licences "
            f"{zp['licences_zenodo_et_cff_concordantes']} · résolution en ligne "
            f"{zp['resolutions_testées_en_ligne']}",
            "OPÉRATIONNEL",
            "les dates lues ici sont celles que l'auteur a écrites dans le dépôt, pas celles des "
            "serveurs de Zenodo : les versions et les associations recid ↔ version viennent des "
            "textes cités, et aucun nœud de ce dossier ne les confronte en ligne", zp),
        _eq("EQ-07", "declaration_base.py → noms_et_attributions() → C07",
            "P = fichiers .py de l'arbre ; avec = { p ∈ P : SPDX-FileCopyrightText ∈ p } ; "
            "couverture = 100 · |avec| / |P| ; X = { p : en-tête cite un ayant-droit automate }",
            f"{n_['avec_en_tete']}/{n_['python_total']} fichiers Python portés par un en-tête SPDX "
            f"({n_['couverture_en_tetes']} %), {n_['sans_en_tete']} sans en-tête "
            f"({' · '.join(n_['exemples_sans_en_tete']) or 'aucun'}) · expressions d'identifier : "
            f"{expressions} · « EL BAHLOUL » {nom_auteur['occurrences']} fois dans "
            f"{nom_auteur['fichiers']} fichiers · pseudonyme {pseudonyme['occurrences']} fois · "
            f"affiliation {affiliation['occurrences']} fois · mention d'IA "
            f"{mention_ia['occurrences']} fois · automate cité comme "
            f"ayant-droit : {n_['automate_cite_comme_ayant_droit']} · {n_['expressions_brutes']} "
            f"expression(s) lues, {len(n_['expressions_rejetees'])} rejetée(s) comme n'étant pas "
            f"une licence ({n_['rejet_contient_le_motif_de_recherche']} contenant le motif cherché)",
            "OPÉRATIONNEL",
            "un en-tête SPDX cite un titulaire du droit d'auteur sur le fichier : il ne vaut ni "
            "dépôt d'invention, ni cession, ni preuve de paternité d'un concept — le nœud n'en "
            "affirme aucune. Le corpus contient le code qui écrit ces en-têtes : les lignes de "
            "programme qui portent le motif sont comptées à part et non effacées", n_),
        _eq("EQ-08", "declaration_base.py → education_ia() → C08",
            "pour la demande « j'ai éduqué les IA », I = ⋃_c fichiers de la catégorie c où c court "
            "sur poids fins, dataset d'alignement, journal d'entraînement, config de fine-tuning ; "
            "la demande n'est étayée que si |I| > 0",
            f"{ed['instruments_fichiers']} instrument d'entraînement dans l'archive "
            f"({categories}, {ed['instruments_toutes_categories']} comptages avant dédoublonnage) · "
            f"verbe « éduqu* » : {ed['par_motif']['éduquer']['occurrences']} occurrence dans "
            f"{ed['par_motif']['éduquer']['fichiers']} fichier · contraste naif « educat* » : "
            f"{ed['contraste_naif']['occurrences']} occurrence dans "
            f"{ed['contraste_naif']['fichiers']} fichier · statut rendu : {ed['statut_du_claim']}",
            "OPÉRATIONNEL",
            "ce nœud compte des fichiers et des lignes : il ne peut ni confirmer ni infirmer "
            "qu'une IA a été éduquée. La demande reste déclarée, et c'est le statut publié", ed),
        _eq("EQ-09", "declaration_base.py → repartition_humain_machine() → C09",
            "E_a = fichiers touchés par les commits de l'auteur a ; M = ⋃_{a automate} E_a, "
            "H = ⋃_{a humain} E_a ; la couche exige |C_h| + |C_a| = |C| et "
            "|M\\H| + |H\\M| + |M∩H| = |M∪H|",
            f"{rm['commits_humains']} commits humains + {rm['commits_automate']} d'automate = "
            f"{rm['commits_total']} (additif {rm['additif_commits']}) · part humaine "
            f"{rm['part_humaine_pct']} % contre {rm['part_automate_pct']} % · "
            f"{rm['fichiers_touches_par_automate']} fichiers touchés par l'automate, "
            f"{rm['fichiers_touches_par_humain']} par un humain, {rm['fichiers_mixtes']} par les "
            f"deux · {rm['fichiers_automate_seul']} par l'automate seul, dont "
            f"{rm['automate_seul_sur_disque']} encore sur disque, "
            f"{rm['automate_seul_portant_equation']} portant une équation et "
            f"{rm['automate_seul_portant_limite']} portant une borne écrite",
            "OPÉRATIONNEL",
            "la signature d'un commit n'est pas l'intention : un fichier écrit sur instruction "
            "humaine et committé par un outil compte du côté de l'outil. La borne cherchée est une "
            "chaîne du source, pas une preuve de qui l'a décidée", rm),
        _eq("EQ-10", "declaration_base.py → frontiere_publication() → C10",
            "T = modules porteurs d'équations du registre (même marche que inventaire_parc) ; "
            "E(T) = |{ EQ-nn }| par module ; publiable = T ∩ chemins du sceau ; la couche exige "
            "Σ_T E = total du parc et |dedans| + |dehors| = |T|",
            f"{fp['modules_porteurs']} module(s) porteur(s) d'équations dans "
            f"{fp['dossiers']} dossier(s) · {fp['modules_dans_le_sceau']} dans le sceau, "
            f"{len(fp['modules_non_scelles'])} hors sceau ({hors_sceau}) · "
            f"{fp['somme_equations_par_module']} équations comptées module à module contre "
            f"{fp['total_parc']} au niveau du parc · {fp['equations_non_scellees']} équations "
            f"lisibles sur ce disque sans publication scellée · cœur secret gardé : "
            f"{fp['coeur_secret_garde']} fichier",
            "OPÉRATIONNEL",
            "la charnière n'est pas l'écriture du fichier mais le commit : une équation hors sceau "
            "est déjà lisible ici et pas encore démontrable comme publiée. Rien dans cette couche "
            "ne retire de la publication", fp),
        _eq("EQ-11", "declaration_base.py → statuts_parc() → C11",
            "pour le parc : Σ E = |{ EQ-nn }| et Σ C = |{ Cnn }| par dossier ; pour chaque module, "
            "la somme des littéraux de statut doit égaler son nombre d'équations ; la distribution "
            "réelle ne s'obtient qu'en exécutant equations() sur un module du parc",
            f"{st['dossiers']} dossiers · {st['equations']} équations · {st['controles']} contrôles "
            f"· {st['tests']} tests · {st['modules']} modules · additif par dossier "
            f"{st['additif_par_dossier']} · {st['modules_reconcilies']}/"
            f"{len(st['litteraux_par_module'])} modules où les littéraux de statut se "
            f"réconcilient avec le compte d'équations · exécution réelle de "
            f"{st['echantillon_nomme']} : {st['echantillon_equations']} équations, statuts "
            f"{statuts}, {st['echantillon_verts']}/{st['echantillon_controles']} contrôles verts",
            "OPÉRATIONNEL",
            "compter des littéraux dans un source n'est pas compter des équations : un mot peut "
            "apparaître dans une limite ou un commentaire. La distribution vraie est celle du "
            "module exécuté, et une seule", st),
        _eq("EQ-12", "declaration_base.py → ablation_limites() → C12",
            "soit B(e) la borne écrite de chaque équation e du module sondé, et P2 la règle "
            "« |B(e)| ≥ seuil ». Ablation : e′ = e \\ {B}. La couche exige P2(e) ∧ ¬P2(e′) et "
            "nombres(e) = nombres(e′)",
            f"sur {al['module']} : {al['equations']} équations, {al['born_avant']} bornes d'au "
            f"moins {al['seuil']} caractères effacées → {al['born_apres']} · P2 tenu "
            f"{al['p2_avant']} puis {al['p2_apres']} · longueurs réellement observées "
            f"{al['longueurs_min_max'][0]}…{al['longueurs_min_max'][1]} caractères · nombres "
            f"rendus inchangés par l'otage : {al['nombres_inchanges_par_otage']} · "
            f"{al['controles_toujours_verts']}/{al['controles']} contrôles du module encore verts",
            "OPÉRATIONNEL", al["enonce"] + " — l'expérience est exécutée en mémoire sur une copie "
            "profonde, aucun fichier du module sondé n'est modifié", al, "S2 REGULARITE"),
        _eq("EQ-13", "declaration_base.py → ablation_chemins() → C13",
            "ablation : e′ = e \\ {chemin, statut}, statut remplacé par une valeur hors registre. "
            "La couche compare deux grilles : les contrôles du module, et le compte P3 de "
            "l'auditeur",
            f"sur {ac['module']} : {ac['sans_chemin_avant']} → {ac['sans_chemin_apres']} équation(s) "
            f"sans chemin, {ac['statuts_inconnus_avant']} → {ac['statuts_inconnus_apres']} statut(s) "
            f"inconnu(s) · grille de l'auditeur P3 tenu {ac['p3_avant']} puis {ac['p3_apres']} · "
            f"contrôles du module {ac['controles_module_verts_avant']} puis "
            f"{ac['controles_module_verts_apres']} vert(s) sur {ac['controles_module_total']} · "
            f"nombres inchangés : {ac['nombres_inchanges']}",
            "OPÉRATIONNEL", ac["enonce"] + " — l'auditeur ne peut donc pas être remplacé par le "
            "module qu'il audite : c'est la raison d'être du pilier P3", ac, "S2 REGULARITE"),
        _eq("EQ-14", "declaration_base.py → ablation_provenance() → C14",
            "R(n) = sha256( ⨁_c sha256(canonique(n_c)) ) sur les nœuds du certificat. Ablations : "
            "retirer l'attribution des nœuds, puis y injecter un nombre ; la couche compare R à la "
            "racine publiée",
            f"{ap['modules_audites']} module(s) d'équations audité(s) par AST · "
            f"{ap['lectures_presentation']} lectures de SOURCE dans le rendu, "
            f"{ap['lectures_hors_presentation']} dans des fonctions de mesure "
            f"({' · '.join(ap['enonces_de_lecture_de_mesure']) or 'aucune'}) · formule de racine "
            f"reproduite à l'identique : {ap['racine_formule_reproduite']} · retirer "
            f"l'attribution des nœuds change la racine : {ap['attribution_dans_la_racine']} "
            f"(clés d'attribution présentes dans les nœuds : "
            f"{' · '.join(ap['cles_attribution_dans_les_noeuds']) or 'aucune'}) · injecter un "
            f"nombre dans {ap['cle_injectee']} change la racine : "
            f"{ap['racine_sensible_aux_nombres']} · le certificat complet (avec « source ») rend "
            f"une autre racine : {ap['certificat_complet_hors_racine']}",
            "OPÉRATIONNEL", ap["enonce"] + " — « sans un humain derrière l'IA elle n'est rien » ne "
            "se prouve donc pas par le hash : la racine est aveugle à l'auteur et sensible aux "
            "nombres", ap, "S2 REGULARITE"),
        _eq("EQ-15", "declaration_base.py → chaine_relu() + plan_svg() + ecritures() → C15",
            "les octets produits sont relus : CSV = BOM + en-tête + lignes de largeur unique "
            "séparées par « ; » en CRLF ; SVG = une barre par entrée de BARRES, largeur "
            "240 · v / max(v) ; le certificat s'exclut lui-même de ses propres empreintes",
            f"{rr['octets']} octets de CSV relu, {rr['nb_lignes_texte']} lignes dont "
            f"{rr['lignes_de_donnees']} de données, en-tête conforme {rr['en_tete_conforme']}, "
            f"largeur unique {rr['largeur_unique']}, BOM {rr['bom']}, CRLF {rr['crlf']} · plan : "
            f"{sv['barres']} barres sur {len(BARRES)} attendues, "
            f"largeurs conformes {sv['largeurs_conformes']}, {sv['barre_de_zero_longueur']} à "
            f"longueur nulle, verdict écrit {sv['absence_ecrite']} · écritures : {tailles} ; "
            f"{ec['auto_reference']}",
            "OPÉRATIONNEL",
            "relire ses propres octets prouve la cohérence de l'écriture, pas la vérité de la "
            "mesure : la chaîne publiée ne contient pas la phrase de verdict, et le certificat ne "
            "scelle pas sa propre taille", ec),
        _eq("EQ-16", "declaration_base.py → limites_ouvertes() → C16",
            "L = liste des limites que ce dossier énonce et ne remplit pas ; la couche exige "
            "|L| > 0, min |l| ≥ seuil de la borne, et que none ne se remplisse en exécutant le "
            "module",
            f"{lo['nb_limites']} limites ouvertes · {lo['remplies']} remplie(s) par l'exécution · "
            f"toutes d'au moins {AP.MIN_LIMITE} caractères : {lo['toutes_au_moins_quarante']} "
            f"(la plus courte : {lo['plus_courte']}) · premier énoncé : {lo['liste'][0]}",
            "SPÉCIFIÉ",
            "une limite ouverte reste ouverte : ce module ne génère ni jeton d'horodatage, ni "
            "signature de commit, ni poids d'entraînement, et ne résout aucun identifiant en ligne",
            lo),
    ]


def controles(eqs: Dict[str, Any], etat: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []

    def ajouter(id_: str, nom: str, verifie: str, attendu: str, obtenu: str, ok: bool) -> None:
        out.append({"id": id_, "equation": f"EQ-{id_[1:]}", "nom": nom, "verifie": verifie,
                    "attendu": attendu, "obtenu": obtenu, "ok": bool(ok)})

    h = etat["horodatages_git"]
    ch, fr, s = etat["chronologie"], etat["fractales"], etat["sceau_contenu"]
    i, zp, n_ = etat["instruments_horodatage"], etat["chaine_zenodo"], etat["noms_et_attributions"]
    ed, rm = etat["education_ia"], etat["repartition_humain_machine"]
    fp, st = etat["frontiere_publication"], etat["statuts_parc"]
    al, ac, ap = etat["ablation_limites"], etat["ablation_chemins"], etat["ablation_provenance"]
    rr, sv, ec = etat["chaine_relu"], etat["plan_svg"], etat["ecritures"]
    lo = etat["limites_ouvertes"]

    ajouter("C01", "le journal est parseé sans horloge murale et les comptes sont additifs",
            "toutes les lignes du journal parsées, la somme des comptes par auteur égale le nombre "
            "de lignes, la tête git longue de 40 hex, signatures portées et absentes épuisant les "
            "commits, et aucun motif d'heure système dans le source de ce module",
            "100 % des lignes · Σ auteurs = |J| · tête 40 hex · signées + non signées = |C| · "
            "horloge absente",
            f"{h['journal_parsees']}/{h['journal_lignes']} lignes · Σ = "
            f"{h['somme_auteurs_journal']} pour {h['journal_parsees']} · tête "
            f"{h['tete_longueur']} hex cohérente avec le journal : {h['tete_coherente']} · "
            f"{h['signatures_portees']} + {h['commits_sans_signature']} = "
            f"{h['signatures_portees'] + h['commits_sans_signature']} commits sur "
            f"{h['commits_atteignables']}, {h['signatures_verifiees']} vérifiée(s) · "
            f"motifs d'horloge reposés : {len(h['motifs_horloge_reposes'])}",
            h["journal_tout_parse"] and h["auteurs_additifs"] and h["tete_longueur"] == 40
            and h["signatures_portees"] + h["commits_sans_signature"] == h["commits_atteignables"]
            and h["aucune_horloge"] and h["git_disponible"])
    ajouter("C02", "la chronologie est celle des dates du dépôt, pas du récit",
            "un objet daté au moins un, chaque dossier daté appartient au registre, et les "
            "antécédents comptés sont exactement ceux déclarés dans SOURCE",
            f"objets datés > 0 · dossiers ⊆ {len(FB.DOSSIERS_EQUATIONS)} du registre · "
            f"antécédents = {len(SOURCE['antecedents_declares'])}",
            f"{ch['objets_dates']} objets datés · {ch['dossiers_avec_date']} dossier(s) daté(s) "
            f"sur {ch['dossiers_attendus']} attendu(s) · {ch['antecedents_total']} antécédent(s) "
            f"compté(s), {ch['antecedents_cites']} nommé(s) dans l'archive · ordre raconté tenu : "
            f"{ch['narratif_ordre_tenu']}",
            ch["objets_dates"] > 0 and ch["dossiers_avec_date"] <= ch["dossiers_attendus"]
            and all(d in FB.DOSSIERS_EQUATIONS for d in ch["dossiers_dates"])
            and ch["antecedents_total"] == len(SOURCE["antecedents_declares"]))
    ajouter("C03", "les fractales sont comptées, pas racontées",
            "la somme des occurrences par fichier égale le total, le nombre de fichiers égale la "
            "taille de l'index, et la comparaison avec l'objet le plus ancien du dépôt est faite",
            f"Σ occurrences = {fr['occurrences']} · |fichiers| = {fr['nb_fichiers']} · comparaison "
            "des deux dates bornées",
            f"Σ = {sum(fr['par_fichier'].values())} · index de {len(fr['par_fichier'])} fichier(s)"
            f" · première trace fractale {fr['la_plus_ancienne_trace_fractale'] or 'aucune'}, objet "
            f"le plus ancien {fr['la_plus_ancienne_trace_du_depot'] or 'aucun'} · égalité : "
            f"{fr['fractales_sont_la_premiere_trace_du_depot']}",
            sum(fr["par_fichier"].values()) == fr["occurrences"]
            and len(fr["par_fichier"]) == fr["nb_fichiers"]
            and bool(fr["la_plus_ancienne_trace_du_depot"]))
    ajouter("C04", "le sceau ne porte ni date, ni commit, ni lui-même",
            "les entrées conformes plus les non conformes épuisent le fichier, les chemins sont "
            "uniques, le manifeste ne se scelle pas lui-même, et le compte des dates et des "
            "identifiants de commit à l'intérieur est nul",
            "Σ comptes = total · 0 date · 0 identifiant de commit · pas d'auto-scellement",
            f"{s['entrees_parsees']} + {s['entrees_non_conformes']} = {s['total_lignes']} · "
            f"{s['dates_trouvees']} date(s) · {s['identifiants_git_40_hex']} identifiant(s) git · "
            f"chemins uniques {s['chemins_uniques']} · auto-scellement "
            f"{not s['le_manifeste_ne_se_scelle_pas_lui_meme']}",
            s["entrees_parsees"] + s["entrees_non_conformes"] == s["total_lignes"]
            and s["chemins_uniques"] and s["le_manifeste_ne_se_scelle_pas_lui_meme"]
            and s["dates_trouvees"] == 0 and s["identifiants_git_40_hex"] == 0 and s["existe"])
    ajouter("C05", "le classifieur sépare l'absence de l'affirmation, et ne ramène pas tout à zéro",
            "pour chaque instrument, lignes = absence + affirmatives ; le contrôle positif SPDX "
            "rend au moins une ligne affirmative ; le compte de fichiers d'instruments réels est "
            "celui du disque",
            "additivité des lignes · contrôle positif > 0",
            f"{i['lignes_total']} lignes = {i['lignes_absence']} d'absence + "
            f"{i['lignes_affirmatives_total']} affirmatives · contrôle positif "
            f"{i['controle_positif_affirmatives']} affirmative(s) sur "
            f"{i['controle_positif_lignes']} ligne(s) · {i['instruments_fichiers']} fichier "
            f"d'instrument réel",
            i["lignes_total"] == i["lignes_absence"] + i["lignes_affirmatives_total"]
            and i["classifieur_non_vacue"] and i["controle_positif_affirmatives"] > 0
            and i["instruments_fichiers"] == 0)
    ajouter("C06", "la chaîne de publication est relue dans le dépôt et rien d'autre",
            "autant d'identifiants distincts que de clés relevées, les identifiants à version "
            "associée et ceux sans association épuisent la liste, les ancêtres n'en sont qu'une "
            "partie stricte, la version des deux fichiers concorde, et la résolution réseau est "
            "absente par déclaration",
            "|R| = |clés| · |associées| + |sans association| = |R| · ancêtres < |R| · "
            "version zenodo = version cff · résolution = Faux",
            f"{zp['recids_distincts']} identifiants pour {len(zp['recids'])} clé(s) · "
            f"{len(zp['paires_recid_version'])} avec version associée + "
            f"{len(zp['recids_sans_version_associee'])} sans = "
            f"{len(zp['paires_recid_version']) + len(zp['recids_sans_version_associee'])} · "
            f"{zp['nb_ancetres_cites']} ancêtre(s) · {zp['total_mentions_doi']} mentions · "
            f"version {zp['version_lue'] or 'absente'} contre {zp['version_cff'] or 'absente'} · "
            f"concordance {zp['versions_zenodo_et_cff_concordantes']} · résolution en ligne : "
            f"{zp['resolutions_testées_en_ligne']}",
            zp["recids_distincts"] == len(zp["recids"])
            and len(zp["paires_recid_version"]) + len(zp["recids_sans_version_associee"])
            == zp["recids_distincts"]
            and zp["nb_ancetres_cites"] < zp["recids_distincts"]
            and zp["total_mentions_doi"] >= zp["recids_distincts"] and bool(zp["version_lue"])
            and zp["versions_zenodo_et_cff_concordantes"]
            and not zp["resolutions_testées_en_ligne"])
    ajouter("C07", "l'attribution écrite est comptée et n'affermit rien",
            "les fichiers avec en-tête plus ceux sans en-tête épuisent les fichiers Python, la "
            "règle d'acceptation des expressions de licence en retient au moins une et n'en retient "
            "pas plus qu'elle n'en voit, et aucun automate n'est cité comme ayant-droit",
            "|avec| + |sans| = |.py| · 0 automate ayant-droit · 0 < retenues ≤ brutes",
            f"{n_['avec_en_tete']} + {n_['sans_en_tete']} = {n_['python_total']} · couverture "
            f"{n_['couverture_en_tetes']} % · {len(n_['expressions_en_tete'])} expression(s) "
            f"retenues sur {n_['expressions_brutes']} lues ("
            f"{' · '.join(n_['expressions_en_tete']) or 'aucune'}) · automates cités : "
            f"{n_['automate_cite_comme_ayant_droit']}",
            n_["avec_en_tete"] + n_["sans_en_tete"] == n_["python_total"]
            and n_["automate_cite_comme_ayant_droit"] == 0
            and 0 < len(n_["expressions_en_tete"]) <= n_["expressions_brutes"]
            and not n_["affirmation_de_paternite_juridique"])
    ajouter("C08", "la demande d'éducation des IA reste déclarée",
            "les instruments par catégorie, dédoublonnés, ne peuvent excéder la somme par "
            "catégorie, et le statut rendu est exactement « déclaré · non vérifié »",
            "|⋃| ≤ Σ|catégories| · statut = déclaré · non vérifié",
            f"{ed['instruments_fichiers']} fichier(s) après dédoublonnage sur "
            f"{ed['instruments_toutes_categories']} comptages par catégorie · verbe « éduqu* » "
            f"{ed['claim_occurrences']} fois · statut : {ed['statut_du_claim']}",
            ed["instruments_fichiers"] <= ed["instruments_toutes_categories"]
            and ed["statut_du_claim"] == "déclaré · non vérifié"
            and len(ed["instruments_par_categorie"]) == len(INSTRUMENTS_EDUCATION))
    ajouter("C09", "le partage humain / machine est additif des deux côtés",
            "commits humains + commits d'automate = commits atteignables, et la partition des "
            "fichiers (automate seul, humain seul, les deux) épuise leur union",
            f"|C_h| + |C_a| = {rm['commits_total']} · Σ 3 cellules = |M ∪ H| = "
            f"{rm['fichiers_union']}",
            f"{rm['commits_humains']} + {rm['commits_automate']} = {rm['commits_total']} · "
            f"{rm['fichiers_automate_seul']} + {rm['fichiers_humain_seul']} + "
            f"{rm['fichiers_mixtes']} = {rm['fichiers_union']} fichiers",
            rm["additif_commits"]
            and rm["fichiers_automate_seul"] + rm["fichiers_humain_seul"] + rm["fichiers_mixtes"]
            == rm["fichiers_union"] and rm["git_disponible"])
    ajouter("C10", "la frontière de publication se referme sur le registre du parc",
            "modules dans le sceau + hors du sceau = modules porteurs, et la somme module à module "
            "des équations égale le total du parc calculé par la même marche",
            f"|dedans| + |dehors| = {fp['modules_porteurs']} · Σ E = total_parc = "
            f"{fp['total_parc']}",
            f"{fp['modules_dans_le_sceau']} + {len(fp['modules_non_scelles'])} = "
            f"{fp['modules_porteurs']} · Σ module à module {fp['somme_equations_par_module']} "
            f"contre {fp['total_parc']} au niveau du parc · {fp['equations_non_scellees']} "
            f"équation(s) hors sceau",
            fp["modules_dans_le_sceau"] + len(fp["modules_non_scelles"]) == fp["modules_porteurs"]
            and fp["somme_equations_par_module"] == fp["total_parc"]
            and fp["controle_de_comptage"])
    ajouter("C11", "le parc se recompte depuis l'unique registre, l'échantillon se fait exécuter",
            "la somme par dossier égale la somme par module, la distribution de statuts de "
            "l'échantillon épuise ses équations, et tous ses contrôles sont verts",
            "additivité des deux compteurs · Σ statuts = |échantillon| · 0 contrôle rouge",
            f"{st['equations']} équations · {st['controles']} contrôles · {st['tests']} tests "
            f"additifs par dossier : {st['additif_par_dossier']} · échantillon "
            f"{st['echantillon_nomme']} : Σ statuts {sum(st['echantillon_statuts'].values())} pour "
            f"{st['echantillon_equations']} équations · {st['echantillon_verts']}/"
            f"{st['echantillon_controles']} contrôles verts",
            st["additif_par_dossier"] and st["echantillon_additif"]
            and st["echantillon_verts"] == st["echantillon_controles"] > 0
            and st["modules_reconcilies"] <= len(st["litteraux_par_module"]))
    ajouter("C12", "retrancher la borne fait tomber P2 sans toucher aux nombres",
            f"toutes les équations de l'échantillon bornées avant, aucune après, les nombres rendus "
            "identiques et la règle P2 de l'auditeur retournée",
            f"P2 Vrai → Faux · {al['equations']} → 0 bornes · nombres inchangés",
            f"{al['born_avant']} → {al['born_apres']} borne(s) d'au moins {al['seuil']} caractères"
            f" · P2 {al['p2_avant']} → {al['p2_apres']} · nombres inchangés : "
            f"{al['nombres_inchanges_par_otage']} · {al['non_born_avant']} → "
            f"{al['non_born_apres']} équation(s) non bornée(s)",
            al["p2_avant"] and not al["p2_apres"] and al["born_apres"] == 0
            and al["limites_otrees"] == al["equations"] and al["nombres_inchanges_par_otage"])
    ajouter("C13", "les contrôles du module ne voient pas la trace effacée, l'auditeur si",
            "après effacement du chemin et invention du statut, la grille P3 de l'auditeur passe au "
            "rouge alors que les nombres rendus ne bougent pas",
            "P3 Vrai → Faux · tous les chemins effacés · nombres inchangés",
            f"{ac['sans_chemin_apres']}/{ac['equations']} équation(s) sans chemin · "
            f"{ac['statuts_inconnus_apres']} statut(s) hors registre · P3 {ac['p3_avant']} → "
            f"{ac['p3_apres']} · module {ac['controles_module_verts_apres']}/"
            f"{ac['controles_module_total']} vert(s) · nombres inchangés : "
            f"{ac['nombres_inchanges']}",
            ac["p3_avant"] and not ac["p3_apres"] and ac["auditeur_rouge_apres"]
            and ac["sans_chemin_apres"] == ac["equations"]
            and ac["statuts_inconnus_apres"] == ac["equations"] and ac["nombres_inchanges"])
    ajouter("C14", "la racine scelle des nombres, pas une attribution",
            "la formule de la racine est reproduite à l'identique, le retrait de l'attribution ne "
            "la change pas, l'injection d'un nombre la change",
            "racine reproduite · retrait sans effet · nombre injecté : effet",
            f"{ap['racine_formule_reproduite']} · attribution présente dans les nœuds : "
            f"{' · '.join(ap['cles_attribution_dans_les_noeuds']) or 'aucune'} · retrait change la "
            f"racine : {ap['attribution_dans_la_racine']} · injection en {ap['cle_injectee']} la "
            f"change : {ap['racine_sensible_aux_nombres']}",
            ap["racine_formule_reproduite"] and not ap["attribution_dans_la_racine"]
            and ap["racine_sensible_aux_nombres"] and ap["certificat_complet_hors_racine"])
    ajouter("C15", "les octets relus disent les nombres du calcul",
            "CSV à en-tête conforme, largeur unique, BOM et CRLF ; SVG avec autant de barres que "
            "BARRES et des largeurs recalculées ; la phrase de verdict absente du CSV et présente "
            "partout ailleurs",
            f"en-tête = {len(COLONNES_CHAINE)} colonnes · 1 largeur · {len(BARRES)} barres "
            "conformes · verdict hors CSV",
            f"{rr['octets']} octets · en-tête conforme {rr['en_tete_conforme']} · largeur unique "
            f"{rr['largeur_unique']} · BOM {rr['bom']} · CRLF {rr['crlf']} · {sv['barres']} barre(s)"
            f" conformes {sv['largeurs_conformes']} · verdict absent du CSV par dessein : "
            f"{rr['phrase_absente_du_csv_par_design']} · verdict écrit ailleurs : "
            f"{ec['absence_partout']}",
            rr["en_tete_conforme"] and rr["largeur_unique"] and rr["bom"] and rr["crlf"]
            and sv["barres"] == len(BARRES) and sv["largeurs_conformes"] and sv["absence_ecrite"]
            and ec["absence_partout"] and rr["phrase_absente_du_csv_par_design"]
            and rr["nb_lignes_texte"] == rr["lignes_de_donnees"] + 1)
    ajouter("C16", "les limites sont énoncées et ouvertes",
            "au moins une limite, chacune longue d'au moins le seuil de la borne, et aucune remplie "
            "par l'exécution de ce module",
            f"|L| > 0 · min |l| ≥ {AP.MIN_LIMITE} · remplies = 0",
            f"{lo['nb_limites']} limite(s) · plus courte {lo['plus_courte']} caractères · toutes au "
            f"moins {AP.MIN_LIMITE} : {lo['toutes_au_moins_quarante']} · {lo['remplies']} remplie(s)",
            lo["nb_limites"] > 0 and lo["toutes_au_moins_quarante"] and lo["remplies"] == 0
            and lo["nb_limites"] == len(lo["liste"])
            and lo["aucune_limite_remplie_en_execuant_le_module"])
    return out


def canonique(objet: Any) -> bytes:
    return json.dumps(objet, ensure_ascii=False, sort_keys=True,
                      default=str).encode("utf-8")


MESURES = ("horodatages_git", "chronologie", "fractales", "sceau_contenu",
           "instruments_horodatage", "chaine_zenodo", "noms_et_attributions", "education_ia",
           "repartition_humain_machine", "frontiere_publication", "statuts_parc",
           "ablation_limites", "ablation_chemins", "ablation_provenance", "limites_ouvertes")


def noeuds_certificat() -> Dict[str, Any]:
    nc: Dict[str, Any] = {nom: globals()[nom]() for nom in MESURES}
    nc["verdict"] = {"enonce": PHRASE_VERIFIEE,
                     "commits_atteignables": nc["horodatages_git"]["commits_atteignables"],
                     "dates_dans_le_sceau": nc["sceau_contenu"]["dates_trouvees"],
                     "instruments_d_horodatage_sur_disque":
                         nc["instruments_horodatage"]["instruments_fichiers"],
                     "instruments_d_education": nc["education_ia"]["instruments_fichiers"],
                     "equations_hors_sceau": nc["frontiere_publication"]["equations_non_scellees"],
                     "limites_ouvertes": nc["limites_ouvertes"]["nb_limites"]}
    # seconde passe : la chaîne, le plan et les écritures mesurent les octets que ce module produit
    base = {**nc, "nb_barres": len(BARRES)}
    relu = chaine_relu(base)
    svg = plan_svg(base)
    nc["chaine_relu"] = relu
    nc["plan_svg"] = svg
    nc["ecritures"] = ecritures({**base, "chaine_relu": relu, "plan_svg": svg})
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
                "cette couche ne prétend qu'une chose : elle date et retranche ce qui est écrit sur "
                "ce disque ; elle ne désigne personne comme inventeur et ne vaut aucun dépôt "
                "juridique",
                "les nœuds d'ablation travaillent en mémoire sur une copie profonde d'un module du "
                "parc : aucun fichier du dépôt n'est modifié par leur exécution",
            ],
            "attribution": {"auteur": SOURCE["auteur"],
                            "statut_des_quatre_demandes": "déclarées ; comptées par ce dossier ; "
                                                          "aucune rendue prouvée",
                            "ce_qu_un_depot_prouve": "une date d'accessibilité du contenu",
                            "ce_qu_un_depot_ne_prouve_pas": "une paternité, ni une priorité "
                                                            "d'invention"},
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
                "enonce_declaration": (
                    f"{cert['horodatages_git']['commits_atteignables']} commits datés par "
                    f"l'horloge cliente, {cert['sceau_contenu']['total_lignes']} entrées de sceau "
                    f"portant {cert['sceau_contenu']['dates_trouvees']} date, "
                    f"{cert['instruments_horodatage']['instruments_fichiers']} instrument "
                    f"d'horodatage qualifié et {cert['education_ia']['instruments_fichiers']} "
                    f"instrument d'éducation sur disque, "
                    f"{cert['repartition_humain_machine']['commits_humains']} commits humains contre "
                    f"{cert['repartition_humain_machine']['commits_automate']} d'automate, "
                    f"{cert['frontiere_publication']['equations_non_scellees']} équations hors "
                    f"sceau — {PHRASE_VERIFIEE}"),
                "commits_attestees": cert["horodatages_git"]["commits_atteignables"],
                "date_debut": cert["horodatages_git"]["date_debut"],
                "date_fin": cert["horodatages_git"]["date_fin"],
                "entrees_de_sceau": cert["sceau_contenu"]["total_lignes"],
                "dates_dans_le_sceau": cert["sceau_contenu"]["dates_trouvees"],
                "instruments_horodatage": cert["instruments_horodatage"]["instruments_fichiers"],
                "instruments_education": cert["education_ia"]["instruments_fichiers"],
                "commits_automate": cert["repartition_humain_machine"]["commits_automate"],
                "equations_hors_sceau": cert["frontiere_publication"]["equations_non_scellees"],
                "limites_ouvertes": cert["limites_ouvertes"]["nb_limites"],
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
    h, s = cert["horodatages_git"], cert["sceau_contenu"]
    ch, fr = cert["chronologie"], cert["fractales"]
    i, zp = cert["instruments_horodatage"], cert["chaine_zenodo"]
    ed, rm = cert["education_ia"], cert["repartition_humain_machine"]
    fp, al = cert["frontiere_publication"], cert["ablation_limites"]
    corps = [
        f"# DECLARATION — {PHRASE_VERIFIEE}",
        "",
        "**Départ** quatre phrases de l'auteur et une feuille de route externe, consignées verbatim "
        "dans `SOURCE` ; aucune n'est reprise comme preuve, chacune est confrontée à l'instrument "
        "qui l'étayerait.",
        "",
        f"**Journal** {h['journal_parsees']}/{h['journal_lignes']} lignes parsées, "
        f"{h['commits_atteignables']} commits du {h['date_debut']} au {h['date_fin']}, "
        f"{len(h['auteurs_journal'])} auteur(s), {h['signatures_portees']} bloc(s) de signature "
        f"porté(s) et {h['signatures_verifiees']} vérifiée(s), aucune horloge "
        f"murale dans ce module.",
        f"**Sceau** {s['total_lignes']} entrées, {s['dates_trouvees']} date à l'intérieur, "
        f"{s['identifiants_git_40_hex']} identifiant de commit, {s['couverture_sceau_pct']} % de "
        f"l'arbre scellé, {s['hors_manifeste']} fichier(s) hors sceau.",
        f"**Instruments** {i['instruments_fichiers']} fichier d'horodatage qualifié (RFC 3161, TSA, "
        f"eIDAS, coffre-fort, e-Soleau) sur {i['mentions_total']} mention(s) textuelle(s), dont "
        f"{i['lignes_absence']} ligne(s) disant justement qu'il n'y en a pas.",
        f"**Chaîne** version Zenodo lue {zp['version_lue']} à la date déclarée "
        f"{zp['date_publication_lue']}, {zp['recids_distincts']} identifiants distincts cités, "
        f"{zp['nb_ancetres_cites']} ancêtre(s) encore cité(s), résolution en ligne non tentée.",
        f"**Fractales** {fr['occurrences']} occurrences dans {fr['nb_fichiers']} fichier(s) ; "
        f"première trace fractale {fr['la_plus_ancienne_trace_fractale'] or 'aucune'} contre "
        f"{fr['la_plus_ancienne_trace_du_depot']} pour l'objet le plus ancien du dépôt : la "
        f"demande « j'ai commencé par les fractales » n'est pas la première trace de l'archive.",
        f"**Éducation des IA** {ed['instruments_fichiers']} instrument (poids fins, dataset, "
        f"journal, config) ; statut rendu : {ed['statut_du_claim']}.",
        f"**Humain / machine** {rm['commits_humains']} commits humains contre "
        f"{rm['commits_automate']} d'automate ({rm['part_humaine_pct']} % / "
        f"{rm['part_automate_pct']} %) ; {rm['fichiers_automate_seul']} fichiers touchés par "
        f"l'automate seul.",
        f"**Frontière** {fp['modules_dans_le_sceau']}/{fp['modules_porteurs']} modules porteurs "
        f"d'équations dans le sceau, {fp['equations_non_scellees']} équations hors publication "
        f"scellée, {fp['coeur_secret_garde']} fichier gardé comme secret de fabrique.",
        "",
        "## Cheminement",
        "",
        "1. le journal git est parseé intégralement et l'absence d'horloge murale est relue dans le "
        "source de ce module ;",
        "2. les dates d'ajout de chaque objet sont comparées à l'ordre raconté ;",
        "3. les traces fractales sont comptées, puis confrontées à l'objet le plus ancien ;",
        "4. le sceau est relu : ses entrées, l'absence de date et l'absence de lien à la tête git ;",
        "5. les six instruments d'horodatage qualifié sont cherchés, et chaque ligne est classée "
        "absence ou affirmation, avec un contrôle positif ;",
        "6. la chaîne Zenodo est relue dans les fichiers, sans aucune requête réseau ;",
        "7. les en-têtes SPDX sont comptés fichier par fichier, et les ayants-droit automates "
        "cherchés ;",
        "8. la demande d'éducation des IA est confrontée aux quatre catégories d'instruments "
        "qu'elle exigerait ;",
        "9. les commits sont partitionnés entre humain et automate, puis les fichiers entre les "
        "deux ensembles ;",
        "10. la frontière de publication est mesurée contre l'unique registre du parc ;",
        "11. trois ablations sont exécutées en mémoire : retirer la borne, retirer le chemin et le "
        "statut, retirer l'attribution de la racine ;",
        "12. les octets produits sont relus, et les limites que rien n'a été rempli sont publiées.",
        "",
        "## Résultat",
        "",
        f"- l'antériorité accessible est faite de dates déclarées par des clients et d'empreintes "
        f"sans date : {s['dates_trouvees']} date dans {s['total_lignes']} entrées de sceau ;",
        f"- aucune paternité n'est instrumentée : {i['instruments_fichiers']} instrument qualifié, "
        f"{h['signatures_portees']} bloc de signature porté et {h['signatures_verifiees']} "
        f"vérifiée sur {h['commits_atteignables']} commits ;",
        f"- la borne écrite par l'humain ne change pas les nombres : les effacer fait tomber P2 "
        f"({al['born_avant']} → {al['born_apres']}) et laisse les mêmes valeurs ;",
        f"- la racine Merkle est aveugle à l'attribution et sensible aux nombres ;",
        f"- {cert['limites_ouvertes']['nb_limites']} limites ouvertes, "
        f"{cert['limites_ouvertes']['remplies']} remplie(s) ;",
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
        "commits_attestees": conclusion["commits_attestees"],
        "plage": [conclusion["date_debut"], conclusion["date_fin"]],
        "entrees_de_sceau": conclusion["entrees_de_sceau"],
        "dates_dans_le_sceau": conclusion["dates_dans_le_sceau"],
        "instruments_horodatage": conclusion["instruments_horodatage"],
        "instruments_education": conclusion["instruments_education"],
        "commits_automate": conclusion["commits_automate"],
        "equations_hors_sceau": conclusion["equations_hors_sceau"],
        "limites_ouvertes": conclusion["limites_ouvertes"],
        "enonce": conclusion["enonce_declaration"],
        "rouges": [c["id"] for c in donnees["controles"] if not c["ok"]],
        "racine": conclusion["racine_merkle_sha256"]}, ensure_ascii=False, indent=2))
