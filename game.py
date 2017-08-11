'''Contains functionality for a tic tac toe game w/o any display
and a Negamax solving algorithm for an AI opponent
'''

from enum import Enum
import random


class Players(Enum):
    '''1 and -1 are used to denote the players, 1 is the first player and -1 is the second
    player. This makes checking for a win very easy since a row/column/diagonal will add
    up to 3 or -3 if someone has won.
    If someone has won, the total can be divided by 3 to get which player won.
    '''
    player_one = 1
    player_two = -1
    unplayed = 0

    @staticmethod
    def max_line_sum():
        '''Get the maximum number a row/column/diagonal will sum to'''
        return 3

    @staticmethod
    def other_player(current_player):
        '''Get the other player, given the current player

        Useful for advancing to the next turn, or reverting to a previous move
        '''
        if current_player == Players.unplayed:
            return NotImplemented
        is_player_one = (current_player == Players.player_one)
        return Players.player_two if is_player_one else Players.player_one


class Results(Enum):
    '''Represents the end of a game

    1 is a win for player one, -1 is a win for player 2, 0 is a tie
    '''
    player_one_win = 1
    player_two_win = -1
    tie = 0
    no_win = None


class Board:
    '''Tic-tac-toe game board'''

    def __init__(self):
        self._player = Players.player_one

        # List of moves played so undo button can be used
        self._moves = []

        # Internal rep of board
        self._board = [[Players.unplayed, Players.unplayed, Players.unplayed],
                       [Players.unplayed, Players.unplayed, Players.unplayed],
                       [Players.unplayed, Players.unplayed, Players.unplayed]]

    def make_move(self, row, column):
        '''Make a move at the tile specified by row, column

        return: True if successful, False if that tile has already been played
        '''
        if self._board[row][column] == Players.unplayed:
            # Update internal board state
            self._board[row][column] = self._player
            # Add move to list of moves
            self._moves.append((row, column))
            self._player = Players.other_player(self._player)
            return True
        return False

    def undo_move(self):
        '''Undo previous move

        Can be called multiple times
        '''
        if self._moves:
            row, column = self._moves.pop()
            # Remove move from internal board
            self._board[row][column] = Players.unplayed
            # Return to previous turn
            self._player = Players.other_player(self._player)
            return row, column
        return False

    def reset(self):
        '''Reset board to default state'''
        self._player = Players.player_one
        self._moves = []
        self._board = [[Players.unplayed, Players.unplayed, Players.unplayed],
                       [Players.unplayed, Players.unplayed, Players.unplayed],
                       [Players.unplayed, Players.unplayed, Players.unplayed]]

    def check_for_win(self):
        '''Returns tuple containing win status

        (gameover, winner)

        gameover: True if someone won/tied game, False otherwise
        winner: A Results object specifiying who won
        '''

        # Check rows and columns
        for i in range(3):
            column = self._board[0][i].value + \
                self._board[1][i].value + self._board[2][i].value
            row = self._board[i][0].value + \
                self._board[i][1].value + self._board[i][2].value

            if abs(column) == Players.max_line_sum():
                return True, Results(column / Players.max_line_sum())
            elif abs(row) == Players.max_line_sum():
                return True, Results(row / Players.max_line_sum())

        # Check diagonals
        top_to_bottom = self._board[0][0].value + \
            self._board[1][1].value + self._board[2][2].value
        bottom_to_top = self._board[2][0].value + \
            self._board[1][1].value + self._board[0][2].value
        if abs(top_to_bottom) == Players.max_line_sum():
            return True, Results(top_to_bottom / Players.max_line_sum())
        elif abs(bottom_to_top) == Players.max_line_sum():
            return True, Results(bottom_to_top / Players.max_line_sum())
        elif self._board_full():
            return True, Results.tie
        return False, Results.no_win

    def get_winning_streak(self):
        '''Returns zipped list of indices for the winning streak, empty list if no win found'''
        indices = [0, 1, 2]

        # Check rows and columns
        for i in range(3):
            column = self._board[0][i].value + \
                self._board[1][i].value + self._board[2][i].value
            row = self._board[i][0].value + \
                self._board[i][1].value + self._board[i][2].value

            indices2 = [i, i, i]

            if abs(column) == Players.max_line_sum():
                return zip(indices, indices2)
            elif abs(row) == Players.max_line_sum():
                return zip(indices2, indices)

        # Check diagonals
        top_to_bottom = self._board[0][0].value + \
            self._board[1][1].value + self._board[2][2].value
        bottom_to_top = self._board[2][0].value + \
            self._board[1][1].value + self._board[0][2].value
        if abs(top_to_bottom) == Players.max_line_sum():
            return zip(indices, indices)
        elif abs(bottom_to_top) == Players.max_line_sum():
            indices2 = indices[::-1]
            return zip(indices2, indices)
        return []

    def get_possible_moves(self):
        '''Returns a list of (row, column) moves available on the board'''
        possible_moves = []

        # Walk through board and record available moves
        for row in range(3):
            for column in range(3):
                if self._board[row][column] == Players.unplayed:
                    possible_moves.append((row, column))

        return possible_moves

    def _board_full(self):
        '''Return True if board is full, False otherwise'''
        # Flag for an empty square existing
        full = True
        for row in range(3):
            for column in range(3):
                if self._board[row][column] == Players.unplayed:
                    full = False
        return full

    def print_board(self):
        '''Print out visual rep of board to stdout'''
        for row in range(3):
            for column in range(3):
                tile_value = self._board[row][column].value
                if tile_value == 1:
                    print("X ", end='')
                elif tile_value == -1:
                    print("O ", end='')
                else:
                    print("  ", end='')
            print("", flush=True)
        print("", flush=True)


class NegamaxResults(Enum):
    '''Game results for the negamax algorithm, not used for other game results'''
    player = 1
    other_player = -1
    tie = 0
    # 'Negative infinity' option, less than all other allowed options
    worst = -100

    def __gt__(self, other):
        return self.value > other.value

    def __lt__(self, other):
        return self.value < other.value

    def __eq__(self, other):
        return self.value == other.value

    def __le__(self, other):
        return self.value <= other.value

    def __ge__(self, other):
        return self.value >= other.value

    def __neg__(self):
        if self == NegamaxResults.worst:
            return NotImplemented
        return NegamaxResults(-int(self.value))


class NegamaxPlayers(Enum):
    '''Players and values designed for negamax algorithm'''
    player = 1
    opponent = -1

    @staticmethod
    def other_player(current_player):
        '''Get the other player, given the current one'''
        is_player = (current_player == NegamaxPlayers.player)
        return NegamaxPlayers.opponent if is_player else NegamaxPlayers.player


class Negamax:
    '''Negamax implementation for two player tic-tac-toe

    Now with alpha-beta pruning!'''

    @staticmethod
    def get_next_move(board, player):
        '''Returns a (row, column) tuple containing the best move for the current player'''

        player = NegamaxPlayers(player.value)

        children = board.get_possible_moves()
        best_value = NegamaxResults.worst
        best_moves = []
        for child in children:
            row, column = child
            board.make_move(row, column)
            child_value, child_best_move = Negamax._negamax(
                board, NegamaxPlayers.other_player(player), NegamaxResults.other_player, NegamaxResults.player)
            child_value = -child_value
            if child_value > best_value:
                best_value = child_value
                best_moves = [child]
            elif child_value == best_value:
                best_moves.append(child)
            board.undo_move()

        # If more than one good move is available, randomly pick one
        if len(best_moves):
            return best_moves[random.randrange(len(best_moves))]
        print(best_moves)
        return best_moves[0]

    @staticmethod
    def _negamax(board, player, alpha, beta):
        '''Negamax for two-player tic-tac-toe'''
        # Get win status of the node
        (game_over, winner) = board.check_for_win()
        if game_over:
            result = NegamaxResults(winner.value * player.value)
            return (result, None)

        children = board.get_possible_moves()

        # Maximum value of child nodes
        best_value = NegamaxResults.worst
        best_move = None
        for child in children:
            row, column = child
            board.make_move(row, column)
            child_value, child_best_move = Negamax._negamax(
                board, NegamaxPlayers.other_player(player), -beta, -alpha)
            child_value = -child_value
            if child_value > best_value:
                best_value = child_value
                best_move = child
            alpha = max(alpha, child_value)
            board.undo_move()
            if alpha >= beta:
                break
        return best_value, best_move
