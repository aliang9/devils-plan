from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .game_state import GameState


class GameAction(ABC):
    """Base class for all player actions"""
    
    @abstractmethod
    def is_valid(self, state: 'GameState', player_id: int) -> bool:
        """Validate if action is legal in current state"""
        pass
