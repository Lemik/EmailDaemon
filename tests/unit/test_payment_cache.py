import pytest
from datetime import datetime, timedelta
from src.data.access.payment_cache import PaymentDataCache, CacheEntry

@pytest.fixture
def cache():
    """Create a PaymentDataCache instance for testing"""
    return PaymentDataCache(default_ttl=60, max_size=5)

def test_cache_entry_expiration():
    """Test cache entry expiration"""
    # Create entry with 1 second TTL
    entry = CacheEntry("test_data", 1)
    assert not entry.is_expired()
    
    # Wait for expiration
    import time
    time.sleep(1.1)
    assert entry.is_expired()

def test_basic_cache_operations(cache):
    """Test basic cache operations"""
    # Test setting and getting data
    cache.set("test_key", "test_value")
    assert cache.get("test_key") == "test_value"
    
    # Test deleting data
    cache.delete("test_key")
    assert cache.get("test_key") is None
    
    # Test clearing cache
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.clear()
    assert cache.get("key1") is None
    assert cache.get("key2") is None

def test_cache_size_limit(cache):
     """Test cache size limit enforcement"""
     # Fill cache beyond limit
     for i in range(10):
        cache.set(f"key{i}", f"value{i}")
    
     # Check that only the most recent entries are kept
     assert len(cache._cache) == 5
     assert "key9" in cache._cache
     assert "key0" not in cache._cache

def test_tenant_payments_caching(cache):
    """Test tenant payments caching"""
    tenant_id = "TENANT_001"
    start_date = datetime.now()
    end_date = start_date + timedelta(days=30)
    payments = [{"id": 1, "amount": 1000}]
    
    # Test setting and getting tenant payments
    cache.set_tenant_payments(tenant_id, start_date, end_date, payments)
    cached_payments = cache.get_tenant_payments(tenant_id, start_date, end_date)
    assert cached_payments == payments
    
    # Test cache invalidation
    cache.invalidate_tenant_data(tenant_id)
    assert cache.get_tenant_payments(tenant_id, start_date, end_date) is None

def test_property_payments_caching(cache):
    """Test property payments caching"""
    property_id = "PROPERTY_001"
    month = 1
    year = 2024
    payments = [{"id": 1, "amount": 1000}]
    
    # Test setting and getting property payments
    cache.set_property_payments(property_id, month, year, payments)
    cached_payments = cache.get_property_payments(property_id, month, year)
    assert cached_payments == payments
    
    # Test cache invalidation
    cache.invalidate_property_data(property_id)
    assert cache.get_property_payments(property_id, month, year) is None

def test_tenant_agreements_caching(cache):
    """Test tenant agreements caching"""
    tenant_id = "TENANT_001"
    agreements = [{"id": 1, "amount": 1000}]
    
    # Test setting and getting tenant agreements
    cache.set_tenant_agreements(tenant_id, agreements)
    cached_agreements = cache.get_tenant_agreements(tenant_id)
    assert cached_agreements == agreements
    
    # Test cache invalidation
    cache.invalidate_tenant_data(tenant_id)
    assert cache.get_tenant_agreements(tenant_id) is None

def test_custom_ttl(cache):
    """Test custom TTL for cache entries"""
    # Set entry with custom TTL
    cache.set("test_key", "test_value", ttl=1)
    assert cache.get("test_key") == "test_value"
    
    # Wait for expiration
    import time
    time.sleep(1.1)
    assert cache.get("test_key") is None

def test_thread_safety(cache):
    """Test thread safety of cache operations"""
    import threading
    
    def worker():
        for i in range(100):
            cache.set(f"key{i}", f"value{i}")
            cache.get(f"key{i}")
    
    # Create multiple threads
    threads = [threading.Thread(target=worker) for _ in range(5)]
    
    # Start all threads
    for thread in threads:
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Verify cache is in a valid state
    assert len(cache._cache) <= cache._max_size 