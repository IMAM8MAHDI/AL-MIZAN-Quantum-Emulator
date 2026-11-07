# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""
===============================================================================
   FRONTEND OPENQASM 2.0 — ÉMULATEUR QUANTIQUE AL-MIZAN
===============================================================================
Parseur minimal mais strict d'OpenQASM 2.0 → liste d'Operation du noyau.
Accepte les fichiers générés par `lang/compilateur_qasm_isa.py`
(ASTRO-Q°ODE → OpenQASM 2.0) ainsi que les circuits canoniques.

Supporté : OPENQASM, include, qreg, creg, h/x/y/z/s/sdg/t/tdg/id, rx/ry/rz,
p/u1/u2/u3/u, cx/cz/cy/ch/swap, ccx, barrier, reset, measure, expressions
arithmétiques avec `pi` (ex: rz(3*pi/4)).
===============================================================================
"""

from __future__ import annotations

import math
import re
from typing import Dict, List, Sequence, Tuple

from noyau_statevector import Operation


class ErreurQasm(ValueError):
    """Erreur de syntaxe OpenQASM 2.0."""


# -- Expressions angulaires sûres (pi, + - * / parenthèses) -------------------

_EXPR_AUTORISEE = re.compile(r"^[\d\s+\-*/().]*pi[\d\s+\-*/().]*$|^[\d\s+\-*/().eE]+$")


def evaluer_angle(expr: str) -> float:
    """Évalue une expression d'angle OpenQASM (ex: 'pi/2', '-3*pi/4', '0.5')."""
    e = expr.strip()
    if not _EXPR_AUTORISEE.match(e):
        raise ErreurQasm(f"Expression d'angle refusée : {expr!r}")
    try:
        return float(eval(e, {"__builtins__": {}}, {"pi": math.pi}))
    except Exception as exc:
        raise ErreurQasm(f"Expression d'angle invalide : {expr!r}") from exc


# -- Déclarations canoniques --------------------------------------------------

def circuit_bell() -> str:
    return (
        "OPENQASM 2.0;\ninclude \"qelib1.inc\";\n"
        "qreg q[2];\ncreg c[2];\n"
        "h q[0];\ncx q[0],q[1];\nmeasure q -> c;\n"
    )


def circuit_ghz(nb_qubits: int = 3) -> str:
    lignes = [
        "OPENQASM 2.0;", 'include "qelib1.inc";',
        f"qreg q[{nb_qubits}];", f"creg c[{nb_qubits}];", "h q[0];",
    ]
    lignes += [f"cx q[0],q[{i}];" for i in range(1, nb_qubits)]
    lignes.append("measure q -> c;")
    return "\n".join(lignes) + "\n"


def circuit_grover_2q() -> str:
    """Grover 2 qubits marquant |11> (oracle cz + diffusion)."""
    return (
        "OPENQASM 2.0;\ninclude \"qelib1.inc\";\n"
        "qreg q[2];\ncreg c[2];\n"
        "h q[0];\nh q[1];\n"
        "cz q[0],q[1];\n"
        "h q[0];\nh q[1];\n"
        "x q[0];\nx q[1];\n"
        "cz q[0],q[1];\n"
        "x q[0];\nx q[1];\n"
        "h q[0];\nh q[1];\n"
        "measure q -> c;\n"
    )


def circuit_qft(nb_qubits: int = 3) -> str:
    """Transformée de Fourier quantique sur n qubits (avec swaps finals)."""
    lignes = [
        "OPENQASM 2.0;", 'include "qelib1.inc";',
        f"qreg q[{nb_qubits}];", f"creg c[{nb_qubits}];",
    ]
    for j in range(nb_qubits):
        lignes.append(f"h q[{j}];")
        for k in range(j + 1, nb_qubits):
            angle = math.pi / (1 << (k - j))
            lignes.append(f"cu1({angle!r}) q[{k}],q[{j}];")
    for j in range(nb_qubits // 2):
        lignes.append(f"swap q[{j}],q[{nb_qubits - 1 - j}];")
    lignes.append("measure q -> c;")
    return "\n".join(lignes) + "\n"


def circuit_deutsch_jozsa() -> str:
    """Deutsch-Jozsa : oracle équilibré f(x)=x (cx) → q[0] mesuré = 1."""
    return (
        "OPENQASM 2.0;\ninclude \"qelib1.inc\";\n"
        "qreg q[2];\ncreg c[2];\n"
        "x q[1];\nh q[0];\nh q[1];\n"
        "cx q[0],q[1];\n"
        "h q[0];\n"
        "measure q -> c;\n"
    )


def circuit_bernstein_vazirani(secret: str = "11") -> str:
    """Bernstein-Vazirani : retrouve la chaîne cachée s par cx depuis chaque bit à 1."""
    n = len(secret)
    lignes = [
        "OPENQASM 2.0;", 'include "qelib1.inc";',
        f"qreg q[{n + 1}];", f"creg c[{n + 1}];",
        f"x q[{n}];",
    ]
    lignes += [f"h q[{i}];" for i in range(n + 1)]
    for i, bit in enumerate(secret):
        if bit == "1":
            lignes.append(f"cx q[{i}],q[{n}];")
    lignes += [f"h q[{i}];" for i in range(n + 1)]
    lignes.append("measure q -> c;")
    return "\n".join(lignes) + "\n"


def circuit_teleportation() -> str:
    """Téléportation d'un état |+> préparé sur q[0] vers q[2] via paire Bell q[1],q[2]."""
    return (
        "OPENQASM 2.0;\ninclude \"qelib1.inc\";\n"
        "qreg q[3];\ncreg c[3];\n"
        "h q[0];\n"
        "h q[1];\ncx q[1],q[2];\n"
        "cx q[0],q[1];\nh q[0];\n"
        "measure q[0] -> c[0];\n"
        "measure q[1] -> c[1];\n"
        "cx q[1],q[2];\n"
        "cz q[0],q[2];\n"
        "measure q -> c;\n"
    )


def circuit_qpe() -> str:
    """Estimation de phase : 2 qubits compteurs + cible, unitaire T (phase π/4)."""
    return (
        "OPENQASM 2.0;\ninclude \"qelib1.inc\";\n"
        "qreg q[3];\ncreg c[3];\n"
        "x q[2];\n"
        "h q[0];\nh q[1];\n"
        "cu1(0.7853981633974483) q[1],q[2];\n"
        "cu1(1.5707963267948966) q[0],q[2];\n"
        "h q[1];\n"
        "cu1(-1.5707963267948966) q[1],q[0];\n"
        "h q[0];\n"
        "measure q -> c;\n"
    )


CIRCUITS_CANONIQUES: Dict[str, str] = {
    "BELL": circuit_bell(),
    "GHZ": circuit_ghz(3),
    "GROVER": circuit_grover_2q(),
    "QFT": circuit_qft(3),
    "DJ": circuit_deutsch_jozsa(),
    "BV": circuit_bernstein_vazirani("11"),
    "TELEPORTATION": circuit_teleportation(),
    "QPE": circuit_qpe(),
}


# -- Parseur -------------------------------------------------------------------

_RE_QREG = re.compile(r"qreg\s+(\w+)\s*\[\s*(\d+)\s*\]")
_RE_CREG = re.compile(r"creg\s+(\w+)\s*\[\s*(\d+)\s*\]")
_RE_PORTE1 = re.compile(
    r"(id|h|x|y|z|s|sdg|t|tdg)\s+(\w+)\s*\[\s*(\d+)\s*\]")
_RE_PORTE_P = re.compile(
    r"(rx|ry|rz|p|u1)\s*\(\s*([^)]+)\)\s*(\w+)\s*\[\s*(\d+)\s*\]")
_RE_PORTE_U = re.compile(
    r"(u2|u3|u)\s*\(\s*([^)]+)\)\s*(\w+)\s*\[\s*(\d+)\s*\]")
_RE_PORTE2 = re.compile(
    r"(cx|cnot|cz|cy|ch|swap|crz|cu1)\s*"
    r"(\w+)\s*\[\s*(\d+)\s*\]\s*,\s*(\w+)\s*\[\s*(\d+)\s*\]")
_RE_CRZ = re.compile(
    r"(crz|cu1)\s*\(\s*([^)]+)\)\s*"
    r"(\w+)\s*\[\s*(\d+)\s*\]\s*,\s*(\w+)\s*\[\s*(\d+)\s*\]")
_RE_CCX = re.compile(
    r"ccx\s+(\w+)\s*\[\s*(\d+)\s*\]\s*,\s*(\w+)\s*\[\s*(\d+)\s*\]\s*,\s*"
    r"(\w+)\s*\[\s*(\d+)\s*\]")
_RE_MESURE_REG = re.compile(r"measure\s+(\w+)\s*->\s*(\w+)")
_RE_MESURE_BIT = re.compile(
    r"measure\s+(\w+)\s*\[\s*(\d+)\s*\]\s*->\s*(\w+)\s*\[\s*(\d+)\s*\]")
_RE_RESET = re.compile(r"reset\s+(\w+)\s*\[\s*(\d+)\s*\]")


def parser_openqasm(source: str) -> Tuple[List[Operation], int]:
    """Parse une source OpenQASM 2.0 → (opérations, nb_qubits du qreg principal)."""
    ops: List[Operation] = []
    tailles_qreg: Dict[str, int] = {}
    nb_qubits = 0

    for numero, brute in enumerate(source.splitlines(), start=1):
        ligne = brute.split("//")[0].strip().rstrip(";").strip()
        if not ligne or ligne.startswith(("OPENQASM", "include", "opaque", "gate ")):
            continue

        m = _RE_QREG.match(ligne)
        if m:
            tailles_qreg[m.group(1)] = int(m.group(2))
            nb_qubits = max(nb_qubits, int(m.group(2)))
            continue
        if _RE_CREG.match(ligne):
            continue
        if ligne.startswith("barrier"):
            continue

        m = _RE_MESURE_REG.match(ligne)
        if m:
            n = tailles_qreg.get(m.group(1), 0)
            ops.append(Operation("measure", tuple(range(n))))
            continue
        m = _RE_MESURE_BIT.match(ligne)
        if m:
            ops.append(Operation("measure", (int(m.group(2)),)))
            continue
        m = _RE_RESET.match(ligne)
        if m:
            ops.append(Operation("reset", (int(m.group(2)),)))
            continue
        m = _RE_CCX.match(ligne)
        if m:
            ops.append(Operation("ccx", (int(m.group(2)), int(m.group(4)), int(m.group(6)))))
            continue
        m = _RE_CRZ.match(ligne)
        if m:
            angle = evaluer_angle(m.group(2))
            # cu1(λ) = phase contrôlée diag(1,1,1,e^{iλ}) → porte p contrôlée
            # crz(λ) = rotation contrôlée → porte rz contrôlée
            nom = "p" if m.group(1) == "cu1" else "rz"
            ops.append(Operation(nom, (int(m.group(6)),), (angle,),
                                 (int(m.group(4)),)))
            continue
        m = _RE_PORTE_U.match(ligne)
        if m:
            angles = [evaluer_angle(a) for a in m.group(2).split(",")]
            nom = m.group(1)
            if nom == "u2":  # u2(φ,λ) = u(π/2, φ, λ)
                angles = [math.pi / 2] + angles
            ops.append(Operation("u", (int(m.group(4)),),
                                 (angles[0], angles[1], angles[2] if len(angles) > 2 else 0.0)))
            continue
        m = _RE_PORTE_P.match(ligne)
        if m:
            ops.append(Operation(m.group(1), (int(m.group(4)),),
                                 (evaluer_angle(m.group(2)),)))
            continue
        m = _RE_PORTE2.match(ligne)
        if m:
            nom = m.group(1)
            q1, q2 = int(m.group(3)), int(m.group(5))
            if nom == "cnot":
                nom = "cx"
            elif nom == "ch":
                ops.append(Operation("h", (q2,), (), (q1,)))
                continue
            ops.append(Operation(nom, (q1, q2)))
            continue
        m = _RE_PORTE1.match(ligne)
        if m:
            ops.append(Operation(m.group(1), (int(m.group(3)),)))
            continue

        raise ErreurQasm(f"Ligne {numero} non reconnue : {brute.strip()!r}")

    if nb_qubits == 0:
        raise ErreurQasm("Aucun qreg déclaré dans la source OpenQASM.")
    return ops, nb_qubits


def _compiler_aq_vers_qasm(source_aq: str) -> str:
    """Compile un fichier .aq ASTRO-Q°ODE en OpenQASM 2.0 via le compilateur
    souverain `lang/compilateur_qasm_isa.py` (import lecture seule)."""
    import sys
    from pathlib import Path
    racine_aq = Path(__file__).resolve().parent.parent / "ASTRO-Q°ODE_SYSTEME"
    if str(racine_aq) not in sys.path:
        sys.path.insert(0, str(racine_aq))
    try:
        from lang.compilateur_qasm_isa import CompilateurQasmIsaAstroQode  # type: ignore
    except Exception as exc:
        raise ErreurQasm(f"Compilateur .aq indisponible : {exc}") from exc
    return CompilateurQasmIsaAstroQode.generer_openqasm_depuis_source_aq(source_aq)


def charger_circuit(nom_ou_source: str) -> Tuple[List[Operation], int, str]:
    """Charge un circuit par nom canonique, chemin de fichier ou source inline.

    Retourne (opérations, nb_qubits, nom_affiché).
    """
    cle = nom_ou_source.strip().upper()
    if cle in CIRCUITS_CANONIQUES:
        ops, n = parser_openqasm(CIRCUITS_CANONIQUES[cle])
        return ops, n, cle

    from pathlib import Path
    chemin = Path(nom_ou_source)
    if chemin.is_file():
        source = chemin.read_text(encoding="utf-8")
        if chemin.suffix.lower() == ".aq":
            source = _compiler_aq_vers_qasm(source)
        ops, n = parser_openqasm(source)
        return ops, n, chemin.stem.upper()

    if "OPENQASM" in nom_ou_source.upper():
        ops, n = parser_openqasm(nom_ou_source)
        return ops, n, "INLINE_QASM"

    raise ErreurQasm(
        f"Circuit introuvable : {nom_ou_source!r}. "
        f"Canoniques : {', '.join(sorted(CIRCUITS_CANONIQUES))}"
    )
