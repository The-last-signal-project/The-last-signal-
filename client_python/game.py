from __future__ import annotations

import queue
import struct
import threading
import uuid

from PySide6.QtCore import QRectF, Qt, QTimer
from PySide6.QtGui import QBrush, QKeyEvent, QPainter, QPen
from PySide6.QtWidgets import QApplication, QMainWindow

from .client import Client
from .packet import PacketType
from .packets.move import MovePacket


class Game(QMainWindow):
    """
    Prototype 2D jouable de The Last Signal.

    Le client 2D est une étape intermédiaire avant la transition
    progressive vers le client 3D.

    Réseau :

        MOVE
            x : i32
            y : i32
            z : i32

        PLAYER_STATE
            player_id : UUID (16 octets)
            x         : i32
            y         : i32
            z         : i32

        PLAYER_REMOVE
            player_id : UUID (16 octets)

    Architecture :

        Thread réseau
              |
              v
        network_queue
              |
              v
        Thread Qt / QTimer
              |
              v
        état du jeu
              |
              v
        rendu Qt
    """

    # =============================================================
    # CONFIGURATION
    # =============================================================

    PLAYER_SIZE = 30
    PLAYER_SPEED = 5

    WORLD_WIDTH = 1000
    WORLD_HEIGHT = 700

    GAME_TIMER_INTERVAL = 16
    NETWORK_TIMER_INTERVAL = 16

    # =============================================================
    # INITIALISATION
    # =============================================================

    def __init__(self, client: Client) -> None:
        super().__init__()

        self.client = client

        self.setWindowTitle(
            "The Last Signal - Prototype 2D"
        )

        self.setFixedSize(
            self.WORLD_WIDTH,
            self.WORLD_HEIGHT,
        )

        # =========================================================
        # ÉTAT DU JOUEUR LOCAL
        # =========================================================

        self.player_x = 100
        self.player_y = 100
        self.player_z = 0

        # =========================================================
        # JOUEURS DISTANTS
        #
        # UUID -> (x, y, z)
        # =========================================================

        self.remote_players: dict[
            uuid.UUID,
            tuple[int, int, int],
        ] = {}

        # =========================================================
        # FILE RÉSEAU
        #
        # Le thread réseau ne modifie jamais directement l'état
        # graphique Qt.
        #
        # Il place uniquement les paquets dans cette file.
        # =========================================================

        self.network_queue: queue.Queue = queue.Queue()

        # =========================================================
        # ÉTAT DES TOUCHES
        # =========================================================

        self.keys: set[int] = set()

        self.setFocusPolicy(
            Qt.StrongFocus
        )

        self.setFocus()

        # =========================================================
        # MURS
        # =========================================================

        self.walls = [
            QRectF(
                250,
                150,
                500,
                30,
            ),
            QRectF(
                250,
                520,
                500,
                30,
            ),
            QRectF(
                250,
                180,
                30,
                340,
            ),
            QRectF(
                720,
                180,
                30,
                340,
            ),
        ]

        # =========================================================
        # ÉTAT DU JEU
        # =========================================================

        self.running = True

        # =========================================================
        # THREAD RÉSEAU
        # =========================================================

        self.network_thread = threading.Thread(
            target=self.network_loop,
            name="GameNetworkThread",
            daemon=True,
        )

        self.network_thread.start()

        # =========================================================
        # TIMER RÉSEAU
        #
        # Le thread Qt récupère les paquets depuis la queue.
        #
        # Cela garantit que les modifications de l'état du jeu
        # restent dans le thread Qt.
        # =========================================================

        self.network_timer = QTimer(self)

        self.network_timer.timeout.connect(
            self.process_network_queue
        )

        self.network_timer.start(
            self.NETWORK_TIMER_INTERVAL
        )

        # =========================================================
        # TIMER DE JEU
        # =========================================================

        self.game_timer = QTimer(self)

        self.game_timer.timeout.connect(
            self.update_game
        )

        self.game_timer.start(
            self.GAME_TIMER_INTERVAL
        )

    # =============================================================
    # RÉSEAU
    # =============================================================

    def network_loop(self) -> None:
        """
        Attend les paquets envoyés par le serveur.

        IMPORTANT :

        Ce thread ne modifie pas directement l'état du jeu Qt.

        Il place simplement les paquets reçus dans network_queue.
        """

        print(
            "[GAME] Thread réseau démarré."
        )

        while self.running:

            if not self.client.connected:
                break

            try:
                packet = self.client.receive_packet()

            except Exception as exc:
                print(
                    "[GAME] Erreur réception réseau :",
                    repr(exc),
                )

                break

            if packet is None:
                continue

            try:
                self.network_queue.put_nowait(
                    packet
                )

            except queue.Full:
                print(
                    "[GAME] File réseau pleine."
                )

        print(
            "[GAME] Thread réseau arrêté."
        )

    # =============================================================
    # TRAITEMENT FILE RÉSEAU
    # =============================================================

    def process_network_queue(self) -> None:
        """
        Traite les paquets reçus par le thread réseau.

        Cette méthode est appelée par QTimer et s'exécute donc
        dans le thread Qt principal.

        Les modifications de l'état du jeu et les appels à update()
        restent ainsi dans le thread graphique.
        """

        processed = 0

        while processed < 100:

            try:
                packet = self.network_queue.get_nowait()

            except queue.Empty:
                break

            try:
                self.handle_packet(packet)

            except Exception as exc:
                print(
                    "[GAME] Erreur traitement paquet :",
                    repr(exc),
                )

            processed += 1

    # =============================================================
    # TRAITEMENT PAQUETS
    # =============================================================

    def handle_packet(self, packet) -> None:
        """
        Traite un paquet reçu du serveur.

        Cette méthode doit être exécutée uniquement dans le thread
        Qt principal.
        """

        packet_type = packet.packet_type

        # ---------------------------------------------------------
        # PLAYER_STATE
        # ---------------------------------------------------------

        if packet_type == PacketType.PLAYER_STATE:

            self.handle_player_state(
                packet.payload
            )

            return

        # ---------------------------------------------------------
        # PLAYER_REMOVE
        # ---------------------------------------------------------

        if packet_type == PacketType.PLAYER_REMOVE:

            self.handle_player_remove(
                packet.payload
            )

            return

    # =============================================================
    # PLAYER STATE
    # =============================================================

    def handle_player_state(
        self,
        payload: bytes,
    ) -> None:
        """
        Traite un PLAYER_STATE.

        Format :

            16 octets : UUID
             4 octets : x
             4 octets : y
             4 octets : z

        Total : 28 octets.
        """

        if len(payload) != 28:

            print(
                "[GAME] PLAYER_STATE invalide : "
                f"{len(payload)} octets "
                "au lieu de 28."
            )

            return

        # ---------------------------------------------------------
        # UUID
        # ---------------------------------------------------------

        try:

            player_id = uuid.UUID(
                bytes=payload[:16]
            )

        except ValueError:

            print(
                "[GAME] UUID PLAYER_STATE invalide."
            )

            return

        # ---------------------------------------------------------
        # POSITION
        # ---------------------------------------------------------

        try:

            x, y, z = struct.unpack(
                "!iii",
                payload[16:28],
            )

        except struct.error:

            print(
                "[GAME] Position PLAYER_STATE invalide."
            )

            return

        # ---------------------------------------------------------
        # JOUEUR LOCAL
        # ---------------------------------------------------------

        local_id = self.get_local_player_id()

        if (
            local_id is not None
            and player_id == local_id
        ):

            self.player_x = x
            self.player_y = y
            self.player_z = z

            self.update()

            return

        # ---------------------------------------------------------
        # JOUEUR DISTANT
        #
        # L'identité repose exclusivement sur l'UUID.
        # ---------------------------------------------------------

        self.remote_players[player_id] = (
            x,
            y,
            z,
        )

        self.update()

    # =============================================================
    # PLAYER REMOVE
    # =============================================================

    def handle_player_remove(
        self,
        payload: bytes,
    ) -> None:
        """
        Traite un PLAYER_REMOVE.

        Format :

            16 octets : UUID
        """

        if len(payload) != 16:

            print(
                "[GAME] PLAYER_REMOVE invalide : "
                f"{len(payload)} octets "
                "au lieu de 16."
            )

            return

        try:

            player_id = uuid.UUID(
                bytes=payload
            )

        except ValueError:

            print(
                "[GAME] UUID PLAYER_REMOVE invalide."
            )

            return

        self.remote_players.pop(
            player_id,
            None,
        )

        self.update()

    # =============================================================
    # UUID LOCAL
    # =============================================================

    def get_local_player_id(
        self,
    ) -> uuid.UUID | None:
        """
        Retourne l'UUID local si Client.session_id
        est renseigné.
        """

        session_id = getattr(
            self.client,
            "session_id",
            None,
        )

        if session_id is None:
            return None

        if isinstance(
            session_id,
            uuid.UUID,
        ):
            return session_id

        try:

            return uuid.UUID(
                str(session_id)
            )

        except (
            ValueError,
            TypeError,
            AttributeError,
        ):

            return None

    # =============================================================
    # BOUCLE DE JEU
    # =============================================================

    def update_game(self) -> None:
        """
        Met à jour le joueur local.

        Le déplacement reste actuellement client-side pour le
        prototype.

        Le protocole conserve x/y/z afin de préparer la future
        transition vers le monde 3D.
        """

        old_x = self.player_x
        old_y = self.player_y
        old_z = self.player_z

        dx = 0
        dy = 0

        # ---------------------------------------------------------
        # HAUT
        # ---------------------------------------------------------

        if (
            Qt.Key_Z in self.keys
            or Qt.Key_W in self.keys
        ):

            dy -= self.PLAYER_SPEED

        # ---------------------------------------------------------
        # BAS
        # ---------------------------------------------------------

        if Qt.Key_S in self.keys:

            dy += self.PLAYER_SPEED

        # ---------------------------------------------------------
        # GAUCHE
        # ---------------------------------------------------------

        if (
            Qt.Key_Q in self.keys
            or Qt.Key_A in self.keys
        ):

            dx -= self.PLAYER_SPEED

        # ---------------------------------------------------------
        # DROITE
        # ---------------------------------------------------------

        if Qt.Key_D in self.keys:

            dx += self.PLAYER_SPEED

        # ---------------------------------------------------------
        # DÉPLACEMENT
        # ---------------------------------------------------------

        if dx != 0 or dy != 0:

            self.move_player(
                dx,
                dy,
            )

        # ---------------------------------------------------------
        # ENVOI AU SERVEUR
        # ---------------------------------------------------------

        if (
            self.player_x != old_x
            or self.player_y != old_y
            or self.player_z != old_z
        ):

            self.send_position_to_server()

        # ---------------------------------------------------------
        # RENDU
        # ---------------------------------------------------------

        self.update()

    # =============================================================
    # DÉPLACEMENT LOCAL
    # =============================================================

    def move_player(
        self,
        dx: int,
        dy: int,
    ) -> None:
        """
        Déplace le joueur local avec limites du monde
        et collisions avec les murs.
        """

        new_x = self.player_x + dx
        new_y = self.player_y + dy

        # ---------------------------------------------------------
        # LIMITES DU MONDE
        # ---------------------------------------------------------

        new_x = max(
            0,
            min(
                new_x,
                self.WORLD_WIDTH - self.PLAYER_SIZE,
            ),
        )

        new_y = max(
            0,
            min(
                new_y,
                self.WORLD_HEIGHT - self.PLAYER_SIZE,
            ),
        )

        player_rect = QRectF(
            new_x,
            new_y,
            self.PLAYER_SIZE,
            self.PLAYER_SIZE,
        )

        # ---------------------------------------------------------
        # COLLISIONS
        # ---------------------------------------------------------

        for wall in self.walls:

            if player_rect.intersects(wall):

                return

        # ---------------------------------------------------------
        # VALIDATION DU DÉPLACEMENT
        # ---------------------------------------------------------

        self.player_x = new_x
        self.player_y = new_y

    # =============================================================
    # ENVOI MOVE
    # =============================================================

    def send_position_to_server(self) -> None:
        """
        Envoie la position actuelle au serveur.
        """

        if not self.client.connected:
            return

        packet = MovePacket(
            int(self.player_x),
            int(self.player_y),
            int(self.player_z),
        )

        try:

            self.client.send_packet(
                packet
            )

        except Exception as exc:

            print(
                "[GAME] Erreur envoi position :",
                repr(exc),
            )

    # =============================================================
    # CLAVIER
    # =============================================================

    def keyPressEvent(
        self,
        event: QKeyEvent,
    ) -> None:
        """
        Enregistre une touche enfoncée.
        """

        if event.isAutoRepeat():
            return

        self.keys.add(
            event.key()
        )

    def keyReleaseEvent(
        self,
        event: QKeyEvent,
    ) -> None:
        """
        Retire une touche lorsqu'elle est relâchée.
        """

        if event.isAutoRepeat():
            return

        self.keys.discard(
            event.key()
        )

    # =============================================================
    # AFFICHAGE
    # =============================================================

    def paintEvent(self, event) -> None:
        """
        Dessine le monde 2D actuel.

        Ce rendu est volontairement simple :
        la 2D sert de prototype avant la transition vers la 3D.
        """

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        # ---------------------------------------------------------
        # FOND
        # ---------------------------------------------------------

        painter.fillRect(
            self.rect(),
            QBrush(Qt.black),
        )

        # ---------------------------------------------------------
        # MURS
        # ---------------------------------------------------------

        painter.setBrush(
            QBrush(Qt.darkGray)
        )

        painter.setPen(
            QPen(
                Qt.gray,
                2,
            )
        )

        for wall in self.walls:

            painter.drawRect(
                wall
            )

        # ---------------------------------------------------------
        # JOUEURS DISTANTS
        #
        # Les joueurs distants sont dessinés avant le joueur local.
        # Cela permet au joueur local de rester clairement visible.
        # ---------------------------------------------------------

        for player_id, position in list(
            self.remote_players.items()
        ):

            x, y, z = position

            self.draw_remote_player(
                painter,
                player_id,
                x,
                y,
            )

        # ---------------------------------------------------------
        # JOUEUR LOCAL
        # ---------------------------------------------------------

        self.draw_local_player(
            painter
        )

        # ---------------------------------------------------------
        # INFORMATIONS DEBUG
        # ---------------------------------------------------------

        self.draw_debug_info(
            painter
        )

        painter.end()

    # =============================================================
    # INFORMATIONS DEBUG
    # =============================================================

    def draw_debug_info(
        self,
        painter: QPainter,
    ) -> None:
        """
        Affiche les informations utiles pendant le développement.
        """

        painter.setPen(
            QPen(Qt.white)
        )

        painter.drawText(
            10,
            20,
            (
                "Joueurs distants : "
                f"{len(self.remote_players)}"
            ),
        )

        local_id = self.get_local_player_id()

        if local_id is None:

            painter.drawText(
                10,
                40,
                "UUID local : inconnu",
            )

        else:

            painter.drawText(
                10,
                40,
                (
                    "UUID local : "
                    f"{str(local_id)[:8]}"
                ),
            )

        painter.drawText(
            10,
            60,
            (
                "Position : "
                f"{self.player_x}, "
                f"{self.player_y}, "
                f"{self.player_z}"
            ),
        )

        painter.drawText(
            10,
            80,
            (
                "Contrôles : "
                "ZQSD / WASD"
            ),
        )

    # =============================================================
    # JOUEUR LOCAL
    # =============================================================

    def draw_local_player(
        self,
        painter: QPainter,
    ) -> None:
        """
        Dessine le joueur local.
        """

        painter.setBrush(
            QBrush(Qt.green)
        )

        painter.setPen(
            QPen(
                Qt.white,
                2,
            )
        )

        painter.drawRect(
            QRectF(
                self.player_x,
                self.player_y,
                self.PLAYER_SIZE,
                self.PLAYER_SIZE,
            )
        )

        painter.setPen(
            QPen(Qt.white)
        )

        painter.drawText(
            int(self.player_x),
            int(self.player_y - 5),
            "MOI",
        )

    # =============================================================
    # JOUEUR DISTANT
    # =============================================================

    def draw_remote_player(
        self,
        painter: QPainter,
        player_id: uuid.UUID,
        x: int,
        y: int,
    ) -> None:
        """
        Dessine un joueur distant.
        """

        same_position = (
            abs(x - self.player_x)
            < self.PLAYER_SIZE
            and
            abs(y - self.player_y)
            < self.PLAYER_SIZE
        )

        # ---------------------------------------------------------
        # JOUEUR SUPERPOSÉ AU JOUEUR LOCAL
        # ---------------------------------------------------------

        if same_position:

            painter.setBrush(
                QBrush(Qt.red)
            )

            painter.setPen(
                QPen(
                    Qt.yellow,
                    4,
                )
            )

            painter.drawEllipse(
                QRectF(
                    x - 8,
                    y - 8,
                    self.PLAYER_SIZE + 16,
                    self.PLAYER_SIZE + 16,
                )
            )

        # ---------------------------------------------------------
        # JOUEUR NORMAL
        # ---------------------------------------------------------

        else:

            painter.setBrush(
                QBrush(Qt.red)
            )

            painter.setPen(
                QPen(
                    Qt.white,
                    2,
                )
            )

            painter.drawRect(
                QRectF(
                    x,
                    y,
                    self.PLAYER_SIZE,
                    self.PLAYER_SIZE,
                )
            )

        # ---------------------------------------------------------
        # IDENTIFIANT
        # ---------------------------------------------------------

        painter.setPen(
            QPen(Qt.white)
        )

        painter.drawText(
            int(x),
            int(y - 5),
            str(player_id)[:8],
        )

    # =============================================================
    # FERMETURE
    # =============================================================

    def closeEvent(
        self,
        event,
    ) -> None:
        """
        Ferme proprement le jeu et arrête les threads/timers.
        """

        self.running = False

        # ---------------------------------------------------------
        # ARRÊT DES TIMERS
        # ---------------------------------------------------------

        self.game_timer.stop()
        self.network_timer.stop()

        # ---------------------------------------------------------
        # VIDAGE DES TOUCHES
        # ---------------------------------------------------------

        self.keys.clear()

        # ---------------------------------------------------------
        # DÉCONNEXION
        # ---------------------------------------------------------

        try:

            self.client.disconnect()

        except Exception as exc:

            print(
                "[GAME] Erreur déconnexion :",
                repr(exc),
            )

        # ---------------------------------------------------------
        # ATTENTE DU THREAD RÉSEAU
        # ---------------------------------------------------------

        if self.network_thread.is_alive():

            self.network_thread.join(
                timeout=1.0
            )

        event.accept()


def run_game(
    client: Client,
) -> None:
    """
    Lance le prototype 2D.
    """

    app = QApplication.instance()

    owns_app = app is None

    if app is None:

        app = QApplication([])

    window = Game(client)

    window.show()

    window.activateWindow()
    window.raise_()
    window.setFocus()

    if owns_app:

        app.exec()