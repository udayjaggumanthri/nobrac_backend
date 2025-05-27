from rest_framework import serializers
from .models import Company
from django.contrib.auth import get_user_model

User = get_user_model()


class CompanySerializer(serializers.ModelSerializer):
    """Serializer for the Company model."""

    user_email = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = [
            'id', 'name', 'email', 'phone', 'address', 'location',
            'industry', 'description', 'website', 'logo', 'join_date',
            'is_active', 'user_email', 'user_id'
        ]
        read_only_fields = ['id', 'join_date', 'user_email', 'user_id']

    def get_user_email(self, obj):
        """Get the email of the associated user."""
        if obj.user:
            return obj.user.email
        return None

    def get_user_id(self, obj):
        """Get the ID of the associated user."""
        if obj.user:
            return obj.user.id
        return None


class CompanyCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new company with user credentials."""

    username = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = Company
        fields = [
            'name', 'email', 'phone', 'address', 'location',
            'industry', 'description', 'website', 'logo',
            'username', 'password'  # Added username and password fields
        ]

    def validate(self, attrs):
        """Validate the data before creating the company."""
        # Check if username is provided
        username = attrs.get('username')
        if not username:
            raise serializers.ValidationError({"username": "Username is required."})

        # Check if email is provided and is valid
        email = attrs.get('email')
        if not email:
            raise serializers.ValidationError({"email": "Email is required."})

        # Check if password is provided
        password = attrs.get('password')
        if not password:
            raise serializers.ValidationError({"password": "Password is required."})

        # Log validation checks for debugging
        print(f"Validation check - Email: {email}")
        print(f"Existing users with this email: {User.objects.filter(email=email).exists()}")
        print(f"Existing companies with this email: {Company.objects.filter(email=email).exists()}")

        # Check if a user with this email already exists - case insensitive
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError({"email": "A user with this email already exists. Please use a different email address."})

        # Check if a company with this email already exists - case insensitive
        if Company.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError({"email": "A company with this email already exists. Please use a different email address."})

        return attrs

    def create(self, validated_data):
        """Create a new company and its associated user account with provided credentials."""
        # Extract user credentials
        username = validated_data.pop('username')
        password = validated_data.pop('password')

        # Get the company email (will be used as the user's email)
        email = validated_data.get('email')

        # Normalize the email to ensure consistent case handling
        normalized_email = email.lower().strip()

        print(f"Creating company with email: {normalized_email}, username: {username}")

        # Double-check if a user with this email already exists - case insensitive
        # This is a safety check in case a user was created between validation and creation
        if User.objects.filter(email__iexact=normalized_email).exists():
            print(f"User with email {normalized_email} already exists during creation")
            raise serializers.ValidationError({
                "email": "A user with this email already exists. Please use a different email address."
            })

        # Double-check if a company with this email already exists - case insensitive
        if Company.objects.filter(email__iexact=normalized_email).exists():
            print(f"Company with email {normalized_email} already exists during creation")
            raise serializers.ValidationError({
                "email": "A company with this email already exists. Please use a different email address."
            })

        # Create the user first
        try:
            print(f"Creating user with email: {normalized_email}")

            # Create the user with company role
            user = User.objects.create_user(
                email=normalized_email,  # Use normalized company email as the user's email (login identifier)
                password=password,
                first_name=validated_data.get('name', ''),
                last_name='',
                role='company',
                is_active=True
            )

            print(f"User created successfully: {user.email} (ID: {user.id})")

            # Now create the company and link it to the user
            try:
                print(f"Creating company with data: {validated_data}")

                # Create the company and link it to the user
                company = Company.objects.create(
                    **validated_data,
                    user=user  # Link the user directly during creation
                )

                print(f"Company created successfully: {company.name} (ID: {company.id})")

                # Store credentials for the response
                company._credentials = {
                    'username': username,  # Store the username for display
                    'login_email': normalized_email,  # Email is used for login
                    'password': password
                }

                return company
            except Exception as company_error:
                # If company creation fails, delete the user we just created
                print(f"Error creating company: {str(company_error)}")
                if user.id:  # Make sure user has an ID before trying to delete
                    print(f"Deleting user {user.email} (ID: {user.id}) due to company creation failure")
                    user.delete()
                raise serializers.ValidationError({
                    "error": f"Failed to create company: {str(company_error)}"
                })

        except serializers.ValidationError:
            # Re-raise validation errors
            raise
        except Exception as user_error:
            # Handle user creation errors
            print(f"Error creating user: {str(user_error)}")
            raise serializers.ValidationError({
                "error": f"Failed to create user account: {str(user_error)}"
            })
