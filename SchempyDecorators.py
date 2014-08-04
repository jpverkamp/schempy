# Rename functions
def Rename(name):
	def wrap(f):
		f.__name__ = name
		return f
	return wrap
	
# Tell the interpreter that we'll evaluate things
# f.Eval will be bound to the evaluation method
# f.Env will be bound to the current environment
#   changes within the environment (f.Env[x] = y) will be preserved
def DelayEval(f):
	f.__delay__ = True
	return f
