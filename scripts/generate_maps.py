#!/usr/bin/env python3
"""Génère map_color.png, map_height.png, map_collision.png dans <racine du jeu>/assets.

    python scripts/generate_maps.py                 # 8192x8192
    python scripts/generate_maps.py --size 1024     # preview rapide
    python scripts/generate_maps.py --seed 42 --out maps
"""
from __future__ import annotations

import argparse
import time
import zlib
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None

GRASS, WATER, SAND, MOUNTAIN = 0, 1, 2, 3
BLOCKED_FLAG = 0x80  # bit posé dans le canal B de map_collision si pente > seuil
BAND = 256  # lignes traitées à la fois (limite la RAM)
ROOT = Path(__file__).resolve().parent.parent  # racine du jeu (parent de scripts/)
ASSETS = ROOT / "assets"


# ----------------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------------
@dataclass
class ColorTolerance:
    """Tolérances de classification des couleurs (map_color.png)."""
    water_blue_margin: int = 25        # b - max(r,g) >= x  -> eau
    grass_green_margin: int = 12       # g - max(r,b) >= x  -> herbe
    sand_min_r_minus_b: int = 28       # beige : r - b >= x
    sand_min_value: int = 140          # beige : max(r,g,b) >= x
    offwhite_min_value: int = 205      # blanc cassé : max >= x
    offwhite_min_r_minus_b: int = 8    # blanc cassé : r - b >= x
    gray_max_chroma: int = 16          # gris : max-min <= x
    # Couleurs de référence pour les pixels non classés (plus proche voisin)
    ref_grass: tuple = (80, 150, 60)
    ref_water: tuple = (35, 90, 195)
    ref_sand: tuple = (228, 208, 155)
    ref_mountain: tuple = (130, 130, 134)


@dataclass
class Config:
    size: int = 8192
    seed: int = 1337
    sand_border_px: int = 50
    max_altitude: int = 255
    normalize_peak: bool = True        # le plus haut sommet vaut exactement max_altitude

    # --- map_height.png ---
    invert_height_png: bool = True     # True : blanc = plat/bas, noir = sommet (dégradé blanc -> noir)

    # --- relief ---
    mountain_freq: float = 4.0
    mountain_threshold: float = 0.57   # plus haut = moins de montagnes (était 0.60)
    mountain_full: float = 0.70        # (était 0.72)
    mountain_biome_min_alt: float = 25.0   # altitude mini pour être "gris"
    plains_max_alt: float = 6.0
    edge_fade_px: int = 600            # les montagnes s'effacent vers le bord (pour 8192)

    # --- eau ---
    river_half_width: float = 0.005    # largeur des rivières
    shore_width: float = 0.003         # sable autour des rivières
    lake_threshold: float = 0.66       # plus bas = plus de lacs
    lake_sand_clearance: float = 0.012 # zone sans sable autour des lacs (unités de bruit)
    lake_border_margin: int = 40       # distance mini lac <-> sable de bordure (px, pour 8192)
    water_max_alt: float = 10.0        # pas d'eau au-dessus

    # --- collision ---
    speed_grass: float = 1.00
    speed_water: float = 0.20
    speed_sand: float = 0.70
    speed_mountain_flat: float = 1.00
    mountain_uphill_mult: float = 0.40   # multiplicateur en montée (configurable)
    max_walk_slope_deg: float = 40.0     # pente max franchissable
    z_scale: float = 1.0                 # 1 unité d'altitude = z_scale pixels
    slope_baseline_px: int = 3

    tol: ColorTolerance = field(default_factory=ColorTolerance)


# ----------------------------------------------------------------------------
# BRUIT (fbm par bandes, bilinéaire lissé)
# ----------------------------------------------------------------------------
class Noise:
    def __init__(self, seed: int, size: int):
        self.seed, self.size = seed, size
        self._grids: dict = {}

    def _grid(self, name: str, octave: int, freq: int) -> np.ndarray:
        key = (name, octave)
        if key not in self._grids:
            rng = np.random.default_rng([self.seed, zlib.crc32(name.encode()), octave])
            self._grids[key] = rng.random((freq + 1, freq + 1), dtype=np.float32)
        return self._grids[key]

    def _sample(self, g, y0, y1, f):
        S = self.size
        ys = np.arange(y0, y1, dtype=np.float32) * (f / S)
        iy = ys.astype(np.int32)
        fy = ys - iy
        fy = fy * fy * (3 - 2 * fy)
        xs = np.arange(S, dtype=np.float32) * (f / S)
        ix = xs.astype(np.int32)
        fx = xs - ix
        fx = fx * fx * (3 - 2 * fx)
        rows = g[iy] * (1 - fy)[:, None] + g[iy + 1] * fy[:, None]
        return rows[:, ix] * (1 - fx) + rows[:, ix + 1] * fx

    def fbm(self, name, y0, y1, freq, octaves, persistence=0.5):
        total = np.zeros((y1 - y0, self.size), np.float32)
        amp, norm, f = 1.0, 0.0, int(freq)
        for o in range(octaves):
            total += amp * self._sample(self._grid(name, o, f), y0, y1, f)
            norm += amp
            amp *= persistence
            f *= 2
        return total / norm


# ----------------------------------------------------------------------------
# PASSE A : altitude + type de sol
# ----------------------------------------------------------------------------
def terrain_pass(cfg: Config, noise: Noise, alt: np.ndarray, cls: np.ndarray):
    S = cfg.size
    fade_px = max(1.0, cfg.edge_fade_px * S / 8192)
    lake_margin = cfg.lake_border_margin * S / 8192
    for y0 in range(0, S, BAND):
        y1 = min(S, y0 + BAND)
        ys = np.arange(y0, y1, dtype=np.int32)[:, None]
        xs = np.arange(S, dtype=np.int32)[None, :]
        d = np.minimum(np.minimum(ys, S - 1 - ys), np.minimum(xs, S - 1 - xs))

        # Relief : collines douces + montagnes en dégradé continu (pas de pic isolé)
        hills = noise.fbm("hills", y0, y1, 6, 4)
        m = noise.fbm("mtn", y0, y1, cfg.mountain_freq, 6)
        t = np.clip((m - cfg.mountain_threshold) / (cfg.mountain_full - cfg.mountain_threshold), 0, 1)
        t = t * t * t * (t * (t * 6 - 15) + 10)  # smootherstep
        ridge = 1 - np.abs(2 * noise.fbm("ridge", y0, y1, 32, 4) - 1)
        a = cfg.plains_max_alt * np.clip((hills - 0.3) / 0.4, 0, 1)
        a = a + cfg.max_altitude * t * (0.75 + 0.25 * ridge)
        fade = np.clip((d - cfg.sand_border_px) / fade_px, 0, 1)
        a = a * (fade * fade * (3 - 2 * fade))
        a = np.minimum(a, cfg.max_altitude)

        # Eau : rivières = courbe de niveau d'un bruit, lacs = cuvettes
        rv = noise.fbm("river", y0, y1, 5, 5, 0.4)
        lk = noise.fbm("lake", y0, y1, 5, 5, 0.5)
        dr = np.abs(rv - 0.5)
        low = a < cfg.water_max_alt

        border = d < cfg.sand_border_px
        lake_ok = d >= cfg.sand_border_px + lake_margin  # les lacs restent loin du sable de bordure

        river_water = (dr < cfg.river_half_width) & low & ~border
        lake_water = (lk > cfg.lake_threshold) & low & lake_ok
        water = river_water | lake_water

        # Sable de berge : rivières uniquement, jamais dans la zone d'un lac
        near_lake = lk > (cfg.lake_threshold - cfg.lake_sand_clearance)
        shore = ((dr < cfg.river_half_width + cfg.shore_width)
                 & (a < cfg.water_max_alt + 4) & ~water & ~near_lake)

        c = np.zeros(a.shape, np.uint8)
        c[shore] = SAND
        c[water] = WATER
        c[border] = SAND
        alt[y0:y1] = a
        cls[y0:y1] = c


# ----------------------------------------------------------------------------
# PASSE B : couleurs
# ----------------------------------------------------------------------------
def color_pass(cfg: Config, noise: Noise, alt, cls, color):
    S = cfg.size
    for y0 in range(0, S, BAND):
        y1 = min(S, y0 + BAND)
        a = alt[y0:y1]
        c = cls[y0:y1].copy()
        c[(c == GRASS) & (a >= cfg.mountain_biome_min_alt)] = MOUNTAIN
        v = (noise.fbm("col", y0, y1, 64, 3) - 0.5) * 2.0
        g = 85 + 105 * (a / cfg.max_altitude) + 25 * v

        conds = [c == WATER, c == SAND, c == MOUNTAIN]
        R = np.select(conds, [25 + 20 * v, 228 + 10 * v, g], 70 + 30 * v)
        G = np.select(conds, [80 + 30 * v, 208 + 10 * v, g], 145 + 35 * v)
        B = np.select(conds, [185 + 30 * v, 155 + 12 * v, g + 4], 58 + 20 * v)
        color[y0:y1, :, 0] = np.clip(R, 0, 255)
        color[y0:y1, :, 1] = np.clip(G, 0, 255)
        color[y0:y1, :, 2] = np.clip(B, 0, 255)


# ----------------------------------------------------------------------------
# CLASSIFICATION ROBUSTE DES COULEURS
# ----------------------------------------------------------------------------
def classify_colors(rgb: np.ndarray, tol: ColorTolerance) -> np.ndarray:
    """rgb (h,w,3) uint8 -> codes GRASS/WATER/SAND/MOUNTAIN (uint8). Tolérances configurables."""
    c = rgb.astype(np.int16)
    r, g, b = c[..., 0], c[..., 1], c[..., 2]
    mx, mn = c.max(-1), c.min(-1)
    chroma = mx - mn

    water = (b - np.maximum(r, g)) >= tol.water_blue_margin
    grass = ~water & ((g - np.maximum(r, b)) >= tol.grass_green_margin)
    rb = r - b
    sand = ~(water | grass) & (
        ((rb >= tol.sand_min_r_minus_b) & (mx >= tol.sand_min_value))
        | ((mx >= tol.offwhite_min_value) & (rb >= tol.offwhite_min_r_minus_b)))
    gray = ~(water | grass | sand) & (chroma <= tol.gray_max_chroma)

    out = np.full(r.shape, 255, np.uint8)
    out[grass], out[water], out[sand], out[gray] = GRASS, WATER, SAND, MOUNTAIN

    # Pixels hors règles : plus proche couleur de référence (jamais de "trou")
    unk = out == 255
    if unk.any():
        refs = np.array([tol.ref_grass, tol.ref_water, tol.ref_sand, tol.ref_mountain], np.int32)
        px = c[unk].astype(np.int32)
        dist = ((px[:, None, :] - refs[None, :, :]) ** 2).sum(-1)
        out[unk] = dist.argmin(1).astype(np.uint8)
    return out


# ----------------------------------------------------------------------------
# PASSE C : collision (couleur + altitude ORIGINALE flottante)
# ----------------------------------------------------------------------------
def slope_band(alt, y0, y1, b, zscale):
    H = alt.shape[0]
    rows = np.clip(np.arange(y0 - b, y1 + b), 0, H - 1)
    blk = np.pad(alt[rows], ((0, 0), (b, b)), mode="edge")
    dzdx = (blk[b:-b, 2 * b:] - blk[b:-b, :-2 * b]) / (2 * b)
    dzdy = (blk[2 * b:, b:-b] - blk[:-2 * b, b:-b]) / (2 * b)
    return np.degrees(np.arctan(np.hypot(dzdx, dzdy) * zscale))


def collision_pass(cfg: Config, alt, color, out):
    """Canaux : R = multiplicateur*100 | G = pente (0..90° -> 0..255) | B = classe | 0x80 si pente > seuil."""
    S = cfg.size
    lut = np.array([cfg.speed_grass, cfg.speed_water, cfg.speed_sand, cfg.speed_mountain_flat], np.float32)
    stats = np.zeros(4, np.int64)
    blocked_total = 0
    for y0 in range(0, S, BAND):
        y1 = min(S, y0 + BAND)
        code = classify_colors(color[y0:y1], cfg.tol)
        slope = slope_band(alt, y0, y1, cfg.slope_baseline_px, cfg.z_scale)
        blocked = (slope > cfg.max_walk_slope_deg) & (code != WATER)
        out[y0:y1, :, 0] = np.rint(lut[code] * 100)
        out[y0:y1, :, 1] = np.clip(np.rint(slope / 90 * 255), 0, 255)
        out[y0:y1, :, 2] = code | (blocked.astype(np.uint8) * BLOCKED_FLAG)
        stats += np.bincount(code.ravel(), minlength=4)[:4]
        blocked_total += int(blocked.sum())
    return stats, blocked_total


# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", type=int, default=8192)
    ap.add_argument("--seed", type=int, default=1337)
    ap.add_argument("--out", default=str(ASSETS))
    args = ap.parse_args()

    cfg = Config(size=args.size, seed=args.seed)
    S = cfg.size
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    noise = Noise(cfg.seed, S)

    alt = np.zeros((S, S), np.float32)
    cls = np.zeros((S, S), np.uint8)
    print("[1/4] relief + eau ...")
    terrain_pass(cfg, noise, alt, cls)
    if cfg.normalize_peak and alt.max() > 0:
        alt *= cfg.max_altitude / alt.max()
    np.clip(alt, 0, cfg.max_altitude, out=alt)

    print("[2/4] couleurs ...")
    color = np.zeros((S, S, 3), np.uint8)
    color_pass(cfg, noise, alt, cls, color)
    del cls

    print("[3/4] collision ...")
    collision = np.zeros((S, S, 3), np.uint8)
    stats, blocked = collision_pass(cfg, alt, color, collision)

    print("[4/4] sauvegarde PNG ...")
    h8 = np.rint(alt).astype(np.uint8)
    if cfg.invert_height_png:
        h8 = 255 - h8  # blanc = plat, noir = sommet
    Image.fromarray(color, "RGB").save(out_dir / "map_color.png", compress_level=3)
    Image.fromarray(h8, "L").save(out_dir / "map_height.png", compress_level=3)
    Image.fromarray(collision, "RGB").save(out_dir / "map_collision.png", compress_level=3)
    print(f"PNG écrits dans : {out_dir}")

    tot = S * S
    print(f"\nTerminé en {time.time() - t0:.0f}s")
    print(f"altitude max : {alt.max():.0f}")
    for n, k in zip(("herbe", "eau", "sable", "montagne"), stats):
        print(f"  {n:9s}: {100 * k / tot:5.2f} %")
    print(f"  bloqué (pente > {cfg.max_walk_slope_deg}°) : {100 * blocked / tot:5.2f} %")


if __name__ == "__main__":
    main()

