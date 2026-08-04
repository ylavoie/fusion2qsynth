# Version 1.0 - Première release stable

Date : 2026-08-03

## Ajouté

### Architecture générale

* Création de l'architecture modulaire Fusion2QSynth.
* Séparation des responsabilités entre :

  * capture des performances ;
  * édition des configurations ;
  * contrôle temps réel ;
  * diagnostic MIDI ;
  * fonctions communes.

### Bibliothèque commune

Création de `fusion_lib.py` regroupant :

* chargement et sauvegarde de `fusion.json` ;
* sauvegarde automatique (`fusion.json.bak`) ;
* recherche des ports MIDI ;
* fonctions MIDI communes ;
* fonction panic MIDI ;
* conversion numéro de note → nom de note ;
* validation des configurations ;
* affichage standardisé des Mix et PARTS ;
* fonctions de manipulation des Mix et PARTS.

### Capture des performances

Ajout de `fusion_capture.py`.

Fonctionnalités :

* détection automatique d'un nouveau Mix Fusion ;
* capture Bank Select ;
* capture Program Change ;
* identification des PARTS actives ;
* détection des canaux MIDI utilisés ;
* génération automatique de la structure `fusion.json`.

### Éditeur de Mix

Ajout de `editor.py`.

Fonctionnalités :

* affichage des Mix disponibles ;
* tri logique des Mix par Bank/Program ;
* affichage détaillé des PARTS ;
* modification des associations instrument ;
* recherche d'instruments SoundFont ;
* prévisualisation sonore ;
* sauvegarde des modifications.

### Gestion SoundFont

Ajout des outils liés aux banques SF2.

Fonctionnalités :

* extraction des instruments SF2 ;
* recherche rapide par nom ;
* association :

  * Bank SF2 ;
  * Program SF2 ;
  * nom d'instrument.

### Contrôleur temps réel

Ajout de `fusion_controller.py`.

Fonctionnalités :

* surveillance du MIDI Fusion ;
* détection des changements de Performance ;
* identification du Mix correspondant ;
* chargement automatique des programmes FluidSynth ;
* envoi des Bank Select et Program Change.

### Monitor MIDI

Ajout de `fusion_monitor.py`.

Fonctionnalités :

* observation des notes MIDI ;
* affichage canal / note / vélocité ;
* correspondance canal MIDI → PART ;
* affichage du preset SF2 associé ;
* diagnostic des problèmes d'assignation.

---

## Amélioré

### Gestion des configurations

* Validation des Mix avant utilisation.
* Vérification :

  * canaux MIDI valides ;
  * présence des paramètres Fusion ;
  * présence des paramètres SF2 ;
  * zones de notes valides ;
  * plages de vélocité valides.

### Affichage utilisateur

* Harmonisation des messages entre les outils.
* Affichage détaillé des PARTS.
* Ajout des informations :

  * canal MIDI ;
  * Bank Fusion ;
  * Program Fusion ;
  * instrument QSynth ;
  * Bank/Program SF2.

### Fiabilité

* Ajout de sauvegardes automatiques.
* Centralisation des fonctions communes.
* Réduction des duplications de code.

---

## Corrigé

* Correction de la détection des PARTS partageant des canaux MIDI.
* Correction des associations PART → SF2.
* Correction du test sonore depuis l'éditeur.
* Correction de l'utilisation des paramètres SF2.
* Correction des erreurs liées aux structures d'instruments.
* Amélioration du diagnostic lorsqu'une PART semble silencieuse.

---

## Documentation

Ajout de :

* `README.md`
* documentation de l'architecture ;
* procédure d'installation ;
* procédure de diagnostic ;
* description des modules.

---

## Compatibilité

Version validée avec :

* Roland Fusion comme source MIDI ;
* FluidSynth comme moteur sonore ;
* QSynth comme interface audio ;
* SoundFonts SF2 compatibles General MIDI.

---

## État de la release

Cette version constitue la première base stable :

* capture fonctionnelle ;
* édition fonctionnelle ;
* contrôle live fonctionnel ;
* diagnostic fonctionnel.

## Changelog 1.1.0 - 2026-08-02

* Introduction de FusionProject
* Centralisation complète de la gestion du projet
* Validation déplacée hors de fusion_lib
* Gestion de fusion.json entièrement encapsulée
* Rechargement automatique centralisé
* Nettoyage de l'architecture
* Séparation claire entre modèle, contrôleur et utilitaires

## Changelog 1.1.1 - 2026-08-03

### Architecture

* Centralisation complète de la gestion du projet avec `FusionProject`.
* `fusion.json` encapsulé dans `FusionProject`.
* Suppression des accès directs au fichier projet depuis les autres modules.
* Déplacement de la validation dans `FusionProject`.
* Centralisation du rechargement automatique du projet.
* Ajout de `fusion_constants.py`.
* Centralisation des constantes globales.

### Nettoyage

* Suppression des anciennes fonctions de chargement/sauvegarde JSON utilisées hors modèle.
* Nettoyage de `fusion_lib`.
* Suppression des références résiduelles à l'ancien modèle d'accès aux données.

### Validation

* Audit complet des références effectué.
* Tests de démarrage, capture, édition, contrôleur Live et monitor MIDI validés.

## Changelog 1.2 - 2026-08-03

### Ajouté

* Bibliothèque centralisée des instruments.
* Gestion des instruments par identifiant dans les PARTS.
* Ajout de la gestion complète des instruments dans l'éditeur.

### Changé

* Migration du modèle PART :
  * suppression des références directes SF2 dans les PARTS ;
  * résolution via la bibliothèque d'instruments.
* Harmonisation du contrôleur Live, des previews et des tests audio.
* Centralisation de la résolution instrument dans FusionProject.

### Correction

* Annulation d'édition d'une PART sans modification accidentelle.
* Gestion des Mix inexistants dans l'éditeur.
* Nettoyage des anciens chemins v1.0.

## Changelog 1.3 - 2026-08-03

### Ajouté

* Validation centralisée du projet via `FusionProject.validate()`.
* Détection des références d'instruments invalides dans les PARTS.
* Diagnostic des canaux MIDI partagés.
* Réparation interactive des instruments absents avec revalidation automatique.

### Modifié

* La validation n'est plus répartie entre l'éditeur et le projet.
* Les canaux MIDI partagés sont maintenant traités comme une information plutôt qu'une erreur bloquante.
* L'affichage des diagnostics de validation a été amélioré.
* La gestion des instruments utilise désormais les références d'instruments du projet.

### Supprimé

* Suppression de `check_parts()` dans l'éditeur.
* Suppression des anciennes validations MIDI dupliquées.
* Suppression des anciennes logiques de configuration directe PART → SoundFont.

### Correction

* Correction de l'annulation d'une édition de PART qui pouvait appliquer un changement non confirmé.
* Correction des erreurs lors de la validation de références d'instruments absentes.
* Correction de la boucle validation/réparation afin de permettre plusieurs corrections successives.

## Changelog 1.4 - 2026-08-04

### Sauvegarde sécurisée du projet

#### Ajout de `save_safe()`

* Remplacement complet de l'ancien mécanisme `save()`.
* Centralisation de toutes les écritures persistantes via `save_safe()`.
* Suppression de la méthode `save()` devenue obsolète.
* Validation du projet avant toute sauvegarde.

#### Protection des données

* Ajout d'une sauvegarde automatique `fusion.json.bak` avant remplacement du fichier principal.
* Utilisation d'un fichier temporaire `fusion.json.tmp` lors de l'écriture.
* Remplacement sécurisé du fichier projet après écriture complète.
* Nettoyage automatique des fichiers temporaires en cas de succès ou d'échec.

#### Gestion des erreurs

* Gestion des erreurs d'écriture disque sans arrêt brutal de l'application.
* Retour booléen de `save_safe()` utilisé par les appelants.
* Correction des messages utilisateurs afin qu'une sauvegarde ne soit annoncée réussie qu'après confirmation réelle.

### Améliorations de l'éditeur

* Adaptation des opérations de l'éditeur au nouveau mécanisme de sauvegarde.
* Correction de la gestion des échecs de sauvegarde lors :

  * des changements d'instruments ;
  * des réparations automatiques ;
  * de l'ajout d'instruments ;
  * de la suppression d'instruments.
* Messages utilisateur ajustés pour refléter l'état réel de persistance.

### Capture Fusion

* Gestion correcte des échecs de sauvegarde après capture.
* L'utilisateur est informé lorsqu'un Mix est créé en mémoire mais n'a pas pu être écrit sur disque.

### Robustesse du chargement

* Détection des fichiers `fusion.json` invalides.
* Remplacement des erreurs techniques JSON par un message utilisateur clair.
* Arrêt propre du programme lorsqu'un projet ne peut pas être chargé.

### Validation et tests

Tests complétés :

* sauvegarde normale ;
* sauvegarde successive avec création du `.bak` ;
* échec d'écriture par permission refusée ;
* absence de fichiers `.tmp` résiduels après erreur ;
* corruption volontaire de `fusion.json` ;
* restauration manuelle depuis `fusion.json.bak` ;
* validation des flux éditeur et capture.

### État final

La v1.4 apporte une couche de persistance fiable :

* écritures sécurisées ;
* protection contre les corruptions partielles ;
* récupération possible depuis une sauvegarde ;
* gestion propre des erreurs utilisateur.

## Version 1.5

### Persistence et récupération de projet

* Ajout d'un mécanisme de sauvegarde sécurisée avec conservation historique.
* Ajout de la rotation automatique des sauvegardes :

  * `fusion.json.bak`
  * `fusion.json.bak1`
  * `fusion.json.bak2`
* Amélioration de la récupération après corruption de `fusion.json`.
* Ajout de la restauration depuis une génération de sauvegarde sélectionnée.
* Ajout d'un flux utilisateur de récupération :

  * détection d'un projet récupérable ;
  * affichage des sauvegardes disponibles ;
  * sélection de la version à restaurer ;
  * validation après restauration.

### Métadonnées des sauvegardes

* Ajout de l'affichage des informations associées aux sauvegardes :

  * nom du fichier ;
  * taille ;
  * date de modification.
* Conservation de la séparation des responsabilités :

  * `FusionProject` gère les données de sauvegarde ;
  * l'interface gère la présentation utilisateur.

### Architecture interne

* Déplacement des constantes de persistance dans `FusionProject`.
* Réduction des dépendances vers les détails internes des fichiers projet.
* Encapsulation accrue de la gestion des fichiers :

  * chargement ;
  * sauvegarde ;
  * restauration ;
  * récupération.

### Gestion des erreurs

* Amélioration de la gestion des fichiers JSON invalides.
* Remplacement des crashes bruts par des messages utilisateur contrôlés.
* Ajout d'un chemin de récupération propre lorsqu'une sauvegarde existe.

### Tests validés

* Corruption volontaire de `fusion.json`.
* Restauration depuis plusieurs générations de sauvegardes.
* Gestion d'une sauvegarde inexistante ou invalide.
* Rotation des backups après sauvegarde.
* Retour normal dans l'application après récupération réussie.

---

## Notes de conception

Les sauvegardes disponibles sont affichées comme des candidats de restauration.
La validation du contenu JSON est effectuée uniquement lors de la tentative de restauration afin de conserver une séparation claire entre :

* découverte des sauvegardes ;
* affichage utilisateur ;
* restauration et validation.

La validation préventive de toutes les sauvegardes n'est pas incluse dans cette version.

## Version 1.6

### Architecture

* Finalisation de la migration vers FusionProject.
* Retrait des responsabilités métier de fusion_lib.
* Nettoyage des dépendances internes.

### Fonctionnalités

* Ajout de note_range() pour l'affichage des plages MIDI des PARTs.
* Amélioration de l'affichage des informations de PART.
