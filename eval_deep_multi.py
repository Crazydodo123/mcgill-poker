from itertools import combinations
from time import time
from multiprocessing import Pool, cpu_count, freeze_support

from cards import Deck, Cards
from game import Player

class eval():
    def __init__(self, hand, board_cards):
        self.hand = hand
        self.board_cards = board_cards

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
        
        return (win + 0.5 * tie) / sum([win, tie, loss])
    
    @staticmethod
    def check_possible_flush(cards):
        suits = {}
        for card in cards:
            suits[card.suit] = suits.get(card.suit, 0) + 1

        return max([suit for suit in suits.values()]) >= 3

    @staticmethod
    def process_p2_hand(args):
        '''Process a single opponent hand and compute its contribution to hand potentials.'''
        # Unpack all arguments
        p2_hand, p1, p1_rank_5, flush_possible_p1, board_cards, look_ahead, computed_p1_ranks, computed_p2_ranks, deck = args
        
        local_hand_potentials = [[0] * 3 for _ in range(3)]
        p2 = Player('opponent')
        p2.clear_hand()
        p2.receive(list(p2_hand))

        p2_rank_5 = p2.handEval(board_cards)
        flush_possible_p2 = eval.check_possible_flush(list(p2_hand) + board_cards)

        if p1_rank_5 > p2_rank_5:
            i = 0  # We are ahead
        elif p1_rank_5 == p2_rank_5:
            i = 1  # We are tied
        else:
            i = 2  # We are behind

        new_d = Deck(shuffle=False, deck=deck, bad_cards=list(p2_hand))

        for new_board_cards in combinations(new_d.deck, look_ahead):
            predicted_board_cards = board_cards + list(new_board_cards)

            hash_p1 = Cards.hash_list(new_board_cards, flush_possible_p1)
            hash_p2 = Cards.hash_list(p2_hand + new_board_cards, flush_possible_p2)

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
                local_hand_potentials[i][0] += 1
            elif p1_rank_7 == p2_rank_7:
                local_hand_potentials[i][1] += 1
            else:
                local_hand_potentials[i][2] += 1

        return local_hand_potentials

    def potential_hand_strength(self, look_ahead):
        '''Compute potential hand strength and return a single winning percentage.'''
        hand_potentials = [[0] * 3 for _ in range(3)]
        
        p1 = Player('player')
        p1.receive(self.hand)

        p1_rank_5 = p1.handEval(self.board_cards)
        flush_possible_p1 = eval.check_possible_flush(list(self.hand) + self.board_cards)

        d = Deck(shuffle=False, bad_cards=self.hand + self.board_cards)
        computed_p1_ranks = {}
        computed_p2_ranks = {}

        p2_hands = list(combinations(d.deck, 2))
        args = [
            (p2_hand, p1, p1_rank_5, flush_possible_p1, self.board_cards, look_ahead, computed_p1_ranks, computed_p2_ranks, d.deck)
            for p2_hand in p2_hands
        ]

        with Pool(cpu_count()) as pool:
            results = pool.map(self.process_p2_hand, args)

        for result in results:
            for i in range(3):
                for j in range(3):
                    hand_potentials[i][j] += result[i][j]

        # Calculate total scenarios
        total_scenarios = sum([sum(row) for row in hand_potentials])

        # Calculate winning percentage
        if total_scenarios == 0:
            return 0.0  # Avoid division by zero

        # Weighted winning percentage
        winning_percentage = (
            (hand_potentials[0][0] + 0.5 * hand_potentials[0][1]) +  # Ahead scenarios
            (hand_potentials[2][0] + 0.5 * hand_potentials[2][1])    # Behind scenarios (ppot)
        ) / total_scenarios

        return winning_percentage


def main():
    d = Deck()

    hand = [d.get('7h'), d.get('9h')]
    board = [d.get('8h'), d.get('6c'), d.get('4h')]

    e = eval(hand, board)

    print(e.hand_strength())

    start_ii = time()

    print(e.potential_hand_strength(2))

    print(time() - start_ii)


if __name__ == "__main__":
    freeze_support()
    main()