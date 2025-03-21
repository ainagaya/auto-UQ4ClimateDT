import argparse
import os
import yaml
from gsv.retriever import GSVRetriever
import xarray


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Retrieve GSV data")
    parser.add_argument(
        "--requests", "-c", type=str, default="request.yaml",
        help="Path to the request folder or file")
    parser.add_argument(
        "--output", "-o", type=str, default="output",
        help="Path to the output folder"
    )
    return parser.parse_args()


def process_requests(requests_path, output_path):
    """Process GSV data requests."""
    gsv = GSVRetriever()

    count = 0

    # initialize empty xarray dataset
    merged_dataset = xarray.Dataset()

    for request in os.listdir(requests_path):
        print(f"Processing request {request}")
        data = gsv.request_data(f"{requests_path}/{request}")
        print("Raw data:")
        print(data)

        data.to_netcdf(f"{output_path}/raw-{count}.nc")

        levels = [
            1000, 975, 950, 925, 900, 875, 850, 825, 800, 775, 750, 700, 650, 600,
            550, 500, 450, 400, 350, 300, 250, 225, 200, 175, 150, 125, 100, 70,
            50, 30, 20, 10, 7, 5, 3, 2, 1
        ]

        try:
            data_interp = data.interp(level=levels)
            print("Interpolated data:")
            print(data_interp)
        except ValueError:
            print("Interpolation failed")
            continue

        # Uncomment the following line to save as Zarr format -> need contianer
        # data_interp.to_zarr("interpol.zarr")
        data_interp.to_netcdf(f"{output_path}/interpol-{count}.nc")

        # Store all the data into a single file
        merged_dataset = xarray.merge([merged_dataset, data_interp])

        count += 1


def main():
    """Main function."""
    args = parse_args()
    process_requests(args.requests, args.output)


if __name__ == "__main__":
    main()
