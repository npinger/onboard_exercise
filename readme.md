# Helpful Background on This Codebase

I've done my best to implement per requirements described here: https://docs.google.com/document/d/1c9inraY1xZX6h9fvGFD6PWjlFRwVdHjuwjiNXh5s08A/edit

Some notes for reading the codebase:

Each folder - analytics, auth, blog, shared - contains /application, /domain, and /infrastructure subdirectories to hint at future maintenance of the architecture.

The only folders that actually have code are:

	.
	./analytics/domain/
	./auth/domain
	./blog/application
	./blog/domain
	./shared/domain  # This contains abstract, shared classes

To run tests, simply:

	cd .../onboard_exercise/
	python3 test.py

## Goals that I tried to achieve:

*Code should look pythonic*

I tried to follow the Zen of Python https://www.python.org/dev/peps/pep-0020/

A few examples:

I took some liberties implementing DomainField to make class definition straightforward and pythonic for new domain models.

Syntax: Tried to follow `Class(**kwargs)` defintion standards in general as opposed to creating new methods, with the exception of `.update(...)` on domain models.

Kept files flat - `flat is better than nested`, rather than splitting into a whole buch of files in the Ruby/Java style.

Imports are explicit (nothing in `__init__`) because `explict is better than implict`.

*Optimize to future code writing*

Abstract classes (eg. DomainField, BaseDomainModel) are hard to read (in violation of `Readability counts`), but they make future domain model definition oh so much easier and more readable (`Although practicality beats purity`).

*Keep interfaces simple, but extend well*

As an example with Post domain model, it will have the following:

	Post.create()
	Post.update()
	Post.from_json() <-- Implicitly calls __init__ to validate
	dict(post) <-- On an instance, this will convert all DomainField name, values to dicts
	# Saving happens at the Repository layer, so not save on the domain model

Adding a new field is as simple as adding:

	new_field = DomainField(<details>)
	# And optionally, called where necessary for specific field validation
	self._validate_new_field(self)


Note: I'm not totally in love with the `_validate_field_name()` pattern. It looks a little ugly in practice, but it is explicit and I'd need to think harder and see more cases to pick a pattern that I like more.

## Finally, a Note on CQRS

I put some semi-detailed thoughts on CQRS into ./blog/application/blog_service.py. I re-looked at chapter 12 of the Cosmic Python book that was shared to kick off this exercise. I wanted to follow the book vs. following our existing code patterns and the instructions as written and raised some future considerations that I believe are worth some serious thought.

In the end, I followed the exercise instructions over the book's suggestions around CQRS to prove that I understood the instructions. I also described in comments what I would have preferred to do given expectations around future growth of the user-facing system.
