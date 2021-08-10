from typing import List

# Import for typehinting
from analytics.domain.models import View
from blog.domain.models import Category, Comment, Post

# Import for queries
from analytics.domain.repository import ViewRepositoryInteface
from blog.domain.models import CommentRepositoryInterface, PostRepositoryInterface


class BlogService:
	"""
	Important Implementation Notes:

	I would have prefered to follow CQRS - Domain is for writing, reads at
	infra layer - per https://www.cosmicpython.com/book/chapter_12_cqrs.html

	Summerized in these lines: "Domain Models Are for Writing . . . as your
	domain model becomes richer and more complex, a simplified read model
	become[s] ever more compelling."

	This would make future caching (infra layer) much easier for reads as
	the blog's traffic grows, and it would also make new read endpoint
	construction simpler/faster as new front end pages are built.

	That would suggest this pattern:

	# Infra layer - views.py reads directly from DB with
	# optimized queries and possible caching
	list_posts(...)
	list_popular_posts(...)
	get_post_by_pk(...)

	# Service layer (here) called into infra layer
	create_post(...) --> Post
	create_comment(...) --> Comment

	Per instructions, I was not supposed to write any infrastructure
	layer, and I wanted to show that I handled the requirements. Further
	I chose to keep service level functions returning consistent objects
	(dict for individual object, list of dicts for lists). That consistency
	would not be necessary if we split via CQRS as described in the book.
	"""
	def __init__(self,
		comment_repository: CommentRepositoryInterface,
		post_repository: PostRepositoryInterface,
		view_repository: ViewRepositoryInteface
	)
	"""
	Notes: I imported comment, post and view repositories because
	there are definitely writing to those tables.

	As mentioned above, I'd probably move reads to infrastructure
	layer for ease of future caching, but even if I didn't, it
	would probably make sense to define quieries at the RepositoryInterface
	level to get nested objects so we can avoid multiple queries and
	instead rely on joins to improve query performance.
	"""
	# Define as private class variables and use public interface
	# to access them.
	self._comment_repository = comment_repository
	self._post_repository = post_repository
	self._view_repository = view_repository

	def list_posts(self) -> List[dict]:
		"""
		Returns a list of all published posts in the format:

		[
			{
				"pk": <primary key of post>
				"title": <post tilte>,
				"author": <author first and last name>,
				"published_at": <published at date>,
				"category": <category name>
			},
			...
		]
		"""
		raise NotImplementedError

	def list_popular_posts(self) -> List[dict]:
		"""
		Returns a list of 10 published posts in the format:

		[
			{
				"pk": <primary key of post>
				"title": <post tilte>,
				"author": <author first and last name>,
				"published_at": <published at date>,
				"category": <category name>
				"views": <view count>
			},
			...
		]
		This list is sorted, decending by <view count>.
		"""

	def get_post_by_pk(self, post_pk: int) -> dict:
		"""
		Returns a blog object based on it's primary key.

		Also should check views and add a new view entry if
		the author is not the viewer and viewed_at is
		more than 5 minutes ago.

		Parameters
		----------
		post_pk: int
			The primary key of the post to be retreived

		returns
			{
				"pk": <
				"title": <post tilte>,
				"author": <author first and last name>,
				"published_at": <published at date>,
				"category": <category name>,
				"status": <post status>,
				"body": <post body>
				"comments": [
					{
						"pk": <comment pk>,
						"post_pk": <post pk>,
						"user_name": <user first + last name>,
						"body": <comment body>
					}
					...
				],
				"views": <number of views>,
				"created_at": <created at datetime>,
				"updated_at": <updated at datetime>
			},
		"""
		raise NotImplementedError

	def create_comment(self, post_pk: int, user_id: int, body: str) -> dict:
		"""
		Create a comment

		Parameters
		----------
		post_pk: int
			The primary key of the post to be commented on
		user_id: int
			The id of the user creating the comment
		body: str
			The body of the comment

		returns
		{
			"pk": <comment pk>,
			"post_pk": <post pk>,
			"user_name": <user first + last name>,
			"body": <comment body>
		}
		"""
		raise NotImplementedError

