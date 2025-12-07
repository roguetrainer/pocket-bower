from ..engine.card import Rank, Card, Suit

def get_hand_strength_bucket(hand: list[Card], up_card_suit: Suit) -> str:
    """
    Classifies a hand into strength tiers based on standard point values.
    Right = 30, Left = 25, Trump = 10, Ace = 3.
    """
    score = 0
    for card in hand:
        # Use the new engine's effective suit logic
        eff_suit = card.get_effective_suit(up_card_suit)
        
        if eff_suit == up_card_suit:
            if card.rank == Rank.JACK:
                if card.suit == up_card_suit:
                    score += 30 # Right Bower
                else:
                    score += 25 # Left Bower
            else:
                score += 10 # Regular Trump
        elif card.rank == Rank.ACE:
            score += 3

    if score > 50: return "Tier4"
    if score > 35: return "Tier3"
    if score > 20: return "Tier2"
    if score > 10: return "Tier1"
    return "Tier0"

def get_info_set_key(hand, history, player_idx, dealer_idx, up_card_suit):
    """
    Creates a unique string key for the CFR lookup table.
    Example: 'Pos1_Tier3_PPP' (Position 1, Tier 3 hand, 3 Passes before me)
    """
    rel_pos = (player_idx - dealer_idx) % 4
    strength = get_hand_strength_bucket(hand, up_card_suit)
    hist_str = "".join(history)
    return f"Pos{rel_pos}_{strength}_{hist_str}"