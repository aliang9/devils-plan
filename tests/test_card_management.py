import unittest
from remove_one.games.remove_one.game import RemoveOneGame
from remove_one.games.remove_one.data_structures import RemoveOneAction
from remove_one.utils.config import RemoveOneConfig


class TestCardManagement(unittest.TestCase):
    """Test card conservation and state transitions"""
    
    def setUp(self):
        self.config = RemoveOneConfig()
        self.game = RemoveOneGame(self.config.to_dict())
    
    def test_initial_card_distribution(self):
        """Test initial card distribution is correct"""
        total_cards = 0
        for player in self.game.players:
            total_cards += len(player.hand)
            total_cards += len(player.holding_box)
        total_cards += len(self.game.discard_pile)
        
        expected_cards = 7 * 8  # 7 players * 8 cards each
        self.assertEqual(total_cards, expected_cards)
        
        for player in self.game.players:
            self.assertEqual(set(player.hand), set(range(1, 9)))
            self.assertEqual(len(player.holding_box), 0)
    
    def test_card_conservation_through_round(self):
        """Test cards are conserved through a complete round"""
        initial_total = sum(len(p.hand) + len(p.holding_box) for p in self.game.players)
        initial_total += len(self.game.discard_pile)
        
        select_actions = {}
        for player_id in range(7):
            hand = self.game.players[player_id].hand
            select_actions[player_id] = RemoveOneAction('select_cards', cards=(hand[0], hand[1]))
        
        choose_state = self.game.apply_simultaneous_actions(select_actions)
        
        mid_total = sum(len(p.hand) + len(p.holding_box) for p in choose_state.players)
        mid_total += len(choose_state.discard_pile)
        self.assertEqual(initial_total, mid_total)
        
        choose_actions = {}
        for player_id in range(7):
            revealed = choose_state.revealed_cards[player_id]
            choose_actions[player_id] = RemoveOneAction('choose_final', final_card=revealed[0])
        
        final_state = choose_state.apply_simultaneous_actions(choose_actions)
        
        final_total = sum(len(p.hand) + len(p.holding_box) for p in final_state.players)
        final_total += len(final_state.discard_pile)
        self.assertEqual(initial_total, final_total)
    
    def test_holding_box_mechanics(self):
        """Test holding box mechanics work correctly"""
        select_actions = {}
        for player_id in range(7):
            hand = self.game.players[player_id].hand
            if player_id == 0:
                select_actions[player_id] = RemoveOneAction('select_cards', cards=(7, 8))
            else:
                select_actions[player_id] = RemoveOneAction('select_cards', cards=(hand[0], hand[1]))
        
        choose_state = self.game.apply_simultaneous_actions(select_actions)
        
        choose_actions = {}
        for player_id in range(7):
            revealed = choose_state.revealed_cards[player_id]
            choose_actions[player_id] = RemoveOneAction('choose_final', final_card=revealed[0])
        
        final_state = choose_state.apply_simultaneous_actions(choose_actions)
        
        for player_id in range(7):
            if player_id != final_state.get_results():  # Not the winner
                self.assertGreater(len(final_state.players[player_id].holding_box), 0)
    
    def test_discard_pile_mechanics(self):
        """Test discard pile accumulates winning cards"""
        initial_discard_size = len(self.game.discard_pile)
        
        select_actions = {}
        for player_id in range(7):
            hand = self.game.players[player_id].hand
            select_actions[player_id] = RemoveOneAction('select_cards', cards=(hand[0], hand[1]))
        
        choose_state = self.game.apply_simultaneous_actions(select_actions)
        
        choose_actions = {}
        for player_id in range(7):
            revealed = choose_state.revealed_cards[player_id]
            choose_actions[player_id] = RemoveOneAction('choose_final', final_card=revealed[0])
        
        final_state = choose_state.apply_simultaneous_actions(choose_actions)
        
        self.assertGreaterEqual(len(final_state.discard_pile), initial_discard_size)
    
    def test_phase_transitions(self):
        """Test proper phase transitions"""
        self.assertEqual(self.game.phase, 'select')
        
        select_actions = {}
        for player_id in range(7):
            hand = self.game.players[player_id].hand
            select_actions[player_id] = RemoveOneAction('select_cards', cards=(hand[0], hand[1]))
        
        choose_state = self.game.apply_simultaneous_actions(select_actions)
        self.assertEqual(choose_state.phase, 'choose')
        
        choose_actions = {}
        for player_id in range(7):
            revealed = choose_state.revealed_cards[player_id]
            choose_actions[player_id] = RemoveOneAction('choose_final', final_card=revealed[0])
        
        final_state = choose_state.apply_simultaneous_actions(choose_actions)
        self.assertEqual(final_state.phase, 'select')
        self.assertEqual(final_state.round_num, 2)  # Should advance to next round


if __name__ == '__main__':
    unittest.main()
