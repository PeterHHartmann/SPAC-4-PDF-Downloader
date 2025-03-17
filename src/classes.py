from sys import stderr
from pandas import DataFrame, read_excel

import style
import queue


class ExcelReader:

    def __init__(self, file_path) -> None:
        self.file_path = file_path
        self.data = None
        pass

    def read(self, index_col="BRnum"):
        try:
            self.data = read_excel(self.file_path, sheet_name=0, index_col=index_col)
        except FileNotFoundError as e:
            stderr.write(
                style.fail(
                    f"Failed to read rapport data from file: {e.strerror}: {e.filename}\n"
                )
            )
            raise e


class Publisher:
    def __init__(self):
        self._message_queue = queue.Queue()
        self._subscribers = []

    def subscribe(self, subscriber):
        self._subscribers.append(subscriber)

    def publish(self, message):
        self._message_queue.put(message)
        for subscriber in self._subscribers:
            subscriber.receive(message)


class Subscriber:

    def receive(self, message):
        pass


class RapportDownloader(Publisher):

    def __init__(
        self,
        data: DataFrame,
        out_dir: str = "temp",
        limit: int = 10,
    ):
        super().__init__()
        self.out_dir = out_dir
        self.limit = limit
        self.data = data
        pass

    def download(self):
        for brnum in self.data[: self.limit]:
            file_path = f"{self.out_dir}/{str(brnum)}.pdf"
            self.publish(brnum)


class Metadata(Subscriber):

    def __init__(self, data: DataFrame, out_dir="temp"):
        super().__init__()
        self.out_dir = out_dir
        self.data = data
        self.foo = []
        pass

    def receive(self, message):
        print(message)
        pass
