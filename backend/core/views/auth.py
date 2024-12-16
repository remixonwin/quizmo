from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token  # Add this import
from backend.core.api.serializers.auth import RegisterSerializer, UserSerializer
from rest_framework.authtoken.views import ObtainAuthToken

User = get_user_model()

def index(request):
    """Basic index view"""
    return render(request, 'index.html')

class RegisterView(APIView):
    permission_classes = []
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ValidateTokenView(APIView):
    def post(self, request):
        token = request.data.get('token')
        if not token:
            return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            token_obj = Token.objects.get(key=token)
            return Response({'valid': True, 'user': UserSerializer(token_obj.user).data}, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response({'valid': False}, status=status.HTTP_404_NOT_FOUND)

class PasswordResetView(APIView):
    permission_classes = []
    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            # Add password reset logic here
            return Response({'message': 'Reset email sent'})
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

class ResetPasswordView(APIView):
    permission_classes = []
    def post(self, request):
        # Add password reset confirmation logic here
        return Response({'message': 'Password reset'})

class CustomAuthToken(ObtainAuthToken):
    """Custom token-based authentication view"""

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})