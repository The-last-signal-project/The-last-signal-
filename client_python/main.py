import sys

from PySide6.QtWidgets import QApplication

from .game import Game
from .client import Client
client = None
raison = "Arrêt normal"

def main():
    global raison, client
    
        
    
    client= Client()
    client.connect()
    app = QApplication.instance()

    if app is None:
        app = QApplication(sys.argv)

    game = Game(client)
    game.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    try:
        main()
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

        sys.exit(0)