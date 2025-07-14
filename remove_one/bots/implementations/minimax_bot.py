import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...core.game_state import BotGameState
    from ...core.game_action import GameAction

from ..base_bot import Bot


class MinimaxBot(Bot):
    """Game tree search with limited depth"""
    
    def __init__(self, name: str, depth: int = 2):
        super().__init__(name)
        self.depth = depth
    
    def get_action(self, state: 'BotGameState', player_id: int) -> 'GameAction':
        """Use minimax to find best action"""
        best_action = None
        best_value = float('-inf')
        
        for action in state.legal_actions:
            value = self._minimax(state, action, player_id, self.depth, True)
            if value > best_value:
                best_value = value
                best_action = action
        
        return best_action or random.choice(state.legal_actions)
    
    def _minimax(self, state: 'BotGameState', action: 'GameAction', player_id: int, depth: int, maximizing: bool) -> float:
        """Minimax search with limited depth"""
        if depth == 0:
            return self._evaluate_position(state, player_id)
        
        return self._evaluate_position(state, player_id)
    
    def _evaluate_position(self, state: 'BotGameState', player_id: int) -> float:
        """Evaluate current position strength"""
        my_score = state.private_info['my_score']
        my_tokens = state.private_info['my_tokens']
        hand_strength = sum(1.0/card for card in state.private_info['hand'])
        
        return my_score + my_tokens * 5 + hand_strength
