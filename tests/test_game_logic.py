import unittest
from remove_one.games.remove_one.game import RemoveOneGame
from remove_one.games.remove_one.data_structures import RemoveOneAction
from remove_one.utils.config import RemoveOneConfig


class TestRemoveOneGameLogic(unittest.TestCase):
    """Test core game logic and state transitions"""
    
    def setUp(self):
        self.config = RemoveOneConfig()
        self.game = RemoveOneGame(self.config.to_dict())
    
    def test_initial_state(self):
        """Test game starts in correct initial state"""
        self.assertEqual(self.game.round_num, 1)
        self.assertEqual(self.game.phase, 'select')
        self.assertEqual(len(self.game.players), 7)
        
        for player in self.game.players:
            self.assertEqual(len(player.hand), 8)
            self.assertEqual(len(player.holding_box), 0)
            self.assertEqual(player.score, 0)
            self.assertFalse(player.eliminated)
    
    def test_card_selection_validation(self):
        """Test card selection action validation"""
        player_id = 0
        hand = self.game.players[player_id].hand
        
        valid_action = RemoveOneAction('select_cards', cards=(hand[0], hand[1]))
        self.assertTrue(valid_action.is_valid(self.game, player_id))
        
        invalid_action = RemoveOneAction('select_cards', cards=(9, 10))
        self.assertFalse(invalid_action.is_valid(self.game, player_id))
    
    def test_phase_transitions(self):
        """Test proper phase transitions"""
        actions = {}
        for player_id in range(7):
            hand = self.game.players[player_id].hand
            actions[player_id] = RemoveOneAction('select_cards', cards=(hand[0], hand[1]))
        
        new_state = self.game.apply_simultaneous_actions(actions)
        self.assertEqual(new_state.phase, 'choose')
    
    def test_card_conservation(self):
        """Test that cards are conserved throughout the game"""
        total_cards = sum(len(p.hand) + len(p.holding_box) for p in self.game.players)
        total_cards += len(self.game.discard_pile)
        
        expected_cards = 7 * 8
        self.assertEqual(total_cards, expected_cards)
    
    def test_elimination_logic(self):
        """Test player elimination at advancement rounds"""
        pass


class TestBotImplementations(unittest.TestCase):
    """Test bot implementations"""
    
    def setUp(self):
        self.config = RemoveOneConfig()
        self.game = RemoveOneGame(self.config.to_dict())
    
    def test_random_bot_actions(self):
        """Test RandomBot produces valid actions"""
        from remove_one.bots.implementations.random_bot import RandomBot
        
        bot = RandomBot("TestBot")
        bot_view = self.game.get_bot_view(0)
        action = bot.get_action(bot_view, 0)
        
        self.assertTrue(action.is_valid(self.game, 0))
    
    def test_greedy_bot_actions(self):
        """Test GreedyBot produces valid actions"""
        from remove_one.bots.implementations.greedy_bot import GreedyBot
        
        bot = GreedyBot("TestBot")
        bot_view = self.game.get_bot_view(0)
        action = bot.get_action(bot_view, 0)
        
        self.assertTrue(action.is_valid(self.game, 0))


if __name__ == '__main__':
    unittest.main()
