from abc import ABC
from dataclasses import dataclass
from typing import List, Tuple


class DomainModelConstructionException(Exception):
	pass


class DomainField:
	"""
	Defines attributes on a domain field

	Parameters
	----------
	dtype: type
		The data type of the field to be passed
	required: bool, default to False
		Whether the field is required or not
	choices: List[Tuple], default to empty list
		If no value is provided, then we do not check against choices.
		If a list of choices is provided
	"""
	def __init__(self, dtype: type, required: bool = False,
		choices: List[Tuple] = [], nullable: bool = False, default=None):
		self.dtype = dtype
		self.required = required
		self.choices = choices
		self.default = default
		self.nullable = nullable



class BaseDomainModel(ABC):

	# {field: (datatype, required), ...} mapping should be
	# be defined for all domain models
	fields = {}

	def __init__(self, *args, **kwargs):
		"""
		Note: Default behavior of init take all arguments
		and load into attributes, checking type and enforcing
		required nature of field.
		"""

		# Get domain field names
		domain_field_names = [field_name for field_name in dir(self)
			if not field_name == '_domain_field_names' and
			isinstance(getattr(self, field_name), DomainField)]

		# domain_field_names to private variables for later access
		for field_name in domain_field_names:
			setattr(self, "_" + field_name, getattr(self, field_name))
			setattr(self, field_name, None)

		# Set defaults
		for field_name in domain_field_names:
			default = getattr(self, "_" + field_name).default
			if default:
				setattr(self, field_name, default)

		# Enforce type constraints, choices and set values
		for k, v in kwargs.items():
			if k not in domain_field_names:
				raise DomainModelConstructionException((
					"Illegal field %s passed to object %s,"
					" legal fields are %s") % (k,
					self.__class__.__name__, ",".join(domain_field_names)))

			domain_field = getattr(self, "_" + k)
			is_nullable = domain_field.nullable
			dtype = domain_field.dtype
			if (not is_nullable and v is None) \
					and not isinstance(v, dtype):
				raise TypeError(
					"Illegal value for field %s, should be %s, got %s" \
					% (k, dtype, type(v)))

			self.validate_choices(k, v)

			setattr(self, k, v)

		# Enforce required constraints
		# Note, the string slice on df[1:] is to cut off the leading underscore
		required_fields = [df[1:] for df in self._domain_field_names
			if getattr(self, df).required]

		for field in required_fields:
			if not getattr(self, field):
				raise ValueError("Required field %s not found" % field)

	def __dict__(self):
		"""
		Returns DomainField attributes as key, value dictionary.
		"""
		raise NotImplementedError

	def __eq__(self, other):
		"""
		Same PK means same object.
		"""
		return self.pk == other.pk

	@property
	def _domain_field_names(self):
		"""
		Returns all DomainFields as a list.
		"""
		return [field_name for field_name in dir(self)
			if field_name.startswith("_")
			and field_name != '_domain_field_names'
			and isinstance(getattr(self, field_name), DomainField)]

	def validate_choices(self, field_name: str, value):
		domain_field = getattr(self, "_" + field_name)
		if domain_field.choices and value not in [choice for choice, _ in domain_field.choices]:
			raise DomainModelConstructionException(
				"Illegal value for field %s, legal values are %s" %
				(field_name, domain_field.choices))

	def validate_values(self, **kwargs):
		"""
		Enforce update rules.

		Parameters
		----------
		**kwargs: field_name=value
			field_name is the name of the field to update, value is the new value.
		"""
		for field, value in kwargs.items():
			dtype = getattr(self, "_" + field).dtype
			if dtype and not isinstance(value, dtype):
				raise ValueError("Illegal type %s for field %s, must be %s" %
					(type(value), field, dtype))

	def to_json(self, fields: list = []) -> str:
		"""
		Converts the domain model to json.

		Parameters
		----------
		fields: list[str], optional
			If included, return only the requested fields
			otherwise, return all self._domain_field_names
			on the domain model
		"""
		raise NotImplementedError

	@classmethod
	def from_json(cls, json_string: str):
		"""
		Builds a domain object from json

		Parameters
		----------
		json_string: str, required
			The json string that will be used to populate the domain model.
			if required fields defined in cls._domain_field_names are not included,
			this should raise a DomainModelConstruction exception
		"""
		raise NotImplementedError

