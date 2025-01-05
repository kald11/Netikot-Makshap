from core.classes.networkComponents.NetworkComponent import NetworkComponent


class Camera(NetworkComponent):
    def __init__(self, port, password, number):
        super().__init__( port, password)
        self.number = number

    def __str__(self):
        return f"Camera( port={self.port}, password={self.password}, number={self.number}"
