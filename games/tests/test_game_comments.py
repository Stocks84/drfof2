from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from games.models import Game, Comment
from users.models import CustomUser

class GameCommentTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        cls.game = Game.objects.create(
            title="Beer Pong",
            description="Classic party game",
            creator=cls.user
        )
        cls.comment_url = reverse('game-comment', kwargs={'pk': cls.game.pk})

    def setUp(self):
        self.client.login(username="testuser", password="password123")

    def test_comment_on_game(self):
        response = self.client.post(self.comment_url, {"text": "Great game!"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)

    def test_edit_comment(self):
        comment = Comment.objects.create(user=self.user, game=self.game, text="Initial comment")
        edit_url = reverse('edit-comment', kwargs={'pk': comment.pk})
        response = self.client.patch(edit_url, {"text": "Updated comment"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        comment.refresh_from_db()
        self.assertEqual(comment.text, "Updated comment")
