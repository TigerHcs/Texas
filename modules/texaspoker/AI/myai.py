# -*-coding:utf-8-*-
import random
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


def is_same_color(card1, card2):
    return id2color(card1) == id2color(card2)


def is_high_power(my_cards):
    num1 = id2num(my_cards[0])
    num2 = id2num(my_cards[1])
    if num1 == num2 and num1 >= 9:
        return True
    elif num1 >= 11 and num2 >= 11:
        return True
    else:
        return False


def turn0_range_judge(my_cards, pos):
    my_cards.sort()
    same_color = is_same_color(my_cards[0], my_cards[1])
    num1 = id2num(my_cards[0])
    num2 = id2num(my_cards[1])
    if num2 == 12 or num1 == num2:
        return True
    if same_color and pos == 0:
        if num1 > 0 and num2 == 11:
            return True
        elif num1 > 2 and num2 == 10:
            return True
        elif num1 > 3 and (num2 == 9 or num2 == 8 or num2 == 7):
            return True
        elif num1 > 2 and (num2 == 6 or num2 == 5):
            return True
        elif num1 > 1 and (num2 == 4 or num2 == 3):
            return True
        elif num1 == 1 and num2 == 2:
            return True
        else:
            return False
    elif same_color and pos == 1:
        if num2 == 11:
            return True
        elif num1 > 1 and (num2 == 10 or num2 == 5):
            return True
        elif num1 > 3 and (num2 == 9 or num2 == 8):
            return True
        elif num1 > 2 and (num2 == 7 or num2 == 6):
            return True
        elif num1 > 0 and (num2 == 4 or num2 == 3 or num2 == 2):
            return True
        elif num1 == 0 and num2 == 1:
            return True
        else:
            return False
    elif not same_color and pos == 0:
        if num1 > 6:
            return True
        else:
            return False
    else:
        if num1 > 5:
            return True
        else:
            return False


# 胜率
def get_win_rate(id, state, my_card, range_util):
    community_card = state.sharedcards
    num_need_cards = 5 - len(community_card)
    active_players = []
    win_time = 0
    simulate_time = 50000
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
            cmp = range_util.judge_two(my_card + c_cards, oppoent_card + c_cards)
            if cmp == 1:
                break
        if cmp != 1:
            win_time += 1

    return 1.0 * win_time / simulate_time


# 赔率
def get_odds(id, state):
    need_bet = state.minbet - state.player[id].bet
    return need_bet / (need_bet + state.moneypot)


def get_top_ranges(ranges, n):
    ans = ""
    cnt = 0
    for range in ranges:
        ans += "(" + ' '.join(id2str(range)) + ")"
        cnt += 1
        if cnt >= n:
            break
    return ans

# 0 bottom, 1 small blind, 2 big blind

def my_ai(id, state, username,range_util):
    small_blind = 20
    big_blind = 40
    shot_case1 = 0.3
    shot_case2 = 0.75
    shot_case3 = 1.25

    my_cards = state.player[id].cards
    win_rate = get_win_rate(id, state, my_cards,range_til)
    odds = get_odds(id, state)

    if state.turnNum == 0:
        state.first_round_win_rate = win_rate

    decision = Decision()
    delta = state.minbet - state.player[id].bet

    file = open(username + ".txt", "a")
    file.write("turn num is " + str(state.turnNum) +
               " shared cards are : " + " ".join(id2str(state.sharedcards)) + "\n")
    for index in range(len(state.player)):
        if index != id and state.player[index].active:
            file.write("player " + str(index) + " range : " + str(len(state.player[index].range)) +
                       " this turn bet : " + str(state.player[index].bet) +
                       " total bet : " + str(state.player[index].totalbet) +
                       " top 5 range: " + get_top_ranges(state.player[index].range, 20) + "\n")

    file.write("my bet : " + str(state.player[id].bet) + " my total bet : " + str(state.player[id].totalbet) + "\n")
    file.write("my card is " + " ".join(id2str(state.player[id].cards)) + " my win rate is " + str(win_rate) + " my odds is " + str(odds) + "\n")

    # flop前
    if state.turnNum == 0:
        # 不知道 或 进攻
        if state.last_raised_id == -1 or state.last_raised_id == id:
            # bottom
            if id == 0:
                if turn0_range_judge(my_cards, 0):
                    p = random.random()
                    if p <= 0.5:
                        if delta > 0:
                            decision.callbet = 1
                        else:
                            decision.check = 1
                    else:
                        add_bet(state, decision, shot_case1 * state.moneypot)
                else:
                    decision.giveup = 1

            # small blind
            elif id == 1:
                if turn0_range_judge(my_cards, 1):
                    p = random.random()
                    if p <= 0.5:
                        if delta > 0:
                            decision.callbet = 1
                        else:
                            decision.check = 1
                    else:
                        add_bet(state, decision, shot_case1 * state.moneypot)
                else:
                    decision.giveup = 1

            # big blind
            else:
                p = random.random()
                if win_rate >= 0.5:
                    if p <= 0.6:
                        if delta > 0:
                            decision.callbet = 1
                        else:
                            decision.check = 1
                    else:
                        add_bet(state, decision, shot_case1 * state.moneypot)
                else:
                    if delta > 0:
                        decision.callbet = 1
                    else:
                        decision.check = 1
        # 防守位
        else:
            if is_high_power(my_cards):
                if delta > 0:
                    decision.callbet = 1
                else:
                    decision.check = 1
            elif win_rate >= 0.7:
                p = random.random()
                if p <= 0.4:
                    if delta > 0:
                        decision.callbet = 1
                    else:
                        decision.check = 1
                else:
                    add_bet(state, decision, shot_case1 * state.moneypot)
            elif win_rate >= 0.5:
                p = random.random()
                if p <= 0.7:
                    if delta > 0:
                        decision.callbet = 1
                    else:
                        decision.check = 1
                else:
                    add_bet(state, decision, shot_case1 * state.moneypot)
            elif win_rate > odds:
                p = random.random()
                if p <= 0.8:
                    if delta > 0:
                        decision.callbet = 1
                    else:
                        decision.check = 1
                else:
                    decision.giveup = 1

            else:
                decision.giveup = 1

    # flop
    elif state.turnNum == 1:
        detla_win_rate = win_rate - state.first_round_win_rate
        print("my win rate change is ", detla_win_rate)
        # 防守位
        if state.last_raised_id != -1 and state.last_raised_id != id:
            if win_rate >= 0.7:
                p = random.random()
                thresh = 0.8 + 0.2 * (win_rate - 0.7) / 0.3
                if p <= thresh:
                    add_bet(state, decision, shot_case1 * state.moneypot)
                else:
                    if delta > 0:
                        decision.callbet = 1
                    else:
                        decision.check = 1

            elif win_rate >= 0.5:
                p = random.random()
                thresh = 0.1 + 0.7 * (win_rate - 0.5) / 0.2
                if p >= thresh:
                    if delta > 0:
                        decision.callbet = 1
                    else:
                        decision.check = 1
                else:
                    add_bet(state, decision, shot_case1 * state.moneypot)

            else:
                p = random.random()
                if win_rate > odds:
                    if p <= 0.8:
                        if delta > 0:
                            decision.callbet = 1
                        else:
                            decision.check = 1
                    else:
                        decision.giveup = 1
                else:
                    decision.giveup = 1

        # 进攻位
        else:
            # 胜率下降5%以上 或 胜率小于50%
            if detla_win_rate < -0.05 or win_rate < 0.5:
                p = random.random()
                if p <= 0.8:
                    decision.check = 1
                else:
                    add_bet(state, decision, shot_case1 * state.moneypot)

            # 胜率未下降5% 且 胜率大于等于50%
            else:
                # 胜率上升了10%
                if detla_win_rate >= 0.1:
                    p = random.random()
                    if p <= 0.7:
                        add_bet(state, decision, shot_case1 * state.moneypot)
                    else:
                        add_bet(state, decision, shot_case2 * state.moneypot)
                else:
                    p = random.random()
                    if p <= 0.8:
                        add_bet(state, decision, shot_case1 * state.moneypot)
                    else:
                        decision.check = 1


    # turn
    elif state.turnNum == 2:
        # 防守位
        if state.last_raised_id != -1 and state.last_raised_id != id:
            if win_rate >= 0.8:
                p = random.random()
                thresh = 0.8 + 0.2 * (win_rate - 0.8) / 0.2
                if p <= thresh:
                    add_bet(state, decision, shot_case1 * state.moneypot)
                else:
                    if delta > 0:
                        decision.callbet = 1
                    else:
                        decision.check = 1

            elif win_rate >= 0.5:
                p = random.random()
                thresh = 0.1 + 0.7 * (win_rate - 0.5) / 0.3
                if p >= thresh:
                    if delta > 0:
                        decision.callbet = 1
                    else:
                        decision.check = 1
                else:
                    add_bet(state, decision, shot_case1 * state.moneypot)
            else:
                p = random.random()
                if win_rate > odds:
                    if p <= 0.8:
                        if delta > 0:
                            decision.callbet = 1
                        else:
                            decision.check = 1
                    else:
                        decision.giveup = 1
                else:
                    decision.giveup = 1

        # 进攻位
        else:
            if win_rate >= 0.7:
                p = random.random()
                if p <= 0.7:
                    add_bet(state, decision, shot_case2 * state.moneypot)
                else:
                    add_bet(state, decision, shot_case1 * state.moneypot)
            elif win_rate >= 0.55:
                p = random.random()
                if p >= 0.8:
                    add_bet(state, decision, shot_case2 * state.moneypot)
                elif p >= 0.2:
                    add_bet(state, decision, shot_case1 * state.moneypot)
                else:
                    if delta > 0:
                        decision.callbet = 1
                    else:
                        decision.check = 1
            else:
                p = random.random()
                if p <= 0.9:
                    if delta > 0:
                        decision.callbet = 1
                    else:
                        decision.check = 1
                else:
                    add_bet(state, decision, shot_case1 * state.moneypot)


    # river
    elif state.turnNum == 3:
        # 防守位
        if state.last_raised_id != -1 and state.last_raised_id != id:
            if win_rate >= 0.85:
                p = random.random()
                thresh = 0.8 + 0.2 * (win_rate - 0.85) / 0.15
                if p <= thresh:
                    p = random.random()
                    if p <= 0.5:
                        add_bet(state, decision, shot_case2 * state.moneypot)
                    else:
                        add_bet(state, decision, shot_case1 * state.moneypot)
                else:
                    if delta > 0:
                        decision.callbet = 1
                    else:
                        decision.check = 1
            elif win_rate >= 0.5:
                p = random.random()
                thresh = 0.1 + 0.7 * (win_rate - 0.5) / 0.35
                if p >= thresh:
                    if delta > 0:
                        decision.callbet = 1
                    else:
                        decision.check = 1
                else:
                    add_bet(state, decision, shot_case1 * state.moneypot)
            else:
                p = random.random()
                if win_rate > odds:
                    if p <= 0.8:
                        if delta > 0:
                            decision.callbet = 1
                        else:
                            decision.check = 1
                    else:
                        decision.giveup = 1
                else:
                    decision.giveup = 1

        # 进攻位
        else:
            if win_rate >= 0.8:
                p = random.random()
                if p >= 0.8:
                    add_bet(state, decision, shot_case3 * state.moneypot)
                elif p >= 0.3:
                    add_bet(state, decision, shot_case2 * state.moneypot)
                else:
                    add_bet(state, decision, shot_case1 * state.moneypot)
            elif win_rate >= 0.6:
                p = random.random()
                if p >= 0.8:
                    add_bet(state, decision, shot_case2 * state.moneypot)
                elif p >= 0.4:
                    add_bet(state, decision, shot_case1 * state.moneypot)
                else:
                    if delta > 0:
                        decision.callbet = 1
                    else:
                        decision.check = 1
            else:
                p = random.random()
                thresh = 0.6 * (win_rate - 0.2) / 0.4
                if p > 0.2 and p <= thresh:
                    add_bet(state, decision, shot_case1 * state.moneypot)
                else:
                    if delta > 0:
                        decision.callbet = 1
                    else:
                        decision.check = 1


    print_decision(file, decision)
    file.close()
    return decision


def print_decision(file, decision):
    if decision.giveup == 1:
        file.write("my decision is give up"+ "\n")
    elif decision.callbet == 1:
        file.write("my decision is callbet" + "\n")
    elif decision.check == 1:
        file.write("my decision is check" + "\n")
    elif decision.allin == 1:
        file.write("my decision is all in " + "\n")
    elif decision.raisebet == 1:
        file.write("my decision is raise bet " + "\n")


def add_bet(state, decision, amount):
    # decision.amount本轮需要加注到的amount
    amount = amount + state.minbet
    minamount = state.last_raised + state.minbet
    real_amount = int(max(amount, minamount))
    decision.raisebet = 1
    decision.amount = real_amount


if __name__ == '__main__':
    print(random.random())
