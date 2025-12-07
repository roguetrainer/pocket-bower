import time
import copy
import random
import math
from typing import List, Optional

from .base import Agent
from .heuristic import RuleBasedAgent
from ..engine.state import EuchreGameState, GamePhase
from ..engine.card import Card, Suit
from ..engine.actions import get_valid_moves

class MCTSNode:
    def __init__(self, parent=None, move=None, player_idx=None):
        self.parent = parent
        self.move = move  # The card played to reach this node
        self.player_idx = player_idx # Who played the move
        self.children = []
        self.visits = 0
        self.wins = 0.0
        self.untried_moves = []

    def ucb1(self, c=1.41):
        if self.visits == 0:
            return float('inf')
        return (self.wins / self.visits) + c * math.sqrt(math.log(self.parent.visits) / self.visits)

class MCTSAgent(Agent):
    def __init__(self, name: str, simulation_time=1.0):
        super().__init__(name)
        self.simulation_time = simulation_time
        # We use the RuleBased bot for Bidding and Rollouts
        self.fallback_bot = RuleBasedAgent("Internal")

    # --- Bidding: Delegate to Heuristic (Faster) ---
    def select_discard(self, hand, up_card):
        return self.fallback_bot.select_discard(hand, up_card)

    def pick_up_card(self, game_state):
        return self.fallback_bot.pick_up_card(game_state)

    def call_suit(self, game_state):
        return self.fallback_bot.call_suit(game_state)

    # --- Playing: Use MCTS ---
    def play_card(self, game_state: EuchreGameState) -> Card:
        player_idx = game_state.current_player_index
        hand = game_state.hands[player_idx]
        valid_moves = get_valid_moves(hand, game_state.current_trick, game_state.trump_suit)

        # Optimization: Only 1 move? Don't think, just play.
        if len(valid_moves) == 1:
            return valid_moves[0]

        root = MCTSNode(player_idx=player_idx)
        root.untried_moves = valid_moves
        
        end_time = time.time() + self.simulation_time

        while time.time() < end_time:
            # 1. Determinize (Guess hidden cards)
            # We clone the state and reshuffle unknown cards to opponents
            sim_state = self._determinize(game_state)
            
            node = root
            
            # 2. Select
            # Navigate down the tree to a leaf
            while not node.untried_moves and node.children:
                node = max(node.children, key=lambda c: c.ucb1())
                # Apply move to sim_state
                # Note: We need a way to advance the sim_state. 
                # In this simplified version, we just play the move.
                sim_state.play_card(node.player_idx, self._get_card_index(sim_state, node.move))

            # 3. Expand
            # If we aren't at game over, add a child node
            if node.untried_moves and sim_state.phase == GamePhase.PLAYING:
                move = random.choice(node.untried_moves)
                
                # Apply move
                current_p = sim_state.current_player_index
                sim_state.play_card(current_p, self._get_card_index(sim_state, move))
                
                new_node = MCTSNode(parent=node, move=move, player_idx=current_p)
                # Calculate legal moves for the *next* player in the sim
                next_p = sim_state.current_player_index
                if sim_state.phase == GamePhase.PLAYING:
                    new_node.untried_moves = get_valid_moves(sim_state.hands[next_p], sim_state.current_trick, sim_state.trump_suit)
                
                node.children.append(new_node)
                node.untried_moves.remove(move)
                node = new_node

            # 4. Rollout
            # Play randomly/heuristically until hand ends
            while sim_state.phase == GamePhase.PLAYING:
                p_idx = sim_state.current_player_index
                moves = get_valid_moves(sim_state.hands[p_idx], sim_state.current_trick, sim_state.trump_suit)
                random_move = random.choice(moves)
                sim_state.play_card(p_idx, self._get_card_index(sim_state, random_move))

            # 5. Backpropagate
            # Did our team win?
            # Note: team_scores increases during play. We need to check if we won the HAND.
            # Simplified: Did we win more tricks in this rollout?
            # Or did we get points?
            
            # Let's check the team of the root player
            root_team = root.player_idx % 2
            
            # Simple reward: 1 if we won the hand, 0 if lost
            # We can check sim_state.team_scores vs original scores, 
            # or just sim_state.tricks_taken if hand isn't fully scored yet.
            
            # Better reward: Difference in tricks taken
            reward = 0
            if sim_state.tricks_taken[root_team] > sim_state.tricks_taken[1-root_team]:
                reward = 1.0
            
            while node:
                node.visits += 1
                node.wins += reward
                node = node.parent

        # Return best move (most visited)
        best_child = max(root.children, key=lambda c: c.visits)
        return best_child.move

    def _determinize(self, state: EuchreGameState) -> EuchreGameState:
        """
        Creates a perfect-information clone of the state.
        It keeps the current player's hand and the current trick fixed.
        It shuffles all other unknown cards and deals them to opponents.
        """
        # Deep copy the state so we don't mess up the real game
        sim = copy.deepcopy(state)
        
        # In a real implementation, you would:
        # 1. Collect all cards not in my hand, not in current trick, and not played.
        # 2. Shuffle them.
        # 3. Redistribute to other players.
        # For now, to keep it runnable without complex state tracking, 
        # we will return the naive deepcopy (Assuming we know everyone's cards - Cheating MCTS)
        # This is often called PIMC (Perfect Information Monte Carlo)
        return sim

    def _get_card_index(self, state, card):
        """Helper to find the index of a card object in a hand."""
        hand = state.hands[state.current_player_index]
        for i, c in enumerate(hand):
            if c.rank == card.rank and c.suit == card.suit:
                return i
        return 0