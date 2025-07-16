# on-demand-dynamic-intercity-shared-taxi-system-with-re-optimization



## 1. Datasets

Our datasets is located within the `datasets` directory. 



## 2. How to config

- Check `para.py` for common config parameter. 

- Check `passenger.py` for stochastic demand config.

- Check `RALNS.py` for operator weight (around line 61). 

- Check `router.py` for congested coefficient.

- ! Chcek `run_a_batch.py` for python command.



## 3. How to run

```
python run_a_batch.py
```



## *4. ! ! ! NOTE ! ! !

  Here is a **slightly simplified** version, as the **engineering implementation** of this algorithm is protected by copyright and cannot be disclosed. However, we have conducted experiments with simulated parameters to the greatest extent possible. We have streamlined some critical engineering details, and the results show that the simplified version still allows the experimental outcomes to largely **fall within our confidence interval**. Specifically, in this implementation, we simplified the following two details:

- In `main.py` , ALNS algorithm is iterated by count (e.x: run 30 times). But in our experiment, it is iterated by  timimg (e.x: run 30 seconds). If you wanna implement this, you need to create a new thread for timing purposes, is a common practice in programming.

- In `router.py`, driving time is calculated by euclidean distance. But in our experiment, it is calculated by BaiduMap and [OSRM](https://github.com/Project-OSRM/osrm-backend) with caching strategy. We applied linear weighting to the euclidean distance to make its results better align with those calculated by the map API. However, BaiduMap is industrial-grade paid API, but OSRM is free. If you want to use more realistic distance or duration infomation, deploy OSRM as backend (the interfaces are already implemented in `router.py`), or buy a map service (crazy expensive). We recommend to use Fujian Province tile data for OSRM, not China tile data (too big and slow).

You'll notice that these details are not directly related to the algorithm itself but rather to engineering considerations. 
