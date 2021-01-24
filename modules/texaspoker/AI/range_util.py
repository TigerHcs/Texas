import os
import pickle
import random
import numpy as np
import time

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

class RangeUtil():
    def __init__(self, path):
        self.origin_range_filename = os.path.join(path, "data/origin_range")
        self.flop_range_filename = os.path.join(path, "data/flop_range")
        # self.dat = list(np.fromfile(os.path.join(path, "data/HandRanks.dat"), int))
        with open(self.flop_range_filename, 'rb') as f:
            self.flop_range = pickle.load(f)
        with open(self.origin_range_filename, 'rb') as f:
            self.origin_range = pickle.load(f)
            self.origin_range = self.origin_range[0]
    '''
    def find_dat(self, cards):
        ret = self.dat[53+cards[0]]
        for i in cards[1:]:
            ret = self.dat[ret+i]
        return ret
        # return ret>>12, ret & 0x00000FFF
    def judge_two(self, cards1,cards2):
        res1 = self.find_dat(cards1)
        res2 = self.find_dat(cards2)
        if res1 > res2:
            return -1
        elif res1 < res2:
            return 1
        else:
            return 0
    '''
    def update_range(self, my_hand, com, cur_range):
        from lib.client_lib import judge_two
        my_hand = sorted(my_hand)
        com = sorted(com)
        if not com: # before flop
            return sorted(cur_range, key = lambda x:-self.origin_range[my_hash(x)])
        elif len(com)==3: #flop
            return sorted(cur_range, key = lambda x:-self.flop_range[my_hash(com)][my_hash(x)])
        elif len(com)==4 or len(com)==5: #turn/river
            total_t = 100000 // len(cur_range)
            dic = {}
            for pair in cur_range:
                now_cards = [_ for _ in range(52) if _ not in (com+my_hand+pair)]
                cnt_win = 0
                need_com = 5 - len(com)
                for _ in range(total_t):
                    cards = random.sample(now_cards,2+need_com)
                    com_ = com[:]
                    if need_com == 1:
                        com_.append(cards[-1])
                    res = judge_two(com_+cards[:2], com_+pair)
                    cnt_win += (res+1)/2.0

                dic[my_hash(pair)] = cnt_win
            return sorted(cur_range, key = lambda x:-dic[my_hash(x)])
        else:
            print("Invalid com cards!!!")
            return cur_range


if __name__ == "__main__":
    range_util = RangeUtil("")
    # lst = []
    # for i in range(52):
    #     for j in range(i+1,52):
    #         lst.append([i,j])
    # lst = range_util.update_range([0,1],[8,9,10,35],lst)
    # print(lst[:100])
    from lib.client_lib import judge_two
    tt = time.time()
    for i in range(100000):
        res = range_util.judge_two([1,2,3,4,5,6,7], [43,42,16,33,25,24,50])
    print(time.time()-tt)
