import time
from datetime import datetime
from config.settings import Config
from core.google_sheets import GoogleSheets
from core.services import NetikotService
from utils.utils import execution_time


def run_pipeline(status_callback=None, stop_flag=None):
    if stop_flag and stop_flag():
        return

    config = Config().get_config()
    gs = GoogleSheets()
    start_time_str = datetime.now().strftime(config["project_setup"]["format_datetime"])
    start_timer = time.perf_counter()

    if stop_flag and stop_flag():
        return

    camera_array = execution_time(gs.get_data, "Fetching data", status_callback)
    if stop_flag and stop_flag():
        return

    service = NetikotService(camera_array)

    if stop_flag and stop_flag():
        return
    execution_time(service.ping, "Ping", status_callback)

    if stop_flag and stop_flag():
        return
    execution_time(service.login_cameras, "Login", status_callback)

    if stop_flag and stop_flag():
        return
    execution_time(service.get_camera_data, "Fetching Captures", status_callback)

    if stop_flag and stop_flag():
        return
    execution_time(service.unknowns, "Unknowns", status_callback)

    if stop_flag and stop_flag():
        return
    service.modem_test()
    results_array = service.get_results()
    gs.upload_data(data=results_array, start_time=start_time_str)

    if status_callback:
        status_callback("ALL_DONE", duration=(time.perf_counter() - start_timer))


def run_single_site(row_index: int, stop_flag=None):
    if stop_flag and stop_flag():
        return None

    gs = GoogleSheets()
    site = gs.get_row(row_index)

    if stop_flag and stop_flag():
        return site
    site.ping_nvr()

    if stop_flag and stop_flag():
        return site
    site.ping_camera()

    if stop_flag and stop_flag():
        return site
    site.try_login("nvr")

    if stop_flag and stop_flag():
        return site
    site.try_login("camera")
    if stop_flag and stop_flag():
        return site
    site.get_camera_time("nvr")

    if stop_flag and stop_flag():
        return site
    site.get_camera_time("camera")

    # if stop_flag and stop_flag():
    #     return site

    if stop_flag and stop_flag():
        return site
    site.get_captures()

    if stop_flag and stop_flag():
        return site
    site.check_playback()

    return site



if __name__ == "__main__":
    try:
        run_pipeline()
    except Exception as e:
        print("ERROR:", e)
        time.sleep(1000)
