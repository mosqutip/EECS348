import struct, string
from copy import deepcopy
from time import time

class OthelloBoard:

    def __init__(self, h, c, hmarker, cmarker):
        self.board = ([0] * 8, [0] * 8, [0] * 8, [0] * 8,
                      [0] * 8, [0] * 8, [0] * 8, [0] * 8)
        self.size = 8
        self.board[4][4] = 1
        self.board[3][4] = -1
        self.board[3][3] = 1
        self.board[4][3] = -1
        self.directions = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
        self.player = 0
        self.opp = 0
        self.human = h
        self.computer = c
        self.human_marker = hmarker
        self.comp_marker = cmarker
        
    # swap player/opponent variables (for min/max value calculations)
    def swap(self):
        self.player *= -1
        self.opp *= -1
        self.human *= -1
        self.computer *= -1
        human_marker = self.human_marker
        self.human_marker = self.comp_marker
        self.comp_marker = human_marker
        return self
    
    #calculates minimax values (with alpha-beta pruning) and uses a heuristic (if provided)
    def alphabeta_score(self, orig_time, max_plies, alpha, beta, heur = None):
        self = self.swap()

        if (max_plies == 0 or (time() - orig_time >= 20) or
                self.has_move(self.player, self.opp) == False): 
            if (heur != None):
                return self.heuristic()
            else:
                return self.score()

        possible_moves = self.get_moves(self.player, self.opp)
        for move in possible_moves:
            temp_board = deepcopy(self)
            temp_board.play_square(move[1], move[0], self.player, self.opp)


            if (beta is not None):
                optimal_alpha = -1 * beta
            else:
                optimal_alpha = None

            if (alpha is not None):
                optimal_beta = -1 * alpha
            else:
                optimal_beta = None

            optimal = -1 * temp_board.alphabeta_score(orig_time, max_plies - 1, optimal_alpha, optimal_beta, heur)

            if (alpha is None or optimal > alpha):
                alpha = optimal

            if ((alpha is not None) and (beta is not None) and (alpha >= beta)):
                return beta

        return alpha

    # finds the best move using minimax with alpha-beta pruning (and an optional heuristic)
    def alphabeta(self, orig_time, max_plies, heur = None):
        score_max = None
        move_max = None

        possible_moves = self.get_moves(self.player, self.opp)
        for move in possible_moves:
            temp_board = deepcopy(self)
            temp_board.play_square(move[1], move[0], self.player, self.opp)
            if (score_max is not None):
                optimal_beta = -1 * score_max
            else:
                optimal_beta = None

            optimal = -1 * temp_board.alphabeta_score(orig_time, max_plies, None, optimal_beta, heur)
            if (score_max is None or optimal > score_max):
                (score_max, move_max) = (optimal, move)

            if (time() - orig_time >= 20):
                break

        return (score_max, move_max)

    #prints the board
    def PrintBoard(self):

        print("  0 1 2 3 4 5 6 7")
        line_str = " "

        for j in range(self.size):
            line_str = line_str + "+-"

        line_str = line_str + "+"

        for i in range(self.size):
            piece_str = str(i) + "|"
            print(line_str)
            for k in range(self.size):
                if (self.board[i][k] == 0):
                    char = ' '
                elif (self.board[i][k] == 1):
                    char = 'B'
                elif (self.board[i][k] == -1):
                    char = 'W'
                piece_str = piece_str + char + "|"
            print(piece_str)
        print(line_str)

    def board_full(self):
        for i in range(self.size):
            for j in range(self.size):
                if self.get_square(j, i) == 0:
                    return False
        return True

    #determines the score of the board by adding +1 for every tile owned by player, and -1 for every tile owned by opp
    def score(self):
        score = 0
        for i in range(self.size):
            for j in range(self.size):
                score += self.get_square(j, i)
        return score * self.player

    def final_score(self):
        score = 0
        for i in range(self.size):
            for j in range(self.size):
                score += self.get_square(j, i)
        return score

    #returns true if the square was played, false if the move is not allowed
    def play_square(self, col, row, player, opp):
        if (self.get_square(col, row) != 0):
            return False
        
        if (player == opp):
            print("player and opponent cannot be the same")
            return False

        legal = False
        #for each direction, check to see if the move is legal by seeing if the adjacent square
        #in that direction is occuipied by the opponent. If it isnt check the next direction.
        #if it is, check to see if one of the players pieces is on the board beyond the oppponent's piece,
        #if the chain of opponent's pieces is flanked on both ends by the players pieces, flip
        #the opponent's pieces 
        for Dir in self.directions:
            #look across the length of the board to see if the neighboring squares are empty,
            #held by the player, or held by the opponent
            for i in range(self.size):
                if  (((row + i * Dir[0]) < self.size)  and ((row + i * Dir[0]) >= 0) and
                        ((col + i * Dir[1]) >= 0) and ((col + i * Dir[1]) < self.size)):
                    #does the adjacent square in direction dir belong to the opponent?
                    if self.get_square(col + i * Dir[1], row + i * Dir[0]) != opp and i == 1:
                        #no pieces will be flipped in this direction, so skip it
                        break
                    #yes the adjacent piece belonged to the opponent, now lets see if there are a chain
                    #of opponent pieces
                    if self.get_square(col + i * Dir[1], row + i * Dir[0]) == 0 and i != 0:
                        break

                    #with one of player's pieces at the other end
                    if self.get_square(col + i * Dir[1], row + i * Dir[0]) == player and i != 0 and i != 1:
                        #set a flag so we know that the move was legal
                        legal = True
                        self.flip_tiles(row, col, Dir, i, player)
                        break
                        
        return legal

# Sets all tiles along a given direction (Dir) from a given starting point (col and row) for a given distance
# (dist) to be a given value ( player )
    def flip_tiles(self, row, col, Dir, dist, player):
        for i in range(dist):
            self.board[row+ i*Dir[0]][col + i*Dir[1]] = player
        return True
    
# Returns the value of a square on the board
    def get_square(self, col, row):
        return self.board[row][col]

# Checks all board positions to see if there is a legal move
    def has_move(self, player, opp):
        for i in range(self.size):
            for j in range(self.size):
                if self.islegal(j, i, player, opp):
                    return True
        return False

    def get_moves(self, player, opp):
        moves = []
        for i in range(self.size):
            for j in range(self.size):
                if self.islegal(j, i, player, opp):
                    moves.append((i, j))
        return moves

#checks every direction from the position which is input via "col" and "row", to see if there is an opponent piece
#in one of the directions. If the input position is adjacent to an opponents piece, this function looks to see if there is a
#a chain of opponent pieces in that direction, which ends with one of the players pieces.    
    def islegal(self, col, row, player, opp):
        if(self.get_square(col, row) != 0):
            return False
        for Dir in self.directions:
            for i in range(self.size):
                if (((row + i * Dir[0]) < self.size)  and ((row + i * Dir[0]) >= 0) and
                        ((col + i * Dir[1]) >= 0) and ((col + i * Dir[1]) < self.size)):
                    #does the adjacent square in direction dir belong to the opponent?
                    if self.get_square(col + i * Dir[1], row + i * Dir[0]) != opp and i == 1:
                        #no pieces will be flipped in this direction, so skip it
                        break
                    #yes the adjacent piece belonged to the opponent, now lets see if there are a chain
                    #of opponent pieces
                    if self.get_square(col + i * Dir[1], row + i * Dir[0]) == 0 and i != 0:
                        break

                    # With one of player's pieces at the other end
                    if self.get_square(col + i * Dir[1], row + i * Dir[0]) == player and i != 0 and i != 1:
                        # Set a flag so we know that the move was legal
                        return True
        return False

# Returns true if no square in the board contains 0, false otherwise
    def full_board(self):
        for i in range(self.size):
            for j in range(self.size):
                if(self.board[i][j] == 0):
                    return False

        return True
    
# Checks to see if the given player controls the entire board
    def all_pieces(self, player):
        for i in range(self.size):
            for j in range(self.size):
                if(self.get_square(j, i) != player and self.get_square(j, i) != 0):
                    return False
        return True
                   
    # Check to see if the game is over
    def game_over(self):
        if (self.full_board() or self.all_pieces(self.player)):
            return True
        return False

    # Utilize an edge-play heuristic
    def heuristic(self):
        if (self.game_over()):
            score = self.score()
            if (score > 0):
                return 1000000
            elif (score < 0):
                return -1000000
            else:
                return 0

        opponent = -1 * self.player
        score = 0
        for i in range(self.size):
            for j in range(self.size):
                heur = 1
                if (i == 0 or i == (self.size - 1)):
                    heur += 5
                if (j == 0 or j == (self.size - 1)):
                    heur += 5
                if (i == 1 or i == (self.size - 2)):
                     heur -= 5
                if (j == 1 or j == (self.size - 2)):
                    heur -= 5

#                if ((i == 0 or i == (self.size - 1)) and
#                        (j == 0 or j == (self.size - 1))):
#                    heur += 49
#                if (i == 1 and j == 1):
#                    if (self.get_square(0, 0) == self.player):
#                        heur += 1
#                    else:
#                        heur -= 11
#                if (i == (self.size - 2) and j == 1):
#                    if (self.get_square((self.size - 1), 0) == self.player):
#                        heur += 1
#                    else:
#                        heur -= 11
#                if (i == 1 and j == (self.size - 2)):
#                    if (self.get_square(0, (self.size - 1)) == self.player):
#                        heur += 1
#                    else:
#                        heur -= 11
#                if (i == (self.size - 2) and j == (self.size - 2)):
#                    if (self.get_square((self.size - 1), (self.size - 1)) == self.player):
#                        heur += 1
#                    else:
#                        heur -= 11
#                if ((i == 1 or i == (self.size - 2)) and
#                        (j == 0 or j == (self.size - 1))):
#                    heur -= 2
#                if ((i == 0 or i == (self.size - 1)) and
#                        (j == 1 or j == (self.size - 2))):
#                    heur -= 2
#                if ((i == 2 or i == (self.size - 3)) and
#                        (j == 0 or j == (self.size - 1))):
#                    heur += 4
#                if ((i == 0 or i == (self.size - 1)) and
#                        (j == 2 or j == (self.size - 3))):
#                    heur += 4

                if self.board[i][j] == self.player:
                    score += heur
#                    print ("adding this score")
#                    print (i, j)
                elif self.board[i][j] == self.opp:
                    score -= heur
#                    print ("subtracting this score")
#                    print (i, j)

        return score

# make a cpu move, in this case, using minimax with alpha/beta and an edge-play heuristic
def make_cpu_move(board, t):
    score, move = board.alphabeta(t, 8, lambda: heuristic)
    board.play_square(move[1], move[0], board.player, board.opp)
    print("CPU played row: " + str(move[0]) + " col: " + str(move[1]) + ", which had a score of " + str(score))

# main play-loop for the game
def play(h, c, hmarker, cmarker, p, o):

    b = OthelloBoard(h, c, hmarker, cmarker)
    b.PrintBoard()

    Human = h
    CPU = c
    b.player = p
    b.opp = o

    #alternate between human's turn and CPU turn. if theres is no available move for one of the players, then
    #it becomes their opponent's turn again.
    #if the board is full, the winner is announced
    while (b.full_board() == False):
        print("Current scoring: " + str(b.score()))
        if (b.player == Human):
            if b.all_pieces(b.player):
                break
            if(b.has_move(b.player, b.opp)):
                humanmoved = False
                while not humanmoved:
                    print("Player: " + hmarker)
                    print("Pick a row index:", end=" ")
                    try:
                        row = int(input())
                        print("Pick a column index:", end=" ")
                        col = int(input())
                        if (row < 0 or row > 7):
                            print ("Invalid row index. Please enter a valid index")
                            continue
                        if (col < 0 or col > 7):
                            print ("Invalid column index. Please enter a valid index")
                            continue
                        if (b.play_square(col, row, b.player, b.opp)):
                            b.PrintBoard()
                            b.player = CPU
                            b.opp = Human
                            #print("done with human move")
                            humanmoved = True
                    except ValueError:
                        print ("Invalid indices. Please enter valid indices.")
                        continue
            else:
                print("no move")
                b.player = CPU
                b.opp = Human
                continue

        elif (b.player == CPU):
            #print("start CPU turn")
            start_time = time()
            if b.all_pieces(b.player):
                break
            if(b.has_move(b.player, b.opp)):
                print("CPU's move")
                make_cpu_move(b, start_time)
                b.PrintBoard()
                b.player = Human
                b.opp = CPU
            else:
                print("no move")
                b.player = Human
                b.opp = CPU
                continue

    if (b.human == 1):
        if(b.final_score() > 0):
            print ("Congratulations, you win!")
        elif(b.final_score() == 0):
            print ("The game is a draw.")
        else:
            print ("The computer wins!")
    elif (b.human == -1):
        if(b.final_score() > 0):
            print ("The computer wins!")
        elif(b.final_score() == 0):
            print ("The game is a draw.")
        else:
            print ("Congratulations, you win!")

def main():
    test_input = -1

    # Validate user input
    while (test_input == -1):
        print("Please enter which player you would like to be, either 1 or 2: ", end="")
        test_input = input()

        # Setup game based on user choice
        try:
            player = int(test_input)
            if (player == 1):
                Human = 1
                CPU = -1
                Human_char = 'B'
                CPU_char = 'W'
                player = Human
                opp = CPU
                play(Human, CPU, Human_char, CPU_char, player, opp)
            elif (player == 2):
                Human = -1
                CPU = 1
                Human_char = 'W'
                CPU_char = 'B'
                player = CPU
                opp = Human
                play(Human, CPU, CPU_char, Human_char, player, opp) #play(Human, CPU, CPU_char, Human_char, player, opp)
            else:
                print ("Please enter either 1 or 2")
                test_input = -1

        except ValueError:
            print ("Please enter either 1 or 2")
            test_input = -1

if __name__ == '__main__':
    main()

