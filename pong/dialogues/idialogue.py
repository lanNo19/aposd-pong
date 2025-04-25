from abc import ABC, abstractmethod


class IDialogue(ABC):
    @abstractmethod
    def mount(self):
        pass

    @abstractmethod
    def unmount(self):
        pass

    @abstractmethod
    def refresh(self):
        pass