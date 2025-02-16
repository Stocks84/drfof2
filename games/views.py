from rest_framework import generics, permissions, pagination
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Game, Like, Comment
from .serializers import GameSerializer, LikeSerializer, CommentSerializer


class GamePagination(pagination.PageNumberPagination):
    page_size = 10  # Default page size
    page_size_query_param = 'page_size'  # Allow clients to override page size
    max_page_size = 50


class GameListCreateView(generics.ListCreateAPIView):
    queryset = Game.objects.all().order_by('-created_at')
    serializer_class = GameSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = GamePagination

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class GameDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.creator != request.user:
            return Response({"error": "You are not allowed to edit this game."}, status=403)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.creator != request.user:
            return Response({"error": "You are not allowed to delete this game."}, status=403)
        return super().destroy(request, *args, **kwargs)


class LikeGameView(generics.CreateAPIView):
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        game = Game.objects.get(pk=kwargs['id'])
        like, created = Like.objects.get_or_create(user=request.user, game=game)
        if not created:
            return Response({"detail": "Already liked"}, status=400)
        return Response({"detail": "Game liked"}, status=201)


class UnlikeGameView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        like = Like.objects.filter(user=request.user, game_id=kwargs['id']).first()
        if like:
            like.delete()
            return Response({"detail": "Like removed"}, status=204)
        return Response({"detail": "Not liked yet"}, status=400)


class CommentGameView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        game = Game.objects.get(pk=self.kwargs['id'])
        serializer.save(user=self.request.user, game=game)


class ViewComments(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Comment.objects.filter(game_id=self.kwargs['id'])


class DeleteCommentView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        comment = Comment.objects.filter(id=kwargs['id'], user=request.user).first()
        if comment:
            comment.delete()
            return Response({"detail": "Comment deleted"}, status=204)
        return Response({"detail": "Not found or unauthorized"}, status=403)
