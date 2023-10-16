import numpy as np
import time
from misc import*

def log_time(func):
    start_time = time.time()
    func()
    end_time = time.time()
    print("Time to execute {} was {}".format(func.__name__, end_time-start_time))

def np_multi():
    a = np.arange(0, 10000)
    b = np.arange(0, 10000)
    print(np.dot(a, b))

def reg_multi():
    a = np.arange(0, 10000)
    b = np.arange(0, 10000)
    
    total = 0
    for i in range(len(a)):
        total += a[i] * b[i]

    print(total)

def fail():
    print("run")

if __name__ == '__main__':
    exec_interval(fail, 5)