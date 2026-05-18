class _Logger:
    def __init__(self, name: str) -> None:
        self._name = name

    def info(self, msg: str, **kw: object) -> None:
        extra = " | " + " ".join(f"{k}={v}" for k, v in kw.items()) if kw else ""
        print(f"[{self._name}] {msg}{extra}")

    def warning(self, msg: str, **kw: object) -> None:
        extra = " | " + " ".join(f"{k}={v}" for k, v in kw.items()) if kw else ""
        print(f"[{self._name}] WARNING {msg}{extra}")


def get_logger(name: str) -> _Logger:
    return _Logger(name)
