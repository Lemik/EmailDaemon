from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from threading import Lock
from ..core.exceptions import CacheError

class CacheEntry:
    """Represents a single cache entry with data and metadata"""
    def __init__(self, data: Any, ttl: int):
        self.data = data
        self.created_at = datetime.now()
        self.last_accessed = datetime.now()
        self.ttl = ttl

    def is_expired(self) -> bool:
        """Check if the cache entry has expired"""
        return (datetime.now() - self.created_at).total_seconds() > self.ttl

    def update_access_time(self):
        """Update the last accessed time"""
        self.last_accessed = datetime.now()

class PaymentDataCache:
    """Cache for payment-related data to improve performance"""
    
    def __init__(self, default_ttl: int = 3600, max_size: int = 1000):
        """
        Initialize the cache
        
        Args:
            default_ttl (int): Default time-to-live for cache entries in seconds
            max_size (int): Maximum number of entries in the cache
        """
        self._cache: Dict[str, CacheEntry] = {}
        self._default_ttl = default_ttl
        self._max_size = max_size
        self._lock = Lock()
        
    def _generate_key(self, prefix: str, *args) -> str:
        """Generate a cache key from prefix and arguments"""
        return f"{prefix}:{':'.join(str(arg) for arg in args)}"
        
    def _cleanup_expired(self):
        """Remove expired entries from the cache"""
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.is_expired()
        ]
        if expired_keys:
            with self._lock:
                for key in expired_keys:
                    self._cache.pop(key, None)
                
    def _enforce_size_limit(self):
        """Remove least recently used entries if cache size exceeds limit"""
        current_size = len(self._cache)
        if current_size <= self._max_size:
            return
            
        # Sort by last access time and remove least recently used entries
        with self._lock:
            if len(self._cache) <= self._max_size:  # Double-check under lock
                return
            sorted_entries = sorted(
                self._cache.items(),
                key=lambda x: x[1].last_accessed
            )
            entries_to_remove = len(self._cache) - self._max_size
            for key, _ in sorted_entries[:entries_to_remove]:
                self._cache.pop(key, None)
                    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve data from cache
        
        Args:
            key (str): Cache key
            
        Returns:
            Optional[Any]: Cached data if found and not expired, None otherwise
        """
        self._cleanup_expired()
        with self._lock:
            entry = self._cache.get(key)
            if entry and not entry.is_expired():
                entry.update_access_time()
                return entry.data
            return None
            
    def set(self, key: str, data: Any, ttl: Optional[int] = None) -> None:
        """
        Store data in cache
        
        Args:
            key (str): Cache key
            data (Any): Data to cache
            ttl (Optional[int]): Time-to-live in seconds, uses default if None
        """
        with self._lock:
            self._cache[key] = CacheEntry(data, ttl or self._default_ttl)
        self._enforce_size_limit()  # Move outside lock to reduce contention
            
    def delete(self, key: str) -> None:
        """
        Remove data from cache
        
        Args:
            key (str): Cache key to remove
        """
        with self._lock:
            self._cache.pop(key, None)
            
    def clear(self) -> None:
        """Clear all cached data"""
        with self._lock:
            self._cache.clear()
            
    # Payment-specific cache methods
    
    def get_tenant_payments(self, tenant_id: str, 
                          start_date: datetime,
                          end_date: datetime) -> Optional[List[Dict]]:
        """Get cached tenant payments for a date range"""
        key = self._generate_key('tenant_payments', tenant_id, 
                               start_date.strftime('%Y%m%d'),
                               end_date.strftime('%Y%m%d'))
        return self.get(key)
        
    def set_tenant_payments(self, tenant_id: str,
                          start_date: datetime,
                          end_date: datetime,
                          payments: List[Dict],
                          ttl: Optional[int] = None) -> None:
        """Cache tenant payments for a date range"""
        key = self._generate_key('tenant_payments', tenant_id,
                               start_date.strftime('%Y%m%d'),
                               end_date.strftime('%Y%m%d'))
        self.set(key, payments, ttl)
        
    def get_property_payments(self, property_id: str,
                            month: int,
                            year: int) -> Optional[List[Dict]]:
        """Get cached property payments for a month/year"""
        key = self._generate_key('property_payments', property_id, month, year)
        return self.get(key)
        
    def set_property_payments(self, property_id: str,
                            month: int,
                            year: int,
                            payments: List[Dict],
                            ttl: Optional[int] = None) -> None:
        """Cache property payments for a month/year"""
        key = self._generate_key('property_payments', property_id, month, year)
        self.set(key, payments, ttl)
        
    def get_tenant_agreements(self, tenant_id: str) -> Optional[List[Dict]]:
        """Get cached tenant agreements"""
        key = self._generate_key('tenant_agreements', tenant_id)
        return self.get(key)
        
    def set_tenant_agreements(self, tenant_id: str,
                            agreements: List[Dict],
                            ttl: Optional[int] = None) -> None:
        """Cache tenant agreements"""
        key = self._generate_key('tenant_agreements', tenant_id)
        self.set(key, agreements, ttl)
        
    def invalidate_tenant_data(self, tenant_id: str) -> None:
        """Invalidate all cached data for a tenant"""
        with self._lock:
            keys_to_remove = [
                key for key in self._cache.keys()
                if key.startswith(f'tenant_payments:{tenant_id}:') or
                   key.startswith(f'tenant_agreements:{tenant_id}')
            ]
            for key in keys_to_remove:
                del self._cache[key]
                
    def invalidate_property_data(self, property_id: str) -> None:
        """Invalidate all cached data for a property"""
        with self._lock:
            keys_to_remove = [
                key for key in self._cache.keys()
                if key.startswith(f'property_payments:{property_id}:')
            ]
            for key in keys_to_remove:
                del self._cache[key] 