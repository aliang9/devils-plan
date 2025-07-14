import unittest
from remove_one.tournament.tournament import Tournament, TournamentResults
from remove_one.bots.implementations.random_bot import RandomBot
from remove_one.utils.config import RemoveOneConfig


class TestTournament(unittest.TestCase):
    """Test tournament system"""
    
    def setUp(self):
        self.config = RemoveOneConfig()
        self.config.games_per_match = 5
        self.bots = [RandomBot(f"Bot_{i}") for i in range(7)]
        self.tournament = Tournament(self.bots, self.config)
    
    def test_tournament_results_tracking(self):
        """Test tournament results are tracked correctly"""
        results = TournamentResults()
        
        game_result = {
            'winner': 0,
            'results': {0: 100, 1: 50, 2: 30, 3: 20, 4: 10, 5: 5, 6: 0}
        }
        
        bot_indices = (0, 1, 2, 3, 4, 5, 6)
        results.add_game_result(bot_indices, game_result)
        
        summary = results.get_summary()
        self.assertEqual(summary[0]['total_wins'], 1)
        self.assertEqual(summary[0]['win_rate'], 1.0)
    
    def test_elo_rating_calculation(self):
        """Test ELO rating calculation"""
        results = TournamentResults()
        
        game_result = {
            'winner': 0,
            'results': {0: 100, 1: 50, 2: 30, 3: 20, 4: 10, 5: 5, 6: 0}
        }
        
        bot_indices = (0, 1, 2, 3, 4, 5, 6)
        results.add_game_result(bot_indices, game_result)
        
        elo_ratings = results.generate_elo_ratings()
        self.assertGreater(elo_ratings[0], 1500)
        self.assertLess(elo_ratings[1], 1500)


if __name__ == '__main__':
    unittest.main()
