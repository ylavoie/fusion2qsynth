# Fusion2QSynth v1.1.0

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

### Added

- Bibliothèque centralisée des instruments.
- Gestion des instruments par identifiant dans les PARTS.
- Ajout de la gestion complète des instruments dans l'éditeur.

### Changed

- Migration du modèle PART :
  - suppression des références directes SF2 dans les PARTS ;
  - résolution via la bibliothèque d'instruments.
- Harmonisation du contrôleur Live, des previews et des tests audio.
- Centralisation de la résolution instrument dans FusionProject.

### Fixed

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
