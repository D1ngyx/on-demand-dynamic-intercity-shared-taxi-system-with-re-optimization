from para import Q
from passenger import Order
from vehicle import Car
from router import euc
from input_data import orders_list, SG
from value_func import calc_extra_cost

def is_time_in_range(order_time_: int, time_l_: int, time_r_: int):
    if time_l_ <= order_time_ < time_r_:
        return True
    else:
        return False

def calc_sg_degree(order_idx_: int, orders_idx_list_: list):
    """ calculate SG value about order_idx_ and cur_orders_idx_list_ """
    dg = 0
    for idx in orders_idx_list_:
        if order_idx_ == idx:
            continue
        dg += SG[order_idx_, idx] + SG[idx, order_idx_]
    return dg

""" --------------------------------------------------------------------------------------------------------------------------------------------------- """

def assign_to_idle_car(cur_time_, order_: Order, cars_list_):
    """ search idle car for order """ 
    cur_car_list_pr = []
    for car in cars_list_:
        if car.city != order_.city or car.is_idle() == False:
            continue
        cur_car_list_pr.append((car, euc([car.get_current_coord(orders_list) , order_.orig])))
    if len(cur_car_list_pr) == 0:
        return
    sorted_cur_car_list_pr = sorted(cur_car_list_pr, key=lambda pr: pr[1])
    car = sorted_cur_car_list_pr[0][0]
    insert_cost, insert_orig_idx, insert_dest_idx = car.insert_to_car_based_value_function(order_, orders_list, calc_extra_cost)
    if insert_cost == 0x3f3f3f3f:
        return
    car.serve_order(order_, insert_orig_idx, insert_dest_idx, cur_time_, orders_list)

def search_car_by_cloest_car(order_: Order, cars_list_, value_function_, no_use_idle_car_):
    """ search busy car for order """
    car: Car
    is_find = False
    best_insert_cost = best_car_id = best_insert_orig_idx = best_insert_dest_idx = 0x3f3f3f3f
    # sort by cloest car
    cur_car_list_pr = []
    for car in cars_list_:
        if car.city != order_.city or car.over_highway() == True or car.get_orders_number_in_car() >= Q:
            continue
        if car.is_idle() == True and no_use_idle_car_ == True:
            continue
        cur_car_list_pr.append((car, euc([car.get_current_coord(orders_list) , order_.orig])))
    sorted_cur_car_list_pr = sorted(cur_car_list_pr, key=lambda pr: pr[1])
    sorted_cur_car_list = [pr[0] for pr in sorted_cur_car_list_pr]
    # search from cloest car
    for car in sorted_cur_car_list:
        insert_cost, insert_orig_idx, insert_dest_idx = car.insert_to_car_based_value_function(order_, orders_list, value_function_)
        if insert_cost == 0x3f3f3f3f or insert_cost >= best_insert_cost:
            continue
        is_find = True
        best_insert_cost = insert_cost
        best_car_id = car.id
        best_insert_orig_idx = insert_orig_idx
        best_insert_dest_idx = insert_dest_idx
        break
    return is_find, best_car_id, best_insert_orig_idx, best_insert_dest_idx, best_insert_cost

def search_car_by_sg_degree(order_: Order, cars_list_: list, value_function_, no_use_idle_car_):
    """ search busy car for order """
    car: Car
    is_find = False
    best_insert_cost = best_car_id = best_insert_orig_idx = best_insert_dest_idx = 0x3f3f3f3f
    # sort by sg degree
    cur_car_list_pr = []
    for car in cars_list_:
        if car.city != order_.city or car.over_highway() == True or car.get_orders_number_in_car() >= Q:
            continue
        if car.is_idle() == True and no_use_idle_car_ == True:
            continue
        cur_car_list_pr.append((car, calc_sg_degree(order_.id, car.get_orders_idx_list_in_car())))
    sorted_cur_car_list_pr = sorted(cur_car_list_pr, key=lambda pr: pr[1], reverse=True)
    sorted_cur_car_list = [pr[0] for pr in sorted_cur_car_list_pr]
    # search
    for car in sorted_cur_car_list:
        insert_cost, insert_orig_idx, insert_dest_idx = car.insert_to_car_based_value_function(order_, orders_list, value_function_)
        if insert_cost == 0x3f3f3f3f or insert_cost >= best_insert_cost:
            continue
        is_find = True
        best_insert_cost = insert_cost
        best_car_id = car.id
        best_insert_orig_idx = insert_orig_idx
        best_insert_dest_idx = insert_dest_idx
        break
    return is_find, best_car_id, best_insert_orig_idx, best_insert_dest_idx, best_insert_cost

def search_car_by_best_value(order_: Order, cars_list: list, value_function_, no_use_idle_car_):
    is_find = False
    best_insert_cost = best_car_id = best_insert_orig_idx = best_insert_dest_idx = 0x3f3f3f3f
    car: Car
    for car in cars_list:
        if car.city != order_.city or car.over_highway() == True or car.get_orders_number_in_car() >= Q:
            continue
        if car.is_idle() == True and no_use_idle_car_ == True:
            continue
        insert_cost, insert_o, insert_d = car.insert_to_car_based_value_function(order_, orders_list, value_function_)
        if insert_cost < best_insert_cost:
            is_find = True
            best_insert_cost = insert_cost
            best_car_id = car.id
            best_insert_orig_idx = insert_o
            best_insert_dest_idx = insert_d
    return is_find, best_car_id, best_insert_orig_idx, best_insert_dest_idx, best_insert_cost

""" --------------------------------------------------------------------------------------------------------------------------------------------------- """

def assign_to_cloest_car(cur_time_, order_, cars_list_, value_function_, no_use_idle_car=False):
    is_find, best_car_id, best_insert_orig_idx, best_insert_dest_idx, best_insert_cost = \
        search_car_by_cloest_car(order_, cars_list_, value_function_, no_use_idle_car)
    if is_find == True:
        car: Car = cars_list_[best_car_id]
        car.serve_order(order_, best_insert_orig_idx, best_insert_dest_idx, cur_time_, orders_list)
    return

def assign_to_sg_degree(cur_time_, order_, cars_list_, value_function_, no_use_idle_car=False):
    is_find, best_car_id, best_insert_orig_idx, best_insert_dest_idx, best_insert_cost = \
        search_car_by_sg_degree(order_, cars_list_, value_function_, no_use_idle_car)
    if is_find == True:
        car: Car = cars_list_[best_car_id]
        car.serve_order(order_, best_insert_orig_idx, best_insert_dest_idx, cur_time_, orders_list)
    return

def assign_to_best_value_car(cur_time_, order_, cars_list_, value_function_, no_use_idle_car=False):
    is_find, best_car_id, best_insert_orig_idx, best_insert_dest_idx, best_insert_cost = \
        search_car_by_best_value(order_, cars_list_, value_function_, no_use_idle_car)
    if is_find == True:
        car: Car = cars_list_[best_car_id]
        car.serve_order(order_, best_insert_orig_idx, best_insert_dest_idx, cur_time_, orders_list)
    return
