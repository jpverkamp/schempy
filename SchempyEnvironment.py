from SchempyException import SchempyException

class SchempyEnvironment:
	"""Represents the environment in Schempy."""

	def __init__(self, base = None):
		"""Create an environment, potentially on top of a base environment."""
		
		self.Items = []
		self.Base = base
	
	def __getitem__(self, a):
		"""Get an item from the environment."""
		
		for k, v in self.Items:
			if k == a:
				return v
		if self.Base:
			return self.Base[a]
		
		raise SchempyException("Unbound variable: %s" % a)
		
	def __setitem__(self, k, v):
		"""Add an item to the environment."""
		
		self.Items = [(k, v)] + self.Items
		
	def __copy__(self):
		"""Create a copy of the current environment."""
		
		return SchempyEnvironment(self)