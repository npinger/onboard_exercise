import datetime

from auth.domain.models import User
from shared.domain.models import BaseDomainModel, DomainField


class Category(BaseDomainModel):
	pk = DomainField(dtype=int)
	name = DomainField(dtype=str, required=True)


class Post(BaseDomainModel):

	STATUS = [
		('d', 'Draft'),
		('r', 'Review'),
		('p', 'Published'),
		('a', 'Archived'),
	]

	pk = DomainField(dtype=int)
	title = DomainField(dtype=str, required=True)
	author = DomainField(dtype=User, required=True)
	category = DomainField(dtype=Category, nullable=True, default=None)
	status = DomainField(dtype=str, required=True, default='d', choices=STATUS)
	body = DomainField(dtype=str, default='')
	published_at = DomainField(dtype=datetime.datetime, nullable=True, default=None)

	created_at = DomainField(dtype=datetime.datetime, nullable=True, default=None)
	updated_at = DomainField(dtype=datetime.datetime, nullable=True, default=None)

	def __init__(self, *args, **kwargs):
		"""
		Enforce creation constraints, relying upon standard python patterns.
		"""
		super().__init__(self, *args, **kwargs)

		if not self.pk and self.status != 'd':
			raise ValueError("Cannot create a new post that is in a state other than draft.")
		self._validate_user_can_write(updated_by=self.author)
		self._validate_title(title=self.title)

	def __str__(self):
		return "<Post pk=%s, title=%s, author=%s>" % (self.pk, self.title, self.author)

	def update(self, **kwargs):
		if 'updated_by' not in kwargs or not isinstance(kwargs['updated_by'], User):
			raise ValueError("Updates must contain an updated_by argument that passes a User.")
		else:
			updated_by = kwargs.pop('updated_by')

		self.validate_values(**kwargs)

		# Validate per field rules
		for field, new_val in kwargs.items():

			self.validate_choices(field_name=field, value=new_val)

			if field == "title":
				self._validate_title(title=new_val)

			if field == 'status':
				self._validate_status(updated_by=updated_by, status=new_val)

				if new_val == 'p':
					self.published_at = datetime.datetime.now()

			setattr(self, field, new_val)


	#############
	# Validations
	def _validate_user_can_write(self, updated_by: User):
		if not updated_by.is_author and not updated_by.is_moderator:
			raise ValueError("Only an author or a moderator can create or"
				" update a post, received %s." % updated_by)

	def _validate_title(self, title: str):
		if not title:
			raise ValueError("Title cannot be an empty string or null.")

		if self.status not in ['d', 'r'] and title != self.title:
			raise ValueError("Can only update title in a draft or review state.")

	def _validate_status(self, updated_by: User, status: str):
		if status == 'p' and not updated_by.is_moderator:
			raise ValueError("Only a User who is_moderator can publish a post.")

		elif status == 'p' and self.status != 'r':
			raise ValueError("A post can only be published from review status.")


class Comment(BaseDomainModel):

	pk = DomainField(dtype=int)
	post = DomainField(dtype=Post, required=True)
	user = DomainField(dtype=User, required=True)
	body = DomainField(dtype=str, required=True)

	created_at = DomainField(dtype=datetime.datetime)

	def __init__(self, *args, **kwargs):
		self.created_at = datetime.datetime.now()
		super().__init__(self, *args, **kwargs)
