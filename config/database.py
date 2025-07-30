from dataclasses import dataclass

@dataclass
class Server:
    host: str
    port: str
    username: str
    password: str

    def __init__(self, host, port, username, password) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password


@dataclass
class DataBaseServer(Server):
    def __init__(self, host, port, username, password, name) -> None:
        super().__init__(host, port, username, password)
        self.name: str = name
