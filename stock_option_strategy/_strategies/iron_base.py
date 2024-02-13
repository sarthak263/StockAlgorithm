from abc import ABC, abstractmethod
class IronOptionStrategyBase(ABC):

    @abstractmethod
    def get_same_width_option_price(self) -> dict[str:str]:
        """
        Abstract method to get the option price for a strategy with the same width.
        """
        pass

    @abstractmethod
    def get_different_width_option_price(self) -> dict[str:str]:
        """
        Abstract method to get the option price for a strategy with a different width.
        """
        pass
