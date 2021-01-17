import pickle
from collections import defaultdict
import os

origin_range_filename = "origin_range"
flop_range_filename = "flop_range"

def my_hash(cards):
    ret = 0
    for card in cards:
        ret *= 100
        ret += card+1
    return ret
def my_dehash(v):
    ret = []
    while v>0:
        ret.append(v%100-1)
        v = v//100
    ret.reverse()
    return ret

with open(flop_range_filename, 'rb') as f:
    flop_range = pickle.load(f)
with open(origin_range_filename, 'rb') as f:
    origin_range = pickle.load(f)
    origin_range = origin_range[0]

def update_range(my_hand, com, cur_range, ratio):
    my_hand = sorted(my_hand)
    com = sorted(com)
    if not com: # before flop
        return sorted(cur_range, key = lambda x:-origin_range[my_hash(x)])
    elif len(com)==3: #flop
        return sorted(cur_range, key = lambda x:-flop_range[my_hash(com)][my_hash(x)])
    elif len(com)==4: #turn
        return cur_range
    elif len(com)==5: #river
        return cur_range
    else:
        print("Invalid com cards!!!")
        return cur_range

lst = []
for k,v in origin_range.items():
    lst.append([k,v])
lst = sorted(lst, key =lambda x:-x[1])
print([[my_dehash(x[0]), x[1]] for x in lst[:100]])