import sys

from PySide6.QtWidgets import QApplication

from .game import Game


def main():
    app = QApplication.instance()

    if app is None:
        app = QApplication(sys.argv)

    game = Game()
    game.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()