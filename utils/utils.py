import threading
from collections import OrderedDict
from datetime import datetime
from config.settings import Config
import pandas as pd


# ----------------------- Arrays and df functions -----------------------
def columns_to_rows_array(columns):
    return [list(row) for row in zip(*columns)]


def array_to_df(data):
    return pd.DataFrame(data[1:], columns=data[0])


def filter_unconnected_cameras(array):
    return [camera for camera in array if camera.flags.get("is_nvr_ping")]


def ordered_dict_to_dict(d):
    if isinstance(d, OrderedDict):
        d = dict(d)
        for k, v in list(d.items()):
            d[k] = ordered_dict_to_dict(v)
    elif isinstance(d, list):
        for i in range(len(d)):
            d[i] = ordered_dict_to_dict(d[i])
    elif d == "false":
        d = False
    elif d == "True":
        d = True
    return d


# ----------------------- Threads functions -----------------------
def use_thread(cameras_array, worker):
    threads = []

    for camera in cameras_array:
        thread = threading.Thread(target=worker, args=(camera,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()


# ----------------------- Formats ----------------------------------
def datetime_format(local_time):
    format = Config().get_config()["project_setup"]["format_datetime"]
    return datetime.strptime(local_time, format)
