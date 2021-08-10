import copy
import datetime
import unittest

from shared.domain.models import DomainModelConstructionException
from auth.domain.models import User
from blog.domain.models import Category, Comment, Post

class BlogDomainTests(unittest.TestCase):

	def setUp(self):
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
		self.author = User(
			username="user2",
			password="testpass",
			email="user@example.com",
			first_name="First",
			last_name="Last",
			is_active=True,
			is_author=True,
			is_moderator=False
		)
		self.moderator = User(
			username="user3",
			password="testpass",
			email="user@example.com",
			first_name="First",
			last_name="Last",
			is_active=True,
			is_author=False,
			is_moderator=True
		)

		self.category = Category(name="For Fun!")

	def test_post_creation(self):
		success_cases = [
			# By author
			{
				'title': 'Hello World',
				'author': self.author,
				'body': 'This is my cool article.'
			},
			# By moderator
			{
				'title': 'Hello World',
				'author': self.moderator,
				'body': 'This is my cool article.'
			},
			# With a category
			{
				'title': 'Hello World',
				'author': self.moderator,
				'body': 'This is my cool article.',
				'category': self.category
			},
			# Aassuming a read from the database instantiation
			{
				'pk': 1,
				'title': 'Hello World',
				'author': self.moderator,
				'status': 'p',
				'body': 'This is my cool article.',
				'category': self.category
			},
		]

		for case in success_cases:
			Post(**case)

		failure_cases = [
			# Reader can't create post
			({
				'title': 'Hello World',
				'author': self.reader,
				'body': 'This is my cool article.'
			}, ValueError),
			# Title can't be falsey (empty string or None)
			({
				'title': '',
				'author': self.author,
				'body': 'This is my cool article.'
			}, ValueError),
			({
				'title': None,
				'author': self.author,
				'body': 'This is my cool article.'
			}, TypeError),
			# Status can't start as something other than Draft (i.e. no pk and draft state)
			({
				'title': 'Hello World',
				'author': self.author,
				'body': 'This is my cool article.',
				'status': 'p'
			}, ValueError),
		]
		for case, expected_exception in failure_cases:
			with self.assertRaises(expected_exception):
				Post(**case)

	def test_post_update_constraints(self):
		initial_post = Post(title="Hello World", author=self.author, body="This is my article.")

		# Author updates
		success_cases = [
			{'updated_by': self.author, 'title': 'My New title'},
			{'updated_by': self.author, 'status': 'a'},
			{'updated_by': self.author, 'status': 'd'},
			{'updated_by': self.author, 'status': 'r'},
			{'updated_by': self.author, 'body': 'Made some edits.', 'category': self.category},
		]

		for case in success_cases:
			initial_post.update(**case)

		failure_cases = [
			({'updated_by': self.author, 'title': ''}, ValueError),
			({'updated_by': self.author, 'status': 'p'}, ValueError),
			({'updated_by': self.author, 'status': 'non-status'}, DomainModelConstructionException),
		]

		for case, expected_exception in failure_cases:
			with self.assertRaises(expected_exception):
				initial_post.update(**case)

		# Moderator updates (can do everything an author can + publish)
		success_cases = success_cases + [
			# Note success cases end with review status so we can publish
			{'updated_by': self.moderator, 'status': 'p'},
		]

		for case in success_cases:
			initial_post.update(**case)

		# Now we have published so check that published_at has been set
		assert isinstance(initial_post.published_at, datetime.datetime)

		failure_cases = [
			# Can't change title on a published post
			({'updated_by': self.moderator, 'title': ''}, ValueError),
			({'updated_by': self.moderator, 'status': 'non-status'}, DomainModelConstructionException),
		]

		for case, expected_exception in failure_cases:
			with self.assertRaises(expected_exception):
				initial_post.update(**case)

		# Finally show we can't change the title of an archived post
		initial_post.update(updated_by=self.moderator, status='a')
		with self.assertRaises(ValueError):
			initial_post.update(updated_by=self.moderator, title='Cannot update this')


class CommentDomainTests(unittest.TestCase):

	def setUp(self):
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
		self.author = User(
			username="user2",
			password="testpass",
			email="user@example.com",
			first_name="First",
			last_name="Last",
			is_active=True,
			is_author=True,
			is_moderator=False
		)
		self.moderator = User(
			username="user3",
			password="testpass",
			email="user@example.com",
			first_name="First",
			last_name="Last",
			is_active=True,
			is_author=False,
			is_moderator=True
		)

		self.post = Post(
			title='Hello World',
			author=self.author,
			body='This is my cool article.'
		)

	def test_comment_creation(self):
		success_cases = [
			# Any type of user can comment
			{'post': self.post, 'user': self.author, 'body': "My comment!"},
			{'post': self.post, 'user': self.moderator, 'body': "My comment!"},
			{'post': self.post, 'user': self.user, 'body': "My comment!"},
		]

		for case in success_cases:
			Comment(**case)

		failure_cases = [
			# Required fields must be present
			({'post': self.post, 'user': self.author}, DomainModelConstructionException),
			({'post': self.post,'body': "My comment!"}, DomainModelConstructionException),
			({'user': self.user, 'body': "My comment!"}, DomainModelConstructionException),
		]

		for case, expected_exception in failure_cases:
			with self.assertRaises(expected_exception):
				Comment(**case)

		# Test that created_at is set on creation

		comment = Comment(**{'post': self.post, 'user': self.author, 'body': "My comment!"})
		assert isinstance(comment.created_at, datetime.datetime)
