from Schemify import Schemify

class InvalidSyntaxException(Exception):
	'''Raise this when syntax is invalid.'''
	def __init__(self, exp, message = None):
		self.Message = 'Invalid syntax: %s, %s' % (Schemify(exp), message if message else '')
	def __repr__(self):
		return self.Message
	def __str__(self):
		return repr(self)
	
class SchempyException(Exception):
	'''Represents a Schempy specific exception.'''
	pass
	
class StopException(Exception):
	'''Tells the interpreter to stop whatever it's doing.'''
	pass

class ParserException(Exception):
	'''An exception occured while parsing.'''
	pass