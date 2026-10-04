import sys

from PySide6.QtCore import QTimer, Qt, QRectF
from PySide6.QtGui import QColor, QKeyEvent, QPainter
from PySide6.QtWidgets import QApplication, QMainWindow


class Game(QMainWindow):
    """Premier prototype jouable de The Last Signal."""

    WIDTH = 900
    HEIGHT = 600

    PLAYER_SIZE = 30
    PLAYER_SPEED = 5

    def __init__(self):
        # QApplication doit exister avant la création de QMainWindow.
        self.app = QApplication.instance()

        if self.app is None:
            self.app = QApplication(sys.argv)

        super().__init__()

        self.setWindowTitle("The Last Signal - Prototype")
        self.setFixedSize(self.WIDTH, self.HEIGHT)

        # ---------------------------------------------------------
        # Joueur
        # ---------------------------------------------------------

        self.player = QRectF(
            self.WIDTH / 2 - self.PLAYER_SIZE / 2,
            self.HEIGHT / 2 - self.PLAYER_SIZE / 2,
            self.PLAYER_SIZE,
            self.PLAYER_SIZE,
        )

        # ---------------------------------------------------------
        # Touches actuellement enfoncées
        # ---------------------------------------------------------

        self.keys = set()

        # ---------------------------------------------------------
        # Murs de la carte
        # ---------------------------------------------------------

        self.walls = [
            QRectF(100, 100, 250, 30),
            QRectF(100, 100, 30, 200),
            QRectF(350, 100, 30, 200),
            QRectF(450, 200, 250, 30),
            QRectF(700, 200, 30, 220),
            QRectF(250, 400, 300, 30),
        ]

        # ---------------------------------------------------------
        # Objets ramassables
        # ---------------------------------------------------------

        self.items = [
            {
                "name": "Cristal",
                "rect": QRectF(150, 350, 24, 24),
            },
            {
                "name": "Ressource",
                "rect": QRectF(600, 120, 24, 24),
            },
            {
                "name": "Objet inconnu",
                "rect": QRectF(780, 480, 24, 24),
            },
        ]

        # ---------------------------------------------------------
        # Inventaire
        # ---------------------------------------------------------

        self.inventory = []

        # ---------------------------------------------------------
        # Message affiché à l'écran
        # ---------------------------------------------------------

        self.message = "Explorez la zone..."

        # ---------------------------------------------------------
        # Boucle de jeu
        # ---------------------------------------------------------

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_game)
        self.timer.start(16)  # environ 60 FPS

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()

    # =============================================================
    # BOUCLE DE JEU
    # =============================================================

    def update_game(self):
        self.move_player()
        self.check_items()
        self.update()

    # =============================================================
    # DEPLACEMENT
    # =============================================================

    def move_player(self):
        dx = 0
        dy = 0

        # ZQSD
        if Qt.Key.Key_Z in self.keys or Qt.Key.Key_W in self.keys:
            dy -= self.PLAYER_SPEED

        if Qt.Key.Key_S in self.keys:
            dy += self.PLAYER_SPEED

        if Qt.Key.Key_Q in self.keys or Qt.Key.Key_A in self.keys:
            dx -= self.PLAYER_SPEED

        if Qt.Key.Key_D in self.keys:
            dx += self.PLAYER_SPEED

        # ---------------------------------------------------------
        # Déplacement horizontal
        # ---------------------------------------------------------

        if dx != 0:
            new_player = QRectF(self.player)
            new_player.translate(dx, 0)

            if self.can_move_to(new_player):
                self.player = new_player

        # ---------------------------------------------------------
        # Déplacement vertical
        # ---------------------------------------------------------

        if dy != 0:
            new_player = QRectF(self.player)
            new_player.translate(0, dy)

            if self.can_move_to(new_player):
                self.player = new_player

    # =============================================================
    # COLLISIONS
    # =============================================================

    def can_move_to(self, rectangle):
        # Empêche le joueur de sortir de la carte.

        if rectangle.left() < 0:
            return False

        if rectangle.right() > self.WIDTH:
            return False

        if rectangle.top() < 0:
            return False

        if rectangle.bottom() > self.HEIGHT:
            return False

        # Collision avec les murs.

        for wall in self.walls:
            if rectangle.intersects(wall):
                return False

        return True

    # =============================================================
    # OBJETS
    # =============================================================

    def check_items(self):
        collected = []

        for item in self.items:
            if self.player.intersects(item["rect"]):
                collected.append(item)

        for item in collected:
            self.items.remove(item)
            self.inventory.append(item["name"])

            self.message = f"Objet récupéré : {item['name']}"

    # =============================================================
    # CLAVIER
    # =============================================================

    def keyPressEvent(self, event: QKeyEvent):
        if event.isAutoRepeat():
            return

        self.keys.add(event.key())

        # Touche I = inventaire
        if event.key() == Qt.Key.Key_I:
            self.show_inventory()

    def keyReleaseEvent(self, event: QKeyEvent):
        if event.isAutoRepeat():
            return

        self.keys.discard(event.key())

    # =============================================================
    # INVENTAIRE
    # =============================================================

    def show_inventory(self):
        if not self.inventory:
            self.message = "Inventaire vide."
            return

        self.message = (
            "Inventaire : "
            + ", ".join(self.inventory)
        )

    # =============================================================
    # RENDU
    # =============================================================

    def paintEvent(self, event):
        painter = QPainter(self)

        # ---------------------------------------------------------
        # Fond
        # ---------------------------------------------------------

        painter.fillRect(
            self.rect(),
            QColor(25, 25, 25),
        )

        # ---------------------------------------------------------
        # Sol
        # ---------------------------------------------------------

        painter.fillRect(
            0,
            0,
            self.WIDTH,
            self.HEIGHT,
            QColor(40, 55, 45),
        )

        # ---------------------------------------------------------
        # Grille
        # ---------------------------------------------------------

        painter.setPen(QColor(55, 70, 60))

        grid_size = 50

        for x in range(0, self.WIDTH, grid_size):
            painter.drawLine(
                x,
                0,
                x,
                self.HEIGHT,
            )

        for y in range(0, self.HEIGHT, grid_size):
            painter.drawLine(
                0,
                y,
                self.WIDTH,
                y,
            )

        # ---------------------------------------------------------
        # Murs
        # ---------------------------------------------------------

        painter.setBrush(QColor(80, 80, 80))
        painter.setPen(Qt.PenStyle.NoPen)

        for wall in self.walls:
            painter.drawRect(wall)

        # ---------------------------------------------------------
        # Objets
        # ---------------------------------------------------------

        painter.setBrush(QColor(80, 180, 255))

        for item in self.items:
            painter.drawEllipse(item["rect"])

        # ---------------------------------------------------------
        # Joueur
        # ---------------------------------------------------------

        painter.setBrush(QColor(220, 220, 220))

        painter.drawRect(self.player)

        # ---------------------------------------------------------
        # Interface
        # ---------------------------------------------------------

        painter.setPen(QColor(255, 255, 255))

        painter.drawText(
            20,
            30,
            "The Last Signal - Prototype",
        )

        painter.drawText(
            20,
            55,
            "Déplacement : ZQSD / WASD    |    I : inventaire",
        )

        painter.drawText(
            20,
            self.HEIGHT - 20,
            self.message,
        )

        painter.drawText(
            self.WIDTH - 180,
            30,
            f"Objets : {len(self.inventory)}",
        )

        painter.end()

    # =============================================================
    # LANCEMENT
    # =============================================================

    def run(self):
        self.show()
        self.setFocus()
        self.app.exec()
