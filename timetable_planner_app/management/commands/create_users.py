from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Create multiple users with profiles'

    def handle(self, *args, **options):
        users_to_create = [
            ('teacher1', 'teacher1@example.com', 'pass1234'),
            ('teacher2', 'teacher2@example.com', 'pass1234'),
            ('admin1', 'admin1@example.com', 'adminpass'),
        ]

        for username, email, password in users_to_create:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username=username, email=email, password=password)
                self.stdout.write(self.style.SUCCESS(f'Created user {username} with profile {user.userprofile}'))
            else:
                self.stdout.write(self.style.WARNING(f'User {username} already exists'))
