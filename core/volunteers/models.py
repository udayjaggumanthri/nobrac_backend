from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Volunteer(models.Model):
    """Model representing a volunteer in the system."""

    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    
    # Additional volunteer fields
    skills = models.CharField(max_length=255, blank=True, null=True)
    availability = models.CharField(max_length=255, blank=True, null=True)
    
    # Registration and status fields
    join_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=20, default='Active', choices=[
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Pending', 'Pending'),
    ])

    # Link to User model
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='volunteer_profile'
    )

    class Meta:
        verbose_name = 'Volunteer'
        verbose_name_plural = 'Volunteers'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Override save method to create a user if one doesn't exist"""
        creating = self.pk is None  # Check if this is a new volunteer
        super().save(*args, **kwargs)

        if creating and not self.user:
            # This will trigger the post_save signal
            self.create_user()

    def create_user(self):
        """Create a user account for this volunteer

        This method creates a new user account with the volunteer's email and the
        password provided by the admin. The user is assigned the 'volunteer' role
        and linked to this volunteer.
        """
        if not self.email:
            print(f"Cannot create user for volunteer {self.name}: No email provided")
            return None

        # Check if a user with this email already exists
        if User.objects.filter(email=self.email).exists():
            print(f"Cannot create user for volunteer {self.name}: User with email {self.email} already exists")
            return None

        try:
            # Create the user with volunteer role
            user = User.objects.create_user(
                email=self.email,
                password=self._admin_password,  # Use the admin-provided password
                first_name=self.name,
                last_name='',  # Can be updated later
                role='volunteer',  # Explicitly set the role to volunteer
                is_active=True  # Ensure the user is active
            )

            # Double-check that the role was set correctly
            if user.role != 'volunteer':
                user.role = 'volunteer'
                user.save(update_fields=['role'])

            # Link the user to this volunteer
            self.user = user

            # Save the volunteer with the user link
            self.save(update_fields=['user'])

            # Log the user creation
            print(f"SECURITY: Created user account for volunteer: {self.name}")
            print(f"SECURITY: User email: {self.email}")
            print(f"SECURITY: User role: {user.role}")

            return user

        except Exception as e:
            print(f"ERROR: Failed to create user for volunteer {self.name}: {str(e)}")
            return None

    def delete_user(self):
        """Delete the user account associated with this volunteer

        This method permanently deletes the user account linked to this volunteer.
        It first unlinks the user from the volunteer to avoid recursion issues,
        then deletes the user account. If an error occurs, it attempts to restore
        the relationship.

        Returns:
            bool: True if the user was successfully deleted, False otherwise
        """
        if not self.user:
            print(f"SECURITY: No user account associated with volunteer: {self.name}")
            return False

        try:
            # Store the user instance and its ID for logging
            user = self.user
            user_id = user.id
            user_email = user.email

            # Log the deletion attempt
            print(f"SECURITY: Attempting to delete user account (ID: {user_id}, Email: {user_email}) "
                  f"for volunteer: {self.name} (ID: {self.id})")

            # Temporarily set the user to None to avoid recursion
            self.user = None
            self.save(update_fields=['user'])

            # Delete the user
            user.delete()

            # Log the successful deletion
            print(f"SECURITY: Successfully deleted user account (ID: {user_id}, Email: {user_email}) "
                  f"for volunteer: {self.name} (ID: {self.id})")

            return True

        except Exception as e:
            print(f"ERROR: Failed to delete user account for volunteer {self.name}: {str(e)}")

            # If there was an error, try to restore the relationship
            if 'user' in locals() and 'user_id' in locals() and User.objects.filter(id=user_id).exists():
                print(f"SECURITY: Restoring user relationship after failed deletion attempt")
                self.user = user
                self.save(update_fields=['user'])

            # Re-raise the exception for the caller to handle
            raise e

    def set_status(self, status):
        """Set the status of the volunteer."""
        self.status = status
        self.save(update_fields=['status'])

    def set_password(self, password):
        """Set a new password for the volunteer's user account."""
        if self.user:
            self.user.set_password(password)
            self.user.save()
