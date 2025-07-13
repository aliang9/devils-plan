"""
Main entry point for Remove One bot simulation system.
"""

from remove_one.utils.config import RemoveOneConfig
from remove_one.core.game_engine import GameEngine
from remove_one.games.remove_one.game import RemoveOneGame
from remove_one.bots.implementations.random_bot import RandomBot
from remove_one.bots.implementations.greedy_bot import GreedyBot
from remove_one.bots.implementations.card_counting_bot import CardCountingBot
from remove_one.bots.implementations.minimax_bot import MinimaxBot
from remove_one.tournament.tournament import Tournament
from remove_one.debug.debugger import GameDebugger, ReplaySystem
from remove_one.utils.profiler import BotProfiler
from remove_one.validation.validator import GameValidator


def main():
    """Example usage of the Remove One simulation system"""
    
    config = RemoveOneConfig()
    config.games_per_match = 50
    config.enable_logging = True
    config.enable_profiling = True
    
    bots = [
        RandomBot("Random_1"),
        RandomBot("Random_2"), 
        GreedyBot("Greedy_1"),
        GreedyBot("Greedy_2"),
        CardCountingBot("Counter_1"),
        CardCountingBot("Counter_2"),
        MinimaxBot("Minimax_1", depth=2),
    ]
    
    tournament = Tournament(bots, config)
    results = tournament.run_round_robin(games_per_matchup=20)
    
    print("=== TOURNAMENT RESULTS ===")
    for bot_idx, stats in results['results'].items():
        bot_name = bots[bot_idx].name
        print(f"{bot_name}: {stats['win_rate']:.2%} win rate, {stats['avg_score']:.1f} avg score")
    
    elo_ratings = tournament.results.generate_elo_ratings()
    print("\n=== ELO RATINGS ===")
    sorted_ratings = sorted(elo_ratings.items(), key=lambda x: x[1], reverse=True)
    for bot_idx, rating in sorted_ratings:
        print(f"{bots[bot_idx].name}: {rating:.0f}")
    
    if config.enable_profiling:
        profiler = BotProfiler()
        perf_report = profiler.generate_report()
        print("\n=== PERFORMANCE ANALYSIS ===")
        for bot_name, metrics in perf_report.items():
            print(f"{bot_name}: {metrics['avg_decision_time']:.3f}s avg decision time")


def run_single_game_debug():
    """Debug a single game with detailed output"""
    config = RemoveOneConfig()
    config.enable_logging = True
    
    bots = [
        GreedyBot("Greedy"),
        RandomBot("Random_1"),
        RandomBot("Random_2"),
        CardCountingBot("Counter"),
        RandomBot("Random_3"),
        RandomBot("Random_4"),
        RandomBot("Random_5"),
    ]
    
    engine = GameEngine(config.to_dict())
    result = engine.run_game(RemoveOneGame, bots, seed=42)
    
    debugger = GameDebugger()
    debugger.debug_game(result)
    
    replay_system = ReplaySystem()
    replay_system.save_game(result, "debug_game_001")


def validate_implementation():
    """Comprehensive validation of game implementation"""
    print("=== VALIDATING GAME IMPLEMENTATION ===")
    
    config = RemoveOneConfig()
    validator = GameValidator()
    
    if not validator.validate_game_setup(RemoveOneGame, config.to_dict()):
        print("❌ Game setup validation failed")
        return False
    print("✅ Game setup validation passed")
    
    bots = [RandomBot(f"Test_{i}") for i in range(7)]
    engine = GameEngine(config.to_dict())
    
    for i in range(10):
        try:
            result = engine.run_game(RemoveOneGame, bots, seed=i)
            
            final_state = result['history'][-1][0] if result['history'] else None
            if final_state:
                errors = validator.validate_state_consistency(final_state)
                if errors:
                    print(f"❌ Game {i} state validation failed: {errors}")
                    return False
            
            print(f"✅ Game {i} completed successfully")
            
        except Exception as e:
            print(f"❌ Game {i} failed with error: {e}")
            return False
    
    print("✅ All validation tests passed")
    return True


if __name__ == "__main__":
    if validate_implementation():
        main()
