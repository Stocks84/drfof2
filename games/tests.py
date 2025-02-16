from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Game, Like, Comment
from users.models import CustomUser


class GameTestCase(APITestCase):
    def setUp(self):
        """Set up users and test data"""
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        self.other_user = CustomUser.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="password123"
        )

        self.login_url = reverse('token_obtain_pair')  # /api/token/
        self.game_list_url = reverse('game-list')      # /api/games/

        # Obtain JWT token for testuser
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'password123'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.access_token = response.data['access']

        # Authenticate all requests
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # Create a test game
        self.game = Game.objects.create(
            title="Beer Pong",
            description="Classic party game",
            creator=self.user
        )
        self.game_detail_url = reverse('game-detail', kwargs={'pk': self.game.pk})  # /api/games/{id}/
        self.like_url = reverse('game-like', kwargs={'pk': self.game.pk})  # /api/games/{id}/like/
        self.comment_url = reverse('game-comment', kwargs={'pk': self.game.pk})  # /api/games/{id}/comment/

    def test_create_game(self):
        """Test that an authenticated user can create a game"""
        data = {
            "title": "Kings Cup",
            "description": "Fun drinking game",
            "rules": "Shuffle the deck and draw cards"
        }
        response = self.client.post(self.game_list_url, data, format="json")

        print(response.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Game.objects.count(), 2)  # Original game + new game

    def test_retrieve_all_games(self):
        """Test retrieving a list of games"""
        response = self.client.get(self.game_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_retrieve_single_game(self):
        """Test retrieving a single game by ID"""
        response = self.client.get(self.game_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Beer Pong")

    def test_update_game(self):
        """Test updating a game (only creator can update)"""
        data = {"title": "Updated Beer Pong"}
        response = self.client.patch(self.game_detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.game.refresh_from_db()
        self.assertEqual(self.game.title, "Updated Beer Pong")

    def test_non_creator_cannot_update_game(self):
        """Test that non-creators cannot update the game"""
        self.client.credentials()  # Reset authentication
        response = self.client.post(self.login_url, {
            "username": "otheruser",
            "password": "password123"
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')

        data = {"title": "Unauthorized Edit"}
        response = self.client.patch(self.game_detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  # Should be forbidden

    def test_delete_game(self):
        """Test that only the creator can delete their game"""
        response = self.client.delete(self.game_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Game.objects.filter(pk=self.game.pk).exists())

    def test_non_creator_cannot_delete_game(self):
        """Test that a non-creator cannot delete the game"""
        self.client.credentials()  # Reset authentication
        response = self.client.post(self.login_url, {
            "username": "otheruser",
            "password": "password123"
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')

        response = self.client.delete(self.game_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  # Should be forbidden

    def test_like_game(self):
        """Test liking a game"""
        response = self.client.post(self.like_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Like.objects.filter(user=self.user, game=self.game).exists())

    def test_unlike_game(self):
        """Test unliking a game"""
        Like.objects.create(user=self.user, game=self.game)  # Like the game first
        response = self.client.post(self.like_url, format="json")  # Unlike

        print("Unlike Response:", response.status_code, response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Like.objects.filter(user=self.user, game=self.game).exists())

    def test_comment_on_game(self):
        """Test commenting on a game"""
        data = {"text": "This game is awesome!", "game": self.game.pk}
        response = self.client.post(self.comment_url, data, format="json")
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.game.comments.count(), 1)
        self.assertEqual(self.game.comments.first().text, "This game is awesome!")
