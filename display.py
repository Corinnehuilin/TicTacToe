'''Python/Kivy tic-tac-toe widget'''

import random

from kivy.clock import Clock
from kivy.config import ConfigParser
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ListProperty
from kivy.properties import ObjectProperty
from kivy.uix.button import Button
from kivy.uix.label import Label

from game import Board, Players, Results
from game import Negamax as AI


class Bidict(dict):
    '''Bidict - each (key -> value) also exists as (value -> key)'''

    def __setitem__(self, key, value):
        # Remove any previous connections with these values
        if key in self:
            del self[key]
        if value in self:
            del self[value]
        dict.__setitem__(self, key, value)
        dict.__setitem__(self, value, key)

    def __delitem__(self, key):
        dict.__delitem__(self, self[key])
        dict.__delitem__(self, key)


class GridEntry(Button):
    '''Clickable tile for display of board'''
    coords = ListProperty([0, 0])
    release_callback = ObjectProperty(None)


class Message(Label):
    '''Message to user, displays across full area given

    Washes out everything behind while message is displayed
     so the message isn't covered up.
    '''

    screencover_color = ListProperty([1, 1, 1, 0])

    def display_message(self, message):
        '''Add message to board, fade board'''
        # Add screen cover
        self.screencover_color[3] = 0.4
        # Add win message
        self.color = 0.1, 0.05, 0, 0.9
        self.text = message

    def clear(self):
        '''Clear message from board, un-fade board'''
        # Remove screen cover
        self.screencover_color[3] = 0
        # Remove message text
        self.color = 0, 0, 0, 0


class Display(FloatLayout):
    '''Tic-tac-toe game display'''

    grid = ObjectProperty(None)
    message = ObjectProperty(None)
    previous = ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        super(Display, self).__init__(*args, **kwargs)

        # 1 and -1 are used to denote the players, 1 is the first player and -1 is the second
        #  player. This makes checking for a win very easy since a row/column/diagonal will add
        #  up to 3 or -3 if someone has won.
        self.player = Players.player_one

        self.config_parser = ConfigParser.get_configparser("app")

        self.game_over = True

        self.two_player = None
        self.human_player = None

        self.player_icons = Bidict()
        self.player_icons[Players.player_one] = "X"
        self.player_icons[Players.player_two] = "O"
        self.player_icons[Players.unplayed] = ""

        self.player_names = Bidict()
        self.player_names[Players.player_one] = "Player One"
        self.player_names[Players.player_two] = "Player Two"

        self.board = Board()

    def set_game_mode(self, two_player):
        '''Set whether the game is in one or two player mode

        If setting to one player mode, specify which player will be played by a human
        '''
        self.two_player = two_player
        if not self.two_player:
            self.human_player = Players.player_one if self.config_parser.get(
                'AI', 'ai_player') == "Second" else Players.player_two
            if self.human_player == Players.player_one:
                self.player_names[Players.player_one] = self.config_parser.get(
                    'Player Names', 'player_one_name')
                self.player_names[Players.player_two] = self.config_parser.get(
                    'AI', 'ai_name')
            else:
                self.player_names[Players.player_one] = self.config_parser.get(
                    'AI', 'ai_name')
                self.player_names[Players.player_two] = self.config_parser.get(
                    'Player Names', 'player_two_name')
        else:
            self.human_player = None
            self.player_names[Players.player_one] = self.config_parser.get(
                'Player Names', 'player_one_name')
            self.player_names[Players.player_two] = self.config_parser.get(
                'Player Names', 'player_two_name')
        self.reset()
        self.game_over = False
        self.previous.title = self.player_names[self.player]
        # If mode is one player and the human is playing as
        #  player two, the ai will make the first move
        if not self.two_player and self.human_player == Players.player_two:
            self._ai_make_move(0)

    def human_make_move(self, row, column):
        '''Make a move at the tile specified by row, column
        If the game is in one player mode, the AI will then make its move.'''
        if (self.two_player or
                self.player == self.human_player) and self._make_move(row, column):
            ai_move_delay = self.config_parser.get('AI', 'ai_move_delay')
            delay = 0
            if ai_move_delay == "Random":
                delay = random.triangular(0.1, 1.5, 0.3)
            elif ai_move_delay == "2 sec.":
                delay = 2.0
            Clock.schedule_once(self._ai_make_move, delay)

    def _ai_make_move(self, dt):
        '''Have the AI make its next move'''
        if not self.two_player:
            ai_move = AI.get_next_move(
                self.board, Players.other_player(self.human_player))
            if ai_move:
                ai_move_row, ai_move_columnn = ai_move
                self._make_move(ai_move_row, ai_move_columnn)

    def _make_move(self, row, column):
        '''Make a move at the tile specified by row, column'''
        if not self.game_over:
            # Update internal board state
            if self.board.make_move(row, column):
                # Display player's icon on tile
                self.grid.set_tile_icon(
                    row, column, self.player_icons[self.player])
                # Check for win
                win_status = self.board.check_for_win()
                return self._handle_move_results(win_status)
        return False

    def undo_move(self):
        '''Undo previous move

        Can be called multiple times, will only work while the game isn't over.
        If in one player mode, the ai's move, and the player's move will both be undone.
        '''
        if not self.game_over:
            if not self.two_player:
                # Undo ai's move
                self._undo_move()
            self._undo_move()

    def _undo_move(self):
        '''Internal method to undo the previous move'''
        # Remove move from internal board
        move = self.board.undo_move()
        # If there was a move to undo
        if move:
            row, column = move
            # Remove player's icon from tile
            self.grid.set_tile_icon(
                row, column, self.player_icons[Players.unplayed])
            # Return to previous turn
            self.player = Players.other_player(self.player)
            self.previous.title = self.player_names[self.player]

    def _handle_move_results(self, win_status):
        '''Handle the results of a move

        Based on the results of a move, end a game and display win/tie message or
         just advance to the next turn
        '''
        gameover, winner = win_status
        if gameover:
            self.game_over = True
            # Cat's game
            if winner == Results.tie:
                self.message.display_message("Cat's game!")
            else:
                self.grid.display_win(self.board.get_winning_streak())
                Clock.schedule_once(self._display_win_message, 0.3)
            return False
        # If no win, advance to next turn
        self.player = Players.other_player(self.player)
        self.previous.title = self.player_names[self.player]
        return True

    def _display_win_message(self, dt):
        '''Display a win message for the current player'''
        if self.two_player:
            self.message.display_message(
                self.player_names[self.player] + " has won!")
        elif self.human_player == self.player:
            self.message.display_message("You won!")
        else:
            self.message.display_message("You lost!")

    def restart(self):
        '''Restart game into the same gamemode, same players'''
        self.reset()
        self.game_over = False
        # If mode is one player and the human is playing as
        #  player two, the ai will make the first move
        if not self.two_player and self.human_player == Players.player_two:
            self._ai_make_move(0)

    def reset(self):
        '''Reset board to default state'''
        self.player = Players.player_one
        self.previous.title = self.player_names[self.player]
        self.game_over = True
        self.board.reset()
        self.grid.reset()
        self.message.clear()


class TicTacToeGrid(GridLayout):
    '''Kivy widget for the tic-tac-toe board'''

    tile_release_callback = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(TicTacToeGrid, self).__init__(**kwargs)

        self.display = []

        # Kivy properties set in kv lang are not populated until *after* init is finished,
        #  _init_ui is scheduled to run once the properites are populated
        Clock.schedule_once(self._init_ui)

    def _init_ui(self, dt):
        '''Second section of __init__, see comment in __init__'''
        # Initialize grid of buttons/tiles
        for row in range(3):
            grid_row = []
            for column in range(3):
                grid_entry = GridEntry(coords=(row, column),
                                       release_callback=self.tile_release_callback)
                self.add_widget(grid_entry)
                grid_row.append(grid_entry)
            self.display.append(grid_row)

    def set_tile_icon(self, row, column, icon):
        '''Display 'icon' on the specified tile'''
        self.display[row][column].text = icon

    def display_win(self, indices):
        '''Change the color of the winning streak to a bright green'''
        for coords in indices:
            for child in self.children:
                if tuple(child.coords) == coords:
                    child.color = 0, 0.6, 0, 0.6

    def reset(self):
        '''Reset board to default state'''
        for child in self.children:
            child.color = 0, 0, 0, 0.4
            child.text = ""
