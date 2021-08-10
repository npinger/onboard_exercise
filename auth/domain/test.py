import unittest

from auth.domain.models import User

class AuthDomainTests(unittest.TestCase):

	def test_creation(self):
		# Test user creation
		self.reader = User(
			username="user1",
			password="testpass",
			email="user@example.com",
			first_name="First",
			last_name="Last",
			is_active=True,
			is_author=False,
			is_moderator=False
		)

		# Test failure missing fields
		with self.assertRaises(ValueError):
			self.author = User(
				username="",
				password="testpass",
				email="user@example.com",
				first_name="First",
				last_name="Last",
				is_active=True,
				is_author=True,
				is_moderator=False
			)
		with self.assertRaises(ValueError):
			self.reader = User(
				username="user1",
				password="",
				email="user@example.com",
				first_name="First",
				last_name="Last",
				is_active=True,
				is_author=False,
				is_moderator=True
			)

		with self.assertRaises(ValueError):
			self.reader = User(
				username="user1",
				password="testpass",
				first_name="First",
				last_name="Last",
				email="",
				is_active=True,
				is_author=False,
				is_moderator=True
			)