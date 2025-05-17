from django.contrib.admin.sites import AdminSite
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from games.models import Game, Comment, Like


class AdminPanelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = get_user_model().objects.create_superuser(
            username="adminuser",
            email="admin@example.com",
            password="adminpassword123"
        )
        cls.regular_user = get_user_model().objects.create_user(
            username="regularuser",
            email="regular@example.com",
            password="userpassword123"
        )
        cls.game = Game.objects.create(
            title="Beer Pong",
            description="Classic party game",
            rules="Some basic rules",
            creator=cls.regular_user
        )

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.admin_user)  # Ensure we are logged in as admin

    def test_admin_can_create_game(self):
        """Test that the admin can create a game through the admin panel"""
        response = self.client.get(reverse('admin:games_game_add'))
        self.assertEqual(response.status_code, 200)  # Ensure the form loads

        # Submitting form data to create a game
        response = self.client.post(reverse('admin:games_game_add'), {
            "title": "Kings Cup",
            "description": "A fun drinking game",
            "rules": "Shuffle the deck and draw cards",
            "creator": self.regular_user.pk,  # Must be the user ID, not the object
            "_save": "Save",  # This mimics the save button in the admin
        }, follow=True)  # Follow redirects for a proper response

        self.assertEqual(response.status_code, 200)  # Redirects to the game list
        self.assertTrue(Game.objects.filter(title="Kings Cup").exists())

    def test_admin_can_edit_game(self):
        """Test that the admin can edit a game through the admin panel"""
        response = self.client.get(reverse('admin:games_game_change', args=[self.game.pk]))
        self.assertEqual(response.status_code, 200)  # Ensure the form loads

        response = self.client.post(reverse('admin:games_game_change', args=[self.game.pk]), {
            "title": "Updated Beer Pong",
            "description": "Classic party game (updated)",
            "rules": "Updated rules for the game",
            "creator": self.regular_user.pk,  # Must be the user ID
            "_save": "Save",  # Mimics the save button in the admin
        }, follow=True)  # Follow redirects for proper processing

        self.assertEqual(response.status_code, 200)  # Redirects to the game list
        self.game.refresh_from_db()
        self.assertEqual(self.game.title, "Updated Beer Pong")

    def test_admin_can_delete_game(self):
        """Test that the admin can delete a game through the admin panel"""
        response = self.client.post(reverse('admin:games_game_delete', args=[self.game.pk]), {
            "post": "yes"  # Confirm delete
        }, follow=True)  # Follow redirects for a proper response

        self.assertEqual(response.status_code, 200)  # Redirects to game list
        self.assertFalse(Game.objects.filter(id=self.game.id).exists())
