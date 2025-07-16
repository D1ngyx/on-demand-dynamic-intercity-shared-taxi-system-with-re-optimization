import numpy as np


def update_temperature(temperature, alpha=0.5):
    return temperature * alpha

def acceptance_criterion(old_obj, new_obj, temperature):
    delta_e = new_obj - old_obj
    if delta_e > 0:
        return True
    else:
        acceptance_probability = np.exp(delta_e / temperature)
        return np.random.rand() < acceptance_probability
    
    