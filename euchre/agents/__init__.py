from .base import Agent
from .basic import RandomAgent
from .heuristic import RuleBasedAgent
from .mcts import MCTSAgent
from .cfr_agent import CFRAgent

# Registry for easy access in UI/Evaluation scripts
AVAILABLE_AGENTS = {
    "Random": RandomAgent,
    "RuleBased": RuleBasedAgent,
    "MCTS": MCTSAgent,
    "CFR": CFRAgent
}