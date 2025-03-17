from classes import ExcelReader, Metadata, RapportDownloader


if __name__ == "__main__":
    print("Running main function")
    reader = ExcelReader("data/GRI_2017_2020.xlsx")
    reader.read()
    downloader = RapportDownloader(reader.data)
    metadata = Metadata(reader.data)
    downloader.subscribe(metadata)
    downloader.download()
