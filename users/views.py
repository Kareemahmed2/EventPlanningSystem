from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    User = get_user_model()
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')

    if not username or not password or not email:
        return Response({'error': 'Please provide username and password and email'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)


    user = User.objects.create_user(username=username, password=password, email=email)
    user.save()
    token, _ = Token.objects.get_or_create(user=user)

    return Response({'message': 'User created successfully' , 'token': token.key}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user is not None:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'message': 'Login successful' , 'token': token.key}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)