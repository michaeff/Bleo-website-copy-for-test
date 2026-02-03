#!/usr/bin/env python3
import os
import sys

# 1) Import your utils module
try:
    import czi_utils
except ImportError:
    print("ERROR: Could not import czi_utils.py")
    sys.exit(1)

# 2) Grab the two functions we need
flat_fn = getattr(czi_utils, 'process_czi_file', None) or getattr(czi_utils, 'process_czi', None)
detailed_fn = getattr(czi_utils, 'process_detailed_czi', None)

if not flat_fn:
    print("ERROR: No flat-CZI function (process_czi_file or process_czi) found in czi_utils.py")
    sys.exit(1)

if not detailed_fn:
    print("WARNING: No 'process_detailed_czi' function found in czi_utils.py – detailed stacks will be skipped.")

# 3) Define input/output roots
MAIN_IN   = os.path.join('static','czi_images')
MAIN_OUT  = os.path.join('static','processed')
DET_IN    = os.path.join('static','czi_images_detailed')
DET_OUT   = os.path.join('static','processed_detailed')

def ensure(path):
    os.makedirs(path, exist_ok=True)
    return path

def batch_flat():
    """Process all single-slice CZIs under static/czi_images/"""
    ensure(MAIN_OUT)
    for fn in sorted(os.listdir(MAIN_IN)):
        if fn.lower().endswith('.czi'):
            src = os.path.join(MAIN_IN, fn)
            print(f"[Flat] → {src}")
            try:
                flat_fn(src, MAIN_OUT)
            except Exception as e:
                print(f"  [ERROR] {fn}: {e}")

def batch_detailed():
    """Process all multi-Z CZIs under static/czi_images_detailed/week*/kmc*/"""
    if not detailed_fn:
        return

    for week in sorted(os.listdir(DET_IN)):
        week_in = os.path.join(DET_IN, week)
        if not os.path.isdir(week_in):
            continue

        for kmc in sorted(os.listdir(week_in)):
            kmc_in = os.path.join(week_in, kmc)
            if not os.path.isdir(kmc_in):
                continue

            out_dir = ensure(os.path.join(DET_OUT, week, kmc))
            for fn in sorted(os.listdir(kmc_in)):
                if fn.lower().endswith('.czi'):
                    src = os.path.join(kmc_in, fn)
                    print(f"[Detail] → {src}")
                    try:
                        detailed_fn(src, out_dir)
                    except Exception as e:
                        print(f"  [ERROR] {fn}: {e}")

if __name__ == "__main__":
    print("=== Starting batch preprocessing ===")
    batch_flat()
    batch_detailed()
    print("=== Batch preprocessing complete ===")
