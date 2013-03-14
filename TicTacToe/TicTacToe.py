class TicTacToeBoard:

    # Constructor for a TicTacToeBoard object
    def __init__(self, computer, human):
        self.board = ['N' for i in range(9)] # Initialize a board to all 'N'
        self.length = len(self.board) # The length (number of squares) on a board
        self.empties = [0, 1, 2, 3, 4, 5, 6, 7, 8] # Empty squares on a board
        self.move_stack = [] # Stack of previous moves
        self.computer = computer # Computer marker
        self.human = human # Human marker
        self.winner = 'N' # Current winner
                                      
    # PrintBoard : board -> void
    # Pretty-prints a board object
    def PrintBoard(self):
        for i in range(len(self.board)):
            if ((i + 1) % 3 == 0):
                if (self.board[i] == 'N'):
                    print (i + 1)
                else:
                    print (self.board[i])
            else:
                if (self.board[i] == 'N'): 
                    print (i + 1, end="")
                else:
                    print (self.board[i], end="")
                print ("|", end="")

    # play-square : board, index, value -> void 
    # Play a square on the board
    def play_square(self, index, val):
        self.board[index] = val
        self.empties.remove(index)
        # Add to the move stack
        self.move_stack.append(index)

    # pop_move_stack : board -> void
    # Pop a move off the previous moves stack
    def pop_move_stack(self):
        index = self.move_stack.pop()
        self.board[index] = 'N'
        self.empties.append(index)
        # Keep the empties index sorted
        self.empties.sort()
        # Undo any win position
        self.winner ='N'

    # get_square : board, index -> value
    # Get the value at a square on the board
    def get_square(self, index):
        return self.board[index]

    # check_winner : board -> boolean
    # Return the winner's symbol, or 'N' if there is no winner
    def check_winner(self):
        # Set of possible board win positions
        wins = [(0, 1, 2), (0, 3, 6), (0, 4, 8), (1, 4, 7),
                (2, 4, 6), (2, 5, 8), (3, 4, 5), (6, 7, 8)]

        # If a win position is reached, return true, and set the winner
        for i, j, k in wins:
            if ((self.board[i] == self.board[j] == self.board[k]) and self.board[i] != 'N'):
                self.winner = self.board[i]
                return True

        # If the board is complete with no winner, there is a cat game
        if (self.complete()):
            self.winner = 'N'
            return True

        # Otherwise, continue the game
        return False

    # complete : board -> boolean
    # Return whether the board is complete or not
    def complete(self):
        for i in range(self.length):
            if (self.board[i] == 'N'):
                return False
        return True

    # move : board -> void
    # make a move for the computer
    def move(self):
        # Call minimax
        move, score = self.maximize()
        self.play_square(move, self.computer)

    # maximize : board -> index, score
    # Maximize the board value for the computer player
    def maximize(self):
        score_max = None 
        move_max = None

        # Generate the board children
        for index in self.empties:
            self.play_square(index, self.computer)
            # Check to see if the game is over
            if (self.check_winner()):
                score = self.calculate_score()
            else:
                # If no win position is reached, minimize the human
                move, score = self.minimize()

            # Undo our changes
            self.pop_move_stack()

            # Set the score based on the recursive calls
            if (score_max == None or score > score_max):
                move_max = index
                score_max = score

        return move_max, score_max

    # minimize : board -> index, score
    # Minimize the board value for the human player
    def minimize(self):
        score_min = None
        move_min = None

        # Generate the board children
        for index in self.empties:
            self.play_square(index, self.human)
            # Check to see if the game is over
            if (self.check_winner()):
                score = self.calculate_score()
            else:
                # If no win position is reached, maximize the computer
                move, score = self.maximize()

            # Undo our changes
            self.pop_move_stack()

            # Set the score based on recursive calls
            if (score_min == None or score < score_min):
                move_min = index
                score_min = score

        return move_min, score_min
    
    # calculate_score : board -> score
    # Calculate the score of a complete board
    def calculate_score(self):
        if (self.check_winner()):
            if (self.winner == self.computer):
                return 1
            elif (self.winner == self.human):
                return -1
            else:
                return 0

# play : TicTacToeBoard -> TicTacToeBoard
def play(Game):
    # Count total moves so far
    moves = 0

    # If the computer moves first, simply play 'X'
    # in the upper-right-hand corner, which is the
    # best move (symmetrically)
    if (Game.computer == 'X'):
        Game.play_square(0, Game.computer)
        moves += 1

    # Print out our game board
    print()
    print("INITIAL GAME BOARD")
    Game.PrintBoard()
    print()
    
    # Main game loop
    while (moves < 9 and not Game.check_winner()):
        print("Your move. Please select an empty square on the board")
        test_input = input()

        # Validate user input
        try:
            index = int(test_input) - 1

            # Validate index
            if (index < 0 or index > 8 or Game.get_square(index) != 'N'):
                print("Invalid move, please enter an available move.")
                continue
            else:
                # Human move
                Game.play_square(index, Game.human)
                moves += 1
                if (Game.check_winner()):
                    break
                # CPU move
                else:
                    Game.PrintBoard()
                    print()
                    print("CPU Move")
                    Game.move()
                    Game.PrintBoard()
                    print()
                    moves += 1

        except ValueError:
            print("Please enter an integer index")

    # Print game results
    print()
    print("Game over.")
    Game.PrintBoard()
    if (Game.winner == 'N'):
        print("Cat game")
    elif (Game.winner == Game.human):
        print("You Win!")
    elif (Game.winner == Game.computer):
        print("CPU Wins!")

# Main function
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
                Game = TicTacToeBoard('O', 'X')
                play(Game)
            elif (player == 2):
                Game = TicTacToeBoard('X', 'O')
                play(Game)
            else:
                print ("Please enter either 1 or 2")
                test_input = -1

        except ValueError:
            print ("Please enter either 1 or 2")
            test_input = -1

if __name__ == '__main__':
    main()
