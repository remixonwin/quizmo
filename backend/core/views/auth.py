
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import render
from django.contrib.auth import get_user_model

User = get_user_model()

def index(request):
    """Basic index view"""
    return render(request, 'index.html')

class RegisterView(APIView):
    permission_classes = []
    def post(self, request):
        return Response({}, status=status.HTTP_201_CREATED)

class ValidateTokenView(APIView):
    def post(self, request):
        return Response({'valid': True})

class PasswordResetView(APIView):
    permission_classes = []
    def post(self, request):
        return Response({'message': 'Reset email sent'})

class ResetPasswordView(APIView):
    permission_classes = []
    def post(self, request):
        return Response({'message': 'Password reset'})

class CustomAuthToken(APIView):
    permission_classes = []
    def post(self, request):
        return Response({'token': 'dummy'})