class TermColor:

    class bcolors:
        HEADER = "\033[95m"
        OKBLUE = "\033[94m"
        OKCYAN = "\033[96m"
        OKGREEN = "\033[92m"
        WARNING = "\033[93m"
        FAIL = "\033[91m"
        ENDC = "\033[0m"
        BOLD = "\033[1m"
        UNDERLINE = "\033[4m"

    @staticmethod
    def success(message: str) -> str:
        return TermColor.bcolors.OKGREEN + message + TermColor.bcolors.ENDC

    @staticmethod
    def info(message: str) -> str:
        return TermColor.bcolors.OKCYAN + message + TermColor.bcolors.ENDC

    @staticmethod
    def warn(message: str) -> str:
        return TermColor.bcolors.WARNING + message + TermColor.bcolors.ENDC

    @staticmethod
    def fail(message: str) -> str:
        return TermColor.bcolors.FAIL + message + TermColor.bcolors.ENDC
