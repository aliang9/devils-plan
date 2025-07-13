import random
from collections import defaultdict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...core.game_state import BotGameState
    from ...core.game_action import GameAction

from ..base_bot import Bot
from ...games.remove_one.data_structures import RemoveOneAction


class CardCountingBot(Bot):
    """Tracks opponent card usage patterns"""
    
    def __init__(self, name: str):
        super().__init__(name)
        self.opponent_cards = defaultdict(set)
        self.card_play_history = defaultdict(list)
    
    def get_action(self, state: 'BotGameState', player_id: int) -> 'GameAction':
        if state.public_info['phase'] == 'select':
            return self._select_cards_strategically(state, player_id)
        elif state.public_info['phase'] == 'choose':
            return self._choose_final_strategically(state, player_id)
        
        return state.legal_actions[0] if state.legal_actions else None
    
    def _select_cards_strategically(self, state: 'BotGameState', player_id: int) -> 'GameAction':
        """Select cards based on opponent modeling"""
        hand = state.private_info['hand']
        
        win_probabilities = {}
        for card in hand:
            prob = self._estimate_win_probability(card, state, player_id)
            win_probabilities[card] = prob
        
        best_cards = sorted(win_probabilities.items(), key=lambda x: x[1], reverse=True)[:2]
        selected = tuple(sorted([card for card, _ in best_cards]))
        
        return RemoveOneAction('select_cards', cards=selected)
    
    def _choose_final_strategically(self, state: 'BotGameState', player_id: int) -> 'GameAction':
        """Choose final card strategically"""
        my_revealed = state.public_info['revealed_cards'][player_id]
        
        win_probabilities = {}
        for card in my_revealed:
            prob = self._estimate_win_probability(card, state, player_id)
            win_probabilities[card] = prob
        
        best_card = max(win_probabilities.items(), key=lambda x: x[1])[0]
        return RemoveOneAction('choose_final', final_card=best_card)
    
    def _estimate_win_probability(self, card: int, state: 'BotGameState', player_id: int) -> float:
        """Estimate probability of winning with given card"""
        base_prob = 1.0 / card
        
        conflict_probability = 0.0
        active_opponents = sum(1 for pid, eliminated in state.public_info['players_eliminated'].items() 
                              if pid != player_id and not eliminated)
        
        for opponent_id in range(len(state.public_info['players_eliminated'])):
            if opponent_id != player_id and not state.public_info['players_eliminated'][opponent_id]:
                if card in self.opponent_cards[opponent_id]:
                    conflict_probability += 0.3
        
        return base_prob * (1.0 - conflict_probability / max(active_opponents, 1))
    
    def observe_action(self, state: 'BotGameState', player_id: int, action: 'GameAction'):
        """Update opponent models based on observed actions"""
        if hasattr(action, 'action_type') and action.action_type == 'select_cards' and hasattr(action, 'cards'):
            self.card_play_history[player_id].append(action.cards)
            for card in action.cards:
                self.opponent_cards[player_id].add(card)
