from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a superuser for testing'

    def handle(self, *args, **options):
        # Check if superuser already exists
        if User.objects.filter(email='admin@example.com').exists():
            self.stdout.write(self.style.WARNING('Superuser admin@example.com already exists'))
            admin_user = User.objects.get(email='admin@example.com')
            # Ensure the user is active and a superuser
            if not admin_user.is_active or not admin_user.is_superuser:
                admin_user.is_active = True
                admin_user.is_superuser = True
                admin_user.is_staff = True
                admin_user.save()
                self.stdout.write(self.style.SUCCESS('Updated admin@example.com to be active and superuser'))
            # Reset password
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Reset password for admin@example.com to "admin123"'))
        else:
            # Create a new superuser
            User.objects.create_superuser(
                email='admin@example.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(self.style.SUCCESS('Created superuser admin@example.com with password "admin123"'))
        
        # List all users
        self.stdout.write(self.style.SUCCESS(f'Total users: {User.objects.count()}'))
        self.stdout.write('All users:')
        for user in User.objects.all():
            self.stdout.write(f'- {user.email} (active: {user.is_active}, superuser: {user.is_superuser}, role: {user.role})')
