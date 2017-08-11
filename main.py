'''Kivy app for playing tic-tac-toe

Includes simple GUI, standard two player mode
and one player mode against the computer'''

from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.settings import SettingsWithSidebar
from kivy.uix.settings import SettingsWithTabbedPanel
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import ObjectProperty

from game import Players


class MenuScreen(Screen):
    '''Main menu screen

    Select play mode, play game, set options
    '''

    game = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)
        Clock.schedule_once(self._init_game)

    def _init_game(self, dt):
        self.game = self.manager.get_screen('GameScreen').game

    def one_player(self):
        '''Start tic-tac-toe game in one player mode'''
        self.game.reset()
        self.game.set_game_mode(False)
        self.manager.current = 'GameScreen'

    def two_player(self):
        '''Start tic-tac-toe game in two player mode'''
        self.game.reset()
        self.game.set_game_mode(True)
        self.manager.current = 'GameScreen'


class GameScreen(Screen):
    '''Game-playing screen

    Tic-tac-toe game with actionbar menu
    '''

    game = ObjectProperty(None)

    def restart(self):
        '''Restart into same game mode'''
        self.game.restart()

    def menu(self):
        '''New game, select new mode'''
        self.manager.current = 'MenuScreen'

    def undo_move(self):
        '''Undo previous moves, can be called multiple time'''
        self.game.undo_move()


class TicTacToeApp(App):
    '''Tic-tac-toe app using Kivy'''

    def build(self):
        Window.clearcolor = (0.688, 0.664, 0.640, 1)
        self.icon = 'resources/icon.ico'

        self.use_kivy_settings = False

        return self.root

    def on_pause(self):
        return True

    def on_resume(self):
        pass

    def build_config(self, config):
        """
        Set the default values for the configs sections.
        """
        config.setdefaults('Player Names', {'player_one_name': 'Player One',
                                            'player_two_name': 'Player Two', })
        config.setdefaults(
            'AI', {'ai_name': 'HAL 9000', 'ai_icon': 'X', "ai_player": "Second",
                   'ai_move_delay': 'Random'})

    def build_settings(self, settings):
        """
        Add our custom section to the default configuration object.
        """
        settings.add_json_panel(
            'Player Settings', self.config, 'resources/settings.json')


if __name__ == "__main__":
    TicTacToeApp().run()
