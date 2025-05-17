from rest_framework import generics, permissions, pagination, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from .models import Game, Like, Comment
from .serializers import GameSerializer, LikeSerializer, CommentSerializer


class GamePagination(pagination.PageNumberPagination):
    page_size = 10  # Default page size
    page_size_query_param = 'page_size'
    max_page_size = 50


class GameListCreateView(generics.ListCreateAPIView):
    serializer_class = GameSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = GamePagination

    def get_queryset(self):
        queryset = Game.objects.all().order_by('-created_at')
        user_games = self.request.query_params.get('user_games')

        if user_games == 'true' and self.request.user.is_authenticated:
            queryset = queryset.filter(creator=self.request.user)

        return queryset

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class GameDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = GameSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Game.objects.all()

    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.creator != self.request.user:
            return Response({"error": "You are not allowed to edit this game."}, status=status.HTTP_403_FORBIDDEN)
        serializer.save()

    def perform_destroy(self, instance):
        if instance.creator != self.request.user:
            return Response({"error": "You are not allowed to delete this game."}, status=status.HTTP_403_FORBIDDEN)
        instance.delete()


# --- Like and Unlike Views (Separate) ---
class LikeGameView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        game = get_object_or_404(Game, pk=kwargs['pk'])
        user = request.user
        
        # Check if the like already exists
        like, created = Like.objects.get_or_create(user=user, game=game)
        
        if created:
            return Response({"detail": "Liked game"}, status=status.HTTP_200_OK)
        
        # If like already exists, just return 200 without error
        return Response({"detail": "Already liked this game"}, status=status.HTTP_200_OK)

class UnlikeGameView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        game = get_object_or_404(Game, pk=kwargs['pk'])
        user = request.user
        
        # Attempt to delete the like
        like = Like.objects.filter(user=user, game=game).first()
        if like:
            like.delete()
            return Response({"detail": "Unliked game"}, status=status.HTTP_200_OK)
        
        # If like does not exist, just return 200 without error
        return Response({"detail": "Already not liked this game"}, status=status.HTTP_200_OK)


# --- Comment Management ---
class CommentGameView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        game = get_object_or_404(Game, pk=self.kwargs['pk'])
        serializer.save(user=self.request.user, game=game)


class ViewComments(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Comment.objects.filter(game_id=self.kwargs['pk'])


class DeleteCommentView(generics.DestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, id=kwargs['pk'])
        if comment.user != request.user:
            return Response({"detail": "You are not allowed to delete this comment."}, status=status.HTTP_403_FORBIDDEN)
        comment.delete()
        return Response({"detail": "Comment deleted"}, status=status.HTTP_204_NO_CONTENT)


class EditCommentView(generics.UpdateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, id=kwargs['pk'])
        if comment.user != request.user:
            return Response({"detail": "You do not have permission to edit this comment."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(comment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

