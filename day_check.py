from core.google_sheets import GoogleSheets
from core.services import NetikotService
from utils.utils import execution_time

gs = GoogleSheets()
camera_array = execution_time(gs.get_data, "Fetching data")
service = NetikotService(camera_array)
execution_time(service.ping, "Ping")
execution_time(service.login_cameras, "Login")
service.get_captures("24_hours")
results = service.get_daily_results()
gs.upload_daily_data(results)
