import unittest
from remove_one.games.remove_one.game import RemoveOneGame
from remove_one.games.remove_one.data_structures import RemoveOneAction
from remove_one.utils.config import RemoveOneConfig
from remove_one.bots.implementations.random_bot import RandomBot
from remove_one.bots.implementations.greedy_bot import GreedyBot
from remove_one.bots.implementations.card_counting_bot import CardCountingBot
from remove_one.bots.implementations.minimax_bot import MinimaxBot


class TestBotStrategies(unittest.TestCase):
    """Test different bot strategy implementations"""
    
    def setUp(self):
        self.config = RemoveOneConfig()
        self.game = RemoveOneGame(self.config.to_dict())
    
    def test_random_bot_consistency(self):
        """Test RandomBot produces valid actions consistently"""
        bot = RandomBot("TestRandom")
        
        for _ in range(10):
            bot_view = self.game.get_bot_view(0)
            action = bot.get_action(bot_view, 0)
            self.assertTrue(action.is_valid(self.game, 0))
            self.assertIn(action, bot_view.legal_actions)
    
    def test_greedy_bot_strategy(self):
        """Test GreedyBot always chooses lowest cards"""
        bot = GreedyBot("TestGreedy")
        bot_view = self.game.get_bot_view(0)
        action = bot.get_action(bot_view, 0)
        
        hand = sorted(bot_view.private_info['hand'])
        expected_cards = (hand[0], hand[1])
        
        self.assertEqual(action.cards, expected_cards)
    
    def test_card_counting_bot_memory(self):
        """Test CardCountingBot tracks opponent cards"""
        bot = CardCountingBot("TestCounter")
        
        self.assertEqual(len(bot.opponent_cards), 0)
        
        bot_view = self.game.get_bot_view(0)
        observed_action = RemoveOneAction('select_cards', cards=(1, 2))
        
        bot.observe_action(bot_view, 1, observed_action)
        
        self.assertIn(1, bot.opponent_cards[1])
        self.assertIn(2, bot.opponent_cards[1])
    
    def test_minimax_bot_depth(self):
        """Test MinimaxBot respects depth parameter"""
        shallow_bot = MinimaxBot("Shallow", depth=1)
        deep_bot = MinimaxBot("Deep", depth=3)
        
        self.assertEqual(shallow_bot.depth, 1)
        self.assertEqual(deep_bot.depth, 3)
        
        bot_view = self.game.get_bot_view(0)
        shallow_action = shallow_bot.get_action(bot_view, 0)
        deep_action = deep_bot.get_action(bot_view, 0)
        
        self.assertTrue(shallow_action.is_valid(self.game, 0))
        self.assertTrue(deep_action.is_valid(self.game, 0))
    
    def test_bot_action_validity_across_phases(self):
        """Test all bots produce valid actions in different game phases"""
        bots = [
            RandomBot("Random"),
            GreedyBot("Greedy"),
            CardCountingBot("Counter"),
            MinimaxBot("Minimax")
        ]
        
        for bot in bots:
            bot_view = self.game.get_bot_view(0)
            action = bot.get_action(bot_view, 0)
            self.assertTrue(action.is_valid(self.game, 0))
            self.assertEqual(action.action_type, 'select_cards')
        
        actions = {}
        for player_id in range(7):
            hand = self.game.players[player_id].hand
            actions[player_id] = RemoveOneAction('select_cards', cards=(hand[0], hand[1]))
        
        choose_state = self.game.apply_simultaneous_actions(actions)
        
        for bot in bots:
            bot_view = choose_state.get_bot_view(0)
            action = bot.get_action(bot_view, 0)
            self.assertTrue(action.is_valid(choose_state, 0))
            self.assertEqual(action.action_type, 'choose_final')


if __name__ == '__main__':
    unittest.main()
