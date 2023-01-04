from __future__ import division
import datetime
from random import choice, randint, random
from math import log, sqrt
from os.path import exists
import tensorflow as tf
import numpy as np

class MonteCarlo(object):
    def __init__(self, board, **kwargs):
        # Takes an instance of a Board and optionally some keyword
        # arguments.  Initializes the list of game states and the
        # statistics tables.
        self.board = board
        self.states = []
        self.states.append(board.start())

        self.debug = True

        seconds = kwargs.get('time', 2)
        self.calculation_time = datetime.timedelta(seconds=seconds)

        self.max_moves = kwargs.get('max_moves', 100)

        self.C = kwargs.get('C', 1.4)

        self.wins = {}
        self.plays = {}

        self.randomness_percent = kwargs.get('randomness_percent', 0.2)

        filename = kwargs.get('filename', "none")
        txt_file = filename + ".txt"
        if(exists(txt_file)):
            file = open(txt_file, 'r')
            for line in file.readlines():
                p1, board, p2, win, play = line.split("|")
                win = int(win)
                play = int(play)
                p1 = int(p1)
                board = board[1:-1].split(",")
                for i in range(len(board)):
                    board[i] = int(board[i])
                board = tuple(board)
                p2 = int(p2)

                key = (p1, (board, p2))
                self.wins[key] = win
                self.plays[key] = play
            print("Successful readin")
        if(exists(filename)):
            self.model = tf.keras.models.load_model(filename)
            print("Model loaded")
        else:
            sizes = kwargs.get('nn_size', [25+1, 100, 1])
            self.model = tf.keras.Sequential()
            self.model.add(tf.keras.layers.Input(shape=(sizes[0],)))
            for i in range(1, len(sizes)-1):
                self.model.add(tf.keras.layers.Dense(sizes[i], activation='relu'))
            self.model.add(tf.keras.layers.Dense(sizes[-1], activation='sigmoid'))
            self.model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy', 'mae', 'mse'])

    def update(self, state):
        # Takes a game state, and appends it to the history.
        self.states.append(state)

    def get_play(self):
        # Causes the AI to calculate the best move from the
        # current game state and return it.
        self.max_depth = 0
        state = self.states[-1]
        player = self.board.current_player(state)
        legal = self.board.legal_plays(self.states[:])

        if(not legal):
            return
        if(len(legal) == 1):
            return legal[0]

        games = 0
        begin = datetime.datetime.utcnow()
        while(datetime.datetime.utcnow() - begin < self.calculation_time):
            self.run_simulation()
            games += 1

        moves_states = [(p, self.board.next_state(state, p)) for p in legal]

        if(self.debug):
            # Display the number of calls of `run_simulation` and the
            # time elapsed.
            print(games, datetime.datetime.utcnow() - begin)

        # Pick the move with the highest percentage of wins.
        percent_wins, move = max(
            (self.wins.get((player, S), 0) / self.plays.get((player, S), 1), p)
            for p, S in moves_states
        )
        percentages = [(self.wins.get((player, S), 0) / self.plays.get((player, S), 1))
            for p, S in moves_states]
        states = [(S) for p, S in moves_states]
        

        self.train_model(states, percentages)

        if(self.debug):
            # Display the stats for each possible play.
            for x in sorted(
                ((100 * self.wins.get((player, S), 0) / self.plays.get((player, S), 1),
                self.wins.get((player, S), 0),
                self.plays.get((player, S), 0), p)
                for p, S in moves_states),
                reverse=True
            ):
                print("{3}: {0:.2f}% ({1} / {2})".format(*x))

            print("Maximum depth searched:", self.max_depth)

        return move

    def run_simulation(self):

        # Plays out a "random" game from the current position,
        # then updates the statistics tables with the result.
        plays, wins = self.plays, self.wins

        states_copy = self.states[:]
        state = states_copy[-1]
        visited_states = set()
        player = self.board.current_player(state)

        expand = True
        for t in range(1, self.max_moves+1):
            legal = self.board.legal_plays(states_copy)
            moves_states = [(p, self.board.next_state(state, p)) for p in legal]

            if all(plays.get((player, S)) for p, S in moves_states):
                # If we have stats on all of the legal moves here, use them.
                log_total = log(
                    sum(plays[(player, S)] for p, S in moves_states))
                value, move, state = max(
                    ((wins[(player, S)] / plays[(player, S)]) +
                     self.C * sqrt(log_total / plays[(player, S)]), p, S)
                    for p, S in moves_states
                )
            else:
                # Otherwise, just make an arbitrary decision.
                rand = random()
                if(rand <= self.randomness_percent):
                    move, state = choice(moves_states)
                else:
                    move, state = self.make_model_choice(moves_states)

            states_copy.append(state)

            # `player` here and below refers to the player
            # who moved into that particular state.
            # adding a new node
            if(expand and (player, state) not in self.plays):
                expand = False
                plays[(player, state)] = 0
                wins[(player, state)] = 0
                if(t > self.max_depth):
                    self.max_depth = t

            visited_states.add((player, state))

            player = self.board.current_player(state)
            winner = self.board.winner(states_copy)
            if(winner != -1):
                if(winner == 2):
                    winner = 1
                else:
                    winner = 2
                break
        
        for player, state in visited_states:
            if((player, state) not in self.plays):
                continue
            self.plays[(player, state)] += 1
            if(player == winner):
                self.wins[(player, state)] += 1

    def save(self, filename):
        file = open(filename+".txt", 'w')
        for key in self.wins:
            to_write = str(key[0]) + "|" + str(key[1][0]) + "|" + str(key[1][1]) + "|" + str(self.wins[key]) + "|" + str(self.plays[key]) + "\n"
            file.write(to_write)
        file.close()
        self.model.save(filename)

    def make_model_choice(self, moves_states):
        inputs = [S for p, S in moves_states]
        for i in range(len(inputs)):
            temp = list(inputs[i][0])
            temp.append(inputs[i][1])
            inputs[i] = np.array(temp)
        inputs = np.array(inputs)
        outputs = self.model.predict(inputs, verbose=0)
        ind = randint(0, int(len(inputs) * self.randomness_percent))
        move_rank = []
        for i in range(len(inputs)):
            move_rank.append((outputs[i][0], moves_states[i]))
        move_rank = sorted(move_rank, reverse=True)
        move_state = move_rank[ind][1]
        return move_state
        

    def train_model(self, states, percentages):
        for i in range(len(states)):
            temp = list(states[i][0])
            temp.append(states[i][1])
            states[i] = np.array(temp)
        states = np.array(states)
        percentages = np.array(percentages)

        self.model.train_on_batch(states, percentages)