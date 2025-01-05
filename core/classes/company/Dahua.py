from core.classes.company.Company import Company
from utils.network_helpers import ping


class Dahua(Company):

    def __init__(self, site):
        super().__init__("Dahua", site=site)

    def ping_camera(self):
        is_cam_ping = ping(self.site.prot, self.site.ip, self.site.camera.port)
        self.site.results.is_camera_ping = is_cam_ping

    def ping_nvr(self):
        is_nvr_ping = ping(self.site.prot, self.site.ip, self.site.nvr.port)
        self.site.results.is_camera_ping = is_nvr_ping

    def get_captures(self):
        # Add the implementation here
        pass

    def get_camera_time(self):
        # Add the implementation here
        pass
