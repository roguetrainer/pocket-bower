from typing import Optional, List
import random

from .base import Agent
from ..engine.state import EuchreGameState
from ..engine.card import Card, Suit, Rank
from ..engine.actions import get_valid_moves

class RuleBasedAgent(Agent):
    """
    A strong baseline agent that uses standard Euchre heuristics.
    """
    def select_discard(self, hand: List[Card], up_card: Card) -> Card:
        """
        Discard logic:
        1. Keep trumps.
        2. Keep Aces.
        3. Throw the lowest value non-trump card.
        """
        # Note: In our engine, the hand passed here typically includes the up_card already
        # if the dealer swap logic handled it, but let's assume we pick the worst from 'hand'.
        trump_suit = up_card.suit
        
        def card_score(c: Card):
            # High score = Keep, Low score = Throw
            if c.get_effective_suit(trump_suit) == trump_suit:
                return 100 + c.rank.value # Keep all trumps
            if c.rank == Rank.ACE:
                return 50
            return c.rank.value

        # Return the card with the lowest score
        return min(hand, key=card_score)

    def pick_up_card(self, game_state: EuchreGameState) -> bool:
        """
        Round 1: Order up if we have a strong hand (score > 7).
        """
        hand = game_state.hands[game_state.current_player_index]
        potential_trump = game_state.up_card.suit
        
        score = self._eval_hand(hand, potential_trump)
        
        # Dealer partner assist bonus
        is_partner_dealer = (game_state.dealer_index == (game_state.current_player_index + 2) % 4)
        if is_partner_dealer:
            score += 3
            
        return score >= 7

    def call_suit(self, game_state: EuchreGameState) -> Optional[Suit]:
        """
        Round 2: Call the best suit if score > 7.
        """
        hand = game_state.hands[game_state.current_player_index]
        invalid_suit = game_state.up_card.suit
        
        best_suit = None
        best_score = 0
        
        for suit in Suit:
            if suit == invalid_suit:
                continue
            
            score = self._eval_hand(hand, suit)
            if score > best_score:
                best_score = score
                best_suit = suit
                
        if best_score >= 7:
            return best_suit
        return None

    def play_card(self, game_state: EuchreGameState) -> Card:
        """
        Play Logic:
        1. Valid moves only.
        2. If leading: Lead high trump or Ace.
        3. If following: Win if possible, otherwise throw low.
        """
        player_idx = game_state.current_player_index
        hand = game_state.hands[player_idx]

        # Safety check for empty hand
        if not hand:
            raise ValueError(f"Player {player_idx} has empty hand")

        valid_moves = get_valid_moves(hand, game_state.current_trick, game_state.trump_suit)

        if not valid_moves:
            # Fallback: return first card if no valid moves (defensive)
            return hand[0]

        # Simple heuristic: Pick first valid move
        # (This is where you would expand the logic significantly)
        return valid_moves[0]

    def _eval_hand(self, hand: List[Card], trump: Suit) -> int:
        """
        Standard Point System:
        Right = 4, Left = 3, Ace = 1, Trump = 2
        """
        score = 0
        for card in hand:
            eff_suit = card.get_effective_suit(trump)
            if eff_suit == trump:
                if card.rank == Rank.JACK and card.suit == trump:
                    score += 4 # Right
                elif card.rank == Rank.JACK:
                    score += 3 # Left
                else:
                    score += 2 # Regular Trump
            elif card.rank == Rank.ACE:
                score += 1
        return score