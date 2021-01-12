#-*-coding:utf-8-*-
import random
from lib.client_lib import judge_two
import time
from lib.client_lib import id2color
from lib.client_lib import id2num

def id2str(cards):
    color = ["S", "H", "D", "C"]
    nums = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
    ans = []
    for card in cards:
        ans.append(color[id2color(card)] + nums[id2num(card)])
    return ans


# 范围类
class PowerRange():
    # 翻牌前 范围是一个定值， 以一个list表示
    def __init__(self, r, num):
        self.range = r
        self.simu_time = num  # 对每个pair模拟

    # 根据公共牌更新range
    def update(self, hole_card, community_card):
        hole_card.sort()
        cnt = 0
        t_start = time.time()
        range_item = {}
        for i in range(len(self.range)):
            key = str(self.range[i][0][0]) + '#' + str(self.range[i][0][1])
            range_item[key] = i
        for item in self.range:
            item[1] = 0  # 重新计数
        cards = [card for card in range(52) if card not in hole_card and card not in community_card]
        n_need_community = 5 - len(community_card)
        for i in range(52):
            if i in hole_card or i in community_card:
                continue
            for j in range(i + 1, 52):
                if j in hole_card or j in community_card:
                    continue
                cnt += 1
                opponent_card = [i, j]
                now_cards = [card for card in cards if card not in opponent_card]
                for x in range(self.simu_time):
                    now_community_card = community_card + random.sample(now_cards, n_need_community)
                    cmp = judge_two(hole_card + now_community_card, opponent_card + now_community_card)
                    # 对手赢
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
        '''     
        for i in range(self.simu_time):
            now_cards = cards.copy()
            now_community_card = community_card.copy()

            # 对手牌
            opponent_card = random.sample(now_cards, 2)
            now_cards = [card for card in now_cards if card not in opponent_card]
            # 公共牌
            n_need_community = 5 - len(now_community_card)
            now_community_card += random.sample(now_cards, n_need_community)

            cmp = judge_two(hole_card + now_community_card, opponent_card + now_community_card)

            # 对手赢
            if cmp != -1 and (str(opponent_card[0]) + '#' + str(opponent_card[1])) in range_item.keys():
                key = str(opponent_card[0]) + '#' + str(opponent_card[1])
                self.range[range_item[key]][1] += 1
                key = str(opponent_card[1]) + '#' + str(opponent_card[0])
                self.range[range_item[key]][1] += 1
            
            # 我赢
            if cmp != 1:
                key = str(hole_card[0]) + '#' + str(hole_card[1])
                self.range[range_item[key]][1] += 1
                key = str(hole_card[1]) + '#' + str(hole_card[0])
                self.range[range_item[key]][1] += 1
        '''
        for item in self.range:
            if item[0] != hole_card:
                item[1] = 1.0 * item[1] / self.simu_time # 得到概率
            else:
                item[1] = 1.0 * item[1] / (self.simu_time * cnt)

        self.range.sort(key=lambda x: x[1], reverse=True)
        print(self.range)
        t_end = time.time()
        print("simulate time = ", self.simu_time, " total time = ", t_end - t_start)


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


if __name__ == '__main__':
    my_hold = [18, 38]
    community_card = [17, 39, 31]
    r = []
    r.append([my_hold, 0.5])
    r.append([[my_hold[1], my_hold[0]], 0.5])
    for i in range(52):
        for j in range(i, 52):
            if i != j and i not in my_hold and j not in my_hold and i not in community_card and j not in community_card:
                t = random.random()
                r.append([[i, j], t])

    commuity_range = PowerRange(r, 15)
    commuity_range.update(my_hold, community_card)