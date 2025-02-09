from itertools import combinations
from time import time

from .cards import *
from .game import *

from random import sample

class eval():
    def __init__(self, hand, board_cards):
        d = Deck()
        self.hand = [d.get(c) for c in hand]
        self.board_cards = [d.get(c) for c in board_cards]


    def hand_strength(self):
        '''Determine the hand strength of your current cards + cards on the board'''
        p1 = Player('player')
        p1.receive(self.hand)
        p1_rank = p1.handEval(self.board_cards)

        d = Deck(shuffle=False, bad_cards=self.hand + self.board_cards)
        
        win = tie = loss = 0
        for i, c1 in enumerate(d.deck):
            for c2 in d.deck[i+1:]:
                p2 = Player('opponent')
                p2.receive([c1, c2])
                p2_rank = p2.handEval(self.board_cards)

                if p1_rank > p2_rank:
                    win += 1
                elif p1_rank == p2_rank:
                    tie += 1
                else:
                    loss += 1
        
        # print(win, tie, loss)
        return (win + 0.5 * tie) / sum([win, tie, loss])
    
    @staticmethod
    def check_possible_flush(cards):
        suits = {}
        for card in cards:
            suits[card.suit] = suits.get(card.suit, 0) + 1

        return max([suit for suit in suits.values()]) >= 3

    def potential_hand_strength(self, only_ppot=False):
        start = 0
        '''Compute potential hand strength. look_ahead is an integer that specifies the number of cards to look ahead for. On turn, it should be one, and on flop, it should be 2.'''      
        look_ahead = 5 - len(self.board_cards)

        if look_ahead == 0:
            return self.hand_strength()

        p1 = Player('player')
        p2 = Player('opponent')

        p1.receive(self.hand)

        p1_rank_5 = p1.handEval(self.board_cards)
        flush_possible_p1 = eval.check_possible_flush(list(self.hand) + self.board_cards)

        d = Deck(shuffle=False, bad_cards=self.hand + self.board_cards)
        computed_p1_ranks = {}
        computed_p2_ranks = {}

        winning = [0, 0, 0]

        for p2_hand in sample(list(combinations(d.deck, 2)), len(list(combinations(d.deck, 2))) // 2):
            p2.clear_hand()
            p2.receive(list(p2_hand))

            p2_rank_5 = p2.handEval(self.board_cards)
            flush_possible_p2 = eval.check_possible_flush(list(p2_hand) + self.board_cards)

            if p1_rank_5 > p2_rank_5:
                if only_ppot: continue    # ppot does not need cases were we are winning
                
                i = 0           # We are ahead
            elif p1_rank_5 == p2_rank_5:
                i = 1           # We are tied
            else:
                i = 2           # We are behind

            new_d = Deck(shuffle=False, deck=d.deck, bad_cards=list(p2_hand))

            for new_board_cards in sample(list(combinations(new_d.deck, look_ahead)), len(list(combinations(new_d.deck, look_ahead))) // 2):
                predicted_board_cards = self.board_cards + list(new_board_cards)

                start_i = time()
                hash_p1 = Cards.hash_list(new_board_cards, flush_possible_p1)
                hash_p2 = Cards.hash_list(p2_hand + new_board_cards, flush_possible_p2)
                start += time() - start_i

                if hash_p1 in computed_p1_ranks:
                    p1_rank_7 = computed_p1_ranks[hash_p1]
                else:
                    p1_rank_7 = p1.handEval(predicted_board_cards)
                    computed_p1_ranks[hash_p1] = p1_rank_7

                if hash_p2 in computed_p2_ranks:
                    p2_rank_7 = computed_p2_ranks[hash_p2]
                else:
                    p2_rank_7 = p2.handEval(predicted_board_cards)
                    computed_p2_ranks[hash_p2] = p2_rank_7


                if p1_rank_7 > p2_rank_7:
                    winning[0] += 1
                elif p1_rank_7 == p2_rank_7:
                    winning[1] += 1
                else:
                    winning[2] += 1


        return (winning[0] + winning[1] * 0.5) / sum(winning)

if __name__ == "__main__":
    d = Deck()

    hand = ['As', '8h']
    board = ['Ad', 'Tc', '3c']

    e = eval(hand, board)

    print(e.hand_strength())

    start_ii = time()

    # print(e.potential_hand_strength(1))
    # print(e.potential_hand_strength(2, only_ppot=True))
    print(e.potential_hand_strength(2))


    print(time() - start_ii)
