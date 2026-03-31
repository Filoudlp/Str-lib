#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Module to define Reinforced Concrete section-material properties.

    Cette classe sert de **conteneur central** pour stocker toutes les
    propriétés d'une section béton armé, avant et après calcul.

    Workflow typique :
        1. Création avec sec + mat_concrete + mat_reinforcement
        2. Calcul externe (flexion, effort tranchant, etc.)
        3. Stockage des résultats (ast, asc, covers, etc.) via setters
        4. Calcul des propriétés dérivées (Ih, Ic, xh, xc)
        5. Affichage / export pour rapports

    UNITS:
        - mm   : lengths
        - mm²  : areas
        - mm⁴  : inertia
        - MPa  : stress
        - N    : forces

    References:
        - EN 1992-1-1 (Eurocode 2)
"""

__all__ = ['SecMatRC']

from typing import Optional, TypeVar
from formula import FormulaResult

section = TypeVar('section')
material_concrete = TypeVar('material_concrete')
material_reinforcement = TypeVar('material_reinforcement')


class SecMatRC:
    """
    Conteneur section-matériau pour le béton armé.

    Stocke les données géométriques liées au matériau (d, d', enrobages,
    armatures, inerties homogènes et fissurées) qui dépendent à la fois
    de la section et du matériau.

    À l'initialisation, seules les valeurs par défaut (d ≈ 0.9h) sont
    définies. Les autres propriétés sont renseignées au fur et à mesure
    des calculs par l'utilisateur.

    :param sec: Section géométrique (SecRectangular, SecCircular, etc.)
    :param mat_concrete: Matériau béton (MatConcrete)
    :param mat_reinforcement: Matériau acier d'armature (MatReinforcement)
    :param phi_fluage: Coefficient de fluage φ(∞,t0) pour αe long terme
                       (défaut None → non calculable)
    :param name: Nom optionnel
    """

    def __init__(
        self,
        sec: section,
        mat_concrete: material_concrete,
        mat_reinforcement: material_reinforcement,
        phi_fluage: Optional[float] = None,
        name: Optional[str] = None,
    ) -> None:

        # ----- Références aux objets de base -----
        self._sec = sec
        self._mat_c = mat_concrete
        self._mat_s = mat_reinforcement
        self._name = name or f"RC_{sec.__class__.__name__}"

        # ----- Hauteur utile — valeur par défaut -----
        self._h: float = sec.h
        self._d: float = 0.9 * self._h          # Estimation initiale
        self._d_prime: float = 0.1 * self._h     # Estimation initiale

        # ----- Bras de levier -----
        self._z: Optional[float] = None          # Renseigné après calcul

        # ----- Armatures [mm²] -----
        self._ast: Optional[float] = None        # Armatures tendues
        self._asc: Optional[float] = None        # Armatures comprimées
        self._asp: Optional[float] = None        # Armatures de précontrainte
        self._asw: Optional[float] = None        # Armatures transversales

        # ----- Diamètres [mm] -----
        self._phi_l: Optional[float] = None      # φ longitudinal max
        self._phi_t: Optional[float] = None      # φ transversal

        # ----- Enrobages [mm] -----
        self._cnom: Optional[float] = None       # Enrobage nominal
        self._cmin: Optional[float] = None       # Enrobage minimal
        self._delta_cdev: float = 10.0           # Tolérance exécution

        # ----- Espacements [mm] -----
        self._ev: Optional[float] = None         # Espacement vertical
        self._eh: Optional[float] = None         # Espacement horizontal
        self._st: Optional[float] = None         # Espacement transversal

        # ----- Exposition / Classe structurale -----
        self._exposure_class: Optional[str] = None    # ex. "XC1", "XD2"
        self._structural_class: str = "S4"            # Défaut EC2

        # ----- Type d'acier -----
        self._steel_kind: str = "HA"  # "HA" | "RL" | "PC"

        # ----- Fluage -----
        self._phi_fluage: Optional[float] = phi_fluage

        # ----- Inerties / axes neutres (calculés quand données dispo) -----
        # Stockés en cache, invalidés par les setters
        self._Ih: Optional[float] = None
        self._Ic: Optional[float] = None
        self._xh: Optional[float] = None
        self._xc: Optional[float] = None

    # =========================================================================
    # Invalidation du cache
    # =========================================================================

    def _invalidate_cache(self) -> None:
        """Remet à None les valeurs calculées pour forcer le recalcul."""
        self._Ih = None
        self._Ic = None
        self._xh = None
        self._xc = None

    # =========================================================================
    # Propriétés en lecture seule — objets de base
    # =========================================================================

    @property
    def sec(self) -> section:
        """Section géométrique associée."""
        return self._sec

    @property
    def mat_concrete(self) -> material_concrete:
        """Matériau béton associé."""
        return self._mat_c

    @property
    def mat_reinforcement(self) -> material_reinforcement:
        """Matériau armature associé."""
        return self._mat_s

    @property
    def h(self) -> float:
        """Hauteur totale de la section [mm]."""
        return self._h

    # =========================================================================
    # Coefficient d'équivalence — EC2
    # =========================================================================

    @property
    def alpha_eq_short(self) -> float:
        """
        Coefficient d'équivalence court terme : αe = Es / Ecm.
        """
        return self._mat_s.Es / self._mat_c.Ecm

    @property
    def alpha_eq_short_report(self) -> FormulaResult:
        return FormulaResult(
            symbol="αe,ct",
            formula="Es / Ecm",
            formula_values=f"{self._mat_s.Es:.0f} / {self._mat_c.Ecm:.0f} = {self.alpha_eq_short:.2f}",
            unit="-",
            ref="EC2 — §5.4(2)",
            value=self.alpha_eq_short,
        )

    @property
    def alpha_eq_long(self) -> Optional[float]:
        """
        Coefficient d'équivalence long terme : αe = Es / (Ecm / (1 + φ)).

        Retourne None si le coefficient de fluage n'est pas renseigné.
        """
        if self._phi_fluage is None:
            return None
        Ec_eff = self._mat_c.Ecm / (1 + self._phi_fluage)
        return self._mat_s.Es / Ec_eff

    @property
    def alpha_eq_long_report(self) -> Optional[FormulaResult]:
        if self._phi_fluage is None:
            return None
        Ec_eff = self._mat_c.Ecm / (1 + self._phi_fluage)
        return FormulaResult(
            symbol="αe,lt",
            formula="Es / (Ecm / (1 + φ))",
            formula_values=(
                f"{self._mat_s.Es:.0f} / ({self._mat_c.Ecm:.0f} / "
                f"(1 + {self._phi_fluage:.2f})) = "
                f"{self._mat_s.Es:.0f} / {Ec_eff:.0f} = {self.alpha_eq_long:.2f}"
            ),
            unit="-",
            ref="EC2 — §5.4(2)",
            value=self.alpha_eq_long,
        )

    # =========================================================================
    # Hauteur utile d / d'
    # =========================================================================

    @property
    def d(self) -> float:
        """Hauteur utile [mm] — distance fibre comprimée au CDG des aciers tendus."""
        return self._d

    @d.setter
    def d(self, val: float) -> None:
        self._d = val
        self._invalidate_cache()

    @property
    def d_report(self) -> FormulaResult:
        return FormulaResult(
            symbol="d",
            formula="h - enrobage - φt - φl/2  (ou 0.9·h par défaut)",
            formula_values=f"d = {self._d:.2f}",
            unit="mm",
            ref="EC2 — §6.1",
            value=self._d,
        )

    @property
    def d_prime(self) -> float:
        """Distance fibre comprimée au CDG des aciers comprimés [mm]."""
        return self._d_prime

    @d_prime.setter
    def d_prime(self, val: float) -> None:
        self._d_prime = val
        self._invalidate_cache()

    @property
    def d_prime_report(self) -> FormulaResult:
        return FormulaResult(
            symbol="d'",
            formula="enrobage + φt + φl/2  (ou 0.1·h par défaut)",
            formula_values=f"d' = {self._d_prime:.2f}",
            unit="mm",
            ref="EC2 — §6.1",
            value=self._d_prime,
        )

    # =========================================================================
    # Bras de levier z
    # =========================================================================

    @property
    def z(self) -> float:
        """
        Bras de levier [mm].
        Si non renseigné, retourne 0.9·d (estimation).
        """
        if self._z is not None:
            return self._z
        return 0.9 * self._d

    @z.setter
    def z(self, val: float) -> None:
        self._z = val

    @property
    def z_report(self) -> FormulaResult:
        estimated = self._z is None
        return FormulaResult(
            symbol="z",
            formula="0.9·d (estimation)" if estimated else "z (calculé)",
            formula_values=f"z = {self.z:.2f}" + (" (estimation)" if estimated else ""),
            unit="mm",
            ref="EC2 — §6.1",
            value=self.z,
        )

    # =========================================================================
    # Armatures
    # =========================================================================

    @property
    def ast(self) -> Optional[float]:
        """Section d'armatures tendues [mm²]."""
        return self._ast

    @ast.setter
    def ast(self, val: float) -> None:
        self._ast = val
        self._invalidate_cache()

    @property
    def asc(self) -> Optional[float]:
        """Section d'armatures comprimées [mm²]."""
        return self._asc

    @asc.setter
    def asc(self, val: float) -> None:
        self._asc = val
        self._invalidate_cache()

    @property
    def asp(self) -> Optional[float]:
        """Section d'armatures de précontrainte [mm²]."""
        return self._asp

    @asp.setter
    def asp(self, val: float) -> None:
        self._asp = val

    @property
    def asw(self) -> Optional[float]:
        """Section d'armatures transversales [mm²]."""
        return self._asw

    @asw.setter
    def asw(self, val: float) -> None:
        self._asw = val

    @property
    def astc(self) -> Optional[float]:
        """Section totale d'armatures longitudinales Ast + Asc [mm²]."""
        ast = self._ast or 0.0
        asc = self._asc or 0.0
        if self._ast is None and self._asc is None:
            return None
        return ast + asc

    # =========================================================================
    # Diamètres
    # =========================================================================

    @property
    def phi_l(self) -> Optional[float]:
        """Diamètre longitudinal max [mm]."""
        return self._phi_l

    @phi_l.setter
    def phi_l(self, val: float) -> None:
        self._phi_l = val

    @property
    def phi_t(self) -> Optional[float]:
        """Diamètre transversal [mm]."""
        return self._phi_t

    @phi_t.setter
    def phi_t(self, val: float) -> None:
        self._phi_t = val

    # =========================================================================
    # Enrobages
    # =========================================================================

    @property
    def cnom(self) -> Optional[float]:
        """Enrobage nominal [mm]."""
        return self._cnom

    @cnom.setter
    def cnom(self, val: float) -> None:
        self._cnom = val

    @property
    def cmin(self) -> Optional[float]:
        """Enrobage minimal [mm]."""
        return self._cmin

    @cmin.setter
    def cmin(self, val: float) -> None:
        self._cmin = val

    @property
    def delta_cdev(self) -> float:
        """Tolérance d'exécution [mm]."""
        return self._delta_cdev

    @delta_cdev.setter
    def delta_cdev(self, val: float) -> None:
        self._delta_cdev = val

    # =========================================================================
    # Espacements
    # =========================================================================

    @property
    def ev(self) -> Optional[float]:
        """Espacement vertical entre armatures [mm]."""
        return self._ev

    @ev.setter
    def ev(self, val: float) -> None:
        self._ev = val

    @property
    def eh(self) -> Optional[float]:
        """Espacement horizontal entre armatures [mm]."""
        return self._eh

    @eh.setter
    def eh(self, val: float) -> None:
        self._eh = val

    @property
    def st(self) -> Optional[float]:
        """Espacement des cadres / étriers [mm]."""
        return self._st

    @st.setter
    def st(self, val: float) -> None:
        self._st = val

    # =========================================================================
    # Exposition / Classe structurale
    # =========================================================================

    @property
    def exposure_class(self) -> Optional[str]:
        """Classe d'exposition (ex. 'XC1', 'XD2')."""
        return self._exposure_class

    @exposure_class.setter
    def exposure_class(self, val: str) -> None:
        self._exposure_class = val

    @property
    def structural_class(self) -> str:
        """Classe structurale (S1 à S6)."""
        return self._structural_class

    @structural_class.setter
    def structural_class(self, val: str) -> None:
        self._structural_class = val

    # =========================================================================
    # Type d'acier
    # =========================================================================

    @property
    def steel_kind(self) -> str:
        """Type d'armature : 'HA', 'RL', 'PC'."""
        return self._steel_kind

    @steel_kind.setter
    def steel_kind(self, val: str) -> None:
        if val not in ("HA", "RL", "PC"):
            raise ValueError(f"steel_kind doit être 'HA', 'RL' ou 'PC' (reçu : {val})")
        self._steel_kind = val

    # =========================================================================
    # Fluage
    # =========================================================================

    @property
    def phi_fluage(self) -> Optional[float]:
        """Coefficient de fluage φ(∞,t0)."""
        return self._phi_fluage

    @phi_fluage.setter
    def phi_fluage(self, val: float) -> None:
        self._phi_fluage = val
        self._invalidate_cache()

    # =========================================================================
    # Inerties homogène / fissurée — Section rectangulaire
    # =========================================================================

    def _check_computable(self) -> list[str]:
        """
        Retourne la liste des paramètres manquants pour calculer
        les inerties homogène et fissurée.
        """
        missing = []
        if self._ast is None:
            missing.append("ast")
        if self._d is None:
            missing.append("d")
        if not hasattr(self._sec, 'b'):
            missing.append("sec.b (section non rectangulaire ou b non défini)")
        return missing

    @property
    def can_compute_inertia(self) -> bool:
        """True si toutes les données sont disponibles pour le calcul."""
        return len(self._check_computable()) == 0

    @property
    def missing_for_inertia(self) -> list[str]:
        """Liste des paramètres manquants pour le calcul des inerties."""
        return self._check_computable()

    # ----- Axe neutre homogène -----

    @property
    def xh(self) -> Optional[float]:
        """
        Position de l'axe neutre en section homogène [mm].

        Section rectangulaire : résolution de l'équation du moment
        statique de la section homogène.

        Retourne None si données manquantes.
        """
        if not self.can_compute_inertia:
            return None
        if self._xh is not None:
            return self._xh

        b = self._sec.b
        h = self._h
        alpha_e = self.alpha_eq_short
        ast = self._ast
        asc = self._asc or 0.0
        d = self._d
        d_p = self._d_prime

        # Moment statique / fibre sup = 0
        # b·h·(h/2) + (αe-1)·Asc·d' + (αe-1)·Ast·d
        # divisé par
        # b·h + (αe-1)·(Ast + Asc)
        A_hom = b * h + (alpha_e - 1) * (ast + asc)
        S_hom = b * h * (h / 2) + (alpha_e - 1) * asc * d_p + (alpha_e - 1) * ast * d

        self._xh = S_hom / A_hom
        return self._xh

    @property
    def xh_report(self) -> Optional[FormulaResult]:
        if not self.can_compute_inertia:
            return FormulaResult(
                symbol="xh",
                formula=f"Données manquantes : {', '.join(self.missing_for_inertia)}",
                formula_values="—",
                unit="mm", ref="EC2", value=None,
            )
        return FormulaResult(
            symbol="xh",
            formula="S_hom / A_hom",
            formula_values=f"xh = {self.xh:.2f}",
            unit="mm",
            ref="EC2 — §5.4",
            value=self.xh,
        )

    # ----- Inertie homogène -----

    @property
    def Ih(self) -> Optional[float]:
        """
        Inertie de la section homogène [mm⁴].
        Retourne None si données manquantes.
        """
        if not self.can_compute_inertia:
            return None
        if self._Ih is not None:
            return self._Ih

        b = self._sec.b
        h = self._h
        alpha_e = self.alpha_eq_short
        ast = self._ast
        asc = self._asc or 0.0
        d = self._d
        d_p = self._d_prime
        xh = self.xh

        self._Ih = (
            b * h**3 / 12
            + b * h * (xh - h / 2) ** 2
            + (alpha_e - 1) * asc * (xh - d_p) ** 2
            + (alpha_e - 1) * ast * (d - xh) ** 2
        )
        return self._Ih

    @property
    def Ih_report(self) -> Optional[FormulaResult]:
        if not self.can_compute_inertia:
            return FormulaResult(
                symbol="Ih",
                formula=f"Données manquantes : {', '.join(self.missing_for_inertia)}",
                formula_values="—",
                unit="mm⁴", ref="EC2", value=None,
            )
        return FormulaResult(
            symbol="Ih",
            formula="b·h³/12 + b·h·(xh-h/2)² + (αe-1)·Asc·(xh-d')² + (αe-1)·Ast·(d-xh)²",
            formula_values=f"Ih = {self.Ih:.0f}",
            unit="mm⁴",
            ref="EC2 — §5.4",
            value=self.Ih,
        )

    # ----- Axe neutre fissuré -----

    @property
    def xc(self) -> Optional[float]:
        """
        Position de l'axe neutre en section fissurée [mm].

        Résolution de l'équation du 2nd degré :
            (b/2)·x² + (αe·Asc + αe·Ast)·x - (αe·Asc·d' + αe·Ast·d) = 0

        Nota : seule la racine positive est retenue.

        Retourne None si données manquantes.
        """
        if not self.can_compute_inertia:
            return None
        if self._xc is not None:
            return self._xc

        b = self._sec.b
        alpha_e = self.alpha_eq_short
        ast = self._ast
        asc = self._asc or 0.0
        d = self._d
        d_p = self._d_prime

        # (b/2)·x² + αe·(Asc+Ast)·x - αe·(Asc·d' + Ast·d) = 0
        a_coef = b / 2
        b_coef = alpha_e * (asc + ast)
        c_coef = -(alpha_e * (asc * d_p + ast * d))

        delta = b_coef**2 - 4 * a_coef * c_coef
        self._xc = (-b_coef + delta**0.5) / (2 * a_coef)
        return self._xc

    @property
    def xc_report(self) -> Optional[FormulaResult]:
        if not self.can_compute_inertia:
            return FormulaResult(
                symbol="xc",
                formula=f"Données manquantes : {', '.join(self.missing_for_inertia)}",
                formula_values="—",
                unit="mm", ref="EC2", value=None,
            )
        return FormulaResult(
            symbol="xc",
            formula="(b/2)·x² + αe·(Asc+Ast)·x - αe·(Asc·d'+Ast·d) = 0",
            formula_values=f"xc = {self.xc:.2f}",
            unit="mm",
            ref="EC2 — §5.4",
            value=self.xc,
        )

    # ----- Inertie fissurée -----

    @property
    def Ic(self) -> Optional[float]:
        """
        Inertie de la section fissurée [mm⁴].
        Retourne None si données manquantes.
        """
        if not self.can_compute_inertia:
            return None
        if self._Ic is not None:
            return self._Ic

        b = self._sec.b
        alpha_e = self.alpha_eq_short
        ast = self._ast
        asc = self._asc or 0.0
        d = self._d
        d_p = self._d_prime
        xc = self.xc

        self._Ic = (
            b * xc**3 / 3
            + alpha_e * asc * (xc - d_p) ** 2
            + alpha_e * ast * (d - xc) ** 2
        )
        return self._Ic

    @property
    def Ic_report(self) -> Optional[FormulaResult]:
        if not self.can_compute_inertia:
            return FormulaResult(
                symbol="Ic",
                formula=f"Données manquantes : {', '.join(self.missing_for_inertia)}",
                formula_values="—",
                unit="mm⁴", ref="EC2", value=None,
            )
        return FormulaResult(
            symbol="Ic",
            formula="b·xc³/3 + αe·Asc·(xc-d')² + αe·Ast·(d-xc)²",
            formula_values=f"Ic = {self.Ic:.0f}",
            unit="mm⁴",
            ref="EC2 — §5.4",
            value=self.Ic,
        )

    # =========================================================================
    # Reporting
    # =========================================================================

    def all_reports(self) -> list[FormulaResult]:
        """Retourne tous les FormulaResult disponibles."""
        reports = [
            self.d_report,
            self.d_prime_report,
            self.z_report,
            self.alpha_eq_short_report,
        ]
        if self._phi_fluage is not None:
            reports.append(self.alpha_eq_long_report)

        reports.extend([
            self.xh_report,
            self.Ih_report,
            self.xc_report,
            self.Ic_report,
        ])
        return reports

    def summary(self) -> dict:
        """
        Résumé de toutes les données stockées.
        Utile pour le debug et l'export.
        """
        return {
            "name": self._name,
            "h": self._h,
            "d": self._d,
            "d'": self._d_prime,
            "z": self.z,
            "ast": self._ast,
            "asc": self._asc,
            "asp": self._asp,
            "asw": self._asw,
            "astc": self.astc,
            "phi_l": self._phi_l,
            "phi_t": self._phi_t,
            "cnom": self._cnom,
            "cmin": self._cmin,
            "delta_cdev": self._delta_cdev,
            "ev": self._ev,
            "eh": self._eh,
            "st": self._st,
            "exposure_class": self._exposure_class,
            "structural_class": self._structural_class,
            "steel_kind": self._steel_kind,
            "phi_fluage": self._phi_fluage,
            "alpha_eq_short": self.alpha_eq_short,
            "alpha_eq_long": self.alpha_eq_long,
            "xh": self.xh,
            "Ih": self.Ih,
            "xc": self.xc,
            "Ic": self.Ic,
        }

    # =========================================================================
    # Affichage
    # =========================================================================

    def __repr__(self) -> str:
        return (
            f"SecMatRC(sec={self._sec.__class__.__name__}, "
            f"concrete={self._mat_c}, "
            f"reinforcement={self._mat_s}, "
            f"d={self._d:.1f})"
        )

    def __str__(self) -> str:
        lines = [
            f"{'=' * 70}",
            f"  {self._name}",
            f"  Section : {self._sec.__class__.__name__} | "
            f"Béton : fck={self._mat_c.fck:.0f} MPa | "
            f"Acier : fyk={self._mat_s.fyk:.0f} MPa",
            f"{'=' * 70}",
            "",
            "  --- Données stockées ---",
        ]

        data = self.summary()
        for key, val in data.items():
            if key == "name":
                continue
            status = "✓" if val is not None else "—"
            val_str = f"{val}" if val is not None else "non renseigné"
            lines.append(f"  {status}  {key:20s} = {val_str}")

        lines.append("")
        lines.append("  --- Formules ---")
        for r in self.all_reports():
            val_str = r.formula_values if r.value is not None else f"⚠ {r.formula}"
            lines.append(f"  {val_str:55s} [{r.unit:5s}]  ({r.ref})")

        lines.append(f"{'=' * 70}")
        return "\n".join(lines)


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":

    from .sec_rectangular import SecRectangular
    from .mat_concrete import MatConcrete
    from .mat_reinforcement import MatReinforcement

    # --- Création de base ---
    sec = SecRectangular(b=300, h=500)
    beton = MatConcrete(fck=30)
    acier = MatReinforcement(fyk=500, ductility_class="B")

    rc = SecMatRC(sec=sec, mat_concrete=beton, mat_reinforcement=acier)
    print(rc)
    print("\n>>> Données manquantes pour inertie :", rc.missing_for_inertia)

    # --- L'utilisateur renseigne les armatures après calcul ---
    print("\n--- Après calcul de flexion ---")
    rc.ast = 1570.0    # 5HA20
    rc.asc = 628.0     # 2HA20
    rc.d = 455.0       # h - cnom - φt - φl/2
    rc.d_prime = 45.0
    rc.cnom = 30.0
    rc.phi_l = 20.0
    rc.phi_t = 8.0
    rc.exposure_class = "XC3"
    rc.phi_fluage = 2.5

    print(rc)
