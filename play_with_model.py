from board import Board
from mcts import MonteCarlo

filename = "saved2"
count = 0
save_lap = 1
b = Board()
mcts = MonteCarlo(b, max_moves=100, time=100, C=1.5, randomness_percent = 0.8, filename=filename)

model_move = True

while(True):
    if(model_move):
        move = mcts.get_play()
        next_state = b.next_state(mcts.states[-1], move)
        mcts.update(next_state)

        b.print_state(mcts.states[-1])
        count += 1
        if(count % save_lap == 0):
            mcts.save(filename)
    else:
        move = input().split()
        move[0] = int(move[0])
        move[1] = int(move[1])
        next_state = b.next_state(mcts.states[-1], move)
        mcts.update(next_state)
        b.print_state(mcts.states[-1])

    model_move = not(model_move)
    winner = b.winner(mcts.states)
    if(winner != -1):
        if(winner == b.red):
            print("Red wins")
        else:
            print("Green wins")
        break