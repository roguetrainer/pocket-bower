import random
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Tuple

class Suit(Enum):
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"
    SPADES = "♠"

    @property
    def color(self):
        if self in (Suit.HEARTS, Suit.DIAMONDS):
            return "RED"
        return "BLACK"

    @property
    def other_color_suit(self):
        """Returns the sister suit (e.g., Hearts <-> Diamonds)."""
        pairs = {
            Suit.HEARTS: Suit.DIAMONDS,
            Suit.DIAMONDS: Suit.HEARTS,
            Suit.CLUBS: Suit.SPADES,
            Suit.SPADES: Suit.CLUBS
        }
        return pairs[self]

class Rank(Enum):
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14

@dataclass(frozen=True)
class Card:
    rank: Rank
    suit: Suit

    def __repr__(self):
        return f"{self.rank.name.title()}{self.suit.value}"

    def get_effective_suit(self, trump_suit: Optional[Suit]) -> Suit:
        """
        The critical Euchre rule: The Left Bower acts as the Trump Suit.
        """
        if trump_suit is None:
            return self.suit
        
        # Check for Left Bower (Jack of the other color suit)
        if self.rank == Rank.JACK and self.suit == trump_suit.other_color_suit:
            return trump_suit
        
        return self.suit

    def get_value(self, trump_suit: Optional[Suit], led_suit: Optional[Suit]) -> int:
        """
        Returns a comparable integer for determining trick winner.
        """
        if trump_suit is None:
            return self.rank.value if self.suit == led_suit else 0

        effective_suit = self.get_effective_suit(trump_suit)

        # 1. Trump Logic
        if effective_suit == trump_suit:
            base = 100
            # Right Bower
            if self.rank == Rank.JACK and self.suit == trump_suit:
                return base + 20 
            # Left Bower
            if self.rank == Rank.JACK and self.suit == trump_suit.other_color_suit:
                return base + 15
            # Regular Trumps
            return base + self.rank.value

        # 2. Led Suit Logic
        if effective_suit == led_suit:
            return self.rank.value

        # 3. Off-suit
        return 0

class Deck:
    def __init__(self):
        self.cards = [Card(r, s) for s in Suit for r in Rank]
    
    def shuffle(self):
        random.shuffle(self.cards)
    
    def deal(self) -> Tuple[List[List[Card]], List[Card]]:
        if len(self.cards) != 24:
            raise ValueError("Deck must have 24 cards")
        
        hands = [[], [], [], []]
        for i in range(20):
            hands[i % 4].append(self.cards[i])
        kitty = self.cards[20:]
        return hands, kitty