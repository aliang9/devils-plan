import time
from itertools import combinations
from collections import defaultdict
from typing import List, Dict, Any, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from ..bots.base_bot import Bot

from ..core.game_engine import GameEngine
from ..games.remove_one.game import RemoveOneGame
from ..utils.config import RemoveOneConfig


class Tournament:
    """Manage bot competitions and rankings"""
    
    def __init__(self, bots: List['Bot'], config: RemoveOneConfig):
        self.bots = bots
        self.config = config
        self.results = TournamentResults()
        self.game_engine = GameEngine(config.to_dict())
    
    def run_round_robin(self, games_per_matchup: int = 10) -> Dict[str, Any]:
        """Every bot combination plays multiple games"""
        total_matchups = 0
        total_games = 0
        
        bot_combinations = list(combinations(range(len(self.bots)), 7))
        
        for combo in bot_combinations:
            selected_bots = [self.bots[i] for i in combo]
            
            for game_num in range(games_per_matchup):
                seed = self.config.random_seed + total_games if self.config.random_seed else None
                
                result = self.game_engine.run_game(
                    RemoveOneGame, 
                    selected_bots, 
                    seed=seed
                )
                
                self.results.add_game_result(combo, result)
                total_games += 1
            
            total_matchups += 1
        
        return {
            'total_matchups': total_matchups,
            'total_games': total_games,
            'results': self.results.get_summary(),
        }
    
    def run_elimination_bracket(self) -> Dict[str, Any]:
        """Single/double elimination tournament"""
        pass
    
    def run_league_season(self, rounds: int = 10) -> Dict[str, Any]:
        """Season-long competition with rankings"""
        for round_num in range(rounds):
            self._run_league_round(round_num)
        
        return self.results.get_final_standings()
    
    def _run_league_round(self, round_num: int):
        """Run a single league round"""
        pass


class TournamentResults:
    """Track and analyze tournament performance"""
    
    def __init__(self):
        self.game_results = []
        self.bot_stats = defaultdict(lambda: {
            'games_played': 0,
            'wins': 0,
            'total_score': 0,
            'eliminations': defaultdict(int),
        })
        self.head_to_head = defaultdict(lambda: defaultdict(int))
    
    def add_game_result(self, bot_indices: Tuple[int, ...], result: Dict[str, Any]):
        """Record result of a single game"""
        self.game_results.append({
            'bot_indices': bot_indices,
            'result': result,
            'timestamp': time.time(),
        })
        
        winner_id = result['winner']
        winner_bot_index = bot_indices[winner_id]
        
        for i, bot_index in enumerate(bot_indices):
            self.bot_stats[bot_index]['games_played'] += 1
            self.bot_stats[bot_index]['total_score'] += result['results'][i]
            
            if i == winner_id:
                self.bot_stats[bot_index]['wins'] += 1
        
        for i, bot_i in enumerate(bot_indices):
            for j, bot_j in enumerate(bot_indices):
                if i != j:
                    if i == winner_id:
                        self.head_to_head[bot_i][bot_j] += 1
    
    def get_summary(self) -> Dict[str, Any]:
        """Generate tournament summary"""
        summary = {}
        
        for bot_index, stats in self.bot_stats.items():
            games = stats['games_played']
            if games > 0:
                summary[bot_index] = {
                    'games_played': games,
                    'win_rate': stats['wins'] / games,
                    'avg_score': stats['total_score'] / games,
                    'total_wins': stats['wins'],
                }
        
        return summary
    
    def get_final_standings(self) -> Dict[str, Any]:
        """Get final tournament standings"""
        return self.get_summary()
    
    def generate_elo_ratings(self, initial_rating: int = 1500) -> Dict[int, float]:
        """Calculate ELO ratings based on game results"""
        ratings = {bot_idx: initial_rating for bot_idx in self.bot_stats.keys()}
        
        def update_elo(winner_rating: float, loser_rating: float, k_factor: float = 32) -> Tuple[float, float]:
            expected_winner = 1 / (1 + 10**((loser_rating - winner_rating) / 400))
            expected_loser = 1 - expected_winner
            
            new_winner_rating = winner_rating + k_factor * (1 - expected_winner)
            new_loser_rating = loser_rating + k_factor * (0 - expected_loser)
            
            return new_winner_rating, new_loser_rating
        
        for game_data in self.game_results:
            bot_indices = game_data['bot_indices']
            winner_id = game_data['result']['winner']
            winner_bot_index = bot_indices[winner_id]
            
            for i, bot_index in enumerate(bot_indices):
                if i != winner_id:
                    new_winner_rating, new_loser_rating = update_elo(
                        ratings[winner_bot_index], 
                        ratings[bot_index]
                    )
                    ratings[winner_bot_index] = new_winner_rating
                    ratings[bot_index] = new_loser_rating
        
        return ratings
