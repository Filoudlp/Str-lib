#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Module to define structural steel material properties according to EC3.

    References:
        - EN 1993-1-1 (Eurocode 3) — Table 3.1

    Supported National Annexes:
        - FR : France (default)
        - BE : Belgique
        - UK : Royaume-Uni
"""

__all__ = ['MatSteel', 'SteelCoefficients']

from dataclasses import dataclass
from typing import Optional

from materials import Material
from formula import FormulaResult


# =============================================================================
# Coefficients nationaux
# =============================================================================

@dataclass
class SteelCoefficients:
    """
    Coefficients partiels de sécurité pour l'acier de construction
    selon l'Annexe Nationale — EC3 §6.1(1).

    :param gamma_m0: Résistance des sections (classe 1-4) [-]
    :param gamma_m1: Résistance des éléments au flambement [-]
    :param gamma_m2: Résistance des sections nettes en traction [-]
    :param gamma_m3: Résistance au glissement à l'ELU [-]
    :param gamma_m3_ser: Résistance au glissement à l'ELS [-]
    :param gamma_m4: Résistance des assemblages par injection [-]
    :param gamma_m5: Résistance des assemblages par goupilles [-]
    :param gamma_m6_ser: Résistance des boulons précontraints à l'ELS [-]
    :param gamma_m7: Résistance des boulons HR précontraints à l'ELU [-]
    :param country: Code pays
    """
    gamma_m0: float = 1.00
    gamma_m1: float = 1.00
    gamma_m2: float = 1.25
    gamma_m3: float = 1.10
    gamma_m3_ser: float = 1.25
    gamma_m4: float = 1.00
    gamma_m5: float = 1.00
    gamma_m6_ser: float = 1.00
    gamma_m7: float = 1.10
    country: str = "FR"


_NATIONAL_ANNEX_REGISTRY: dict[str, SteelCoefficients] = {
    "FR": SteelCoefficients(
        gamma_m0=1.00, gamma_m1=1.00, gamma_m2=1.25,
        gamma_m3=1.10, gamma_m3_ser=1.25, gamma_m4=1.00,
        gamma_m5=1.00, gamma_m6_ser=1.00, gamma_m7=1.10,
        country="FR",
    ),
    "BE": SteelCoefficients(
        gamma_m0=1.00, gamma_m1=1.00, gamma_m2=1.25,
        gamma_m3=1.25, gamma_m3_ser=1.10, gamma_m4=1.00,
        gamma_m5=1.00, gamma_m6_ser=1.00, gamma_m7=1.10,
        country="BE",
    ),
    "UK": SteelCoefficients(
        gamma_m0=1.00, gamma_m1=1.00, gamma_m2=1.10,
        gamma_m3=1.25, gamma_m3_ser=1.10, gamma_m4=1.00,
        gamma_m5=1.00, gamma_m6_ser=1.00, gamma_m7=1.10,
        country="UK",
    ),
}


# =============================================================================
# Registre des nuances d'acier — EC3 Table 3.1
# =============================================================================

# {nuance: {épaisseur_max: (fy, fu)}} # Need to be complet with the full table from EC3
_STEEL_GRADES: dict[str, dict[float, tuple[float, float]]] = {
    "S235": {
        40:  (235, 360),
        80:  (215, 360),
    },
    "S275": {
        50:  (275, 430),
        80:  (255, 410),
    },
    "S355": {
        40:  (355, 490),
        80:  (335, 470),
    },
    "S450": {
        40:  (440, 550),
        80:  (410, 550),
    },
}

def _get_fy_fu(grade: str, thickness: float) -> tuple[float, float]:
    """
    Retourne (fy, fu) selon la nuance et l'épaisseur.

    :param grade: Nuance d'acier (ex: "S355")
    :param thickness: Épaisseur de l'élément [mm]
    :raises ValueError: Si la nuance ou l'épaisseur n'est pas supportée
    """
    grade = grade.upper()
    if grade not in _STEEL_GRADES:
        raise ValueError(
            f"Nuance '{grade}' non supportée. "
            f"Choix possibles : {list(_STEEL_GRADES.keys())}"
        )
    thresholds = _STEEL_GRADES[grade]
    for t_max in sorted(thresholds.keys()):
        if thickness <= t_max:
            return thresholds[t_max]
    raise ValueError(
        f"Épaisseur {thickness} mm hors limites pour la nuance {grade}. "
        f"Épaisseur max : {max(thresholds.keys())} mm"
    )


# =============================================================================
# MatSteel
# =============================================================================

class MatSteel(Material):
    """
    Acier de construction selon EC3 — EN 1993-1-1.

    Deux modes d'instanciation :
        - Par nuance et épaisseur : MatSteel(grade="S355", thickness=20)
        - Par valeurs directes    : MatSteel(fy=345, fu=490)

    :param grade: Nuance d'acier ("S235", "S275", "S355", "S460")
    :param thickness: Épaisseur de l'élément [mm] (pour déterminer fy/fu)
    :param fy: Limite d'élasticité [MPa] (prioritaire sur grade)
    :param fu: Résistance ultime en traction [MPa] (prioritaire sur grade)
    :param country: Code pays de l'Annexe Nationale
    :param coefficients: Coefficients personnalisés (prioritaire sur country)
    """

    _DEFAULT_E = 210000.0       # MPa
    _DEFAULT_NU = 0.3
    _DEFAULT_ALPHA = 12e-6      # K⁻¹
    _DEFAULT_RHO = 7850.0       # kg/m³

    def __init__(
        self,
        grade: Optional[str] = None,
        thickness: float = 16.0,
        fy: Optional[float] = None,
        fu: Optional[float] = None,
        country: str = "FR",
        coefficients: Optional[SteelCoefficients] = None,
    ) -> None:

        # -- Résistances --
        if fy is not None and fu is not None:
            self._fy = fy
            self._fu = fu
            self._grade = grade or "Custom"
            self._thickness = thickness
        elif grade is not None:
            self._grade = grade.upper()
            self._thickness = thickness
            self._fy, self._fu = _get_fy_fu(self._grade, self._thickness)
        else:
            raise ValueError(
                "Fournir soit (grade + thickness), soit (fy + fu)."
            )

        # -- Annexe Nationale --
        self._country = country.upper()
        if coefficients is not None:
            self._coefficients = coefficients
        else:
            self._coefficients = self._get_coefficients(self._country)

        # -- Init Material --
        super().__init__(
            name=self._grade,
            E=self._DEFAULT_E,
            nu=self._DEFAULT_NU,
            rho=self._DEFAULT_RHO,
        )

    # ---- helpers internes ----

    @staticmethod
    def _get_coefficients(country: str) -> SteelCoefficients:
        country = country.upper()
        if country not in _NATIONAL_ANNEX_REGISTRY:
            raise ValueError(
                f"Annexe Nationale '{country}' non supportée. "
                f"Choix possibles : {list(_NATIONAL_ANNEX_REGISTRY.keys())}"
            )
        return _NATIONAL_ANNEX_REGISTRY[country]

    # ---- country (dynamique) ----

    @property
    def country(self) -> str:
        return self._country

    @country.setter
    def country(self, value: str) -> None:
        self._country = value.upper()
        self._coefficients = self._get_coefficients(self._country)

    @property
    def coefficients(self) -> SteelCoefficients:
        return self._coefficients

    # =================================================================
    # Propriétés de base
    # =================================================================

    @property
    def grade(self) -> str:
        return self._grade

    @grade.setter
    def grade(self, value: str) -> None:
        """Permet de changer la nuance et mettre à jour fy/fu en conséquence.
        Note : L'épaisseur doit être définie pour que cela fonctionne."""
        self._grade = value.upper()
        if self._thickness is not None:
            self._fy, self._fu = _get_fy_fu(self._grade, self._thickness)
        else:
            raise ValueError(
                "L'épaisseur doit être définie pour mettre à jour fy/fu lors du changement de nuance."
            )

    @property
    def thickness(self) -> float:
        return self._thickness

    @thickness.setter
    def thickness(self, value: float) -> None:
        """Permet de changer l'épaisseur et mettre à jour fy/fu en conséquence.
        Note : La nuance doit être définie pour que cela fonctionne."""
        self._thickness = value
        if self._grade is not None:
            self._fy, self._fu = _get_fy_fu(self._grade, self._thickness)
        else:
            raise ValueError(
                "La nuance doit être définie pour mettre à jour fy/fu lors du changement d'épaisseur."
            )

    # ---- fy ----

    @property
    def fy(self) -> float:
        return self._fy

    @fy.setter 
    def fy(self, value: float) -> None:
        """Permet de changer fy directement (mode valeurs directes)."""
        self._fy = value

    @property
    def fy_report(self) -> FormulaResult:
        return FormulaResult(
            name="fy",
            formula="fy = f(nuance, épaisseur) — EC3 Table 3.1",
            formula_values=f"fy({self._grade}, t≤{self._thickness:.0f}mm) = {self._fy:.2f}",
            result=self._fy,
            unit="MPa",
            ref="EC3 — Table 3.1",
        )

    # ---- fu ----

    @property
    def fu(self) -> float:
        return self._fu

    @fu.setter 
    def fu(self, value: float) -> None:
        """Permet de changer fu directement (mode valeurs directes)."""
        self._fu = value

    @property
    def fu_report(self) -> FormulaResult:
        return FormulaResult(
            name="fu",
            formula="fu = f(nuance, épaisseur) — EC3 Table 3.1",
            formula_values=f"fu({self._grade}, t≤{self._thickness:.0f}mm) = {self._fu:.2f}",
            result=self._fu,
            unit="MPa",
            ref="EC3 — Table 3.1",
        )

    # ---- epsilon (paramètre de ductilité) ----

    @property
    def epsilon(self) -> float:
        """ε = √(235/fy) — EC3 §5.5.2"""
        return (235 / self._fy) ** 0.5

    @property
    def epsilon_report(self) -> FormulaResult:
        return FormulaResult(
            name="ε",
            formula="ε = √(235 / fy)",
            formula_values=f"ε = √(235 / {self._fy:.2f}) = {self.epsilon:.4f}",
            result=self.epsilon,
            unit="-",
            ref="EC3 — §5.5.2",
        )

    # =================================================================
    # Propriétés dépendantes de l'AN (gamma)
    # =================================================================

    @property
    def gamma_m0(self) -> float:
        return self._coefficients.gamma_m0

    @property
    def gamma_m1(self) -> float:
        return self._coefficients.gamma_m1

    @property
    def gamma_m2(self) -> float:
        return self._coefficients.gamma_m2

    # =================================================================
    # Résistances de calcul
    # =================================================================

    # ---- fy / gamma_m0 ----

    @property
    def fy_d(self) -> float:
        """fy / γM0"""
        return self._fy / self._coefficients.gamma_m0

    @property
    def fy_d_report(self) -> FormulaResult:
        c = self._coefficients
        return FormulaResult(
            name="fy,d",
            formula="fy,d = fy / γM0",
            formula_values=f"fy,d = {self._fy:.2f} / {c.gamma_m0} = {self.fy_d:.2f}",
            result=self.fy_d,
            unit="MPa",
            ref=f"EC3 — §6.1(1) — AN {c.country}",
        )

    # ---- fu / gamma_m2 ----

    @property
    def fu_d(self) -> float:
        """fu / γM2"""
        return self._fu / self._coefficients.gamma_m2

    @property
    def fu_d_report(self) -> FormulaResult:
        c = self._coefficients
        return FormulaResult(
            name="fu,d",
            formula="fu,d = fu / γM2",
            formula_values=f"fu,d = {self._fu:.2f} / {c.gamma_m2} = {self.fu_d:.2f}",
            result=self.fu_d,
            unit="MPa",
            ref=f"EC3 — §6.1(1) — AN {c.country}",
        )

    # =================================================================
    # Rapport complet
    # =================================================================

    def all_reports(self) -> list[FormulaResult]:
        """Renvoie la liste de tous les FormulaResult pour un rapport complet."""
        return [
            self.fy_report,
            self.fu_report,
            self.epsilon_report,
            self.fy_d_report,
            self.fu_d_report,
        ]

    # =================================================================
    # Affichage
    # =================================================================

    def __repr__(self) -> str:
        return (
            f"MatSteel(grade='{self._grade}', thickness={self._thickness}, "
            f"fy={self._fy}, fu={self._fu}, country='{self._country}')"
        )

    def __str__(self) -> str:
        lines = [
            f"{'=' * 60}",
            f"  Acier {self._grade} — t={self._thickness:.0f}mm — AN {self._country}",
            f"{'=' * 60}",
        ]
        for r in self.all_reports():
            lines.append(f"  {r.formula_values:50s} [{r.unit}]  ({r.ref})")
        lines.append(f"{'=' * 60}")
        return "\n".join(lines)


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":

    # Par nuance
    s355 = MatSteel(grade="S355", thickness=20)
    print(s355)

    # Par valeurs directes
    custom = MatSteel(fy=345, fu=490)
    print(custom)

    # Accès individuel
    print(f"\nfy = {s355.fy} MPa")
    print(f"ε  = {s355.epsilon:.4f}")
    print(s355.epsilon_report)

    # Changement AN
    s355.country = "UK"
    print(f"\nfu,d (UK) = {s355.fu_d:.2f} MPa")
    print(s355.fu_d_report)
