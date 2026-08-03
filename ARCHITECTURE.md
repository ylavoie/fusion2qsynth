# Fusion2QSynth – Architecture

Version : 1.1

---

# Objectif

Fusion2QSynth permet de piloter automatiquement FluidSynth (QSynth) à partir des changements de Performance (Mix) d'un Yamaha Montage M / MODX / Motif compatible.

Le projet capture la configuration des PARTS du synthétiseur, associe chaque PART à un instrument SoundFont et recharge automatiquement FluidSynth lorsqu'un changement de Mix est détecté.

L'architecture est volontairement simple :

* une seule source de vérité (`FusionProject`)
* une séparation claire entre les données, les traitements et les utilitaires
* aucun accès direct au fichier `fusion.json` en dehors du modèle.

---

# Architecture générale

```text
                 +----------------+
                 | fusion2qsynth  |
                 +--------+-------+
                          |
      +-------------------+-------------------+
      |                   |                   |
      v                   v                   v
+-------------+   +---------------+   +---------------+
| Capture     |   | Controller    |   | Monitor       |
+-------------+   +---------------+   +---------------+
      |                   |                   |
      +-------------------+-------------------+
                          |
                          v
                 +------------------+
                 | FusionProject    |
                 +------------------+
                          |
                          v
                    fusion.json

          +-------------------------------+
          |          fusion_lib           |
          +-------------------------------+
          | MIDI | Notes | Logs | Helpers |
          +-------------------------------+
```

---

# FusionProject

`FusionProject` est le modèle central de l'application.

Il est le seul composant autorisé à connaître le fichier `fusion.json`.

Responsabilités :

* chargement du projet
* sauvegarde
* création d'une copie de sauvegarde
* rechargement automatique
* validation des données
* diagnostic
* gestion des Mix
* gestion des PARTS
* recherche dans le projet

Tous les autres modules utilisent exclusivement son interface publique.

---

# fusion_controller

Responsable du fonctionnement temps réel.

Fonctions :

* ouverture des ports MIDI
* communication avec FluidSynth
* détection des changements de Mix
* chargement des instruments SF2
* suivi de l'état courant
* forwarding MIDI

Le contrôleur ne modifie jamais directement les données du projet.

Il utilise uniquement les méthodes de `FusionProject`.

---

# fusion_capture

Responsable de l'apprentissage des Mix.

Fonctions :

* lecture des informations MIDI
* apprentissage des PARTS
* création des Mix
* mise à jour du projet

Aucune connaissance de `fusion.json`.

Toutes les modifications passent par `FusionProject`.

---

# fusion_editor

Responsable de la modification du projet.

Fonctions :

* affichage des Mix
* modification des PARTS
* configuration SoundFont
* suppression
* renommage
* sauvegarde

L'éditeur ne manipule jamais directement les fichiers.

---

# fusion_monitor

Outil de diagnostic.

Fonctions :

* affichage des événements MIDI
* affichage de la PART correspondante
* contrôle des canaux
* aide au dépannage

Le monitor est uniquement en lecture.

---

# fusion_lib

Bibliothèque de fonctions utilitaires.

Elle ne contient aucune logique métier.

Responsabilités :

## MIDI

* recherche des ports
* Panic
* fonctions génériques MIDI

## Notes

* conversion numéro → nom
* helpers de notes

## Logs

* journalisation

## Affichage

* affichage des Mix
* affichage des PARTS

## Helpers

Fonctions génériques indépendantes du projet.

---

# Structure des données

Chaque Mix est identifié par :

```text
bank:program
```

Exemple :

```text
2:15
```

Chaque Mix contient :

```text
Mix
 ├── name
 └── parts
        ├── 1
        ├── 2
        ├── ...
        └── 16
```

Une PART contient notamment :

```text
midi_channel
bank
program

note_min
note_max

velocity_min
velocity_max

name
sf2_bank
sf2_program
```

---

# Principes de conception

## Source de vérité unique

Toutes les données proviennent de :

```text
FusionProject
```

Il n'existe aucun second modèle.

---

## Encapsulation

Le fichier

```text
fusion.json
```

est entièrement encapsulé.

Aucun autre module ne connaît :

* son nom
* son emplacement
* son format de sauvegarde

---

## Responsabilités

Chaque module possède une responsabilité unique.

FusionProject

→ données

Controller

→ temps réel

Capture

→ apprentissage

Editor

→ modification

Monitor

→ diagnostic

fusion_lib

→ utilitaires

---

## Utilitaires

Une fonction placée dans `fusion_lib` doit :

* être indépendante du projet
* être réutilisable
* ne modifier aucun état global

---

## Validation

La validation est réalisée exclusivement par :

```text
FusionProject.validate()
```

ou

```text
FusionProject.validate_mix()
```

Aucune validation n'est effectuée automatiquement lors d'une sauvegarde.

---

## Sauvegarde

La sauvegarde suit toujours le même processus :

```text
backup

↓

écriture JSON

↓

fin
```

La sauvegarde ne réalise aucune validation.

---

## Rechargement

Le contrôleur ne surveille pas directement le fichier.

Il demande simplement :

```text
project.reload_if_changed()
```

La logique de surveillance appartient au projet.

---

# Dépendances autorisées

```text
fusion_controller
        |
        v
FusionProject

fusion_editor
        |
        v
FusionProject

fusion_capture
        |
        v
FusionProject

fusion_monitor
        |
        v
FusionProject
```

Les dépendances inverses sont interdites.

---

# Dépendances interdites

Les modules applicatifs ne doivent jamais :

* ouvrir directement `fusion.json`
* écrire directement `fusion.json`
* connaître le nom du fichier
* modifier `project.data` sans passer par les méthodes prévues

---

# Évolutions futures

Les nouvelles fonctionnalités devront respecter cette architecture.

Toute évolution devra :

* utiliser `FusionProject` pour accéder aux données
* conserver `fusion_lib` comme bibliothèque technique
* éviter l'introduction d'un second modèle de données
* préserver la séparation entre données, traitements et interface.

---

# Philosophie du projet

Fusion2QSynth privilégie :

* la simplicité
* la lisibilité
* la stabilité
* une architecture facile à maintenir

L'objectif est qu'un nouveau développeur puisse comprendre l'organisation générale du projet en quelques minutes et ajouter de nouvelles fonctionnalités sans remettre en cause l'architecture existante.
