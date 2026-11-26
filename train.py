"""Commande d'un train avec une telecommande LEGO Powered Up.

Pour un City Hub equipe du firmware Pybricks, d'un moteur de train
Powered Up et d'une paire de lumieres Powered Up. Voir le README.
"""

from pybricks.hubs import CityHub
from pybricks.parameters import Button, Color, Direction, Port
from pybricks.pupdevices import DCMotor, Light, Remote
from pybricks.tools import StopWatch, wait
from uerrno import ENODEV


# A adapter au montage. Les valeurs de puissance sont des pourcentages.
PORT_MOTEUR = Port.A
PORT_LUMIERES = Port.B
SENS_MOTEUR = Direction.CLOCKWISE  # COUNTERCLOCKWISE si le train part a l'envers
PUISSANCE_MAX = 100
PAS_PUISSANCE = 10
PAS_LUMINOSITE = 10
NOM_TELECOMMANDE = None  # None : premiere telecommande disponible
INTERVALLE_BOUCLE_MS = 20
INTERVALLE_VERIFICATION_MS = 250
DELAI_CONNEXION_MS = 15000
DUREE_APPUI_MIN_MS = 40
DUREE_APPUI_MAX_MS = 1500

# Valeur lumineuse (None = eteint) et duree en ms. SOS : unite de 200 ms,
# espace d'une unite dans une lettre et de trois unites entre les lettres.
SIGNAL_WARNING = ((None, 200),) + ((100, 300), (None, 300)) * 3
SIGNAL_SOS = ((None, 200),) + (
    (100, 200), (None, 200), (100, 200), (None, 200), (100, 200), (None, 600),
    (100, 600), (None, 200), (100, 600), (None, 200), (100, 600), (None, 600),
    (100, 200), (None, 200), (100, 200), (None, 200), (100, 200), (None, 200),
)


def limiter(valeur, minimum, maximum):
    return max(minimum, min(maximum, valeur))


class ErreurMoteur(Exception):
    pass


class ErreurTelecommande(Exception):
    pass


def moteur_commande(moteur, puissance=None):
    try:
        if puissance is None:
            moteur.brake()
        else:
            moteur.dc(puissance)
    except OSError as erreur:
        print("Erreur du moteur sur", PORT_MOTEUR, ":", erreur)
        raise ErreurMoteur(erreur)


def lumieres_commande(lumieres, luminosite):
    if lumieres is None:
        return None
    try:
        if luminosite is None:
            lumieres.off()
        else:
            lumieres.on(luminosite)
    except OSError as erreur:
        if erreur.args and erreur.args[0] == ENODEV:
            print("Lumieres indisponibles sur", PORT_LUMIERES, ":", erreur)
            print("Le train continue sans lumieres. Rebrancher et relancer le programme.")
            return None
        raise
    return lumieres


def telecommande_appel(operation, *arguments):
    try:
        return operation(*arguments)
    except OSError as erreur:
        raise ErreurTelecommande(erreur)


def attendre_appui(hub):
    """Attend un appui bref ; ignore l'appui ayant lance le programme."""
    hub.light.blink(Color.BLUE, [300, 300])
    print("Pret : appuyer sur le bouton du hub pour connecter.")

    # Ne pas compter un bouton encore maintenu au demarrage ou a l'echec.
    while Button.CENTER in hub.buttons.pressed():
        wait(INTERVALLE_BOUCLE_MS)

    chrono = StopWatch()
    debut_appui = None
    precedent = False

    while True:
        maintenant = chrono.time()
        appuye = Button.CENTER in hub.buttons.pressed()
        if appuye and not precedent:
            debut_appui = maintenant
        elif not appuye and precedent and debut_appui is not None:
            duree = maintenant - debut_appui
            if DUREE_APPUI_MIN_MS <= duree <= DUREE_APPUI_MAX_MS:
                return
            debut_appui = None
        precedent = appuye
        wait(INTERVALLE_BOUCLE_MS)


def conduire(telecommande, hub, moteur, lumieres):
    """Retourne si l'utilisateur arrete le programme, leve OSError si deconnecte."""
    telecommande_appel(telecommande.light.on, Color.GREEN)
    hub.light.on(Color.GREEN)
    print("Telecommande connectee.")

    puissance = 0
    # Etat normal : 0 est eteint. Les signaux ne modifient pas ce reglage.
    luminosite = 0
    dernier_eclairage = None
    signal = None
    etape_signal = 0
    fin_etape = 0
    chrono_signal = StopWatch()
    # Un bouton deja maintenu a la connexion ne provoque aucune action.
    precedent = telecommande_appel(telecommande.buttons.pressed)
    verification = StopWatch()

    while True:
        # name() leve OSError lorsque le firmware constate une deconnexion.
        # Ce controle ne garantit pas un delai de detection d'une perte radio.
        if verification.time() >= INTERVALLE_VERIFICATION_MS:
            telecommande_appel(telecommande.name)
            verification.reset()

        touches = telecommande_appel(telecommande.buttons.pressed)
        nouvelles = touches - precedent
        precedent = touches

        # Le bouton vert termine le programme. Le bouton rouge gauche freine
        # tant qu'il est maintenu, meme si une autre touche est appuyee.
        if Button.CENTER in nouvelles:
            lumieres[0] = lumieres_commande(lumieres[0], luminosite or None)
            return
        if Button.LEFT in touches:
            puissance = 0
            moteur_commande(moteur)
        else:
            changement = (Button.LEFT_PLUS in nouvelles) - (Button.LEFT_MINUS in nouvelles)
            if changement:
                puissance = limiter(
                    puissance + changement * PAS_PUISSANCE,
                    -PUISSANCE_MAX,
                    PUISSANCE_MAX,
                )
                if puissance == 0:
                    moteur_commande(moteur)
                else:
                    moteur_commande(moteur, puissance)

        # Le warning interrompt un SOS et a priorite sur le bouton rouge droit.
        # Une pression maintenue ne redemarre pas la sequence.
        if Button.LEFT in nouvelles:
            signal = SIGNAL_WARNING
            etape_signal = 0
            chrono_signal.reset()
            fin_etape = signal[0][1]
        elif Button.RIGHT in nouvelles and signal is not SIGNAL_WARNING:
            signal = SIGNAL_SOS
            etape_signal = 0
            chrono_signal.reset()
            fin_etape = signal[0][1]

        # + et - modifient l'eclairage normal, meme pendant un signal.
        changement = (Button.RIGHT_PLUS in nouvelles) - (Button.RIGHT_MINUS in nouvelles)
        if changement:
            luminosite = limiter(luminosite + changement * PAS_LUMINOSITE, 0, 100)

        # Aucun wait pendant les clignotements : le frein reste reactif.
        if signal is not None:
            maintenant = chrono_signal.time()
            while signal is not None and maintenant >= fin_etape:
                etape_signal += 1
                if etape_signal == len(signal):
                    signal = None
                else:
                    fin_etape += signal[etape_signal][1]
        eclairage = signal[etape_signal][0] if signal is not None else luminosite or None
        if eclairage != dernier_eclairage:
            lumieres[0] = lumieres_commande(lumieres[0], eclairage)
            dernier_eclairage = eclairage

        wait(INTERVALLE_BOUCLE_MS)


def main():
    hub = CityHub()
    moteur = None
    try:
        try:
            moteur = DCMotor(PORT_MOTEUR, SENS_MOTEUR)
            moteur_commande(moteur)
        except OSError as erreur:
            print("Moteur indisponible sur", PORT_MOTEUR, ":", erreur)
            print("Verifier le branchement du moteur, puis relancer le programme.")
            return

        try:
            lumieres = Light(PORT_LUMIERES)
            lumieres = lumieres_commande(lumieres, None)
        except OSError as erreur:
            if erreur.args and erreur.args[0] == ENODEV:
                print("Lumieres indisponibles sur", PORT_LUMIERES, ":", erreur)
                print("Le train continue sans lumieres. Rebrancher et relancer le programme.")
                lumieres = None
            else:
                print("Erreur d'initialisation des lumieres sur", PORT_LUMIERES, ":", erreur)
                raise

        # Partage l'etat pour garder les lumieres desactivees apres une perte.
        lumieres = [lumieres]

        # Un appui bref lance la recherche. Un appui long eteint toujours le hub.
        hub.system.set_stop_button(None)
        while True:
            attendre_appui(hub)
            hub.light.blink(Color.YELLOW, [200, 200])
            print("Recherche de la telecommande pendant 15 secondes...")
            try:
                telecommande = Remote(name=NOM_TELECOMMANDE, timeout=DELAI_CONNEXION_MS)
            except OSError as erreur:
                print("Telecommande introuvable :", erreur)
            else:
                try:
                    conduire(telecommande, hub, moteur, lumieres)
                    break  # Bouton vert de la telecommande : fin du programme.
                except ErreurTelecommande as erreur:
                    print("Erreur de communication avec la telecommande :", erreur)
                    moteur_commande(moteur)
                    lumieres[0] = lumieres_commande(lumieres[0], None)
            hub.light.on(Color.RED)
            print("Reessayer avec un appui lorsque le voyant clignote en bleu.")
            wait(2000)
    except ErreurMoteur:
        print("Programme arrete. Verifier le moteur et son branchement sur", PORT_MOTEUR)
    finally:
        # Ne pas masquer la cause initiale si le moteur a ete debranche.
        try:
            if moteur is not None:
                try:
                    moteur.brake()
                except OSError as erreur:
                    print("Freinage impossible sur", PORT_MOTEUR, ":", erreur)
        finally:
            try:
                hub.system.set_stop_button(Button.CENTER)
            except OSError as erreur:
                print("Impossible de restaurer le bouton d'arret du hub :", erreur)


main()
