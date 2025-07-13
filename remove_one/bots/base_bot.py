from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.game_state import BotGameState
    from ..core.game_action import GameAction


class Bot(ABC):
    """Abstract bot interface"""
    
    def __init__(self, name: str):
        self.name = name
        self.game_history = []
    
    @abstractmethod
    def get_action(self, state: 'BotGameState', player_id: int) -> 'GameAction':
        """Choose action based on visible game state"""
        pass
    
    def observe_action(self, state: 'BotGameState', player_id: int, action: 'GameAction'):
        """Called after each action for learning/tracking (optional override)"""
        pass
    
    def game_ended(self, final_state: 'BotGameState', results: dict):
        """Called when game ends (optional override)"""
        pass
