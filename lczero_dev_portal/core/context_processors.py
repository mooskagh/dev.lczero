"""
Context processors for LCZero Dev Portal.

Provides global context data available to all templates.
"""

from lczero_dev_portal.menu import get_active_menu_item, get_menu_for_user


def menu_context(request):
    """
    Add menu data to template context.

    Args:
        request: Django HttpRequest object

    Returns:
        Dictionary with menu context data
    """
    if not hasattr(request, "user"):
        return {"menu_groups": [], "active_menu_item": None}

    menu_groups = get_menu_for_user(request.user, request.path)
    active_item = get_active_menu_item(menu_groups, request.path)

    return {
        "menu_groups": menu_groups,
        "active_menu_item": active_item,
    }
