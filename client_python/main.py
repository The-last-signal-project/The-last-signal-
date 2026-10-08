import sys

from vispy import app

from .game import Game
from .client import Client


client = None
raison = "Arrêt normal"


def main():
    global client

    client = Client()

    # Création de la fenêtre AVANT la connexion réseau.
    game = Game(client)
    game.show()

    # Connexion au serveur après création de la fenêtre.
    try:
        client.connect()
    except Exception as e:
        print(f"Connexion au serveur impossible : {e}")
        print("La fenêtre 3D reste ouverte pour permettre le débogage.")

    # Boucle événementielle VisPy.
    app.run()


if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        print("Nettoyage avant l'arrêt du programme.")
        raison = "Interruption"

    except SystemExit:
        print("Nettoyage avant l'arrêt du programme.")
        raison = "Arrêt normal"

    except Exception as e:
        print(f"Il y a une erreur : {e}")
        raison = "crash"

    finally:
        print("Le jeu s'arrête....")

        if client is not None:
            try:
                client.disconnect(raison)
            except Exception as e:
                print(f"Erreur lors de la déconnexion : {e}")
