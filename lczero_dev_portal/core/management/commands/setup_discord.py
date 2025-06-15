import os

from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Setup Discord OAuth2 integration"

    def add_arguments(self, parser):
        parser.add_argument(
            "--domain",
            type=str,
            default="127.0.0.1:8000",
            help="Domain for the site (default: 127.0.0.1:8000)",
        )

    def handle(self, *args, **options):
        domain = options["domain"]

        # Update Site configuration
        try:
            site = Site.objects.get(id=1)
            site.domain = domain
            site.name = f"LCZero Dev Portal ({domain})"
            site.save()
            self.stdout.write(
                self.style.SUCCESS(f"Updated site domain to: {domain}")
            )
        except Site.DoesNotExist:
            site = Site.objects.create(
                id=1, domain=domain, name=f"LCZero Dev Portal ({domain})"
            )
            self.stdout.write(
                self.style.SUCCESS(f"Created site with domain: {domain}")
            )

        # Get Discord credentials from environment
        client_id = os.environ.get("DISCORD_CLIENT_ID")
        client_secret = os.environ.get("DISCORD_CLIENT_SECRET")

        if not client_id or not client_secret:
            self.stdout.write(
                self.style.ERROR(
                    "DISCORD_CLIENT_ID and DISCORD_CLIENT_SECRET must be set in environment"
                )
            )
            return

        # Create or update Discord SocialApp
        app, created = SocialApp.objects.get_or_create(
            provider="discord",
            defaults={
                "name": "Discord",
                "client_id": client_id,
                "secret": client_secret,
            },
        )

        if not created:
            app.client_id = client_id
            app.secret = client_secret
            app.save()
            self.stdout.write(
                self.style.SUCCESS("Updated existing Discord SocialApp")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("Created new Discord SocialApp")
            )

        # Associate with site
        app.sites.add(site)

        self.stdout.write(
            self.style.SUCCESS(
                f"Discord OAuth2 setup complete!\n"
                f"Callback URL: http://{domain}/auth/discord/login/callback/"
            )
        )
