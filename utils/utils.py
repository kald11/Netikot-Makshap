import threading
import uuid
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


def get_body_by_model(model, index, start_time, end_time, camera_number):
    search_id = str(uuid.uuid4())
    match model:
        case 1:
            return f'''
                                   <DataOperation>
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
                                               <channel>{camera_number}</channel>
                                               <violationType>0</violationType>
                                               <surveilType>0</surveilType>
                                               <analysised>true</analysised>
                                           </criteria>
                                           <searchResultPosition>{index}</searchResultPosition>                                    
                                       </searchCond>
                                   </DataOperation>'''
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
                <searchResultPostion>100</searchResultPostion>                
                <metadataList>
                    <metadataDescriptor>//recordType.meta.std-cgi.com/vehicleDetection</metadataDescriptor>
                    <SearchProperity>
                        <country>255</country>
                    </SearchProperity>                  
                </metadataList>
            </CMSearchDescription>'''
        case 3:
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
                    <contentType>picture</contentType>
                </contentTypeList>
                <maxResults>5000</maxResults>                
                <searchResultPostion>{index}</searchResultPostion>
                <metadataList>
                    <metadataDescriptor>//recordType.meta.std-cgi.com/allPic</metadataDescriptor>
                </metadataList>

            </CMSearchDescription>'''

        case 4:
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
