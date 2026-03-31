#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Module to define FormulaResult dataclass for structural engineering reports.
"""

__all__ = ['FormulaResult']

from dataclasses import dataclass

@dataclass
class FormulaResult:
    """
    Résultat d'une formule pour les rapports de calcul.

    :param name: Nom de la grandeur calculée (ex: "fcm")
    :param formula: Formule littérale (ex: "fcm = fck + 8")
    :param formula_values: Formule avec valeurs numériques (ex: "fcm = 30.00 + 8 = 38.00")
    :param result: Valeur numérique du résultat
    :param unit: Unité du résultat (ex: "MPa")
    :param ref: Référence normative (ex: "EC2 — Table 3.1")
    """
    name: str
    formula: str
    formula_values: str
    result: float
    unit: str = ""
    ref: str = ""

    def __str__(self) -> str:
        parts = [f"{self.formula_values}"]
        if self.unit:
            parts[0] += f" [{self.unit}]"
        if self.ref:
            parts.append(f"  Réf: {self.ref}")
        return "\n".join(parts)