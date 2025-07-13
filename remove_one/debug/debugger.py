import json
import pickle
import time
from typing import Dict, Any, List
from collections import defaultdict

from ..games.remove_one.data_structures import RemoveOneState


class GameDebugger:
    """Comprehensive debugging tools"""
    
    def __init__(self):
        self.replay_system = ReplaySystem()
        self.state_inspector = StateInspector()
    
    def debug_game(self, game_result: Dict[str, Any]):
        """Interactive game debugging"""
        history = game_result['history']
        
        print("=== GAME DEBUG SESSION ===")
        print(f"Total rounds: {len(history)}")
        print(f"Winner: {game_result['winner']}")
        
        for i, (state, player_id, action) in enumerate(history):
            print(f"\nStep {i}: Player {player_id} in {state.phase} phase")
            print(f"Action: {action}")
            
            response = input("Continue? (y/n/q): ").lower()
            if response == 'q':
                break
    
    def visualize_state(self, state: RemoveOneState):
        """ASCII visualization of game state"""
        print(f"\n=== ROUND {state.round_num} - {state.phase.upper()} PHASE ===")
        
        active_players = [p for p in state.players if not p.eliminated]
        eliminated_players = [p for p in state.players if p.eliminated]
        
        print("\nACTIVE PLAYERS:")
        for player in active_players:
            hand_str = ", ".join(map(str, sorted(player.hand)))
            holding_str = ", ".join(map(str, sorted(player.holding_box)))
            print(f"  Player {player.player_id}: Score={player.score}, Tokens={player.victory_tokens}")
            print(f"    Hand: [{hand_str}]")
            if player.holding_box:
                print(f"    Holding: [{holding_str}]")
        
        if eliminated_players:
            print(f"\nELIMINATED PLAYERS: {[p.player_id for p in eliminated_players]}")
        
        if state.revealed_cards:
            print(f"\nREVEALED CARDS: {state.revealed_cards}")
        
        if state.final_choices:
            print(f"FINAL CHOICES: {state.final_choices}")
        
        print(f"DISCARD PILE: {list(state.discard_pile)}")


class ReplaySystem:
    """Save and replay games for analysis"""
    
    def save_game(self, game_result: Dict[str, Any], filename: str):
        """Save complete game to file"""
        serializable_data = {
            'results': game_result['results'],
            'winner': game_result['winner'],
            'stats': game_result['stats'],
            'config': game_result.get('config', {}),
            'timestamp': time.time(),
        }
        
        with open(f"{filename}.pkl", 'wb') as f:
            pickle.dump(game_result['history'], f)
        
        with open(f"{filename}.json", 'w') as f:
            json.dump(serializable_data, f, indent=2)
    
    def load_game(self, filename: str) -> Dict[str, Any]:
        """Load saved game"""
        with open(f"{filename}.json", 'r') as f:
            data = json.load(f)
        
        with open(f"{filename}.pkl", 'rb') as f:
            history = pickle.load(f)
        
        data['history'] = history
        return data
    
    def replay_game_step_by_step(self, filename: str):
        """Interactive replay of saved game"""
        game_data = self.load_game(filename)
        debugger = GameDebugger()
        debugger.debug_game(game_data)


class StateInspector:
    """Deep inspection of game states"""
    
    def inspect_card_conservation(self, state: RemoveOneState) -> Dict[str, Any]:
        """Verify all cards are accounted for"""
        total_in_hands = sum(len(p.hand) for p in state.players)
        total_in_holding = sum(len(p.holding_box) for p in state.players)
        total_discarded = len(state.discard_pile)
        total_revealed = sum(len(cards) for cards in state.revealed_cards.values())
        
        expected_total = len(state.players) * 8
        actual_total = total_in_hands + total_in_holding + total_discarded + total_revealed
        
        return {
            'expected_cards': expected_total,
            'actual_cards': actual_total,
            'in_hands': total_in_hands,
            'in_holding': total_in_holding,
            'discarded': total_discarded,
            'revealed': total_revealed,
            'balanced': expected_total == actual_total,
        }
    
    def analyze_game_balance(self, history: List) -> Dict[str, Any]:
        """Analyze game balance and fairness"""
        round_winners = []
        score_progression = defaultdict(list)
        
        for state, player_id, action in history:
            if state.phase == 'resolve':
                for player in state.players:
                    score_progression[player.player_id].append(player.score)
        
        return {
            'score_progression': dict(score_progression),
            'round_winners': round_winners,
            'final_score_spread': max(score_progression.values(), key=lambda x: x[-1])[-1] - 
                                  min(score_progression.values(), key=lambda x: x[-1])[-1] if score_progression else 0,
        }
