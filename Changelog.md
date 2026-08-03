Fusion2QSynth v1.1.0

- Introduction de FusionProject
- Centralisation complète de la gestion du projet
- Validation déplacée hors de fusion_lib
- Gestion de fusion.json entièrement encapsulée
- Rechargement automatique centralisé
- Nettoyage de l'architecture
- Séparation claire entre modèle, contrôleur et utilitaires

# Changelog

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

