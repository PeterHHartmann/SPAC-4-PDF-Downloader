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


def success(message: str) -> str:
    return bcolors.OKGREEN + message + bcolors.ENDC


def info(message: str) -> str:
    return bcolors.OKCYAN + message + bcolors.ENDC


def warn(message: str) -> str:
    return bcolors.WARNING + message + bcolors.ENDC


def fail(message: str) -> str:
    return bcolors.FAIL + message + bcolors.ENDC
