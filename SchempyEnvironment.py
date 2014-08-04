import types

from SchempyException import SchempyException

class SchempyEnvironment:
	"""Represents a current environment in Schempy."""

	def __init__(self, base = None):
		"""Create a new environment with a (possible) base environment."""

		self.Base = base
		self.Vars = {}

	def __getitem__(self, key):
		"""Get an item from this environment."""

		if key in self.Vars:
			return self.Vars[key]
		elif self.Base:
			return self.Base[key]
		else:
			raise SchempyException('Unbound variable: %s' % key)

	def __setitem__(self, key, val):
		"""Set an item in this environment."""

		self.Vars[key] = val
		
	def __str__(self):
		"""Stringify the environment."""
		
		result = '[env ' + ', '.join([str(k) + ':' + ('function' if isinstance(v, types.FunctionType) else str(v)) for k, v in self.Vars.items()])
		if self.Base:
			result += ' ' + str(self.Base)
		result += ']'
		return result
		
	def __repr__(self):
		"""Return a representation of the environment."""
		
		return str(self)
