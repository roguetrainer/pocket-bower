from enum import Enum, auto
from typing import List, Optional, Tuple
from dataclasses import dataclass, field

from .card import Deck, Card, Suit
from .actions import get_valid_moves, resolve_trick

class GamePhase(Enum):
    PRE_DEAL = auto()
    BIDDING_ROUND_1 = auto()
    BIDDING_ROUND_2 = auto()
    PLAYING = auto()
    HAND_OVER = auto()
    GAME_OVER = auto()

class EuchreGameState:
    def __init__(self, target_score=10):
        self.target_score = target_score
        self.team_scores = [0, 0]
        self.dealer_index = 0
        
        # State Variables
        self.phase = GamePhase.PRE_DEAL
        self.hands: List[List[Card]] = [[], [], [], []]
        self.kitty: List[Card] = []
        self.up_card: Optional[Card] = None
        self.trump_suit: Optional[Suit] = None
        
        self.maker_team: Optional[int] = None
        self.is_loner = False
        self.loner_player_index: Optional[int] = None
        
        self.current_player_index = 0
        self.tricks_taken = [0, 0]
        self.current_trick: List[Tuple[int, Card]] = []

    def start_hand(self):
        deck = Deck()
        deck.shuffle()
        self.hands, self.kitty = deck.deal()
        self.up_card = self.kitty[0]
        self.trump_suit = None
        self.maker_team = None
        self.is_loner = False
        self.tricks_taken = [0, 0]
        self.phase = GamePhase.BIDDING_ROUND_1
        self.current_player_index = (self.dealer_index + 1) % 4
        print(f"\n--- New Hand! Dealer: P{self.dealer_index}, Up Card: {self.up_card} ---")

    def order_up(self, player_idx: int, going_alone: bool = False):
        if self.phase != GamePhase.BIDDING_ROUND_1:
            raise ValueError("Not in Round 1")
        
        self.trump_suit = self.up_card.suit
        self.maker_team = player_idx % 2
        self.is_loner = going_alone
        if going_alone:
            self.loner_player_index = player_idx
        
        print(f"P{player_idx} orders up {self.trump_suit.name}")
        self._dealer_swap()
        self._start_playing_phase()

    def call_suit(self, player_idx: int, suit: Suit, going_alone: bool = False):
        if self.phase != GamePhase.BIDDING_ROUND_2:
            raise ValueError("Not in Round 2")
        if suit == self.up_card.suit:
            raise ValueError("Cannot call turned-down suit")
            
        self.trump_suit = suit
        self.maker_team = player_idx % 2
        self.is_loner = going_alone
        if going_alone:
            self.loner_player_index = player_idx

        print(f"P{player_idx} calls {suit.name}")
        self._start_playing_phase()

    def pass_turn(self):
        print(f"P{self.current_player_index} passes")
        self.current_player_index = (self.current_player_index + 1) % 4
        
        if self.current_player_index == (self.dealer_index + 1) % 4:
            if self.phase == GamePhase.BIDDING_ROUND_1:
                self.phase = GamePhase.BIDDING_ROUND_2
                print("Up-card turned down.")
            else:
                print("Stuck the dealer (or redeal). Restarting.")
                self.dealer_index = (self.dealer_index + 1) % 4
                self.start_hand()

    def play_card(self, player_idx: int, card_idx: int):
        if self.phase != GamePhase.PLAYING:
            raise ValueError("Not in playing phase")
        if player_idx != self.current_player_index:
            raise ValueError(f"Not P{player_idx}'s turn")

        hand = self.hands[player_idx]
        card = hand[card_idx]
        
        # USE ACTIONS.PY FOR VALIDATION
        valid_moves = get_valid_moves(hand, self.current_trick, self.trump_suit)
        if card not in valid_moves:
            raise ValueError(f"Illegal move: {card}. Valid: {valid_moves}")

        hand.pop(card_idx)
        self.current_trick.append((player_idx, card))
        print(f"P{player_idx} plays {card}")

        if len(self.current_trick) == 4:
            self._resolve_trick()
        else:
            self._advance_turn_playing()

    def _resolve_trick(self):
        # USE ACTIONS.PY FOR LOGIC
        winner_idx = resolve_trick(self.current_trick, self.trump_suit)
        winning_team = winner_idx % 2
        
        self.tricks_taken[winning_team] += 1
        print(f"P{winner_idx} wins trick.")
        
        self.current_trick = []
        if sum(self.tricks_taken) == 5:
            self._score_hand()
        else:
            self.current_player_index = winner_idx

    def _dealer_swap(self):
        # Simplified swap logic
        dealer_hand = self.hands[self.dealer_index]
        dealer_hand.append(self.up_card)
        # Discard lowest value non-trump
        dealer_hand.sort(key=lambda c: c.get_value(self.trump_suit, None))
        dealer_hand.pop(0)

    def _start_playing_phase(self):
        self.phase = GamePhase.PLAYING
        self.current_player_index = (self.dealer_index + 1) % 4

    def _advance_turn_playing(self):
        self.current_player_index = (self.current_player_index + 1) % 4
        # Loner Logic: Skip partner
        if self.is_loner and self.maker_team is not None:
            partner_idx = (self.loner_player_index + 2) % 4
            if self.current_player_index == partner_idx:
                self.current_player_index = (self.current_player_index + 1) % 4

    def _score_hand(self):
        maker_tricks = self.tricks_taken[self.maker_team]
        points = 0
        if maker_tricks == 5:
            points = 4 if self.is_loner else 2
        elif maker_tricks >= 3:
            points = 1
        else:
            points = 2 # Euchred
            
        winning_team = self.maker_team if maker_tricks >=3 else (1 - self.maker_team)
        self.team_scores[winning_team] += points
        
        print(f"Hand Over. Score: {self.team_scores}")
        if max(self.team_scores) >= self.target_score:
            self.phase = GamePhase.GAME_OVER
            print("GAME OVER")
        else:
            self.dealer_index = (self.dealer_index + 1) % 4
            self.start_hand()