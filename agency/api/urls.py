from django.urls import path

from agency.api.views import SpyCatListCreateView, MissionListCreateView, \
    MissionDetailView, assign_spy_cat_to_mission, TargetUpdateView, SpyCatDetailUpdateView

urlpatterns = [
    path('spy-cats/', SpyCatListCreateView.as_view()),
    path('spy-cats/<int:pk>/', SpyCatDetailUpdateView.as_view()),

    path('missions/', MissionListCreateView.as_view()),
    path('missions/<int:pk>/', MissionDetailView.as_view()),
    path('missions/<int:mission_pk>/assign-cat/<int:cat_pk>/', assign_spy_cat_to_mission),

    path('targets/<int:pk>/', TargetUpdateView.as_view()),
]
