import types

import Procedure
import Evaluate
import Syntax as SyntaxModule

from Exceptions import SchempyException, InvalidSyntaxException
from Decorators import Syntax
from Types import symbol

@Syntax
def define(exp, env):
	'''Add a variable to the environment.'''
	
	# Has to have two parts and the first has to be a symbol.
	if len(exp) != 3 or not isinstance(exp[1], symbol):
		raise InvalidSyntaxException(exp)
	
	# Evaluate the variable.
	value = Evaluate(exp[2], env)
	
	# Give the name to procedures or syntaxes without names.
	if (isinstance(value, Procedure) or isinstance(value, SyntaxModule.Syntax)) and not value.Name:
		value.Name = exp[1]
	
	# Bind it to the environment.
	env[exp[1]] = value

@Syntax
def load(exp, env):
	'''Load a file.'''
	
	# Has to be two parts and the second part has to be a string.
	if len(exp) != 2 or not isinstance(exp[1], str):
		raise InvalidSyntaxException(exp)
		
	# Otherwise, try to load the file.
	env.Load(exp[1])

def trace(f):
	'''Toggle tracing on a function.'''
	
	if (isinstance(f, Procedure) or isinstance(f, SyntaxModule.Syntax)):
		f.Trace = not f.Trace
	else:
		raise ValueError('Cannot trace non-procedure: %s' % f)