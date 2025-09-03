import threading
import time
import uuid
from collections import OrderedDict
from datetime import datetime, timedelta

import pytz

from config.settings import Config
import pandas as pd


# ----------------------- Arrays and df functions -----------------------
def columns_to_rows_array(columns):
    pad_lists(columns)
    return [list(row) for row in zip(*columns)]


def array_to_df(data):
    return pd.DataFrame(data[1:], columns=data[0])


def filter_unconnected_cameras(array):
    return [camera for camera in array if camera.flags.get("is_nvr_ping")]


def parse_text_to_dict(d):
    if isinstance(d, OrderedDict):
        d = dict(d)
        for k, v in list(d.items()):
            d[k] = parse_text_to_dict(v)
    elif isinstance(d, list):
        for i in range(len(d)):
            d[i] = parse_text_to_dict(d[i])
    elif d == "false":
        d = False
    elif d == "True":
        d = True
    return d


def pad_lists(lists):
    max_length = max(len(lst) for lst in lists)
    for i in range(len(lists)):
        while len(lists[i]) < max_length:
            lists[i].append('')
    return lists


def build_index_map(index_list):
    return {i + 1: idx for i, idx in enumerate(index_list)}


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
def get_captures_times(type=None):
    format = "%Y-%m-%dT%H:%M:%SZ"
    jerusalem_tz = pytz.timezone('Asia/Jerusalem')
    current_time = datetime.now(jerusalem_tz)
    match type:
        case "morning":
            yesterday = current_time - timedelta(days=1)
            start_time = yesterday.strftime("%Y-%m-%dT10:00:00Z")
            end_time = yesterday.strftime("%Y-%m-%dT11:00:00Z")
        case "night":
            yesterday = current_time - timedelta(days=1)
            start_time = yesterday.strftime("%Y-%m-%dT22:00:00Z")
            end_time = yesterday.strftime("%Y-%m-%dT23:00:00Z")
        case "24_hours":
            start_time = (current_time - timedelta(hours=24)).strftime(format)
            end_time = current_time.strftime(format)
        case None:
            start_time = (current_time - timedelta(hours=3)).strftime(format)
            end_time = current_time.strftime(format)
    return start_time, end_time


def datetime_format(local_time):
    format = Config().get_config()["project_setup"]["format_datetime"]
    return datetime.strptime(local_time, format)


def get_body_by_model(model, index, start_time, end_time, camera_number, is_retry, unknown):
    search_id = str(uuid.uuid4())
    if is_retry:
        return f"""<DataOperation>
                   <operationType>search</operationType>
                   <searchCond>
                       <searchID>{search_id}</searchID>
                       <timeSpanList>
                           <timeSpan>
                               <startTime>{start_time}</startTime>
                               <endTime>{end_time}</endTime>
                           </timeSpan>
                       </timeSpanList>
                       <criteria>
                           <dataType>0</dataType>
                           <violationType>0</violationType>
                           <channel/>
                           <plateType/>
                           <plateColor/>
                           <direction/>
                           <incidentCorrect/>
                           <plate/>
                           <speedMin/>
                           <speedMax/>
                           <vehicleType/>
                           <vehicleColor/>
                           <laneNo/>
                           <surveilType>0</surveilType>
                           <romoteHost/>
                           <analysised>true</analysised>
                           <sendFlag/>
                       </criteria>
                       <searchResultPosition>0</searchResultPosition>
                       <maxResults>20</maxResults>
                       <vehicleSubTypeList/>
                   </searchCond>
               </DataOperation>"""
    # else:
    #     return f"""<DataOperation>
    #     <operationType>search</operationType>
    #     <searchCond>
    #         <searchID>{search_id}</searchID>
    #         <timeSpanList>
    #             <timeSpan>
    #                 <startTime>{start_time}</startTime>
    #                 <endTime>{end_time}</endTime>
    #             </timeSpan>
    #         </timeSpanList>
    #         <criteria>
    #             <dataType>0</dataType>
    #             <violationType>0</violationType>
    #             <channel>{index}</channel>
    #             <plateType/>
    #             <plateColor/>
    #             <direction/>
    #             <incidentCorrect/>
    #             <plate/>
    #             <speedMin/>
    #             <speedMax/>
    #             <vehicleType/>
    #             <vehicleColor/>
    #             <laneNo/>
    #             <surveilType>0</surveilType>
    #             <romoteHost/>
    #             <analysised>true</analysised>
    #             <sendFlag/>
    #         </criteria>
    #         <searchResultPosition>{index}</searchResultPosition>
    #         <maxResults>100</maxResults>
    #         <vehicleSubTypeList/>
    #     </searchCond>
    # </DataOperation>"""
    match model:
        case 1:
            return f"""<DataOperation>
            <operationType>search</operationType>
            <searchCond>
                <searchID>{search_id}</searchID>
                <timeSpanList>
                    <timeSpan>
                        <startTime>{start_time}</startTime>
                        <endTime>{end_time}</endTime>
                    </timeSpan>
                </timeSpanList>
                <criteria>
                    <dataType>0</dataType>
                    <violationType>0</violationType>
                    <channel/>
                    <plateType/>
                    <plateColor/>
                    <direction/>
                    <incidentCorrect/>
                    <plate/>
                    <speedMin/>
                    <speedMax/>
                    <vehicleType/>
                    <vehicleColor/>
                    <laneNo/>
                    <surveilType>0</surveilType>
                    <romoteHost/>
                    <analysised>true</analysised>
                    <sendFlag/>
                </criteria>
                <searchResultPosition>0</searchResultPosition>
                <maxResults>20</maxResults>
                <vehicleSubTypeList/>
            </searchCond>
        </DataOperation>"""

            # return f'''
            #                        <DataOperation>
            #                            <operationType>search</operationType>
            #                            <searchCond>
            #                                <searchID>{search_id}</searchID>
            #                                <timeSpanList>
            #                                    <timeSpan>
            #                                        <startTime>{start_time}</startTime>
            #                                        <endTime>{end_time}</endTime>
            #                                    </timeSpan>
            #                                </timeSpanList>
            #                                <criteria>
            #                                    <dataType>0</dataType>
            #                                    <channel>{camera_number}</channel>
            #                                    <violationType>0</violationType>
            #                                    <surveilType>0</surveilType>
            #                                    <analysised>true</analysised>
            #                                </criteria>
            #                                <searchResultPosition>{index}</searchResultPosition>
            #                            </searchCond>
            #                        </DataOperation>'''

        case 2:
            return f'''
            <CMSearchDescription>
                <searchID>{search_id}</searchID>
                <trackList>
                    <trackID>{camera_number}03</trackID>
                </trackList>
                <timeSpanList>
                    <timeSpan>
                        <startTime>{start_time}</startTime>
                        <endTime>{end_time}</endTime>
                    </timeSpan>
                </timeSpanList>
                <contentTypeList>
                    <contentType>metadata</contentType>
                </contentTypeList>                
                <maxResults>50</maxResults>
                <searchResultPostion>{index}</searchResultPostion>                
                <metadataList>
                    <metadataDescriptor>//recordType.meta.std-cgi.com/vehicleDetection</metadataDescriptor>
                    <SearchProperity>
                        <country>255</country>
                    </SearchProperity>                  
                </metadataList>
            </CMSearchDescription>'''

        case 3:
            return f'''<CMSearchDescription>
                        <searchID>{search_id}</searchID>
                        <timeSpanList>
                            <timeSpan>
                                <startTime>{start_time}</startTime>
                                <endTime>{end_time}</endTime>
                            </timeSpan>
                        </timeSpanList>
                        <critera>
                            <channel>{camera_number}</channel>
                            <surveilType>0</surveilType>
                            <dataType>0</dataType>
                            <violationType>0</violationType>
                        </critera>
                        <searchResultPostion>{index}</searchResultPostion>
                        <maxResults>5000</maxResults>
                    </CMSearchDescription>'''


# ----------------------- Formats ----------------------------------
def execution_time(func, func_name, status_callback=None,*args):
    if status_callback:
        status_callback(func_name, started=True)

    start = time.perf_counter()
    result = func(*args)
    end = time.perf_counter()

    duration = end - start

    if status_callback:
        status_callback(func_name, started=False, finished=True, duration=duration)

    return result

