#!/usr/bin/env python3
"""
Interactive terminal UI for human vs bot gameplay
"""
import sys
import random
from typing import List, Dict, Any

from remove_one.utils.config import RemoveOneConfig
from remove_one.core.game_engine import GameEngine
from remove_one.games.remove_one.game import RemoveOneGame
from remove_one.games.remove_one.data_structures import RemoveOneAction
from remove_one.bots.implementations.random_bot import RandomBot
from remove_one.bots.implementations.greedy_bot import GreedyBot
from remove_one.bots.implementations.card_counting_bot import CardCountingBot
from remove_one.bots.implementations.minimax_bot import MinimaxBot


class HumanPlayer:
    """Human player interface for terminal gameplay"""
    
    def __init__(self, name: str):
        self.name = name
    
    def get_action(self, state, player_id: int):
        """Get human player action through terminal input"""
        self._display_game_state(state, player_id)
        
        if state.public_info['phase'] == 'select':
            return self._get_card_selection(state, player_id)
        elif state.public_info['phase'] == 'choose':
            return self._get_final_choice(state, player_id)
        
        return None
    
    def _display_game_state(self, state, player_id: int):
        """Display current game state in ASCII format"""
        print("\n" + "="*60)
        print(f"ROUND {state.public_info['round_num']} - {state.public_info['phase'].upper()} PHASE")
        print("="*60)
        
        print(f"\nYour hand: {sorted(state.private_info['hand'])}")
        if state.private_info['holding_box']:
            print(f"Holding box: {sorted(state.private_info['holding_box'])}")
        
        print(f"\nYour score: {state.private_info['my_score']} | Victory tokens: {state.private_info['my_tokens']}")
        
        print("\nOther players:")
        for pid in range(len(state.public_info['players_scores'])):
            if pid != player_id:
                eliminated = state.public_info['players_eliminated'][pid]
                if not eliminated:
                    score = state.public_info['players_scores'][pid]
                    tokens = state.public_info['players_tokens'][pid]
                    print(f"  Bot {pid}: Score {score}, Tokens {tokens}")
                else:
                    print(f"  Bot {pid}: ELIMINATED")
        
        if state.public_info['revealed_cards']:
            print("\nRevealed cards this round:")
            for pid, cards in state.public_info['revealed_cards'].items():
                if pid != player_id:
                    print(f"  Bot {pid}: {cards}")
                else:
                    print(f"  You: {cards}")
        
        if state.public_info['discard_pile']:
            print(f"\nDiscard pile: {sorted(state.public_info['discard_pile'])}")
        
        advancement_rounds = state.public_info['advancement_rounds']
        next_advancement = next((r for r in advancement_rounds if r > state.public_info['round_num']), None)
        if next_advancement:
            print(f"\nNext elimination round: {next_advancement}")
    
    def _get_card_selection(self, state, player_id: int):
        """Get card selection from human player"""
        hand = sorted(state.private_info['hand'])
        
        print(f"\nSelect 2 cards from your hand: {hand}")
        print("Enter two card numbers separated by space (e.g., '1 3'):")
        
        while True:
            try:
                user_input = input("> ").strip()
                if user_input.lower() in ['quit', 'exit']:
                    sys.exit(0)
                
                card_strs = user_input.split()
                if len(card_strs) != 2:
                    print("Please enter exactly 2 card numbers.")
                    continue
                
                card1, card2 = int(card_strs[0]), int(card_strs[1])
                
                if card1 == card2:
                    print("Please select two different cards.")
                    continue
                
                if card1 not in hand or card2 not in hand:
                    print(f"Both cards must be in your hand: {hand}")
                    continue
                
                selected_cards = tuple(sorted([card1, card2]))
                action = RemoveOneAction('select_cards', cards=selected_cards)
                
                if action.is_valid(state, player_id):
                    return action
                else:
                    print("Invalid card selection. Please try again.")
                    
            except ValueError:
                print("Please enter valid numbers.")
            except KeyboardInterrupt:
                print("\nGoodbye!")
                sys.exit(0)
    
    def _get_final_choice(self, state, player_id: int):
        """Get final card choice from human player"""
        revealed = state.public_info['revealed_cards'][player_id]
        
        print(f"\nYour revealed cards: {revealed}")
        print("Choose which card to submit (enter the card number):")
        
        while True:
            try:
                user_input = input("> ").strip()
                if user_input.lower() in ['quit', 'exit']:
                    sys.exit(0)
                
                final_card = int(user_input)
                
                if final_card not in revealed:
                    print(f"Card must be one of your revealed cards: {revealed}")
                    continue
                
                action = RemoveOneAction('choose_final', final_card=final_card)
                
                if action.is_valid(state, player_id):
                    return action
                else:
                    print("Invalid choice. Please try again.")
                    
            except ValueError:
                print("Please enter a valid number.")
            except KeyboardInterrupt:
                print("\nGoodbye!")
                sys.exit(0)


class HumanVsBotsGame:
    """Main game controller for human vs bots"""
    
    def __init__(self):
        self.config = RemoveOneConfig()
        self.bot_types = {
            'random': RandomBot,
            'greedy': GreedyBot,
            'counter': CardCountingBot,
            'minimax': MinimaxBot
        }
    
    def show_welcome(self):
        """Display welcome message and instructions"""
        print("="*60)
        print("WELCOME TO REMOVE ONE - HUMAN VS BOTS")
        print("="*60)
        print("\nGame Rules:")
        print("- You and 6 bots start with cards 1-8")
        print("- Each round: Select 2 cards → Choose 1 to submit")
        print("- Lowest unique card wins points equal to card value")
        print("- Elimination rounds at 3, 6, 9, 12, and 18")
        print("- Last player standing wins!")
        print("\nCommands: Type 'quit' or 'exit' to leave anytime")
        print("         Press Ctrl+C to quit")
    
    def select_opponents(self) -> List:
        """Let human select bot opponents"""
        print("\nAvailable bot types:")
        print("1. Random - Makes random legal moves")
        print("2. Greedy - Always plays lowest cards")
        print("3. Counter - Tracks opponent card usage")
        print("4. Minimax - Uses game tree search")
        print("5. Mixed - Random selection of all types")
        
        while True:
            try:
                choice = input("\nSelect opponent type (1-5): ").strip()
                
                if choice == '1':
                    return [RandomBot(f"Random_{i}") for i in range(6)]
                elif choice == '2':
                    return [GreedyBot(f"Greedy_{i}") for i in range(6)]
                elif choice == '3':
                    return [CardCountingBot(f"Counter_{i}") for i in range(6)]
                elif choice == '4':
                    return [MinimaxBot(f"Minimax_{i}") for i in range(6)]
                elif choice == '5':
                    bots = []
                    bot_names = ['random', 'greedy', 'counter', 'minimax']
                    for i in range(6):
                        bot_type = random.choice(bot_names)
                        if bot_type == 'random':
                            bots.append(RandomBot(f"Random_{i}"))
                        elif bot_type == 'greedy':
                            bots.append(GreedyBot(f"Greedy_{i}"))
                        elif bot_type == 'counter':
                            bots.append(CardCountingBot(f"Counter_{i}"))
                        elif bot_type == 'minimax':
                            bots.append(MinimaxBot(f"Minimax_{i}"))
                    return bots
                else:
                    print("Please enter 1, 2, 3, 4, or 5")
                    
            except KeyboardInterrupt:
                print("\nGoodbye!")
                sys.exit(0)
    
    def run_game(self):
        """Run the main game loop"""
        self.show_welcome()
        
        try:
            player_name = input("\nEnter your name: ").strip() or "Human"
        except KeyboardInterrupt:
            print("\nGoodbye!")
            sys.exit(0)
        
        bot_opponents = self.select_opponents()
        
        human_player = HumanPlayer(player_name)
        all_players = [human_player] + bot_opponents
        
        print(f"\nStarting game with {player_name} vs 6 bots...")
        print("Bot opponents:", [bot.name for bot in bot_opponents])
        
        result = self._run_human_game(all_players)
        
        self._show_final_results(result, player_name)
    
    def _run_human_game(self, players):
        """Run game with human player integration"""
        from remove_one.core.game_engine import GameEngine
        
        engine = GameEngine(self.config.to_dict())
        game = RemoveOneGame(self.config.to_dict())
        
        history = []
        
        while not game.is_terminal():
            actions = {}
            
            for player_id, player in enumerate(players):
                if not game.players[player_id].eliminated:
                    bot_view = game.get_bot_view(player_id)
                    
                    if isinstance(player, HumanPlayer):
                        action = player.get_action(bot_view, player_id)
                    else:
                        action = player.get_action(bot_view, player_id)
                    
                    actions[player_id] = action
            
            game = game.apply_simultaneous_actions(actions)
            history.append((game, actions))
            
            if game.phase == 'select' and len(history) > 1:
                self._show_round_results(history[-2][0], history[-1][0])
        
        results = game.get_results()
        winner_id = max(results.keys(), key=lambda k: results[k])
        
        return {
            'winner': winner_id,
            'results': results,
            'history': history,
            'final_state': game
        }
    
    def _show_round_results(self, prev_state, current_state):
        """Show results of the completed round"""
        if prev_state.revealed_cards and prev_state.final_choices:
            print(f"\n--- ROUND {prev_state.round_num} RESULTS ---")
            
            choices = []
            for pid, card in prev_state.final_choices.items():
                if not prev_state.players[pid].eliminated:
                    player_name = "You" if pid == 0 else f"Bot {pid}"
                    choices.append((card, player_name, pid))
            
            choices.sort()  # Sort by card value
            
            print("Final card submissions:")
            for card, name, pid in choices:
                print(f"  {name}: {card}")
            
            from collections import defaultdict
            card_counts = defaultdict(int)
            for card, _, _ in choices:
                card_counts[card] += 1
            
            unique_cards = [card for card, count in card_counts.items() if count == 1]
            
            if unique_cards:
                winning_card = min(unique_cards)
                winner_name = next(name for card, name, pid in choices if card == winning_card)
                print(f"\nWinner: {winner_name} with card {winning_card}!")
            else:
                print("\nNo winner this round (all cards duplicated)")
            
            print()
    
    def _show_final_results(self, result, player_name):
        """Display final game results"""
        print("\n" + "="*60)
        print("GAME OVER!")
        print("="*60)
        
        winner_id = result['winner']
        final_state = result['final_state']
        
        if winner_id == 0:
            print(f"🎉 Congratulations {player_name}! You won! 🎉")
        else:
            print(f"Game won by Bot {winner_id}")
            print(f"Better luck next time, {player_name}!")
        
        print("\nFinal Standings:")
        results = result['results']
        sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
        
        for rank, (player_id, score) in enumerate(sorted_results, 1):
            player_name_display = player_name if player_id == 0 else f"Bot {player_id}"
            eliminated = final_state.players[player_id].eliminated
            status = " (ELIMINATED)" if eliminated else ""
            print(f"{rank}. {player_name_display}: {score} points{status}")
        
        print(f"\nTotal rounds played: {final_state.round_num - 1}")


def main():
    """Main entry point"""
    try:
        game = HumanVsBotsGame()
        game.run_game()
    except KeyboardInterrupt:
        print("\n\nThanks for playing!")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Please report this issue.")


if __name__ == "__main__":
    main()
