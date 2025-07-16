""" SG based algorithm. For initial greedy assign. """

from vehicle import Car, print_tot_drivetime, print_tot_trip_cnt, refresh_car
import tqdm
import random
import time
from copy import deepcopy

print(" >>> import data... ") 
time_begin_record = time.time() 
from input_data import orders_list, cars_list
from para import *
from initial_assign import assign_to_best_value_car, is_time_in_range
from value_func import calc_extra_cost

print(f" > ---------------------------------------------------------------- < ")
print(f" > Method: SG-RALNS")
print(f" > Time start: {TIME_START}")
print(f" > Time end: {TIME_END}")
print(f" > Time step: {TIME_STEP}")
print(f" > Reoptimize iterval: {REOP}")
print(f" > Total taxi numbers: {CARNUM*2}")
print(f" > Max waiting time: {DET1}")
print(f" > Max detoure coff: {DET2}")
print(" >>> Done, Good Luck! ")
print(f" > ---------------------------------------------------------------- < ")

# CITYCODE: 0=Xiamen; 1=Anxi/Zhangzhou 

from RALNS import RALNS
import SA
from reoptimize import remove_orders_from_cars_list, INSERT

tiem_alns = []

it_I = [[],[],[],[]]
it_R = [[],[],[],[]]
freq_I = [0,0,0,0]
freq_R = [0,0,0,0]


INSERT_OP_NUM = 4
REMOVE_OP_NUM = 4
alns = RALNS(INSERT_OP_NUM,REMOVE_OP_NUM,R_X,R_Y,R_Z,0.9975)
change_num = 0
CNT = []
""" ----------------------- main code ----------------------- """
time_spend = []
for t in tqdm.trange(TIME_START, TIME_END_SERVING, TIME_STEP):
    cur_time = t + TIME_STEP
    record_time = time.time()  
    refresh_car(cur_time, cars_list, orders_list)
    car: Car
    if cur_time > TIME_END:
        continue
    begin_time = time.time()
    """ generate initial solution """
    cur_orders_idx_list = []
    for order in orders_list:
        if order.id == 0:
            continue
        if is_time_in_range(order.order_time, t, cur_time):
            cur_orders_idx_list.append(order.id)
    for order_idx in cur_orders_idx_list:
        order = orders_list[order_idx]
        assign_to_best_value_car(cur_time, order, cars_list, calc_extra_cost)

    IK = random.randint(16,32) 

    PROB = 0.01
    """ ALNS loop count """
    TEMP = random.randint(25,50)
    
    original_cars_list = deepcopy(cars_list)

    for ik in range(IK):
        """ record old object value """
        old_order_cnt, old_obj = alns.calc_obj_value(cars_list)
        new_cars_list = deepcopy(cars_list)
        removable_orders_idx = alns.get_removable_orders_idx(new_cars_list)
        if len(removable_orders_idx) < 1:
            break
        """ choose remove operator """
        remove_operator_id_1 = alns.choose_remove_operator()
        """ get removable order index in the list """
        if remove_operator_id_1 == 0:
            removed_orders_idx_1 = alns.R_0(removable_orders_idx)
        elif remove_operator_id_1 == 1:
            removed_orders_idx_1 = alns.R_1(removable_orders_idx)
        elif remove_operator_id_1 == 2:
            removed_orders_idx_1 = alns.R_2(removable_orders_idx, new_cars_list)
        elif remove_operator_id_1 == 3:
            removed_orders_idx_1 = alns.R_3(removable_orders_idx, new_cars_list)        
        """ imp remove """
        remove_orders_from_cars_list(removed_orders_idx_1, new_cars_list)

        """ remove one more time, check ALNS original paper(Ropke 2006), this logic is SUPER IMPORTANT """
        remove_operator_id_2= alns.choose_remove_operator()
        removable_orders_idx = [it for it in removable_orders_idx if it not in removed_orders_idx_1]
        """ below, same with first remove """
        if len(removable_orders_idx) == 0:
            removed_orders_idx_2 = []
        else:
            if remove_operator_id_2 == 0:
                removed_orders_idx_2 = alns.R_0(removable_orders_idx)
            elif remove_operator_id_2 == 1:
                removed_orders_idx_2 = alns.R_1(removable_orders_idx)
            elif remove_operator_id_2 == 2:
                removed_orders_idx_2 = alns.R_2(removable_orders_idx, new_cars_list)
            elif remove_operator_id_2 == 3:
                removed_orders_idx_2 = alns.R_3(removable_orders_idx, new_cars_list)   
            remove_orders_from_cars_list(removed_orders_idx_2, new_cars_list)
        removed_orders_idx = list(set(removed_orders_idx_1) | set(removed_orders_idx_2))

        """ impl insert """
        new_cars_list, insert_operator_id = INSERT(cur_time, removed_orders_idx, alns, new_cars_list)
        
        """ record new object value """
        new_order_cnt, new_obj = alns.calc_obj_value(new_cars_list)
        
        """ determine whether to accept a new solution """    
        if SA.acceptance_criterion(old_obj, new_obj, TEMP):
            cars_list = deepcopy(new_cars_list)
            TEMP = SA.update_temperature(TEMP)
            alns.update_prob(old_obj, new_obj, remove_operator_id_1, remove_operator_id_2, insert_operator_id) 
        else:
            for car in cars_list:
                for order_idx in car.serving_list:
                    orders_list[order_idx].st = 1
        
        """ [OPT]: record frequence of operator """
        freq_R[remove_operator_id_1] += 1 # type: ignore
        freq_R[remove_operator_id_2] += 1 # type: ignore
        freq_I[insert_operator_id] += 1 # type: ignore
        for j in range(INSERT_OP_NUM):
            it_I[j].append(alns.insert_op_weight[j])
        for j in range(REMOVE_OP_NUM):
            it_R[j].append(alns.remove_op_weight[j])
               
    """ [OPT]: record exec time """
    end_time = time.time()
    alns_runtime = end_time - begin_time
    time_spend.append(time.time()-record_time)
""" ----------------------- main code ----------------------- """



serving_num = 0
for order in orders_list:
    if order.pick_time != -1:
        serving_num += 1
tot_detour_coef = 0
tot_wait_time = 0
for order in orders_list:
    if order.pick_time != -1:
        tot_detour_coef += (order.arrive_time - order.pick_time) - order.o2d
        tot_wait_time += order.pick_time - order.order_time

tot_trip_cnt = print_tot_trip_cnt()
tot_drive_time = print_tot_drivetime()

res_profit = serving_num * 50 - tot_trip_cnt * 80 - (tot_drive_time/3600) * 30
res_ave_wait_time = tot_wait_time / serving_num
res_ave_detour_time = tot_detour_coef / serving_num
res_profit = f"{res_profit:.2f}"
res_ave_wait_time = f"{res_ave_wait_time:.2f}"
res_ave_detour_time = f"{res_ave_detour_time:.2f}"

from save_res import save_experiment_data
save_experiment_data(
    f"result/SGALNS-{DATA_NAME}-{'Jam' if CONSIDER_TRAFFIC_CONGESTION==1 else 'noJam'}-{CARNUM*2}-{DET1}-{DET2}-{Q}.xlsx", 
    [res_profit, res_ave_wait_time, res_ave_detour_time])



