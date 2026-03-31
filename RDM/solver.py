#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Solveur par méthode de rigidité directe (Direct Stiffness Method)
    pour analyse 2D de portique.
    
    Workflow:
        1. Créer les nœuds et éléments
        2. Appeler Solver(nodes, elements).solve()
        3. Récupérer les résultats dans les nœuds et éléments
    
    Units: N, mm, rad
"""

__all__ = ['Solver']

from typing import List, Dict, Tuple, Optional
import numpy as np
import time

from .node import Node
from .element import Element


class Solver:
    """
        Solveur par rigidité directe pour portique 2D.
        
        Parameters
        ----------
        nodes : list of Node
        elements : list of Element
        verbose : bool
            Afficher les temps de calcul
        
        Examples
        --------
        >>> solver = Solver([n1, n2, n3], [b1, b2])
        >>> solver.solve()
        >>> print(n2.results.dy)
        >>> print(n1.results.ry)
        >>> solver.internal_forces(b1, nb_points=50)
    """

    DOF_PER_NODE: int = 3  # dx, dy, θz

    def __init__(self, nodes: List[Node], elements: List[Element],
                 verbose: bool = False) -> None:

        if not nodes:
            raise ValueError("La liste de nœuds est vide")
        if not elements:
            raise ValueError("La liste d'éléments est vide")

        self._nodes: List[Node] = nodes
        self._elements: List[Element] = elements
        self._verbose: bool = verbose

        # Dimensions
        self._n_nodes: int = len(nodes)
        self._n_dof: int = self._n_nodes * self.DOF_PER_NODE

        # Mapping nœud.id → position 0-based
        self._node_index: Dict[int, int] = {
            node.id: i for i, node in enumerate(nodes)
        }

        # Résultats (remplis par solve())
        self._K_global: Optional[np.ndarray] = None
        self._F_global: Optional[np.ndarray] = None
        self._U_global: Optional[np.ndarray] = None
        self._is_solved: bool = False

    # =================================================================
    #  Résolution principale
    # =================================================================

    def solve(self) -> 'Solver':
        """
            Résout le système complet.
            
            Étapes:
                1. Reset des résultats
                2. Assemblage K_global
                3. Assemblage F_global
                4. Partition des DDL libres/bloqués
                5. Résolution K_ff · U_f = F_f
                6. Calcul des réactions R = K·U - F
                7. Écriture dans les nœuds
            
            Returns
            -------
            Solver
                self (pour chaînage)
        """
        t0 = time.perf_counter()

        # 1. Reset
        for node in self._nodes:
            node.reset_results()
        self._is_solved = False

        # 2. Assemblage K
        self._K_global = self._assemble_stiffness()
        self._log("Assemblage K", t0)

        # 3. Assemblage F
        t1 = time.perf_counter()
        self._F_global = self._assemble_forces()
        self._log("Assemblage F", t1)

        # 4-5. Résolution
        t2 = time.perf_counter()
        self._U_global = self._solve_system()
        self._log("Résolution", t2)

        # 6-7. Post-traitement
        t3 = time.perf_counter()
        self._compute_reactions()
        self._write_displacements_to_nodes()
        self._log("Post-traitement", t3)

        self._is_solved = True
        self._log("=== TOTAL", t0)

        return self

    # =================================================================
    #  Assemblage
    # =================================================================

    def _assemble_stiffness(self) -> np.ndarray:
        """
            Assemble la matrice de rigidité globale K (n_dof × n_dof).
            
            Pour chaque élément :
                K_global[dofs, dofs] += elem.k_global
        """
        n = self._n_dof
        K = np.zeros((n, n), dtype=float)

        for elem in self._elements:
            k_e = elem.k_global             # 6×6 en repère global
            dofs = self._element_dofs(elem)  # 6 indices globaux

            # Assemblage vectorisé via numpy
            idx = np.array(dofs, dtype=int)
            K[np.ix_(idx, idx)] += k_e

        return K

    def _assemble_forces(self) -> np.ndarray:
        """
            Assemble le vecteur de forces global F (n_dof).
            
            Sources :
                - Forces nodales directes (node.forces)
                - Forces nodales équivalentes des chargements sur barres
        """
        n = self._n_dof
        F = np.zeros(n, dtype=float)

        # Forces nodales directes
        for node in self._nodes:
            i = self._node_dof_start(node)
            F[i:i + 3] += node.forces.as_array()

        # Forces nodales équivalentes
        for elem in self._elements:
            f_eq = elem.equivalent_nodal_forces_global  # 6 composantes
            dofs = self._element_dofs(elem)

            for loc, glob in enumerate(dofs):
                F[glob] += f_eq[loc]

        return F

    # =================================================================
    #  Résolution du système linéaire
    # =================================================================

    def _solve_system(self) -> np.ndarray:
        """
            Résout K·U = F par partition.
            
            Sépare les DDL en :
                - free_dofs   : déplacements inconnus
                - blocked_dofs: déplacements imposés (= 0)
            
            Résout K_ff · U_f = F_f
            
            Raises
            ------
            RuntimeError
                Si le système est singulier (mécanisme)
        """
        free_dofs, blocked_dofs = self._partition_dofs()

        if len(free_dofs) == 0:
            return np.zeros(self._n_dof, dtype=float)

        K_ff = self._K_global[np.ix_(free_dofs, free_dofs)]
        F_f = self._F_global[free_dofs]

        try:
            U_f = np.linalg.solve(K_ff, F_f)
        except np.linalg.LinAlgError:
            raise RuntimeError(
                "Système singulier — la structure est un mécanisme. "
                "Vérifier les conditions d'appui."
            )

        U = np.zeros(self._n_dof, dtype=float)
        U[free_dofs] = U_f
        return U

    # =================================================================
    #  Post-traitement
    # =================================================================

    def _compute_reactions(self) -> None:
        """
            Calcule les réactions d'appui : R = K·U - F
            
            Seules les composantes des DDL bloqués sont non nulles.
        """
        R = self._K_global @ self._U_global - self._F_global

        for node in self._nodes:
            i = self._node_dof_start(node)
            blocked = node.support.dof_blocked  # [bool, bool, bool]

            if blocked[0]:
                node.results.rx = R[i]
            if blocked[1]:
                node.results.ry = R[i + 1]
            if blocked[2]:
                node.results.mz = R[i + 2]

    def _write_displacements_to_nodes(self) -> None:
        """Écrit les déplacements calculés dans chaque nœud."""
        for node in self._nodes:
            i = self._node_dof_start(node)
            node.results.dx = self._U_global[i]
            node.results.dy = self._U_global[i + 1]
            node.results.theta = self._U_global[i + 2]

    # =================================================================
    #  Efforts internes
    # =================================================================

    def internal_forces(self, elem: Element,
                        nb_points: int = 51) -> Dict[str, np.ndarray]:
        """
            Calcule N, V, M le long d'un élément.
            
            Parameters
            ----------
            elem : Element
                L'élément à analyser
            nb_points : int
                Nombre de points de discrétisation
            
            Returns
            -------
            dict avec clés :
                'x' : np.ndarray — abscisses locales (0 à L)
                'N' : np.ndarray — effort normal
                'V' : np.ndarray — effort tranchant
                'M' : np.ndarray — moment fléchissant
            
            Raises
            ------
            RuntimeError
                Si solve() n'a pas été appelé
            
            Examples
            --------
            >>> results = solver.internal_forces(beam, nb_points=100)
            >>> plt.plot(results['x'], results['M'])
        """
        if not self._is_solved:
            raise RuntimeError("Appeler solve() avant internal_forces()")

        L = elem.length
        x_arr = np.linspace(0, L, nb_points)

        # Récupérer les déplacements globaux des 2 nœuds
        d_global = self._element_displacements(elem)

        # Efforts aux nœuds en local : f = K_local · R · d - f_eq_local
        R = elem.rotation_matrix
        d_local = R @ d_global
        f_nodal = elem.k_local @ d_local - elem.equivalent_nodal_forces_local

        # Efforts au nœud i (convention : N = traction positive)
        #   f_nodal = [Fx_i, Fy_i, Mz_i, Fx_j, Fy_j, Mz_j]
        #   N_i = -Fx_i (effort interne = opposé de la réaction nodale)
        #   V_i = Fy_i
        #   M_i = Mz_i
        N_i = -f_nodal[0]
        V_i = f_nodal[1]
        M_i = f_nodal[2]

        # Charges réparties (pour l'intégration le long de la barre)
        from .loads import DistributedLoad
        q_x = sum(ld.fx for ld in elem.loads if isinstance(ld, DistributedLoad))
        q_y = sum(ld.fy for ld in elem.loads if isinstance(ld, DistributedLoad))

        # Efforts le long de la barre
        N_arr = N_i + q_x * x_arr
        V_arr = V_i - q_y * x_arr
        M_arr = M_i + V_i * x_arr - q_y * x_arr**2 / 2

        return {
            'x': x_arr,
            'N': N_arr,
            'V': V_arr,
            'M': M_arr,
        }

    def all_internal_forces(self, nb_points: int = 51) -> Dict[str, Dict[str, np.ndarray]]:
        """
            Calcule les efforts internes de TOUS les éléments.
            
            Returns
            -------
            dict
                {elem.name: {'x': ..., 'N': ..., 'V': ..., 'M': ...}}
        """
        if not self._is_solved:
            raise RuntimeError("Appeler solve() avant all_internal_forces()")

        return {
            elem.name: self.internal_forces(elem, nb_points)
            for elem in self._elements
        }

    # =================================================================
    #  Indexation
    # =================================================================

    def _node_dof_start(self, node: Node) -> int:
        """Premier index global d'un nœud (0-based)."""
        return self._node_index[node.id] * self.DOF_PER_NODE

    def _element_dofs(self, elem: Element) -> List[int]:
        """
            6 indices de DDL globaux d'un élément.
            
            Returns
            -------
            list of int
                [dx_i, dy_i, θ_i, dx_j, dy_j, θ_j]
        """
        i_start = self._node_dof_start(elem.node_i)
        j_start = self._node_dof_start(elem.node_j)
        return [
            i_start, i_start + 1, i_start + 2,
            j_start, j_start + 1, j_start + 2,
        ]

    def _element_displacements(self, elem: Element) -> np.ndarray:
        """
            Extrait les 6 déplacements globaux d'un élément
            depuis le vecteur U_global.
        """
        dofs = self._element_dofs(elem)
        return self._U_global[dofs]

    def _partition_dofs(self) -> Tuple[List[int], List[int]]:
        """
            Sépare les DDL en libres et bloqués.
            
            Returns
            -------
            (free_dofs, blocked_dofs) : tuple of list of int
        """
        free = []
        blocked = []

        for node in self._nodes:
            i = self._node_dof_start(node)
            for k, is_blocked in enumerate(node.support.dof_blocked):
                if is_blocked:
                    blocked.append(i + k)
                else:
                    free.append(i + k)

        return free, blocked

    # =================================================================
    #  Analyse statique
    # =================================================================

    @staticmethod
    def hyperstaticity(nodes: List[Node]) -> Tuple[int, str]:
        """
            Degré d'hyperstaticité de la structure.
            
            Parameters
            ----------
            nodes : list of Node
            
            Returns
            -------
            (degree, label) : tuple
                degree : int (négatif = hypostatique)
                label  : "Hypostatique" / "Isostatique" / "Hyperstatique (n)"
        """
        n_reactions = sum(n.hyper_degree for n in nodes)
        degree = n_reactions - 3

        if degree < 0:
            return degree, "Hypostatique"
        elif degree == 0:
            return degree, "Isostatique"
        else:
            return degree, f"Hyperstatique ({degree})"

    # =================================================================
    #  Accès aux résultats bruts
    # =================================================================

    @property
    def is_solved(self) -> bool:
        """True si solve() a été exécuté avec succès."""
        return self._is_solved

    @property
    def K_global(self) -> Optional[np.ndarray]:
        """Matrice de rigidité globale assemblée."""
        return self._K_global

    @property
    def F_global(self) -> Optional[np.ndarray]:
        """Vecteur de forces global assemblé."""
        return self._F_global

    @property
    def U_global(self) -> Optional[np.ndarray]:
        """Vecteur des déplacements globaux."""
        return self._U_global

    # =================================================================
    #  Logging
    # =================================================================

    def _log(self, label: str, t_start: float) -> None:
        """Affiche le temps écoulé si verbose=True."""
        if self._verbose:
            dt = (time.perf_counter() - t_start) * 1000  # ms
            print(f"  [{label}] {dt:.2f} ms")

    # =================================================================
    #  Repr
    # =================================================================

    def __repr__(self) -> str:
        deg, label = self.hyperstaticity(self._nodes)
        status = "✅ Résolu" if self._is_solved else "⏳ Non résolu"
        return (
            f"Solver | {self._n_nodes} nœuds | "
            f"{len(self._elements)} éléments | "
            f"{self._n_dof} DDL | {label} | {status}"
        )


# =============================================================================
#  TESTS
# =============================================================================

if __name__ == "__main__":
    from .node import Node
    from .element import Element
    from .loads import DistributedLoad

    Node.reset_counter()
    Element.reset_counter()

    # --- Poutre sur 2 appuis, charge répartie ---
    #
    #   q = -10 N/mm
    #   ├──────────────────────┤
    #   A (appui fixe)         B (appui simple)
    #   0                      6000 mm

    n1 = Node(0, 0, name="A")
    n2 = Node(6000, 0, name="B")

    n1.set_support(rx=True, ry=True)       # Appui fixe
    n2.set_support(ry=True)                # Appui simple

    beam = Element(n1, n2, E=210000, A=5000, I=8.356e7, name="Poutre")
    beam.add_load(DistributedLoad(fy=-10))

    solver = Solver([n1, n2], [beam], verbose=True)
    print(solver)

    solver.solve()
    print(solver)

    # Résultats
    print(f"\nDéplacements nœud B:")
    print(f"  dy    = {n2.results.dy:.4f} mm")
    print(f"  theta = {n2.results.theta:.6f} rad")

    print(f"\nRéactions nœud A:")
    print(f"  Rx = {n1.results.rx:.1f} N")
    print(f"  Ry = {n1.results.ry:.1f} N")

    print(f"\nRéactions nœud B:")
    print(f"  Ry = {n2.results.ry:.1f} N")

    # Efforts internes
    results = solver.internal_forces(beam)
    print(f"\nMoment max = {max(abs(results['M'])):.0f} N·mm")
    print(f"Tranchant max = {max(abs(results['V'])):.0f} N")

    # Vérification analytique
    q = 10  # N/mm
    L = 6000
    M_max_th = q * L**2 / 8
    print(f"\nMoment max théorique (isostatique) = {M_max_th:.0f} N·mm")
