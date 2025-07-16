from copy import deepcopy
from initial_assign import assign_to_best_value_car, assign_to_cloest_car, assign_to_sg_degree, is_time_in_range, assign_to_idle_car
from value_func import calc_extra_cost, calc_slack_time, calc_longterm_cost
from vehicle import Car
from input_data import orders_list
from para import ANLS_TIME_POINT
from RALNS import RALNS


def perception_alsn(cur_time_):
    return cur_time_ in ANLS_TIME_POINT


def remove_orders_from_cars_list(removed_orders_idx_, cars_list_):
    """ remove order from cars """
    car: Car
    for car in cars_list_:
        set_removed_orders_idx_ = set(removed_orders_idx_)
        set_car_serving = set(car.get_orders_idx_list_in_car())
        need_to_remove = list(set_removed_orders_idx_ & set_car_serving)
        """ Record the indices of order_idx in car.waypoints and car.times, sort these indices in reverse order (to prevent position changes during deletion), then delete them sequentially from car.waypoints, car.times, and car.serving_list """
        car.remove_based_on_orders_idx(need_to_remove, orders_list)

def INSERT(cur_time_, removed_orders_idx_, alns_: RALNS, cars_list_):
        others_orders_list = []
        others_orders_list += deepcopy(removed_orders_idx_)
        for car in cars_list_:
            others_orders_list += deepcopy(car.get_orders_idx_list_in_car())
        others_orders_list = list(set(others_orders_list))  # others_orders_list refer to orders in **taxis** 
        for order in orders_list:
            if order.order_time < cur_time_ < order.ddlo and order.st != 1:
                removed_orders_idx_.append(order.id)
        removed_orders_idx_ = list(set(removed_orders_idx_))
        """ choose insert operator """
        insert_operator_id = alns_.choose_insert_operator() 
        if insert_operator_id == 0:
            insert_orders_idx = alns_.I_0(removed_orders_idx_, others_orders_list)
            insert_orders_to_cars_list(cur_time_, insert_orders_idx, cars_list_)
        if insert_operator_id == 1:
            insert_orders_idx = alns_.I_1(removed_orders_idx_, others_orders_list)
            insert_orders_to_cars_list(cur_time_, insert_orders_idx, cars_list_)
        if insert_operator_id == 2:
            while len(removed_orders_idx_) > 0:
                insert_orders_idx = alns_.I_2(removed_orders_idx_, cars_list_)
                insert_order_idx = insert_orders_idx[0]
                assign_to_best_value_car(cur_time_, orders_list[insert_order_idx], cars_list_, calc_extra_cost, no_use_idle_car=True)
                if orders_list[insert_order_idx].st != 1:
                    assign_to_idle_car(cur_time_, orders_list[insert_order_idx], cars_list_)
                removed_orders_idx_.remove(insert_order_idx)
        if insert_operator_id == 3:
            while len(removed_orders_idx_) > 0:
                insert_orders_idx = alns_.I_3(removed_orders_idx_, cars_list_)
                insert_order_idx = insert_orders_idx[0]
                assign_to_best_value_car(cur_time_, orders_list[insert_order_idx], cars_list_, calc_extra_cost, no_use_idle_car=True)
                if orders_list[insert_order_idx].st != 1:
                    assign_to_idle_car(cur_time_, orders_list[insert_order_idx], cars_list_)
                removed_orders_idx_.remove(insert_order_idx)

        return cars_list_, insert_operator_id

def insert_orders_to_cars_list(cur_time_, insert_orders_idx_, cars_list_):
    """ The logic for inserting orders into the vehicle's route is the same as before, except that insert_orders_idx_ is pre-sorted. """
    for order_idx in insert_orders_idx_:
        assign_to_best_value_car(cur_time_, orders_list[order_idx], cars_list_, calc_extra_cost)




