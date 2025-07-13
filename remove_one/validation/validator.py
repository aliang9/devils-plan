from typing import Dict, List, Any


class GameValidator:
    """Comprehensive game rule validation"""
    
    def validate_game_setup(self, game_class, config: Dict) -> bool:
        """Validate game configuration is legal"""
        if config.get('num_players', 0) < 2:
            return False
        if not config.get('advancement_rounds'):
            return False
        return True
    
    def validate_state_consistency(self, state) -> List[str]:
        """Check for state consistency errors"""
        errors = []
        
        total_cards = 0
        for player in state.players:
            total_cards += len(player.hand) + len(player.holding_box)
        total_cards += len(state.discard_pile)
        
        expected_cards = len(state.players) * (state.config.get('hand_size', 9) - 1)
        if total_cards != expected_cards:
            errors.append(f"Card count mismatch: {total_cards} vs {expected_cards}")
        
        for player in state.players:
            if player.score < 0:
                errors.append(f"Player {player.player_id} has negative score")
        
        return errors
    
    def validate_action_sequence(self, history: List) -> List[str]:
        """Validate that action sequence follows game rules"""
        errors = []
        
        expected_phases = ['select', 'choose', 'resolve']
        phase_sequence = []
        
        for state, player_id, action in history:
            phase_sequence.append(state.phase)
        
        return errors
