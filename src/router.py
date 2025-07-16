import requests
from result_data import mttq_cnt
import math
import numpy as np
from para import CONSIDER_TRAFFIC_CONGESTION, DATA_NAME

XM_MORNING_LOGNROMAL_MEAN = -1.4031
XM_MORNING_LOGNROMAL_SIGM = 0.7935
XM_EVENING_LOGNROMAL_MEAN = -0.6152
XM_EVENING_LOGNROMAL_SIGM = 0.4483

AX_MORNING_LOGNROMAL_MEAN = -1.7195
AX_MORNING_LOGNROMAL_SIGM = 0.4804
AX_EVENING_LOGNROMAL_MEAN = -0.8501
AX_EVENING_LOGNROMAL_SIGM = 0.3035

ZZ_MORNING_LOGNROMAL_MEAN = -1.8210
ZZ_MORNING_LOGNROMAL_SIGM = 0.3672
ZZ_EVENING_LOGNROMAL_MEAN = -1.1114
ZZ_EVENING_LOGNROMAL_SIGM = 0.5136

NORMAL_LOGNROMAL_MEAN = -2.5276
NORMAL_LOGNROMAL_SIGM = 0.1963

# samples = np.random.lognormal(XM_EVENING_LOGNROMAL_MEAN, XM_EVENING_LOGNROMAL_SIGM, 10)
# print(samples)

def is_in_congrestion_time(cur_time: int):
    """ 0 refer to morning peak, 2 refer to evening peak, 0 refer to normal situation """
    if 25200 <= cur_time <= 32400: 
        return 1
    elif 61200 <= cur_time <= 68400:
        return 2
    else:
        return 0

def degrees_to_radians(degrees):     
    return degrees * math.pi / 180
def euc(coords: list[tuple]) -> float:
    coord1, coord2 = coords
    lat1, lon1 = map(float, coord1)
    lat2, lon2 = map(float, coord2)
    lat1_rad = degrees_to_radians(lat1)
    lon1_rad = degrees_to_radians(lon1)
    lat2_rad = degrees_to_radians(lat2)
    lon2_rad = degrees_to_radians(lon2)
    distance = math.sqrt((lat2_rad - lat1_rad)**2 + (lon2_rad - lon1_rad)**2)
    return distance

def is_same_coord(coord1:tuple, coord2:tuple) -> bool:
    global mttq_cnt
    res = tt([coord1, coord2])
    mttq_cnt -= 1
    return True if res == 0 else False

def trans_from_coords_to_osrmstr(coords_list: list) -> str:
    """
    Trans coordinates to OSRM format. 

    input:
        - coor_tuple: coordinate info.
        - e.x.: [(lon1,lat1), (lon2,lat2), (lon3,lat3)].

    output:
        - string. 
        - e.x.: "lon1,lat1;lon2,lat2;lon3,lat3;...".
    """
    coords_str = [f"{lon},{lat}" for lon, lat in coords_list]
    res = ";".join(coords_str)
    return res


def trans_from_osrmstr_to_corrds(waypoints: str):
    coords_list = waypoints.split(";")
    res = [tuple(map(float, coord.split(","))) for coord in coords_list]
    return res


def tt(coords_list: list[tuple], cur_time:int = -1, city:int = -1) -> int:
    """ if you don't want to config real map data with OSRM, then ues this. BUT,
        ATTENTION: the difference bewteen ORSM and euclidean-liked method is VERY VERY VERY BIG."""
    """ NEW FEATURE(R2): Added traffic congestion simulation using the Monte Carlo method to weight travel time with a congestion index """
    def haversine(coord1, coord2):
        R = 6371.0  
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c  
        return distance
    if len(coords_list) != 2:
        raise ValueError("coords_list must contain exactly two coordinate tuples.")
    coord1, coord2 = coords_list
    distance_km = haversine(coord1, coord2)
    average_speed_kmh = 60
    travel_time_hours = distance_km / average_speed_kmh
    travel_time_seconds = travel_time_hours * 3600
    travel_time_seconds *= 2 
    if CONSIDER_TRAFFIC_CONGESTION == 1:
        #! Monte Carlo
        in_congrestion_time = is_in_congrestion_time(cur_time)
        if in_congrestion_time == 0:
            travel_time_seconds *= (1 + np.random.lognormal(NORMAL_LOGNROMAL_MEAN, NORMAL_LOGNROMAL_SIGM, 1)[0])
        elif in_congrestion_time == 1:
            if city == 0: 
                travel_time_seconds *= (1 + np.random.lognormal(XM_MORNING_LOGNROMAL_MEAN, XM_MORNING_LOGNROMAL_SIGM, 1)[0])
            else:
                if DATA_NAME == "XZ":
                    travel_time_seconds *= (1 + np.random.lognormal(ZZ_MORNING_LOGNROMAL_MEAN, ZZ_MORNING_LOGNROMAL_SIGM, 1)[0])
                elif DATA_NAME == "XA":
                    travel_time_seconds *= (1 + np.random.lognormal(AX_MORNING_LOGNROMAL_MEAN, AX_MORNING_LOGNROMAL_SIGM, 1)[0])
                else:
                    raise Exception("[ERROR]: wrong dataset name")
        elif in_congrestion_time == 2:
            if city == 0:
                travel_time_seconds *= (1 + np.random.lognormal(XM_EVENING_LOGNROMAL_MEAN, XM_EVENING_LOGNROMAL_SIGM, 1)[0])
            else:
                if DATA_NAME == "XZ":
                    travel_time_seconds *= (1 + np.random.lognormal(ZZ_EVENING_LOGNROMAL_MEAN, ZZ_EVENING_LOGNROMAL_SIGM, 1)[0])
                elif DATA_NAME == "XA":
                    travel_time_seconds *= (1 + np.random.lognormal(AX_EVENING_LOGNROMAL_MEAN, AX_EVENING_LOGNROMAL_SIGM, 1)[0])
                else:
                    raise Exception("[ERROR]: wrong dataset name")
        else:
            pass
    else:
        pass
    return int(travel_time_seconds)

class Router:
    def __init__(self, coords_list: list) -> None:
        """
        Para:
            - waypoints
            - e.x.: "lon1,lat1;lon2,lat2;lon3,lat3;...".

        Retn:
            - json format data. 
        """
        waypoints = trans_from_coords_to_osrmstr(coords_list)
        url = f"http://127.0.0.1:5000/route/v1/driving/{waypoints}?steps=true"
        global mttq_cnt
        response = requests.get(url)
        self.json_data = response.json();

    def fix_incorrect_coords(self, i: int) -> tuple:
        """ Returns the corrected road network point for the i-th waypoint, primarily adjusting passenger coordinates to align with the actual road network when generating passenger information. """
        return tuple(self.json_data["waypoints"][i]["location"])

    def generate_maneuver_waypoints(self):
        """
        Generate more detailed navigation routes using passenger pickup/drop-off points.
        For example: X → Y → Z becomes X → a → b → Y → Y → c → Z, where the intermediate stop Y appears twice.
        """
        coords_list = []
        for i in range(len(self.json_data["routes"][0]["legs"])): 
            for j in range(len(self.json_data["routes"][0]["legs"][i]["steps"])):
                coords_list.append(tuple(self.json_data["routes"][0]["legs"][i]["steps"][j]["maneuver"]["location"]))
        return coords_list

    def generate_maneuver_times_list(self, last_time: int):
        """
        Get the segment travel time list based on the last vehicle visit time.

        e.x.:
            [ a -> b -> c ]
            [9:00, 9:10, 9:20]: 9:00 visit a，9:10 visit b，9:20 visit c .

        """
        duration_list = []
        visit_times_list = []
        for i in range(len(self.json_data["routes"][0]["legs"])): 
            for j in range(len(self.json_data["routes"][0]["legs"][i]["steps"])):
                duration_list.append(int(self.json_data["routes"][0]["legs"][i]["steps"][j]["duration"]))
        visit_times_list.append(last_time) 
        for i in range(0, len(duration_list)-1):
            visit_times_list.append(visit_times_list[i] + duration_list[i]) 
        return visit_times_list
    
    def generate_maneuver_types(self):
        """ Generate detailed navigation routes based on passenger pickup/drop-off points. """ 
        maneuver_type_list = []
        for i in range(len(self.json_data["routes"][0]["legs"])): 
            for j in range(len(self.json_data["routes"][0]["legs"][i]["steps"])):
                maneuver_type_list.append(self.json_data["routes"][0]["legs"][i]["steps"][j]["maneuver"]["type"])
        return maneuver_type_list
    




