import sys
from .menu import App
from PySide6.QtWidgets import QApplication

from .game import Game
from .client import Client
import argparse
import os


def main():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    client = Client()

    try:
        raison = "Arrêt normal"
        client.connect()
        if args.signal_file:
            with open(args.signal_file, "w", encoding="utf-8") as f:
                f.write("connected")
        
        game = Game(client)
        game.show()

        return app.exec()
    except KeyboardInterrupt:
        print("Nettoyage avant l'arrêt du programme.")
        raison = "Interruption"
    except SystemExit:
        print("Nettoyage avant l'arrêt du programme.")
        raison= "Arrêt normal"
    except Exception as e:
        print(f"il y a une erreur : {e}")
        raison = "crash"
    finally:
        
        print("Le jeu s'arrête....")
        client.disconnect(raison)
    
        


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="solo")
    parser.add_argument("--save")
    parser.add_argument("--signal-file")
    args, _ = parser.parse_known_args()
    sys.exit(main())
