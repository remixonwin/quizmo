
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from ..serializers import UserSerializer, RegisterSerializer

User = get_user_model()

class CustomAuthToken(ObtainAuthToken):
    """Custom token-based authentication view"""
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                         context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })

class RegisterView(APIView):
    """User registration view"""
    
    permission_classes = []
    
    @method_decorator(csrf_exempt)
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ValidateTokenView(APIView):
    """Token validation view"""
    
    def post(self, request):
        token = request.data.get('token')
        if not token:
            return Response({'error': 'Token is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            token_obj = Token.objects.get(key=token)
            return Response({
                'valid': True,
                'user': UserSerializer(token_obj.user).data
            })
        except Token.DoesNotExist:
            return Response({'valid': False}, status=status.HTTP_404_NOT_FOUND)

class PasswordResetView(APIView):
    """Password reset request view"""
    
    permission_classes = []
    
    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            # Add password reset logic here
            return Response({'message': 'Password reset email sent'})
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

class ResetPasswordView(APIView):
    """Password reset confirmation view"""
    
    permission_classes = []
    
    def post(self, request):
        # Add password reset confirmation logic here
        return Response({'message': 'Password reset successful'})