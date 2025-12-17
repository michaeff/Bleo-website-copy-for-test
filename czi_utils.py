# czi_utils.py



import os
from czifile import CziFile
import numpy as np
from PIL import Image

# Tint colors per channel (R, G, B)
CHANNEL_COLORS = {
    1: (255,   255,   255),   # ASE
    2: (0,   255,   100),   # GFP
    3: (255,     0, 0),   # aSMA
    4: (100, 100, 255)    # DAPI
}

# Per–week rotations (k counts of 90° CCW):
# week0: 90° CW  → k=3
# week1: 180°   → k=2
# week2: 90° CCW→ k=1
# week3: 90° CW → k=3
# all others: 0
WEEK_ROT_K = {
    'week0': 3,
    'week1': 2,
    'week2': 1,
    'week3': 3
}

# Predefined thresholds [0–1] per channel
CHANNEL_THRESHOLDS = {
    1: 6/255,
    2: 6/200,
    3: 40/230,
    4: 10/230
}

def _apply_threshold(norm_arr: np.ndarray, ch_idx: int) -> np.ndarray:
    thr = CHANNEL_THRESHOLDS.get(ch_idx, 0.0)
    mask = norm_arr >= thr
    out = np.zeros_like(norm_arr, dtype=np.float32)
    if thr < 1.0:
        out[mask] = (norm_arr[mask] - thr) / (1.0 - thr)
    return out

def process_czi(czi_path: str, output_dir: str) -> list[str]:
    os.makedirs(output_dir, exist_ok=True)
    base = os.path.splitext(os.path.basename(czi_path))[0]

    # 1) Load & squeeze
    arr = np.squeeze(CziFile(czi_path).asarray())

    # 2) Rotate array if needed
    k = WEEK_ROT_K.get(base, 0)
    if k:
        # rotate last two dims (Y,X)
        arr = np.rot90(arr, k=k, axes=(-2, -1))

    # 3) Split into channels
    if arr.ndim == 2:
        channels = [arr]
    else:
        # arr shape: (C, Y, X)
        channels = [arr[c] for c in range(arr.shape[0])]

    out_names = []
    for idx, ch in enumerate(channels, start=1):
        # Normalize
        f = ch.astype(np.float32)
        f -= f.min()
        span = np.ptp(f) or 1.0
        f /= span

        # Threshold
        f = _apply_threshold(f, idx)

        # To uint8
        p8 = (f * 255).astype(np.uint8)

        # Tint RGBA
        color = CHANNEL_COLORS[idx]
        img = Image.new("RGBA", p8.shape[::-1], color + (0,))
        alpha = Image.fromarray(p8, mode="L")
        img.putalpha(alpha)

        # Save
        name = f"{base}_channel{idx}.png"
        img.save(os.path.join(output_dir, name))
        out_names.append(name)

    return out_names

def process_detailed_czi(czi_path: str, output_root: str) -> tuple[int,int]:
    os.makedirs(output_root, exist_ok=True)
    base = os.path.splitext(os.path.basename(czi_path))[0]
    k = WEEK_ROT_K.get(base, 0)
    out_base = os.path.join(output_root, base)
    os.makedirs(out_base, exist_ok=True)

    arr = np.squeeze(CziFile(czi_path).asarray())

    # Determine dims
    if arr.ndim == 2:
        channels, zcount = 1, 1
    elif arr.ndim == 3:
        channels, zcount = arr.shape[0], 1
    else:
        channels, zcount = arr.shape[0], arr.shape[1]

    for c in range(channels):
        ch_dir = os.path.join(out_base, f"channel{c+1}")
        os.makedirs(ch_dir, exist_ok=True)

        for z in range(zcount):
            if zcount == 1:
                plane = arr[c] if arr.ndim >= 3 else arr
            else:
                plane = arr[c, z]

            # Rotate if needed
            if k:
                plane = np.rot90(plane, k=k, axes=(-2, -1))

            # Normalize
            f = plane.astype(np.float32)
            f -= f.min()
            span = np.ptp(f) or 1.0
            f /= span

            # Threshold
            f = _apply_threshold(f, c+1)

            # To uint8
            p8 = (f * 255).astype(np.uint8)

            # Tint RGBA
            color = CHANNEL_COLORS[c+1]
            img = Image.new("RGBA", p8.shape[::-1], color + (0,))
            alpha = Image.fromarray(p8, mode="L")
            img.putalpha(alpha)

            # Save slice
            img.save(os.path.join(ch_dir, f"slice{z}.png"))

    return channels, zcount
# in czi_utils.py


def process_detailed_czi(filename, output_dir):
    czi = CziFile(filename)
    arr = np.squeeze(czi.asarray())  # e.g. (Z,C,Y,X)
    if arr.ndim != 4:
        raise ValueError("Expected 4D (Z,C,Y,X), got %s" % (arr.shape,))
    Z, C, H, W = arr.shape

    os.makedirs(output_dir, exist_ok=True)
    for z in range(Z):
        for c in range(C):
            plane = arr[z, c, :, :].astype(np.float32)
            plane = (plane/plane.max()*255).astype(np.uint8)
            img = Image.fromarray(plane)
            name = os.path.basename(filename).replace('.czi','')
            out = os.path.join(output_dir,
                 f"{name}_z{z+1}_ch{c+1}.png")
            img.save(out)

