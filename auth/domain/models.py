from shared.domain.models import BaseDomainModel, DomainField


class User(BaseDomainModel):

	pk = DomainField(dtype=int)
	username = DomainField(dtype=str, required=True)
	password = DomainField(dtype=str, required=True)
	email = DomainField(dtype=str)
	first_name = DomainField(dtype=str, required=True)
	last_name = DomainField(dtype=str, required=True)
	is_active = DomainField(dtype=bool)
	is_moderator = DomainField(dtype=bool)
	is_author = DomainField(dtype=bool)

	def __init__(self, *args, **kwargs):
		"""
		Enforce creation constraints.
		"""
		super().__init__(self, *args, **kwargs)
		# Check non empty string constraints explicitly.
		for field in ['username', 'password', 'email']:
			if not getattr(self, field):
				raise ValueError("Field %s cannot be empty string" % field)

	def __str__(self):
		return "<User: %s>" % self.username