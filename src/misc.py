import technical_indicators as ti
import time

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

class ProcessingQueue(Queue):
    def __init__(self, size, initial = None):
        super().__init__(size, initial)

    def get_sma(self, length = None):
        if length is not None:
            return ti.sma(self.queue[0:length])
        return ti.sma(self.queue)
    
    def get_wma(self, data, length = None):
        if length is not None:
            return ti.wma(self.queue[0:length])
        return ti.wma(self.queue)
    
    def get_hma(self, sp):
        return ti.hma(self.queue, sp)
    
def exec(func, timeout = 1):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            return func()
        except:
            continue
        break
    raise TimeoutError("{} took too long to run".format(func.__name__))

def exec_interval(func, interval):
    start_time = time.time()
    exec(func)
    time_elapsed = time.time() - start_time
    time.sleep(interval-(time_elapsed))
    exec_interval(func, interval)

    