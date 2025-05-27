from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from companies.models import Company

User = get_user_model()

class Command(BaseCommand):
    help = 'Fix company users and ensure they are active'

    def handle(self, *args, **options):
        # Get all companies
        companies = Company.objects.all()
        self.stdout.write(f'Found {companies.count()} companies')
        
        for company in companies:
            self.stdout.write(f'Processing company: {company.name} (ID: {company.id})')
            
            # Check if company has a user
            if company.user:
                user = company.user
                self.stdout.write(f'  User exists: {user.email} (active: {user.is_active})')
                
                # Ensure the user is active
                if not user.is_active:
                    user.is_active = True
                    user.save()
                    self.stdout.write(self.style.SUCCESS(f'  Activated user: {user.email}'))
                
                # Reset password for testing
                test_password = f'Company{company.id}@123'
                user.set_password(test_password)
                user.save()
                self.stdout.write(self.style.SUCCESS(f'  Reset password for {user.email} to "{test_password}"'))
            else:
                self.stdout.write(self.style.WARNING(f'  No user associated with company: {company.name}'))
                
                # Create a user for this company
                if company.email:
                    # Check if a user with this email already exists
                    existing_user = User.objects.filter(email=company.email).first()
                    if existing_user:
                        self.stdout.write(self.style.WARNING(f'  User with email {company.email} already exists'))
                        
                        # Link the existing user to this company
                        company.user = existing_user
                        company.save()
                        self.stdout.write(self.style.SUCCESS(f'  Linked existing user {existing_user.email} to company {company.name}'))
                    else:
                        # Create a new user
                        test_password = f'Company{company.id}@123'
                        new_user = User.objects.create_user(
                            email=company.email,
                            password=test_password,
                            first_name=company.name,
                            role='company'
                        )
                        company.user = new_user
                        company.save()
                        self.stdout.write(self.style.SUCCESS(f'  Created new user {new_user.email} with password "{test_password}"'))
                else:
                    self.stdout.write(self.style.ERROR(f'  Company {company.name} has no email, cannot create user'))
        
        # List all company users
        self.stdout.write('\nCompany users:')
        for user in User.objects.filter(role='company'):
            company = Company.objects.filter(user=user).first()
            company_name = company.name if company else 'No company'
            self.stdout.write(f'- {user.email} (active: {user.is_active}, company: {company_name})')
