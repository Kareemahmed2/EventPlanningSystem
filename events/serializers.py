from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from .models import Event
from django.contrib.auth import get_user_model


User = get_user_model()



# Define a minimal serializer for the organizer to avoid circular dependency
class MinimalUserSerializer(serializers.ModelSerializer):
    """Minimal serializer to represent the event organizer."""

    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class EventSerializer(serializers.ModelSerializer):
    # Set the organizer field to use the MinimalUserSerializer for read operations (GET)
    # This makes the organizer appear as an object {id: ..., username: ...} instead of just an ID.
    organizer = MinimalUserSerializer(read_only=True)

    # Use a hidden field for the actual user object during creation (POST)
    # When validating data for a POST request, this field will be set to request.user
    # but it will not be expected in the incoming data.
    organizer_object = serializers.HiddenField(
        default=CurrentUserDefault(),
        source='organizer'  # Maps the hidden field to the 'organizer' model field
    )

    class Meta:
        model = Event
        # Include the explicit organizer_object field in the fields list
        fields = '__all__'

        # 'organizer' is now read-only because it uses the MinimalUserSerializer for output
        read_only_fields = ['id', 'created_at']

        # We override the create method to handle the nested list/dict fields if necessary,

    # but the primary goal is to ensure the organizer is correctly set.
    # The default save() method handles setting the 'organizer' from 'organizer_object'
    # because of the 'source' attribute.
    def create(self, validated_data):


        # If your Event model has non-standard fields like lists/dicts that need
        # special handling (like removing a key before save), you would do it here.
        # Assuming standard model fields:
        return Event.objects.create(**validated_data)