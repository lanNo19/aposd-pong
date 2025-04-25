import turtle
from turtle import Screen
import time

from pong.dialogues.idialogue import IDialogue
from pong.draw import Drawer


class DialogueMaster:

    dialogue: IDialogue
    screen: Screen
    drawer: Drawer

    def __init__(self, s: Screen, d: Drawer):
        self.dialogue = None
        self.screen = s
        self.drawer = d

    def put_dialogue(self, d: IDialogue) -> None:
        if self.dialogue:
            self.dialogue.unmount()
        self.dialogue = d
        self.dialogue.mount()

    def endless_loop(self) -> None:
        while True:
            start = time.time()

            if self.dialogue:
                self.dialogue.refresh()

            delta = time.time() - start
            time.sleep(max(0, (1 / 25 - delta)))
            self.screen.update()