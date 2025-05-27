from rest_framework import viewsets, permissions, status, views
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.shortcuts import get_object_or_404
from companies.models import Company
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    CustomTokenObtainPairSerializer,
    UserLoginSerializer
)
import logging

# Set up logger
logger = logging.getLogger('security')

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom token view that uses our enhanced token serializer."""
    serializer_class = CustomTokenObtainPairSerializer


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing User instances."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action in ['login', 'register']:
            return [permissions.AllowAny()]
        return super().get_permissions()

    @action(detail=False, methods=['post'])
    def login(self, request):
        try:
            # Log the incoming request data
            logger.info(f"Login attempt with data: {request.data}")
            
            serializer = UserLoginSerializer(data=request.data)
            if not serializer.is_valid():
                logger.error(f"Login validation failed: {serializer.errors}")
                return Response({
                    'status': 'error',
                    'message': 'Validation failed',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            username = serializer.validated_data.get('username')
            password = serializer.validated_data.get('password')
            requested_role = serializer.validated_data.get('role')

            # Log authentication attempt
            logger.info(f"Attempting to authenticate user: {username} with role: {requested_role}")

            # Try to find the user by email
            try:
                user = User.objects.get(email=username)
                logger.info(f"User found: {user.email} with role: {user.role}")
            except User.DoesNotExist:
                logger.warning(f"User not found: {username}")
                return Response({
                    'status': 'error',
                    'message': 'Invalid email or password'
                }, status=status.HTTP_401_UNAUTHORIZED)

            # Authenticate user using email
            user = authenticate(username=user.username, password=password)
            
            if not user:
                logger.warning(f"Authentication failed for user: {username}")
                return Response({
                    'status': 'error',
                    'message': 'Invalid email or password'
                }, status=status.HTTP_401_UNAUTHORIZED)

            # Check if user is active
            if not user.is_active:
                logger.warning(f"Login attempt for inactive user: {username}")
                return Response({
                    'status': 'error',
                    'message': 'User account is disabled'
                }, status=status.HTTP_403_FORBIDDEN)

            # Check role if specified
            if requested_role:
                logger.info(f"Checking role: requested={requested_role}, actual={user.role}")
                if user.role != requested_role:
                    logger.warning(f"Role mismatch: requested={requested_role}, actual={user.role}")
                    return Response({
                        'status': 'error',
                        'message': f'Access denied. You do not have the {requested_role} role.'
                    }, status=status.HTTP_403_FORBIDDEN)

            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            # Get the appropriate dashboard URL based on user role
            dashboard_url = user.get_dashboard_url()
            
            # Log successful login
            logger.info(f"Successful login: {user.email} ({user.role})")
            
            return Response({
                'status': 'success',
                'message': 'Login successful',
                'data': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'role': user.role,
                        'is_staff': user.is_staff,
                        'is_superuser': user.is_superuser
                    },
                    'dashboard_url': dashboard_url
                }
            })
        except Exception as e:
            logger.error(f"Unexpected error during login: {str(e)}")
            return Response({
                'status': 'error',
                'message': 'An unexpected error occurred during login'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def me(self, request):
        if request.user.is_authenticated:
            dashboard_url = request.user.get_dashboard_url()
            return Response({
                'status': 'success',
                'data': {
                    'user': UserSerializer(request.user).data,
                    'dashboard_url': dashboard_url
                }
            })
        return Response({
            'status': 'error',
            'message': 'Not authenticated'
        }, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            dashboard_url = user.get_dashboard_url()
            return Response({
                'status': 'success',
                'message': 'User registered successfully',
                'data': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user': UserSerializer(user).data,
                    'dashboard_url': dashboard_url
                }
            }, status=status.HTTP_201_CREATED)
        return Response({
            'status': 'error',
            'message': 'Registration failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def debug_user(self, request):
        """Debug endpoint to check user details"""
        if not request.user.is_superuser:
            return Response({
                'status': 'error',
                'message': 'Only superusers can access this endpoint'
            }, status=status.HTTP_403_FORBIDDEN)

        username = request.query_params.get('username')
        if not username:
            return Response({
                'status': 'error',
                'message': 'Username parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(username=username)
            return Response({
                'status': 'success',
                'data': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                    'is_staff': user.is_staff,
                    'is_superuser': user.is_superuser,
                    'is_active': user.is_active,
                    'last_login': user.last_login
                }
            })
        except User.DoesNotExist:
            return Response({
                'status': 'error',
                'message': f'User {username} does not exist'
            }, status=status.HTTP_404_NOT_FOUND)


class UserLoginView(views.APIView):
    """Custom login view that validates role and returns user data with tokens."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            # Log the incoming request data
            logger.info(f"Login attempt with data: {request.data}")
            
            # Get credentials from request
            email = request.data.get('email')
            password = request.data.get('password')
            requested_role = request.data.get('role')

            if not email or not password:
                return Response(
                    {"detail": "Email and password are required."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Try to find and authenticate the user by email
            try:
                user = User.objects.get(email=email)
                logger.info(f"User found: {user.email} with role: {user.role}")
                
                # Authenticate using email as username
                authenticated_user = authenticate(request, username=email, password=password)
                
                if not authenticated_user:
                    logger.warning(f"Authentication failed for user: {email}")
                    return Response(
                        {"detail": "Invalid credentials."},
                        status=status.HTTP_401_UNAUTHORIZED
                    )

                # Check if user is active
                if not authenticated_user.is_active:
                    logger.warning(f"Login attempt for inactive user: {email}")
                    return Response(
                        {"detail": "User account is disabled."},
                        status=status.HTTP_403_FORBIDDEN
                    )

                # Check role if specified
                if requested_role:
                    logger.info(f"Checking role: requested={requested_role}, actual={authenticated_user.role}")
                    if authenticated_user.role != requested_role:
                        logger.warning(f"Role mismatch: requested={requested_role}, actual={authenticated_user.role}")
                        return Response(
                            {"detail": f"Access denied. You do not have the {requested_role} role."},
                            status=status.HTTP_403_FORBIDDEN
                        )

                # Generate tokens
                refresh = RefreshToken.for_user(authenticated_user)
                
                # Get the appropriate dashboard URL based on user role
                dashboard_url = authenticated_user.get_dashboard_url()
                
                # Log successful login
                logger.info(f"Successful login: {authenticated_user.email} ({authenticated_user.role})")
                
                # Create response data
                response_data = {
                    'status': 'success',
                    'message': 'Login successful',
                    'data': {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh),
                        'user': {
                            'id': authenticated_user.id,
                            'email': authenticated_user.email,
                            'first_name': authenticated_user.first_name,
                            'last_name': authenticated_user.last_name,
                            'role': authenticated_user.role,
                            'is_staff': authenticated_user.is_staff,
                            'is_superuser': authenticated_user.is_superuser
                        },
                        'dashboard_url': dashboard_url
                    }
                }

                # If user is a company, add company information
                if authenticated_user.role == 'company':
                    try:
                        company = Company.objects.get(user=authenticated_user)
                        response_data['data']['user']['company'] = {
                            'id': company.id,
                            'name': company.name,
                            'email': company.email
                        }
                        logger.info(f"Added company data to response: {company.name} (ID: {company.id})")
                    except Company.DoesNotExist:
                        logger.warning(f"No company found for user: {authenticated_user.email}")
                
                logger.info(f"Sending response: {response_data}")
                return Response(response_data)

            except User.DoesNotExist:
                logger.warning(f"User not found: {email}")
                return Response(
                    {"detail": "Invalid credentials."},
                    status=status.HTTP_401_UNAUTHORIZED
                )

        except Exception as e:
            logger.error(f"Unexpected error during login: {str(e)}")
            return Response({
                'status': 'error',
                'message': 'An unexpected error occurred during login'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserRegistrationView(views.APIView):
    """View for user registration."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Only admin users can register new users
        if request.user.role != 'admin' and not request.user.is_superuser:
            return Response(
                {"detail": "Only admin users can register new users."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            logger.info(f"User registered: {user.email} ({user.role}) by {request.user.email}")

            # Generate tokens for the new user
            refresh = RefreshToken.for_user(user)

            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(views.APIView):
    """View for retrieving and updating user profile."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get the current user's profile."""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        """Update the current user's profile."""
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CompanyProfileView(views.APIView):
    """View for retrieving and updating company profile."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get the company profile for the current user."""
        # Ensure the user has the company role
        if request.user.role != 'company':
            return Response(
                {"detail": "Only company users can access company profiles."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            company = Company.objects.get(user=request.user)
            from companies.serializers import CompanySerializer
            serializer = CompanySerializer(company)
            return Response(serializer.data)
        except Company.DoesNotExist:
            return Response(
                {"detail": "No company profile found for this user."},
                status=status.HTTP_404_NOT_FOUND
            )

    def patch(self, request):
        """Update the company profile for the current user."""
        # Ensure the user has the company role
        if request.user.role != 'company':
            return Response(
                {"detail": "Only company users can update company profiles."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            company = Company.objects.get(user=request.user)
            from companies.serializers import CompanySerializer
            serializer = CompanySerializer(company, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Company.DoesNotExist:
            return Response(
                {"detail": "No company profile found for this user."},
                status=status.HTTP_404_NOT_FOUND
            )
