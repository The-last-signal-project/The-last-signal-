# Guide complet des erreurs Flake8

> **Document de référence professionnel** pour la compréhension et la correction des erreurs Flake8 en Python.  
>

---

## Sommaire

- [Introduction](#introduction)
- [Tableau récapitulatif global](#tableau-récapitulatif-global)
- [Famille E - Erreurs de style (PyCodestyle)](#famille-e---erreurs-de-style-pycodestyle)
- [Famille F - Erreurs logiques (PyFlakes)](#famille-f---erreurs-logiques-pyflakes)
- [Famille W - Avertissements de style (PyCodestyle)](#famille-w---avertissements-de-style-pycodestyle)
- [Famille C90 - Complexité cyclomatique (McCabe)](#famille-c90---complexité-cyclomatique-mccabe)
- [Famille B - Bugbear (Extensions de sécurité et style)](#famille-b---bugbear-extensions-de-sécurité-et-style)
- [Famille N - Naming (Conventions de nommage)](#famille-n---naming-conventions-de-nommage)
- [Famille ANN - Annotations (Typage statique)](#famille-ann---annotations-typage-statique)
- [Famille COM - Comprehensions (Optimisations)](#famille-com---comprehensions-optimisations)
- [Famille D - Docstrings (Documentation)](#famille-d---docstrings-documentation)
- [Famille I - Isort (Tri des imports)](#famille-i---isort-tri-des-imports)
- [Famille PIE - Pie (Optimisations diverses)](#famille-pie---pie-optimisations-diverses)
- [Famille SIM - Simplify (Simplifications)](#famille-sim---simplify-simplifications)
- [Famille UP - Pyupgrade (Modernisation du code)](#famille-up---pyupgrade-modernisation-du-code)
- [Outils de correction automatique](#outils-de-correction-automatique)
- [Bibliographie](#bibliographie)

---

## Introduction

**Flake8** est un outil d'analyse statique pour Python qui combine :

- **PyCodestyle** (PEP 8) : conformité au guide de style
- **PyFlakes** : détection d'erreurs logiques
- **McCabe** : mesure de complexité cyclomatique

Codes d'erreur format : `[FAMILLE][NUMERO]`

---

## Tableau récapitulatif global


| Famille | Plugin                | Catégorie       | Codes | Exemple |
| ------- | --------------------- | --------------- | ----- | ------- |
| E       | -                     | Style           | \~50  | E128    |
| F       | -                     | Logique         | \~25  | F401    |
| W       | -                     | Avertissements  | \~15  | W291    |
| C90     | -                     | Complexité      | 1     | C901    |
| B       | flake8-bugbear        | Sécurité        | \~35  | B007    |
| N       | flake8-naming         | Nommage         | \~25  | N801    |
| ANN     | flake8-annotations    | Typage          | \~15  | ANN001  |
| COM     | flake8-comprehensions | Optimisations   | \~10  | COM812  |
| D       | flake8-docstrings     | Documentation   | \~20  | D100    |
| I       | flake8-isort          | Imports         | \~10  | I001    |
| PIE     | flake8-pie            | Optimisations   | \~30  | PIE798  |
| SIM     | flake8-simplify       | Simplifications | \~35  | SIM101  |
| UP      | flake8-pyupgrade      | Modernisation   | \~30  | UP001   |


---

## Famille E - Erreurs de style (PyCodestyle)

> **Plugin** : Intégré | **Doc** : [PEP 8](https://peps.python.org/pep-0008/)

### Tableau des codes E


| Code          | Description                          | Sévérité      |
| ------------- | ------------------------------------ | ------------- |
| [E101](#e101) | Indentation mélangeant des tabulations et des espaces       | Erreur        |
| [E111](#e111) | Indentation incorrecte ( il faut quatre espaces)              | Erreur        |
| [E112](#e112) | block d'indentation inattendue                 | Erreur        |
| [E113](#e113) | Indentation inattendue          | Erreur        |
| [E114](#e114) | Indentation commentaire  incorecte cf. E111               | Erreur        |
| [E115](#e115) | block d'indentation incorrecte commentaire  cf.E112 | Erreur        |
| [E116](#e116) | Indentation inattendue pour les commentaires cf.E113         | Erreur        |
| [E117](#e117) | Indentation excessive                | Erreur        |
| [E121](#e121) | Alignement incorrect                 | Avertissement |
| [E131](#e131) | Lignes vides commentaires            | Avertissement |
| [E133](#e133) | Espaces incorrects slices            | Erreur        |
| [E201](#e201) | Espace manquant après (              | Erreur        |
| [E202](#e202) | Espace manquant avant )              | Erreur        |
| [E203](#e203) | Espace manquant avant ,              | Erreur        |
| [E211](#e211) | Espaces opérateurs                   | Erreur        |
| [E221](#e221) | Espaces multiples opérateurs         | Erreur        |
| [E222](#e222) | Espace manquant opérateurs           | Erreur        |
| [E223](#e223) | Tabulation avant un opérateur                 | Erreur        |
| [E224](#e224) | Tabulation après un  opérateur              | Erreur        |
| [E231](#e231) | Espace manquant après ":" "," ou ";"              | Erreur        |
| [E241](#e241) | Espaces multiples après ,            | Erreur        |
| [E242](#e242) | Espace manquant après ,              | Erreur        |
| [E261](#e261) | Espace avant commentaire             | Avertissement |
| [E262](#e262) | Espace manquant commentaire          | Avertissement |
| [E265](#e265) | Espace manquant bloc commentaire     | Avertissement |
| [E266](#e266) | Espaces multiples commentaire        | Avertissement |
| [E271](#e271) | Espaces multiples mot-clé            | Erreur        |
| [E301](#e301) | Ligne vide manquante                 | Avertissement |
| [E302](#e302) | Lignes vides excessives              | Avertissement |
| [E401](#e401) | Import multiple ligne                | Erreur        |
| [E402](#e402) | Import multi-lignes                  | Erreur        |
| [E501](#e501) | Ligne trop longue                    | Erreur        |
| [E502](#e502) | Backslash inutile                    | Avertissement |
| [E701](#e701) | Deux points manquants slice          | Erreur        |
| [E703](#e703) | Point-virgule avant commentaire      | Avertissement |
| [E704](#e704) | Plusieurs instructions ligne         | Erreur        |
| [E711](#e711) | Comparaison avec None                | Erreur        |
| [E712](#e712) | Comparaison avec True/False          | Erreur        |
| [E721](#e721) | Comparaison de types                 | Erreur        |
| [E722](#e722) | `is` pour comparer littéraux         | Erreur        |
| [E731](#e731) | Assigner une lambda                  | Erreur        |


---

### E101

**Description** : Indentation non cohérente.

**Cause** : Mélange d'espaces et de tabulations.

**Exemple incorrect**

```python
def fonction():
    if True:
        print("Hello")
    else:
	print("World")
```

**Exemple corrigé**

```python
def fonction():
    if True:
        print("Hello")
    else:
        print("World")
```

**Explication** : PEP 8 recommande **4 espaces par niveau**.

**Bonnes pratiques** : Configurer `.editorconfig` : `indent_style = space` et `indent_size = 4`

---

### E111

**Description** : Indentation incorrecte.

**Exemple incorrect**

```python
def fonction():
  if True:
    print("Hello")
```

**Exemple corrigé**

```python
def fonction():
    if True:
        print("Hello")
```

---

### E112

**Description** : Indentation attendue manquante.

**Exemple incorrect**

```python
def fonction():
if True:
    print("Hello")
```

**Exemple corrigé**

```python
def fonction():
    if True:
        print("Hello")
```

---

### E113

**Description** : Indentation non attendue.

**Exemple incorrect**

```python
def fonction():
    if True:
        print("Hello")
    print("World")
```

**Exemple corrigé**

```python
def fonction():
    if True:
        print("Hello")
    print("World")
```

---

### E114-E116

**Description** : Problèmes d'indentation avec commentaires.

**Exemple corrigé** : Aligner les commentaires avec le code.

---

### E117

**Description** : Indentation excessive.

**Exemple corrigé** : Utiliser 4 espaces par niveau.

---

### E121

**Description** : Alignement incorrect.

**Exemple incorrect**

```python
x    = 1
yy   = 2
```

**Exemple corrigé**

```python
x = 1
yy = 2
```

**Explication** : PEP 8 recommande de **ne pas aligner** les opérateurs.

---

### E122-E129

**Description** : Problèmes d'alignement.

---

### E131

**Description** : Lignes vides autour des commentaires.

**Exemple corrigé** : 0 ligne avant commentaire en ligne, 1 ligne avant bloc.

---

### E133

**Description** : Espaces incorrects dans les slices.

**Exemple incorrect**

```python
lst[1 : 5]
lst[1:5 : 2]
```

**Exemple corrigé**

```python
lst[1:5]
lst[1:5:2]
```

---

### E201

**Description** : Espace manquant après (.

**Exemple corrigé** :

```python
if (x > 5):
```

---

### E202

**Description** : Espace manquant avant ).

---

### E203

**Description** : Espace manquant avant ,.

**Exemple corrigé** :

```python
lst = [1, 2, 3]
```

---

### E211

**Description** : Espaces autour des opérateurs.

**Exemple incorrect**

```python
x=5
x =5
x= 5
x  =  5
```

**Exemple corrigé**

```python
x = 5
```

**Explication** : PEP 8 : **un espace de chaque côté** des opérateurs binaires.  
**Exceptions** : unaires (`-5`), slices (`[1:5]`).

---

### E221-E228

**Description** : Espaces incorrects autour opérateurs.

---

### E231

**Description** : Espace manquant avant :.

---

### E241-E242

**Description** : Espaces incorrects après ,.

**Exemple corrigé** :

```python
lst = [1, 2, 3]
```

---

### E261-E266

**Description** : Espaces incorrects commentaires.

**Exemple corrigé** :

```python
x = 5  # Commentaire
```

**Explication** : **2 espaces** avant commentaire en ligne.

---

### E271-E275

**Description** : Espaces incorrects mots-clés.

---

### E301

**Description** : Ligne vide manquante.

**Exemple corrigé** :

```python
def f1():
    pass

def f2():
    pass
```

**Explication** : **2 lignes vides** entre définitions niveau supérieur.

---

### E302-E306

**Description** : Problèmes lignes vides.

---

### E401

**Description** : Import multiple sur une ligne.

**Exemple incorrect**

```python
import os, sys
```

**Exemple corrigé**

```python
import os
import sys
```

---

### E402

**Description** : Import multi-lignes mal formaté.

**Exemple corrigé** :

```python
from module import (
    name1,
    name2,
)
```

---

### E501

**Description** : Ligne trop longue (&gt;79 caractères par défaut).

**Exemple corrigé** :

```python
print(
    "Ligne très longue divisée en "
    "plusieurs parties"
)
```

**Bonnes pratiques** : Configurer `max-line-length = 88`

---

### E502

**Description** : Backslash inutile.

**Exemple corrigé** :

```python
x = (1 + 2 +
     3 + 4)
```

---

### E701-E702

**Description** : Deux points manquants dans slice.

---

### E703

**Description** : Point-virgule avant commentaire.

**Exemple corrigé** :

```python
x = 5
print(x)
```

---

### E704

**Description** : Plusieurs instructions sur une ligne.

**Exemple corrigé** :

```python
x = 5
y = 10
```

---

### E711

**Description** : Comparaison avec None.

**Exemple incorrect**

```python
if x == None:
    pass
```

**Exemple corrigé**

```python
if x is None:
    pass
```

**Références** : [PEP 8 - None](https://peps.python.org/pep-0008/#id53)

---

### E712

**Description** : Comparaison avec True/False.

**Exemple corrigé** :

```python
if x:  # au lieu de if x == True:
    pass
```

---

### E713-E714

**Description** : Test d'appartenance avec None/True/False.

---

### E721

**Description** : Comparaison de types.

**Exemple corrigé** :

```python
if isinstance(x, int):
    pass
```

---

### E722

**Description** : Ne pas utiliser `is` pour comparer littéraux.

**Exemple corrigé** :

```python
if x == 5:
    pass
```

---

### E731

**Description** : Ne pas assigner une lambda.

**Exemple corrigé** :

```python
def f(x):
    return x + 1
```

---

[↑ Retour au sommaire](#sommaire)

---

## Famille F - Erreurs logiques (PyFlakes)

> **Plugin** : Intégré | **Doc** : [PyFlakes](https://pypi.org/project/pyflakes/)

### Tableau des codes F


| Code          | Description                        | Sévérité      | Catégorie   |
| ------------- | ---------------------------------- | ------------- | ----------- |
| [F401](#f401) | Import inutilisé                   | Erreur        | Imports     |
| [F403](#f403) | Import avec \*                     | Avertissement | Imports     |
| [F405](#f405) | Import en double                   | Erreur        | Imports     |
| [F601](#f601) | Variable utilisée avant définition | Erreur        | Variables   |
| [F602](#f602) | Variable non définie               | Erreur        | Variables   |
| [F621](#f621) | Arguments non utilisés             | Avertissement | Fonctions   |
| [F622](#f622) | Fonction non utilisée              | Avertissement | Fonctions   |
| [F631](#f631) | Assertion avec tuple               | Erreur        | Assertions  |
| [F632](#f632) | Utilisation de input()             | Avertissement | Sécurité    |
| [F633](#f633) | Utilisation de print()             | Avertissement | Style       |
| [F634](#f634) | If avec tuple                      | Avertissement | Conditions  |
| [F701](#f701) | Break hors boucle                  | Erreur        | Contrôle    |
| [F702](#f702) | Continue hors boucle               | Erreur        | Contrôle    |
| [F704](#f704) | Yield hors fonction                | Erreur        | Générateurs |
| [F706](#f706) | Return hors fonction               | Erreur        | Contrôle    |
| [F811](#f811) | Variable redéfinie                 | Avertissement | Variables   |
| [F821](#f821) | Variable non définie               | Erreur        | Variables   |
| [F841](#f841) | Variable locale non utilisée       | Avertissement | Variables   |
| [F901](#f901) | Return avec valeur dans **init**   | Erreur        | Classes     |


---

### F401

**Description** : Import inutilisé.

**Exemple incorrect**

```python
import os  # Non utilisé
import sys
```

**Exemple corrigé**

```python
import sys
```

---

### F403

**Description** : Import avec \*.

**Exemple incorrect**

```python
from os import *
```

**Exemple corrigé**

```python
from os import path, environ
```

---

### F405

**Description** : Import en double.

---

### F601

**Description** : Variable utilisée avant définition.

**Exemple corrigé** :

```python
x = 5
print(x)
```

---

### F602

**Description** : Variable non définie.

---

### F621

**Description** : Arguments non utilisés.

**Exemple corrigé** :

```python
def f(x):
    return x
```

---

### F622

**Description** : Fonction non utilisée.

---

### F631

**Description** : Assertion avec tuple.

**Exemple corrigé** :

```python
assert x and y
```

---

### F632

**Description** : Utilisation de input().

**Bonnes pratiques** : Utiliser argparse/click pour CLI.

---

### F633

**Description** : Utilisation de print().

**Bonnes pratiques** : Utiliser logging module.

---

### F634

**Description** : If avec tuple.

**Exemple corrigé** :

```python
if x and y:
    pass
```

---

### F701-F702

**Description** : Break/Continue hors boucle.

---

### F704

**Description** : Yield hors fonction.

**Exemple corrigé** :

```python
def gen():
    yield 42
```

---

### F706

**Description** : Return hors fonction.

---

### F811

**Description** : Variable redéfinie.

---

### F821

**Description** : Variable non définie.

---

### F841

**Description** : Variable locale non utilisée.

**Exemple corrigé** : Supprimer la variable.

---

### F901

**Description** : Return avec valeur dans **init**.

**Exemple corrigé** :

```python
def __init__(self):
    self.x = 42
```

---

[↑ Retour au sommaire](#sommaire)

---

## Famille W - Avertissements de style

> **Plugin** : Intégré

### Tableau des codes W


| Code          | Description                          | Sévérité      |
| ------------- | ------------------------------------ | ------------- |
| [W191](#w191) | Indentation avec tabulations         | Avertissement |
| [W291](#w291) | Espaces de fin de ligne              | Avertissement |
| [W292](#w292) | Nouvelle ligne manquante fin fichier | Avertissement |
| [W391](#w391) | Saut de ligne vide fin fichier       | Avertissement |
| [W503](#w503) | Espace avant opérateur binaire       | Avertissement |
| [W504](#w504) | Espace après opérateur binaire       | Avertissement |


---

### W191

**Description** : Indentation avec tabulations.

**Exemple corrigé** : Utiliser des espaces.

---

### W291

**Description** : Espaces de fin de ligne.

**Exemple corrigé** :

```python
x = 5
```

---

### W292

**Description** : Nouvelle ligne manquante en fin de fichier.

**Explication** : POSIX recommande que les fichiers se terminent par une nouvelle ligne.

---

### W391

**Description** : Saut de ligne vide en fin de fichier.

---

### W503-W504

**Description** : Espaces autour opérateurs binaires continuations.

**Explication** : Choisir un style. Configurer `ignore = W503` ou `ignore = W504`.

---

[↑ Retour au sommaire](#sommaire)

---

## Famille C90 - Complexité cyclomatique

> **Plugin** : Intégré (McCabe)

### C901

**Description** : Fonction trop complexe (&gt;10 par défaut).

**Exemple corrigé** : Refactorer en fonctions plus petites.

**Bonnes pratiques** :

- Garder complexité &lt; 10
- Éviter les if imbriqués
- Configurer : `max-complexity = 15`

**Références** : [McCabe Complexity](https://en.wikipedia.org/wiki/Cyclomatic_complexity)

---

[↑ Retour au sommaire](#sommaire)

---

## Famille B - Bugbear (Sécurité et style)

> **Plugin** : ✱ `flake8-bugbear` | **Installation** : `pip install flake8-bugbear` | **Doc** : [Bugbear](https://github.com/PyCQA/flake8-bugbear)

### Tableau des codes B


| Code          | Description                        | Sévérité      | Catégorie   |
| ------------- | ---------------------------------- | ------------- | ----------- |
| [B001](#b001) | Nom variable boucle non descriptif | Avertissement | Nommage     |
| [B002](#b002) | Accès attribut dans exception      | Erreur        | Sécurité    |
| [B003](#b003) | Utilisation os.system              | Avertissement | Sécurité    |
| [B004](#b004) | subprocess avec shell=True         | Avertissement | Sécurité    |
| [B005](#b005) | strip() sans arguments             | Avertissement | Style       |
| [B006](#b006) | Opérateurs unaires avant appels    | Avertissement | Style       |
| [B008](#b008) | Appel fonction dans if             | Avertissement | Performance |
| [B009](#b009) | Appel fonction dans boucle         | Avertissement | Performance |
| [B010](#b010) | assert avec chaîne                 | Erreur        | Assertions  |
| [B012](#b012) | Comparaison avec True/False        | Avertissement | Style       |
| [B013](#b013) | Comparaison avec None              | Avertissement | Style       |
| [B015](#b015) | len() dans condition               | Avertissement | Performance |
| [B017](#b017) | assertRaises(Exception)            | Avertissement | Tests       |
| [B020](#b020) | getattr avec valeur par défaut     | Avertissement | Style       |
| [B023](#b023) | Fonction sans return               | Avertissement | Fonctions   |
| [B024](#b024) | Classe abstraite sans ABC          | Avertissement | Classes     |


---

### B001

**Description** : Nom de variable de boucle non descriptif.

**Exemple corrigé** :

```python
for index in range(10):
    print(index)
# ou
for _ in range(10):
    print("Hello")
```

---

### B002

**Description** : Accès à un attribut dans une exception.

**Exemple corrigé** :

```python
try:
    x = obj.attr
except AttributeError as e:
    print(str(e))
```

---

### B003

**Description** : Utilisation de os.system.

**Exemple corrigé** :

```python
import subprocess
subprocess.run(["ls", "-la"], check=True)
```

---

### B004

**Description** : subprocess avec shell=True.

**Exemple corrigé** :

```python
subprocess.run(["ls", "-la"], shell=False)
```

---

### B005

**Description** : strip() sans arguments.

**Exemple corrigé** :

```python
clean = text.strip(" ")
```

---

### B006

**Description** : Opérateurs unaires avant appels.

**Exemple corrigé** :

```python
x = -1 * len([1, 2, 3])
```

---

### B008

**Description** : Appel de fonction dans if.

**Exemple corrigé** :

```python
if lst:
    pass
```

---

### B009

**Description** : Appel de fonction dans boucle.

**Exemple corrigé** :

```python
for item in lst:
    print(item)
```

---

### B010

**Description** : assert avec chaîne.

**Exemple corrigé** :

```python
assert x > 0, "x doit être positif"
```

---

### B012

**Description** : Comparaison avec True/False.

**Exemple corrigé** :

```python
if x:
    pass
```

---

### B013

**Description** : Comparaison avec None.

**Exemple corrigé** :

```python
if x is None:
    pass
```

---

### B015

**Description** : len() dans condition.

**Exemple corrigé** :

```python
if lst:
    pass
```

---

### B017

**Description** : assertRaises(Exception).

**Exemple corrigé** :

```python
with self.assertRaises(ValueError):
    pass
```

---

### B020

**Description** : getattr avec valeur par défaut.

**Exemple corrigé** :

```python
try:
    x = obj.attr
except AttributeError:
    x = None
```

---

### B023

**Description** : Fonction sans return.

**Exemple corrigé** :

```python
def f(x, y):
    return x + y
```

---

### B024

**Description** : Classe abstraite sans ABC.

**Exemple corrigé** :

```python
from abc import ABC, abstractmethod

class MaClasse(ABC):
    @abstractmethod
    def methode(self):
        pass
```

---

[↑ Retour au sommaire](#sommaire)

---

## Famille N - Naming (Conventions de nommage)

> **Plugin** : ✱ `flake8-naming` | **Installation** : `pip install flake8-naming` | **Doc** : [Naming](https://github.com/PyCQA/flake8-naming)

### Tableau des codes N


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

**Description** : Nom de classe non en CamelCase.

**Exemple corrigé** :

```python
class MaClasse:
    pass
```

---

### N802

**Description** : Nom de fonction non en snake\_case.

**Exemple corrigé** :

```python
def ma_fonction():
    pass
```

---

### N803

**Description** : Nom de variable non en snake\_case.

**Exemple corrigé** :

```python
ma_variable = 5
```

---

### N804

**Description** : Nom de module en CamelCase.

**Exemple corrigé** : `mon_module.py`

---

### N805

**Description** : Nom de variable en majuscules.

**Exemple corrigé** :

```python
MAX_VALUE = 100  # Constante
max_value = 50   # Variable
```

---

### N811

**Description** : Nom constant non en majuscules.

**Exemple corrigé** :

```python
MAX_VALUE = 100
```

---

[↑ Retour au sommaire](#sommaire)

---

## Famille ANN - Annotations (Typage statique)

> **Plugin** : ✱ `flake8-annotations` | **Installation** : `pip install flake8-annotations` | **Doc** : [Annotations](https://github.com/sdeors/flake8-annotations)

### Tableau des codes ANN


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

**Description** : Annotation manquante pour un argument.

**Exemple corrigé** :

```python
def fonction(x: int, y: int) -> int:
    return x + y
```

---

### ANN002

**Description** : Annotation manquante pour la valeur de retour.

---

### ANN003

**Description** : Annotation manquante pour une variable.

**Exemple corrigé** :

```python
x: int = 5
```

---

### ANN101

**Description** : Annotation manquante pour self.

**Exemple corrigé** :

```python
class MaClasse:
    def methode(self: "MaClasse") -> None:
        pass
```

---

### ANN102

**Description** : Annotation manquante pour cls.

**Exemple corrigé** :

```python
@classmethod
def methode(cls: type["MaClasse"]) -> None:
    pass
```

---

### ANN401

**Description** : Utilisation de Any.

**Exemple corrigé** :

```python
from typing import Union

def fonction(x: Union[int, str]) -> Union[int, str]:
    return x
```

---

[↑ Retour au sommaire](#sommaire)

---

## Famille COM - Comprehensions (Optimisations)

> **Plugin** : ✱ `flake8-comprehensions` | **Installation** : `pip install flake8-comprehensions` | **Doc** : [Comprehensions](https://github.com/Rars0/flake8-comprehensions)

### Tableau des codes COM


| Code              | Description                    | Optimisation |
| ----------------- | ------------------------------ | ------------ |
| [COM810](#com810) | range(len(...)) simplifiable   | Performance  |
| [COM812](#com812) | Liste peut être ensemble       | Performance  |
| [COM813](#com813) | Liste peut être dictionnaire   | Performance  |
| [COM814](#com814) | Liste compréhension inutiles   | Performance  |
| [COM815](#com815) | dict.keys() dans compréhension | Performance  |


---

### COM810

**Description** : range(len(...)) peut être simplifié.

**Exemple corrigé** :

```python
for item in lst:
    print(item)
# ou
for i, item in enumerate(lst):
    print(i, item)
```

---

### COM812

**Description** : Liste peut être un ensemble.

**Exemple corrigé** :

```python
s = {x * 2 for x in range(10)}
```

---

### COM813

**Description** : Liste peut être un dictionnaire.

**Exemple corrigé** :

```python
d = {x: x * 2 for x in range(10)}
```

---

### COM814

**Description** : Liste compréhension inutiles.

**Exemple corrigé** :

```python
gen = (x * 2 for x in range(1000000))
```

---

### COM815

**Description** : dict.keys() dans compréhension.

**Exemple corrigé** :

```python
for key in d:
    print(key)
```

---

[↑ Retour au sommaire](#sommaire)

---

## Famille D - Docstrings (Documentation)

> **Plugin** : ✱ `flake8-docstrings` | **Installation** : `pip install flake8-docstrings` | **Doc** : [Docstrings](https://github.com/PyCQA/flake8-docstrings)

### Tableau des codes D


| Code          | Description                  | Convention    |
| ------------- | ---------------------------- | ------------- |
| [D100](#d100) | Docstring manquante module   | Documentation |
| [D101](#d101) | Docstring manquante classe   | Documentation |
| [D102](#d102) | Docstring manquante méthode  | Documentation |
| [D103](#d103) | Docstring manquante fonction | Documentation |
| [D205](#d205) | Docstring saut ligne début   | Format        |


---

### D100

**Description** : Docstring manquante pour un module.

**Exemple corrigé** :

```python
"""Module pour les opérations sur les fichiers."""
import os
```

---

### D101

**Description** : Docstring manquante pour une classe.

**Exemple corrigé** :

```python
class MaClasse:
    """Description de la classe."""
    pass
```

---

### D102

**Description** : Docstring manquante pour une méthode publique.

**Exemple corrigé** :

```python
def methode(self):
    """Description de la méthode."""
    pass
```

---

### D205

**Description** : Docstring avec saut de ligne au début.

**Exemple corrigé** :

```python
def f():
    """Description.
    
    Détails.
    """
    pass
```

---

[↑ Retour au sommaire](#sommaire)

---

## Famille I - Isort (Tri des imports)

> **Plugin** : ✱ `flake8-isort` | **Installation** : `pip install flake8-isort` | **Doc** : [Isort](https://github.com/PyCQA/isort)

### Tableau des codes I


| Code          | Description                        | Catégorie  |
| ------------- | ---------------------------------- | ---------- |
| [I001](#i001) | Imports non triés                  | Tri        |
| [I002](#i002) | Imports non groupés                | Groupement |
| [I201](#i201) | Ligne vide manquante entre groupes | Format     |


---

### I001

**Description** : Imports non triés.

**Exemple corrigé** :

```python
import os
import sys
```

**Explication** : isort trie par : standard → third-party → local.

---

### I201

**Description** : Ligne vide manquante entre groupes.

**Exemple corrigé** :

```python
import os
import sys

import numpy
```

---

[↑ Retour au sommaire](#sommaire)

---

## Famille PIE - Pie (Optimisations)

> **Plugin** : ✱ `flake8-pie` | **Installation** : `pip install flake8-pie` | **Doc** : [Pie](https://github.com/str42/flake8-pie)

### Tableau des codes PIE


| Code              | Description            | Optimisation |
| ----------------- | ---------------------- | ------------ |
| [PIE788](#pie788) | == pour comparer None  | Style        |
| [PIE789](#pie789) | != pour comparer None  | Style        |
| [PIE796](#pie796) | len() dans condition   | Performance  |
| [PIE798](#pie798) | == pour comparer types | Style        |


---

### PIE788

**Description** : Utilisation de == pour comparer avec None.

**Exemple corrigé** :

```python
if x is None:
    pass
```

---

### PIE796

**Description** : Utilisation de len() dans une condition.

**Exemple corrigé** :

```python
if lst:
    pass
```

---

### PIE798

**Description** : Utilisation de == pour comparer des types.

**Exemple corrigé** :

```python
if isinstance(x, int):
    pass
```

---

[↑ Retour au sommaire](#sommaire)

---

## Famille SIM - Simplify (Simplifications)

> **Plugin** : ✱ `flake8-simplify` | **Installation** : `pip install flake8-simplify` | **Doc** : [Simplify](https://github.com/MartijnBraam/flake8-simplify)

### Tableau des codes SIM


| Code              | Description         | Simplification |
| ----------------- | ------------------- | -------------- |
| [SIM108](#sim108) | if ternaire         | Style          |
| [SIM115](#sim115) | open sans with      | Sécurité       |
| [SIM116](#sim116) | dict sans littéral  | Style          |
| [SIM118](#sim118) | in avec dict.keys() | Performance    |


---

### SIM108

**Description** : Utilisation de if ternaire.

**Exemple corrigé** :

```python
x = a if condition else b
```

---

### SIM115

**Description** : Utilisation de open sans with.

**Exemple corrigé** :

```python
with open("fichier.txt") as f:
    data = f.read()
```

---

### SIM116

**Description** : Utilisation de dict sans littéral.

**Exemple corrigé** :

```python
d = {"a": 1, "b": 2}
```

---

### SIM118

**Description** : Utilisation de in avec dict.keys().

**Exemple corrigé** :

```python
if key in d:
    pass
```

---

[↑ Retour au sommaire](#sommaire)

---

## Famille UP - Pyupgrade (Modernisation)

> **Plugin** : ✱ `flake8-pyupgrade` | **Installation** : `pip install flake8-pyupgrade` | **Doc** : [Pyupgrade](https://github.com/asottile/pyupgrade)

### Tableau des codes UP


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

**Description** : Utilisation de % pour formatage.

**Exemple corrigé** :

```python
print(f"Hello, {name}!")
```

---

### UP002

**Description** : Utilisation de .format().

**Exemple corrigé** :

```python
print(f"Hello, {name}!")
```

---

### UP003

**Description** : Utilisation de dict().

**Exemple corrigé** :

```python
d = {}
```

---

### UP005

**Description** : Utilisation de list().

**Exemple corrigé** :

```python
lst = []
```

---

### UP017

**Description** : Utilisation de range(len(...)).

**Exemple corrigé** :

```python
for item in lst:
    print(item)
```

---

### UP020

**Description** : Utilisation de open sans encoding.

**Exemple corrigé** :

```python
with open("fichier.txt", encoding="utf-8") as f:
    pass
```

---

[↑ Retour au sommaire](#sommaire)

---

## Outils de correction automatique

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

### Comparaison


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

## Bibliographie

### Documentation officielle

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
