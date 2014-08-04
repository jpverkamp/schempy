import types

class Thunk:
	def __init__(self, f, *args):
		self.F = f
		self.Args = args
	def __call__(self):
		return self.F(*(self.Args))
		
class Export:
	"""Export functions to Scheme."""

	def __init__(self, name = None, minimumArgs = -1, thunkify = False):
		"""Create a specific decorator."""

		self.Name = name
		self.MinimumArgs = minimumArgs
		self.Thunkify = thunkify

	def __call__(self, f):
		"""Create the new function."""

		# Create the function.
		def new_f(*args, **kwargs):
			# Print traceif requested.
			if new_f.Trace:
				print '%s(%s)' % (new_f.Name, ' '.join([str(arg()) if isinstance(arg, Thunk) else str(arg) for arg in args]))
				
			# Call the actual function.
			return f(*args, **kwargs)

		# Leave a note that this function was exported
		new_f.SchempyFunction = True
		new_f.Trace = False

		# Directly copy docstrings.
		new_f.Help = f.__doc__	

		# Use the function's name if no name was specified.
		if self.Name:
			new_f.Name = self.Name
			new_f.__name__ = self.Name
		else:
			new_f.Name = f.__name__
			new_f.__name__ = f.__name__

		# Get the argument count for collected arguments.
		if self.MinimumArgs < 0:
			new_f.CollectArgs = False
			new_f.ArgCount = f.__code__.co_argcount
		else:
			new_f.CollectArgs = True
			new_f.ArgCount = self.MinimumArgs

		# Remember if evaluation should be delayed for this function.
		new_f.Thunkify = self.Thunkify

		# Return the new function.
		return new_f

