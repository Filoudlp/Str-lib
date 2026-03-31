# Librairy
import timeit

import copy
import math
import numpy as np
import os
# import sympy as sp

start = timeit.default_timer()
print("Librairy importation: " + str(timeit.default_timer()-start))

__all__ = ['Point', 'Barre', 'Stiffness_methode', 'Split']
 

class Point:
    """
        Class to define point element:
        FEM
        Cross section

        This class can be define a "symbolic class"
        it's mean that all calculation will be algerbric

        :@param __NB_POINT: Nb of point created
        :@type __NB_POINT: integer
        :@default name: 0 (No elements created)

        Instance attribute:
        :@param name: Name of the point

        :@param x: X coordinate of the point
        :@param y: Y coordinate of the point

        :@param pt_num: point number

        :@param rx: Support reaction in X
        :@param ry: Support reaction in Y
        :@param mt: Support reaction in Moment

        :@param delta_x: Displacement in X
        :@param delta_y: Displacement in Y
        :@param theta: Rotation theta

        :@param rx_cond: Support condition in X
        :@param ry_cond: Support condition in Y
        :@param mt_cond: Support condition in Mz
        :@note: those variable are call if you want
            to define a point as a support

        :@param fx: External force in X
        :@param fy: External force in Y
        :@param mt: External moment

        :@param normal: Internale Normal force
        :@param shear: Internale Shear force
        :@param moment: Internal Bending Moment

        :@type name: int, float, str

        :@type x: int, float
        :@type y: int, float

        :@type pt_num: int

        :@type rx: float
        :@type ry: float
        :@type mt: float

        :@type delta_x: float
        :@type delta_y: float
        :@type theta: float

        :@type rx_cond: boolean
        :@type ry_cond: boolean
        :@type mt_cond: boolean

        :@type fx: float
        :@type fy: float
        :@type mt: float

        :@type normal: float
        :@type shear: float
        :@type moment: float



    """
    NB_POINT = 0

    @classmethod
    def reset(cls) -> None:
        """ """
        cls.NB_POINT = 0

    def __del__(self) -> None:
        """ function when an element of the classe if delate """
        Point.NB_POINT -= 1

    def __init__(self, x: float, y: float, name: str = None,
                 symbolic: bool = False) -> None:
        """ Constructor 
            :@param x: X coordonate
            :@param y: Y coordonate
            :@param name: Node name
            :@param symbolic: Choose if all calculation will be algerbric
            :@type x: float
            :@type y: float
            :@type name: float
            :@type symbolic: boolean
            :@default name: 0 (No name given)
            :@default symbolic: False (Numerical calculation)
        """
        Point.NB_POINT += 1
        self.__Symbolic_class = symbolic

        # Coordonate
        if symbolic:
            raise NotImplementedError("Not implented yet")
            # self.__define_default_value_symb(name)
        else:
            self.__X: float = x
            self.__Y: float = y
            self.__Pt_num: int = Point.NB_POINT
            self.__define_default_value(name)
    
    def __define_default_value(self, name: str) -> str:
        """ Initialize default value  
            :@param name: Point Name
            :@type name: String
        """
        
        # Set value as P_number by default
        if name is None:
            self.__Name = "P" + str(Point.NB_POINT) 
        else:  # Other the name choosen
            self.__Name = name

        self.__Rx: float = 0
        self.__Ry: float = 0
        self.__Mt: float = 0

        self.__Delta_x: float = 0
        self.__Delta_y: float = 0
        self.__Rot: float = 0

        # False mean no support
        self.__Rx_cond: int = 0
        self.__Ry_cond: int = 0
        self.__Mt_cond: int = 0

        self.__Fx: float = 0
        self.__Fy: float = 0
        self.__Mz: float = 0
      
    def define_external_force(self, fx: float, fy: float, mz: float) -> None:
        """ Function to define external force 

            :@param fx: External force in X
            :@param fy: External force in Y
            :@param mz: External moment in Z
            :@type fx: float
            :@type fy: float
            :@type mz: float
        """

        self.__Fx: float = fx
        self.__Fy: float = fy
        self.__Mz: float = mz

    def define_internal_force(self, fx: float, fy: float, mz: float) -> None:
        """ Function to define external force 
        
            :@param fx: Normal node force
            :@param fy: Shear node force
            :@param mz: Moment node force
            :@type fx: float
            :@type fy: float
            :@type mz: float
        """

        self.__Normal: float = fx
        self.__Shear: float = fy
        self.__Moment: float = mz
    
    def define_support_reaction(self, rx: float, ry: float, mt: float) -> None:
        """ Function to define support reaction 
        
            :@param rx: X reaction
            :@param ry: Y reaction
            :@param mt: Moment reaction
            :@type rx: float
            :@type ry: float
            :@type mt: float
        """

        self.__Rx: float = rx
        self.__Ry: float = ry
        self.__Mt: float = mt
    
    def define_displacement(self, dx: float, dy: float, theta: float) -> None:
        """ Function to define displacement 
        
            :@param dx: X displacement
            :@param dy: Y displacement
            :@param theta: rotation
            :@type dx: float
            :@type dy: float
            :@type theta: float
        """

        self.__Delta_x: float = dx
        self.__Delta_y: float = dy
        self.__Rot: float = theta
    
    def define_support_condition(self, rx: bool = False,
                                 ry: bool = False, mt: bool = False) -> None:
        """ Function to define displacement 
        
            :@param rx: Block X displacement (True)
            :@param ry: Block Y displacement (True)
            :@param mt: Block rotation (True)
            :@type rx: bool
            :@type ry: bool
            :@type mt: bool
            :@default rx: False (Allow displacement)
            :@default ry: False (Allow displacement)
            :@default mt: False (Allow rotation)
        """
        self.__Rx_cond: int = 1 if rx else 0
        self.__Ry_cond: int = 1 if ry else 0
        self.__Mt_cond: int = 1 if mt else 0

# Get
    # Name
    @property
    def Name(self) -> str:
        """Name of the point"""
        return self.__Name

    # Pt_num
    @property
    def Pt_num(self) -> int:
        """Number of the point"""
        return self.__Pt_num

    # Coordonate
    @property
    def Y(self) -> float:
        """Y coordinate of the point"""
        return self.__Y

    @property
    def X(self) -> float:
        """X coordinate of the point"""
        return self.__X
    
    # External force
    @property  
    def Fx(self) -> float:
        """Fx of the point"""
        return self.__Fx

    @property
    def Fy(self) -> float:
        """Fy of the point"""
        return self.__Fy
    
    @property
    def Mz(self) -> float:
        """Mz of the point"""
        return self.__Mz

    # Internal force
    @property
    def Normal(self) -> float:
        """Normal force of the point"""
        return self.__Normal
    
    @property
    def Shear(self) -> float:
        """Shear force of the point"""
        return self.__Shear
    
    @property
    def Moment(self) -> float:
        """Bending Moment of the point"""
        return self.__Moment
    
    # Support reaction
    @property
    def Rx(self) -> float:
        """X support reaction of the point"""
        return self.__Rx
    
    @property
    def Ry(self) -> float:
        """Y support reaction of the point"""
        return self.__Ry
    
    @property
    def Mt(self) -> float:
        """Moment support reaction of the point"""
        return self.__Mt

    @property
    def Rx_cond(self) -> bool:
        """X Support condition of the point
        True: Fixed
        False: Free"""
        return True if self.__Rx_cond == 1 else False
    
    @property
    def Ry_cond(self) -> bool:
        """Y Support condition of the point
        True: Fixed
        False: Free"""
        return True if self.__Ry_cond == 1 else False
    
    @property
    def Mt_cond(self) -> bool:
        """Mt support condition of the point
        True: Fixed
        False: Free"""
        return True if self.__Mt_cond == 1 else False

    # Displacement
    @property
    def Dx(self) -> float:
        """X displacement of the point"""
        return self.__Delta_x
    
    @property
    def Dy(self) -> float:
        """Y displacement of the point"""
        return self.__Delta_y
    
    @property
    def Theta(self) -> float:
        """Rotation of the point"""
        return self.__Rot

    # Other
    @property
    def Hyper_degree(self) -> float:
        counter = 0
        if self.__Rx_cond:
            counter += 1
        if self.__Ry_cond:
            counter += 1
        if self.__Mt_cond:
            counter += 1
        return counter 

# Set 
    # Name
    @Name.setter
    def Name(self, name: float) -> None:
        self.__Name = name
    
    # Pt_num
    @Pt_num.setter
    def Pt_num(self, val: int) -> None:
        self.__Pt_num = val
    
    # Support reaction
    @Rx.setter
    def Rx(self, val: float) -> None:
        self.__Rx = val
    
    @Ry.setter
    def Ry(self, val: float) -> None:
        self.__Ry = val
    
    @Mt.setter
    def Mt(self, val: float) -> None:
        self.__Mt = val

    # Displacement
    @Dx.setter
    def Dx(self, val: float) -> None:
        self.__Delta_x = val
    
    @Dy.setter
    def Dy(self, val: float) -> None:
        self.__Delta_y = val
        
    @Theta.setter
    def Theta(self, val: float) -> None:
        self.__Rot = val
    

class Barre: 
    """
        Class to create barre element  
        according to 2 points

        :@param __NB_BARRE: Nb of element created
        :@type __NB_BARRE: integer
        :@default __NB_BARRE: 0 (No elements created)
    
        Instance attribute:
        :@param p_beg:
        :@param p_end:
        :@param beg_type:
        :@param end_type:

        :@param cross_section:
        :@param material:

        :@param p_beg_name:
        :@param p_end_name:

        :@param pt_num_beg:
        :@param pt_num_end:

        :@param fx_x_beg:
        :@param fx_y_beg:
        :@param fx_m_beg:

        :@param fx_x_end:
        :@param fx_y_end:
        :@param fx_m_end:

        :@param fy_x_beg:
        :@param fy_y_beg:
        :@param fy_m_beg:

        :@param fy_x_end:
        :@param fy_y_end:
        :@param fy_m_end:

        :@param mz_x_beg:
        :@param mz_y_beg:
        :@param mz_m_beg:

        :@param mz_x_end:
        :@param mz_y_end:
        :@param mz_m_end:

        :@param dt_x_beg:
        :@param dt_y_beg:
        :@param dt_m_beg:

        :@param dt_x_end:
        :@param dt_y_end:
        :@param dt_m_end:

        :@param pc_x_beg:
        :@param pc_y_beg:
        :@param pc_m_beg:

        :@param pc_x_end:
        :@param pc_y_end:
        :@param pc_m_end:

        :@param length:
        :@param angle:

        :@param rot_mat:
        :@param k_local_mat:
        :@param k_barre:

        :@param fx:
        :@param fy:
        :@param mz:
        :@param dt_x:
        :@param dt_m:
        :@param pc:

        :@param x_beg:
        :@param y_beg:
        :@param x_end:
        :@param y_end:
    
    """
# Attribute
    NB_BARRE = 0 

    @classmethod
    def reset(cls) -> None:
        """ """
        cls.NB_BARRE = 0
    
    @property
    def Nb_barre(self) -> int:
        """Number of barre created"""
        return Barre.NB_BARRE
    
    def __del__(self) -> None:
        """ Function when a barre object is delete"""
        Barre.NB_BARRE -= 1

    def __init__(self,  point1: 'Point', point2: 'Point',
                 section: 'Point' = None, material: 'Point' = None,
                 beg_type: str = "FIXED", end_type: str = "FIXED",
                 symbolic: bool = False) -> None:
        """ Constructor
            :@param point1: 1st node of the barre
            :@param point2: last node of the barre
            :@param section: Barre cross_section
            :@param material: Barre material
            :@param beg_type: 1st node support condition for calculation
            :@param end_type: last node support condition for calculation
            :@param symbolic: Choose if all calculation will be algerbric
            :@type point1: Point object
            :@type point2: Point object
            :@type section: TCross_section object or boolean
            :@type material: TMaterial object or boolean
            :@type beg_type: String
            :@type end_type: String
            :@type symbolic: boolean
            :@default section: False (mean we take A and I = 1)
            :@default material: False (mean we take E = 1)
            :@default beg_type: "FIXED" (Node condition for the matrix creation) # noqa E501
            :@default end_type: "FIXED" (Node condition for the matrix creation) # noqa E501
            :@default symbolic: False (Numerical calculation)
        """
        Barre.NB_BARRE += 1

        self.beg_type = beg_type
        self.end_type = end_type

        # Point
        self.__P_beg: 'Point' = point1
        self.__P_end: 'Point' = point2
        
        # Section property
        self.__Cross_section: 'Section' = section  # noqa: F821
        self.__Material: 'Material' = material  # noqa: F821
        
        # Define
        if symbolic:
            raise NotImplementedError("Not implented yet")
        else:
            self.__default_value()
            self.define_property()

    # Initialisation

    def define_property(self) -> None:
        """ Function to define point property 
        :@param beg_type: 1st node support condition for calculation
        :@param end_type: last node support condition for calculation
        :@type beg_type: str
        :@type end_type: str
        """             
        self.__Angle: float = self.__define_alpha()
        self.__Length: float = self.__define_length()
        self.__Rot_mat: 'Array float' = self.__define_rotation_mat()  # noqa F722
        self.define_local_mat(self.beg_type, self.end_type)

    def __default_value(self):
        """ Function to define default value """
        self.__Fx = False
        self.__Fy = False
        self.__Mz = False
        self.__dT_x = False
        self.__dT_m = False
        self.__PC = False

        self.__Fx_force = 0
        self.__Fy_force = 0
        self.__Mz_force = 0
        self.__Kind_force = "GLOBAL"
        self.__Angle_force = 0
        
        self.__dT_force_x = 0
        self.__dT_force_m = 0
        
        self.__PC_equation = 0
        self.__PC_value = 0
        self.__PC_coef = 0
        self.__PC_kind = 0
        
        # Fx
        self.__Fx_x_beg = 0 
        self.__Fx_y_beg = 0
        self.__Fx_m_beg = 0
        
        self.__Fx_x_end = 0 
        self.__Fx_y_end = 0
        self.__Fx_m_end = 0
      
        # Fy
        self.__Fy_x_beg = 0 
        self.__Fy_y_beg = 0
        self.__Fy_m_beg = 0
        
        self.__Fy_x_end = 0 
        self.__Fy_y_end = 0
        self.__Fy_m_end = 0

        # Mz
        self.__Mz_x_beg = 0 
        self.__Mz_y_beg = 0
        self.__Mz_m_beg = 0
        
        self.__Mz_x_end = 0 
        self.__Mz_y_end = 0
        self.__Mz_m_end = 0
        
        # dt
        self.__dT_x_beg = 0
        self.__dT_y_beg = 0
        self.__dT_m_beg = 0
        
        self.__dT_x_end = 0 
        self.__dT_y_end = 0
        self.__dT_m_end = 0
        
        # PC
        self.__PC_x_beg = 0
        self.__PC_y_beg = 0
        self.__PC_m_beg = 0
        
        self.__PC_x_end = 0 
        self.__PC_y_end = 0
        self.__PC_m_end = 0

    def redefine_property(self, point1: 'Point', point2: 'Point',
                          section: 'Section' = False,  # noqa: F821
                          material: 'Material' = False,  # noqa: F821
                          beg_type: str = "FIXED", 
                          end_type: str = "FIXED") -> None:  # noqa: E501
        """ Function to define point property """
        # Point
        self.p_beg = point1
        self.p_end = point2

        self.beg_type = beg_type
        self.end_type = end_type

        # Section property
        self.cross_section = section  # noqa: F821
        self.material = material  # noqa: F821
        self.define_property()
        
    def redefine_force(self) -> None:
        """ Function to redifine property after a split """

        fx = self.__Fx_force
        fy = self.__Fy_force
        mz = self.__Mz_force
        kind_f = self.__Kind_force
        angle = self.__Angle_force

        self.uniforme_load(fx, fy, mz, kind_f, angle)
        
        dT_x = self.__dT_force_x
        dT_m = self.__dT_force_m
        
        self.temperature(dT_x, dT_m)
        
        eq = self.__PC_equation
        PC_value = self.__PC_value
        coef = self.__PC_coef
        kind = self.__PC_kind
        
        self.prestress_load(eq, kind, coef, PC_value)
        
    def __define_length(self) -> float:
        """ Function to define the length of the barre """
        x_beg: float = self.__P_beg.X
        y_beg: float = self.__P_beg.Y

        x_end: float = self.__P_end.X
        y_end: float = self.__P_end.Y
        
        length = math.sqrt((x_end - x_beg)**2 + (y_end - y_beg)**2)
        return length
    
    def __define_alpha(self) -> float:
        """ Function to define the angle of the barre 
            compare to a default axe |_ -> _ (x) ; | (y)
        """
        x_beg: float = self.__P_beg.X
        y_beg: float = self.__P_beg.Y

        x_end: float = self.__P_end.X
        y_end: float = self.__P_end.Y
        
        if (x_end - x_beg) != 0:
            atan: float = math.atan((y_end - y_beg) / (x_end - x_beg))
            angle: float = math.degrees(atan)
        else:
            sign: int = math.copysign(1, (y_end - y_beg))
            angle: int = sign * 90
        return angle
        
    # Define matrix
   
    def __define_rotation_mat(self) -> 'Array_float':  # noqa: F821
        """ Function to define the rotation mat 
            __Rot_mat = [[ cos alpha, sin alpha, 0, 0, 0, 0],
                         [ -sin alpha, cos alpha, 0, 0, 0, 0],
                         [ 0, 0, 1, 0, 0, 0],
                         [ 0, 0, 0, cos alpha, sin alpha, 0],
                         [ 0, 0, 0, -sin alpha, cos alpha, 0],
                         [ 0, 0, 0, 0, 0, 1]] 
        """
        angle_rad = math.radians(self.__Angle)
        
        cos, sin = math.cos(angle_rad), math.sin(angle_rad)
        
        rot_mat = np.array([[cos, sin, 0, 0, 0, 0],
                            [-sin, cos, 0, 0, 0, 0],
                            [0, 0, 1, 0, 0, 0],
                            [0, 0, 0, cos, sin, 0],
                            [0, 0, 0, -sin, cos, 0],
                            [0, 0, 0, 0, 0, 1]], dtype=float)
        return rot_mat

    def define_local_mat(self, beg_type: str = "FIXED", 
                         end_type: float = "FIXED") -> None:
        """ Function to define local stiffness matrix to all element
            in local axes
            :@param beg_type_: 1st node of the barre
            :@param end_type_: 1st node of the barre
            :@type beg_type_: String
            :@type end_type_: String
            :@default beg_type_: FIXED (for frame element)
            :@default end_type_: FIXED (for frame element)
            :@other beg_type_: Pined (Truss element); LINTEL (Lintel element)
            :@other end_type_: Pined (Truss element); LINTEL (Lintel element)
        """
        
        l = self.__Length  # noqa: E741
        # Coefficient
        if self.__Material is None and self.__Cross_section is None:
            eal = 1 * 1 / l
            ei = 1 * 1
        else:
            eal = self.__Material.E * self.__Cross_section.Area / l
            ei = self.__Material.E * self.__Cross_section.Inertia_y
        
        # Matrix definition 
        if beg_type == "FIXED" and end_type == "FIXED":
            self.__k_local: 'Array float' = np.array([  # noqa: F722
                [eal, 0, 0, -eal, 0, 0], 
                [0, 12 * ei / (l**3), 6 * ei / (l**2), 0, -12 * ei / (l**3), 6 * ei / (l**2)],  # noqa: E501
                [0, 6 * ei / (l**2), 4 * ei / l, 0, -6 * ei / (l**2), 2 * ei / l],  # noqa: E501
                [-eal, 0, 0, eal, 0, 0],
                [0, -12 * ei / (l**3), -6 * ei / (l**2), 0, 12 * ei / (l**3), -6 * ei / (l**2)],  # noqa: E501
                [0, 6 * ei / (l**2), 2 * ei / l, 0, -6 * ei / (l**2), 4 * ei / l]], dtype=float)  # noqa: E501
        elif beg_type == "PINED" and end_type == "FIXED":  # Need a vérification # noqa: E501
            self.__k_local: 'Array float' = np.array([   # noqa: F722
                [eal, 0, 0, -eal, 0, 0],
                [0, 3 * ei / (l**3), 0, 0, -3 * ei / (l**3), 3 * ei / (l**2)],  # noqa: E501
                [0, 0, 0, 0, 0, 0],
                [-eal, 0, 0, eal, 0, 0],
                [0, -3 * ei / (l**3), 0, 0, 3 * ei / (l**3), -3 * ei / (l**2)],  # noqa: E501 
                [0, 3 * ei / (l**2), 0, 0, -3 * ei / (l**2), 3 * ei / l]], dtype=float)  # noqa: E501

        elif beg_type == "FIXED" and end_type == "PINED":  # Need a vérification # noqa: E501
            self.__k_local: 'Array float' = np.array([  # noqa: F722
                [eal, 0, 0, -eal, 0, 0],
                [0, 3 * ei / (l**3), 3 * ei / (l**2), 0, -3 * ei / (l**3), 0],  # noqa: E501
                [0, 3 * ei / (l**2), 3 * ei / l, 0, -3 * ei / (l**2), 0],  # noqa: E501
                [-eal, 0, 0, eal, 0, 0],
                [0, -3 * ei / (l**3), -3 * ei / (l**2), 0, 3 * ei / (l**3), 0],  # noqa: E501
                [0, 0, 0, 0, 0, 0]], dtype=float)
        elif beg_type == "PINED" and end_type == "PINED":
            self.__k_local: 'Array float' = np.array([  # noqa: F722
                [eal, 0, 0, -eal, 0, 0],
                [0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0],
                [-eal, 0, 0, eal, 0, 0],
                [0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0]], dtype=float)
        
        elif beg_type == "LINTEL" and end_type == "LINTEL":  # Need a vérification - HB IGH # noqa: F722, E501
            """self.__k_local: 'Array float' = np.array([
                [0, 0, 0, 0, 0, 0]
                [0, 3, 3 * (b1 + a), 0, -3, 3 * (b2 + a)]
                [0, 3 * (b1 + a), 3 * b1**2 + 6 * a * b1 + 4 * a**2, 0, -3 * (b1 + a), 3 * (b1 + a) * (b2 + a) - a**2]  # noqa: E501
                [0, 0, 0, 0, 0, 0]
                [0, -3, -3 * (b1 + a), 0, 3, 3 * (b2 + a)]
                [0, 3 * (b2 + a), 3 * (b1 + a) * (b2 + a) - a**2, 0, 3 * (b2 + a), 3 * b2**2 + 6 * a * b2 + 4 * a**2]], dtype=float)"""  # noqa: E501
            raise NotImplementedError
        
        self.__K_barre: 'Array float' = self.__define_k_barre_mat()  # noqa: F722, E501

    def __define_k_barre_mat(self) -> 'Array float':  # noqa: F722
        """ Function to define local stiffness matrix to all element
            in global axes
        """
        rot_t: 'Array float' = np.transpose(self.__Rot_mat)  # noqa: F722
        return np.matmul(
                    np.matmul(rot_t, self.__k_local),
                    self.__Rot_mat)
    
    def uniforme_load(self, fx: float, fy: float,
                      mz: float, kind: str = "GLOBAL",
                      angle: float = 0) -> None:
        """ Function to define uniforme load on the barre
            Only Load fy without angle
        
            fx, fy, mz are global value

            :@param fx: uniforme fx
            :@param fy: uniforme fy
            :@param mz: uniforme mz
            :@param kind: 
                GLOBAL: Force under global axes
                LOCAL: Force under local axes
            :@param angle: Load angle in the global axes 
            :@type fx: float
            :@type fy: float
            :@type mz: float
        """
        l: float = self.__Length   

        # angle_barre_rad: float = math.radians(self.__Angle)
        # cos_barre: float = math.cos(angle_barre_rad)
        # sin_barre: float = math.sin(angle_barre_rad)
        
        self.__Fx: bool = True if fx != 0 else False
        self.__Fy: bool = True if fy != 0 else False
        self.__Mz: bool = True if mz != 0 else False
        
        self.__Fx_force: float = fx
        self.__Fy_force: float = fy 
        self.__Mz_force: float = mz
        self.__Kind_force: str = kind
        self.__Angle_force: float = angle
        
        # Fx Not implemented Yet
        
        # Fy
        if kind.upper() == "GLOBAL": 
            # angle_force_rad = math.radians(angle)
            # cos_force = math.cos(angle_force_rad_)
            # sin_force = math.sin(angle_force_rad_)
            
            self.__Fy_x_beg: float = 0  # fy * l_/2 * sin_barre * sin_force
            self.__Fy_y_beg: float = fy * l / 2  # * cos_barre * cos_force
            self.__Fy_m_beg: float = fy * l * l / 12  # * cos_barre * cos_force
            
            self.__Fy_x_end: float = 0  # -fy * l_/2  * sin_barre * sin_force
            self.__Fy_y_end: float = fy * l / 2  # * cos_barre * cos_force_
            self.__Fy_m_end: float = -fy * l * l / 12  # * cos_barre * cos_force # noqa: E501

        elif kind.upper() == "LOCAL":
            self.__Fy_x_beg: float = fy * l / 2
            self.__Fy_y_beg: float = fy * l / 2
            self.__Fy_m_beg: float = fy * l * l / 12

            self.__Fy_x_end: float = 0
            self.__Fy_y_end: float = fy * l / 2
            self.__Fy_m_end: float = -fy * l * l / 12

        # mz Not implemented Yet

    def temperature(self, dT_x: float, dT_m: float, **kwargs: dict) -> None:
        """ Function to define uniforme load on the barre

            :@param dT_x: thermal load in X axis
            :@param dT_m: thermal load in Z axis
            :@param kwargs: way to bypass value
            :@type dT_x: float
            :@type dT_m: float
            :@type kwargs: dict
        """

        self.__dT_x: bool = True if dT_x != 0 else False
        self.__dT_m: bool = True if dT_m != 0 else False
        
        self.__dT_force_x: float = dT_x
        self.__dT_force_m: float = dT_m

        if self.__Material is None and \
           self.__Cross_section is None and not (kwargs.items()):
            E: int = 1
            Iy: int = 1
            alpha: int = 1
            h: int = 1
            A: int = 1
        elif kwargs.items():
            for key, value in kwargs.items():
                if key.upper() == "E":
                    E: float = value
                elif key.upper() == "IY":
                    Iy: float = value
                elif key.upper() == "ALPHA":
                    alpha: float = value
                elif key.upper() == "H":
                    h: float = value
                elif key.upper() == "A":
                    A: float = value
        else:
            E: float = self.__Material.E
            Iy: float = self.__Cross_section.Inertia_y
            A: float = self.__Cross_section.Area
            alpha: float = self.__Material.Alpha
            h: float = self.__Cross_section.H
            
        self.__dT_x_beg: float = E * A * alpha * dT_x / self.__Length
        self.__dT_y_beg: float = 0
        self.__dT_m_beg: float = E * Iy * alpha * dT_m / h
        
        self.__dT_x_end: float = -E * A * alpha * dT_x
        self.__dT_y_end: float = 0
        self.__dT_m_end: float = -E * Iy * alpha * dT_m / h

    def prestress_load(self, equation: str, kind: str = "RIVE",
                       coef: float = [], 
                       prestress_value: float = 1) -> None:  # To do
        """ Function to define prestress_load on the barre

            We considere that the equation is 2 polynomials
            
            M is define as P.ep(x)

            :@param equation: ep(x) equation
            :@param kind: position of the beam
            :@param coef: coefficient of the second degree equation
            :@param prestress_value: value of the prestress
            :@type equation: string
            :@type kind: string
            :@type coef: List
            :@type prestress_value: float
            :@default equation:          
            :@default kind: RIVE (or INTER)
            :@default coef: table  
            :@default prestress_value: 1 (to considere in function of th prestress) # noqa: E501
        """

        self.__PC = True if prestress_value != 0 else False
        
        self.__PC_equation = equation
        self.__PC_value = prestress_value
        self.__PC_coef = coef
        self.__PC_kind = kind
        
        x_beg_ = self.__P_beg.X
        y_beg_ = self.__P_beg.Y

        x_end_ = self.__P_end.X
        y_end_ = self.__P_end.Y
        
        print(x_beg_," ", y_beg_)
        print(x_end_," ", y_end_)

        Length_ = math.sqrt((x_end_ - x_beg_)**2 + (y_end_ - y_beg_)**2)

        if type(equation) == float or type(equation) == int:
            self.__PC_x_beg = -prestress_value
            self.__PC_y_beg = 0
            self.__PC_m_beg = prestress_value * equation

            self.__PC_x_end = -prestress_value
            self.__PC_y_end = 0
            self.__PC_m_end = -prestress_value * equation
  
        else: 
            if kind == "RIVE":
                L_alpha_L = coef[0]  # (1-alpha)*L
                # alpha_L = coef[1]
                
                X_beg = self.P_beg.X
                X_end = self.P_end.X
                
                if X_end > Length_:
                    X_beg -= self.__P_beg.X
                    X_end -= self.__P_beg.X
 
                if X_beg <= L_alpha_L:
                    a1 = equation[0][0]
                    b1 = equation[0][1]
                    c1 = equation[0][2]

                else:
                    a1 = equation[1][0]
                    b1 = equation[1][1]
                    c1 = equation[1][2]

                if X_end <= L_alpha_L:
                    a2 = equation[0][0]
                    b2 = equation[0][1]
                    c2 = equation[0][2]

                else:
                    a2 = equation[1][0]
                    b2 = equation[1][1]
                    c2 = equation[1][2]

                eq_beg = a1 * X_beg**2 + b1 * X_beg + c1
                eq_end = a2 * X_end**2 + b2 * X_end + c2
                
                # Beg
                # f_a_beg = eq_beg
                # f_p_a_beg = 2 * a1 * eq_beg + b1
  
                
                # y_0_beg = f_a_beg + f_p_a_beg * (0 - eq_beg)
                # y_1_beg = f_a_beg + f_p_a_beg * (1 - eq_beg)
                
                # y_1_beg = 
                
                # a_angle_beg = y_0_beg-y_1_beg
                # b_angle_beg = 0.001
                
                # angle_beg = math.atan(-a_angle_beg/b_angle_beg)
  
                # end
                # f_a_end = eq_end
                # f_p_a_end = 2 * a2 * eq_end + b2
                
                # y_0_end = f_a_end + f_p_a_end * (0 - eq_end)
                # y_1_end = f_a_end + f_p_a_end * (1 - eq_end)
                y_0_beg = eq_beg
                y_1_end = eq_end
                
                a_angle_end = y_1_end - y_0_beg
                b_angle_end = X_end - X_beg
                
                # angle_end = math.atan(-a_angle_end/b_angle_end)
                angle_ = math.atan(-a_angle_end/b_angle_end) 

            elif kind == "INTER":               
                beta_L = coef[0]  # (1-alpha)*L
                L_beta_gamma_L = coef[1]  # (1-beta-gamma)*L
                # gamma_L = coef[2]

                X_beg = self.P_beg.X
                X_end = self.P_end.X

                X_beg -= self.__P_beg.X
                X_end -= self.__P_beg.X    
            
                if X_beg <= beta_L:
                    a1 = equation[0][0]
                    b1 = equation[0][1]
                    c1 = equation[0][2]
                    
                elif X_beg <= (beta_L + L_beta_gamma_L):
                    a1 = equation[1][0]
                    b1 = equation[1][1]
                    c1 = equation[1][2]

                else:
                    a1 = equation[2][0]
                    b1 = equation[2][1]
                    c1 = equation[2][2]  

                if X_end <= beta_L:
                    a2 = equation[0][0]
                    b2 = equation[0][1]
                    c2 = equation[0][2]
                    
                elif X_end <= (beta_L + L_beta_gamma_L):
                    a2 = equation[1][0]
                    b2 = equation[1][1]
                    c2 = equation[1][2]

                else:
                    a2 = equation[2][0]
                    b2 = equation[2][1]
                    c2 = equation[2][2]   

                eq_beg = a1 * X_beg**2 + b1 * X_beg + c1
                eq_end = a2 * X_end**2 + b2 * X_end + c2
                
                # Beg
                # f_a_beg = eq_beg
                # f_p_a_beg = 2 * a1 * eq_beg + b1
                
                # y_0_beg = f_a_beg + f_p_a_beg * (0 - eq_beg)
                # y_1_beg = f_a_beg + f_p_a_beg * (1 - eq_beg)
                
                # a_angle_beg = y_0_beg-y_1_beg
                # b_angle_beg = 0.001
                
                # angle_beg = math.atan(-a_angle_beg / b_angle_beg)

                #end
                # f_a_end = eq_end
                # f_p_a_end = 2 * a2 * eq_end + b2
                
                # y_0_end = f_a_end + f_p_a_end * (0 - eq_end)
                # y_1_end = f_a_end + f_p_a_end * (1 - eq_end)
                
                # a_angle_end = y_0_end - y_1_end
                # b_angle_end = 0.001
                
                # angle_end = math.atan(-a_angle_end / b_angle_end)
                y_0_beg = eq_beg
                y_1_end = eq_end
                
                a_angle_end = y_1_end - y_0_beg
                b_angle_end = X_end - X_beg
                
                # angle_end = math.atan(-a_angle_end/b_angle_end)
                angle_ = math.atan(-a_angle_end/b_angle_end) 


            self.__PC_x_beg = -prestress_value
            self.__PC_y_beg = 0
            self.__PC_m_beg = prestress_value * eq_beg * math.cos(angle_)#math.cos(angle_beg)

            self.__PC_x_end = -prestress_value
            self.__PC_y_end = 0
            self.__PC_m_end = -prestress_value * eq_end * math.cos(angle_) #math.cos(angle_end)  

# Special methode

    def __len__(self) -> float:
        """Get the length of the barre"""
        return self.__Length

    def __repr__(self) -> str:
        """ used when you print(Barre object) """
        if self.NB_BARRE == 1:
            return "It exist {} element ".format(self.NB_BARRE)
        else:
            return "It exist {} elements".format(self.NB_BARRE)
   
# Get
    @property
    def Length(self) -> float:
        """Barre Legnth"""
        return self.__Length

    @property
    def Angle(self) -> float:
        """Barre angle to a global scale"""
        return self.__Angle

    @property
    def Rot_mat(self) -> 'Array float':  # noqa: F722
        """Barre Rotation matrix"""
        return self.__Rot_mat

    @property
    def K_local(self) -> 'Array float':  # noqa: F722
        """Barre stifness matrix in local axes"""
        return self.__k_local

    @property
    def Name_p_beg(self) -> str:
        """Name of the point at the beginning of the barre"""
        return self.__P_beg.Name

    @property        
    def Name_p_end(self) -> str:
        """Name of the point at the ending of the barre"""
        return self.__P_end.Name

    @property
    def K_barre(self) -> 'Array float':  # noqa: F722
        """Barre stifness matrix in local axes"""
        return self.__K_barre

    @property
    def X_beg(self) -> float:
        """X coordinate of the beginning point"""
        return self.__P_beg.X

    @property
    def Y_beg(self) -> float:
        """Y coordinate of the beginning point"""
        return self.__P_beg.Y

    @property
    def X_end(self) -> float:
        """X coordinate of the ending point"""
        return self.__P_end.X

    @property
    def Y_end(self) -> float:
        """Y coordinate of the ending point"""
        return self.__P_end.Y

    @property
    def Pt_num_beg(self) -> float:
        """Number of the first point of the barre"""
        return self.__P_beg.Pt_num

    @property
    def Pt_num_end(self) -> float:
        """Number of the last point of the barre"""
        return self.__P_end.Pt_num

    @property
    def P_beg(self) -> 'Point':
        """Property of the fist point of the barre"""
        return self.__P_beg

    @property
    def P_end(self) -> 'Point':
        """Property of the last point of the barre"""
        return self.__P_end

    @property
    def P_beg_name(self) -> str:
        return self.__P_beg.Name

    @property
    def P_end_name(self) -> str:
        return self.__P_end.Name

    @property
    def P_num_beg(self) -> str:
        return self.__P_beg.Pt_num

    @property
    def P_num_end(self) -> str:
        return self.__P_end.Pt_num

    @property
    def Fx_x_beg(self) -> float:
        """Force in X in the first point du to Fx"""
        return self.__Fx_x_beg

    @property
    def Fx_y_beg(self) -> float:
        """Force in Y in the first point du to Fx"""
        return self.__Fx_y_beg

    @property
    def Fx_m_beg(self) -> float:
        """Moment in the first point du to Fx"""
        return self.__Fx_m_beg
        
    @property
    def Fx_x_end(self) -> float:
        """Force in X in the last point du to Fx"""
        return self.__Fx_x_end

    @property
    def Fx_y_end(self) -> float:
        """Force in Y in the last point du to Fx"""
        return self.__Fx_y_end

    @property
    def Fx_m_end(self) -> float:
        """Moment in the last point du to Fx"""
        return self.__Fx_m_end
    
    @property
    def Fy_x_beg(self) -> float:
        """Force in X in the first point du to Fy"""
        return self.__Fy_x_beg

    @property
    def Fy_y_beg(self) -> float:
        """Force in Y in the first point du to Fy"""
        return self.__Fy_y_beg

    @property
    def Fy_m_beg(self) -> float:
        """Moment in the first point du to Fy"""
        return self.__Fy_m_beg

    @property   
    def Fy_x_end(self) -> float:
        """Force in X in the last point du to Fy"""
        return self.__Fy_x_end

    @property
    def Fy_y_end(self) -> float:
        """Force in Y in the last point du to Fy"""
        return self.__Fy_y_end

    @property
    def Fy_m_end(self) -> float:
        """Moment in the last point du to Fy"""
        return self.__Fy_m_end

    @property   
    def Mz_x_beg(self) -> float:
        """Force in X in the first point du to Mz"""
        return self.__Mz_x_beg

    @property
    def Mz_y_beg(self) -> float:
        """Force in Y in the first point du to Mz"""
        return self.__Mz_y_beg

    @property
    def Mz_m_beg(self) -> float:
        """Moment in the first point du to Mz"""
        return self.__Mz_m_beg

    @property
    def Mz_x_end(self) -> float:
        """Force in X in the last point du to Mz"""
        return self.__Mz_x_end

    @property
    def Mz_y_end(self) -> float:
        """Force in Y in the last point du to Mz"""
        return self.__Mz_y_end

    @property
    def Mz_m_end(self) -> float:
        """Moment in the last point du to Mz"""
        return self.__Mz_m_end
        
    @property
    def dT_x_beg(self) -> float:
        """Force in X in the first point du to dT"""
        return self.__dT_x_beg

    @property
    def dT_y_beg(self) -> float:
        """Force in Y in the first point du to dT"""
        return self.__dT_y_beg

    @property
    def dT_m_beg(self) -> float:
        """Moment in the first point du to dT"""
        return self.__dT_m_beg
    
    @property
    def dT_x_end(self) -> float:
        """Force in X in the last point du to dT"""
        return self.__dT_x_end

    @property
    def dT_y_end(self) -> float:
        """Force in Y in the last point du to dT"""
        return self.__dT_y_end

    @property
    def dT_m_end(self) -> float:
        """Moment in the last point du to dT"""
        return self.__dT_m_end

    @property
    def PC_x_beg(self) -> float:
        """Force in X in the first point du to prestress"""
        return self.__PC_x_beg

    @property
    def PC_y_beg(self) -> float:
        """Force in Y in the first point du to prestress"""
        return self.__PC_y_beg

    @property
    def PC_m_beg(self) -> float:
        """Moment in the first point du to prestress"""
        return self.__PC_m_beg 
 
    @property
    def PC_x_end(self) -> float:
        """Force in X in the last point du to prestress"""
        return self.__PC_x_end

    @property
    def PC_y_end(self) -> float:
        """Force in Y in the last point du to prestress"""
        return self.__PC_y_end

    @property
    def PC_m_end(self) -> float:
        """Moment in the last point du to prestress"""
        return self.__PC_m_end

    @property
    def Fx(self) -> float:
        """Force in X"""
        return self.__Fx

    @property
    def Fy(self) -> float:
        """Force in Y"""
        return self.__Fy

    @property
    def Mz(self) -> float:
        """Bending moment"""
        return self.__Mz

    @property
    def dT_x(self) -> float:
        """Temperature load in X"""
        return self.__dT_x

    @property
    def dT_m(self) -> float:
        """Temperature load in M"""
        return self.__dT_m

    @property
    def PC(self) -> float:
        """Prestress load"""
        return self.__PC_value

# Set
    def section_property(self, val: 'Section') -> None:  # noqa: F722, F821
        self.__Cross_section = val  

    @P_beg.setter
    def P_beg(self, val: 'Point') -> None:  # noqa: F722
        self.__P_beg = val

    @P_end.setter
    def P_end(self, val: 'Point') -> None:  # noqa: F722
        self.__P_end = val

    @P_beg_name.setter
    def P_beg_name(self, val: 'Point') -> None:  # noqa: F722
        self.__P_beg.Name = val

    @P_end_name.setter
    def P_end_name(self, val: 'Point') -> None:  # noqa: F722
        self.__P_end.Name = val

    @P_num_beg.setter
    def P_num_beg(self, val: float) -> None:
        self.__P_beg.Pt_num = val

    @P_num_end.setter
    def P_num_end(self, val: float) -> None:
        self.__P_end.Pt_num = val
    
    @Fx_x_beg.setter
    def Fx_x_beg(self, val: float) -> None:
        self.__Fx_x_beg = val

    @Fx_y_beg.setter
    def Fx_y_beg(self, val: float) -> None:
        self.__Fx_y_beg = val

    @Fx_m_beg.setter
    def Fx_m_beg(self, val: float) -> None:
        self.__Fx_m_beg = val
        
    @Fx_x_end.setter
    def Fx_x_end(self, val: float) -> None:
        self.__Fx_x_end = val

    @Fx_y_end.setter
    def Fx_y_end(self, val: float) -> None:
        self.__Fx_y_end = val

    @Fx_m_end.setter
    def Fx_m_end(self, val: float) -> None:
        self.__Fx_m_end = val
        
    @Fy_x_beg.setter
    def Fy_x_beg(self, val: float) -> None:
        self.__Fy_x_beg = val

    @Fy_y_beg.setter
    def Fy_y_beg(self, val: float) -> None:
        self.__Fy_y_beg = val

    @Fy_m_beg.setter
    def Fy_m_beg(self, val: float) -> None:
        self.__Fy_m_beg = val
        
    @Fy_x_end.setter
    def Fy_x_end(self, val: float) -> None:
        self.__Fy_x_end = val

    @Fy_y_end.setter
    def Fy_y_end(self, val: float) -> None:
        self.__Fy_y_end = val

    @Fy_m_end.setter
    def Fy_m_end(self, val: float) -> None:
        self.__Fy_m_end = val
        
    @Fy_m_end.setter
    def Mz_x_beg(self, val: float) -> None:
        self.__Mz_x_beg = val

    @Fy_m_end.setter
    def Mz_y_beg(self, val: float) -> None:
        self.__Mz_y_beg = val

    @Fy_m_end.setter
    def Mz_m_beg(self, val: float) -> None:
        self.__Mz_m_beg = val
        
    @Mz_x_end.setter
    def Mz_x_end(self, val: float) -> None:
        self.__Mz_x_end = val

    @Mz_y_end.setter
    def Mz_y_end(self, val: float) -> None:
        self.__Mz_y_end = val
        
    @Mz_m_end.setter
    def Mz_m_end(self, val: float) -> None:
        self.__Mz_m_end = val
        
    @dT_x_beg.setter
    def dT_x_beg(self, val: float) -> None:
        self.__dT_x_beg = val

    @dT_y_beg.setter
    def dT_y_beg(self, val: float) -> None:
        self.__dT_y_beg = val

    @dT_m_beg.setter
    def dT_m_beg(self, val: float) -> None:
        self.__dT_m_beg = val

    @dT_x_end.setter
    def dT_x_end(self, val: float) -> None:
        self.__dT_x_end  = val

    @dT_y_end.setter
    def dT_y_end(self, val: float) -> None:
        self.__dT_y_end = val

    @dT_m_end.setter
    def dT_m_end(self, val: float) -> None:
        self.__dT_m_end = val
        
    @PC_x_beg.setter
    def PC_x_beg(self, val: float) -> None:
        self.__PC_x_beg  = val

    @PC_y_beg.setter
    def PC_y_beg(self, val: float) -> None:
        self.__PC_y_beg = val

    @PC_m_beg.setter
    def PC_m_beg(self, val: float) -> None:
        self.__PC_m_beg = val
 
    @PC_x_end.setter
    def PC_x_end(self, val: float) -> None:
        self.__PC_x_end  = val

    @PC_y_end.setter
    def PC_y_end(self, val: float) -> None:
        self.__PC_y_end = val

    @PC_m_end.setter
    def PC_m_end(self, val: float) -> None:
        self.__PC_m_end = val
    
 # Property
    
    Cross_section = property(None,section_property)


class Stiffness_methode:
    """
        Class to do calculation
        
        This class can be define a "symbolic class"
        it's mean that all calculation will be algerbric

        :@param __INTERVAL_POINT: 
        :@param SUM_EQ: 
        :@type __INTERVAL_POINT: integer
        :@type SUM_EQ: integer
        :@default __INTERVAL_POINT: 50 (Number of point between two node to make graphic)
        :@default SUM_EQ: 3 (Number of equation by node)
        
        Class variable:
        :@param __INTERVAL_POINT:
        :@param SUM_EQ:
        :@type __INTERVAL_POINT: integer
        :@type SUM_EQ: integer
        :@default __INTERVAL_POINT: 50 (Number of point between two node to make graphic) # noqa: E501
        :@default SUM_EQ: 3 (Number of equation by node)

        Instance variable:
        :@param support_tab:
        :@param d_tab:
        :@param force_tab:
        :@param connect_tab:
        :@param k_global:
        :@param unds_tab:

        :@type support_tab: numpy int
        :@type d_tab: numpy float ?
        :@type force_tab: numpy float
        :@type connect_tab: numpy int
        :@type k_global: numpy float
        :@type unds_tab: numpy float
        
    """
 # Attribute
    __INTERVAL_POINT = 50
    SUM_EQ = 3

    def __init__(self, barre_array: 'Array Barre', point_array: 'Array point', symbolic: bool = False) -> None:
        """ Constructor
            :@param barre_array: tuple of all barre
            :@param point_array: tuple of all point
            :@param symbolic: Choose if all calculation will be algerbric
            :@type barre_array: tuple
            :@type point_array: tuple
            :@type symbolic: bool
        """
        
        self.__Barre_tab: 'Array Barre' = barre_array
        self.__Point_tab: 'Array point' = point_array    
        
        # Lintel variable
        
        # self.__a = 0
        # self.__b = 0
        
        # Calculation
        self.routine_calculation()

    def routine_calculation(self) -> None:
        """ Function to make and remake all calculaion """
        
        # Define element
        start = timeit.default_timer()
        
        self.__Support_tab = self.__define_Support_tab()
        self.__D_tab = self.__define_D_tab()
        self.__Force_tab = self.__define_Force_tab()
        
        print("     Définition des éléments: " + str(timeit.default_timer()-start))
        
        # Define matrix         
        start = timeit.default_timer()
        self.__Connect_tab = self.__define_connection_table()
        print("     Définition des la tables des connexions: " + str(timeit.default_timer()-start))   
        start = timeit.default_timer()        
        self.__K_global = self.__define_global_stiffness_mat()
        print("     Définition de la mat global: " + str(timeit.default_timer()-start)) 
        # Calculation
        start = timeit.default_timer()
        self.k_d_wz_r = self.__mat_modif()
        
        print("     Modification de la matrice: " + str(timeit.default_timer()-start)) 
        
        start = timeit.default_timer()
        
        self.__Unds_tab = self.__calc_D_Rint()
        
        print("     Calcul des resultats: " + str(timeit.default_timer()-start)) 
        
        start = timeit.default_timer()
        
        self.__Delta_theta_str = self.__fill_point()
        
        print("     Ecriture des données dans points: " + str(timeit.default_timer()-start)) 
        start = timeit.default_timer()
        
        self.__NSM_effort = self.__interne_force()
        
        print("     Définition des forces internes: " + str(timeit.default_timer()-start)) 
        start = timeit.default_timer()
        
        self.__write_interal_force()
        
        print("     Ecriture des forces internes: " + str(timeit.default_timer()-start)) 

    def __define_Support_tab(self) -> 'Array float':
        """ Function to fill support matrix 
            support_tab  = [Rax, Ray, M]
            1 mean reaction existe
            0 mean reaction doesn't existe
        """
        point: int = Point.NB_POINT * self.SUM_EQ #  Number of point
        support_tab: 'Array float' = np.zeros(point)
        counter: int = 0

        for i in self.__Point_tab:
            support_tab[counter] = 1 if i.Rx_cond else 0
            support_tab[counter + 1] = 1 if i.Ry_cond else 0
            support_tab[counter + 2] = 1 if i.Mt_cond else 0
            counter += 3
        
        return support_tab

    def __define_D_tab(self) -> 'Array float':
        """ Function to fill displacement tab
            d_tab  = [dx, dy, theta]
            1 mean displacement existe
            0 mean displacement doesn't existe
        """
        point: int = Point.NB_POINT * self.SUM_EQ #  Number of point
        d_tab: 'Array float' = np.zeros(point) # 1, point)
    
        self.__Sum_int: int = 0 # sum of unknown reaction
        
        for i in range(0, point):
            if self.__Support_tab[i] == 1:
                d_tab[i] = 0
                self.__Sum_int += 1
            else:
                d_tab[i] = 1

        return d_tab

    def __define_Force_tab(self) -> 'Array float':
        """ Function to fill force tab
            Force_tab  = [Fx, Fy, Mt]
        """
        point: int = Point.NB_POINT * self.SUM_EQ #  Number of point
        force_tab: 'Array float' = np.zeros(point)#(1,point)
        counter: int = 0

        for i in self.__Point_tab:
            force_tab[counter] = i.Fx
            force_tab[counter + 1] = i.Fy
            force_tab[counter + 2] = i.Mz

            if Barre.NB_BARRE != 1:
                for ii in self.__Barre_tab:
                    if (ii.Fx or ii.Fy or ii.Mz or ii.dT_x or ii.dT_m or ii.PC):
                        if i.Name == ii.P_beg_name:
                            force_tab[counter] += ii.Fx_x_beg  \
                                                + ii.Fy_x_beg + ii.Mz_x_beg \
                                                + ii.dT_x_beg + ii.PC_x_beg
                            force_tab[counter + 1] += ii.Fx_y_beg \
                                                + ii.Fy_y_beg + ii.Mz_y_beg \
                                                + ii.dT_y_beg + ii.PC_y_beg
                            force_tab[counter + 2] += ii.Fx_m_beg \
                                                + ii.Fy_m_beg + ii.Mz_m_beg \
                                                + ii.dT_m_beg + ii.PC_m_beg
                        elif i.Name == ii.P_end_name:
                            force_tab[counter] += ii.Fx_x_end \
                                                + ii.Fy_x_end + ii.Mz_x_end \
                                                + ii.dT_x_end + ii.PC_x_end
                            force_tab[counter + 1] += ii.Fx_y_end \
                                                + ii.Fy_y_end + ii.Mz_y_end \
                                                + ii.dT_y_end + ii.PC_y_end
                            force_tab[counter + 2] += ii.Fx_m_end \
                                                + ii.Fy_m_end + ii.Mz_m_end \
                                                + ii.dT_m_end + ii.PC_m_end
            else:
                ii = self.__Barre_tab
                if (ii.Fx or ii.Fy or ii.Mz or ii.dT_x or ii.dT_m or ii.PC):
                    if i.Name == ii.P_beg_name:
                        force_tab[counter] += ii.Fx_x_beg  \
                                            + ii.Fy_x_beg + ii.Mz_x_beg \
                                            + ii.dT_x_beg + ii.PC_x_beg
                        force_tab[counter + 1] += ii.Fx_y_beg \
                                            + ii.Fy_y_beg + ii.Mz_y_beg \
                                            + ii.dT_y_beg + ii.PC_y_beg
                        force_tab[counter + 2] += ii.Fx_m_beg \
                                            + ii.Fy_m_beg + ii.Mz_m_beg \
                                            +  ii.dT_m_beg + ii.PC_m_beg
                    elif i.Name == ii.P_end_name:
                        force_tab[counter] += ii.Fx_x_end \
                                            + ii.Fy_x_end + ii.Mz_x_end \
                                            + ii.dT_x_end + ii.PC_x_end
                        force_tab[counter + 1] += ii.Fx_y_end \
                                            + ii.Fy_y_end + ii.Mz_y_end \
                                            + ii.dT_y_end + ii.PC_y_end
                        force_tab[counter + 2] += ii.Fx_m_end \
                                            + ii.Fy_m_end + ii.Mz_m_end \
                                            + ii.dT_m_end + ii.PC_m_end
            counter += 3
        return force_tab

    def __define_connection_table(self) -> 'Array float':
        """ Function the connection table
        
            The connection table to create stiffness matrix
            
            pt_1(0,0); pt_2(0,1); pt_3(1,1); pt_4(1,0)
            b1(pt_1,pt_2); b2(pt_2,pt_3); b3(pt_3,pt_4)
            
                pt_1 | pt_2 | pt_3 | pt_4 |
            b1 |  x  |   x  |   -  |   -  |
            b2 |  -  |   x  |   x  |   -  |
            b3 |  -  |   -  |   x  |   x  |
        """
        row: int = 0 # row counter to establish connection tab
        Connect_tab: 'Array int' = np.zeros((Barre.NB_BARRE, len(self.__Point_tab)))
        if Barre.NB_BARRE != 1:
            for barre in self.__Barre_tab:
                col: int = 0 # col counter to establish connection tab
                for point in self.__Point_tab:
                    if barre.P_beg.Name == point.Name or barre.P_end.Name == point.Name:
                        Connect_tab[row, col] = 1 
                    else:
                        Connect_tab[row, col] = 0
                    col += 1
                row += 1
        else:
            col = 0
            barre = self.__Barre_tab
            for point in self.__Point_tab:
                if barre.P_beg.Name == point.Name or barre.P_end.Name == point.Name:
                    Connect_tab[row, col] = 1
                else:
                    Connect_tab[row, col] = 0
                col += 1
            row += 1
        return Connect_tab   

    def __define_global_stiffness_mat(self) -> 'Array float':
        """ Function to mix the global stifness matrix """
        point: int = Point.NB_POINT * self.SUM_EQ #  Number of point
        K_global: 'Array float' = np.zeros((point, point), dtype=float)
        passage: 'Array float' = np.zeros(Barre.NB_BARRE)
                
        for i in range(0, Point.NB_POINT * 3, 3):
            for ii in range(0, Point.NB_POINT * 3, 3):
                for iii in range(0, Barre.NB_BARRE):
                    if Barre.NB_BARRE != 1:
                        my_tab: 'Array float' = self.__Barre_tab[iii].K_barre
                    else:
                        my_tab: 'Array float' = self.__Barre_tab.K_barre
                
                    if self.__Connect_tab[iii, int(i / 3)] != 0 and self.__Connect_tab[iii, int(ii / 3)] != 0:
                        if i == 0 and ii == 0: # k11
                            for j in range(i, i + 3):
                                for jj in range(ii, ii + 3):
                                    K_global[j, jj] += self.__Connect_tab[iii, int(ii / 3)] * self.__Connect_tab[iii, int(i / 3)] * my_tab[j - i , jj - ii]
                            passage[iii] = 1
                        elif i == ii: # k11 + k22
                            if passage[iii] == 1:
                                for j in range(i, i + 3):
                                    for jj in range(ii, ii + 3):
                                        K_global[j, jj] += self.__Connect_tab[iii, int(ii / 3)] * self.__Connect_tab[iii, int(i / 3)] * my_tab[j - i  + 3, jj - ii  + 3]
                            else:
                                for j in range(i, i + 3):
                                    for jj in range(ii, ii + 3):
                                        K_global[j, jj] += self.__Connect_tab[iii, int(i / 3)] * self.__Connect_tab[iii, int(i / 3)] * my_tab[j - i , jj - ii ]
                                passage[iii] = 1
                        elif i + 3 == ii: # k12
                            for j in range(i, i + 3):
                                for jj in range(ii, ii + 3):
                                    K_global[j, jj] += + self.__Connect_tab[iii, int(ii / 3)] * self.__Connect_tab[iii, int(i / 3)] * my_tab[j - i , jj - ii + 3 ]
                        elif i == ii + 3: # k21 
                            for j in range(i, i + 3):
                                for jj in range(ii, ii + 3):
                                    K_global[j, jj] += self.__Connect_tab[iii, int(ii / 3)] * self.__Connect_tab[iii, int(i / 3)] * my_tab[j - i + 3 , jj - ii ] 
        return K_global
   
    def __mat_modif(self) -> 'Array float':
        """ Multiply k_global by D_tab
            Removing zero form D_tab
        """

        point: int = Point.NB_POINT * self.SUM_EQ #  Number of point
        kxd: 'Array float' = np.zeros((point, point) ,dtype=float)
        k_d_wz: 'Array float' = np.zeros((point, point), dtype=float)
        b = 0
        passage = False
        
        for i in range(0,point): # Row
            a = 0
            for ii in range(0,point): # Col
                kxd[ii,i] = self.__K_global[i, ii] * self.__D_tab[i]              
                if self.__D_tab[i] != 0:
                    k_d_wz[a, b] = kxd[ii,i]
                    a += 1
                    passage = True
            if passage:
                b += 1
                passage = False
        
        k_d_wz_r = k_d_wz
        
        
        a = point - 1
        
        for i in range(point - 1, -1, -1):
            if self.__Support_tab[i] != 0:
                for ii in range(point - 1, -1, -1):
                    if ii == i:
                        k_d_wz_r[ii, a] = -1
                a -= 1
        return k_d_wz_r

    def __calc_D_Rint(self) -> 'Array float':
        """ Calculate the matrix of displacement
            and support reaction
            
            Support reaction will alway be at the end_type_
            [dx, dy, rx, ry]
        """
        point: int = Point.NB_POINT * self.SUM_EQ #  Number of point
        Unds_tab: 'Array float' = np.zeros(point)
        
        start = timeit.default_timer()
        
        mat_inverse: 'Array float' = np.linalg.inv(self.k_d_wz_r) # Matrix inversion
        print("         Inversion de la matrice de rigidité: " + str(timeit.default_timer()-start))
        
        Unds_tab =  np.matmul(mat_inverse, self.__Force_tab)
        return Unds_tab
        
    def __fill_point(self) -> 'Array float':
        """ fill reaction in point
            fill displacement in point
        """
        point: int = Point.NB_POINT * self.SUM_EQ #  Number of point
        Delta_theta_str: 'Array float' = np.zeros(point) 
        a: int = 0
        b: int = 0
        
        for i in range(0, point):
            if self.__Support_tab[i] == 1:
                if i%3 == 0:
                    self.__Point_tab[int(i / 3)].Rx = self.__Unds_tab[point - self.__Sum_int + a]
                elif i%3 == 1:
                    self.__Point_tab[int((i - 1) / 3)].Ry = self.__Unds_tab[point - self.__Sum_int + a]
                elif i%3 == 2:
                    self.__Point_tab[int((i - 2) / 3)].Mt = self.__Unds_tab[point - self.__Sum_int + a]
                a += 1
      
            if self.__D_tab[i] == 1:
                if i%3 == 0:
                    self.__Point_tab[int(i / 3)].Delta_x = self.__Unds_tab[b]
                elif i%3 == 1:
                    self.__Point_tab[int((i - 1) / 3)].Delta_y = self.__Unds_tab[b]
                elif i%3 == 2:
                    self.__Point_tab[int((i - 1) / 3)].Theta = self.__Unds_tab[b]
                Delta_theta_str[i] = self.__Unds_tab[b]
                b += 1
            else:
                if i%3 == 0:
                    self.__Point_tab[int(i/3)].Delta_x = 0
                elif i%3 == 1:
                    self.__Point_tab[int((i-1)/3)].Delta_y = 0
                elif i%3 == 2:
                    self.__Point_tab[int((i-2)/3)].Theta = 0
                Delta_theta_str[i] = 0
        return Delta_theta_str

    def __interne_force(self) -> 'Array float':
        """ calculate internal force 
            fill in odered fonction of node
        """
        
        point: int = Point.NB_POINT * self.SUM_EQ #  Number of point
        tmp_delta: 'Array float' = np.zeros(self.SUM_EQ * 2)
       
        NSM_effort: 'Array float' = np.zeros(point)
        
        if Barre.NB_BARRE != 1:
            for i in self.__Barre_tab:
                for ii in range(0,3):

                    tmp_delta[ii] = self.__Delta_theta_str[i.P_num_beg * 3 + ii - 3]
                    tmp_delta[ii + 3] = self.__Delta_theta_str[i.P_num_end * 3 + ii - 3]
                
                tmp: 'Array float' = np.matmul(i.K_local, i.Rot_mat)
                NSM_tmp = np.matmul(tmp, tmp_delta)
                
                for ii in range(0,3):
                    if ii == 0: # Fx
                        add_beg: float = i.Fx_x_beg + i.Fy_x_beg + i.Mz_x_beg + i.dT_x_beg + i.PC_x_beg  
                        add_end: float = i.Fx_x_end + i.Fy_x_end + i.Mz_x_end + i.dT_x_end + i.PC_x_end                       
                    elif ii == 1: # Fy
                        add_beg: float = i.Fx_y_beg + i.Fy_y_beg + i.Mz_y_beg + i.dT_y_beg + i.PC_y_beg    
                        add_end: float = i.Fx_y_end + i.Fy_y_end + i.Mz_y_end + i.dT_y_end + i.PC_y_end
                    elif ii == 2: # Mz
                        add_beg: float = i.Fx_m_beg + i.Fy_m_beg + i.Mz_m_beg + i.dT_m_beg + i.PC_m_beg     
                        add_end: float = i.Fx_m_end + i.Fy_m_end + i.Mz_m_end + i.dT_m_end + i.PC_m_end 
                    NSM_effort[i.P_num_beg * 3 + ii - 3] = NSM_tmp[ii]  - add_beg
                    NSM_effort[i.P_num_end * 3 + ii - 3] = -NSM_tmp[ii+3]  + add_end
        else:
            i: 'Array float' = self.__Barre_tab
            for ii in range(0,3):

                tmp_delta[ii] = self.__Delta_theta_str[i.P_num_beg * 3 + ii - 3] 
                tmp_delta[ii + 3] = self.__Delta_theta_str[i.P_num_end * 3 + ii - 3] 

            tmp: 'Array float' = np.matmul(i.K_local, i.Rot_mat)
            NSM_tmp = np.matmul(tmp, tmp_delta)
            
            for ii in range(0,3):
                if ii == 0: # Fx
                    add_beg = i.Fx_x_beg + i.Fy_x_beg + i.Mz_x_beg + i.dT_x_beg + i.PC_x_beg  
                    add_end = i.Fx_x_end + i.Fy_x_end + i.Mz_x_end + i.dT_x_end + i.PC_x_end                       
                elif ii == 1: # Fy
                    add_beg = i.Fx_y_beg + i.Fy_y_beg + i.Mz_y_beg + i.dT_y_beg + i.PC_y_beg    
                    add_end = i.Fx_y_end + i.Fy_y_end + i.Mz_y_end + i.dT_y_end + i.PC_y_end
                elif ii == 2: # Mz
                    add_beg = i.Fx_m_beg + i.Fy_m_beg + i.Mz_m_beg + i.dT_m_beg + i.PC_m_beg     
                    add_end = i.Fx_m_end + i.Fy_m_end + i.Mz_m_end + i.dT_m_end + i.PC_m_end 

                NSM_effort[i.P_num_beg * 3 + ii - 3] = NSM_tmp[1, ii] - add_beg
                NSM_effort[i.P_num_end * 3 + ii - 3] = NSM_tmp[1, ii + 3] + add_end
        return NSM_effort
             
    def __write_interal_force(self) -> None:
        """ fill force in point """
        
        ii: int = 0
        
        for i in self.__Point_tab:
            i.define_internal_force(self.__NSM_effort[ii], self.__NSM_effort[ii+1],self.__NSM_effort[ii+2])
            ii += 3
            
    @classmethod
    def test_iso(cls, point_array: 'Array float') -> None:
        """
            Function to know the hyperstaticity of the structure
            @parma point_array: List of all point
            @type point_array: tuple
            
            @param return: Hypostatic; Isostatique; Hyperstatic
            @type return: String
        """
        counter: int = 0
        for pt in point_array:
            counter += pt.Hyper_degree
        if counter - 3 < 0:
            return "Hypostatic"
        elif counter - 3 == 0:
            return "Isostatique"
        else:
            return "Hyperstatic"
# Get
    @property
    def K_global(self) -> 'Array float':
        return self.__K_global
    @property
    def Interval_point(self) -> int:
        return self.__INTERVAL_POINT
    @property
    def Sum_eq(self) -> int:
        return self.SUM_EQ
    @property
    def Support_tab(self) -> 'Array float':
        return self.__Support_tab
    @property
    def D_tab(self):
        return self.__D_tab
    @property
    def Force_tab(self) -> 'Array float':
        return self.__Force_tab
    @property
    def Unds_tab(self) -> 'Array float':
        return self.__Unds_tab
    @property
    def a(self) -> 'Unknown':
        return self.__a 
    @property
    def b(self) -> 'Unknown':
        return self.__b
    @property
    def Connect_tab(self) -> 'Array float':
        return self.__Connect_tab


# Set
    @Interval_point.setter
    def Interval_point(self, val: int) -> None:
        self.__INTERVAL_POINT = val
    @Sum_eq.setter
    def Sum_eq(self, val: float) -> None:
        self.SUM_EQ = val
    @a.setter
    def a(self, var: 'Unknown') -> None:
        self.__a = var
    @b.setter
    def b(self, var: 'Unknown') -> None:
        self.__b = var
    def Point(self, var: 'Array float') -> None:
        self.__Point_tab = var
    def Barre(self, var: 'Array float') -> None:
        self.__Barre_tab = var
    

 # Property
    Point = property(None, Point)
    Barre = property(None, Barre)
    

class Split:
    """
        this class is for splitting the barre
    """

    def __init__(self, P_beg: 'Point', P_end: 'Point', Barre: 'Barre', step: int, \
                point_all: 'Point', barre_all: 'Barre') -> None:
        """
           Constructor
           
            :@type P_beg: 
        """
        self.__Step: float = step
        self.__Point: 'Point' = []
        self.__Barre: 'Barre' = []
        
        self.__Point_all: 'Point' = point_all
        self.__Barre_all: 'Point' = barre_all
        
        self.__Barre_lmt: 'Barre' = Barre
        
        self.__Pt_beg: 'Point' = P_beg
        self.__Pt_end: 'Point' = P_end
        
        self.__Pt_beg_Name: str = P_beg.Name
        self.__Pt_end_Name: str = P_end.Name
        
        self.__Pt_X_beg: float = P_beg.X
        self.__Pt_X_end: float = P_end.X

        self.__Pt_Y_beg: float = P_beg.Y
        self.__Pt_Y_end: float = P_end.Y
        
        start = timeit.default_timer()
        self.__devide_point()
        print("     Division des points: " + str(timeit.default_timer()-start))
        start = timeit.default_timer()

        self.__devide_barre()

        print("     Division des barres: " + str(timeit.default_timer()-start))
        start = timeit.default_timer()

        self.__rename_elmt()

        print("     Renumerotation: " + str(timeit.default_timer()-start))
        print("\n")
    
    def __devide_point(self) -> None:
        """
            function
        """
        if self.__Pt_Y_beg == 0 and self.__Pt_Y_end == 0:
            
            counter: int = 0
            Length: float = abs(self.__Pt_X_beg - self.__Pt_X_end)
            step_tab: 'Array float' = np.arange(0.0, (Length + Length / self.__Step), Length / self.__Step)
            step_name: float = Length * Length / self.__Step
            Name: str = self.__Pt_beg_Name + self.__Pt_end_Name
            
            value_name: float = step_name

            for i in step_tab:
                if i != 0 and i != Length:
                    point = Point(self.__Pt_X_beg + i, 0, Name + " " + str(value_name))
                    self.__Point.append(point)
                    value_name += step_name
                elif i == 0:
                    self.__Point.append(self.__Pt_beg)
                elif i == Length:
                    self.__Point.append(self.__Pt_end)  
                counter += 1

    def __devide_barre(self) -> None:
        """
            Function
        """
        if self.__Pt_Y_beg == 0 and self.__Pt_Y_end == 0:
            
            Length_tmp: float = abs(self.__Pt_X_beg - self.__Pt_X_end)
            step_tab = np.arange(0.0, (Length_tmp + Length_tmp / self.__Step), Length_tmp / self.__Step)
            
            length = len(self.__Point)
            
            counter = 0

            for i in range(0, length - 1):
                tmp_barre = copy.copy(self.__Barre_lmt)

                self.__Barre.append(tmp_barre)
                self.__Barre[counter].P_beg = self.__Point[i]
                self.__Barre[counter].P_end = self.__Point[i + 1]
                self.__Barre[counter].define_property()  
                self.__Barre[counter].redefine_force()
 
                counter += 1
            Barre.NB_BARRE +=  counter - 1         

    def __rename_elmt(self) -> None:
        Barre_tmp = []
        Point_tmp = []
        try:
            Length = len(self.__Barre_all)
        except:
            Length = 1
        passage = False
        counter = 0

        if Length != 1:
            for i in range(0, Length):
                if self.__Barre_all[i] == self.__Barre_lmt:
                    for ii in self.__Barre:
                        if counter == 0:
                            if i == 0:
                                self.__Point[0].Pt_num = 1
                                self.__Point[1].Pt_num = 2
                                
                                Point_tmp.append(self.__Point[0])
                                Point_tmp.append(self.__Point[1])
                                
                                ii.P_num_beg = 1
                                ii.P_num_end = 2
                                Barre_tmp.append(ii)
                            else:
                                P_beg_num = self.__Barre_all[i].P_num_beg                           
                                P_end_num = P_beg_num + 1
                                self.__Point[counter+1].Pt_num = P_end_num
                                
                                Point_tmp.append(self.__Point[counter+1])
                                
                                ii.P_num_end = P_end_num
                                Barre_tmp.append(ii)
                        else:
                            P_beg_num = Barre_tmp[i + counter - 1].P_num_end
                            P_end_num = P_beg_num + 1
                            
                            self.__Point[counter + 2 - 1].Pt_num = P_end_num
                            
                            Point_tmp.append(self.__Point[counter + 2 - 1])
                            
                            ii.P_num_beg = P_beg_num                        
                            ii.P_num_end = P_end_num
                            Barre_tmp.append(ii)
                        
                        counter += 1
                    passage = True
                
                elif passage == True:
                    P_beg_num = Barre_tmp[i+counter - 1 - 1].P_num_end
                    P_end_num = P_beg_num + 1


                    self.__Barre_all[i].P_num_beg = P_beg_num                        
                    self.__Barre_all[i].P_num_end = P_end_num
                         
                    self.__Barre_all[i].P_end.Pt_num = P_end_num
                    
                    Point_tmp.append(self.__Barre_all[i].P_end)
                            
                    Barre_tmp.append(self.__Barre_all[i])

                elif passage == False:
                    if i == 0:
                        Point_tmp.append(self.__Barre_all[i].P_beg)
                        Point_tmp.append(self.__Barre_all[i].P_end)
                        Barre_tmp.append(self.__Barre_all[i])
                    else:
                        Point_tmp.append(self.__Barre_all[i].P_end)
                        Barre_tmp.append(self.__Barre_all[i])
        else:
            for ii in self.__Barre:
                if counter == 0:
                    self.__Point[0].Pt_num = 1
                    self.__Point[1].Pt_num = 2
                    
                    Point_tmp.append(self.__Point[0])
                    Point_tmp.append(self.__Point[1])
                    
                    ii.P_num_beg = 1
                    ii.P_num_end = 2
                    Barre_tmp.append(ii)
                else:
                    P_beg_num = Barre_tmp[counter - 1].P_num_end
                    P_end_num = P_beg_num + 1
                    
                    self.__Point[counter + 2 - 1].Pt_num = P_end_num
                    
                    Point_tmp.append(self.__Point[counter + 2 - 1])
                    
                    ii.P_num_beg = P_beg_num                        
                    ii.P_num_end = P_end_num
                    Barre_tmp.append(ii)
                
                counter += 1
        
        self.__Barre = Barre_tmp
        self.__Point = Point_tmp
# Get

    @property
    def Point(self) -> 'Point':
        """ """
        return self.__Point

    @property
    def Barre(self) -> 'Point':
        """ """
        return self.__Barre

if __name__ == "__main__":    

# prestress_load(self, equation: str, kind: str = "RIVE",
#                       coef: float = [], 
#                       prestress_value: float = 1
    
    P1 = Point(0,0)
    P2 = Point(25,0)
    P3 = Point(50,0)  
     
    P1.define_support_condition(True,True, False) 
    P2.define_support_condition(True, True, False) 
    P3.define_support_condition(True,True, False)

    B1 = Barre(P1, P2)
    B2 = Barre(P2, P3)

    eq1 = [[0.000368, -0.018400, 0.350000],[0, 0, 0]]
    
    B1.uniforme_load(0,-10,0)
    B2.uniforme_load(0,-10,0)
    #B1.prestress_load(eq1, "RIVE", [25])
    #B1.prestress_load(eq1, "RIVE", [25])

    point = (P1, P2, P3)
    barre = (B1, B2)

    nb_devid = 100     

    my_eltm = Split(P1, P2, B1, nb_devid, point, barre)
    
    point = my_eltm.Point
    barre = my_eltm.Barre

    
    my_eltm = Split(P2, P3, B2, nb_devid , point, barre)

    point = my_eltm.Point
    barre = my_eltm.Barre

 
    # P1 = Point(0,0)
    # P2 = Point(50,0)
    # P3 = Point(110,0) 
    # P4 = Point(170,0)   
    # P5 = Point(230,0)   
    # P6 = Point(290,0)  
    # P7 = Point(340,0)  
    
    # P1.define_support_condition(True,True, False) 
    # P2.define_support_condition(True, True, False) 
    # P3.define_support_condition(True,True, False) 
    # P4.define_support_condition(True,True, False) 
    # P5.define_support_condition(True,True, False)
    # P6.define_support_condition(True,True, False)    
    # P7.define_support_condition(True,True, False) 
    
    # B1 = Barre(P1, P2)
    # B2 = Barre(P2, P3)
    # B3 = Barre(P3, P4)
    # B4 = Barre(P4, P5)
    # B5 = Barre(P5, P6)
    # B6 = Barre(P6, P7)
    
    # eq1 = [[0.005300263, -0.225261176, 2.5134],[-0.027850667, 2.785066667, -65.54666667]]
    # eq2 = [[-0.019340741, 0, 4.08],[0.005427211, -0.325632653, 5.004489796],
            # [-0.019340741, 2.320888889, -65.54666667]]
    # eq3 = eq2
    # eq4 = eq2
    # eq5 = eq2
    # eq6 = [[-0.027850667, 0, 4.08],[0.005300263, -0.304765121, 4.50099861591695]]
    # alpha_rive1 = [50*(1-0.15)]
    # alpha_inter1 =[]
    
    # B1.prestress_load(eq1, "RIVE", [42.5])
    # B2.prestress_load(eq2, "INTER", [9.0, 42.0])
    # B3.prestress_load(eq2, "INTER", [9.0, 42.0])
    # B4.prestress_load(eq2, "INTER", [9.0, 42.0])
    # B5.prestress_load(eq2, "INTER", [9.0, 42.0])
    # B6.prestress_load(eq6, "RIVE", [7.5])

    
    
    # point = (P1, P2, P3, P4, P5, P6, P7)
    # barre = (B1, B2, B3, B4, B5, B6)

    # nb_devid = 75 
    
    # my_eltm = Split(P1, P2, B1, nb_devid, point, barre)
    
    # point = my_eltm.Point
    # barre = my_eltm.Barre

    
    # my_eltm = Split(P2, P3, B2, nb_devid , point, barre)

    # point = my_eltm.Point
    # barre = my_eltm.Barre
    
    # my_eltm = Split(P3, P4, B3, nb_devid , point, barre)

    # point = my_eltm.Point
    # barre = my_eltm.Barre

    # my_eltm = Split(P4, P5, B4, nb_devid , point, barre)

    # point = my_eltm.Point
    # barre = my_eltm.Barre

    # my_eltm = Split(P5, P6, B5, nb_devid , point, barre)

    # point = my_eltm.Point
    # barre = my_eltm.Barre

    # my_eltm = Split(P6, P7, B6, nb_devid , point, barre)

    # point = my_eltm.Point
    # barre = my_eltm.Barre

    result = Stiffness_methode(barre, point)
    
    import matplotlib.pyplot as plt

    X = []
    Moment = []
    Shear = []
    Normal = []
    Deflection = []
    for i in point:
        X.append(i.X)
        Moment.append(i.Moment)
        # Shear.append(i.Shear)
        Normal.append(i.Normal)
        # Deflection.append(i.Delta_y)

    max = len(Moment)
    
    plt.title("Moment force")
    plt.plot(X, Moment, "b", marker="+",label="Moment")
    plt.plot(X, Moment, "y", marker="v",label="Normal")
    # plt.plot(X, Shear, "g", marker="*",label="Shear")
    # plt.plot(X, Deflection, "r", marker=".",label="Deflection")

    plt.plot([0,25, 50], [0,0,0], "g^")#,170, 230, 290 ,340], [0,0,0,0,0,0,0], "g^")
    plt.xlabel('Abscisse')
    plt.ylabel('Effort')
    plt.grid(True)
    plt.legend()
    plt.show()

"""    P1 = Point(0,0)
    P2 = Point(2.5,0)
    P3 = Point(5,0)
    
    P1.define_support_condition(True,True, True) 

    B1 = Barre(P1, P2)
    B2 = Barre(P2, P3)

    UDL = 48.9 /1000 # MN/m

    Value_uniforme = - UDL
    
    P2.define_external_force(0, -10,0)
    P3.define_external_force(0, 5,0)

    point = (P1, P2, P3)
    barre = (B1, B2)

    nb_devid = 100

    my_eltm = Split(P1, P2, B1, nb_devid, point, barre)
    
    point = my_eltm.Point
    barre = my_eltm.Barre

    
    my_eltm = Split(P2, P3, B2, nb_devid , point, barre)

    point = my_eltm.Point
    barre = my_eltm.Barre

    result = Stiffness_methode(barre, point)
    
    import matplotlib.pyplot as plt

    X = []
    Moment = []
    Shear = []
    Normal = []
    Deflection = []
    for i in point:
        X.append(i.X)
        Moment.append(i.Moment)
        Shear.append(i.Shear)
        Normal.append(i.Normal)
        Deflection.append(i.Delta_y)

    max = len(Moment)
    
    plt.title("Moment force")
    plt.plot(X, Moment, "b", marker="+",label="Moment")
    plt.plot(X, Shear, "g", marker="*",label="Shear")
    plt.plot(X, Deflection, "r", marker=".",label="Deflection")

    plt.plot([0,2.5, 5], [0,0,0], "g^")
    plt.xlabel('Abscisse')
    plt.ylabel('Effort')
    plt.grid(True)
    plt.legend()
    plt.show()
   
    ""P1 = Point(0,0)
    P2 = Point(50,0)
    P3 = Point(110,0)
    P4 = Point(170,0)
    P5 = Point(230,0)
    P6 = Point(290,0)
    P7 = Point(340,0)
    
    P1.define_support_condition(True,True,False)
    P2.define_support_condition(True,True,False)
    P3.define_support_condition(True,True,False)
    P4.define_support_condition(True,True,False)
    P5.define_support_condition(True,True,False)
    P6.define_support_condition(True,True,False)
    P7.define_support_condition(True,True,False)
    
    B1 = Barre(P1, P2)  #, my_sec, my_mat)
    B2 = Barre(P2, P3)#, my_sec, my_mat)
    B3 = Barre(P3, P4)#, my_sec, my_mat)
    B4 = Barre(P4, P5)#, my_sec, my_mat)
    B5 = Barre(P5, P6)#, my_sec, my_mat)
    B6 = Barre(P6, P7)#, my_sec, my_mat)

    
    super = 3.5  # MN/m
    UDL = 48.9 /1000 # MN/m

    Value_uniforme = - UDL
    

    B1.uniforme_load(0,Value_uniforme,0)
    B2.uniforme_load(0,Value_uniforme,0)
    B3.uniforme_load(0,Value_uniforme,0)
    B4.uniforme_load(0,Value_uniforme,0)
    B5.uniforme_load(0,Value_uniforme,0)
    B6.uniforme_load(0,Value_uniforme,0)

    point = (P1, P2, P3, P4, P5, P6, P7)
    barre = (B1, B2, B3, B4, B5, B6) 

    
    print("Mise en place des données: " + str(timeit.default_timer()-start))

    start = timeit.default_timer()
    start_2 = timeit.default_timer()
    nb_devid = 20

    my_eltm = TSplit(P1, P2, B1, nb_devid, point, barre)
    
    point = my_eltm.Point
    barre = my_eltm.Barre
    
    print("Division d'un élément: " + str(timeit.default_timer()-start))
    print("\n")
    
    my_eltm = TSplit(P2, P3, B2, nb_devid , point, barre)

    point = my_eltm.Point
    barre = my_eltm.Barre
    
    my_eltm = TSplit(P3, P4, B3, nb_devid , point, barre)

    point = my_eltm.Point
    barre = my_eltm.Barre

    my_eltm = TSplit(P4, P5, B4, nb_devid , point, barre)

    point = my_eltm.Point
    barre = my_eltm.Barre

    my_eltm = TSplit(P5, P6, B5, nb_devid , point, barre)

    point = my_eltm.Point
    barre = my_eltm.Barre

    my_eltm = TSplit(P6, P7, B6, nb_devid , point, barre)

    point = my_eltm.Point
    barre = my_eltm.Barre
    
    print("Division de tous les éléments: " + str(timeit.default_timer()-start_2))
  
    print("\n")
    print("Lancement des calculs:")
    start = timeit.default_timer()
    print(" Nb de point: " + str(len(point)))
    print(" Nb de barre: " + str(len(barre)))
    result = Stiffness_methode(barre, point)

    print("Fin du calcul: " + str(timeit.default_timer()-start))
    

    import matplotlib.pyplot as plt

    X = []
    Moment = []
    Shear = []
    Normal = []
    for i in point:
        X.append(i.X)
        Moment.append(i.Moment)
        Shear.append(i.Shear)
        Normal.append(i.Normal)

    max = len(Moment)
    
    plt.title("Moment force")
    plt.plot(X, Moment, "b", marker="+",label="Moment")
    plt.plot(X, Shear, "g", marker="*",label="Shear")

    plt.plot([0,50, 110, 170, 230, 290 ,340], [0,0,0,0,0,0,0], "g^")
    plt.xlabel('Abscisse')
    plt.ylabel('Effort')
    plt.grid(True)
    plt.legend()
    plt.show()"""