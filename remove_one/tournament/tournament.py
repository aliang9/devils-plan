import time
from itertools import combinations
from collections import defaultdict
from typing import List, Dict, Any, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from ..bots.base_bot import Bot

from ..core.game_engine import GameEngine
from ..games.remove_one.game import RemoveOneGame
from ..utils.config import RemoveOneConfig
from ..utils.analytics import GameAnalytics


class Tournament:
    """Manage bot competitions and rankings"""
    
    def __init__(self, bots: List['Bot'], config=None):
        self.bots = bots
        self.config = config or RemoveOneConfig()
        self.results = TournamentResults()
        self.game_engine = GameEngine(self.config.to_dict() if hasattr(self.config, 'to_dict') else self.config)
        self.analytics = GameAnalytics()
        self.elo_ratings = {bot.name: 1000.0 for bot in bots}
    
    def run_tournament(self, tournament_type='round_robin', games_per_matchup=10):
        """Run tournament with specified type"""
        if tournament_type == 'round_robin':
            return self.run_round_robin(games_per_matchup)
        elif tournament_type == 'elimination':
            return self.run_elimination_bracket()
        elif tournament_type == 'league':
            return self.run_league_season()
        else:
            return self.run_round_robin(games_per_matchup)
    
    def run_round_robin(self, games_per_matchup: int = 10) -> Dict[str, Any]:
        """Every bot combination plays multiple games"""
        total_matchups = 0
        total_games = 0
        
        max_players = min(len(self.bots), 4)  # Limit to 4 players for better performance
        if len(self.bots) >= max_players:
            bot_combinations = list(combinations(range(len(self.bots)), max_players))
        else:
            bot_combinations = [tuple(range(len(self.bots)))]
        
        for combo in bot_combinations:
            selected_bots = [self.bots[i] for i in combo]
            
            for game_num in range(games_per_matchup):
                config_dict = self.config.to_dict() if hasattr(self.config, 'to_dict') else self.config
                config_dict['num_players'] = len(selected_bots)
                
                game = RemoveOneGame(config_dict)
                
                result = self._play_match_simple(selected_bots, game)
                
                self.results.add_game_result(combo, result)
                total_games += 1
            
            total_matchups += 1
        
        return {
            'total_matchups': total_matchups,
            'total_games': total_games,
            'results': self.results.get_summary(),
        }
    
    def _play_match_simple(self, bots, game):
        """Play a simple match between bots"""
        current_state = game
        
        while not current_state.is_terminal():
            if current_state.phase == 'select':
                actions = {}
                for i, bot in enumerate(bots):
                    if i < len(current_state.players) and not current_state.players[i].eliminated:
                        bot_state = current_state.get_bot_view(i)
                        action = bot.get_action(bot_state, i)
                        actions[i] = action
                
                current_state = current_state.apply_simultaneous_actions(actions)
                
            elif current_state.phase == 'choose':
                actions = {}
                for i, bot in enumerate(bots):
                    if i < len(current_state.players) and not current_state.players[i].eliminated:
                        bot_state = current_state.get_bot_view(i)
                        action = bot.get_action(bot_state, i)
                        actions[i] = action
                
                current_state = current_state.apply_simultaneous_actions(actions)
        
        results = current_state.get_results()
        winner = max(results.items(), key=lambda x: x[1])[0] if results else 0
        
        return {
            'winner': winner,
            'results': results,
            'final_state': current_state
        }
    
    def _play_match(self, bot1, bot2):
        """Play a match between two bots"""
        config_dict = self.config.to_dict() if hasattr(self.config, 'to_dict') else self.config
        config_dict['num_players'] = 2
        
        game = RemoveOneGame(config_dict)
        bots = [bot1, bot2]
        
        result = self._play_match_simple(bots, game)
        winner_id = result['winner']
        
        return bots[winner_id]
    
    def run_elimination_bracket(self) -> Dict[str, Any]:
        """Single/double elimination tournament"""
        remaining_bots = [bot for bot in self.bots if not getattr(bot, 'eliminated', False)]
        if len(remaining_bots) <= 1:
            return {
                'tournament_type': 'elimination_bracket',
                'champion': remaining_bots[0] if remaining_bots else None,
                'champion_name': remaining_bots[0].name if remaining_bots else 'None',
                'bracket_results': [],
                'total_rounds': 0
            }
        
        bracket = remaining_bots[:]
        bracket_results = []
        round_num = 1
        
        while len(bracket) > 1:
            next_round = []
            for i in range(0, len(bracket), 2):
                if i + 1 < len(bracket):
                    winner = self._play_match(bracket[i], bracket[i + 1])
                    next_round.append(winner)
                    bracket_results.append({
                        'round': round_num,
                        'participants': [bracket[i].name, bracket[i + 1].name],
                        'winner': winner.name
                    })
                else:
                    next_round.append(bracket[i])
            bracket = next_round
            round_num += 1
        
        champion = bracket[0] if bracket else None
        champion_idx = self.bots.index(champion) if champion else -1
        
        return {
            'tournament_type': 'elimination_bracket',
            'champion': champion_idx,
            'champion_name': champion.name if champion else 'None',
            'bracket_results': bracket_results,
            'total_rounds': round_num - 1
        }
    
    def run_league_season(self, rounds: int = 10) -> Dict[str, Any]:
        """Season-long competition with rankings"""
        for round_num in range(rounds):
            self._run_league_round(round_num)
        
        return self.results.get_final_standings()
    
    def _run_league_round(self, round_num: int = 0):
        """Run a single league round (all vs all)"""
        remaining_bots = [bot for bot in self.bots if not getattr(bot, 'eliminated', False)]
        for i, bot1 in enumerate(remaining_bots):
            for j, bot2 in enumerate(remaining_bots[i + 1:], i + 1):
                winner = self._play_match(bot1, bot2)
                if winner == bot1:
                    self.elo_ratings[bot1.name] += 10
                    self.elo_ratings[bot2.name] -= 10
                else:
                    self.elo_ratings[bot2.name] += 10
                    self.elo_ratings[bot1.name] -= 10


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
