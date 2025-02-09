import asyncio
import argparse
from typing import Tuple
import treys

from tg.bot import Bot
import tg.types as pokerTypes
from time import sleep

from cards import Deck, Cards
from game import Player
from eval_deep_multi import eval

parser = argparse.ArgumentParser(
    prog='Template bot',
    description='A Turing Games poker bot that always checks or calls, no matter what the target bet is (it never folds and it never raises)')

parser.add_argument('--room', type=str, default='my-new-room',
                    help='The room to connect to')
parser.add_argument('--username', type=str, default='bot',
                    help='The username for this bot (make sure it\'s unique)')

args = parser.parse_args()



def card_name(long):
    if long == "1":
        return 'A'
    if long == "10":
        return 'T'
    elif long == "11":
        return 'J'
    elif long == "12":
        return 'Q'
    elif long == "13":
        return 'K'
    else:
        return long

def short_suit(long):
    if long == "hearts":
        return "h"
    elif long == "diamonds":
        return "d"
    elif long == "clubs":
        return "c"
    elif long == "spades":
        return "s"
    else:
        return "s"

# cnt = 0



# Always call
class TemplateBot(Bot):

    income_rates = [
        [-121, -440, -409, -382, -411, -432, -394, -357, -301, -259, -194, -116, 16 ],
        [-271, -42,  -345, -312, -340, -358, -371, -328, -277, -231, -165, -87,  54 ],
        [-245, -183,  52,  -246, -269, -287, -300, -308, -252, -204, -135, -55,  84 ],
        [-219, -151, -91,   152, -200, -211, -227, -236, -227, -169, -104, -24,  118],
        [-247, -177, -113, -52,   256, -145, -152, -158, -152, -145, -74,   9,   99 ],
        [-261, -201, -129, -65,   3,    376, -76,  -79,  -68,  -66,  -44,  48,   148],
        [-226, -204, -140, -73,  -2,    66,   503,  0,    15,   24,   45,  84,   194],
        [-191, -166, -147, -79,  -5,    68,   138,  647,  104,  113,  136, 177,  241],
        [-141, -116, -91,  -69,  -4,    75,   150,  235,  806,  226,  255, 295,  354],
        [-89,  -67,  -41,  -12,   7,    82,   163,  248,  349,  965,  301, 348,  410],
        [-29,  -3,    22,   51,   80,   108,  185,  274,  379,  423,  1141,403,  473],
        [47,    76,   101,  128,  161,  199,  230,  318,  425,  473,  529, 1325, 541],
        [175,   211,  237,  266,  249,  295,  338,  381,  491,  539,  594, 655, 1554]
    ]

    # No action
    income_rates = [
        # 2    3    4    5    6    7    8    9    T    J    Q    K    A
        ["R", "F", "F", "F", "F", "F", "F", "F", "F", "F", "R", "R", "R"],  # 2
        ["R", "R", "F", "F", "F", "F", "F", "F", "F", "R", "R", "R", "R"],  # 3          
        ["R", "R", "R", "R", "R", "F", "F", "F", "F", "R", "R", "R", "R"],  # 4
        ["R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R"],  # 5
        ["R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R"],  # 6
        ["R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R"],  # 7
        ["R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R"],  # 8
        ["R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R"],  # 9
        ["R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R"],  # T
        ["R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R"],  # J
        ["R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R"],  # Q
        ["R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R"],  # K
        ["R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R"],  # A
    ]  #  2    3    4    5    6    7    8    9    T    J    Q    K    A 



    # Call Raise Raise
    income_rates = [
        # 2    3    4    5    6    7    8    9    T    J    Q    K    A
        ["C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C"],  # 2
        ["C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C"],  # 3          
        ["C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C"],  # 4
        ["C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C"],  # 5
        ["C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C"],  # 6
        ["C", "C", "C", "C", "C", "R", "C", "C", "C", "C", "C", "C", "C"],  # 7
        ["C", "C", "C", "C", "C", "C", "R", "C", "C", "C", "C", "C", "C"],  # 8
        ["C", "C", "C", "C", "C", "C", "C", "R", "C", "C", "C", "C", "C"],  # 9
        ["C", "C", "C", "C", "C", "C", "C", "C", "R", "C", "C", "C", "C"],  # T
        ["C", "C", "C", "C", "C", "C", "C", "C", "C", "R", "C", "C", "R"],  # J
        ["C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "R", "C", "R"],  # Q
        ["C", "C", "C", "C", "C", "C", "C", "C", "C", "R", "R", "R", "R"],  # K
        ["C", "C", "C", "C", "C", "C", "R", "R", "R", "R", "R", "R", "R"],  # A
    ]  #  2    3    4    5    6    7    8    9    T    J    Q    K    A 


    def act(self, state, hand):
        # sleep(5)
        # print(state)
        # print('asked to act')
        print('acting', hand)

        # Get win probability

        # start_ii = time.time()
        k = self.p_hand_eval(state, hand)

        pot_size = state.pot

        if len(state.cards) == 0:
            # anti troll measures
            print("preflop")
            me = [p for p in state.players if p.id == args.username][0]
            raise_amount = state.target_bet - me.current_bet
            if raise_amount > state.big_blind * 7:
                self.preflop_strategy = ['monster']
                mi = self.get_income_rates(hand)
                if raise_amount > 200 * state.big_blind:
                    if mi > 1500:
                        return {'type': 'raise','amount':200 * state.big_blind}
                    else:
                        return {'type': 'fold'}
                if raise_amount > 100 * state.big_blind:
                    if mi > 1300:
                        return {'type': 'call'}
                    else:
                        return {'type': 'fold'}
                if raise_amount > 75 * state.big_blind:
                    if mi > 1000:
                        return {'type': 'call'}
                    else:
                        return {'type': 'fold'}
                if raise_amount > 40 * state.big_blind:
                    if mi > 800:
                        return {'type': 'call'}
                    else:
                        return {'type': 'fold'}
                if raise_amount > 20 * state.big_blind:
                    if mi > 400:
                        return {'type': 'call'}
                    else:
                        return {'type': 'fold'}
                if mi > 200:
                    return {'type': 'call'}
                else:
                    return {'type': 'fold'}
                    
                
            h = self.get_income_rates(hand)
            if h == "R":
                self.preflop_strategy.append("raise")
                return {'type': 'raise', 'amount': state.target_bet * 2}
            elif h == "C":
                self.preflop_strategy.append("call")
                return {'type': 'call'}
            else:
                return self.cheap_fold(state)

        if k > 0.85 + state.pot / 2000 * 0.1:
            print("RAISED 2x POT")
            return {'type': 'raise', 'amount': pot_size * 2}

        elif k < 0.25:
            print("FOLD")
            return self.cheap_fold(state)

        elif k < 0.45 and k >= 0.25:
            print("CHECK")
            return self.should_check(state, k)
        #CHANGE STATE POT THINGIE IF FUTURE GAME IS NOT 5000
        elif k >= 0.45 and k <= 0.65 and state.pot < 1000:
            match self.is_flush_straight_draw(state, hand):
                case 0:
                    print("CHECK")
                    return self.should_check(state, k)
                case 1:
                    print("RAISE POT")
                    return {'type': 'raise', 'amount' : pot_size+17}
                case 2:
                    print("RAISE 2x POT")
                    return {'type': 'raise', 'amount' : pot_size*2-31}

        elif k >= 0.75:
            print("RAISED 1/3x POT")
            return {'type': 'raise', 'amount': pot_size / 3}
        else:
            print("CHECK")
            return self.should_check(state, k)

    def cheap_fold(self, state):
        '''Fold if it costs more than zero to play. i.e.: folds every round'''
        me = [p for p in state.players if p.id == args.username][0]

        if state.target_bet - me.current_bet >= 10:
            return { 'type': 'fold' }
        else:
            return {'type': 'call'}


    def should_check(self, state, k):
        me = [p for p in state.players if p.id == args.username][0]

        raise_amount = state.target_bet - me.current_bet

        print("raise_amount", raise_amount / (state.pot + raise_amount))

        if k >= min(raise_amount / (state.pot + raise_amount) * state.pot / 1500, 0.9):
            print("-> calling")
            return {'type': 'call'}
        else:
            print("-> folding")
            return {'type': 'fold'}



    def opponent_action(self, action, player):
        self.preflop_strategy.append(action.type)
        print('opponent action?', action, player)
        pass

    def game_over(self, payouts):
        # global cnt
        print('game over', payouts)
        self.preflop_strategy = []
        # cnt += 1
        # print(cnt)
        pass

    def start_game(self, my_id):
        self.my_id = my_id
        self.preflop_strategy = []
        pass


    def is_flush_straight_draw(self, state, hand) -> int:
        """Returns whether state + hand is a flush or straight draw (1), or both (2)"""
        if len(state.cards) == 0:
            return 0

        # Combine hand and community cards
        all_cards = state.cards + hand

        # Flush draw check
        suit_counts = {}
        for card in all_cards:
            suit = card.suit
            suit_counts[suit] = suit_counts.get(suit, 0) + 1

        flush_draw = False
        for suit, count in suit_counts.items():
            if count == 4:
                # Check if both cards in the hand are of this suit
                if all(card.suit == suit for card in hand):
                    flush_draw = True
                    break

        # Straight draw check
        ranks = sorted([card.rank for card in all_cards])
        unique_ranks = sorted(list(set(ranks)))

        # Handle Ace low straight (A-2-3-4-5)
        if 1 in unique_ranks:
            unique_ranks.append(14)  # Add Ace as high

        straight_draw = False
        for i in range(len(unique_ranks) - 3):
            if unique_ranks[i+3] - unique_ranks[i] == 3:
                # Check if both cards in the hand are contributing to the straight draw
                required_ranks = set(range(unique_ranks[i], unique_ranks[i] + 4))
                if all(card.rank in required_ranks for card in hand):
                    straight_draw = True
                    break

        # Determine the result
        if flush_draw and straight_draw:
            return 2
        elif flush_draw or straight_draw:
            return 1
        else:
            return 0


    def p_hand_eval(self, state, hand):
        
        # print(state.cards)
        # print(hand)

        d = Deck()
        if len(state.cards) < 3:
            return 0
        elif len(state.cards) == 3:
            hand = [d.get(str(card_name(str(hand[0].rank)))+short_suit(hand[0].suit)), d.get(str(card_name(str(hand[1].rank)))+short_suit(hand[1].suit))]
            board = [d.get(str(card_name(str(state.cards[0].rank)))+short_suit(state.cards[0].suit)), d.get(str(card_name(str(state.cards[1].rank)))+short_suit(state.cards[1].suit)), d.get(str(card_name(str(state.cards[2].rank)))+short_suit(state.cards[2].suit))]
            e = eval(hand, board)
            print("3 potential strength: ")
            h = e.potential_hand_strength(2)
            print(h)
            return h
        elif len(state.cards) == 4:
            hand = [d.get(str(card_name(str(hand[0].rank)))+short_suit(hand[0].suit)), d.get(str(card_name(str(hand[1].rank)))+short_suit(hand[1].suit))]
            board = [d.get(str(card_name(str(state.cards[0].rank)))+short_suit(state.cards[0].suit)), d.get(str(card_name(str(state.cards[1].rank)))+short_suit(state.cards[1].suit)), d.get(str(card_name(str(state.cards[2].rank)))+short_suit(state.cards[2].suit)), d.get(str(card_name(str(state.cards[3].rank)))+short_suit(state.cards[3].suit))]
            e = eval(hand, board)
            print("4 potential strength: ")
            h = e.potential_hand_strength(1)
            print(h)
            return h
        elif len(state.cards) == 5:
            hand = [d.get(str(card_name(str(hand[0].rank)))+short_suit(hand[0].suit)), d.get(str(card_name(str(hand[1].rank)))+short_suit(hand[1].suit))]
            board = [d.get(str(card_name(str(state.cards[0].rank)))+short_suit(state.cards[0].suit)), d.get(str(card_name(str(state.cards[1].rank)))+short_suit(state.cards[1].suit)), d.get(str(card_name(str(state.cards[2].rank)))+short_suit(state.cards[2].suit)), d.get(str(card_name(str(state.cards[3].rank)))+short_suit(state.cards[3].suit)), d.get(str(card_name(str(state.cards[4].rank)))+short_suit(state.cards[4].suit))]
            e = eval(hand, board)
            print("5 potential strength: ")
            h = e.hand_strength()
            print(h)
            return h

        # print(e.hand_strength())

    def get_income_rates(self, hand: Tuple[pokerTypes.Card, pokerTypes.Card]):
        
        if len(self.preflop_strategy) == 0:
            print("using no action")
            TemplateBot.income_rates = [
                # 2    3    4    5    6    7    8    9    T    J    Q    K    A
                ["R", "F", "F", "F", "F", "F", "F", "F", "F", "F", "R", "R", "R"],  # 2
                ["R", "R", "F", "F", "F", "F", "F", "F", "F", "R", "R", "R", "R"],  # 3          
                ["R", "R", "R", "R", "R", "F", "F", "F", "F", "R", "R", "R", "R"],  # 4
                ["R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R"],  # 5
                ["R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R"],  # 6
                ["R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R"],  # 7
                ["R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R"],  # 8
                ["R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R"],  # 9
                ["R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R"],  # T
                ["R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R"],  # J
                ["R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R"],  # Q
                ["R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R"],  # K
                ["R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R"],  # A
            ]  #  2    3    4    5    6    7    8    9    T    J    Q    K    A 

        elif self.preflop_strategy == ["call"]:
            print("using call")
            TemplateBot.income_rates = [
                ["C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C"],  # 2
                ["C", "R", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "R"],  # 3
                ["C", "R", "R", "R", "C", "C", "C", "C", "C", "C", "C", "C", "R"],  # 4
                ["C", "R", "R", "R", "R", "C", "C", "C", "C", "C", "C", "R", "R"],  # 5
                ["C", "R", "R", "R", "R", "R", "R", "C", "C", "C", "R", "R", "R"],  # 6
                ["C", "C", "R", "R", "R", "R", "R", "R", "R", "C", "C", "R", "R"],  # 7
                ["C", "C", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R"],  # 8
                ["C", "C", "C", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R"],  # 9
                ["C", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R"],  # T
                ["R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R"],  # J
                ["R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R"],  # Q
                ["R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R"],  # K
                ["R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R"]
            ]  #  2    3    4    5    6    7    8    9    T    J    Q    K    A 

        elif self.preflop_strategy == ["call", "raise", "raise"]:
            print("using call, raise, raise")
            TemplateBot.income_rates = [
                # 2    3    4    5    6    7    8    9    T    J    Q    K    A
                ["C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C"],  # 2
                ["C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C"],  # 3          
                ["C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C"],  # 4
                ["C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C"],  # 5
                ["C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C"],  # 6
                ["C", "C", "C", "C", "C", "R", "C", "C", "C", "C", "C", "C", "C"],  # 7
                ["C", "C", "C", "C", "C", "C", "R", "C", "C", "C", "C", "C", "C"],  # 8
                ["C", "C", "C", "C", "C", "C", "C", "R", "C", "C", "C", "C", "C"],  # 9
                ["C", "C", "C", "C", "C", "C", "C", "C", "R", "C", "C", "C", "C"],  # T
                ["C", "C", "C", "C", "C", "C", "C", "C", "C", "R", "C", "C", "R"],  # J
                ["C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "R", "C", "R"],  # Q
                ["C", "C", "C", "C", "C", "C", "C", "C", "C", "R", "R", "R", "R"],  # K
                ["C", "C", "C", "C", "C", "C", "R", "R", "R", "R", "R", "R", "R"],  # A
            ]  #  2    3    4    5    6    7    8    9    T    J    Q    K    A 

        elif self.preflop_strategy == ["raise"]:
            print("using raise")
            TemplateBot.income_rates = [
                ["C", "F", "F", "F", "F", "F", "F", "C", "C", "C", "C", "C", "C"],
                ["C", "R", "C", "C", "C", "F", "F", "C", "C", "C", "C", "C", "C"],
                ["C", "R", "R", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C"],
                ["C", "R", "R", "R", "C", "C", "C", "C", "C", "C", "C", "C", "C"],
                ["C", "C", "R", "R", "R", "C", "C", "C", "C", "C", "C", "C", "C"],
                ["C", "C", "C", "R", "R", "R", "C", "C", "C", "C", "C", "C", "C"],
                ["C", "C", "C", "R", "R", "R", "R", "C", "C", "C", "C", "C", "R"],
                ["C", "C", "C", "R", "R", "R", "R", "R", "C", "C", "C", "C", "R"],
                ["C", "C", "C", "C", "R", "R", "R", "R", "R", "C", "C", "C", "R"],
                ["C", "C", "R", "R", "C", "R", "R", "R", "R", "R", "C", "R", "R"],
                ["C", "C", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R"],
                ["C", "C", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R"],
                ["C", "C", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R", "R"]
            ]
        elif self.preflop_strategy == ["monster"]:
            print("using monster")
            TemplateBot.income_rates = [
                [-121, -440, -409, -382, -411, -432, -394, -357, -301, -259, -194, -116, 16 ],
                [-271, -42,  -345, -312, -340, -358, -371, -328, -277, -231, -165, -87,  54 ],
                [-245, -183,  52,  -246, -269, -287, -300, -308, -252, -204, -135, -55,  84 ],
                [-219, -151, -91,   152, -200, -211, -227, -236, -227, -169, -104, -24,  118],
                [-247, -177, -113, -52,   256, -145, -152, -158, -152, -145, -74,   9,   99 ],
                [-261, -201, -129, -65,   3,    376, -76,  -79,  -68,  -66,  -44,  48,   148],
                [-226, -204, -140, -73,  -2,    66,   503,  0,    15,   24,   45,  84,   194],
                [-191, -166, -147, -79,  -5,    68,   138,  647,  104,  113,  136, 177,  241],
                [-141, -116, -91,  -69,  -4,    75,   150,  235,  806,  226,  255, 295,  354],
                [-89,  -67,  -41,  -12,   7,    82,   163,  248,  349,  965,  301, 348,  410],
                [-29,  -3,    22,   51,   80,   108,  185,  274,  379,  423,  1141,403,  473],
                [47,    76,   101,  128,  161,  199,  230,  318,  425,  473,  529, 1325, 541],
                [175,   211,  237,  266,  249,  295,  338,  381,  491,  539,  594, 655, 1554]
    ]
        else:
            print("using", self.preflop_strategy)
            TemplateBot.income_rates = [
                ["C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C"],
                ["C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C"],
                ["C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C"],
                ["C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C"],
                ["C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C"],
                ["C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C"],
                ["C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C"],
                ["C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C"],
                ["C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C"],
                ["C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C"],
                ["C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C"],
                ["C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C"],
                ["C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C", "C"]
            ]



        for card in hand:
            if card.rank == 1:
                card.rank = 14
        temp = sorted(hand, key=lambda x: x.rank)
        if hand[0].suit == hand[1].suit:
            return TemplateBot.income_rates[temp[1].rank-2][temp[0].rank-2]
        else:
            return TemplateBot.income_rates[temp[0].rank-2][temp[1].rank-2]       

        

if __name__ == "__main__":
    bot = TemplateBot("ws.turingpoker.com", "80", args.room+"-timeout=10000-minPlayers=2-maxRounds=1000-defaultStack=5000-bigBlind=10-smallBlind=5", args.username)
    asyncio.run(bot.start())