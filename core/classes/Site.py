from config.settings import Config
from requests.auth import HTTPDigestAuth


class Site:
    def __init__(self, site_name=None, ip=None, camera=None, nvr=None, modem=None, brigade=None, camera_id=None, camera_type=None, prot=None, longitude=None, latitude=None):
        self.config = Config().get_config()
        self.prot = "https" if prot.upper() == "V" else "http"
        self.site_name = site_name
        self.ip = ip
        self.camera = camera
        self.nvr = nvr
        self.modem = modem
        self.camera_type = camera_type
        self.brigade = brigade
        self.camera_id = camera_id
        self.credentials = HTTPDigestAuth(self.config["project_setup"]["username"], nvr.password)
        self.credentials_camera = HTTPDigestAuth(self.config["project_setup"]["username"], camera.password)
        self.longitude = longitude
        self.latitude = latitude

    def get_camera_url(self):
        return f'{self.prot}://{self.ip}:{self.camera.port}'

    def get_nvr_url(self):
        return f'{self.prot}://{self.ip}:{self.nvr.port}'

    def __str__(self):
        return f"Site Name: {self.site_name},IP: {self.ip}:{self.nvr.port} {self.nvr.password}, Camera Number: {self.camera.number}"
