import os
import argparse
import numpy

from astropy.io import fits

FILE_WRITE_LOCATION = "./fits_csv_output"
SEPARATOR_STRING = "\n==================================================\n"

numpy.set_printoptions(threshold=numpy.inf)

PARSEC_TO_METER = 3.0857e16


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
    x_m = x_pc * PARSEC_TO_METER
    y_m = y_pc * PARSEC_TO_METER
    z_m = z_pc * PARSEC_TO_METER

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


def combine_fits(files, column_names):
    if len(files) != len(column_names):
        raise ValueError("Number of files must match number of column names")

    print(SEPARATOR_STRING)
    print("Combining FITS files...")

    datasets = []
    coord_to_index_maps = []

    all_coords = set()

    for f in files:
        _, data = load_fits_data(f)

        datasets.append(data)

        # Builds a map of coordinates to index values
        # i.e. (1, 2, 3) -> 0, (2, 2, 3) -> 1, ...
        # Assumes first three columns are x, y, z
        coord_to_index_map = {tuple(row[:3]): i for i, row in enumerate(data)}
        coord_to_index_maps.append(coord_to_index_map)

        all_coords.update(coord_to_index_map.keys())

    all_coords = sorted(list(all_coords))

    # Build output rows
    rows = []

    for coord in all_coords:
        x, y, z = coord

        # convert parsecs to meters
        x = x * PARSEC_TO_METER
        y = y * PARSEC_TO_METER
        z = z * PARSEC_TO_METER

        row = [x, y, z]

        for data, coord_to_index_map in zip(datasets, coord_to_index_maps):
            index = coord_to_index_map.get(coord)
            if index is None:
                # This dataset does not contain this coord
                row.append("")
            else:
                # Append the data column of the given coord to the final row
                row.append(data[index, 3])

        rows.append(row)

    # Write the CSV file
    os.makedirs(FILE_WRITE_LOCATION, exist_ok=True)

    filename = "m1_combined_" + "_".join(column_names) + ".csv"

    header = "X,Y,Z," + ",".join(column_names)

    numpy.savetxt(
        f"{FILE_WRITE_LOCATION}/{filename}",
        numpy.array(rows, dtype=object),
        delimiter=",",
        header=header,
        fmt="%s",
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

    # Combine command
    combine_parser = subparsers.add_parser("combine")
    combine_parser.add_argument(
        "--files",
        nargs="+",
        required=True,
        help="List of FITS files"
    )
    combine_parser.add_argument(
        "--data_names",
        nargs="+",
        required=True,
        help="Column names for each dataset"
    )

    args = parser.parse_args()

    if args.command == "inspect":
        inspect_fits_file(args.fits_file, args.data_name)

    elif args.command == "csv":
        create_csv(args.fits_file, args.data_name)

    elif args.command == "combine":
        combine_fits(args.files, args.data_names)


if __name__ == "__main__":
    main()