from typing import Optional


class PlayerNotExistError(Exception):
    """Custom API Error."""

    def __init__(self, username: Optional[str], *args: object) -> None:
        self.username = username
        super().__init__(*args)


class NotFoundError(Exception):
    def __init__(self, name: str, search: str, *args: object) -> None:
        self.name = name
        self.search = search
        super().__init__(*args)


class ProvideServerError(Exception):
    """Custom API Error."""

    pass


class ServerUnavailableError(Exception):
    def __init__(self, name: str, *args: object) -> None:
        self.name = name
        super().__init__(*args)
