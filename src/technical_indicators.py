import numpy as np

def sma(data):
    return sum(data)/len(data)

def wma(data):
    weights = np.flip(np.arange(1, len(data)+1))
    return np.dot(data, weights)/sum(weights)

def raw_hma(data):
    wma1 = wma(data[int(len(data))/2:])
    wma2 = wma(data)
    return (2*wma1)-wma2

def hma(data, sp):
    raws = []
    length = len(data)-sp+1
    for i in range(sp):
        raw = raw_hma(data[i:length+i])
        raws.append(raw)
    return wma(raws)
