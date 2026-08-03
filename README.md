# Fusion2QSynth

Conversion de performances Roland Fusion vers FluidSynth / SoundFonts SF2.

**Version : 1.0**

---

# 1. Description

Fusion2QSynth permet d'utiliser les performances d'un clavier Roland Fusion avec un moteur sonore externe basé sur FluidSynth/QSynth.

Le système :

* capture les performances Fusion ;
* identifie les PARTS MIDI ;
* associe chaque PART à un instrument SF2 ;
* recharge automatiquement les sons lors d'un changement de Performance.

---

# 2. Architecture

```text
Roland Fusion
      |
      | MIDI USB
      |
      v

fusion_capture.py
      |
      v

fusion.json
      |
      +----------------+
      |                |
      v                v

 editor.py     fusion_controller.py
      |                |
      +-------+--------+
              |
              v

        FluidSynth
              |
              v

          Audio
```

---

# 3. Modules

## fusion_lib.py

Bibliothèque commune du projet.

Contient :

* lecture et écriture JSON ;
* sauvegarde automatique ;
* recherche des ports MIDI ;
* validation des Mix ;
* affichage des Mix et PARTS ;
* fonctions MIDI utilitaires.

---

## fusion_capture.py

Module d'apprentissage des performances Fusion.

Capture :

* Bank Select ;
* Program Change ;
* canaux MIDI utilisés ;
* PARTS actives.

Produit et met à jour :

```text
fusion.json
```

---

## editor.py

Éditeur des associations Fusion → SF2.

Permet :

* l'affichage des Mix disponibles ;
* l'édition des PARTS ;
* la recherche d'instruments SF2 ;
* le test sonore ;
* la sauvegarde des configurations.

---

## fusion_controller.py

Contrôleur temps réel.

Fonction :

* détecter un changement de Performance Fusion ;
* identifier le Mix correspondant ;
* charger les programmes SF2 associés dans FluidSynth.

---

## fusion_monitor.py

Outil de diagnostic MIDI.

Affiche en temps réel :

* canal MIDI ;
* note ;
* vélocité ;
* Mix associé ;
* PART correspondante ;
* preset SF2.

---

# 4. Installation

## Dépendances système

```bash
sudo apt install fluidsynth qsynth python3-mido
```

## Dépendances Python

```bash
pip install mido python-rtmidi
```

---

# 5. Configuration MIDI

Ports utilisés :

```text
Entrée Fusion :
CH345

Sortie synthèse :
Fluid Synth
```

Ces paramètres sont centralisés dans :

```text
fusion_lib.py
```

---

# 6. Utilisation

Lancement principal :

```bash
python3 fusion2qsynth.py
```

Menu :

```text
=========================
 Fusion2QSynth
=========================

1 - Capture Fusion
2 - Éditer un Mix
3 - Contrôleur Live
4 - Monitor MIDI
5 - Quitter
```

---

# 7. Capture d'une Performance

Utiliser :

```text
1 - Capture Fusion
```

Sélectionner une Performance sur le Fusion.

Le système détecte :

* Bank ;
* Program ;
* PARTS ;
* canaux MIDI.

Les données sont enregistrées dans :

```text
fusion.json
```

---

# 8. Édition d'un Mix

Utiliser :

```text
2 - Éditer un Mix
```

Fonctions :

* liste triée des Mix ;
* sélection d'une PART ;
* recherche d'un instrument SF2 ;
* écoute de prévisualisation ;
* sauvegarde.

Exemple :

```json
{
  "midi_channel": 1,
  "bank": 2,
  "program": 5,
  "name": "Timpani",
  "sf2_bank": 0,
  "sf2_program": 47
}
```

---

# 9. Contrôle Live

Utiliser :

```text
3 - Contrôleur Live
```

Lors d'un changement de Performance Fusion :

```text
Fusion
 |
 | Bank Select
 | Program Change
 |
 v

fusion_controller.py
 |
 v

FluidSynth
```

Les presets SF2 correspondants sont chargés automatiquement.

---

# 10. Diagnostic MIDI

Utiliser :

```text
4 - Monitor MIDI
```

Exemple :

```text
NOTE_ON

Canal : 8
Note : C3
Velocity : 25

Mix : 2:5
PART : 3

QSynth :
Pan Flute

SF2 :
Bank 0 Program 75
```

Permet de diagnostiquer :

* absence de note ;
* mauvais canal ;
* mauvaise PART ;
* mauvais preset.

---

# 11. Validation et sauvegarde

Le fichier principal :

```text
fusion.json
```

Une copie automatique est créée :

```text
fusion.json.bak
```

Avant toute modification importante, il est recommandé de conserver une copie :

```bash
cp fusion.json fusion_backup.json
```

---

# 12. Structure du projet

```text
fusion2qsynth/

fusion2qsynth.py

fusion_lib.py
sf2_lib.py

fusion_capture.py
editor.py
fusion_controller.py
fusion_monitor.py

sf2dump.py

fusion.json
fusion.json.bak

sf2_library.json
```

---

# 13. Dépannage rapide

## Une PART ne produit aucun son

Vérifier :

1. le canal MIDI ;
2. la zone de notes ;
3. le preset SF2 ;
4. le monitor MIDI.

Commande :

```bash
python3 fusion_monitor.py
```

---

## Le changement de Performance ne charge rien

Vérifier :

* port MIDI Fusion ;
* sortie FluidSynth ;
* contenu de `fusion.json`.

---

# 14. Version

```text
Fusion2QSynth v1.0
```

Projet de conversion Roland Fusion → FluidSynth / SF2.
