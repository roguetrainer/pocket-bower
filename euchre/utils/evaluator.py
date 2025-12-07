"""
Tournament Evaluator for Euchre Agents

Runs multiple games between different agent configurations and tracks statistics.
"""
import sys
import os
from typing import List, Dict, Tuple
from collections import defaultdict
import time

# Add current directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from euchre.engine.state import EuchreGameState, GamePhase
from euchre.agents import Agent, RandomAgent, RuleBasedAgent, MCTSAgent, CFRAgent


class GameResult:
    """Stores the outcome of a single game."""
    def __init__(self, team0_score: int, team1_score: int, num_hands: int):
        self.team0_score = team0_score
        self.team1_score = team1_score
        self.num_hands = num_hands
        self.winner = 0 if team0_score > team1_score else 1


class TournamentStats:
    """Tracks statistics across multiple games."""
    def __init__(self, team0_name: str, team1_name: str):
        self.team0_name = team0_name
        self.team1_name = team1_name
        self.games_played = 0
        self.team0_wins = 0
        self.team1_wins = 0
        self.total_hands = 0
        self.team0_total_score = 0
        self.team1_total_score = 0

    def add_result(self, result: GameResult):
        """Add a game result to the statistics."""
        self.games_played += 1
        self.total_hands += result.num_hands
        self.team0_total_score += result.team0_score
        self.team1_total_score += result.team1_score

        if result.winner == 0:
            self.team0_wins += 1
        else:
            self.team1_wins += 1

    def print_summary(self):
        """Print tournament statistics."""
        print("\n" + "="*60)
        print(f"TOURNAMENT RESULTS: {self.team0_name} vs {self.team1_name}")
        print("="*60)
        print(f"Games Played: {self.games_played}")
        print(f"Total Hands: {self.total_hands}")
        print(f"Avg Hands/Game: {self.total_hands / self.games_played:.1f}")
        print()
        print(f"{self.team0_name:20s} | Wins: {self.team0_wins:4d} ({self.team0_wins/self.games_played*100:5.1f}%)")
        print(f"{self.team1_name:20s} | Wins: {self.team1_wins:4d} ({self.team1_wins/self.games_played*100:5.1f}%)")
        print()
        print(f"Avg Score - {self.team0_name}: {self.team0_total_score / self.games_played:.1f}")
        print(f"Avg Score - {self.team1_name}: {self.team1_total_score / self.games_played:.1f}")
        print("="*60)


def play_single_game(agents: List[Agent], target_score: int = 10, verbose: bool = False) -> GameResult:
    """
    Play a single game to target_score with the given agents.

    Args:
        agents: List of 4 Agent objects (Team 0: agents[0] & agents[2], Team 1: agents[1] & agents[3])
        target_score: Score required to win the game
        verbose: Whether to print game progress

    Returns:
        GameResult object with final scores and stats
    """
    if len(agents) != 4:
        raise ValueError("Must provide exactly 4 agents")

    game = EuchreGameState(target_score=target_score)
    hands_played = 0
    max_steps = 1000  # Safety limit to prevent infinite loops
    step_count = 0

    while game.phase != GamePhase.GAME_OVER and step_count < max_steps:
        # Start new hand if needed
        if game.phase == GamePhase.PRE_DEAL:
            game.start_hand()
            hands_played += 1
            if verbose:
                print(f"\n--- Hand {hands_played} ---")

        current_player = game.current_player_index
        agent = agents[current_player]

        try:
            if game.phase == GamePhase.BIDDING_ROUND_1:
                decision = agent.pick_up_card(game)
                if decision:
                    game.order_up(current_player)
                else:
                    game.pass_turn()

            elif game.phase == GamePhase.BIDDING_ROUND_2:
                suit = agent.call_suit(game)
                if suit:
                    game.call_suit(current_player, suit)
                else:
                    game.pass_turn()

            elif game.phase == GamePhase.PLAYING:
                card = agent.play_card(game)
                hand = game.hands[current_player]

                # Find card index
                card_idx = None
                for i, c in enumerate(hand):
                    if c.rank == card.rank and c.suit == card.suit:
                        card_idx = i
                        break

                if card_idx is None:
                    if verbose:
                        print(f"ERROR: Agent {agent.name} tried to play {card} not in hand {hand}")
                    # Play first legal card as fallback
                    card_idx = 0

                game.play_card(current_player, card_idx)

        except Exception as e:
            if verbose:
                print(f"ERROR in game: {e}")
            break

        step_count += 1

    if step_count >= max_steps:
        if verbose:
            print(f"WARNING: Game hit max steps ({max_steps}), terminating early")

    return GameResult(game.team_scores[0], game.team_scores[1], hands_played)


def run_tournament(
    team0_agents: Tuple[Agent, Agent],
    team1_agents: Tuple[Agent, Agent],
    num_games: int = 100,
    target_score: int = 10,
    verbose: bool = False
) -> TournamentStats:
    """
    Run a tournament between two teams.

    Args:
        team0_agents: Tuple of 2 agents for team 0 (players 0 and 2)
        team1_agents: Tuple of 2 agents for team 1 (players 1 and 3)
        num_games: Number of games to play
        target_score: Points needed to win each game
        verbose: Whether to print progress

    Returns:
        TournamentStats object with results
    """
    team0_name = f"{team0_agents[0].name} & {team0_agents[1].name}"
    team1_name = f"{team1_agents[0].name} & {team1_agents[1].name}"

    stats = TournamentStats(team0_name, team1_name)

    print(f"\nStarting Tournament: {team0_name} vs {team1_name}")
    print(f"Playing {num_games} games to {target_score} points each...")

    start_time = time.time()

    for game_num in range(num_games):
        if not verbose and (game_num + 1) % 10 == 0:
            print(f"  Progress: {game_num + 1}/{num_games} games completed")

        # Arrange agents: Team 0 = positions 0 & 2, Team 1 = positions 1 & 3
        agents = [
            team0_agents[0],  # Player 0 (Team 0)
            team1_agents[0],  # Player 1 (Team 1)
            team0_agents[1],  # Player 2 (Team 0)
            team1_agents[1],  # Player 3 (Team 1)
        ]

        result = play_single_game(agents, target_score, verbose)
        stats.add_result(result)

    elapsed = time.time() - start_time
    print(f"\nTournament completed in {elapsed:.1f} seconds ({elapsed/num_games:.2f}s per game)")

    return stats


# ============================================================================
# Example Usage / Main
# ============================================================================

def main():
    """Run example tournaments."""

    print("\n" + "="*60)
    print("POCKET BOWER - AGENT EVALUATOR")
    print("="*60)

    # Tournament 1: Random vs Random (baseline)
    print("\n\n### Tournament 1: Random vs Random (Control) ###")
    team0 = (RandomAgent("R0"), RandomAgent("R2"))
    team1 = (RandomAgent("R1"), RandomAgent("R3"))
    stats1 = run_tournament(team0, team1, num_games=100)
    stats1.print_summary()

    # Tournament 2: RuleBased vs Random
    print("\n\n### Tournament 2: RuleBased vs Random ###")
    team0 = (RuleBasedAgent("H0"), RuleBasedAgent("H2"))
    team1 = (RandomAgent("R1"), RandomAgent("R3"))
    stats2 = run_tournament(team0, team1, num_games=100)
    stats2.print_summary()

    # Tournament 3: MCTS vs RuleBased (if time permits)
    print("\n\n### Tournament 3: MCTS vs RuleBased ###")
    print("(Note: MCTS is slow, running fewer games)")
    team0 = (MCTSAgent("M0", simulation_time=0.5), MCTSAgent("M2", simulation_time=0.5))
    team1 = (RuleBasedAgent("H1"), RuleBasedAgent("H3"))
    stats3 = run_tournament(team0, team1, num_games=20)  # Fewer games due to speed
    stats3.print_summary()

    # Tournament 4: CFR vs RuleBased (if policy file exists)
    try:
        print("\n\n### Tournament 4: CFR vs RuleBased ###")
        team0 = (CFRAgent("C0"), CFRAgent("C2"))
        team1 = (RuleBasedAgent("H1"), RuleBasedAgent("H3"))
        stats4 = run_tournament(team0, team1, num_games=100)
        stats4.print_summary()
    except FileNotFoundError:
        print("\nCFR policy file not found. Train CFR first with:")
        print("  python -m euchre.training.cfr_trainer")

    print("\n\n" + "="*60)
    print("ALL TOURNAMENTS COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()
