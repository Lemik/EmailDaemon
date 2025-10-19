from typing import Dict, Any, List
from ..core.exceptions import AuthorizationError

class PermissionManager:
    def __init__(self):
        self.role_permissions = {
            'admin': ['read', 'write', 'delete', 'manage_users'],
            'manager': ['read', 'write'],
            'user': ['read']
        }

    def check_permission(self, role: str, permission: str) -> bool:
        """
        Check if a role has a specific permission.
        
        Args:
            role: User role
            permission: Permission to check
            
        Returns:
            True if role has permission, False otherwise
        """
        return permission in self.role_permissions.get(role, [])

    def get_role_permissions(self, role: str) -> List[str]:
        """
        Get all permissions for a role.
        
        Args:
            role: User role
            
        Returns:
            List of permissions
        """
        return self.role_permissions.get(role, [])

    def authorize(self, user_data: Dict[str, Any], required_permission: str) -> None:
        """
        Authorize a user for a specific action.
        
        Args:
            user_data: User data including role
            required_permission: Permission required for the action
            
        Raises:
            AuthorizationError: If user is not authorized
        """
        role = user_data.get('role', 'user')
        if not self.check_permission(role, required_permission):
            raise AuthorizationError(
                f"User with role '{role}' is not authorized for '{required_permission}'"
            )

    def add_role_permission(self, role: str, permission: str) -> None:
        """
        Add a permission to a role.
        
        Args:
            role: Role to modify
            permission: Permission to add
        """
        if role not in self.role_permissions:
            self.role_permissions[role] = []
        if permission not in self.role_permissions[role]:
            self.role_permissions[role].append(permission)

    def remove_role_permission(self, role: str, permission: str) -> None:
        """
        Remove a permission from a role.
        
        Args:
            role: Role to modify
            permission: Permission to remove
        """
        if role in self.role_permissions and permission in self.role_permissions[role]:
            self.role_permissions[role].remove(permission) 