from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from .models import User
from .serializers import UserSerializer
from .utils import send_verification_email


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = []  # No authentication required for registration

    def perform_create(self, serializer):
        user = serializer.save(is_verified=False)
        send_verification_email(user)


class VerifyEmailView(APIView):
    permission_classes = []  # No authentication required for email verification

    def get(self, request, uid, token):
        try:
            user = User.objects.get(pk=uid)
            if user and user.check_verification_token(token):
                user.is_verified = True
                user.save()
                return Response({"detail": "Email verified successfully."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "Invalid token or user does not exist."}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = []  # No authentication required for login

    def post(self, request, *args, **kwargs):
        email_or_username = request.data.get('email_or_username')
        password = request.data.get('password')
        user = authenticate(request, username=email_or_username, password=password)
        if user is not None and user.is_verified:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "user_id": user.user_id,
                "username": user.username
            }, status=status.HTTP_200_OK)
        return Response({"detail": "Invalid credentials or unverified account."}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        request.auth.delete()
        return Response({"detail": "Logged out successfully."}, status=status.HTTP_200_OK)
