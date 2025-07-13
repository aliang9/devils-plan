import time
import os
from contextlib import contextmanager
from collections import defaultdict
from typing import Dict, Any


class BotProfiler:
    """Performance monitoring for bots"""
    
    def __init__(self):
        self.decision_times = defaultdict(list)
        self.memory_usage = defaultdict(list)
        self.action_counts = defaultdict(int)
    
    @contextmanager
    def profile_decision(self, bot_name: str):
        """Context manager for timing bot decisions"""
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        yield
        
        end_time = time.time()
        end_memory = self._get_memory_usage()
        
        self.decision_times[bot_name].append(end_time - start_time)
        self.memory_usage[bot_name].append(end_memory - start_memory)
        self.action_counts[bot_name] += 1
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            import psutil
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            return 0.0
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate performance analysis report"""
        report = {}
        
        for bot_name in self.decision_times:
            times = self.decision_times[bot_name]
            memory = self.memory_usage[bot_name]
            
            report[bot_name] = {
                'avg_decision_time': sum(times) / len(times),
                'max_decision_time': max(times),
                'total_decisions': self.action_counts[bot_name],
                'avg_memory_delta': sum(memory) / len(memory) if memory else 0,
                'max_memory_delta': max(memory) if memory else 0,
            }
        
        return report
