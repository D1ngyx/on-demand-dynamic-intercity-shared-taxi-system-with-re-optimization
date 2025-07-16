def calc_longterm_cost(waypoints_, times_, wpidx_, orders_list_, insert_order_idx):
    idxo = waypoints_.index(insert_order_idx)
    idxd = waypoints_.index(-insert_order_idx)
    return - ( (orders_list_[insert_order_idx].ddlo - times_[idxo]) + (orders_list_[insert_order_idx].ddld - times_[idxd]) )

def calc_extra_cost(waypoints_, times_, wpidx_, orders_list_, insert_order_idx):
    return (times_[-1] - times_[0])

def calc_slack_time(waypoints_, times_, wpidx_, orders_list_, insert_order_idx):
    n = len(waypoints_)
    if n == 1:
        return 0
    slk = 0
    for i in range(1, n // 2):
        id = waypoints_[i]
        if id > 0:
            slk += min(orders_list_[id].ddlo - times_[i], orders_list_[id].ddlo - times_[waypoints_.index(-id)])
    return - slk / (n//2)



