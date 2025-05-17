from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from games.models import Game, Like
from users.models import CustomUser

class GameLikeUnlikeTestCase(APITestCase):
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
        cls.like_url = reverse('game-like', kwargs={'pk': cls.game.pk})
        cls.unlike_url = reverse('game-unlike', kwargs={'pk': cls.game.pk})

    def setUp(self):
        self.client.login(username="testuser", password="password123")

    def test_like_game(self):
        response = self.client.post(self.like_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Like.objects.filter(user=self.user, game=self.game).exists())

    def test_like_game_multiple_times(self):
        self.client.post(self.like_url)
        response = self.client.post(self.like_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unlike_game(self):
        self.client.post(self.like_url)
        response = self.client.delete(self.unlike_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Like.objects.filter(user=self.user, game=self.game).exists())

    def test_unlike_without_liking(self):
        response = self.client.delete(self.unlike_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_like_non_existent_game(self):
        non_existent_like_url = reverse('game-like', kwargs={'pk': 9999})
        response = self.client.post(non_existent_like_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
