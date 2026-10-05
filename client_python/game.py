import sys
import threading
import time

from PySide6.QtCore import QTimer, Qt, QRectF
from PySide6.QtGui import QColor, QKeyEvent, QPainter, QPen
from PySide6.QtWidgets import QApplication, QMainWindow

from .client import Client
from .packets.move import MovePacket


class Game(QMainWindow):
    """
    Client graphique de The Last Signal.

    Architecture :

        CLIENT PYTHON
             |
             | MovePacket
             v
        SERVEUR RUST
             |
             | position validée
             v
        CLIENT PYTHON

    Le client n'est pas l'autorité du monde.
    """

    WIDTH = 900
    HEIGHT = 600

    PLAYER_SIZE = 30

    # Vitesse locale utilisée pour construire les demandes
    # de déplacement.
    PLAYER_SPEED = 5

    # Coordonnées réseau.
    #
    # Le protocole actuel utilise trois entiers :
    #
    #     x, y, z
    #
    # Le client graphique utilise x/y comme coordonnées de
    # déplacement et z comme hauteur.
    START_X = WIDTH // 2
    START_Y = HEIGHT // 2
    START_Z = 0

    SERVER_HOST = "127.0.0.1"
    SERVER_PORT = 5000

    NETWORK_UPDATE_INTERVAL = 50

    def __init__(self):
        super().__init__()

        self.app = QApplication.instance()

        if self.app is None:
            self.app = QApplication(sys.argv)

        self.setWindowTitle(
            "The Last Signal - Multiplayer"
        )

        self.setFixedSize(
            self.WIDTH,
            self.HEIGHT,
        )

        self.setFocusPolicy(
            Qt.FocusPolicy.StrongFocus
        )

        # =========================================================
        # RESEAU
        # =========================================================

        self.client = Client(
            host=self.SERVER_HOST,
            port=self.SERVER_PORT,
        )

        self.network_connected = False
        self.network_error = None

        self.network_thread = None
        self.network_running = False

        # Les paquets reçus sont stockés ici afin que le thread
        # réseau ne modifie jamais directement l'interface Qt.
        self.received_packets = []

        self.received_packets_lock = (
            threading.Lock()
        )

        # =========================================================
        # JOUEUR LOCAL
        # =========================================================

        self.player = QRectF(
            self.START_X - self.PLAYER_SIZE / 2,
            self.START_Y - self.PLAYER_SIZE / 2,
            self.PLAYER_SIZE,
            self.PLAYER_SIZE,
        )

        self.server_position = (
            self.START_X,
            self.START_Y,
            self.START_Z,
        )

        self.last_sent_position = None

        # =========================================================
        # JOUEURS DISTANTS
        # =========================================================

        # Cette structure est volontairement prête pour le futur
        # système de synchronisation serveur.
        #
        # Exemple futur :
        #
        # remote_players[player_id] = {
        #     "x": ...,
        #     "y": ...,
        #     "z": ...,
        #     "name": ...
        # }
        #
        # Le serveur actuel ne fournit cependant pas encore
        # d'identifiant de joueur dans MovePacket.
        self.remote_players = {}

        # =========================================================
        # TOUCHES
        # =========================================================

        self.keys = set()

        # =========================================================
        # MONDE VISUEL
        # =========================================================

        self.walls = [
            QRectF(
                100,
                100,
                250,
                30,
            ),
            QRectF(
                100,
                100,
                30,
                200,
            ),
            QRectF(
                350,
                100,
                30,
                200,
            ),
            QRectF(
                450,
                200,
                250,
                30,
            ),
            QRectF(
                700,
                200,
                30,
                220,
            ),
            QRectF(
                250,
                400,
                300,
                30,
            ),
        ]

        # =========================================================
        # ETAT
        # =========================================================

        self.game_started = False
        self.connection_failed = False

        self.message = (
            "Connexion au serveur..."
        )

        self.last_network_update = (
            time.monotonic()
        )

        # =========================================================
        # TIMER PRINCIPAL
        # =========================================================

        self.timer = QTimer(self)

        self.timer.timeout.connect(
            self.update_game
        )

        self.timer.start(16)

        # =========================================================
        # TIMER RESEAU
        # =========================================================

        self.network_timer = QTimer(self)

        self.network_timer.timeout.connect(
            self.process_network_packets
        )

        self.network_timer.start(
            self.NETWORK_UPDATE_INTERVAL
        )

        # =========================================================
        # CONNEXION
        # =========================================================

        self.connect_to_server()

        self.setFocus()

    # =============================================================
    # RESEAU
    # =============================================================

    def connect_to_server(self):
        """
        Connecte le client au serveur Rust.

        La connexion est effectuée dans un thread afin de ne pas
        bloquer l'interface Qt.
        """

        self.message = (
            f"Connexion à "
            f"{self.SERVER_HOST}:{self.SERVER_PORT}..."
        )

        self.network_running = True

        self.network_thread = threading.Thread(
            target=self.network_worker,
            daemon=True,
        )

        self.network_thread.start()

    def network_worker(self):
        """
        Thread réseau.

        Il est responsable de la réception des paquets.
        """

        try:
            self.client.connect()

            self.network_connected = True
            self.connection_failed = False

            self.enqueue_message(
                "Connecté au serveur."
            )

            while self.network_running:

                packet = (
                    self.client.receive_packet()
                )

                if packet is None:
                    if self.network_running:
                        self.enqueue_message(
                            "Connexion au serveur perdue."
                        )

                    break

                self.enqueue_packet(
                    packet
                )

        except Exception as error:
            self.network_connected = False
            self.connection_failed = True

            self.enqueue_message(
                f"Erreur réseau : {error}"
            )

        finally:
            self.network_connected = False

    def enqueue_packet(self, packet):
        """
        Ajoute un paquet reçu à la file consommée par Qt.
        """

        with self.received_packets_lock:
            self.received_packets.append(
                packet
            )

    def enqueue_message(self, message):
        """
        Ajoute un message réseau à la file.
        """

        with self.received_packets_lock:
            self.received_packets.append(
                ("__MESSAGE__", message)
            )

    def process_network_packets(self):
        """
        Traite les paquets reçus sans toucher à l'interface depuis
        le thread réseau.
        """

        packets = []

        with self.received_packets_lock:

            if self.received_packets:
                packets = list(
                    self.received_packets
                )

                self.received_packets.clear()

        for packet in packets:

            if (
                isinstance(packet, tuple)
                and len(packet) == 2
                and packet[0] == "__MESSAGE__"
            ):
                self.message = packet[1]
                continue

            self.handle_network_packet(
                packet
            )

    def handle_network_packet(self, packet):
        """
        Traite un paquet reçu du serveur.
        """

        if isinstance(packet, MovePacket):

            self.handle_move_packet(
                packet
            )

            return

        self.message = (
            f"Paquet reçu : "
            f"{packet.packet_type.name}"
        )

    def handle_move_packet(self, packet):
        """
        Traite la réponse MOVE actuelle du serveur.

        Le protocole actuel du dépôt fait :

            client -> MOVE(x,y,z)
            serveur -> MOVE(x,y,z)

        Nous considérons donc cette position comme la position
        validée par le serveur.

        Lorsque le serveur sera modifié pour broadcaster les
        positions de plusieurs joueurs, cette méthode pourra
        alimenter remote_players.
        """

        x = int(packet.x)
        y = int(packet.y)
        z = int(packet.z)

        self.server_position = (
            x,
            y,
            z,
        )

        # Le protocole actuel ne possède pas encore d'identifiant
        # de joueur dans MovePacket.
        #
        # Nous ne pouvons donc pas savoir si le paquet correspond
        # à un autre joueur.
        #
        # Pour l'instant il représente la confirmation du joueur
        # local.
        self.apply_server_position(
            x,
            y,
            z,
        )

        self.game_started = True

    def apply_server_position(
        self,
        x,
        y,
        z,
    ):
        """
        Applique une position fournie par le serveur.

        IMPORTANT :

        Le serveur reste l'autorité.
        """

        x = max(
            self.PLAYER_SIZE / 2,
            min(
                self.WIDTH
                - self.PLAYER_SIZE / 2,
                x,
            ),
        )

        y = max(
            self.PLAYER_SIZE / 2,
            min(
                self.HEIGHT
                - self.PLAYER_SIZE / 2,
                y,
            ),
        )

        new_player = QRectF(
            x - self.PLAYER_SIZE / 2,
            y - self.PLAYER_SIZE / 2,
            self.PLAYER_SIZE,
            self.PLAYER_SIZE,
        )

        if self.can_move_to(
            new_player
        ):
            self.player = new_player

    # =============================================================
    # ENVOI DEPLACEMENT
    # =============================================================

    def send_position_to_server(self):
        """
        Envoie la position demandée au serveur.

        Le format actuel du protocole est :

            !iii

        donc trois entiers signés 32 bits.
        """

        if not self.network_connected:
            return

        center = self.player.center()

        x = int(
            round(center.x())
        )

        y = int(
            round(center.y())
        )

        z = int(
            self.START_Z
        )

        position = (
            x,
            y,
            z,
        )

        # Evite de spammer le serveur avec exactement la même
        # position.
        if position == self.last_sent_position:
            return

        try:
            packet = MovePacket(
                x,
                y,
                z,
            )

            self.client.send_packet(
                packet
            )

            self.last_sent_position = (
                position
            )

        except Exception as error:
            self.message = (
                f"Erreur d'envoi : {error}"
            )

    # =============================================================
    # BOUCLE DE JEU
    # =============================================================

    def update_game(self):
        """
        Boucle principale du client.

        Le client calcule une demande de mouvement puis l'envoie
        au serveur.

        La position définitive est ensuite reçue du serveur.
        """

        if not self.network_connected:
            self.update()
            return

        if self.connection_failed:
            self.update()
            return

        self.move_player_request()

        self.send_position_to_server()

        self.update()

    # =============================================================
    # DEPLACEMENT
    # =============================================================

    def move_player_request(self):
        """
        Construit une demande de déplacement.

        Cette fonction ne doit pas être considérée comme une
        modification autoritaire du monde.

        Le serveur devra ultérieurement valider la position.
        """

        dx = 0
        dy = 0

        if (
            Qt.Key.Key_Z in self.keys
            or Qt.Key.Key_W in self.keys
        ):
            dy -= self.PLAYER_SPEED

        if Qt.Key.Key_S in self.keys:
            dy += self.PLAYER_SPEED

        if (
            Qt.Key.Key_Q in self.keys
            or Qt.Key.Key_A in self.keys
        ):
            dx -= self.PLAYER_SPEED

        if Qt.Key.Key_D in self.keys:
            dx += self.PLAYER_SPEED

        if dx == 0 and dy == 0:
            return

        # Normalisation diagonale.
        if dx != 0 and dy != 0:
            factor = 0.70710678

            dx *= factor
            dy *= factor

        requested_player = QRectF(
            self.player
        )

        requested_player.translate(
            dx,
            dy,
        )

        if not self.can_move_to(
            requested_player
        ):
            return

        self.player = requested_player

    def can_move_to(
        self,
        rectangle,
    ):
        """
        Collision locale utilisée uniquement pour éviter de
        produire des demandes manifestement impossibles.

        Le serveur devra également vérifier les collisions.
        """

        if rectangle.left() < 0:
            return False

        if rectangle.right() > self.WIDTH:
            return False

        if rectangle.top() < 0:
            return False

        if rectangle.bottom() > self.HEIGHT:
            return False

        for wall in self.walls:

            if rectangle.intersects(
                wall
            ):
                return False

        return True

    # =============================================================
    # JOUEURS DISTANTS
    # =============================================================

    def update_remote_player(
        self,
        player_id,
        x,
        y,
        z=0,
        name="Joueur",
    ):
        """
        Ajoute ou met à jour un joueur distant.

        Cette méthode n'est pas encore appelée par le protocole
        actuel, car MovePacket ne contient pas de player_id.

        Elle constitue l'interface utilisée lorsque le serveur
        commencera à envoyer les états des autres joueurs.
        """

        self.remote_players[
            player_id
        ] = {
            "x": float(x),
            "y": float(y),
            "z": float(z),
            "name": str(name),
        }

    def remove_remote_player(
        self,
        player_id,
    ):
        """
        Supprime un joueur distant.
        """

        self.remote_players.pop(
            player_id,
            None,
        )

    # =============================================================
    # CLAVIER
    # =============================================================

    def keyPressEvent(
        self,
        event: QKeyEvent,
    ):
        if event.isAutoRepeat():
            return

        key = event.key()

        # Echap
        if key == Qt.Key.Key_Escape:
            self.close()
            return

        self.keys.add(
            key
        )

    def keyReleaseEvent(
        self,
        event: QKeyEvent,
    ):
        if event.isAutoRepeat():
            return

        self.keys.discard(
            event.key()
        )

    # =============================================================
    # FERMETURE
    # =============================================================

    def closeEvent(self, event):
        """
        Arrêt propre du thread réseau.
        """

        self.network_running = False

        try:
            self.client.disconnect()
        except Exception:
            pass

        if (
            self.network_thread is not None
            and self.network_thread.is_alive()
        ):
            self.network_thread.join(
                timeout=1.0
            )

        event.accept()

    # =============================================================
    # RENDU
    # =============================================================

    def paintEvent(self, event):
        painter = QPainter(
            self
        )

        # =========================================================
        # FOND
        # =========================================================

        painter.fillRect(
            self.rect(),
            QColor(
                40,
                55,
                45,
            ),
        )

        # =========================================================
        # GRILLE
        # =========================================================

        painter.setPen(
            QColor(
                55,
                70,
                60,
            )
        )

        grid_size = 50

        for x in range(
            0,
            self.WIDTH,
            grid_size,
        ):
            painter.drawLine(
                x,
                0,
                x,
                self.HEIGHT,
            )

        for y in range(
            0,
            self.HEIGHT,
            grid_size,
        ):
            painter.drawLine(
                0,
                y,
                self.WIDTH,
                y,
            )

        # =========================================================
        # MURS
        # =========================================================

        painter.setPen(
            Qt.PenStyle.NoPen
        )

        painter.setBrush(
            QColor(
                80,
                80,
                80,
            )
        )

        for wall in self.walls:

            painter.drawRect(
                wall
            )

        # =========================================================
        # JOUEURS DISTANTS
        # =========================================================

        for player_id, remote in (
            self.remote_players.items()
        ):
            self.draw_remote_player(
                painter,
                player_id,
                remote,
            )

        # =========================================================
        # JOUEUR LOCAL
        # =========================================================

        painter.setBrush(
            QColor(
                220,
                220,
                220,
            )
        )

        painter.setPen(
            QPen(
                QColor(
                    255,
                    255,
                    255,
                ),
                2,
            )
        )

        painter.drawRect(
            self.player
        )

        # =========================================================
        # TITRE
        # =========================================================

        painter.setPen(
            QColor(
                255,
                255,
                255,
            )
        )

        painter.drawText(
            20,
            30,
            "The Last Signal - Multiplayer",
        )

        painter.drawText(
            20,
            55,
            "ZQSD / WASD : déplacer"
            "   |   Échap : quitter",
        )

        # =========================================================
        # ETAT RESEAU
        # =========================================================

        if self.network_connected:

            network_text = (
                "SERVEUR : CONNECTÉ"
            )

            network_color = QColor(
                100,
                220,
                120,
            )

        else:

            network_text = (
                "SERVEUR : DÉCONNECTÉ"
            )

            network_color = QColor(
                220,
                100,
                100,
            )

        painter.setPen(
            network_color
        )

        painter.drawText(
            self.WIDTH - 230,
            30,
            network_text,
        )

        # =========================================================
        # POSITION
        # =========================================================

        center = self.player.center()

        painter.setPen(
            QColor(
                255,
                255,
                255,
            )
        )

        painter.drawText(
            self.WIDTH - 230,
            55,
            (
                f"Position : "
                f"{int(center.x())}, "
                f"{int(center.y())}"
            ),
        )

        # =========================================================
        # JOUEURS
        # =========================================================

        painter.drawText(
            self.WIDTH - 230,
            80,
            (
                f"Joueurs distants : "
                f"{len(self.remote_players)}"
            ),
        )

        # =========================================================
        # MESSAGE
        # =========================================================

        painter.drawText(
            20,
            self.HEIGHT - 20,
            self.message,
        )

        painter.end()

    # =============================================================
    # RENDU JOUEUR DISTANT
    # =============================================================

    def draw_remote_player(
        self,
        painter,
        player_id,
        player,
    ):
        """
        Dessine un joueur distant.

        Le serveur fournira plus tard les informations permettant
        de remplir remote_players.
        """

        x = float(
            player["x"]
        )

        y = float(
            player["y"]
        )

        rect = QRectF(
            x - self.PLAYER_SIZE / 2,
            y - self.PLAYER_SIZE / 2,
            self.PLAYER_SIZE,
            self.PLAYER_SIZE,
        )

        painter.setBrush(
            QColor(
                80,
                160,
                255,
            )
        )

        painter.setPen(
            QPen(
                QColor(
                    120,
                    200,
                    255,
                ),
                2,
            )
        )

        painter.drawRect(
            rect
        )

        # Nom du joueur
        painter.setPen(
            QColor(
                255,
                255,
                255,
            )
        )

        painter.drawText(
            int(x - 30),
            int(y - 22),
            str(
                player.get(
                    "name",
                    player_id,
                )
            ),
        )

    # =============================================================
    # LANCEMENT
    # =============================================================

    def run(self):
        self.show()

        self.setFocus()

        self.app.exec()


