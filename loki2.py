#!/usr/bin/env python3
import asyncio
import argparse

from tg.bot import Bot
from typing import Dict, Tuple

from websockets.client import connect
from tg import types, util
from eval import eval, cards


import treys
import asyncio
import argparse

from tg.bot import Bot

parser = argparse.ArgumentParser(
    prog='Template bot',
    description='A Turing Games poker bot that always checks or calls, no matter what the target bet is (it never folds and it never raises)')

parser.add_argument('--port', type=int, default=1999,
                    help='The port to connect to the server on')
parser.add_argument('--host', type=str, default='localhost',
                    help='The host to connect to the server on')
parser.add_argument('--room', type=str, default='my-new-room',
                    help='The room to connect to')
parser.add_argument('--username', type=str, default='bot',
                    help='The username for this bot (make sure it\'s unique)')

args = parser.parse_args()


def card_name(card: types.Card):
    val = str(card.rank)
    if card.rank == 1:
        val = 'A'
    if card.rank == 10:
        val = 'T'
    elif card.rank == 11:
        val = 'J'
    elif card.rank == 12:
        val = 'Q'
    elif card.rank == 13:
        val = 'K'
    return f"{val}{card.suit[0]}"

class Loki(Bot):
    # --- Pre-Flop Betting Strategy --- #
    # Income rates for pre-flop. Used to determine what strategy to play
    # From left to right, each column goes from 2 to A
    # From top to bottom, each row goes from 2 to A
    # Suited hand's IR is calculated for row>column, otherwise an unsuited hand's IR will be calculated as column<row
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

    # Expert-defined values to calculate strategy thresholds. There are technically different thresholds, but we'll use the ones for 3-4 players for the sake of simplicity.
    # Dictionnary values are as:
    # 'tightness': [(make1 values), (make2 values), (make3 values)] where values are a tuple (base, increment)
    # The values for 'call1' and 'make1' are the same, as well as the values for 'call2' and 'make2'
    preflop_strategy_values = {
        'tight': {'make1': (75, 50), 'make2': (225, 50), 'make4': (600,0)},
        'moderate': {'make1': (25, 25), 'make2': (200, 25), 'make4': (580,0)},
        'loose': {'make1': (25, 10), 'make2': (175, 10), 'make4': (480,0)}
    }

    # The values for the thresholds of effective hand strength used to determine post-flop strategies. All vary by 0.05, depending on the tightness.
    ehs = {
        'tight': {'make2': 0.90, 'make1': 0.55},
        'moderate': {'make2': 0.85, 'make1': 0.50},
        'loose': {'make2': 0.80, 'make1': 0.45}
    }

    # The values for which the bots would bluff.
    bluff_percentage = {
        'tight': 0.04,
        'moderate': 0.07,
        'loose': 0.10
    }

    def act(self, state: types.PokerSharedState, hand: Tuple[types.Card, types.Card]) -> types.Action:
        '''Playing function for the bot.'''

        if state.round == "pre-flop":       # We are in pre-flop
            # if self.are_we_bluffing():
            #     print('(bluffing): ', end='')

            return self.play_preflop(state, hand)
    
        e = eval.eval([card_name(c) for c in hand], [card_name(c) for c in state.cards])

        ehs = e.potential_hand_strength()


        if ehs >= 0.85:
            return self.make2(state)

        elif ehs >= 0.45:
            return self.make1(state)

        return self.make0(state)
    

    def play_preflop(self, state, hand: Tuple[types.Card, types.Card]) -> types.Action:
        self.IR = self.get_income_rates(hand)

        if self.IR >= 480:
            return self.make4(state)
        
        elif self.IR >= 175:
            return self.make2(state)

        elif self.IR >= 25:
            return self.make1(state)

        else:
            return self.make0(state)


    def get_income_rates(self, hand: Tuple[types.Card, types.Card]):
        for card in hand:
            if card.rank == 1:
                card.rank = 14
        temp = sorted(hand, key=lambda x: x.rank)
        if hand[0].suit == hand[1].suit:
            return Loki.income_rates[temp[1].rank-2][temp[0].rank-2]
        else:
            return Loki.income_rates[temp[0].rank-2][temp[1].rank-2]

    def compute_ppot(self):
        '''Compute the PPOT of the hand. Used for semi-bluffing''' 
        a = eval(self.hand(), self.table.board.cards())
        return a.potential_hand_strength(2, True)[0]

    # Strategies
    def make0(self, state: types.PokerSharedState):
        '''Fold if it costs more than zero to play. i.e.: folds every round'''
        print("(make0):", end=' ')
        if state.target_bet >= 10:
            return {'type': 'fold'}
        else:
            return {'type': 'call'}
        
    # def call1(self, state: types.PokerSharedState):
    #     '''Fold if it costs more than 3 bet to continue playing and the bot hasn't put money into the pot this round yet, otherwise check/call.'''
    #     print("(call1):", end=' ')
    #     if (self.table.required_bet > self.table.blind_amount * 6 and
    #         (self.current_bet == 0 or
    #          self.current_bet == self.table.blind_amount and self.position == 1 or
    #          self.current_bet == self.table.blind_amount * 2 and self.position == 2
    #         )):
    #         return {'type': 'fold'}
    #     else:
    #         return {'type': 'call'}
    
    def make1(self, state: types.PokerSharedState):
        # '''If no bets have been made this round, then bet. Fold if two or more bets are required to continue. Otherwise check/call. THIS STRATEGY SHOULD NOT BE CALLED IF BOT IS THE BIG BLIND (it shouldn't happen).'''
        # print("(make1):", end=' ')
        return {'type': 'call'}

    def call2(self, state: types.PokerSharedState):
        '''Always check/call, whatever bet is on the table.'''
        print("(call2):", end=' ')
        return {'type': 'call'}

    def make2(self, state: types.PokerSharedState):
        '''Bet/raise if less than two bets/raises have been made this round, otherwise call.'''
        print("(make2):", end=' ')
        return {'type': 'bet', 'amount': state.pot * 2 / 3}

    def make4(self, state: types.PokerSharedState):
        '''Bet/raise until betting is capped, or player goes all-in.'''
        print("(make4):", end=' ')
        return {'type': 'bet', 'amount': state.pot * 2 / 3}

    def opponent_action(self, action, player):
        #print('opponent action?', action, player)
        pass

    def game_over(self, payouts):
        print('game over', payouts)

    def start_game(self, my_id):
        self.my_id = my_id
        pass

    
    def win_prob(self, state: types.PokerSharedState, hand: Tuple[types.Card, types.Card]):
        out = 0
        hand = [
            treys.Card.new(card_name(hand[0])),
            treys.Card.new(card_name(hand[1]))]
        board = [treys.Card.new(card_name(card)) for card in state.cards]
        evaluator = treys.Evaluator()

        for i in range(10000):
            deck = treys.Deck()
            deck.shuffle()
            for card in hand+board:
                deck.cards.remove(card)
            pred = board + deck.draw(5-len(board))
            score = evaluator.evaluate(hand, pred)
            other = 10**9

            for player in state.players:
                if player.id != self.my_id:
                    other = min(other, evaluator.evaluate(deck.draw(2), pred))
            if score < other:
                out += 1
        return out/10000

if __name__ == "__main__":
    bot = Loki("ws.turingpoker.com", "80", args.room, args.username)
    asyncio.run(bot.start())