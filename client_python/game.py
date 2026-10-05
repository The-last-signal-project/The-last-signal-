import json
import sys
import time
from pathlib import Path

from PySide6.QtCore import QTimer, Qt, QRectF
from PySide6.QtGui import QColor, QKeyEvent, QPainter, QPen
from PySide6.QtWidgets import QApplication, QMainWindow


class Game(QMainWindow):
    """Prototype jouable de The Last Signal."""

    WIDTH = 900
    HEIGHT = 600

    PLAYER_SIZE = 30
    PLAYER_SPEED = 5
    PLAYER_MAX_HP = 100

    ENEMY_SIZE = 34
    ENEMY_MAX_HP = 50
    ENEMY_SPEED = 1.5
    ENEMY_DAMAGE = 10

    ENEMY_DETECTION_RANGE = 350
    ENEMY_ATTACK_RANGE = 42
    ENEMY_ATTACK_COOLDOWN = 700

    ATTACK_DAMAGE = 25
    ATTACK_RANGE = 65
    ATTACK_COOLDOWN = 350

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

        self.player_hp = self.PLAYER_MAX_HP

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
        # OBJETS DE LA CARTE
        # =========================================================

        self.base_items = [
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

        self.items = self.copy_items(self.base_items)

        # =========================================================
        # INVENTAIRE
        # =========================================================

        self.inventory = {}

        # =========================================================
        # ENNEMI
        # =========================================================

        self.enemy_start_rect = QRectF(
            650,
            400,
            self.ENEMY_SIZE,
            self.ENEMY_SIZE,
        )

        self.enemy = self.create_enemy()

        # Permet d'éviter de créer plusieurs fois le même loot.
        self.enemy_loot_spawned = False

        # =========================================================
        # COMBAT
        # =========================================================

        self.last_attack_time = 0.0
        self.last_enemy_attack_time = 0.0

        # =========================================================
        # ETAT DU JEU
        # =========================================================

        self.inventory_open = False
        self.game_over = False

        self.message = "Explorez la zone."

        # =========================================================
        # BOUCLE DE JEU
        # =========================================================

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_game)
        self.timer.start(16)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()

    # =============================================================
    # CREATION / COPIE DES DONNEES
    # =============================================================

    @staticmethod
    def copy_items(items):
        """Copie les objets sans partager les QRectF."""

        return [
            {
                "id": item["id"],
                "name": item["name"],
                "rect": QRectF(item["rect"]),
            }
            for item in items
        ]

    def create_enemy(self):
        return {
            "id": "enemy_1",
            "name": "Mutant",
            "rect": QRectF(self.enemy_start_rect),
            "hp": self.ENEMY_MAX_HP,
            "alive": True,
        }

    # =============================================================
    # BOUCLE DE JEU
    # =============================================================

    def update_game(self):
        if self.game_over:
            self.update()
            return

        if not self.inventory_open:
            self.move_player()
            self.check_items()
            self.update_enemy()
            self.check_enemy_damage()

        self.update()

    # =============================================================
    # JOUEUR
    # =============================================================

    def move_player(self):
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

        if dx != 0:
            new_player = QRectF(self.player)
            new_player.translate(dx, 0)

            if self.can_move_to(new_player):
                self.player = new_player

        if dy != 0:
            new_player = QRectF(self.player)
            new_player.translate(0, dy)

            if self.can_move_to(new_player):
                self.player = new_player

    def can_move_to(self, rectangle):
        if rectangle.left() < 0:
            return False

        if rectangle.right() > self.WIDTH:
            return False

        if rectangle.top() < 0:
            return False

        if rectangle.bottom() > self.HEIGHT:
            return False

        for wall in self.walls:
            if rectangle.intersects(wall):
                return False

        return True

    # =============================================================
    # OBJETS / RAMASSAGE
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
    # ENNEMI
    # =============================================================

    def distance_player_enemy(self):
        if not self.enemy["alive"]:
            return float("inf")

        player_center = self.player.center()
        enemy_center = self.enemy["rect"].center()

        dx = player_center.x() - enemy_center.x()
        dy = player_center.y() - enemy_center.y()

        return (dx * dx + dy * dy) ** 0.5

    def update_enemy(self):
        if not self.enemy["alive"]:
            return

        distance = self.distance_player_enemy()

        if distance > self.ENEMY_DETECTION_RANGE:
            return

        enemy_rect = self.enemy["rect"]

        dx = self.player.center().x() - enemy_rect.center().x()
        dy = self.player.center().y() - enemy_rect.center().y()

        # Normalisation pour éviter que la diagonale soit plus rapide.
        length = (dx * dx + dy * dy) ** 0.5

        if length == 0:
            return

        dx = dx / length * self.ENEMY_SPEED
        dy = dy / length * self.ENEMY_SPEED

        # Déplacement horizontal.
        new_enemy = QRectF(enemy_rect)
        new_enemy.translate(dx, 0)

        if self.can_enemy_move_to(new_enemy):
            self.enemy["rect"] = new_enemy

        # Déplacement vertical.
        enemy_rect = self.enemy["rect"]
        new_enemy = QRectF(enemy_rect)
        new_enemy.translate(0, dy)

        if self.can_enemy_move_to(new_enemy):
            self.enemy["rect"] = new_enemy

    def can_enemy_move_to(self, rectangle):
        if rectangle.left() < 0:
            return False

        if rectangle.right() > self.WIDTH:
            return False

        if rectangle.top() < 0:
            return False

        if rectangle.bottom() > self.HEIGHT:
            return False

        for wall in self.walls:
            if rectangle.intersects(wall):
                return False

        return True

    # =============================================================
    # ATTAQUE DU JOUEUR
    # =============================================================

    def attack(self):
        if self.game_over or self.inventory_open:
            return

        if not self.enemy["alive"]:
            self.message = "Il n'y a plus d'ennemi."
            return

        now = time.monotonic() * 1000

        if now - self.last_attack_time < self.ATTACK_COOLDOWN:
            return

        self.last_attack_time = now

        distance = self.distance_player_enemy()

        if distance > self.ATTACK_RANGE:
            self.message = "L'ennemi est trop loin."
            return

        self.enemy["hp"] -= self.ATTACK_DAMAGE

        if self.enemy["hp"] <= 0:
            self.enemy["hp"] = 0
            self.enemy["alive"] = False
            self.spawn_enemy_loot()
            self.message = "Mutant vaincu ! Loot disponible."
            return

        self.message = (
            f"Attaque ! Mutant : "
            f"{self.enemy['hp']}/{self.ENEMY_MAX_HP} PV"
        )

    # =============================================================
    # DEGATS DE L'ENNEMI
    # =============================================================

    def check_enemy_damage(self):
        if not self.enemy["alive"]:
            return

        if not self.player.intersects(self.enemy["rect"]):
            return

        now = time.monotonic() * 1000

        if (
            now - self.last_enemy_attack_time
            < self.ENEMY_ATTACK_COOLDOWN
        ):
            return

        self.last_enemy_attack_time = now

        self.player_hp -= self.ENEMY_DAMAGE

        if self.player_hp <= 0:
            self.player_hp = 0
            self.game_over = True
            self.keys.clear()
            self.message = "Vous êtes tombé au combat."
        else:
            self.message = (
                f"Vous avez subi {self.ENEMY_DAMAGE} dégâts ! "
                f"PV : {self.player_hp}/{self.PLAYER_MAX_HP}"
            )

    # =============================================================
    # LOOT
    # =============================================================

    def spawn_enemy_loot(self):
        if self.enemy_loot_spawned:
            return

        enemy_rect = self.enemy["rect"]

        loot_rect = QRectF(
            enemy_rect.center().x() - 12,
            enemy_rect.center().y() - 12,
            24,
            24,
        )

        self.items.append(
            {
                "id": "mutant_loot",
                "name": "Loot de mutant",
                "rect": loot_rect,
            }
        )

        self.enemy_loot_spawned = True

    # =============================================================
    # CLAVIER
    # =============================================================

    def keyPressEvent(self, event: QKeyEvent):
        if event.isAutoRepeat():
            return

        key = event.key()

        # ---------------------------------------------------------
        # GAME OVER
        # ---------------------------------------------------------

        if self.game_over:
            if key == Qt.Key.Key_R:
                self.restart_game()

            return

        # ---------------------------------------------------------
        # INVENTAIRE
        # ---------------------------------------------------------

        if key == Qt.Key.Key_I:
            self.inventory_open = not self.inventory_open
            self.keys.clear()

            if self.inventory_open:
                self.message = "Inventaire ouvert."
            else:
                self.message = "Inventaire fermé."

            self.update()
            return

        # ---------------------------------------------------------
        # SAUVEGARDE
        # ---------------------------------------------------------

        if key == Qt.Key.Key_F5:
            self.save_game()
            return

        # ---------------------------------------------------------
        # CHARGEMENT
        # ---------------------------------------------------------

        if key == Qt.Key.Key_F9:
            self.load_game()
            return

        # ---------------------------------------------------------
        # ATTAQUE
        # ---------------------------------------------------------

        if key == Qt.Key.Key_Space:
            self.attack()
            return

        # ---------------------------------------------------------
        # DEPLACEMENT
        # ---------------------------------------------------------

        if self.inventory_open:
            return

        self.keys.add(key)

    def keyReleaseEvent(self, event: QKeyEvent):
        if event.isAutoRepeat():
            return

        self.keys.discard(event.key())

    # =============================================================
    # RECOMMENCER
    # =============================================================

    def restart_game(self):
        self.player = QRectF(
            self.WIDTH / 2 - self.PLAYER_SIZE / 2,
            self.HEIGHT / 2 - self.PLAYER_SIZE / 2,
            self.PLAYER_SIZE,
            self.PLAYER_SIZE,
        )

        self.player_hp = self.PLAYER_MAX_HP

        self.items = self.copy_items(self.base_items)

        self.inventory = {}

        self.enemy = self.create_enemy()
        self.enemy_loot_spawned = False

        self.last_attack_time = 0.0
        self.last_enemy_attack_time = 0.0

        self.inventory_open = False
        self.game_over = False
        self.message = "Nouvelle partie."

        self.keys.clear()

    # =============================================================
    # SAUVEGARDE
    # =============================================================

    def save_game(self):
        try:
            data = {
                "player": {
                    "x": self.player.x(),
                    "y": self.player.y(),
                    "hp": self.player_hp,
                },
                "inventory": self.inventory,
                "items": [
                    {
                        "id": item["id"],
                        "name": item["name"],
                        "x": item["rect"].x(),
                        "y": item["rect"].y(),
                    }
                    for item in self.items
                ],
                "enemy": {
                    "x": self.enemy["rect"].x(),
                    "y": self.enemy["rect"].y(),
                    "hp": self.enemy["hp"],
                    "alive": self.enemy["alive"],
                },
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
            # JOUEUR
            # -----------------------------------------------------

            player_data = data.get("player", {})

            player_x = float(
                player_data.get("x", self.player.x())
            )

            player_y = float(
                player_data.get("y", self.player.y())
            )

            loaded_player = QRectF(
                player_x,
                player_y,
                self.PLAYER_SIZE,
                self.PLAYER_SIZE,
            )

            if self.can_move_to(loaded_player):
                self.player = loaded_player

            self.player_hp = max(
                0,
                min(
                    int(
                        player_data.get(
                            "hp",
                            self.PLAYER_MAX_HP,
                        )
                    ),
                    self.PLAYER_MAX_HP,
                ),
            )

            # -----------------------------------------------------
            # INVENTAIRE
            # -----------------------------------------------------

            loaded_inventory = data.get(
                "inventory",
                {},
            )

            if isinstance(loaded_inventory, dict):
                self.inventory = {
                    str(name): max(
                        0,
                        int(quantity),
                    )
                    for name, quantity
                    in loaded_inventory.items()
                }

            # -----------------------------------------------------
            # OBJETS
            # -----------------------------------------------------

            loaded_items = data.get("items", [])

            if isinstance(loaded_items, list):
                restored_items = []

                for item in loaded_items:
                    try:
                        restored_items.append(
                            {
                                "id": str(item["id"]),
                                "name": str(item["name"]),
                                "rect": QRectF(
                                    float(item["x"]),
                                    float(item["y"]),
                                    24,
                                    24,
                                ),
                            }
                        )
                    except (
                        KeyError,
                        TypeError,
                        ValueError,
                    ):
                        continue

                self.items = restored_items

            # -----------------------------------------------------
            # ENNEMI
            # -----------------------------------------------------

            enemy_data = data.get("enemy", {})

            enemy_x = float(
                enemy_data.get(
                    "x",
                    self.enemy_start_rect.x(),
                )
            )

            enemy_y = float(
                enemy_data.get(
                    "y",
                    self.enemy_start_rect.y(),
                )
            )

            enemy_hp = max(
                0,
                min(
                    int(
                        enemy_data.get(
                            "hp",
                            self.ENEMY_MAX_HP,
                        )
                    ),
                    self.ENEMY_MAX_HP,
                ),
            )

            enemy_alive = bool(
                enemy_data.get(
                    "alive",
                    enemy_hp > 0,
                )
            )

            self.enemy["rect"] = QRectF(
                enemy_x,
                enemy_y,
                self.ENEMY_SIZE,
                self.ENEMY_SIZE,
            )

            self.enemy["hp"] = enemy_hp
            self.enemy["alive"] = (
                enemy_alive and enemy_hp > 0
            )

            self.enemy_loot_spawned = any(
                item["id"] == "mutant_loot"
                for item in self.items
            ) or not self.enemy["alive"]

            # -----------------------------------------------------
            # ETAT
            # -----------------------------------------------------

            self.game_over = self.player_hp <= 0
            self.inventory_open = False
            self.keys.clear()

            if self.game_over:
                self.message = "Vous êtes tombé au combat."
            elif not self.enemy["alive"]:
                self.message = "Partie chargée. Mutant vaincu."
            else:
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

        painter.setPen(
            QColor(55, 70, 60)
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
            QColor(80, 80, 80)
        )

        for wall in self.walls:
            painter.drawRect(wall)

        # =========================================================
        # OBJETS
        # =========================================================

        for item in self.items:
            if item["id"] == "mutant_loot":
                painter.setBrush(
                    QColor(255, 200, 70)
                )
            else:
                painter.setBrush(
                    QColor(80, 180, 255)
                )

            painter.drawEllipse(
                item["rect"]
            )

        # =========================================================
        # ENNEMI
        # =========================================================

        if self.enemy["alive"]:
            painter.setBrush(
                QColor(190, 70, 70)
            )

            painter.drawRect(
                self.enemy["rect"]
            )

            # Barre de vie
            enemy_x = int(
                self.enemy["rect"].x()
            )

            enemy_y = int(
                self.enemy["rect"].y() - 12
            )

            enemy_width = self.ENEMY_SIZE

            painter.setBrush(
                QColor(50, 50, 50)
            )

            painter.drawRect(
                enemy_x,
                enemy_y,
                enemy_width,
                6,
            )

            hp_width = int(
                enemy_width
                * self.enemy["hp"]
                / self.ENEMY_MAX_HP
            )

            painter.setBrush(
                QColor(220, 80, 80)
            )

            painter.drawRect(
                enemy_x,
                enemy_y,
                hp_width,
                6,
            )

        # =========================================================
        # JOUEUR
        # =========================================================

        painter.setBrush(
            QColor(220, 220, 220)
        )

        painter.drawRect(
            self.player
        )

        # =========================================================
        # TITRE / COMMANDES
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
            "   |   ESPACE : attaquer"
            "   |   I : inventaire",
        )

        painter.drawText(
            20,
            78,
            "F5 : sauvegarder"
            "   |   F9 : charger"
            "   |   R : recommencer après une défaite",
        )

        # =========================================================
        # BARRE DE VIE
        # =========================================================

        hp_bar_x = 20
        hp_bar_y = 100
        hp_bar_width = 200
        hp_bar_height = 18

        painter.setBrush(
            QColor(60, 60, 60)
        )

        painter.drawRect(
            hp_bar_x,
            hp_bar_y,
            hp_bar_width,
            hp_bar_height,
        )

        player_hp_width = int(
            hp_bar_width
            * self.player_hp
            / self.PLAYER_MAX_HP
        )

        painter.setBrush(
            QColor(80, 200, 100)
        )

        painter.drawRect(
            hp_bar_x,
            hp_bar_y,
            player_hp_width,
            hp_bar_height,
        )

        painter.setPen(
            QColor(255, 255, 255)
        )

        painter.drawText(
            hp_bar_x + 8,
            hp_bar_y + 14,
            f"PV : {self.player_hp}/{self.PLAYER_MAX_HP}",
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
        # MESSAGE
        # =========================================================

        painter.drawText(
            20,
            self.HEIGHT - 20,
            self.message,
        )

        # =========================================================
        # INVENTAIRE
        # =========================================================

        if self.inventory_open:
            self.draw_inventory(
                painter
            )

        # =========================================================
        # GAME OVER
        # =========================================================

        if self.game_over:
            self.draw_game_over(
                painter
            )

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

        painter.setPen(
            QColor(255, 255, 255)
        )

        painter.drawText(
            int(panel_x + 25),
            int(panel_y + 40),
            "INVENTAIRE",
        )

        painter.drawLine(
            int(panel_x + 20),
            int(panel_y + 55),
            int(panel_x + panel_width - 20),
            int(panel_y + 55),
        )

        if not self.inventory:
            painter.drawText(
                int(panel_x + 25),
                int(panel_y + 100),
                "Inventaire vide.",
            )
        else:
            y = panel_y + 90

            for name, quantity in self.inventory.items():
                painter.drawText(
                    int(panel_x + 30),
                    int(y),
                    f"{name} × {quantity}",
                )

                y += 35

        painter.setPen(
            QColor(180, 180, 180)
        )

        painter.drawText(
            int(panel_x + 25),
            int(panel_y + panel_height - 25),
            "I : fermer",
        )

    # =============================================================
    # GAME OVER
    # =============================================================

    def draw_game_over(self, painter):
        panel_width = 500
        panel_height = 250

        panel_x = (
            self.WIDTH - panel_width
        ) / 2

        panel_y = (
            self.HEIGHT - panel_height
        ) / 2

        painter.setBrush(
            QColor(10, 10, 10, 235)
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

        painter.setPen(
            QColor(255, 255, 255)
        )

        painter.drawText(
            int(panel_x + 160),
            int(panel_y + 70),
            "VOUS ÊTES TOMBE",
        )

        painter.drawText(
            int(panel_x + 105),
            int(panel_y + 130),
            "R : recommencer",
        )

        painter.drawText(
            int(panel_x + 105),
            int(panel_y + 165),
            "F5 : sauvegarder",
        )

    # =============================================================
    # LANCEMENT
    # =============================================================

    def run(self):
        self.show()
        self.setFocus()
        self.app.exec()

