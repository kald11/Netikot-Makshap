from core.classes.NetworkComponent import NetworkComponent
class Camera(NetworkComponent):
    def __init__(self, port, password,number,id):
        super().__init__(port,password)
        self.number = number
        self.id = id

    def __str__(self):
        return f"Camera(port={self.port}, password={self.password}, number={self.number}, id={self.id})"
