from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from django.utils.safestring import mark_safe
from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """Admin configuration for the Company model."""

    # Add a custom deletion confirmation message
    def get_deleted_objects(self, objs, request):
        """Override to add a custom message about user deletion."""
        deleted_objects, model_count, perms_needed, protected = super().get_deleted_objects(objs, request)

        # Add a warning about user deletion
        for obj in objs:
            if obj.user:
                deleted_objects.append(f"⚠️ User account for {obj.name} ({obj.user.email}) will also be permanently deleted!")

        return deleted_objects, model_count, perms_needed, protected

    list_display = ('name', 'email', 'phone', 'location', 'industry', 'join_date', 'is_active', 'user_status')
    list_filter = ('is_active', 'industry', 'join_date')
    search_fields = ('name', 'email', 'phone', 'location')
    readonly_fields = ('join_date', 'user_link')
    fieldsets = (
        (None, {
            'fields': ('name', 'email', 'phone')
        }),
        ('Company Details', {
            'fields': ('address', 'location', 'industry', 'description', 'website', 'logo')
        }),
        ('Status', {
            'fields': ('is_active', 'join_date')
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

        When a new company is created, this method automatically creates a user account
        for the company and displays the generated credentials to the admin.
        """
        # First save the company object
        super().save_model(request, obj, form, change)

        # If this is a new company (not an update) and no user exists, create one
        if not change and not obj.user:
            # Create the user account
            user = obj.create_user()

            if user and hasattr(obj, '_generated_password'):
                # Get the generated password
                password = obj._generated_password

                # Create a styled credential box with the login information
                credential_box = mark_safe(
                    f"""
                    <div style="background-color: #f8f9fa; border: 1px solid #ddd; padding: 15px;
                               border-radius: 5px; margin: 10px 0; max-width: 500px;">
                        <h3 style="color: #28a745; margin-top: 0;">Company User Account Created</h3>
                        <p>A user account has been created for <strong>{obj.name}</strong> with the following credentials:</p>
                        <div style="background-color: #fff; border: 1px solid #ccc; padding: 10px; border-radius: 3px;">
                            <p><strong>Email:</strong> {obj.email}</p>
                            <p><strong>Password:</strong> <code style="background-color: #f1f1f1; padding: 2px 5px;">{password}</code></p>
                        </div>
                        <p style="color: #dc3545; margin-top: 15px; font-weight: bold;">
                            ⚠️ IMPORTANT: Please save these credentials and share them with the company.
                            This password will not be shown again.
                        </p>
                    </div>
                    """
                )

                # Show the credential box to the admin
                messages.success(request, credential_box)

                # Log the credential generation (without the actual password)
                print(f"SECURITY: Credentials generated for company: {obj.name} (ID: {obj.id})")
            else:
                # Show a warning if user creation failed
                messages.warning(
                    request,
                    f"Company '{obj.name}' was created, but no user account could be created. "
                    f"This may be because a user with email '{obj.email}' already exists."
                )

                # Log the failure
                print(f"WARNING: Failed to create user account for company: {obj.name} (ID: {obj.id})")

    def delete_model(self, request, obj):
        """Override delete_model to handle user deletion.

        When a company is deleted, this method ensures that the associated user account
        is also deleted. It provides feedback to the admin about the deletion process.
        """
        company_name = obj.name
        company_id = obj.id
        user_email = obj.user.email if obj.user else None

        try:
            # Log the deletion attempt
            print(f"SECURITY: Admin initiated deletion of company: {company_name} (ID: {company_id})")

            # Delete the associated user first
            if obj.user:
                print(f"SECURITY: Deleting associated user: {user_email}")
                obj.delete_user()

                # Notify the admin about the user deletion
                messages.info(
                    request,
                    f"The user account ({user_email}) associated with {company_name} has been permanently deleted."
                )
            else:
                print(f"SECURITY: No user account associated with company: {company_name}")

            # Then delete the company
            super().delete_model(request, obj)

            # Log the successful deletion
            print(f"SECURITY: Company {company_name} (ID: {company_id}) successfully deleted")

            # Notify the admin about the successful deletion
            messages.success(
                request,
                f"Company '{company_name}' has been permanently deleted from the system."
            )

        except Exception as e:
            # Log the error
            print(f"ERROR: Failed to delete company {company_name} (ID: {company_id}): {str(e)}")

            # Notify the admin about the error
            messages.error(
                request,
                f"An error occurred while deleting company '{company_name}': {str(e)}"
            )

            # Re-raise the exception for Django to handle
            raise e

    def delete_queryset(self, request, queryset):
        """Override delete_queryset to handle bulk deletions.

        When multiple companies are deleted at once, this method ensures that all
        associated user accounts are also deleted. It provides feedback to the admin
        about the bulk deletion process.
        """
        company_count = queryset.count()
        deleted_users = []

        try:
            # Log the bulk deletion attempt
            print(f"SECURITY: Admin initiated bulk deletion of {company_count} companies")

            # Delete the associated users first
            for obj in queryset:
                if obj.user:
                    user_email = obj.user.email
                    print(f"SECURITY: Deleting associated user for company: {obj.name} (Email: {user_email})")
                    obj.delete_user()
                    deleted_users.append(user_email)
                else:
                    print(f"SECURITY: No user account for company: {obj.name}")

            # Then delete the companies
            super().delete_queryset(request, queryset)

            # Log the successful deletion
            print(f"SECURITY: Successfully deleted {company_count} companies and {len(deleted_users)} user accounts")

            # Notify the admin about the successful deletion
            if deleted_users:
                user_list = ", ".join(deleted_users[:5])
                if len(deleted_users) > 5:
                    user_list += f" and {len(deleted_users) - 5} more"

                messages.success(
                    request,
                    f"Successfully deleted {company_count} companies and {len(deleted_users)} user accounts ({user_list})."
                )
            else:
                messages.success(
                    request,
                    f"Successfully deleted {company_count} companies. No user accounts were associated with these companies."
                )

        except Exception as e:
            # Log the error
            print(f"ERROR: Failed to delete companies in bulk: {str(e)}")

            # Notify the admin about the error
            messages.error(
                request,
                f"An error occurred while deleting companies: {str(e)}"
            )

            # Re-raise the exception for Django to handle
            raise e
