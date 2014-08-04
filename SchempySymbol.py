class SchempySymbol(str):
	"""Symbols are distinct from strings."""

	def __repr__(self):
		"""Make symbols look distinct from strings."""
		
		return '%s' % str.__str__(self)
