import sys

from PySide6.QtWidgets import QApplication

from .game import Game
from .client import Client

def main():
    client= Client()
    client.connect()
    app = QApplication.instance()

    if app is None:
        app = QApplication(sys.argv)

    game = Game(client)
    game.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()