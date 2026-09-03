# Fusion2QSynth – Architecture

Version : 2.7

---

## Objectif

Fusion2QSynth permet d'utiliser un Alesis Fusion 8HD comme contrôleur de performances MIDI pour piloter FluidSynth à partir de SoundFonts.

Le projet reconnaît trois types de performances du Fusion :

* PROGRAM ;
* MIX ;
* SONG.

Il permet notamment :

* de capturer les informations MIDI émises par le Fusion ;
* d'identifier les performances sélectionnées ;
* d'associer les sons du Fusion à des instruments SoundFont ;
* de conserver ces associations dans un projet local ;
* de configurer FluidSynth en fonction de la performance active ;
* de transférer les événements MIDI du Fusion vers FluidSynth ;
* d'éditer et de valider la configuration propre à Fusion2QSynth.

Fusion2QSynth ne constitue pas un éditeur complet de l'Alesis Fusion.

---

## Principe fondamental

Trois systèmes distincts doivent toujours être séparés :

```text
Alesis Fusion 8HD
        |
        | MIDI
        v
Fusion2QSynth
        |
        | configuration MIDI / SoundFont
        v
FluidSynth
```

Le Fusion possède sa propre configuration interne.

`fusion.json` ne constitue pas une copie complète de cette configuration.

Il contient uniquement :

* les informations observables par MIDI ;
* les informations apprises ou saisies par l'utilisateur ;
* les associations nécessaires au fonctionnement de Fusion2QSynth ;
* les paramètres nécessaires au routage vers FluidSynth.

Une information absente du flux MIDI du Fusion ne doit pas être inventée par Fusion2QSynth.

---

## Architecture générale

```text
                         +-------------------+
                         | fusion2qsynth.py   |
                         | Orchestration      |
                         +---------+---------+
                                   |
        +--------------------------+--------------------------+
        |                          |                          |
        v                          v                          v
+----------------+        +----------------+        +----------------+
| fusion_capture |        | fusion_editor  |        | fusion_monitor |
+----------------+        +----------------+        +----------------+
        |                          |                          |
        +--------------------------+--------------------------+
                                   |
                                   v
                         +-------------------+
                         | FusionProject      |
                         | Modèle / données   |
                         +---------+---------+
                                   |
                                   v
                              fusion.json


Temps réel :

fusion_controller
        |
        +--> fusion_controller_state
        |
        +--> fusion_controller_loop
        |
        +--> fusion_performance
        |
        +--> FusionProject
        |
        +--> FluidSynth


Résolution musicale :

fusion_gm_map
        |
        +--> fusion_suggestions
        |
        +--> sf2_library
```

---

## Couches de l'application

### Orchestration

#### fusion2qsynth.py

Point d'entrée principal de l'application.

Responsabilités :

* initialisation du projet ;
* récupération éventuelle d'un projet endommagé ;
* affichage du menu principal ;
* lancement de la Capture ;
* lancement de l'Éditeur ;
* lancement du Contrôleur Live ;
* lancement du Monitor MIDI.

Il ne contient pas la logique métier détaillée des différents sous-systèmes.

---

### Modèle et persistance

#### fusion_project.py

`FusionProject` constitue le modèle central et la couche de persistance
du projet Fusion2QSynth.

Il est responsable notamment de :

* charger et recharger `fusion.json` ;
* valider les données du projet ;
* identifier les erreurs bloquantes ;
* sauvegarder de manière sécurisée ;
* gérer les backups et les archives ;
* restaurer un projet à partir d'une sauvegarde ou d'une archive ;
* gérer les PROGRAM ;
* gérer les MIX ;
* gérer les SONG ;
* gérer la bibliothèque d'instruments ;
* gérer les PARTS et les canaux associés ;
* résoudre les références d'instruments ;
* produire les diagnostics du projet ;
* préparer certaines opérations de capture ;
* fournir des fonctions communes de recherche, d'itération et d'affichage.

`FusionProject` encapsule la représentation persistante du projet.

Les autres modules peuvent contenir leur propre logique métier, mais
la persistance de `fusion.json` doit toujours passer par les mécanismes
prévus par `FusionProject`.

---

### Capture

#### fusion_capture.py

Responsable de l'observation et de l'apprentissage des performances du Fusion.

La Capture traite séparément :

* PROGRAM ;
* MIX ;
* SONG.

Elle observe les événements MIDI réellement transmis par le Fusion et construit ou complète la représentation correspondante dans `fusion.json`.

La Capture ne doit pas déduire des paramètres que le Fusion ne transmet pas.

##### PROGRAM

La sélection d'un PROGRAM transmet sur le canal MIDI par défaut du Fusion :

* la banque Fusion par `CC0` ;
* le numéro de programme par `Program Change`.

À partir de ces informations, Fusion2QSynth construit l'identifiant :

```text
bank:program
```

Une période d'apprentissage permet ensuite d'observer :

la note minimale ;
la note maximale ;
la vélocité minimale ;
la vélocité maximale.

Le PROGRAM est représenté par une PART unique utilisant le canal MIDI
par défaut du Fusion.

La sauvegarde est effectuée par FusionProject.save_safe().

##### MIX

La sélection d'un MIX transmet sur le canal MIDI principal du Fusion :

* la banque du MIX par `CC0` ;
* le numéro du MIX par `Program Change`.

Ces informations identifient le MIX sous la forme :

```text
bank:program
```

La sélection du MIX n'identifie pas les PROGRAM utilisés par ses PARTS.

Pendant la période de capture, Fusion2QSynth découvre les PARTS à partir
des messages `note_on` réellement observés.

Chaque nouveau canal MIDI observé crée une PART contenant initialement :

```json
{
  "midi_channel": 1
}
```

Le numéro de canal varie naturellement selon le canal observé.

La capture ne déduit donc pas les champs `bank` et `program` des PARTS
à partir du message ayant servi à sélectionner le MIX.

Les notes et vélocités sont observées pendant la capture, mais leurs
plages ne sont actuellement pas enregistrées dans les PARTS d'un MIX.

Pour les MIX ROM des banques 0 et 1, une recapture peut préserver les
métadonnées déjà connues d'une PART lorsque son canal MIDI correspond
à celui d'une ancienne PART.

Les champs pouvant être préservés sont :

* `bank` ;
* `program` ;
* `instrument` ;
* `fusion_name`.

Pour les MIX HD/User, ces anciennes métadonnées ne sont pas
automatiquement réutilisées.

Si le MIX contient déjà des PARTS, l'utilisateur doit confirmer leur
remplacement.

Les nouvelles PARTS sont validées par `FusionProject.replace_mix_parts()`
avant la sauvegarde définitive par `FusionProject.save_safe()`.

##### SONG

La capture d'une SONG est pilotée par les messages de transport MIDI.

Lorsqu'un message `song_select` est reçu, Fusion2QSynth demande à
l'utilisateur l'identifiant sous lequel la SONG doit être enregistrée.

La capture commence ensuite à la réception d'un message :

```text
START
```

et se termine à la réception de :

```text
STOP
```

Pendant la capture, les informations sont recueillies séparément pour
chaque canal MIDI.

Les données actuellement observées comprennent notamment :

* la banque Fusion transmise par `CC0` ;
* le numéro de programme transmis par `Program Change` ;
* le volume (`CC7`) ;
* le panoramique (`CC10`) ;
* l'expression (`CC11`) ;
* la réverbération (`CC91`) ;
* le chorus (`CC93`).

Les messages `CC32` sont également mémorisés pendant la capture, mais
leur valeur n'est actuellement pas combinée avec `CC0` pour construire
le champ `bank`.

Le champ :

```text
bank
```

correspond donc directement à la valeur `CC0` observée sur le canal.

Lors d'une recapture d'une SONG existante, les champs :

* `instrument` ;
* `fusion_name`

peuvent être conservés lorsqu'un canal possède toujours le même couple
`bank` / `program`.

Si aucun canal n'a été détecté entre `START` et `STOP`, la SONG n'est
pas sauvegardée.

La sauvegarde définitive est effectuée par
`FusionProject.save_safe()`.

---

### Contrôle temps réel

#### fusion_controller.py

`fusion_controller.py` constitue le point d'entrée du Contrôleur Live.

Il assure l'orchestration entre l'interface utilisateur du contrôleur,
l'état d'exécution, la boucle MIDI temps réel et le chargement des
performances.

Ses principales responsabilités sont :

* initialiser le projet ;
* valider la configuration disponible ;
* ouvrir les ports MIDI du Fusion et de FluidSynth ;
* permettre la sélection du mode PROGRAM, MIX ou SONG ;
* afficher le diagnostic correspondant au mode sélectionné ;
* retrouver la dernière performance utilisée dans ce mode ;
* charger cette performance lorsqu'une reprise est possible ;
* sélectionner la SONG à utiliser en mode SONG ;
* lancer `fusion_controller_loop` avec le contexte approprié ;
* gérer le retour de la boucle temps réel vers les menus du contrôleur.

La sélection du mode établit le contexte d'exécution du Contrôleur Live :

```text id="ib1jbr"
PROGRAM
MIX
SONG
```

En mode PROGRAM ou MIX, si une dernière performance utilisable est connue,
elle est chargée avant l'entrée dans la boucle temps réel.

Le contrôleur attend ensuite les changements de performance transmis par
le Fusion.

En mode SONG, la SONG est déterminée avant l'entrée dans la boucle temps
réel. La boucle attend ensuite le message MIDI `START` provenant du Fusion
pour charger sa configuration dans FluidSynth.

Une interruption clavier dans la boucle temps réel ne termine pas
nécessairement le Contrôleur Live.

Selon le mode actif, elle permet de revenir :

* au menu du Contrôleur Live en mode PROGRAM ou MIX ;
* à la sélection des SONG en mode SONG.

`fusion_controller.py` ne traite pas directement les événements MIDI
individuels et ne programme pas directement les instruments SoundFont.

Ces responsabilités appartiennent respectivement à :

```text id="0p68u7"
fusion_controller_loop.py
fusion_performance.py
```

---

#### fusion_controller_state.py

`fusion_controller_state.py` centralise l'état mutable nécessaire au
fonctionnement du Contrôleur Live.

Il permet aux modules du contrôleur de partager l'état de la performance
courante sans disperser ces informations dans plusieurs variables globales.

L'état courant comprend notamment :

```text
current_mode
current_performance
current_parts
active_notes
pending_reload
```

`current_mode` indique le type de performance actuellement chargé :

```text
program
mix
song
```

`current_performance` contient l'identifiant de la performance effectivement
chargée.

Pour un PROGRAM ou un MIX, cet identifiant prend normalement la forme :

```text
bank:program
```

Pour une SONG, il correspond à l'identifiant utilisé dans la section
`songs` du projet.

`current_parts` contient les canaux MIDI actifs de la performance courante.
Cette information est utilisée par la boucle temps réel pour déterminer
quels événements MIDI peuvent être retransmis à FluidSynth.

`active_notes` permet de suivre les notes actuellement enfoncées. Ce suivi
est notamment utilisé pour différer le rechargement d'une performance
lorsqu'une modification du projet survient pendant que des notes sont
encore actives.

`pending_reload` indique qu'un rechargement de la performance courante a
été demandé mais doit attendre le relâchement des notes actives.

Le module assure également la persistance de l'identifiant de la dernière
performance utilisable pour chacun des modes du Contrôleur Live.

Cette information permet de reprendre automatiquement la dernière
performance connue lors d'un retour en mode PROGRAM, MIX ou SONG.

L'état contenu dans ce module est uniquement un état d'exécution du
Contrôleur Live.

Il ne remplace pas `FusionProject` et ne constitue pas une seconde
représentation persistante de `fusion.json`.

---

#### fusion_controller_loop.py

`fusion_controller_loop.py` contient la boucle MIDI temps réel du contrôleur.

Il assure principalement :

* la surveillance des modifications de `fusion.json` ;
* le rechargement de la performance courante ;
* le suivi des notes actives ;
* le filtrage des canaux MIDI ;
* la retransmission des messages de jeu vers FluidSynth ;
* la détection des sélections PROGRAM et MIX ;
* le déclenchement d'une SONG sélectionnée.

##### Rechargement du projet

La boucle appelle régulièrement :

```text
reload_if_changed()
```

Lorsqu'une modification du projet est détectée, le rechargement de la
performance courante est demandé.

Si aucune note n'est active, le rechargement est immédiat.

Si des notes sont encore actives, il est différé jusqu'à leur
relâchement.

L'état :

```text
pending_reload
```

permet de mémoriser cette demande.

##### Notes actives

Les messages `note_on` et `note_off` maintiennent l'ensemble :

```text
active_notes
```

Une note est identifiée par son couple :

```text
(channel, note)
```

Un `note_on` avec une vélocité nulle est traité comme un relâchement de
note.

##### Filtrage des canaux

Les messages de notes ne sont retransmis que lorsque leur canal appartient
à :

```text
state.current_parts
```

Les messages suivants suivent également cette règle :

* `pitchwheel` ;
* `aftertouch` ;
* `polytouch`.

Cela empêche les canaux qui ne font pas partie de la performance active
de piloter FluidSynth.

##### Contrôleurs MIDI

En modes PROGRAM et MIX, un `CC0` reçu sur le canal MIDI principal du
Fusion mémorise la banque utilisée pour identifier la prochaine
performance.

Les messages :

```text
CC0
CC32
```

provenant ensuite des PARTS ne sont pas retransmis vers FluidSynth.

Cette règle évite que les Bank Select générés par le Fusion écrasent les
banques SoundFont programmées par `fusion_performance.py`.

Les autres Control Change provenant de canaux actifs sont retransmis.

##### Détection des performances Fusion

En mode PROGRAM ou MIX, la boucle observe sur le canal MIDI principal du
Fusion :

* `CC0` pour mémoriser la banque sélectionnée ;
* `Program Change` pour obtenir le numéro de performance.

La banque courante est initialisée à :

```python
bank = None
```

Cet état représente l'absence de banque Fusion observée.

Un `CC0` reçu sur le canal MIDI principal du Fusion initialise ou remplace
cette valeur. Le message est utilisé uniquement pour la détection de la
performance et n'est pas transmis à FluidSynth.

Lorsqu'un `Program Change` est ensuite reçu sur ce même canal, l'identifiant
de la performance est construit sous la forme :

```text
bank:program
```

Un `Program Change` reçu alors qu'aucune banque n'a encore été observée
n'est donc pas interprété comme appartenant implicitement à la banque `0`.

Cette distinction est importante puisque `0` constitue une valeur de banque
Fusion valide.

La banque est interprétée selon le mode actif :

* table des banques PROGRAM en mode PROGRAM ;
* table des banques MIX en mode MIX.

Les messages `CC0` et `CC32` provenant des PARTs ne sont pas transmis
à FluidSynth.

Cela évite que les Bank Select émis par le Fusion remplacent le mapping
SoundFont déjà chargé par Fusion2QSynth.

Les autres contrôleurs MIDI provenant d'un canal actif peuvent être
retransmis normalement.

##### Mode SONG

Le mode SONG fonctionne différemment.

Les messages `Program Change` ne servent pas à sélectionner une SONG.

La SONG à utiliser est choisie avant l'entrée dans la boucle du
contrôleur.

Lorsqu'un message MIDI :

```text
START
```

est reçu, la SONG sélectionnée est chargée par :

```text
load_song()
```

Les messages `song_select` reçus pendant cette boucle ne provoquent pas
eux-mêmes un changement de SONG.

#### fusion_performance.py

`fusion_performance.py` assure le chargement des performances configurées
dans FluidSynth.

Il ne détecte pas les sélections effectuées sur le Fusion et ne modifie
pas la structure des performances dans `fusion.json`.

Ses principales responsabilités sont :

* charger un PROGRAM ;
* charger un MIX ;
* charger une SONG ;
* résoudre les instruments SoundFont associés ;
* programmer les banques et presets SoundFont dans FluidSynth ;
* appliquer les paramètres statiques d'une SONG ;
* maintenir l'état de la performance courante ;
* sauvegarder l'identifiant de la dernière performance chargée ;
* recharger la performance courante lorsque nécessaire.

##### Sélection d'un instrument SoundFont

Pour chaque instrument, les champs :

```text id="ptb0rz"
sf2_bank
sf2_program
```

sont utilisés pour programmer FluidSynth.

La banque SoundFont est transmise selon le découpage MMA :

```text id="a0ua33"
CC0  = sf2_bank // 128
CC32 = sf2_bank % 128
```

puis le preset est sélectionné par `Program Change`.

Cette banque SoundFont est indépendante de la banque Fusion enregistrée
dans les données capturées.

##### PROGRAM

Le PROGRAM utilise sa première PART configurée pour FluidSynth.

Avant le chargement :

* le PROGRAM doit exister ;
* il doit contenir au moins une PART ;
* cette PART doit être prête pour FluidSynth ;
* son instrument SoundFont doit pouvoir être résolu.

Le canal et l'instrument correspondants sont ensuite programmés dans
FluidSynth.

##### MIX

Avant son chargement, le MIX est validé.

Les erreurs de validation peuvent être affichées sans nécessairement
empêcher le chargement.

Seules les PARTS considérées comme prêtes pour FluidSynth sont chargées.
Les PARTS incomplètes sont ignorées.

Chaque PART valide programme son instrument SoundFont sur son propre
canal MIDI.

##### SONG

Chaque canal configuré d'une SONG peut charger son instrument SoundFont.

Les paramètres statiques suivants sont également restaurés lorsqu'ils
sont présents :

* volume (`CC7`) ;
* panoramique (`CC10`) ;
* expression (`CC11`) ;
* réverbération (`CC91`) ;
* chorus (`CC93`).

Les canaux sans instrument résolvable sont ignorés.

##### Changement de performance

Le chargement d'un PROGRAM, d'un MIX ou d'une SONG est centralisé dans
`fusion_performance.py`.

Avant de programmer une nouvelle performance dans FluidSynth, un `panic`
MIDI est envoyé afin d'arrêter les notes encore actives.

L'état courant mémorise notamment :

```text
current_mode
current_performance
current_parts
active_notes
pending_reload
```

Lorsqu'un chargement réussit, `current_performance` identifie la performance
effectivement active et `current_parts` contient les canaux MIDI autorisés
pour cette performance.

L'identifiant de la dernière performance utilisable est également enregistré
par `save_last_performance()`. Cette information permet au Contrôleur Live
de reprendre la dernière performance connue lors de l'entrée dans un mode.

En mode PROGRAM ou MIX, une nouvelle performance est chargée lorsque la
boucle du contrôleur détecte un nouvel identifiant `bank:program`.

Si l'identifiant détecté correspond déjà à `current_performance`, aucun
nouveau chargement n'est effectué.

En mode SONG, la SONG est sélectionnée préalablement par le contrôleur.
Son chargement est déclenché par la réception du message MIDI `START`.

Une modification externe de `fusion.json` peut également demander le
rechargement de la performance courante.

`reload_current_performance()` utilise alors `current_mode` et
`current_performance` pour recharger le PROGRAM, le MIX ou la SONG
correspondante.

Si des notes sont encore actives, ce rechargement peut être différé jusqu'à
leur relâchement afin de ne pas interrompre inutilement le jeu en cours.

---

### Édition

#### fusion_editor.py

`fusion_editor.py` fournit l'interface interactive permettant de consulter,
compléter, corriger et tester la configuration utilisée par Fusion2QSynth.

L'Éditeur modifie la représentation du projet gérée par `FusionProject`.

Il n'édite pas directement la mémoire interne du Fusion 8HD.

L'interface est organisée autour de quatre domaines :

```text
Gestion MIX
Gestion PROGRAM
Gestion SONG
Gestion Instruments
```

Au démarrage, le projet est validé et les erreurs pouvant faire l'objet
d'une réparation assistée peuvent être présentées à l'utilisateur.

Les listes de PROGRAM, MIX et SONG utilisent les diagnostics fournis par
`FusionProject` afin de distinguer notamment :

```text
OK
À configurer
Erreur Fusion
```

Cette classification permet de travailler directement sur les performances
incomplètes ou invalides sans devoir parcourir systématiquement l'ensemble
du projet.

##### PROGRAM

L'Éditeur permet notamment :

* de consulter les PROGRAM ;
* de filtrer les PROGRAM à configurer ou en erreur ;
* de modifier l'instrument SoundFont associé ;
* de modifier les paramètres de la PART ;
* de modifier le nom Fusion ;
* de renommer un PROGRAM ;
* de supprimer un PROGRAM.

Un PROGRAM utilise normalement une PART unique.

Les paramètres éditables de cette PART peuvent comprendre :

```text
midi_channel
bank
program
note_min
note_max
velocity_min
velocity_max
instrument
```

Les valeurs saisies sont vérifiées avant leur persistance.

##### MIX

L'Éditeur permet notamment :

* de consulter les MIX ;
* de filtrer les MIX à configurer ou en erreur ;
* de renommer un MIX ;
* de dupliquer un MIX ;
* de supprimer un MIX ;
* de supprimer les MIX vides ;
* de modifier individuellement les PARTS ;
* de modifier l'instrument associé à une PART ;
* de modifier les paramètres d'une PART ;
* de modifier son nom Fusion ;
* de tester séparément les PARTS ;
* de tester simultanément l'ensemble des PARTS configurées.

Lors de la sélection d'un instrument, l'utilisateur peut écouter le nouvel
instrument ou effectuer une comparaison A/B avant de conserver
l'association.

##### SONG

L'Éditeur permet notamment :

* de consulter les SONG ;
* de filtrer les SONG à configurer ou en erreur ;
* de modifier une SONG ;
* de renommer une SONG ;
* de supprimer une SONG ;
* de modifier les paramètres de ses canaux ;
* d'associer un instrument SoundFont à chaque canal.

Les paramètres éditables d'un canal peuvent notamment comprendre :

```text
bank
program
volume
pan
expression
reverb
chorus
instrument
fusion_name
```

##### Instruments

La bibliothèque d'instruments du projet peut être :

* consultée ;
* enrichie ;
* modifiée ;
* nettoyée par suppression des instruments inutilisés.

Un instrument peut être ajouté :

* à partir de la bibliothèque de presets SoundFont ;
* par saisie manuelle.

Avant de supprimer un instrument, l'Éditeur vérifie ses utilisations dans
le projet afin d'éviter de supprimer une référence encore nécessaire.

##### Suggestions et tests SoundFont

Lorsqu'un nom Fusion et un numéro de programme sont disponibles,
`fusion_suggestions` peut proposer des presets SoundFont susceptibles de
correspondre au son recherché.

Ces suggestions constituent une aide à la configuration et non une
identification certaine du son interne du Fusion.

L'Éditeur peut programmer temporairement FluidSynth afin d'écouter un
preset proposé.

Les banques SoundFont utilisées pour ces tests sont converties en Bank
Select MIDI selon le découpage :

```text
CC0  = sf2_bank // 128
CC32 = sf2_bank % 128
```

puis le preset est sélectionné par `Program Change`.

##### Validation et réparation progressive

L'Éditeur s'appuie sur les mécanismes de validation de `FusionProject`.

Lorsqu'une modification est effectuée sur un projet contenant déjà des
erreurs bloquantes, l'Éditeur peut conserver la liste des erreurs
préexistantes et l'utiliser comme `allowed_errors`.

Une modification ne doit pas introduire de nouvelle erreur bloquante.

Lorsque la sauvegarde échoue après une modification effectuée directement
en mémoire, l'Éditeur restaure autant que possible l'état précédent.

Certaines erreurs, notamment les références à des instruments absents,
peuvent faire l'objet d'une réparation assistée.

La persistance définitive reste toujours effectuée par
`FusionProject.save_safe()`.

---

### Diagnostic

#### fusion_monitor.py

`fusion_monitor.py` permet d'observer directement les événements MIDI
transmis par le Fusion 8HD.

Il utilise `find_fusion_input()` pour localiser automatiquement le port
MIDI d'entrée du Fusion, puis ouvre ce port avec `mido`.

Le monitor n'interprète pas les événements en fonction d'un PROGRAM, d'un
MIX ou d'une SONG.

Son rôle est volontairement plus bas niveau : afficher exactement ce qui
est reçu du Fusion afin de faciliter l'analyse et le dépannage du
comportement MIDI.

Les principaux événements affichés sont :

```text
NOTE ON
NOTE OFF
CONTROL
PROGRAM
PITCHWHEEL
AFTERTOUCH
POLYTOUCH
SYSEX
QUARTER FRAME
SONG POSITION
SONG SELECT
TUNE REQUEST
CLOCK
START
CONTINUE
STOP
ACTIVE SENSING
RESET
```

Les événements non reconnus sont affichés sous la forme `UNKNOWN` avec leur
représentation Mido complète.

##### Notes

Pour les messages `note_on` et `note_off`, le monitor affiche :

* le canal MIDI ;
* le nom de la note ;
* la vélocité.

Le numéro de canal interne Mido est converti vers la représentation
utilisateur `1-16`.

Le nom de la note est obtenu par `note_name()`.

##### Control Change

Les messages `control_change` affichent :

```text
canal
numéro CC
nom du contrôleur
valeur
```

Une table locale `CC_NAMES` fournit un nom lisible pour plusieurs
contrôleurs MIDI courants, notamment :

```text
CC0   Bank Select
CC1   Modulation
CC7   Volume
CC10  Pan
CC11  Expression
CC64  Sustain
CC91  Reverb
CC93  Chorus
CC120 All Sound Off
CC121 Reset Controllers
CC123 All Notes Off
```

Les contrôleurs absents de cette table sont affichés comme `Undefined`.

Cette fonction est particulièrement utile pour observer les Bank Select,
les contrôleurs de performance et les messages envoyés lors des changements
de PROGRAM, MIX ou SONG.

##### Messages système temps réel

Le monitor affiche également les messages MIDI système utilisés notamment
par les séquences du Fusion :

```text
CLOCK
START
CONTINUE
STOP
```

Cela permet entre autres de vérifier le comportement du Fusion en mode
SONG et la présence du message `START` utilisé par le Contrôleur Live.

Le monitoring fonctionne jusqu'à une interruption clavier.

`Ctrl-C` ferme proprement le monitor et retourne au menu appelant.

#### fusion_diagnostic.py

`fusion_diagnostic.py` centralise la présentation des messages de validation
et d'erreur produits par les autres modules.

Il ne constitue pas lui-même le moteur de validation du projet.

La validation des données demeure la responsabilité de `FusionProject`.

Le module fournit principalement :

```text
print_validation_errors()
print_error_messages()
```

##### print_validation_errors()

`print_validation_errors()` reçoit :

* le projet courant ;
* une liste d'erreurs ;
* éventuellement un titre d'affichage.

Les erreurs textuelles sont regroupées selon la partie du projet à laquelle
elles appartiennent :

```text
MIX
PROGRAM
SONG
AUTRES
```

Pour déterminer leur catégorie, la fonction construit les ensembles des
identifiants de MIX, PROGRAM et SONG existants dans le projet et compare le
début du message d'erreur à ces identifiants.

Cette organisation permet de présenter les résultats de validation de
manière plus lisible sans déplacer la logique de validation hors de
`FusionProject`.

##### Erreurs structurées

Certaines validations utilisent des dictionnaires plutôt que de simples
chaînes de caractères.

`fusion_diagnostic.py` fournit un affichage spécialisé pour ces erreurs.

Le type :

```text
missing_instrument
```

indique qu'une PART de MIX référence un instrument absent de la bibliothèque
du projet.

Le diagnostic affiche alors notamment :

```text
Mix
PART
Canal MIDI
Instrument
```

Cette information peut ensuite être utilisée par l'Éditeur pour proposer
une réparation assistée.

Le type :

```text
midi_channel_conflict
```

signale que plusieurs PARTS d'un même MIX utilisent le même canal MIDI.

Le diagnostic affiche :

```text
Mix
Canal MIDI
PARTS concernées
```

Ce cas est présenté comme une information plutôt que comme une erreur
nécessairement fatale, puisque le partage d'un canal peut être volontaire.

Les autres erreurs structurées utilisent leur champ `message` lorsqu'il est
disponible.

##### print_error_messages()

`print_error_messages()` fournit un affichage simplifié d'une liste
d'erreurs.

Une erreur textuelle est affichée directement.

Pour une erreur structurée, le champ `message` est utilisé lorsqu'il
existe.

Cette fonction est notamment utilisée lorsqu'un module doit présenter le
résultat d'une opération refusée sans produire le rapport complet de
validation.

##### Séparation des responsabilités

La séparation entre validation et présentation suit le principe :

```text
FusionProject
    |
    | produit les erreurs
    v
fusion_diagnostic
    |
    | organise et présente
    v
Interface utilisateur
```

Ainsi :

* `FusionProject` détermine si les données sont valides ;
* `fusion_diagnostic.py` présente les problèmes ;
* `fusion_editor.py`, le contrôleur ou les autres interfaces décident de
  l'action à proposer à l'utilisateur.

Cette séparation évite de dupliquer les règles de validation dans les
différentes interfaces de Fusion2QSynth.

---

### Mapping musical et SoundFont

#### fusion_gm_map.py

`fusion_gm_map.py` constitue la base de connaissances statique utilisée pour
interpréter les banques et les noms de sons du Fusion 8HD.

Le module ne réalise pas lui-même la recherche de presets SoundFont.

Il fournit les tables de référence utilisées notamment par :

```text
fusion_suggestions.py
interfaces d'affichage des PROGRAM
interfaces d'affichage des MIX
gestion des banques SONG
```

Ses données couvrent plusieurs domaines distincts :

```text
noms des banques Fusion
référentiel General MIDI
indices de correspondance Fusion → GM
kits de batterie
familles instrumentales
exceptions de classification
```

##### Noms des banques Fusion

Les tables :

```text
FUSION_PROGRAM_BANK_NAMES
FUSION_MIX_BANK_NAMES
```

associent les numéros de banques transmis par le Fusion à leurs noms
lisibles.

Par exemple, les banques PROGRAM permettent de distinguer notamment :

```text
ROM:PRESET 1
ROM:PRESET 2
ROM:ELECTRONICA
ROM:SYNTH DRUM
ROM:GM
HD:USER
ROM:Hollow Sun ...
```

La fonction :

```text
fusion_program_bank_name()
```

retourne le nom connu d'une banque PROGRAM.

Lorsqu'aucun nom n'est défini, une représentation générique de la forme :

```text
BANK n
```

est utilisée.

`fusion_mix_bank_name()` applique le même principe aux banques MIX.

##### Banques SONG

`fusion_song_bank_name()` fournit une représentation lisible de la banque
associée à une SONG.

La valeur de banque est interprétée comme une combinaison MSB/LSB :

```text
bank_msb = bank // 128
bank_lsb = bank % 128
```

Le MSB est résolu à l'aide de la table des banques PROGRAM du Fusion.

Lorsque le LSB est différent de zéro, il est ajouté à la représentation
affichée.

Cette fonction concerne la représentation de la banque Fusion et non la
sélection d'un preset SoundFont.

##### Référentiel General MIDI

`GM_PROGRAMS` constitue le référentiel des programmes General MIDI.

Chaque nom GM est associé notamment à :

```text
family
gm_program
```

Les numéros de programme suivent la représentation MIDI interne utilisée
par le projet, soit :

```text
0 à 127
```

Le référentiel couvre les familles General MIDI telles que :

```text
pianos
percussions chromatiques
orgues
guitares
basses
cordes
cuivres
bois
leads
pads
effets
instruments ethniques
effets sonores
```

##### Correspondances Fusion → General MIDI

`FUSION_GM_DATA` contient les connaissances spécifiques permettant
d'associer des noms de PROGRAM du Fusion à une famille instrumentale et à
un programme General MIDI plausible.

Chaque entrée possède conceptuellement la forme :

```text
(
    noms Fusion,
    famille,
    programme GM
)
```

Plusieurs noms Fusion peuvent donc partager la même correspondance.

Cette table contient aussi bien des noms relativement génériques que des
noms propres aux banques internes du Fusion, notamment les banques ROM et
les collections Hollow Sun.

Elle constitue une base de connaissances empirique sur les sons du Fusion
et non une table officielle garantissant une équivalence sonore exacte.

##### Construction des indices Fusion

À partir de `FUSION_GM_DATA`, le module construit :

```text
FUSION_GM_HINTS
```

Chaque nom connu devient directement accessible sous la forme :

```text
nom Fusion
    |
    +----> family
    |
    +----> gm_program
```

Cette transformation évite au moteur de suggestions de parcourir
directement la grande table source pour chaque recherche.

`fusion_suggestions.py` peut ainsi utiliser `FUSION_GM_HINTS` comme index
de correspondance.

##### Programmes de kits de batterie

Les kits de batterie disposent d'un traitement particulier dans le moteur
de suggestions.

`GM_DRUM_KIT_PROGRAMS` contient les numéros de programmes General MIDI
considérés comme des kits de batterie :

```text
0
8
16
24
25
32
48
56
```

Cette information permet à `fusion_suggestions.py` de vérifier qu'une
correspondance General MIDI détectée pour un son de batterie représente
effectivement un programme de kit reconnu.

La détection du kit lui-même repose sur les informations contenues dans
`FUSION_GM_HINTS`.

Il n'existe donc pas de seconde table indépendante de correspondance entre
les noms Fusion et les kits SoundFont.

##### Familles instrumentales

`FAMILIES` définit les termes permettant de reconnaître les principales
familles instrumentales dans les noms de presets.

Par exemple :

```text
piano
electric_piano
harpsichord
organ
guitar
bass
contrabass
strings
harp
trumpet
trombone
french_horn
clarinet
oboe
bassoon
flute
recorder
sax
pan_flute
marimba
vibraphone
xylophone
bells
choir
pad
lead
drums
square_wave
```

Chaque famille possède une liste d'alias susceptibles d'apparaître dans un
nom de son.

Ces alias sont exploités par `fusion_suggestions.detect_families()`.

##### Exceptions de classification

La détection par mots-clés ne suffit pas pour tous les sons.

`FUSION_FAMILY_OVERRIDES` permet donc d'imposer explicitement une ou
plusieurs familles à certains noms Fusion.

Par exemple, un nom ambigu peut être forcé vers :

```text
drums
guitar
strings
electric_piano
```

ou vers plusieurs familles lorsque plusieurs interprétations sont
pertinentes.

Ces overrides ont priorité sur la détection générale effectuée à partir de
`FAMILIES`.

Ils servent notamment à corriger :

* les noms propriétaires dont la fonction musicale n'est pas évidente ;
* les faux positifs produits par certains mots ;
* les sons de batterie dont le nom ne contient pas nécessairement `drum`
  ou `kit` ;
* les sons dont la classification doit être plus spécialisée.

##### Nature de la base de connaissances

Les données contenues dans `fusion_gm_map.py` ne constituent pas une
conversion automatique et certaine entre le moteur sonore du Fusion et un
SoundFont.

Elles représentent plutôt :

```text
connaissances General MIDI
        +
classification des noms Fusion
        +
correspondances empiriques
        +
exceptions connues
```

Le résultat est utilisé comme information heuristique par
`fusion_suggestions.py`.

Le choix final du preset SoundFont reste sous le contrôle de l'utilisateur
dans l'Éditeur.

##### Séparation des responsabilités

La chaîne de connaissances et de sélection peut être représentée ainsi :

```text
                    fusion_gm_map.py
                    /       |       \
                   /        |        \
             données GM   familles   exceptions
                   \        |        /
                    \       |       /
                     v      v      v
                  fusion_suggestions.py
                          |
                          | candidats classés
                          v
                    fusion_editor.py
                          |
                          | choix utilisateur
                          v
                     FusionProject
```

`fusion_gm_map.py` contient donc les connaissances.

`fusion_suggestions.py` contient les algorithmes qui exploitent ces
connaissances.

`fusion_editor.py` présente les résultats et permet leur évaluation.

`FusionProject` conserve le choix retenu.

#### fusion_suggestions.py

`fusion_suggestions.py` fournit le moteur de suggestions utilisé pour
associer un PROGRAM du Fusion à un ou plusieurs presets SoundFont
plausibles.

Le module ne modifie pas directement le projet.

Il analyse le nom du son Fusion et compare ses caractéristiques avec les
presets disponibles dans la bibliothèque SoundFont.

Son fonctionnement repose principalement sur :

```text
normalisation des noms
détection General MIDI
détection de familles instrumentales
règles sémantiques
comparaison de similarité
classement des candidats
```

Les tables de référence sont fournies par `fusion_gm_map.py`, notamment :

```text
FUSION_GM_HINTS
GM_PROGRAMS
GM_DRUM_KIT_PROGRAMS
FAMILIES
FUSION_FAMILY_OVERRIDES
```

##### Normalisation des noms

`normalize_name()` convertit les noms en une représentation uniforme :

```text
minuscules
caractères non alphanumériques remplacés par des espaces
espaces multiples supprimés
```

Cette normalisation facilite les comparaisons entre les noms provenant du
Fusion et ceux des presets SoundFont.

`normalize_preset_name()` applique en plus une normalisation particulière
aux noms de presets.

Le terme :

```text
expr
```

est retiré avant le calcul de similarité.

Cela permet notamment de ne pas pénaliser excessivement un preset dont le
nom indique simplement une variante expressive.

##### Détection General MIDI

`detect_gm_program()` tente d'abord de reconnaître directement le nom du
PROGRAM Fusion dans la table `GM_PROGRAMS`.

Lorsqu'une correspondance exacte normalisée existe, les informations GM
associées sont retournées.

Si aucune correspondance directe n'est trouvée, `detect_gm_hint()` analyse
les termes présents dans le nom.

Les indices définis dans `FUSION_GM_HINTS` peuvent notamment fournir :

```text
family
gm_program
```

Lorsque plusieurs termes correspondent, le terme le plus long est
privilégié.

Cette règle permet de favoriser une expression spécialisée plutôt qu'un
mot plus général contenu dans la même expression.

##### Détection des kits de batterie

`detect_gm_drum_kit()` applique un traitement particulier aux kits de
batterie General MIDI.

Lorsqu'un indice GM :

* appartient à la famille `drums` ;
* correspond à un programme reconnu dans `GM_DRUM_KIT_PROGRAMS` ;

le preset recherché est considéré comme appartenant à la banque :

```text
128
```

avec le programme GM correspondant.

Lorsqu'un tel preset existe dans la bibliothèque SoundFont, il est retourné
avec un score maximal.

##### Familles instrumentales

`detect_families()` détermine une ou plusieurs familles susceptibles de
correspondre au nom du son Fusion.

Les familles et leurs alias proviennent de :

```text
FAMILIES
```

Une même désignation peut appartenir à plusieurs familles.

Des substitutions explicites peuvent être fournies par :

```text
FUSION_FAMILY_OVERRIDES
```

Lorsqu'un override existe, il remplace la détection générale.

##### Corrections sémantiques

Certaines expressions nécessitent un traitement particulier afin d'éviter
les faux positifs produits par une simple recherche de mots.

Par exemple :

```text
bass drum
```

doit être considéré comme appartenant à la famille `drums` et non à la
famille `bass`.

Inversement :

```text
drum n bass
drum and bass
```

sont classés dans la famille `bass` plutôt que comme instruments de
batterie.

Le moteur applique également plusieurs spécialisations.

Par exemple :

```text
contrabass
```

ne conserve pas automatiquement la famille générique `bass`.

De même :

```text
electric_piano
```

remplace la classification générique `piano`.

Et :

```text
pan_flute
```

remplace la classification générique `flute`.

Les sons de type `square_wave` font également l'objet d'une spécialisation.

Lorsqu'ils ne sont pas déjà identifiés comme des basses, ils sont classés
dans :

```text
square_lead
```

`list_presets()` constitue l'interface de consultation de la bibliothèque
SoundFont utilisée notamment par l'Éditeur.

Les coordonnées d'un preset dans cette bibliothèque sont désignées par :

```text
sf2_bank
sf2_program
```

afin de les distinguer explicitement des champs :

```text
bank
program
```

utilisés pour représenter les coordonnées de banque et de programme du
Fusion.

Lorsqu'il appelle le moteur de suggestions, `fusion_editor.py` adapte
temporairement la représentation des presets SoundFont au format attendu
par `fusion_suggestions.py`.

Cette conversion ne modifie pas les données conservées dans
`sf2_library.json`.

##### Représentation utilisée par le moteur

Le moteur reçoit deux espaces de données distincts.

Le PROGRAM Fusion est représenté notamment par :

```text
name
program
```

Les presets SoundFont fournis au moteur sont représentés temporairement
par :

```text
id
name
bank
program
```

Dans ce contexte interne à `fusion_suggestions.py`, les champs `bank` et
`program` des candidats représentent les coordonnées SoundFont adaptées
par l'Éditeur.

Dans la bibliothèque persistante `sf2_library.json`, ces mêmes valeurs
demeurent explicitement nommées :

```text
sf2_bank
sf2_program
```

Cette adaptation est effectuée par `fusion_editor.py` avant l'appel à
`suggest_instruments()` et permet au moteur de comparaison de travailler
avec une structure simplifiée sans confondre les deux représentations
persistantes.

##### Recherche des candidats

`matches_for_family()` compare un PROGRAM Fusion avec les presets SoundFont
d'une famille donnée.

Un preset devient candidat lorsqu'au moins une des conditions suivantes
est remplie :

* il appartient à la famille recherchée ;
* il correspond exactement à un indice General MIDI applicable.

Chaque candidat reçoit ensuite un score.

Le score de base est calculé avec :

```text
difflib.SequenceMatcher
```

sur les noms normalisés.

Des ajustements sont ensuite appliqués.

Une correspondance exacte avec l'indice General MIDI ajoute :

```text
+0.40
```

au score.

Une correspondance entre le numéro de programme Fusion et le numéro de
programme du preset ajoute :

```text
+0.10
```

Un preset dont le nom contient :

```text
expr
```

reçoit une légère pénalité :

```text
-0.05
```

Les candidats sont ensuite triés en privilégiant :

```text
correspondance GM
score de similarité
```

##### Production des suggestions

`suggest_instruments()` constitue l'interface principale du moteur.

Le traitement suit globalement le flux :

```text
PROGRAM Fusion
    |
    v
nom Fusion
    |
    +----> détection kit GM
    |
    +----> détection familles
    |
    +----> override éventuel
    |
    +----> indice GM éventuel
    |
    v
recherche des presets par famille
    |
    v
calcul des scores
    |
    v
classement
    |
    v
suggestions
```

Les suggestions sont retournées sous forme d'un dictionnaire organisé par
famille.

Pour chaque famille, plusieurs candidats peuvent être retournés, selon la
limite demandée.

La valeur par défaut est :

```text
limit = 3
```

Chaque suggestion contient :

```text
score
preset
```

##### Nature des suggestions

Les résultats produits par `fusion_suggestions.py` sont heuristiques.

Ils ne constituent pas une identification certaine du son interne du
Fusion.

Le moteur cherche plutôt à réduire le nombre de presets SoundFont à
examiner en combinant :

* les conventions General MIDI ;
* le vocabulaire contenu dans le nom du son ;
* les familles instrumentales ;
* des règles de désambiguïsation ;
* la similarité textuelle.

La décision finale reste donc effectuée dans l'Éditeur, où l'utilisateur
peut écouter et comparer les presets proposés.

##### Séparation des responsabilités

La chaîne fonctionnelle est :

```text
fusion_gm_map.py
    |
    | tables et règles de référence
    v
fusion_suggestions.py
    |
    | analyse et classement
    v
fusion_editor.py
    |
    | écoute et choix utilisateur
    v
FusionProject
```

Ainsi :

* `fusion_gm_map.py` contient les connaissances de classification ;
* `fusion_suggestions.py` applique les heuristiques de correspondance ;
* `fusion_editor.py` présente les propositions ;
* `FusionProject` conserve uniquement le choix finalement retenu.

---

#### sf2_library.py

`sf2_library.py` construit et exploite une bibliothèque locale des presets
contenus dans un fichier SoundFont `.sf2`.

Le module s'appuie sur l'utilitaire externe :

```text
sf2dump
```

pour analyser le contenu du fichier SoundFont.

##### Extraction des presets

`dump_sf2()` exécute :

```text
sf2dump fichier.sf2
```

et récupère sa sortie standard.

Si `sf2dump` retourne une erreur, l'exécution est interrompue avec le
message retourné par l'outil.

La sortie de `sf2dump` est ensuite analysée par `parse_presets()`.

Chaque preset reconnu est converti en une structure de la forme :

```text
id
name
sf2_bank
sf2_program
```

L'identifiant est dérivé du nom du preset :

```text
nom en minuscules
→ caractères non alphanumériques remplacés par "_"
→ "_" de début et de fin supprimés
```

Par exemple, un nom tel que :

```text
Acoustic Grand Piano
```

peut produire :

```text
acoustic_grand_piano
```

##### Structure de la bibliothèque

`build_library()` produit une structure contenant :

```text
soundfont
presets
```

Le champ `soundfont` contient le chemin du fichier SoundFont analysé.

Le champ `presets` contient la liste des presets extraits.

Chaque preset possède au minimum :

```text
id
name
sf2_bank
sf2_program
```

##### Persistance

La bibliothèque est sauvegardée par défaut dans :

```text
sf2_library.json
```

à l'aide de `save_library()`.

Le fichier JSON est écrit en UTF-8 avec indentation et conservation des
caractères Unicode.

`load_library()` recharge cette bibliothèque lorsqu'elle existe.

Si le fichier est absent, le module signale :

```text
Bibliothèque SF2 absente
```

##### Consultation des presets

`list_presets()` constitue l'interface de consultation de la bibliothèque
SoundFont utilisée notamment par l'Éditeur.

Les coordonnées d'un preset dans cette bibliothèque sont désignées par :

```text
sf2_bank
sf2_program
```

afin de les distinguer explicitement des champs :

```text
bank
program
```

utilisés pour représenter les coordonnées de banque et de programme du
Fusion.

Lorsqu'il appelle le moteur de suggestions, `fusion_editor.py` adapte
temporairement la représentation des presets SoundFont au format attendu
par `fusion_suggestions.py`.

Cette conversion ne modifie pas les données conservées dans
`sf2_library.json`.

##### Utilisation autonome

`sf2_library.py` peut également être exécuté directement :

```text
python3 sf2_library.py fichier.sf2
```

Dans ce mode, le module :

```text
fichier .sf2
    |
    v
sf2dump
    |
    v
parse_presets()
    |
    v
build_library()
    |
    +----> affichage des presets
    |
    v
sf2_library.json
```

Le fichier `sf2_library.json` devient ainsi une représentation simplifiée
et rapidement exploitable du contenu du SoundFont.

##### Séparation des responsabilités

`sf2_library.py` ne choisit pas lui-même quel preset doit correspondre à un
son du Fusion.

Son rôle est uniquement de :

* analyser le SoundFont ;
* extraire les presets disponibles ;
* conserver leur banque et leur programme ;
* rendre cette information accessible aux autres modules.

La mise en correspondance entre un son Fusion et les presets disponibles
est laissée à `fusion_suggestions.py` et aux interfaces d'édition.

---

### Infrastructure commune

#### fusion_lib.py

`fusion_lib.py` regroupe les fonctions utilitaires partagées par plusieurs
modules de Fusion2QSynth.

Il ne contient pas de logique métier propre aux PROGRAM, MIX ou SONG.

Ses responsabilités principales sont :

```text
journalisation
détection des ports MIDI
commandes MIDI générales
conversion des notes
état général du système
```

##### Journalisation

Le module fournit deux mécanismes de journalisation.

Les fonctions :

```text
log_info()
log_warning()
```

s'appuient sur une fonction interne :

```text
_log()
```

qui écrit directement dans le fichier défini par :

```text
LOG_FILE
```

Chaque ligne contient :

```text
date et heure
niveau
message
```

sous une forme comparable à :

```text
YYYY-MM-DD HH:MM:SS [INFO] message
```

Le module configure également le système standard `logging` de Python.

Les fonctions :

```text
log_event()
log_error()
```

utilisent respectivement :

```text
logging.info()
logging.error()
```

La destination est également `LOG_FILE`.

Ces deux mécanismes coexistent actuellement dans le module.

##### Détection des ports MIDI

`find_fusion_input()` recherche le port MIDI d'entrée correspondant au
Fusion.

La recherche parcourt :

```text
mido.get_input_names()
```

et compare chaque nom avec :

```text
FUSION_INPUT_NAME
```

sans tenir compte de la casse.

La première correspondance trouvée est retournée.

Si aucun port ne correspond, la fonction retourne :

```text
None
```

`find_fluidsynth_output()` applique le même principe aux sorties MIDI
disponibles à partir de :

```text
mido.get_output_names()
```

et de la chaîne :

```text
FLUIDSYNTH_OUTPUT_NAME
```

Ces deux fonctions constituent le mécanisme commun de découverte des ports
utilisé par les autres modules.

##### Panic MIDI

`panic()` permet d'arrêter rapidement l'état MIDI courant de FluidSynth.

La fonction parcourt les 16 canaux MIDI et transmet successivement :

```text
CC123  All Notes Off
CC121  Reset All Controllers
```

sur chacun des canaux.

Le flux est donc :

```text
canal 1
    CC123
    CC121
canal 2
    CC123
    CC121
...
canal 16
    CC123
    CC121
```

Cette fonction est notamment utilisée avant certains changements de
performance afin d'éviter que des notes ou des contrôleurs restent actifs
après une reconfiguration.

##### Noms des notes MIDI

La table :

```text
NOTE_NAMES
```

définit les douze notes chromatiques :

```text
C
C#
D
D#
E
F
F#
G
G#
A
A#
B
```

`note_name()` convertit un numéro de note MIDI en notation musicale.

Par exemple :

```text
60 → C4
69 → A4
```

Le calcul d'octave suit la convention MIDI :

```text
octave = note // 12 - 1
```

##### Conversion d'un nom de note

`note_number()` effectue l'opération inverse.

La fonction accepte soit :

```text
un numéro MIDI
```

soit :

```text
un nom de note
```

comme :

```text
C4
F#3
A0
```

Une valeur numérique est acceptée uniquement dans l'intervalle :

```text
0 à 127
```

Les noms de notes sont convertis selon la même convention d'octave que
`note_name()`.

Si la valeur ne peut pas être interprétée comme une note MIDI valide, la
fonction retourne :

```text
None
```

Les altérations prises en charge sont les dièses représentés par :

```text
#
```

Les noms utilisant explicitement un bémol ne sont pas interprétés par cette
fonction.

##### Affichage d'une plage de notes

`note_range()` produit une représentation lisible d'une plage MIDI définie
par :

```text
note_min
note_max
```

Lorsque les deux limites sont absentes, la fonction affiche la plage par
défaut :

```text
défaut (C-1) → défaut (G9)
```

Lorsqu'une seule limite est fournie, l'autre extrémité reste indiquée comme
valeur par défaut.

Lorsque les deux limites existent, elles sont converties avec
`note_name()`.

Si :

```text
note_min > note_max
```

les deux valeurs sont automatiquement inversées pour produire une plage
cohérente à l'affichage.

`note_range()` est donc principalement une fonction de présentation et ne
modifie pas les valeurs enregistrées dans le projet.

##### État général du système

`system_status()` construit un résumé de l'état courant de Fusion2QSynth.

La fonction vérifie d'abord la disponibilité des deux extrémités MIDI :

```text
Fusion
FluidSynth
```

à l'aide de :

```text
find_fusion_input()
find_fluidsynth_output()
```

Elle ajoute ensuite les statistiques fournies par `FusionProject` :

```text
mix_count
program_count
song_count
```

La structure retournée contient donc :

```text
fusion
fluidsynth
mix_count
program_count
song_count
```

Les champs :

```text
fusion
fluidsynth
```

sont des booléens indiquant si les ports correspondants ont été trouvés.

`system_status()` ne valide pas la configuration détaillée du projet et ne
teste pas le fonctionnement audio de FluidSynth.

Il fournit uniquement un état synthétique utilisé pour l'affichage général
du système.

##### Dépendances

`fusion_lib.py` dépend directement de :

```text
mido
fusion_constants.py
```

Les constantes utilisées sont :

```text
FUSION_INPUT_NAME
FLUIDSYNTH_OUTPUT_NAME
LOG_FILE
```

Pour `system_status()`, le projet lui est fourni comme paramètre.

Le module ne dépend donc pas directement de `FusionProject`, ce qui évite
d'introduire une dépendance circulaire avec le modèle du projet.

##### Séparation des responsabilités

La place de `fusion_lib.py` dans l'architecture peut être représentée ainsi :

```text
fusion_constants.py
        |
        v
   fusion_lib.py
   /     |      \
  /      |       \
MIDI   notes    logging
  \      |       /
   \     |      /
    modules applicatifs
```

`fusion_lib.py` fournit des services communs.

Les modules applicatifs restent responsables de l'interprétation des
événements MIDI, de la gestion des performances et de la persistance du
projet.

##### MIDI

* recherche des ports ;
* envoi MIDI ;
* fonctions de support FluidSynth ;
* fonctions de Panic.

##### Notes

* conversion numéro MIDI → nom de note ;
* conversion nom de note → numéro MIDI ;
* gestion des plages de notes.

Exemples acceptés :

```text
60
C3
D#4
```

##### Logging

Fonctions communes de journalisation.

##### Helpers

Fonctions indépendantes du modèle métier.

Une fonction placée dans `fusion_lib` doit autant que possible :

* être indépendante de `FusionProject` ;
* être réutilisable ;
* ne pas dépendre de l'interface utilisateur.

---

#### fusion_constants.py

`fusion_constants.py` centralise les constantes globales utilisées par
Fusion2QSynth.

Le module ne contient aucune logique applicative.

Son rôle est de fournir une source commune pour les paramètres qui doivent
être partagés entre plusieurs modules.

Les constantes sont regroupées selon les domaines suivants :

```text
projet et version
fichiers
configuration MIDI
limites MIDI
limites SoundFont
debug
```

##### Projet et version

Les constantes :

```text
PROJECT
VERSION
```

identifient l'application et sa version courante.

```text
PROJECT = "Fusion2QSynth"
```

`VERSION` doit être maintenue en cohérence avec la version publiée du
projet.

##### Fichiers

`LOG_FILE` définit le fichier utilisé pour la journalisation :

```text
fusion.log
```

`LAST_PERFORMANCE_FILE` définit le fichier utilisé pour conserver
l'identifiant de la dernière performance connue du Contrôleur Live :

```text
last_performance.json
```

Cette constante permet notamment à `fusion_controller_state.py` de
persister l'état nécessaire à la reprise d'une performance entre deux
exécutions.

##### Configuration MIDI

`FUSION_INPUT_NAME` contient la chaîne utilisée pour identifier le port
MIDI d'entrée du Fusion 8HD :

```text
CH345
```

`FLUIDSYNTH_OUTPUT_NAME` contient la chaîne utilisée pour identifier le
port MIDI de sortie de FluidSynth :

```text
FLUID Synth
```

Ces valeurs sont notamment utilisées par les fonctions de découverte des
ports de `fusion_lib.py`.

`FUSION_DEFAULT_CHANNEL` définit le canal MIDI principal utilisé par le
Fusion pour transmettre les informations globales nécessaires à
l'identification des performances :

```text
FUSION_DEFAULT_CHANNEL = 1
```

Cette valeur utilise la représentation utilisateur des canaux MIDI,
numérotés de `1` à `16`.

Lorsqu'elle est comparée au champ `channel` d'un message Mido, une
conversion vers la représentation interne `0-15` peut donc être
nécessaire.

##### Limites MIDI

Les limites générales des canaux MIDI sont définies par :

```text
MIDI_CHANNEL_MIN = 1
MIDI_CHANNEL_MAX = 16
```

Les numéros de notes MIDI utilisent :

```text
MIDI_NOTE_MIN = 0
MIDI_NOTE_MAX = 127
```

Les vélocités utilisent :

```text
MIDI_VELOCITY_MIN = 0
MIDI_VELOCITY_MAX = 127
```

Ces constantes permettent aux modules d'édition et de validation de
partager les mêmes limites plutôt que de les redéfinir localement.

##### Limites SoundFont

Les coordonnées des presets SoundFont sont limitées par :

```text
SF2_BANK_MIN = 0
SF2_BANK_MAX = 127

SF2_PROGRAM_MIN = 0
SF2_PROGRAM_MAX = 127
```

Ces constantes concernent la représentation utilisée par Fusion2QSynth
pour les banques et programmes SoundFont.

Elles ne doivent pas être confondues avec les coordonnées de banque et de
programme utilisées pour identifier les performances du Fusion.

##### Debug

La constante :

```text
DEBUG
```

active ou désactive les affichages de diagnostic conditionnels prévus dans
certains modules.

Sa valeur normale est :

```text
DEBUG = False
```

Elle constitue un réglage global de développement et ne fait pas partie
des données persistantes de `FusionProject`.

##### Place dans l'architecture

`fusion_constants.py` se situe à la base de plusieurs dépendances du
projet :

```text
             fusion_constants.py
                    |
        +-----------+-----------+
        |           |           |
        v           v           v
   fusion_lib   contrôleur   autres modules
        |           |           |
        +-----------+-----------+
                    |
                    v
              Fusion2QSynth
```

Le module doit rester indépendant des autres modules applicatifs.

Cette absence de dépendances permet aux constantes d'être utilisées
librement sans introduire de dépendances circulaires.

Les valeurs qui représentent l'état d'un PROGRAM, d'un MIX ou d'une SONG
ne doivent pas être placées dans `fusion_constants.py`.

Elles appartiennent soit au modèle persistant `FusionProject`, soit à
l'état d'exécution du Contrôleur Live.

---

### Outils de validation et de développement

#### integration-globale.py

`integration-globale.py` constitue un outil de validation globale du moteur
de correspondance entre les sons du Fusion et les presets SoundFont.

Il n'est pas utilisé par le fonctionnement normal de Fusion2QSynth.

Son rôle est de vérifier conjointement :

```text
fusion.json
fusion_gm_map.py
fusion_suggestions.py
sf2_library.json
```

afin de détecter les incohérences pouvant apparaître entre les données
réelles du projet, les correspondances General MIDI et le classement des
suggestions SoundFont.

##### Sources utilisées

Le script charge :

```text
FusionProject
FUSION_GM_DATA
la bibliothèque SoundFont
les fonctions de fusion_suggestions.py
```

Les presets issus de `sf2_library.py` sont adaptés vers la représentation
utilisée par le moteur de suggestions :

```text
id
name
bank
program
sf2_bank
sf2_program
```

Les champs temporaires :

```text
bank
program
```

reprennent respectivement :

```text
sf2_bank
sf2_program
```

Cette adaptation permet de tester directement `fusion_suggestions.py`
sans modifier la représentation persistante de la bibliothèque SoundFont.

##### Collecte des noms Fusion

Le script parcourt les trois types de performances enregistrés dans le
projet :

```text
MIX
PROGRAM
SONG
```

Pour les MIX et PROGRAM, il récupère le champ :

```text
fusion_name
```

des PARTS.

Pour les SONG, il récupère le même champ dans les canaux.

Les noms trouvés sont regroupés dans un ensemble afin que chaque nom Fusion
ne soit testé qu'une seule fois.

##### Validation des familles

Pour chaque nom Fusion, le script appelle :

```text
detect_gm_hint()
detect_families()
suggest_instruments()
```

Les familles détectées sont comparées avec la famille fournie par le hint
General MIDI.

Une table locale :

```text
FAMILY_COMPATIBILITY
```

autorise certaines relations sémantiques entre familles proches.

Par exemple :

```text
brass
    ↔ trumpet
    ↔ trombone
    ↔ french_horn

strings
    ↔ violin
    ↔ viola
    ↔ cello
    ↔ contrabass

woodwind
    ↔ flute
    ↔ clarinet
    ↔ oboe
    ↔ english_horn
    ↔ bassoon
    ↔ sax
```

Cette vérification permet de distinguer une véritable contradiction d'une
classification simplement plus générale ou plus spécialisée.

##### Classification des noms Fusion

Les noms rencontrés sont classés notamment dans les catégories :

```text
Hint GM
Famille seulement
Inconnus
Aucune suggestion
Hint / famille à vérifier
```

Cette classification permet d'identifier rapidement les zones encore
incomplètes dans `FUSION_GM_DATA`, `FAMILIES` ou les règles de détection.

##### Validation des suggestions

Le script vérifie plusieurs propriétés des résultats produits par
`suggest_instruments()`.

Les contrôles comprennent notamment :

```text
présence d'une suggestion
validité banque/programme
présence des champs obligatoires
absence de doublons
ordre des scores
plage raisonnable des scores
respect de la limite demandée
stabilité du meilleur résultat
stabilité du TOP N
respect du hint General MIDI
```

Les champs minimaux attendus pour un preset proposé sont :

```text
name
bank
program
```

Une suggestion est considérée comme invalide si sa banque ou son programme
sort des plages admises par le test.

##### Validation du paramètre limit

Le moteur de suggestions est testé avec plusieurs valeurs de :

```text
limit
```

notamment :

```text
1
2
3
```

Pour chaque famille, le script vérifie que le nombre de résultats retournés
ne dépasse pas la limite demandée.

Il vérifie également que le meilleur résultat reste identique lorsque la
valeur de `limit` change.

Par exemple, le résultat numéro 1 obtenu avec :

```text
limit=1
```

doit normalement être le même que le premier résultat obtenu avec :

```text
limit=2
limit=3
```

Le script vérifie également que :

```text
TOP 2 avec limit=2
```

correspond aux deux premiers résultats de :

```text
limit=3
```

Cela permet de détecter un classement instable dépendant artificiellement
du nombre de résultats demandé.

##### Validation des hints General MIDI

Lorsqu'un hint General MIDI existe, le script vérifie que le preset
correspondant au programme attendu apparaît dans les suggestions.

Pour une famille normale, la banque attendue est :

```text
0
```

Pour les kits de batterie, la banque attendue peut être :

```text
128
```

Le programme attendu provient du champ :

```text
gm_program
```

du hint.

Le script contrôle également que le meilleur résultat de la famille du hint
correspond au programme General MIDI attendu.

##### Validation complète de FUSION_GM_DATA

Une seconde passe parcourt directement toutes les entrées de :

```text
FUSION_GM_DATA
```

et chacun de leurs alias.

Chaque alias est soumis à :

```text
detect_gm_hint()
detect_gm_drum_kit()
suggest_instruments()
```

Le test vérifie successivement :

```text
alias
    |
    v
detect_gm_hint()
    |
    +---- famille correcte ?
    |
    +---- programme GM correct ?
    |
    v
suggest_instruments()
    |
    +---- suggestion disponible ?
    |
    +---- banque correcte ?
    |
    +---- programme correct ?
    |
    v
validation réussie
```

Cette vérification permet de confirmer que les données déclarées dans
`FUSION_GM_DATA` sont effectivement interprétées de la même manière par le
moteur de suggestions.

##### Rapport produit

Le script produit plusieurs sections de diagnostic, notamment :

```text
HINT GM
FAMILLE SEULEMENT
INCONNUS
AUCUNE SUGGESTION
HINT / FAMILLE À VÉRIFIER
HINT GM NON RESPECTÉ
MEILLEUR HINT GM INCORRECT
FAMILLE SEULEMENT À VÉRIFIER
SUGGESTIONS INVALIDES
SUGGESTIONS EN DOUBLON
CHAMPS MANQUANTS
SCORES MAL ORDONNÉS
SCORES ABERRANTS
LIMIT DÉPASSÉE
LIMIT PARAMÈTRE INCORRECT
TOP 1 INSTABLE
TOP N INSTABLE
VALIDATION FUSION_GM_DATA
```

Un résumé final indique le nombre de cas observés dans chacune de ces
catégories.

L'objectif est qu'après stabilisation du moteur de suggestions, les
catégories représentant de véritables anomalies tendent vers zéro.

##### Nature de l'outil

`integration-globale.py` est un test d'intégration exploratoire et de
régression.

Il ne modifie pas le projet.

Il ne corrige pas automatiquement les données.

Il observe les résultats produits par les différentes couches et signale
les incohérences éventuelles.

Sa place dans l'architecture est donc :

```text
                fusion.json
                    |
                    v
               FusionProject

fusion_gm_map.py --------+
                         |
                         v
                 fusion_suggestions.py
                         |
                         v
                   résultats testés
                         ^
                         |
                  sf2_library.py
                         |
                         v
              integration-globale.py
                         |
                         v
                 rapport de validation
```

Il constitue ainsi un outil de contrôle de cohérence globale du sous-système
de suggestions SoundFont.

---

#### compare_fusion_sf2.py

Outil de comparaison et d'analyse entre les données Fusion et les presets SoundFont.

Il sert principalement au développement et à la validation des mappings.

---

## Structure de `fusion.json`

`fusion.json` constitue le modèle persistant principal de Fusion2QSynth.

Son contenu est chargé, validé et sauvegardé exclusivement par `FusionProject`.

La structure générale est :

```json
{
  "format_version": 2,
  "instruments": {},
  "programs": {},
  "mixes": {},
  "songs": {}
}
```

Les quatre collections principales ont des rôles distincts :

```text
fusion.json
    |
    +-- instruments
    |
    +-- programs
    |
    +-- mixes
    |
    +-- songs
```

---

### `format_version`

`format_version` identifie la version du format de données de `fusion.json`.

Cette valeur est indépendante de la version de l'application Fusion2QSynth.

Elle permet à `FusionProject` de reconnaître la structure attendue du fichier et pourra servir à gérer d'éventuelles évolutions futures du modèle.

---

### Instruments

La section :

```text
instruments
```

constitue la bibliothèque d'instruments SoundFont configurés dans le projet.

Chaque instrument possède un identifiant interne utilisé par les PROGRAM, MIX et SONG.

Exemple conceptuel :

```json
"grand_piano": {
  "name": "Grand Piano",
  "sf2_bank": 0,
  "sf2_program": 0
}
```

L'identifiant :

```text
grand_piano
```

est la clé utilisée par les performances.

Les coordonnées SoundFont sont conservées dans la définition de l'instrument :

```text
sf2_bank
sf2_program
```

Elles ne doivent pas être confondues avec :

```text
bank
program
```

présents dans les données Fusion.

Les banques et programmes Fusion identifient les sons ou performances du Fusion 8HD.

Les valeurs `sf2_bank` et `sf2_program` identifient le preset à charger dans FluidSynth.

---

### PROGRAM

La section :

```text
programs
```

contient les PROGRAM connus du Fusion.

Un PROGRAM est identifié par :

```text
bank:program
```

par exemple :

```text
0:12
```

Sa structure générale est :

```text
PROGRAM
 |
 +-- name
 |
 +-- parts
      |
      +-- 1
           |
           +-- midi_channel
           +-- bank
           +-- program
           +-- note_min
           +-- note_max
           +-- velocity_min
           +-- velocity_max
           +-- instrument
           +-- fusion_name
```

Un PROGRAM comporte normalement une seule PART dans le modèle actuel.

Les données réellement présentes dépendent des informations capturées et de celles ajoutées ensuite par l'Éditeur.

`fusion_name` représente, lorsqu'il est connu, le nom du son correspondant sur le Fusion.

`instrument` référence un instrument de la collection :

```text
instruments
```

---

### MIX

La section :

```text
mixes
```

contient les MIX connus du Fusion.

Comme un PROGRAM, un MIX est identifié par :

```text
bank:program
```

par exemple :

```text
2:5
```

Sa structure générale est :

```text
MIX
 |
 +-- name
 |
 +-- parts
      |
      +-- 1
      +-- 2
      +-- ...
```

Chaque PART peut contenir notamment :

```text
midi_channel
bank
program
note_min
note_max
velocity_min
velocity_max
instrument
fusion_name
```

Le numéro de PART est une clé interne au MIX.

Le champ :

```text
midi_channel
```

détermine le canal MIDI utilisé par cette PART.

Les canaux MIDI stockés dans `fusion.json` utilisent la numérotation utilisateur :

```text
1 .. 16
```

Les modules utilisant Mido effectuent la conversion vers :

```text
0 .. 15
```

au moment de communiquer avec la bibliothèque MIDI.

Les champs :

```text
bank
program
```

d'une PART représentent le PROGRAM Fusion associé à cette PART.

Ils ne représentent pas les coordonnées SoundFont.

Le preset SoundFont utilisé est déterminé par la référence :

```text
instrument
```

vers la bibliothèque d'instruments.

Tous les champs ne sont pas nécessairement présents.

L'absence d'une information peut signifier qu'elle n'a pas été observée pendant la capture ou qu'elle n'a pas encore été configurée dans l'Éditeur.

---

### SONG

La section :

```text
songs
```

contient les SONG configurées pour le mode SONG.

Contrairement aux PROGRAM et MIX, une SONG est organisée directement par canal MIDI :

```text
SONG
 |
 +-- name
 |
 +-- channels
      |
      +-- 1
      +-- 2
      +-- ...
```

Chaque canal peut notamment contenir :

```text
bank
program
volume
pan
expression
reverb
chorus
instrument
fusion_name
```

Les clés de `channels` utilisent également la numérotation MIDI :

```text
1 .. 16
```

`bank` et `program` décrivent les données Fusion observées ou configurées pour le canal.

`instrument` référence le preset SoundFont à utiliser par l'intermédiaire de la bibliothèque `instruments`.

Les paramètres MIDI tels que :

```text
volume
pan
expression
reverb
chorus
```

peuvent être utilisés lors du chargement de la SONG dans FluidSynth.

---

### Références vers les instruments

PROGRAM, MIX et SONG ne doivent pas dupliquer les coordonnées SoundFont lorsqu'un instrument existe dans la bibliothèque.

Le principe est :

```text
PROGRAM / MIX / SONG
        |
        | instrument
        v
instruments
        |
        +-- name
        +-- sf2_bank
        +-- sf2_program
```

Par exemple :

```json
"instrument": "grand_piano"
```

référence :

```json
"grand_piano": {
  "name": "Grand Piano",
  "sf2_bank": 0,
  "sf2_program": 0
}
```

Cette séparation permet de modifier la définition SoundFont d'un instrument sans devoir modifier chaque PROGRAM, MIX ou SONG qui l'utilise.

---

### Séparation Fusion / SoundFont

Le modèle distingue volontairement deux espaces de données :

```text
Fusion 8HD                      FluidSynth / SoundFont
-----------                     ----------------------
bank                            sf2_bank
program                         sf2_program
fusion_name                     instrument → name
```

Cette distinction est essentielle.

Les informations reçues du Fusion décrivent la performance d'origine.

La bibliothèque `instruments` décrit la manière dont Fusion2QSynth reproduit cette performance avec FluidSynth.

---

### Propriété et persistance

`fusion.json` ne doit pas être manipulé directement par les modules applicatifs.

Le chemin normal est :

```text
Capture
Éditeur
Contrôleur / outils
        |
        v
FusionProject
        |
        +-- validation
        +-- réparation éventuelle
        +-- sauvegarde sécurisée
        |
        v
fusion.json
```

`FusionProject` constitue ainsi l'unique interface métier vers le modèle persistant.

L'état temporaire du Contrôleur Live n'est pas stocké dans `fusion.json`.

Il est maintenu séparément par `fusion_controller_state.py`.

## Banques SoundFont

Les banques SoundFont sont indépendantes des banques utilisées par le Fusion 8HD.

Cette distinction est fondamentale dans Fusion2QSynth.

Un instrument de la bibliothèque contient ses coordonnées SoundFont :

```text
sf2_bank
sf2_program
```

Par exemple :

```json
"grand_piano": {
  "name": "Grand Piano",
  "sf2_bank": 0,
  "sf2_program": 0
}
```

Ces valeurs indiquent le preset que FluidSynth doit utiliser.

Elles ne doivent pas être confondues avec :

```text
bank
program
```

présents dans les PROGRAM, MIX et SONG et provenant de l'organisation des sons du Fusion.

---

### Numérotation des banques SoundFont

Une banque SoundFont peut dépasser la plage d'un contrôleur MIDI individuel :

```text
0 .. 127
```

Fusion2QSynth conserve donc la banque SoundFont sous forme d'une valeur unique :

```text
sf2_bank
```

Lors de la programmation de FluidSynth, cette valeur est décomposée en Bank Select MIDI :

```text
MSB = sf2_bank // 128
LSB = sf2_bank % 128
```

Les messages envoyés sont ensuite :

```text
CC0             = MSB
CC32            = LSB
Program Change  = sf2_program
```

Par exemple :

```text
sf2_bank = 128
```

devient :

```text
CC0  = 1
CC32 = 0
```

alors que :

```text
sf2_bank = 8
```

devient :

```text
CC0  = 0
CC32 = 8
```

Cette représentation permet à Fusion2QSynth d'utiliser les différentes banques disponibles dans les fichiers SoundFont sans les confondre avec les banques du Fusion.

---

### Bibliothèque SoundFont

`sf2_library.py` analyse les fichiers SoundFont et représente leurs presets avec :

```text
sf2_bank
sf2_program
```

Ces coordonnées sont ensuite utilisées par l'Éditeur et le système de suggestions pour créer ou sélectionner les instruments de la bibliothèque du projet.

Le chemin logique est :

```text
SoundFont
    |
    v
sf2_library.py
    |
    | sf2_bank / sf2_program
    v
instrument
    |
    v
fusion.json
    |
    | référence instrument
    v
PROGRAM / MIX / SONG
```

Les PROGRAM, MIX et SONG référencent donc normalement un instrument plutôt que de conserver directement les coordonnées du preset SoundFont.

---

### Envoi vers FluidSynth

Lorsqu'une performance est chargée, Fusion2QSynth résout d'abord la référence :

```text
instrument
```

dans la bibliothèque du projet.

Il obtient ainsi :

```text
sf2_bank
sf2_program
```

puis programme le canal FluidSynth correspondant avec :

```text
CC0
CC32
Program Change
```

La conversion est effectuée uniquement au moment de la communication MIDI.

Le modèle persistant conserve toujours la représentation SoundFont :

```text
sf2_bank
sf2_program
```

---

### Séparation des espaces de banques

Trois notions de banque doivent donc rester distinctes :

```text
Banque de performance Fusion
        |
        | identifie un PROGRAM ou un MIX
        v
bank:program


Banque PROGRAM d'une PART Fusion
        |
        | décrit le son utilisé par la PART
        v
bank / program


Banque SoundFont
        |
        | sélectionne le preset FluidSynth
        v
sf2_bank / sf2_program
        |
        | conversion MIDI
        v
CC0 / CC32 / Program Change
```

Une banque MIX identifie une performance MIX.

La banque d'une PART d'un MIX appartient en revanche à l'espace des PROGRAM du Fusion.

La banque SoundFont appartient exclusivement à la configuration FluidSynth et ne doit jamais remplacer les données de banque reçues du Fusion.

---

## Flux de capture

La capture permet d'observer une performance directement sur le Fusion 8HD et d'enregistrer sa structure dans le projet.

Elle constitue le point d'entrée principal pour construire automatiquement les définitions des PROGRAM et MIX.

Le flux général est :

```text
Fusion 8HD
    |
    | MIDI
    v
fusion_capture.py
    |
    | détection de la performance
    | observation des PARTs
    | détection des canaux MIDI
    | plages de notes et vélocités
    v
FusionProject
    |
    | validation
    | sauvegarde sécurisée
    v
fusion.json
```

---

### Détection de la performance

En mode PROGRAM ou MIX, le Fusion transmet les informations permettant d'identifier la performance sélectionnée.

L'identifiant logique utilisé par Fusion2QSynth est :

```text
bank:program
```

par exemple :

```text
2:5
```

La banque et le programme identifient donc la performance Fusion à capturer.

---

### Détection des PARTs

Une fois la performance identifiée, la capture observe les événements MIDI produits lorsque l'utilisateur joue sur le Fusion.

Les canaux MIDI permettent d'identifier les PARTs actives.

Pour chaque PART observée, la capture peut déterminer notamment :

```text
midi_channel
note_min
note_max
velocity_min
velocity_max
```

Les plages sont construites à partir des événements réellement reçus.

La capture décrit donc ce qui a été observé sur le Fusion et ne suppose pas qu'une PART utilise nécessairement toute l'étendue du clavier ou toute la plage de vélocité.

---

### Données Fusion

Lorsque les informations correspondantes sont disponibles, une PART peut également conserver :

```text
bank
program
fusion_name
```

Ces données appartiennent à l'espace des PROGRAM du Fusion.

Elles ne représentent pas le preset SoundFont utilisé par FluidSynth.

L'association avec un preset SoundFont est réalisée séparément par la référence :

```text
instrument
```

gérée dans le modèle du projet.

---

### Construction de la performance

Les données capturées sont regroupées selon le type de performance :

```text
PROGRAM
    |
    +-- parts
         |
         +-- PART


MIX
    |
    +-- parts
         |
         +-- PART 1
         +-- PART 2
         +-- ...
```

Un PROGRAM comporte normalement une seule PART.

Un MIX peut contenir plusieurs PARTs utilisant des canaux MIDI différents.

Les canaux enregistrés dans le modèle utilisent la numérotation :

```text
1 .. 16
```

même si Mido utilise en interne :

```text
0 .. 15
```

---

### Persistance

`fusion_capture.py` ne constitue pas une seconde couche de persistance.

Une fois la capture terminée, les données passent par :

```text
FusionProject
```

qui reste responsable du modèle persistant.

Le flux d'écriture est donc :

```text
événements MIDI
      |
      v
données capturées
      |
      v
FusionProject
      |
      +-- validation
      +-- sauvegarde sécurisée
      |
      v
fusion.json
```

Cette séparation garantit que la Capture, l'Éditeur et les autres modules utilisent le même modèle de données.

---

### Capture et configuration SoundFont

La capture décrit d'abord la configuration observée sur le Fusion.

La sélection du son FluidSynth constitue une étape distincte :

```text
Capture Fusion
      |
      v
bank / program / canal / plages
      |
      v
fusion.json
      |
      v
Éditeur
      |
      +-- identification du son Fusion
      +-- suggestions SoundFont
      +-- choix de l'instrument
      |
      v
instrument
      |
      v
sf2_bank / sf2_program
```

Cette séparation permet de conserver les caractéristiques originales de la performance Fusion tout en choisissant indépendamment le preset SoundFont chargé par FluidSynth.

---

## Flux d'édition

L'Éditeur permet de compléter, corriger et enrichir les données capturées depuis le Fusion 8HD.

Il intervient principalement après la capture afin d'associer les performances Fusion aux instruments SoundFont et d'ajuster leur configuration.

Le flux général est :

```text
fusion.json
    |
    v
FusionProject
    |
    v
fusion_editor.py
    |
    +-- PROGRAM
    +-- MIX
    +-- SONG
    +-- Instruments
    |
    v
FusionProject
    |
    +-- validation
    +-- sauvegarde sécurisée
    |
    v
fusion.json
```

---

### Chargement du projet

L'Éditeur travaille sur le modèle chargé par :

```text
FusionProject
```

Il ne lit ni n'écrit directement `fusion.json`.

Les modifications sont effectuées sur le modèle du projet puis sauvegardées par les mécanismes fournis par `FusionProject`.

Cette organisation maintient une seule couche responsable de la persistance et de la validation des données.

---

### Édition des performances

L'Éditeur permet de travailler séparément sur :

```text
PROGRAM
MIX
SONG
```

Pour un PROGRAM ou un MIX, l'édition porte principalement sur les PARTs.

Une PART peut notamment être configurée avec :

```text
midi_channel
bank
program
note_min
note_max
velocity_min
velocity_max
instrument
fusion_name
```

Pour une SONG, l'édition s'effectue par canal MIDI.

Un canal peut notamment contenir :

```text
bank
program
volume
pan
expression
reverb
chorus
instrument
fusion_name
```

L'Éditeur permet ainsi de compléter les informations qui n'ont pas pu être déterminées automatiquement pendant la capture.

---

### Association des instruments

L'une des fonctions principales de l'Éditeur consiste à associer un son Fusion à un instrument de la bibliothèque du projet.

Le flux est :

```text
PROGRAM / MIX / SONG
        |
        | fusion_name
        v
Système de suggestions
        |
        +-- fusion_suggestions.py
        +-- fusion_gm_map.py
        +-- sf2_library.py
        |
        v
Presets SoundFont candidats
        |
        v
Choix utilisateur
        |
        v
instrument
        |
        v
Bibliothèque instruments
```

Les suggestions facilitent le choix mais ne modifient pas automatiquement la signification de la performance.

Le choix final de l'instrument reste enregistré explicitement dans le projet.

---

### Création d'un instrument

Lorsqu'un preset SoundFont est choisi et qu'aucun instrument correspondant n'existe encore dans le projet, l'Éditeur peut créer une entrée dans :

```text
instruments
```

La définition persistante contient notamment :

```text
name
sf2_bank
sf2_program
```

La performance conserve ensuite seulement la référence :

```text
instrument
```

Le modèle obtenu est donc :

```text
PART / canal
     |
     | instrument
     v
Bibliothèque instruments
     |
     +-- name
     +-- sf2_bank
     +-- sf2_program
```

Cette organisation évite de dupliquer les coordonnées SoundFont dans chaque performance.

---

### Préécoute et comparaison

L'Éditeur peut programmer temporairement FluidSynth afin de permettre l'écoute d'un preset SoundFont avant de l'associer définitivement à une performance.

Le flux de préécoute est :

```text
Preset SoundFont
      |
      +-- sf2_bank
      +-- sf2_program
      |
      v
conversion Bank Select
      |
      +-- CC0
      +-- CC32
      +-- Program Change
      |
      v
FluidSynth
```

Cette opération sert à l'évaluation du son.

Elle ne modifie pas à elle seule le modèle persistant.

L'Éditeur permet également de comparer des instruments ou de tester les PARTs d'un MIX séparément ou ensemble afin de vérifier le résultat avant sauvegarde.

---

### Modification du modèle

Une opération d'édition suit conceptuellement le chemin :

```text
sélection
    |
    v
modification
    |
    v
modèle en mémoire
    |
    v
validation
    |
    +-- valide
    |      |
    |      v
    |   sauvegarde
    |
    +-- invalide
           |
           v
       correction /
       annulation
```

Certaines opérations peuvent également déclencher les mécanismes de réparation du projet lorsque des incohérences sont détectées.

Les contrôles de validité restent centralisés dans `FusionProject`.

---

### Sauvegarde sécurisée

Les modifications persistantes passent par le mécanisme de sauvegarde sécurisée de `FusionProject`.

Le principe est :

```text
fusion_editor.py
      |
      v
FusionProject
      |
      +-- validation
      +-- contrôle des erreurs
      +-- sauvegarde sécurisée
      |
      v
fusion.json
```

Lorsque l'opération ne peut pas être enregistrée correctement, l'Éditeur évite autant que possible de laisser le modèle dans un état partiellement modifié.

Les opérations concernées peuvent restaurer l'état précédent lorsqu'une sauvegarde échoue.

---

### Relation Capture / Éditeur

La Capture et l'Éditeur ont des responsabilités complémentaires :

```text
Fusion 8HD
    |
    v
Capture
    |
    | observation
    v
Données Fusion
    |
    v
Éditeur
    |
    | correction
    | enrichissement
    | association SoundFont
    v
Configuration complète
    |
    v
FusionProject
    |
    v
fusion.json
```

La Capture cherche à représenter fidèlement les données observées sur le Fusion.

L'Éditeur transforme ensuite cette capture en configuration exploitable par le Contrôleur Live, notamment en établissant les associations avec la bibliothèque d'instruments SoundFont.

---

## Flux du Contrôleur Live

Le Contrôleur Live assure l'exécution en temps réel des performances configurées dans `fusion.json`.

Il reçoit les événements MIDI du Fusion 8HD, détecte les changements de performance et configure FluidSynth selon les données du projet.

Le flux général est :

```text
Fusion 8HD
    |
    | MIDI
    v
fusion_controller.py
    |
    v
fusion_controller_loop.py
    |
    +-- détection PROGRAM / MIX
    +-- gestion SONG
    +-- filtrage des événements
    +-- suivi des notes actives
    |
    v
fusion_performance.py
    |
    +-- résolution de la performance
    +-- résolution des instruments
    +-- configuration des canaux
    |
    v
FluidSynth
```

L'état d'exécution est maintenu séparément par :

```text
fusion_controller_state.py
```

Il n'est pas enregistré dans `fusion.json`.

---

### Initialisation

Au démarrage, `fusion_controller.py` initialise le projet, les connexions MIDI et l'état du Contrôleur Live.

Le mode sélectionné détermine ensuite le comportement du contrôleur :

```text
PROGRAM
MIX
SONG
```

Lorsque cela est applicable, la dernière performance utilisée peut être rechargée afin de rétablir l'état musical précédent.

Le contrôleur entre ensuite dans la boucle MIDI gérée par :

```text
fusion_controller_loop.py
```

---

### État du contrôleur

L'état dynamique du Contrôleur Live comprend notamment :

```text
current_mode
current_performance
current_parts
active_notes
pending_reload
```

Ces informations décrivent uniquement l'exécution en cours.

La séparation est donc :

```text
fusion.json
    |
    | configuration persistante
    v
FusionProject


fusion_controller_state.py
    |
    | état d'exécution
    v
Contrôleur Live
```

Cette distinction évite de mélanger la configuration du projet avec l'état temporaire d'une session MIDI.

---

### Mode PROGRAM

En mode PROGRAM, le Fusion transmet sur son canal MIDI par défaut les messages permettant d'identifier le PROGRAM sélectionné.

Le principe est :

```text
Fusion
  |
  +-- CC0
  |
  +-- Program Change
          |
          v
      bank:program
          |
          v
       PROGRAM
```

Le contrôleur utilise cet identifiant pour rechercher le PROGRAM correspondant dans le projet.

La performance est ensuite chargée par `fusion_performance.py`.

Le PROGRAM comporte normalement une seule PART.

---

### Mode MIX

La détection d'un MIX utilise le même principe :

```text
CC0
 |
Program Change
 |
 v
bank:program
 |
 v
MIX
```

Le CC0 reçu sur le canal MIDI par défaut du Fusion sert à mémoriser la banque de la performance.

Le Program Change suivant permet de construire l'identifiant :

```text
bank:program
```

Le MIX correspondant est alors chargé depuis le projet.

Chaque PART active est associée à son canal MIDI et à l'instrument SoundFont configuré.

---

### Bank Select des PARTs

En modes PROGRAM et MIX, il est essentiel de distinguer le Bank Select servant à identifier la performance des Bank Select émis par les PARTs.

Le principe est :

```text
Canal Fusion par défaut
        |
        +-- CC0
        |
        v
détection de la banque
PROGRAM / MIX


Canaux des PARTs
        |
        +-- CC0
        +-- CC32
        |
        v
ignorés pour la sélection
SoundFont
```

Les CC0 et CC32 provenant des PARTs ne sont pas retransmis à FluidSynth.

Ils pourraient autrement modifier la banque SoundFont programmée par Fusion2QSynth et remplacer le mapping défini dans la bibliothèque `instruments`.

La sélection SoundFont reste donc sous le contrôle de `fusion_performance.py`.

---

### Chargement d'une performance

Lorsqu'un PROGRAM ou un MIX est détecté, le contrôleur transmet son identifiant au mécanisme de chargement des performances.

Le flux devient :

```text
bank:program
      |
      v
fusion_performance.py
      |
      v
FusionProject
      |
      +-- PROGRAM ou MIX
      |
      v
PARTs
      |
      +-- midi_channel
      +-- instrument
      |
      v
Bibliothèque instruments
      |
      +-- sf2_bank
      +-- sf2_program
      |
      v
FluidSynth
```

Pour chaque PART active, l'instrument configuré est résolu dans la bibliothèque du projet.

Les coordonnées SoundFont sont ensuite converties en messages MIDI nécessaires à la programmation du canal FluidSynth.

---

### PARTs actives

Après le chargement d'une performance, le contrôleur connaît les PARTs qui doivent participer à l'exécution.

Cette information est conservée dans :

```text
current_parts
```

Les événements MIDI appartenant à des PARTs non actives peuvent ainsi être ignorés.

Le principe est :

```text
événement MIDI
      |
      v
canal associé à une PART active ?
      |
   +--+--+
   |     |
  oui   non
   |     |
   v     v
traité  ignoré
```

Cela empêche des canaux inutilisés du Fusion d'influencer la performance chargée dans FluidSynth.

---

### Événements MIDI

Une fois la performance chargée, les événements nécessaires à l'interprétation musicale sont transmis à FluidSynth.

Cela comprend notamment les notes et les contrôleurs MIDI qui ne sont pas réservés au fonctionnement interne du contrôleur.

Le filtrage permet donc de distinguer :

```text
Messages de contrôle
de Fusion2QSynth
        |
        +-- détection performance
        +-- Bank Select des PARTs
        |
        v
consommés / filtrés


Messages d'interprétation
        |
        +-- notes
        +-- contrôleurs autorisés
        +-- autres événements utiles
        |
        v
FluidSynth
```

Le Contrôleur Live agit ainsi comme une couche entre le Fusion et FluidSynth plutôt que comme un simple relais MIDI.

---

### Notes actives

Le contrôleur maintient également :

```text
active_notes
```

afin de connaître les notes actuellement actives.

Cette information permet de gérer proprement les transitions de performance et d'éviter qu'un changement de configuration laisse des notes suspendues dans FluidSynth.

La gestion des notes actives appartient à l'état d'exécution et n'est donc pas persistée dans `fusion.json`.

---

### Mode SONG

Le mode SONG utilise un fonctionnement différent.

Une SONG n'est pas sélectionnée par le couple :

```text
CC0 + Program Change
```

comme un PROGRAM ou un MIX.

En mode SONG, les Program Change reçus du Fusion sont donc ignorés par le mécanisme de sélection des performances.

La SONG choisie est chargée lors de la réception de l'événement MIDI :

```text
START
```

Le principe est :

```text
SONG sélectionnée
      |
      v
en attente
      |
      | MIDI START
      v
chargement SONG
      |
      v
configuration des canaux
      |
      v
FluidSynth
```

La SONG peut configurer plusieurs canaux avec leurs instruments et paramètres MIDI.

---

### Rechargement différé

Certaines modifications ou transitions ne doivent pas nécessairement être appliquées immédiatement pendant qu'une performance est en cours.

L'état :

```text
pending_reload
```

permet au contrôleur de mémoriser qu'un rechargement doit être effectué au moment approprié.

Cette information reste entièrement dynamique et appartient à `fusion_controller_state.py`.

---

### Persistance de la dernière performance

Le Contrôleur Live peut conserver l'identité de la dernière performance utilisée afin de la retrouver lors d'une session suivante.

Le flux conceptuel est :

```text
performance chargée
      |
      v
save_last_performance()
      |
      v
état persistant de dernière performance


démarrage
      |
      v
load_last_performance()
      |
      v
restauration de la sélection
```

Cette fonction ne transforme pas `fusion.json` en stockage de l'état d'exécution du contrôleur.

La configuration des performances et l'état courant demeurent deux responsabilités distinctes.

---

### Flux global

Le fonctionnement complet peut être résumé ainsi :

```text
                    Fusion 8HD
                        |
                        | MIDI
                        v
              fusion_controller_loop.py
                        |
             +----------+----------+
             |                     |
             v                     v
      PROGRAM / MIX               SONG
             |                     |
      CC0 + Program Change       MIDI START
             |                     |
             +----------+----------+
                        |
                        v
              fusion_performance.py
                        |
                        v
                  FusionProject
                        |
                        v
               PROGRAM / MIX / SONG
                        |
                        v
                      PARTs
                   ou canaux
                        |
                        v
                  instruments
                        |
                        v
              sf2_bank / sf2_program
                        |
                        v
                   FluidSynth
                        ^
                        |
              événements MIDI
                 autorisés
```

Le Contrôleur Live relie ainsi les trois couches principales du système :

```text
Fusion 8HD
    |
    v
configuration Fusion2QSynth
    |
    v
FluidSynth / SoundFont
```

Il conserve la configuration persistante dans `FusionProject`, l'état d'exécution dans `fusion_controller_state.py` et centralise le chargement des performances dans `fusion_performance.py`.

## Validation

Fusion2QSynth utilise deux niveaux de validation complémentaires :

```text
Validation du projet
        |
        v
FusionProject
        |
        +-- structure
        +-- cohérence
        +-- références
        +-- sauvegarde


Validation de développement
        |
        v
integration-globale.py
        |
        +-- mapping Fusion / GM
        +-- familles
        +-- suggestions SoundFont
        +-- scores et classement
        +-- stabilité
```

Le premier niveau protège les données persistantes.

Le second vérifie la cohérence globale des mécanismes de correspondance et de suggestion utilisés par l'application.

---

### Validation du modèle

`FusionProject` constitue le point central de validation de `fusion.json`.

La validation porte sur les quatre collections principales :

```text
instruments
programs
mixes
songs
```

ainsi que sur leurs relations.

Le principe général est :

```text
fusion.json
    |
    v
FusionProject
    |
    +-- structure valide ?
    +-- champs valides ?
    +-- canaux valides ?
    +-- références valides ?
    |
    +------ oui ------> modèle utilisable
    |
    +------ non ------> erreurs
                         |
                         +-- réparation possible
                         +-- correction utilisateur
```

La validation ne dépend donc pas de l'interface qui a produit les données.

Une donnée provenant de la Capture ou de l'Éditeur passe par les mêmes règles de cohérence.

---

### Validation des performances

Les PROGRAM et MIX sont validés à partir de leurs PARTs.

Les contrôles portent notamment sur la structure de la performance et sur les paramètres contenus dans chaque PART.

Les canaux MIDI persistants doivent respecter la convention du projet :

```text
1 .. 16
```

Une même performance doit également conserver une structure cohérente entre ses PARTs.

Les SONG sont validées selon leur structure par canaux :

```text
SONG
 |
 +-- channels
      |
      +-- canal
           |
           +-- paramètres MIDI
           +-- instrument
```

Les valeurs invalides ou les incohérences détectées sont rapportées par `FusionProject`.

---

### Validation des instruments

La bibliothèque :

```text
instruments
```

est également soumise à validation.

Une définition d'instrument doit fournir les informations nécessaires pour identifier le preset SoundFont associé, notamment :

```text
name
sf2_bank
sf2_program
```

Les références :

```text
instrument
```

utilisées dans les PROGRAM, MIX et SONG doivent correspondre à des instruments existants.

Cette vérification protège la chaîne :

```text
PART / canal
     |
     | instrument
     v
instruments
     |
     +-- sf2_bank
     +-- sf2_program
     |
     v
FluidSynth
```

---

### Réparation

Certaines incohérences peuvent être réparées.

Le mécanisme de validation et réparation permet de présenter les problèmes détectés puis d'appliquer les corrections appropriées lorsque celles-ci peuvent être déterminées sans ambiguïté.

Le cycle peut se répéter :

```text
validation
    |
    +-- aucune erreur
    |       |
    |       v
    |     terminé
    |
    +-- erreurs
            |
            v
        réparation
            |
            v
        validation
            |
            +-- ...
```

Ce fonctionnement permet de corriger plusieurs problèmes successifs dans un même projet.

Les erreurs qui ne peuvent pas être réparées automatiquement doivent rester visibles afin d'être corrigées explicitement.

---

### Validation avant sauvegarde

La validation fait partie du mécanisme de protection de la persistance.

Le flux normal est :

```text
modification
    |
    v
FusionProject
    |
    v
validation
    |
    +-- acceptable
    |       |
    |       v
    |   sauvegarde sécurisée
    |
    +-- non acceptable
            |
            v
       sauvegarde refusée
       ou correction requise
```

La sauvegarde ne doit donc pas transformer silencieusement une incohérence du modèle en donnée persistante valide en apparence.

Certaines opérations de l'Éditeur conservent également l'état précédent afin de pouvoir revenir en arrière lorsqu'une sauvegarde échoue.

---

### Validation globale de développement

`integration-globale.py` est un outil de développement.

Il ne participe pas au fonctionnement normal de Fusion2QSynth et ne modifie pas `fusion.json`.

Son rôle est de vérifier globalement les mécanismes utilisés pour établir les correspondances entre les noms Fusion et les presets SoundFont.

Il teste notamment :

```text
fusion_gm_map.py
        |
        v
fusion_suggestions.py
        |
        v
sf2_library.py
```

à partir des données réellement présentes dans le projet et des tables de correspondance définies par l'application.

---

### Couverture de `integration-globale.py`

La validation globale contrôle notamment :

```text
détection des hints GM
détection des familles
suggestions SoundFont
respect du programme GM attendu
classement des suggestions
cohérence des scores
absence de doublons
respect du paramètre limit
stabilité du Top 1
stabilité du Top N
validité des presets
couverture des aliases FUSION_GM_DATA
```

L'outil distingue également les situations qui ne constituent pas nécessairement des erreurs :

```text
nom Fusion inconnu
absence de hint GM
absence de suggestion
conflit apparent de famille
```

Ces cas permettent d'identifier les zones où les tables de correspondance pourraient être enrichies sans considérer automatiquement le projet comme invalide.

---

### Validation exhaustive de `FUSION_GM_DATA`

`integration-globale.py` vérifie également les aliases définis dans :

```text
FUSION_GM_DATA
```

Chaque nom connu peut ainsi être soumis au même mécanisme de détection que les noms provenant de `fusion.json`.

Le flux est :

```text
FUSION_GM_DATA
      |
      v
alias Fusion
      |
      v
détection GM / famille
      |
      v
suggestions
      |
      v
vérification du résultat
```

Cette validation exhaustive permet de détecter une régression dans les tables de correspondance même lorsqu'un alias particulier n'est pas présent dans le projet actuellement chargé.

---

### Non-modification des données

La distinction entre validation applicative et validation de développement est importante :

```text
FusionProject
     |
     +-- valide les données
     +-- peut participer à leur réparation
     +-- contrôle leur sauvegarde


integration-globale.py
     |
     +-- analyse
     +-- teste
     +-- rapporte
     +-- ne modifie pas le projet
```

`integration-globale.py` doit donc pouvoir être exécuté librement pendant le développement sans modifier la configuration utilisateur.

---

### Objectif architectural

L'ensemble forme une chaîne de contrôle à deux niveaux :

```text
                 fusion.json
                     |
                     v
                FusionProject
                     |
             validation du modèle
                     |
                     v
              Application
          Capture / Éditeur / Live


fusion.json + tables GM + SoundFonts
                     |
                     v
           integration-globale.py
                     |
              tests de cohérence
                     |
                     v
             développement
```

`FusionProject` garantit la cohérence du modèle persistant nécessaire au fonctionnement de l'application.

`integration-globale.py` protège quant à lui la cohérence des mécanismes de mapping et de suggestion lors de leur évolution.

### Réparation progressive

La réparation d'un projet peut nécessiter plusieurs étapes.

Une erreur corrigée peut rendre visible une autre incohérence qui ne pouvait pas être traitée correctement auparavant.

Fusion2QSynth utilise donc un principe de réparation progressive :

```text
validation
    |
    v
erreurs détectées ?
    |
 +--+--+
 |     |
non   oui
 |     |
 v     v
fin   réparation
        |
        v
   nouvelle validation
        |
        +------> ...
```

Après chaque réparation, le projet est validé de nouveau.

Le processus se poursuit jusqu'à ce que :

```text
aucune erreur ne subsiste
```

ou que l'utilisateur décide de ne pas effectuer une réparation proposée.

Ce fonctionnement évite de supposer qu'une seule passe de validation permet nécessairement d'identifier et de corriger toutes les incohérences du projet.

Il permet également de conserver un ordre logique entre les réparations lorsqu'une correction dépend de la validité d'une structure corrigée précédemment.

Le principe général est donc :

```text
détecter
   |
   v
réparer
   |
   v
revalider
   |
   v
détecter
   |
   v
...
```

La réparation progressive reste contrôlée par les mécanismes de validation de `FusionProject`.

L'Éditeur fournit l'interaction avec l'utilisateur, mais ne définit pas un second système indépendant de validation du modèle.

## Sauvegarde

La sauvegarde de `fusion.json` est centralisée dans `FusionProject`.

Les modules applicatifs ne doivent pas écrire directement dans le fichier.

Le principe est :

```text
Capture
Éditeur
autres modules
     |
     v
FusionProject
     |
     +-- validation
     +-- sauvegarde sécurisée
     |
     v
fusion.json
```

Cette centralisation garantit que toutes les modifications persistantes passent par les mêmes mécanismes de contrôle.

---

### Sauvegarde sécurisée

La méthode de sauvegarde sécurisée constitue le chemin normal d'écriture du projet.

Le flux général est :

```text
modification du modèle
        |
        v
FusionProject
        |
        v
validation
        |
   +----+----+
   |         |
valide    erreurs
   |         |
   v         v
écriture   traitement
             |
             +-- correction
             +-- réparation
             +-- refus éventuel
```

La validation précède donc la persistance des modifications.

L'objectif est d'éviter qu'une modification incorrecte remplace silencieusement un projet utilisable.

---

### Erreurs préexistantes

Une distinction doit être faite entre :

```text
erreur introduite par
la modification courante
```

et :

```text
erreur déjà présente
dans le projet
```

Un projet peut contenir une incohérence préexistante sans rapport avec l'opération actuellement effectuée.

La sauvegarde sécurisée peut tenir compte de cette situation afin qu'une erreur ancienne ne bloque pas nécessairement toute modification indépendante.

Le principe recherché est :

```text
état avant modification
        |
        +-- erreurs connues
        |
        v
modification
        |
        v
état après modification
        |
        +-- aucune nouvelle
        |   erreur bloquante
        |
        v
sauvegarde possible
```

Une opération ne doit toutefois pas être autorisée à introduire de nouvelles incohérences dans le modèle.

---

### Échec de sauvegarde

Lorsqu'une modification ne peut pas être sauvegardée correctement, le module appelant doit éviter autant que possible de conserver un modèle partiellement modifié.

Certaines opérations de l'Éditeur utilisent donc le principe :

```text
état initial
     |
     v
modification en mémoire
     |
     v
tentative de sauvegarde
     |
 +---+---+
 |       |
succès  échec
 |       |
 v       v
nouvel  restauration
état    de l'état initial
```

Cette stratégie permet de maintenir la cohérence entre l'état en mémoire et l'état réellement enregistré.

---

### Relation avec la réparation

La sauvegarde et la réparation sont deux mécanismes distincts.

```text
Validation
    |
    +-- projet cohérent
    |       |
    |       v
    |   sauvegarde
    |
    +-- incohérence
            |
            v
        réparation
            |
            v
        revalidation
            |
            v
        sauvegarde
```

La réparation progressive peut donc précéder une sauvegarde lorsqu'une incohérence doit être corrigée.

La sauvegarde ne remplace jamais la validation ou la réparation.

---

### Responsabilités

La séparation des responsabilités est :

```text
fusion_editor.py
fusion_capture.py
autres modules
        |
        | demandent une modification
        v
FusionProject
        |
        +-- possède le modèle
        +-- valide le modèle
        +-- contrôle la sauvegarde
        |
        v
fusion.json
```

Les modules applicatifs décident des modifications métier à effectuer.

`FusionProject` décide si l'état obtenu peut être persisté et assure l'écriture du fichier.

---

### Objectif architectural

Le mécanisme de sauvegarde protège la chaîne :

```text
données utilisateur
       |
       v
modèle en mémoire
       |
       v
validation
       |
       v
sauvegarde sécurisée
       |
       v
fusion.json
```

L'objectif n'est pas seulement d'écrire un fichier JSON valide syntaxiquement.

La sauvegarde doit préserver un modèle Fusion2QSynth cohérent et exploitable par la Capture, l'Éditeur et le Contrôleur Live.

## Encapsulation

Fusion2QSynth sépare les différentes responsabilités de l'application dans des modules spécialisés.

L'objectif est d'éviter qu'un module d'interface ou une boucle MIDI contienne directement la logique de persistance, de validation, de gestion des performances ou d'analyse SoundFont.

Le principe général est :

```text
Interface / orchestration
        |
        v
Modules spécialisés
        |
        v
Modèle et services
```

Chaque module possède ainsi une responsabilité clairement définie.

---

### Modèle persistant

La gestion de `fusion.json` est encapsulée dans :

```text
FusionProject
```

Les autres modules utilisent `FusionProject` pour accéder au modèle, le valider, le réparer et le sauvegarder.

Ils ne doivent pas développer leur propre mécanisme indépendant de persistance.

```text
Capture
Éditeur
Contrôleur
Diagnostic
    |
    v
FusionProject
    |
    v
fusion.json
```

Cette encapsulation garantit une représentation commune du projet dans toute l'application.

---

### Contrôleur Live

Le Contrôleur Live est lui-même divisé selon plusieurs responsabilités :

```text
fusion_controller.py
        |
        +-- initialisation
        +-- orchestration
        |
        v
fusion_controller_loop.py
        |
        +-- traitement MIDI
        +-- filtrage
        +-- détection des performances
        |
        +--------------------------+
        |                          |
        v                          v
fusion_controller_state.py   fusion_performance.py
        |                          |
        | état dynamique           | chargement
        |                          | des performances
        v                          v
   état courant                FluidSynth
```

`fusion_controller.py` reste ainsi le point d'entrée du Contrôleur Live sans devoir contenir toute sa logique.

`fusion_controller_loop.py` traite les événements MIDI.

`fusion_controller_state.py` encapsule l'état dynamique.

`fusion_performance.py` centralise le chargement des PROGRAM, MIX et SONG.

---

### Éditeur

`fusion_editor.py` constitue principalement la couche interactive permettant de modifier le projet.

Les responsabilités spécialisées sont déléguées aux modules appropriés :

```text
fusion_editor.py
       |
       +-- FusionProject
       |      |
       |      +-- modèle
       |      +-- validation
       |      +-- sauvegarde
       |
       +-- sf2_library.py
       |      |
       |      +-- presets SoundFont
       |
       +-- fusion_suggestions.py
       |      |
       |      +-- recherche de correspondances
       |
       +-- fusion_gm_map.py
              |
              +-- données Fusion / GM
```

L'Éditeur orchestre ces services mais ne doit pas dupliquer leur logique.

---

### SoundFont et suggestions

La gestion des correspondances entre les sons Fusion et les presets SoundFont est également encapsulée.

```text
fusion_gm_map.py
       |
       | données de référence
       v
fusion_suggestions.py
       |
       | logique de correspondance
       v
sf2_library.py
       |
       | presets disponibles
       v
fusion_editor.py
```

Les responsabilités sont distinctes :

`fusion_gm_map.py` contient les connaissances de référence sur les noms Fusion, les familles et les programmes GM.

`fusion_suggestions.py` applique les règles permettant de rechercher et classer les correspondances.

`sf2_library.py` fournit la représentation des presets réellement disponibles dans les SoundFonts.

Cette séparation permet de modifier une table de correspondance ou un algorithme de suggestion sans modifier directement l'Éditeur.

---

### Diagnostic

Les fonctions de diagnostic sont séparées de l'interface qui les utilise.

```text
fusion_monitor.py
       |
       v
fusion_diagnostic.py
       |
       v
analyse du système
et des données MIDI
```

Le monitor fournit l'interaction tandis que le module de diagnostic regroupe les fonctions spécialisées nécessaires à l'analyse.

---

### Fonctions communes

Les fonctions utilisées par plusieurs parties de l'application sont regroupées dans :

```text
fusion_lib.py
```

Les constantes communes sont regroupées dans :

```text
fusion_constants.py
```

Le principe est :

```text
modules applicatifs
      |
      +------> fusion_lib.py
      |
      +------> fusion_constants.py
```

Cela évite de recopier les mêmes fonctions ou valeurs dans plusieurs modules.

Les constantes utilisent les conventions du modèle Fusion2QSynth, notamment les canaux MIDI :

```text
1 .. 16
```

La conversion vers les conventions propres aux bibliothèques externes est effectuée à la frontière correspondante.

Par exemple :

```text
Fusion2QSynth : 1 .. 16
        |
        | -1
        v
Mido          : 0 .. 15
```

---

### Dépendances

L'encapsulation cherche à maintenir les dépendances dans une direction claire :

```text
Interfaces / points d'entrée
          |
          v
Logique applicative
          |
          v
Services spécialisés
          |
          v
Modèle / bibliothèques externes
```

Un module de bas niveau ne devrait pas dépendre de l'interface qui l'utilise.

Par exemple, `FusionProject` n'a pas besoin de connaître le fonctionnement de l'Éditeur ou du Contrôleur Live.

De même, `fusion_suggestions.py` fournit un service de suggestion sans dépendre du menu interactif qui présente les résultats.

---

### État persistant et état dynamique

L'encapsulation sépare également deux catégories d'état :

```text
État persistant
      |
      v
FusionProject
      |
      v
fusion.json


État dynamique
      |
      v
fusion_controller_state.py
      |
      v
session du Contrôleur Live
```

Cette distinction empêche les informations temporaires d'exécution de contaminer le modèle persistant.

---

### Objectif architectural

L'architecture obtenue peut être résumée ainsi :

```text
                    Fusion2QSynth
                         |
        +----------------+----------------+
        |                |                |
        v                v                v
     Capture          Éditeur        Contrôleur
        |                |                |
        |        +-------+-------+        |
        |        |               |        |
        |        v               v        |
        |   Suggestions      SoundFont    |
        |                                |
        +--------------+-----------------+
                       |
                       v
                  FusionProject
                       |
                       v
                   fusion.json
```

L'encapsulation vise principalement à obtenir :

```text
responsabilités distinctes
dépendances explicites
logique réutilisable
état centralisé
validation commune
maintenance simplifiée
```

Chaque nouvelle fonctionnalité doit autant que possible être ajoutée au module correspondant à sa responsabilité plutôt que d'étendre indéfiniment les points d'entrée de l'application.

---

## Dépendances

Fusion2QSynth utilise une architecture modulaire dans laquelle les dépendances suivent autant que possible une direction claire.

Le principe général est :

```text
Points d'entrée / interfaces
          |
          v
Logique applicative
          |
          v
Services spécialisés
          |
          v
Modèle / bibliothèques externes
```

Les modules de bas niveau ne doivent pas dépendre des interfaces qui les utilisent.

Cette organisation limite les dépendances circulaires et permet aux services d'être réutilisés par plusieurs parties de l'application.

---

### Dépendances internes

Les principales relations entre modules peuvent être représentées ainsi :

```text
                    fusion2qsynth.py
                           |
              +------------+------------+
              |            |            |
              v            v            v
           Capture       Éditeur    Contrôleur Live
              |            |            |
              |            |     +------+------+
              |            |     |      |      |
              |            |     v      v      v
              |            |   loop   state  performance
              |            |                   |
              |            +---------+---------+
              |                      |
              v                      v
                        FusionProject
                             |
                             v
                         fusion.json
```

Les modules spécialisés complètent cette structure :

```text
fusion_editor.py
      |
      +-- fusion_suggestions.py
      |          |
      |          +-- fusion_gm_map.py
      |
      +-- sf2_library.py
      |
      +-- fusion_diagnostic.py
      |
      +-- FusionProject
```

Les fonctions et constantes communes sont fournies par :

```text
fusion_lib.py
fusion_constants.py
```

et peuvent être utilisées par plusieurs modules.

---

### `FusionProject`

`FusionProject` constitue une dépendance centrale de l'application.

Il fournit l'accès au modèle persistant et concentre :

```text
chargement
validation
réparation
sauvegarde
```

Les modules qui manipulent le projet doivent passer par cette couche plutôt que d'implémenter leur propre accès à `fusion.json`.

La dépendance doit rester orientée ainsi :

```text
module applicatif
      |
      v
FusionProject
      |
      v
fusion.json
```

et non :

```text
FusionProject
      |
      v
fusion_editor.py
ou
fusion_controller.py
```

`FusionProject` reste ainsi indépendant des interfaces qui l'utilisent.

---

### Dépendances du Contrôleur Live

Le Contrôleur Live est réparti entre plusieurs modules :

```text
fusion_controller.py
        |
        +-- fusion_controller_loop.py
        |
        +-- fusion_controller_state.py
        |
        +-- fusion_performance.py
        |
        +-- FusionProject
```

`fusion_controller.py` assure l'orchestration.

`fusion_controller_loop.py` dépend des services nécessaires au traitement des événements MIDI, mais ne doit pas devenir propriétaire du modèle persistant.

`fusion_controller_state.py` contient uniquement l'état dynamique nécessaire à l'exécution.

`fusion_performance.py` dépend du modèle du projet pour résoudre et charger les performances.

Cette séparation permet de faire évoluer la boucle MIDI, l'état d'exécution et le chargement des performances indépendamment.

---

### Dépendances SoundFont

Le système SoundFont repose sur trois responsabilités distinctes :

```text
fusion_gm_map.py
       |
       v
fusion_suggestions.py
       |
       +----------+
       |          |
       v          v
sf2_library.py   Éditeur
```

`fusion_gm_map.py` fournit les données de référence Fusion et General MIDI.

`fusion_suggestions.py` utilise ces données pour déterminer les familles et produire des suggestions.

`sf2_library.py` représente les presets réellement disponibles dans les fichiers SoundFont.

L'Éditeur combine ces services afin de permettre à l'utilisateur de choisir les instruments à enregistrer dans le projet.

---

### Bibliothèques externes

Fusion2QSynth dépend de plusieurs composants extérieurs à l'application.

Les principales dépendances sont :

```text
Python
 |
 +-- mido
 |     |
 |     v
 |   MIDI
 |
 +-- ALSA sequencer
       |
       v
 périphériques MIDI


FluidSynth
    |
    v
synthèse SoundFont


PipeWire
    |
    v
sortie audio
```

Mido fournit l'interface MIDI utilisée par les modules Python.

ALSA Sequencer assure les ports et connexions MIDI sous Linux.

FluidSynth assure la synthèse à partir des presets SoundFont.

PipeWire assure la sortie audio utilisée par FluidSynth dans la configuration actuelle.

---

### Outils SoundFont externes

L'analyse de la bibliothèque SoundFont peut également dépendre d'outils externes utilisés pour obtenir les informations contenues dans les fichiers `.sf2`.

Ces informations sont ensuite normalisées par :

```text
sf2_library.py
```

afin que le reste de l'application travaille avec une représentation commune :

```text
name
sf2_bank
sf2_program
```

Le reste de l'application ne doit donc pas dépendre directement du format de sortie d'un outil externe.

Cette dépendance est encapsulée dans la couche SoundFont.

---

### Conventions aux frontières

Certaines dépendances externes utilisent des conventions différentes de celles du modèle Fusion2QSynth.

Le cas principal concerne les canaux MIDI :

```text
Fusion2QSynth
1 .. 16
    |
    | conversion
    v
Mido
0 .. 15
```

La conversion doit être effectuée à la frontière avec Mido.

De la même manière, une banque SoundFont est conservée dans le modèle sous forme :

```text
sf2_bank
```

puis convertie au moment de l'envoi MIDI :

```text
sf2_bank
    |
    +-- MSB = sf2_bank // 128
    |
    +-- LSB = sf2_bank % 128
    |
    v
CC0 / CC32
```

Les conventions propres aux bibliothèques externes ne doivent donc pas se propager inutilement dans le modèle interne.

---

### Dépendances de développement

Les outils de validation peuvent dépendre des modules applicatifs afin de les tester.

Par exemple :

```text
integration-globale.py
       |
       +-- FusionProject
       +-- fusion_gm_map.py
       +-- fusion_suggestions.py
       +-- sf2_library.py
```

La relation inverse ne doit pas exister.

Les modules applicatifs ne doivent pas dépendre de :

```text
integration-globale.py
```

Un outil de développement peut donc observer et tester l'application sans devenir nécessaire à son fonctionnement.

---

### Principe général

La direction recherchée des dépendances est :

```text
Interface
    |
    v
Logique applicative
    |
    v
Services
    |
    v
Modèle
```

avec, parallèlement :

```text
Outils de développement
          |
          v
Modules applicatifs
```

Les dépendances externes sont introduites aux frontières appropriées :

```text
MIDI       -> Mido / ALSA
Synthèse   -> FluidSynth
Audio      -> PipeWire
SoundFont  -> outils SF2
```

Cette organisation permet de modifier une interface, un mécanisme de suggestion ou un outil de développement sans imposer inutilement ces changements aux autres couches de l'application.

---

## Limites MIDI du Fusion

Fusion2QSynth doit tenir compte de plusieurs caractéristiques du comportement MIDI du Fusion 8HD.

Ces contraintes expliquent certaines décisions prises dans la Capture et dans le Contrôleur Live.

---

### Canaux MIDI des PARTs

Dans un MIX, chaque PART doit utiliser un canal MIDI distinct pour pouvoir être identifiée et contrôlée indépendamment par Fusion2QSynth.

Le Fusion transmet les notes selon le canal configuré pour chaque PART :

```text
PART 1 ----> canal MIDI 1
PART 2 ----> canal MIDI 2
PART 3 ----> canal MIDI 3
...
```

Fusion2QSynth ne peut pas déduire deux PARTs distinctes si celles-ci transmettent exactement les mêmes événements sur le même canal MIDI.

La configuration MIDI du MIX sur le Fusion fait donc partie des conditions nécessaires à une capture exploitable.

---

### Sélection d'un MIX

Lorsqu'un MIX est sélectionné, le Fusion transmet les informations permettant d'identifier le MIX sous la forme :

```text
CC0
 |
Program Change
 |
 v
bank:program
```

Ces messages sont émis sur le canal MIDI par défaut du Fusion.

Fusion2QSynth utilise cette séquence pour détecter le changement de performance.

Le canal MIDI par défaut constitue donc un canal de contrôle pour la détection du PROGRAM ou du MIX sélectionné.

---

### Configuration des PARTs

La sélection d'un MIX ne transmet pas à elle seule une description complète de toutes ses PARTs.

Fusion2QSynth doit observer les événements MIDI produits par les PARTs pour déterminer leur utilisation effective.

La Capture peut notamment établir :

```text
midi_channel
note_min
note_max
velocity_min
velocity_max
```

à partir des événements réellement observés.

Cela signifie que la capture dépend de ce qui est effectivement joué pendant la phase d'apprentissage.

---

### Bank Select des PARTs

Les PARTs peuvent transmettre leurs propres messages :

```text
CC0
CC32
Program Change
```

Ces informations décrivent la sélection des sons du Fusion.

Elles ne correspondent pas aux banques SoundFont configurées dans Fusion2QSynth.

Le problème serait :

```text
PART Fusion
    |
    +-- CC0
    +-- CC32
    |
    v
FluidSynth
    |
    v
banque SoundFont modifiée
```

Le preset choisi par Fusion2QSynth pourrait alors être remplacé par les Bank Select provenant du Fusion.

Pour cette raison, en modes PROGRAM et MIX, les CC0 et CC32 des PARTs ne sont pas retransmis à FluidSynth.

La banque SoundFont demeure sous le contrôle de Fusion2QSynth.

---

### Program Change et identification de performance

Le Program Change possède deux significations possibles selon son origine :

```text
canal MIDI par défaut
        |
        v
identification PROGRAM / MIX


canal d'une PART
        |
        v
sélection d'un son Fusion
```

Fusion2QSynth doit donc interpréter le message selon le canal sur lequel il est reçu.

En mode PROGRAM ou MIX, le Program Change utilisé pour sélectionner la performance n'est pris en compte que sur le canal MIDI par défaut du Fusion.

---

### Mode SONG

Le mode SONG présente une différence importante.

La sélection d'une SONG n'est pas détectée par le même mécanisme :

```text
CC0 + Program Change
```

que les PROGRAM et MIX.

Les Program Change reçus en mode SONG ne sont donc pas utilisés pour changer la SONG active dans Fusion2QSynth.

La SONG sélectionnée est chargée lors de la réception de :

```text
MIDI START
```

Le fonctionnement est ainsi :

```text
sélection SONG
      |
      v
SONG en attente
      |
      | START
      v
chargement
      |
      v
FluidSynth
```

Cette différence impose un traitement spécifique du mode SONG dans le Contrôleur Live.

---

### Numérotation des canaux

Le Fusion et l'interface utilisateur représentent naturellement les canaux MIDI sous la forme :

```text
1 .. 16
```

Fusion2QSynth conserve cette convention dans son modèle persistant.

Mido utilise cependant :

```text
0 .. 15
```

La conversion est donc effectuée à la frontière MIDI :

```text
Fusion / fusion.json
       1 .. 16
          |
          | -1
          v
        Mido
       0 .. 15
```

Cette conversion doit rester explicite afin d'éviter les erreurs de décalage de canal.

---

### Informations non transmises

Fusion2QSynth ne doit pas supposer que toute la configuration interne d'une performance Fusion est disponible par MIDI.

Le système travaille uniquement avec les informations que le Fusion transmet effectivement et avec celles que l'utilisateur complète ensuite dans l'Éditeur.

Le principe architectural est :

```text
Configuration interne
du Fusion
      |
      | informations MIDI
      | effectivement transmises
      v
Capture
      |
      v
fusion.json
      |
      | enrichissement
      v
Éditeur
```

L'Éditeur complète donc volontairement les informations que la communication MIDI ne permet pas de déterminer automatiquement.

---

### Conséquences architecturales

Ces limites expliquent plusieurs choix de Fusion2QSynth :

```text
Fusion 8HD
    |
    +-- identification partielle
    |   des performances
    |
    +-- PARTs observées
    |   par canal MIDI
    |
    +-- Bank Select Fusion
    |   distinct du SoundFont
    |
    +-- comportement SONG
        spécifique
    |
    v
Fusion2QSynth
    |
    +-- Capture
    +-- filtrage MIDI
    +-- modèle persistant
    +-- Éditeur
    +-- mapping SoundFont
```

Fusion2QSynth ne cherche donc pas à reproduire automatiquement toute la configuration interne du Fusion 8HD.

Il construit une représentation exploitable à partir des données MIDI disponibles, puis permet de la compléter et de l'associer explicitement aux instruments SoundFont.

---

## Principes de conception

L'architecture de Fusion2QSynth repose sur plusieurs principes destinés à préserver la cohérence du projet et à faciliter son évolution.

Ces principes servent également de règles pour les développements futurs.

---

### Une responsabilité principale par module

Chaque module doit posséder une responsabilité clairement identifiable.

```text
fusion_capture.py
    -> capture MIDI

fusion_editor.py
    -> édition interactive

fusion_controller_loop.py
    -> traitement MIDI temps réel

fusion_controller_state.py
    -> état dynamique du contrôleur

fusion_performance.py
    -> chargement des performances

fusion_project.py
    -> modèle persistant

sf2_library.py
    -> bibliothèque SoundFont

fusion_suggestions.py
    -> suggestions d'instruments

fusion_gm_map.py
    -> connaissances Fusion / GM
```

Lorsqu'une fonctionnalité appartient naturellement à un service existant, elle doit être ajoutée à ce service plutôt que dupliquée dans le module qui l'utilise.

---

### Une seule représentation persistante

`fusion.json` constitue la représentation persistante du projet.

Son accès est encapsulé par :

```text
FusionProject
```

Les modules applicatifs travaillent avec le modèle fourni par `FusionProject` et ne maintiennent pas leur propre représentation persistante parallèle.

```text
Application
    |
    v
FusionProject
    |
    v
fusion.json
```

Cette règle garantit que la Capture, l'Éditeur et le Contrôleur Live utilisent les mêmes données.

---

### Séparer données Fusion et données SoundFont

Les informations provenant du Fusion doivent rester distinctes des informations nécessaires à FluidSynth.

```text
Fusion                         SoundFont
------                         ---------
bank                           sf2_bank
program                        sf2_program
fusion_name                    instrument
```

Les données Fusion décrivent la performance d'origine.

Les données SoundFont décrivent la manière choisie pour la reproduire.

Cette séparation permet de modifier le mapping SoundFont sans perdre les informations provenant du Fusion.

---

### Référencer plutôt que dupliquer

Les coordonnées SoundFont sont centralisées dans la bibliothèque :

```text
instruments
```

Les PROGRAM, MIX et SONG utilisent une référence :

```text
instrument
```

plutôt que de dupliquer systématiquement :

```text
sf2_bank
sf2_program
```

Le principe est :

```text
performance
    |
    | instrument
    v
bibliothèque
    |
    +-- sf2_bank
    +-- sf2_program
```

Une modification de l'instrument peut ainsi être répercutée partout où celui-ci est utilisé.

---

### Conserver les conventions internes

Le modèle Fusion2QSynth utilise ses propres conventions de façon uniforme.

Par exemple, les canaux MIDI sont représentés par :

```text
1 .. 16
```

La convention Mido :

```text
0 .. 15
```

n'est utilisée qu'à la frontière avec la bibliothèque.

```text
modèle
1 .. 16
   |
   | conversion
   v
Mido
0 .. 15
```

Une convention imposée par une dépendance externe ne doit pas se propager inutilement dans l'ensemble de l'application.

---

### Observer plutôt que supposer

La Capture doit représenter ce que le Fusion transmet réellement.

Elle ne doit pas inventer une configuration qui n'a pas été observée.

```text
Fusion
   |
   | événements observés
   v
Capture
   |
   v
modèle
```

Les informations absentes peuvent ensuite être complétées explicitement dans l'Éditeur.

Ce principe est particulièrement important pour les PARTs, les plages de notes et les plages de vélocité.

---

### Ne pas confondre détection et configuration

Les messages utilisés pour détecter une performance ne doivent pas nécessairement être retransmis à FluidSynth.

Par exemple :

```text
CC0 du canal Fusion par défaut
        |
        v
détection PROGRAM / MIX
```

alors que :

```text
CC0 / CC32 des PARTs
        |
        v
filtrage
```

permet de protéger la configuration SoundFont.

Le Contrôleur Live interprète donc le flux MIDI avant de décider quels messages doivent atteindre FluidSynth.

---

### Centraliser le chargement des performances

Le chargement des PROGRAM, MIX et SONG doit passer par :

```text
fusion_performance.py
```

Le Contrôleur Live détecte la performance.

`fusion_performance.py` détermine comment cette performance doit être appliquée à FluidSynth.

```text
détection
    |
    v
performance
    |
    v
fusion_performance.py
    |
    v
FluidSynth
```

Cette centralisation évite de reproduire la logique de chargement dans plusieurs branches de la boucle MIDI.

---

### Séparer état persistant et état d'exécution

La configuration du projet et l'état courant du Contrôleur Live sont deux choses différentes.

```text
Configuration persistante
        |
        v
FusionProject
        |
        v
fusion.json


État d'exécution
        |
        v
fusion_controller_state.py
```

Les notes actives, la performance courante ou un rechargement en attente ne doivent pas devenir des propriétés permanentes du projet.

---

### Valider avant de persister

Toute modification persistante doit passer par les mécanismes de validation de `FusionProject`.

```text
modification
    |
    v
validation
    |
    v
sauvegarde
```

Une sauvegarde ne doit pas être considérée comme une simple écriture JSON.

Elle doit préserver la cohérence du modèle Fusion2QSynth.

---

### Réparer progressivement

Lorsqu'une incohérence est réparée, le projet doit être validé de nouveau.

```text
détecter
   |
   v
réparer
   |
   v
revalider
   |
   v
...
```

Cette stratégie permet de traiter correctement les erreurs qui dépendent les unes des autres.

---

### Les suggestions restent des suggestions

Le système de correspondance Fusion / GM / SoundFont aide l'utilisateur à choisir un instrument.

Il ne doit pas transformer une estimation en vérité persistante sans décision explicite.

```text
fusion_name
     |
     v
suggestions
     |
     v
choix utilisateur
     |
     v
instrument
```

La logique automatique fournit des candidats.

Le choix enregistré dans le projet reste explicite.

---

### Les outils de développement restent externes à l'application

Les outils tels que :

```text
integration-globale.py
```

peuvent dépendre des modules applicatifs pour les tester.

L'application ne doit pas dépendre de ces outils.

```text
outil de développement
        |
        v
application
```

et jamais :

```text
application
        |
        v
outil de développement
```

Les tests et outils d'analyse peuvent ainsi évoluer ou disparaître sans modifier le fonctionnement de Fusion2QSynth.

---

### Privilégier les données explicites

Lorsque plusieurs sources d'information sont possibles, une donnée explicitement enregistrée dans le projet doit avoir priorité sur une déduction pouvant être recalculée.

Le système de suggestions sert principalement à compléter les informations manquantes.

Le principe est :

```text
donnée configurée
      |
      v
utilisation directe


donnée absente
      |
      v
détection / suggestion
      |
      v
choix
```

Cela évite qu'une évolution de l'algorithme de suggestion modifie implicitement une configuration déjà établie.

---

### Préserver la traçabilité

Lorsque cela est possible, les données provenant du Fusion doivent être conservées même après l'association avec un instrument SoundFont.

Ainsi :

```text
fusion_name
bank
program
```

permettent de conserver la connaissance de la source Fusion tandis que :

```text
instrument
```

décrit la configuration choisie pour FluidSynth.

Cette séparation facilite le diagnostic, la modification des mappings et l'évolution future des SoundFonts.

---

### Principe général

L'architecture de Fusion2QSynth peut finalement être résumée par :

```text
Observer
   |
   v
Conserver
   |
   v
Valider
   |
   v
Enrichir
   |
   v
Associer
   |
   v
Exécuter
```

avec les règles suivantes :

```text
ne pas dupliquer la logique
ne pas mélanger les responsabilités
ne pas confondre Fusion et SoundFont
ne pas persister l'état temporaire
ne pas supposer ce qui n'a pas été observé
ne pas contourner FusionProject
```

Ces principes doivent rester prioritaires lors de l'ajout de nouvelles fonctionnalités afin que l'évolution du projet ne réintroduise pas les dépendances et duplications éliminées par l'architecture actuelle.

---

## Évolutions futures

L'architecture de Fusion2QSynth a été conçue pour permettre l'évolution du projet sans remettre en cause la séparation actuelle des responsabilités.

Les nouvelles fonctionnalités doivent autant que possible s'intégrer aux modules existants plutôt que créer des chemins parallèles vers le modèle, le MIDI ou FluidSynth.

---

### Évolution du modèle

Le champ :

```text id="5f08br"
format_version
```

permet de faire évoluer la structure de `fusion.json`.

Une modification incompatible du modèle devra pouvoir être identifiée explicitement et accompagnée, lorsque nécessaire, d'un mécanisme de migration.

Le principe est :

```text id="s4m4zb"
ancien format
     |
     v
détection
     |
     v
migration
     |
     v
nouveau format
```

Les évolutions du modèle doivent rester sous la responsabilité de `FusionProject`.

---

### Enrichissement des données Fusion

Les connaissances disponibles sur les PROGRAM, MIX et SONG pourront être enrichies à mesure que de nouvelles informations MIDI seront observées ou comprises.

Ces ajouts doivent préserver le principe :

```text id="c3rdr8"
donnée observée
     |
     v
modèle Fusion
```

et rester distincts des choix SoundFont effectués pour reproduire la performance.

---

### Évolution du mapping Fusion / GM

Les tables de :

```text id="3n3zlu"
fusion_gm_map.py
```

peuvent être enrichies lorsque de nouveaux noms Fusion sont rencontrés.

Les modifications doivent continuer à être vérifiées par :

```text id="34v6dg"
integration-globale.py
```

afin d'éviter qu'une nouvelle correspondance dégrade les mappings existants.

---

### Évolution des suggestions

Le système de suggestions peut évoluer indépendamment de l'Éditeur grâce à :

```text id="wth6ge"
fusion_suggestions.py
```

De nouvelles règles de classement ou de correspondance pourront être ajoutées sans modifier le principe fondamental :

```text id="if9pdu"
analyse automatique
       |
       v
suggestions
       |
       v
choix utilisateur
```

Une suggestion ne doit pas devenir automatiquement une modification persistante sans décision explicite.

---

### Support SoundFont

L'encapsulation de la bibliothèque SoundFont permet de faire évoluer :

```text id="5mlc7q"
analyse des fichiers SF2
recherche des presets
présentation des banques
sélection des instruments
```

sans modifier la représentation utilisée par le reste de l'application :

```text id="0v2xf5"
name
sf2_bank
sf2_program
```

Les détails propres aux outils ou formats externes doivent continuer à rester confinés à cette couche.

---

### Contrôleur Live

Le découpage :

```text id="7vzc5i"
controller
   |
   +-- loop
   +-- state
   +-- performance
```

permet de faire évoluer séparément :

```text id="5zpnqm"
traitement MIDI
gestion de l'état
chargement des performances
```

Les évolutions futures du Contrôleur Live doivent préserver cette séparation plutôt que réintroduire toute la logique dans le point d'entrée principal.

---

### Validation

Toute extension significative du modèle ou des mécanismes de mapping doit être accompagnée de contrôles correspondants.

Le principe reste :

```text id="gqegft"
nouvelle fonctionnalité
        |
        v
validation
        |
        v
intégration
```

`FusionProject` protège la cohérence du modèle persistant.

Les outils de développement vérifient les comportements qui dépassent la simple validité structurelle du projet.

---

### Compatibilité

Les évolutions futures doivent chercher à préserver :

```text id="ff02rn"
les projets existants
les instruments configurés
les mappings utilisateur
les données capturées
```

Une amélioration automatique ne doit pas remplacer silencieusement une configuration explicitement choisie par l'utilisateur.

Lorsque le modèle doit évoluer, la transformation doit être identifiable et contrôlée.

---

### Orientation générale

Les évolutions futures doivent respecter les frontières déjà établies :

```text id="m3ql4e"
Fusion
   |
   v
Capture
   |
   v
FusionProject
   |
   +------> Éditeur
   |
   +------> Contrôleur Live
   |
   v
SoundFont / FluidSynth
```

L'objectif n'est pas de figer l'architecture.

Il est de permettre son évolution tout en conservant :

```text id="f01paf"
un modèle unique
des responsabilités distinctes
des dépendances maîtrisées
une validation centralisée
une séparation Fusion / SoundFont
```

Les fonctionnalités envisagées mais non encore implantées doivent être suivies séparément dans `TODO` plutôt que décrites comme faisant partie de l'architecture actuelle.

---

## Philosophie du projet

Fusion2QSynth est né d'un objectif simple : permettre au Fusion 8HD de piloter naturellement un environnement logiciel moderne tout en conservant la logique de travail de l'instrument.

Le projet ne cherche pas à remplacer le Fusion.

Il cherche à prolonger son utilisation.

---

### Le Fusion reste l'instrument

Le Fusion 8HD demeure le point de départ de l'interaction musicale.

```text
Musicien
   |
   v
Fusion 8HD
   |
   v
Fusion2QSynth
   |
   v
FluidSynth
   |
   v
SoundFont
```

Les PROGRAM, MIX et SONG sélectionnés sur le Fusion déterminent le contexte musical.

Fusion2QSynth interprète ce contexte et configure l'environnement logiciel correspondant.

L'ordinateur devient ainsi une extension du Fusion plutôt qu'un instrument indépendant qu'il faudrait constamment reconfigurer.

---

### S'adapter au comportement réel de l'instrument

Fusion2QSynth est construit à partir du comportement MIDI réellement observé du Fusion.

Le projet privilégie :

```text
observer
comprendre
modéliser
```

plutôt que supposer le fonctionnement de l'instrument.

Lorsque le MIDI ne fournit pas suffisamment d'information, le système permet à l'utilisateur de compléter explicitement le modèle.

Cette approche explique la complémentarité entre :

```text
Capture
   |
   v
observation

Éditeur
   |
   v
enrichissement

Contrôleur Live
   |
   v
exécution
```

---

### Automatiser sans retirer le contrôle

Fusion2QSynth automatise ce qui peut être déterminé de façon fiable.

Lorsqu'une décision comporte une part d'interprétation, le système propose plutôt qu'il n'impose.

C'est notamment le principe du mapping des instruments :

```text
Fusion
   |
   v
analyse
   |
   v
suggestions
   |
   v
choix utilisateur
   |
   v
SoundFont
```

L'automatisation doit réduire le travail nécessaire sans rendre les décisions du système opaques.

---

### Conserver l'information d'origine

Les données provenant du Fusion sont conservées indépendamment de leur interprétation pour FluidSynth.

Le projet distingue donc :

```text
ce que le Fusion représente
```

de :

```text
la manière choisie pour le reproduire
```

Cette séparation permet de changer de SoundFont, d'améliorer un mapping ou de faire évoluer les règles de suggestion sans perdre la connaissance acquise sur les performances du Fusion.

---

### Une configuration compréhensible

Le fichier :

```text
fusion.json
```

constitue une représentation explicite du travail effectué avec Fusion2QSynth.

Il ne doit pas devenir un simple état interne opaque nécessaire au fonctionnement du programme.

Les PROGRAM, MIX, SONG et instruments doivent rester suffisamment structurés pour pouvoir être :

```text
inspectés
validés
corrigés
enrichis
réutilisés
```

Cette transparence facilite également le diagnostic lorsque le comportement obtenu ne correspond pas au résultat attendu.

---

### Construire progressivement

Le projet s'est développé par observation, expérimentation et validation successive.

Cette méthode reste adaptée à son évolution :

```text
observer
   |
   v
comprendre
   |
   v
implanter
   |
   v
tester
   |
   v
valider
   |
   v
intégrer
```

Une fonctionnalité n'est pas considérée comme acquise uniquement parce qu'elle semble correcte théoriquement.

Elle doit fonctionner avec le Fusion, le flux MIDI réel et l'environnement FluidSynth utilisé par le projet.

---

### Préserver la simplicité d'utilisation

La complexité technique nécessaire à l'intégration MIDI, aux banques SoundFont et au mapping des instruments doit autant que possible rester à l'intérieur de Fusion2QSynth.

L'objectif final reste simple :

```text
sélectionner sur le Fusion
        |
        v
jouer
```

Le travail de configuration, de capture et d'édition sert à rendre cette utilisation quotidienne aussi transparente que possible.

---

### Faire évoluer sans reconstruire

Fusion2QSynth n'est pas conçu comme une succession de scripts indépendants.

Son architecture doit permettre d'ajouter progressivement de nouvelles capacités en conservant ce qui fonctionne déjà.

Chaque évolution doit donc chercher à :

```text
réutiliser les données existantes
préserver les configurations utilisateur
respecter les responsabilités des modules
éviter les duplications
maintenir la compatibilité
```

L'architecture n'est pas une fin en soi.

Elle sert à rendre le projet suffisamment stable pour continuer à évoluer.

---

### Finalité

Fusion2QSynth établit un pont entre deux environnements :

```text
Alesis Fusion 8HD
        |
        | MIDI
        v
Fusion2QSynth
        |
        | mapping
        v
FluidSynth
        |
        v
SoundFonts
```

Le Fusion fournit l'interface musicale et les performances.

Fusion2QSynth fournit l'interprétation, la mémoire et l'adaptation.

FluidSynth et les SoundFonts fournissent le moteur sonore.

La philosophie du projet peut ainsi se résumer à :

```text
Comprendre le Fusion.
Conserver ce qu'il transmet.
Compléter ce qu'il ne transmet pas.
Adapter ce qui doit l'être.
Puis laisser le musicien jouer.
```
