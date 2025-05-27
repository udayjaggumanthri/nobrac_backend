from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from django.db import transaction
from .models import Volunteer
from .serializers import VolunteerSerializer, VolunteerCreateSerializer
import logging

# Set up logger for security events
logger = logging.getLogger('security')


class VolunteerViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing Volunteer instances."""

    queryset = Volunteer.objects.all()
    serializer_class = VolunteerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return VolunteerCreateSerializer
        return VolunteerSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        Custom admins can manage volunteers.
        """
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]  # Allow any authenticated user to manage volunteers
        return [permissions.IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        """Override create method to return the full volunteer details after creation.

        This method handles the creation of a new volunteer and automatically creates
        a user account for the volunteer. It includes enhanced logging and error handling.
        """
        try:
            # Log the creation attempt with client info for security auditing
            client_ip = self.get_client_ip(request)
            user_info = f"User: {request.user}" if request.user.is_authenticated else "Unauthenticated user"
            logger.info(f"Volunteer creation initiated - {user_info} from IP: {client_ip}")

            # Validate the request data
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                logger.warning(f"Invalid volunteer data submitted: {serializer.errors}")
                return Response(
                    {"detail": "Invalid data", "errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Use a transaction to ensure data consistency
            with transaction.atomic():
                # Create the volunteer
                self.perform_create(serializer)

                # Get the created volunteer instance
                volunteer = serializer.instance

                # Log the successful creation
                logger.info(f"Volunteer created successfully: {volunteer.name} (ID: {volunteer.id})")

                # Prepare credentials if available
                credentials = None
                if hasattr(volunteer, '_generated_password') and volunteer.user:
                    credentials = {
                        'email': volunteer.user.email,
                        'password': volunteer._generated_password
                    }

                # Return the full volunteer details using the regular serializer, plus credentials if present
                response_serializer = VolunteerSerializer(volunteer)
                response_data = response_serializer.data
                if credentials:
                    response_data['user_credentials'] = credentials
                return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Log the error
            logger.error(f"Error creating volunteer: {str(e)}")

            # Return a user-friendly error response
            return Response(
                {"detail": "An error occurred while creating the volunteer. Please try again."},
                status=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request, *args, **kwargs):
        """Override destroy method to handle user deletion.

        When a volunteer is deleted, this method also deletes the associated user account.
        """
        volunteer = self.get_object()
        
        # Log the deletion attempt
        client_ip = self.get_client_ip(request)
        logger.info(f"Volunteer deletion initiated - User: {request.user}, Volunteer: {volunteer.name} (ID: {volunteer.id}) from IP: {client_ip}")
        
        # Store user info before deletion for logging
        user_info = None
        if volunteer.user:
            user_info = f"{volunteer.user.email} (ID: {volunteer.user.id})"
            
            # Delete the associated user
            try:
                volunteer.user.delete()
                logger.info(f"User account deleted - {user_info}")
            except Exception as e:
                logger.error(f"Error deleting user account for volunteer {volunteer.name}: {str(e)}")
        
        # Delete the volunteer
        response = super().destroy(request, *args, **kwargs)
        
        # Log the successful deletion
        logger.info(f"Volunteer deleted successfully: {volunteer.name} (ID: {volunteer.id})")
        
        return response
    
    def update(self, request, *args, **kwargs):
        """Override update to allow status and password update from admin dashboard."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Handle password update if provided
        password = request.data.get('password')
        if password and instance.user:
            instance.user.set_password(password)
            instance.user.save()
        # Handle status update if provided
        status_val = request.data.get('status')
        if status_val:
            instance.status = status_val
            instance.save(update_fields=['status'])

        return Response(serializer.data)

    def get_client_ip(self, request):
        """Get the client IP address from the request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
