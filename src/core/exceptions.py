class EmailDaemonError(Exception):
    """Base exception class for all EmailDaemon errors."""
    pass

class DataAccessError(EmailDaemonError):
    """Raised when there's an error accessing the database."""
    pass

class DataValidationError(EmailDaemonError):
    """Raised when data validation fails."""
    pass

class EmailProcessingError(EmailDaemonError):
    """Raised when there's an error processing emails."""
    pass

class NotificationError(EmailDaemonError):
    """Raised when there's an error sending notifications."""
    pass

class AnalysisError(EmailDaemonError):
    """Raised when there's an error during payment analysis."""
    pass

class ConfigurationError(EmailDaemonError):
    """Raised when there's an error in the configuration."""
    pass

class AuthenticationError(EmailDaemonError):
    """Raised when there's an error during authentication."""
    pass

class AuthorizationError(EmailDaemonError):
    """Raised when there's an error during authorization."""
    pass

class ValidationError(Exception):
    """Exception raised for validation errors"""
    pass

class CacheError(Exception):
    """Exception raised for cache-related errors"""
    pass 