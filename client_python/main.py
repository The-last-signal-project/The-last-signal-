
import sys

from vispy import app

from .game import Game
from .client import Client


def main() -> int:
    client = Client()
    game = None

    try:
        # Game gère lui-même la connexion dans son thread réseau.
        game = Game(client)
        game.show()

        # Boucle événementielle VisPy.
        app.run()

        return 0

    except KeyboardInterrupt:
        print("Interruption du jeu.")
        return 130

    except Exception as exc:
        print(f"Erreur pendant l'exécution du jeu : {exc}")
        raise

    finally:
        print("Arrêt du jeu...")

        if game is not None:
            try:
                game.running = False

                if hasattr(game, "timer"):
                    game.timer.stop()
            except Exception as exc:
                print(f"Erreur pendant l'arrêt du jeu : {exc}")

        try:
            if client.connected:
                client.disconnect("Arrêt normal")
        except Exception as exc:
            print(f"Erreur lors de la déconnexion : {exc}")

        if (
            game is not None
            and hasattr(game, "network_thread")
            and game.network_thread.is_alive()
        ):
            game.network_thread.join(timeout=1.0)


if __name__ == "__main__":
    sys.exit(main())
