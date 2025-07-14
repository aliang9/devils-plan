#!/usr/bin/env python3
"""
Comprehensive simulation runner for Remove One bot research experiments
"""
import argparse
import json
import time
import csv
import random
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict

from remove_one.utils.config import RemoveOneConfig
from remove_one.tournament.tournament import Tournament
from remove_one.bots.implementations.random_bot import RandomBot
from remove_one.bots.implementations.greedy_bot import GreedyBot
from remove_one.bots.implementations.card_counting_bot import CardCountingBot
from remove_one.bots.implementations.minimax_bot import MinimaxBot
from remove_one.utils.analytics import GameAnalytics


class SimulationRunner:
    """Comprehensive simulation runner for AI research experiments"""
    
    def __init__(self, config_file: str = None):
        self.config = self._load_config(config_file)
        self.analytics = GameAnalytics()
        self.results = {}
        
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load simulation configuration from file or use defaults"""
        default_config = {
            'bot_composition': {
                'random': 2,
                'greedy': 2, 
                'card_counting': 0,  # Reduced for performance
                'minimax': 0         # Reduced for performance
            },
            'tournament_settings': {
                'games_per_matchup': 100,
                'tournament_type': 'round_robin'
            },
            'analysis_settings': {
                'track_decision_patterns': True,
                'generate_heatmaps': True,
                'statistical_significance': 0.05
            },
            'output_settings': {
                'save_detailed_logs': True,
                'export_csv': True,
                'generate_plots': False,
                'output_dir': 'simulation_results'
            }
        }
        
        if config_file and Path(config_file).exists():
            with open(config_file, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def run_simulation(self):
        """Run the complete simulation with configured parameters"""
        print("=== REMOVE ONE BOT SIMULATION ===")
        print(f"Configuration: {self.config}")
        
        bots = []
        bot_config = self.config['bot_composition']
        
        for _ in range(bot_config.get('random', 0)):
            bots.append(RandomBot(f"Random_{len(bots)}"))
        for _ in range(bot_config.get('greedy', 0)):
            bots.append(GreedyBot(f"Greedy_{len(bots)}"))
        for _ in range(bot_config.get('card_counting', 0)):
            bots.append(CardCountingBot(f"Counter_{len(bots)}"))
        for _ in range(bot_config.get('minimax', 0)):
            bots.append(MinimaxBot(f"Minimax_{len(bots)}"))
        
        # Run tournament
        tournament = Tournament(bots)
        results = tournament.run_tournament(
            tournament_type=self.config['tournament_settings']['tournament_type'],
            games_per_matchup=self.config['tournament_settings']['games_per_matchup']
        )
        
        metrics = self._generate_metrics(tournament, results)
        
        self._output_results(metrics)
        
        return metrics
    
    def _generate_metrics(self, tournament, results):
        """Generate comprehensive metrics for research analysis"""
        metrics = {
            'tournament_results': results,
            'elo_ratings': tournament.elo_ratings,
            'game_statistics': tournament.analytics.get_game_statistics(),
            'selection_patterns': tournament.analytics.get_selection_patterns(),
            'performance_summary': self._calculate_performance_summary(tournament),
            'statistical_significance': self._test_statistical_significance(tournament)
        }
        return metrics
    
    def _calculate_performance_summary(self, tournament):
        """Calculate performance summary statistics"""
        summary = {}
        for bot in tournament.bots:
            summary[bot.name] = {
                'games_played': getattr(bot, 'games_played', 0),
                'games_won': getattr(bot, 'games_won', 0),
                'win_rate': getattr(bot, 'games_won', 0) / max(getattr(bot, 'games_played', 1), 1),
                'elo_rating': tournament.elo_ratings.get(bot.name, 1000)
            }
        return summary
    
    def _test_statistical_significance(self, tournament):
        """Test statistical significance of performance differences"""
        return {"note": "Statistical significance testing not yet implemented"}
    
    def _output_results(self, metrics):
        """Output results in multiple formats"""
        import json
        
        print("\n=== SIMULATION RESULTS ===")
        print(f"ELO Ratings: {metrics['elo_ratings']}")
        print(f"Performance Summary: {metrics['performance_summary']}")
        
        if self.config['output_settings']['save_detailed_logs']:
            with open('simulation_results.json', 'w') as f:
                json.dump(metrics, f, indent=2, default=str)
            print("Detailed results saved to simulation_results.json")
        
        if self.config['output_settings']['export_csv']:
            self._export_csv(metrics)
            print("CSV results saved to simulation_results.csv")
    
    def _export_csv(self, metrics):
        """Export results to CSV format"""
        import csv
        
        with open('simulation_results.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Bot Name', 'Games Played', 'Games Won', 'Win Rate', 'ELO Rating'])
            
            for bot_name, stats in metrics['performance_summary'].items():
                writer.writerow([
                    bot_name,
                    stats['games_played'],
                    stats['games_won'],
                    f"{stats['win_rate']:.3f}",
                    stats['elo_rating']
                ])

def main():
    """Main entry point for simulation script"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run Remove One bot simulation experiments')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--random-bots', type=int, default=2, help='Number of random bots')
    parser.add_argument('--greedy-bots', type=int, default=2, help='Number of greedy bots')
    parser.add_argument('--counter-bots', type=int, default=2, help='Number of card counting bots')
    parser.add_argument('--minimax-bots', type=int, default=1, help='Number of minimax bots')
    parser.add_argument('--games', type=int, default=100, help='Games per matchup')
    parser.add_argument('--tournament-type', default='round_robin', help='Tournament type')
    
    args = parser.parse_args()
    
    config_overrides = {
        'bot_composition': {
            'random': args.random_bots,
            'greedy': args.greedy_bots,
            'card_counting': args.counter_bots,
            'minimax': args.minimax_bots
        },
        'tournament_settings': {
            'games_per_matchup': args.games,
            'tournament_type': args.tournament_type
        }
    }
    
    runner = SimulationRunner(args.config)
    runner.config.update(config_overrides)
    
    results = runner.run_simulation()
    
    print("\n=== SIMULATION COMPLETE ===")
    print("Results saved to simulation_results.json and simulation_results.csv")
    print("Use these files for further analysis and research.")

if __name__ == "__main__":
    main()
    
    def create_bot_pool(self) -> List:
        """Create bot pool based on configuration"""
        bots = []
        composition = self.config['bot_composition']
        
        for i in range(composition.get('random', 0)):
            bots.append(RandomBot(f"Random_{i+1}"))
        
        for i in range(composition.get('greedy', 0)):
            bots.append(GreedyBot(f"Greedy_{i+1}"))
        
        for i in range(composition.get('card_counting', 0)):
            bots.append(CardCountingBot(f"Counter_{i+1}"))
        
        for i in range(composition.get('minimax', 0)):
            bots.append(MinimaxBot(f"Minimax_{i+1}"))
        
        return bots
    
    def run_simulation(self) -> Dict[str, Any]:
        """Run the complete simulation"""
        print("Starting Remove One Bot Simulation...")
        print(f"Configuration: {self.config['bot_composition']}")
        
        start_time = time.time()
        
        bots = self.create_bot_pool()
        print(f"Created {len(bots)} bots: {[bot.name for bot in bots]}")
        
        game_config = RemoveOneConfig()
        game_config.games_per_match = self.config['tournament_settings']['games_per_matchup']
        
        tournament = Tournament(bots, game_config)
        
        tournament_type = self.config['tournament_settings']['tournament_type']
        
        if tournament_type == 'round_robin':
            results = tournament.run_round_robin(
                games_per_matchup=self.config['tournament_settings']['games_per_matchup']
            )
        elif tournament_type == 'elimination':
            results = tournament.run_elimination_bracket()
        elif tournament_type == 'league':
            results = tournament.run_league_season(rounds=10)
        else:
            raise ValueError(f"Unknown tournament type: {tournament_type}")
        
        metrics = self._calculate_metrics(results, bots)
        
        analysis = self._generate_analysis(results, metrics, bots)
        
        end_time = time.time()
        
        simulation_results = {
            'configuration': self.config,
            'tournament_results': results,
            'metrics': metrics,
            'analysis': analysis,
            'execution_time': end_time - start_time,
            'timestamp': time.time()
        }
        
        self._save_results(simulation_results)
        
        return simulation_results
    
    def _calculate_metrics(self, results: Dict, bots: List) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics"""
        metrics = {
            'bot_performance': {},
            'strategy_analysis': {},
            'decision_patterns': {},
            'theory_of_mind_indicators': {}
        }
        
        if 'results' in results:
            for bot_idx, stats in results['results'].items():
                bot_name = bots[bot_idx].name
                bot_type = bot_name.split('_')[0].lower()
                
                metrics['bot_performance'][bot_name] = {
                    'win_rate': stats['win_rate'],
                    'avg_score': stats['avg_score'],
                    'games_played': stats['games_played'],
                    'total_wins': stats['total_wins'],
                    'bot_type': bot_type
                }
        
        strategy_stats = defaultdict(lambda: {
            'total_games': 0,
            'total_wins': 0,
            'total_score': 0
        })
        
        for bot_name, perf in metrics['bot_performance'].items():
            bot_type = perf['bot_type']
            strategy_stats[bot_type]['total_games'] += perf['games_played']
            strategy_stats[bot_type]['total_wins'] += perf['total_wins']
            strategy_stats[bot_type]['total_score'] += perf['avg_score'] * perf['games_played']
        
        for bot_type, stats in strategy_stats.items():
            if stats['total_games'] > 0:
                metrics['strategy_analysis'][bot_type] = {
                    'win_rate': stats['total_wins'] / stats['total_games'],
                    'avg_score': stats['total_score'] / stats['total_games'],
                    'total_games': stats['total_games']
                }
        
        metrics['theory_of_mind_indicators'] = {
            'opponent_modeling_accuracy': 0.0,  # To be implemented
            'prediction_success_rate': 0.0,     # To be implemented
            'adaptation_rate': 0.0               # To be implemented
        }
        
        return metrics
    
    def _generate_analysis(self, results: Dict, metrics: Dict, bots: List) -> Dict[str, Any]:
        """Generate comprehensive analysis for research"""
        analysis = {
            'summary': {},
            'statistical_significance': {},
            'recommendations': []
        }
        
        bot_performances = list(metrics['bot_performance'].values())
        if bot_performances:
            win_rates = [p['win_rate'] for p in bot_performances]
            avg_scores = [p['avg_score'] for p in bot_performances]
            
            analysis['summary'] = {
                'mean_win_rate': sum(win_rates) / len(win_rates),
                'win_rate_std': self._calculate_std(win_rates),
                'mean_avg_score': sum(avg_scores) / len(avg_scores),
                'score_std': self._calculate_std(avg_scores),
                'best_performing_bot': max(bot_performances, key=lambda x: x['win_rate']),
                'most_consistent_strategy': self._find_most_consistent_strategy(metrics['strategy_analysis'])
            }
        
        strategy_performances = metrics['strategy_analysis']
        if len(strategy_performances) > 1:
            strategies = list(strategy_performances.keys())
            analysis['statistical_significance'] = {
                'significant_differences': self._test_significance(strategy_performances),
                'confidence_level': self.config['analysis_settings']['statistical_significance']
            }
        
        analysis['recommendations'] = self._generate_recommendations(metrics)
        
        return analysis
    
    def _calculate_std(self, values: List[float]) -> float:
        """Calculate standard deviation"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return variance ** 0.5
    
    def _find_most_consistent_strategy(self, strategy_analysis: Dict) -> str:
        """Find strategy with most consistent performance"""
        if not strategy_analysis:
            return "None"
        
        return max(strategy_analysis.keys(), key=lambda k: strategy_analysis[k]['win_rate'])
    
    def _test_significance(self, strategy_performances: Dict) -> List[str]:
        """Test for statistically significant differences (simplified)"""
        significant_diffs = []
        
        strategies = list(strategy_performances.keys())
        for i, strategy1 in enumerate(strategies):
            for strategy2 in strategies[i+1:]:
                perf1 = strategy_performances[strategy1]['win_rate']
                perf2 = strategy_performances[strategy2]['win_rate']
                
                if abs(perf1 - perf2) > 0.1:  # 10% difference threshold
                    significant_diffs.append(f"{strategy1} vs {strategy2}: {abs(perf1 - perf2):.3f}")
        
        return significant_diffs
    
    def _generate_recommendations(self, metrics: Dict) -> List[str]:
        """Generate research recommendations based on results"""
        recommendations = []
        
        strategy_analysis = metrics['strategy_analysis']
        
        if 'minimax' in strategy_analysis and 'random' in strategy_analysis:
            minimax_wr = strategy_analysis['minimax']['win_rate']
            random_wr = strategy_analysis['random']['win_rate']
            
            if minimax_wr > random_wr + 0.1:
                recommendations.append("Minimax strategy shows significant advantage - investigate depth parameter optimization")
            elif abs(minimax_wr - random_wr) < 0.05:
                recommendations.append("Minimax performance similar to random - check implementation or increase search depth")
        
        if 'card_counting' in strategy_analysis:
            cc_wr = strategy_analysis['card_counting']['win_rate']
            if cc_wr > 0.6:
                recommendations.append("Card counting strategy highly effective - study opponent modeling techniques")
        
        if len(strategy_analysis) > 2:
            win_rates = [s['win_rate'] for s in strategy_analysis.values()]
            if max(win_rates) - min(win_rates) < 0.1:
                recommendations.append("All strategies perform similarly - investigate game balance or add more sophisticated bots")
        
        return recommendations
    
    def _save_results(self, results: Dict[str, Any]):
        """Save simulation results to files"""
        output_dir = Path(self.config['output_settings']['output_dir'])
        output_dir.mkdir(exist_ok=True)
        
        timestamp = int(time.time())
        
        if self.config['output_settings']['save_detailed_logs']:
            json_file = output_dir / f"simulation_results_{timestamp}.json"
            with open(json_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"Detailed results saved to: {json_file}")
        
        if self.config['output_settings']['export_csv']:
            csv_file = output_dir / f"bot_performance_{timestamp}.csv"
            self._save_csv_summary(results, csv_file)
            print(f"CSV summary saved to: {csv_file}")
        
        self._print_summary(results)
    
    def _save_csv_summary(self, results: Dict, csv_file: Path):
        """Save bot performance summary to CSV"""
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Bot Name', 'Bot Type', 'Win Rate', 'Avg Score', 'Games Played', 'Total Wins'])
            
            for bot_name, perf in results['metrics']['bot_performance'].items():
                writer.writerow([
                    bot_name,
                    perf['bot_type'],
                    f"{perf['win_rate']:.3f}",
                    f"{perf['avg_score']:.2f}",
                    perf['games_played'],
                    perf['total_wins']
                ])
    
    def _print_summary(self, results: Dict):
        """Print simulation summary to console"""
        print("\n" + "="*60)
        print("SIMULATION RESULTS SUMMARY")
        print("="*60)
        
        metrics = results['metrics']
        analysis = results['analysis']
        
        print(f"Execution time: {results['execution_time']:.2f} seconds")
        print(f"Tournament type: {results['configuration']['tournament_settings']['tournament_type']}")
        
        print("\nBot Performance:")
        for bot_name, perf in metrics['bot_performance'].items():
            print(f"  {bot_name:15} | Win Rate: {perf['win_rate']:.3f} | Avg Score: {perf['avg_score']:.2f}")
        
        print("\nStrategy Analysis:")
        for strategy, stats in metrics['strategy_analysis'].items():
            print(f"  {strategy.capitalize():15} | Win Rate: {stats['win_rate']:.3f} | Games: {stats['total_games']}")
        
        if analysis['summary']:
            print(f"\nOverall Statistics:")
            summary = analysis['summary']
            print(f"  Mean win rate: {summary['mean_win_rate']:.3f} ± {summary['win_rate_std']:.3f}")
            print(f"  Best bot: {summary['best_performing_bot']['bot_type']} ({summary['best_performing_bot']['win_rate']:.3f})")
        
        if analysis['recommendations']:
            print("\nResearch Recommendations:")
            for i, rec in enumerate(analysis['recommendations'], 1):
                print(f"  {i}. {rec}")
        
        print("="*60)


def create_sample_config():
    """Create a sample configuration file"""
    sample_config = {
        "bot_composition": {
            "random": 3,
            "greedy": 2,
            "card_counting": 1,
            "minimax": 1
        },
        "tournament_settings": {
            "games_per_matchup": 50,
            "tournament_type": "round_robin"
        },
        "analysis_settings": {
            "track_decision_patterns": True,
            "generate_heatmaps": False,
            "statistical_significance": 0.05
        },
        "output_settings": {
            "save_detailed_logs": True,
            "export_csv": True,
            "generate_plots": False,
            "output_dir": "simulation_results"
        }
    }
    
    with open("simulation_config.json", "w") as f:
        json.dump(sample_config, f, indent=2)
    
    print("Sample configuration saved to: simulation_config.json")


def main():
    """Main entry point for simulation runner"""
    parser = argparse.ArgumentParser(description="Remove One Bot Simulation Runner")
    parser.add_argument("--config", "-c", help="Configuration file path")
    parser.add_argument("--create-config", action="store_true", help="Create sample configuration file")
    parser.add_argument("--games", "-g", type=int, help="Number of games per matchup")
    parser.add_argument("--tournament", "-t", choices=['round_robin', 'elimination', 'league'], 
                       help="Tournament type")
    parser.add_argument("--bots", help="Bot composition (e.g., 'random:2,greedy:2,minimax:3')")
    
    args = parser.parse_args()
    
    if args.create_config:
        create_sample_config()
        return
    
    try:
        runner = SimulationRunner(args.config)
        
        if args.games:
            runner.config['tournament_settings']['games_per_matchup'] = args.games
        
        if args.tournament:
            runner.config['tournament_settings']['tournament_type'] = args.tournament
        
        if args.bots:
            bot_comp = {}
            for bot_spec in args.bots.split(','):
                bot_type, count = bot_spec.split(':')
                bot_comp[bot_type.strip()] = int(count)
            runner.config['bot_composition'] = bot_comp
        
        results = runner.run_simulation()
        
        print(f"\nSimulation completed successfully!")
        print(f"Results saved to: {runner.config['output_settings']['output_dir']}")
        
    except Exception as e:
        print(f"Error running simulation: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
