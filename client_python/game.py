import json
import sys
from pathlib import Path

from PySide6.QtCore import QTimer, Qt, QRectF
from PySide6.QtGui import QColor, QKeyEvent, QPainter, QPen
from PySide6.QtWidgets import QApplication, QMainWindow


class Game(QMainWindow):
    """Premier prototype jouable de The Last Signal."""

    WIDTH = 900
    HEIGHT = 600

    PLAYER_SIZE = 30
    PLAYER_SPEED = 5

    # Le fichier de sauvegarde est placé dans client_python/.
    SAVE_FILE = Path(__file__).resolve().parent / "save.json"

    def __init__(self):
        self.app = QApplication.instance()

        if self.app is None:
            self.app = QApplication(sys.argv)

        super().__init__()

        self.setWindowTitle("The Last Signal - Prototype")
        self.setFixedSize(self.WIDTH, self.HEIGHT)

        # =========================================================
        # JOUEUR
        # =========================================================

        self.player = QRectF(
            self.WIDTH / 2 - self.PLAYER_SIZE / 2,
            self.HEIGHT / 2 - self.PLAYER_SIZE / 2,
            self.PLAYER_SIZE,
            self.PLAYER_SIZE,
        )

        # =========================================================
        # TOUCHES
        # =========================================================

        self.keys = set()

        # =========================================================
        # MURS
        # =========================================================

        self.walls = [
            QRectF(100, 100, 250, 30),
            QRectF(100, 100, 30, 200),
            QRectF(350, 100, 30, 200),
            QRectF(450, 200, 250, 30),
            QRectF(700, 200, 30, 220),
            QRectF(250, 400, 300, 30),
        ]

        # =========================================================
        # OBJETS
        # =========================================================

        self.items = [
            {
                "id": "cristal",
                "name": "Cristal",
                "rect": QRectF(150, 350, 24, 24),
            },
            {
                "id": "ressource",
                "name": "Ressource",
                "rect": QRectF(600, 120, 24, 24),
            },
            {
                "id": "objet_inconnu",
                "name": "Objet inconnu",
                "rect": QRectF(780, 480, 24, 24),
            },
        ]

        # =========================================================
        # INVENTAIRE
        # =========================================================

        self.inventory = {}

        # =========================================================
        # INTERFACE
        # =========================================================

        self.inventory_open = False
        self.message = "Explorez la zone."

        # =========================================================
        # BOUCLE DE JEU
        # =========================================================

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_game)
        self.timer.start(16)  # environ 60 FPS

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()

    # =============================================================
    # BOUCLE DE JEU
    # =============================================================

    def update_game(self):
        if not self.inventory_open:
            self.move_player()
            self.check_items()

        self.update()

    # =============================================================
    # DEPLACEMENT
    # =============================================================

    def move_player(self):
        dx = 0
        dy = 0

        # Haut : Z ou W
        if (
            Qt.Key.Key_Z in self.keys
            or Qt.Key.Key_W in self.keys
        ):
            dy -= self.PLAYER_SPEED

        # Bas : S
        if Qt.Key.Key_S in self.keys:
            dy += self.PLAYER_SPEED

        # Gauche : Q ou A
        if (
            Qt.Key.Key_Q in self.keys
            or Qt.Key.Key_A in self.keys
        ):
            dx -= self.PLAYER_SPEED

        # Droite : D
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
        # Empêcher le joueur de sortir de la carte.

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
    # RAMASSAGE
    # =============================================================

    def check_items(self):
        collected_items = []

        for item in self.items:
            if self.player.intersects(item["rect"]):
                collected_items.append(item)

        for item in collected_items:
            self.items.remove(item)

            name = item["name"]

            self.inventory[name] = (
                self.inventory.get(name, 0) + 1
            )

            self.message = f"{name} récupéré !"

    # =============================================================
    # CLAVIER
    # =============================================================

    def keyPressEvent(self, event: QKeyEvent):
        if event.isAutoRepeat():
            return

        key = event.key()

        # ---------------------------------------------------------
        # Inventaire
        # ---------------------------------------------------------

        if key == Qt.Key.Key_I:
            self.inventory_open = not self.inventory_open

            if self.inventory_open:
                self.message = "Inventaire ouvert."
            else:
                self.message = "Inventaire fermé."

            self.update()
            return

        # ---------------------------------------------------------
        # Sauvegarde
        # ---------------------------------------------------------

        if key == Qt.Key.Key_F5:
            self.save_game()
            return

        # ---------------------------------------------------------
        # Chargement
        # ---------------------------------------------------------

        if key == Qt.Key.Key_F9:
            self.load_game()
            return

        # ---------------------------------------------------------
        # Pendant l'inventaire, pas de déplacement
        # ---------------------------------------------------------

        if self.inventory_open:
            return

        self.keys.add(key)

    def keyReleaseEvent(self, event: QKeyEvent):
        if event.isAutoRepeat():
            return

        self.keys.discard(event.key())

    # =============================================================
    # SAUVEGARDE
    # =============================================================

    def save_game(self):
        try:
            data = {
                "player": {
                    "x": self.player.x(),
                    "y": self.player.y(),
                },
                "inventory": self.inventory,
                "remaining_items": [
                    item["id"]
                    for item in self.items
                ],
            }

            with self.SAVE_FILE.open(
                "w",
                encoding="utf-8",
            ) as file:
                json.dump(
                    data,
                    file,
                    indent=4,
                    ensure_ascii=False,
                )

            self.message = "Partie sauvegardée."

        except OSError as error:
            self.message = (
                f"Erreur de sauvegarde : {error}"
            )

    # =============================================================
    # CHARGEMENT
    # =============================================================

    def load_game(self):
        if not self.SAVE_FILE.exists():
            self.message = "Aucune sauvegarde trouvée."
            return

        try:
            with self.SAVE_FILE.open(
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(file)

            # -----------------------------------------------------
            # Position du joueur
            # -----------------------------------------------------

            player_data = data.get("player", {})

            x = float(
                player_data.get(
                    "x",
                    self.player.x(),
                )
            )

            y = float(
                player_data.get(
                    "y",
                    self.player.y(),
                )
            )

            loaded_player = QRectF(
                x,
                y,
                self.PLAYER_SIZE,
                self.PLAYER_SIZE,
            )

            if self.can_move_to(loaded_player):
                self.player = loaded_player
            else:
                self.message = (
                    "Position sauvegardée invalide."
                )

            # -----------------------------------------------------
            # Inventaire
            # -----------------------------------------------------

            loaded_inventory = data.get(
                "inventory",
                {},
            )

            if isinstance(loaded_inventory, dict):
                self.inventory = {
                    str(name): int(quantity)
                    for name, quantity
                    in loaded_inventory.items()
                }

            # -----------------------------------------------------
            # Objets encore présents
            # -----------------------------------------------------

            remaining_ids = set(
                data.get(
                    "remaining_items",
                    [],
                )
            )

            all_items = [
                {
                    "id": "cristal",
                    "name": "Cristal",
                    "rect": QRectF(
                        150,
                        350,
                        24,
                        24,
                    ),
                },
                {
                    "id": "ressource",
                    "name": "Ressource",
                    "rect": QRectF(
                        600,
                        120,
                        24,
                        24,
                    ),
                },
                {
                    "id": "objet_inconnu",
                    "name": "Objet inconnu",
                    "rect": QRectF(
                        780,
                        480,
                        24,
                        24,
                    ),
                },
            ]

            self.items = [
                item
                for item in all_items
                if item["id"] in remaining_ids
            ]

            self.message = "Partie chargée."

        except (
            OSError,
            json.JSONDecodeError,
            TypeError,
            ValueError,
        ) as error:
            self.message = (
                f"Erreur de chargement : {error}"
            )

    # =============================================================
    # RENDU
    # =============================================================

    def paintEvent(self, event):
        painter = QPainter(self)

        # =========================================================
        # FOND
        # =========================================================

        painter.fillRect(
            self.rect(),
            QColor(40, 55, 45),
        )

        # =========================================================
        # GRILLE
        # =========================================================

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

        # =========================================================
        # MURS
        # =========================================================

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(80, 80, 80))

        for wall in self.walls:
            painter.drawRect(wall)

        # =========================================================
        # OBJETS
        # =========================================================

        painter.setBrush(QColor(80, 180, 255))

        for item in self.items:
            painter.drawEllipse(item["rect"])

        # =========================================================
        # JOUEUR
        # =========================================================

        painter.setBrush(QColor(220, 220, 220))
        painter.drawRect(self.player)

        # =========================================================
        # INTERFACE
        # =========================================================

        painter.setPen(
            QPen(QColor(255, 255, 255))
        )

        painter.drawText(
            20,
            30,
            "The Last Signal - Prototype",
        )

        painter.drawText(
            20,
            55,
            "ZQSD / WASD : déplacer"
            "   |   I : inventaire"
            "   |   F5 : sauvegarder"
            "   |   F9 : charger",
        )

        painter.drawText(
            20,
            self.HEIGHT - 20,
            self.message,
        )

        # =========================================================
        # COMPTEUR
        # =========================================================

        total_items = sum(
            self.inventory.values()
        )

        painter.drawText(
            self.WIDTH - 180,
            30,
            f"Objets : {total_items}",
        )

        # =========================================================
        # INVENTAIRE
        # =========================================================

        if self.inventory_open:
            self.draw_inventory(painter)

        painter.end()

    # =============================================================
    # INVENTAIRE
    # =============================================================

    def draw_inventory(self, painter):
        panel_width = 500
        panel_height = 400

        panel_x = (
            self.WIDTH - panel_width
        ) / 2

        panel_y = (
            self.HEIGHT - panel_height
        ) / 2

        # ---------------------------------------------------------
        # Panneau
        # ---------------------------------------------------------

        painter.setBrush(
            QColor(20, 20, 20, 240)
        )

        painter.setPen(
            QPen(
                QColor(180, 180, 180),
                2,
            )
        )

        painter.drawRect(
            int(panel_x),
            int(panel_y),
            panel_width,
            panel_height,
        )

        # ---------------------------------------------------------
        # Titre
        # ---------------------------------------------------------

        painter.setPen(
            QColor(255, 255, 255)
        )

        painter.drawText(
            int(panel_x + 25),
            int(panel_y + 40),
            "INVENTAIRE",
        )

        # ---------------------------------------------------------
        # Séparation
        # ---------------------------------------------------------

        painter.drawLine(
            int(panel_x + 20),
            int(panel_y + 55),
            int(panel_x + panel_width - 20),
            int(panel_y + 55),
        )

        # ---------------------------------------------------------
        # Inventaire vide
        # ---------------------------------------------------------

        if not self.inventory:
            painter.drawText(
                int(panel_x + 25),
                int(panel_y + 100),
                "Inventaire vide.",
            )

        # ---------------------------------------------------------
        # Objets
        # ---------------------------------------------------------

        else:
            y = panel_y + 90

            for name, quantity in self.inventory.items():
                painter.drawText(
                    int(panel_x + 30),
                    int(y),
                    f"{name} × {quantity}",
                )

                y += 35

        # ---------------------------------------------------------
        # Instruction
        # ---------------------------------------------------------

        painter.setPen(
            QColor(180, 180, 180)
        )

        painter.drawText(
            int(panel_x + 25),
            int(panel_y + panel_height - 25),
            "I : fermer    |    F5 : sauvegarder",
        )

    # =============================================================
    # LANCEMENT
    # =============================================================

    def run(self):
        self.show()
        self.setFocus()
        self.app.exec()

