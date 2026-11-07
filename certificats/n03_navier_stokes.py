# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""Nœud 3 — NAVIER-STOKES : existence et régularité.

Énoncé : pour toute donnée initiale lisse, la solution 3D reste-t-elle
régulière ∀t>0 ? Certificat borné : solveur spectral 2D périodique
(vorticité ω) sur donnée initiale lisse — mesure de sup|ω| dans le temps.
Aucun blow-up n'est attendu en 2D (théorème connu) ; le fruit est une
mesure reproductible, pas le problème 3D général.
"""

from __future__ import annotations

import math
from typing import Any, Dict

from .socle import noeud_certificat


def _solveur_vorticite_2d(n: int = 32, nu: float = 0.01, dt: float = 0.005,
                          pas: int = 200) -> Dict[str, Any]:
    """Spectral 2D périodique : ∂t ω = νΔω − u·∇ω, FFT pseudo-spectrale."""
    try:
        import numpy as np
    except Exception:
        return {"disponible": False, "raison": "numpy absent"}

    x = np.linspace(0, 2 * math.pi, n, endpoint=False)
    X, Y = np.meshgrid(x, x, indexing="ij")
    omega = np.sin(X) * np.sin(Y) + 0.5 * np.cos(2 * X) * np.cos(2 * Y)

    k = np.fft.fftfreq(n, d=1.0 / n)
    KX, KY = np.meshgrid(k, k, indexing="ij")
    K2 = KX ** 2 + KY ** 2
    K2[0, 0] = 1.0  # évite la division par zéro du mode moyen

    omega_hat = np.fft.fft2(omega)
    max_omega = [float(np.abs(omega).max())]
    enstrophie = [float(np.mean(omega ** 2))]

    for _ in range(pas):
        # ψ = Δ⁻¹ ω ; u = (∂y ψ, −∂x ψ)
        psi_hat = omega_hat / K2
        u = np.real(np.fft.ifft2(1j * KY * psi_hat))
        v = np.real(np.fft.ifft2(-1j * KX * psi_hat))
        dwx = np.real(np.fft.ifft2(1j * KX * omega_hat))
        dwy = np.real(np.fft.ifft2(1j * KY * omega_hat))
        adv = np.fft.fft2(u * dwx + v * dwy)
        omega_hat = (omega_hat - dt * adv) / (1.0 + dt * nu * K2)
        omega = np.real(np.fft.ifft2(omega_hat))
        max_omega.append(float(np.abs(omega).max()))
        enstrophie.append(float(np.mean(omega ** 2)))

    return {
        "disponible": True,
        "grille": n, "nu": nu, "dt": dt, "pas": pas,
        "max_omega_initial": round(max_omega[0], 6),
        "max_omega_final": round(max_omega[-1], 6),
        "enstrophie_initiale": round(enstrophie[0], 6),
        "enstrophie_finale": round(enstrophie[-1], 6),
        "blowup_detecte": bool(max_omega[-1] > 10 * max_omega[0]
                               or not math.isfinite(max_omega[-1])),
    }


def certificat() -> Dict[str, Any]:
    r = _solveur_vorticite_2d()
    statut = "CERTIFICAT_BORNE" if r.get("disponible") else "NON_DECIDABLE"
    return noeud_certificat(
        "NAVIER-STOKES (existence & régularité)",
        "∀u₀ lisse, ∃u(x,t) C∞ solution globale des équations de Navier-Stokes 3D ?",
        r,
        statut,
        "Régularité mesurée sur UNE donnée initiale 2D lisse — conforme au "
        "théorème 2D connu. La question ouverte porte sur la 3D générale.")


if __name__ == "__main__":
    import json
    print(json.dumps(certificat(), indent=2, ensure_ascii=False))
