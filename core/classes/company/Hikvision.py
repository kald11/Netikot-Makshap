from core.classes.company.Company import Company


class Hikvision(Company):

    def __init__(self, site):
        super().__init__("Hikvision", site=site)
        print(self.site)

    def get_captures(self):
        pass

    def get_camera_time(self):
        pass


