"""
config file
"""

DATA_NAME = "XA"                 # Name of dataset
EXP_EXECUTE_TIME = 50            # How many times does the experiment need to be repeated ?
CONSIDER_TRAFFIC_CONGESTION = 0  # Consider congestion ?

Q = 6        # Seats number
CARNUM = 25  # taxis number
DET1 = 1200  # wait time
DET2 = 1.2   # detour coefficient

TIME_START = 28800        # Start time, 28800 refer to 8:00 AM
TIME_END = 72000          # End time, 72000 refer to 8:00 PM
TIME_END_SERVING = 80000  # Deley time，greater than end time, make sure all taxis send passenger to their destinaton

OFFSET = 0
R_X = 1
R_Y = 0
R_Z = 1

# taxis start position (taxis no need to back depot after each trip, they need only go depot when they start or end the all day job)
ANXI_DEPOT = (118.1889,25.0672)
XIAMEN_DEPOT = (118.1199,24.4875)
ZHANGZHOU_DEPOT = (117.6984,24.5078)

TIME_STEP = 300  # How many seconds between each optimization execution
REOP = TIME_STEP
ANLS_TIME_POINT = []
for t in range(TIME_START, TIME_END, REOP):
    ANLS_TIME_POINT.append(t+REOP)
