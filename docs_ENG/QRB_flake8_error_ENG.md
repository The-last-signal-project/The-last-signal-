# Comprehensive Guide to Flake8 Errors

> **Professional Reference Guide** for understanding and resolving Flake8 errors and warnings in Python.  
>

---

## Table of Contents

- [Introduction](#introduction)
- [Global Summary Table](#global-summary-table)
- [Family E - Style Errors (PyCodestyle)](#family-e---style-errors-pycodestyle)
- [Family F - Logic Errors (PyFlakes)](#family-f---logic-errors-pyflakes)
- [Family W - Style Warnings (PyCodestyle)](#family-w---style-warnings-pycodestyle)
- [Family C90 - Cyclomatic Complexity (McCabe)](#family-c90---cyclomatic-complexity-mccabe)
- [Family B - Bugbear (Security & Style)](#family-b---bugbear-security--style)
- [Family N - Naming (Naming Conventions)](#family-n---naming-naming-conventions)
- [Family ANN - Annotations (Static Type Hints)](#family-ann---annotations-static-type-hints)
- [Family COM - Comprehensions (Optimizations)](#family-com---comprehensions-optimizations)
- [Family D - Docstrings (Documentation)](#family-d---docstrings-documentation)
- [Family I - Isort (Import Sorting)](#family-i---isort-import-sorting)
- [Family PIE - Pie (Optimizations)](#family-pie---pie-optimizations)
- [Family SIM - Simplify (Code Simplifications)](#family-sim---simplify-code-simplifications)
- [Family UP - Pyupgrade (Code Modernization)](#family-up---pyupgrade-code-modernization)
- [Automated Formatting & Fixing Tools](#automated-formatting--fixing-tools)
- [References & Bibliography](#references--bibliography)

---

## Introduction

**Flake8** is a static analysis tool for Python that combines:

- **PyCodestyle** (PEP 8): style guide conformance
- **PyFlakes**: logic error detection
- **McCabe**: cyclomatic complexity measurement

Error code format: `[FAMILY][NUMBER]`

---

## Global Summary Table


| Family | Plugin | Category | Codes | Example |
| ------- | --------------------- | --------------- | ----- | ------- |
| E       | -                     | Style | \~50  | E128    |
| F       | -                     | Logic | \~25  | F401    |
| W       | -                     | Warnings | \~15  | W291    |
| C90     | -                     | Complexity | 1     | C901    |
| B       | flake8-bugbear        | Security | \~35  | B007    |
| N       | flake8-naming         | Naming | \~25  | N801    |
| ANN     | flake8-annotations    | Type Hints | \~15  | ANN001  |
| COM     | flake8-comprehensions | Optimizations | \~10  | COM812  |
| D       | flake8-docstrings     | Documentation | \~20  | D100    |
| I       | flake8-isort          | Imports | \~10  | I001    |
| PIE     | flake8-pie            | Optimizations | \~30  | PIE798  |
| SIM     | flake8-simplify       | Simplifications | \~35  | SIM101  |
| UP      | flake8-pyupgrade      | Modernization | \~30  | UP001   |


---

## Family E - Style Errors (PyCodestyle)

> **Plugin**: Built-in | **Docs**: [PEP 8](https://peps.python.org/pep-0008/)

### Table of E Codes


| Code | Description | Severity |
| ------------- | ------------------------------------ | ------------- |
| [E101](#e101) | Indentation mixing tabs and spaces       | Error |
| [E111](#e111) | Incorrect indentation (4 spaces required)              | Error |
| [E112](#e112) | Unexpected indentation block                 | Error |
| [E113](#e113) | Unexpected indentation          | Error |
| [E114](#e114) | Incorrect comment indentation (see E111)               | Error |
| [E115](#e115) | Incorrect comment indentation block (see E112) | Error |
| [E116](#e116) | Unexpected indentation in comment (see E113)         | Error |
| [E117](#e117) | Excessive indentation                | Error |
| [E121](#e121) | Incorrect alignment                 | Warning |
| [E131](#e131) | Blank lines in comments            | Warning |
| [E133](#e133) | Incorrect whitespace in slice            | Error |
| [E201](#e201) | Missing whitespace after '('              | Error |
| [E202](#e202) | Missing whitespace before ')'              | Error |
| [E203](#e203) | Missing whitespace before ','              | Error |
| [E211](#e211) | Whitespace around operators                   | Error |
| [E221](#e221) | Multiple spaces around operators         | Error |
| [E222](#e222) | Missing whitespace around operators           | Error |
| [E223](#e223) | Tab character before operator                 | Error |
| [E224](#e224) | Tab character after operator              | Error |
| [E231](#e231) | Missing whitespace after ':', ',', or ';'              | Error |
| [E241](#e241) | Multiple spaces after ','            | Error |
| [E242](#e242) | Missing whitespace after ','              | Error |
| [E261](#e261) | Whitespace before inline comment             | Warning |
| [E262](#e262) | Missing whitespace in comment          | Warning |
| [E265](#e265) | Missing whitespace in block comment     | Warning |
| [E266](#e266) | Multiple spaces in comment        | Warning |
| [E271](#e271) | Multiple spaces around keyword            | Error |
| [E301](#e301) | Missing blank line                 | Warning |
| [E302](#e302) | Excessive blank lines              | Warning |
| [E401](#e401) | Multiple imports on a single line                | Error |
| [E402](#e402) | Multi-line import error                  | Error |
| [E501](#e501) | Line too long                    | Error |
| [E502](#e502) | Redundant backslash                    | Warning |
| [E701](#e701) | Missing colon in slice          | Error |
| [E703](#e703) | Semicolon before comment      | Warning |
| [E704](#e704) | Multiple statements on one line         | Error |
| [E711](#e711) | Comparison to None                | Error |
| [E712](#e712) | Comparison to True/False          | Error |
| [E721](#e721) | Type comparison                 | Error |
| [E722](#e722) | `is` used to compare literals         | Error |
| [E731](#e731) | Assigning a lambda expression                  | Error |


---

### E101

**Description**: Inconsistent indentation.

**Cause**: Mixing tabs and spaces.

**Incorrect Example**

```python
def fonction():
    if True:
        print("Hello")
    else:
	print("World")
```

**Corrected Example**

```python
def fonction():
    if True:
        print("Hello")
    else:
        print("World")
```

**Explanation**: PEP 8 recommends **4 spaces per indentation level**.

**Best Practices**: Configure `.editorconfig`: `indent_style = space` and `indent_size = 4`

---

### E111

**Description**: Incorrect indentation.

**Incorrect Example**

```python
def fonction():
  if True:
    print("Hello")
```

**Corrected Example**

```python
def fonction():
    if True:
        print("Hello")
```

---

### E112

**Description**: Expected an indented block.

**Incorrect Example**

```python
def fonction():
if True:
    print("Hello")
```

**Corrected Example**

```python
def fonction():
    if True:
        print("Hello")
```

---

### E113

**Description**: Unexpected indentation.

**Incorrect Example**

```python
def fonction():
    if True:
        print("Hello")
    print("World")
```

**Corrected Example**

```python
def fonction():
    if True:
        print("Hello")
    print("World")
```

---

### E114-E116

**Description**: Indentation issues with comments.

**Corrected Example**: Align comments with code.

---

### E117

**Description**: Excessive indentation.

**Corrected Example**: Use 4 spaces per indentation level.

---

### E121

**Description**: Incorrect alignment.

**Incorrect Example**

```python
x    = 1
yy   = 2
```

**Corrected Example**

```python
x = 1
yy = 2
```

**Explanation**: PEP 8 recommande de **ne pas aligner** les opérateurs.

---

### E122-E129

**Description**: Visual alignment issues.

---

### E131

**Description**: Lignes vides autour des commentaires.

**Corrected Example**: 0 ligne avant commentaire en ligne, 1 ligne avant bloc.

---

### E133

**Description**: Incorrect whitespace in slices.

**Incorrect Example**

```python
lst[1 : 5]
lst[1:5 : 2]
```

**Corrected Example**

```python
lst[1:5]
lst[1:5:2]
```

---

### E201

**Description**: Missing whitespace after '('.

**Corrected Example**:

```python
if (x > 5):
```

---

### E202

**Description**: Missing whitespace before ')'.

---

### E203

**Description**: Missing whitespace before ','.

**Corrected Example**:

```python
lst = [1, 2, 3]
```

---

### E211

**Description**: Espaces autour des opérateurs.

**Incorrect Example**

```python
x=5
x =5
x= 5
x  =  5
```

**Corrected Example**

```python
x = 5
```

**Explanation**: PEP 8 : **un espace de chaque côté** des opérateurs binaires.  
**Exceptions** : unaires (`-5`), slices (`[1:5]`).

---

### E221-E228

**Description**: Espaces incorrects autour opérateurs.

---

### E231

**Description**: Missing whitespace before ':'.

---

### E241-E242

**Description**: Espaces incorrects après ,.

**Corrected Example**:

```python
lst = [1, 2, 3]
```

---

### E261-E266

**Description**: Espaces incorrects commentaires.

**Corrected Example**:

```python
x = 5  # Commentaire
```

**Explanation**: **2 espaces** avant commentaire en ligne.

---

### E271-E275

**Description**: Espaces incorrects mots-clés.

---

### E301

**Description**: Missing blank line.

**Corrected Example**:

```python
def f1():
    pass

def f2():
    pass
```

**Explanation**: **2 lignes vides** entre définitions niveau supérieur.

---

### E302-E306

**Description**: Problèmes lignes vides.

---

### E401

**Description**: Import multiple sur une ligne.

**Incorrect Example**

```python
import os, sys
```

**Corrected Example**

```python
import os
import sys
```

---

### E402

**Description**: Multi-line import error mal formaté.

**Corrected Example**:

```python
from module import (
    name1,
    name2,
)
```

---

### E501

**Description**: Line too long (&gt;79 caractères par défaut).

**Corrected Example**:

```python
print(
    "Ligne très longue divisée en "
    "plusieurs parties"
)
```

**Best Practices**: Configurer `max-line-length = 88`

---

### E502

**Description**: Redundant backslash.

**Corrected Example**:

```python
x = (1 + 2 +
     3 + 4)
```

---

### E701-E702

**Description**: Missing colon in slice.

---

### E703

**Description**: Semicolon before comment.

**Corrected Example**:

```python
x = 5
print(x)
```

---

### E704

**Description**: Plusieurs instructions sur une ligne.

**Corrected Example**:

```python
x = 5
y = 10
```

---

### E711

**Description**: Comparison to None.

**Incorrect Example**

```python
if x == None:
    pass
```

**Corrected Example**

```python
if x is None:
    pass
```

**Références** : [PEP 8 - None](https://peps.python.org/pep-0008/#id53)

---

### E712

**Description**: Comparison to True/False.

**Corrected Example**:

```python
if x:  # au lieu de if x == True:
    pass
```

---

### E713-E714

**Description**: Membership test with None/True/False.

---

### E721

**Description**: Type comparison.

**Corrected Example**:

```python
if isinstance(x, int):
    pass
```

---

### E722

**Description**: Ne pas utiliser `is` used to compare literals.

**Corrected Example**:

```python
if x == 5:
    pass
```

---

### E731

**Description**: Ne pas assigner une lambda.

**Corrected Example**:

```python
def f(x):
    return x + 1
```

---

[↑ Back to Table of Contents](#table-of-contents)

---

## Family F - Logic Errors (PyFlakes)

> **Plugin**: Built-in | **Docs**: [PyFlakes](https://pypi.org/project/pyflakes/)

### Table of F Codes


| Code          | Description                        | Sévérité      | Catégorie   |
| ------------- | ---------------------------------- | ------------- | ----------- |
| [F401](#f401) | Import inutilisé                   | Error | Imports     |
| [F403](#f403) | Wildcard import (`*`)                     | Warning | Imports     |
| [F405](#f405) | Import en double                   | Error | Imports     |
| [F601](#f601) | Variable utilisée avant définition | Error | Variables   |
| [F602](#f602) | Variable non définie               | Error | Variables   |
| [F621](#f621) | Arguments non utilisés             | Warning | Fonctions   |
| [F622](#f622) | Fonction non utilisée              | Warning | Fonctions   |
| [F631](#f631) | Assert with tuple (always true)               | Error | Assertions  |
| [F632](#f632) | Utilisation de input()             | Warning | Sécurité    |
| [F633](#f633) | Utilisation de print()             | Warning | Style       |
| [F634](#f634) | If condition with tuple (always evaluates to True)                      | Warning | Conditions  |
| [F701](#f701) | Break hors boucle                  | Error | Contrôle    |
| [F702](#f702) | Continue hors boucle               | Error | Contrôle    |
| [F704](#f704) | Yield hors fonction                | Error | Générateurs |
| [F706](#f706) | Return hors fonction               | Error | Contrôle    |
| [F811](#f811) | Variable redéfinie                 | Warning | Variables   |
| [F821](#f821) | Variable non définie               | Error | Variables   |
| [F841](#f841) | Variable locale non utilisée       | Warning | Variables   |
| [F901](#f901) | Return with value in `__init__`   | Error | Classes     |


---

### F401

**Description**: Import inutilisé.

**Incorrect Example**

```python
import os  # Non utilisé
import sys
```

**Corrected Example**

```python
import sys
```

---

### F403

**Description**: Wildcard import (`*`).

**Incorrect Example**

```python
from os import *
```

**Corrected Example**

```python
from os import path, environ
```

---

### F405

**Description**: Import en double.

---

### F601

**Description**: Variable utilisée avant définition.

**Corrected Example**:

```python
x = 5
print(x)
```

---

### F602

**Description**: Variable non définie.

---

### F621

**Description**: Arguments non utilisés.

**Corrected Example**:

```python
def f(x):
    return x
```

---

### F622

**Description**: Fonction non utilisée.

---

### F631

**Description**: Assert with tuple (always true).

**Corrected Example**:

```python
assert x and y
```

---

### F632

**Description**: Utilisation de input().

**Best Practices**: Use `argparse` or `click` for CLI tools.

---

### F633

**Description**: Utilisation de print().

**Best Practices**: Utiliser logging module.

---

### F634

**Description**: If condition with tuple (always evaluates to True).

**Corrected Example**:

```python
if x and y:
    pass
```

---

### F701-F702

**Description**: Break/Continue hors boucle.

---

### F704

**Description**: Yield hors fonction.

**Corrected Example**:

```python
def gen():
    yield 42
```

---

### F706

**Description**: Return hors fonction.

---

### F811

**Description**: Variable redéfinie.

---

### F821

**Description**: Variable non définie.

---

### F841

**Description**: Variable locale non utilisée.

**Corrected Example**: Supprimer la variable.

---

### F901

**Description**: Return with value in `__init__`.

**Corrected Example**:

```python
def __init__(self):
    self.x = 42
```

---

[↑ Back to Table of Contents](#table-of-contents)

---

## Family W - Style Warnings (PyCodestyle)

> **Plugin** : Intégré

### Table of W Codes


| Code | Description | Severity |
| ------------- | ------------------------------------ | ------------- |
| [W191](#w191) | Indentation using tabs         | Warning |
| [W291](#w291) | Espaces de fin de ligne              | Warning |
| [W292](#w292) | Nouvelle ligne manquante fin fichier | Warning |
| [W391](#w391) | Saut de ligne vide fin fichier       | Warning |
| [W503](#w503) | Espace avant opérateur binaire       | Warning |
| [W504](#w504) | Espace après opérateur binaire       | Warning |


---

### W191

**Description**: Indentation using tabs.

**Corrected Example**: Utiliser des espaces.

---

### W291

**Description**: Espaces de fin de ligne.

**Corrected Example**:

```python
x = 5
```

---

### W292

**Description**: Nouvelle ligne manquante en fin de fichier.

**Explanation**: POSIX recommande que les fichiers se terminent par une nouvelle ligne.

---

### W391

**Description**: Saut de ligne vide en fin de fichier.

---

### W503-W504

**Description**: Espaces autour opérateurs binaires continuations.

**Explanation**: Choisir un style. Configurer `ignore = W503` ou `ignore = W504`.

---

[↑ Back to Table of Contents](#table-of-contents)

---

## Family C90 - Cyclomatic Complexity (McCabe)

> **Plugin** : Intégré (McCabe)

### C901

**Description**: Fonction trop complexe (&gt;10 par défaut).

**Corrected Example**: Refactorer en fonctions plus petites.

**Best Practices**:

- Garder complexité &lt; 10
- Éviter les if imbriqués
- Configurer : `max-complexity = 15`

**Références** : [McCabe Complexity](https://en.wikipedia.org/wiki/Cyclomatic_complexity)

---

[↑ Back to Table of Contents](#table-of-contents)

---

## Family B - Bugbear (Security & Style)

> **Plugin** : ✱ `flake8-bugbear` | **Installation** : `pip install flake8-bugbear` | **Doc** : [Bugbear](https://github.com/PyCQA/flake8-bugbear)

### Table of B Codes


| Code          | Description                        | Sévérité      | Catégorie   |
| ------------- | ---------------------------------- | ------------- | ----------- |
| [B001](#b001) | Nom variable boucle non descriptif | Warning | Nommage     |
| [B002](#b002) | Attribute access inside exception block      | Error | Sécurité    |
| [B003](#b003) | Utilisation os.system              | Warning | Sécurité    |
| [B004](#b004) | `subprocess` call with `shell=True` (security risk)         | Warning | Sécurité    |
| [B005](#b005) | strip() sans arguments             | Warning | Style       |
| [B006](#b006) | Opérateurs unaires avant appels    | Warning | Style       |
| [B008](#b008) | Function call in `if` condition             | Warning | Performance |
| [B009](#b009) | Function call inside loop condition         | Warning | Performance |
| [B010](#b010) | `assert` with literal string                 | Error | Assertions  |
| [B012](#b012) | Comparison to True/False        | Warning | Style       |
| [B013](#b013) | Comparison to None              | Warning | Style       |
| [B015](#b015) | `len()` check in condition               | Warning | Performance |
| [B017](#b017) | assertRaises(Exception)            | Warning | Tests       |
| [B020](#b020) | `getattr` with default value     | Warning | Style       |
| [B023](#b023) | Fonction sans return               | Warning | Fonctions   |
| [B024](#b024) | Classe abstraite sans ABC          | Warning | Classes     |


---

### B001

**Description**: Nom de variable de boucle non descriptif.

**Corrected Example**:

```python
for index in range(10):
    print(index)
# ou
for _ in range(10):
    print("Hello")
```

---

### B002

**Description**: Accès à un attribut dans une exception.

**Corrected Example**:

```python
try:
    x = obj.attr
except AttributeError as e:
    print(str(e))
```

---

### B003

**Description**: Utilisation de os.system.

**Corrected Example**:

```python
import subprocess
subprocess.run(["ls", "-la"], check=True)
```

---

### B004

**Description**: `subprocess` call with `shell=True` (security risk).

**Corrected Example**:

```python
subprocess.run(["ls", "-la"], shell=False)
```

---

### B005

**Description**: strip() sans arguments.

**Corrected Example**:

```python
clean = text.strip(" ")
```

---

### B006

**Description**: Opérateurs unaires avant appels.

**Corrected Example**:

```python
x = -1 * len([1, 2, 3])
```

---

### B008

**Description**: Appel de fonction dans if.

**Corrected Example**:

```python
if lst:
    pass
```

---

### B009

**Description**: Appel de fonction dans boucle.

**Corrected Example**:

```python
for item in lst:
    print(item)
```

---

### B010

**Description**: `assert` with literal string.

**Corrected Example**:

```python
assert x > 0, "x doit être positif"
```

---

### B012

**Description**: Comparison to True/False.

**Corrected Example**:

```python
if x:
    pass
```

---

### B013

**Description**: Comparison to None.

**Corrected Example**:

```python
if x is None:
    pass
```

---

### B015

**Description**: `len()` check in condition.

**Corrected Example**:

```python
if lst:
    pass
```

---

### B017

**Description**: assertRaises(Exception).

**Corrected Example**:

```python
with self.assertRaises(ValueError):
    pass
```

---

### B020

**Description**: `getattr` with default value.

**Corrected Example**:

```python
try:
    x = obj.attr
except AttributeError:
    x = None
```

---

### B023

**Description**: Fonction sans return.

**Corrected Example**:

```python
def f(x, y):
    return x + y
```

---

### B024

**Description**: Classe abstraite sans ABC.

**Corrected Example**:

```python
from abc import ABC, abstractmethod

class MaClasse(ABC):
    @abstractmethod
    def methode(self):
        pass
```

---

[↑ Back to Table of Contents](#table-of-contents)

---

## Family N - Naming (Naming Conventions)

> **Plugin** : ✱ `flake8-naming` | **Installation** : `pip install flake8-naming` | **Doc** : [Naming](https://github.com/PyCQA/flake8-naming)

### Table of N Codes


| Code          | Description                  | Convention |
| ------------- | ---------------------------- | ---------- |
| [N801](#n801) | Nom classe non CamelCase     | PEP 8      |
| [N802](#n802) | Nom fonction non snake\_case | PEP 8      |
| [N803](#n803) | Nom variable non snake\_case | PEP 8      |
| [N804](#n804) | Nom module CamelCase         | PEP 8      |
| [N805](#n805) | Nom variable majuscules      | PEP 8      |
| [N811](#n811) | Nom constant non majuscules  | PEP 8      |


---

### N801

**Description**: Nom de classe non en CamelCase.

**Corrected Example**:

```python
class MaClasse:
    pass
```

---

### N802

**Description**: Nom de fonction non en snake\_case.

**Corrected Example**:

```python
def ma_fonction():
    pass
```

---

### N803

**Description**: Nom de variable non en snake\_case.

**Corrected Example**:

```python
ma_variable = 5
```

---

### N804

**Description**: Nom de module en CamelCase.

**Corrected Example**: `mon_module.py`

---

### N805

**Description**: Nom de variable en majuscules.

**Corrected Example**:

```python
MAX_VALUE = 100  # Constante
max_value = 50   # Variable
```

---

### N811

**Description**: Nom constant non en majuscules.

**Corrected Example**:

```python
MAX_VALUE = 100
```

---

[↑ Back to Table of Contents](#table-of-contents)

---

## Family ANN - Annotations (Static Type Hints)

> **Plugin** : ✱ `flake8-annotations` | **Installation** : `pip install flake8-annotations` | **Doc** : [Annotations](https://github.com/sdeors/flake8-annotations)

### Table of ANN Codes


| Code              | Description                   | Type      |
| ----------------- | ----------------------------- | --------- |
| [ANN001](#ann001) | Annotation manquante argument | Fonctions |
| [ANN002](#ann002) | Annotation manquante retour   | Fonctions |
| [ANN003](#ann003) | Annotation manquante variable | Variables |
| [ANN101](#ann101) | Annotation manquante self     | Méthodes  |
| [ANN102](#ann102) | Annotation manquante cls      | Méthodes  |
| [ANN401](#ann401) | Utilisation Any               | Typage    |


---

### ANN001

**Description**: Annotation manquante pour un argument.

**Corrected Example**:

```python
def fonction(x: int, y: int) -> int:
    return x + y
```

---

### ANN002

**Description**: Annotation manquante pour la valeur de retour.

---

### ANN003

**Description**: Annotation manquante pour une variable.

**Corrected Example**:

```python
x: int = 5
```

---

### ANN101

**Description**: Annotation manquante pour self.

**Corrected Example**:

```python
class MaClasse:
    def methode(self: "MaClasse") -> None:
        pass
```

---

### ANN102

**Description**: Annotation manquante pour cls.

**Corrected Example**:

```python
@classmethod
def methode(cls: type["MaClasse"]) -> None:
    pass
```

---

### ANN401

**Description**: Utilisation de Any.

**Corrected Example**:

```python
from typing import Union

def fonction(x: Union[int, str]) -> Union[int, str]:
    return x
```

---

[↑ Back to Table of Contents](#table-of-contents)

---

## Family COM - Comprehensions (Optimizations)

> **Plugin** : ✱ `flake8-comprehensions` | **Installation** : `pip install flake8-comprehensions` | **Doc** : [Comprehensions](https://github.com/Rars0/flake8-comprehensions)

### Table of COM Codes


| Code              | Description                    | Optimisation |
| ----------------- | ------------------------------ | ------------ |
| [COM810](#com810) | range(len(...)) simplifiable   | Performance  |
| [COM812](#com812) | Liste peut être ensemble       | Performance  |
| [COM813](#com813) | Liste peut être dictionnaire   | Performance  |
| [COM814](#com814) | Liste compréhension inutiles   | Performance  |
| [COM815](#com815) | dict.keys() dans compréhension | Performance  |


---

### COM810

**Description**: range(len(...)) peut être simplifié.

**Corrected Example**:

```python
for item in lst:
    print(item)
# ou
for i, item in enumerate(lst):
    print(i, item)
```

---

### COM812

**Description**: Liste peut être un ensemble.

**Corrected Example**:

```python
s = {x * 2 for x in range(10)}
```

---

### COM813

**Description**: Liste peut être un dictionnaire.

**Corrected Example**:

```python
d = {x: x * 2 for x in range(10)}
```

---

### COM814

**Description**: Liste compréhension inutiles.

**Corrected Example**:

```python
gen = (x * 2 for x in range(1000000))
```

---

### COM815

**Description**: dict.keys() dans compréhension.

**Corrected Example**:

```python
for key in d:
    print(key)
```

---

[↑ Back to Table of Contents](#table-of-contents)

---

## Family D - Docstrings (Documentation)

> **Plugin** : ✱ `flake8-docstrings` | **Installation** : `pip install flake8-docstrings` | **Doc** : [Docstrings](https://github.com/PyCQA/flake8-docstrings)

### Table of D Codes


| Code          | Description                  | Convention    |
| ------------- | ---------------------------- | ------------- |
| [D100](#d100) | Docstring manquante module   | Documentation |
| [D101](#d101) | Docstring manquante classe   | Documentation |
| [D102](#d102) | Docstring manquante méthode  | Documentation |
| [D103](#d103) | Docstring manquante fonction | Documentation |
| [D205](#d205) | Docstring saut ligne début   | Format        |


---

### D100

**Description**: Docstring manquante pour un module.

**Corrected Example**:

```python
"""Module pour les opérations sur les fichiers."""
import os
```

---

### D101

**Description**: Docstring manquante pour une classe.

**Corrected Example**:

```python
class MaClasse:
    """Description de la classe."""
    pass
```

---

### D102

**Description**: Docstring manquante pour une méthode publique.

**Corrected Example**:

```python
def methode(self):
    """Description de la méthode."""
    pass
```

---

### D205

**Description**: Docstring avec saut de ligne au début.

**Corrected Example**:

```python
def f():
    """Description.
    
    Détails.
    """
    pass
```

---

[↑ Back to Table of Contents](#table-of-contents)

---

## Family I - Isort (Import Sorting)

> **Plugin** : ✱ `flake8-isort` | **Installation** : `pip install flake8-isort` | **Doc** : [Isort](https://github.com/PyCQA/isort)

### Table of I Codes


| Code          | Description                        | Catégorie  |
| ------------- | ---------------------------------- | ---------- |
| [I001](#i001) | Imports unsorted                  | Tri        |
| [I002](#i002) | Imports non groupés                | Groupement |
| [I201](#i201) | Missing blank line entre groupes | Format     |


---

### I001

**Description**: Imports unsorted.

**Corrected Example**:

```python
import os
import sys
```

**Explanation**: isort trie par : standard → third-party → local.

---

### I201

**Description**: Missing blank line entre groupes.

**Corrected Example**:

```python
import os
import sys

import numpy
```

---

[↑ Back to Table of Contents](#table-of-contents)

---

## Family PIE - Pie (Optimizations)

> **Plugin** : ✱ `flake8-pie` | **Installation** : `pip install flake8-pie` | **Doc** : [Pie](https://github.com/str42/flake8-pie)

### Table of PIE Codes


| Code              | Description            | Optimisation |
| ----------------- | ---------------------- | ------------ |
| [PIE788](#pie788) | == pour comparer None  | Style        |
| [PIE789](#pie789) | != pour comparer None  | Style        |
| [PIE796](#pie796) | `len()` check in condition   | Performance  |
| [PIE798](#pie798) | == pour comparer types | Style        |


---

### PIE788

**Description**: Utilisation de == pour comparer avec None.

**Corrected Example**:

```python
if x is None:
    pass
```

---

### PIE796

**Description**: Utilisation de len() dans une condition.

**Corrected Example**:

```python
if lst:
    pass
```

---

### PIE798

**Description**: Utilisation de == pour comparer des types.

**Corrected Example**:

```python
if isinstance(x, int):
    pass
```

---

[↑ Back to Table of Contents](#table-of-contents)

---

## Family SIM - Simplify (Code Simplifications)

> **Plugin** : ✱ `flake8-simplify` | **Installation** : `pip install flake8-simplify` | **Doc** : [Simplify](https://github.com/MartijnBraam/flake8-simplify)

### Table of SIM Codes


| Code              | Description         | Simplification |
| ----------------- | ------------------- | -------------- |
| [SIM108](#sim108) | if ternaire         | Style          |
| [SIM115](#sim115) | open sans with      | Sécurité       |
| [SIM116](#sim116) | dict sans littéral  | Style          |
| [SIM118](#sim118) | in avec dict.keys() | Performance    |


---

### SIM108

**Description**: Utilisation de if ternaire.

**Corrected Example**:

```python
x = a if condition else b
```

---

### SIM115

**Description**: Utilisation de open sans with.

**Corrected Example**:

```python
with open("fichier.txt") as f:
    data = f.read()
```

---

### SIM116

**Description**: Utilisation de dict sans littéral.

**Corrected Example**:

```python
d = {"a": 1, "b": 2}
```

---

### SIM118

**Description**: Utilisation de in avec dict.keys().

**Corrected Example**:

```python
if key in d:
    pass
```

---

[↑ Back to Table of Contents](#table-of-contents)

---

## Family UP - Pyupgrade (Code Modernization)

> **Plugin** : ✱ `flake8-pyupgrade` | **Installation** : `pip install flake8-pyupgrade` | **Doc** : [Pyupgrade](https://github.com/asottile/pyupgrade)

### Table of UP Codes


| Code            | Description        | Modernisation |
| --------------- | ------------------ | ------------- |
| [UP001](#up001) | % pour formatage   | Strings       |
| [UP002](#up002) | .format()          | Strings       |
| [UP003](#up003) | dict()             | Littéraux     |
| [UP005](#up005) | list()             | Littéraux     |
| [UP017](#up017) | range(len(...))    | Boucles       |
| [UP020](#up020) | open sans encoding | Fichiers      |


---

### UP001

**Description**: Utilisation de % pour formatage.

**Corrected Example**:

```python
print(f"Hello, {name}!")
```

---

### UP002

**Description**: Utilisation de .format().

**Corrected Example**:

```python
print(f"Hello, {name}!")
```

---

### UP003

**Description**: Utilisation de dict().

**Corrected Example**:

```python
d = {}
```

---

### UP005

**Description**: Utilisation de list().

**Corrected Example**:

```python
lst = []
```

---

### UP017

**Description**: Utilisation de range(len(...)).

**Corrected Example**:

```python
for item in lst:
    print(item)
```

---

### UP020

**Description**: Utilisation de open sans encoding.

**Corrected Example**:

```python
with open("fichier.txt", encoding="utf-8") as f:
    pass
```

---

[↑ Back to Table of Contents](#table-of-contents)

---

## Automated Formatting & Fixing Tools

### Black

> **Site** : [https://github.com/psf/black](https://github.com/psf/black) | **Installation** : `pip install black`

Formateur **opinionné** qui reformate automatiquement selon PEP 8.

**Configuration** (pyproject.toml) :

```toml
[tool.black]
line-length = 88
target-version = ['py310']
```

**Commandes** :

```bash
black .
black --check .
```

**✅ Avantages** : Rapide, déterministe, compatible.  
**❌ Inconvénients** : Peu de personnalisation, ne corrige pas toutes les erreurs Flake8.

---

### Ruff

> **Site** : [https://github.com/astral-sh/ruff](https://github.com/astral-sh/ruff) | **Installation** : `pip install ruff`

Linter et formateur **ultra-rapide** écrit en Rust.

**Configuration** (pyproject.toml) :

```toml
[tool.ruff]
line-length = 88
select = ["E", "F", "W", "C90", "I", "N", "UP", "B", "SIM"]
fixable = ["ALL"]

[tool.ruff.format]
quote-style = "double"
```

**Commandes** :

```bash
ruff check .
ruff check --fix .
ruff format .
```

**✅ Avantages** : **Extrêmement rapide** (10-100x Flake8), correction automatique, intègre Black/isort/pyupgrade.

---

### autopep8

> **Site** : [https://github.com/hhatto/autopep8](https://github.com/hhatto/autopep8) | **Installation** : `pip install autopep8`

Correcteur automatique des erreurs PEP 8.

**Commandes** :

```bash
autopep8 --in-place --aggressive mon_fichier.py
```

---

### isort

> **Site** : [https://github.com/PyCQA/isort](https://github.com/PyCQA/isort) | **Installation** : `pip install isort`

Trieur et formateur d'imports.

**Configuration** (pyproject.toml) :

```toml
[tool.isort]
profile = "black"
line_length = 88
```

**Commandes** :

```bash
isort .
isort --check-only .
```

---

### pyupgrade

> **Site** : [https://github.com/asottile/pyupgrade](https://github.com/asottile/pyupgrade) | **Installation** : `pip install pyupgrade`

Modernisateur de code Python.

**Commandes** :

```bash
pyupgrade --py310-plus .
```

---

### Tool Comparison


| Outil    | Type                 | Vitesse         | Correction | Config |
| -------- | -------------------- | --------------- | ---------- | ------ |
| Flake8   | Linter               | Moyenne         | ❌ Non      | ⚠️     |
| Black    | Formatter            | Rapide          | ✅ Oui      | ❌      |
| **Ruff** | **Linter+Formatter** | **Très rapide** | ✅ Oui      | ⚠️     |
| autopep8 | Formatter            | Moyenne         | ✅ Oui      | ✅      |
| isort    | Import Sorter        | Rapide          | ✅ Oui      | ✅      |


---

### Recommandations

1. **Nouveaux projets** : **Ruff** (linter + formateur)
2. **Projets existants** : Flake8 + Black + isort
3. **Configuration recommandée** (pyproject.toml) :
  ```toml
   [tool.ruff]
   line-length = 88
   select = ["E", "F", "W", "C90", "I", "N", "UP", "B", "SIM", "COM", "D"]
   fixable = ["ALL"]
  ```
4. **CI/CD** :
  ```yaml
   # .github/workflows/lint.yml
   - run: pip install ruff
   - run: ruff check .
   - run: ruff format --check .
  ```
5. **pre-commit** :
  ```yaml
   repos:
     - repo: https://github.com/astral-sh/ruff-pre-commit
       hooks:
         - id: ruff
           args: [--fix, --exit-non-zero-on-fix]
         - id: ruff-format
  ```

---

## References & Bibliography

### Official Documentation

- [PEP 8](https://peps.python.org/pep-0008/)
- [Flake8](https://flake8.pycqa.org/en/latest/)
- [PyCodestyle](https://pycodestyle.pycqa.org/en/latest/)
- [PyFlakes](https://pypi.org/project/pyflakes/)

### Plugins

- [flake8-bugbear](https://github.com/PyCQA/flake8-bugbear)
- [flake8-naming](https://github.com/PyCQA/flake8-naming)
- [flake8-annotations](https://github.com/sdeors/flake8-annotations)
- [flake8-comprehensions](https://github.com/Rars0/flake8-comprehensions)
- [flake8-docstrings](https://github.com/PyCQA/flake8-docstrings)
- [flake8-isort](https://github.com/PyCQA/flake8-isort)
- [flake8-pie](https://github.com/str42/flake8-pie)
- [flake8-simplify](https://github.com/MartijnBraam/flake8-simplify)
- [flake8-pyupgrade](https://github.com/asottile/pyupgrade)

### Outils

- [Black](https://github.com/psf/black)
- [Ruff](https://github.com/astral-sh/ruff)
- [autopep8](https://github.com/hhatto/autopep8)
- [isort](https://github.com/PyCQA/isort)
- [mypy](https://mypy-lang.org/)

### Ressources

- [Flake8 Rules Explained](https://www.flake8rules.com/)
- [PEP 8 Cheat Sheet](https://gist.github.com/roachhd/d11830d0b4b49d87a024)
- [The Ultimate Guide to Linting in Python](https://realpython.com/python-linting/)

### Livres

- "Clean Code in Python" - James Padolsey
- "Effective Python" - Brett Slatkin

---

*Document généré le 20 juillet 2026. Pour les mises à jour, consulter les documentations officielles.*
