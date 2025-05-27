from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from django.utils.safestring import mark_safe
from django import forms
from .models import Volunteer


class VolunteerAdminForm(forms.ModelForm):
    """Custom form for Volunteer admin with password field."""
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput,
        required=False,
        help_text='Required for new volunteers. Leave empty for existing volunteers.'
    )

    class Meta:
        model = Volunteer
        fields = '__all__'


@admin.register(Volunteer)
class VolunteerAdmin(admin.ModelAdmin):
    """Admin configuration for the Volunteer model."""
    form = VolunteerAdminForm

    # Add a custom deletion confirmation message
    def get_deleted_objects(self, objs, request):
        """Override to add a custom message about user deletion."""
        deleted_objects, model_count, perms_needed, protected = super().get_deleted_objects(objs, request)

        # Add a warning about user deletion
        for obj in objs:
            if obj.user:
                deleted_objects.append(f"⚠️ User account for {obj.name} ({obj.user.email}) will also be permanently deleted!")

        return deleted_objects, model_count, perms_needed, protected

    list_display = ('name', 'email', 'phone', 'location', 'join_date', 'is_active', 'user_status')
    list_filter = ('is_active', 'join_date', 'status')
    search_fields = ('name', 'email', 'phone', 'location')
    readonly_fields = ('join_date', 'user_link')
    fieldsets = (
        (None, {
            'fields': ('name', 'email', 'phone', 'password')
        }),
        ('Volunteer Details', {
            'fields': ('address', 'location', 'skills', 'availability')
        }),
        ('Status', {
            'fields': ('is_active', 'status', 'join_date')
        }),
        ('User Account', {
            'fields': ('user_link',),
            'classes': ('collapse',),
        }),
    )

    def user_status(self, obj):
        """Display user account status with color indicator."""
        if obj.user:
            return format_html(
                '<span style="color: green;">✓ Account Created</span>'
            )
        return format_html(
            '<span style="color: red;">✗ No Account</span>'
        )
    user_status.short_description = 'User Account'

    def user_link(self, obj):
        """Display a link to the user in the admin."""
        if obj.user:
            url = f"/admin/users/user/{obj.user.id}/change/"
            return format_html(
                '<a href="{}" target="_blank">View User: {}</a>',
                url, obj.user.email
            )
        return "No user account created yet."
    user_link.short_description = 'User Account'

    def save_model(self, request, obj, form, change):
        """Override save_model to handle user creation and credential display.

        When a new volunteer is created, this method automatically creates a user account
        for the volunteer using the admin-provided password.
        """
        # Get the password from the form
        password = form.cleaned_data.get('password')

        # If this is a new volunteer (not an update) and no user exists
        if not change and not obj.user:
            if not password:
                messages.error(
                    request,
                    "Password is required when creating a new volunteer."
                )
                return

            # Store the password temporarily for user creation
            obj._admin_password = password

        # First save the volunteer object
        super().save_model(request, obj, form, change)

        # If this is a new volunteer (not an update) and no user exists, create one
        if not change and not obj.user:
            # Create the user account
            user = obj.create_user()

            if user:
                # Create a styled credential box with the login information
                credential_box = mark_safe(
                    f"""
                    <div style="background-color: #f8f9fa; border: 1px solid #ddd; padding: 15px;
                               border-radius: 5px; margin: 10px 0; max-width: 500px;">
                        <h3 style="color: #28a745; margin-top: 0;">Volunteer User Account Created</h3>
                        <p>A user account has been created for <strong>{obj.name}</strong> with the following credentials:</p>
                        <div style="background-color: #fff; border: 1px solid #ccc; padding: 10px; border-radius: 3px;">
                            <p><strong>Email:</strong> {obj.email}</p>
                            <p><strong>Password:</strong> <code style="background-color: #f1f1f1; padding: 2px 5px;">{password}</code></p>
                        </div>
                        <p style="color: #dc3545; margin-top: 15px; font-weight: bold;">
                            ⚠️ IMPORTANT: Please save these credentials and share them with the volunteer.
                            This password will not be shown again.
                        </p>
                    </div>
                    """
                )

                # Show the credential box to the admin
                messages.success(request, credential_box)

                # Log the credential generation (without the actual password)
                print(f"SECURITY: User account created for volunteer: {obj.name} (ID: {obj.id})")
            else:
                # Show a warning if user creation failed
                messages.warning(
                    request,
                    f"Volunteer '{obj.name}' was created, but no user account could be created. "
                    f"This may be because a user with email '{obj.email}' already exists."
                )

                # Log the failure
                print(f"WARNING: Failed to create user account for volunteer: {obj.name} (ID: {obj.id})")

    def delete_model(self, request, obj):
        """Override delete_model to handle user deletion.

        When a volunteer is deleted, this method ensures that the associated user account
        is also deleted. It provides feedback to the admin about the deletion process.
        """
        volunteer_name = obj.name
        volunteer_id = obj.id
        user_email = obj.user.email if obj.user else None

        try:
            # Log the deletion attempt
            print(f"SECURITY: Admin initiated deletion of volunteer: {volunteer_name} (ID: {volunteer_id})")

            # Delete the associated user first
            if obj.user:
                print(f"SECURITY: Deleting associated user: {user_email}")
                obj.delete_user()

                # Notify the admin about the user deletion
                messages.info(
                    request,
                    f"The user account ({user_email}) associated with {volunteer_name} has been permanently deleted."
                )
            else:
                print(f"SECURITY: No user account associated with volunteer: {volunteer_name}")

            # Then delete the volunteer
            super().delete_model(request, obj)

            # Log the successful deletion
            print(f"SECURITY: Volunteer {volunteer_name} (ID: {volunteer_id}) successfully deleted")

            # Notify the admin about the successful deletion
            messages.success(
                request,
                f"Volunteer '{volunteer_name}' has been permanently deleted from the system."
            )

        except Exception as e:
            # Log the error
            print(f"ERROR: Failed to delete volunteer {volunteer_name} (ID: {volunteer_id}): {str(e)}")

            # Notify the admin about the error
            messages.error(
                request,
                f"An error occurred while deleting volunteer '{volunteer_name}': {str(e)}"
            )

            # Re-raise the exception for Django to handle
            raise e

    def delete_queryset(self, request, queryset):
        """Override delete_queryset to handle bulk deletions.

        When multiple volunteers are deleted at once, this method ensures that all
        associated user accounts are also deleted. It provides feedback to the admin
        about the bulk deletion process.
        """
        volunteer_count = queryset.count()
        deleted_users = []

        try:
            # Log the bulk deletion attempt
            print(f"SECURITY: Admin initiated bulk deletion of {volunteer_count} volunteers")

            # Delete the associated users first
            for obj in queryset:
                if obj.user:
                    user_email = obj.user.email
                    print(f"SECURITY: Deleting associated user for volunteer: {obj.name} (Email: {user_email})")
                    obj.delete_user()
                    deleted_users.append(user_email)
                else:
                    print(f"SECURITY: No user account for volunteer: {obj.name}")

            # Then delete the volunteers
            super().delete_queryset(request, queryset)

            # Log the successful deletion
            print(f"SECURITY: Successfully deleted {volunteer_count} volunteers and {len(deleted_users)} user accounts")

            # Notify the admin about the successful deletion
            if deleted_users:
                user_list = ", ".join(deleted_users[:5])
                if len(deleted_users) > 5:
                    user_list += f" and {len(deleted_users) - 5} more"

                messages.success(
                    request,
                    f"Successfully deleted {volunteer_count} volunteers and {len(deleted_users)} user accounts ({user_list})."
                )
            else:
                messages.success(
                    request,
                    f"Successfully deleted {volunteer_count} volunteers. No user accounts were associated with these volunteers."
                )

        except Exception as e:
            # Log the error
            print(f"ERROR: Failed to delete volunteers in bulk: {str(e)}")

            # Notify the admin about the error
            messages.error(
                request,
                f"An error occurred while deleting volunteers: {str(e)}"
            )

            # Re-raise the exception for Django to handle
            raise e
