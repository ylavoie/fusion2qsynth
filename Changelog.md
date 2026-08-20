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
