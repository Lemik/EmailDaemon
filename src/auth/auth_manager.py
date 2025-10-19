import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from ..core.config import Config
from ..core.exceptions import AuthenticationError

class AuthManager:
    def __init__(self):
        self.config = Config()
        self.secret_key = self.config.get('JWT_SECRET_KEY', 'your-secret-key')
        self.token_expiry = int(self.config.get('TOKEN_EXPIRY_HOURS', '24'))

    def generate_token(self, user_data: Dict[str, Any]) -> str:
        """
        Generate a JWT token for a user.
        
        Args:
            user_data: Dictionary containing user information
            
        Returns:
            JWT token string
        """
        try:
            # Add expiration time
            payload = {
                'user_id': user_data['id'],
                'email': user_data['email'],
                'role': user_data.get('role', 'user'),
                'exp': datetime.utcnow() + timedelta(hours=self.token_expiry)
            }
            
            # Generate token
            token = jwt.encode(payload, self.secret_key, algorithm='HS256')
            return token
        except Exception as e:
            raise AuthenticationError(f"Failed to generate token: {str(e)}")

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify a JWT token and return the payload.
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token payload or None if invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid token")
        except Exception as e:
            raise AuthenticationError(f"Failed to verify token: {str(e)}")

    def refresh_token(self, token: str) -> str:
        """
        Refresh an existing token.
        
        Args:
            token: Current JWT token
            
        Returns:
            New JWT token
        """
        try:
            # Verify current token
            payload = self.verify_token(token)
            
            # Generate new token with same data
            return self.generate_token(payload)
        except Exception as e:
            raise AuthenticationError(f"Failed to refresh token: {str(e)}")

    def validate_credentials(self, email: str, password: str) -> Dict[str, Any]:
        """
        Validate user credentials.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            User data if valid
            
        Raises:
            AuthenticationError: If credentials are invalid
        """
        try:
            # TODO: Implement actual credential validation
            # This is a placeholder for database validation
            user_data = {
                'id': 'user123',
                'email': email,
                'role': 'user'
            }
            return user_data
        except Exception as e:
            raise AuthenticationError(f"Failed to validate credentials: {str(e)}") 