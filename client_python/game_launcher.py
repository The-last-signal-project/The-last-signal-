import sys
import json
from .menu import App
from PySide6.QtWidgets import QApplication

from .game import Game
from .client import Client
from .auth_session import AuthError, authenticate_client, spawn
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
        pending = []
        if args.auth_stdin:
            # Le menu transmet les identifiants et le compte choisi (une ligne JSON sur l'entree standard)
            creds = json.loads(sys.stdin.readline())
            pending = authenticate_client(client, creds["email"], creds["password"],
                                          creds["account_id"])
        if args.signal_file:
            with open(args.signal_file, "w", encoding="utf-8") as f:
                f.write("connected")
        
        game = Game(client)
        # paquets (snapshot des joueurs) lus pendant l'authentification : le jeu doit aussi les traiter
        for packet in pending:
            game.network_queue.put_nowait(packet)
        if args.auth_stdin:
            spawn(client)      # le joueur entre dans le monde maintenant, pas a la connexion TCP
        game.show()

        return app.exec()
    except AuthError as e:
        # Connexion ou compte refuse : pas de signal, le menu le voit et rouvre sa session.
        print(f"Authentification impossible : {e.key}")
        try:
            client.socket.close()
        except Exception:
            pass
        os._exit(2)
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
    parser.add_argument("--auth-stdin", action="store_true")
    args, _ = parser.parse_known_args()
    sys.exit(main())
