import random
from typing import Optional

from .base import Agent
from ..engine.state import EuchreGameState
from ..engine.card import Card, Suit
from ..engine.actions import get_valid_moves

class RandomAgent(Agent):
    """
    A chaos bot that makes legally valid but completely random moves.
    Useful for testing game stability and establishing a baseline win rate.
    """
    def select_discard(self, hand: list[Card], up_card: Card) -> Card:
        # Randomly discard one card
        return random.choice(hand)

    def pick_up_card(self, game_state: EuchreGameState) -> bool:
        # 50/50 chance to order it up
        return random.choice([True, False])

    def call_suit(self, game_state: EuchreGameState) -> Optional[Suit]:
        # Cannot pick the suit that was just turned down
        invalid_suit = game_state.up_card.suit
        valid_suits = [s for s in Suit if s != invalid_suit]
        
        # 20% chance to pass, otherwise pick a random valid suit
        if random.random() < 0.2:
            return None
        return random.choice(valid_suits)

    def play_card(self, game_state: EuchreGameState) -> Card:
        player_idx = game_state.current_player_index
        hand = game_state.hands[player_idx]
        
        # Must use the engine's validation logic to find legal moves
        valid_moves = get_valid_moves(hand, game_state.current_trick, game_state.trump_suit)
        
        return random.choice(valid_moves)