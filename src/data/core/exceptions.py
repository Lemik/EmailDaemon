class ValidationError(Exception):
    """Exception raised for validation errors"""
    pass

class DataAccessError(Exception):
    """Exception raised for data access errors"""
    pass

class CacheError(Exception):
    """Exception raised for cache-related errors"""
    pass 