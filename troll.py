#!/usr/bin/env python3
import asyncio
import argparse

from tg.bot import Bot
import copy

parser = argparse.ArgumentParser(
    prog='Template bot',
    description='A Turing Games poker bot that always checks or calls, no matter what the target bet is (it never folds and it never raises)')

parser.add_argument('--room', type=str, default='my-new-room',
                    help='The room to connect to')
parser.add_argument('--username', type=str, default='bot',
                    help='The username for this bot (make sure it\'s unique)')

args = parser.parse_args()

cnt = 0
# Always call

push_set = ('KQs', 'AQs', 'AKs', 'AAo', 'KKo', 'QQo', 'JJo', 'AJs', 'TTo', '99o', '88o', '77o', 'AKo', 'AQo', 'AJo')

def card_name(card):
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
    return f"{val}"

def isFirst(card1, card2):
    return card1.rank > card2.rank


def isPush(hand):
    card1 = copy.deepcopy(hand[0])
    card2 = copy.deepcopy(hand[1])
    if not isFirst(hand[0], hand[1]):
        card1, card2 = card2, card1
    name1 = card_name(card1)
    name2 = card_name(card2)
    fullName = name1 + name2
    if (card1.suit == card2.suit):
        fullName += 's'
    else:
        fullName += 'o'
    print(fullName)
    return fullName in push_set


class Troll(Bot):

    def act(self, state, hand):
        cost_to_play = state.target_bet
        if isPush(hand):
            print("all innnn")
            return {'type': 'raise', 'amount': 10000000}
        else:
            if cost_to_play == 0:
                return {'type': 'check'}
            return {'type': 'fold'}

    def opponent_action(self, action, player):
        pass

    def game_over(self, payouts):
        print('game over', payouts)
        pass

    def start_game(self, my_id):
        self.my_id = my_id
        print('start game', my_id)

if __name__ == "__main__":
    bot = Troll("ws.turingpoker.com", "80", args.room, args.username)
    asyncio.run(bot.start())