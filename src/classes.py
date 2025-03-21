import os
from concurrent.futures import ProcessPoolExecutor, as_completed
import sys
from pandas import DataFrame, ExcelWriter, read_excel
import weasyprint
import style
from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError
import requests


class ExcelReader:

    def __init__(self, file_path, limit) -> None:
        self.file_path = file_path
        self.limit = limit
        pass

    def read(self, index_col="BRnum"):
        try:
            return read_excel(
                self.file_path,
                sheet_name=0,
                index_col=index_col,
                nrows=self.limit,
            )
        except FileNotFoundError as e:
            sys.stderr.write(
                style.fail(
                    f"Failed to read rapport data from file: {e.strerror}: {e.filename}\n"
                )
            )
            raise e


class RapportDownloader:

    def __init__(
        self,
        out_dir: str = "temp",
    ):
        self.out_dir = out_dir
        pass

    def ensure_output_dir(self) -> None:
        os.makedirs(self.out_dir, exist_ok=True)

    @staticmethod
    def process_single_entry(
        brnum: int, pdf_url: str, html_address: str, out_dir: str
    ) -> None:
        file_path = os.path.join(out_dir, f"{brnum}.pdf")

        def validate_downloaded_rapport(file_path) -> bool:
            if os.path.isfile(file_path):
                try:
                    pdfReader = PdfReader(open(file_path, "rb"))
                    return len(pdfReader.pages) > 0
                except PdfReadError as e:
                    print(style.warn(f"{brnum} - PDF reader Error: {e}"), flush=True)
                    return False
            return False

        # Attempt to download from Pdf_URL
        try:
            response = requests.get(pdf_url, timeout=10, stream=True)
            response.raise_for_status()
            with open(file_path, "wb") as out_file:
                for chunk in response.iter_content(chunk_size=8192):
                    out_file.write(chunk)

            if validate_downloaded_rapport(file_path):
                print(style.success(f"{brnum} downloaded from Pdf_URL"), flush=True)
                return
        except Exception as e:
            print(style.warn(f"{brnum} - Download Error for Pdf_URL: {e}"), flush=True)
            pass

        # If PDF download from "Pdf_URL" fails, try HTML link
        if isinstance(html_address, str):
            try:
                weasyprint.HTML(html_address).write_pdf(file_path)
                if validate_downloaded_rapport(file_path):
                    print(
                        style.success(
                            f"{brnum} downloaded from Report Html Address",
                        ),
                        flush=True,
                    )
                    return
            except Exception as e:
                print(
                    style.warn(
                        f"{brnum} - Download Error for Report Html Address: {e}"
                    ),
                    flush=True,
                )
                pass  # Log error if needed

    def parallel_download(self, data: DataFrame, max_workers: int = None) -> None:
        """
        Downloads reports in parallel using multiple worker processes.

        Args:
            max_workers (int, optional): Number of parallel processes to use. Defaults to the number of CPU cores.
        """

        self.ensure_output_dir()

        # If max_workers is not specified, use all available CPU cores
        if max_workers is None:
            max_workers = (
                os.cpu_count() - 1 or 4
            )  # Fallback to 4 if os.cpu_count() returns None

        # Create a ProcessPoolExecutor with the specified number of workers
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(
                    self.process_single_entry,
                    brnum,
                    data.at[brnum, "Pdf_URL"],
                    data.at[brnum, "Report Html Address"],
                    self.out_dir,
                ): brnum
                for brnum in data.index
            }

            for future in as_completed(futures):  # Allows real-time output
                try:
                    future.result()  # Ensures exceptions are raised in the main process
                except Exception as e:
                    print(style.fail(f"Error in process {futures[future]}: {e}"))

    def download_slow(self, data: DataFrame) -> None:
        for brnum in self.data.index:
            self.process_single_entry(
                brnum=brnum,
                pdf_url=data.at[brnum, "Pdf_URL"],
                html_address=data.at[brnum, "Report Html Address"],
                out_dir=self.out_dir,
            )


class Metadata:

    def __init__(
        self, data: DataFrame, out_dir: str, source_file: str, download_output_dir: str
    ):
        self.out_dir = out_dir
        self.out_file = f"Metadata{source_file[4:-5]}.xlsx"
        self.metadata = data
        self.metadata["pdf_downloaded"] = "No"
        downloaded_files = [
            file
            for file in os.listdir(download_output_dir)
            if os.path.isfile(os.path.join(download_output_dir, file))
        ]
        for file in downloaded_files:
            self.metadata.loc[file[:-4], "pdf_downloaded"] = "Yes"
        pass

    def save(self):
        """
        Saves collected metadata to a excel file
        """
        try:
            os.makedirs(self.out_dir, exist_ok=True)
            writer = ExcelWriter(
                os.path.join(self.out_dir, self.out_file), engine="openpyxl"
            )
            self.metadata.to_excel(writer, sheet_name="Sheet1")
            writer._save()
        except Exception as e:
            print(e)
