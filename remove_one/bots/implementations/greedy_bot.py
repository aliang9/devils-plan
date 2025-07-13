from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...core.game_state import BotGameState
    from ...core.game_action import GameAction

from ..base_bot import Bot
from ...games.remove_one.data_structures import RemoveOneAction


class GreedyBot(Bot):
    """Always plays lowest available cards"""
    
    def get_action(self, state: 'BotGameState', player_id: int) -> 'GameAction':
        if state.public_info['phase'] == 'select':
            hand = sorted(state.private_info['hand'])
            return RemoveOneAction('select_cards', cards=(hand[0], hand[1]))
        
        elif state.public_info['phase'] == 'choose':
            my_revealed = state.public_info['revealed_cards'][player_id]
            return RemoveOneAction('choose_final', final_card=min(my_revealed))
        
        return state.legal_actions[0] if state.legal_actions else None
