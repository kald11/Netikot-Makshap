from datetime import datetime

from core.google_sheets import GoogleSheets
from core.services import NetikotService
from utils.utils import execution_time

start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
gs = GoogleSheets()
camera_array = execution_time(gs.get_data, "Fetching data from Google Sheet")
service = NetikotService(camera_array)
# execution_time(service.ping, "Ping")
# execution_time(service.login_cameras, "Login")


def main_captures():
    service.get_camera_data()


def main_unknowns_check():
    service.unknowns()


if __name__ == "__main__":
    execution_time(main_unknowns_check, "Unknowns")
    execution_time(main_captures, "Fetching captures")
    results_array = service.get_results()
    gs.upload_data(data=results_array, start_time=start_time)
