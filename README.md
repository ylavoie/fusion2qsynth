# Fusion2QSynth

Interface MIDI entre un **Alesis Fusion 8HD** et **FluidSynth**, permettant d'utiliser des SoundFonts SF2 avec les PROGRAM, MIX et SONG du Fusion.

**Version : 2.7**

---

## 1. Description

Fusion2QSynth permet d'utiliser l'Alesis Fusion 8HD comme contrôleur principal d'un moteur sonore FluidSynth.

Le projet permet de :

* capturer les performances MIDI du Fusion ;
* identifier les PROGRAM et MIX par Bank Select / Program Change ;
* identifier les PARTs et leurs canaux MIDI ;
* capturer les SONG ;
* associer les sons Fusion à des instruments SoundFont ;
* gérer une bibliothèque centralisée d'instruments ;
* charger automatiquement les presets correspondants dans FluidSynth ;
* contrôler FluidSynth en temps réel depuis le Fusion ;
* diagnostiquer les échanges MIDI.

L'objectif est de conserver le Fusion comme interface musicale :

```text
Musicien
   |
   v
Alesis Fusion 8HD
   |
   | MIDI
   v
Fusion2QSynth
   |
   v
FluidSynth
   |
   v
SoundFonts SF2
   |
   v
Audio
```

---

## 2. Architecture

Le projet utilise `FusionProject` comme modèle persistant central.

```text
                    Alesis Fusion 8HD
                           |
                           | MIDI
                           v
                     Fusion2QSynth
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
       Capture          Éditeur        Contrôleur Live
          |                |                |
          +----------------+----------------+
                           |
                           v
                     FusionProject
                           |
                           v
                       fusion.json

                    Contrôleur Live
                           |
                           v
                      FluidSynth
                           |
                           v
                         Audio
```

`FusionProject` assure notamment :

* le chargement du projet ;
* la validation ;
* la réparation ;
* la gestion des PROGRAM, MIX, SONG et instruments ;
* la sauvegarde du modèle.

Les modules applicatifs utilisent `FusionProject` plutôt que de gérer directement `fusion.json`.

Pour une description détaillée de l'architecture, consulter :

```text
ARCHITECTURE.md
```

---

## 3. Modèle du projet

Le fichier principal est :

```text
fusion.json
```

Sa structure générale est :

```json
{
  "format_version": 2,
  "instruments": {},
  "programs": {},
  "mixes": {},
  "songs": {}
}
```

Les quatre collections ont des responsabilités distinctes :

```text
instruments
    bibliothèque des instruments SoundFont

programs
    performances PROGRAM du Fusion

mixes
    performances MIX du Fusion

songs
    configurations SONG du Fusion
```

Les performances référencent les instruments de la bibliothèque plutôt que de dupliquer les coordonnées SoundFont.

---

## 4. Instruments SoundFont

Un instrument est enregistré dans la collection :

```text
instruments
```

Exemple :

```json
{
  "grand_piano": {
    "name": "Grand Piano",
    "sf2_bank": 0,
    "sf2_program": 0
  }
}
```

Une PART ou un canal SONG référence ensuite cet instrument :

```json
{
  "instrument": "grand_piano"
}
```

Cette organisation sépare :

```text
Informations Fusion          Informations SoundFont
-------------------          ----------------------
bank                         sf2_bank
program                      sf2_program
fusion_name                  instrument
```

Le mapping SoundFont peut ainsi évoluer sans perdre les informations provenant du Fusion.

---

## 5. Modules principaux

### `fusion2qsynth.py`

Point d'entrée principal de l'application.

Il donne accès aux principales fonctions :

```text
Capture
Éditeur
Contrôleur Live
Monitor MIDI
```

---

### `fusion_project.py`

Modèle persistant central.

Il assure notamment :

* le chargement de `fusion.json` ;
* la gestion des données du projet ;
* la validation ;
* la réparation ;
* la sauvegarde.

---

### `fusion_capture.py`

Module de capture et d'apprentissage des performances du Fusion.

Il permet d'observer notamment :

* Bank Select ;
* Program Change ;
* canaux MIDI utilisés ;
* PARTs actives ;
* plages de notes ;
* plages de vélocité.

Les informations capturées sont intégrées au projet par `FusionProject`.

---

### `fusion_editor.py`

Éditeur interactif du projet.

Il permet notamment de gérer :

* PROGRAM ;
* MIX ;
* SONG ;
* PARTs ;
* canaux SONG ;
* instruments SoundFont ;
* associations Fusion → SoundFont ;
* prévisualisation des instruments ;
* validation et réparation du projet.

---

### `fusion_controller.py`

Point d'entrée du Contrôleur Live.

Il initialise le contrôleur et orchestre son fonctionnement.

La logique du contrôleur est répartie entre :

```text
fusion_controller.py
fusion_controller_loop.py
fusion_controller_state.py
fusion_performance.py
```

---

### `fusion_controller_loop.py`

Traite les événements MIDI reçus du Fusion.

Il assure notamment :

* la détection des changements de PROGRAM et MIX ;
* le traitement particulier du mode SONG ;
* le filtrage MIDI ;
* la transmission des événements autorisés vers FluidSynth.

---

### `fusion_controller_state.py`

Contient l'état dynamique du Contrôleur Live.

Il gère notamment :

```text
current_mode
current_performance
current_parts
active_notes
pending_reload
```

Cet état est temporaire et n'est pas enregistré dans `fusion.json`.

---

### `fusion_performance.py`

Centralise le chargement des performances dans FluidSynth.

Il prend en charge :

```text
PROGRAM
MIX
SONG
```

et applique les instruments SoundFont correspondant à la performance sélectionnée.

---

### `fusion_monitor.py`

Interface de diagnostic MIDI.

Il permet d'observer les événements MIDI reçus et d'obtenir les informations nécessaires au diagnostic.

---

### `fusion_diagnostic.py`

Regroupe les fonctions spécialisées utilisées pour le diagnostic.

---

### `sf2_library.py`

Gère la représentation des presets disponibles dans les SoundFonts.

Les presets sont normalisés autour des informations :

```text
name
sf2_bank
sf2_program
```

---

### `fusion_suggestions.py`

Fournit les mécanismes de suggestion permettant d'associer un nom Fusion à des presets SoundFont.

Les suggestions restent des propositions : le choix persistant de l'instrument appartient à l'utilisateur.

---

### `fusion_gm_map.py`

Contient les données de référence utilisées pour les correspondances entre les sons du Fusion et General MIDI.

---

### `fusion_lib.py`

Bibliothèque de fonctions techniques communes.

Elle contient notamment des fonctions utilisées pour :

* MIDI ;
* recherche de ports ;
* journalisation ;
* opérations utilitaires communes.

La gestion du modèle du projet appartient à `FusionProject`.

---

### `fusion_constants.py`

Regroupe les constantes communes de l'application.

Les canaux MIDI y suivent la convention utilisée par Fusion2QSynth :

```text
1 .. 16
```

La conversion vers la convention Mido :

```text
0 .. 15
```

est effectuée à la frontière MIDI.

---

## 6. Installation

### Dépendances système

Fusion2QSynth nécessite notamment :

```text
Python 3
ALSA MIDI
FluidSynth
PipeWire
SoundFonts SF2
```

Sous Ubuntu, FluidSynth peut par exemple être installé avec :

```bash
sudo apt install fluidsynth
```

Les paquets exacts nécessaires à Mido et au backend MIDI peuvent dépendre de l'environnement Python utilisé.

---

## 7. Configuration MIDI

Dans la configuration actuelle, le Fusion 8HD apparaît comme périphérique MIDI USB sous le nom :

```text
CH345
```

FluidSynth expose une sortie MIDI :

```text
FLUID Synth
```

Le flux général est :

```text
Fusion 8HD
    |
    | USB MIDI
    v
Fusion2QSynth
    |
    | MIDI
    v
FluidSynth
```

La détection des ports est centralisée dans les fonctions techniques du projet.

---

## 8. FluidSynth

La configuration utilisée avec le projet repose sur :

```text
PipeWire
48 kHz
buffer 256
```

FluidSynth charge les SoundFonts utilisées pour reproduire les instruments du Fusion.

Une banque SoundFont est convertie en Bank Select MIDI selon :

```text
MSB = sf2_bank // 128
LSB = sf2_bank % 128
```

puis envoyée sous la forme :

```text
CC0  = MSB
CC32 = LSB
Program Change = sf2_program
```

Cette conversion permet notamment l'utilisation de banques SoundFont supérieures à 127.

---

## 9. Utilisation

L'application principale est lancée avec :

```bash
python3 fusion2qsynth.py
```

Elle donne accès aux fonctions principales :

```text
Capture Fusion
Éditeur
Contrôleur Live
Monitor MIDI
```

---

## 10. Capture

La Capture apprend les informations transmises par le Fusion.

Pour les PROGRAM et MIX, une performance est identifiée par :

```text
bank:program
```

à partir des messages :

```text
CC0
Program Change
```

transmis sur le canal MIDI par défaut du Fusion.

Les PARTs sont ensuite observées à partir des événements MIDI réellement reçus.

La Capture peut déterminer notamment :

```text
midi_channel
note_min
note_max
velocity_min
velocity_max
```

Les données sont intégrées au projet par `FusionProject`.

---

## 11. Éditeur

L'Éditeur permet de compléter et modifier les informations capturées.

Il permet notamment :

* de gérer les PROGRAM ;
* de gérer les MIX ;
* de gérer les SONG ;
* d'éditer les PARTs ;
* d'éditer les canaux SONG ;
* d'associer des instruments SoundFont ;
* de créer et modifier la bibliothèque d'instruments ;
* de rechercher des suggestions ;
* de prévisualiser des presets ;
* de tester les PARTs d'un MIX ;
* de valider et réparer le projet.

Le flux général d'association est :

```text
fusion_name
     |
     v
analyse Fusion / GM
     |
     v
suggestions SoundFont
     |
     v
choix utilisateur
     |
     v
instrument
```

---

## 12. Contrôleur Live

Le Contrôleur Live permet au Fusion de piloter FluidSynth en temps réel.

Trois modes sont supportés :

```text
PROGRAM
MIX
SONG
```

### PROGRAM et MIX

Le Fusion transmet :

```text
CC0
Program Change
```

sur son canal MIDI par défaut.

Fusion2QSynth construit alors :

```text
bank:program
```

et charge la performance correspondante.

```text
Fusion
   |
   | CC0 + Program Change
   v
Contrôleur Live
   |
   v
fusion_performance.py
   |
   v
FluidSynth
```

Les messages CC0 et CC32 provenant des PARTs ne sont pas retransmis à FluidSynth pour la sélection des sons.

Cela empêche les Bank Select du Fusion d'écraser le mapping SoundFont défini dans Fusion2QSynth.

### SONG

En mode SONG, les Program Change ne servent pas à sélectionner la SONG.

La SONG sélectionnée est chargée lors de la réception du message :

```text
MIDI START
```

---

## 13. Diagnostic MIDI

Le Monitor MIDI permet d'observer le fonctionnement du système.

Il peut notamment aider à diagnostiquer :

* absence de notes ;
* mauvais canal MIDI ;
* PART incorrecte ;
* mauvaise performance ;
* problèmes de mapping ;
* événements MIDI inattendus.

Le monitor peut être lancé depuis l'application principale.

---

## 14. Validation et réparation

`FusionProject` assure la validation du modèle persistant.

La validation porte notamment sur :

```text
instruments
programs
mixes
songs
```

ainsi que sur leurs relations.

Lorsqu'une incohérence peut être réparée, la réparation peut être effectuée progressivement :

```text
validation
    |
    v
erreur
    |
    v
réparation
    |
    v
nouvelle validation
```

Le cycle continue jusqu'à ce que le projet soit valide ou que l'utilisateur décide de ne pas poursuivre la réparation.

---

## 15. Suggestions et validation globale

Les correspondances Fusion / General MIDI / SoundFont peuvent être vérifiées avec :

```text
integration-globale.py
```

Cet outil de développement contrôle notamment :

* mappings GM ;
* familles d'instruments ;
* suggestions ;
* scores et classement ;
* doublons ;
* limites de résultats ;
* stabilité des suggestions ;
* validité des presets ;
* aliases de `FUSION_GM_DATA`.

Il ne modifie pas le projet.

---

## 16. Limites MIDI du Fusion

Fusion2QSynth travaille avec les informations réellement transmises par le Fusion 8HD.

Certaines informations internes au Fusion ne sont pas directement disponibles par MIDI.

Pour les MIX, les PARTs doivent notamment être configurées de façon à utiliser des canaux MIDI permettant de les distinguer.

Les Bank Select transmis par les PARTs décrivent les sons du Fusion et non les banques SoundFont utilisées par FluidSynth.

Fusion2QSynth filtre donc ces informations lorsque nécessaire et conserve indépendamment son propre mapping SoundFont.

---

## 17. Structure du projet

Les principaux fichiers sont :

```text
fusion2qsynth/
|
+-- fusion2qsynth.py
+-- fusion_project.py
+-- fusion_capture.py
+-- fusion_editor.py
+-- fusion_controller.py
+-- fusion_controller_loop.py
+-- fusion_controller_state.py
+-- fusion_performance.py
+-- fusion_monitor.py
+-- fusion_diagnostic.py
+-- fusion_suggestions.py
+-- fusion_gm_map.py
+-- sf2_library.py
+-- fusion_lib.py
+-- fusion_constants.py
+-- integration-globale.py
|
+-- fusion.json
|
+-- README.md
+-- ARCHITECTURE.md
+-- CHANGELOG.md
+-- TODO
```

---

## 18. Principes du projet

Fusion2QSynth suit quelques principes fondamentaux :

```text
observer plutôt que supposer
séparer les données Fusion des données SoundFont
centraliser le modèle dans FusionProject
référencer les instruments plutôt que les dupliquer
séparer l'état persistant de l'état d'exécution
valider avant de sauvegarder
proposer plutôt qu'imposer
```

Le Fusion demeure l'instrument principal.

Fusion2QSynth sert de couche d'adaptation entre son fonctionnement MIDI et FluidSynth.

---

## 19. Documentation

La documentation du projet est répartie entre :

```text
README.md
    présentation et utilisation générale

ARCHITECTURE.md
    architecture interne et principes de conception

CHANGELOG.md
    historique des versions

TODO
    améliorations futures
```

---

## 20. Version

```text
Fusion2QSynth v2.7
```

Alesis Fusion 8HD → Fusion2QSynth → FluidSynth / SoundFonts SF2.
