class Site:
    def __init__(self, site_name, ip, camera, nvr, modem):
        self._site_name = site_name
        self._ip = ip
        self.camera = camera
        self.nvr = nvr
        self.modem = modem

    def __str__(self):
        return f"Site Name: {self.site_name}, Cameras: {self.camera}, NVR: {self.nvr}, Modem: {self.modem}"
