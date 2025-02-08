#!/usr/bin/env python3
import asyncio
import argparse

from tg.bot import Bot
import time

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
class TemplateBot(Bot):
    def act(self, state, hand):
        print('asked to act')
        print('acting', state, hand, self.my_id)

        time.sleep(2)
        return { 'type': 'raise', 'amount': 100 }

    def opponent_action(self, action, player):
        #print('opponent action?', action, player)
        pass

    def game_over(self, payouts):
        global cnt
        print('game over', payouts)
        cnt += 1
        print(cnt)

    def start_game(self, my_id):
        self.my_id = my_id
        pass

if __name__ == "__main__":
    bot = TemplateBot("ws.turingpoker.com", "80", args.room, args.username)
    asyncio.run(bot.start())