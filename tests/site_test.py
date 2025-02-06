from core.google_sheets import GoogleSheets
from main import service

gs = GoogleSheets()
site = gs.get_row(453)
site.flags["is_nvr_ping"] = True
# site.try_login()

service.get_camera_data()



