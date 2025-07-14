import unittest
from remove_one.core.game_engine import GameEngine
from remove_one.games.remove_one.game import RemoveOneGame
from remove_one.bots.implementations.random_bot import RandomBot
from remove_one.bots.implementations.greedy_bot import GreedyBot
from remove_one.utils.config import RemoveOneConfig
from remove_one.validation.validator import GameValidator


class TestFullGameIntegration(unittest.TestCase):
    """Integration tests for complete game scenarios"""
    
    def setUp(self):
        self.config = RemoveOneConfig()
        self.engine = GameEngine(self.config.to_dict())
        self.validator = GameValidator()
    
    def test_complete_game_execution(self):
        """Test a complete game from start to finish"""
        bots = [RandomBot(f"Random_{i}") for i in range(7)]
        
        result = self.engine.run_game(RemoveOneGame, bots, seed=42)
        
        self.assertIn('winner', result)
        self.assertIn('results', result)
        self.assertIn('history', result)
        
        winner = result['winner']
        self.assertGreaterEqual(winner, 0)
        self.assertLess(winner, 7)
        
        self.assertEqual(len(result['results']), 7)
        
        self.assertGreater(len(result['history']), 0)
    
    def test_mixed_bot_game(self):
        """Test game with different bot types"""
        bots = [
            RandomBot("Random1"),
            RandomBot("Random2"),
            GreedyBot("Greedy1"),
            GreedyBot("Greedy2"),
            RandomBot("Random3"),
            RandomBot("Random4"),
            RandomBot("Random5")
        ]
        
        result = self.engine.run_game(RemoveOneGame, bots, seed=123)
        
        self.assertIn('winner', result)
        self.assertTrue(0 <= result['winner'] < 7)
    
    def test_game_state_consistency(self):
        """Test game state remains consistent throughout"""
        bots = [RandomBot(f"Test_{i}") for i in range(7)]
        
        result = self.engine.run_game(RemoveOneGame, bots, seed=456)
        
        if result['history']:
            final_state = result['history'][-1][0]
            errors = self.validator.validate_state_consistency(final_state)
            self.assertEqual(len(errors), 0, f"State consistency errors: {errors}")
    
    def test_multiple_games_stability(self):
        """Test system stability across multiple games"""
        bots = [RandomBot(f"Stable_{i}") for i in range(7)]
        
        for game_num in range(5):
            with self.subTest(game=game_num):
                result = self.engine.run_game(RemoveOneGame, bots, seed=game_num)
                
                self.assertIn('winner', result)
                self.assertIn('results', result)
                
                self.assertTrue(0 <= result['winner'] < 7)
    
    def test_game_termination_conditions(self):
        """Test various game termination scenarios"""
        bots = [RandomBot(f"Term_{i}") for i in range(7)]
        
        for seed in range(10):
            result = self.engine.run_game(RemoveOneGame, bots, seed=seed)
            
            self.assertIn('winner', result)
            
            if result['history']:
                final_state = result['history'][-1][0]
                self.assertTrue(final_state.is_terminal())
    
    def test_score_calculation_accuracy(self):
        """Test that final scores are calculated correctly"""
        bots = [RandomBot(f"Score_{i}") for i in range(7)]
        
        result = self.engine.run_game(RemoveOneGame, bots, seed=789)
        
        for player_id, score in result['results'].items():
            self.assertGreaterEqual(score, 0)
        
        winner_score = result['results'][result['winner']]
        
        if result['history']:
            final_state = result['history'][-1][0]
            active_players = [i for i, p in enumerate(final_state.players) if not p.eliminated]
            
            if len(active_players) == 1:
                self.assertEqual(result['winner'], active_players[0])
            else:
                self.assertGreaterEqual(winner_score, 0)


if __name__ == '__main__':
    unittest.main()
