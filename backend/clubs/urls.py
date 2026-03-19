from django.urls import path

from .views import (
    ClubCreateView,
    ApproveClubView,
    ClubListView,
    ClubDetailView
)

urlpatterns = [

    path("clubs/", ClubListView.as_view()),

    path("clubs/<int:pk>/", ClubDetailView.as_view()),

    path("clubs/create/", ClubCreateView.as_view()),

    path("clubs/<int:club_id>/approve/", ApproveClubView.as_view()),
]