# LCZero Dev Portal Installation Guide

## Discord OAuth2 Setup

After running migrations, setup Discord integration:

```bash
python manage.py setup_discord
```

For custom domain (e.g., production):
```bash
python manage.py setup_discord --domain dev.lczero.org
```

## Discord Developer Portal Configuration

Add the callback URL to your Discord application:

1. Go to https://discord.com/developers/applications
2. Select your "LCZero Dev Portal" application  
3. Navigate to "OAuth2" → "General"
4. Add to Redirect URIs:
   - Local: `http://127.0.0.1:8000/auth/discord/login/callback/`
   - Production: `https://dev.lczero.org/auth/discord/login/callback/`