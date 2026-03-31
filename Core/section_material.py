#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Module to define section variable specific to a material

    UNITS USED:
        - m -> Metter
        - MN -> Mega Newton
        - MPa -> Mega Pascal
"""

class ReinforcedConcrete:
    """
        Class to define default variable for concrete section
    """
    ALPHA_SHEAR = 90

    def __init__(self, h):
        """
            Constructor
        """
        # Variable that will be used
        # Steel or prestress
        self.ast = None
        self.asc = None
        self.asp = None # Prestress reinforce

        self.astc = None # ast + asc

        self.phy_t_max = None # Maximal size of a reinforcement

        self._steel_kind = "HA" # type of steel, by default HA

        # Equivalent coefficient
        self._alpha_eq = 15 # Defautl value for RC

        self.__bw = None

        # Geometrical property
        self._Ih = None # homogenous inertia
        self._Ic = None # Crack inertia
        
        self._xh = None # Homogenous neutral axis
        self._xc = None # Crack neutral axis
        self._xn = None # Neutral axis
        
        self._d = None
        self._d_p = None

        self._h = h

        self.__z = z
        self.__bw = bw

        # Space
        self._ev = None # Vertical space between two reinforcement
        self._eh = None # Horizontal space between two reinforcement

        # Concrete cover
        self._cnom = None

        # Exposition class
        self._expo_class = None

        # Structural class
        self._str_class = None

        self._define_value()
    
    def _define_value(self):
        """ function to define value """
        self.__define_d()
        self.__define_d_p()

    def __define_d(self):
        """ function to define d """
        self._d = 0.9 * self._h

    def __define_d_p(self):
        """ function to define d """
        self._d_p = 0.1 * self._h

    def __define_steel_kind(self):
        """
            function to define steel kind
            value could be:
                - HA
                - PC -> prestress concrete
                - RL -> Ronds lisse
        """
        self._steel_kind = "HA"
    # GET
    @property
    def d(self):
        """ d getter """
        return self._d
    @property
    def d_p(self):
        """ d_p getter """
        return self._d_p
    @property
    def steel_kind(self):
        return self._steel_kind

    # SET
    @d.setter
    def d(self, val):
        """ redefine value when changing d """
        self._d = val
        self._define_value()

    @d_p.setter
    def d_p(self, val):
        """ redefinie value when changing d_p """
        self._d_p = val
        self._define_value()

    @steel_kind.setter
    def steel_kind(self, val):
        self._steel_kind = val
        self.__define_steel_kind()


class BoltSteel:

    def __init__(self, t:float, d0:float):
        
        self.__t = t
        self.__d0 = d0
        self.define_min_max()

    def define_min_max(self):

        self.__e1_min = self.__e2_min = 1.2 * self.__d0
        self.__e3_min, self.__e4_min = 1.5 * self.__d0
        self.__p1_min = 2.2 * self.__d0
        self.__p2_min = 2.4 * self.__d0

        self.__e1_max = self.__e2_max = 4 * self.__t + 40 # 40 mm
        self.__p1_max = self.__p10_max = \
        self.__p2_max = min(14 * self.__t, 200) # 200 mm
        self.__p1i_max = min(28 * self.__t, 400) # 400 mm

    @property
    def e1_min(self):
        return self.__e1_min
    
    @property
    def e2_min(self):
        return self.__e2_min

    @property
    def e3_min(self):
        return self.__e3_min
    
    @property
    def e4_min(self):
        return self.__e4_min

    @property
    def p1_min(self):
        return self.__p1_min
    
    @property
    def p2_min(self):
        return self.__p2_min

class Mixte:
    
    def __init__(self):
        pass
        

class Timber:
    
    def __init__(self):
        pass

if __name__ == "__main__":
    test = BoltSteel(7, 10)

    print(test.e1_min)
    print(test.e2_min)