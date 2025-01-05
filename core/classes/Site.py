from core.classes.Results import Results


class Site:
    def __init__(self, site_name, ip, camera, nvr, modem,brigade,camera_id):
        self.prot = "http"
        self.site_name = site_name
        self.ip = ip
        self.camera = camera
        self.nvr = nvr
        self.modem = modem
        self.results = Results()
        self.brigade = brigade
        self.camera_id = camera_id

    def get_camera_url(self):
        return f'{self.prot}://{self.ip}:{self.camera.port}'

    def get_nvr_url(self):
        return f'{self.prot}://{self.ip}:{self.nvr.port}'

    def __str__(self):
        return f"Site Name: {self.site_name},IP: {self.ip}, Cameras: {self.camera}, NVR: {self.nvr}, Modem: {self.modem}"

