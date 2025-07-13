from typing import Dict, Any


class RemoveOneConfig:
    """Comprehensive configuration for Remove One game"""
    
    def __init__(self):
        self.num_players = 7
        self.hand_size = 8
        self.advancement_rounds = [3, 6, 9, 12, 18]
        self.enable_victory_tokens = True
        self.enable_holding_box = True
        
        self.games_per_match = 100
        self.enable_logging = False
        self.save_replays = True
        self.enable_profiling = False
        self.random_seed = None
        self.parallel_execution = False
        
        self.strict_validation = True
        self.timeout_seconds = 5.0
        self.max_memory_mb = 100
        
        self.track_decision_times = True
        self.track_win_patterns = True
        self.generate_reports = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for game engine"""
        return {
            'num_players': self.num_players,
            'hand_size': self.hand_size,
            'advancement_rounds': self.advancement_rounds,
            'enable_victory_tokens': self.enable_victory_tokens,
            'enable_holding_box': self.enable_holding_box,
            'games_per_match': self.games_per_match,
            'enable_logging': self.enable_logging,
            'save_replays': self.save_replays,
            'enable_profiling': self.enable_profiling,
            'random_seed': self.random_seed,
            'parallel_execution': self.parallel_execution,
            'strict_validation': self.strict_validation,
            'timeout_seconds': self.timeout_seconds,
            'max_memory_mb': self.max_memory_mb,
            'track_decision_times': self.track_decision_times,
            'track_win_patterns': self.track_win_patterns,
            'generate_reports': self.generate_reports,
        }
