from router import Router,tt 
from para import DET1, DET2
import numpy as np

STO_ORDERTIME_L = -3600
STO_ORDERTIME_R =  3600
STO_CANCEL      =  0.05

class Order:
    def __init__(self, id:int, Oy:float, Ox:float, Dy:float, Dx:float, order_time:int, from_city:int) -> None:
        #router = Router([(Oy,Ox), (Dy,Dx)])
        self.id:int = id
        # self.orig:tuple = router.fix_incorrect_coords(0)
        # self.dest:tuple = router.fix_incorrect_coords(1)
        self.orig:tuple = (Oy,Ox)
        self.dest:tuple = (Dy,Dx)
        self.order_time:int = order_time
        # sto
        self.order_time += np.random.randint(STO_ORDERTIME_L, STO_ORDERTIME_R)
        self.o2d: int = tt([self.orig, self.dest])
        self.ddlo:int = self.order_time + DET1
        self.ddld:int = self.ddlo + int(self.o2d*DET2)
        self.city:int = from_city
        self.pick_time:int = -1
        self.arrive_time:int = -1
        self.st = 0
        # sto
        if np.random.rand() <= STO_CANCEL:
            self.st = 1

""" Unit Test """
# olist = []
# o = Order(118.113277, 24.497131, 118.098473, 24.573, 10, 1)
# print(o)
# olist.append(o)
# print(olist[0])
# del(o)
# print(olist[0])
# print(o.orig, o.dest, o.order_time, o.city, o.pick_time, o.arrive_time)
# print(type(o.orig), type(o.dest), type(o.order_time), type(o.city), type(o.pick_time), type(o.arrive_time))
