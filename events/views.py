from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Event
from .serializers import EventSerializer


# GET /api/events

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_events(request):
    events = Event.objects.filter(organizer=request.user)
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)


# GET /api/events/:id

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def event_detail(request, id):
    try:
        event = Event.objects.get(id=id)
    except Event.DoesNotExist:
        return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
    return Response(EventSerializer(event).data)


#POST   /api/events

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_event(request):
    data = request.data
    serializer = EventSerializer(data=data)

    if serializer.is_valid():
        serializer.save(organizer=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#DELETE /api/events/:id
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_event(request, id):
    try:
        event = Event.objects.get(id=id)
    except Event.DoesNotExist:
        return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)

    #ONLY ORG CAN DELETE
    if event.organizer != request.user:
        return Response({'error': 'Not Authorized'}, status=status.HTTP_403_FORBIDDEN)

    event.delete()
    return Response({'message': 'Event deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


#PATCH api/events/:id/attendance
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_attendees(request, id):
    try:
        event = Event.objects.get(id=id)
    except Event.DoesNotExist:
        return Response({'error': 'Event not found'}, status=404)


    email = request.data.get('email')
    status = request.data.get('status')   #GOING/MAYBE/NOTGOING
    attendees = event.attendees
    attendees[email] = status
    event.attendees = attendees
    event.save()

    return Response({'message': 'updated'}, status=200)


#PATCH EDIT Event

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_event(request, id):
    try:
        event = Event.objects.get(id=id)
    except Event.DoesNotExist:
        return Response({'error': 'Event not found'}, status=404)

    updatable_fields = ['title', 'description', 'date', 'location', 'invitees']
    for field in updatable_fields:
        if field in request.data:
            setattr(event, field, request.data[field])


    email = request.data.get('email')
    status = request.data.get('status')   #GOING/MAYBE/NOTGOING

    if email and status:
        attendees = event.attendees
        attendees[email] = status
        event.attendees = attendees
    event.save()

    return Response({'message': 'updated'}, status=200)


#POST  /api/events/:id/invitees
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_invitees(request, id):
    try:
        event = Event.objects.get(id=id)
    except Event.DoesNotExist:
        return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
    email = request.data.get('email')
    if email not in event.invitees:
        event.invitees.append(email)
        event.save()
    return Response({'message': 'Invitee added'}, status=status.HTTP_200_OK)


#DELETE /api/events/:id/invitees/:email
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_invitee(request, id, email):
    try:
        event = Event.objects.get(id=id)
    except Event.DoesNotExist:
        return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)

    if email in event.invitees:
        event.invitees.remove(email)
        event.save()

    return Response({'message': 'Invitee removed'}, status=status.HTTP_200_OK)

