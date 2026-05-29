import os
import numpy

from astropy.io import fits

FILE_WRITE_LOCATION = "./fits_csv_output"
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


def print_data_ranges(data_name, data):
    # Separate columns
    x = data[:, 0]
    y = data[:, 1]
    z = data[:, 2]
    values = data[:, 3]

    print(SEPARATOR_STRING)
    print("COLUMN RANGES\n"
          "-------------")
    print("X range:", x.min(), x.max())
    print("Y range:", y.min(), y.max())
    print("Z range:", z.min(), z.max())
    print(f"{data_name} range:", values.min(), values.max())


def print_data(data):
    print(SEPARATOR_STRING)
    print("DATA (First Row)\n"
          "----")
    print(data[0, :])


def create_csv(data_name, data):
    print(SEPARATOR_STRING)
    print("Converting data to csv...")

    # Get coordinate columns
    x_pc = data[:, 0]
    y_pc = data[:, 1]
    z_pc = data[:, 2]

    # Convert parsecs to meters
    pc_to_m = 3.0857e16
    x_m = x_pc * pc_to_m
    y_m = y_pc * pc_to_m
    z_m = z_pc * pc_to_m

    # Get data column
    data_column = data[:, 3]

    # Stack columns into numpy array
    final_data = numpy.column_stack((x_m, y_m, z_m, data_column))

    # Ensure output directory exists
    os.makedirs(FILE_WRITE_LOCATION, exist_ok=True)

    # Save to CSV
    filename = f"m1_xyz{data_name}_meters.csv"

    numpy.savetxt(
        f"{FILE_WRITE_LOCATION}/{filename}",
        final_data,
        delimiter=",",
        header=f"X,Y,Z,{data_name}",
        comments=""
    )

    print("Done\n"
          f"Created file \"{filename}\"")


def main(fits_file_path, data_name, make_csv_file=False):
    hdul = fits.open(fits_file_path)
    data = hdul[0].data

    print_hdul_info(hdul)
    print_data_shape(data)
    print_data_ranges(data_name, data)
    print_data(data)

    if make_csv_file:
        create_csv(data_name, data)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "fits_file",
        help="Path to the FITS file"
    )

    parser.add_argument(
        "data_name",
        help="Name of the data field (e.g. flux, sii_sii)"
    )

    parser.add_argument(
        "--csv",
        action="store_true",
        help="Create CSV output"
    )

    args = parser.parse_args()

    main(
        fits_file_path=args.fits_file,
        data_name=args.data_name,
        make_csv_file=args.csv
    )