# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""
===============================================================================
   SERVEUR DIE SILICIUM ÉMULÉ :5030 — ÉMULATEUR QUANTIQUE AL-MIZAN
===============================================================================
Backend réseau TCP (JSON-lignes) émulant un die QPU, compatible avec le
protocole de `lib_pont_materiel_emule.PontMaterielEmuleAlmizan` :

  → {"command": "id"}
  → {"command": "reset"}
  → {"command": "pulse",  "qubit": q, "theta": θ, "phi": φ}
  → {"command": "cnot",   "control": c, "target": t}
  → {"command": "measure", "shots": n}

Chaque client : les commandes pulse/cnot accumulent un circuit ;
measure l'exécute sur le noyau vecteur d'état et renvoie counts + born_mizan.

Aucun matériel : c'est un émulateur logiciel derrière une socket.
===============================================================================
"""

from __future__ import annotations

import json
import socket
import socketserver
import sys
import threading
from pathlib import Path
from typing import Dict, List

RACINE = Path(__file__).resolve().parent
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

from noyau_statevector import (  # noqa: E402
    ModeleBruit,
    Operation,
    SimulateurVecteurEtat,
)

MIZAN = 0.6225
PORT_DEFAUT = 5030
NB_QUBITS_DEFAUT = 4


class SessionDie:
    """État d'un die virtuel : circuit accumulé + bruit optionnel."""

    def __init__(self, nb_qubits: int, bruit: ModeleBruit | None = None):
        self.nb_qubits = nb_qubits
        self.bruit = bruit or ModeleBruit()
        self.ops: List[Operation] = []

    def traiter(self, requete: Dict[str, object]) -> Dict[str, object]:
        cmd = str(requete.get("command", "id")).lower()

        if cmd == "id":
            return {"ok": True, "command": "id",
                    "die": "DIE_SILICIUM_EMULE_ALMIZAN",
                    "nb_qubits": self.nb_qubits,
                    "protocole": "JSON-lignes TCP :5030"}

        if cmd == "reset":
            self.ops.clear()
            return {"ok": True, "command": "reset"}

        if cmd == "pulse":
            q = int(requete.get("qubit", 0))
            theta = float(requete.get("theta", 0.0))
            phi = float(requete.get("phi", 0.0))
            # Impulsion micro-onde : rotation Ry(θ) suivie de Rz(φ)
            self.ops.append(Operation("ry", (q,), (theta,)))
            self.ops.append(Operation("rz", (q,), (phi,)))
            return {"ok": True, "command": "pulse", "qubit": q,
                    "theta": theta, "phi": phi}

        if cmd == "cnot":
            c = int(requete.get("control", 0))
            t = int(requete.get("target", 1))
            self.ops.append(Operation("cx", (c, t)))
            return {"ok": True, "command": "cnot", "control": c, "target": t}

        if cmd == "measure":
            shots = int(requete.get("shots", 500))
            counts: Dict[str, int] = {}
            ops = list(self.ops)
            for tir in range(shots):
                sim = SimulateurVecteurEtat(self.nb_qubits, graine=tir)
                sim.executer(ops, self.bruit if self.bruit.actif else None)
                cle = format(sim.mesurer_tout(), f"0{self.nb_qubits}b")
                counts[cle] = counts.get(cle, 0) + 1
            return {
                "ok": True, "command": "measure", "shots": shots,
                "counts": counts,
                "born_mizan": {f"|{k}>": round(v / shots * MIZAN, 6)
                               for k, v in counts.items()},
                "nb_portes": len(ops),
            }

        return {"ok": False, "command": cmd, "erreur": "commande inconnue"}


class GestionnaireDie(socketserver.StreamRequestHandler):
    """Toutes les connexions partagent LE MÊME die — comme du vrai matériel,
    l'état du circuit persiste entre les requêtes jusqu'au reset."""

    def handle(self) -> None:
        for ligne in self.rfile:
            ligne = ligne.strip()
            if not ligne:
                continue
            try:
                requete = json.loads(ligne.decode("utf-8"))
                with self.server.verrou:
                    reponse = self.server.die.traiter(requete)
            except Exception as exc:
                reponse = {"ok": False, "erreur": str(exc)[:200]}
            self.wfile.write((json.dumps(reponse) + "\n").encode("utf-8"))


class ServeurDie5030(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, port: int = PORT_DEFAUT, nb_qubits: int = NB_QUBITS_DEFAUT,
                 bruit: ModeleBruit | None = None, host: str = "127.0.0.1"):
        self.nb_qubits = nb_qubits
        self.bruit = bruit
        self.verrou = threading.Lock()
        self.die = SessionDie(nb_qubits, bruit)
        super().__init__((host, port), GestionnaireDie)


def lancer_serveur(port: int = PORT_DEFAUT, nb_qubits: int = NB_QUBITS_DEFAUT,
                   p_depolarisant: float = 0.0, host: str = "127.0.0.1") -> None:
    bruit = ModeleBruit(p_depolarisant) if p_depolarisant > 0 else None
    serveur = ServeurDie5030(port, nb_qubits, bruit, host)
    print(f"Die silicium émulé AL-MIZAN en écoute sur {host}:{port} "
          f"({nb_qubits} qubits, p={p_depolarisant}) — Ctrl+C pour arrêter")
    try:
        serveur.serve_forever()
    except KeyboardInterrupt:
        print("\nArrêt du die émulé.")
    finally:
        serveur.server_close()


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Serveur die silicium émulé :5030")
    p.add_argument("--port", type=int, default=PORT_DEFAUT)
    p.add_argument("--qubits", type=int, default=NB_QUBITS_DEFAUT)
    p.add_argument("-p", "--pdepol", type=float, default=0.0)
    a = p.parse_args()
    lancer_serveur(a.port, a.qubits, a.pdepol)
