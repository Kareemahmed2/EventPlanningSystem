from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_events),
    path('<int:id>', views.event_detail),
    path('create/', views.create_event),
    path('<int:id>/delete/', views.delete_event),
    path('<int:id>/details/', views.update_event),
    path('<int:id>/attendance/', views.update_attendees),
    path('<int:id>/invitees/', views.add_invitees),
    path('<int:id>/invitees/<str:email>', views.remove_invitee),
    path('invited/', views.invited_events),
    path('search/', views.search_events),



]