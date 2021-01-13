#-*-coding:utf-8-*-
import random,sys
sys.path.append("..")
from lib.client_lib import judge_two
import time
from lib.client_lib import id2color
from lib.client_lib import id2num
from lib.client_lib import Player


def id2str(cards):
    color = ["S", "H", "D", "C"]
    nums = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
    ans = []
    for card in cards:
        ans.append(color[id2color(card)] + nums[id2num(card)])
    return ans


class MyPlayer(Player):
    pass


# 范围类
class PowerRange():
    # 翻牌前 范围是一个定值， 以一个list表示
    def __init__(self, r, num):
        self.range = r
        self.simu_time = num  # 对每个pair模拟

    # 根据公共牌更新range
    def update(self, hole_card, community_card):
        hole_card.sort()
        t_start = time.time()
        range_item = {}
        for i in range(len(self.range)):
            key = str(self.range[i][0][0]) + '#' + str(self.range[i][0][1])
            range_item[key] = i
        for item in self.range:
            item[1] = 0  # 重新计数

        # 当前牌库
        cards = [card for card in range(52) if card not in hole_card and card not in community_card]
        n_need_community = 5 - len(community_card)

        # 所有对手可能手牌组合
        possible_opponent_cards = [x[0] for x in self.range if x[0][0] not in hole_card + community_card and x[0][1] not
                                   in hole_card + community_card]

        # 对每种组合进行模拟
        for opponent_card in possible_opponent_cards:
            now_cards = [card for card in cards if card not in opponent_card]
            for x in range(self.simu_time):
                now_community_card = community_card + random.sample(now_cards, n_need_community)
                cmp = judge_two(hole_card + now_community_card, opponent_card + now_community_card)

                if (str(opponent_card[0]) + '#' + str(opponent_card[1])) in range_item.keys():
                    if cmp == 1:
                        key = str(opponent_card[0]) + '#' + str(opponent_card[1])
                        self.range[range_item[key]][1] += 1

                    elif cmp == 0:
                        key = str(opponent_card[0]) + '#' + str(opponent_card[1])
                        self.range[range_item[key]][1] += 0.5

                    if cmp == -1:
                        key = str(hole_card[0]) + '#' + str(hole_card[1])
                        self.range[range_item[key]][1] += 1

        for item in self.range:
            if item[0] != hole_card:
                item[1] = 1.0 * item[1] / self.simu_time # 得到概率
            else:
                item[1] = 1.0 * item[1] / (self.simu_time * len(possible_opponent_cards))

        self.range.sort(key=lambda x: x[1], reverse=True)
        print(self.range)
        t_end = time.time()
        print("simulate time = ", self.simu_time, " total time = ", t_end - t_start)

        for i in range(len(self.range)):
            if hole_card[0] == self.range[i][0][0]:
                print("My card power is top", (i + 1.0) / len(self.range) * 100, "%")
                break


# 假定对手均匀分布，计算胜率
def get_win_rate(total_times, num_player, hole_card, community_card):
    win_times = 0
    cards = [card for card in range(52) if card not in hole_card and card not in community_card]
    for i in range(total_times):
        now_cards = cards.copy()
        now_community_card = community_card.copy()
        '''
        # 给对手发牌
        for j in range(num_player - 1):
            t = random.sample(now_cards, 2)
            opponents_cards.append(t)
            now_cards = [card for card in now_cards if card not in t]
        # 发公共牌
        n_need_community = 5 - len(now_community_card)
        now_community_card += random.sample(now_cards, n_need_community)
        '''
        # 发公共牌
        n_need_community = 5 - len(now_community_card)
        now_community_card += random.sample(now_cards, n_need_community)
        now_cards = [card for card in now_cards if card not in now_community_card]
        # 发对手牌
        t = random.sample(now_cards, (num_player - 1) * 2)
        opponents_cards = [t[2*i:2*i+2] for i in range(num_player - 1)]
        # 计算胜者
        for j in range(num_player - 1):
            # cmp == 1 说明比某人小
            cmp = judge_two(hole_card + now_community_card, opponents_cards[j] + now_community_card)
            if cmp == 1:
                break
        if cmp != 1:
            win_times += 1

    return 1.0 * win_times / total_times

def my_hash(cards):
    ret = 0.0
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

if __name__ == '__main__':
    flop_list = []
    for i in range(52):
        for j in range(i + 1, 52):
            for k in range(j + 1, 52):
                flop_list.append([i, j, k])
    from tqdm import tqdm
    from collections import defaultdict
    import pickle
    import itertools
    flop_range={}
    n = 2
    for idx in tqdm(range(len(flop_list))):
        flop = flop_list[idx]
        cards = [card for card in range(52) if card not in flop]
        cnt_win = defaultdict(int)
        cnt_in  = defaultdict(int)
        for C in itertools.combinations(cards, 2+2*n):
            c = list(C)
            com = flop + c[:2]
            n_pairs = []
            for i in range(n):
                n_pairs.append(c[2*i+2:2*i+4])
            for pair in n_pairs:
                cnt_in[my_hash(pair)] += 1
            cur = 0
            for i in range(1,n):
                cmp = judge_two(n_pairs[cur]+com, n_pairs[i]+com)
                if cmp >= 0:
                    cur = i
            cnt_win[my_hash(n_pairs[cur])] += 1
        for key in cnt_win.keys():
            cnt_win[key] = cnt_win[key] / cnt_in[key]
        flop_range[my_hash(flop)] = cnt_win
        with open('flop_range','wb') as f:
            pickle.dump(flop_range,f)
        break