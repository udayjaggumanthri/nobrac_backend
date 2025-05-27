from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils.text import slugify
import random
import string

User = get_user_model()

def generate_random_password(length=10):
    """Generate a random password of specified length"""
    # Use a mix of letters, digits, and a few special characters for better usability
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    # Ensure at least one of each type of character for stronger passwords
    password = ''.join(random.choice(characters) for i in range(length-3))
    password += random.choice(string.ascii_uppercase)  # At least one uppercase
    password += random.choice(string.digits)           # At least one digit
    password += random.choice("!@#$%^&*")              # At least one special char

    # Shuffle the password to make it more random
    password_list = list(password)
    random.shuffle(password_list)
    return ''.join(password_list)

class Company(models.Model):
    """Model representing a company in the system."""

    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    industry = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)

    # Registration and status fields
    join_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    # Link to User model
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='company_profile'
    )

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Override save method to create a user if one doesn't exist"""
        creating = self.pk is None  # Check if this is a new company
        super().save(*args, **kwargs)

        if creating and not self.user:
            # This will trigger the post_save signal
            self.create_user()

    def create_user(self):
        """Create a user account for this company

        This method creates a new user account with the company's email and a secure
        random password. The user is assigned the 'company' role and linked to this company.
        The generated password is stored temporarily in memory for the admin to see.
        """
        if not self.email:
            print(f"Cannot create user for company {self.name}: No email provided")
            return None

        # Check if a user with this email already exists
        if User.objects.filter(email=self.email).exists():
            print(f"Cannot create user for company {self.name}: User with email {self.email} already exists")
            return None

        # Generate a secure random password
        password = generate_random_password()

        try:
            # Create the user with company role
            user = User.objects.create_user(
                email=self.email,
                password=password,
                first_name=self.name,
                last_name='',  # Can be updated later
                role='company',
                is_active=True  # Ensure the user is active
            )

            # Link the user to this company
            self.user = user

            # Store the generated password temporarily for the admin to see
            # This will not be saved to the database
            self._generated_password = password

            # Save the company with the user link
            self.save(update_fields=['user'])

            # Log the user creation
            print(f"SECURITY: Created user account for company: {self.name}")
            print(f"SECURITY: User email: {self.email}")
            print(f"SECURITY: Generated secure password (not stored in database)")

            return user

        except Exception as e:
            print(f"ERROR: Failed to create user for company {self.name}: {str(e)}")
            return None

    def delete_user(self):
        """Delete the user account associated with this company

        This method permanently deletes the user account linked to this company.
        It first unlinks the user from the company to avoid recursion issues,
        then deletes the user account. If an error occurs, it attempts to restore
        the relationship.

        Returns:
            bool: True if the user was successfully deleted, False otherwise
        """
        if not self.user:
            print(f"SECURITY: No user account associated with company: {self.name}")
            return False

        try:
            # Store the user instance and its ID for logging
            user = self.user
            user_id = user.id
            user_email = user.email

            # Log the deletion attempt
            print(f"SECURITY: Attempting to delete user account (ID: {user_id}, Email: {user_email}) "
                  f"for company: {self.name} (ID: {self.id})")

            # Temporarily set the user to None to avoid recursion
            self.user = None
            self.save(update_fields=['user'])

            # Delete the user
            user.delete()

            # Log the successful deletion
            print(f"SECURITY: Successfully deleted user account (ID: {user_id}, Email: {user_email}) "
                  f"for company: {self.name} (ID: {self.id})")

            return True

        except Exception as e:
            print(f"ERROR: Failed to delete user account for company {self.name}: {str(e)}")

            # If there was an error, try to restore the relationship
            if 'user' in locals() and 'user_id' in locals() and User.objects.filter(id=user_id).exists():
                print(f"SECURITY: Restoring user relationship after failed deletion attempt")
                self.user = user
                self.save(update_fields=['user'])

            # Re-raise the exception for the caller to handle
            raise e


@receiver(post_save, sender=Company)
def create_company_user(sender, instance, created, **kwargs):
    """Signal to create a user when a company is created"""
    if created and not instance.user:
        instance.create_user()
