from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .game_action import GameAction


class BotGameState:
    """Filtered game state containing only information visible to a specific player"""
    
    def __init__(self, public_info: Dict, private_info: Dict, legal_actions: List['GameAction']):
        self.public_info = public_info
        self.private_info = private_info
        self.legal_actions = legal_actions


class GameState(ABC):
    """Immutable game state representation"""
    
    @abstractmethod
    def get_legal_actions(self, player_id: int) -> List['GameAction']:
        """Return all valid actions for specified player"""
        pass
    
    @abstractmethod
    def apply_action(self, action: 'GameAction', player_id: int) -> 'GameState':
        """Return new state after applying action"""
        pass
    
    @abstractmethod
    def apply_simultaneous_actions(self, actions: Dict[int, 'GameAction']) -> 'GameState':
        """Return new state after applying simultaneous actions"""
        pass
    
    @abstractmethod
    def is_terminal(self) -> bool:
        """Check if game has ended"""
        pass
    
    @abstractmethod
    def get_results(self) -> Dict[int, float]:
        """Return final scores/rankings for all players"""
        pass
    
    @abstractmethod
    def get_current_player(self) -> Optional[int]:
        """Return player whose turn it is (None if simultaneous)"""
        pass
    
    @abstractmethod
    def get_bot_view(self, player_id: int) -> BotGameState:
        """Return filtered state with only information visible to specified player"""
        pass
    
    @abstractmethod
    def is_player_eliminated(self, player_id: int) -> bool:
        """Check if player is eliminated"""
        pass
    
    @abstractmethod
    def copy(self) -> 'GameState':
        """Return deep copy of current state"""
        pass
