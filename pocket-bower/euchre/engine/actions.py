from typing import List, Tuple, Optional
from .card import Card, Suit

def get_valid_moves(hand: List[Card], current_trick: List[Tuple[int, Card]], trump_suit: Optional[Suit]) -> List[Card]:
    """
    Returns a list of cards from the hand that are legal to play.
    Enforces the 'Must Follow Suit' rule, accounting for Left Bower.
    """
    # If leading (first in trick), any card is valid
    if not current_trick:
        return hand.copy()
        
    # Determine the led suit (effective suit of the first card played)
    led_card = current_trick[0][1]
    led_suit = led_card.get_effective_suit(trump_suit)
    
    # Find cards in hand that match the led suit
    following_cards = []
    for card in hand:
        if card.get_effective_suit(trump_suit) == led_suit:
            following_cards.append(card)
            
    # Rule: If you can follow suit, you must.
    if following_cards:
        return following_cards
    
    # Otherwise, you can play anything (slough or trump)
    return hand.copy()

def resolve_trick(trick: List[Tuple[int, Card]], trump_suit: Optional[Suit]) -> int:
    """
    Determines the index of the player who won the trick.
    Returns the player_idx of the winner.
    """
    if not trick:
        raise ValueError("Cannot resolve empty trick")

    led_card = trick[0][1]
    led_suit = led_card.get_effective_suit(trump_suit)
    
    winner_idx = -1
    highest_val = -1
    
    for p_idx, card in trick:
        val = card.get_value(trump_suit, led_suit)
        if val > highest_val:
            highest_val = val
            winner_idx = p_idx
            
    return winner_idx