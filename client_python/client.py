import socket
import time
import traceback
from .packet import Packet,PacketType
from .packets.Deco import decoPacket
from .logs import log
import time
class Client:
    """
    Client réseau de The Last Signal.
    """
    

    def __init__(
        self,
        host="127.0.0.1",
        port=5000,
    ):
        """
        Initialisation du Client réseau de The Last Signal.
        """

        self.host = host
        self.port = port
        self.session_id = None

        self.socket = None

        self.connected = False
    
    def connect(self):
        """
        Connexion du client
        """
        if self.connected:
            print(self.connected)
            return
        timeout = 90
        interval = 0.5
        start_time = time.monotonic()
        while True:
            elapsed = time.monotonic() - start_time
            if elapsed >= timeout:
                self.connected = False
                raise SystemExit(1)
            self.socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )
            self.socket.settimeout(1)
            try:
                print(
                       f"[CLIENT] Tentative TCP vers "
                       f"{self.host}:{self.port}"
                       )

                self.socket.connect(
                     (self.host, self.port)
            )
                print(
                        f"[CLIENT] TCP connecté à "
                        f"{self.host}:{self.port}"
                         )

                self.connected = True
                packet = self.receive_packet()
                if packet.packet_type == PacketType.SESSION:
                    
                    self.session_id = packet.session_id
                    print(self.session_id)
                
                self.socket.settimeout(None)

                log(
                      self,
                      "INFO",
                      "Connexion au serveur réussie."
                    )
                return
                
            except (ConnectionRefusedError, socket.timeout):
                self.socket.close()
                self.socket = None
                time.sleep(interval)
            except Exception:
                self.socket.close()
                self.socket = None
                self.connected = False
                raise
    
    def send_packet(self, packet):
        """Envoi d'un packet par le client"""

        if not self.connected:
        
            return

        try:

            self.socket.sendall(
                packet.encode()
            ) 

        except Exception:

            log(self,"ERROR",
                f"Erreur d'envoi : {traceback.format_exc()}"
            )
    
    def receive_packet(self):
        """Réception d'un packet par le client"""
        if not self.connected:
            
            return None
        try:
            while self.connected:
                header = self._recv_exact(4)
                if header is None:
                    return None
                size = int.from_bytes(
                            header,
                            "big"
                            )
                data = self._recv_exact(size)
                if data is None:
                    return None
                packet = Packet.decode(data)
                if packet.packet_type == packet.packet_type.BAN:
                    raise SystemExit(1)
                    
                return packet
                
        except Exception:
            log(
                     self,
                     "ERROR",
                      f"Erreur de réception : "
                      f"{traceback.format_exc()}"
                     )
            return None
        return None
    
    def _recv_exact(self, size):
        """
        Fonction auxilliaire de réception d'un packet par le client 
        qui vérifie la taille exacte du packet
        """

        if not self.connected:
            return None

        data = bytearray()

        try:

            while len(data) < size:

                chunk = self.socket.recv(
                    size - len(data)
                )

                if not chunk:

                    

                    self.connected = False

                    return None

                data.extend(chunk)

            return bytes(data)

        except Exception:

            log(self,"ERROR",
                f"Erreur : {traceback.format_exc()}"
            )

            self.connected = False

            return None

    def disconnect(self,raison):
        """
        Deconnexion du client
        """
        print("deconnexion")
        self.send_packet(decoPacket(raison))
        time.sleep(10)

        if self.socket:

            self.socket.close()

        self.connected = False
        print(self.connected)

        
