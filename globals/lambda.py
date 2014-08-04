from Exceptions import InvalidSyntaxException
from Decorators import Syntax, Rename
from Procedure import Procedure
from Types import dot, symbol

@Syntax
@Rename("lambda")
def _lambda(exp, env):
	'''Create a function.'''
	
	# Should have at least 3 parts: (lambda params *bodies)
	if len(exp) < 3: 
		raise InvalidSyntaxException(exp)
	
	# Name the parts.
	params = exp[1]
	bodies = exp[2:]
	
	# 'Fix' the formatting on (lambda <symbol> body)
	if isinstance(params, symbol):
		params = [dot(), params]
		
	# Check that the params list is valid otherwise.
	else:
		# All should by symbols or dots.
		for param in params:
			if not (isinstance(param, symbol) or isinstance(param, dot)):
				raise InvalidSyntaxException(exp, '%s is not a symbol' % param)

		# Dots can only be second last.
		for param in params[0:-2] + params[-1:]:
			if isinstance(param, dot):
				raise InvalidSyntaxException(exp, 'only one element allowed after dot')
	
	# Create the procedure.
	return Procedure(params, bodies)
