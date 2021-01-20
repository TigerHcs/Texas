# -*-coding:utf-8-*-
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


# 胜率
def get_win_rate(id, state, my_card):
    community_card = state.sharedcards
    num_need_cards = 5 - len(community_card)
    active_players = []
    win_time = 0
    simulate_time = 10000
    for index in range(len(state.player)):
        if index != id and state.player[index].active:
            active_players.append(state.player[index])

    for time in range(simulate_time):
        used_card = my_card + community_card
        c_cards = community_card.copy()
        opponent_cards = []
        for player in active_players:
            t = random.sample(player.range, 1)[0]
            while t[0] in used_card or t[1] in used_card:
                t = random.sample(player.range, 1)[0]
            used_card += t
            opponent_cards.append(t)

        now_cards = [card for card in range(52) if card not in used_card]
        c_cards += random.sample(now_cards, num_need_cards)
        for oppoent_card in opponent_cards:
            cmp = judge_two(my_card + c_cards, oppoent_card + c_cards)
            if cmp == 1:
                break
        if cmp != 1:
            win_time += 1

    return 1.0 * win_time / simulate_time


# 赔率
def get_odds(id, state):
    need_bet = state.minbet - state.player[id].bet
    return need_bet / (need_bet + state.moneypot)


# 前后置位判断, 针对3人桌, 0 bottom, 1 small blind, 2 big blind
def pos_judge(id, state):
    bottom = 0
    small_blind = 1
    big_blind = 2
    if state.playernum == 2:
        if state.turnNum == 0:
            if id == bottom:
                is_prepos = True
            elif id == big_blind:
                is_prepos = False
            else:
                if state.player[big_blind].active:
                    is_prepos = True
                else:
                    is_prepos = False
        else:
            if id == small_blind:
                is_prepos = True
            elif id == bottom:
                is_prepos = False
            else:
                if state.player[bottom].active:
                    is_prepos = True
                else:
                    is_prepos = False

    else:
        if state.turnNum == 0:
            is_prepos = True if id == 0 or id == 1 else False
        else:
            is_prepos = True if id == 1 or id == 2 else False
    return is_prepos


def my_ai(id, state, username):
    small_blind = 20
    big_blind = 40
    shot_case1 = 0.4
    shot_case2 = 0.75
    shot_case3 = 1.25
    win_odd_factor = 0.1
    check_or_raise_front = 0.2
    check_or_raise_behind = 0.4
    first_shot = 0.2

    win_rate = get_win_rate(id, state, state.player[id].cards)
    odds = get_odds(id, state)

    decision = Decision()
    delta = state.minbet - state.player[id].bet

    is_prepos = pos_judge(id, state)

    file = open(username + ".txt", "a")
    file.write("turn num is " + str(state.turnNum) +
               " shared cards are : " + " ".join(id2str(state.sharedcards)) + "\n")
    for index in range(len(state.player)):
        if index != id and state.player[index].active:
            file.write("player " + str(index) + " range : " + str(len(state.player[index].range)) +
                       " this turn bet : " + str(state.player[index].bet) +
                       " total bet : " + str(state.player[index].totalbet) + "\n")

    file.write("my bet : " + str(state.player[id].bet) + " my total bet : " + str(state.player[id].totalbet) + "\n")
    file.write("my card is " + " ".join(id2str(state.player[id].cards)) + " my win rate is " + str(win_rate) + " my odds is " + str(odds) + "\n")

    '''
    # 最少加注量， state.last_raised
    # 我方主动，最低需要check
    if delta == 0:
        # 后置位
        if not is_prepos:
            # 胜率大幅高于赔率
            if win_rate > odds + win_odd_factor:
                t = random.random()
                if t <= check_or_raise_behind:
                    decision.raisebet = 1
                    decision.amount = 1 * state.moneypot if random.random() >= 0.5 else 2 * state.moneypot
                else:
                    decision.check = 1

            # 胜率约等于赔率
            elif odds + win_odd_factor >= win_rate >= odds - win_odd_factor:
                decision.check = 1

            # 胜率大幅低于赔率
            else:
                if delta > small_blind:
                    decision.giveup = 1
                else:
                    decision.check = 1

        # 前置位
        else:
            # 胜率大幅高于赔率
            if win_rate > odds + win_odd_factor:
                t = random.random()
                if t <= check_or_raise_front:
                    decision.raisebet = 1
                    decision.amount = 1 * state.moneypot if random.random() >= 0.5 else 2 * state.moneypot
                else:
                    decision.check = 1

            # 胜率约等于赔率
            elif odds + win_odd_factor >= win_rate >= odds - win_odd_factor:
                decision.check = 1

            # 胜率大幅低于赔率
            else:
                if delta > small_blind:
                    decision.giveup = 1
                else:
                    decision.check = 1

    # 我方被动，最低需要call
    else:
        # 后置位，最低需要call
        if not is_prepos:
            # 胜率大幅高于赔率
            if win_rate > odds + win_odd_factor:
                t = random.random()
                if t <= check_or_raise_behind:
                    if delta >= state.moneypot:
                        decision.callbet = 1
                    else:
                        decision.raisebet = 1
                        decision.amount = state.moneypot
                else:
                    decision.callbet = 1

            # 胜率约等于赔率
            elif odds + win_odd_factor >= win_rate >= odds - win_odd_factor:
                decision.callbet = 1

            # 胜率大幅低于赔率
            else:
                if delta > small_blind:
                    decision.giveup = 1
                else:
                    decision.callbet = 1

        # 前置位，最低需要call
        else:
            # 胜率大幅高于赔率
            if win_rate > odds + win_odd_factor:
                t = random.random()
                if t <= check_or_raise_front:
                    if delta >= state.moneypot:
                        decision.callbet = 1
                    else:
                        decision.raisebet = 1
                        decision.amount = state.moneypot
                else:
                    decision.callbet = 1

            # 胜率约等于赔率
            elif odds + win_odd_factor >= win_rate >= odds - win_odd_factor:
                decision.callbet = 1

            # 胜率大幅低于赔率
            else:
                if delta > small_blind:
                    decision.giveup = 1
                else:
                    decision.callbet = 1
    '''
    if state.turnNum == 0:
        pass
    elif state.turnNum == 1:
        pass
    elif state.turnNum == 2:
        pass
    elif state.turnNum == 3:
        pass
    file.close()
    return decision

def add_bet(state, total):
    # amount: 本局需要下的总注
    amount = total - state.player[state.currpos].totalbet
    assert(amount > state.player[state.currpos].bet)
    # Obey the rule of last_raised
    minamount = state.last_raised + state.minbet
    real_amount = max(amount, minamount)
    # money_needed = real_amount - state.player[state.currpos].bet
    decision = Decision()
    decision.raisebet = 1
    decision.amount = real_amount
    return decision


if __name__ == '__main__':
    player = Player(1000, 1)
