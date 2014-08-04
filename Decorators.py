# Use stackless to bounce functions and avoid the stack.
def Bouncy(f):
	try:
		import stackless
		
		def new_f(*args, **kwargs):
			def wrap(channel, f, args, kwargs):
				try:
					result = f(*args, **kwargs)
					channel.send(result)
				except Exception as e:
					channel.send(e)

			channel = stackless.channel()
			stackless.tasklet(wrap)(channel, f, args, kwargs)
			result = channel.receive()
			if isinstance(result, Exception):
				raise result
			else:
				return result
		
		new_f.__name__ = f.__name__
		new_f.__doc__ = f.__doc__	
		
		return new_f
	except:
		return f

# Rename functions
def Rename(name):
	def wrap(f):
		f.__name__ = name
		return f
	return wrap
	
# Define syntax, it's up to the function to evaluate it's arguments.
# f.Evaluate will be bound to Evaluate(exp, env, k)
# f.Environment will be bound to the current environment
# f.Continuation will be bound to the current continuation
def Syntax(f):
	f.Syntax = True
	return f
