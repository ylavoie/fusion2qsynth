# Version 1.0 - Première release stable

Date : 2026-08-03

## Ajouté

### Architecture générale

- Création de l'architecture modulaire Fusion2QSynth.
- Séparation des responsabilités entre :

  - capture des performances ;
  - édition des configurations ;
  - contrôle temps réel ;
  - diagnostic MIDI ;
  - fonctions communes.

### Bibliothèque commune

Création de `fusion_lib.py` regroupant :

- chargement et sauvegarde de `fusion.json` ;
- sauvegarde automatique (`fusion.json.bak`) ;
- recherche des ports MIDI ;
- fonctions MIDI communes ;
- fonction panic MIDI ;
- conversion numéro de note → nom de note ;
- validation des configurations ;
- affichage standardisé des Mix et PARTS ;
- fonctions de manipulation des Mix et PARTS.

### Capture des performances

Ajout de `fusion_capture.py`.

Fonctionnalités :

- détection automatique d'un nouveau Mix Fusion ;
- capture Bank Select ;
- capture Program Change ;
- identification des PARTS actives ;
- détection des canaux MIDI utilisés ;
- génération automatique de la structure `fusion.json`.

### Éditeur de Mix

Ajout de `editor.py`.

Fonctionnalités :

- affichage des Mix disponibles ;
- tri logique des Mix par Bank/Program ;
- affichage détaillé des PARTS ;
- modification des associations instrument ;
- recherche d'instruments SoundFont ;
- prévisualisation sonore ;
- sauvegarde des modifications.

### Gestion SoundFont

Ajout des outils liés aux banques SF2.

Fonctionnalités :

- extraction des instruments SF2 ;
- recherche rapide par nom ;
- association :

  - Bank SF2 ;
  - Program SF2 ;
  - nom d'instrument.

### Contrôleur temps réel

Ajout de `fusion_controller.py`.

Fonctionnalités :

- surveillance du MIDI Fusion ;
- détection des changements de Performance ;
- identification du Mix correspondant ;
- chargement automatique des programmes FluidSynth ;
- envoi des Bank Select et Program Change.

### Monitor MIDI

Ajout de `fusion_monitor.py`.

Fonctionnalités :

- observation des notes MIDI ;
- affichage canal / note / vélocité ;
- correspondance canal MIDI → PART ;
- affichage du preset SF2 associé ;
- diagnostic des problèmes d'assignation.

---

## Amélioré

### Gestion des configurations

- Validation des Mix avant utilisation.
- Vérification :

  - canaux MIDI valides ;
  - présence des paramètres Fusion ;
  - présence des paramètres SF2 ;
  - zones de notes valides ;
  - plages de vélocité valides.

### Affichage utilisateur

- Harmonisation des messages entre les outils.
- Affichage détaillé des PARTS.
- Ajout des informations :

  - canal MIDI ;
  - Bank Fusion ;
  - Program Fusion ;
  - instrument QSynth ;
  - Bank/Program SF2.

### Fiabilité

- Ajout de sauvegardes automatiques.
- Centralisation des fonctions communes.
- Réduction des duplications de code.

---

## Corrigé

- Correction de la détection des PARTS partageant des canaux MIDI.
- Correction des associations PART → SF2.
- Correction du test sonore depuis l'éditeur.
- Correction de l'utilisation des paramètres SF2.
- Correction des erreurs liées aux structures d'instruments.
- Amélioration du diagnostic lorsqu'une PART semble silencieuse.

---

## Documentation

Ajout de :

- `README.md`
- documentation de l'architecture ;
- procédure d'installation ;
- procédure de diagnostic ;
- description des modules.

---

## Compatibilité

Version validée avec :

- Roland Fusion comme source MIDI ;
- FluidSynth comme moteur sonore ;
- QSynth comme interface audio ;
- SoundFonts SF2 compatibles General MIDI.

---

## État de la release

Cette version constitue la première base stable :

- capture fonctionnelle ;
- édition fonctionnelle ;
- contrôle live fonctionnel ;
- diagnostic fonctionnel.

## [v1.1.0] - 2026-08-02

- Introduction de FusionProject
- Centralisation complète de la gestion du projet
- Validation déplacée hors de fusion_lib
- Gestion de fusion.json entièrement encapsulée
- Rechargement automatique centralisé
- Nettoyage de l'architecture
- Séparation claire entre modèle, contrôleur et utilitaires

## [1.1.1] - 2026-08-03

### Architecture

- Centralisation complète de la gestion du projet avec `FusionProject`.
- `fusion.json` encapsulé dans `FusionProject`.
- Suppression des accès directs au fichier projet depuis les autres modules.
- Déplacement de la validation dans `FusionProject`.
- Centralisation du rechargement automatique du projet.
- Ajout de `fusion_constants.py`.
- Centralisation des constantes globales.

### Nettoyage

- Suppression des anciennes fonctions de chargement/sauvegarde JSON utilisées hors modèle.
- Nettoyage de `fusion_lib`.
- Suppression des références résiduelles à l'ancien modèle d'accès aux données.

### Validation

- Audit complet des références effectué.
- Tests de démarrage, capture, édition, contrôleur Live et monitor MIDI validés.

## 1.2.0

### Ajouté

- Bibliothèque centralisée des instruments.
- Gestion des instruments par identifiant dans les PARTS.
- Ajout de la gestion complète des instruments dans l'éditeur.

### Changé

- Migration du modèle PART :
  - suppression des références directes SF2 dans les PARTS ;
  - résolution via la bibliothèque d'instruments.
- Harmonisation du contrôleur Live, des previews et des tests audio.
- Centralisation de la résolution instrument dans FusionProject.

### Correction

- Annulation d'édition d'une PART sans modification accidentelle.
- Gestion des Mix inexistants dans l'éditeur.
- Nettoyage des anciens chemins v1.0.

## v1.3

### Ajouté

- Validation centralisée du projet via `FusionProject.validate()`.
- Détection des références d'instruments invalides dans les PARTS.
- Diagnostic des canaux MIDI partagés.
- Réparation interactive des instruments absents avec revalidation automatique.

### Modifié

- La validation n'est plus répartie entre l'éditeur et le projet.
- Les canaux MIDI partagés sont maintenant traités comme une information plutôt qu'une erreur bloquante.
- L'affichage des diagnostics de validation a été amélioré.
- La gestion des instruments utilise désormais les références d'instruments du projet.

### Supprimé

- Suppression de `check_parts()` dans l'éditeur.
- Suppression des anciennes validations MIDI dupliquées.
- Suppression des anciennes logiques de configuration directe PART → SoundFont.

### Correction

- Correction de l'annulation d'une édition de PART qui pouvait appliquer un changement non confirmé.
- Correction des erreurs lors de la validation de références d'instruments absentes.
- Correction de la boucle validation/réparation afin de permettre plusieurs corrections successives.
