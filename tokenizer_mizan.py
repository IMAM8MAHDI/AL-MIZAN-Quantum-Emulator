#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""
TOKENIZER MIZAN — code d'entrée sans vocabulaire apprêté
IMAM8MAHDI · AL-MIZAN × ASTRO-Q°ODE
Auteur : M. Ahmed El Bahloul (IMAM8MAHDI)

Pourquoi octet-à-octet, et ce que ça coûte :

  Chaque octet UTF-8 devient un jeton. Aucun `vocab.json`, aucun `merges.txt`, aucun
  SentencePiece, aucun poids de tiers — parce que ce sont exactement les objets qu'un
  tokeniseur de tiers apporte avec lui. L'espace d'entrée est fixé par le codage UTF-8
  (259 symboles : 3 spéciaux + 256 octets), pas par un corpus appris : il est identique sur
  toute machine et couvre français, arabe, chinois ou sanscrit sans rien télécharger.

  Coût assumé : un octet ≈ 1/4 de mot. À contexte égal, le modèle voit environ quatre fois
  moins de mots qu'avec un BPE de 50 000. La comparaison honnête se fait en bits par OCTET,
  métrique qui ne dépend pas du tokeniseur et reste comparable d'un modèle à l'autre.

  `Tampon` est la pièce qui rend le stream possible sans stockage : les jetons arrivent,
  remplissent une fenêtre bornée, sont soutirés en batchs, puis oubliés. La mémoire retenue
  ne dépasse jamais `capacite`, quelle que soit la durée de l'entraînement — c'est le
  mécanisme qui materialise « pas besoin de stocker la data sur mon pc ».
"""

from __future__ import annotations

import re
from typing import Iterator, List, Optional, Sequence, Tuple

# 0 = EOS (fin de document), 1 = BOS (début), 2 = PAD. Les octets UTF-8 commencent à 3.
EOS, BOS, PAD = 0, 1, 2
DECALAGE_OCTET = 3
TAILLE_VOCAB = 256 + DECALAGE_OCTET   # 259 : borné par UTF-8, pas par un corpus

# Les C0 non textuels sont retirés ; \t (09), \n (0a) et \r (0d) survivent.
_CONTROLE = re.compile(rb"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def encoder(texte: str, avec_bords: bool = True) -> List[int]:
    """str -> ids. Round-trip exact : `decoder(encoder(s)) == s` pour tout texte propre."""
    brut = _CONTROLE.sub(b"", texte.encode("utf-8", "replace"))
    ids = [octet + DECALAGE_OCTET for octet in brut]
    return [BOS] + ids + [EOS] if avec_bords else ids


def decoder(ids: Sequence[int]) -> str:
    """ids -> str. Les spéciaux sont retirés, les octets reconcaténés puis décodés en UTF-8."""
    octets = bytearray(int(v) - DECALAGE_OCTET for v in ids if int(v) >= DECALAGE_OCTET)
    return octets.decode("utf-8", "replace")


pieces_document = encoder


class Tampon:
    """Fenêtre glissante de jetons, de capacité bornée. Rien n'est jamais écrit sur disque."""

    def __init__(self, capacite: int = 65_536):
        if capacite < 8:
            raise ValueError("capacité du tampon trop faible pour former une fenêtre")
        self.capacite = capacite
        self._file: List[int] = []
        self.pousses = 0
        self.evides = 0
        self.trop_petits = 0

    def __len__(self) -> int:
        return len(self._file)

    def pousser(self, ids: Sequence[int]) -> None:
        self._file.extend(ids)
        self.pousses += len(ids)
        excedent = len(self._file) - self.capacite
        if excedent > 0:                 # la tête sort : le flux ne s'accumule pas
            del self._file[:excedent]
            self.evides += excedent

    def soutenir(self, contexte: int, batch: int) -> Optional[Tuple[List[List[int]],
                                                                    List[List[int]]]]:
        """Rend (x, y) de `batch` lignes de `contexte` jetons, ou None si le flux manque.

        y est x décalé d'un cran : la cible est l'octet suivant, jamais un jeton inventé.
        Rendu par tranches de `contexte + 1` pour que (x, y) utilise les mêmes octets.
        """
        besoin = (contexte + 1) * batch
        if len(self._file) < besoin:
            self.trop_petits += 1
            return None
        bloc = self._file[:besoin]
        del self._file[:besoin]
        pas = contexte + 1
        x = [bloc[i * pas:(i + 1) * pas - 1] for i in range(batch)]
        y = [bloc[i * pas + 1:(i + 1) * pas] for i in range(batch)]
        return x, y

    def etat(self) -> dict:
        return {"en_attente": len(self._file), "capacite": self.capacite,
                "pousses": self.pousses, "evites": self.evides,
                "rejets_par_attente": self.trop_petits}


def batches_flux(stream: Iterator[Sequence[int]], contexte: int, batch: int,
                 capacite: int = 65_536) -> Iterator[Tuple[List[List[int]], List[List[int]]]]:
    """Adapte un flux d'ids (le stream réseau) en batchs, tampon borné inclus."""
    tampon = Tampon(capacite)
    for ids in stream:
        tampon.pousser(ids)
        while True:
            sortie = tampon.soutenir(contexte, batch)
            if sortie is None:
                break
            yield sortie


# ---------------------------------------------------------------------------
# Autocontrôles : ce module est si petit qu'il peut se vérifier lui-même.
# ---------------------------------------------------------------------------

def _autocontrole() -> int:
    echecs: List[str] = []
    for texte in ("quantum error correction", "codes correcteurs d'erreurs quantiques",
                  "تصحيح الأخطاء الكمومية", "量子纠错码", "EPR ⟩ ⊗ |ψ\n\t tabulé"):
        if decoder(encoder(texte)) != texte:
            echecs.append(f"round-trip rompu : {texte[:30]!r}")
    ids = encoder("ab")
    if ids[:1] != [BOS] or ids[-1:] != [EOS]:
        echecs.append("bords absents")
    if min(ids) < 0 or max(ids) >= TAILLE_VOCAB:
        echecs.append(f"jeton hors vocabulaire : {min(ids)}..{max(ids)}")
    tampon = Tampon(capacite=64)
    for _ in range(200):
        tampon.pousser(encoder("0123456789abcdef"))
    if len(tampon) > 64:
        echecs.append(f"tampon débordé : {len(tampon)} > 64")
    sortie = tampon.soutenir(contexte=8, batch=2)
    if sortie is None:
        echecs.append("tampon plein mais aucun batch soutiré")
    else:
        x, y = sortie
        if any(len(ligne) != 8 for ligne in x + y):
            echecs.append("longueur de fenêtre incohérente")
        if x[0][1:] != y[0][:-1]:
            echecs.append("y n'est pas x décalé d'un cran")
    try:
        Tampon(capacite=7)
        echecs.append("capacité aberrante acceptée")
    except ValueError:
        pass
    for message in echecs:
        print("[ÉCHEC]", message)
    print("autocontrôle tokenizer :", "OK" if not echecs else f"{len(echecs)} échec(s)")
    return 0 if not echecs else 1


if __name__ == "__main__":
    raise SystemExit(_autocontrole())
