#-*-coding:utf-8-*-


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