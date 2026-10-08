from __future__ import annotations

import queue
import struct
import threading
import uuid
from pathlib import Path

import numpy as np
from PIL import Image
from vispy import app, scene
from vispy.scene import visuals

from .client import Client
from .packet import PacketType
from .packets.move import MovePacket


class Game(scene.SceneCanvas):
    """
    3D first-person game client.

    Architecture:
        Server
          ↓
        Client
          ↓
        network thread
          ↓
        network_queue
          ↓
        Game
          ↓
        VisPy

    Coordinate conversion:

        Server:
            x = horizontal
            y = depth
            z = vertical

        VisPy:
            X = server x
            Y = server z
            Z = server y
    """

    # ------------------------------------------------------------------
    # WORLD
    # ------------------------------------------------------------------

    WORLD_WIDTH = 1000.0
    WORLD_DEPTH = 1000.0
    WORLD_HEIGHT = 120.0

    # Heightmap resolution after optional downsampling.
    MAX_TERRAIN_SIZE = 512

    # First-person camera.
    PLAYER_HEIGHT = 2.0
    PLAYER_SPEED = 5.0

    # Network.
    NETWORK_QUEUE_LIMIT = 100

    # Visuals.
    REMOTE_PLAYER_RADIUS = 2.0

    # ------------------------------------------------------------------
    # INIT
    # ------------------------------------------------------------------

    def __init__(self, client: Client):
        super().__init__(
            keys="interactive",
            title="The Last Signal",
            size=(1280, 720),
            bgcolor="black",
        )

        self.client = client

        # Prevent VisPy from automatically closing the application
        # when this canvas disappears unexpectedly.
        self.unfreeze()

        # --------------------------------------------------------------
        # GAME STATE
        # --------------------------------------------------------------

        self.running = True

        self.local_x = 100.0
        self.local_y = 100.0
        self.local_z = 0.0

        self.remote_players: dict[uuid.UUID, tuple[int, int, int]] = {}

        # UUID -> VisPy visual
        self.remote_visuals: dict[uuid.UUID, visuals.Markers] = {}

        # --------------------------------------------------------------
        # NETWORK
        # --------------------------------------------------------------

        self.network_queue: queue.Queue = queue.Queue(
            maxsize=self.NETWORK_QUEUE_LIMIT
        )

        self.network_thread = threading.Thread(
            target=self._network_loop,
            name="GameNetworkThread",
            daemon=True,
        )

        # --------------------------------------------------------------
        # SCENE
        # --------------------------------------------------------------

        self.view = self.central_widget.add_view()

        self.view.camera = scene.cameras.FlyCamera(
            fov=70.0,
            parent=self.view.scene,
        )

        self.camera = self.view.camera

        # Movement speed of the FlyCamera.
        self.camera.scale_factor = self.PLAYER_SPEED

        # First-person camera should not roll.
        self.camera.auto_roll = False

        # --------------------------------------------------------------
        # TERRAIN
        # --------------------------------------------------------------

        self.heightmap: np.ndarray | None = None
        self.color_map: np.ndarray | None = None

        self.terrain = None

        self._load_terrain()

        # --------------------------------------------------------------
        # CAMERA INITIAL POSITION
        # --------------------------------------------------------------

        self._place_camera_initially()

        # --------------------------------------------------------------
        # VISPY TIMER
        # --------------------------------------------------------------

        self.timer = app.Timer(
            interval=1.0 / 60.0,
            connect=self._update,
            start=True,
        )

        # --------------------------------------------------------------
        # EVENTS
        # --------------------------------------------------------------

        self.events.key_press.connect(self._on_key_press)
        self.events.key_release.connect(self._on_key_release)
        self.events.mouse_press.connect(self._on_mouse_press)

        # --------------------------------------------------------------
        # NETWORK THREAD
        # --------------------------------------------------------------

        self.network_thread.start()

    # ==================================================================
    # TERRAIN
    # ==================================================================

    def _assets_directory(self) -> Path:
        """
        Find the project assets directory.

        Expected:

            project/
                assets/
                    map_height.png
                    map_color.png
                    map_collision.png
        """

        current_file = Path(__file__).resolve()

        # client_python/game.py
        # -> project root
        project_root = current_file.parent.parent

        assets = project_root / "assets"

        if assets.exists():
            return assets

        # Fallback for unusual launch locations.
        return Path("assets")

    def _load_terrain(self) -> None:
        """
        Load map_height.png and create the 3D terrain mesh.
        """

        assets = self._assets_directory()

        height_path = assets / "map_height.png"
        color_path = assets / "map_color.png"

        if not height_path.exists():
            raise FileNotFoundError(
                f"Heightmap introuvable : {height_path}"
            )

        print(f"[GAME] Chargement heightmap : {height_path}")

        # --------------------------------------------------------------
        # HEIGHTMAP
        # --------------------------------------------------------------

        height_image = Image.open(height_path).convert("L")

        height = np.asarray(
            height_image,
            dtype=np.float32,
        )

        if height.ndim != 2:
            raise ValueError(
                "map_height.png doit être une image en niveaux de gris."
            )

        # Normalize 0 -> 1.
        height_min = float(height.min())
        height_max = float(height.max())

        if height_max > height_min:
            height = (height - height_min) / (
                height_max - height_min
            )
        else:
            height.fill(0.0)

        # --------------------------------------------------------------
        # DOWNSAMPLING
        # --------------------------------------------------------------

        height = self._downsample_height(height)

        self.heightmap = height

        terrain_height, terrain_width = height.shape

        print(
            "[GAME] Terrain : "
            f"{terrain_width} x {terrain_height}"
        )

        # --------------------------------------------------------------
        # WORLD COORDINATES
        # --------------------------------------------------------------

        x = np.linspace(
            -self.WORLD_WIDTH / 2.0,
            self.WORLD_WIDTH / 2.0,
            terrain_width,
            dtype=np.float32,
        )

        z = np.linspace(
            -self.WORLD_DEPTH / 2.0,
            self.WORLD_DEPTH / 2.0,
            terrain_height,
            dtype=np.float32,
        )

        xx, zz = np.meshgrid(x, z)

        yy = height * self.WORLD_HEIGHT

        vertices = np.column_stack(
            (
                xx.ravel(),
                yy.ravel(),
                zz.ravel(),
            )
        ).astype(np.float32)

        # --------------------------------------------------------------
        # TRIANGLES
        # --------------------------------------------------------------

        faces = self._build_faces(
            terrain_width,
            terrain_height,
        )

        # --------------------------------------------------------------
        # COLORS
        # --------------------------------------------------------------

        vertex_colors = self._load_terrain_colors(
            color_path,
            terrain_width,
            terrain_height,
        )

        # --------------------------------------------------------------
        # MESH
        # --------------------------------------------------------------

        self.terrain = visuals.Mesh(
            vertices=vertices,
            faces=faces,
            vertex_colors=vertex_colors,
            shading="smooth",
            parent=self.view.scene,
        )

        print("[GAME] Terrain 3D chargé.")

    def _downsample_height(
        self,
        height: np.ndarray,
    ) -> np.ndarray:
        """
        Reduce the heightmap if it is too large.

        Keeps the terrain reasonably lightweight.
        """

        h, w = height.shape

        if max(h, w) <= self.MAX_TERRAIN_SIZE:
            return height

        scale = max(h, w) / self.MAX_TERRAIN_SIZE

        new_w = max(2, int(w / scale))
        new_h = max(2, int(h / scale))

        image = Image.fromarray(
            np.uint8(height * 255.0),
            mode="L",
        )

        image = image.resize(
            (new_w, new_h),
            Image.Resampling.BILINEAR,
        )

        result = np.asarray(
            image,
            dtype=np.float32,
        ) / 255.0

        return result

    @staticmethod
    def _build_faces(
        width: int,
        height: int,
    ) -> np.ndarray:
        """
        Create two triangles for every terrain quad.
        """

        faces = []

        for y in range(height - 1):
            row = y * width
            next_row = (y + 1) * width

            for x in range(width - 1):
                a = row + x
                b = row + x + 1
                c = next_row + x
                d = next_row + x + 1

                faces.append((a, b, c))
                faces.append((b, d, c))

        return np.asarray(
            faces,
            dtype=np.uint32,
        )

    def _load_terrain_colors(
        self,
        color_path: Path,
        width: int,
        height: int,
    ) -> np.ndarray:
        """
        Load map_color.png if available.

        The image is converted to per-vertex colors.
        """

        if not color_path.exists():
            print(
                "[GAME] map_color.png absent, "
                "utilisation d'une couleur par défaut."
            )

            colors = np.zeros(
                (width * height, 4),
                dtype=np.float32,
            )

            colors[:, 0] = 0.25
            colors[:, 1] = 0.55
            colors[:, 2] = 0.25
            colors[:, 3] = 1.0

            return colors

        print(f"[GAME] Chargement couleurs : {color_path}")

        image = Image.open(color_path).convert("RGB")

        image = image.resize(
            (width, height),
            Image.Resampling.BILINEAR,
        )

        rgb = np.asarray(
            image,
            dtype=np.float32,
        ) / 255.0

        # PNG is indexed [row, column].
        # This corresponds directly to our vertex ordering.
        colors = rgb.reshape(
            width * height,
            3,
        )

        alpha = np.ones(
            (colors.shape[0], 1),
            dtype=np.float32,
        )

        return np.concatenate(
            (colors, alpha),
            axis=1,
        )

    # ==================================================================
    # CAMERA
    # ==================================================================

    def _place_camera_initially(self) -> None:
        """
        Place the first-person camera above the initial server position.
        """

        world_x = self._server_x_to_world(self.local_x)
        world_z = self._server_y_to_world(self.local_y)

        terrain_y = self._terrain_height_at(
            world_x,
            world_z,
        )

        self.camera.center = (
            world_x,
            terrain_y + self.PLAYER_HEIGHT,
            world_z,
        )

        print(
            "[GAME] Caméra initiale : "
            f"({world_x:.1f}, "
            f"{terrain_y + self.PLAYER_HEIGHT:.1f}, "
            f"{world_z:.1f})"
        )

    def _update_camera_position(self) -> None:
        """
        Keep the camera at player height above the terrain.

        The FlyCamera handles horizontal first-person movement.
        """

        center = self.camera.center

        if center is None:
            return

        try:
            x = float(center[0])
            z = float(center[2])
        except (TypeError, ValueError, IndexError):
            return

        terrain_y = self._terrain_height_at(x, z)

        self.camera.center = (
            x,
            terrain_y + self.PLAYER_HEIGHT,
            z,
        )

    def _terrain_height_at(
        self,
        world_x: float,
        world_z: float,
    ) -> float:
        """
        Return terrain height at a world position.
        """

        if self.heightmap is None:
            return 0.0

        height, width = self.heightmap.shape

        normalized_x = (
            world_x + self.WORLD_WIDTH / 2.0
        ) / self.WORLD_WIDTH

        normalized_z = (
            world_z + self.WORLD_DEPTH / 2.0
        ) / self.WORLD_DEPTH

        normalized_x = float(
            np.clip(normalized_x, 0.0, 1.0)
        )

        normalized_z = float(
            np.clip(normalized_z, 0.0, 1.0)
        )

        px = int(
            normalized_x * (width - 1)
        )

        pz = int(
            normalized_z * (height - 1)
        )

        value = float(
            self.heightmap[pz, px]
        )

        return value * self.WORLD_HEIGHT

    # ==================================================================
    # COORDINATES
    # ==================================================================

    def _server_x_to_world(
        self,
        x: float,
    ) -> float:
        """
        Server X -> VisPy X.

        The server currently uses the 0..1000 world.
        VisPy centers the terrain around 0.
        """

        return x - self.WORLD_WIDTH / 2.0

    def _server_y_to_world(
        self,
        y: float,
    ) -> float:
        """
        Server Y -> VisPy Z.
        """

        return y - self.WORLD_DEPTH / 2.0

    def _world_x_to_server(
        self,
        x: float,
    ) -> int:
        return int(
            round(
                x + self.WORLD_WIDTH / 2.0
            )
        )

    def _world_z_to_server(
        self,
        z: float,
    ) -> int:
        return int(
            round(
                z + self.WORLD_DEPTH / 2.0
            )
        )

    # ==================================================================
    # NETWORK
    # ==================================================================

    def _network_loop(self) -> None:
        """
        Receive packets without blocking the VisPy event loop.

        Connection itself is also performed here so the window can
        appear before networking starts.
        """

        try:
            print("[GAME] Connexion au serveur...")

            self.client.connect()

            print("[GAME] Connecté au serveur.")

        except Exception as exc:
            print(
                f"[GAME] Connexion impossible : {exc}"
            )
            return

        while self.running:
            try:
                if not self.client.connected:
                    break

                packet = self.client.receive_packet()

                if packet is None:
                    continue

                try:
                    self.network_queue.put_nowait(packet)
                except queue.Full:
                    # Drop the oldest packet if the queue is full.
                    try:
                        self.network_queue.get_nowait()
                    except queue.Empty:
                        pass

                    try:
                        self.network_queue.put_nowait(packet)
                    except queue.Full:
                        pass

            except Exception as exc:
                if self.running:
                    print(
                        f"[GAME] Erreur réseau : {exc}"
                    )

                break

    # ==================================================================
    # PACKET PROCESSING
    # ==================================================================

    def _process_network_queue(self) -> None:
        """
        Process packets from the network thread.
        """

        processed = 0

        while processed < 100:
            try:
                packet = self.network_queue.get_nowait()
            except queue.Empty:
                break

            processed += 1

            try:
                self._handle_packet(packet)
            except Exception as exc:
                print(
                    f"[GAME] Erreur traitement paquet : {exc}"
                )

    def _handle_packet(self, packet) -> None:
        """
        Dispatch server packets.
        """

        # Packet objects in the project normally expose:
        # packet_type and payload.
        packet_type = getattr(
            packet,
            "packet_type",
            None,
        )

        payload = getattr(
            packet,
            "payload",
            b"",
        )

        # Some implementations may expose type instead.
        if packet_type is None:
            packet_type = getattr(
                packet,
                "type",
                None,
            )

        if packet_type == PacketType.SESSION:
            self._handle_session(payload)

        elif packet_type == PacketType.PLAYER_STATE:
            self._handle_player_state(payload)

        elif packet_type == PacketType.PLAYER_REMOVE:
            self._handle_player_remove(payload)

    def _handle_session(
        self,
        payload: bytes,
    ) -> None:
        """
        Handle SESSION packet.

        SESSION payload:
            UUID = 16 bytes
        """

        if len(payload) != 16:
            print(
                "[GAME] SESSION invalide : "
                f"{len(payload)} octets"
            )
            return

        try:
            session_id = uuid.UUID(
                bytes=payload
            )

            # Keep the client's session identifier synchronized
            # if the Client implementation allows it.
            try:
                self.client.session_id = session_id
            except Exception:
                pass

            print(
                f"[GAME] Session : {session_id}"
            )

        except ValueError:
            print("[GAME] UUID SESSION invalide.")

    def _handle_player_state(
        self,
        payload: bytes,
    ) -> None:
        """
        PLAYER_STATE:

            UUID  = 16 bytes
            x/y/z = 12 bytes

        Total:
            28 bytes
        """

        if len(payload) != 28:
            print(
                "[GAME] PLAYER_STATE invalide : "
                f"{len(payload)} octets"
            )
            return

        try:
            player_id = uuid.UUID(
                bytes=payload[:16]
            )

            x, y, z = struct.unpack(
                "!iii",
                payload[16:28],
            )

        except (ValueError, struct.error):
            print("[GAME] PLAYER_STATE invalide.")
            return

        local_id = self._get_local_player_id()

        # --------------------------------------------------------------
        # LOCAL PLAYER
        # --------------------------------------------------------------

        if local_id is not None and player_id == local_id:
            self.local_x = float(x)
            self.local_y = float(y)
            self.local_z = float(z)

            return

        # --------------------------------------------------------------
        # REMOTE PLAYER
        # --------------------------------------------------------------

        self.remote_players[player_id] = (
            x,
            y,
            z,
        )

        self._create_or_update_remote_player(
            player_id,
            x,
            y,
            z,
        )

    def _handle_player_remove(
        self,
        payload: bytes,
    ) -> None:
        """
        PLAYER_REMOVE:

            UUID = 16 bytes
        """

        if len(payload) != 16:
            print(
                "[GAME] PLAYER_REMOVE invalide : "
                f"{len(payload)} octets"
            )
            return

        try:
            player_id = uuid.UUID(
                bytes=payload
            )
        except ValueError:
            print(
                "[GAME] UUID PLAYER_REMOVE invalide."
            )
            return

        self.remote_players.pop(
            player_id,
            None,
        )

        visual = self.remote_visuals.pop(
            player_id,
            None,
        )

        if visual is not None:
            visual.parent = None

        print(
            f"[GAME] Joueur supprimé : "
            f"{player_id}"
        )

    def _get_local_player_id(
        self,
    ) -> uuid.UUID | None:
        """
        Get the local session UUID.
        """

        session_id = getattr(
            self.client,
            "session_id",
            None,
        )

        if session_id is None:
            return None

        if isinstance(
            session_id,
            uuid.UUID,
        ):
            return session_id

        try:
            return uuid.UUID(
                str(session_id)
            )
        except (ValueError, AttributeError):
            return None

    # ==================================================================
    # REMOTE PLAYERS
    # ==================================================================

    def _create_or_update_remote_player(
        self,
        player_id: uuid.UUID,
        x: int,
        y: int,
        z: int,
    ) -> None:
        """
        Create or move a remote player marker.
        """

        world_x = self._server_x_to_world(x)

        world_z = self._server_y_to_world(y)

        terrain_y = self._terrain_height_at(
            world_x,
            world_z,
        )

        # Server Z is reserved for vertical position.
        # For now terrain determines the visual Y position.
        world_y = terrain_y + self.REMOTE_PLAYER_RADIUS

        position = np.array(
            [[world_x, world_y, world_z]],
            dtype=np.float32,
        )

        visual = self.remote_visuals.get(
            player_id
        )

        if visual is None:
            visual = visuals.Markers(
                pos=position,
                size=14,
                face_color="red",
                edge_color="white",
                parent=self.view.scene,
            )

            self.remote_visuals[player_id] = visual

        else:
            visual.set_data(
                position,
                size=14,
                face_color="red",
                edge_color="white",
            )

    # ==================================================================
    # LOCAL MOVEMENT / SERVER SYNC
    # ==================================================================

    def _sync_camera_to_server(self) -> None:
        """
        Convert the first-person camera position into server
        coordinates and send movement when it changes.
        """

        center = self.camera.center

        if center is None:
            return

        try:
            world_x = float(center[0])
            world_z = float(center[2])
        except (
            TypeError,
            ValueError,
            IndexError,
        ):
            return

        server_x = self._world_x_to_server(
            world_x
        )

        server_y = self._world_z_to_server(
            world_z
        )

        # Keep inside the server world.
        server_x = max(
            0,
            min(
                int(self.WORLD_WIDTH),
                server_x,
            ),
        )

        server_y = max(
            0,
            min(
                int(self.WORLD_DEPTH),
                server_y,
            ),
        )

        if (
            server_x == int(self.local_x)
            and server_y == int(self.local_y)
        ):
            return

        self.local_x = float(server_x)
        self.local_y = float(server_y)

        self._send_position_to_server(
            server_x,
            server_y,
            int(self.local_z),
        )

    def _send_position_to_server(
        self,
        x: int,
        y: int,
        z: int,
    ) -> None:
        """
        Send MOVE packet to the server.
        """

        try:
            if not self.client.connected:
                return

            packet = MovePacket(
                int(x),
                int(y),
                int(z),
            )

            self.client.send_packet(packet)

        except Exception as exc:
            print(
                f"[GAME] Impossible d'envoyer MOVE : "
                f"{exc}"
            )

    # ==================================================================
    # VISPY UPDATE
    # ==================================================================

    def _update(self, event) -> None:
        """
        Main game loop.

        Runs on the VisPy thread.
        """

        if not self.running:
            return

        # Network packets.
        self._process_network_queue()

        # Keep player above terrain.
        self._update_camera_position()

        # Synchronize camera movement with server.
        self._sync_camera_to_server()

        # Redraw.
        self.update()

    # ==================================================================
    # INPUT
    # ==================================================================

    def _on_key_press(self, event) -> None:
        """
        FlyCamera already handles first-person keyboard movement.

        This callback exists mainly for debugging / future controls.
        """

        key = getattr(
            event,
            "key",
            None,
        )

        if key is None:
            return

        key_name = getattr(
            key,
            "name",
            str(key),
        )

        key_name = str(
            key_name
        ).lower()

        if key_name == "escape":
            self.close()

    def _on_key_release(self, event) -> None:
        """
        Reserved for future custom controls.
        """

        pass

    def _on_mouse_press(self, event) -> None:
        """
        Mouse input is primarily handled by FlyCamera.
        """

        pass

    # ==================================================================
    # CLOSE
    # ==================================================================

    def on_close(self, event) -> None:
        """
        Clean shutdown.
        """

        if not self.running:
            return

        self.running = False

        print("[GAME] Arrêt du client 3D...")

        try:
            self.timer.stop()
        except Exception:
            pass

        # Disconnect first so receive_packet() can unblock.
        try:
            if self.client.connected:
                self.client.disconnect(
                    "Arrêt normal"
                )
        except Exception as exc:
            print(
                f"[GAME] Erreur déconnexion : {exc}"
            )

        if (
            self.network_thread.is_alive()
            and threading.current_thread()
            is not self.network_thread
        ):
            self.network_thread.join(
                timeout=1.0
            )

        print("[GAME] Client 3D arrêté.")


def run_game(client: Client | None = None) -> None:
    """
    Launch the 3D game.

    If no Client is supplied, one is created.
    """

    if client is None:
        client = Client()

    game = Game(client)

    game.show()

    app.run()


