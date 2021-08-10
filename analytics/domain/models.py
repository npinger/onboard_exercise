import datetime

from shared.domain.models import BaseDomainModel, DomainField
from auth.domain.models import User
from blog.domain.models import Post


class View(BaseDomainModel):

	pk = DomainField(dtype=int)
	post = DomainField(dtype=Post, required=True)
	user = DomainField(dtype=User, required=True)
	viewed_at = DomainField(dtype=datetime.datetime)

	def __init__(self, *args, **kwargs):
		super().__init__(self, *args, **kwargs)
		self.viewed_at = datetime.datetime.now()
