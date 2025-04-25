import turtle

from pexpect.screen import screen

from dialogue_master import DialogueMaster
from dialogues.main_menu_dialogue import MainMenuDialogue
from pong import draw



def main():
    s = turtle.Screen()
    d = draw.Drawer(s, 800, 600)
    dm = DialogueMaster(s, d)
    dm.put_dialogue(MainMenuDialogue(switch_callback = dm.put_dialogue, s=s, d=d))
    dm.endless_loop()

if __name__ == '__main__':
    main()