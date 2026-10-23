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
from PySide6 import QtWidgets, QtCore


class Game(scene.SceneCanvas):
    """Client 3D de The Last Signal avec terrain découpé en chunks."""

    # ==============================================================
    # WORLD
    # ==============================================================

    WORLD_WIDTH = 1000.0
    WORLD_DEPTH = 1000.0
    WORLD_HEIGHT = 120.0

    # Taille maximale de la heightmap après réduction.
    MAX_TERRAIN_SIZE = 1024

    # Taille d'un chunk en unités du monde.
    CHUNK_SIZE = 64.0

    # Nombre de chunks dans chaque direction autour du joueur.
    # 2 = jusqu'à 25 chunks actifs.
    RENDER_DISTANCE = 0

    # Caméra et joueur.
    PLAYER_HEIGHT = 2.0
    PLAYER_SPEED = 5.0
    WATER_SPEED_MULTIPLIER = 0.20
    SAND_SPEED_MULTIPLIER = 0.70
    MOUNTAIN_UPHILL_MULTIPLIER = 0.40
    MAX_WALKABLE_SLOPE_DEGREES = 38.0
    MOUNTAIN_BLOCK_SLOPE_DEGREES = 52.0
    HEIGHT_SMOOTH_RADIUS = 1.25
    COLLISION_SAMPLE_STEP = 1.5

    # Réseau.
    NETWORK_QUEUE_LIMIT = 100

    # Joueurs distants.
    REMOTE_PLAYER_RADIUS = 2.0
    REMOTE_PLAYER_SIZE = 14

    # ==============================================================
    # INITIALIZATION
    # ==============================================================

    def __init__(self, client: Client):
        super().__init__(
            keys=None,
            title="The Last Signal",
            size=(1280, 720),
            bgcolor="black",
        )

        self.unfreeze()

        self.client = client
        self.running = True

        # Position initiale côté serveur.
        self.local_x = 100.0
        self.local_y = 100.0
        self.local_z = 0.0
        self._last_sent_position: tuple[int, int, int] | None = None
        self.local_marker: visuals.Markers | None = None

        # Joueurs distants.
        self.remote_players: dict[
            uuid.UUID, tuple[int, int, int]
        ] = {}

        self.remote_visuals: dict[
            uuid.UUID, visuals.Markers
        ] = {}

        # ==========================================================
        # NETWORK
        # ==========================================================

        self.network_queue: queue.Queue = queue.Queue(
            maxsize=self.NETWORK_QUEUE_LIMIT
        )

        self.network_thread = threading.Thread(
            target=self._network_loop,
            name="GameNetworkThread",
            daemon=True,
        )

        # ==========================================================
        # SCENE AND CAMERA
        # ==============================================================

        self.view = self.central_widget.add_view()

        # Caméra orbitale demandée. Le terrain du jeu utilise Y comme axe
        # vertical ; up="y" garde donc la caméra cohérente avec les sommets
        # du terrain (X, hauteur Y, profondeur Z).
        self.view.camera = scene.cameras.TurntableCamera(
            elevation=42,
            azimuth=45,
            distance=38,
            fov=48.0,
            up="y",
            parent=self.view.scene,
        )
        # La caméra est pilotée exclusivement par le code : aucun drag/zoom
        # souris ni raccourci hérité du contrôleur VisPy.
        self.view.camera.interactive = False
        self.camera = self.view.camera

        # ==========================================================
        # TERRAIN DATA
        # ==============================================================

        self.heightmap: np.ndarray | None = None
        # Couleurs et classes de biome sont conservées en uint8, sans conversion
        # RGB/BGR ni interpolation de couleurs qui inventerait des teintes.
        self.color_map: np.ndarray | None = None
        self.biome_map: np.ndarray | None = None
        self.collision_map: np.ndarray | None = None
        self._last_update_time = None

        # (chunk_x, chunk_z) -> maillage VisPy.
        self.terrain_chunks: dict[
            tuple[int, int], visuals.Mesh
        ] = {}

        self._last_chunk_center: tuple[int, int] | None = None

        self._load_terrain()
        self._place_camera_initially()
        self._update_terrain_chunks()

        # ==========================================================
        # TIMER
        # ==============================================================

        self.timer = app.Timer(
            interval=1.0 / 60.0,
            connect=self._update,
            start=True,
        )

        # ==========================================================
        # EVENTS
        # ==============================================================

        self.events.key_press.connect(self._on_key_press)
        self.events.key_release.connect(self._on_key_release)
        self.events.mouse_press.connect(self._on_mouse_press)

        # ==========================================================
        # NETWORK THREAD
        # ==============================================================

        self.network_thread.start()

    # ==============================================================
    # ASSETS
    # ==============================================================

    def _assets_directory(self) -> Path:
        """Retourne le dossier assets du projet."""

        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent

        assets = project_root / "assets"

        if assets.is_dir():
            return assets

        fallback = Path("assets")

        if fallback.is_dir():
            return fallback

        raise FileNotFoundError(
            "Dossier assets introuvable. "
            f"Chemin recherché : {assets}"
        )

    # ==============================================================
    # TERRAIN DATA
    # ==============================================================

    def _load_terrain(self) -> None:
        """Charge les cartes et prépare une heightmap lissée et des biomes."""
        assets = self._assets_directory()
        height_path = assets / "map_height.png"
        color_path = assets / "map_color.png"
        collision_path = assets / "map_collision.png"
        if not height_path.is_file():
            raise FileNotFoundError(f"Heightmap introuvable : {height_path}")

        with Image.open(height_path) as image:
            print(f"[GAME] Heightmap source : {image.size}, mode={image.mode}")
            raw = image.convert("L")
            source = np.asarray(raw, dtype=np.uint8)
            low, high = int(source.min()), int(source.max())
            if high > low:
                normalized = np.uint8(np.clip((source.astype(np.float32) - low)
                                              * (255.0 / (high - low)), 0, 255))
            else:
                normalized = np.zeros_like(source, dtype=np.uint8)
            raw = Image.fromarray(normalized)
            # Un flou spatial léger atténue les marches de hauteur avant
            # l'échantillonnage du maillage ; map_color reste intacte.
            if self.HEIGHT_SMOOTH_RADIUS > 0:
                from PIL import ImageFilter
                raw = raw.filter(ImageFilter.GaussianBlur(self.HEIGHT_SMOOTH_RADIUS))
            height = np.asarray(raw, dtype=np.float32) / 255.0

        self.heightmap = self._downsample_height(height)
        terrain_height, terrain_width = self.heightmap.shape

        if color_path.is_file():
            with Image.open(color_path) as image:
                print(f"[GAME] Couleurs source : {image.size}, mode={image.mode}")
                # NEAREST préserve les couleurs de référence au lieu de créer
                # des couleurs intermédiaires par interpolation bilinéaire.
                color = image.convert("RGB").resize(
                    (terrain_width, terrain_height), Image.Resampling.NEAREST
                )
                self.color_map = np.asarray(color, dtype=np.uint8).copy()
            self.biome_map = self._classify_biomes(self.color_map)
        else:
            self.color_map = None
            self.biome_map = np.zeros((terrain_height, terrain_width), dtype=np.uint8)
            print("[GAME] map_color.png absent : collisions de biome désactivées.")

        # Le fichier est inspecté (dimensions/mode), mais son encodage n'est pas
        # interprété arbitrairement : aucune sémantique n'est supposée.
        if collision_path.is_file():
            with Image.open(collision_path) as image:
                print(f"[GAME] Collision source : {image.size}, mode={image.mode}; "
                      "non utilisée sans convention de codage documentée.")
                self.collision_map = np.asarray(image.convert("L"), dtype=np.uint8)
        else:
            self.collision_map = None
            print("[GAME] map_collision.png absent.")

        print(f"[GAME] Terrain préparé : {terrain_width} x {terrain_height}; "
              f"chunk={self.CHUNK_SIZE:g}; rendu=1 chunk")

    def _classify_biomes(self, rgb: np.ndarray) -> np.ndarray:
        """Classes 0=normal, 1=eau bleue, 2=sable clair, 3=montagne grise."""
        colors = rgb.astype(np.int16)
        r, g, b = colors[..., 0], colors[..., 1], colors[..., 2]
        blue = (b >= 75) & (b > r * 1.18) & (b > g * 1.10)
        light = (r >= 170) & (g >= 155) & (b >= 125) & ((r - b) <= 100)
        gray = (np.abs(r - g) <= 22) & (np.abs(g - b) <= 22) & (r >= 65) & (r <= 205)
        result = np.zeros(rgb.shape[:2], dtype=np.uint8)
        result[blue] = 1
        result[light & ~blue] = 2
        result[gray & ~blue & ~light] = 3
        return result

    def _downsample_height(self, height: np.ndarray) -> np.ndarray:
        """Réduit la heightmap sans parcourir l'image complète à chaque frame."""
        h, w = height.shape
        if max(h, w) <= self.MAX_TERRAIN_SIZE:
            return height.astype(np.float32, copy=False)
        scale = max(h, w) / self.MAX_TERRAIN_SIZE
        new_w = max(2, int(round(w / scale)))
        new_h = max(2, int(round(h / scale)))
        image = Image.fromarray(np.uint8(np.clip(height, 0.0, 1.0) * 255.0))
        image = image.resize((new_w, new_h), Image.Resampling.BILINEAR)
        return np.asarray(image, dtype=np.float32) / 255.0

    # ==============================================================
    # MESH HELPERS
    # ==============================================================

    @staticmethod
    def _build_faces(
        width: int,
        height: int,
    ) -> np.ndarray:
        """Construit deux triangles pour chaque cellule du maillage."""

        if width < 2 or height < 2:
            return np.empty((0, 3), dtype=np.uint32)

        grid = np.arange(
            width * height,
            dtype=np.uint32,
        ).reshape(height, width)

        a = grid[:-1, :-1].ravel()
        b = grid[:-1, 1:].ravel()
        c = grid[1:, :-1].ravel()
        d = grid[1:, 1:].ravel()

        faces = np.empty(
            (a.size * 2, 3),
            dtype=np.uint32,
        )

        # Ordre des sommets orienté vers le haut (+Y). Avec X horizontal
        # et Z profondeur, l'ancien ordre produisait des normales vers -Y.
        faces[0::2] = np.column_stack((a, c, b))
        faces[1::2] = np.column_stack((b, c, d))

        return faces

    def _chunk_counts(self) -> tuple[int, int]:
        """Nombre de chunks sur les axes X et Z."""

        count_x = int(
            np.ceil(self.WORLD_WIDTH / self.CHUNK_SIZE)
        )

        count_z = int(
            np.ceil(self.WORLD_DEPTH / self.CHUNK_SIZE)
        )

        return count_x, count_z

    def _chunk_coordinates(
        self,
        world_x: float,
        world_z: float,
    ) -> tuple[int, int]:
        """Convertit une position du monde en coordonnées de chunk."""

        count_x, count_z = self._chunk_counts()

        chunk_x = int(
            np.floor(
                (world_x + self.WORLD_WIDTH / 2.0)
                / self.CHUNK_SIZE
            )
        )

        chunk_z = int(
            np.floor(
                (world_z + self.WORLD_DEPTH / 2.0)
                / self.CHUNK_SIZE
            )
        )

        return (
            int(np.clip(chunk_x, 0, count_x - 1)),
            int(np.clip(chunk_z, 0, count_z - 1)),
        )

    # ==============================================================
    # CHUNK MESH CREATION
    # ==============================================================

    def _create_terrain_chunk(
        self,
        chunk_x: int,
        chunk_z: int,
    ) -> visuals.Mesh | None:
        """Construit un seul chunk du terrain."""

        if self.heightmap is None:
            return None

        heightmap = self.heightmap
        map_height, map_width = heightmap.shape

        # Limites mondiales du chunk.
        world_x0 = (
            -self.WORLD_WIDTH / 2.0
            + chunk_x * self.CHUNK_SIZE
        )

        world_z0 = (
            -self.WORLD_DEPTH / 2.0
            + chunk_z * self.CHUNK_SIZE
        )

        world_x1 = min(
            world_x0 + self.CHUNK_SIZE,
            self.WORLD_WIDTH / 2.0,
        )

        world_z1 = min(
            world_z0 + self.CHUNK_SIZE,
            self.WORLD_DEPTH / 2.0,
        )

        # Conversion des limites mondiales en indices de heightmap.
        col0 = int(round(
            (world_x0 + self.WORLD_WIDTH / 2.0)
            / self.WORLD_WIDTH
            * (map_width - 1)
        ))

        col1 = int(round(
            (world_x1 + self.WORLD_WIDTH / 2.0)
            / self.WORLD_WIDTH
            * (map_width - 1)
        ))

        row0 = int(round(
            (world_z0 + self.WORLD_DEPTH / 2.0)
            / self.WORLD_DEPTH
            * (map_height - 1)
        ))

        row1 = int(round(
            (world_z1 + self.WORLD_DEPTH / 2.0)
            / self.WORLD_DEPTH
            * (map_height - 1)
        ))

        col0 = int(np.clip(col0, 0, map_width - 2))
        col1 = int(np.clip(col1, col0 + 1, map_width - 1))

        row0 = int(np.clip(row0, 0, map_height - 2))
        row1 = int(np.clip(row1, row0 + 1, map_height - 1))

        heights = heightmap[
            row0:row1 + 1,
            col0:col1 + 1,
        ]

        rows, cols = heights.shape

        # Coordonnées calculées à partir des indices réels :
        # les sommets des chunks voisins coïncident exactement.
        x = (
            -self.WORLD_WIDTH / 2.0
            + np.arange(col0, col1 + 1, dtype=np.float32)
            / (map_width - 1)
            * self.WORLD_WIDTH
        )

        z = (
            -self.WORLD_DEPTH / 2.0
            + np.arange(row0, row1 + 1, dtype=np.float32)
            / (map_height - 1)
            * self.WORLD_DEPTH
        )

        xx, zz = np.meshgrid(x, z)
        yy = heights * self.WORLD_HEIGHT

        vertices = np.column_stack((
            xx.ravel(),
            yy.ravel(),
            zz.ravel(),
        )).astype(np.float32)

        faces = self._build_faces(cols, rows)

        # Couleurs du chunk.
        if self.color_map is not None:
            rgb = (
                self.color_map[row0:row1 + 1, col0:col1 + 1]
                .astype(np.float32) / 255.0
            ).reshape(-1, 3)

            alpha = np.ones(
                (rgb.shape[0], 1),
                dtype=np.float32,
            )

            colors = np.concatenate(
                (rgb, alpha),
                axis=1,
            )
        else:
            colors = np.empty(
                (rows * cols, 4),
                dtype=np.float32,
            )

            colors[:, 0] = 0.25
            colors[:, 1] = 0.55
            colors[:, 2] = 0.25
            colors[:, 3] = 1.0

        return visuals.Mesh(
            vertices=vertices,
            faces=faces,
            vertex_colors=colors,
            shading="smooth",
            parent=self.view.scene,
        )

    # ==============================================================
    # CHUNK STREAMING
    # ==============================================================

    def _update_terrain_chunks(self) -> None:
        """Ne conserve qu'un unique maillage : celui du chunk du joueur."""
        if self.heightmap is None:
            return
        world_x = self._server_x_to_world(self.local_x)
        world_z = self._server_y_to_world(self.local_y)
        center_chunk = self._chunk_coordinates(world_x, world_z)
        if center_chunk == self._last_chunk_center and len(self.terrain_chunks) <= 1:
            return
        self._last_chunk_center = center_chunk
        for key, mesh in list(self.terrain_chunks.items()):
            if key != center_chunk:
                mesh.parent = None
                del self.terrain_chunks[key]
        if center_chunk not in self.terrain_chunks:
            mesh = self._create_terrain_chunk(*center_chunk)
            if mesh is not None:
                self.terrain_chunks[center_chunk] = mesh
        print(f"[GAME] Chunk actif : {center_chunk}; maillages={len(self.terrain_chunks)}")

    # ==============================================================
    # CAMERA
    # ==============================================================

    def _place_camera_initially(self) -> None:
        """Centre la caméra orbitale sur la position initiale du joueur."""
        world_x = self._server_x_to_world(self.local_x)
        world_z = self._server_y_to_world(self.local_y)
        terrain_y = self._terrain_height_at(world_x, world_z)
        target = (world_x, terrain_y + self.PLAYER_HEIGHT, world_z)
        self.camera.center = target

        marker_pos = np.array(
            [[world_x, terrain_y + self.PLAYER_HEIGHT, world_z]],
            dtype=np.float32,
        )
        self.local_marker = visuals.Markers(
            pos=marker_pos,
            size=14,
            face_color=(1.0, 0.1, 0.1, 1.0),
            edge_color="white",
            parent=self.view.scene,
        )

        print(
            "[GAME] Caméra fixe de suivi prête : "
            f"joueur=({world_x:.1f}, {terrain_y:.1f}, {world_z:.1f}), "
            "distance=38, fov=48"
        )

    def _update_camera_position(self) -> None:
        """Suit le joueur avec le centre de l'orbite sans déplacer le terrain."""
        world_x = self._server_x_to_world(self.local_x)
        world_z = self._server_y_to_world(self.local_y)
        terrain_y = self._terrain_height_at(world_x, world_z)
        target_y = terrain_y + self.PLAYER_HEIGHT

        # Le centre est le point autour duquel TurntableCamera orbite.
        self.camera.center = (world_x, target_y, world_z)

        if self.local_marker is not None:
            self.local_marker.set_data(
                pos=np.array([[world_x, target_y, world_z]], dtype=np.float32),
                size=14,
                face_color=(1.0, 0.1, 0.1, 1.0),
                edge_color="white",
            )

    def _terrain_height_at(
        self,
        world_x: float,
        world_z: float,
    ) -> float:
        """Interpole la hauteur du terrain à une position mondiale."""

        if self.heightmap is None:
            return 0.0

        height, width = self.heightmap.shape

        normalized_x = float(np.clip(
            (world_x + self.WORLD_WIDTH / 2.0)
            / self.WORLD_WIDTH,
            0.0,
            1.0,
        ))

        normalized_z = float(np.clip(
            (world_z + self.WORLD_DEPTH / 2.0)
            / self.WORLD_DEPTH,
            0.0,
            1.0,
        ))

        px = normalized_x * (width - 1)
        pz = normalized_z * (height - 1)

        x0 = int(np.floor(px))
        z0 = int(np.floor(pz))

        x1 = min(x0 + 1, width - 1)
        z1 = min(z0 + 1, height - 1)

        fx = px - x0
        fz = pz - z0

        h00 = float(self.heightmap[z0, x0])
        h10 = float(self.heightmap[z0, x1])
        h01 = float(self.heightmap[z1, x0])
        h11 = float(self.heightmap[z1, x1])

        h0 = h00 * (1.0 - fx) + h10 * fx
        h1 = h01 * (1.0 - fx) + h11 * fx

        value = h0 * (1.0 - fz) + h1 * fz

        return value * self.WORLD_HEIGHT

    # ==============================================================
    def _sample_map_index(self, world_x: float, world_z: float) -> tuple[int, int]:
        """Coordonnées source cohérentes avec le maillage (colonne, ligne)."""
        assert self.heightmap is not None
        h, w = self.heightmap.shape
        col = int(round(np.clip((world_x + self.WORLD_WIDTH / 2) / self.WORLD_WIDTH, 0, 1) * (w - 1)))
        row = int(round(np.clip((world_z + self.WORLD_DEPTH / 2) / self.WORLD_DEPTH, 0, 1) * (h - 1)))
        return col, row

    def _slope_degrees_at(self, world_x: float, world_z: float) -> float:
        if self.heightmap is None:
            return 0.0
        step_x = self.WORLD_WIDTH / max(1, self.heightmap.shape[1] - 1)
        step_z = self.WORLD_DEPTH / max(1, self.heightmap.shape[0] - 1)
        gx = (self._terrain_height_at(world_x + step_x, world_z) -
              self._terrain_height_at(world_x - step_x, world_z)) / (2 * step_x)
        gz = (self._terrain_height_at(world_x, world_z + step_z) -
              self._terrain_height_at(world_x, world_z - step_z)) / (2 * step_z)
        return float(np.degrees(np.arctan(np.hypot(gx, gz))))

    def _terrain_multiplier(self, world_x: float, world_z: float,
                            old_world_x: float, old_world_z: float) -> float:
        biome = 0
        if self.biome_map is not None:
            col, row = self._sample_map_index(world_x, world_z)
            biome = int(self.biome_map[row, col])
        if biome == 1:
            return self.WATER_SPEED_MULTIPLIER
        if biome == 2:
            return self.SAND_SPEED_MULTIPLIER
        slope = self._slope_degrees_at(world_x, world_z)
        if slope >= self.MOUNTAIN_BLOCK_SLOPE_DEGREES:
            return 0.0
        if slope > self.MAX_WALKABLE_SLOPE_DEGREES:
            return 0.0
        old_h = self._terrain_height_at(old_world_x, old_world_z)
        new_h = self._terrain_height_at(world_x, world_z)
        if (biome == 3 or new_h > old_h + 0.05) and slope > 8.0:
            return self.MOUNTAIN_UPHILL_MULTIPLIER
        return 1.0

    # COORDINATE CONVERSION
    # ==============================================================

    def _server_x_to_world(self, x: float) -> float:
        """Serveur X -> VisPy X."""

        return x - self.WORLD_WIDTH / 2.0

    def _server_y_to_world(self, y: float) -> float:
        """Serveur Y horizontal -> VisPy Z."""

        return y - self.WORLD_DEPTH / 2.0

    def _world_x_to_server(self, x: float) -> int:
        return int(round(x + self.WORLD_WIDTH / 2.0))

    def _world_z_to_server(self, z: float) -> int:
        return int(round(z + self.WORLD_DEPTH / 2.0))

    # ==============================================================
    # NETWORK RECEIVE THREAD
    # ==============================================================

    def _network_loop(self) -> None:
        """Reçoit les paquets sans bloquer la boucle graphique."""

        try:
            print("[GAME] Connexion au serveur...")
            self.client.connect()
            print("[GAME] Connecté au serveur.")
        except Exception as exc:
            if self.running:
                print(f"[GAME] Connexion impossible : {exc}")
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
                    # La file est pleine : supprimer le paquet le
                    # plus ancien pour garder les données récentes.
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
                    print(f"[GAME] Erreur réseau : {exc}")
                break

    # ==============================================================
    # NETWORK PACKET PROCESSING
    # ==============================================================

    def _process_network_queue(self) -> None:
        """Traite les paquets sur le thread graphique."""

        for _ in range(100):
            try:
                packet = self.network_queue.get_nowait()
            except queue.Empty:
                break

            try:
                self._handle_packet(packet)
            except Exception as exc:
                print(f"[GAME] Erreur de traitement réseau : {exc}")

    def _handle_packet(self, packet) -> None:
        """Distribue les paquets selon leur type."""

        packet_type = getattr(packet, "packet_type", None)
        payload = getattr(packet, "payload", b"")

        if packet_type is None:
            packet_type = getattr(packet, "type", None)

        if packet_type == PacketType.SESSION:
            self._handle_session(payload)

        elif packet_type == PacketType.PLAYER_STATE:
            self._handle_player_state(payload)

        elif packet_type == PacketType.PLAYER_REMOVE:
            self._handle_player_remove(payload)

    def _handle_session(self, payload: bytes) -> None:
        """Traite le paquet SESSION contenant un UUID de 16 octets."""

        if len(payload) != 16:
            print(
                f"[GAME] SESSION invalide : {len(payload)} octets"
            )
            return

        try:
            session_id = uuid.UUID(bytes=payload)
            self.client.session_id = session_id
            print(f"[GAME] Session : {session_id}")
        except (ValueError, AttributeError, TypeError) as exc:
            print(f"[GAME] SESSION invalide : {exc}")

    def _handle_player_state(self, payload: bytes) -> None:
        """Traite UUID + x/y/z sous forme de trois entiers signés."""

        if len(payload) != 28:
            print(
                "[GAME] PLAYER_STATE invalide : "
                f"{len(payload)} octets"
            )
            return

        try:
            player_id = uuid.UUID(bytes=payload[:16])
            x, y, z = struct.unpack("!iii", payload[16:28])
        except (ValueError, struct.error):
            print("[GAME] PLAYER_STATE invalide.")
            return

        local_id = self._get_local_player_id()

        if local_id is not None and player_id == local_id:
            self.local_x = float(np.clip(x, 0, self.WORLD_WIDTH))
            self.local_y = float(np.clip(y, 0, self.WORLD_DEPTH))
            self.local_z = float(z)
            self._last_sent_position = (int(x), int(y), int(z))
            return

        self.remote_players[player_id] = (x, y, z)

        self._create_or_update_remote_player(
            player_id,
            x,
            y,
            z,
        )

    def _handle_player_remove(self, payload: bytes) -> None:
        """Supprime un joueur distant."""

        if len(payload) != 16:
            print(
                "[GAME] PLAYER_REMOVE invalide : "
                f"{len(payload)} octets"
            )
            return

        try:
            player_id = uuid.UUID(bytes=payload)
        except ValueError:
            print("[GAME] UUID PLAYER_REMOVE invalide.")
            return

        self.remote_players.pop(player_id, None)

        visual = self.remote_visuals.pop(player_id, None)

        if visual is not None:
            visual.parent = None

        print(f"[GAME] Joueur supprimé : {player_id}")

    def _get_local_player_id(self) -> uuid.UUID | None:
        """Retourne l'identifiant de session local."""

        session_id = getattr(self.client, "session_id", None)

        if session_id is None:
            return None

        if isinstance(session_id, uuid.UUID):
            return session_id

        try:
            return uuid.UUID(str(session_id))
        except (ValueError, TypeError, AttributeError):
            return None

    # ==============================================================
    # REMOTE PLAYERS
    # ==============================================================

    def _create_or_update_remote_player(
        self,
        player_id: uuid.UUID,
        x: int,
        y: int,
        z: int,
    ) -> None:
        """Crée ou met à jour le marqueur d'un joueur distant."""

        world_x = self._server_x_to_world(x)
        world_z = self._server_y_to_world(y)

        terrain_y = self._terrain_height_at(
            world_x,
            world_z,
        )

        # Le serveur reste la source de la position verticale.
        # Le terrain sert de solution de repli si Z vaut zéro.
        world_y = (
            float(z)
            if z != 0
            else terrain_y + self.REMOTE_PLAYER_RADIUS
        )

        position = np.array(
            [[world_x, world_y, world_z]],
            dtype=np.float32,
        )

        visual = self.remote_visuals.get(player_id)

        if visual is None:
            visual = visuals.Markers(
                pos=position,
                size=self.REMOTE_PLAYER_SIZE,
                face_color="red",
                edge_color="white",
                parent=self.view.scene,
            )

            self.remote_visuals[player_id] = visual
        else:
            visual.set_data(
                pos=position,
                size=self.REMOTE_PLAYER_SIZE,
                face_color="red",
                edge_color="white",
            )

    # ==============================================================
    # MOVEMENT AND SERVER SYNCHRONIZATION
    # ==============================================================

    def _sync_camera_to_server(self) -> None:
        """Envoie uniquement les nouvelles coordonnées du joueur au serveur."""
        server_x = max(0, min(int(self.WORLD_WIDTH), int(round(self.local_x))))
        server_y = max(0, min(int(self.WORLD_DEPTH), int(round(self.local_y))))
        server_z = int(round(self.local_z))
        position = (server_x, server_y, server_z)

        if position == self._last_sent_position:
            return

        self._send_position_to_server(*position)
        self._last_sent_position = position

    def _move_player(self, dx: float, dz: float) -> None:
        """Déplace le joueur avec ralentissement de biome et collisions de pente."""
        length = float(np.hypot(dx, dz))
        if length == 0:
            return
        dx /= length
        dz /= length
        azimuth = np.deg2rad(45.0)
        forward_x, forward_z = np.sin(azimuth), np.cos(azimuth)
        right_x, right_z = np.cos(azimuth), -np.sin(azimuth)
        direction_x = right_x * dx + forward_x * dz
        direction_z = right_z * dx + forward_z * dz
        old_x = self._server_x_to_world(self.local_x)
        old_z = self._server_y_to_world(self.local_y)

        # Le biome est évalué à l'emplacement visé ; son multiplicateur agit
        # réellement sur la distance, pas seulement sur l'affichage.
        probe_x = float(np.clip(self.local_x + direction_x * self.PLAYER_SPEED,
                                0, self.WORLD_WIDTH))
        probe_y = float(np.clip(self.local_y + direction_z * self.PLAYER_SPEED,
                                0, self.WORLD_DEPTH))
        probe_wx = self._server_x_to_world(probe_x)
        probe_wz = self._server_y_to_world(probe_y)
        multiplier = self._terrain_multiplier(probe_wx, probe_wz, old_x, old_z)
        if multiplier <= 0:
            # Une pente trop raide bloque le mouvement vers l'avant, mais le
            # joueur peut toujours glisser latéralement le long de l'obstacle.
            return
        distance = self.PLAYER_SPEED * multiplier
        candidate_x = float(np.clip(self.local_x + direction_x * distance, 0, self.WORLD_WIDTH))
        candidate_y = float(np.clip(self.local_y + direction_z * distance, 0, self.WORLD_DEPTH))
        new_x = self._server_x_to_world(candidate_x)
        new_z = self._server_y_to_world(candidate_y)

        travel = float(np.hypot(new_x - old_x, new_z - old_z))
        steps = max(1, int(np.ceil(travel / self.COLLISION_SAMPLE_STEP)))
        accepted_x, accepted_z = old_x, old_z
        for i in range(1, steps + 1):
            t = i / steps
            test_x = old_x + (new_x - old_x) * t
            test_z = old_z + (new_z - old_z) * t
            if self._terrain_multiplier(test_x, test_z, accepted_x, accepted_z) <= 0:
                break
            accepted_x, accepted_z = test_x, test_z

        self.local_x = float(np.clip(accepted_x + self.WORLD_WIDTH / 2, 0, self.WORLD_WIDTH))
        self.local_y = float(np.clip(accepted_z + self.WORLD_DEPTH / 2, 0, self.WORLD_DEPTH))
        self.local_z = self._terrain_height_at(accepted_x, accepted_z)
        self._update_camera_position()
        self._update_terrain_chunks()
        self._sync_camera_to_server()

    def _send_position_to_server(
        self,
        x: int,
        y: int,
        z: int,
    ) -> None:
        """Envoie un paquet MOVE."""

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
            print(f"[GAME] Impossible d'envoyer MOVE : {exc}")

    # ==============================================================
    # GAME LOOP
    # ==============================================================

    def _update(self, event) -> None:
        """Boucle principale exécutée sur le thread VisPy."""

        if not self.running:
            return

        self._process_network_queue()
        self._update_camera_position()
        self._update_terrain_chunks()
        self._sync_camera_to_server()

        self.update()

    # ==============================================================
    # INPUT
    # ==============================================================

    def _on_key_press(self, event) -> None:
        """Contrôles : flèches/WASD pour se déplacer, Échap pour quitter."""
        key = getattr(event, "key", None)
        if key is None:
            return

        key_name = str(getattr(key, "name", key)).lower()
        key_name = key_name.replace("key_", "").replace("arrow", "")

        if key_name in ("escape", "esc"):
            self.close()
            return

        # Flèches ou WASD. La caméra reste orbitale ; elle ne se déplace
        # pas librement et ne contrôle plus directement les coordonnées joueur.
        movement = {
            "up": (0.0, 1.0), "w": (0.0, 1.0),
            "down": (0.0, -1.0), "s": (0.0, -1.0),
            "left": (-1.0, 0.0), "a": (-1.0, 0.0),
            "right": (1.0, 0.0), "d": (1.0, 0.0),
        }
        if key_name in movement:
            self._move_player(*movement[key_name])

    def _on_key_release(self, event) -> None:
        """Aucun état de touche maintenue n'est nécessaire pour le moment."""
        pass

    def _on_mouse_press(self, event) -> None:
        """TurntableCamera gère l'orbite et le zoom à la souris."""
        pass

    # ==============================================================
    # SHUTDOWN
    # ==============================================================

    def on_close(self, event) -> None:
        """Arrête proprement le client et son thread réseau."""

        if not self.running:
            return

        self.running = False

        print("[GAME] Arrêt du client 3D...")

        try:
            self.timer.stop()
        except Exception:
            pass

        # Déconnecter le client débloque normalement la réception.
        try:
            if self.client.connected:
                self.client.disconnect("Arrêt normal")
        except Exception as exc:
            print(f"[GAME] Erreur déconnexion : {exc}")

        if (
            self.network_thread.is_alive()
            and threading.current_thread() is not self.network_thread
        ):
            self.network_thread.join(timeout=1.0)

        print("[GAME] Client 3D arrêté.")




class VispyWidget:
    """
    Adaptateur de lancement : héberge le canvas VisPy existant dans une
    fenêtre Qt. Le terrain en chunks et le réseau restent gérés par Game.

    joueur_obj est facultatif : il permet de garder une référence vers
    l'objet métier du joueur si le reste de l'application en possède un.
    """
    def __init__(self, client: Client, joueur_obj=None):
        

        self.joueur = joueur_obj
        self.open_tresors = []
        self.game = Game(client)

        self.window = QtWidgets.QMainWindow()
        self.window.setWindowTitle("The Last Signal")
        self.window.resize(1280, 760)

        central = QtWidgets.QWidget(self.window)
        layout = QtWidgets.QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Game est un SceneCanvas VisPy ; .native est son widget Qt.
        layout.addWidget(self.game.native, stretch=1)

        self.info_text = QtWidgets.QTextEdit(central)
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(80)
        self.info_text.setPlainText(
            "The Last Signal — Échap : quitter. "
            "Le déplacement et la synchronisation réseau sont gérés par le client 3D."
        )
        layout.addWidget(self.info_text)

        self.window.setCentralWidget(central)
        self.window.installEventFilter(self)

        # Le canvas reçoit les événements clavier pour garder les contrôles VisPy.
        self.game.native.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.game.native.setFocus()

    def show(self):
        self.window.show()
        self.game.native.setFocus()

    def close(self):
        self.game.close()
        self.window.close()

    def eventFilter(self, watched, event):
        # La fermeture de la fenêtre doit également arrêter le thread réseau.
        
        if (
            watched is self.window
            and event.type() == QtCore.QEvent.Type.Close
        ):
            self.game.close()
        return False


def run_game(client: Client | None = None, joueur_obj=None) -> None:
    """Lance le client 3D dans une fenêtre Qt."""

    if client is None:
        client = Client()

    widget = VispyWidget(client, joueur_obj=joueur_obj)
    widget.show()
    app.run()
