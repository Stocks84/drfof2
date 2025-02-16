from django.urls import path
from .views import (
    GameListCreateView,
    GameDetailView,
    LikeGameView,
    UnlikeGameView,
    CommentGameView,
    ViewComments,
    DeleteCommentView
)

urlpatterns = [
    path('games/', GameListCreateView.as_view(), name='game-list'),
    path('games/<int:pk>/', GameDetailView.as_view(), name='game-detail'),
    path('games/<int:pk>/like/', LikeGameView.as_view(), name='game-like'),
    path('games/<int:pk>/unlike/', UnlikeGameView.as_view(), name='game-unlike'),
    path('games/<int:pk>/comment/', CommentGameView.as_view(), name='game-comment'),
    path('games/<int:pk>/comments/', ViewComments.as_view(), name='view-comments'),
    path('games/comments/<int:pk>/', DeleteCommentView.as_view(), name='delete-comment'),
]
