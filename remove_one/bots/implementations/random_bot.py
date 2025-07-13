import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...core.game_state import BotGameState
    from ...core.game_action import GameAction

from ..base_bot import Bot


class RandomBot(Bot):
    """Baseline random decision maker"""
    
    def get_action(self, state: 'BotGameState', player_id: int) -> 'GameAction':
        if not state.legal_actions:
            raise ValueError("No legal actions available")
        return random.choice(state.legal_actions)
