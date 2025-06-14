# Menu System Plan: Mikrotik-style Interface

## Overview
Implementation plan for a mikrotik webfig-like menu structure with two-level navigation, icons, and permission-based visibility using static Python configuration.

## Approach: Static Python Configuration

Create a `menu.py` file with menu structure defined in Python code. This approach provides:
- No database overhead
- Easy to maintain and version control
- Clear, centralized configuration
- Simple permission management

## Implementation Plan

### 1. Create Menu Infrastructure
- Create `lczero_dev_portal/menu.py` with menu configuration classes
- Define MenuItem and MenuGroup classes with fields:
  - title
  - url (to navigate to when clicked)
  - url_prefix (for marking as "current")
  - icon
  - permissions (which user groups should see it)

### 2. Template Integration  
- Create base template `templates/base.html` with sidebar menu structure
- Add CSS for mikrotik-style two-level menu layout
- Create template context processor to make menu available globally

### 3. Context Processor
- Create `core/context_processors.py` to inject menu data into all templates
- Handle permission-based menu filtering
- Mark current menu item based on URL matching

### 4. Update Settings
- Add context processor to TEMPLATES configuration
- Configure static files for menu CSS/JS if needed

### 5. Convert Existing Template
- Update `core/templates/core/home.html` to extend base template
- Remove inline styles and use new base template structure

## Menu Structure Example

```python
MENU_STRUCTURE = [
    MenuGroup(
        title="Dashboard",
        icon="fas fa-home",
        permissions=None,  # Visible to all authenticated users
        items=[
            MenuItem(title="Home", url="/", url_prefix="/", icon="fas fa-home"),
            MenuItem(title="Status", url="/status/", url_prefix="/status", icon="fas fa-info-circle"),
        ]
    ),
    MenuGroup(
        title="Development",
        icon="fas fa-code",
        permissions=["developers", "admins"],  # Only specific groups
        items=[
            MenuItem(title="Blunderbase", url="/blunderbase/", url_prefix="/blunderbase", icon="fas fa-chess"),
            MenuItem(title="PR Builds", url="/builds/", url_prefix="/builds", icon="fas fa-hammer"),
            MenuItem(title="Networks", url="/networks/", url_prefix="/networks", icon="fas fa-network-wired"),
        ]
    ),
    MenuGroup(
        title="Admin",
        icon="fas fa-cog",
        permissions=["admins"],  # Admin only
        items=[
            MenuItem(title="User Management", url="/admin/users/", url_prefix="/admin/users", icon="fas fa-users"),
            MenuItem(title="System Config", url="/admin/config/", url_prefix="/admin/config", icon="fas fa-wrench"),
        ]
    ),
]
```

## Permission Configuration
- `permissions=None` - Visible to all authenticated users
- `permissions=["group1", "group2"]` - Visible only to users in specified groups
- Permission checking handled in context processor
- Groups can be Django groups or custom Discord role mappings

## Benefits
- Clean, maintainable solution similar to mikrotik's webfig interface
- No database tables required
- Easy permission management through Python configuration
- Centralized menu structure
- Version controlled alongside code