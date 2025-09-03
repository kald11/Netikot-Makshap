from datetime import datetime
from config.settings import Config
from core.google_sheets import GoogleSheets
from core.services import NetikotService
from utils.utils import execution_time

# --------------------------GET_DATA---------------------
config = Config().get_config()
start_time_str = datetime.now().strftime(config["project_setup"]["format_datetime"])
gs = GoogleSheets()
cameras_array = execution_time(gs.get_data, "Fetching data from Google Sheet")
cameras_array_DEV = execution_time(gs.get_data_test, "Fetching data from Google Sheet")

#-----------------------FILTER---------------------------
filter_rules = {
    "company" : 'Hikvision'
}
filtered_array = []

#filter via gs headers
for i, site in enumerate(cameras_array_DEV):
    if i==718:
        x=1
    is_ok = True
    for rule, value in filter_rules.items():
        if site[rule] != value:
            is_ok = False
            break
    if is_ok:
        filtered_array.append(cameras_array[i])

#--------------------MUST_FUNCTIONS
service = NetikotService(filtered_array)
service.ping()
service.login_cameras()

# --------------------FUNCTIONS--------------------
service.get_camera_data()
service.unknowns()
service.modem_test()

# --------------------UPLOAD--------------------
results_array = service.get_results()
gs.upload_data_test(data=results_array, start_time=start_time_str)