from __future__ import annotations
import math
import queue
import struct
import threading
import time
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


class FixedFollowCamera(scene.cameras.TurntableCamera):
    """Caméra de suivi pilotée uniquement par le code.

    TurntableCamera se connecte aux événements souris/clavier du ViewBox
    (orbite, zoom, translation, reset). On neutralise ici ces deux
    gestionnaires : ni la souris, ni les flèches, ni la molette ne peuvent
    déplacer ou faire tourner la caméra. Les événements clavier/souris du
    canvas (déplacement du joueur, Échap) ne sont pas affectés.
    """

    def viewbox_mouse_event(self, event):
        return None

    def viewbox_key_event(self, event):
        return None


class Game(scene.SceneCanvas):
    """Client 3D de The Last Signal avec terrain découpé en chunks."""

    # ==============================================================
    # WORLD
    # ==============================================================

    WORLD_WIDTH = 1000.0
    WORLD_DEPTH = 1000.0
    # Amplitude verticale totale (sommet des montagnes). 120 rendait les
    # bords de montagne quasi verticaux (pente > 80°) ; 40 les rend
    # franchissables par endroits tout en gardant un relief net.
    WORLD_HEIGHT = 40.0

    # Taille maximale de la heightmap après réduction (une 8192x8192 est
    # réduite une seule fois au chargement, jamais par frame).
    MAX_TERRAIN_SIZE = 1024

    # map_height.png : le noir correspond aux montagnes et le blanc au sol
    # bas / à l'eau (vérifié sur les données). L'altitude = 1 - valeur.
    INVERT_HEIGHT = True

    # Lissage gaussien de l'altitude, exprimé en unités du monde
    # (indépendant de la résolution de l'image). 0 = désactivé.
    HEIGHT_SMOOTH_SIGMA = 5.0

    # Taille d'un chunk en unités du monde.
    CHUNK_SIZE = 64.0

    # Conservé pour compatibilité : 0 = un seul chunk (le chunk actif).
    RENDER_DISTANCE = 0

    # Marge (unités) avant de changer de chunk : évite de reconstruire le
    # maillage en boucle quand le joueur longe une frontière.
    CHUNK_SWITCH_MARGIN = 3.0

    # Éclairage cuit dans les couleurs de sommet. 0.0 = couleurs EXACTES de
    # map_color.png (défaut). Une valeur entre 0 et 1 ajoute un léger relief
    # ombré ; le sol plat garde sa couleur d'origine.
    RELIEF_SHADING_STRENGTH = 0.0
    RELIEF_LIGHT_DIRECTION = (0.45, 0.80, 0.40)

    # Joueur.
    PLAYER_HEIGHT = 1.8              # hauteur du point visé par la caméra
    MARKER_HEIGHT = 1.0              # hauteur du marqueur rouge du joueur
    PLAYER_SPEED = 12.0              # unités par seconde en terrain normal
    WATER_SPEED_MULTIPLIER = 0.20
    SAND_SPEED_MULTIPLIER = 0.70
    MOUNTAIN_UPHILL_MULTIPLIER = 0.40
    MAX_WALKABLE_SLOPE_DEGREES = 38.0       # pente de la marche (montée)
    MOUNTAIN_BLOCK_SLOPE_DEGREES = 52.0     # falaise : montée interdite
    UPHILL_SLOW_MIN_DEGREES = 6.0           # pente à partir de laquelle on ralentit
    COLLISION_SAMPLE_STEP = 0.5             # pas max de test de collision

    # Caméra de suivi rapprochée (fixe en orientation).
    CAMERA_DISTANCE = 7.0
    CAMERA_ELEVATION = 24.0
    CAMERA_AZIMUTH = 45.0
    CAMERA_FOV = 55.0
    CAMERA_MIN_GROUND_CLEARANCE = 1.2
    CAMERA_LIFT_SMOOTHING = 0.25

    # Classification des biomes (tolérances configurables).
    BLUE_MIN = 75
    BLUE_OVER_RED = 1.18
    BLUE_OVER_GREEN = 1.10
    SAND_MIN_RED = 150
    SAND_MIN_RED_MINUS_BLUE = 35
    GRAY_CHANNEL_TOLERANCE = 14
    GRAY_MIN = 60
    GRAY_MAX = 215
    # Codes observés dans map_collision.png : R=20 eau, R=70 sable,
    # R=100 terre ; B>=128 marque la zone montagneuse.
    COLLISION_CODE_WATER = 20
    COLLISION_CODE_SAND = 70
    COLLISION_CODE_TOLERANCE = 8
    COLLISION_MOUNTAIN_MIN_BLUE = 100

    BIOME_NORMAL = 0
    BIOME_WATER = 1
    BIOME_SAND = 2
    BIOME_MOUNTAIN = 3

    # Réseau.
    NETWORK_QUEUE_LIMIT = 100
    # Écart (unités) au-delà duquel une position serveur est une correction
    # (téléportation) ; en dessous c'est un simple écho de notre position.
    SERVER_CORRECTION_THRESHOLD = 4.0

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

        # Touches de déplacement maintenues.
        self._pressed_keys: set[str] = set()

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
        # ==========================================================

        self.view = self.central_widget.add_view()

        # Caméra de suivi rapprochée. Le terrain utilise Y comme axe
        # vertical (X, hauteur Y, profondeur Z) donc up="y".
        # FixedFollowCamera ignore souris, molette et clavier ; seul le code
        # modifie son centre. Orientation fixe (azimut/élévation constants).
        self.view.camera = FixedFollowCamera(
            elevation=self.CAMERA_ELEVATION,
            azimuth=self.CAMERA_AZIMUTH,
            distance=self.CAMERA_DISTANCE,
            fov=self.CAMERA_FOV,
            up="y",
            parent=self.view.scene,
        )
        self.view.camera.interactive = False
        self.camera = self.view.camera
        self._camera_lift = 0.0

        # ==========================================================
        # TERRAIN DATA
        # ==========================================================

        self.heightmap: np.ndarray | None = None
        # Couleurs et classes de biome sont conservées en uint8, sans conversion
        # RGB/BGR ni interpolation de couleurs qui inventerait des teintes.
        self.color_map: np.ndarray | None = None
        self.biome_map: np.ndarray | None = None
        self.collision_map: np.ndarray | None = None
        self.slope_map: np.ndarray | None = None
        self._grad_x: np.ndarray | None = None
        self._grad_z: np.ndarray | None = None
        self._last_update_time: float | None = None

        # (chunk_x, chunk_z) -> maillage VisPy. Contient au plus UN élément.
        self.terrain_chunks: dict[
            tuple[int, int], visuals.Mesh
        ] = {}

        self._last_chunk_center: tuple[int, int] | None = None

        self._load_terrain()
        self._place_camera_initially()
        self._update_terrain_chunks()

        # ==========================================================
        # TIMER
        # ==========================================================

        self.timer = app.Timer(
            interval=1.0 / 60.0,
            connect=self._update,
            start=True,
        )

        # ==========================================================
        # EVENTS
        # ==========================================================

        self.events.key_press.connect(self._on_key_press)
        self.events.key_release.connect(self._on_key_release)
        self.events.mouse_press.connect(self._on_mouse_press)

        # ==========================================================
        # NETWORK THREAD
        # ==========================================================

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

    @staticmethod
    def _gaussian_blur(data: np.ndarray, sigma: float) -> np.ndarray:
        """Flou gaussien séparable en float32 (pas de quantification 8 bits)."""
        if sigma <= 0.05:
            return data.astype(np.float32, copy=False)
        radius = max(1, int(math.ceil(3.0 * sigma)))
        offsets = np.arange(-radius, radius + 1, dtype=np.float32)
        kernel = np.exp(-(offsets ** 2) / (2.0 * sigma * sigma))
        kernel /= kernel.sum()
        h, w = data.shape

        padded = np.pad(data, ((0, 0), (radius, radius)), mode="edge")
        horizontal = np.zeros((h, w), dtype=np.float32)
        for i, weight in enumerate(kernel):
            horizontal += weight * padded[:, i:i + w]

        padded = np.pad(horizontal, ((radius, radius), (0, 0)), mode="edge")
        result = np.zeros((h, w), dtype=np.float32)
        for i, weight in enumerate(kernel):
            result += weight * padded[i:i + h, :]
        return result

    def _load_terrain(self) -> None:
        """Charge les cartes et prépare altitude lissée, couleurs et biomes."""
        assets = self._assets_directory()
        height_path = assets / "map_height.png"
        color_path = assets / "map_color.png"
        collision_path = assets / "map_collision.png"
        if not height_path.is_file():
            raise FileNotFoundError(f"Heightmap introuvable : {height_path}")

        # --- Altitude : réduction éventuelle, normalisation, inversion,
        # lissage en float32 -------------------------------------------
        with Image.open(height_path) as image:
            print(f"[GAME] Heightmap source : {image.size}, mode={image.mode}")
            gray = image.convert("L")
            width, height = gray.size
            largest = max(width, height)
            if largest > self.MAX_TERRAIN_SIZE:
                scale = largest / self.MAX_TERRAIN_SIZE
                gray = gray.resize(
                    (max(2, int(round(width / scale))),
                     max(2, int(round(height / scale)))),
                    Image.Resampling.BOX,
                )
            source = np.asarray(gray, dtype=np.float32) / 255.0

        low, high = float(source.min()), float(source.max())
        if high > low:
            source = (source - low) / (high - low)
        else:
            source = np.zeros_like(source)
        if self.INVERT_HEIGHT:
            source = 1.0 - source

        terrain_height, terrain_width = source.shape
        spacing_x = self.WORLD_WIDTH / max(1, terrain_width - 1)
        sigma_px = self.HEIGHT_SMOOTH_SIGMA / spacing_x
        self.heightmap = np.ascontiguousarray(
            self._gaussian_blur(source, sigma_px), dtype=np.float32
        )

        # --- Pente et gradients (une seule fois) -----------------------
        spacing_z = self.WORLD_DEPTH / max(1, terrain_height - 1)
        grad_z, grad_x = np.gradient(
            self.heightmap * self.WORLD_HEIGHT, spacing_z, spacing_x
        )
        self._grad_x = grad_x.astype(np.float32)
        self._grad_z = grad_z.astype(np.float32)
        self.slope_map = np.degrees(
            np.arctan(np.hypot(grad_x, grad_z))
        ).astype(np.float32)

        # --- Couleurs : jamais lissées ni modifiées --------------------
        if color_path.is_file():
            with Image.open(color_path) as image:
                print(f"[GAME] Couleurs source : {image.size}, mode={image.mode}")
                color = image.convert("RGB")
                if color.size != (terrain_width, terrain_height):
                    # NEAREST : aucune couleur intermédiaire inventée.
                    color = color.resize(
                        (terrain_width, terrain_height),
                        Image.Resampling.NEAREST,
                    )
                self.color_map = np.asarray(color, dtype=np.uint8).copy()
        else:
            self.color_map = None
            print("[GAME] map_color.png absent : couleurs de repli.")

        # --- Collision : codes observés (voir constantes COLLISION_*) --
        if collision_path.is_file():
            with Image.open(collision_path) as image:
                print(f"[GAME] Collision source : {image.size}, mode={image.mode}")
                collision = image.convert("RGB")
                if collision.size != (terrain_width, terrain_height):
                    collision = collision.resize(
                        (terrain_width, terrain_height),
                        Image.Resampling.NEAREST,
                    )
                self.collision_map = np.asarray(collision, dtype=np.uint8).copy()
        else:
            self.collision_map = None
            print("[GAME] map_collision.png absent : biomes via map_color seul.")

        self.biome_map = self._classify_biomes(self.color_map, self.collision_map)

        print(f"[GAME] Terrain préparé : {terrain_width} x {terrain_height}; "
              f"chunk={self.CHUNK_SIZE:g}; rendu=1 chunk; "
              f"sigma={sigma_px:.2f}px")

    def _classify_biomes(
        self,
        rgb: np.ndarray | None,
        collision: np.ndarray | None = None,
    ) -> np.ndarray:
        """Classes 0=normal, 1=eau, 2=sable, 3=montagne.

        Priorité : eau > montagne grise > sable > zone montagneuse de
        map_collision. La couleur est comparée avec tolérances ; map_collision
        confirme l'eau et le sable (codes R) et ajoute la zone montagneuse (B).
        """
        if rgb is not None:
            shape = rgb.shape[:2]
        elif collision is not None:
            shape = collision.shape[:2]
        else:
            return np.zeros(self.heightmap.shape, dtype=np.uint8)

        water = np.zeros(shape, dtype=bool)
        sand = np.zeros(shape, dtype=bool)
        gray = np.zeros(shape, dtype=bool)
        coll_mountain = np.zeros(shape, dtype=bool)

        if rgb is not None:
            c = rgb.astype(np.int16)
            r, g, b = c[..., 0], c[..., 1], c[..., 2]
            water |= ((b >= self.BLUE_MIN)
                      & (b > r * self.BLUE_OVER_RED)
                      & (b > g * self.BLUE_OVER_GREEN))
            # Sable : beige chaud (R > G > B). Le gris clair des sommets
            # (R≈G≈B) n'est donc plus pris pour du sable.
            sand |= ((r >= self.SAND_MIN_RED)
                     & ((r - b) >= self.SAND_MIN_RED_MINUS_BLUE)
                     & (g > b) & (r >= g - 4) & ~water)
            tol = self.GRAY_CHANNEL_TOLERANCE
            gray |= ((np.abs(r - g) <= tol) & (np.abs(g - b) <= tol)
                     & (b >= r - 10)
                     & (r >= self.GRAY_MIN) & (r <= self.GRAY_MAX)
                     & ~water & ~sand)

        if collision is not None:
            cr = collision[..., 0].astype(np.int16)
            cb = collision[..., 2].astype(np.int16)
            tol = self.COLLISION_CODE_TOLERANCE
            water |= np.abs(cr - self.COLLISION_CODE_WATER) <= tol
            sand |= (np.abs(cr - self.COLLISION_CODE_SAND) <= tol) & ~water
            coll_mountain = cb >= self.COLLISION_MOUNTAIN_MIN_BLUE

        result = np.zeros(shape, dtype=np.uint8)
        result[coll_mountain] = self.BIOME_MOUNTAIN
        result[sand] = self.BIOME_SAND
        result[gray] = self.BIOME_MOUNTAIN
        result[water] = self.BIOME_WATER
        return result

    # ==============================================================
    # MESH HELPERS
    # ==============================================================

    @staticmethod
    def _build_faces(
        width: int,
        height: int,
    ) -> np.ndarray:
        """Construit deux triangles pour chaque cellule du maillage.

        La diagonale de chaque cellule va de b (haut-droite) à c (bas-gauche) ;
        _heights_at() interpole exactement sur ces mêmes triangles.
        """

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

        # Ordre des sommets orienté vers le haut (+Y).
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

    def _chunk_world_bounds(
        self,
        chunk_x: int,
        chunk_z: int,
    ) -> tuple[float, float, float, float]:
        """(x0, z0, x1, z1) du chunk en coordonnées monde."""
        x0 = -self.WORLD_WIDTH / 2.0 + chunk_x * self.CHUNK_SIZE
        z0 = -self.WORLD_DEPTH / 2.0 + chunk_z * self.CHUNK_SIZE
        x1 = min(-self.WORLD_WIDTH / 2.0 + (chunk_x + 1) * self.CHUNK_SIZE,
                 self.WORLD_WIDTH / 2.0)
        z1 = min(-self.WORLD_DEPTH / 2.0 + (chunk_z + 1) * self.CHUNK_SIZE,
                 self.WORLD_DEPTH / 2.0)
        return x0, z0, x1, z1

    def _chunk_edge_pixel(self, edge_index: int, axis_length: float,
                          pixel_count: int) -> int:
        """Indice pixel de la frontière numéro edge_index.

        Même fonction pour la fin du chunk k et le début du chunk k+1 : les
        sommets frontières sont donc strictement identiques (pas de trou).
        """
        position = min(edge_index * self.CHUNK_SIZE, axis_length)
        return int(round(position / axis_length * (pixel_count - 1)))

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

        col0 = self._chunk_edge_pixel(chunk_x, self.WORLD_WIDTH, map_width)
        col1 = self._chunk_edge_pixel(chunk_x + 1, self.WORLD_WIDTH, map_width)
        row0 = self._chunk_edge_pixel(chunk_z, self.WORLD_DEPTH, map_height)
        row1 = self._chunk_edge_pixel(chunk_z + 1, self.WORLD_DEPTH, map_height)

        col0 = int(np.clip(col0, 0, map_width - 2))
        col1 = int(np.clip(col1, col0 + 1, map_width - 1))
        row0 = int(np.clip(row0, 0, map_height - 2))
        row1 = int(np.clip(row1, row0 + 1, map_height - 1))

        heights = heightmap[row0:row1 + 1, col0:col1 + 1]
        rows, cols = heights.shape

        # Coordonnées calculées à partir des indices pixel globaux : un
        # sommet a la même position quel que soit le chunk qui le produit.
        x = (
            -self.WORLD_WIDTH / 2.0
            + np.arange(col0, col1 + 1, dtype=np.float64)
            / (map_width - 1)
            * self.WORLD_WIDTH
        )

        z = (
            -self.WORLD_DEPTH / 2.0
            + np.arange(row0, row1 + 1, dtype=np.float64)
            / (map_height - 1)
            * self.WORLD_DEPTH
        )

        xx, zz = np.meshgrid(x, z)
        yy = heights.astype(np.float64) * self.WORLD_HEIGHT

        vertices = np.column_stack((
            xx.ravel(),
            yy.ravel(),
            zz.ravel(),
        )).astype(np.float32)

        faces = self._build_faces(cols, rows)

        # Couleurs : un sommet par pixel, couleur du pixel copiée telle
        # quelle (même grille que l'altitude : correspondance pixel à pixel).
        if self.color_map is not None:
            rgb = (
                self.color_map[row0:row1 + 1, col0:col1 + 1]
                .astype(np.float32) / 255.0
            ).reshape(-1, 3)
        else:
            rgb = np.empty((rows * cols, 3), dtype=np.float32)
            rgb[:, 0] = 0.25
            rgb[:, 1] = 0.55
            rgb[:, 2] = 0.25

        strength = float(self.RELIEF_SHADING_STRENGTH)
        if strength > 0.0 and self._grad_x is not None:
            gx = self._grad_x[row0:row1 + 1, col0:col1 + 1].ravel()
            gz = self._grad_z[row0:row1 + 1, col0:col1 + 1].ravel()
            normal = np.stack((-gx, np.ones_like(gx), -gz), axis=1)
            normal /= np.linalg.norm(normal, axis=1, keepdims=True)
            light = np.asarray(self.RELIEF_LIGHT_DIRECTION, dtype=np.float32)
            light /= np.linalg.norm(light)
            lambert = np.clip(normal @ light, 0.0, 1.0)
            # Sol plat (normale verticale) -> facteur 1.0 : couleur intacte.
            factor = 1.0 + strength * (lambert - light[1]) / light[1]
            rgb = np.clip(rgb * np.clip(factor, 0.2, 1.15)[:, None], 0.0, 1.0)

        colors = np.concatenate(
            (rgb, np.ones((rgb.shape[0], 1), dtype=np.float32)),
            axis=1,
        ).astype(np.float32)

        # shading=None : aucun éclairage VisPy ne modifie les couleurs.
        return visuals.Mesh(
            vertices=vertices,
            faces=faces,
            vertex_colors=colors,
            shading=None,
            parent=self.view.scene,
        )

    # ==============================================================
    # CHUNK STREAMING
    # ==============================================================

    def _chunk_contains(self, chunk: tuple[int, int], world_x: float,
                        world_z: float, margin: float) -> bool:
        x0, z0, x1, z1 = self._chunk_world_bounds(*chunk)
        return (x0 - margin <= world_x <= x1 + margin
                and z0 - margin <= world_z <= z1 + margin)

    def _update_terrain_chunks(self) -> None:
        """Ne conserve qu'un unique maillage : celui du chunk du joueur."""
        if self.heightmap is None:
            return
        world_x = self._server_x_to_world(self.local_x)
        world_z = self._server_y_to_world(self.local_y)

        active = self._last_chunk_center
        if (active is not None and active in self.terrain_chunks
                and len(self.terrain_chunks) == 1
                and self._chunk_contains(active, world_x, world_z,
                                         self.CHUNK_SWITCH_MARGIN)):
            return

        new_chunk = self._chunk_coordinates(world_x, world_z)
        if new_chunk == active and new_chunk in self.terrain_chunks \
                and len(self.terrain_chunks) == 1:
            return

        # Le nouveau maillage est créé avant de retirer l'ancien : aucune
        # frame sans terrain pendant la transition.
        new_mesh = None
        if new_chunk not in self.terrain_chunks:
            new_mesh = self._create_terrain_chunk(*new_chunk)

        for key, mesh in list(self.terrain_chunks.items()):
            if key != new_chunk:
                mesh.parent = None
                del self.terrain_chunks[key]
        if new_mesh is not None:
            self.terrain_chunks[new_chunk] = new_mesh

        self._last_chunk_center = new_chunk
        print(f"[GAME] Chunk actif : {new_chunk}; "
              f"maillages={len(self.terrain_chunks)}")

    # ==============================================================
    # CAMERA
    # ==============================================================

    def _place_camera_initially(self) -> None:
        """Centre la caméra sur la position initiale du joueur."""
        world_x = self._server_x_to_world(self.local_x)
        world_z = self._server_y_to_world(self.local_y)
        terrain_y = self._terrain_height_at(world_x, world_z)
        self.local_z = terrain_y
        self._camera_lift = 0.0
        self.camera.center = (world_x, terrain_y + self.PLAYER_HEIGHT, world_z)

        marker_pos = np.array(
            [[world_x, terrain_y + self.MARKER_HEIGHT, world_z]],
            dtype=np.float32,
        )
        self.local_marker = visuals.Markers(
            pos=marker_pos,
            size=14,
            face_color=(1.0, 0.1, 0.1, 1.0),
            edge_color="white",
            parent=self.view.scene,
        )
        self._update_camera_position()

        print(
            "[GAME] Caméra de suivi prête : "
            f"joueur=({world_x:.1f}, {terrain_y:.1f}, {world_z:.1f}), "
            f"distance={self.CAMERA_DISTANCE:g}, fov={self.CAMERA_FOV:g}"
        )

    def _required_camera_lift(self, world_x: float, world_z: float,
                              eye_y: float) -> float:
        """Hauteur supplémentaire pour que la caméra reste au-dessus du sol.

        La position exacte de la caméra dépend de la convention d'azimut de
        VisPy ; on teste donc le terrain sur tout le cercle de rayon
        distance*cos(élévation) (et à mi-rayon) : estimation conservatrice,
        indépendante de la convention.
        """
        elevation = math.radians(self.CAMERA_ELEVATION)
        horizontal = self.CAMERA_DISTANCE * math.cos(elevation)
        camera_rise = self.CAMERA_DISTANCE * math.sin(elevation)
        angles = np.linspace(0.0, 2.0 * math.pi, 16, endpoint=False)
        radii = np.array([0.5 * horizontal, horizontal])
        xs = (world_x + np.outer(radii, np.cos(angles))).ravel()
        zs = (world_z + np.outer(radii, np.sin(angles))).ravel()
        highest = float(self._heights_at(xs, zs).max())
        needed = highest + self.CAMERA_MIN_GROUND_CLEARANCE
        return max(0.0, needed - (eye_y + camera_rise))

    def _update_camera_position(self) -> None:
        """Suit le joueur : seul le centre de la caméra change."""
        world_x = self._server_x_to_world(self.local_x)
        world_z = self._server_y_to_world(self.local_y)
        terrain_y = self._terrain_height_at(world_x, world_z)
        self.local_z = terrain_y
        eye_y = terrain_y + self.PLAYER_HEIGHT

        target_lift = self._required_camera_lift(world_x, world_z, eye_y)
        # Montée immédiate (jamais sous le sol), descente progressive.
        if target_lift > self._camera_lift:
            self._camera_lift = target_lift
        else:
            self._camera_lift += (
                (target_lift - self._camera_lift) * self.CAMERA_LIFT_SMOOTHING
            )

        self.camera.center = (world_x, eye_y + self._camera_lift, world_z)

        if self.local_marker is not None:
            self.local_marker.set_data(
                pos=np.array(
                    [[world_x, terrain_y + self.MARKER_HEIGHT, world_z]],
                    dtype=np.float32,
                ),
                size=14,
                face_color=(1.0, 0.1, 0.1, 1.0),
                edge_color="white",
            )

    def _heights_at(self, world_x, world_z) -> np.ndarray:
        """Altitude (unités monde) aux positions données, vectorisée.

        Interpolation exacte sur les triangles du maillage (diagonale b-c),
        donc le joueur marche sur la surface réellement affichée.
        """
        height, width = self.heightmap.shape
        nx = np.clip((np.asarray(world_x, dtype=np.float64)
                      + self.WORLD_WIDTH / 2.0) / self.WORLD_WIDTH, 0.0, 1.0)
        nz = np.clip((np.asarray(world_z, dtype=np.float64)
                      + self.WORLD_DEPTH / 2.0) / self.WORLD_DEPTH, 0.0, 1.0)
        px = nx * (width - 1)
        pz = nz * (height - 1)

        x0 = np.minimum(np.floor(px).astype(np.intp), width - 2)
        z0 = np.minimum(np.floor(pz).astype(np.intp), height - 2)
        fx = px - x0
        fz = pz - z0

        hm = self.heightmap
        ha = hm[z0, x0]
        hb = hm[z0, x0 + 1]
        z1 = z0 + 1
        hc = hm[z1, x0]
        hd = hm[z1, x0 + 1]

        lower = (fx + fz) <= 1.0
        value = np.where(
            lower,
            ha + fx * (hb - ha) + fz * (hc - ha),
            hd + (1.0 - fx) * (hc - hd) + (1.0 - fz) * (hb - hd),
        )
        return value * self.WORLD_HEIGHT

    def _terrain_height_at(
        self,
        world_x: float,
        world_z: float,
    ) -> float:
        """Altitude du terrain à une position mondiale."""

        if self.heightmap is None:
            return 0.0
        return float(self._heights_at(np.float64(world_x),
                                      np.float64(world_z)))

    # ==============================================================
    # TERRAIN QUERIES
    # ==============================================================

    def _sample_map_index(self, world_x: float, world_z: float) -> tuple[int, int]:
        """Coordonnées source cohérentes avec le maillage (colonne, ligne)."""
        assert self.heightmap is not None
        h, w = self.heightmap.shape
        col = int(round(np.clip((world_x + self.WORLD_WIDTH / 2) / self.WORLD_WIDTH, 0, 1) * (w - 1)))
        row = int(round(np.clip((world_z + self.WORLD_DEPTH / 2) / self.WORLD_DEPTH, 0, 1) * (h - 1)))
        return col, row

    def _slope_degrees_at(self, world_x: float, world_z: float) -> float:
        """Pente du terrain (précalculée au chargement)."""
        if self.slope_map is None:
            return 0.0
        col, row = self._sample_map_index(world_x, world_z)
        return float(self.slope_map[row, col])

    def _biome_at(self, world_x: float, world_z: float) -> int:
        if self.biome_map is None:
            return self.BIOME_NORMAL
        col, row = self._sample_map_index(world_x, world_z)
        return int(self.biome_map[row, col])

    def _terrain_multiplier(self, world_x: float, world_z: float,
                            old_world_x: float, old_world_z: float) -> float:
        """Multiplicateur de vitesse pour aller de old vers (x, z).

        Retourne 0.0 si le passage est bloqué. Appliqué à chaque sous-pas du
        déplacement, jamais déduit de la couleur affichée.
        """
        biome = self._biome_at(world_x, world_z)

        new_h = self._terrain_height_at(world_x, world_z)
        old_h = self._terrain_height_at(old_world_x, old_world_z)
        distance = max(0.05, math.hypot(world_x - old_world_x,
                                        world_z - old_world_z))
        rise = new_h - old_h

        uphill_slope = 0.0
        if rise > 1e-4:
            # Pente réelle du déplacement (dénivelé / distance horizontale).
            uphill_slope = math.degrees(math.atan2(rise, distance))
            terrain_slope = self._slope_degrees_at(world_x, world_z)
            if uphill_slope > self.MAX_WALKABLE_SLOPE_DEGREES:
                return 0.0
            if terrain_slope >= self.MOUNTAIN_BLOCK_SLOPE_DEGREES:
                return 0.0

        if biome == self.BIOME_WATER:
            multiplier = self.WATER_SPEED_MULTIPLIER
        elif biome == self.BIOME_SAND:
            multiplier = self.SAND_SPEED_MULTIPLIER
        else:
            multiplier = 1.0

        if uphill_slope >= self.UPHILL_SLOW_MIN_DEGREES:
            multiplier = min(multiplier, self.MOUNTAIN_UPHILL_MULTIPLIER)
        return multiplier

    # ==============================================================
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
            # Le déplacement étant continu côté client, un écho serveur
            # retardé de notre propre position ne doit pas nous ramener en
            # arrière ; seule une vraie correction (écart important) ou la
            # position initiale est appliquée.
            last = self._last_sent_position
            if last is not None:
                gap = math.hypot(x - last[0], y - last[1])
                if gap <= self.SERVER_CORRECTION_THRESHOLD:
                    return
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

    def _move_player(self, dx: float, dz: float, dt: float = 1.0 / 60.0) -> bool:
        """Déplace le joueur pendant dt secondes.

        La distance totale est PLAYER_SPEED * dt, découpée en sous-pas de
        COLLISION_SAMPLE_STEP au plus : aucun obstacle ne peut être sauté,
        même à grande vitesse ou avec un dt élevé. Chaque sous-pas applique
        le multiplicateur du terrain visé (eau, sable, montée) et, si le
        sous-pas est bloqué, tente de glisser le long de l'obstacle.
        Retourne True si le joueur a bougé.
        """
        length = float(np.hypot(dx, dz))
        if length == 0 or dt <= 0:
            return False
        dx /= length
        dz /= length

        # Repère de déplacement lié à l'orientation FIXE de la caméra.
        azimuth = np.deg2rad(self.CAMERA_AZIMUTH)
        forward_x, forward_z = np.sin(azimuth), np.cos(azimuth)
        right_x, right_z = np.cos(azimuth), -np.sin(azimuth)
        direction_x = float(right_x * dx + forward_x * dz)
        direction_z = float(right_z * dx + forward_z * dz)

        x = self._server_x_to_world(self.local_x)
        z = self._server_y_to_world(self.local_y)
        half_w = self.WORLD_WIDTH / 2.0
        half_d = self.WORLD_DEPTH / 2.0

        budget = self.PLAYER_SPEED * dt
        sub_step = max(0.05, self.COLLISION_SAMPLE_STEP)
        moved = False

        while budget > 1e-6:
            step = min(sub_step, budget)
            budget -= step
            for vx, vz in ((direction_x, direction_z),
                           (direction_x, 0.0),
                           (0.0, direction_z)):
                if vx == 0.0 and vz == 0.0:
                    continue
                probe_x = float(np.clip(x + vx * step, -half_w, half_w))
                probe_z = float(np.clip(z + vz * step, -half_d, half_d))
                multiplier = self._terrain_multiplier(probe_x, probe_z, x, z)
                if multiplier <= 0.0:
                    continue
                x = float(np.clip(x + vx * step * multiplier, -half_w, half_w))
                z = float(np.clip(z + vz * step * multiplier, -half_d, half_d))
                moved = True
                break
            else:
                break  # bloqué dans toutes les directions testées

        if not moved:
            return False

        self.local_x = float(np.clip(x + half_w, 0, self.WORLD_WIDTH))
        self.local_y = float(np.clip(z + half_d, 0, self.WORLD_DEPTH))
        self.local_z = self._terrain_height_at(x, z)
        return True

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

    def _held_direction(self) -> tuple[float, float]:
        """Direction de déplacement résultant des touches maintenues."""
        dx = (1.0 if "right" in self._pressed_keys or "d" in self._pressed_keys else 0.0) \
            - (1.0 if "left" in self._pressed_keys or "a" in self._pressed_keys else 0.0)
        dz = (1.0 if "up" in self._pressed_keys or "w" in self._pressed_keys else 0.0) \
            - (1.0 if "down" in self._pressed_keys or "s" in self._pressed_keys else 0.0)
        return dx, dz

    def _update(self, event) -> None:
        """Boucle principale exécutée sur le thread VisPy."""

        if not self.running:
            return

        now = time.perf_counter()
        if self._last_update_time is None:
            dt = 1.0 / 60.0
        else:
            dt = min(now - self._last_update_time, 0.1)
        self._last_update_time = now

        self._process_network_queue()

        dx, dz = self._held_direction()
        if dx or dz:
            self._move_player(dx, dz, dt)

        self._update_camera_position()
        self._update_terrain_chunks()
        self._sync_camera_to_server()

        self.update()

    # ==============================================================
    # INPUT
    # ==============================================================

    @staticmethod
    def _key_name(event) -> str | None:
        key = getattr(event, "key", None)
        if key is None:
            return None
        name = str(getattr(key, "name", key)).lower()
        return name.replace("key_", "").replace("arrow", "")

    def _on_key_press(self, event) -> None:
        """Contrôles : flèches/WASD pour se déplacer, Échap pour quitter.

        Les flèches ne pilotent que le personnage ; la caméra ignore tout
        événement clavier/souris (voir FixedFollowCamera).
        """
        key_name = self._key_name(event)
        if key_name is None:
            return

        if key_name in ("escape", "esc"):
            self.close()
            return

        if key_name in ("up", "w", "down", "s", "left", "a", "right", "d"):
            self._pressed_keys.add(key_name)

    def _on_key_release(self, event) -> None:
        """Relâche une touche de déplacement."""
        key_name = self._key_name(event)
        if key_name is not None:
            self._pressed_keys.discard(key_name)

    def _on_mouse_press(self, event) -> None:
        """La souris ne contrôle plus la caméra ; rien à faire ici."""
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
            "The Last Signal — Flèches / WASD : se déplacer, Échap : quitter. "
            "La caméra suit automatiquement le personnage."
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
