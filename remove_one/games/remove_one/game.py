from typing import Dict, Any

from .data_structures import RemoveOneState, RemoveOnePlayer


class RemoveOneGame:
    """Remove One game factory - creates initial game state"""
    
    def __init__(self, config: Dict[str, Any]):
        players = tuple(
            RemoveOnePlayer(
                player_id=i,
                hand=tuple(range(1, config.get('hand_size', 8) + 1)),
                holding_box=()
            )
            for i in range(config.get('num_players', 7))
        )
        
        self._state = RemoveOneState(
            players=players,
            round_num=1,
            phase='select',
            revealed_cards={},
            final_choices={},
            advancement_rounds=tuple(config.get('advancement_rounds', [3, 6, 9, 12, 18])),
            discard_pile=(),
            config=config
        )
    
    def __getattr__(self, name):
        """Delegate all attribute access to the underlying state"""
        return getattr(self._state, name)
    
    def copy(self):
        """Return the underlying state for copying"""
        return self._state.copy()
    
    def copy_with_updates(self, **kwargs):
        """Return new state with updates"""
        return self._state.copy_with_updates(**kwargs)
