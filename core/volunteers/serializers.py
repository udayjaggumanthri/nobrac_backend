from rest_framework import serializers
from .models import Volunteer
from django.contrib.auth import get_user_model

User = get_user_model()


class VolunteerSerializer(serializers.ModelSerializer):
    """Serializer for the Volunteer model."""
    
    user_email = serializers.SerializerMethodField()
    status = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Volunteer
        fields = [
            'id', 'name', 'email', 'phone', 'address', 'location', 
            'skills', 'availability', 'join_date', 'is_active', 'user_email', 'status'
        ]
        read_only_fields = ['id', 'join_date', 'user_email', 'status']
    
    def get_user_email(self, obj):
        """Get the email of the associated user."""
        if obj.user:
            return obj.user.email
        return None


class VolunteerCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new volunteer."""
    
    status = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = Volunteer
        fields = [
            'name', 'email', 'phone', 'address', 'location', 
            'skills', 'availability', 'status', 'password'
        ]
    
    def create(self, validated_data):
        """Create a new volunteer and associated user account."""
        status = validated_data.pop('status', 'Active')
        password = validated_data.pop('password')
        email = validated_data.get('email')
        name = validated_data.get('name')

        # Create user first
        if not User.objects.filter(email=email).exists():
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=name.split()[0] if ' ' in name else name,
                last_name=' '.join(name.split()[1:]) if ' ' in name else '',
                role='volunteer',  # Explicitly set role to volunteer
                is_active=True
            )
        else:
            user = User.objects.get(email=email)
            # Update existing user's role if needed
            if user.role != 'volunteer':
                user.role = 'volunteer'
                user.save(update_fields=['role'])

        # Create the volunteer
        volunteer = Volunteer.objects.create(
            user=user,
            status=status,
            **validated_data
        )

        # Store the password for API response
        volunteer._generated_password = password

        return volunteer
