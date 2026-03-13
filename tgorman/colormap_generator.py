import numpy

OUTPUT_FILE_NAME="m1_sii_ha.cmap"
FILE_WRITE_LOCATION="./colormap_output"
OUTPUT_FILE_PATH=f"{FILE_WRITE_LOCATION}/{OUTPUT_FILE_NAME}"

COLOR_VALUE_COUNT=256

r, g, b = 1.0, 0.5, 0.0
alphas = numpy.linspace(0.125, 1, COLOR_VALUE_COUNT)

print(f"Writing colormap values to file {OUTPUT_FILE_PATH}:\n"
      f"alphas:\n"
      f"{alphas}")

with open(OUTPUT_FILE_PATH, "w") as f:
    f.write(f"{COLOR_VALUE_COUNT}\n")
    for a in alphas:
        f.write(f"{r} {g} {b} {a}\n")