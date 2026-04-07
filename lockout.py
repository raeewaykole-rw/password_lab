import time
from collections import defaultdict
from typing import DefaultDict, Dict, List


class LockoutPolicy:
    def __init__(self, threshold: int = 5, lock_seconds: int = 60) -> None:
        self.threshold = threshold
        self.lock_seconds = lock_seconds
        self._attempts: DefaultDict[str, List[float]] = defaultdict(list)
        self._locked_until: Dict[str, float] = {}

    def is_locked(self, user_id: str) -> bool:
        now = time.time()
        until = self._locked_until.get(user_id, 0)
        return now < until

    def record_failure(self, user_id: str) -> bool:
        now = time.time()
        self._attempts[user_id].append(now)
        if len(self._attempts[user_id]) >= self.threshold:
            self._locked_until[user_id] = now + self.lock_seconds
            self._attempts[user_id].clear()
            return True
        return False

    def reset(self, user_id: str) -> None:
        self._attempts[user_id].clear()
        self._locked_until.pop(user_id, None)
