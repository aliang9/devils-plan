from collections import defaultdict
from typing import List, Dict, Any


class GameAnalytics:
    """Statistical analysis of game outcomes"""
    
    def __init__(self):
        self.game_results = []
        self.bot_performance = defaultdict(list)
        self.win_patterns = defaultdict(list)
    
    def process_game(self, history: List, results: Dict[int, float]) -> Dict[str, Any]:
        """Analyze completed game"""
        game_stats = {
            'total_rounds': len([h for h in history if h[0].phase == 'resolve']),
            'eliminations': self._count_eliminations(history),
            'card_distribution': self._analyze_card_usage(history),
            'winner_profile': self._analyze_winner(history, results),
        }
        
        self.game_results.append(game_stats)
        return game_stats
    
    def _count_eliminations(self, history: List) -> Dict[str, int]:
        """Count eliminations by round"""
        eliminations = defaultdict(int)
        
        for state, player_id, action in history:
            eliminated_count = sum(1 for p in state.players if p.eliminated)
            if hasattr(state, 'advancement_rounds') and state.round_num in state.advancement_rounds:
                eliminations[f"round_{state.round_num}"] = eliminated_count
        
        return dict(eliminations)
    
    def _analyze_card_usage(self, history: List) -> Dict[str, Any]:
        """Analyze patterns in card selection and usage"""
        card_selections = defaultdict(int)
        winning_cards = defaultdict(int)
        
        for state, player_id, action in history:
            if hasattr(action, 'cards') and action.cards:
                for card in action.cards:
                    card_selections[card] += 1
            
            if hasattr(action, 'final_card') and action.final_card:
                pass
        
        return {
            'card_selection_frequency': dict(card_selections),
            'winning_card_distribution': dict(winning_cards),
        }
    
    def _analyze_winner(self, history: List, results: Dict[int, float]) -> Dict[str, Any]:
        """Analyze characteristics of the winner"""
        winner_id = max(results.items(), key=lambda x: x[1])[0]
        
        final_state = history[-1][0] if history else None
        if not final_state:
            return {}
        
        winner = final_state.players[winner_id]
        
        return {
            'winner_id': winner_id,
            'final_score': winner.score,
            'victory_tokens': winner.victory_tokens,
            'cards_remaining': len(winner.hand),
        }
    
    def generate_comprehensive_report(self) -> str:
        """Generate detailed analysis report"""
        if not self.game_results:
            return "No games analyzed yet."
        
        total_games = len(self.game_results)
        avg_rounds = sum(g['total_rounds'] for g in self.game_results) / total_games
        
        report = f"""

- Total Games Analyzed: {total_games}
- Average Game Length: {avg_rounds:.1f} rounds
- Total Eliminations: {sum(len(g['eliminations']) for g in self.game_results)}

[Detailed analysis would include bot win rates, card usage patterns, etc.]

[Strategic insights based on observed patterns]
"""
        return report
