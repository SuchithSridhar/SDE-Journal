
debug = "DEBUG"
info = "INFO"
warn = "WARNING"
critical = "CRITICAL"


def log(string, type="INFO"):
    print(f"{type}: {string}")
