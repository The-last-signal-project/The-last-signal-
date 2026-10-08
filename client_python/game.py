from __future__ import annotations

import queue
import struct
import threading
import uuid
from pathlib import Path

import numpy as np
from vispy import app, io, scene
from vispy.scene import visuals

from .client import Client
from .packet import PacketType
from .packets.move import MovePacket


class Game:
    """
    3D first-person game client.

    Coordinate mapping:
        Server X -> World X
        Server Y -> World Z
        Server Z -> World Y

    The server protocol remains unchanged.

    The player does not appear as a visible mesh locally because
    the camera represents the player's eyes.

    Network architecture:
        Network thread
              ↓
        network_queue
              ↓
        game update
              ↓
        local / remote players
    """

    # ------------------------------------------------------------------
    # Window
    # ------------------------------------------------------------------

    WINDOW_SIZE = (1280, 720)
    WINDOW_TITLE = "The Last Signal Online - 3D"

    # ------------------------------------------------------------------
    # Terrain
    # ------------------------------------------------------------------

    HEIGHTMAP_PATH = "assets/map_height.png"
    COLOR_MAP_PATH = "assets/map_color.png"

    TERRAIN_SIZE = 1000.0
    TERRAIN_HEIGHT = 120.0

    # ------------------------------------------------------------------
    # Player
    # ------------------------------------------------------------------

    PLAYER_HEIGHT = 2.0
    PLAYER_SPEED = 5.0

    # ------------------------------------------------------------------
    # Network
    # ------------------------------------------------------------------

    PLAYER_STATE_SIZE = 28
    PLAYER_REMOVE_SIZE = 16

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    UPDATE_INTERVAL = 1.0 / 60.0
    NETWORK_INTERVAL = 1.0 / 60.0

    def __init__(self, client: Client):
        self.client = client

        self.running = True

        # --------------------------------------------------------------
        # Network state
        # --------------------------------------------------------------

        self.network_queue: queue.Queue[bytes] = queue.Queue()

        self.remote_players: dict[uuid.UUID, tuple[int, int, int]] = {}

        self.network_thread = threading.Thread(
            target=self._network_loop,
            name="GameNetworkThread",
            daemon=True,
        )

        # --------------------------------------------------------------
        # Local player
        #
        # Server coordinates are kept exactly as before:
        #
        #   x = horizontal X
        #   y = horizontal Z
        #   z = vertical
        #
        # The camera uses:
        #
        #   world X = server X
        #   world Y = terrain height / vertical
        #   world Z = server Y
        # --------------------------------------------------------------

        self.player_x = 100.0
        self.player_z = 100.0
        self.player_server_z = 0

        # --------------------------------------------------------------
        # Input
        # --------------------------------------------------------------

        self.keys: set[str] = set()

        # --------------------------------------------------------------
        # Terrain
        # --------------------------------------------------------------

        self.height_data: np.ndarray | None = None
        self.terrain_size_x = self.TERRAIN_SIZE
        self.terrain_size_z = self.TERRAIN_SIZE

        # --------------------------------------------------------------
        # VisPy
        # --------------------------------------------------------------

        self.canvas = scene.SceneCanvas(
            keys="interactive",
            size=self.WINDOW_SIZE,
            bgcolor=(0.03, 0.03, 0.04, 1.0),
            show=False,
        )

        self.canvas.title = self.WINDOW_TITLE

        self.view = self.canvas.central_widget.add_view()

        # FlyCamera = first-person / FPS-style camera.
        self.camera = scene.cameras.FlyCamera(
            fov=75.0,
            parent=self.view.scene,
        )

        self.camera.auto_roll = True
        self.camera.scale_factor = self.PLAYER_SPEED

        self.view.camera = self.camera

        # --------------------------------------------------------------
        # Scene objects
        # --------------------------------------------------------------

        self.terrain: visuals.Mesh | None = None

        self.remote_visuals: dict[uuid.UUID, visuals.Sphere] = {}

        self._load_terrain()

        # --------------------------------------------------------------
        # Start position
        # --------------------------------------------------------------

        self._place_camera_at_player()

        # --------------------------------------------------------------
        # VisPy timers
        # --------------------------------------------------------------

        self.game_timer = app.Timer(
            interval=self.UPDATE_INTERVAL,
            connect=self._game_update,
            start=True,
        )

        self.network_timer = app.Timer(
            interval=self.NETWORK_INTERVAL,
            connect=self._process_network_queue,
            start=True,
        )

        # --------------------------------------------------------------
        # Events
        # --------------------------------------------------------------

        self.canvas.events.key_press.connect(self._on_key_press)
        self.canvas.events.key_release.connect(self._on_key_release)
        self.canvas.events.close.connect(self._on_close)

        # --------------------------------------------------------------
        # Network
        # --------------------------------------------------------------

        self.network_thread.start()

    # ==================================================================
    # TERRAIN
    # ==================================================================

    def _find_asset(self, relative_path: str) -> Path:
        """
        Find an asset regardless of the directory from which the client
        was launched.
        """

        path = Path(relative_path)

        if path.exists():
            return path

        # Project root when this file is:
        # project/client_python/game.py
        project_root = Path(__file__).resolve().parent.parent

        candidate = project_root / relative_path

        if candidate.exists():
            return candidate

        raise FileNotFoundError(
            f"Asset introuvable: {relative_path}\n"
            f"Chemin testé: {path}\n"
            f"Chemin projet: {candidate}"
        )

    def _load_terrain(self) -> None:
        """
        Build the 3D terrain from map_height.png.

        map_height.png:
            grayscale heightmap

        map_color.png:
            optional RGB/RGBA color map used as vertex colors.
        """

        height_path = self._find_asset(self.HEIGHTMAP_PATH)

        height_image = io.read(str(height_path))

        if height_image.ndim == 3:
            height_gray = height_image[..., :3].mean(axis=2)
        else:
            height_gray = height_image.astype(np.float32)

        height_gray = height_gray.astype(np.float32)

        # Normalize heightmap to [0, 1].
        min_height = float(height_gray.min())
        max_height = float(height_gray.max())

        if max_height > min_height:
            height_normalized = (
                height_gray - min_height
            ) / (max_height - min_height)
        else:
            height_normalized = np.zeros_like(height_gray)

        # Downsample very large maps to keep the prototype responsive.
        max_resolution = 512

        height_normalized = self._resize_grid(
            height_normalized,
            max_resolution,
        )

        rows, cols = height_normalized.shape

        # Terrain dimensions.
        xs = np.linspace(
            -self.TERRAIN_SIZE / 2.0,
            self.TERRAIN_SIZE / 2.0,
            cols,
            dtype=np.float32,
        )

        zs = np.linspace(
            -self.TERRAIN_SIZE / 2.0,
            self.TERRAIN_SIZE / 2.0,
            rows,
            dtype=np.float32,
        )

        grid_x, grid_z = np.meshgrid(xs, zs)

        grid_y = height_normalized * self.TERRAIN_HEIGHT

        vertices = np.column_stack(
            (
                grid_x.ravel(),
                grid_y.ravel(),
                grid_z.ravel(),
            )
        ).astype(np.float32)

        # --------------------------------------------------------------
        # Faces
        # --------------------------------------------------------------

        face_count = (rows - 1) * (cols - 1) * 2

        faces = np.empty(
            (face_count, 3),
            dtype=np.uint32,
        )

        index = 0

        for z in range(rows - 1):
            row_start = z * cols
            next_row = (z + 1) * cols

            for x in range(cols - 1):
                a = row_start + x
                b = a + 1
                c = next_row + x
                d = c + 1

                faces[index] = (a, b, c)
                faces[index + 1] = (b, d, c)

                index += 2

        # --------------------------------------------------------------
        # Terrain colors
        # --------------------------------------------------------------

        vertex_colors = self._load_terrain_colors(
            rows,
            cols,
            height_normalized,
        )

        self.height_data = height_normalized

        self.terrain = visuals.Mesh(
            vertices=vertices,
            faces=faces,
            vertex_colors=vertex_colors,
            shading="smooth",
            parent=self.view.scene,
        )

    def _load_terrain_colors(
        self,
        rows: int,
        cols: int,
        height_normalized: np.ndarray,
    ) -> np.ndarray:
        """
        Load map_color.png when available.

        If it is unavailable, generate a simple terrain gradient.
        """

        try:
            color_path = self._find_asset(self.COLOR_MAP_PATH)
            image = io.read(str(color_path))

            if image.ndim == 2:
                image = np.repeat(
                    image[..., None],
                    3,
                    axis=2,
                )

            image = image[..., :3]

            image = self._resize_image(
                image,
                rows,
                cols,
            )

            colors = image.astype(np.float32)

            if colors.max() > 1.0:
                colors /= 255.0

            alpha = np.ones(
                (rows, cols, 1),
                dtype=np.float32,
            )

            colors = np.concatenate(
                (colors, alpha),
                axis=2,
            )

            return colors.reshape(-1, 4)

        except FileNotFoundError:
            # Fallback if map_color.png isn't available yet.
            h = height_normalized[..., None]

            colors = np.concatenate(
                (
                    0.15 + h * 0.25,
                    0.25 + h * 0.35,
                    0.12 + h * 0.15,
                    np.ones_like(h),
                ),
                axis=2,
            )

            return colors.reshape(-1, 4).astype(np.float32)

    @staticmethod
    def _resize_grid(
        data: np.ndarray,
        max_resolution: int,
    ) -> np.ndarray:
        """
        Reduce a heightmap while preserving its proportions.
        """

        rows, cols = data.shape

        scale = min(
            1.0,
            max_resolution / max(rows, cols),
        )

        if scale >= 1.0:
            return data

        new_rows = max(2, int(rows * scale))
        new_cols = max(2, int(cols * scale))

        row_indices = np.linspace(
            0,
            rows - 1,
            new_rows,
        ).astype(np.int32)

        col_indices = np.linspace(
            0,
            cols - 1,
            new_cols,
        ).astype(np.int32)

        return data[
            row_indices[:, None],
            col_indices[None, :],
        ]

    @staticmethod
    def _resize_image(
        image: np.ndarray,
        rows: int,
        cols: int,
    ) -> np.ndarray:
        """
        Resize an RGB image using nearest-neighbour sampling.

        This avoids adding another dependency just for the prototype.
        """

        source_rows, source_cols = image.shape[:2]

        row_indices = np.linspace(
            0,
            source_rows - 1,
            rows,
        ).astype(np.int32)

        col_indices = np.linspace(
            0,
            source_cols - 1,
            cols,
        ).astype(np.int32)

        return image[
            row_indices[:, None],
            col_indices[None, :],
        ]

    # ==================================================================
    # FIRST PERSON CAMERA
    # ==================================================================

    def _terrain_height_at(
        self,
        server_x: float,
        server_y: float,
    ) -> float:
        """
        Return the terrain height under a server X/Y position.
        """

        if self.height_data is None:
            return 0.0

        rows, cols = self.height_data.shape

        normalized_x = (
            server_x / self.TERRAIN_SIZE + 0.5
        )

        normalized_z = (
            server_y / self.TERRAIN_SIZE + 0.5
        )

        normalized_x = float(
            np.clip(normalized_x, 0.0, 1.0)
        )

        normalized_z = float(
            np.clip(normalized_z, 0.0, 1.0)
        )

        column = int(
            normalized_x * (cols - 1)
        )

        row = int(
            normalized_z * (rows - 1)
        )

        return float(
            self.height_data[row, column]
            * self.TERRAIN_HEIGHT
        )

    def _place_camera_at_player(self) -> None:
        """
        Put the camera at the player's eye position.
        """

        terrain_y = self._terrain_height_at(
            self.player_x,
            self.player_z,
        )

        eye_y = terrain_y + self.PLAYER_HEIGHT

        self.camera.center = (
            self.player_x - self.TERRAIN_SIZE / 2.0,
            eye_y,
            self.player_z - self.TERRAIN_SIZE / 2.0,
        )

    # ==================================================================
    # NETWORK
    # ==================================================================

    def _network_loop(self) -> None:
        """
        Blocking network receive loop.

        The rendering thread never blocks on network I/O.
        """

        while self.running:
            try:
                if not self.client.connected:
                    break

                packet = self.client.receive_packet()

                if packet is None:
                    continue

                self.network_queue.put(packet)

            except Exception:
                if self.running:
                    # The existing client/network layer remains
                    # responsible for reporting detailed errors.
                    pass

                break

    def _process_network_queue(self, event) -> None:
        """
        Process network packets on the rendering thread.
        """

        processed = 0

        while processed < 100:
            try:
                packet = self.network_queue.get_nowait()
            except queue.Empty:
                break

            try:
                self._handle_packet(packet)
            except Exception:
                # Invalid packets must never kill the rendering loop.
                pass

            processed += 1

    def _handle_packet(self, packet) -> None:
        """
        Handle the existing multiplayer protocol.
        """

        if not packet:
            return

        packet_type = packet[0]
        payload = packet[1:]

        if packet_type == PacketType.PLAYER_STATE:
            self._handle_player_state(payload)

        elif packet_type == PacketType.PLAYER_REMOVE:
            self._handle_player_remove(payload)

        elif packet_type == PacketType.SESSION:
            self._handle_session(payload)

    def _handle_session(self, payload: bytes) -> None:
        """
        SESSION contains the UUID assigned to this client.

        Do not replace the Client's session management here; this only
        exists so the game can remain compatible with the current
        protocol.
        """

        if len(payload) != 16:
            return

        try:
            session_id = uuid.UUID(bytes=payload)
        except ValueError:
            return

        try:
            self.client.session_id = session_id
        except Exception:
            pass

    def _handle_player_state(self, payload: bytes) -> None:
        if len(payload) != self.PLAYER_STATE_SIZE:
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
            return

        local_id = self._get_local_player_id()

        if local_id is not None and player_id == local_id:
            self.player_x = float(x)
            self.player_z = float(y)
            self.player_server_z = z

            self._place_camera_at_player()
            return

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

    def _handle_player_remove(self, payload: bytes) -> None:
        if len(payload) != self.PLAYER_REMOVE_SIZE:
            return

        try:
            player_id = uuid.UUID(
                bytes=payload
            )
        except ValueError:
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

    def _get_local_player_id(self) -> uuid.UUID | None:
        session_id = getattr(
            self.client,
            "session_id",
            None,
        )

        if isinstance(session_id, uuid.UUID):
            return session_id

        if session_id:
            try:
                return uuid.UUID(str(session_id))
            except (ValueError, AttributeError):
                return None

        return None

    # ==================================================================
    # REMOTE PLAYERS
    # ==================================================================

    def _create_or_update_remote_player(
        self,
        player_id: uuid.UUID,
        server_x: int,
        server_y: int,
        server_z: int,
    ) -> None:
        """
        Remote players are temporary simple spheres.

        They are only visible to the local player.
        """

        world_x = (
            float(server_x)
            - self.TERRAIN_SIZE / 2.0
        )

        world_z = (
            float(server_y)
            - self.TERRAIN_SIZE / 2.0
        )

        terrain_y = self._terrain_height_at(
            float(server_x),
            float(server_y),
        )

        world_y = (
            terrain_y
            + self.PLAYER_HEIGHT / 2.0
        )

        visual = self.remote_visuals.get(player_id)

        if visual is None:
            visual = visuals.Sphere(
                radius=0.7,
                method="ico",
                parent=self.view.scene,
            )

            self.remote_visuals[player_id] = visual

        visual.set_data(
            center=(world_x, world_y, world_z),
            color=(0.85, 0.15, 0.15, 1.0),
        )

    # ==================================================================
    # GAME UPDATE
    # ==================================================================

    def _game_update(self, event) -> None:
        if not self.running:
            return

        # FlyCamera itself handles first-person keyboard/mouse
        # interaction. We synchronize its movement with the server here.
        self._sync_camera_to_server()

        self.canvas.update()

    def _sync_camera_to_server(self) -> None:
        """
        Convert the camera's world position back into server coordinates.

        Server:
            X = horizontal world X
            Y = horizontal world Z
            Z = vertical

        The camera's vertical coordinate is controlled by the terrain.
        """

        center = np.asarray(
            self.camera.center,
            dtype=np.float64,
        )

        server_x = (
            center[0]
            + self.TERRAIN_SIZE / 2.0
        )

        server_y = (
            center[2]
            + self.TERRAIN_SIZE / 2.0
        )

        server_x = float(
            np.clip(
                server_x,
                0.0,
                self.TERRAIN_SIZE,
            )
        )

        server_y = float(
            np.clip(
                server_y,
                0.0,
                self.TERRAIN_SIZE,
            )
        )

        terrain_y = self._terrain_height_at(
            server_x,
            server_y,
        )

        desired_camera_y = (
            terrain_y
            + self.PLAYER_HEIGHT
        )

        # Keep the camera at eye level.
        center[1] = desired_camera_y

        self.camera.center = tuple(center)

        new_x = int(round(server_x))
        new_y = int(round(server_y))

        if (
            new_x == int(round(self.player_x))
            and new_y == int(round(self.player_z))
        ):
            return

        self.player_x = float(new_x)
        self.player_z = float(new_y)

        self._send_position_to_server(
            new_x,
            new_y,
            self.player_server_z,
        )

    def _send_position_to_server(
        self,
        x: int,
        y: int,
        z: int,
    ) -> None:
        if not self.client.connected:
            return

        try:
            packet = MovePacket(
                int(x),
                int(y),
                int(z),
            )

            self.client.send_packet(packet)

        except Exception:
            pass

    # ==================================================================
    # INPUT
    # ==================================================================

    def _on_key_press(self, event) -> None:
        if event.text:
            self.keys.add(event.text.lower())

        # Escape releases focus from the FPS camera.
        if event.key.name == "Escape":
            self.canvas.close()

    def _on_key_release(self, event) -> None:
        if event.text:
            self.keys.discard(event.text.lower())

    # ==================================================================
    # CLOSE
    # ==================================================================

    def _on_close(self, event) -> None:
        self.running = False

        try:
            self.game_timer.stop()
        except Exception:
            pass

        try:
            self.network_timer.stop()
        except Exception:
            pass

        try:
            self.client.disconnect()
        except Exception:
            pass

        if self.network_thread.is_alive():
            self.network_thread.join(timeout=1.0)

    # ==================================================================
    # RUN
    # ==================================================================

    def show(self) -> None:
        self.canvas.show()

        # Put the mouse/canvas in focus so the FPS camera can immediately
        # receive input.
        try:
            self.canvas.native.activateWindow()
            self.canvas.native.setFocus()
        except Exception:
            pass


def run_game(client: Client) -> None:
    """
    Entry point used by the existing client launcher.
    """

    game = Game(client)
    game.show()

    app.run()
