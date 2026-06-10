import argparse
import numpy as np

# Default stops produce the M1 nii_ha colormap:
# low ratio (inner ionized gas) → blue-teal
# mid                           → yellow
# high ratio (outer filaments)  → red-orange
# Alpha ramps from 0.125 → 1.0 across the three stops.
M1_STOPS = [
    "0.0  0.1 0.55 0.9  1.0",
    "0.5  1.0 1.0  0.0  1.0",
    "1.0  0.9 0.15 0.0  1.0",
]

def parse_stop(s):
    parts = s.split()
    if len(parts) != 5:
        raise argparse.ArgumentTypeError(f"Stop must be 'position r g b a', got: {s!r}")
    pos, r, g, b, a = map(float, parts)
    for name, val in [("position", pos), ("r", r), ("g", g), ("b", b), ("a", a)]:
        if not (0.0 <= val <= 1.0):
            raise argparse.ArgumentTypeError(f"{name} must be in [0, 1], got {val}")
    return (pos, r, g, b, a)

parser = argparse.ArgumentParser(
    description="Generate an OpenSpace .cmap colormap file.",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="""
Color stops are "position r g b a" strings, all values in [0, 1].
Stops are linearly interpolated across the colormap.

Defaults produce the M1 Crab Nebula nii_ha colormap:
  0.0  0.1 0.55 0.9  1.0   (blue-teal,  low ionization)
  0.5  1.0 1.0  0.0  1.0   (yellow,     mid)
  1.0  0.9 0.15 0.0  1.0   (red-orange, outer filaments)

Examples:
  # Generate default M1 colormap
  python colormap_generator.py

  # Custom two-stop blue-to-red, fully opaque
  python colormap_generator.py -o blue_red.cmap --stops "0.0 0 0 1 1" "1.0 1 0 0 1"
""",
)
parser.add_argument("--output", "-o", default="m1_nii_ha.cmap",
                    help="Output filename (default: m1_nii_ha.cmap)")
parser.add_argument("--dir", "-d", default="./colormap_output",
                    help="Output directory (default: ./colormap_output)")
parser.add_argument("--count", "-n", type=int, default=256,
                    help="Number of color entries (default: 256)")
parser.add_argument("--stops", type=parse_stop, nargs="+", metavar="'pos r g b a'",
                    default=[parse_stop(s) for s in M1_STOPS],
                    help='Color stops as "position r g b a" strings (all values in [0, 1]). '
                         "Default: M1 nii_ha colormap.")
args = parser.parse_args()

stops = sorted(args.stops, key=lambda s: s[0])
stop_points  = [s[0] for s in stops]
stop_reds       = [s[1] for s in stops]
stop_greens     = [s[2] for s in stops]
stop_blues      = [s[3] for s in stops]
stop_alphas     = [s[4] for s in stops]

colormap_points   = np.linspace(0.0, 1.0, args.count)
colormap_reds   = np.interp(colormap_points, stop_points, stop_reds)
colormap_greens = np.interp(colormap_points, stop_points, stop_greens)
colormap_blues  = np.interp(colormap_points, stop_points, stop_blues)
colormap_alphas = np.interp(colormap_points, stop_points, stop_alphas)

output_path = f"{args.dir}/{args.output}"
print(f"Writing {args.count} colormap entries to {output_path}")
print(f"  Color stops (pos r g b a): {stops}")

with open(output_path, "w") as f:
    f.write(f"{args.count}\n")
    for r, g, b, a in zip(colormap_reds, colormap_greens, colormap_blues, colormap_alphas):
        f.write(f"{r:.6f} {g:.6f} {b:.6f} {a:.6f}\n")
