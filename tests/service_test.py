from datetime import datetime
from config.settings import Config
from core.google_sheets import GoogleSheets
from core.services import NetikotService
from utils.utils import execution_time

config = Config().get_config()
start_time = datetime.now().strftime(config["project_setup"]["format_datetime"])
gs = GoogleSheets()
cameras_array = execution_time(gs.get_data, "Fetching data from Google Sheet")
service = NetikotService(cameras_array)
service.ping()
# service.login_cameras()
service.get_playback()
