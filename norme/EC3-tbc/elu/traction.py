#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    ec3/tension.py - Vérification à la traction selon EC3-1-1 §6.2.3

    Résistances :
        - Npl,Rd = A · fy / γM0           (section brute, plastique)
        - Nu,Rd  = 0.9 · Anet · fu / γM2  (section nette, rupture)
        - Nt,Rd  = min(Npl,Rd ; Nu,Rd)
"""
__all__ = ['Tension']

from typing import TypeVar, Optional
from formula import FormulaResult, FormulaCollection

section = TypeVar('section')
material = TypeVar('material')


class Tension:
    """
    Vérification à la traction d'une section acier selon EC3-1-1 §6.2.3.

    :param Ned:      Effort normal de traction de calcul [N]
    :param mat:      Objet material (fy, fu, gamma_m0, gamma_m2)
    :param sec:      Objet section  (A, Anet)
    :param kwargs:   Surcharge manuelle des paramètres
    """

    def __init__(self, Ned: float,
                 mat: Optional[material] = None,
                 sec: Optional[section] = None,
                 **kwargs) -> None:

        self.__ned = abs(Ned)

        # --- Matériau ---
        self.__fy = mat.fy if mat else kwargs.get("fy", 0.0)
        self.__fu = mat.fu if mat else kwargs.get("fu", 0.0)
        self.__gamma_m0 = mat.gamma_m0 if mat else kwargs.get("gamma_m0", 1.0)
        self.__gamma_m2 = mat.gamma_m2 if mat else kwargs.get("gamma_m2", 1.25)

        # --- Section ---
        self.__A = sec.A if sec else kwargs.get("A", 0.0)
        self.__Anet = sec.Anet if sec else kwargs.get("Anet", self.__A)

    # =========================================================================
    # PROPRIÉTÉS DE BASE
    # =========================================================================

    @property
    def ned(self) -> float:
        """Effort de traction de calcul [N]"""
        return self.__ned

    # =========================================================================
    # Npl,Rd  —  Résistance plastique de la section brute  (§6.2.3 (2)a)
    # =========================================================================

    @property
    def npl_rd(self) -> float:
        """Npl,Rd = A · fy / γM0"""
        if self.__gamma_m0 == 0:
            return 0.0
        return self.__A * self.__fy / self.__gamma_m0

    def get_npl_rd(self, with_values: bool = False) -> FormulaResult:
        """FormulaResult pour Npl,Rd"""
        r = self.npl_rd
        fv = ""
        if with_values:
            fv = (f"Npl,Rd = {self.__A:.2f} × {self.__fy:.2f} / "
                  f"{self.__gamma_m0} = {r:.2f} N")
        return FormulaResult(
            name="Npl,Rd",
            formula="Npl,Rd = A · fy / γM0",
            formula_values=fv,
            result=r,
            unit="N",
            ref="EC3-1-1 — §6.2.3 (2)a",
        )

    # =========================================================================
    # Nu,Rd  —  Résistance ultime de la section nette  (§6.2.3 (2)b)
    # =========================================================================

    @property
    def nu_rd(self) -> float:
        """Nu,Rd = 0.9 · Anet · fu / γM2"""
        if self.__gamma_m2 == 0:
            return 0.0
        return 0.9 * self.__Anet * self.__fu / self.__gamma_m2

    def get_nu_rd(self, with_values: bool = False) -> FormulaResult:
        """FormulaResult pour Nu,Rd"""
        r = self.nu_rd
        fv = ""
        if with_values:
            fv = (f"Nu,Rd = 0.9 × {self.__Anet:.2f} × {self.__fu:.2f} / "
                  f"{self.__gamma_m2} = {r:.2f} N")
        return FormulaResult(
            name="Nu,Rd",
            formula="Nu,Rd = 0.9 · Anet · fu / γM2",
            formula_values=fv,
            result=r,
            unit="N",
            ref="EC3-1-1 — §6.2.3 (2)b",
        )

    # =========================================================================
    # Nt,Rd  —  Résistance de calcul à la traction  (§6.2.3 (2))
    # =========================================================================

    @property
    def nt_rd(self) -> float:
        """Nt,Rd = min(Npl,Rd ; Nu,Rd)"""
        return min(self.npl_rd, self.nu_rd)

    def get_nt_rd(self, with_values: bool = False) -> FormulaResult:
        """FormulaResult pour Nt,Rd"""
        r = self.nt_rd
        fv = ""
        if with_values:
            fv = (f"Nt,Rd = min({self.npl_rd:.2f} ; {self.nu_rd:.2f}) "
                  f"= {r:.2f} N")
        return FormulaResult(
            name="Nt,Rd",
            formula="Nt,Rd = min(Npl,Rd ; Nu,Rd)",
            formula_values=fv,
            result=r,
            unit="N",
            ref="EC3-1-1 — §6.2.3 (2)",
        )

    # =========================================================================
    # VÉRIFICATION  —  Ned / Nt,Rd ≤ 1.0
    # =========================================================================

    @property
    def verif(self) -> float:
        """Taux de travail Ned / Nt,Rd"""
        if self.nt_rd == 0:
            return float('inf')
        return round(self.__ned / self.nt_rd, 4)

    @property
    def is_ok(self) -> bool:
        """True si la vérification est satisfaite"""
        return self.verif <= 1.0

    def get_verif(self, with_values: bool = False) -> FormulaResult:
        """FormulaResult pour la vérification"""
        r = self.verif
        fv = ""
        if with_values:
            status = "OK ✓" if self.is_ok else "NON VÉRIFIÉ ✗"
            fv = (f"Ned / Nt,Rd = {self.__ned:.2f} / {self.nt_rd:.2f} "
                  f"= {r:.4f} ≤ 1.0 → {status}")
        return FormulaResult(
            name="Ned/Nt,Rd",
            formula="Ned / Nt,Rd ≤ 1.0",
            formula_values=fv,
            result=r,
            unit="-",
            ref="EC3-1-1 — §6.2.3 (1)",
        )

    # =========================================================================
    # RAPPORT COMPLET
    # =========================================================================

    def report(self, with_values: bool = True) -> FormulaCollection:
        """
        Génère un FormulaCollection regroupant toutes les étapes du calcul.
        """
        fc = FormulaCollection(
            title="Vérification à la traction",
            ref="EC3-1-1 — §6.2.3",
        )
        fc.add(self.get_npl_rd(with_values=with_values))
        fc.add(self.get_nu_rd(with_values=with_values))
        fc.add(self.get_nt_rd(with_values=with_values))
        fc.add(self.get_verif(with_values=with_values))
        return fc

    # =========================================================================
    # REPR
    # =========================================================================

    def __repr__(self) -> str:
        return (f"Tension(Ned={self.__ned:.2f}, Nt,Rd={self.nt_rd:.2f}, "
                f"taux={self.verif:.4f}, ok={self.is_ok})")


# =============================================================================
# FONCTION STANDALONE
# =============================================================================

def nt_rd(A: float, fy: float, gamma_m0: float = 1.0,
          Anet: Optional[float] = None, fu: Optional[float] = None,
          gamma_m2: float = 1.25) -> float:
    """
    Calcul rapide de Nt,Rd sans instancier la classe.

    :param A:        Section brute [mm²]
    :param fy:       Limite d'élasticité [MPa]
    :param gamma_m0: Coefficient de sécurité γM0
    :param Anet:     Section nette [mm²] (défaut = A)
    :param fu:       Résistance ultime [MPa] (défaut = fy)
    :param gamma_m2: Coefficient de sécurité γM2
    :return:         Nt,Rd [N]
    """
    if Anet is None:
        Anet = A
    if fu is None:
        fu = fy
    npl = A * fy / gamma_m0
    nu = 0.9 * Anet * fu / gamma_m2
    return min(npl, nu)


# =============================================================================
# DEBUG
# =============================================================================

if __name__ == "__main__":
    # Exemple : IPE 200, S355, trou de 22 mm dans chaque aile
    t = Tension(
        Ned=500_000,
        fy=355, fu=510,
        gamma_m0=1.0, gamma_m2=1.25,
        A=2848, Anet=2848 - 2 * 22 * 8.5
    )

    print(t)
    print()

    # Rapport complet
    rpt = t.report(with_values=True)
    print(rpt)
