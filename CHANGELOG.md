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

Ajout de `fusion_editor.py`.

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

## v1.7.3

### Gestion améliorée des instruments

Ajout de la gestion des instruments SoundFont depuis la bibliothèque SF2.

Nouveautés :

* ajout d'un instrument directement depuis `sf2_library.json` ;
* recherche de presets SoundFont par nom dans l'éditeur ;
* conservation de la saisie manuelle d'un instrument ;
* ajout de la modification des instruments existants ;
* utilisation de l'identifiant généré par la bibliothèque SF2 pour les nouveaux instruments.

Améliorations :

* le menu de gestion des instruments permet maintenant le cycle complet :

  * ajout ;
  * affichage ;
  * modification ;
  * suppression.

Corrections :

* prise en compte des presets SoundFont de type kit percussion utilisant des banques supérieures à 127.

## Version 1.8

### Édition des PARTs

* Amélioration de l’édition des paramètres d’une PART.
* Ajout de la modification du canal MIDI avec validation de la plage 1 à 16.
* Ajout de la modification des plages de notes et de vélocité.
* Ajout de la validation des modifications avant leur application.
* Protection contre les plages de notes ou de vélocité invalides.
* Ajout de la saisie des notes sous forme musicale (`C3`, `C#3`, `A#4`, etc.).
* Conservation de la saisie numérique MIDI pour les notes.
* Ajout du contrôle des bornes lors de la saisie des plages de notes.
* Harmonisation de l’affichage des plages de notes en notation musicale.
* Amélioration et uniformisation de l’affichage des paramètres des PARTs.

### Gestion des instruments

* Amélioration de la bibliothèque d’instruments SoundFont.
* Ajout d’une sélection d’instrument commune et triée alphabétiquement.
* Affichage de l’instrument actuellement affecté à une PART.
* Ajout d’un marqueur permettant d’identifier l’instrument courant dans la liste.
* Amélioration de l’affectation d’un instrument à une PART.
* Amélioration de la liste des instruments avec affichage de l’identifiant, de la banque, du programme et du nombre d’utilisations.
* Sécurisation de l’ajout manuel d’un instrument.
* Amélioration de l’ajout d’un instrument depuis la bibliothèque SoundFont.
* Sécurisation de la modification des instruments.
* Amélioration de la sélection lors de la modification et de la suppression d’un instrument.
* Protection contre la suppression d’un instrument utilisé par une ou plusieurs PARTs.
* Affichage des MIX et PARTs utilisant un instrument avant le refus de sa suppression.
* Détection centralisée dans `FusionProject` des références vers des instruments absents.
* Ajout de la réparation interactive des PARTs faisant référence à un instrument absent.
* Simplification de la représentation des instruments dans les PARTs en privilégiant les références à la bibliothèque.

### Gestion des MIX

* Amélioration de la gestion et de l’édition des MIX.
* Ajout du renommage d’un MIX.
* Ajout de la duplication d’un MIX.
* Ajout du test d’un MIX depuis l’éditeur.
* Ajout de la suppression ciblée d’un MIX.
* Ajout de la suppression des MIX vides.
* Amélioration de la modification des PARTs d’un MIX.
* Validation des modifications avant leur application.
* Conservation des données précédentes lorsqu’une modification est refusée par la validation.

### Validation et robustesse

* Renforcement de la validation des canaux MIDI.
* Renforcement de la validation des plages de notes et de vélocité.
* Centralisation de la validation des références d’instruments dans `FusionProject`.
* Amélioration du traitement et de la réparation des instruments manquants.
* Correction d’une utilisation incorrecte de `sf2_bank` à la place de `sf2_program` lors du test d’un instrument.
* Maintien de la validation métier comme protection finale après les contrôles effectués dans l’éditeur.

### Interface et ergonomie

* Amélioration de la présentation des menus d’édition.
* Uniformisation des listes et sélecteurs d’instruments.
* Tri alphabétique des instruments lors de leur sélection.
* Amélioration des messages de confirmation, d’annulation et d’erreur.
* Affichage plus lisible des plages de notes et de vélocité.
* Réduction des saisies techniques d’identifiants au profit de sélections numérotées.

### Nettoyage interne

* Suppression de méthodes devenues inutilisées dans `FusionProject`.
* Suppression d’anciennes fonctions de sélection et de gestion des instruments devenues redondantes.
* Suppression du code mort de prévisualisation des instruments.
* Suppression de fonctions MIX devenues inutilisées.
* Audit des accès aux MIX, PARTs et instruments afin de conserver la logique métier dans `FusionProject`.
* Simplification et harmonisation de la logique de sélection, de validation et de prévisualisation.

## Version 1.9 - Contrôleur Live et diagnostic MIDI

Date : 2026-08-09

### Amélioré

#### Contrôleur Live

* Fiabilisation du rechargement à chaud de `fusion.json`.
* Ajout du reload immédiat lorsqu’aucune note n’est active.
* Ajout du reload différé lorsqu’une modification survient pendant le jeu.
* Le reload différé est exécuté automatiquement dès que la dernière note active est relâchée.
* Ajout d’un suivi fiable des notes actives indépendamment du mode DEBUG.
* Gestion de `note_on` avec vélocité 0 comme un `note_off`.
* Protection contre les lectures transitoirement invalides de `fusion.json` pendant une sauvegarde externe.
* Suppression du rechargement périodique forcé du projet.
* Amélioration des messages indiquant les reloads immédiats et différés.
* Refactorisation de la logique de reload afin de réduire les duplications.

#### Détection des changements de Mix

* Ajout d’un canal MIDI par défaut configurable pour le Fusion 8HD.
* La détection des changements de Mix utilise maintenant le canal MIDI par défaut configuré dans le Fusion.
* Les Bank Select et Program Change des autres canaux ne déclenchent plus de faux changements de Mix.
* Validation du comportement avec plusieurs configurations de canal MIDI par défaut du Fusion.

#### Chargement des Mix

* Amélioration de la gestion du dernier Mix chargé.
* Le dernier Mix n’est sauvegardé que lorsqu’au moins une PART a réellement été chargée dans FluidSynth.
* Synchronisation de l’état interne des notes actives après un MIDI panic.
* Les PARTs incomplètes restent ignorées sans empêcher le chargement des PARTs valides.
* Correction du diagnostic afin d’exclure la bibliothèque `instruments` de la liste des Mix.

#### Routage MIDI

* Le routage MIDI est maintenant limité aux PARTs réellement actives dans FluidSynth.
* Les notes provenant de PARTs non configurées sont ignorées.
* Les Control Change provenant de PARTs non configurées sont ignorés.
* Le Pitch Bend, l’Aftertouch et le Polyphonic Aftertouch sont transmis uniquement pour les PARTs actives.
* Les Control Change musicaux des PARTs actives sont transmis à FluidSynth.
* Les Bank Select reçus du Fusion sont interceptés afin de ne pas écraser le mapping SoundFont configuré.
* Suppression de la fonction de routage MIDI devenue redondante après la spécialisation du traitement des messages.

#### Banques SoundFont

* Correction de la sélection des banques SoundFont supérieures à 127.
* Ajout du découpage des banques MIDI sur MSB et LSB.
* Validation des banques 0, 8 et 128.
* Validation du chargement de presets de percussion et de banques étendues.

#### Configuration

* Déplacement du mode DEBUG dans `fusion_constants.py`.
* Centralisation du canal MIDI par défaut du Fusion dans la configuration.

### Monitor MIDI

* Refonte du Monitor MIDI en outil de diagnostic indépendant de `fusion.json`.
* Suppression de la dépendance au modèle des Mix et PARTs.
* Affichage compact d’un événement MIDI par ligne.
* Affichage des canaux MIDI de 1 à 16.
* Affichage des noms de notes.
* Ajout de l’affichage des messages :

  * Note On ;
  * Note Off ;
  * Control Change ;
  * Program Change ;
  * Pitch Wheel ;
  * Aftertouch ;
  * Polyphonic Aftertouch ;
  * SysEx ;
  * Quarter Frame ;
  * Song Position ;
  * Song Select ;
  * Tune Request ;
  * MIDI Clock ;
  * Start ;
  * Continue ;
  * Stop ;
  * Active Sensing ;
  * Reset.
* Affichage des messages MIDI inconnus plutôt que leur suppression silencieuse.
* Ajout des noms standards des principaux contrôleurs MIDI CC.
* Affichage lisible des contrôleurs comme Modulation, Brightness, Resonance, Reverb, Chorus et contrôleurs généraux.

### Bibliothèque SoundFont

* Tri alphabétique des presets SoundFont lors de l’ajout d’un instrument.

### Nettoyage interne

* Suppression de code devenu redondant dans le Contrôleur Live.
* Simplification des tests de canaux actifs.
* Audit des fonctions du contrôleur et conservation uniquement des chemins réellement utilisés.

---

## Version 2.0 - Support PROGRAM, MIX et SONG

Date : 2026-08-17

### Ajouté

#### Nouveau format de projet

* Introduction du format de projet v2.
* Ajout de `format_version`.
* Séparation des données en sections :
  * `instruments` ;
  * `programs` ;
  * `mixes` ;
  * `songs`.
* Migration des MIX existants sous la section `mixes`.
* Encapsulation des accès aux MIX dans `FusionProject`.

#### Mode PROGRAM

* Ajout de la capture des PROGRAM du Fusion 8HD.
* Stockage des PROGRAM dans `fusion.json`.
* Ajout de la gestion des PROGRAM dans l'éditeur.
* Affectation d'instruments SoundFont aux PROGRAM.
* Ajout du support PROGRAM dans le Contrôleur Live.
* Détection des changements de PROGRAM par Bank Select et Program Change.
* Routage MIDI d'un PROGRAM vers l'instrument SoundFont configuré.

#### Mode SONG

* Ajout de la capture des SONG du Fusion 8HD.
* Capture de la configuration statique des canaux :
  * Bank ;
  * Program ;
  * Volume ;
  * Pan ;
  * Expression ;
  * Reverb ;
  * Chorus.
* Les événements temporels de la SONG restent pilotés par le séquenceur du Fusion.
* Utilisation de `SONG SELECT` comme signal de sélection et non comme identifiant de SONG.
* Ajout d'identifiants libres pour les SONG.
* Demande de l'identifiant à chaque nouvelle sélection de SONG.
* Détection des SONG déjà enregistrées avant réenregistrement.
* Confirmation avant remplacement d'une SONG existante.
* Possibilité de choisir un autre identifiant sans refaire un `SONG SELECT`.
* Conservation des associations SoundFont lors d'un réenregistrement si le Bank/Program Fusion du canal n'a pas changé.
* Refus de sauvegarder une SONG lorsqu'aucun canal n'a été détecté.

#### Éditeur SONG

* Ajout de la liste des SONG.
* Affichage des canaux et des Bank/Program Fusion.
* Affectation d'un instrument SoundFont à chaque canal d'une SONG.
* Réutilisation de la bibliothèque commune d'instruments SoundFont.

#### Contrôleur Live SONG

* Ajout du mode SONG au Contrôleur Live.
* Sélection d'une SONG enregistrée par son identifiant.
* Chargement de la configuration SoundFont au `START`.
* Chargement des instruments et des paramètres statiques par canal.
* Transmission des notes, contrôleurs MIDI et Pitch Bend des canaux actifs.
* Interception des Bank Select et Program Change Fusion afin de préserver le mapping SoundFont.
* Rechargement d'une SONG à chaque `START`.

### Amélioré

#### Contrôleur Live

* Généralisation de l'état courant :
  * `current_mode` ;
  * `current_performance`.
* Support uniforme des modes PROGRAM, MIX et SONG.
* Généralisation du rechargement de la performance courante.
* Ajout d'un menu de sélection du mode Live.

#### Éditeur

* Renommage de `editor.py` en `fusion_editor.py`.
* Harmonisation du menu principal :
  * Gestion MIX ;
  * Gestion PROGRAM ;
  * Gestion SONG ;
  * Gestion Instruments.
* Organisation cohérente des sous-menus par type de performance.

#### État du système

* Ajout du nombre de PROGRAM enregistrés.
* Ajout du nombre de SONG enregistrées.
* Conservation du nombre de MIX enregistrés.

### Nettoyage interne

* Suppression d'anciens fichiers de sauvegarde du projet.
* Nettoyage de constantes devenues redondantes.
* Correction de résidus de code issus du format v1.
* Ajout de fichiers accessoires à `.gitignore`.

---

## Version 2.1 - Gestion et validation des performances

Date : 2026-08-19

### Ajouté

#### Gestion PROGRAM

* Ajout du renommage des PROGRAM.
* Ajout de la suppression des PROGRAM.
* Ajout d'un diagnostic détaillé des PROGRAM.
* Ajout d'un état synthétique dans la liste :
  * OK ;
  * À configurer ;
  * Erreur Fusion.
* Ajout d'un vrai menu d'édition PROGRAM :
  * modification de l'instrument ;
  * modification des paramètres de la PART.
* Réutilisation de l'éditeur commun des paramètres de PART.
* Validation des paramètres PROGRAM :
  * canal MIDI ;
  * plage de notes ;
  * plage de vélocité.

#### Gestion SONG

* Ajout du renommage des SONG.
* Ajout de la suppression des SONG.
* Ajout d'un diagnostic détaillé par canal.
* Ajout d'un résumé de configuration par SONG.
* Affichage du nombre de canaux configurés.
* Ajout d'un vrai menu d'édition des canaux SONG :
  * modification de l'instrument ;
  * modification des paramètres ;
  * modification du canal MIDI.
* Édition des paramètres SONG :
  * Bank ;
  * Program ;
  * Volume ;
  * Pan ;
  * Expression ;
  * Reverb ;
  * Chorus.
* Validation des canaux MIDI entre 1 et 16.
* Validation des Bank et Program.
* Validation des contrôleurs MIDI entre 0 et 127.
* Refus du déplacement d'un canal SONG vers un canal déjà utilisé.
* Correction progressive des erreurs d'une SONG sans annuler les corrections déjà valides.

### Amélioré

#### Diagnostic MIX

* Enrichissement de la liste des MIX avec :
  * nombre de PARTS ;
  * nombre de PARTS configurées ;
  * état global.
* Ajout des états :
  * OK ;
  * À configurer ;
  * Erreur Fusion ;
  * Canaux partagés.
* Validation étendue des PARTS :
  * canal MIDI ;
  * plage de notes ;
  * plage de vélocité.
* Affichage détaillé des erreurs lors de l'édition d'un MIX.

#### Diagnostic PROGRAM

* Affichage de l'état de chaque PROGRAM directement dans la liste.
* Affichage détaillé des erreurs lors de l'édition.
* Distinction entre erreur Fusion et absence de configuration SoundFont.

#### Diagnostic SONG

* Affichage du nombre de canaux configurés.
* Distinction entre :
  * OK ;
  * À configurer ;
  * Erreur Fusion.
* Centralisation de la validation des canaux SONG.
* Utilisation de la même logique de validation par :
  * la validation globale ;
  * le diagnostic ;
  * l'éditeur.

#### Validation globale

* Extension de la validation globale aux MIX, PROGRAM et SONG.
* Regroupement des erreurs par catégorie :
  * MIX ;
  * PROGRAM ;
  * SONG.
* Conservation des diagnostics informatifs séparément des erreurs bloquantes.
* Les conflits de canaux MIDI dans un MIX restent signalés comme information lorsqu'ils peuvent être volontaires.
* Les diagnostics informatifs n'empêchent plus la sauvegarde.
* Affichage de la cause réelle lorsqu'une sauvegarde est refusée.

#### Éditeur

* Harmonisation accrue des fonctions de gestion entre MIX, PROGRAM et SONG.
* Amélioration de la lisibilité des listes PROGRAM, MIX et SONG.
* Ajout de résumés d'état permettant d'identifier rapidement les configurations à corriger.
* Extraction de la saisie commune des paramètres de PART afin de la réutiliser pour MIX et PROGRAM.

### Nettoyage interne

* Centralisation des règles de validation des canaux SONG.
* Réduction de la duplication entre diagnostic et validation.
* Traitement uniforme des erreurs bloquantes et des diagnostics informatifs.

---

## Version 2.2 - Diagnostic et correction assistée

Date : 2026-08-20

### Ajouté

#### Résumé global du projet

* Ajout d'un résumé de l'état du projet dans l'éditeur.
* Affichage synthétique pour MIX, PROGRAM et SONG :
  * nombre total ;
  * éléments OK ;
  * éléments à configurer ;
  * éléments en erreur ;
  * informations non bloquantes pour les MIX.
* Les canaux partagés d'un MIX sont comptabilisés comme information sans invalider l'état global.

#### Filtres de diagnostic

* Ajout de filtres dans les menus MIX, PROGRAM et SONG :
  * liste complète ;
  * à configurer ;
  * en erreur.
* Les listes filtrées ne présentent que les performances correspondant à l'état demandé.
* Ajout d'un message explicite lorsqu'aucun élément ne correspond au filtre.

#### Correction assistée

* Ajout de l'édition directe depuis les listes filtrées.
* Les listes filtrées retournent les identifiants réellement affichés.
* Validation de l'identifiant choisi avant l'ouverture de l'éditeur.
* Recalcul automatique de la liste après chaque correction.
* Une performance disparaît automatiquement de la liste lorsqu'elle devient valide ou entièrement configurée.
* Possibilité d'enchaîner les corrections sans revenir au menu principal.
* Support de la correction assistée pour :
  * MIX ;
  * PROGRAM ;
  * SONG.

#### Ajout d'instrument en contexte

* Ajout de l'option `Ajouter un instrument` directement dans le choix d'instrument.
* Possibilité d'ajouter un instrument depuis :
  * la bibliothèque SoundFont ;
  * la saisie manuelle.
* Reconstruction automatique de la liste des instruments après ajout.
* Le nouvel instrument peut être sélectionné immédiatement sans quitter l'édition en cours.

### Amélioré

#### Éditeur

* Réduction du nombre d'étapes nécessaires pour corriger une configuration.
* Navigation plus directe entre diagnostic et édition.
* Conservation du contexte courant lors de l'ajout d'un instrument.
* Mise à jour dynamique du résumé global après les corrections.

#### Diagnostic

* Uniformisation de la classification des performances :
  * OK ;
  * À configurer ;
  * Erreur Fusion.
* Conservation des informations non bloquantes indépendamment de l'état principal.
* Traitement cohérent des performances vides comme éléments à configurer plutôt que comme éléments valides.

### Nettoyage interne

* Réutilisation des diagnostics existants pour construire le résumé global.
* Centralisation du calcul des états sans duplication des règles de validation.
* Réutilisation du même mécanisme de filtrage pour MIX, PROGRAM et SONG.

---

## Version 2.3 - Continuité et robustesse du Contrôleur Live

Date : 2026-08-21

### Ajouté

#### Persistance des performances Live

* Remplacement de la mémorisation spécifique au dernier MIX par une persistance commune aux trois modes Live.
* Mémorisation indépendante de la dernière performance utilisée pour :
  * PROGRAM ;
  * MIX ;
  * SONG.
* Ajout du fichier d'état `last_performance.json`.
* Conservation simultanée de la dernière performance de chaque mode.
* Reprise automatique de la dernière performance PROGRAM.
* Reprise automatique de la dernière performance MIX.
* Présélection de la dernière SONG utilisée.
* La SONG présélectionnée reste chargée uniquement lors de la réception du `START`.

#### Navigation SONG

* Ajout d'une boucle de sélection dédiée au mode SONG.
* `Ctrl+C` en mode SONG retourne à la sélection des SONG plutôt qu'au menu principal.
* Possibilité d'enchaîner plusieurs SONG sans quitter le Contrôleur Live.
* `q` dans la sélection SONG permet de revenir au menu principal.
* Conservation du comportement du Fusion :
  * `SONG SELECT` reste traité comme signal de sélection et non comme identifiant ;
  * le chargement de la SONG reste déclenché au `START`.
* Refus propre des SONG sans canal utilisable sans perturber la dernière configuration active.

### Amélioré

#### Contrôleur Live

* Uniformisation des en-têtes de chargement pour PROGRAM, MIX et SONG.
* Ajout d'un message explicite lors de la reprise automatique d'un PROGRAM ou d'un MIX.
* Remplacement des messages d'attente par un état reflétant la disponibilité réelle du contrôleur :
  * PROGRAM prêt à jouer en attente d'un changement ;
  * MIX prêt à jouer en attente d'un changement ;
  * SONG sélectionnée en attente du `START`.
* Les performances MIX sans PART configurée pour FluidSynth sont désormais refusées avant de remplacer la performance courante.
* Une sélection MIX inconnue ou inutilisable ne détruit plus la configuration Live déjà active.
* Extraction de la boucle MIDI principale afin de simplifier la gestion distincte des modes PROGRAM, MIX et SONG.

#### Diagnostic

* Ajout du module `fusion_diagnostic.py`.
* Centralisation de l'affichage des erreurs et diagnostics.
* Utilisation commune du même affichage par :
  * l'éditeur ;
  * le Contrôleur Live ;
  * la capture lorsque pertinent.
* Ajout de deux niveaux de présentation :
  * diagnostic complet regroupé par MIX, PROGRAM et SONG ;
  * messages d'erreur courts pour les opérations locales.
* Les conflits de canaux MIDI sont affichés comme informations non bloquantes dans le Contrôleur Live au lieu d'être montrés sous forme de dictionnaire Python brut.

#### Robustesse des transactions

* Généralisation du filtrage des diagnostics non bloquants dans les opérations transactionnelles du projet.
* Les conflits de canaux MIDI volontairement partagés ne bloquent plus :
  * renommage des MIX ;
  * duplication des MIX ;
  * suppression des MIX ;
  * suppression des MIX vides ;
  * remplacement des PARTS ;
  * renommage et suppression des PROGRAM ;
  * renommage et suppression des SONG.
* Uniformisation de la règle déjà appliquée à la sauvegarde et à la modification des PARTS.

### Nettoyage interne

* Remplacement de `LAST_MIX_FILE` par une persistance générique des performances.
* Suppression des derniers chemins de reprise spécifiques au MIX.
* Réduction de la duplication dans l'affichage des erreurs.
* Séparation plus nette entre :
  * validation du projet ;
  * présentation des diagnostics ;
  * logique du Contrôleur Live.

---

## Version 2.4 - Restructuration et navigation du Contrôleur Live

Date : 2026-08-21

### Ajouté

#### Architecture du Contrôleur Live

* Séparation de l'état du contrôleur dans `fusion_controller_state.py`.
* Centralisation de l'état courant :
  * mode actif ;
  * performance courante ;
  * PARTS ou canaux actifs ;
  * notes actives ;
  * état du reload différé.
* Déplacement de la persistance des dernières performances dans le module d'état.

#### Chargement des performances

* Ajout du module `fusion_performance.py`.
* Déplacement de la logique de chargement des performances hors de `fusion_controller.py`.
* Regroupement des fonctions liées à :
  * PROGRAM ;
  * MIX ;
  * SONG ;
  * envoi Bank/Program vers FluidSynth ;
  * rechargement de la performance courante.
* Conservation du comportement Live existant après extraction.

#### Boucle MIDI

* Ajout du module `fusion_controller_loop.py`.
* Extraction de la boucle principale de traitement MIDI.
* Déplacement de la gestion du reload différé dans la couche de boucle Live.
* Conservation du traitement existant pour :
  * notes ;
  * contrôleurs MIDI ;
  * Pitch Bend ;
  * Aftertouch ;
  * Program Change ;
  * Bank Select ;
  * START ;
  * SONG SELECT.

### Amélioré

#### Navigation du Contrôleur Live

* Le Contrôleur Live devient une interface autonome.
* Possibilité de passer entre PROGRAM, MIX et SONG sans revenir au menu principal de Fusion2QSynth.
* `Ctrl+C` en mode PROGRAM revient au menu du Contrôleur Live.
* `Ctrl+C` en mode MIX revient au menu du Contrôleur Live.
* En mode SONG :
  * `Ctrl+C` revient à la sélection des SONG ;
  * `q` depuis la sélection retourne au menu du Contrôleur Live.
* `q` depuis le menu du Contrôleur Live retourne au menu principal.
* Les ports MIDI restent ouverts lors des changements de mode.

#### Orchestration

* Extraction de la sélection du mode hors de `main()`.
* Extraction de l'affichage des diagnostics propres à chaque mode.
* Simplification de `main()` afin qu'il se concentre sur :
  * l'ouverture des ports MIDI ;
  * la sélection du mode ;
  * la reprise de la dernière performance ;
  * l'orchestration des différentes boucles Live.

### Nettoyage interne

* Réduction importante de la taille de `fusion_controller.py`.
* Passage d'un contrôleur monolithique d'environ 1500 lignes à plusieurs modules spécialisés.
* Séparation plus nette entre :
  * orchestration ;
  * état et persistance ;
  * chargement des performances ;
  * traitement MIDI Live.
* Conservation d'un comportement fonctionnel identique après chaque étape de restructuration.

---

## Version 2.5 - Suggestions d'instruments et validation fonctionnelle

Date : 2026-09-01

### Ajouté

#### Correspondance des sons Fusion vers General MIDI

* Ajout d'une table de correspondance entre les noms de sons du Fusion et les programmes General MIDI.
* Prise en charge des aliases et variantes de noms provenant des différentes banques du Fusion.
* Normalisation des noms afin de reconnaître les variations de ponctuation, d'espacement et de typographie.
* Association des sons reconnus à une famille d'instruments et, lorsque possible, à un programme GM précis.
* Validation exhaustive de la table de correspondance et de ses aliases.

#### Suggestions d'instruments

* Ajout de suggestions automatiques dans l'Éditeur à partir du nom du son Fusion.
* Priorité donnée à une correspondance GM exacte lorsqu'elle existe.
* Recherche par famille d'instruments lorsqu'aucune correspondance exacte n'est disponible.
* Classement des suggestions selon leur pertinence.
* Possibilité d'afficher tous les instruments lorsque les suggestions proposées ne conviennent pas.
* Conservation du comportement existant pour les sons Fusion inconnus.

#### Kits de batterie

* Identification spécifique des véritables kits de batterie General MIDI.
* Distinction entre kits de batterie et instruments de percussion mélodiques.
* Association des kits GM à la banque SoundFont 128 appropriée.

### Amélioré

#### Gestion des banques SoundFont

* Prise en charge des banques SoundFont sur 14 bits.
* Conversion des numéros de banque en Bank Select MSB et LSB.
* Compatibilité avec le mode MIDI Bank Select `mma` de FluidSynth.
* Prise en charge correcte des banques de percussion telles que la banque 128.
* Correction de la sélection des banques lors :

  * du test d'un instrument ;
  * du test complet d'un MIX ;
  * du chargement des performances dans le Contrôleur Live.

#### Éditeur

* Correction du test d'un instrument utilisant une banque SoundFont supérieure à 127.
* Correction de la comparaison A/B lorsqu'une PART ne possède encore aucun instrument configuré.
* Validation réelle des suggestions avec :

  * correspondance GM exacte ;
  * correspondance par famille ;
  * kit de batterie ;
  * son Fusion inconnu.

### Validation

#### Tests fonctionnels

* Validation complète de la capture :

  * MIX existant et nouveau ;
  * remplacement d'un MIX ;
  * PROGRAM ;
  * SONG ;
  * retour propre par `Ctrl+C`.
* Validation des fonctions essentielles de l'Éditeur :

  * MIX ;
  * PROGRAM ;
  * SONG ;
  * gestion de la bibliothèque d'instruments.
* Validation du Contrôleur Live en modes :

  * PROGRAM ;
  * MIX ;
  * SONG.
* Validation du Monitor MIDI.
* Confirmation du comportement des zones clavier du Fusion lors du routage des PARTS.

#### Validation des suggestions

* Validation exhaustive des aliases de la table GM.
* Vérification de la stabilité et du classement des suggestions.
* Vérification des limites et des paramètres des instruments proposés.
* Validation réelle dans l'Éditeur des sons :

  * `Chimey` ;
  * `French Horn` ;
  * `Ethnic Percussion Kit` ;
  * `TransForce` ;
  * `Velo Pulls` ;
  * `We Are Electric Friends`.

### Nettoyage des données

* Validation de la structure de `fusion.json`.
* Migration d'anciennes PARTS utilisant directement `name`, `sf2_bank` et `sf2_program` vers le schéma actuel basé sur la bibliothèque d'instruments.
* Vérification des références d'instruments des MIX, PROGRAM et SONG.
* Vérification des plages MIDI et des banques SoundFont.
* Confirmation de la représentation 14 bits des banques MIDI dans les SONG.
* Suppression du doublon historique `drawbarorgan` au profit de l'identifiant canonique `drawbar_organ`.

---

## Version 2.6 — Harmonisation des banques Fusion et de l’édition

Date : 2026-09-02

### Banques Fusion

* Ajout des noms des banques PROGRAM du Fusion :

  * `ROM:PRESET 1` à `ROM:PRESET 4` ;
  * `ROM:ELECTRONICA` ;
  * `ROM:SYNTH DRUM` ;
  * `ROM:MORE` ;
  * `ROM:GM` ;
  * `HD:USER` ;
  * banques `ROM:Hollow Sun`.
* Ajout des noms des banques MIX :

  * `ROM:GROOVE MIX` ;
  * `ROM:SPLIT LAYER` ;
  * `HD:User` ;
  * `HD:My Bank1`.
* Affichage des noms de banques dans les listes et les écrans d'édition.
* Ajout d'un sélecteur de banque Fusion par nom dans les éditeurs.
* Affichage des noms de banques dans le Contrôleur Live, selon le type de performance PROGRAM ou MIX.
* Conservation des identifiants numériques `bank:program` pour le stockage et le traitement interne.

### Capture SONG

* Correction de l'interprétation du `Bank Select` reçu lors de la capture d'une SONG.
* Le `CC0` reçu du Fusion est maintenant conservé directement comme numéro de banque Fusion.
* Suppression de la conversion erronée du couple MSB/LSB en banque MIDI 14 bits pour le champ `bank` d'un canal SONG.
* Validation réelle d'une banque `HD:USER` transmise par `CC0 = 8`.
* Conservation de la détection du `CC32` pour permettre l'analyse ultérieure d'éventuelles banques utilisant un LSB.

### Capture MIX

* Distinction entre l'identifiant du MIX transmis lors de sa sélection et les PARTS réellement jouées.
* La détection des PARTS d'un MIX repose maintenant sur leurs canaux MIDI actifs.
* Suppression de l'attribution artificielle d'une banque et d'un programme aux PARTS lorsque ces informations ne sont pas transmises par le Fusion.
* Conservation des informations connues des PARTS des MIX ROM lors d'une nouvelle capture, par correspondance de canal MIDI.
* Prévention de la réutilisation silencieuse d'informations potentiellement périmées pour les MIX utilisateur modifiables.

### Éditeur

* Harmonisation de l'édition des PROGRAM, MIX et SONG.
* Affichage uniforme :

  * du nom Fusion ;
  * de la banque Fusion ;
  * du programme Fusion ;
  * de l'instrument associé ;
  * des paramètres MIDI pertinents.
* Ajout de boucles d'édition imbriquées :

  * une PART MIX reste sélectionnée pendant plusieurs modifications ;
  * un canal SONG reste sélectionné pendant plusieurs modifications ;
  * `q` retourne uniquement au niveau d'édition précédent.
* Amélioration de l'affichage des plages de notes, incluant les limites MIDI par défaut.
* Ajout et modification du nom Fusion directement depuis les éditeurs.
* Utilisation des suggestions d'instruments à partir du nom Fusion dans les différents types de performances.

### Validation et réparation progressive

* Amélioration de `save_safe()` pour permettre explicitement la conservation d'erreurs préexistantes pendant une réparation progressive.
* Une modification est acceptée lorsqu'elle corrige ou conserve l'état existant sans introduire de nouvelle erreur bloquante.
* Annulation en mémoire des modifications lorsqu'une sauvegarde est refusée.
* Application de cette logique aux PARTS, PROGRAM et canaux SONG.

### Listes

* Amélioration de la liste PROGRAM avec affichage des noms de banques Fusion.
* Amélioration de la liste SONG avec :

  * état de configuration ;
  * instrument associé ;
  * nom de banque Fusion ;
  * couple `bank:program`.
* Distinction visuelle correcte des banques ROM et utilisateur.

### Validation

* Validation de la capture réelle des PROGRAM, MIX et SONG.
* Validation de l'édition des PROGRAM, MIX et SONG.
* Validation des nouvelles boucles d'édition imbriquées.
* Validation d'une SONG utilisant la banque `HD:USER`.
* Validation du Contrôleur Live avec affichage des banques nommées en modes PROGRAM et MIX.
* Validation de `integration-globale.py` :

  * aucune suggestion invalide ;
  * aucun doublon de suggestion ;
  * aucun champ manquant ;
  * aucun score mal ordonné ou aberrant ;
  * aucune limite dépassée ;
  * aucune instabilité du classement ;
  * 1209 aliases GM testés ;
  * aucune erreur dans `FUSION_GM_DATA`.

---

## Fusion2QSynth v2.7

### Version 2.7

La version 2.7 poursuit la consolidation de l'architecture de Fusion2QSynth, avec une séparation plus nette des responsabilités du Contrôleur Live, une meilleure protection du mapping SoundFont et une validation renforcée des correspondances Fusion / General MIDI.

#### Contrôleur Live

* Refactorisation du Contrôleur Live afin de séparer l'orchestration, la boucle MIDI, l'état dynamique et le chargement des performances.
* Répartition des responsabilités entre :

  * `fusion_controller.py` ;
  * `fusion_controller_loop.py` ;
  * `fusion_controller_state.py` ;
  * `fusion_performance.py`.
* Centralisation du chargement des PROGRAM, MIX et SONG dans `fusion_performance.py`.
* Centralisation de l'état dynamique dans `fusion_controller_state.py`.
* Gestion explicite de :

  * `current_mode` ;
  * `current_performance` ;
  * `current_parts` ;
  * `active_notes` ;
  * `pending_reload`.
* Séparation claire entre l'état persistant du projet et l'état temporaire du Contrôleur Live.

#### Traitement MIDI du Contrôleur Live

* Correction du traitement des `Bank Select` en modes PROGRAM et MIX.
* Le `CC0` reçu sur le canal MIDI par défaut du Fusion est utilisé pour détecter la banque de la performance sélectionnée.
* Initialisation de la banque détectée avec `None` afin de distinguer correctement :

  * l'absence de `Bank Select` ;
  * la banque valide `0`.
* Un `Program Change` de sélection de performance n'est traité que lorsqu'une banque a préalablement été détectée.
* Les `CC0` et `CC32` provenant des PARTS ne sont plus retransmis à FluidSynth en modes PROGRAM et MIX.
* Cette protection empêche les `Bank Select` du Fusion d'écraser le mapping SoundFont défini dans Fusion2QSynth.
* Les contrôleurs provenant de PARTS non actives sont ignorés.
* Les autres contrôleurs MIDI autorisés continuent d'être transmis à FluidSynth.
* En mode SONG, les `Program Change` sont ignorés.
* Le chargement de la SONG sélectionnée reste déclenché par le message MIDI `START`.

#### Mapping Fusion / General MIDI

* Consolidation de `fusion_gm_map.py` comme source centrale des données de correspondance Fusion / General MIDI.
* Consolidation de `fusion_suggestions.py` pour la détection des familles et le classement des presets proposés.
* Suppression de l'ancienne structure `GM_DRUM_KITS` devenue inutile.
* Utilisation de `GM_DRUM_KIT_PROGRAMS` pour l'identification des kits de batterie GM.
* Correction des mappings responsables des conflits apparents :

  * `Sine Lead` ;
  * `Stereo 12-Strings`.
* Validation exhaustive des aliases définis dans `FUSION_GM_DATA`.

#### SoundFonts

* Consolidation de `sf2_library.py` comme interface de la bibliothèque de presets SoundFont.
* Séparation explicite entre :

  * les banques et programmes provenant du Fusion ;
  * les banques et programmes des SoundFonts.
* Les instruments persistants utilisent :

  * `sf2_bank` ;
  * `sf2_program`.
* Les performances référencent les instruments par leur identifiant plutôt que de dupliquer les coordonnées SoundFont.
* Prise en charge des banques SoundFont supérieures à 127 par conversion :

  * `MSB = sf2_bank // 128` ;
  * `LSB = sf2_bank % 128`.
* Programmation de FluidSynth par `CC0`, `CC32` et `Program Change`.

#### Encapsulation et architecture

* Consolidation de `FusionProject` comme interface unique du modèle persistant.
* Séparation entre :

  * modèle persistant ;
  * logique applicative ;
  * état dynamique ;
  * services SoundFont ;
  * outils de diagnostic ;
  * outils de développement.
* Clarification de la convention des canaux MIDI :

  * Fusion2QSynth et `fusion.json` : canaux `1..16` ;
  * Mido : canaux `0..15`.
* Conversion des canaux effectuée à la frontière avec Mido.
* Maintien de la séparation entre données Fusion et données SoundFont.
* Centralisation des constantes communes dans `fusion_constants.py`.
* Centralisation des fonctions techniques communes dans `fusion_lib.py`.

#### Nettoyage

* Suppression ou retrait de la documentation des anciens outils de développement devenus obsolètes :

  * `compare_fusion_sf2.py` ;
  * `plage-GM.py` ;
  * `parse_sf2_program_list.py` ;
  * `test-global.py`.
* Conservation de `integration-globale.py` comme outil officiel de validation globale.
* Retrait de l'ancien `ROADMAP.md`, devenu obsolète.

#### Documentation

* Révision complète de `ARCHITECTURE.md` pour refléter l'architecture actuelle.
* Documentation du modèle `fusion.json` et de ses collections :

  * `instruments` ;
  * `programs` ;
  * `mixes` ;
  * `songs`.
* Documentation des banques SoundFont et de leur conversion MIDI.
* Documentation des flux :

  * Capture ;
  * Édition ;
  * Contrôleur Live.
* Documentation de la validation et de la réparation progressive.
* Documentation de la sauvegarde du modèle.
* Documentation de l'encapsulation et des dépendances entre modules.
* Documentation des limites MIDI observées du Fusion 8HD.
* Formalisation des principes de conception du projet.
* Documentation des possibilités d'évolution future.
* Ajout d'une section décrivant la philosophie du projet.
* Révision complète de `README.md` afin de l'aligner sur l'architecture et les fonctionnalités de la version 2.7.
* Création d'un `TODO` séparant les améliorations futures de l'architecture actuellement implantée.

#### Validation

* Validation finale de `integration-globale.py`.
* Validation de 61 noms Fusion :

  * 56 avec Hint GM ;
  * 3 identifiés par famille seulement ;
  * 2 inconnus (`Program 1` et `TransForce`).
* Aucun conflit apparent.
* Aucun Hint GM non respecté.
* Aucun meilleur Hint GM incorrect.
* Aucune famille seule incorrecte.
* Aucune suggestion invalide.
* Aucun doublon de suggestion.
* Aucun preset avec champ manquant.
* Aucun score mal ordonné.
* Aucun score aberrant.
* Aucune limite dépassée.
* Aucune erreur du paramètre `limit`.
* Aucun Top 1 instable.
* Aucun Top N instable.
* Validation exhaustive de 1209 aliases GM.
* Aucune erreur dans `FUSION_GM_DATA`.

---

## Fusion2QSynth v2.8

### Version 2.8

La version 2.8 poursuit la consolidation de Fusion2QSynth en unifiant le système de journalisation, en documentant les mécanismes de sauvegarde, d'archivage et de récupération du projet, et en améliorant la capture des SONG afin de réutiliser automatiquement les PROGRAM déjà connus.

#### Journalisation

* Unification du système de journalisation dans `fusion_lib.py`.
* Suppression de l'ancien mécanisme `_log()` qui écrivait directement dans le fichier journal.
* Utilisation du module standard Python `logging` pour l'ensemble des messages du projet.
* Conservation des interfaces publiques :
  * `log_info()` ;
  * `log_warning()` ;
  * `log_event()` ;
  * `log_error()`.
* Conservation de la distinction sémantique entre les messages d'information et les événements, tout en utilisant le même niveau `INFO` dans le journal.
* Centralisation du format et de la destination du journal par `logging.basicConfig()`.

#### Sauvegarde du projet

* Documentation détaillée de `save_safe()` comme mécanisme central de sauvegarde de `fusion.json`.
* Validation du modèle avant toute sauvegarde.
* Distinction entre les erreurs bloquantes et les erreurs autorisées ou préexistantes.
* Rotation automatique des sauvegardes locales :
  * `fusion.json.bak` ;
  * `fusion.json.bak1` ;
  * `fusion.json.bak2`.
* Écriture du nouveau modèle dans un fichier temporaire avant le remplacement final de `fusion.json`.
* Utilisation de `os.replace()` pour le remplacement final du fichier.
* Maintien de `FusionProject` comme interface unique de modification et de sauvegarde du modèle persistant.

#### Archivage

* Documentation du mécanisme d'archivage historique de `fusion.json`.
* Conservation des archives dans le répertoire `backups`.
* Création d'archives horodatées sous la forme :
  * `fusion-YYYY-MM-DD_HHMMSS.json`.
* Conservation automatique des 30 archives les plus récentes.
* Utilisation de SHA-256 pour déterminer si l'état courant du projet est déjà présent parmi les archives conservées.
* `archive_if_changed()` évite la création d'une nouvelle archive lorsqu'un contenu identique existe déjà.
* Création automatique d'une archive lors de la sortie normale du programme lorsque le projet a changé.
* Possibilité de créer manuellement une archive depuis le menu principal.

#### Récupération

* Documentation détaillée du mécanisme de récupération d'un projet dont `fusion.json` est invalide.
* Distinction entre :
  * une erreur permettant une récupération depuis les sauvegardes locales ;
  * une erreur de chargement ne permettant pas cette récupération automatique.
* Présentation des sauvegardes `.bak`, `.bak1` et `.bak2` disponibles lors d'une récupération.
* Validation du projet après restauration depuis une sauvegarde locale.
* Journalisation séparée des opérations de récupération dans `fusion_recovery.log`.
* Validation des archives avant leur présentation comme candidates à une restauration.
* Les erreurs non bloquantes, notamment les conflits de canaux MIDI autorisés par le modèle, n'empêchent pas une archive d'être considérée comme valide.
* Validation d'une archive avant le remplacement du projet courant.
* Protection de l'état courant par `archive_if_changed()` avant une restauration depuis une archive.
* Possibilité de restaurer manuellement une archive depuis le menu principal.

#### Capture SONG

* Amélioration de la capture des SONG par reconnaissance automatique des PROGRAM déjà enregistrés.
* Utilisation de la combinaison `bank:program` comme identifiant d'un PROGRAM connu.
* Pour chaque canal capturé, recherche du PROGRAM correspondant dans le projet.
* Lorsqu'un PROGRAM connu possède un seul PART, récupération automatique :
  * du nom Fusion dans `fusion_name` ;
  * de l'instrument associé dans `instrument`.
* Les canaux dont le `bank:program` ne correspond à aucun PROGRAM connu restent non configurés.
* Aucune correspondance approximative n'est effectuée lors de cette assignation.

#### Recapture SONG

* Amélioration de la recapture d'une SONG déjà enregistrée.
* Comparaison du `bank:program` capturé avec celui déjà enregistré pour chaque canal.
* Lorsque le PROGRAM est inchangé, conservation des choix existants de `instrument` et `fusion_name`.
* Lorsqu'un PROGRAM diffère, présentation des valeurs enregistrées et capturées à l'utilisateur.
* L'utilisateur peut alors choisir entre :
  * conserver la configuration existante de Fusion2QSynth ;
  * accepter la nouvelle configuration reçue du Fusion.
* La conservation de la configuration existante préserve le canal enregistré complet.
* L'acceptation de la nouvelle configuration permet à une modification effectuée directement sur le Fusion d'être intégrée au projet.
* Lorsqu'une nouvelle configuration acceptée correspond à un PROGRAM connu, son nom Fusion et son instrument sont assignés automatiquement.
* Ce mécanisme permet de modifier une SONG aussi bien sur le Fusion que dans Fusion2QSynth sans imposer systématiquement la priorité de l'un sur l'autre.

#### Documentation

* Mise à jour de `ARCHITECTURE.md` pour documenter l'unification du système de journalisation.
* Documentation détaillée des mécanismes de :
  * sauvegarde ;
  * rotation des sauvegardes ;
  * archivage ;
  * rotation des archives ;
  * détection des archives identiques ;
  * récupération depuis une sauvegarde ;
  * restauration depuis une archive.
* Documentation de l'assignation automatique des PROGRAM lors de la capture SONG.
* Documentation de la gestion des conflits entre une SONG modifiée sur le Fusion et une SONG modifiée dans Fusion2QSynth.
* Résolution des améliorations restantes consignées dans `TODO`.

---

## Fusion2QSynth v2.9

### SONG — Support multi-PROGRAM

* Ajout du support de plusieurs PROGRAMs Fusion sur un même canal MIDI d'une SONG.
* Nouveau format `programs` par canal permettant de mémoriser tous les PROGRAMs observés pendant la capture.
* Traitement dynamique des `PROGRAM_CHANGE` pendant la lecture d'une SONG.
* Le Fusion demeure maître du séquencement et du moment où les changements de PROGRAM doivent être appliqués.
* Mémorisation indépendante de la banque Fusion courante pour chaque canal MIDI.
* Les `CC0` et `CC32` utilisés par le Fusion ne remplacent pas les banques SoundFont programmées par Fusion2QSynth.
* Les PROGRAMs non configurés sont détectés et ignorés proprement sans interrompre la SONG.
* Les notes provenant d'un canal dont le PROGRAM courant n'est pas configuré ne sont pas transmises à FluidSynth.

### Capture SONG

* Capture de plusieurs PROGRAMs successifs sur un même canal MIDI.
* Conservation de tous les PROGRAMs observés sous leur identifiant `bank:program`.
* Création automatique d'un PROGRAM global minimal valide lorsqu'un PROGRAM Fusion inconnu est détecté.
* Déduplication des PROGRAMs inconnus utilisés par plusieurs canaux.
* Support des canaux ne transmettant aucun `PROGRAM_CHANGE`, notamment les canaux pilotés par l'arpégiateur.
* Un canal sans PROGRAM est représenté par `programs: {}` et demeure valide.
* Conservation des PROGRAMs déjà connus lors d'une capture partielle.
* Conservation des paramètres statiques non observés lors d'une capture partielle.
* Conservation des canaux non observés lors d'une capture partielle.
* Migration progressive des SONGs de l'ancien format vers le nouveau format lors de leur recapture.
* Compatibilité conservée avec les SONGs de l'ancien format.

### PROGRAM global et héritage SONG

* Le PROGRAM global devient la configuration de référence pour l'instrument associé à un `bank:program`.
* Une occurrence de PROGRAM dans une SONG hérite automatiquement de l'instrument configuré dans le PROGRAM global.
* Une SONG peut définir une surcharge locale d'instrument pour un PROGRAM particulier.
* Une surcharge locale peut être supprimée afin de revenir à l'instrument hérité du PROGRAM global.
* Les modifications apportées à un PROGRAM global sont immédiatement utilisables par les SONGs qui en héritent, sans duplication de configuration.
* Le nom Fusion du PROGRAM demeure une propriété du PROGRAM global.
* Suppression des copies locales redondantes de `fusion_name`.
* Suppression des instruments locaux redondants lorsqu'ils sont identiques à l'instrument hérité.
* Conservation des véritables surcharges locales lors de la recapture d'une SONG.

### Éditeur SONG

* Adaptation de la liste des SONGs au modèle multi-PROGRAM.
* Affichage de tous les PROGRAMs associés à chaque canal.
* Tri numérique des canaux MIDI.
* Un canal multi-PROGRAM est considéré configuré seulement si tous ses PROGRAMs possèdent un instrument effectif.
* Distinction entre instrument hérité du PROGRAM global et instrument local à la SONG.
* Sélection d'un PROGRAM particulier avant l'édition de son instrument local.
* Édition des paramètres statiques au niveau du canal : volume, panoramique, expression, réverbération et chorus.
* Conservation du déplacement complet d'un canal MIDI.
* Amélioration des suggestions d'instruments pour les PROGRAMs utilisés dans une SONG.
* Utilisation du nom et du numéro du PROGRAM global pour produire les suggestions SoundFont.
* Suppression de l'édition locale du nom Fusion d'un PROGRAM dans une SONG.

### Diagnostic SONG

* Adaptation du diagnostic au modèle multi-PROGRAM.
* Résolution de l'instrument effectif par héritage global ou surcharge locale.
* Un canal contenant plusieurs PROGRAMs est considéré configuré uniquement lorsque tous ses PROGRAMs sont résolus.
* Les canaux `programs: {}` sont reconnus comme valides côté Fusion mais non configurés pour FluidSynth.
* Compatibilité conservée avec le diagnostic des SONGs de l'ancien format.
* Tri numérique des canaux dans l'affichage du diagnostic.

### Contrôleur Live — SONG

* Chargement des paramètres statiques de la SONG à la réception de `START`.
* Les PROGRAMs du nouveau format ne sont plus préchargés au démarrage de la SONG.
* Sélection de l'instrument SoundFont au moment où le Fusion transmet le `PROGRAM_CHANGE`.
* Suivi du PROGRAM et de l'instrument effectivement actifs sur chaque canal pendant l'exécution.
* Mise à jour correcte du nom de l'instrument dans les traces de notes après un changement dynamique de PROGRAM.
* Désactivation d'un canal lorsqu'un nouveau PROGRAM reçu n'est pas configuré afin d'éviter l'utilisation du preset précédent.
* Les canaux sans PROGRAM demeurent silencieux tant qu'aucun PROGRAM exploitable n'est reçu.
* Conservation de la compatibilité avec les SONGs de l'ancien format.

### Sélection et changement de SONG

* La sélection de la SONG dans Fusion2QSynth demeure manuelle, le Fusion ne fournissant pas un identifiant `song_select` exploitable pour distinguer les SONGs.
* Le Fusion demeure maître du message MIDI `START`.
* Les `song_select` successifs générés par le Fusion pendant la navigation vers une SONG sont ignorés avant `START`.
* Après `START`, un nouveau `song_select` est interprété comme un changement de SONG et provoque le retour au sélecteur de SONG.
* Le changement de SONG peut ainsi être effectué sans quitter le Contrôleur Live.

### Reload du projet

* Validation du reload immédiat d'une SONG après modification de `fusion.json`.
* La SONG courante est rechargée en conservant correctement son identité.
* Les modifications apportées aux PROGRAMs globaux deviennent immédiatement disponibles pour l'héritage SONG.
* Le reload ne provoque pas à lui seul un retour au menu de sélection de SONG.
* Les `song_select` reçus avant `START` demeurent filtrés après la sélection d'une nouvelle SONG.
* Aucun retour intempestif au sélecteur de SONG n'a été observé lors des validations.

### Régression PROGRAM

* Validation de la détection `bank:program`.
* Validation du chargement d'un PROGRAM configuré dans FluidSynth.
* Validation du traitement propre d'un PROGRAM non configuré.
* Validation de la transmission des `NOTE ON` et `NOTE OFF`.

### Régression MIX

* Validation de la détection et du changement de MIX.
* Validation du chargement des PARTs configurées d'un MIX.
* Les PARTs incomplètes sont correctement ignorées sans empêcher le chargement des autres PARTs.
* Les notes provenant des PARTs non configurées sont correctement filtrées.
* Validation du maintien de la banque de performance entre les cycles de lecture de la boucle MIDI.

### Nettoyage

* Suppression des traces DEBUG temporaires `SONG BANK CH ... Bank ...` et `PROGRAM SONG CH ... bank:program`.
* Conservation des traces DEBUG utiles au diagnostic MIDI, notamment `SONG SELECT`, `NOTE ON/OFF` et les notes ignorées.
* Conservation des messages fonctionnels indiquant les changements de PROGRAM effectifs pendant une SONG.

### Validation

* Régression du mode PROGRAM validée avec PROGRAM configuré et non configuré.
* Régression du mode MIX validée avec MIX sans PART configurée et MIX comportant plusieurs PARTs configurées et non configurées.
* Mode SONG validé avec plusieurs PROGRAMs successifs par canal, héritage depuis les PROGRAMs globaux, surcharge locale d'instrument, PROGRAMs non configurés, canaux sans PROGRAM, changements dynamiques de PROGRAM, changement de SONG et reload immédiat du projet.
* `integration-globale.py` validé sans suggestion invalide, doublon de suggestion, score mal ordonné ou aberrant, limite dépassée ni instabilité Top 1 ou Top N.
* 1209 aliases GM testés sans erreur dans `FUSION_GM_DATA`.
* Les cas `Program 1` et `TransForce` demeurent sans suggestion connue et ne constituent pas des erreurs de validation.

---

## Fusion2QSynth v2.10

### Architecture MIX — Modèle par canal

* Migration du modèle MIX vers une représentation centrée sur les canaux MIDI.
* Un canal MIX peut référencer un PROGRAM global par son identifiant `bank:program`.
* Un canal observé dont le PROGRAM est inconnu peut être représenté par `{}` et demeure valide mais non configuré.
* Un canal peut définir une surcharge locale d'instrument.
* Un instrument local peut être configuré même lorsque le PROGRAM Fusion du canal est inconnu.
* Suppression de la duplication des informations `bank`, `program`, `fusion_name`, `midi_channel` et des paramètres SoundFont dans le nouveau modèle MIX.
* Conservation de la compatibilité avec les MIX de l'ancien format basé sur les PARTs.
* Migration progressive des MIX de l'ancien format vers le nouveau format lors de leur recapture.

### Capture MIX

* La capture d'un MIX mémorise uniquement les informations réellement observables depuis le Fusion : identité du MIX et canaux MIDI actifs.
* Suppression de l'invention de valeurs `bank` ou `program` lorsqu'elles ne sont pas transmises par le Fusion.
* La recapture remplace les anciens PARTs par les canaux effectivement observés.
* Conservation du mécanisme de rollback lorsqu'une recapture introduit de nouvelles erreurs de validation.
* Prise en compte des erreurs préexistantes afin qu'elles ne bloquent pas une recapture qui n'en introduit aucune nouvelle.

### PROGRAM global et héritage MIX

* Le PROGRAM global devient la configuration de référence pour l'instrument associé à un `bank:program` utilisé dans un MIX.
* Un canal MIX hérite automatiquement de l'instrument configuré dans le PROGRAM global.
* Une surcharge locale d'instrument prend priorité sur l'instrument hérité.
* Une surcharge locale peut être supprimée afin de revenir à l'instrument du PROGRAM global.
* Les modifications d'un PROGRAM global deviennent immédiatement disponibles aux MIX qui y font référence.
* Résolution uniforme de l'instrument effectif d'un canal MIX par surcharge locale puis héritage global.

### Éditeur MIX

* Adaptation de l'éditeur au nouveau modèle MIX par canal.
* Sélection et édition des canaux MIDI d'un MIX.
* Association d'un canal à un PROGRAM global.
* Configuration d'une surcharge locale d'instrument.
* Suppression d'une surcharge locale afin de rétablir l'héritage du PROGRAM global.
* Conservation de l'éditeur historique pour les MIX de l'ancien format.

### Test MIDI MIX

* Adaptation du test MIDI au nouveau modèle par canal.
* Test individuel d'un canal ou de tous les canaux configurés d'un MIX.
* Résolution correcte des instruments hérités et des surcharges locales.
* Les canaux non configurés sont ignorés proprement.
* Arrêt sécurisé du test MIDI avec libération des notes et contrôleurs nécessaires.
* Conservation de la compatibilité avec les MIX de l'ancien format.

### Diagnostic et états de configuration

* Harmonisation des états de configuration utilisés par PROGRAM, MIX et SONG.
* Utilisation des états internes `configured`, `partial`, `unconfigured` et `error`.
* Distinction entre données valides mais non configurées, configuration partielle et erreur de validation.
* Un MIX ou une SONG est partiellement configuré lorsque certains canaux sont exploitables et d'autres non.
* Un ensemble vide ou ne contenant aucun instrument exploitable est considéré non configuré.
* Les canaux partagés de l'ancien modèle MIX demeurent un avertissement et ne constituent pas à eux seuls une erreur.
* Adaptation du diagnostic MIX au nouveau format `channels`.
* Correction du résumé global du projet afin que les erreurs des MIX au nouveau format soient correctement comptabilisées.
* Tri numérique conservé dans les diagnostics et listes de canaux.

### Validation et sauvegarde

* Les canaux MIX `{}` sont reconnus comme valides mais non configurés.
* Validation des références `bank:program` utilisées par les canaux MIX.
* Une référence vers un PROGRAM global inexistant est signalée comme erreur.
* Validation des instruments locaux associés aux canaux MIX.
* Propagation des erreurs préexistantes autorisées lors des opérations d'édition nécessitant une sauvegarde intermédiaire.
* Correction de l'éditeur PROGRAM afin qu'une erreur préexistante sans rapport avec le PROGRAM édité ne bloque plus l'affectation d'un nouvel instrument.
* Propagation de `allowed_errors` lors de la création ou de l'enregistrement d'un instrument SoundFont.

### Contrôleur Live — MIX

* Adaptation du chargement des MIX au nouveau modèle par canal.
* Chargement uniquement des canaux possédant un instrument effectif.
* Support de l'héritage depuis un PROGRAM global.
* Support des surcharges locales d'instrument.
* Support d'un instrument local sur un canal dont le PROGRAM Fusion est inconnu.
* Les canaux non configurés demeurent silencieux.
* Correction du changement vers un MIX ne contenant aucun canal configuré afin que l'ancien MIX ne demeure pas actif.
* Réinitialisation correcte de l'état du contrôleur et de FluidSynth lors d'un tel changement.
* Affichage DEBUG du véritable instrument effectif pour les MIX utilisant l'héritage PROGRAM.

### Contrôleur Live — Notes et transitions MIDI

* Unification du traitement des `NOTE ON` et `NOTE OFF`.
* Reconnaissance de `NOTE ON` avec vélocité zéro comme un `NOTE OFF` logique.
* Les `NOTE ON` provenant d'un canal inactif sont ignorés.
* Un `NOTE OFF` correspondant à une note précédemment transmise demeure accepté même si le canal est devenu inactif entre-temps.
* Suivi centralisé des notes réellement actives dans `active_notes`.
* Le reload différé attend la libération de la dernière note active.
* Le dernier `NOTE OFF` est transmis à FluidSynth avant l'exécution du reload différé.
* Prévention des notes bloquées lors des changements de configuration ou de PROGRAM.
* Conservation du filtrage des contrôleurs MIDI selon l'état actif du canal.
* Les Bank Select Fusion `CC0` et `CC32` demeurent isolés des banques SoundFont.

### Contrôleur Live — SONG

* Désactivation explicite d'un canal lorsqu'un `PROGRAM_CHANGE` reçu ne correspond à aucun PROGRAM connu de la SONG.
* Désactivation explicite d'un canal lorsqu'un PROGRAM historique ne correspond plus au PROGRAM reçu.
* Conservation des notes actives lors de la désactivation d'un canal afin que leurs `NOTE OFF` puissent encore atteindre FluidSynth.
* Validation des transitions dynamiques entre PROGRAM configuré, PROGRAM non configuré et nouveau PROGRAM configuré.
* Amélioration du sélecteur de SONG afin d'afficher systématiquement l'identifiant de la SONG et son nom descriptif lorsqu'ils diffèrent.
* Correction du retour depuis le sélecteur de SONG vers le menu du Contrôleur Live.

### Régressions PROGRAM, MIX et SONG

* Régression PROGRAM validée avec changement de PROGRAM, remplacement du son et suivi complet des `NOTE ON` et `NOTE OFF`.
* Régression MIX validée avec héritage PROGRAM global, surcharge locale, instrument local sans PROGRAM et canaux non configurés.
* Validation du remplacement complet de `current_parts` lors d'un changement de MIX.
* Validation d'un MIX ne possédant aucun canal configuré.
* Régression SONG validée sur une séquence complète avec changements dynamiques de PROGRAM.
* Validation d'un passage d'un PROGRAM non configuré vers un PROGRAM configuré pendant une SONG.
* Validation d'un passage d'un PROGRAM configuré vers un PROGRAM non configuré.
* Validation du remplacement d'instrument sur un même canal pendant l'exécution.
* Validation de la transmission du `NOTE OFF` d'une note déjà active après un changement dynamique de PROGRAM.
* Validation de la fin d'une SONG sans note active résiduelle.

### Validation globale

* `integration-globale.py` validé sans conflit apparent, hint non respecté, suggestion invalide, doublon de suggestion, preset incomplet, score mal ordonné ou aberrant, limite dépassée ni instabilité Top 1 ou Top N.
* 1221 aliases GM testés sans erreur dans `FUSION_GM_DATA`.
* Les cas `Program 1` et `TransForce` demeurent sans suggestion connue et ne constituent pas des erreurs de validation.
* Validation syntaxique finale des modules du contrôleur avec `py_compile`.

---

## Fusion2QSynth v2.11

### Migration définitive des MIX

* Migration automatique des MIX de l'ancien format `parts` vers le modèle `channels` introduit en v2.10.
* Conservation du canal MIDI observé et des éventuelles surcharges locales d'instrument lors de la migration.
* Abandon des anciennes informations redondantes `bank`, `program` et `fusion_name` des PARTs MIX.
* Migration effectuée automatiquement au chargement du projet puis sauvegardée de manière sécurisée.
* Migration atomique : aucune modification du projet n'est appliquée lorsqu'une incohérence empêche la conversion complète.
* Migration idempotente : un projet déjà converti n'est pas migré de nouveau.
* Validation finale de 139 MIX au nouveau format `channels` et absence de MIX restant à l'ancien format.

### Suppression de la compatibilité historique MIX

* Suppression du support runtime des MIX basés sur `parts`.
* Suppression des chemins de compatibilité historiques dans la validation, le diagnostic, l'éditeur, la capture et le Contrôleur Live.
* Suppression des fonctions devenues inutiles pour la manipulation des anciens PARTs MIX.
* Simplification du diagnostic et du résumé global afin d'utiliser exclusivement le modèle `channels`.
* Simplification du test MIDI MIX afin d'utiliser exclusivement les canaux du nouveau modèle.
* Conservation de `PROGRAM.parts`, qui demeure le modèle normal des PROGRAMs et n'est pas concerné par cette migration.

### Migration définitive des SONG

* Migration automatique des anciens canaux SONG utilisant directement `bank` et `program` vers le modèle `programs`.
* Conversion d'un ancien couple `bank` / `program` en référence `bank:program` dans la collection `programs` du canal.
* Conservation des paramètres statiques de canal `volume`, `pan`, `expression`, `reverb` et `chorus`.
* Conservation des surcharges locales d'instrument lorsqu'elles étaient présentes dans l'ancien format.
* Les canaux sans `bank` ni `program` deviennent des canaux valides avec `programs: {}` et demeurent non configurés.
* Une ancienne définition contenant seulement `bank` ou seulement `program` est considérée incohérente et n'est pas convertie en inventant la valeur manquante.
* Migration effectuée automatiquement au chargement du projet puis sauvegardée de manière sécurisée.
* Migration atomique et idempotente.
* Validation finale de 109 canaux SONG au nouveau format `programs` et absence de canal restant à l'ancien format.

### Suppression de la compatibilité historique SONG

* Suppression du support runtime des canaux SONG utilisant directement `bank` et `program`.
* Suppression des chemins de compatibilité historiques dans la validation, le diagnostic, l'éditeur, la capture et le Contrôleur Live.
* Le chargement d'une SONG prépare désormais les paramètres statiques des canaux puis attend les `PROGRAM_CHANGE` réellement transmis par le Fusion.
* La résolution dynamique des instruments utilise exclusivement les occurrences présentes dans `channel.programs`.
* Aucune valeur `bank`, `program` ou instrument n'est inventée pour un canal dont le Fusion ne transmet pas l'information.

### Validation différentielle

* Généralisation de la validation différentielle aux opérations de modification du projet.
* Les erreurs déjà présentes avant une opération sont tolérées lorsqu'elles ne sont pas aggravées par cette opération.
* Toute nouvelle erreur introduite par une modification demeure bloquante.
* Application de ce mécanisme aux opérations de renommage, duplication et suppression des PROGRAMs, MIX et SONG.
* Application de la validation différentielle aux captures PROGRAM, MIX et SONG.
* Application de la validation différentielle à la création et à la modification des instruments SoundFont.
* Une duplication reproduisant une erreur existante sous un nouvel identifiant est correctement détectée comme une nouvelle erreur.
* La suppression d'un PROGRAM global encore référencé par un MIX ou une SONG demeure interdite.

### Sauvegarde, archives et restauration

* Correction de la détection des archives afin qu'une archive JSON structurellement valide demeure disponible même si le projet qu'elle contient possède des erreurs de validation préexistantes.
* Séparation de la validité d'une archive et de la validité métier du projet contenu dans cette archive.
* Correction de la restauration afin que les erreurs préexistantes n'empêchent plus la récupération d'une archive lisible.
* Le chargement suivant une restauration applique automatiquement les migrations de format nécessaires.
* Validation de la restauration complète d'un projet contenant des erreurs préexistantes autorisées.

### Éditeur SONG

* Adaptation définitive de l'éditeur au modèle `channel.programs`.
* Support uniforme des canaux sans PROGRAM, avec un PROGRAM ou avec plusieurs PROGRAMs.
* Correction de la navigation avec `q` afin de revenir au niveau logique précédent selon le nombre de PROGRAMs disponibles.
* Conservation et édition correcte des surcharges locales d'instrument.
* Résolution correcte des instruments hérités depuis les PROGRAMs globaux.

### Capture PROGRAM et SONG

* Correction de la capture PROGRAM afin que les erreurs préexistantes du projet ne bloquent pas une capture valide.
* Correction équivalente de la capture SONG.
* Conservation du mécanisme de rollback lorsqu'une capture introduit une nouvelle erreur.
* Validation de la recapture partielle d'une SONG avec conservation des PROGRAMs existants, des surcharges locales et des contrôleurs statiques non remplacés.

### Contrôleur Live — SONG

* Validation du fonctionnement du Contrôleur Live avec le modèle SONG définitif basé sur `programs`.
* Validation des changements dynamiques de PROGRAM pendant l'exécution d'une SONG.
* Validation de l'héritage depuis les PROGRAMs globaux et des surcharges locales d'instrument.
* Les PROGRAMs non configurés sont correctement détectés et les canaux concernés demeurent silencieux.
* Validation d'une SONG contenant un canal sans PROGRAM connu sans invention de PROGRAM ni d'instrument.
* Validation du fonctionnement sans dépendance envers l'ancien format SONG.

### Nettoyage du projet

* Suppression du script temporaire `migration_mix_test.py` après intégration et validation de la migration dans `FusionProject`.
* Suppression des fonctions et chemins d'exécution devenus inutiles après la disparition des formats historiques MIX et SONG.
* Réduction du code de compatibilité tout en conservant les mécanismes de migration nécessaires à l'ouverture d'anciens projets.
* Les MIX vides demeurent valides et sont conservés ; leur suppression reste une opération volontaire de nettoyage.

### Validation globale

* Adaptation de `integration-globale.py` afin d'utiliser `PROGRAM.name` comme source canonique des noms de PROGRAM Fusion.
* Le test global couvre désormais l'ensemble du catalogue de PROGRAMs ROM importé dans le projet plutôt que seulement les anciens noms observés dans les structures capturées.
* 1164 noms de PROGRAM Fusion uniques validés.
* 952 noms reconnus par hint GM.
* 27 noms classés uniquement par famille.
* 185 noms demeurent sans suggestion connue.
* Aucun hint non respecté, meilleur hint incorrect, famille seule incorrecte, suggestion invalide ou suggestion en doublon détecté.
* Aucun preset avec champ manquant, score mal ordonné ou aberrant, limite dépassée ou instabilité Top 1 ou Top N détecté.
* 1221 aliases GM testés sans erreur dans `FUSION_GM_DATA`.
* Validation syntaxique finale de l'ensemble des modules modifiés avec `py_compile`.
* Validation finale du diff avec `git diff --check`.
