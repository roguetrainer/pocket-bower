from abc import ABC, abstractmethod
from typing import Optional, List
from ..engine.state import EuchreGameState
from ..engine.card import Card, Suit

class Agent(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def select_discard(self, hand: List[Card], up_card: Card) -> Card:
        """Called when the agent is the dealer and picked up the up-card."""
        pass

    @abstractmethod
    def pick_up_card(self, game_state: EuchreGameState) -> bool:
        """
        Round 1 Bidding.
        Return True to order up the dealer, False to pass.
        """
        pass

    @abstractmethod
    def call_suit(self, game_state: EuchreGameState) -> Optional[Suit]:
        """
        Round 2 Bidding.
        Return a Suit to make it trump, or None to pass.
        """
        pass

    @abstractmethod
    def play_card(self, game_state: EuchreGameState) -> Card:
        """
        Playing Phase.
        Return the Card from hand to play.
        """
        pass