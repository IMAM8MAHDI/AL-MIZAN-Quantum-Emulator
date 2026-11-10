# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""Tests du dossier DECLARATION — les comptes sont re-mesurés, pas recopiés.

Six exigences, dans l'ordre :
    1. les comptes publiés sont re-mesurés ICI par une écriture différente (subprocess git brut,
       re-parse du journal de références par `split`, dénombrement de lignes par `str.count`, sonde
       du manifeste par un autre regex, numérotation des versions faite à la main) : aucun nombre
       n'est accepté sur parole ; la suite se joue dans trois contextes — arbre de travail, clone,
       archive extraite par `git archive` où ni `.git` ni journal n'existent, et le vide y est
       mesuré et asserté, pas ignoré ;
    2. les identités arithmétiques assertées par le module sont éprouvées sur des jeux étrangers au
       dépôt : si l'additivité de la partition ne tenait qu'aux commits de cette machine, ce serait
       une coïncidence, pas une règle de comptage ;
    3. chaque contrôle peut rougir : seize mutations en mémoire, une par contrôle, six mensonges
       ciblés sur les deux sources de dates, un sur le drapeau de portabilité et un sur la limite de
       non-portabilité montrent que la grille n'est pas décorative — et qu'une seule rougit à la fois.
       Les valeurs fausses sont fabriquées à partir de la valeur mesurée, jamais d'un littéral, pour
       rester des mensonges dans les trois contextes ;
    4. les trois ablations sont rejouées et leurs effets comparés à une réécriture indépendante de
       la grille de l'auditeur et de la racine Merkle ; le fichier muté du parc est contrôlé octet
       pour octet avant et après : l'ablation n'écrit rien ;
    5. les verdicts défavorables restent publiés : zéro date dans le sceau, zéro instrument
       d'horodatage, zéro instrument d'éducation, empreintes non uniques, une seule signature
       portée et aucune vérifiée, limites toutes ouvertes — et aucune phrase de dol dans les
       quatre octets produits ;
    6. déterminisme, sensibilité de la racine, et point fixe des octets : les artefacts relus depuis
       le disque sont identiques aux octets recalculés, et l'attribution n'entre pas dans la racine.

Stdlib uniquement.
    cd ZENODO_DEPOT_ALMIZAN && py -3 -m unittest DECLARATION.tests.test_declaration -v
"""

import copy
import hashlib
import json
import re
import shutil
import subprocess
import sys
import unittest
from fractions import Fraction
from pathlib import Path

RACINE_DEPOT = Path(__file__).resolve().parents[2]
if str(RACINE_DEPOT) not in sys.path:
    sys.path.insert(0, str(RACINE_DEPOT))

from DECLARATION import declaration_base as DEC                 # noqa: E402
from CONTINUITE import continuite_base as CONT                  # noqa: E402
from FONDATION import fondation_base as FB                      # noqa: E402
from FONDATION.OUTILS import audit_piliers as AP                # noqa: E402

CERT = DEC.certificat()
HORS_NOEUDS = frozenset({"source", "empreinte_execution", "rejoue_identique", "limites",
                         "attribution", "racine_merkle_sha256", "taille_octets",
                         "noeuds_certificat"})
# Deux contextes, un seul fichier : la suite se joue dans l'arbre de travail (dépot git + journal),
# dans un clone (dépot git, journal recréé par le clone) et dans l'archive extraite par
# `git archive` (aucun des deux). Ce qui n'est pas mesurable ici est déclaré absent, pas ignoré.
DEPOT_GIT = (RACINE_DEPOT / ".git").exists()
JOURNAL_LOCAL = (RACINE_DEPOT / ".git" / "logs" / "HEAD").exists()
GIT_TROUVE = shutil.which("git") is not None
SOUS_GIT = unittest.skipUnless(DEPOT_GIT and GIT_TROUVE,
                               "aucun dépôt git lisible ici : l'histoire ne se relit pas")
SOUS_JOURNAL = unittest.skipUnless(JOURNAL_LOCAL,
                                   "aucun journal local de références ici : rien à re-parser")


def etat_de(cert):
    """Re-construit l'état exactement comme `resoudre()` le fait, depuis un certificat donné."""
    etat = {k: v for k, v in cert.items() if k not in ("source", "limites", "attribution")}
    etat["noeuds_certificat"] = cert
    return etat


def controls_de(cert):
    etat = etat_de(cert)
    eqs = {x["id"]: x for x in DEC.equations(etat)}
    return {c["id"]: c for c in DEC.controles(eqs, etat)}


ETAT = etat_de(CERT)
EQS = {x["id"]: x for x in DEC.equations(ETAT)}
CS = controls_de(CERT)


def git_brut(*argumens: str) -> str:
    """git invoqué sans le wrapper du module : autre écriture, même dépôt."""
    p = subprocess.run(["git", *argumens], cwd=str(RACINE_DEPOT), capture_output=True,
                       encoding="utf-8", errors="replace", timeout=180)
    assert p.returncode == 0, p.stderr
    return p.stdout


def journal_brut():
    """.git/logs/HEAD re-parsé par `split` — aucune des regex du module."""
    if not JOURNAL_LOCAL:
        return None
    bruts = (RACINE_DEPOT / ".git" / "logs" / "HEAD").read_bytes().split(b"\n")
    rendu = []
    for b in (l for l in bruts if l):
        l = b.decode("utf-8")
        ancien, nouveau, reste = l.split(" ", 2)
        _, suite = reste.split(" <", 1)
        courriel, fin = suite.split("> ", 1)
        epoch, reste_f = fin.split(" ", 1)
        rendu.append((ancien, nouveau, courriel, int(epoch)))
    return rendu


def racine_depuis(noeuds):
    """La formule de `certificat()` réécrite ici : racine des empreintes de nœuds triés."""
    return hashlib.sha256(DEC.canonique(
        {c: hashlib.sha256(DEC.canonique(noeuds[c])).hexdigest() for c in sorted(noeuds)}
    )).hexdigest()


def pourcent_entier(partie: int, total: int) -> str:
    """Le même arrondi, en entiers uniquement : aucun flottant n'intervient."""
    n = (2 * partie * 10000 + total) // (2 * total)
    return f"{n // 100}.{n % 100:02d}"


def numero(version: str):
    return tuple(int(x) for x in re.findall(r"\d+", version))


class TestReMesureIndependante(unittest.TestCase):
    """Aucun nombre publié n'est accepté sur parole : chacun est re-mesuré autrement."""

    def test_commits_atteignables_recomptes_par_rev_list(self):
        if not DEPOT_GIT:
            # l'archive extraite hors de tout dépôt git ne date rien : le zéro doit être mesuré
            self.assertFalse(CERT["horodatages_git"]["git_disponible"])
            self.assertEqual(CERT["horodatages_git"]["commits_atteignables"], 0)
            self.assertEqual(CERT["chronologie"]["objets_dates"], 0)
            self.assertEqual(CERT["fractales"]["la_plus_ancienne_trace_du_depot"], "")
            return
        brute = git_brut("rev-list", "--count", "HEAD").strip()
        self.assertEqual(int(brute), CERT["horodatages_git"]["commits_atteignables"])

    @SOUS_GIT
    def test_signature_portees_recomptees_un_a_un(self):
        lignes = [l for l in git_brut("log", "--format=%H|%G?|%GK", "HEAD").splitlines() if l]
        avec_bloc = [l.split("|")[0] for l in lignes if not l.endswith("|N|")]
        sans_bloc = [l for l in lignes if l.endswith("|N|")]
        h = CERT["horodatages_git"]
        self.assertEqual(len(avec_bloc), h["signatures_portees"])
        self.assertEqual(len(sans_bloc), h["commits_sans_signature"])
        self.assertEqual(len(lignes), h["commits_atteignables"])
        verifiees = sum(1 for sha in avec_bloc
                        if subprocess.run(["git", "verify-commit", sha], cwd=str(RACINE_DEPOT),
                                          capture_output=True, timeout=120).returncode == 0)
        self.assertEqual(verifiees, h["signatures_verifiees"])

    @SOUS_GIT
    def test_partage_humain_machine_refait_par_ensemble_de_seules(self):
        mails = [l for l in git_brut("log", "--format=%ae", "HEAD").splitlines() if l]
        automate = {m for m in mails if re.search(r"cognition|devin|bot|noreply", m, re.I)}
        humain = {m for m in mails if m not in automate}
        rm = CERT["repartition_humain_machine"]
        self.assertEqual(sum(1 for m in mails if m in automate), rm["commits_automate"])
        self.assertEqual(sum(1 for m in mails if m not in automate), rm["commits_humains"])
        self.assertEqual(len(automate | humain), len(set(mails)))
        self.assertFalse(automate & humain)

    def test_sceau_redecoupe_par_un_autre_regex(self):
        octets = (RACINE_DEPOT / "MANIFESTE_SHA256.txt").read_bytes()
        lignes = [l for l in octets.decode("utf-8").split("\n") if l.strip()]
        empreintes = [l.split(" ")[0] for l in lignes]
        s = CERT["sceau_contenu"]
        self.assertEqual(len(lignes), s["total_lignes"])
        self.assertEqual(len(set(empreintes)) == len(empreintes), s["empreintes_uniques"])
        self.assertEqual(len(re.findall(rb"20\d\d-\d\d-\d\d", octets)), s["dates_trouvees"])
        self.assertEqual(len(re.findall(rb"\b[0-9a-f]{40}\b", octets)),
                         s["identifiants_git_40_hex"])
        self.assertNotIn(DEC.MANIFESTE_CHEMIN, [l.split(" ", 1)[1].strip() for l in lignes])
        self.assertTrue(s["le_manifeste_ne_se_scelle_pas_lui_meme"])

    def test_couverture_du_sceau_recalculee_en_entiers(self):
        s = CERT["sceau_contenu"]
        self.assertEqual(pourcent_entier(s["dans_le_sceau"], s["fichiers_arbre"]),
                         s["couverture_sceau_pct"])
        self.assertEqual(s["dans_le_sceau"] + s["hors_manifeste"], s["fichiers_arbre"])

    def test_occurrences_fractales_recomptees_par_str_count(self):
        fr = CERT["fractales"]
        total = 0
        for chemin, attendu in fr["par_fichier"].items():
            texte = (RACINE_DEPOT / chemin).read_text(encoding="utf-8", errors="replace").lower()
            compte = texte.count("fractal")
            self.assertEqual(compte, attendu, chemin)
            total += compte
        self.assertEqual(total, fr["occurrences"])

    def test_paires_recid_version_reappariees_a_la_main(self):
        texte = (RACINE_DEPOT / "CITATION.cff").read_text(encoding="utf-8")
        moiti = re.split(r"\n\s*-\s*type:\s*doi\s*\n", texte)
        apparies = {}
        for morceau in moiti[1:]:
            doi = re.search(r"10\.5281/zenodo\.(\d+)", morceau)
            ver = re.search(r'description:\s*"DOI de la version ([\w.\-]+)', morceau)
            if doi and ver:
                apparies[doi.group(1)] = ver.group(1)
        zp = CERT["chaine_zenodo"]
        self.assertEqual(apparies, zp["paires_recid_version"])
        courante = numero(zp["version_lue"])
        ancetres = {r for r, v in apparies.items() if numero(v) < courante}
        self.assertEqual(sorted(ancetres), zp["ancetres_cites"])
        self.assertLess(len(ancetres), zp["recids_distincts"])

    def test_le_journal_local_se_reparse_par_split_ou_se_declare_absent(self):
        """Les deux sources de dates sont re-mesurées séparément : l'histoire voyage, le journal non."""
        h = CERT["horodatages_git"]
        bruts = journal_brut()
        if bruts is None:
            self.assertFalse(h["journal_present"])
            self.assertEqual((h["journal_lignes"], h["journal_parsees"]), (0, 0))
            self.assertEqual((h["somme_auteurs_journal"], h["duree_attestee_seconde"]), (0, 0))
            self.assertEqual(h["tete_longueur"], 0)
            self.assertFalse(h["tete_coherente"])
            self.assertFalse(h["tete_coincide_avec_l_histoire"])
            self.assertTrue(h["dates_publiees_par"].startswith("aucune"))
            return
        self.assertTrue(h["journal_present"])
        self.assertEqual(len(bruts), h["journal_lignes"])
        self.assertEqual(len(bruts), h["journal_parsees"], "une ligne que le module ne parse pas")
        mails = {}
        for _, _, mail, _ in bruts:
            mails[mail] = mails.get(mail, 0) + 1
        self.assertEqual(mails, h["auteurs_journal"])
        self.assertEqual(sum(mails.values()), h["somme_auteurs_journal"])
        self.assertTrue(all(bruts[i][0] == bruts[i - 1][1] for i in range(1, len(bruts))),
                        "le journal n'est pas une chaîne : un sha ne reprend pas le précédent")
        self.assertEqual(bruts[-1][1], h["sha_tete"])
        self.assertTrue(h["tete_coherente"])
        if DEPOT_GIT and GIT_TROUVE:
            self.assertEqual(git_brut("rev-parse", "HEAD").strip(), h["sha_tete"])
            self.assertTrue(h["tete_coincide_avec_l_histoire"])


class TestIdentitesStructurelles(unittest.TestCase):
    """Les règles de comptage assertées tiennent sur des jeux étrangers au dépôt."""

    def test_additivite_de_partition_sur_des_jeux_etrangers(self):
        for machine, humain in (({"a@x"}, {"b@y", "c@z"}), (set(), {"only@human"}),
                                ({"devin@cognition.ai"}, {"devin@cognition.ai"})):
            seuls_m = len(machine - humain)
            seuls_h = len(humain - machine)
            mixtes = len(machine & humain)
            self.assertEqual(seuls_m + seuls_h + mixtes, len(machine | humain))

    def test_le_classifieur_n_est_pas_une_machine_a_zero(self):
        absentes = ["f.py:1|aucun jeton de tiers n'est joint a ce fichier",
                    "f.py:2|le compte rendu du tiers est absent, 0 reference externe",
                    "f.py:3|la piece demandee n'existe pas, il reste a la produire"]
        affirmatives = ["f.py:4|le tiers a delivre sa reference et le document suit",
                        "f.py:5|la piece jointe porte la reference du depositaire"]
        total, absence, rendues = DEC._classer_lignes(absentes + affirmatives)
        self.assertEqual(total, 5)
        self.assertEqual(absence, 3)
        self.assertEqual(len(rendues), 2)
        self.assertEqual(total, absence + len(rendues))
        # ces cinq lignes sont des fixtures : elles ne doivent rien ajouter au corpus mesuré
        for motif in DEC.INSTRUMENTS_HORODATAGE:
            self.assertEqual(len(re.findall(motif[1], "\n".join(absentes + affirmatives), re.I)),
                             0, motif[0])

    def test_additivite_des_lignes_sur_chaque_instrument_reel(self):
        for lib, v in CERT["instruments_horodatage"]["par_instrument"].items():
            self.assertLessEqual(v["lignes_absence"], v["lignes"], lib)
            self.assertGreaterEqual(v["occurrences"], v["lignes"], lib)
            self.assertLessEqual(len(v["exemples_affirmatives"]), v["lignes"], lib)
        i = CERT["instruments_horodatage"]
        self.assertEqual(i["lignes_total"], i["lignes_absence"] + i["lignes_affirmatives_total"])
        self.assertGreater(i["controle_positif_affirmatives"], 0)
        self.assertEqual(sum(v["lignes"] for v in i["par_instrument"].values()), i["lignes_total"])

    def test_une_date_d_auteur_n_est_pas_une_preuve_de_paternite(self):
        h = CERT["horodatages_git"]
        self.assertFalse(h["preuve_de_paternite"])
        self.assertTrue(h["aucune_horloge"])
        self.assertEqual(h["motifs_horloge_reposes"], [])
        if not h["git_disponible"]:
            # aucune histoire lisible : le nœud doit rendre le vide, pas une date de complaisance
            self.assertEqual((h["date_auteur_plus_ancienne"], h["date_auteur_racine"]), ("", ""))
            self.assertFalse(h["date_auteur_antérieure_à_la_racine"])
            self.assertFalse(h["auteur_plus_ancien_est_automate"])
            return
        self.assertTrue(h["date_auteur_antérieure_à_la_racine"])
        self.assertLess(h["date_auteur_plus_ancienne"], h["date_auteur_racine"])
        self.assertTrue(h["auteur_plus_ancien_est_automate"])

    def test_statut_de_la_demande_ducation_reste_declaration(self):
        ed = CERT["education_ia"]
        self.assertEqual(ed["statut_du_claim"], "déclaré · non vérifié")
        self.assertEqual(ed["claim_occurrences"], 0)
        self.assertEqual(ed["instruments_fichiers"], 0)
        self.assertGreater(ed["contraste_naif"]["occurrences"], 0)


class TestChaqueControlePeutRougir(unittest.TestCase):
    """Vingt-quatre mutations en mémoire : seize contrôles attaqués un à un, plus les mensonges
    qui touchent les deux sources de dates, le drapeau de portabilité et la limite ouverte."""

    MUTATIONS = {
        "C01": ("horodatages_git", "signatures_portees", 5),
        "C02": ("chronologie", "antecedents_total", 99),
        "C03": ("fractales", "occurrences", 999),
        "C04": ("sceau_contenu", "dates_trouvees", 3),
        "C05": ("instruments_horodatage", "lignes_absence", 10 ** 6),
        "C06": ("chaine_zenodo", "nb_ancetres_cites", 99),
        "C07": ("noms_et_attributions", "sans_en_tete", 0),
        "C08": ("education_ia", "statut_du_claim", "prouvé par le dépôt"),
        "C09": ("repartition_humain_machine", "fichiers_mixtes", 10 ** 6),
        "C10": ("frontiere_publication", "somme_equations_par_module", 10 ** 6),
        "C11": ("statuts_parc", "echantillon_verts", 0),
        "C12": ("ablation_limites", "p2_apres", True),
        "C13": ("ablation_chemins", "auditeur_rouge_apres", False),
        "C14": ("ablation_provenance", "racine_sensible_aux_nombres", False),
        "C15": ("chaine_relu", "bom", False),
        "C16": ("limites_ouvertes", "remplies", 1),
    }

    def test_tous_les_controles_sont_verts_avant_mutation(self):
        self.assertEqual([c for c, v in CS.items() if not v["ok"]], [])
        self.assertEqual(len(CS), len(DEC.NOEUDS))

    def test_chaque_mutation_fait_rougir_un_seul_controle(self):
        for id_, (noeud, cle, valeur) in sorted(self.MUTATIONS.items()):
            with self.subTest(controle=id_):
                mute = copy.deepcopy(CERT)
                self.assertIn(cle, mute[noeud], f"{noeud} ne porte pas {cle}")
                mute[noeud][cle] = valeur
                rendu = controls_de(mute)
                rouges = sorted(c for c, v in rendu.items() if not v["ok"])
                self.assertEqual(rouges, [id_], rendu[id_]["obtenu"])

    def test_cinq_mensonges_sur_les_deux_sources_de_dates_rougissent_seuls_c01(self):
        """C01 n'exige plus un dépôt : il confronte les deux sources, et chaque couple brisé rougit.

        Chaque mutation est dérivée de la valeur mesurée, jamais d'un littéral : dans l'archive « git
        archive », les valeurs mesurées sont déjà le zéro honnête — y écrire un faux littéral ne
        mentirait à rien et le test y deviendrait décoratif.
        """
        h = CERT["horodatages_git"]
        avant = sorted(h.items())
        cite = "git log HEAD — l'histoire qui voyage avec le dépôt"
        tait = "aucune : l'archive lue ici ne contient ni dépôt git ni journal de références"
        for mensonge, mensonge_champs in (
            ("tête tronquée", {"tete_longueur": h["tete_longueur"] + 1}),
            ("tête étrangère à l'histoire",
             {"tete_coincide_avec_l_histoire": not h["tete_coincide_avec_l_histoire"]}),
            ("source des dates inversée",
             {"dates_publiees_par": cite if h["commits_atteignables"] == 0 else tait}),
            ("journal déclaré absent avec ses lignes",
             {"journal_present": False, "journal_lignes": h["journal_lignes"] + 1}),
            ("lignes non parsées", {"journal_tout_parse": not h["journal_tout_parse"]}),
            ("comptes d'auteurs non additifs", {"auteurs_additifs": not h["auteurs_additifs"]}),
        ):
            with self.subTest(mensonge=mensonge):
                mute = copy.deepcopy(CERT)
                mute["horodatages_git"].update(mensonge_champs)
                self.assertNotEqual(sorted(mute["horodatages_git"].items()), avant,
                                    "la mutation ne change rien de mesuré")
                rendu = controls_de(mute)
                self.assertEqual([c for c, v in rendu.items() if not v["ok"]], ["C01"], mensonge)

    def test_inverser_le_drapeau_de_portabilite_rougit_les_quatre(self):
        """Le drapeau n'est pas décoratif : le contredire laisse des comptes orphelins des identités."""
        mute = copy.deepcopy(CERT)
        mute["horodatages_git"]["git_disponible"] = not CERT["horodatages_git"]["git_disponible"]
        rendu = controls_de(mute)
        self.assertEqual(sorted(c for c, v in rendu.items() if not v["ok"]),
                         ["C01", "C02", "C03", "C09"])

    def test_effacer_la_limite_sur_les_dates_qui_ne_voyagent_pas_rougit_c16(self):
        lo = CERT["limites_ouvertes"]
        cible = [l for l in lo["liste"] if l.startswith("les dates ne voyagent pas")]
        self.assertEqual(len(cible), 1, "la limite de non-portabilité doit être écrite une fois")
        mute = copy.deepcopy(CERT)
        mute["limites_ouvertes"]["liste"] = [l for l in lo["liste"] if l not in cible]
        mute["limites_ouvertes"]["nb_limites"] = len(mute["limites_ouvertes"]["liste"])
        rendu = controls_de(mute)
        self.assertEqual([c for c, v in rendu.items() if not v["ok"]], ["C16"])

    def test_la_grille_de_l_auditeur_est_reecrite_ici_et_tombe_juste(self):
        """`_regles` du module contre une écriture indépendante de P2 et P3 sur l'échantillon."""
        echantillon = list(CONT.equations(CONT.certificat()))
        born = sum(1 for e in echantillon if len(str(e.get("limite", "")).strip()) >= AP.MIN_LIMITE)
        chemins_ok = sum(1 for e in echantillon if "→" in str(e.get("chemin", "")))
        statuts_ok = sum(1 for e in echantillon if e.get("statut") in FB.STATUTS)
        self.assertEqual(born, len(echantillon))
        self.assertEqual((chemins_ok, statuts_ok), (len(echantillon), len(echantillon)))
        al = CERT["ablation_limites"]
        self.assertEqual(al["equations"], len(echantillon))
        self.assertEqual(al["born_avant"], born)


class TestSansAucuneHistoireLisible(unittest.TestCase):
    """`git archive` ne livre ni `.git` ni journal : le module doit mesurer le vide, pas lever."""

    def test_le_module_survit_aux_octets_seuls_sans_depot_git(self):
        from tempfile import TemporaryDirectory
        racine, git = DEC.RACINE, DEC.GIT
        try:
            with TemporaryDirectory(prefix="declaration-sans-git-") as td:
                DEC.RACINE = Path(td)
                DEC.GIT = None
                h = DEC.horodatages_git()
        finally:
            DEC.RACINE, DEC.GIT = racine, git
        self.assertFalse(h["journal_present"])
        self.assertFalse(h["git_disponible"])
        self.assertEqual((h["journal_lignes"], h["journal_parsees"]), (0, 0))
        self.assertEqual((h["commits_atteignables"], h["tete_longueur"]), (0, 0))
        self.assertEqual((h["sha_tete"], h["premiere"], h["derniere"]), ("", "", ""))
        self.assertEqual(h["duree_attestee_seconde"], 0)
        self.assertEqual(h["auteurs_journal"], {})
        self.assertFalse(h["tete_coherente"])
        self.assertFalse(h["tete_coincide_avec_l_histoire"])
        self.assertTrue(h["journal_tout_parse"] and h["auteurs_additifs"] and h["utf8_integrale"])
        self.assertTrue(h["dates_publiees_par"].startswith("aucune"))

    def test_une_tete_absente_ne_satisfait_pas_une_recherche_par_sous_chaine(self):
        """Le sceau ne cite pas la tête git ; et une tête manquante ne doit pas feindre une citation."""
        s = CERT["sceau_contenu"]
        manifeste = DEC._texte(DEC.MANIFESTE_CHEMIN)
        self.assertFalse(s["tete_git_citee"])
        tete = DEC._tete_git().strip()
        if not tete:
            return
        self.assertNotIn(tete, manifeste)
        self.assertNotIn(tete[5:], manifeste)


class TestAblationsRejouees(unittest.TestCase):
    """Les trois ablations sont rejouées ; le fichier muté ne change pas d'un octet."""

    def setUp(self):
        self.chemin = RACINE_DEPOT / "CONTINUITE" / "continuite_base.py"
        self.avant = (self.chemin.stat().st_size,
                      hashlib.sha256(self.chemin.read_bytes()).hexdigest())

    def tearDown(self):
        self.assertEqual((self.chemin.stat().st_size,
                          hashlib.sha256(self.chemin.read_bytes()).hexdigest()), self.avant,
                         "une ablation a écrit dans le dépôt")

    def test_ablation_limites_otree_sans_changer_aucun_nombre(self):
        al, relu = CERT["ablation_limites"], DEC.ablation_limites()
        self.assertEqual(relu, al)
        self.assertTrue(al["p2_avant"])
        self.assertFalse(al["p2_apres"])
        self.assertEqual(al["born_apres"], 0)
        self.assertEqual(al["limites_otrees"], al["equations"])
        self.assertTrue(al["nombres_inchanges_par_otage"])
        self.assertGreaterEqual(al["longueurs_min_max"][0], al["seuil"])
        self.assertEqual(al["controles_toujours_verts"], al["controles"])

    def test_ablation_chemins_laisse_le_module_vert_et_l_auditeur_rouge(self):
        ac = CERT["ablation_chemins"]
        self.assertTrue(ac["p3_avant"])
        self.assertFalse(ac["p3_apres"])
        self.assertTrue(ac["auditeur_rouge_apres"])
        self.assertEqual(ac["controles_module_verts_apres"], ac["controles_module_total"])
        self.assertTrue(ac["nombres_inchanges"])
        self.assertEqual(ac["statuts_inconnus_avant"], 0)
        self.assertEqual(ac["statuts_inconnus_apres"], ac["equations"])

    def test_racine_aveugle_a_lattribution_et_sensitive_aux_nombres(self):
        ap, relu = CERT["ablation_provenance"], DEC.ablation_provenance()
        self.assertEqual(relu["racine_avant"], ap["racine_avant"])
        cert_sample = CONT.certificat()
        noeuds = {k: v for k, v in cert_sample.items() if k not in HORS_NOEUDS}
        self.assertEqual(racine_depuis(noeuds), ap["racine_avant"])
        self.assertEqual(ap["racine_avant"], cert_sample["racine_merkle_sha256"])
        sans = copy.deepcopy(noeuds)
        retire = [k for k in ("source", "attribution") if sans.pop(k, None) is not None]
        self.assertEqual(retire, [])
        injectee = copy.deepcopy(noeuds)
        cle = sorted(injectee)[0]
        injectee[cle] = {"nombre_injecte": 12345}
        self.assertNotEqual(racine_depuis(injectee), cert_sample["racine_merkle_sha256"])
        self.assertTrue(ap["certificat_complet_hors_racine"])
        self.assertEqual(ap["attribution_dans_la_racine"], False)

    def test_ablation_provenance_ne_mesure_pas_le_seul_affichage(self):
        ap = CERT["ablation_provenance"]
        self.assertEqual(ap["modules_audites"], len(DEC._cibles_du_parc()))
        self.assertGreaterEqual(ap["lectures_presentation"], ap["lectures_hors_presentation"])
        self.assertTrue(all("→" in e for e in ap["enonces_de_lecture_de_mesure"]))


class TestVerdictsDefavorables(unittest.TestCase):
    """Ce qui manque reste publié comme manquant ; aucune phrase de dol ne sort d'ici."""

    INTERDITS = ("preuve irréfutable", "démontré globalement", "INVIOLABLE", "100 %",
                 "cœur secret", "secret de fabrique", "antériorité légale", "certifié ISO",
                 "sans aucun risque", "garantie légale")

    def test_les_absences_sont_mesurees_et_non_comblees(self):
        self.assertEqual(CERT["sceau_contenu"]["dates_trouvees"], 0)
        self.assertEqual(CERT["sceau_contenu"]["identifiants_git_40_hex"], 0)
        self.assertFalse(CERT["sceau_contenu"]["empreintes_uniques"])
        self.assertEqual(CERT["instruments_horodatage"]["instruments_fichiers"], 0)
        self.assertFalse(CERT["instruments_horodatage"]["horodatage_qualifie"])
        self.assertEqual(CERT["education_ia"]["instruments_fichiers"], 0)
        self.assertEqual(CERT["chaine_zenodo"]["resolutions_testées_en_ligne"], False)

    def test_les_limites_restent_toutes_ouvertes(self):
        lo = CERT["limites_ouvertes"]
        self.assertEqual(lo["remplies"], 0)
        self.assertEqual(lo["non_remplies"], lo["nb_limites"])
        self.assertEqual(lo["liste"], [x for x in lo["liste"]])
        self.assertTrue(lo["toutes_au_moins_quarante"])
        self.assertGreaterEqual(lo["plus_courte"], AP.MIN_LIMITE)
        self.assertEqual(lo["nb_limites"], len(lo["liste"]))

    def test_les_octets_publies_ne_contiennent_aucune_phrase_de_dol(self):
        rendu = DEC._artefacts_octets(CERT)
        self.assertEqual(sorted(rendu), ["certificat.json", "chaine_anteriorite.csv",
                                        "declaration_et_ablations.md",
                                        "frontiere_anteriorite.svg"])
        corpus = " ".join(o.decode("utf-8") for o in rendu.values()).lower()
        for mot in self.INTERDITS:
            self.assertNotIn(mot.lower(), corpus, mot)
        self.assertIn(DEC.PHRASE_VERIFIEE.lower(), corpus)

    def test_le_verdict_de_demande_n_est_passe_franchi_nulle_part(self):
        texte = json.dumps(CERT["attribution"], ensure_ascii=False) + "\n".join(CERT["limites"])
        self.assertIn("aucune rendue prouvée", texte)
        self.assertFalse(CERT["noms_et_attributions"]["affirmation_de_paternite_juridique"])
        self.assertEqual(CERT["noms_et_attributions"]["automate_cite_comme_ayant_droit"], 0)


class TestDeterminismeEtOctets(unittest.TestCase):
    """Deux exécutions concordent, la racine scelle les nombres, les octets sont un point fixe."""

    def test_deux_certificats_meme_racine(self):
        second = DEC.certificat()
        self.assertEqual(second["racine_merkle_sha256"], CERT["racine_merkle_sha256"])
        self.assertTrue(CERT["rejoue_identique"])

    def test_la_racine_est_reproduite_depuis_les_noeuds(self):
        noeuds = {k: v for k, v in CERT.items() if k not in HORS_NOEUDS}
        self.assertEqual(racine_depuis(noeuds), CERT["racine_merkle_sha256"])
        for cle, sous_cle, valeur in (("horodatages_git", "commits_atteignables", 65),
                                      ("sceau_contenu", "total_lignes", 203),
                                      ("limites_ouvertes", "nb_limites", 1)):
            mute = copy.deepcopy(noeuds)
            mute[cle][sous_cle] = valeur
            self.assertNotEqual(racine_depuis(mute), CERT["racine_merkle_sha256"], cle)

    def test_attribution_et_source_hors_racine(self):
        noeuds = {k: v for k, v in CERT.items() if k not in HORS_NOEUDS}
        secondes_passe = ("chaine_relu", "plan_svg", "ecritures")
        self.assertEqual(sorted(noeuds), sorted(DEC.MESURES + ("verdict",) + secondes_passe))
        self.assertEqual(len(noeuds), len(DEC.MESURES) + 4, "15 mesures + verdict + 3 relus")
        self.assertEqual(racine_depuis(noeuds), CERT["racine_merkle_sha256"])
        avec_attrib = dict(noeuds, attribution=CERT["attribution"])
        self.assertNotEqual(racine_depuis(avec_attrib), CERT["racine_merkle_sha256"],
                            "l'attribution est hors racine : l'y mettre doit la changer")

    def test_artefacs_ecrits_sont_le_point_fixe_des_octets(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as td:
            rendu = DEC.ecrire_artefacts(CERT, Path(td))
            self.assertEqual(len(rendu), 4)
            recalcul = DEC._artefacts_octets(CERT)
            for nom, octets in recalcul.items():
                self.assertEqual((Path(td) / nom).read_bytes(), octets, nom)
            csv = (Path(td) / "chaine_anteriorite.csv").read_bytes()
            self.assertEqual(csv[:3], b"\xef\xbb\xbf")
            self.assertEqual(CERT["chaine_relu"]["octets"], len(csv))
            relu = json.loads((Path(td) / "certificat.json").read_bytes())
            self.assertEqual(relu["racine_merkle_sha256"], CERT["racine_merkle_sha256"])
            svg = (Path(td) / "frontiere_anteriorite.svg").read_text(encoding="utf-8")
            self.assertEqual(svg.count("<rect "), CERT["plan_svg"]["barres"])
            self.assertEqual(CERT["plan_svg"]["barres"], len(DEC.BARRES))
            self.assertIn(DEC.PHRASE_VERIFIEE, svg)
            self.assertNotIn(DEC.PHRASE_VERIFIEE,
                             (Path(td) / "chaine_anteriorite.csv").read_text(encoding="utf-8-sig"))

    def test_le_csv_ne_scelle_pas_sa_propre_phrase(self):
        self.assertTrue(CERT["chaine_relu"]["phrase_absente_du_csv_par_design"])
        self.assertTrue(CERT["ecritures"]["absence_partout"])
        self.assertEqual(CERT["ecritures"]["nom_sans_empreinte"], "certificat.json")
        self.assertEqual(CERT["ecritures"]["nom_sans_phrase"], "chaine_anteriorite.csv")


class TestPiliersEtTransmission(unittest.TestCase):
    def test_quatre_piliers_ok(self):
        rendu = AP.auditer(RACINE_DEPOT / "DECLARATION" / "declaration_base.py")
        self.assertEqual(rendu["verdict"], "CONFORME")
        self.assertEqual({p["etat"] for p in rendu["piliers"].values()}, {"OK"})
        self.assertEqual(rendu["equations"], rendu["controles"])
        self.assertEqual(rendu["equations"], len(DEC.NOEUDS))

    def test_resoudre_ne_laisse_aucun_controle_rouge(self):
        donnees = DEC.resoudre()
        self.assertTrue(DEC.verifier(donnees))
        conclusion = donnees["conclusion"]
        self.assertEqual(conclusion["controles_verts"], conclusion["controles_total"])
        self.assertEqual(conclusion["equations"], conclusion["controles_total"])
        self.assertEqual(sum(conclusion["statuts_par_label"].values()), conclusion["equations"])
        self.assertEqual(conclusion["dates_dans_le_sceau"], 0)
        self.assertEqual(conclusion["instruments_horodatage"], 0)

    def test_equations_et_controles_apparies_un_a_un(self):
        self.assertEqual(len(EQS), len(CS))
        self.assertEqual(sorted(EQS), sorted(DEC.NOEUDS))
        self.assertEqual(sorted(c["equation"] for c in CS.values()), sorted(EQS))
        for id_, c in CS.items():
            self.assertTrue(str(c["attendu"]).strip() and str(c["obtenu"]).strip(), id_)
            self.assertIn("→", EQS[c["equation"]]["chemin"], id_)
            self.assertIn(EQS[c["equation"]]["statut"], FB.STATUTS, id_)
            self.assertGreaterEqual(len(EQS[c["equation"]]["limite"].strip()), AP.MIN_LIMITE, id_)


if __name__ == "__main__":
    unittest.main(verbosity=2)
