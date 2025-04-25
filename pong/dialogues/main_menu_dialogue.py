import sys
import turtle
from turtle import Screen
from typing import Callable, List

from pong.dialogues.game_dialogue import GameDialogue
from pong.dialogues.idialogue import IDialogue
from pong.draw import Drawer


class MainMenuDialogue(IDialogue):

    switch_callback: Callable
    options: List[str]
    selected_index: int
    screen: Screen
    drawer: Drawer

    def __init__(self, switch_callback: Callable, s: Screen, d: Drawer):
        self.switch_callback = switch_callback
        self.options = ["Play", "Quit"]
        self.selected_index = 0
        self.screen = s
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
        self.drawer.draw_menu("PONG", self.options, self.selected_index)

    def _move_up(self) -> None:
        self.selected_index = (self.selected_index - 1) % len(self.options)
        self.refresh()

    def _move_down(self) -> None:
        self.selected_index = (self.selected_index + 1) % len(self.options)
        self.refresh()

    def _select(self) -> None:
        s = self.options[self.selected_index]
        if s == "Play":
            self.switch_callback(GameDialogue(self.switch_callback, self.screen, self.drawer))
        else:
            turtle.bye()