import types

import Evaluate

from Types import dot

class Procedure:
	'''Represents a procedure / closure in Schempy.'''

	def __init__(self, paramsOrFunction, bodies = None):
		'''Create a new procedure.'''

		self.Trace = False
		
		if isinstance(paramsOrFunction, types.FunctionType) and not bodies:
			self.IsPython = True
                        if paramsOrFunction.__name__ == '<lambda>':
                                self.Name = None
                        else:
        			self.Name = paramsOrFunction.__name__
			self.Function = paramsOrFunction
		else:
			self.IsPython = False
        		self.Name = None
			self.Params = paramsOrFunction
			self.Bodies = bodies
			
	def __call__(self, env, *args):
		'''Run the procedure.'''

		# Evaluate Python procedures.
		if self.IsPython:
			return self.Function(*args)
			
		# Otherwise, it's a Scheme procedure.
		
		# Extend the environment.
		local_env = env.Extend()
		
		# Get parameter counts, check if they are valid.
		if len(self.Params) >= 2 and isinstance(self.Params[-2], dot):
			dotted = True
			paramCount = len(self.Params) - 2
			if len(args) < paramCount:
				raise ValueError('%s expects at least %d argument%s, given %d, arguments were: %s' %
					(f.__name__, paramCount, '' if paramCount == 1 else 's', len(args), args))
		else:
			dotted = False
			paramCount = len(self.Params) 
			if len(args) != paramCount:
				raise ValueError('%s expects exactly %d argument%s, given %d, arguments were: %s' %
					(f.__name__, paramCount, '' if paramCount == 1 else 's', len(args), args))
					
		# Bind parameters.
		for i in range(paramCount):
			local_env[self.Params[i]] = args[i]
			
		# Bind everything else to the dot parameter (if set).
		if dotted:
			local_env[self.Params[-1]] = list(args[paramCount:])
			
		# Evaluate the bodies in the new environment.
		# Return the last result.
		result = None
		for body in self.Bodies:
			result = Evaluate.Evaluate(body, local_env)
		return result
