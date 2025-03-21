import os
from classes import (
    ExcelReader,
    Metadata,
    RapportDownloader,
)
import time


def main(limit: int, is_multithreaded_off: bool):
    start_time = time.time()
    source_dir = "data"
    source_file = "GRI_2017_2020.xlsx"
    download_output_dir = "downloads"
    metadata_output_dir = "metadata"
    excel_reader = ExcelReader(os.path.join(source_dir, source_file), limit=limit)
    data = excel_reader.read()
    downloader = RapportDownloader(is_multithreaded_off)
    downloader.download(data=data, out_dir=download_output_dir)
    metadata = Metadata(metadata_output_dir, source_file, download_output_dir)
    metadata.save(data)
    print(
        f"{'Single-threaded execution time' if is_multithreaded_off else 'Parallel execution time' }--- %s seconds ---"
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
        "--multithreaded-off",
        action="store_true",
        required=False,
        help="Disables multithreaded mode",
    )
    args = parser.parse_args()
    main(limit=args.limit, is_multithreaded_off=args.multithreaded_off)
