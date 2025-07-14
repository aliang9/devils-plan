#!/usr/bin/env python3
"""
Comprehensive test runner for Remove One simulation system
"""
import unittest
import sys
import time
from pathlib import Path


def run_all_tests():
    """Run all test suites with detailed reporting"""
    print("="*60)
    print("REMOVE ONE SIMULATION TEST SUITE")
    print("="*60)
    
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent / 'tests'
    
    test_files = [
        'test_game_logic.py',
        'test_bot_strategies.py', 
        'test_card_management.py',
        'test_tournament_system.py',
        'test_full_game.py',
        'test_elimination_working.py'
    ]
    
    suite = unittest.TestSuite()
    for test_file in test_files:
        try:
            module_suite = loader.loadTestsFromName(f'tests.{test_file[:-3]}')
            suite.addTest(module_suite)
        except Exception as e:
            print(f"Warning: Could not load {test_file}: {e}")
    
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    start_time = time.time()
    result = runner.run(suite)
    end_time = time.time()
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Time: {end_time - start_time:.2f}s")
    
    if result.failures:
        print(f"\nFAILURES ({len(result.failures)}):")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print(f"\nERRORS ({len(result.errors)}):")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    if result.wasSuccessful():
        print("\n🎉 ALL TESTS PASSED! 🎉")
    else:
        print(f"\n❌ {len(result.failures + result.errors)} TEST(S) FAILED")
    
    print("="*60)
    
    return result.wasSuccessful()


def run_specific_test_module(module_name):
    """Run tests from a specific module"""
    print(f"Running tests from: {module_name}")
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(f'tests.{module_name}')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def run_performance_benchmark():
    """Run performance benchmarks for bot decision times"""
    print("\n" + "="*60)
    print("PERFORMANCE BENCHMARK")
    print("="*60)
    
    from remove_one.games.remove_one.game import RemoveOneGame
    from remove_one.utils.config import RemoveOneConfig
    from remove_one.bots.implementations.random_bot import RandomBot
    from remove_one.bots.implementations.greedy_bot import GreedyBot
    from remove_one.bots.implementations.card_counting_bot import CardCountingBot
    from remove_one.bots.implementations.minimax_bot import MinimaxBot
    
    config = RemoveOneConfig()
    game = RemoveOneGame(config.to_dict())
    
    bots = [
        RandomBot("Random"),
        GreedyBot("Greedy"),
        CardCountingBot("Counter"),
        MinimaxBot("Minimax")
    ]
    
    print("Bot decision time benchmarks (1000 decisions each):")
    
    for bot in bots:
        bot_view = game.get_bot_view(0)
        
        start_time = time.time()
        for _ in range(1000):
            action = bot.get_action(bot_view, 0)
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 1000 * 1000  # Convert to milliseconds
        print(f"  {bot.name:12} | Avg: {avg_time:.3f}ms per decision")
    
    print("="*60)


def validate_game_rules():
    """Validate that game implementation follows rules correctly"""
    print("\n" + "="*60)
    print("GAME RULE VALIDATION")
    print("="*60)
    
    from remove_one.validation.validator import GameValidator
    from remove_one.games.remove_one.game import RemoveOneGame
    from remove_one.utils.config import RemoveOneConfig
    
    validator = GameValidator()
    config = RemoveOneConfig()
    game = RemoveOneGame(config.to_dict())
    
    setup_valid = validator.validate_game_setup(RemoveOneGame, config.to_dict())
    print(f"Game setup validation: {'✓ PASS' if setup_valid else '✗ FAIL'}")
    
    consistency_errors = validator.validate_state_consistency(game)
    if not consistency_errors:
        print("State consistency validation: ✓ PASS")
    else:
        print("State consistency validation: ✗ FAIL")
        for error in consistency_errors:
            print(f"  - {error}")
    
    print("="*60)


def main():
    """Main entry point for test runner"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--benchmark":
            run_performance_benchmark()
            return
        elif sys.argv[1] == "--validate":
            validate_game_rules()
            return
        elif sys.argv[1].startswith("--module="):
            module_name = sys.argv[1].split("=")[1]
            success = run_specific_test_module(module_name)
            sys.exit(0 if success else 1)
        elif sys.argv[1] == "--help":
            print("Usage: python run_tests.py [options]")
            print("Options:")
            print("  --benchmark    Run performance benchmarks")
            print("  --validate     Run game rule validation")
            print("  --module=NAME  Run specific test module")
            print("  --help         Show this help message")
            return
    
    success = run_all_tests()
    
    validate_game_rules()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
