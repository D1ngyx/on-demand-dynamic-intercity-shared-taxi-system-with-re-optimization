import pandas as pd
import tqdm
import numpy as np
import time
from time_test import cal_expected_ride_time

D = 10000 # !!!!
V = 16 # m/s == 60km/h
TWL = 12000 # !!!!
TWR = 36000 # !!!!
cnt = 0
CSV_FILE = "361_to_362_small.csv"
df = pd.read_csv(CSV_FILE)
n = df.shape[0]

begin_time = time.time()

def euclidean_distance(lat1, lon1, lat2, lon2):
    ori = str(lat1) + ',' + str(lon1)
    des = str(lat2) + ',' + str(lon2)
    return cal_expected_ride_time(ori, des)
    
    # lat1, lon1, lat2, lon2 = map(float, [lat1, lon1, lat2, lon2])
    # lat1_rad, lon1_rad = np.radians(lat1), np.radians(lon1)
    # lat2_rad, lon2_rad = np.radians(lat2), np.radians(lon2)
    # distance = np.sqrt((lat2_rad - lat1_rad)**2 + (lon2_rad - lon1_rad)**2)
    # earth_radius = 6371.0
    # distance_km = earth_radius * distance
    # return distance_km * 1000  # 米

def get_loc(r):
    return (r["Ox"],r["Oy"]), (r["Dx"],r["Dy"])

def cal_dev(route, index):
    dist = []
    for i in range(1, 4):
        dist.append(euclidean_distance(route[i-1][0], route[i-1][1], route[i][0], route[i][1]))
    dev12 = []
    for od in index:
        real_dist = 0
        for j in range(od[0], od[1]):
            real_dist += dist[j]
        dev12.append(real_dist - euclidean_distance(route[od[0]][0], route[od[0]][1], route[od[1]][0], route[od[1]][1]))
    return dev12  # [乘客1的偏移, 乘客2的偏移]

def cal_tw(route, index, t1, t2):
    time_o2o = euclidean_distance(route[0][0], route[0][1], route[1][0], route[1][1]) * V
    t1, t2 = map(int, [t1, t2])
    tw_1_l = t1 - TWL
    tw_1_r = t1 + TWR
    tw_2_l = t2 - TWL
    tw_2_r = t2 + TWR
    if index[0][0] == 0: # 枚举r1时间窗
        for t in range(tw_1_l, tw_1_r):
            if tw_2_l <= t + time_o2o <= tw_2_r:
                return 1
        return 0 
    else:  # 枚举r2时间窗
        for t in range(tw_2_l, tw_2_r):
            if tw_1_l <= t + time_o2o <= tw_1_r:
                return 1
        return 0
    
def calc(r1, r2):
    o1, d1 = get_loc(r1)
    o2, d2 = get_loc(r2)
    t1 = r1["TIME"]
    t2 = r2["TIME"]
    routes = [(o1, o2, d1, d2), (o1, o2, d2, d1), (o2, o1, d1, d2), (o2, o1, d2, d1)]
    indexs = [((0,2), (1,3)), ((0,3),(1,2)), ((1,2),(0,3)), ((1,3),(0,2))]
    dev = []
    tw = []
    for i in range(4):
        dev.append(cal_dev(routes[i], indexs[i]))
        tw.append(cal_tw(routes[i], indexs[i], t1, t2))
    return dev, tw
    
    
adj = []
for _ in range(n):
    adj.append([])
    
for i in tqdm.trange(n):
    r1 = df.loc[i]
    for j in tqdm.trange(i+1, n):
    # for j in range(i+1, n):
        r2 = df.loc[j]
        dev, tw = calc(r1, r2)
        for k in range(0, 4):
            if dev[k][0] < D and dev[k][1] < D and tw[k] == 1:
                adj[i].append(j)
                adj[j].append(i)
                break

print(time.time() - begin_time)

adj_str = str(adj)
with open('adj.txt', 'w') as file:
    file.write(adj_str)
        
""" 2023/12/26 18:45 """


