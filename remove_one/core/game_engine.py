import random
import time
from contextlib import contextmanager
from typing import List, Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..bots.base_bot import Bot
    from .game_state import GameState

from ..validation.validator import GameValidator
from ..utils.analytics import GameAnalytics
from ..utils.profiler import BotProfiler


class GameEngine:
    """Core simulation engine - extensible to multiple games"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.validator = GameValidator()
        self.analytics = GameAnalytics()
        self.profiler = BotProfiler() if config.get('enable_profiling') else None
    
    def run_game(self, game_class, bots: List['Bot'], seed: Optional[int] = None) -> Dict[str, Any]:
        """Execute a single game and return results"""
        if seed is not None:
            random.seed(seed)
        
        if not self._validate_setup(game_class, bots):
            raise ValueError("Invalid game setup")
        
        state = game_class(self.config)
        history = []
        
        while not state.is_terminal():
            current_player = state.get_current_player()
            
            if current_player is None:
                actions = self._collect_simultaneous_actions(state, bots)
                state = state.apply_simultaneous_actions(actions)
                
                for player_id, action in actions.items():
                    history.append((state.copy(), player_id, action))
                    self._notify_bots(bots, state, player_id, action)
            else:
                bot_view = state.get_bot_view(current_player)
                
                with self._profile_decision(bots[current_player].name):
                    action = bots[current_player].get_action(bot_view, current_player)
                
                if not action.is_valid(state, current_player):
                    raise ValueError(f"Illegal action by {bots[current_player].name}")
                
                state = state.apply_action(action, current_player)
                history.append((state.copy(), current_player, action))
                self._notify_bots(bots, state, current_player, action)
        
        results = state.get_results()
        self._notify_game_end(bots, state, results)
        
        return {
            'results': results,
            'history': history,
            'stats': self.analytics.process_game(history, results),
            'winner': max(results.items(), key=lambda x: x[1])[0],
        }
    
    def _collect_simultaneous_actions(self, state: 'GameState', bots: List['Bot']) -> Dict[int, Any]:
        """Collect actions from all active players simultaneously"""
        actions = {}
        for player_id, bot in enumerate(bots):
            if not state.is_player_eliminated(player_id):
                bot_view = state.get_bot_view(player_id)
                with self._profile_decision(bot.name):
                    actions[player_id] = bot.get_action(bot_view, player_id)
        return actions
    
    def _validate_setup(self, game_class, bots: List['Bot']) -> bool:
        """Validate game setup"""
        return self.validator.validate_game_setup(game_class, self.config)
    
    def _notify_bots(self, bots: List['Bot'], state: 'GameState', player_id: int, action):
        """Notify all bots of an action"""
        for bot_id, bot in enumerate(bots):
            if not state.is_player_eliminated(bot_id):
                bot_view = state.get_bot_view(bot_id)
                bot.observe_action(bot_view, player_id, action)
    
    def _notify_game_end(self, bots: List['Bot'], state: 'GameState', results: Dict[int, float]):
        """Notify all bots that game has ended"""
        for bot_id, bot in enumerate(bots):
            bot_view = state.get_bot_view(bot_id)
            bot.game_ended(bot_view, results)
    
    @contextmanager
    def _profile_decision(self, bot_name: str):
        """Context manager for profiling bot decisions"""
        if self.profiler:
            with self.profiler.profile_decision(bot_name):
                yield
        else:
            yield
