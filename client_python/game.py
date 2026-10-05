
from __future__ import annotations

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
    """

    PLAYER_SIZE = 30
    PLAYER_SPEED = 5

    WORLD_WIDTH = 1000
    WORLD_HEIGHT = 700

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
        # JOUEUR LOCAL
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
        # CLAVIER
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
        # RÉSEAU
        # =========================================================

        self.running = True

        self.network_thread = threading.Thread(
            target=self.network_loop,
            daemon=True,
        )

        self.network_thread.start()

        # =========================================================
        # TIMER DE JEU
        # =========================================================

        self.game_timer = QTimer(self)

        self.game_timer.timeout.connect(
            self.update_game
        )

        self.game_timer.start(16)

    # =============================================================
    # RÉSEAU
    # =============================================================

    def network_loop(self) -> None:
        """
        Attend les paquets envoyés par le serveur.
        """

        print("[GAME] Thread réseau démarré.")

        while self.running and self.client.connected:

            packet = self.client.receive_packet()

            if packet is None:
                continue

            try:
                self.handle_packet(packet)

            except Exception as exc:
                print(
                    "[GAME] Erreur traitement paquet :",
                    repr(exc),
                )

        print("[GAME] Thread réseau arrêté.")

    def handle_packet(self, packet) -> None:
        """
        Traite les paquets reçus du serveur.
        """

        print(
            "[GAME] Paquet reçu :",
            packet.packet_type,
        )

        # ---------------------------------------------------------
        # PLAYER_STATE
        # ---------------------------------------------------------

        if packet.packet_type == PacketType.PLAYER_STATE:

            self.handle_player_state(
                packet.payload
            )

            return

        # ---------------------------------------------------------
        # PLAYER_REMOVE
        # ---------------------------------------------------------

        if packet.packet_type == PacketType.PLAYER_REMOVE:

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
        PLAYER_STATE :

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

        player_id = uuid.UUID(
            bytes=payload[:16]
        )

        # ---------------------------------------------------------
        # Position
        # ---------------------------------------------------------

        x, y, z = struct.unpack(
            "!iii",
            payload[16:28],
        )

        print(
            "[GAME] PLAYER_STATE :",
            player_id,
            "=>",
            (x, y, z),
        )

        # ---------------------------------------------------------
        # Si on connaît notre UUID, on peut identifier le joueur
        # local.
        # ---------------------------------------------------------

        local_id = self.get_local_player_id()

        if (
            local_id is not None
            and player_id == local_id
        ):

            self.player_x = x
            self.player_y = y
            self.player_z = z

            return

        # ---------------------------------------------------------
        # Sinon, on conserve le joueur comme joueur distant.
        #
        # IMPORTANT :
        # On ne fait aucune comparaison de position.
        # L'UUID est l'identité du joueur.
        # ---------------------------------------------------------

        self.remote_players[player_id] = (
            x,
            y,
            z,
        )

        print(
            "[GAME] Joueurs distants :",
            len(self.remote_players),
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
        PLAYER_REMOVE :

            16 octets : UUID
        """

        if len(payload) != 16:

            print(
                "[GAME] PLAYER_REMOVE invalide : "
                f"{len(payload)} octets "
                "au lieu de 16."
            )

            return

        player_id = uuid.UUID(
            bytes=payload
        )

        print(
            "[GAME] PLAYER_REMOVE :",
            player_id,
        )

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

        self.update()

    # =============================================================
    # DÉPLACEMENT LOCAL
    # =============================================================

    def move_player(
        self,
        dx: int,
        dy: int,
    ) -> None:

        new_x = self.player_x + dx
        new_y = self.player_y + dy

        # ---------------------------------------------------------
        # LIMITES
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

        self.player_x = new_x
        self.player_y = new_y

    # =============================================================
    # ENVOI MOVE
    # =============================================================

    def send_position_to_server(self) -> None:

        packet = MovePacket(
            int(self.player_x),
            int(self.player_y),
            int(self.player_z),
        )

        self.client.send_packet(
            packet
        )

    # =============================================================
    # CLAVIER
    # =============================================================

    def keyPressEvent(
        self,
        event: QKeyEvent,
    ) -> None:

        if event.isAutoRepeat():
            return

        self.keys.add(
            event.key()
        )

    def keyReleaseEvent(
        self,
        event: QKeyEvent,
    ) -> None:

        if event.isAutoRepeat():
            return

        self.keys.discard(
            event.key()
        )

    # =============================================================
    # AFFICHAGE
    # =============================================================

    def paintEvent(self, event) -> None:

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
            painter.drawRect(wall)

        # ---------------------------------------------------------
        # JOUEUR LOCAL
        # ---------------------------------------------------------

        self.draw_local_player(
            painter
        )

        # ---------------------------------------------------------
        # JOUEURS DISTANTS
        #
        # On les dessine APRÈS le joueur local.
        #
        # Ainsi, si deux joueurs sont exactement à la même
        # position, le joueur distant reste visible.
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
        # INFORMATIONS DEBUG
        # ---------------------------------------------------------

        painter.setPen(
            QPen(Qt.white)
        )

        painter.drawText(
            10,
            20,
            f"Joueurs distants : "
            f"{len(self.remote_players)}",
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
                f"UUID local : "
                f"{str(local_id)[:8]}",
            )

        painter.end()

    # =============================================================
    # JOUEUR LOCAL
    # =============================================================

    def draw_local_player(
        self,
        painter: QPainter,
    ) -> None:

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

        # ---------------------------------------------------------
        # Si le joueur distant est exactement sous le joueur local,
        # on dessine un contour beaucoup plus grand pour qu'il
        # reste visible.
        # ---------------------------------------------------------

        same_position = (
            abs(x - self.player_x) < self.PLAYER_SIZE
            and abs(y - self.player_y) < self.PLAYER_SIZE
        )

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
        # UUID
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

    def closeEvent(self, event) -> None:

        self.running = False

        self.game_timer.stop()

        try:
            self.client.disconnect()

        except Exception:
            pass

        if self.network_thread.is_alive():

            self.network_thread.join(
                timeout=1.0
            )

        event.accept()


def run_game(client: Client) -> None:
    """
    Lance le jeu.
    """

    app = QApplication.instance()

    owns_app = app is None

    if app is None:
        app = QApplication([])

    window = Game(client)

    window.show()

    if owns_app:
        app.exec()
