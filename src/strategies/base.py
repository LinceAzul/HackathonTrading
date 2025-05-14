from abc import ABC, abstractmethod

class StrategyInterface(ABC):
    @abstractmethod
    def __init__(self):
        """Initialize strategy state."""
        pass

    @abstractmethod
    def on_data(self, market_data, balances):
        """Process market data and balances to produce trading signals or actions."""
        pass
