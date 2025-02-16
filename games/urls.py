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
    path('games/<int:id>/like/', LikeGameView.as_view(), name='like-game'),
    path('games/<int:id>/unlike/', UnlikeGameView.as_view(), name='unlike-game'),
    path('games/<int:id>/comment/', CommentGameView.as_view(), name='comment-game'),
    path('games/<int:id>/comments/', ViewComments.as_view(), name='view-comments'),
    path('games/comments/<int:id>/', DeleteCommentView.as_view(), name='delete-comment'),
]
