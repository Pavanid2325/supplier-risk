import threading
import time
from typing import List, Dict, Any

class NaiveReducer:
    """
    Demonstrates unsafe shared mutation race condition for test verification.
    Under heavy multi-threading without locks, appending to shared state can drop items or corrupt count.
    """
    def __init__(self):
        self.results = []
        self.count = 0

    def add_result(self, result: Any):
        # Intentional unsafety simulation for race condition test
        current = self.count
        time.sleep(0.001)  # Context switch window
        self.count = current + 1
        self.results.append(result)

class SafeReducer:
    """
    Thread-safe deterministic reducer using a Reentrant Lock and immutable list aggregation.
    Ensures exactly expected count of tool execution results (4 out of 4).
    """
    def __init__(self):
        self._results: Dict[str, Any] = {}
        self._lock = threading.Lock()

    def add_result(self, tool_name: str, result: Dict[str, Any]):
        with self._lock:
            self._results[tool_name] = result

    def get_aggregated_results(self) -> Dict[str, Any]:
        with self._lock:
            return dict(self._results)
