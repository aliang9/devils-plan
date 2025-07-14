import unittest
from remove_one.games.remove_one.game import RemoveOneGame
from remove_one.games.remove_one.data_structures import RemoveOnePlayer
from remove_one.utils.config import RemoveOneConfig


class TestEliminationLogic(unittest.TestCase):
    """Test player elimination logic"""
    
    def setUp(self):
        self.config = RemoveOneConfig()
        self.game = RemoveOneGame(self.config.to_dict())
    
    def test_advancement_round_elimination(self):
        """Test elimination at advancement rounds 3, 6, 9, 12"""
        test_players = list(self.game.players)
        
        test_players[0] = RemoveOnePlayer(
            player_id=0, hand=test_players[0].hand, holding_box=test_players[0].holding_box,
            score=20, victory_tokens=test_players[0].victory_tokens, eliminated=False,
            last_victory_round=test_players[0].last_victory_round
        )
        
        for i in range(1, 7):
            test_players[i] = RemoveOnePlayer(
                player_id=i, hand=test_players[i].hand, holding_box=test_players[i].holding_box,
                score=10, victory_tokens=test_players[i].victory_tokens, eliminated=False,
                last_victory_round=test_players[i].last_victory_round
            )
        
        test_state = self.game.copy_with_updates(
            round_num=3,
            players=tuple(test_players)
        )
        
        eliminated_state = test_state._handle_elimination(test_state)
        
        eliminated_count = sum(1 for p in eliminated_state.players if p.eliminated)
        self.assertEqual(eliminated_count, 1)
        
        self.assertTrue(eliminated_state.players[0].eliminated)
    
    def test_game_termination_conditions(self):
        """Test various game termination conditions"""
        test_players = list(self.game.players)
        for i in range(6):
            test_players[i] = RemoveOnePlayer(
                player_id=test_players[i].player_id,
                hand=test_players[i].hand,
                holding_box=test_players[i].holding_box,
                score=test_players[i].score,
                victory_tokens=test_players[i].victory_tokens,
                eliminated=True,
                last_victory_round=test_players[i].last_victory_round
            )
        
        test_state = self.game.copy_with_updates(players=tuple(test_players))
        self.assertTrue(test_state.is_terminal())


if __name__ == '__main__':
    unittest.main()
