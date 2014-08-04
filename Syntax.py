
# TODO: Should have self.Name, set to None if no name is defined.

class Syntax:
	'''Represents a macro in Schempy.'''

	def __init__(self, f):
		'''Create new syntax.'''

		self.Trace = False
		
		self.Function = f
		self.Name = f.__name__

	def __call__(self, exp, env):
		'''Run the procedure.'''
		
		return self.Function(exp, env)
