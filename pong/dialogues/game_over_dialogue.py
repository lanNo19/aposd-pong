import sys
import turtle
from turtle import Screen
from typing import Callable, List

from pong.dialogues.idialogue import IDialogue
from pong.draw import Drawer


class GameOverDialogue(IDialogue):
    switch_callback: Callable
    options: List[str]
    selected_index: int
    winner: int
    screen: Screen
    drawer: Drawer

    def __init__(self, switch_callback: Callable, s: Screen, d: Drawer, w: 1|2):
        self.switch_callback = switch_callback
        self.screen = s
        self.options = ["Retry", "Quit"]
        self.selected_index = 0
        self.winner = w
        self.drawer = d

    def mount(self):
        turtle.listen()
        turtle.onkey(self._move_up, "Up")
        turtle.onkey(self._move_down, "Down")
        turtle.onkey(self._select, "Return")
        self.refresh()

    def unmount(self):
        turtle.onkey(None, "Up")
        turtle.onkey(None, "Down")
        turtle.onkey(None, "Return")
        self.drawer.clear_screen()

    def refresh(self):
        self.drawer.draw_menu(f"Player {self.winner} Won!", self.options, self.selected_index)

    def _move_up(self):
        self.selected_index = (self.selected_index - 1) % len(self.options)
        self.refresh()

    def _move_down(self):
        self.selected_index = (self.selected_index + 1) % len(self.options)
        self.refresh()

    def _select(self):
        s = self.options[self.selected_index]
        if s == "Retry":
            from pong.dialogues.game_dialogue import GameDialogue
            self.switch_callback(GameDialogue(self.switch_callback, self.screen, self.drawer))
        else:
            from pong.dialogues.main_menu_dialogue import MainMenuDialogue
            # Switch to MainMenuDialogue, passing necessary arguments
            self.switch_callback(MainMenuDialogue(self.switch_callback, self.screen, self.drawer))