#-*-coding:utf-8-*-
import random
from lib.client_lib import judge_two
import time
from lib.client_lib import id2color
from lib.client_lib import id2num
from lib.client_lib import Player
from lib.client_lib import Decision


def id2str(cards):
    color = ["S", "H", "D", "C"]
    nums = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
    ans = []
    for card in cards:
        ans.append(color[id2color(card)] + nums[id2num(card)])
    return ans


def card2str(cards):
    return str(cards[0]) + "#" + str(cards[1])


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


# 胜率
def get_win_rate():
    return 1


# 赔率
def get_odds(id, state):
    need_bet = state.minbet - state.player[id].totalbet   # 不太确定是bet还是totalbet
    return need_bet / (need_bet + state.moneypot)


def my_ai(id, state):
    win_odd_factor = 0.1
    check_raise = 0.4
    cards = state.sharedcards + state.player[id].cards
    win_rate = get_win_rate()
    odds = get_odds(id, state)

    decision = Decision()
    delta = state.minbet - state.player[id].totalbet  # 不太确定是bet还是totalbet

    if id >= state.playernum - 2:  # 后置位
        if win_rate > odds + win_odd_factor:  # 胜率大幅高于赔率
            t = random.random()
            if t < check_raise:
                pass
            else:
                decision.check = 1

        elif odds + win_odd_factor >= win_rate >= odds - win_odd_factor:   # 胜率约等于赔率
            pass

        else:  # 胜率大幅低于赔率
            decision.giveup = 1

    else:  # 前置位
        pass


if __name__ == '__main__':
    player = Player(1000, 1)
    player.add_action(0, "check")
    player.add_action(1, "give up")
    player.add_action(2, "raise#100#50#2000")
    player.add_action(3, "call bet#100#200#2000")