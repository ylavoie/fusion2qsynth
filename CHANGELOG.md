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
