# -*- coding: UTF-8 -*-
from rabboni import *
import time
import os

def get_available_filename(base_name):
    counter = 1
    filename = f"./{base_name}_{counter}"
    while os.path.exists(filename + ".csv"):
        counter += 1
        filename = f"{base_name}_{counter}"
    return filename

rabo = Rabboni(mode = "USB")


rabo.connect()

rabo.rst_count()
rabo.set_sensor_config(acc_scale = 16, gyr_scale = 2000, rate=100, threshold = 100)
rabo.read_data()

try:
    print("start!")
    t = time.time()
    while time.time() - t < 1:
        pass
    print("1 sec passed")
    while time.time() - t < 2:
        pass
    print("1 sec passed")
    while time.time() - t < 3:
        pass
    print("1 sec passed")
    rabo.stop()
    print("write file in ", get_available_filename("AccX"))
    rabo.write_csv(data = rabo.Accx_list,file_name =get_available_filename("AccX"))
    
    

except KeyboardInterrupt:
    print('Shut done!')

    rabo.stop()
    rabo.write_csv(data = rabo.Accx_list,file_name ="AccX_1")
