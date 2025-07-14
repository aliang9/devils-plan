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
        """Analyze card selection and usage patterns"""
        card_selections = defaultdict(int)
        winning_cards = defaultdict(int)
        final_choices = defaultdict(int)
        
        for state, player_id, action in history:
            if hasattr(action, 'cards') and action.cards:
                for card in action.cards:
                    card_selections[card] += 1
            
            if hasattr(action, 'final_card') and action.final_card:
                final_card = action.final_card
                final_choices[final_card] += 1
                
                if hasattr(state, 'final_choices') and state.final_choices:
                    from collections import defaultdict as dd
                    card_counts = dd(int)
                    for pid, card in state.final_choices.items():
                        card_counts[card] += 1
                    
                    unique_cards = [card for card, count in card_counts.items() if count == 1]
                    if unique_cards and final_card == min(unique_cards):
                        winning_cards[final_card] += 1
        
        return {
            'card_selection_frequency': dict(card_selections),
            'final_choice_frequency': dict(final_choices),
            'winning_card_distribution': dict(winning_cards),
            'selection_patterns': self._analyze_selection_patterns(card_selections)
        }
    
    def track_card_usage(self, final_card: int, player_id: int):
        """Track final card choices for pattern analysis"""
        if not hasattr(self, 'final_choices'):
            self.final_choices = {}
        
        if player_id not in self.final_choices:
            self.final_choices[player_id] = []
        
        self.final_choices[player_id].append(final_card)
    
    def get_selection_patterns(self) -> Dict[int, Dict[str, float]]:
        """Get card selection pattern analysis for each player"""
        if not hasattr(self, 'card_selections'):
            self.card_selections = {}
        
        patterns = {}
        for player_id in range(7):
            if player_id in self.card_selections:
                selections = self.card_selections[player_id]
                total_selections = len(selections)
                if total_selections > 0:
                    card_counts = {}
                    for cards in selections:
                        for card in cards:
                            card_counts[card] = card_counts.get(card, 0) + 1
                    
                    patterns[player_id] = {
                        'high_cards_preference': sum(1 for cards in selections for card in cards if card >= 6) / (total_selections * 2),
                        'low_cards_preference': sum(1 for cards in selections for card in cards if card <= 3) / (total_selections * 2),
                        'variance': self._calculate_variance([card for cards in selections for card in cards]),
                        'most_selected': max(card_counts.items(), key=lambda x: x[1])[0] if card_counts else 0
                    }
                else:
                    patterns[player_id] = {
                        'high_cards_preference': 0.0,
                        'low_cards_preference': 0.0,
                        'variance': 0.0,
                        'most_selected': 0
                    }
        return patterns
    
    def get_game_statistics(self) -> Dict[str, Any]:
        """Get comprehensive game statistics"""
        if not self.game_results:
            return {}
        
        total_games = len(self.game_results)
        avg_rounds = sum(g['total_rounds'] for g in self.game_results) / total_games
        
        return {
            'total_games': total_games,
            'average_rounds': avg_rounds,
            'total_eliminations': sum(len(g['eliminations']) for g in self.game_results)
        }
    
    def _analyze_selection_patterns(self, card_selections: Dict) -> Dict[str, Any]:
        """Analyze patterns in card selection"""
        if not card_selections:
            return {}
        
        total_selections = sum(card_selections.values())
        most_selected = max(card_selections.keys(), key=lambda k: card_selections[k])
        least_selected = min(card_selections.keys(), key=lambda k: card_selections[k])
        
        return {
            'most_selected_card': most_selected,
            'least_selected_card': least_selected,
            'selection_variance': self._calculate_variance(list(card_selections.values())),
            'total_selections': total_selections
        }
    
    def _calculate_variance(self, values: List[int]) -> float:
        """Calculate variance of selection frequencies"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        return sum((x - mean) ** 2 for x in values) / len(values)
    
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
