import pickle
import random
import os
from typing import Optional

from .base import Agent
from .heuristic import RuleBasedAgent
from .cfr_utils import get_info_set_key
from ..engine.state import EuchreGameState
from ..engine.card import Card, Suit

class CFRAgent(Agent):
    def __init__(self, name: str, policy_file="cfr_policy.pkl"):
        super().__init__(name)
        self.policy = {}
        # Load the trained policy if it exists
        if os.path.exists(policy_file):
            with open(policy_file, "rb") as f:
                self.policy = pickle.load(f)
        
        # Use Heuristic bot for phases we haven't trained CFR for yet
        self.fallback_bot = RuleBasedAgent("Internal")

    def pick_up_card(self, game_state: EuchreGameState) -> bool:
        """
        Round 1 Bidding: Uses the CFR Policy Lookup.
        """
        player_idx = game_state.current_player_index
        hand = game_state.hands[player_idx]
        dealer_idx = game_state.dealer_index
        up_card_suit = game_state.up_card.suit

        # Reconstruct the history string (Who passed before me?)
        # Logic: If I am 1 spot left of dealer, 0 people passed.
        # If I am 2 spots left, 1 person passed (if we are here).
        # In this engine, pick_up_card is called in order. 
        # So we can infer passes based on relative position to (dealer + 1).
        
        # Calculate how many people passed before me in this round
        start_idx = (dealer_idx + 1) % 4
        # Handling the wrap-around logic to count steps
        steps = (player_idx - start_idx + 4) % 4
        
        history = ["P"] * steps
        
        key = get_info_set_key(hand, history, player_idx, dealer_idx, up_card_suit)

        # Default strategy: 50/50 if key missing
        strategy = self.policy.get(key, {"P": 0.5, "O": 0.5})
        
        choice = random.choices(list(strategy.keys()), weights=list(strategy.values()))[0]

        return choice == "O" # Returns True if "Order Up"

    # --- Delegate other phases to Heuristic Bot for stability ---

    def select_discard(self, hand: list[Card], up_card: Card) -> Card:
        return self.fallback_bot.select_discard(hand, up_card)

    def call_suit(self, game_state: EuchreGameState) -> Optional[Suit]:
        # You could implement CFR for Round 2 here later
        return self.fallback_bot.call_suit(game_state)

    def play_card(self, game_state: EuchreGameState) -> Card:
        return self.fallback_bot.play_card(game_state)