import logging
from django.contrib.auth import authenticate
from rest_framework import status, permissions
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import UserSerializer
from .utils import send_verification_email

# logger = logging.getLogger(__name__)

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # logger.debug("Received registration request.")
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                send_verification_email(user)
                # logger.info(f"User registered successfully: {user.email}")
                return Response({"detail": "User registered successfully. Please check your email for the OTP."},
                                status=status.HTTP_201_CREATED)
            except IntegrityError:
                # logger.warning("User with this email already exists.")
                return Response({"detail": "User with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)
            except ValidationError as e:
                # logger.warning(f"Validation error: {str(e)}")
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                # logger.error(f"Unexpected error: {str(e)}")
                return Response({"detail": "An unexpected error occurred."},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # logger.debug(f"Serializer errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        otp = request.data.get('otp')
        # logger.debug(f"Received OTP verification request for email: {email}")
        try:
            user = User.objects.get(email=email)
            if user.check_otp(otp):
                user.is_verified = True
                user.otp = None
                user.otp_expiration = None
                user.save()
                # logger.info(f"Email verified successfully for user: {email}")
                return Response({"detail": "Email verified successfully."}, status=status.HTTP_200_OK)
            # logger.warning("Invalid or expired OTP.")
            return Response({"detail": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            # logger.warning(f"User does not exist: {email}")
            return Response({"detail": "User does not exist."}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        email_or_username = request.data.get('email_or_username')
        password = request.data.get('password')

        # logger.debug(f"Received login request for user: {email_or_username}")

        if not email_or_username or not password:
            # logger.warning("Email/Username and password are required.")
            return Response({"detail": "Email/Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = authenticate(request, username=email_or_username, password=password)
            if user is not None and user.is_verified:
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                # logger.info(f"User logged in successfully: {email_or_username}")
                return Response({
                    "user_id": user.user_id,
                    "username": user.username,
                    "access_token": access_token,
                }, status=status.HTTP_200_OK)
            else:
                # logger.warning("Invalid credentials or unverified account.")
                return Response({"detail": "Invalid credentials or unverified account."},
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # logger.error(f"Unexpected error during login: {str(e)}")
            return Response({"detail": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # logger.debug(f"User logged out: {request.user.username}")
        request.auth.delete()
        return Response({"detail": "Logged out successfully."}, status=status.HTTP_200_OK)
