from core.classes.NetworkComponent import NetworkComponent


class Nvr(NetworkComponent):
    def __init__(self, port, password):
        super().__init__(port, password)

    def __str__(self):
        return f"Network Video Recorder (NVR) on port {self.port} with password {self.password}"
