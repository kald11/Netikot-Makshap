from core.google_sheets import GoogleSheets
from core.services import NetikotService

gs = GoogleSheets()
site = gs.get_row(8)
site.flags["is_nvr_ping"] = True
service = NetikotService([site])
service.login_cameras()
service.unknowns()
