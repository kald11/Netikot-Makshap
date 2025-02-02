from core.google_sheets import GoogleSheets
from core.services import NetikotService

gs = GoogleSheets()
cameras = gs.get_data()
cameras = [camera for camera in cameras if camera.company_name == "Dahua"]
service = NetikotService(cameras)
service.ping()
service.login_cameras()
service.get_camera_data()