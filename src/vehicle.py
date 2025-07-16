from router import Router, tt, is_same_coord
from passenger import Order
from copy import deepcopy
import random 
from value_func import calc_longterm_cost

all_cars_data = []

tot_drivetime = 0
tot_trip_cnt = 0
no_mttq_cnt = 0
# tot_detour_coef = 0
# tot_wait_time = 0

insert_times = [[],[],[],[],[],[],[],[],[]]

def insert_after(lst, index, element):
    if index < 0:
        index += len(lst)
    if index >= len(lst):
        lst.append(element)
    else:
        lst.insert(index + 1, element)
        
def get_wp(wpid, orders_list):
    """ Convert waypoint ID information into tuple-formatted coordinates, automatically handling negative values. """
    if isinstance(wpid, tuple):
        return wpid
    if wpid > 0:
        return orders_list[wpid].orig
    elif wpid < 0:
        return orders_list[abs(wpid)].dest
    else:
        raise Exception("nonono")

def sync_times_and_waypoints(waypoints_, times_, start_, orders_list_, city_):
    """ Update the times array starting from the start position in waypoints (the start itself remains unchanged). 
        If the vehicle arrives before the order appears, the vehicle will wait. """
    end = len(waypoints_)
    times_ = times_[:start_+1]
    for i in range(start_+1, end):
        prewp = waypoints_[i-1]
        wp = waypoints_[i]
        if wp > 0:
            times_.append( max( times_[i-1]+tt([get_wp(prewp, orders_list_), get_wp(wp, orders_list_)]), orders_list_[abs(wp)].order_time ) )
        else:
            times_.append( times_[i-1]+tt([get_wp(prewp, orders_list_), get_wp(wp, orders_list_)]) ) 
    """ check feasible """
    feasible = True
    for i in range(start_, end):
        if i == 0:
            continue
        order_idx = waypoints_[i]
        arrive_time = times_[i]
        if order_idx > 0:
            if arrive_time > orders_list_[order_idx].ddlo or arrive_time < orders_list_[order_idx].order_time:
                feasible = False
                break
        else:
            if arrive_time > orders_list_[abs(order_idx)].ddld:
                feasible = False
                break   
    return feasible, times_ 

def shuffle_arr(arr, x, y):
    arr[x:y+1] = random.sample(arr[x:y+1], len(arr[x:y+1]))
    return arr

      
class Car:
    def __init__(self, id: int, city: int,
                 waypoints: list, times: list[int],
                 serving_list: list[int]):
        """ 
        id: The vehicle’s unique identifier, sequentially numbered starting from 1.
        waypoints: A list of waypoints (stops) represented by indices.
        Example: [start, 1, 2, -2, -1] denotes the route:
        start: Vehicle’s initial position (a tuple of (longitude, latitude)).
        1: Pickup location of passenger 1.
        2: Pickup location of passenger 2.
        -2: Drop-off location of passenger 2.
        -1: Drop-off location of passenger 1.

        times: Timestamps when the vehicle reaches each waypoint.
        Note: times[0] is the departure time from the initial location (start).
        wpidx: The estimated current position index of the vehicle in waypoints. Updated only once per vehicle status refresh (e.g., during simulation ticks).
        serving_list: List of passenger indices currently being served by this vehicle.
        """
        self.id = id
        self.city = city
        self.wpidx = 0
        self.waypoints = waypoints 
        self.times = times
        self.serving_list = serving_list
        self.seq = 0
        self.save_wp = []
        self.save_tm = []
        self.work_time = 0


    def update_wpidx(self, cur_time_: int):
        for i in range(0, len(self.waypoints)-1):
            if self.times[i] <= cur_time_ < self.times[i+1]: 
                self.wpidx = i
                return
        self.wpidx = -1
    
    def get_wp(self, id, orders_list):
        """ 将途经点的编号信息转化成tuple表示的坐标 """
        if isinstance(id, tuple):
            return id
        if id > 0:
            return orders_list[id].orig
        elif id < 0:
            return orders_list[abs(id)].dest
        else:
            raise Exception("nonono")

    def record(self, orders_list):
        """ finisha one trip, update all information """   
        for i in range(1, len(self.waypoints)):
            order_idx = self.waypoints[i]
            if order_idx > 0: # type: ignore
                orders_list[order_idx].pick_time = self.times[i]
            else:
                orders_list[abs(order_idx)].arrive_time = self.times[i] # type: ignore
        self.work_time += (self.times[-1] - self.times[0])
        global tot_drivetime, tot_trip_cnt
        tot_drivetime += self.times[-1] - self.times[0] 
        tot_trip_cnt += 1
        gps_waypoints = [get_wp(wp, orders_list) for wp in self.waypoints]
        self.save_wp.append(deepcopy(gps_waypoints)) 
        self.save_tm.append(deepcopy(self.times))

    def new_report(self, cur_time, orders_list):
        self.times = [cur_time]  # 更新时间和途经点信息
        self.waypoints = [self.get_wp(self.waypoints[-1], orders_list)]  
        self.wpidx = 0  # 重置wpidx
        self.city ^= 1   # 城市转换为对象城市
        self.serving_list = []
        self.seq += 1
            
    def refresh(self, cur_time: int, orders_list) -> None:
        if len(self.serving_list) == 0:  # if it is ideal car, just update time.
            self.times[0] = cur_time
            return
        global no_mttq_cnt
        no_mttq_cnt += 1
        self.update_wpidx(cur_time)  # update car position

        if self.wpidx == -1:  # finish his trip
            self.record(orders_list)
            self.new_report(cur_time, orders_list)

    def serve_order(self, order: Order, orig_idx:int, dest_idx:int, cur_time, orders_list):
        """ 
        Order Service Logic:
        1. Add the order to serving_list.
        2. Update the waypoints after insertion:
          a) Insert the pickup location into a specific position in waypoints.
          b) Insert the drop-off location into a specific position in waypoints.
        3. Update the times array after insertion.
        """
        self.serving_list.append(order.id)
        order.st = 1
        new_waypoints = deepcopy(self.waypoints)
        new_times = deepcopy(self.times)
        new_waypoints.insert(dest_idx+1, -order.id) # type: ignore
        new_waypoints.insert(orig_idx+1,  order.id) # type: ignore
        feasible, new_times = sync_times_and_waypoints(new_waypoints, new_times, self.wpidx, orders_list, self.city)
        self.waypoints = deepcopy(new_waypoints)
        self.times = deepcopy(new_times)

    def over_highway(self):
        """ Determine whether the vehicle has already passed the highway. The purpose is to avoid inserting new passengers for vehicles that have already used the highway. """
        if self.wpidx <= len(self.waypoints) // 2:
            return False
        else:
            return True
    
    def insert_to_car_based_value_function(self, order: Order, orders_list, val_func_):
        n = len(self.waypoints)
        min_delta = oidx = didx = 0x3f3f3f3f
        if val_func_ == calc_longterm_cost:
            old_value = 0
        else:
            old_value = val_func_(self.waypoints, self.times, self.wpidx, orders_list, order.id)
        if n == 1:  # ideal taxi
            new_waypoints = deepcopy(self.waypoints)
            new_times = deepcopy(self.times)
            new_waypoints.insert(1, -order.id) # type: ignore
            new_waypoints.insert(1,  order.id) # type: ignore
            feasible, new_times = sync_times_and_waypoints(new_waypoints, new_times, self.wpidx, orders_list, self.city)
            if feasible == False:
                return 0x3f3f3f3f, 0x3f3f3f3f, 0x3f3f3f3f
            else:
                new_value = val_func_(new_waypoints, new_times, self.wpidx, orders_list, order.id)
                delta = new_value - old_value
                if delta < min_delta:
                    min_delta = delta
                    oidx = 0
                    didx = 0
                return min_delta, oidx, didx 
        else:
            for i in range(self.wpidx, n//2+1):  
                for j in range(n//2, n):
                    new_waypoints = deepcopy(self.waypoints)
                    new_times = deepcopy(self.times)
                    new_waypoints.insert(j+1, -order.id) # type: ignore
                    new_waypoints.insert(i+1,  order.id) # type: ignore
                    feasible, new_times = sync_times_and_waypoints(new_waypoints, new_times, self.wpidx, orders_list, self.city)
                    if feasible == False:
                        continue
                    else:
                        new_value = val_func_(new_waypoints, new_times, self.wpidx, orders_list, order.id)
                        delta = new_value - old_value
                        if delta < min_delta:
                            min_delta = delta
                            oidx = i
                            didx = j
            return min_delta, oidx, didx    

    def get_orders_number_in_car(self):
        return len(self.serving_list)

    def is_idle(self):
        if self.get_orders_number_in_car() == 0:
            return True
        else:
            return False

    def get_current_coord(self, orders_list):
        if self.wpidx == 0:
            return self.waypoints[0]
        else:
            return self.get_wp(self.waypoints[self.wpidx], orders_list)

    def empty_serve(self, order: Order, cur_time, orders_list):
        self.serve_order(order, 0, 0, cur_time, orders_list)
        
    def get_orders_idx_list_in_car(self):
        orders_idx_list_in_car = deepcopy(self.serving_list)
        return orders_idx_list_in_car

    def remove_based_on_orders_idx(self, need_to_remove_, orders_list):
        if len(need_to_remove_) == 0:
            return
        remove_idx = []
        for order_idx in need_to_remove_:
            if order_idx not in self.waypoints:
                continue
            remove_idx.append(self.waypoints.index(order_idx))
            remove_idx.append(self.waypoints.index(-order_idx))
            orders_list[order_idx].st = 0       
            self.serving_list.remove(order_idx) 
        remove_idx.sort(reverse=True)
        for idx in remove_idx:
            del self.waypoints[idx]
            del self.times[idx]
        """ update """
        feasible, self.times = sync_times_and_waypoints(self.waypoints, self.times, self.wpidx, orders_list, self.city)
        if self.is_idle() == True:
            self.wpidx = 0




def generate_cars(id_from: int, car_numbers: int, car_city: int, cur_time:int, car_coord: tuple[float,float]) -> list[Car]:
    """ 
    Input: quantity, city, coordinates. 
    At the specified coordinates in the given city, generate the specified number of vehicles, with vehicle IDs starting from id_from. 
    """
    cars_list = []
    for i in range(car_numbers):
        cars_list.append(Car(id=id_from+i, city=car_city, 
                             waypoints=[car_coord], 
                             times=[cur_time], 
                             serving_list=[]))
    return cars_list





def refresh_car(time_, cars_list_, orders_list):
    """ update car info by time """
    car:Car
    for car in cars_list_:
        car.refresh(time_, orders_list)

def print_no_mttq_cnt():
    global no_mttq_cnt
    print(f" >>> no_mttq_cnt {no_mttq_cnt} ")
    
def print_tot_drivetime():
    global tot_drivetime
    return tot_drivetime
    
    
def print_tot_trip_cnt():
    global tot_trip_cnt
    return tot_trip_cnt


""" Unit Test """


