import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from euchre.engine.card import Card, Suit, Rank
from euchre.engine.state import EuchreGameState

def test_bower_logic():
    trump = Suit.SPADES
    
    # Create Cards (Note: Rank comes first in the new Engine)
    js = Card(Rank.JACK, Suit.SPADES)   # Right Bower
    jc = Card(Rank.JACK, Suit.CLUBS)    # Left Bower
    ah = Card(Rank.ACE, Suit.HEARTS)    # Random non-trump
    ks = Card(Rank.KING, Suit.SPADES)   # Second highest trump (usually)

    # 1. Test Effective Suit (The "Left Bower acts as Trump" rule)
    assert js.get_effective_suit(trump) == Suit.SPADES
    assert jc.get_effective_suit(trump) == Suit.SPADES  # CRITICAL: Clubs becomes Spades
    assert ah.get_effective_suit(trump) == Suit.HEARTS

    # 2. Test Value Hierarchy (Right > Left > Ace > King)
    # We pass 'None' as the led_suit for raw power comparison
    val_right = js.get_value(trump, None)
    val_left = jc.get_value(trump, None)
    val_king = ks.get_value(trump, None)
    
    print(f"Right: {val_right}, Left: {val_left}, King: {val_king}")

    assert val_right > val_left, "Right Bower must beat Left Bower"
    assert val_left > val_king, "Left Bower must beat King of Trump"

    print("✅ Bower logic tests passed.")

def test_game_init():
    game = EuchreGameState()
    game.start_hand()
    
    assert len(game.hands) == 4
    assert len(game.hands[0]) == 5
    assert len(game.kitty) == 4
    assert game.up_card is not None
    
    print("✅ Game state initialization passed.")

if __name__ == "__main__":
    test_bower_logic()
    test_game_init()