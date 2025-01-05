from abc import ABC, abstractmethod


class Company(ABC):
    def __init__(self, company_name,site):
        self.site = site
        self.company_name = company_name

    @abstractmethod
    def get_captures(self):
        pass

    @abstractmethod
    def get_camera_time(self):
        pass

    @abstractmethod
    def ping_camera(self):
        pass

    @abstractmethod
    def ping_nvr(self):
        pass

    def get_company_name(self):
        return self.company_name

    def get_site(self):
        return self.site

    def set_site(self, site):
        self.site = site
