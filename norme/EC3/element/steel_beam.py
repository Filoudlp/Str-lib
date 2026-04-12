#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Classe orchestratrice pour la vérification complète d'une poutre acier
selon l'Eurocode 3 (EN 1993-1-1).

SteelBeam ne contient aucune logique de calcul EC3 : elle délègue tout
aux fonctions pures situées dans les modules ``elu.*``, ``els.*`` et
``buckling.*`` (approche composition).

Unités attendues :
    - Forces      : N
    - Moments     : N·mm
    - Contraintes : MPa
    - Longueurs   : mm
    - Flèches     : mm
"""

__all__ = ['SteelBeam']

from typing import TypeVar, Optional
from core.formula import FormulaResult, FormulaCollection

# --- ELU checks ---
from norme.EC3.elu.traction import Tension
from norme.EC3.elu.compression import Compression
from norme.EC3.elu.shear import Shear
from norme.EC3.elu.bending import Bending
#from norme.EC3.elu.combined import check_combined

# --- ELS checks ---
#from norme.EC3.els.deflection import check_deflection
#from norme.EC3.els.drift import check_drift
#from norme.EC3.els.vibration import check_vibration

# --- Buckling checks ---
#from norme.EC3.buckling.flexural_buckling import check_flexural_buckling
#from norme.EC3.buckling.lateral_torsional import check_lateral_torsional
#from norme.EC3.buckling.interaction_NM import check_interaction_NM

SecMatSteel = TypeVar('SecMatSteel')


class SteelBeam:
    """
    Orchestrateur de vérification d'une poutre acier EC3-1-1.

    Parameters
    ----------
    sec_mat : SecMatSteel
        Objet portant toutes les propriétés section + matériau.
    N : float
        Effort normal de calcul [N]. Positif = traction si
        ``tension_positive=True`` (par défaut).
    V : float
        Effort tranchant de calcul [N].
    M : float
        Moment fléchissant de calcul [N·mm].
    deflection : float, optional
        Flèche calculée [mm] pour vérification ELS.
    deflection_limit : float, optional
        Flèche admissible [mm].
    drift : float, optional
        Déplacement horizontal calculé [mm].
    drift_limit : float, optional
        Déplacement horizontal admissible [mm].
    tension_positive : bool
        Convention de signe. ``True`` ⇒ N > 0 = traction.
    """

    # ------------------------------------------------------------------
    #  Construction
    # ------------------------------------------------------------------
    def __init__(
        self,
        sec_mat: SecMatSteel,
        N: float = 0.0,
        V: float = 0.0,
        M: float = 0.0,
        deflection: Optional[float] = None,
        deflection_limit: Optional[float] = None,
        drift: Optional[float] = None,
        drift_limit: Optional[float] = None,
        tension_positive: bool = True,
    ) -> None:

        self.__sec_mat = sec_mat
        self.__tension_positive = tension_positive

        # --- Convention de signe ---
        self.__N_raw = N
        self.__N = N if tension_positive else -N
        self.__V = abs(V)
        self.__M = abs(M)

        # --- ELS ---
        self.__deflection = deflection
        self.__deflection_limit = deflection_limit
        self.__drift = drift
        self.__drift_limit = drift_limit

    # ------------------------------------------------------------------
    #  Propriétés — Efforts
    # ------------------------------------------------------------------
    @property
    def N(self) -> float:
        """Effort normal signé (convention interne : + = traction) [N]"""
        return self.__N

    @property
    def V(self) -> float:
        """Effort tranchant (valeur absolue) [N]"""
        return self.__V

    @property
    def M(self) -> float:
        """Moment fléchissant (valeur absolue) [N·mm]"""
        return self.__M

    @property
    def is_tension(self) -> bool:
        """True si l'effort normal est de traction."""
        return self.__N > 0.0

    @property
    def is_compression(self) -> bool:
        """True si l'effort normal est de compression."""
        return self.__N < 0.0

    @property
    def sec_mat(self) -> SecMatSteel:
        """Objet section-matériau associé."""
        return self.__sec_mat

    # ------------------------------------------------------------------
    #  Propriétés — ELS
    # ------------------------------------------------------------------
    @property
    def deflection(self) -> Optional[float]:
        """Flèche calculée [mm]"""
        return self.__deflection

    @property
    def deflection_limit(self) -> Optional[float]:
        """Flèche admissible [mm]"""
        return self.__deflection_limit

    @property
    def drift(self) -> Optional[float]:
        """Déplacement horizontal calculé [mm]"""
        return self.__drift

    @property
    def drift_limit(self) -> Optional[float]:
        """Déplacement horizontal admissible [mm]"""
        return self.__drift_limit

    # ------------------------------------------------------------------
    #  Vérifications ELU individuelles
    # ------------------------------------------------------------------
    @property
    def check_traction(self) -> Optional[FormulaCollection]:
        """Vérification en traction — EC3-1-1 §6.2.3. None si N ≤ 0."""
        if not self.is_tension:
            return None
        sm = self.__sec_mat
        r = Tension(self.__N, sec_mat=sm)
        
        return r.verif

    @property
    def check_compression(self) -> Optional[FormulaCollection]:
        """Vérification en compression — EC3-1-1 §6.2.4. None si N ≥ 0."""
        if not self.is_compression:
            return None
        
        sm = self.__sec_mat
        r = Compression(self.__N, sec_mat=sm)
        
        return r.verif

    @property
    def check_shear(self) -> Optional[FormulaCollection]:
        """Vérification au cisaillement — EC3-1-1 §6.2.6. None si V = 0."""
        if self.__V == 0.0:
            return None
        sm = self.__sec_mat
        r = Shear(Ved=self.__V, sec_mat=sm)
        
        
        return r.verif

    
    def check_bending(self, axis="y") -> Optional[FormulaCollection]:
        """Vérification en flexion — EC3-1-1 §6.2.5. None si M = 0."""
        if self.__M == 0.0:
            return None
        
        sm = self.__sec_mat
        r = Bending(My_ed=self.__M, sec_mat=sm)
        if axis == "y":
            return r.verif_my
        elif axis == "z":
            return r.verif_mz
    @property
    def check_bending_y(self) -> Optional[FormulaCollection]:
        """Vérification en flexion — EC3-1-1 §6.2.5. None si M = 0."""
        if self.__M == 0.0:
            return None
        
        return self.check_bending(axis="y")

    @property
    def check_bending_z(self) -> Optional[FormulaCollection]:
        """Vérification en flexion — EC3-1-1 §6.2.5. None si M = 0."""
        if self.__M == 0.0:
            return None
        
        return self.check_bending(axis="z")

    def check_combinedbendingshear(self, with_values: bool = False) -> Optional[FormulaCollection]:
        """Vérification interaction M+V — EC3-1-1 §6.2.8. None si V=0 ou M=0."""
        #Not implemented yet
        if self.__V == 0.0 or self.__M == 0.0:
            return None
        sm = self.__sec_mat
        return check_combined(
            Ned=abs(self.__N), Med=self.__M, Ved=self.__V,
            A=sm.A, Av=sm.Av,
            Wpl=sm.Wpl_y, fy=sm.fy, gamma_m0=sm.gamma_m0,
            section_class=sm.section_class,
            with_values=with_values,
        )

    def check_combined(self, with_values: bool = False) -> Optional[FormulaCollection]:
        """Vérification interaction N+M+V — EC3-1-1 §6.2.9/10. None si N=0 et M=0."""
        if self.__N == 0.0 and self.__M == 0.0:
            return None
        sm = self.__sec_mat
        return check_combined(
            Ned=abs(self.__N), Med=self.__M, Ved=self.__V,
            A=sm.A, Av=sm.Av,
            Wpl=sm.Wpl_y, fy=sm.fy, gamma_m0=sm.gamma_m0,
            section_class=sm.section_class,
            with_values=with_values,
        )

    def check_elu(self, with_values: bool = False) -> FormulaCollection:
        """
        Vérification ELU globale : agrège traction, compression,
        cisaillement, flexion et interaction.
        """
        fc = FormulaCollection(
            title="Vérifications ELU — Résistance de section",
            ref="EC3-1-1 — §6.2",
        )
        print(1)
        for check_fn in [
            self.check_traction,
            self.check_compression,
            self.check_shear,
            self.check_bending,
            self.check_combined,
        ]:
            print(2)
            result = check_fn(with_values=with_values)
            print(3)
            if result is not None:
                fc.merge(result)
        return fc

    # ------------------------------------------------------------------
    #  Vérifications ELS individuelles
    # ------------------------------------------------------------------
    def check_deflection(self, with_values: bool = False) -> Optional[FormulaCollection]:
        """Vérification de flèche. None si non renseigné."""
        if self.__deflection is None or self.__deflection_limit is None:
            return None
        return check_deflection(
            deflection=self.__deflection,
            limit=self.__deflection_limit,
            with_values=with_values,
        )

    def check_drift(self, with_values: bool = False) -> Optional[FormulaCollection]:
        """Vérification de déplacement horizontal. None si non renseigné."""
        if self.__drift is None or self.__drift_limit is None:
            return None
        return check_drift(
            drift=self.__drift,
            limit=self.__drift_limit,
            with_values=with_values,
        )

    def check_vibration(self, with_values: bool = False) -> FormulaCollection:
        """Placeholder — vérification vibratoire (non implémenté)."""
        fc = FormulaCollection(
            title="Vérification vibratoire",
            ref="EC3-1-1",
        )
        fc.add(FormulaResult(
            name="Vibration",
            formula="-",
            formula_values="Non implémenté" if with_values else "",
            result=0.0,
            unit="-",
            ref="-",
        ))
        return fc

    def check_els(self, with_values: bool = False) -> FormulaCollection:
        """Vérification ELS globale : flèche + drift + vibration."""
        fc = FormulaCollection(
            title="Vérifications ELS",
            ref="EC3-1-1",
        )
        for check_fn in [
            self.check_deflection,
            self.check_drift,
        ]:
            result = check_fn(with_values=with_values)
            if result is not None:
                fc.merge(result)
        return fc

    # ------------------------------------------------------------------
    #  Vérifications stabilité individuelles
    # ------------------------------------------------------------------
    def check_flexural_buckling(self, with_values: bool = False) -> Optional[FormulaCollection]:
        """Vérification flambement — EC3-1-1 §6.3.1. None si N ≥ 0."""
        if not self.is_compression:
            return None
        sm = self.__sec_mat
        return check_flexural_buckling(
            Ned=abs(self.__N),
            A=sm.A, Aeff=sm.Aeff,
            fy=sm.fy, E=sm.E,
            Iy=sm.Iy, Iz=sm.Iz,
            Lcr_y=sm.Lcr_y, Lcr_z=sm.Lcr_z,
            gamma_m1=sm.gamma_m1,
            section_class=sm.section_class,
            with_values=with_values,
        )

    def check_lateral_torsional(self, with_values: bool = False) -> Optional[FormulaCollection]:
        """Vérification déversement — EC3-1-1 §6.3.2. None si M = 0."""
        if self.__M == 0.0:
            return None
        sm = self.__sec_mat
        return check_lateral_torsional(
            Med=self.__M,
            Wpl=sm.Wpl_y, Wel=sm.Wel_y,
            fy=sm.fy, E=sm.E,
            Iz=sm.Iz, Iy=sm.Iy,
            LTB_length=sm.LTB_length,
            gamma_m1=sm.gamma_m1,
            section_class=sm.section_class,
            with_values=with_values,
        )

    def check_interaction_NM(self, with_values: bool = False) -> Optional[FormulaCollection]:
        """Interaction N+M instabilité — EC3-1-1 §6.3.3. None si N=0 ou M=0."""
        if self.__N == 0.0 or self.__M == 0.0:
            return None
        sm = self.__sec_mat
        return check_interaction_NM(
            Ned=abs(self.__N), Med=self.__M,
            A=sm.A, Aeff=sm.Aeff,
            Wpl=sm.Wpl_y, Wel=sm.Wel_y,
            fy=sm.fy, E=sm.E,
            Iy=sm.Iy, Iz=sm.Iz,
            Lcr_y=sm.Lcr_y, Lcr_z=sm.Lcr_z,
            LTB_length=sm.LTB_length,
            gamma_m1=sm.gamma_m1,
            section_class=sm.section_class,
            with_values=with_values,
        )

    def check_stability(self, with_values: bool = False) -> FormulaCollection:
        """Vérification stabilité globale : flambement + déversement + interaction."""
        fc = FormulaCollection(
            title="Vérifications Stabilité",
            ref="EC3-1-1 — §6.3",
        )
        for check_fn in [
            self.check_flexural_buckling,
            self.check_lateral_torsional,
            self.check_interaction_NM,
        ]:
            result = check_fn(with_values=with_values)
            if result is not None:
                fc.merge(result)
        return fc

    # ------------------------------------------------------------------
    #  Vérification complète
    # ------------------------------------------------------------------
    def full_check(self, with_values: bool = False) -> FormulaCollection:
        """Vérification complète : ELU + ELS + Stabilité."""
        fc = FormulaCollection(
            title="Vérification complète — Poutre acier",
            ref="EC3-1-1",
        )
        fc.merge(self.check_elu(with_values=with_values))
        fc.merge(self.check_els(with_values=with_values))
        fc.merge(self.check_stability(with_values=with_values))
        return fc

    # ------------------------------------------------------------------
    #  Résumé
    # ------------------------------------------------------------------
    @staticmethod
    def _extract_max_ratio(fc: Optional[FormulaCollection]) -> Optional[float]:
        """Extrait le taux max (result du dernier FormulaResult) d'un FC."""
        if fc is None or len(fc) == 0:
            return None
        return fc[-1].result

    @staticmethod
    def _extract_governing_check(fc: Optional[FormulaCollection]) -> Optional[str]:
        """Extrait le nom du check déterminant (result max) d'un FC."""
        if fc is None or len(fc) == 0:
            return None
        max_ratio = 0.0
        governing = None
        for fr in fc:
            if fr.result is not None and fr.result >= max_ratio:
                max_ratio = fr.result
                governing = fr.name
        return governing

    def summary(self) -> dict:
        """
        Retourne un dictionnaire résumé de toutes les vérifications.

        Returns
        -------
        dict
            {
                "elu":       {"governing_check": str, "max_ratio": float, "is_ok": bool},
                "els":       {"governing_check": str, "max_ratio": float, "is_ok": bool},
                "stability": {"governing_check": str, "max_ratio": float, "is_ok": bool},
                "is_ok":     bool or None,
            }
        """
        result = {}

        for category, fc_method in [
            ("elu", self.check_elu),
            ("els", self.check_els),
            ("stability", self.check_stability),
        ]:
            fc = fc_method(with_values=False)
            ratio = self._extract_max_ratio(fc)
            check = self._extract_governing_check(fc)

            if ratio is not None:
                is_ok = ratio <= 1.0
            else:
                is_ok = None

            result[category] = {
                "governing_check": check,
                "max_ratio": ratio,
                "is_ok": is_ok,
            }

        all_checks = [result[k]["is_ok"] for k in ("elu", "els", "stability")]
        evaluated = [v for v in all_checks if v is not None]
        result["is_ok"] = all(evaluated) if evaluated else None

        return result

    # ------------------------------------------------------------------
    #  Représentation
    # ------------------------------------------------------------------
    def __repr__(self) -> str:
        N_kN = self.__N_raw / 1e3
        V_kN = self.__V / 1e3
        M_kNm = self.__M / 1e6
        return (
            f"SteelBeam(sec_mat={self.__sec_mat}, "
            f"N={N_kN:+.1f}kN, V={V_kN:.1f}kN, M={M_kNm:.1f}kN·m)"
        )


# ======================================================================
#  Debug / exemple d'utilisation
# ======================================================================
if __name__ == "__main__":
    from types import SimpleNamespace

    # --- Faux SecMatSteel : IPE 300 / S355 ---
    sec_mat = SimpleNamespace(
        h=300.0, b=150.0, tf=10.7, tw=7.1,
        A=5381.0, Anet=4800.0, Av_z=2567.0, Aeff=5381.0,
        Iy=8356e4, Iz=603.8e4,
        Wel_y=5571e3, Wpl_y=6284e3,
        Wel_z=80.5e3, Wpl_z=125.2e3,
        Weff_y=5571e3,
        fy=355.0, fu=490.0, E=210000.0,
        gamma_m0=1.0, gamma_m1=1.0, gamma_m2=1.25,
        section_class=1,
        Lcr_y=6000.0, Lcr_z=3000.0, LTB_length=3000.0,
        section_type="I",
    )

    

    sep = "-" * 60

    # --- Cas 1 : flexion + cisaillement ---
    print(f"\n{sep}")
    print("  CAS 1 : Flexion + Cisaillement")
    print(sep)
    beam1 = SteelBeam(sec_mat=sec_mat, N=0.0, V=120e3, M=200e6)
    print(f"  {repr(beam1)}")
    try:
        print(f"  ELU : {beam1.check_elu(with_values=True)}")
    except Exception as e:
        print(f"  ⚠ {type(e).__name__}: {e}")

    # --- Cas 2 : compression + flexion ---
    print(f"\n{sep}")
    print("  CAS 2 : Compression + Flexion")
    print(sep)
    beam2 = SteelBeam(sec_mat=sec_mat, N=-150e3, V=80e3, M=220e6)
    print(f"  {repr(beam2)}")
    try:
        s = beam2.summary()
        for cat in ("elu", "els", "stability"):
            d = s[cat]
            print(f"  {cat.upper():12s} | check: {str(d['governing_check']):20s} "
                  f"| ratio: {d['max_ratio'] or '-':>8} | ok: {d['is_ok']}")
        print(f"  {'GLOBAL':12s} | is_ok: {s['is_ok']}")
    except Exception as e:
        print(f"  ⚠ {type(e).__name__}: {e}")

    # --- Cas 3 : traction pure --- OK
    print(f"\n{sep}")
    print("  CAS 3 : Traction pure")
    print(sep)
    beam3 = SteelBeam(sec_mat=sec_mat, N=500e3)
    print(f"  {repr(beam3)}")
    print("before")
    try:
        print("in")
        fc = beam3.check_traction
        print(f"  Traction : {fc}")
    except Exception as e:
        print(f"  ⚠ {type(e).__name__}: {e}")

    # --- Cas 3.1 : compression pure --- OK
    print(f"\n{sep}")
    print("  CAS 3.1 : Compression pure")
    print(sep)
    beam3 = SteelBeam(sec_mat=sec_mat, N=-500e3)
    print(f"  {repr(beam3)}")
    try:
        fc = beam3.check_compression
        print(f"  Compression : {fc}")
    except Exception as e:
        print(f"  ⚠ {type(e).__name__}: {e}")

    # --- Cas 3.2: cisaillement pure --- OK
    print(f"\n{sep}")
    print("  CAS 3.2 : Cisaillement pure")
    print(sep)
    beam3 = SteelBeam(sec_mat=sec_mat, V=500e3)
    print(f"  {repr(beam3)}")
    try:
        fc = beam3.check_shear
        print(f"  Cisaillement : {fc}")
    except Exception as e:
        print(f"  ⚠ {type(e).__name__}: {e}")

    # --- Cas 3.3: flexion pure --- OK
    print(f"\n{sep}")
    print("  CAS 3.3 : Flexion pure")
    print(sep)
    beam3 = SteelBeam(sec_mat=sec_mat, M=500e6)
    print(f"  {repr(beam3)}")
    try:
        fc = beam3.check_bending_y
        print(f"  Flexion y : {fc}")
        fc = beam3.check_bending_y
        print(f"  Flexion z : {fc}")
    except Exception as e:
        print(f"  ⚠ {type(e).__name__}: {e}")

    # --- Cas 4 : avec ELS ---
    print(f"\n{sep}")
    print("  CAS 4 : Avec flèche ELS")
    print(sep)
    beam4 = SteelBeam(
        sec_mat=sec_mat, N=0.0, V=60e3, M=150e6,
        deflection=18.5, deflection_limit=20.0,
        drift=3.2, drift_limit=5.0,
    )
    print(f"  {repr(beam4)}")
    try:
        fc = beam4.check_els(with_values=True)
        print(f"  ELS : {fc}")
    except Exception as e:
        print(f"  ⚠ {type(e).__name__}: {e}")

    # --- Cas 5 : convention inversée ---
    print(f"\n{sep}")
    print("  CAS 5 : tension_positive=False (N=-100kN → traction)")
    print(sep)
    beam5 = SteelBeam(sec_mat=sec_mat, N=-100e3, tension_positive=False)
    print(f"  {repr(beam5)}")
    print(f"  is_tension = {beam5.is_tension}")
    print(f"  is_compression = {beam5.is_compression}")

    # --- Cas 6 : aucun effort ---
    print(f"\n{sep}")
    print("  CAS 6 : Aucun effort")
    print(sep)
    beam6 = SteelBeam(sec_mat=sec_mat)
    print(f"  {repr(beam6)}")
    try:
        s = beam6.summary()
        print(f"  summary is_ok = {s['is_ok']}")
    except Exception as e:
        print(f"  ⚠ {type(e).__name__}: {e}")

    print(f"\n{'=' * 60}")
    print("  FIN DES TESTS")
    print(f"{'=' * 60}")
