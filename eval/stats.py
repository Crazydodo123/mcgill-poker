class Stats():
    def __init__(self):
        self.__stats = {}
        self.__moves = []

    def __repr__(self):
        return repr(self.__stats) + '\n' + repr(self.__moves)
    
    def __bool__(self):
        return len(self.__moves) != 0
    
    def __getitem__(self, arg):
        return self.__stats.get(arg, 0)
    
    def add_move(self, move, amount=0):
        self.__stats[move] = self.__stats.get(move, 0) + 1
        self.__moves.append((move, amount))

    def check_stat(self, move):
        return self.__stats.get(move, 0)
    
    def past_moves(self):
        return self.__moves
    
    def reset(self):
        self.__stats.clear()
        self.__moves.clear()
