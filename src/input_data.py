import pandas as pd 
from passenger import Order 
import numpy as np
from vehicle import generate_cars
from para import *

""" read data """

ORDER_DATA_FILE = f"{DATA_NAME}.csv"

orders_df = pd.read_csv(ORDER_DATA_FILE)

orders_df["TIME"] = orders_df["TIME"].astype(int)
orders_df["Oy"] = orders_df["Oy"].astype(float)
orders_df["Ox"] = orders_df["Ox"].astype(float)
orders_df["Dy"] = orders_df["Dy"].astype(float)
orders_df["Dx"] = orders_df["Dx"].astype(float)
orders_df["CITY"] = orders_df["CITY"].astype(int)

""" init orders_df """
orders_list = []
for i in range(orders_df.shape[0]):
    orders_list.append(Order(i, orders_df.at[i, "Oy"], orders_df.at[i, "Ox"],
                 orders_df.at[i, "Dy"], orders_df.at[i, "Dx"],
                 orders_df.at[i, "TIME"],
                 orders_df.at[i, "CITY"]))
orders_list[0].st = 1 # we ues positive and negtive to judge it is startpoint or endpoint, 0 is special, so we cancel this

""" init cars list """
cars_list = []
if DATA_NAME == "XZ":
    cars_list += generate_cars(id_from=0, car_numbers=CARNUM, car_city=1, cur_time=28800, car_coord=ZHANGZHOU_DEPOT)  # Zhangzhou
elif DATA_NAME == "XA":
    cars_list += generate_cars(id_from=0, car_numbers=CARNUM, car_city=1, cur_time=28800, car_coord=ANXI_DEPOT)  # Anxi
else:
    raise Exception("[ERROR]: dataset name error ")
cars_list += generate_cars(id_from=CARNUM, car_numbers=CARNUM, car_city=0, cur_time=28800, car_coord=XIAMEN_DEPOT)  # Xiamen

SG = np.load(f'{DATA_NAME}.npy')

          

