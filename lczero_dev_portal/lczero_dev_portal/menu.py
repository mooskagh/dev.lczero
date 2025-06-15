"""
Menu system configuration for LCZero Dev Portal.

This module defines the menu structure using static Python configuration,
providing a mikrotik webfig-like two-level navigation system.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class MenuItem:
    """Represents a single menu item."""

    title: str
    url: str
    url_prefix: str
    icon: Optional[str] = None
    permissions: Optional[List[str]] = None


@dataclass
class MenuGroup:
    """Represents a menu group with nested items."""

    title: str
    icon: Optional[str] = None
    permissions: Optional[List[str]] = None
    items: Optional[List[MenuItem]] = None

    def __post_init__(self):
        if self.items is None:
            self.items = []


# Main menu structure - top-level items for Home and Artifacts
MENU_STRUCTURE = [
    MenuGroup(
        title="Home",
        icon="home",
        permissions=None,
        items=[
            MenuItem(title="Home", url="/", url_prefix="/", icon="home"),
        ],
    ),
    MenuGroup(
        title="Artifacts",
        icon="archive",
        permissions=None,
        items=[
            MenuItem(
                title="Artifacts",
                url="/artifacts/",
                url_prefix="/artifacts",
                icon="archive",
            ),
        ],
    ),
]


def get_menu_for_user(user, current_path: str = "") -> List[MenuGroup]:
    """
    Get filtered menu structure for a specific user based on permissions.

    Args:
        user: Django user object
        current_path: Current request path for marking active items

    Returns:
        List of MenuGroup objects filtered by user permissions
    """
    filtered_menu = []

    for group in MENU_STRUCTURE:
        # Check group permissions
        if not _has_permission(user, group.permissions):
            continue

        # Filter items within the group
        filtered_items = [
            item
            for item in group.items or []
            if _has_permission(user, item.permissions)
        ]

        # Only include group if it has visible items
        if filtered_items:
            filtered_menu.append(
                MenuGroup(
                    title=group.title,
                    icon=group.icon,
                    permissions=group.permissions,
                    items=filtered_items,
                )
            )

    return filtered_menu


def _has_permission(user, required_permissions: Optional[List[str]]) -> bool:
    """
    Check if user has required permissions.

    Args:
        user: Django user object
        required_permissions: List of required permission names, or None

    Returns:
        True if user has access, False otherwise
    """
    if required_permissions is None:
        # No specific permissions required - allow all users
        return True

    if not user.is_authenticated:
        return False

    # For now, just check if user is staff/admin for any restricted permissions
    # This can be extended later to check Django groups or Discord roles
    return user.is_staff or user.is_superuser


def get_active_menu_item(
    menu_groups: List[MenuGroup], current_path: str
) -> Optional[MenuItem]:
    """
    Find the currently active menu item based on URL path.

    Args:
        menu_groups: List of menu groups to search
        current_path: Current request path

    Returns:
        Active MenuItem or None
    """
    # Sort items by url_prefix length (longest first) for specific matching
    all_items = [item for group in menu_groups for item in group.items or []]

    # Sort by url_prefix length descending to match most specific path first
    all_items.sort(key=lambda x: len(x.url_prefix), reverse=True)

    for item in all_items:
        if current_path.startswith(item.url_prefix):
            return item
    return None
