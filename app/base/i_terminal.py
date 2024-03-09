from abc import ABC, abstractmethod


class ITerminal(ABC):
    @abstractmethod
    def close(self) -> None:
        pass

    def clear(slef) -> None:
        pass
