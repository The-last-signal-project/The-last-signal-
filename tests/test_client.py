from client_python.client import Client
from client_python.packet import PacketType
from client_python.packets.chat import ChatPacket
from client_python.packets.login import LoginPacket
from client_python.packets.ping import PingPacket
from client_python.packets.move import MovePacket
from client_python.packets.singup import SingupPacket
import sys
import atexit
import random
import secrets
import string
def generate_random_password(min_length=1, max_length=101):
    characters = string.ascii_letters + string.digits + string.punctuation
    length = random.randint(min_length, max_length)

    return ''.join(
        secrets.choice(characters)
        for _ in range(length)
    )
def main():
    client = Client()
    def on_exit():
        client.disconnect()
    atexit.register(on_exit)
    client.connect()
    while True:
        
        
        a = random.choice(["Chat", "Login", "Ping", "Move","Singup"])
        message = [
                    "Le serveur est en rust",
                    "Le client est en python",
                    "Momo dirige le jeu"
                  ]
        personne = [
                    "Admin",
                    "Dev",
                    "Momo",
                    "Modo"
                  ]
        password = generate_random_password()
        email = f'{random.choice(personne)}@gmail.com'
        
        if a == "Chat":
            client.send_packet(ChatPacket(random.choice(message)))
            print("chat")
        elif a == "Login":
            client.send_packet(LoginPacket(email, password))
            print("login")
        elif a == "Singup":
            client.send_packet(SingupPacket(email, password))
            print("singup")
        elif a == "Ping":
            client.send_packet(PingPacket())
            print("ping")
        elif a == "Move":
            client.send_packet(MovePacket(random.randint(0,8096),random.randint(0,8096),random.randint(0,100)))
            print("move")
        client.receive_packet()

        

    
    
from security import vault
import pytest

def test_main():
    
    with pytest.raises(SystemExit) as exc:
        try:
            main()
        except KeyboardInterrupt:
            print("arrêt du programme.")
        except SystemExit:
            print("arrêt du programme.")
        except Exception as e:
            print(f"il y a une erreur : {e}")
        finally:
            print("Le jeu s'arrête....")
            sys.exit(0)

    assert exc.value.code == 0
    
def test_key():
    key1 = vault.get_or_create_communication_key()
    print(len(key1))
    key2 = vault.get_or_create_communication_key()
    print(key1 == key2)
