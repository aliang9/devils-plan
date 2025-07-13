from typing import Dict, Any

from .data_structures import RemoveOneState, RemoveOnePlayer


class RemoveOneGame(RemoveOneState):
    """Remove One game implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        players = tuple(
            RemoveOnePlayer(
                player_id=i,
                hand=tuple(range(1, config.get('hand_size', 9))),
                holding_box=()
            )
            for i in range(config.get('num_players', 7))
        )
        
        super().__init__(
            players=players,
            round_num=1,
            phase='select',
            advancement_rounds=tuple(config.get('advancement_rounds', [3, 6, 9, 12, 18])),
            config=config
        )
