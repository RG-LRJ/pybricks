# Commander le train avec une télécommande LEGO

Ce programme est prévu pour un **City Hub LEGO Powered Up équipé du firmware Pybricks**, une télécommande LEGO Powered Up, un moteur de train sans capteur de rotation et des lumières LEGO Powered Up. Branche le moteur sur le **port A** et les lumières sur le **port B**.

## Installation et appairage

1. Si nécessaire, installe le firmware Pybricks sur le City Hub depuis [Pybricks Code](https://code.pybricks.com/), puis connecte le hub à cette application.
2. Ouvre `train.py` dans Pybricks Code, puis lance-le une fois avec le bouton ▶ pour le transférer sur le hub. Le voyant du hub clignote régulièrement en bleu (environ trois clignotements toutes les deux secondes) pendant que le programme attend. Déconnecte ensuite Pybricks Code si tu le souhaites.
3. Allume la télécommande avec son bouton vert : son voyant doit clignoter en blanc. Si elle est déjà connectée à un autre appareil, déconnecte-la d'abord.
4. Appuie une fois brièvement sur le bouton du hub. Il clignote en jaune pendant la recherche, puis les voyants du hub et de la télécommande passent au vert si la connexion réussit.

La recherche dure 15 secondes au maximum : en cas d'échec, le hub s'allume en rouge pendant 2 secondes, puis clignote à nouveau en bleu. Rapproche la télécommande, vérifie qu'elle clignote en blanc et appuie de nouveau sur le bouton du hub. Le programme connecte la première télécommande disponible ; aucun appairage Bluetooth séparé dans le téléphone ou l'ordinateur n'est nécessaire.

Si Pybricks indique que les lumières ne sont pas reconnues sur le port B, vérifie leur branchement et leur compatibilité avec les lumières LEGO Powered Up. Le programme peut continuer sans lumières pour permettre l'appairage et la conduite ; après avoir rebranché les lumières, relance-le pour les utiliser. Si le moteur sur le port A n'est pas reconnu, vérifie son branchement avant de relancer le programme.

Après avoir éteint le hub, il faut d'abord l'allumer par un appui, puis lancer le programme enregistré par un autre appui. Ensuite, un appui bref supplémentaire déclenche la recherche. Un voyant bleu peut aussi indiquer que le programme ne tourne pas : dans ce cas, vérifie son lancement dans Pybricks Code. L'appui de recherche ne peut être détecté que si le programme est en cours d'exécution.

Pendant ce programme, un appui bref sur le hub ne l'arrête pas et déclenche la recherche uniquement quand le programme est en attente. Pour l'éteindre, maintiens son bouton environ 3 secondes ; tu peux aussi arrêter le programme depuis Pybricks Code.

## Commandes

Chaque pression sur `+` ou `−` modifie la puissance d'un cran ; le moteur continue à tourner après le relâchement. Il démarre à l'arrêt et les lumières sont éteintes au lancement.

| Bouton | Action |
| --- | --- |
| Gauche `+` | Augmente la puissance vers l'avant. |
| Gauche `−` | Diminue la puissance ; en continuant au-delà de zéro, fait marche arrière. |
| Rouge gauche | Arrêt d'urgence : remet la puissance à zéro, freine et déclenche trois clignotements des feux. |
| Rouge droit | Envoie le signal SOS en morse (`··· −−− ···`) avec les feux à pleine luminosité. |
| Droit `+` / `−` | Augmente ou diminue la luminosité par crans de 10 %. Descends jusqu'à 0 % pour éteindre les feux. |
| Vert central | Termine le programme et freine le moteur. |

Le frein est passif : le train peut encore parcourir une courte distance. Garde-le à portée et surveille-le : si le hub détecte une déconnexion ou une erreur, le programme freine, mais la détection d'une perte de liaison radio et son délai ne sont pas garantis.

Les signaux lumineux ne bloquent pas les commandes du moteur. Le signal d'arrêt est prioritaire et interrompt un SOS en cours. Après chaque signal, les feux reviennent au réglage normal, qui peut être modifié avec `+` ou `−` pendant le signal.

## Réglages

Au début de `train.py`, modifie `SENS_MOTEUR` en `Direction.COUNTERCLOCKWISE` si le train part dans le mauvais sens. Tu peux aussi changer les ports, la puissance maximale, le pas de puissance et la luminosité. Avec plusieurs télécommandes, `NOM_TELECOMMANDE` permet de choisir un nom Bluetooth précis ; `None` sélectionne la première télécommande trouvée. Le nom par défaut est généralement `Handset` ; donne des noms distincts aux télécommandes pour les différencier.

Références : [connexion de la télécommande Pybricks](https://pybricks.com/projects/tutorials/wireless/remote-control/button-basics/) et [documentation de la télécommande](https://docs.pybricks.com/en/stable/pupdevices/remote.html).
