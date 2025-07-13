import copy
import dataclasses
from dataclasses import dataclass, field
from typing import Tuple, Dict, Optional
from collections import defaultdict

from ...core.game_action import GameAction
from ...core.game_state import GameState, BotGameState


@dataclass(frozen=True)
class RemoveOnePlayer:
    player_id: int
    hand: Tuple[int, ...]
    holding_box: Tuple[int, ...]
    score: int = 0
    victory_tokens: int = 0
    eliminated: bool = False
    last_victory_round: int = 0


@dataclass
class RemoveOneAction(GameAction):
    action_type: str
    cards: Optional[Tuple[int, int]] = None
    final_card: Optional[int] = None
    
    def is_valid(self, state: 'RemoveOneState', player_id: int) -> bool:
        if state.players[player_id].eliminated:
            return False
            
        if self.action_type == 'select_cards' and state.phase == 'select':
            if not self.cards or len(self.cards) != 2:
                return False
            return all(card in state.players[player_id].hand for card in self.cards)
        
        elif self.action_type == 'choose_final' and state.phase == 'choose':
            revealed = state.revealed_cards.get(player_id, ())
            return self.final_card in revealed
        
        return False


@dataclass(frozen=True)
class RemoveOneState(GameState):
    players: Tuple[RemoveOnePlayer, ...]
    round_num: int
    phase: str
    revealed_cards: Dict[int, Tuple[int, int]] = field(default_factory=dict)
    final_choices: Dict[int, int] = field(default_factory=dict)
    advancement_rounds: Tuple[int, ...] = (3, 6, 9, 12, 18)
    discard_pile: Tuple[int, ...] = field(default_factory=tuple)
    config: Dict = field(default_factory=dict)
    
    def copy(self) -> 'RemoveOneState':
        return copy.deepcopy(self)
    
    def copy_with_updates(self, **kwargs) -> 'RemoveOneState':
        """Create new state with specified updates"""
        return dataclasses.replace(self, **kwargs)
    
    def get_legal_actions(self, player_id: int) -> list:
        """Return all valid actions for player"""
        if self.players[player_id].eliminated:
            return []
        
        if self.phase == 'select':
            hand = self.players[player_id].hand
            return [
                RemoveOneAction('select_cards', cards=(card1, card2))
                for i, card1 in enumerate(hand)
                for card2 in hand[i+1:]
            ]
        
        elif self.phase == 'choose':
            revealed = self.revealed_cards.get(player_id, ())
            return [
                RemoveOneAction('choose_final', final_card=card)
                for card in revealed
            ]
        
        return []
    
    def apply_action(self, action: RemoveOneAction, player_id: int) -> 'RemoveOneState':
        """Apply player action and return new state"""
        if action.action_type == 'select_cards':
            new_revealed = dict(self.revealed_cards)
            new_revealed[player_id] = action.cards
            
            active_players = [p.player_id for p in self.players if not p.eliminated]
            if len(new_revealed) == len(active_players):
                return self.copy_with_updates(
                    revealed_cards=new_revealed,
                    phase='choose'
                )
            else:
                return self.copy_with_updates(revealed_cards=new_revealed)
        
        elif action.action_type == 'choose_final':
            new_choices = dict(self.final_choices)
            new_choices[player_id] = action.final_card
            
            active_players = [p.player_id for p in self.players if not p.eliminated]
            if len(new_choices) == len(active_players):
                return self._resolve_round(new_choices)
            else:
                return self.copy_with_updates(final_choices=new_choices)
        
        return self
    
    def apply_simultaneous_actions(self, actions: Dict[int, RemoveOneAction]) -> 'RemoveOneState':
        """Apply simultaneous actions"""
        new_state = self
        for player_id, action in actions.items():
            new_state = new_state.apply_action(action, player_id)
        return new_state
    
    def _resolve_round(self, final_choices: Dict[int, int]) -> 'RemoveOneState':
        """Resolve round and determine winner"""
        card_counts = defaultdict(int)
        for card in final_choices.values():
            card_counts[card] += 1
        
        unique_cards = {card: count for card, count in card_counts.items() if count == 1}
        
        if unique_cards:
            winning_card = min(unique_cards.keys())
            winner_id = next(pid for pid, card in final_choices.items() if card == winning_card)
            return self._award_points_and_advance(winner_id, winning_card, final_choices)
        else:
            return self._advance_round_no_winner(final_choices)
    
    def _award_points_and_advance(self, winner_id: int, winning_card: int, final_choices: Dict[int, int]) -> 'RemoveOneState':
        """Award points to winner and advance game state"""
        new_players = list(self.players)
        
        winner = new_players[winner_id]
        new_players[winner_id] = dataclasses.replace(
            winner,
            score=winner.score + winning_card,
            victory_tokens=winner.victory_tokens + 1,
            last_victory_round=self.round_num
        )
        
        for player_id, player in enumerate(new_players):
            if player.eliminated:
                continue
                
            new_hand = list(player.hand) + list(player.holding_box)
            new_holding_box = []
            
            if player_id in self.revealed_cards:
                revealed = self.revealed_cards[player_id]
                final_choice = final_choices[player_id]
                
                if player_id == winner_id:
                    unused_card = next(card for card in revealed if card != final_choice)
                    new_holding_box.append(unused_card)
                else:
                    new_holding_box.append(final_choice)
                    unused_card = next(card for card in revealed if card != final_choice)
                    new_hand.append(unused_card)
                
                for card in revealed:
                    if card in new_hand:
                        new_hand.remove(card)
            
            new_players[player_id] = dataclasses.replace(
                player,
                hand=tuple(sorted(new_hand)),
                holding_box=tuple(new_holding_box)
            )
        
        new_state = self.copy_with_updates(
            players=tuple(new_players),
            phase='select',
            revealed_cards={},
            final_choices={}
        )
        
        if self.round_num in self.advancement_rounds:
            new_state = self._handle_elimination(new_state)
        
        return self._advance_to_next_round(new_state)
    
    def _advance_round_no_winner(self, final_choices: Dict[int, int]) -> 'RemoveOneState':
        """Advance round when no winner"""
        new_players = list(self.players)
        
        for player_id, player in enumerate(new_players):
            if player.eliminated:
                continue
                
            new_hand = list(player.hand) + list(player.holding_box)
            new_holding_box = []
            
            if player_id in self.revealed_cards:
                revealed = self.revealed_cards[player_id]
                final_choice = final_choices[player_id]
                
                new_holding_box.append(final_choice)
                unused_card = next(card for card in revealed if card != final_choice)
                new_hand.append(unused_card)
                
                for card in revealed:
                    if card in new_hand:
                        new_hand.remove(card)
            
            new_players[player_id] = dataclasses.replace(
                player,
                hand=tuple(sorted(new_hand)),
                holding_box=tuple(new_holding_box)
            )
        
        new_state = self.copy_with_updates(
            players=tuple(new_players),
            phase='select',
            revealed_cards={},
            final_choices={}
        )
        
        return self._advance_to_next_round(new_state)
    
    def _handle_elimination(self, state: 'RemoveOneState') -> 'RemoveOneState':
        """Handle player elimination at checkpoint rounds"""
        active_players = [p for p in state.players if not p.eliminated]
        
        if state.round_num == 18:
            if len(active_players) == 3:
                lowest_scorer = min(active_players, key=lambda p: (p.score, p.victory_tokens, -p.last_victory_round))
                new_players = list(state.players)
                new_players[lowest_scorer.player_id] = dataclasses.replace(lowest_scorer, eliminated=True)
                return state.copy_with_updates(players=tuple(new_players))
        else:
            if len(active_players) > 1:
                highest_scorer = max(active_players, key=lambda p: (p.score, p.victory_tokens, p.last_victory_round))
                new_players = list(state.players)
                new_players[highest_scorer.player_id] = dataclasses.replace(highest_scorer, eliminated=True)
                return state.copy_with_updates(players=tuple(new_players))
        
        return state
    
    def _advance_to_next_round(self, state: 'RemoveOneState') -> 'RemoveOneState':
        """Advance to next round"""
        return state.copy_with_updates(round_num=state.round_num + 1)
    
    def is_terminal(self) -> bool:
        """Check if game has ended"""
        active_players = [p for p in self.players if not p.eliminated]
        return (len(active_players) <= 1 or 
                (self.round_num > 18 and len(active_players) <= 2))
    
    def get_results(self) -> Dict[int, float]:
        """Return final player rankings"""
        results = {}
        for player in self.players:
            if not player.eliminated:
                results[player.player_id] = 1000 + player.score
            else:
                results[player.player_id] = player.score
        return results
    
    def get_current_player(self) -> Optional[int]:
        """Return None for simultaneous phases"""
        return None
    
    def get_bot_view(self, player_id: int) -> BotGameState:
        """Return information visible to specified player"""
        player = self.players[player_id]
        
        public_info = {
            'round_num': self.round_num,
            'phase': self.phase,
            'advancement_rounds': self.advancement_rounds,
            'players_scores': {p.player_id: p.score for p in self.players},
            'players_tokens': {p.player_id: p.victory_tokens for p in self.players},
            'players_eliminated': {p.player_id: p.eliminated for p in self.players},
            'revealed_cards': dict(self.revealed_cards),
            'discard_pile': self.discard_pile,
        }
        
        private_info = {
            'hand': player.hand,
            'holding_box': player.holding_box,
            'my_score': player.score,
            'my_tokens': player.victory_tokens,
        }
        
        legal_actions = self.get_legal_actions(player_id)
        
        return BotGameState(public_info, private_info, legal_actions)
    
    def is_player_eliminated(self, player_id: int) -> bool:
        """Check if player is eliminated"""
        return self.players[player_id].eliminated
