# README.md

```markdown
<div align="center">

# 🏗️ StructLib

**Librairie Python pour les calculs d'ingénierie structure selon les Eurocodes**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

*Automatisez vos vérifications réglementaires avec des résultats traçables, des formules explicites et des rapports prêts à l'emploi.*

</div>

---

## 📋 Table des matières

- [Présentation](#-présentation)
- [Fonctionnalités](#-fonctionnalités)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Démarrage rapide](#-démarrage-rapide)
- [Les 3 classes fondamentales](#-les-3-classes-fondamentales)
- [Eurocodes supportés](#-eurocodes-supportés)
- [Système de reporting](#-système-de-reporting)
- [Contribuer](#-contribuer)
- [Licence](#-licence)

---

## 🎯 Présentation

**StructLib** est une librairie Python pensée par et pour les ingénieurs structure. Elle implémente les vérifications courantes des Eurocodes avec une philosophie claire :

> Chaque résultat doit être **traçable**, chaque formule doit être **explicite**, chaque vérification doit être **référencée**.

Que vous souhaitiez vérifier rapidement une section en traction, dimensionner un assemblage boulonné ou produire une note de calcul complète, StructLib vous accompagne.

---

## ✨ Fonctionnalités

| Fonctionnalité | Description |
|---|---|
| 🧮 **Calculs rapides** | Fonctions standalone pour des vérifications en une ligne |
| 🏛️ **Calculs détaillés** | Classes complètes avec accès à chaque étape intermédiaire |
| 📄 **Rapports traçables** | `FormulaResult` et `FormulaCollection` pour des sorties normalisées |
| 🔗 **Formules explicites** | Chaque résultat affiche sa formule littérale, ses valeurs numériques et sa référence Eurocode |
| 🧱 **Modulaire** | Matériaux, sections et calculs sont découplés et réutilisables |
| 🐍 **Pythonic** | `@property`, type hints, `__repr__`, kwargs flexibles |

---

## 🏗 Architecture **Will be modify**

```
structlib/
│
├── core/                           # Classes fondamentales
│   ├── material.py                 # Material — propriétés mécaniques
│   ├── section.py                  # Section — propriétés géométriques
│   └── section_material.py         # SectionMaterial — propriétés couplées
│
├── formula/                        # Système de reporting
│   ├── formula_result.py           # FormulaResult — résultat unique traçable
│   └── formula_collection.py       # FormulaCollection — regroupement d'étapes
│
├── ec2/                            # Eurocode 2 — Béton armé
│   ├── bending.py
│   ├── shear.py
│   └── ...
│
├── ec3/                            # Eurocode 3 — Structures en acier
│   ├── tension.py
│   ├── compression.py
│   ├── bending.py
│   ├── shear.py
│   ├── buckling.py
│   └── ...
│
├── ec4/                            # Eurocode 4 — Structures mixtes
│   └── ...
│
├── ec5/                            # Eurocode 5 — Structures en bois
│   └── ...
│
├── ec8/                            # Eurocode 8 — Sismique
│   └── ...
│
└── utils/                          # Utilitaires
    ├── units.py
    └── helpers.py
```

---

## ⚙️ Installation

```bash
# Cloner le dépôt
git clone https://github.com/<votre-username>/structlib.git
cd structlib

# Installer en mode développement
pip install -e .
```

> **Pré-requis** : Python ≥ 3.10

---

## 🚀 Démarrage rapide

### Calcul rapide (une ligne)

```python
from structlib.ec3.tension import nt_rd

# Nt,Rd pour un IPE 300, S235
resistance = nt_rd(A=5381, fy=235, Anet=4800, fu=360)
print(f"Nt,Rd = {resistance:.0f} N")
```

### Calcul détaillé avec rapport

```python
from structlib.ec3.tension import Tension

# Définition du problème
verif = Tension(
    Ned=250_000,        # Effort de traction [N]
    A=5381,             # Section brute [mm²]
    fy=235,             # Limite d'élasticité [MPa]
    fu=360,             # Résistance ultime [MPa]
    Anet=4800,          # Section nette [mm²]
)

# Résultats
print(f"Npl,Rd  = {verif.npl_rd:.0f} N")
print(f"Nu,Rd   = {verif.nu_rd:.0f} N")
print(f"Nt,Rd   = {verif.nt_rd:.0f} N")
print(f"Taux    = {verif.verif:.2%}")
print(f"Vérifié = {verif.is_ok}")
```

### Avec les classes Material et Section

```python
from structlib.core import Material, Section
from structlib.ec3.tension import Tension

acier = Material(fy=235, fu=360, gamma_m0=1.0, gamma_m2=1.25)
ipe300 = Section(A=5381, Anet=4800)

verif = Tension(Ned=250_000, mat=acier, sec=ipe300)

# Génération du rapport complet
rapport = verif.report(with_values=True)
print(rapport)
```

**Sortie :**
```
══════════════════════════════════════════════════
  Vérification à la traction
  Réf. : EC3-1-1 — §6.2.3
══════════════════════════════════════════════════

  Npl,Rd = A · fy / γM0
  Npl,Rd = 5381.00 × 235.00 / 1.0 = 1264535.00 N
  ► Npl,Rd = 1264535.00 N          [EC3-1-1 — §6.2.3 (2)a]

  Nu,Rd = 0.9 · Anet · fu / γM2
  Nu,Rd = 0.9 × 4800.00 × 360.00 / 1.25 = 1244160.00 N
  ► Nu,Rd = 1244160.00 N           [EC3-1-1 — §6.2.3 (2)b]

  Nt,Rd = min(Npl,Rd ; Nu,Rd)
  Nt,Rd = min(1264535.00 ; 1244160.00) = 1244160.00 N
  ► Nt,Rd = 1244160.00 N           [EC3-1-1 — §6.2.3 (2)]

  Ned / Nt,Rd ≤ 1.0
  Ned / Nt,Rd = 250000.00 / 1244160.00 = 0.2010 ≤ 1.0 → OK ✓
  ► Ned/Nt,Rd = 0.2010              [EC3-1-1 — §6.2.3 (1)]

══════════════════════════════════════════════════
```

---

## 🧱 Les 3 classes fondamentales

### `Material` — Propriétés mécaniques

Encapsule les caractéristiques du matériau indépendamment de la géométrie.

```python
from structlib.core import Material

# Acier S355
acier = Material(fy=355, fu=510, E=210_000, gamma_m0=1.0, gamma_m2=1.25)

# Béton C30/37
beton = Material(fck=30, fctm=2.9, Ecm=33_000, gamma_c=1.5)
```

| Propriété | Description | Unité |
|---|---|---|
| `fy` | Limite d'élasticité | MPa |
| `fu` | Résistance ultime à la traction | MPa |
| `fck` | Résistance caractéristique en compression (béton) | MPa |
| `E` | Module d'Young | MPa |
| `gamma_m0` | Coefficient partiel γ_M0 | — |
| `gamma_m2` | Coefficient partiel γ_M2 | — |
| `gamma_c` | Coefficient partiel γ_c (béton) | — |

### `Section` — Propriétés géométriques

Décrit la géométrie pure de la section transversale.

```python
from structlib.core import Section

ipe300 = Section(
    A=5381,         # Aire brute [mm²]
    Anet=4800,      # Aire nette [mm²]
    Iy=8356e4,      # Inertie axe fort [mm⁴]
    Iz=604e4,       # Inertie axe faible [mm⁴]
    Wply=628.4e3,   # Module plastique y [mm³]
    Wplz=125.2e3,   # Module plastique z [mm³]
)
```

### `SectionMaterial` — Propriétés couplées

Contient les propriétés qui dépendent à la fois de la section **et** du matériau.

```python
from structlib.core import SectionMaterial

# Béton armé — hauteur utile, enrobage, etc.
sec_ba = SectionMaterial(
    d=267,          # Hauteur utile [mm]
    c_nom=30,       # Enrobage nominal [mm]
)

# Assemblage boulonné — pinces par défaut, etc.
sec_boulon = SectionMaterial(
    e1=40,          # Pince longitudinale [mm]
    e2=30,          # Pince transversale [mm]
    p1=70,          # Entraxe longitudinal [mm]
)
```

---

## 📐 Eurocodes supportés

| Eurocode | Domaine | Statut |
|---|---|---|
| **EC2** | Béton armé et précontraint | 🔲 En cours |
| **EC3** | Structures en acier | 🔲 En cours |
| **EC4** | Structures mixtes acier-béton | 🔲 Prévu |
| **EC5** | Structures en bois | 🔲 Prévu |
| **EC8** | Dimensionnement parasismique | 🔲 Prévu |

### EC3 — Détail des modules

| Module | Vérification | Référence | Statut |
|---|---|---|---|
| `tension.py` | Traction simple | §6.2.3 | ✅ |
| `compression.py` | Compression simple | §6.2.4 | 🔲 |
| `bending.py` | Flexion | §6.2.5 | 🔲 |
| `shear.py` | Cisaillement | §6.2.6 | 🔲 |
| `buckling.py` | Flambement | §6.3.1 | 🔲 |
| `ltb.py` | Déversement | §6.3.2 | 🔲 |
| `combined.py` | Efforts combinés | §6.3.3 | 🔲 |

---

## 📄 Système de reporting

Chaque calcul produit des objets `FormulaResult` regroupables en `FormulaCollection` :

```python
# Un résultat unique
result = verif.get_npl_rd(with_values=True)
print(result.name)            # "Npl,Rd"
print(result.formula)         # "Npl,Rd = A · fy / γM0"
print(result.formula_values)  # "Npl,Rd = 5381.00 × 235.00 / 1.0 = 1264535.00 N"
print(result.result)          # 1264535.0
print(result.unit)            # "N"
print(result.ref)             # "EC3-1-1 — §6.2.3 (2)a"

# Collection complète
rapport = verif.report(with_values=True)
# Exportable, itérable, affichable
```

---

## 🤝 Contribuer

Les contributions sont les bienvenues ! Voici comment participer :

1. **Fork** le dépôt
2. **Créer** une branche (`git checkout -b feature/ec3-buckling`)
3. **Coder** en respectant le template de classe existant
4. **Tester** vos calculs avec des exemples de référence
5. **Soumettre** une Pull Request

### Convention de code

- Chaque classe de vérification suit le **template standardisé** (propriétés, `get_xxx`, `report`)
- Chaque formule est **référencée** (article Eurocode)
- Les unités sont en **N, mm, MPa** (système cohérent)
- Type hints obligatoires
- Docstrings en français

---

## 📜 Licence

Ce projet est distribué sous licence **MIT**. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

<div align="center">

**Fait avec ❤️ pour la communauté des ingénieurs structure**

*Si ce projet vous est utile, laissez une ⭐ !*

</div>
```