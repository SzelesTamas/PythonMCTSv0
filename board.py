# state: (tuple(25), player)
# move: (from, to)
from random import choice


class Board(object):
    def start(self):
        # Returns a representation of the starting state of the game.
        self.red = 1
        self.green = 2

        self.board = []
        for i in range(25):
            self.board.append(0)
        
        r = [4, 5, 14, 15, 22, 24]
        g = [0, 2, 9, 10, 19, 20]
        for pos in r:
            self.board[pos] = self.red
        for pos in g:
            self.board[pos] = self.green
        return (tuple(self.board), self.green)


    def current_player(self, state):
        # Takes the game state and returns the current player's
        # number.
        return state[1]

    def next_state(self, state, play):
        # Takes the game state, and the move to be applied.
        # Returns the new game state.
        board = list(state[0])
        player = state[1]

        board[play[0]], board[play[1]] = board[play[1]], board[play[0]]

        if(player == self.red):
            player = self.green
        else:
            player = self.red
        return (tuple(board), player)

    def ind_to_pos(self, ind):
        return (ind % 5, int(ind / 5))
    
    def pos_to_ind(self, pos):
        return pos[1]*5 + pos[0]

    def legal_plays(self, state_history):
        # Takes a sequence of game states representing the full
        # game history, and returns the full list of moves that
        # are legal plays for the current player.
        board = list(state_history[-1][0])
        curr_player = state_history[-1][1]

        legal = []
        if(curr_player == self.red):
            next_player = self.green
        else:
            next_player = self.red

        x_move = [-1, 0, 1, 1, 1, 0, -1, -1]
        y_move = [1, 1, 1, 0, -1, -1, -1, 0]
        for ind in range(25):
            if(board[ind] != next_player):
                continue
            pos = self.ind_to_pos(ind)
            for i in range(8):
                new_pos = (pos[0] + x_move[i], pos[1] + y_move[i])
                if(new_pos[0] < 0 or new_pos[0] >= 5):
                    continue
                if(new_pos[1] < 0 or new_pos[1] >= 5):
                    continue

                new_ind = self.pos_to_ind(new_pos)
                if(board[new_ind] != 0):
                    continue
                
                next_state = self.next_state(state_history[-1], (ind, new_ind))
                if(not(next_state in state_history)):
                    legal.append((ind, new_ind))

        return legal

    def print_state(self, state):
        if(state[1] == self.red):
            print("Green to move")
        else:
            print("Red to move")
        board = list(state[0])
        for row in range(4, -1, -1):
            print("|", end="")
            for column in range(5):
                ind = self.pos_to_ind((column, row))
                if(board[ind] == 0):
                    print(" ", end="|")
                elif(board[ind] == self.red):
                    print("R", end="|")
                else:
                    print("G", end="|")
            print()

    def check_direction(self, board, start, direction):
        ind = self.pos_to_ind(start)
        color = board[ind]
        if(color == 0):
            return False
        start = list(start)

        for i in range(3):
            start[0] += direction[0]
            start[1] += direction[1]
            if(start[0] < 0 or start[0] >= 5):
                return False
            if(start[1] < 0 or start[1] >= 5):
                return False
            new_ind = self.pos_to_ind(start)
            if(board[new_ind] != color):
                return False
        return True

    def winner(self, state_history):
        # Takes a sequence of game states representing the full
        # game history.  If the game is now won, return the player
        # number.  If the game is still ongoing, return zero.  If
        # the game is tied, return a different distinct value, e.g. -1.
        state = state_history[-1]
        board = list(state[0])
        winner = -1
        directions = ((-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0))
        for row in range(5):
            for column in range(5):
                ind = self.pos_to_ind((column, row))
                color = board[ind]
                for direction in directions:
                    if(self.check_direction(board, (column, row), direction)):
                        winner = color
                
        return winner

'''
b = Board()
states = []
states.append(b.start())
while(True):
    legal = b.legal_plays(states)
    move = choice(legal)
    states.append(b.next_state(states[-1], move))
    winner = b.winner(states)
    if(winner != -1):
        
        break

#states.append(b.next_state(states[0], (0, 6)))

count = 0
for state in states:
    b.print_state(state)
    print("Move: ", count, " ----------------------------")
    count += 1

if(winner == b.red):
    print("Red wins")
else:
    print("Green wins")
'''