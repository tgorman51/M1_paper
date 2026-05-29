import os
import argparse
import numpy

from astropy.io import fits

FILE_WRITE_LOCATION = "./fits_csv_output"
SEPARATOR_STRING = "\n==================================================\n"

numpy.set_printoptions(threshold=numpy.inf)


def load_fits_data(fits_file_path):
    hdul = fits.open(fits_file_path)
    data = hdul[0].data
    return hdul, data


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


def inspect_fits_file(fits_file_path, data_name):
    hdul, data = load_fits_data(fits_file_path)

    print_hdul_info(hdul)
    print_data_shape(data)
    print_data_ranges(data_name, data)
    print_data(data)


def create_csv(fits_file_path, data_name):
    hdul, data = load_fits_data(fits_file_path)

    print(SEPARATOR_STRING)
    print("Converting data to csv...")

    # Coordinate columns
    x_pc = data[:, 0]
    y_pc = data[:, 1]
    z_pc = data[:, 2]

    # Convert parsecs to meters
    pc_to_m = 3.0857e16
    x_m = x_pc * pc_to_m
    y_m = y_pc * pc_to_m
    z_m = z_pc * pc_to_m

    # Data column
    data_column = data[:, 3]

    # Final output array
    final_data = numpy.column_stack((x_m, y_m, z_m, data_column))

    # Ensure output directory exists
    os.makedirs(FILE_WRITE_LOCATION, exist_ok=True)

    # Output filename
    filename = f"m1_xyz{data_name}_meters.csv"

    # Save CSV
    numpy.savetxt(
        f"{FILE_WRITE_LOCATION}/{filename}",
        final_data,
        delimiter=",",
        header=f"X,Y,Z,{data_name}",
        comments=""
    )

    print("Done\n"
          f"Created file \"{filename}\"")


def main():
    parser = argparse.ArgumentParser(
        description="Utility for inspecting and converting FITS point cloud data."
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Inspect command
    inspect_parser = subparsers.add_parser(
        "inspect",
        help="Inspect FITS file contents"
    )

    inspect_parser.add_argument(
        "fits_file",
        help="Path to FITS file"
    )

    inspect_parser.add_argument(
        "data_name",
        help="Name of data field (e.g. flux, sii_sii)"
    )

    # CSV command
    csv_parser = subparsers.add_parser(
        "csv",
        help="Convert FITS data to CSV"
    )

    csv_parser.add_argument(
        "fits_file",
        help="Path to FITS file"
    )

    csv_parser.add_argument(
        "data_name",
        help="Name of data field (e.g. flux, sii_sii)"
    )

    args = parser.parse_args()

    if args.command == "inspect":
        inspect_fits_file(args.fits_file, args.data_name)

    elif args.command == "csv":
        create_csv(args.fits_file, args.data_name)


if __name__ == "__main__":
    main()