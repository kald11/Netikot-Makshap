from abc import ABC, abstractmethod


class NetworkComponent(ABC):
    def __init__(self, port,password):
        self.port = port
        self.password = password

