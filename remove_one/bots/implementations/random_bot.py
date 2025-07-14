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
            from ...games.remove_one.data_structures import RemoveOneAction
            hand = list(state.private_info.get('hand', [1, 2, 3, 4, 5, 6, 7, 8]))
            if len(hand) >= 2:
                return RemoveOneAction('select_cards', cards=(hand[0], hand[1]))
            else:
                return RemoveOneAction('select_cards', cards=(1, 2))
        return random.choice(state.legal_actions)
