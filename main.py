from board import Board
from mcts import MonteCarlo

filename = "saved2"
lap = 0
while(True):
    count = 0
    save_lap = 5
    stop = 100
    b = Board()
    mcts = MonteCarlo(b, max_moves=100, time=100, C=3, filename=filename, randomness_percent=0.7, nn_size=[25+1, 50, 50, 50, 50, 50, 50, 1])

    while(True):
        move = mcts.get_play()
        next_state = b.next_state(mcts.states[-1], move)
        mcts.update(next_state)

        winner = b.winner(mcts.states)
        b.print_state(mcts.states[-1])
        count += 1
        if(count % save_lap == 0):
            mcts.save(filename)

        if(winner != -1):
            if(winner == b.red):
                print("Red wins")
            else:
                print("Green wins")
            break
        if(count > stop):
            break

    mcts.save(filename)
    print("Lap:", lap, "----------------------------------------------")
    lap += 1