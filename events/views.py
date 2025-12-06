from django.db.models import Q
from datetime import datetime
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from . import models
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
    serializer = EventSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()  # organizer will now be set automatically
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


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
        return Response({'error': 'Event not found'}, status=404)


    if request.user != event.organizer:
        return Response({'error': 'Not allowed'}, status=403)


    if event.invitees is None:
        event.invitees = []

    if isinstance(event.invitees, dict):
        if email in event.invitees:
            del event.invitees[email]
        else:
            return Response({'error': 'Email not found'}, status=404)

    # If invitees is a list
    elif isinstance(event.invitees, list):
        if email in event.invitees:
            event.invitees.remove(email)
        else:
            return Response({'error': 'Email not found'}, status=404)

    else:
        return Response({'error': 'Invalid invitees format'}, status=500)

    event.save()
    return Response({'message': 'Invitee removed'}, status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def invited_events(request):
    user_email = request.user.email

    events = Event.objects.all()

    invited = []

    for event in events:

        if user_email in (event.invitees or []):
            invited.append(event)
            continue


        if isinstance(event.attendees, dict) and user_email in event.attendees:
            invited.append(event)
            continue

    serializer = EventSerializer(invited, many=True)
    return Response(serializer.data, status=200)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_events(request):
    try:
        keyword = request.GET.get('keyword', '').strip()
        date_str = request.GET.get('date', '').strip()
        role_filter = request.GET.get('role', '').strip().lower()

        user = request.user
        user_email = user.email

        events = Event.objects.all()

        #Keyword filter
        if keyword:
            events = events.filter(
                Q(title__icontains=keyword) |
                Q(description__icontains=keyword)
            )

        #Date filter
        if date_str:
            try:
                parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                events = events.filter(date=parsed_date)
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

        #Role filter
        if role_filter == "organizer":
            events = events.filter(organizer=user)
        elif role_filter == "attendee":
            # Use string-based contains instead of list for Djongo
            events = events.filter(
                Q(invitees__icontains=user_email) |
                Q(attendees__has_key=user_email)
            )

        safe_events = []
        for e in events:
            safe_events.append({
                "id": e.id,
                "title": e.title,
                "description": e.description,
                "date": e.date,
                "location": e.location,
                "organizer": e.organizer_id,
                "invitees": e.invitees,
                "attendees": e.attendees,
                "created_at": e.created_at,
                "role": (
                    "organizer" if e.organizer == user else
                    "attendee" if user_email in (e.invitees or []) or user_email in (e.attendees or {}) else
                    "none"
                )
            })

        return Response(safe_events, status=200)

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return Response({"error": str(e)}, status=500)
