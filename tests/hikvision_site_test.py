from core.google_sheets import GoogleSheets
from core.services import NetikotService

gs = GoogleSheets()
site = gs.get_row(18)
site.flags["is_nvr_ping"] = True
service = NetikotService([site])
service.get_camera_data()
