import turtle
from turtle import Screen
from typing import Callable, List

from matplotlib.backend_bases import DrawEvent

from pong.dialogues.game_over_dialogue import GameOverDialogue
from pong.dialogues.idialogue import IDialogue
from pong.draw import Drawer
from pong.world import World


class GameDialogue(IDialogue):

    switch_callback: Callable
    screen: Screen
    world: World
    score: List
    winning_score: int
    drawer: Drawer

    def __init__(self, switch_callback: Callable, s: Screen, d: Drawer):
        self.switch_callback = switch_callback
        self.screen = s
        self.world = World()
        self.score = [0, 0]
        self.winning_score = 5
        self.drawer = d

    def mount(self):
        turtle.listen()
        turtle.onkeypress(self.world.move_left_paddle_up, "w")
        turtle.onkeypress(self.world.move_left_paddle_down, "s")
        turtle.onkeypress(self.world.move_right_paddle_up, "Up")
        turtle.onkeypress(self.world.move_right_paddle_down, "Down")

    def unmount(self):
        turtle.onkeypress(None, "W")
        turtle.onkeypress(None, "S")
        turtle.onkeypress(None, "Up")
        turtle.onkeypress(None, "Down")
        self.drawer.clear_screen()

    def refresh(self):
        state = self.world.update_world()
        self.drawer.draw_world(self.world, self.score)
        if state == 1:
            self.score[0] += 1
            if self.score[0] == self.winning_score:
                # Pass self.drawer as the third argument
                self.switch_callback(GameOverDialogue(self.switch_callback, self.screen, self.drawer, 1))
            else:
                self.world.restart_game()

        elif state == 2:
            self.score[1] += 1
            if self.score[1] == self.winning_score:
                # Pass self.drawer as the third argument
                self.switch_callback(GameOverDialogue(self.switch_callback, self.screen, self.drawer, 2))
            else:
                self.world.restart_game()