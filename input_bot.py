import asyncio
import argparse

from tg.bot import Bot
# from time import sleep

import sys
import os
import time

if os.name == 'nt':
    import msvcrt
else:
    import tty
    import termios
    import select

parser = argparse.ArgumentParser(
    prog='Input bot',
    description='Allows users to input actions, j for call or check, f for fold, number for raise')

parser.add_argument('--room', type=str, default='my-new-room',
                    help='The room to connect to')
parser.add_argument('--username', type=str, default='bot',
                    help='The username for this bot (make sure it\'s unique)')

args = parser.parse_args()

cnt = 0

def get_action():
    if os.name == 'nt':
        # Windows handling
        # Read the first character
        if not msvcrt.kbhit():
            # No input available, wait for a character
            char = msvcrt.getch().decode('utf-8', errors='ignore').lower()
        else:
            char = msvcrt.getch().decode('utf-8', errors='ignore').lower()
    else:
        # Unix handling
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            # Enable echo after setting raw mode
            new_settings = termios.tcgetattr(fd)
            new_settings[3] |= termios.ECHO  # c_lflag is at index 3
            termios.tcsetattr(fd, termios.TCSADRAIN, new_settings)
            char = sys.stdin.read(1).lower()
        finally:
            # Restore original settings
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    if char == 'j':
        return 'call'
    elif char == 'f':
        return 'fold'
    elif char == 'b':
        return 'all'
    elif char.isdigit():
        number = [char]
        deadline = time.time() + 0.9
        while True:
            if os.name == 'nt':
                # Windows: check for additional digits
                time_left = deadline - time.time()
                if time_left <= 0:
                    break
                if msvcrt.kbhit():
                    next_char = msvcrt.getch().decode('utf-8', errors='ignore')
                    if next_char.isdigit():
                        number.append(next_char)
                        deadline = time.time() + 0.9
                    else:
                        print('Invalid action')
                        return "call"
                else:
                    time.sleep(min(0.05, time_left))
            else:
                # Unix: use select to check for input with timeout
                fd = sys.stdin.fileno()
                old_loop_settings = termios.tcgetattr(fd)
                try:
                    tty.setraw(fd)
                    new_loop_settings = termios.tcgetattr(fd)
                    new_loop_settings[3] |= termios.ECHO
                    termios.tcsetattr(fd, termios.TCSADRAIN, new_loop_settings)
                    remaining = deadline - time.time()
                    if remaining <= 0:
                        break
                    rlist, _, _ = select.select([sys.stdin], [], [], remaining)
                    if rlist:
                        next_char = sys.stdin.read(1)
                        if next_char.isdigit():
                            number.append(next_char)
                            deadline = time.time() + 0.9
                        else:
                            print('Invalid action')
                            return "call"
                    else:
                        break
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_loop_settings)
            if time.time() >= deadline:
                break
        return int(''.join(number))
    else:
        print('Invalid action')
        return "call"


# Always call
class TemplateBot(Bot):
    def act(self, state, hand):
        # print('asked to act')
        # print('acting', state, hand, self.my_id)


        os.system('clear')
        print(state)
        print(hand)

        print("Enter action: ")

        action = get_action()

        if action == "call":
            return { 'type': 'call' }
        elif action == "fold":
            return { 'type': 'fold' }
        elif action == "all":
            return { 'type': 'raise', 'amount': 1000000 }
        elif int(action) > 0:
            return { 'type': 'raise', 'amount': int(action) }
        else:
            print('Invalid action')
            return { 'type': 'call' }

        

    def opponent_action(self, action, player):
        #print('opponent action?', action, player)
        pass

    def game_over(self, payouts):
        global cnt
        #print('game over', payouts)
        cnt += 1
        # print(cnt)

    def start_game(self, my_id):
        self.my_id = my_id
        pass

if __name__ == "__main__":
    bot = TemplateBot("ws.turingpoker.com", "80", args.room, args.username)
    asyncio.run(bot.start())