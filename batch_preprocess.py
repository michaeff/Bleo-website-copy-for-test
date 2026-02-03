#!/usr/bin/env python3
import os
import sys

# 1) Import your utils module
# czi_utils.py



import os
from czifile import CziFile
import numpy as np
from PIL import Image

# Tint colors per channel (R, G, B)
CHANNEL_COLORS = {
    1: (255,   255,   255),   # ASE
    2: (0,   255,   0),   # GFP
    3: (255,     0, 0),   # aSMA
    4: (0, 0, 255)    # DAPI
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
    print("FIRST HELLO")
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
            print( "HELLO")
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
    print("HELLO 4")
    os.makedirs(output_dir, exist_ok=True)
    for z in range(Z):
        for c in range(C):
            plane = arr[z, c, :, :].astype(np.float32)
            # Normalize
            f = plane.astype(np.float32)
            f -= f.min()
            span = np.ptp(f) or 1.0
            f /= span

            # Threshold
            f = _apply_threshold(f, z+1)

            # To uint8
            p8 = (f * 255).astype(np.uint8)

            # Tint RGBA
            color = CHANNEL_COLORS[z+1]
            img = Image.new("RGBA", p8.shape[::-1], color + (0,))
            alpha = Image.fromarray(p8, mode="L")
            img.putalpha(alpha)


            out = os.path.join(output_dir,
                 f"week6_HV_z{c+1}_ch{z+1}.png")
            img.save(out)




# 2) Grab the two functions we need
#flat_fn = getattr(czi_utils, 'process_czi_file', None) or getattr(czi_utils, 'process_czi', None)
#process_detailed_czi = getattr(czi_utils, 'process_detailed_czi', None)

#if not flat_fn:
 #   print("ERROR: No flat-CZI function (process_czi_file or process_czi) found in czi_utils.py")
  #  sys.exit(1)

#if not process_detailed_czi:
   # print("WARNING: No 'process_detailed_czi' function found in czi_utils.py – detailed stacks will be skipped.")

# 3) Define input/output roots
#MAIN_IN   = os.path.join('static','czi_images')
#MAIN_OUT  = os.path.join('static','processed')
DET_IN    = "C:/Users/micha/Downloads/bigguyczi/week6_HV.czi"
DET_OUT   = "C:/Users/micha/Downloads/bigguypng/"

def ensure(path):
    os.makedirs(path, exist_ok=True)
    return path

#def batch_flat():
   # """Process all single-slice CZIs under static/czi_images/"""
    #ensure(MAIN_OUT)
    #or fn in sorted(os.listdir(MAIN_IN)):
     #   if fn.lower().endswith('.czi'):
      #######    print(f"  [ERROR] {fn}: {e}")

def batch_detailed():
    print("""Process all multi-Z CZIs under static/czi_images_detailed/week*/kmc*/""")
    if not process_detailed_czi:
        return
    
    print("help me")      
                        
    process_detailed_czi(DET_IN, DET_OUT)
                    
           

if __name__ == "__main__":
    print("=== Starting batch preprocessing ===")
    #batch_flat()
    a=batch_detailed()
    print("=== Batch preprocessing complete ===")
    print(a)

