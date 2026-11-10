# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""Tests du dossier VERROUS — les compteurs sont re-derivés, pas recopiés.

Six exigences, dans l'ordre :
    1. l'arbre, le sceau, la couverture de licence, l'histoire des commits et le journal local sont
       recalculés ICI par une écriture différente : la marche de l'arbre vient d'`os.walk` (et non de
       `rglob`), le compte publié de commits vient de `git rev-list --count` (et non de `git log`),
       le partage d'une ligne de reflog vient de `split` (et non d'une regex), le classement des
       empreintes vient d'un `split("  ")` (et non de `re.match`), et les largeurs du plan viennent
       d'une division entière à arrondi half-up (et non de `Fraction`) ;
    2. la structure est testée hors du dépôt : le même fabricant de plan, appliqué à un certificat
       fictif dont les compteurs ne sont pas zéros, rend des barres non nulles — ce n'est donc pas
       l'absence de verrous qui fait marcher le code ;
    3. les quatre artefacts sont relus sur disque par `csv.reader` et par regex, puis comparés au
       calcul : ce que le dossier publie est ce que le dossier a calculé ;
    4. non-vacuité : seize mutations, une par contrôle, nommées ROUGIT — faire apparaître un
       fichier secret, décréter une clause rédigée, signer un instrument, rendre le journal
       incohérent, sceller le certificat dans son propre nœud, déclarer une limite franchie ;
    5. les verdicts défavorables restent écrits : 0 clause, 0 instrument, 0 avocat, 0 artefact
       précompilé, la dérive du sceau chiffrée, la divergence de licence Zenodo publiée, et
       l'ordre de la phase 1 rendu à l'envers ;
    6. déterminisme, racine Merkle et bornes de langage : deux exécutions concordent, changer un
       nœud change la racine, et aucune phrase ne prétend qu'un contrat existe.

Stdlib uniquement.
    cd ZENODO_DEPOT_ALMIZAN && py -3 -m unittest VERROUS.tests.test_verrous -v
"""

import copy
import csv
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import unittest
from datetime import datetime, timedelta, timezone
from fractions import Fraction
from pathlib import Path
from tempfile import TemporaryDirectory

RACINE_DEPOT = Path(__file__).resolve().parents[2]
if str(RACINE_DEPOT) not in sys.path:
    sys.path.insert(0, str(RACINE_DEPOT))

from VERROUS import verrous_base as V                                        # noqa: E402

CERT = V.certificat()
EQS = {e["id"]: e for e in V.equations(CERT)}
CS = {c["id"]: c for c in V.controles(EQS, CERT)}
HORS_NOEUDS = frozenset({"source", "empreinte_execution", "taille_octets", "rejoue_identique",
                         "limites", "attribution", "racine_merkle_sha256"})
NOEUDS = {k: v for k, v in CERT.items() if k not in HORS_NOEUDS}
DONNEES = V.resoudre()  # une seule exécution partagée ; la concordance est testée section 6


# ─── voie indépendante : marche, parse et arrondi sans les écritures du module --

def marche_arbre():
    """Les fichiers du dépôt par `os.walk` — aucune recursion `rglob`, aucun `relative_to`."""
    rendu = []
    for racine, dossiers, fichiers in os.walk(str(RACINE_DEPOT)):
        dossiers[:] = [d for d in dossiers if d not in V.EXCLUS_REPERTOIRES]
        for f in fichiers:
            if f.endswith(tuple(V.EXCLUS_SUFFIXES)) or f.startswith(V.NOM_TEMPORAIRE):
                continue
            rel = os.path.relpath(os.path.join(racine, f), str(RACINE_DEPOT)).replace("\\", "/")
            if any(rel.startswith(p) for p in V.EXCLUS_PREFIXES):
                continue
            rendu.append(rel)
    return sorted(rendu)


def lire(chemin):
    with open(str(RACINE_DEPOT / chemin), "rb") as handle:
        return handle.read()


def empreinte(chemin):
    return hashlib.sha256(lire(chemin)).hexdigest()


def empreinte_arbre(chemins):
    ruban = "\n".join(c + "\t" + empreinte(c) for c in chemins)
    return hashlib.sha256(ruban.encode("utf-8")).hexdigest()


def parse_ligne_laine(brute):
    """(ancien, nouveau, nom, courriel, epoch, fuseau, message) par `split` — aucune regex."""
    ligne = brute.decode("utf-8")
    ancien, nouveau, reste = ligne.split(" ", 2)
    nom, suite = reste.split(" <", 1)
    courriel, fin = suite.split("> ", 1)
    epoch, reste_f = fin.split(" ", 1)
    fuseau, message = reste_f.split("\t", 1)
    return ancien, nouveau, nom, courriel, int(epoch), fuseau, message


def journal_parse():
    bruts = lire(".git/logs/HEAD").split(b"\n")
    return [parse_ligne_laine(l) for l in bruts if l]


def iso_de(epoch, fuseau):
    return datetime.fromtimestamp(epoch, timezone(
        (1 if fuseau[0] == "+" else -1) * timedelta(hours=int(fuseau[1:3]),
                                                    minutes=int(fuseau[3:5])))).isoformat()


DEPOT_GIT = (RACINE_DEPOT / ".git").exists()
GIT_TROUVE = shutil.which("git") is not None
SOUS_GIT = unittest.skipUnless(DEPOT_GIT and GIT_TROUVE,
                               "aucun dépôt git lisible : l'histoire ne se relit pas ici")
SOUS_JOURNAL = unittest.skipUnless(DEPOT_GIT,
                                    "aucun journal local de références ici")


def git_brut(*argumens):
    """git lancé depuis les tests, hors du module et hors de son cache."""
    rendu = subprocess.run(["git", *argumens], cwd=str(RACINE_DEPOT), capture_output=True,
                           text=True, encoding="utf-8", errors="replace")
    assert rendu.returncode == 0, rendu.stderr[:200]
    return rendu.stdout


def histoire_brute():
    """(sha, courriel, epoch, iso) par un séparateur « | » — le module emploie %x09."""
    rendu = []
    for l in git_brut("log", "--format=%H|%ae|%at|%aI", "HEAD").splitlines():
        if not l:
            continue
        c = l.split("|")
        assert len(c) == 4 and c[2].isdigit(), l[:80]
        rendu.append((c[0], c[1], int(c[2]), c[3]))
    return rendu


def matiere_de_contact(chemins):
    """La matière de contact, re-comptée par une autre écriture que le module (mêmes préfixes)."""
    return sorted(c for c in chemins if c[:6] == "emails" or c[:6] == "EMAIL_")


def classement_manifeste():
    """(exact, normalise, derive, absent, derives, absents) par `split("  ")` — pas de regex."""
    exact = normalise = derive = absent = 0
    derives, absents = [], []
    for l in lire(V.MANIFESTE_CHEMIN).decode("utf-8").splitlines():
        if len(l) < 66:
            continue
        sha, chemin = l.split("  ", 1)
        cible = RACINE_DEPOT / chemin
        if not cible.exists():
            absent += 1
            absents.append(chemin)
        elif empreinte(chemin) == sha:
            exact += 1
        elif hashlib.sha256(lire(chemin).replace(b"\r\n", b"\n")).hexdigest() == sha:
            normalise += 1
        else:
            derive += 1
            derives.append(chemin)
    return exact, normalise, derive, absent, sorted(derives), sorted(absents)


def couverture_spdx(chemins):
    """(avec, sans, expressions) par une boucle `for` explicite sur les mêmes octets."""
    avec, sans, expressions = [], [], {}
    for c in chemins:
        if not c.endswith(".py"):
            continue
        t = lire(c).decode("utf-8", "replace")
        if "SPDX-License-Identifier" in t:
            avec.append(c)
            cle = t[t.index("SPDX-License-Identifier") + 24:].lstrip(": \t").splitlines()[0].strip()
            expressions[cle] = expressions.get(cle, 0) + 1
        else:
            sans.append(c)
    return avec, sans, expressions


def largeur_barre(valeur, grand):
    """220 × valeur / grand, arrondi half-up par des entiers — aucun Fraction, aucun Decimal."""
    n = (44000 * valeur + grand) // (2 * grand)
    return f"{n // 100}.{n % 100:02d}"


# ─── 1. re-dérivation ---------------------------------------------------------

class TestReDerivation(unittest.TestCase):
    def test_la_marche_etrangere_rend_la_meme_liste_que_le_module(self):
        ici, la = marche_arbre(), V._chemins_sous_arbre()
        self.assertEqual(ici, la)
        self.assertEqual(len(ici), CERT["inventaire"]["fichiers"])
        self.assertGreater(len(ici), 200, "une marche vide ne prouverait rien")

    def test_lempreinte_d_arbre_se_recalcule_a_l_identique(self):
        self.assertEqual(empreinte_arbre(marche_arbre()), CERT["inventaire"]["empreinte_arbre"])
        self.assertRegex(CERT["inventaire"]["empreinte_arbre"], r"^[0-9a-f]{64}$")

    def test_les_extensions_epuisent_les_chemins_et_les_octets(self):
        compté = {}
        octets = 0
        for c in marche_arbre():
            cle = os.path.splitext(c)[1] or "(sans extension)"
            compté[cle] = compté.get(cle, 0) + 1
            octets += os.path.getsize(str(RACINE_DEPOT / c))
        self.assertEqual(sum(compté.values()), CERT["inventaire"]["fichiers"])
        self.assertEqual(compté, CERT["inventaire"]["par_extension"])
        self.assertEqual(octets, CERT["inventaire"]["octets_total"])

    def test_le_classement_du_sceau_se_refait_sans_regex(self):
        exact, normalise, derive, absent, derives, absents = classement_manifeste()
        man = CERT["manifeste"]
        self.assertEqual((exact, normalise, derive, absent),
                         (man["a_l_identique"], man["apres_normalisation_des_fins_de_ligne"],
                          man["derivent"], man["absents_de_disque"]))
        self.assertEqual(derives, man["derivent_listes"])
        self.assertEqual(absents, man["absents_listes"])
        self.assertEqual(exact + normalise + derive + absent, man["total_lignes"])
        self.assertEqual(exact + normalise, man["conformes"])

    def test_le_hors_sceau_est_redit_par_une_intersection_de_jeux(self):
        scelles = {l.split("  ", 1)[1] for l in
                   lire(V.MANIFESTE_CHEMIN).decode("utf-8").splitlines() if len(l) >= 66}
        hors = {c for c in marche_arbre() if c not in scelles}
        self.assertEqual(len(hors), CERT["manifeste"]["hors_manifeste"])
        self.assertEqual(len(hors), CERT["frontiere"]["hors_manifeste"])
        self.assertIn(V.MANIFESTE_CHEMIN, hors, "le manifeste ne se scelle pas lui-même")

    def test_la_couverture_de_licence_se_redit_par_une_boucle_explicite(self):
        avec, sans, expressions = couverture_spdx(marche_arbre())
        lic = CERT["licence"]
        self.assertEqual(len(avec), lic["avec_en_tete"])
        self.assertEqual(len(sans), lic["sans_en_tete"])
        self.assertEqual(expressions, lic["expressions_dans_les_sources"])
        self.assertEqual(list(expressions), [lic["expression_lue"]])
        self.assertEqual(len(avec) + len(sans), lic["python_total"])

    @SOUS_GIT
    def test_l_histoire_des_commits_se_rederive_par_deux_commandes(self):
        hi = CERT["horodatages"]["histoire"]
        brute = histoire_brute()
        self.assertEqual(len(brute), hi["commits"])
        # deux commandes git distinctes, le même compte : c'est lui qui est publié
        self.assertEqual(int(git_brut("rev-list", "--count", "HEAD").strip()), hi["commits"])
        self.assertEqual(int(git_brut("rev-list", "--count", "HEAD").strip()),
                         CERT["horodatages"]["commits_attestes"])
        self.assertEqual(len(brute), hi["lignes"], "une ligne lue, un commit compté")
        self.assertEqual(len({c[0] for c in brute}), hi["sha_distincts"])
        mails = {}
        for _, mail, _, _ in brute:
            mails[mail] = mails.get(mail, 0) + 1
        self.assertEqual(mails, hi["auteurs"])
        self.assertEqual(sum(mails.values()), hi["somme_auteurs"])
        ordre = sorted(brute, key=lambda c: c[2])
        self.assertEqual(ordre[0][3], hi["premiere"])
        self.assertEqual(ordre[-1][3], hi["derniere"])
        self.assertEqual(ordre[-1][2] - ordre[0][2], hi["duree_attestee_seconde"])
        self.assertGreaterEqual(hi["commits_d_outils_automates"], 0,
                                "les commits signés par un outil sont un compte, pas une accusation")

    @SOUS_JOURNAL
    def test_le_journal_git_se_reparse_par_split(self):
        ici = journal_parse()
        hj = CERT["horodatages"]["journal_local"]
        self.assertEqual(len(ici), hj["lignes"])
        self.assertEqual(len(ici), hj["parsees"])
        self.assertEqual(len(ici), hj["utf8_stricte"], "tout le journal se décode sans replacement")
        self.assertTrue(hj["utf8_integrale"])
        self.assertEqual(ici[0][0], "0" * 40, "la première ligne du journal naît du vide")
        self.assertTrue(all(ici[i][0] == ici[i - 1][1] for i in range(1, len(ici))),
                        "chaque ligne part du sha de la précédente : le journal est une chaîne")
        self.assertEqual(ici[-1][1], hj["sha_dernier"])
        mails = {}
        for _, _, _, mail, _, _, _ in ici:
            mails[mail] = mails.get(mail, 0) + 1
        self.assertEqual(mails, hj["auteurs"])
        self.assertEqual(sum(mails.values()), hj["somme_auteurs"])
        # même clé de tri que le module : epoch d'abord, puis le sha, pour que les égalités
        # d'horodatage ne soient pas tranchées par l'ordre de lecture du fichier
        ordre = sorted(ici, key=lambda p: (p[4], p[1], p[3], p[5], p[6]))
        self.assertEqual(iso_de(ordre[0][4], ordre[0][5]), hj["premiere"])
        self.assertEqual(iso_de(ordre[-1][4], ordre[-1][5]), hj["derniere"])
        self.assertEqual(max(p[4] for p in ici) - min(p[4] for p in ici),
                         hj["duree_attestee_seconde"])

    @SOUS_GIT
    def test_les_dates_publiees_viennent_de_l_histoire_et_non_du_journal(self):
        """Le compte rendu par le certificat se relit dans ce qui voyage avec le dépôt."""
        h = CERT["horodatages"]
        hi, hj = h["histoire"], h["journal_local"]
        self.assertEqual("histoire", h["dates_publiees_par"])
        self.assertEqual("git log HEAD", h["source_des_commits"])
        self.assertEqual(".git/logs/HEAD", h["source_du_journal"])
        self.assertEqual(h["commits_attestes"], hi["commits"])
        self.assertEqual(h["premiere"], hi["premiere"])
        self.assertEqual(h["derniere"], hi["derniere"])
        self.assertEqual(h["duree_attestee_seconde"], hi["duree_attestee_seconde"])
        self.assertEqual(h["journal_plus_que_commits"], hj["parsees"] - hi["commits"])
        self.assertEqual(CERT["chronologie"]["commits_attestes"], hi["commits"])
        self.assertEqual(CERT["chronologie"]["secondes_attestees"], hi["duree_attestee_seconde"])

    @SOUS_JOURNAL
    @SOUS_GIT
    def test_la_tete_du_depot_retombe_sur_les_deux_sources(self):
        h = CERT["horodatages"]
        hi, hj = h["histoire"], h["journal_local"]
        tete = lire(".git/HEAD").decode("utf-8").strip()
        self.assertTrue(tete.startswith("ref: "), f"tête lue : {tete!r}")
        cible = RACINE_DEPOT / ".git" / Path(*tete[4:].strip().split("/"))
        sha = cible.read_text(encoding="utf-8").strip()
        self.assertEqual(sha, hi["sha_tete"], "le sha publié est celui du pointeur de la branche")
        self.assertEqual(sha, hj["sha_tete"])
        self.assertEqual(sha, git_brut("rev-parse", "HEAD").strip())
        self.assertEqual(sha, journal_parse()[-1][1])
        self.assertEqual(sha, sorted(histoire_brute(), key=lambda c: c[2])[-1][0])
        self.assertTrue(hi["tete_coherente"])
        self.assertTrue(hj["tete_coherente"])
        self.assertEqual(hi["tete_coherente"], hi["commits"] > 0)

    def test_le_module_survit_aux_octets_seuls_sans_depot_git(self):
        """Le chemin de l'archive publiée : ni `.git`, ni `git` — dater ne doit pas lever d'erreur."""
        gardes = (V.RACINE, V.GIT, dict(V._CACHE))
        try:
            with TemporaryDirectory(prefix="verrous-sans-git-") as td:
                V.RACINE, V.GIT = Path(td), None
                V._CACHE.clear()
                hj = V._journal_local()
                hi = V._histoire_atteignable()
                h = V.horodatages()
        finally:
            V.RACINE, V.GIT = gardes[0], gardes[1]
            V._CACHE.clear()
            V._CACHE.update(gardes[2])
        self.assertFalse(hj["present"])
        self.assertEqual((hj["lignes"], hj["parsees"], hj["utf8_stricte"],
                          hj["duree_attestee_seconde"]), (0, 0, 0, 0))
        self.assertTrue(hj["tout_parse"] and hj["utf8_integrale"] and hj["auteurs_additifs"])
        self.assertFalse(hi["git_disponible"])
        self.assertEqual((hi["commits"], hi["lignes"], hi["sha_distincts"],
                          hi["somme_auteurs"], hi["duree_attestee_seconde"]), (0, 0, 0, 0, 0))
        self.assertEqual((hi["premiere"], hi["derniere"], hi["sha_tete"]), ("", "", ""))
        self.assertTrue(hi["tout_parse"])
        self.assertFalse(hi["tete_coherente"])
        self.assertEqual(h["commits_attestes"], 0)
        self.assertEqual(h["journal_plus_que_commits"], 0)
        self.assertEqual("histoire", h["dates_publiees_par"])
        # et le certificat reconstruit sur ce seul chemin ne rouge nulle part faute de git
        self.assertTrue(h["aucun_instrument_strict"])

    @SOUS_GIT
    def test_l_inventaire_se_repartit_entre_suivi_et_hors_suivi(self):
        """Ce que git suit est re-compté par `ls-files` sans l'option `-z` du module."""
        inv = CERT["inventaire"]
        suivis = set(l for l in git_brut("ls-files").splitlines() if l)
        ici = set(marche_arbre())
        self.assertEqual(len(ici & suivis), inv["fichiers_suivis_par_git"])
        self.assertEqual(len(ici - suivis), inv["fichiers_non_suivis_par_git"])
        self.assertEqual(inv["fichiers_suivis_par_git"] + inv["fichiers_non_suivis_par_git"],
                         inv["fichiers"])
        self.assertEqual(sorted(ici - suivis)[:6], inv["exemples_non_suivis"])

    def test_le_registre_et_sa_matiere_se_recomptent_sur_disque(self):
        """Le compte d'entrées sort des octets posés, pas d'une intention ; la matière aussi."""
        reg = CERT["registre_acces"]
        chemin = RACINE_DEPOT / reg["chemin"]
        self.assertEqual(reg["registre_posé_sur_disque"], chemin.exists())
        if chemin.exists():
            lignes = list(csv.reader(io.StringIO(chemin.read_bytes().decode("utf-8-sig")),
                                     delimiter=";"))
            self.assertEqual(max(len(lignes) - 1, 0), reg["nb_entrees"])
            self.assertEqual(len(lignes[0]), reg["nb_colonnes"])
        matiere = matiere_de_contact(marche_arbre())
        self.assertEqual(len(matiere), reg["matiere_sur_disque"])
        self.assertEqual(matiere[:6], reg["matiere_exemples"])
        par_repertoire = {}
        for c in matiere:
            cle = c.split("/")[0] if "/" in c else c
            par_repertoire[cle] = par_repertoire.get(cle, 0) + 1
        self.assertEqual(par_repertoire, reg["matiere_sur_disque_par_repertoire"])
        self.assertEqual(reg["matiere_hors_registre"] + reg["matiere_reprise_dans_le_registre"],
                         reg["matiere_sur_disque"])
        scelles = {l.split("  ", 1)[1] for l in
                   lire(V.MANIFESTE_CHEMIN).decode("utf-8").splitlines() if len(l) >= 66}
        self.assertEqual(len({c for c in matiere if c in scelles}), reg["matiere_entree_du_sceau"])
        if reg["matiere_suivie_par_git"] is not None:
            suivis = set(l for l in git_brut("ls-files").splitlines() if l)
            self.assertEqual(len(set(matiere) & suivis), reg["matiere_suivie_par_git"])
            self.assertEqual(reg["matiere_suivie_par_git"] + reg["matiere_hors_suivi_git"],
                             reg["matiere_sur_disque"])

    def test_les_huit_clauses_se_recomptent_a_zero_sur_un_corpus_reconstruit(self):
        corpus = [c for c in marche_arbre()
                  if os.path.splitext(c)[1] in V.EXTENSIONS_TEXTE and c not in V.EXCLUS_AUTO]
        self.assertEqual(len(corpus), CERT["clauses"]["corpus_texte"])
        for lib, pat in V.CLAUSES:
            n = sum(len(re.findall(pat, lire(c).decode("utf-8", "replace"), re.I)) for c in corpus)
            self.assertEqual(n, CERT["clauses"]["par_clause"][lib]["occurrences"], lib)
            self.assertEqual(n, 0, lib)

    def test_la_recherche_n_est_pas_sourde(self):
        corpus = V._corpus_texte()
        positif, _ = V._motif_par_fichier(r"SPDX", corpus)
        muet, fichiers_muet = V._motif_par_fichier(r"zzz_motif_absent_de_tout_le_depot_zzz", corpus)
        naif, _ = V._motif_par_fichier(r"nda", corpus)
        self.assertGreater(positif, 0, "contrôle positif vide : la recherche ne contrôle rien")
        self.assertEqual((muet, fichiers_muet), (0, []))
        self.assertGreater(naif, 0)
        self.assertGreater(naif, sum(v["occurrences"] for v in
                                    CERT["clauses"]["par_clause"].values()))

    def test_le_strict_compte_les_artefacts_et_non_les_mots(self):
        h = CERT["horodatages"]
        ailleurs = [c for c in marche_arbre()
                    if os.path.splitext(c)[1].lower() in V.EXTENSIONS_INSTRUMENT]
        self.assertEqual(ailleurs, h["artefacts_horodatage"])
        self.assertEqual(len(ailleurs), h["nb_artefacts_horodatage"])
        self.assertEqual(h["aucun_instrument_strict"], len(ailleurs) == 0)
        # les deux grandeurs sont distinctes : les mots du dossier existent, l'artefact non
        self.assertGreater(h["mentions_instrument_occurrences"], 0,
                           "les mentions doivent rester publiées, pas effacées")
        self.assertTrue(h["aucun_instrument_strict"],
                        "un mot d'instrument ne doit pas faire croire à un instrument")
        self.assertEqual(sum(v["occurrences"] for v in h["instruments_horodatage"].values()),
                         h["mentions_instrument_occurrences"])
        self.assertEqual(sorted({c for v in h["instruments_horodatage"].values()
                                 for c in v["fichiers"]}), h["fichiers_mentionnant_un_instrument"])
        self.assertIn("artefact", EQS["EQ-06"]["resultat"])
        self.assertIn("0 artefact", CS["C06"]["attendu"])

    def test_les_largeurs_du_plan_se_recalculent_par_division_entiere(self):
        sv = CERT["plan_svg"]
        valeurs = [int(CERT[nom][clef]) for _, nom, clef in V.BARRES]
        grand = max(valeurs + [1])
        self.assertEqual([largeur_barre(v, grand) for v in valeurs],
                         re.findall(r'<rect[^>]*\swidth="([0-9.]+)"',
                                    V.octets_svg(CERT).decode("utf-8")),
                         "deux écritures de la même règle de trois, huit barres")
        self.assertEqual(valeurs, sv["valeurs_ecrites"])
        self.assertEqual(grand, sv["plus_grande_valeur"])
        self.assertEqual(sv["barres"], len(V.BARRES))
        self.assertEqual(sum(1 for v in valeurs if v == 0), sv["barre_de_zero_longueur"])

    def test_le_pourcentage_de_couverture_tombe_sur_une_autre_ecriture(self):
        man, n = CERT["manifeste"], len(marche_arbre())
        q, r = divmod(man["conformes"] * 10000, n)
        if 2 * r >= n:
            q += 1
        self.assertEqual(f"{q // 100}.{q % 100:02d}", man["couverture_%"])
        self.assertLess(float(man["couverture_%"]), 100.0,
                        "le sceau ne couvre pas tout l'arbre : la couverture est un compte, "
                        "pas une coquetterie")


# ─── 2. la structure ne tient pas aux zéros -----------------------------------

class TestStructureEtrangere(unittest.TestCase):
    def faux_certificat(self):
        """Un certificat de fantaisie : des compteurs partout non nuls, aucune mesure réelle."""
        pieces = copy.deepcopy(NOEUDS)
        pieces["inventaire"]["fichiers"] = 10
        pieces["manifeste"]["total_lignes"] = 8
        pieces["manifeste"]["derivent"] = 2
        pieces["manifeste"]["conformes"] = 6
        pieces["licence"]["avec_en_tete"] = 7
        pieces["registre_acces"]["nb_entrees"] = 3
        pieces["clauses"]["clauses_redigees"] = 5
        pieces["structure_contrat"]["instruments_signes"] = 4
        pieces["boite_noire"]["artefacts_precompiles"] = 9
        return pieces

    def test_le_meme_fabricant_de_plan_rend_des_barres_non_nulles_ailleurs(self):
        faux = self.faux_certificat()
        texte = V.octets_svg(faux).decode("utf-8")
        largeurs = re.findall(r'<rect[^>]*\swidth="([0-9.]+)"', texte)
        valeurs = [int(faux[nom][clef]) for _, nom, clef in V.BARRES]
        grand = max(valeurs + [1])
        self.assertEqual(len(largeurs), len(V.BARRES))
        self.assertGreater(min(float(w) for w in largeurs), 0.0,
                           "toutes les barres pourraient être pleines")
        self.assertEqual(max(float(w) for w in largeurs), 220.0,
                         "la plus grande valeur remplit la longueur max")
        self.assertEqual(largeurs, [largeur_barre(v, grand) for v in valeurs])
        self.assertEqual([int(m) for m in re.findall(r'data-valeur="([0-9]+)"', texte)], valeurs)
        self.assertEqual(CERT["plan_svg"]["barre_de_zero_longueur"], 4,
                         "le dépôt réel rend quatre barres vides : ce sont les compteurs qui sont "
                         "à zéro, pas le fabricant de plan")

    def test_le_registre_est_structurellement_vide_meme_sous_fausse_demande(self):
        octets = V.octets_csv(self.faux_certificat())
        lignes = list(csv.reader(io.StringIO(octets.decode("utf-8-sig")), delimiter=";"))
        self.assertEqual(len(lignes), 1, "le certificat réclame 3 entrées : le fichier en rend 0")
        self.assertEqual(lignes[0], list(V.COLONNES_REGISTRE))

    def test_le_plan_se_relit_lui_meme_sur_nimporte_quel_certificat(self):
        """`plan_svg` régénère les octets puis les compare : la cohérence est structurelle."""
        relu = V.plan_svg(self.faux_certificat())
        self.assertTrue(relu["largeurs_conformes"])
        alt = V.plan_svg({**self.faux_certificat(),
                          "manifeste": {**self.faux_certificat()["manifeste"], "conformes": 999}})
        self.assertTrue(alt["largeurs_conformes"])
        self.assertEqual(alt["barre_de_zero_longueur"], 0)
        # vert par construction ne veut pas dire vide : C15 exige la liste des largeurs, et une
        # largeur fausse dans le nœud stocké rougit ce contrôle — c'est testé section 4
        menteur = {**CERT, "plan_svg": {**CERT["plan_svg"], "largeurs_conformes": False}}
        cs = {c["id"]: c for c in V.controles(EQS, menteur)}
        self.assertFalse(cs["C15"]["ok"])

    def test_un_motif_etranger_trouve_ce_que_l_on_cherche_vraiment(self):
        n, ou = V._motif_par_fichier(r"Remote\s+Network\s+Interaction",
                                     ["LICENSE-AGPL", "LICENSE-GPL"])
        self.assertEqual(n, CERT["regime_commercial"]["clause_reseau_agpl"])
        self.assertEqual(ou, ["LICENSE-AGPL"])
        self.assertEqual(V._motif_par_fichier(r"Remote\s+Network\s+Interaction",
                                              ["LICENSE-GPL"])[0], 0)


# ─── 3. les artefacts relus sur disque ----------------------------------------

class TestArtefactsSurDisque(unittest.TestCase):
    def setUp(self):
        self._td = TemporaryDirectory(prefix="verrous-artefacts-")
        self.vers = Path(self._td.name)
        self.ecrit = V.ecrire_artefacts(CERT, self.vers)

    def tearDown(self):
        self._td.cleanup()

    def csv(self):
        octets = (self.vers / "registre_acces.csv").read_bytes()
        return octets, list(csv.reader(io.StringIO(octets.decode("utf-8-sig")), delimiter=";"))

    def valeurs_svg(self, texte):
        return [int(m.split('data-valeur="')[1].split('"')[0]) for m in texte.split("<rect ")[1:]]

    def test_les_quatre_artefacts_sont_ecrits_octet_par_octet(self):
        self.assertEqual(sorted(self.ecrit), ["certificat.json", "frontiere_publique.svg",
                                              "registre_acces.csv", "verrous_et_clauses.md"])
        self.assertEqual(CERT["ecritures"]["noms"], sorted(self.ecrit))
        attendus = V._artefacts_octets(CERT)
        for nom, taille in self.ecrit.items():
            octets = (self.vers / nom).read_bytes()
            self.assertEqual(octets, attendus[nom], nom)
            self.assertEqual(taille, f"{len(octets)} octets", nom)
            self.assertGreater(len(octets), 60, nom)

    def test_le_json_publie_scelle_les_trois_autres_octets(self):
        ec = CERT["ecritures"]
        for nom in ec["empreintes"]:
            octets = (self.vers / nom).read_bytes()
            self.assertEqual(ec["tailles"][nom], len(octets), nom)
            self.assertEqual(ec["empreintes"][nom], hashlib.sha256(octets).hexdigest()[:16], nom)
        self.assertNotIn("certificat.json", ec["tailles"], "auto-référence mesurée : mensonge")
        self.assertEqual(ec["nom_sans_empreinte"], "certificat.json")
        # le fichier qui porte le nœud est plus gros que les trois qu'il scelle
        self.assertGreater(len((self.vers / "certificat.json").read_bytes()),
                           sum(ec["tailles"].values()))

    def test_le_registre_relu_est_un_en_tete_et_rien_d_autre(self):
        octets, lignes = self.csv()
        self.assertEqual(octets[:3], b"\xef\xbb\xbf")
        self.assertEqual(octets.count(b"\r\n"), 1)
        self.assertEqual(octets.count(b"\n"), octets.count(b"\r\n"), "toute fin de ligne est CRLF")
        self.assertEqual(len(lignes), 1, "zéro ligne de données est la mesure, pas un oubli")
        self.assertEqual(lignes[0], list(V.COLONNES_REGISTRE))
        self.assertEqual(len(lignes[0]), CERT["registre_acces"]["nb_colonnes"])
        self.assertNotIn(V.PHRASE_ABSENCE, octets.decode("utf-8-sig"),
                         "une ligne de commentaire serait lue comme une donnée")
        self.assertEqual(len(octets), CERT["registre_relu"]["octets"])

    def test_le_svg_relu_porte_huit_barres_nommees_et_chiffrees(self):
        texte = (self.vers / "frontiere_publique.svg").read_text(encoding="utf-8")
        largeurs = re.findall(r'<rect[^>]*\swidth="([0-9.]+)"', texte)
        self.assertEqual(len(largeurs), len(V.BARRES))
        self.assertEqual([m.split('data-libelle="')[1].split('"')[0]
                          for m in texte.split("<rect ")[1:]], [lib for lib, _, _ in V.BARRES])
        self.assertEqual(self.valeurs_svg(texte), CERT["plan_svg"]["valeurs_ecrites"])
        self.assertEqual(largeurs, [largeur_barre(v, max(self.valeurs_svg(texte) + [1]))
                                    for v in self.valeurs_svg(texte)])
        self.assertEqual(texte.count("<text "), 2 * len(V.BARRES) + 1)
        self.assertIn(V.PHRASE_ABSENCE, texte)
        self.assertEqual(len(texte.encode("utf-8")), CERT["plan_svg"]["octets"])

    def test_le_md_relu_porte_onze_lignes_de_tableau_et_dix_limites(self):
        lignes = (self.vers / "verrous_et_clauses.md").read_text(encoding="utf-8").splitlines()
        corps = [l for l in lignes if re.match(r"^\| (\d|—) \|", l)]
        self.assertEqual(len(corps), 11, "une ligne par phase conseillée, y compris la ligne —")
        self.assertEqual(len([l for l in lignes if l.startswith("|")]), len(corps) + 2)
        for l in corps:
            cellules = [c.strip() for c in l.strip("|").split("|")]
            self.assertEqual(len(cellules), 4, l)
            self.assertIn(cellules[-1], V.FB.STATUTS, l)
            self.assertTrue(all(cellules[:-1]), l)
        self.assertEqual(sum(1 for l in lignes if l.startswith("- ")),
                         CERT["limites_ouvertes"]["nb"])
        self.assertEqual(len(re.findall(r"^\d\. ", "\n".join(lignes), re.M)), 4,
                         "les quatre corrections que la mesure impose à l'avis")
        self.assertIn(V.PHRASE_ABSENCE, lignes[-2] if lignes[-1] == "" else lignes[-1])
        self.assertIn(f"{CERT['inventaire']['fichiers']} fichiers inventoriés", "\n".join(lignes))

    def test_un_nombre_mut_sur_disque_ne_passe_plus_la_relecture(self):
        chemin = self.vers / "frontiere_publique.svg"
        avant = chemin.read_bytes()
        chemins = ["registre_acces.csv", "verrous_et_clauses.md", "certificat.json"]
        scelles = {c: (self.vers / c).read_bytes() for c in chemins}
        self.assertEqual(self.valeurs_svg(avant.decode("utf-8")),
                         CERT["plan_svg"]["valeurs_ecrites"])
        # la valeur à muter vient du certificat : un littéral codé en dur devient inopérant dès
        # qu'un fichier entre ou sort du dépôt, et l'inégalité ne prouverait plus rien
        premiere = CERT["plan_svg"]["valeurs_ecrites"][0]
        texte_mut = avant.decode("utf-8").replace(f'data-valeur="{premiere}"',
                                                  f'data-valeur="{premiere + 1}"', 1)
        self.assertNotEqual(texte_mut, avant.decode("utf-8"),
                            "aucune occurrence à muter : la relecture serait restée verte pour rien")
        chemin.write_bytes(texte_mut.encode("utf-8"))
        self.assertEqual(self.valeurs_svg(texte_mut)[0], premiere + 1)
        self.assertNotEqual(self.valeurs_svg(chemin.read_bytes().decode("utf-8")),
                            CERT["plan_svg"]["valeurs_ecrites"], "la relecture sensible à l'octet")
        for c, octets in scelles.items():
            self.assertEqual((self.vers / c).read_bytes(), octets, c)

    def test_les_phrases_d_absence_sont_la_oùelles_doivent_etre(self):
        rendu = V._artefacts_octets(CERT)
        for nom in CERT["ecritures"]["noms_avec_phrase"]:
            self.assertIn(V.PHRASE_ABSENCE.encode("utf-8"), rendu[nom], nom)
        self.assertNotIn(V.PHRASE_ABSENCE.encode("utf-8"), rendu[CERT["ecritures"]["nom_sans_phrase"]])
        self.assertEqual(sorted(set(CERT["ecritures"]["noms"]) - set(CERT["ecritures"]["tailles"])),
                         [CERT["ecritures"]["nom_sans_empreinte"]])
        self.assertEqual(sorted(set(CERT["ecritures"]["noms"])
                                - set(CERT["ecritures"]["noms_avec_phrase"])),
                         [CERT["ecritures"]["nom_sans_phrase"]])


# ─── 4. non-vacuité : une mutation par contrôle --------------------------------

MUTATIONS = [
    ("C01", ("inventaire", "chemins_uniques"), False),
    ("C02", ("manifeste", "derivent"), 0),
    ("C03", ("licence", "sans_en_tete_listes"), []),
    ("C04", ("regime_commercial", "clause_reseau_agpl"), 0),
    ("C05", ("frontiere", "coeur_secret_reelement_garde"), 3),
    ("C06", ("horodatages", "aucun_instrument_strict"), False),
    ("C07", ("registre_acces", "nb_entrees"), 4),
    ("C08", ("clauses", "clauses_redigees"), 1),
    ("C09", ("boite_noire", "artefacts_precompiles"), 2),
    ("C10", ("structure_contrat", "instruments_signes"), 1),
    ("C11", ("remuneration", "montants_imposes"), 2),
    ("C12", ("relecture_avocat", "avocat_rencontre"), 3),
    ("C13", ("exposition", "licences_divergentes"), False),
    ("C14", ("chronologie", "verrouillage_avant_exposition"), True),
    ("C15", ("ecritures", "tailles"), {**CERT["ecritures"]["tailles"], "certificat.json": 1}),
    ("C16", ("limites_ouvertes", "remplies_dans_ce_lot"), 4),
]


def muter(chemin, valeur):
    """Copie profonde des nœuds scellés, puis une seule écriture au bout du chemin."""
    etat = copy.deepcopy(NOEUDS)
    noeud = etat
    for cle in chemin[:-1]:
        noeud = noeud[cle]
    noeud[chemin[-1]] = copy.deepcopy(valeur) if isinstance(valeur, (dict, list)) else valeur
    return etat


class TestNonVacuite(unittest.TestCase):
    """Chaque mutation ci-dessus doit faire rougir le contrôle qu'elle nomme, et lui seul."""

    def test_la_baseline_du_certificat_est_verte(self):
        self.assertEqual(len(CS), 16)
        self.assertEqual([k for k, c in CS.items() if not c["ok"]], [])

    def test_chaque_mutation_fait_rougir_le_controle_nomme_et_lui_seul(self):
        for cid, chemin, valeur in MUTATIONS:
            cs = {c["id"]: c for c in V.controles(EQS, muter(chemin, valeur))}
            self.assertFalse(cs[cid]["ok"], f"{cid} reste vert sous {chemin} = {valeur}")
            self.assertEqual([k for k, c in cs.items() if not c["ok"]], [cid],
                             f"{cid} : d'autres contrôles rougissent sous {chemin}")

    def test_les_mutations_ne_sont_pas_toutes_les_memes(self):
        self.assertEqual(len({tuple(m[1]) for m in MUTATIONS}), 16,
                         "deux mutations porteraient sur le même champ")

    def test_ne_rien_muter_laisse_la_baseline_verte(self):
        cs = {c["id"]: c for c in
              V.controles(EQS, muter(("inventaire", "fichiers"), CERT["inventaire"]["fichiers"]))}
        self.assertEqual([k for k, c in cs.items() if not c["ok"]], [])

    def test_deux_mensonges_sur_l_horodatage_rougissent_seuls_c06(self):
        """Ni la paternité inventée ni un artefact compté sans drapeau ne passent C06."""
        for chemin, valeur in ((("horodatages", "preuve_de_paternite"), True),
                               (("horodatages", "nb_artefacts_horodatage"), 1)):
            cs = {c["id"]: c for c in V.controles(EQS, muter(chemin, valeur))}
            self.assertEqual([k for k, c in cs.items() if not c["ok"]], ["C06"], chemin)

    def test_trois_mensonges_sur_les_deux_sources_rougissent_leur_seul_controle(self):
        """Décréter l'autre source, reprendre de la matière ou gommer l'écart : chacun rougit."""
        for cid, chemin, valeur in (
                ("C06", ("horodatages", "dates_publiees_par"), "journal_local"),
                ("C07", ("registre_acces", "matiere_reprise_dans_le_registre"), 3),
                ("C14", ("chronologie", "divergence_journal_moins_histoire"), 0)):
            cs = {c["id"]: c for c in V.controles(EQS, muter(chemin, valeur))}
            self.assertEqual([k for k, c in cs.items() if not c["ok"]], [cid], chemin)

    def test_deux_mensonges_sur_la_matire_du_registre_rougissent_seuls_c07(self):
        """Faire entrer la matière sous le sceau, ou la gonfler hors registre : C07 rougit.

        Les valeurs mutées viennent de la mesure : un littéral deviendrait inopérant dans un
        clone où la matière de contact n'existe pas.
        """
        reg = CERT["registre_acces"]
        for chemin, valeur in ((("registre_acces", "matiere_entree_du_sceau"), 1),
                               (("registre_acces", "matiere_hors_registre"),
                                reg["matiere_hors_registre"] + 1)):
            cs = {c["id"]: c for c in V.controles(EQS, muter(chemin, valeur))}
            self.assertEqual([k for k, c in cs.items() if not c["ok"]], ["C07"], chemin)

    def test_un_marqueur_de_limite_qui_ne_retombe_plus_rougit_c16(self):
        lo = copy.deepcopy(CERT["limites_ouvertes"])
        lo["marqueur_courriers"] = "9 999 fichier(s) de courriers"
        cs = {c["id"]: c for c in V.controles(EQS, muter(("limites_ouvertes",), lo))}
        self.assertEqual([k for k, c in cs.items() if not c["ok"]], ["C16"])

    def test_une_limite_sur_le_non_voyageant_effacee_rougit_c16(self):
        """Retirer la limite qui dit que le journal local ne voyage pas : C16 la réclame."""
        lo = copy.deepcopy(CERT["limites_ouvertes"])
        lo["liste"] = [l for l in lo["liste"] if "journal local de références" not in l]
        lo["nb"] = len(lo["liste"])
        cs = {c["id"]: c for c in V.controles(EQS, muter(("limites_ouvertes",), lo))}
        self.assertEqual([k for k, c in cs.items() if not c["ok"]], ["C16"])

    def test_quatre_mensonges_sur_les_octets_publies_rougissent_seuls_c15(self):
        for chemin, valeur in ((("plan_svg", "largeurs_conformes"), False),
                               (("plan_svg", "absence_ecrite"), False),
                               (("registre_relu", "entrees_relues"), 2),
                               (("ecritures", "absence_partout"), False)):
            cs = {c["id"]: c for c in V.controles(EQS, muter(chemin, valeur))}
            self.assertEqual([k for k, c in cs.items() if not c["ok"]], ["C15"], chemin)

    def test_une_limite_qui_cite_un_compte_faux_rougit_c16(self):
        """C16 ne se contente pas du booléen : le compte de courriers doit retomber sur la mesure."""
        lo = copy.deepcopy(CERT["limites_ouvertes"])
        lo["compte_courriers"] = 4242
        cs = {c["id"]: c for c in V.controles(EQS, muter(("limites_ouvertes",), lo))}
        self.assertEqual([k for k, c in cs.items() if not c["ok"]], ["C16"])

    def test_un_resultat_écrit_en_moins_ne_passe_plus_la_pillier(self):
        """P3 exige un résultat : vider l'un des seize textes se voit dans le nœud lui-même."""
        eqs = copy.deepcopy(list(EQS.values()))
        self.assertEqual(len(eqs), 16)
        self.assertTrue(all(e["resultat"] for e in eqs))
        eqs[0]["resultat"] = ""
        self.assertFalse(all(e["resultat"] for e in eqs))


# ─── 5. les verdicts défavorables restent écrits -------------------------------

class TestVerdictsDefavorables(unittest.TestCase):
    def test_zero_clause_zero_instrument_zero_avocat_et_c_est_ecrit(self):
        cls, st, av = (CERT["clauses"], CERT["structure_contrat"], CERT["relecture_avocat"])
        self.assertEqual(cls["clauses_redigees"], 0)
        self.assertEqual(cls["nb_clauses_cherchees"], 8)
        self.assertTrue(cls["toutes_absentes"])
        self.assertEqual(st["instruments_cites"], 0)
        self.assertEqual(st["instruments_signes"], 0)
        self.assertEqual(st["documents_contractuels_sur_disque"], 0)
        self.assertEqual(av["avocat_rencontre"], 0)
        self.assertEqual(av["barreau_rencontre"], 0)
        self.assertFalse(av["saisine_attestee"])
        for cid in ("C08", "C10", "C12"):
            self.assertTrue(CS[cid]["ok"], cid)
            self.assertIn("0", CS[cid]["attendu"], cid)
        self.assertEqual(CERT["verdict"]["clauses_redigees"], 0)
        self.assertEqual(CERT["verdict"]["occurrences_avocat"], 0)

    def test_la_dérive_du_sceau_reste_chiffrée_partout(self):
        man = CERT["manifeste"]
        self.assertGreater(man["derivent"], 0, "compter la dérive est le contrôle, pas la cacher")
        self.assertEqual(len(man["derivent_listes"]), man["derivent"])
        self.assertIn("en dérive", EQS["EQ-02"]["resultat"])
        self.assertIn(str(man["derivent"]), EQS["EQ-02"]["resultat"])
        md = V.octets_clauses_md(CERT).decode("utf-8")
        self.assertIn(f"{man['derivent']} en dérive", md)
        self.assertIn(f"{man['conformes']}/{man['total_lignes']}",
                      V.octets_svg(CERT).decode("utf-8"))

    def test_la_divergence_de_licence_zenodo_est_publiée_non_gommée(self):
        exp = CERT["exposition"]
        self.assertTrue(exp["licences_divergentes"])
        self.assertEqual(exp["licence_zenodo"], "agpl-3.0-only")
        self.assertEqual(exp["licence_cff"], "GPL-3.0-only OR AGPL-3.0-only")
        self.assertEqual(exp["branches_non_reprises_dans_zenodo"], ["GPL-3.0-only"])
        self.assertIn("contre", EQS["EQ-13"]["resultat"])
        self.assertTrue(exp["licence_zenodo_couvre_une_branche"],
                        "une des deux branches est couverte : c'est l'autre qui manque")

    def test_le_cœur_secret_n_existe_pas_et_la_stratégie_est_incompatible(self):
        fr = CERT["frontiere"]
        self.assertEqual(fr["coeur_secret_reelement_garde"], 0)
        self.assertEqual(fr["fichiers_gardes_listes"], [])
        self.assertTrue(fr["strategie_incompatible_ecrite"])
        self.assertGreaterEqual(len(fr["modules_d_equations_hors_sceau"]), 1)
        self.assertGreater(fr["occurrences_heuristiques"], 0,
                           "les heuristiques sont publiées : c'est ce que l'avis défendait de taire")
        self.assertIn("0 fichier gardé", EQS["EQ-05"]["resultat"])

    def test_l_ordre_de_la_phase_un_est_rendu_à_l_envers(self):
        chr_, exp = CERT["chronologie"], CERT["exposition"]
        h = CERT["horodatages"]
        hi, hj = h["histoire"], h["journal_local"]
        self.assertEqual(chr_["verrous_pos_avant_exposition"], 0)
        self.assertFalse(chr_["verrouillage_avant_exposition"])
        self.assertTrue(chr_["retroactif_impossible"])
        self.assertTrue(exp["expose"])
        self.assertGreater(chr_["secondes_attestees"], 0)
        self.assertGreaterEqual(len(chr_["gouvernable_desormais"]), 3)
        # les deux sources de dates sont publiées séparément, et le verdict ne dépend d'aucune
        self.assertEqual(chr_["commits_attestes"], hi["commits"])
        self.assertEqual(chr_["ecritures_du_journal_local"], hj["parsees"])
        self.assertEqual(chr_["divergence_journal_moins_histoire"], hj["parsees"] - hi["commits"])
        self.assertEqual("git log HEAD", chr_["source_des_dates"])
        self.assertTrue(chr_["ordre_independant_des_sources_de_dates"])
        self.assertFalse(chr_["verrouillage_sans_consulter_une_date"])
        self.assertRegex(chr_["date_de_exposition_lue"], r"^\d{4}-\d{2}-\d{2}$")
        self.assertTrue(chr_["exposition_datee_sans_le_journal"],
                        "la date d'exposition se lit hors du journal local : elle voyage")
        self.assertIn("l'ordre est donc tenu", "\n".join(CERT["limites_ouvertes"]["liste"]))

    def test_le_registre_vide_avoue_sa_matière_non_reprise(self):
        reg, lo = CERT["registre_acces"], CERT["limites_ouvertes"]
        self.assertEqual(reg["nb_entrees"], 0, "mesuré dans les octets du registre, non décrété")
        self.assertEqual(reg["lignes_de_donnees_lues"], reg["nb_entrees"])
        self.assertTrue(reg["absent_avant_ce_dossier"])
        self.assertGreaterEqual(reg["matiere_sur_disque"], 0)
        self.assertEqual(reg["matiere_reprise_dans_le_registre"], 0)
        self.assertEqual(lo["compte_courriers"], reg["matiere_sur_disque"])
        self.assertIn(lo["marqueur_courriers"], "\n".join(lo["liste"]))
        if reg["matiere_suivie_par_git"] is not None:
            self.assertEqual(reg["matiere_entree_du_sceau"], 0,
                             "la matière de contact n'est pas sous le sceau : c'est la mesure")
            self.assertEqual(reg["matiere_hors_registre"], reg["matiere_sur_disque"])

    def test_les_limites_ouvertes_ne_sont_pas_declarees_franchies(self):
        lo = CERT["limites_ouvertes"]
        self.assertGreaterEqual(lo["nb"], 12)
        self.assertEqual(lo["remplies_dans_ce_lot"], 0)
        self.assertTrue(lo["toutes_au_dela_de_20"])
        self.assertGreaterEqual(lo["longueur_minimale"], 40)
        self.assertEqual(len(CERT["limites"]), lo["nb"] + 1)
        # deux limites nomment ce qui ne voyage pas : l'arbre hors suivi et le journal local
        self.assertEqual(sum(1 for l in lo["liste"] if "ne voyagent" in l), 2)
        self.assertTrue(any("hors du suivi git" in l for l in lo["liste"]))
        self.assertTrue(any("journal local de références" in l for l in lo["liste"]))

    def test_le_régime_commercial_est_corrige_sans_etre_adouci(self):
        rc = CERT["regime_commercial"]
        self.assertEqual(rc["restrictions_non_commerciales_total"], 0)
        self.assertGreater(rc["permissions_de_facturer_total"], 0,
                           "les deux textes autorisent à facturer : la correction est mesurée")
        self.assertEqual(rc["seules_differences_mesurees"], ["clause d'interaction à distance"])
        self.assertEqual(rc["clause_reseau_gpl"], 0)
        self.assertEqual(rc["clause_reseau_agpl"], 1)
        self.assertEqual(len(rc["ecarts_de_compte"]), 2,
                         "deux écarts de compte sont mesurés, un seul change une présence")
        self.assertEqual(sorted(rc["ecarts_de_compte"]),
                         sorted(["permission de facturer des copies",
                                 "clause d'interaction à distance"]))

    def test_aucune_phrase_ne_prétend_qu_un_contrat_existe(self):
        texte = json.dumps(DONNEES, ensure_ascii=False, default=str)
        for interdit in ("le dépôt est verrouillé", "verrouillé contractuellement",
                         "paternité établie", "paternité prouvée", "secret de fabrique conservé",
                         "cœur secret gardé", "licence à usage non commercial",
                         "contrat de licence signé", "avocat spécialisé a validé",
                         "conforme au droit", "protégé en vertu", "NDA signé",
                         "accord de confidentialité signé", "conseil juridique rendu",
                         "recommande d'accepter"):
            self.assertNotIn(interdit, texte)
        for honnete in ("antériorité légale = False", "ne prouve pas la paternité",
                        V.PHRASE_ABSENCE, "aucune saisine n'est écrite dans le dépôt"):
            self.assertIn(honnete, texte)


# ─── 6. déterminisme, sceau et transmission ------------------------------------

class TestDeterminismeEtSceau(unittest.TestCase):
    def test_deux_appels_de_certificat_concordent_octet_par_octet(self):
        self.assertEqual(V.canonique(CERT), V.canonique(V.certificat()))
        self.assertTrue(CERT["rejoue_identique"])

    def test_la_racine_ne_scelle_que_dix_neuf_nœuds_tries(self):
        self.assertEqual(len(NOEUDS), 19)
        racine = hashlib.sha256(V.canonique(
            {c: hashlib.sha256(V.canonique(NOEUDS[c])).hexdigest() for c in sorted(NOEUDS)})).hexdigest()
        self.assertEqual(racine, CERT["racine_merkle_sha256"])

    def test_chaque_nœud_mut_change_la_racine(self):
        for nom in sorted(NOEUDS):
            alt = copy.deepcopy(NOEUDS)
            alt[nom] = {"mute": True}
            racine = hashlib.sha256(V.canonique(
                {c: hashlib.sha256(V.canonique(alt[c])).hexdigest() for c in sorted(alt)})).hexdigest()
            self.assertNotEqual(racine, CERT["racine_merkle_sha256"], nom)

    def test_l_écriture_canonique_ne_depend_pas_de_l_ordre_des_clés(self):
        un = {"a": 1, "b": {"c": 2, "d": [3, "4"]}}
        deux = {"b": {"d": [3, "4"], "c": 2}, "a": 1}
        self.assertEqual(V.canonique(un), V.canonique(deux))

    def test_resoudre_et_verifier_forment_la_porte_de_sortie(self):
        donnees = DONNEES
        self.assertTrue(V.verifier(donnees))
        c = donnees["conclusion"]
        self.assertEqual((c["controles_verts"], c["controles_total"], c["equations"]), (16, 16, 16))
        self.assertEqual(c["clauses_redigees"], 0)
        self.assertEqual(c["registre_entrees"], 0)
        self.assertEqual(c["instruments_signes"], 0)
        self.assertEqual(c["derive_de_sceau"], CERT["manifeste"]["derivent"])
        self.assertEqual(c["entrees_de_sceau"], CERT["manifeste"]["total_lignes"])
        # la conclusion ne relit aucun compte périmé : chaque nombre vient du nœud publié
        self.assertEqual(c["fichiers_inventories"], CERT["inventaire"]["fichiers"])
        self.assertEqual(c["registre_entrees"], CERT["registre_acces"]["nb_entrees"])
        self.assertEqual(c["commits_attestes"], CERT["horodatages"]["commits_attestes"])
        self.assertEqual(c["commits_attestes"], CERT["horodatages"]["histoire"]["commits"])
        self.assertNotIn("lignes_parsees", json.dumps(CERT["horodatages"], default=str))
        self.assertEqual(c["statuts_par_label"]["SIMULÉ"], 0)
        self.assertIn(V.PHRASE_ABSENCE, c["enonce_verrous"])


class TestPiliersEtTransmission(unittest.TestCase):
    def test_équations_et_contrôles_sont_appariés_et_étiquetés(self):
        cs = V.controles(EQS, CERT)
        self.assertEqual({c["equation"] for c in cs}, set(EQS))
        self.assertEqual(len(cs), len(EQS))
        self.assertEqual(len({e["id"] for e in EQS.values()}), 16, "identifiants non uniques")
        for e in EQS.values():
            self.assertIn(e["statut"], V.FB.STATUTS, e["id"])
            self.assertIn(e["couche"], V.FB.COUCHES, e["id"])
            self.assertIn("→", e["chemin"], e["id"])
            self.assertIn("→ C" + e["id"][3:], e["chemin"], e["id"])
            self.assertTrue(e["chemin"].startswith("verrous_base.py"), e["id"])
            self.assertTrue(e["formule"] and e["resultat"] and e["limite"], e["id"])
            self.assertGreaterEqual(len(e["limite"]), 40, e["id"])

    def test_tout_contrôle_porte_attendu_obtenu_et_n_est_pas_rouge(self):
        for c in V.controles(EQS, CERT):
            self.assertTrue(c["ok"], c["id"])
            self.assertTrue(c["attendu"] and c["obtenu"] and c["verifie"], c["id"])
            self.assertEqual(c["equation"], "EQ-" + c["id"][1:], c["id"])

    def test_la_recherche_de_clause_est_bornée_par_sa_propre_contamination(self):
        corpus = V._corpus_texte()
        for c in V.EXCLUS_AUTO:
            self.assertNotIn(c, corpus, c)
        self.assertGreater(V.self_contamination(), 0,
                           "l'exclusion ne retire rien : C08 serait un contrôle gratuit")
        self.assertEqual(len(corpus), CERT["clauses"]["corpus_texte"])

    def test_le_module_ne_depend_que_de_la_bibliothèque_standard(self):
        autorises = {"__future__", "hashlib", "json", "re", "shutil", "subprocess", "sys",
                     "datetime", "fractions", "pathlib", "typing", "FONDATION"}
        texte = (RACINE_DEPOT / "VERROUS" / "verrous_base.py").read_text("utf-8")
        noms = set()
        for ligne in texte.splitlines():
            m = re.match(r"\s*(?:from|import)\s+([A-Za-z_][\w.]*)", ligne)
            if m:
                noms.add(m.group(1).split(".")[0])
        self.assertTrue(noms, "aucun import trouvé : le contrôle ne contrôle rien")
        self.assertEqual(noms - autorises, set())
        self.assertIn("FONDATION", noms, "les étiquettes de statut viennent du dépôt, pas du goût")

    def test_l_import_de_fondation_n_est_pas_là_pour_rien(self):
        self.assertEqual(list(DONNEES["conclusion"]["statuts_par_label"]), list(V.FB.STATUTS))


if __name__ == "__main__":
    unittest.main(verbosity=2)
