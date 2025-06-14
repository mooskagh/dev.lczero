# Discord Authentication & Multifunctional Bot Implementation Plan

## Overview
Implement Discord OAuth2 authentication with environment-specific callback URLs and a standalone multifunctional Discord bot for role synchronization and future features.

## Phase 1: Discord Developer Portal Setup

### 1.1 OAuth2 Application Setup
**Step-by-step Discord Developer Portal instructions:**
1. Go to https://discord.com/developers/applications
2. Click "New Application" → Name: "LCZero Dev Portal"
3. Navigate to "OAuth2" → "General"
4. Add Redirect URIs:
   - Production: `https://dev.lczero.org/auth/discord/callback/`
   - Development: `https://dev-dev.lczero.org/auth/discord/callback/`
   - Local dev: `http://localhost:8000/auth/discord/callback/`
5. Set Scopes: `identify`, `email`, `guilds.members.read`
6. Copy Client ID and Client Secret for environment configuration

### 1.2 Bot Application Setup
1. Same application → "Bot" section
2. Click "Add Bot"
3. Configure bot permissions: `Read Messages`, `Manage Roles`, `View Server`
4. Copy Bot Token for standalone bot application
5. Enable "Server Members Intent" and "Message Content Intent"

## Phase 2: Django OAuth2 Implementation

### 2.1 Dependencies & Configuration
- Install `django-allauth[discord]`
- Configure environment-specific callback URLs
- Implement custom Discord provider if needed for additional scopes
- Set up environment variables: `DISCORD_CLIENT_ID`, `DISCORD_CLIENT_SECRET`

### 2.2 User Model & Authentication
- Extend Django User model with Discord fields (discord_id, discord_username, avatar_url)
- Configure Django to use Discord-only authentication
- Implement user registration/login flow
- Handle Discord profile updates

## Phase 3: Standalone Multifunctional Discord Bot

### 3.1 Bot Architecture
```
discord_bot/
├── __init__.py
├── main.py                 # Entry point with django.setup()
├── bot.py                  # Discord bot instance and event handlers
├── cogs/
│   ├── __init__.py
│   ├── role_sync.py        # Role synchronization functionality  
│   ├── moderation.py       # Future: moderation features
│   └── notifications.py   # Future: notification system
├── models.py              # Django model interactions
├── config.py              # Bot configuration
└── requirements.txt       # Bot-specific dependencies
```

### 3.2 Role Synchronization Features
- Monitor Discord role changes via bot events
- Periodic full role sync (configurable interval)
- Real-time role updates when users join/leave/change roles
- Role mapping configuration (Discord role → Django group)
- Audit logging for role changes

### 3.3 Bot Extensibility
- Cog-based architecture for modularity
- Database integration via Django ORM
- Event-driven role synchronization
- Future features: competition notifications, PR status updates, etc.

## Implementation Priority
1. Discord Developer Portal setup documentation
2. Django OAuth2 authentication implementation
3. Standalone bot foundation with Django integration
4. Role synchronization cog implementation
5. Documentation and deployment guides

This approach provides a scalable foundation for Discord integration while maintaining separation between the web application and bot functionality.