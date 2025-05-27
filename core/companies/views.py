from rest_framework import viewsets, permissions, status, serializers
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from django.db import transaction
from .models import Company
from .serializers import CompanySerializer, CompanyCreateSerializer
from api.permissions import IsAdminRole, IsCompanyRole
import logging

# Set up logger for security events
logger = logging.getLogger('security')


class CompanyViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing Company instances."""

    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        print(f"CompanyViewSet.get_serializer_class called for action: {self.action}")
        if self.action == 'create':
            print("Returning CompanyCreateSerializer")
            return CompanyCreateSerializer
        print("Returning CompanySerializer")
        return CompanySerializer

    def list(self, request, *args, **kwargs):
        """Override list method to return all companies.

        This method adds additional logging to help debug issues with the company list.
        """
        print(f"CompanyViewSet.list called by user: {request.user}")

        # Get all companies
        queryset = self.filter_queryset(self.get_queryset())
        print(f"Found {queryset.count()} companies in the database")

        # Log each company for debugging
        for company in queryset:
            print(f"Company: {company.name}, ID: {company.id}, Email: {company.email}")

        # Serialize the data
        serializer = self.get_serializer(queryset, many=True)
        print(f"Serialized {len(serializer.data)} companies")

        # Return the response with a wrapper to match frontend expectations
        return Response({
            'companies': serializer.data,
            'count': len(serializer.data)
        })

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        Only admin role users can create companies, and authenticated users can view them.
        """
        print(f"CompanyViewSet.get_permissions called for action: {self.action}")
        print(f"User: {self.request.user}, authenticated: {self.request.user.is_authenticated}")

        if hasattr(self.request.user, 'role'):
            print(f"User role: {self.request.user.role}")

        if self.action == 'list' or self.action == 'retrieve':
            print("Returning IsAuthenticated permission for list/retrieve")
            return [permissions.IsAuthenticated()]
        elif self.action == 'create' or self.action == 'update' or self.action == 'partial_update' or self.action == 'destroy':
            # Only admin role users can create, update, or delete companies
            print("Returning IsAdminRole permission for create/update/partial_update/destroy")
            return [IsAdminRole()]
        elif self.action == 'my_company':
            # Company users can access their own company profile
            print("Returning IsCompanyRole permission for my_company")
            return [IsCompanyRole()]

        print("Returning default permissions")
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        """Override create method to create a company with user credentials.

        This method handles the creation of a new company and automatically creates
        a user account for the company using the provided credentials. It includes
        enhanced logging and error handling.
        """
        # The IsAdminRole permission class already ensures the user has the admin role
        # Log the admin user for audit purposes
        logger.info(f"Admin user creating company - User: {request.user.email} (ID: {request.user.id})")

        # Log the creation attempt with client info for security auditing
        client_ip = self.get_client_ip(request)
        user_info = f"Admin: {request.user.email}"
        logger.info(f"Company creation initiated - {user_info} from IP: {client_ip}")
        logger.info(f"Request data: {request.data}")

        # Validate the request data
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Invalid company data submitted: {serializer.errors}")

            # Format the error response for better readability
            error_messages = {}
            for field, errors in serializer.errors.items():
                if isinstance(errors, list):
                    error_messages[field] = errors[0]
                else:
                    error_messages[field] = str(errors)

            return Response(
                error_messages,
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Create the company with user account
            company = serializer.save()

            # Get the username and password from the request data
            username = request.data.get('username')
            password = request.data.get('password')

            # Get the company email
            company_email = company.email

            # Log the successful creation
            logger.info(f"Company created successfully: {company.name} (ID: {company.id})")
            logger.info(f"User account created for company with email: {company_email}")
            logger.info(f"Username: {username}")

            # Return the company details along with the user credentials
            response_serializer = CompanySerializer(company)
            response_data = response_serializer.data

            # Add user credentials to the response
            response_data.update({
                'user_credentials': {
                    'username': username,  # Regular username for display
                    'login_email': company_email,  # Email is used for login
                    'password': password,
                    'role': 'company'
                },
                'message': 'Company created successfully with user account. Please securely share these credentials with the company.',
                'id': company.id  # Include the company ID in the response
            })

            logger.info(f"Returning response: {response_data}")
            return Response(response_data, status=status.HTTP_201_CREATED)

        except serializers.ValidationError as e:
            # Log the validation error
            logger.error(f"Validation error creating company: {str(e)}")

            # Format the error response
            if hasattr(e, 'detail') and isinstance(e.detail, dict):
                error_response = e.detail
            else:
                error_response = {"detail": str(e)}

            return Response(
                error_response,
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            # Log the error
            logger.error(f"Error creating company: {str(e)}")
            logger.exception(e)  # Log the full traceback

            # Return a user-friendly error response
            return Response(
                {"detail": f"An error occurred while creating the company: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

    def get_client_ip(self, request):
        """Get the client IP address from the request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def destroy(self, request, pk=None, **kwargs):
        """Override destroy method to handle user deletion.

        This method ensures that when a company is deleted, its associated user account
        is also deleted. It includes enhanced logging, error handling, and security checks.
        The IsAdminRole permission class already ensures the user has the admin role.

        Args:
            request: The HTTP request
            pk: The primary key of the company to delete
            **kwargs: Additional keyword arguments
        """
        try:
            # Get the company instance
            instance = self.get_object()

            # Store company info for logging
            company_id = instance.id
            company_name = instance.name

            # Log the deletion attempt with client info for security auditing
            client_ip = self.get_client_ip(request)
            user_info = f"User: {request.user}" if request.user.is_authenticated else "Unauthenticated user"
            logger.info(f"Company deletion initiated - {user_info} from IP: {client_ip} - "
                       f"Company: {company_name} (ID: {company_id})")

            # Use a transaction to ensure data consistency
            with transaction.atomic():
                # Delete the associated user first
                if instance.user:
                    user_email = instance.user.email
                    user_id = instance.user.id

                    logger.info(f"Deleting associated user account - Email: {user_email}, ID: {user_id}")

                    try:
                        instance.delete_user()
                        logger.info(f"Successfully deleted user account - Email: {user_email}, ID: {user_id}")
                    except Exception as user_error:
                        logger.error(f"Error deleting user account - Email: {user_email}: {str(user_error)}")
                        # Continue with company deletion even if user deletion fails
                else:
                    logger.info(f"No user account associated with company: {company_name} (ID: {company_id})")

                # Then perform the standard deletion
                self.perform_destroy(instance)

                # Log the successful deletion
                logger.info(f"Company successfully deleted - Name: {company_name}, ID: {company_id}")

                # Return a success response
                return Response(
                    {"detail": "Company and its associated user account have been permanently deleted."},
                    status=status.HTTP_204_NO_CONTENT
                )

        except Exception as e:
            # Log the error
            logger.error(f"Error deleting company: {str(e)}")

            # Return a user-friendly error response
            return Response(
                {"detail": "An error occurred while deleting the company. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def my_company(self, request):
        """Get the company associated with the current user.

        This endpoint allows company users to retrieve their own company profile.
        It includes security checks to ensure only authenticated company users
        can access their own company data.
        """
        user = request.user

        # Log the access attempt
        client_ip = self.get_client_ip(request)
        logger.info(f"Company profile access attempt - User: {user} from IP: {client_ip}")

        # Check if the user is authenticated
        if not user.is_authenticated:
            logger.warning(f"Unauthenticated company profile access attempt from IP: {client_ip}")
            return Response(
                {"detail": "Authentication required to access company profile"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Check if the user has the company role
        if user.role != 'company':
            logger.warning(f"Non-company user attempted to access company profile - User: {user.email}, Role: {user.role}")
            return Response(
                {"detail": "Access denied. Only company users can access this endpoint."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            # Get the company associated with the user
            company = Company.objects.get(user=user)

            # Log the successful access
            logger.info(f"Company profile accessed - Company: {company.name} (ID: {company.id}), User: {user.email}")

            # Return the company data
            serializer = self.get_serializer(company)
            return Response(serializer.data)

        except Company.DoesNotExist:
            # Log the error
            logger.error(f"Company not found for user - User: {user.email} (ID: {user.id})")

            # Return a user-friendly error response
            return Response(
                {"detail": "No company profile found for your account. Please contact an administrator."},
                status=status.HTTP_404_NOT_FOUND
            )
