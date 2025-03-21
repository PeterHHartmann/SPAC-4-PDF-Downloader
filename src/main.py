import os
from classes import (
    ExcelReader,
    Metadata,
    RapportDownloader,
)
import time


def main(limit, multiprocess):
    start_time = time.time()
    source_dir = "data"
    source_file = "GRI_2017_2020.xlsx"
    download_output_dir = "downloads"
    metadata_output_dir = "metadata"
    reader = ExcelReader(os.path.join(source_dir, source_file), limit=limit)
    data = reader.read()
    downloader = RapportDownloader(out_dir=download_output_dir)
    if multiprocess == 1:
        downloader.parallel_download(data=data, max_workers=12)
    else:
        downloader.download_slow()
    metadata = Metadata(data, metadata_output_dir, source_file, download_output_dir)
    metadata.save()
    print(
        f"{'Parallel execution time' if multiprocess == 1 else 'Single-threaded execution time'}--- %s seconds ---"
        % (time.time() - start_time)
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="PDF Downloader")
    parser.add_argument(
        "--limit",
        metavar="Integer",
        required=False,
        type=int,
        help="Limit the program to a maximum amount of rows to try and download",
    )
    parser.add_argument(
        "--multiprocess",
        metavar="Integer",
        required=False,
        type=int,
        help="Chose whether or not to run the program in multiprocessesing mode",
    )
    args = parser.parse_args()
    main(limit=args.limit, multiprocess=args.multiprocess)
