import unittest
from remove_one.tournament.tournament import Tournament, TournamentResults
from remove_one.bots.implementations.random_bot import RandomBot
from remove_one.bots.implementations.greedy_bot import GreedyBot
from remove_one.utils.config import RemoveOneConfig


class TestTournamentSystem(unittest.TestCase):
    """Test tournament mechanics and ELO ratings"""
    
    def setUp(self):
        self.config = RemoveOneConfig()
        self.config.games_per_match = 2  # Reduced for testing
        self.bots = [
            RandomBot("Random1"),
            RandomBot("Random2"),
            GreedyBot("Greedy1"),
            GreedyBot("Greedy2"),
            RandomBot("Random3"),
            RandomBot("Random4"),
            RandomBot("Random5")
        ]
        self.tournament = Tournament(self.bots, self.config)
    
    def test_round_robin_tournament(self):
        """Test round robin tournament execution"""
        small_bots = self.bots[:4]  # Only use 4 bots instead of 7
        small_tournament = Tournament(small_bots, self.config)
        
        results = small_tournament.run_round_robin(games_per_matchup=1)
        
        self.assertIn('total_matchups', results)
        self.assertIn('total_games', results)
        self.assertIn('results', results)
        self.assertGreater(results['total_games'], 0)
    
    def test_elimination_bracket_tournament(self):
        """Test elimination bracket tournament"""
        results = self.tournament.run_elimination_bracket()
        
        self.assertEqual(results['tournament_type'], 'elimination_bracket')
        self.assertIn('champion', results)
        self.assertIn('champion_name', results)
        self.assertIn('bracket_results', results)
        
        champion_idx = results['champion']
        self.assertGreaterEqual(champion_idx, 0)
        self.assertLess(champion_idx, len(self.bots))
        
        self.assertGreater(len(results['bracket_results']), 0)
    
    def test_league_season_tournament(self):
        """Test league season tournament"""
        results = self.tournament.run_league_season(rounds=2)
        
        self.assertIsInstance(results, dict)
        
        for bot_idx, stats in results.items():
            self.assertIn('games_played', stats)
            self.assertIn('win_rate', stats)
            self.assertIn('avg_score', stats)
    
    def test_tournament_results_tracking(self):
        """Test tournament results tracking accuracy"""
        results = TournamentResults()
        
        bot_indices = (0, 1, 2, 3, 4, 5, 6)
        game_result = {
            'winner': 2,
            'results': {0: 50, 1: 40, 2: 100, 3: 30, 4: 20, 5: 10, 6: 5}
        }
        
        results.add_game_result(bot_indices, game_result)
        
        summary = results.get_summary()
        
        self.assertEqual(summary[2]['total_wins'], 1)
        self.assertEqual(summary[2]['win_rate'], 1.0)
        
        for bot_idx in [0, 1, 3, 4, 5, 6]:
            self.assertEqual(summary[bot_idx]['total_wins'], 0)
            self.assertEqual(summary[bot_idx]['win_rate'], 0.0)
    
    def test_elo_rating_calculation(self):
        """Test ELO rating calculation system"""
        results = TournamentResults()
        
        bot_indices = (0, 1, 2, 3, 4, 5, 6)
        
        for i in range(5):
            game_result = {
                'winner': 0,
                'results': {0: 100, 1: 50, 2: 40, 3: 30, 4: 20, 5: 10, 6: 5}
            }
            results.add_game_result(bot_indices, game_result)
        
        elo_ratings = results.generate_elo_ratings()
        
        self.assertGreater(elo_ratings[0], 1500)
        
        for bot_idx in [1, 2, 3, 4, 5, 6]:
            self.assertLess(elo_ratings[bot_idx], 1500)
    
    def test_head_to_head_tracking(self):
        """Test head-to-head record tracking"""
        results = TournamentResults()
        
        bot_indices = (0, 1, 2, 3, 4, 5, 6)
        
        game_result = {
            'winner': 0,
            'results': {0: 100, 1: 50, 2: 40, 3: 30, 4: 20, 5: 10, 6: 5}
        }
        results.add_game_result(bot_indices, game_result)
        
        for opponent_idx in [1, 2, 3, 4, 5, 6]:
            self.assertEqual(results.head_to_head[0][opponent_idx], 1)
            self.assertEqual(results.head_to_head[opponent_idx][0], 0)


if __name__ == '__main__':
    unittest.main()
