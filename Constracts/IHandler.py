from abc import ABCMeta, abstractmethod
from GlobalVariables.GlobalVariables import GlobalVariables


class IHandler(metaclass=ABCMeta):
    globalVariable = GlobalVariables()

    @abstractmethod
    def handler(self, item):
        pass
