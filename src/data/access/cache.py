from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from ...core.config import Config
from ...core.exceptions import DataAccessError

class DataCache:
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._ttl = Config.CACHE_TTL

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve data from cache if it exists and is not expired.
        
        Args:
            key: Cache key
            
        Returns:
            Cached data or None if not found or expired
        """
        if key in self._cache:
            cache_entry = self._cache[key]
            if datetime.now() - cache_entry['timestamp'] < timedelta(seconds=self._ttl):
                return cache_entry['data']
            else:
                del self._cache[key]
        return None

    def set(self, key: str, data: Dict[str, Any]) -> None:
        """
        Store data in cache with timestamp.
        
        Args:
            key: Cache key
            data: Data to cache
        """
        self._cache[key] = {
            'data': data,
            'timestamp': datetime.now()
        }

    def clear(self, key: Optional[str] = None) -> None:
        """
        Clear cache entry or entire cache.
        
        Args:
            key: Optional specific key to clear, if None clears entire cache
        """
        if key:
            if key in self._cache:
                del self._cache[key]
        else:
            self._cache.clear()

    def is_valid(self, key: str) -> bool:
        """
        Check if cache entry exists and is not expired.
        
        Args:
            key: Cache key
            
        Returns:
            True if valid, False otherwise
        """
        if key in self._cache:
            return datetime.now() - self._cache[key]['timestamp'] < timedelta(seconds=self._ttl)
        return False 