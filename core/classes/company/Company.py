from abc import ABC, abstractmethod


class Company(ABC):
    def __init__(self, company_name, site):
        self.site = site
        self.company_name = company_name
        self.num_captures = 0
        self.flags = {"login_ok": False, "have_captures": False, "is_cam_ping": False, "is_nvr_ping": False}
        self.times = {"check_time": "", "current_camera_time": "", "is_synchronized": False}

    @abstractmethod
    def get_captures(self):
        pass

    @abstractmethod
    def get_camera_time(self):
        pass
