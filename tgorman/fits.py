import numpy

from astropy.io import fits

FITS_FILE_PATH = "../3dmap_XYZvel.fits"
SEPARATOR_STRING = "\n==================================================\n"

numpy.set_printoptions(threshold=numpy.inf)

def print_hdul_info(hdul):
    print("DATA INFO\n"
          "---------")
    print(hdul.info())

def print_data_shape(data):
    print(SEPARATOR_STRING)
    print("DATA SHAPE\n"
          "----------")
    print(data.shape)

def print_data_ranges(data):
    # Separate columns
    x = data[:, 0]
    y = data[:, 1]
    z = data[:, 2]
    flux = data[:, 3]

    print(SEPARATOR_STRING)
    print("COLUMN RANGES\n"
          "-------------")
    print("X range:", x.min(), x.max())
    print("Y range:", y.min(), y.max())
    print("Z range:", z.min(), z.max())
    print("Vel range:", flux.min(), flux.max())

def print_data(data):
    print(SEPARATOR_STRING)
    print("DATA (First Row)\n"
          "----")
    print(data[0, :])

def create_csv(data):
    print(SEPARATOR_STRING)
    print("Converting data to csv...")

    # Add a row for high-end flux to control color map range in OpenSpace
    new_row = numpy.array([0, 0, 0, 1000000000000])
    data = numpy.vstack((data, new_row))
    
    # Get coordinate columns
    x_pc = data[:, 0]
    y_pc = data[:, 1]
    z_pc = data[:, 2]

    # Convert parsecs to meters
    pc_to_m = 3.0857e16
    x_m = x_pc * pc_to_m
    y_m = y_pc * pc_to_m
    z_m = z_pc * pc_to_m

    # Get flux column
    flux = data[:, 3]

    # Invert Flux data
    # to handle color mappings which use the lowest values as the brightest color
    # flux_min = flux.min()
    # flux_max = flux.max()
    #
    # flux_inverted = flux_max - (flux - flux_min)

    # Stack columns into numpy array
    final_data = numpy.column_stack((x_m, y_m, z_m, flux))

    # Save to CSV
    filename = "m1_xyzflux_meters_highfluxrow.csv"
    numpy.savetxt(filename, final_data, delimiter=",", header="X,Y,Z,flux", comments="")

    print("Done\n"
          f"Created file \"{filename}\"")

def main(make_csv_file=False):
    hdul = fits.open(FITS_FILE_PATH)
    data = hdul[0].data

    print_hdul_info(hdul)
    print_data_shape(data)
    print_data_ranges(data)
    print_data(data)

    if make_csv_file:
        create_csv(data)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--create-csv", action="store_true")
    args = parser.parse_args()

    main(make_csv_file=args.create_csv)