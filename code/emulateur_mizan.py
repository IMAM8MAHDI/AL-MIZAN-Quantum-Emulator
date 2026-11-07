# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""
===============================================================================
   ÉMULATEUR QUANTIQUE AL-MIZAN — LIGNE DE COMMANDE SOUVERAINE
===============================================================================
Unifie les briques ASTRO-Q°ODE en un émulateur quantique à vecteur d'état :

  run  <circuit>   Simule un circuit (nom canonique, fichier .qasm ou source).
                   Bruit optionnel (-p, -g), ZNE (--zne), traduction
                   déterministe (activée par défaut, --no-deterministe pour couper).
  qec              Analyse de la couche de correction d'erreur Steane [[7,1,3]]
                   + démonstration de correction des erreurs de poids 1.
  zne  <circuit>   Atténuation d'erreur par extrapolation à bruit nul.
  canoniques       Liste les circuits canoniques (BELL, GHZ, GROVER, QFT)
                   et affiche leur source OpenQASM 2.0.
  demo             Démonstration complète sur l'état de Bell.
  etat             Diagnostic des ponts vers ASTRO-Q°ODE_SYSTEME.

Statut honnête : émulation classique (coût 2^n) — aucun QPU n'est utilisé.
Codes de sortie : 0 succès · 2 erreur circuit · 3 pont système indisponible.
===============================================================================
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, Optional

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

RACINE = Path(__file__).resolve().parent
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

from noyau_statevector import (  # noqa: E402
    ModeleBruit,
    SimulateurVecteurEtat,
    distribution_depuis_counts,
    executer_counts,
)
from frontend_qasm import CIRCUITS_CANONIQUES, ErreurQasm, charger_circuit  # noqa: E402
from attenuation_zne import executer_zne  # noqa: E402
from rendu_circuit import dessiner_circuit  # noqa: E402
from metriques import metriques_completes  # noqa: E402
from algorithmes import shor_factoriser, vqe_h2  # noqa: E402
from generateur_gds import generer_puce_steane  # noqa: E402
from noyau_matrice_densite import (  # noqa: E402
    QUBITS_MAX_DENSITE,
    comparer_vecteur_densite,
)
import ponts_systeme  # noqa: E402

DOSSIER_RESULTATS = RACINE / "resultats"
VERSION = "1.0"


# ---------------------------------------------------------------------------
# Utilitaires
# ---------------------------------------------------------------------------

def _fidelite_classique(p: Dict[str, float], q: Dict[str, float]) -> float:
    """Fidélité de Bhattacharyya entre deux distributions de mesure."""
    cles = set(p) | set(q)
    bc = sum(math.sqrt(p.get(k, 0.0) * q.get(k, 0.0)) for k in cles)
    return bc * bc


def _sceau_rapport(rapport: Dict[str, Any]) -> str:
    brut = json.dumps(rapport, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(brut.encode("utf-8")).hexdigest()


def _ecrire_rapport(rapport: Dict[str, Any], prefixe: str) -> Path:
    DOSSIER_RESULTATS.mkdir(parents=True, exist_ok=True)
    horodatage = time.strftime("%Y%m%d_%H%M%S")
    chemin = DOSSIER_RESULTATS / f"{prefixe}_{horodatage}.json"
    chemin.write_text(json.dumps(rapport, indent=2, ensure_ascii=False),
                      encoding="utf-8")
    return chemin


def _emettre_scpi_5025(commande: str, timeout: float = 0.2) -> bool:
    """Transmet une trame SCPI à l'AWG local sur le port 5025 (comme le moteur RF)."""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect(("127.0.0.1", 5025))
        sock.sendall((commande + "\n").encode("utf-8"))
        return True
    except Exception:
        return False
    finally:
        sock.close()


def _probas_ideales(ops, nb_qubits: int) -> Dict[str, float]:
    """Distribution idéale sans bruit (simulation exacte du vecteur d'état)."""
    ops_sans_mesure = [op for op in ops if op.nom != "measure"]
    sim = SimulateurVecteurEtat(nb_qubits, graine=0)
    sim.executer(ops_sans_mesure)
    probas = sim.probabilites()
    return {
        format(i, f"0{nb_qubits}b"): p for i, p in probas.items()
    }


# ---------------------------------------------------------------------------
# Commande RUN
# ---------------------------------------------------------------------------

def cmd_run(args: argparse.Namespace) -> int:
    try:
        ops, nb_qubits, nom = charger_circuit(args.circuit)
    except ErreurQasm as exc:
        print(f"✗ {exc}")
        return 2

    print("=" * 72)
    print(f" ÉMULATEUR QUANTIQUE AL-MIZAN v{VERSION} — circuit {nom} ({nb_qubits} qubits)")
    print("=" * 72)
    print()
    print(dessiner_circuit(ops, nb_qubits))
    print()

    bruit = ModeleBruit(args.p, args.gamma)
    probas_ideal = _probas_ideales(ops, nb_qubits)

    counts = executer_counts(ops, nb_qubits, args.shots, bruit,
                             graine=args.graine)
    total = sum(counts.values())
    dist_mesuree = {k: v / total for k, v in counts.items()}

    fidelite = _fidelite_classique(probas_ideal, dist_mesuree)

    # Entropie de Shannon de la distribution mesurée (bits)
    entropie = -sum(p * math.log2(p) for p in dist_mesuree.values() if p > 0)
    entropie_norm = entropie / nb_qubits if nb_qubits else 0.0

    print(f"\n[1] HISTOGRAMME DE MESURE ({total} tirs"
          f"{', bruit p=%.4f γ=%.4f' % (bruit.p_depolarisant, bruit.gamma_amortissement) if bruit.actif else ', sans bruit'}) :")
    for cle in sorted(counts, key=lambda k: -counts[k]):
        barre = "█" * int(40 * counts[cle] / total)
        print(f"    |{cle}> : {counts[cle]:5d}  {dist_mesuree[cle]:7.3%}  {barre}")
    print(f"\n    Fidélité distribution vs idéal : {fidelite:.4f}")
    print(f"    Entropie de Shannon mesurée    : {entropie:.4f} bits "
          f"(normalisée {entropie_norm:.4f})")

    rapport: Dict[str, Any] = {
        "emulateur": "AL-MIZAN",
        "version": VERSION,
        "circuit": nom,
        "nb_qubits": nb_qubits,
        "shots": total,
        "bruit": asdict(bruit),
        "counts": counts,
        "distribution_ideale": probas_ideal,
        "fidelite_distribution": round(fidelite, 6),
        "entropie_shannon_bits": round(entropie, 6),
        "horodatage_noyau": ponts_systeme.battement_noyau(),
    }

    # -- Métriques de l'état idéal -------------------------------------------
    ops_sans_mesure = [op for op in ops if op.nom != "measure"]
    sim_ideal = SimulateurVecteurEtat(nb_qubits, graine=0)
    sim_ideal.executer(ops_sans_mesure)
    metriques = metriques_completes(sim_ideal.etat, nb_qubits)
    rapport["metriques_etat_ideal"] = metriques
    print("\n[1b] MÉTRIQUES DE L'ÉTAT IDÉAL :")
    for q, v in metriques["bloch"].items():
        print(f"    Bloch {q} : ({v[0]:+.3f}, {v[1]:+.3f}, {v[2]:+.3f})  "
              f"pureté locale {metriques['purete_locale'][q]:.3f}")
    if "concurrence" in metriques:
        print(f"    Concurrence (intrication) : {metriques['concurrence']:.4f} "
              f"— entropie {metriques['entropie_intrication_bits']:.4f} bits")

    # -- Mode matrice densité exacte ------------------------------------------
    if args.densite:
        if nb_qubits > QUBITS_MAX_DENSITE:
            print(f"\n[1c] Matrice densité ignorée : {nb_qubits} > {QUBITS_MAX_DENSITE} qubits.")
        else:
            print("\n[1c] SIMULATION EXACTE PAR MATRICE DENSITÉ (canaux de Kraus) :")
            densite = comparer_vecteur_densite(ops, nb_qubits, bruit, args.dephasage)
            rapport["matrice_densite_exacte"] = densite
            print(f"    Pureté Tr(ρ²)            : {densite['purete_tr_rho2']:.6f}")
            print(f"    Entropie von Neumann     : {densite['entropie_von_neumann_bits']:.6f} bits")
            if "fidelite_vs_ideal" in densite:
                print(f"    Fidélité <ψ|ρ|ψ>         : {densite['fidelite_vs_ideal']:.6f}")
            for ket, p in sorted(densite["probabilites_exactes"].items(),
                                 key=lambda kv: -kv[1])[:6]:
                print(f"    |{ket}> : {p:.4f}")

    # -- Émission SCPI :5025 optionnelle --------------------------------------
    if args.scpi:
        trame = f"SOUR{nom}:FREQ {total};VOLT {min(0.6225, fidelite):.4f};OUTP ON"
        ok = _emettre_scpi_5025(trame)
        rapport["scpi_5025"] = {"trame": trame, "envoyee": ok}
        print(f"\n[1d] SCPI :5025 → {'✓ émise' if ok else '✗ port fermé (simulation locale)'} : {trame}")

    # -- ZNE optionnel -------------------------------------------------------
    if args.zne and bruit.actif:
        print("\n[2] ATTÉNUATION ZNE (extrapolation à bruit nul) :")
        zne = executer_zne(ops, nb_qubits, args.p,
                           gamma_amortissement=args.gamma,
                           shots_par_echelle=max(64, args.shots // 4),
                           qubit_observable=args.qubit_obs)
        rapport["zne"] = zne
        for pt in zne["points"]:
            print(f"    λ={pt['lambda']:.0f}  p_eff={pt['p_eff']:.4f}  "
                  f"<Z_{args.qubit_obs}>={pt['observable_Z']:+.4f}")
        print(f"    → <Z> extrapolé à bruit nul : {zne['observable_extrapolee_bruit_nul']}")

    # -- Traduction déterministe ---------------------------------------------
    if not args.no_deterministe:
        print("\n[3] TRADUCTION QUANTIQUE → LOGIQUE DÉTERMINISTE (MIZAN 0.6225) :")
        dist_ket = distribution_depuis_counts(counts)
        trad = ponts_systeme.traduire_deterministe(
            dist_ket, algorithme=nom,
            fidelite=fidelite, entropie=entropie_norm)
        rapport["traduction_deterministe"] = trad
        if trad.get("disponible"):
            t = trad["traduction"]
            print(f"    Espérance hermitienne : {t['esperance_hermitienne']:+.4f}")
            print(f"    Valeur bridée Mizan   : {t['valeur_continue_mizan']:.4f}")
            print(f"    Chiffre socle [-9;+9] : {t['chiffre_socle']:+d}")
            print(f"    Lettre socle [A;S]    : {t['lettre_socle']}")
            print(f"    Tétrade               : {t['etat_tetrade']}")
            print(f"    Assertion             : {'VRAI' if t['assertion_booleenne'] else 'FAUX'}")
            print(f"    Sceau SHA-256         : {t['sceau_sha256'][:32]}…")
        else:
            print(f"    (transducteur indisponible : {trad.get('raison')})")

    rapport["sceau_rapport_sha256"] = _sceau_rapport(rapport)
    chemin = _ecrire_rapport(rapport, f"run_{nom.lower()}")
    print(f"\n✓ Rapport scellé écrit : {chemin}")
    return 0


# ---------------------------------------------------------------------------
# Commande QEC
# ---------------------------------------------------------------------------

def cmd_qec(args: argparse.Namespace) -> int:
    print("=" * 72)
    print(" COUCHE DE CORRECTION D'ERREUR — CODE DE STEANE [[7,1,3]]")
    print("=" * 72)

    demo = ponts_systeme.demonstration_correction_poids_un()
    if not demo.get("disponible"):
        print("✗ Module qubit_logique_mizan indisponible.")
        return 3

    print(f"\n[1] CORRECTION DES ERREURS DE POIDS 1 :")
    print(f"    Erreurs testées   : {demo['erreurs_testees']} (X et Z sur 7 qubits)")
    print(f"    Erreurs corrigées : {demo['erreurs_corrigees']}")
    print(f"    Toutes corrigées  : {'✓ OUI' if demo['tous_poids_un_corriges'] else '✗ NON'}")

    analyse = ponts_systeme.analyse_qec_steane(
        p_depolarisant=args.p, echantillons_mc=args.mc)
    print(f"\n[2] ANALYSE SOUS BRUIT DÉPOLARISANT p={args.p:g} :")
    print(f"    Distance du code           : {analyse['distance']}")
    print(f"    Taux d'échec logique exact : {analyse['taux_echec_logique_exact']:.6e}")
    mc = analyse["monte_carlo"]
    print(f"    Monte Carlo ({mc['echantillons']} tirages) : "
          f"{mc['taux']:.6e}  IC95 [{mc['ic95'][0]:.3e} ; {mc['ic95'][1]:.3e}]")
    if analyse["pseudo_seuil_depolarisant"]:
        print(f"    Pseudo-seuil dépolarisant  : {analyse['pseudo_seuil_depolarisant']:.6e}")
    print(f"    Empreinte source           : {analyse['empreinte_source_sha256'][:32]}…")
    print(f"\n    Statut : {analyse['statut']}")

    analyse["demo_poids_un"] = demo
    analyse["horodatage_noyau"] = ponts_systeme.battement_noyau()
    analyse["sceau_rapport_sha256"] = _sceau_rapport(analyse)
    chemin = _ecrire_rapport(analyse, "qec_steane")
    print(f"\n✓ Rapport scellé écrit : {chemin}")
    return 0


# ---------------------------------------------------------------------------
# Commande ZNE dédiée
# ---------------------------------------------------------------------------

def cmd_zne(args: argparse.Namespace) -> int:
    try:
        ops, nb_qubits, nom = charger_circuit(args.circuit)
    except ErreurQasm as exc:
        print(f"✗ {exc}")
        return 2
    print(f"ZNE sur {nom} ({nb_qubits} qubits), p={args.p}, qubit observable={args.qubit_obs}")
    res = executer_zne(ops, nb_qubits, args.p,
                       gamma_amortissement=args.gamma,
                       shots_par_echelle=args.shots,
                       qubit_observable=args.qubit_obs)
    res["circuit"] = nom
    res["horodatage_noyau"] = ponts_systeme.battement_noyau()
    res["sceau_rapport_sha256"] = _sceau_rapport(res)
    chemin = _ecrire_rapport(res, f"zne_{nom.lower()}")
    print(json.dumps(res, indent=2, ensure_ascii=False))
    print(f"\n✓ Rapport écrit : {chemin}")
    return 0


# ---------------------------------------------------------------------------
# Canoniques / démo / état
# ---------------------------------------------------------------------------

def cmd_canoniques(_args: argparse.Namespace) -> int:
    print("Circuits canoniques disponibles :")
    for nom, source in sorted(CIRCUITS_CANONIQUES.items()):
        print(f"\n──── {nom} ────")
        print(source)
    return 0


def cmd_demo(args: argparse.Namespace) -> int:
    args.circuit = "BELL"
    args.shots = max(args.shots, 512)
    return cmd_run(args)


def cmd_vqe(args: argparse.Namespace) -> int:
    print("VQE — molécule H₂ (2 qubits, hamiltonien STO-3G jouet)")
    res = vqe_h2(essais=args.essais)
    res["horodatage_noyau"] = ponts_systeme.battement_noyau()
    res["sceau_rapport_sha256"] = _sceau_rapport(res)
    print(f"  Énergie VQE     : {res['energie_vqe_ha']:.6f} Ha")
    print(f"  Énergie exacte  : {res['energie_exacte_ha']:.6f} Ha")
    print(f"  Écart           : {res['ecart_mha']:.2f} mHa")
    print(f"  Ansatz θ (rad)  : {res['ansatz_params_rad']}")
    chemin = _ecrire_rapport(res, "vqe_h2")
    print(f"\n✓ Rapport écrit : {chemin}")
    return 0


def cmd_shor(args: argparse.Namespace) -> int:
    print(f"SHOR — factorisation de {args.n} (a={args.a}, QPE émulée)")
    res = shor_factoriser(n_cible=args.n, a=args.a)
    res["horodatage_noyau"] = ponts_systeme.battement_noyau()
    res["sceau_rapport_sha256"] = _sceau_rapport(res)
    print(f"  Registre        : {res['nb_qubits']} qubits ({res['nb_portes']} portes)")
    for k, v in res["distribution_comptage"].items():
        print(f"    |{k}> : {v:.4f}")
    print(f"  Périodes        : {res['periodes_candidats']}")
    print(f"  FACTEURS        : {res['facteurs']}")
    chemin = _ecrire_rapport(res, f"shor_{args.n}")
    print(f"\n✓ Rapport écrit : {chemin}")
    return 0


def cmd_gds(_args: argparse.Namespace) -> int:
    print("GÉNÉRATEUR GDSII — tuile qubit logique Steane [[7,1,3]]")
    m = generer_puce_steane()
    print(f"  Fichier         : {m['fichier_gds']} ({m['taille_octets']} octets)")
    print(f"  Géométrie       : {m['nb_rectangles']} rectangles, {m['nb_textes']} textes")
    d = m["drc_generique"]
    print(f"  DRC générique   : {d['nb_violations']} violation(s) "
          f"(largeur≥{d['regles']['largeur_min_um']}µm, "
          f"espacement≥{d['regles']['espacement_min_um']}µm)")
    for v in d["violations"][:8]:
        print(f"    - {v}")
    print(f"  SHA-256         : {m['sha256_gds'][:40]}…")
    print(f"  ⚠ {m['statut']}")
    return 0


def cmd_serveur(args: argparse.Namespace) -> int:
    from serveur_die_5030 import lancer_serveur
    lancer_serveur(port=args.port, nb_qubits=args.qubits,
                   p_depolarisant=args.p)
    return 0


def cmd_arbre(_args: argparse.Namespace) -> int:
    from certificats.arbre_savoir import afficher_arbre, construire_arbre
    from certificats.socle import ecrire_arbre
    a = construire_arbre()
    print(afficher_arbre(a))
    chemin = ecrire_arbre(a)
    print(f"\n✓ Arbre scellé écrit : {chemin}")
    return 0


def cmd_plan(_args: argparse.Namespace) -> int:
    from certificats.plan_global import afficher_plan, construire_plan
    from certificats.socle import ecrire_arbre
    a = construire_plan()
    print(afficher_plan(a))
    print(f"\n✓ Plan écrit : {ecrire_arbre(a, 'plan_resolution_globale')}")
    return 0


def cmd_reductions(_args: argparse.Namespace) -> int:
    from certificats.niveau3_reductions import (afficher_reductions,
                                              construire_reductions)
    from certificats.socle import ecrire_arbre
    a = construire_reductions()
    print(afficher_reductions(a))
    chemin = ecrire_arbre(a, "reductions_niveau3")
    print(f"\n✓ Réductions écrites : {chemin}")
    return 0


def cmd_conjecture(_args: argparse.Namespace) -> int:
    from conjecture_point_carre import certificat_point_carre
    print("=" * 72)
    print(" CONJECTURE DU POINT CARRÉ — vérification par exhaustion")
    print("=" * 72)
    c = certificat_point_carre()
    for pc_id, res in c["resultats"].items():
        marque = "✓ VÉRIFIÉ" if res["verdict"] else "✗ FALSIFIÉ"
        print(f"\n  {pc_id} : {marque}")
        if pc_id == "PC-3":
            for nom, d in res["cycles"].items():
                print(f"      {nom:12s} : {d['num = k²·reste']}")
    print(f"\n  VERDICT GLOBAL : {c['statut']}")
    print(f"  Sceau SHA-256  : {c['sceau_sha256'][:40]}…")
    chemin = _ecrire_rapport(c, "conjecture_point_carre")
    print(f"\n✓ Certificat écrit : {chemin}")
    return 0 if c["verdict_global"] else 2


def cmd_etat(_args: argparse.Namespace) -> int:
    print("Diagnostic des ponts ASTRO-Q°ODE_SYSTEME :\n")
    qlm = ponts_systeme.charger_module_qec()
    print(f"  qubit_logique_mizan (QEC Steane) : {'✓' if qlm else '✗'}")
    trad = ponts_systeme.traduire_deterministe({"|0>": 1.0}, "SONDE", 1.0, 0.0)
    print(f"  transducteur déterministe        : "
          f"{'✓' if trad.get('disponible') else '✗ ' + str(trad.get('raison'))}")
    horloge = ponts_systeme.battement_noyau()
    print(f"  horloge_noyau (scellée, lecture) : "
          f"{'✓' if horloge.get('disponible') else '✗ ' + str(horloge.get('raison'))}")
    print(f"\n  Racine système : {ponts_systeme.RACINE_SYSTEME_AQ}")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def construire_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="emulateur_mizan",
        description="Émulateur quantique à vecteur d'état AL-MIZAN "
                    "(pur Python, OpenQASM 2.0, bruit, ZNE, QEC Steane, "
                    "traduction déterministe).")
    sous = p.add_subparsers(dest="commande", required=True)

    def options_sim(sp, defaut_p=0.0):
        sp.add_argument("-s", "--shots", type=int, default=1024,
                        help="Nombre de tirs Monte Carlo (défaut 1024)")
        sp.add_argument("-p", type=float, default=defaut_p,
                        help="Probabilité de bruit dépolarisant par porte")
        sp.add_argument("-g", "--gamma", type=float, default=0.0,
                        help="Amortissement d'amplitude γ (T1) par porte")
        sp.add_argument("-d", "--dephasage", type=float, default=0.0,
                        help="Déphasage pur (T2) par porte (matrice densité)")
        sp.add_argument("--densite", action="store_true",
                        help="Simulation exacte par matrice densité (≤8 qubits)")
        sp.add_argument("--scpi", action="store_true",
                        help="Émettre une trame SCPI vers le port 5025")
        sp.add_argument("--graine", type=int, default=20261107,
                        help="Graine du générateur aléatoire")

    sp_run = sous.add_parser("run", help="Simuler un circuit")
    sp_run.add_argument("circuit",
                        help="Nom canonique (BELL/GHZ/GROVER/QFT), "
                             "fichier .qasm ou source inline")
    options_sim(sp_run)
    sp_run.add_argument("--zne", action="store_true",
                        help="Appliquer l'atténuation ZNE (nécessite -p > 0)")
    sp_run.add_argument("--qubit-obs", type=int, default=0,
                        help="Qubit observable pour ZNE (défaut 0)")
    sp_run.add_argument("--no-deterministe", action="store_true",
                        help="Désactiver la traduction déterministe")
    sp_run.set_defaults(func=cmd_run)

    sp_qec = sous.add_parser("qec", help="Analyse couche Steane [[7,1,3]]")
    sp_qec.add_argument("-p", type=float, default=1e-3,
                        help="Bruit dépolarisant physique (défaut 1e-3)")
    sp_qec.add_argument("--mc", type=int, default=50_000,
                        help="Tirages Monte Carlo (défaut 50000)")
    sp_qec.set_defaults(func=cmd_qec)

    sp_zne = sous.add_parser("zne", help="ZNE dédié sur un circuit")
    sp_zne.add_argument("circuit")
    options_sim(sp_zne, defaut_p=0.05)
    sp_zne.add_argument("--qubit-obs", type=int, default=0)
    sp_zne.set_defaults(func=cmd_zne)

    sous.add_parser("canoniques", help="Lister les circuits canoniques") \
        .set_defaults(func=cmd_canoniques)

    sp_demo = sous.add_parser("demo", help="Démonstration Bell de bout en bout")
    options_sim(sp_demo)
    sp_demo.add_argument("--zne", action="store_true")
    sp_demo.add_argument("--qubit-obs", type=int, default=0)
    sp_demo.add_argument("--no-deterministe", action="store_true")
    sp_demo.set_defaults(func=cmd_demo)

    sous.add_parser("arbre",
                    help="Arbre de savoir : les 7 problèmes du millénaire") \
        .set_defaults(func=cmd_arbre)

    sous.add_parser("plan",
                    help="Plan de résolution globale : échelles de lemmes") \
        .set_defaults(func=cmd_plan)

    sous.add_parser("reductions",
                    help="Niveau 3 : équations du pont fini → infini") \
        .set_defaults(func=cmd_reductions)

    sous.add_parser("conjecture",
                    help="Vérifier la Conjecture du Point Carré (PC-1..PC-4)") \
        .set_defaults(func=cmd_conjecture)

    sous.add_parser("etat", help="Diagnostic des ponts système") \
        .set_defaults(func=cmd_etat)

    sp_vqe = sous.add_parser("vqe", help="VQE jouet H₂ (2 qubits)")
    sp_vqe.add_argument("--essais", type=int, default=400,
                        help="Échantillons de la recherche aléatoire")
    sp_vqe.set_defaults(func=cmd_vqe)

    sp_shor = sous.add_parser("shor", help="Shor jouet : factorisation par QPE")
    sp_shor.add_argument("-n", type=int, default=15, help="Entier à factoriser")
    sp_shor.add_argument("-a", type=int, default=7, help="Base copr première avec n")
    sp_shor.set_defaults(func=cmd_shor)

    sous.add_parser("gds", help="Générer le layout GDSII Steane [[7,1,3]]") \
        .set_defaults(func=cmd_gds)

    sp_srv = sous.add_parser("serveur", help="Lancer le die émulé :5030 (TCP JSON)")
    sp_srv.add_argument("--port", type=int, default=5030)
    sp_srv.add_argument("--qubits", type=int, default=4)
    sp_srv.add_argument("-p", type=float, default=0.0)
    sp_srv.set_defaults(func=cmd_serveur)

    return p


def main(argv=None) -> int:
    parser = construire_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
