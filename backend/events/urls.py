from django.urls import path

from users.views import ChangePasswordView, ProfileView, StudentListView, UpdateProfileView
from .views import (
    # AdminAllEventsView,
    ApproveEventView,
    CreateEventView,

    EventDetailView,
    EventListView,
  
    StudentDashboardView,
    EventRegisterView,
    EventRecommendationView,
    AdminPendingEventsView,
    AdminDashboardStats,
    EventViewTrack,
    OrganizerEventHistoryView,
)

urlpatterns = [
    # Create Event
    path("events/", EventListView.as_view()),

    path("events/<int:pk>/", EventDetailView.as_view()),

    path("events/create/", CreateEventView.as_view()),

    path("events/<int:event_id>/approve/", ApproveEventView.as_view()),
    # Student
    path("student/events/", StudentDashboardView.as_view()),
    path("student/events/<int:event_id>/register/", EventRegisterView.as_view()),
    path("student/events/<int:event_id>/view/", EventViewTrack.as_view()),
    path("student/recommendations/", EventRecommendationView.as_view()), 
    path("students/", StudentListView.as_view()),
    path("profile/", ProfileView.as_view()),
    path("profile/update/", UpdateProfileView.as_view()),
    path("change-password/", ChangePasswordView.as_view()),

   
    # Organizer
    path("organizer/events/history/", OrganizerEventHistoryView.as_view()),

    # Admin
    path("admin/events/<int:event_id>/approve/", ApproveEventView.as_view()),
    path("admin/events/pending/", AdminPendingEventsView.as_view()),
    path("admin/dashboard/", AdminDashboardStats.as_view()),
    # path("admin/events/all/", AdminAllEventsView.as_view()),
]