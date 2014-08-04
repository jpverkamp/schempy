import Exceptions
import Evaluate

from Decorators import Syntax, Rename

@Syntax
@Rename('and')
def _and(exp, env):
	'''Logical and.'''

	# (and) is True.
	if len(exp) == 1:
		return True
		
	# Otherwise, run the first one.
	else:
		if Evaluate(exp[1], env) == False:
			return False
		else:
			return _and(exp[0:1] + exp[2:], env)

@Syntax
@Rename('or')
def _or(exp, env):
	'''Logical or.'''
	
	# (or) is False.
	if len(exp) == 1:
		return False
		
	# Otherwise, run the first one.
	else:
		if Evaluate(exp[1], env) != False:
			return True
		else:
			return _or(exp[0:1] + exp[2:], env)

@Rename('not')
def _not(a):
	'''Logical not.'''
	return a == False

@Syntax
@Rename('if')
def _if(exp, env):
	'''If statements.'''
	
	# Has to be of the form (if cond then) or (if cond then else).
	if not (len(exp) == 3 or len(exp) == 4):
		raise Exceptions.InvalidSyntaxException(exp)
		
	# Evaluate the condition.
	# If it's true, run the then case.
	if Evaluate(exp[1], env) != False:
		return Evaluate(exp[2], env)
	
	# If not, run the else case (if it exists).
	elif len(exp) == 4:
		return Evaluate(exp[3], env)

# These could probably be combined.
# NOTE: Turns out AND has a higher precedence than < > <= >= etc
		
@Rename('=')
def _equalSign(*args):
	'''Tests if numbers or symbols are equal.'''
	if len(args) < 1:
		raise ValueError('= expects at least 1 argument, given %d' % len(args))
	if len(args) == 1:
		return True
	else:
		return (args[0] == args[1]) and _equalSign(*args[1:])

@Rename('eq?')
def _eq(*args):
	'''Tests if two things point to the same memory.'''
	_equalSign(*args)

@Rename('eqv?')
def _eqv(*args):
	'''Tests if two things are equivalent.'''
	_equalSign(*args)

@Rename('equal?')
def _equal(*args):
	'''Tests if two things have the same values.'''
	_equalSign(*args)
	
@Rename('<')
def _lt(*args):
	'''Tests less than.'''
	if len(args) < 1:
		raise ValueError('< expects at least 1 argument, given %d' % len(args))
	a = args[0]
	for i in range(len(args) - 1):
		b = args[i + 1]
		if not (a < b):
			return False
		a = b
	return True

@Rename('<=')
def _lte(*args):
	'''Tests less than or equal to.'''
	if len(args) < 1:
		raise ValueError('<= expects at least 1 argument, given %d' % len(args))
	a = args[0]
	for i in range(len(args) - 1):
		b = args[i + 1]
		if not (a <= b):
			return False
		a = b
	return True

@Rename('>')
def _gt(*args):
	'''Tests greater than.'''
	if len(args) < 1:
		raise ValueError('> expects at least 1 argument, given %d' % len(args))
	a = args[0]()
	for i in range(len(args) - 1):
		b = args[i + 1]()
		if not (a > b):
			return False
		a = b
	return True

@Rename('>=')
def _gte(*args):
	'''Tests greater than or equal to.'''
	if len(args) < 1:
		raise ValueError('>= expects at least 1 argument, given %d' % len(args))
	a = args[0]()
	for i in range(len(args) - 1):
		b = args[i + 1]()
		if not (a >= b):
			return False
		a = b
	return True