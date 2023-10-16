import technical_indicators as ti
import time
from enum import Enum

class Queue:
    def __init__(self, size, initial = None):
        self.size = size
        self.queue = []
        if initial is not None:
            self.queue = initial

    def add(self, element):
        if len(self.queue) < self.size:
            self.queue.append(element)
        else:
            self.queue.pop(0)
            self.queue.append(element)

    def is_full(self):
        return len(self.queue) == self.size
    
    def last(self):
        return self.queue[-1]

class ProcessingQueue(Queue):
    def __init__(self, size, initial = None):
        super().__init__(size, initial)

    def get_sma(self, length = None):
        if length is not None:
            return ti.sma(self.queue[0:length])
        return ti.sma(self.queue)
    
    def get_wma(self, length = None):
        if length is not None:
            return ti.wma(self.queue[0:length])
        return ti.wma(self.queue)
    
    def get_hma(self, sp, length = None):
        if length is not None:
            return ti.hma(self.queue[0:length], sp)
        return ti.hma(self.queue, sp)
    
class Transactions(Enum):
    BUY = 1
    SELL = 2
    SELL_SHORT = 3
    BUY_TO_COVER = 4

class Trends(Enum):
    BULL = 1
    BEAR = 2
    RALLY = 3
    PULLBACK = 4
    RANGING = 5
    
def exec(func):
    #timeout = 1
    def wrapper(*args, **kwargs):
        #start_time = time.time()
        while 1:#time.time() - start_time < timeout:
            try:
                return func(*args, **kwargs)
            except:
                continue
            break
        raise TimeoutError("{} took too long to run".format(func.__name__))
    time.sleep(0.5)
    return wrapper

def exec_interval(func, interval, condition):
    start_time = time.time()
    func()
    time_elapsed = time.time() - start_time
    if condition:
        time.sleep(interval-(time_elapsed))
        exec_interval(func, interval)
    else:
        print("program aborted")

    