import os
from concurrent.futures import ProcessPoolExecutor, as_completed
import sys
import PyPDF2.errors
from pandas import DataFrame, ExcelWriter, read_excel
import weasyprint
from style import TermColor
import PyPDF2
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
                TermColor.fail(
                    f"Failed to read rapport data from file: {e.strerror}: {e.filename}\n"
                )
            )
            raise e


class RapportDownloader:

    def __init__(self, multithreaded_off: bool = True):
        self.multithreaded_off = multithreaded_off
        pass

    @staticmethod
    def process_single_entry(
        brnum: int, pdf_url: str, html_address: str, out_dir: str
    ) -> None:
        """
        Downloads a PDF from a given URL. If the download fails, attempts to generate a PDF from an HTML address.

        Args:
            brnum (int): Unique identifier for the rapport.
            pdf_url (str): Direct URL to the PDF file.
            html_address (str): URL of an HTML page to convert to PDF if the direct download fails.
            out_dir (str): Output directory to save the downloaded/generated PDF.
        """

        file_path = os.path.join(out_dir, f"{brnum}.pdf")

        def validate_downloaded_pdf(file_path) -> bool:
            """Checks if the downloaded PDF is valid by verifying its existence and readability."""
            if os.path.isfile(file_path):  # Check if file exists
                try:
                    #
                    pdfReader = PyPDF2.PdfReader(
                        open(file_path, "rb")
                    )  # Attempt to read PDF
                    return len(pdfReader.pages) > 0  # Ensure it contains pages
                except PyPDF2.errors.PdfReadError as e:
                    print(
                        TermColor.warn(f"{brnum} - PDF reader Error: {e}"), flush=True
                    )
                    return False
                except Exception as e:
                    print(
                        TermColor.fail(f"{brnum} - PDF reader Error: {e}"), flush=True
                    )
            return False

        # Attempt to download from Pdf_URL
        try:
            response = requests.get(pdf_url, timeout=10, stream=True)
            response.raise_for_status()
            with open(file_path, "wb") as out_file:
                for chunk in response.iter_content(chunk_size=8192):
                    out_file.write(chunk)  # Write downloaded content to file

            if validate_downloaded_pdf(file_path):
                print(
                    TermColor.success(f"{brnum} downloaded from Pdf_URL"),
                    flush=True,
                )
                return  # Exit function if successful
        except Exception as e:
            print(
                TermColor.warn(f"{brnum} - Download Error for Pdf_URL: {e}"), flush=True
            )
            pass  # Log error and proceed to next step

        # If the direct PDF download fails, attempt to generate from HTML address
        if isinstance(
            html_address, str
        ):  # Ensure that HTML address exists and is a string
            try:
                weasyprint.HTML(html_address).write_pdf(
                    file_path
                )  # Convert HTML to PDF

                if validate_downloaded_pdf(file_path):
                    print(
                        TermColor.success(
                            f"{brnum} downloaded from Report Html Address",
                        ),
                        flush=True,
                    )
                    return
            except Exception as e:
                print(
                    TermColor.warn(
                        f"{brnum} - Download Error for Report Html Address: {e}"
                    ),
                    flush=True,
                )
                pass  # Log error if needed

    def __parallel_download(
        self,
        data: DataFrame,
        out_dir: str,
        max_workers: int = None,
    ) -> None:
        """
        Downloads reports in parallel using multiple worker processes.

        Args:
            max_workers (int, optional): Number of parallel processes to use. Defaults to the number of CPU cores.
        """

        # If max_workers is not specified, use all available CPU cores
        if max_workers is None:
            max_workers = (
                os.cpu_count() or 4
            )  # Fallback to 4 if os.cpu_count() returns None

        # Create a ProcessPoolExecutor with the specified number of workers
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(
                    self.process_single_entry,
                    brnum,
                    data.at[brnum, "Pdf_URL"],
                    data.at[brnum, "Report Html Address"],
                    out_dir,
                ): brnum
                for brnum in data.index
            }

            for future in as_completed(futures):  # Allows real-time output
                try:
                    future.result()  # Ensures exceptions are raised in the main process
                except Exception as e:
                    print(TermColor.fail(f"Error in process {futures[future]}: {e}"))

    def __single_thread_download(self, data: DataFrame, out_dir: str) -> None:
        """
        Downloads pdf files in single-threaded mode
        """
        for brnum in data.index:
            self.process_single_entry(
                brnum=brnum,
                pdf_url=data.at[brnum, "Pdf_URL"],
                html_address=data.at[brnum, "Report Html Address"],
                out_dir=out_dir,
            )

    def download(self, data: DataFrame, out_dir):
        """
        General method for download of pdf files.
            runs in multi-threaded mode unless otherwise specified
        """
        # Ensure that output directory exists
        os.makedirs(out_dir, exist_ok=True)

        if self.multithreaded_off:
            print("downloading in single-threaded mode")
            self.__single_thread_download(data=data, out_dir=out_dir)
        else:
            print("downloading in multi-threaded mode")
            self.__parallel_download(data=data, out_dir=out_dir)


class Metadata:

    def __init__(self, out_dir: str, source_file: str, download_output_dir: str):
        self.out_dir = out_dir
        self.out_file = f"Metadata{source_file[4:-5]}.xlsx"
        self.download_output_dir = download_output_dir
        pass

    def save(self, data: DataFrame):
        """
        Saves collected metadata to a excel file
        """
        try:
            os.makedirs(self.out_dir, exist_ok=True)
            # Create new column in DataFrame and set all to "No" by default
            data["pdf_downloaded"] = "No"

            # Look through files in folder where they were downloaded
            for file in os.listdir(self.download_output_dir):
                # Ensure that it is actually a file and now something else
                if os.path.isfile(os.path.join(self.download_output_dir, file)):
                    # Remove .pdf from filename string to get the row index of the file in the data
                    index = file[:-4]
                    # Set to "Yes" for the column "pdf_downloaded" on the row
                    data.loc[index, "pdf_downloaded"] = "Yes"

            # Write DataFrame to excel file
            writer = ExcelWriter(
                os.path.join(self.out_dir, self.out_file), engine="openpyxl"
            )
            data.to_excel(writer, sheet_name="Sheet1")
            writer._save()
        except Exception as e:
            print(e)
