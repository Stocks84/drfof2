from django.urls import path
from .views import GameListCreateView, GameDetailView

urlpatterns = [
    path('games/', GameListCreateView.as_view(), name='game-list-create'),
    path('games/<int:pk>/', GameDetailView.as_view(), name='game-detail',)
]
