#!/usr/bin/env python3
import asyncio
from typing import Tuple
import argparse
import treys
import time

from tg.bot import Bot
import tg.types as pokerTypes

parser = argparse.ArgumentParser(
    prog='Template bot',
    description='A Turing Games poker bot that always checks or calls, no matter what the target bet is (it never folds and it never raises)')

parser.add_argument('--port', type=int, default=1999,
                    help='The port to connect to the server on')
parser.add_argument('--host', type=str, default='localhost',
                    help='The host to connect to the server on')
parser.add_argument('--room', type=str, default='my-new-room',
                    help='The room to connect to')
parser.add_argument('--simulations', type=int, default=1000)
parser.add_argument('--username', type=str, default='bot',
                    help='The username for this bot (make sure it\'s unique)')


args = parser.parse_args()

def card_name(card: pokerTypes.Card):
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

# Use kelly criterion to bet based on the win probability
class KellyCriterion(Bot):
    def act(self, state, hand):
        print("acting")

        prob = self.win_prob(state, hand)
        me = None
        for player in state.players:
            if player.id == self.my_id:
                me = player
                break
        p = prob

        b = len(state.players)

        raise_to = (p - (1-p)/b)*(me.stack)
        print('my stack:', me.stack, raise_to, p, ''.join(map(card_name, hand)), ''.join(map(card_name, state.cards)))

        cost_to_play = min(state.target_bet-me.current_bet, me.stack)

        if raise_to > state.target_bet:
            return {'type': 'raise', 'amount': raise_to-state.target_bet}
        elif raise_to >= cost_to_play or cost_to_play == 0:
            return {'type': 'call'}
        print('fold')
        return {'type': 'fold'}

    def opponent_action(self, action, player):
        print("opponent_action")
        pass

    def game_over(self, payouts):
        print('game over', payouts)
        pass

    def start_game(self, my_id):
        self.my_id = my_id
        print('start game', my_id)

    def win_prob(self, state: pokerTypes.PokerSharedState, hand: Tuple[pokerTypes.Card, pokerTypes.Card]):
        out = 0
        hand = [
            treys.Card.new(card_name(hand[0])),
            treys.Card.new(card_name(hand[1]))]
        board = [treys.Card.new(card_name(card)) for card in state.cards]
        evaluator = treys.Evaluator()
        for i in range(args.simulations):
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
        return out/args.simulations


if __name__ == "__main__":
    bot = KellyCriterion("ws.turingpoker.com", "80", args.room, args.username)
    asyncio.run(bot.start())