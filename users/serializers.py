from rest_framework import serializers
from django.contrib.auth import get_user_model

# Get the custom User model defined in your models.py
User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the custom User model.

    This is used to serialize User objects into JSON responses,
    typically for displaying user details after successful login or signup.
    It includes read-only fields for security.
    """

    class Meta:
        model = User
        # Define the fields you want to expose in the API responses
        fields = ('id', 'username', 'email', 'date_joined', 'is_staff', 'is_active')

        # Ensure these fields can only be read, not modified via the serializer
        read_only_fields = ('id', 'date_joined', 'is_staff', 'is_active')

# Note: For creating/signing up a user (which you handle in views.py
# via User.objects.create_user), you often don't need a serializer for the POST
# data if you are handling validation manually, as you did with:
# if not username or not password or not email: ...
# If you wanted to use a serializer for creation and automatic validation,
# you would create a separate UserCreateSerializer and define the password field:
#
# class UserCreateSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True)
#
#     class Meta:
#         model = User
#         fields = ('username', 'email', 'password')
#
#     def create(self, validated_data):
#         user = User.objects.create_user(**validated_data)
#         return user