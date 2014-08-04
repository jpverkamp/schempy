import Exceptions
import Procedure
import Schemify
import Syntax

from Decorators import Bouncy
from Types import dot, symbol

@Bouncy
def Evaluate(exp, env):
	'''Evaluate an expression in the given environment'''
	
	#print 'Evaluating %s of type %s' % (exp, type(exp))
	
	# Lookup symbols in the environment.
	if isinstance(exp, symbol):
		return env[exp]
		
	# Everything else (except for lists) is a literal, return it.
	elif not isinstance(exp, list):
		return exp
	
	# Otherwise, apply macros then run it.
	elif isinstance(exp, list):
		# Error handling for empty lists.
		if (len(exp) == 0):
			raise Exceptions.InvalidSyntaxException(exp)
		
		# Get the function / syntax rules.
		rator = Evaluate(exp[0], env)
		
		# Syntax rules need to access the evaluator and current environment.
		# The syntax expression is responsible for recursive calls if needed.
		if isinstance(rator, Syntax.Syntax):
			return rator(exp, env)

		# Procedure arguments will be evaluated here.
		elif isinstance(rator, Procedure.Procedure):
			# Evaluate the arguments.
			rands = [Evaluate(rand, env) for rand in exp[1:]]
			
			# Trace, if requested.
			if rator.Trace:
				print Schemify.Schemify([rator.Name] + rands)
			
			# Apply the procedure.
			return rator(env, *rands)
			
		# Otherwise, I have no idea how to evaluate it.
		else:
			raise Exceptions.InvalidSyntaxException(exp, '%s is not a procedure' % rator)