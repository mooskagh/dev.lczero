from allauth.socialaccount.models import SocialAccount
from core.models import User
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Make a user a superuser by Discord ID or Django User ID"

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            "--discord-id",
            type=str,
            help="Discord ID of the user (numeric, e.g., 123456789012345678)",
        )
        group.add_argument(
            "--discord-username",
            type=str,
            help="Discord username of the user",
        )
        group.add_argument(
            "--user-id",
            type=int,
            help="Django User model ID (numeric)",
        )

    def handle(self, *args, **options):
        discord_id = options.get("discord_id")
        discord_username = options.get("discord_username")
        user_id = options.get("user_id")

        try:
            if discord_id:
                social_account = SocialAccount.objects.get(
                    provider="discord", uid=discord_id
                )
                user = social_account.user
                identifier = f"Discord ID: {discord_id}"
            elif discord_username:
                social_account = SocialAccount.objects.get(
                    provider="discord", extra_data__username=discord_username
                )
                user = social_account.user
                identifier = f"Discord username: {discord_username}"
            else:
                user = User.objects.get(id=user_id)
                identifier = f"User ID: {user_id}"
        except (SocialAccount.DoesNotExist, User.DoesNotExist) as e:
            error_messages = {
                "discord_id": (
                    f"User with Discord ID '{discord_id}' does not exist. User"
                    " must log in via Discord authentication first."
                ),
                "discord_username": (
                    f"User with Discord username '{discord_username}' does not"
                    " exist. User must log in via Discord authentication"
                    " first."
                ),
                "user_id": f"User with ID '{user_id}' does not exist.",
            }

            if discord_id:
                key = "discord_id"
            elif discord_username:
                key = "discord_username"
            else:
                key = "user_id"

            raise CommandError(error_messages[key]) from e

        if user.is_superuser:
            self.stdout.write(
                self.style.WARNING(
                    f"User {user.username} ({identifier}) "
                    "is already a superuser"
                )
            )
            return

        user.is_superuser = True
        user.is_staff = True
        user.save()
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully made {user.username} ({identifier}) a superuser"
            )
        )
