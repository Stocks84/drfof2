from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Game, Like, Comment
from users.models import CustomUser


# Game managemnt tests
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
        self.game_detail_url = reverse('game-detail', kwargs={'pk': self.game.pk})
        self.like_url = reverse('game-like', kwargs={'pk': self.game.pk})
        self.comment_url = reverse('game-comment', kwargs={'pk': self.game.pk})

    # --- Game Creation Tests ---
    def test_create_game(self):
        """Test that an authenticated user can create a game"""
        data = {
            "title": "Kings Cup",
            "description": "Fun drinking game",
            "rules": "Shuffle the deck and draw cards"
        }
        response = self.client.post(self.game_list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Game.objects.count(), 2)  # Original game + new game

    def test_create_game_unauthenticated(self):
        """Test that an unauthenticated user cannot create a game"""
        self.client.credentials()  # Remove authentication
        data = {
            "title": "Unauthorized Game",
            "description": "Should not be created"
        }
        response = self.client.post(self.game_list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- Game Retrieval Tests ---
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

    def test_retrieve_non_existent_game(self):
        """Test retrieving a non-existent game (should return 404)"""
        response = self.client.get(reverse('game-detail', kwargs={'pk': 999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # --- Game Update and Deletion Tests ---
    def test_update_game(self):
        """Test updating a game (only creator can update)"""
        data = {"title": "Updated Beer Pong"}
        response = self.client.patch(self.game_detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.game.refresh_from_db()
        self.assertEqual(self.game.title, "Updated Beer Pong")

    def test_delete_game(self):
        """Test that only the creator can delete their game"""
        response = self.client.delete(self.game_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Game.objects.filter(pk=self.game.pk).exists())

    def test_delete_non_existent_game(self):
        """Test deleting a non-existent game (should return 404)"""
        response = self.client.delete(reverse('game-detail', kwargs={'pk': 999}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # --- Like/Unlike Tests ---
    def test_like_game(self):
        """Test liking a game"""
        response = self.client.post(self.like_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Like.objects.filter(user=self.user, game=self.game).exists())

    def test_like_game_unauthenticated(self):
        """Test liking a game as an unauthenticated user (should fail)"""
        self.client.credentials()  # Remove authentication
        response = self.client.post(self.like_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- Comment Tests ---
    def test_comment_on_game(self):
        """Test commenting on a game"""
        data = {"text": "This game is awesome!"}
        response = self.client.post(self.comment_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.game.comments.count(), 1)

    def test_comment_without_text(self):
        """Test commenting on a game without text (should fail)"""
        data = {"text": ""}
        response = self.client.post(self.comment_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


#   like/Unlike tests

class GameLikeUnlikeTestCase(APITestCase):
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
        self.like_url = reverse('game-like', kwargs={'pk': self.game.pk})  # /api/games/{id}/like/

    def test_like_game(self):
        """Test liking a game"""
        response = self.client.post(self.like_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Like.objects.filter(user=self.user, game=self.game).exists())

    def test_unlike_game(self):
        """Test unliking a game (toggle)"""
        # First like the game
        Like.objects.create(user=self.user, game=self.game)
        response = self.client.post(self.like_url, format="json")  # Unlike
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Like.objects.filter(user=self.user, game=self.game).exists())

    def test_like_game_multiple_times(self):
        """Test that a user cannot like the same game multiple times"""
        # First like the game
        Like.objects.create(user=self.user, game=self.game)
        response = self.client.post(self.like_url, format="json")  # Attempt to like again (toggle)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Like.objects.filter(user=self.user, game=self.game).exists())

    def test_like_game_unauthenticated(self):
        """Test liking a game as an unauthenticated user (should fail)"""
        self.client.credentials()  # Remove authentication
        response = self.client.post(self.like_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unlike_game_unauthenticated(self):
        """Test unliking a game as an unauthenticated user (should fail)"""
        self.client.credentials()  # Remove authentication
        response = self.client.post(self.like_url, format="json")  # Toggle (like/unlike)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_like_non_existent_game(self):
        """Test liking a non-existent game (should return 404)"""
        non_existent_like_url = reverse('game-like', kwargs={'pk': 9999})  # Non-existent game ID
        response = self.client.post(non_existent_like_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unlike_without_liking(self):
        """Test unliking a game without liking it first (no error)"""
        response = self.client.post(self.like_url, format="json")  # First like
        response = self.client.post(self.like_url, format="json")  # Unlike
        response = self.client.post(self.like_url, format="json")  # Attempt unlike again (no like exists)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Like.objects.filter(user=self.user, game=self.game).exists())
        