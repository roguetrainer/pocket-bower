import pickle
import random
from collections import defaultdict
from ..engine.state import EuchreGameState, GamePhase
from ..engine.card import Deck
from ..agents.cfr_utils import get_info_set_key
from ..agents.heuristic import RuleBasedAgent

class CFRTrainer:
    def __init__(self):
        # Map of info_set_key -> { 'regret_sum': {act: val}, 'strategy_sum': {act: val} }
        self.nodes = defaultdict(lambda: {
            'regret_sum': {'P': 0.0, 'O': 0.0},
            'strategy_sum': {'P': 0.0, 'O': 0.0}
        })
        # We use the heuristic bot to simulate the rest of the hand (playout)
        self.evaluator = RuleBasedAgent("Eval")

    def train(self, iterations=1000):
        print(f"Starting CFR Training for {iterations} iterations...")
        
        for i in range(iterations):
            if i % 100 == 0:
                print(f"Iteration {i}/{iterations}")
                
            # Initialize a fresh game
            state = EuchreGameState()
            state.start_hand() # Deals cards, sets up_card, phase = BIDDING_ROUND_1
            
            # Start CFR traversal
            # P0 and P1 represent reach probabilities for team 0 and team 1
            self.cfr(state, [], 1.0, 1.0)

        self._save_policy()

    def cfr(self, state: EuchreGameState, history, p0, p1):
        """
        Recursive CFR function.
        state: Current game state
        history: List of actions taken so far in this round (e.g. ['P', 'P'])
        p0: Reach probability for Team 0
        p1: Reach probability for Team 1
        """
        # 1. Terminal Check: Round 1 ends if someone orders up or everyone passes
        if history and history[-1] == 'O':
            # Someone ordered up. Play out the hand to see who wins.
            return self._get_playout_reward(state, history)
            
        if len(history) == 4:
            # Everyone passed. In this simplified Trainer, we assume redeal = 0 payoff
            # Or we could train Round 2 here. For now, return 0.
            return 0

        # 2. Determine whose turn it is
        # Bidding starts left of dealer
        start_player = (state.dealer_index + 1) % 4
        current_player = (start_player + len(history)) % 4
        current_team = current_player % 2
        
        # 3. Get Information Set
        hand = state.hands[current_player]
        # Only pass the history relevant to this specific decision point
        info_set_key = get_info_set_key(hand, history, current_player, state.dealer_index, state.up_card.suit)
        
        node = self.nodes[info_set_key]
        
        # 4. Get Strategy (Regret Matching)
        strategy = self._get_strategy(node['regret_sum'])
        
        actions = ['P', 'O'] # Pass, Order Up
        util = {'P': 0, 'O': 0}
        node_util = 0
        
        # 5. Recursively Call CFR for each action
        for act in actions:
            # Update history
            next_history = history + [act]
            
            # Update reach probs
            next_p0 = p0 * strategy[act] if current_team == 0 else p0
            next_p1 = p1 * strategy[act] if current_team == 1 else p1
            
            # If 'O', we need to mutate state for the playout
            next_state = state # In purely abstract CFR we clone, but here we lazy-mutate logic in terminal step
            
            # RECURSE
            # Note: The utility returned is from the perspective of the *current_player*
            util[act] = -1 * self.cfr(next_state, next_history, next_p0, next_p1) if current_team != (current_player % 2) else self.cfr(next_state, next_history, next_p0, next_p1)
            # Actually, standard CFR returns utility for the active player.
            # Let's simplify: Return utility for Team 0 always.
            
            util[act] = self.cfr(next_state, next_history, next_p0, next_p1)
            
            node_util += strategy[act] * util[act]

        # 6. Compute Regrets & Update Node
        # Reach prob for this player
        pr = p0 if current_team == 0 else p1
        
        for act in actions:
            regret = util[act] - node_util
            node['regret_sum'][act] += pr * regret
            node['strategy_sum'][act] += pr * strategy[act]
            
        return node_util

    def _get_strategy(self, regret_sum):
        """Regret Matching to get current strategy"""
        total_positive_regret = sum(max(r, 0) for r in regret_sum.values())
        strategy = {}
        if total_positive_regret > 0:
            for act in ['P', 'O']:
                strategy[act] = max(regret_sum[act], 0) / total_positive_regret
        else:
            strategy = {'P': 0.5, 'O': 0.5}
        return strategy

    def _get_playout_reward(self, state, history):
        """
        Simulates the rest of the hand using the Heuristic Agent
        to determine if the 'Order Up' decision was good.
        Returns: +1 if Team 0 won, -1 if Team 1 won.
        """
        # Who ordered it up? The last player in history.
        start_player = (state.dealer_index + 1) % 4
        # The history length (including the 'O') tells us who acted
        actor_offset = len(history) - 1
        maker_idx = (start_player + actor_offset) % 4
        
        # Apply the 'Order Up' logic to the state
        # In a real game, dealer swaps. We simulate that.
        state.maker_team = maker_idx % 2
        state.trump_suit = state.up_card.suit
        state.phase = GamePhase.PLAYING
        
        # Simple dealer discard simulation
        dealer_hand = state.hands[state.dealer_index]
        dealer_hand.append(state.up_card)
        discard = self.evaluator.select_discard(dealer_hand, state.up_card)
        # Find and remove discard (tricky because select_discard assumes it's picking form hand)
        # Let's just blindly remove lowest for speed/safety in trainer
        dealer_hand.sort(key=lambda c: c.get_value(state.trump_suit, None))
        dealer_hand.pop(0) # Remove worst
        
        # Play out the hand using Heuristic agents
        # We start from left of dealer
        state.current_player_index = (state.dealer_index + 1) % 4
        
        while state.phase == GamePhase.PLAYING:
            p_idx = state.current_player_index
            hand = state.hands[p_idx]

            # Safety check for empty hand
            if not hand:
                break

            card = self.evaluator.play_card(state)

            # Find card index safely
            card_idx = None
            for i, c in enumerate(hand):
                if c.rank == card.rank and c.suit == card.suit:
                    card_idx = i
                    break

            if card_idx is None:
                # Card not found, play first card as fallback
                card_idx = 0

            state.play_card(p_idx, card_idx)
            
        # Game Over (for this hand)
        # Calculate utility for Team 0
        # Winning 3+ tricks is the goal.
        # But points matter more.
        
        team0_score = state.team_scores[0]
        team1_score = state.team_scores[1]
        
        # Normalized payoff
        if team0_score > team1_score:
            return (team0_score - team1_score) # e.g. +1, +2, +4
        elif team1_score > team0_score:
            return -(team1_score - team0_score)
        return 0

    def _save_policy(self):
        # Convert cumulative strategy sum to average strategy
        final_policy = {}
        for key, node in self.nodes.items():
            strategy_sum = node['strategy_sum']
            total = sum(strategy_sum.values())
            if total > 0:
                final_policy[key] = {k: v/total for k, v in strategy_sum.items()}
            else:
                final_policy[key] = {'P': 0.5, 'O': 0.5}
                
        with open("cfr_policy.pkl", "wb") as f:
            pickle.dump(final_policy, f)
        print("Policy saved to cfr_policy.pkl")

if __name__ == "__main__":
    trainer = CFRTrainer()
    trainer.train(iterations=100) # Small number for test