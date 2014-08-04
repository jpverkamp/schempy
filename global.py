from __future__ import division
from SchempyExport import Export

# ----- ----- ----- ----- ----- 
# Mathematical functions
# ----- ----- ----- ----- ----- 

@Export('+', 0)
def add(*args):
	"""Add numbers."""
	result = 0
	for arg in args:
		result += arg
	return result

@Export('-', 1)
def sub(*args):
	"""Subtract numbers."""
	result = args[0]
	for arg in args[1:]:
		result -= arg
	return result
	
@Export('*', 0)
def mul(*args):
	"""Multiply numbers."""
	result = 1
	for arg in args:
		result *= arg
	return result
	
@Export('/', 1)
def div(*args):
	"""Divide numbers."""
	result = args[0]
	for arg in args[1:]:
		result /= arg
	return result
	
@Export()
def add1(n):
	"""Add one to a number."""
	return n + 1

@Export()
def sub1(n):
	"""Subtract one from a number."""
	return n - 1
	
# ----- ----- ----- ----- ----- 
# Logical functions
# ----- ----- ----- ----- ----- 

@Export('and', 0, True)
def _and(*args):
	"""Logical and."""
	if args:
		if args[0]() == False:
			return False
		else:
			return _and(*args[1:])
	else:
		return True

@Export('or', 0, True)
def _or(*args):
	"""Logical or."""
	if args:
		if args[0]() != False:
			return True
		else:
			return _or(*args[1:])
	else:
		return False

@Export('not')
def _not(a):
	"""Logical not."""
	return not a

@Export('if', thunkify = True)
def _if(test, then, alt):
	"""If statements."""
	if test() != False:
		return then()
	else:
		return alt()
		
# TODO: Figure out how these should be different.
# NOTE: Turns out AND has a higher precedence than < > <= >= etc

@Export('=', 1, True)
def _equalSign(*args):
	"""Tests if numbers or symbols are equal."""
	if len(args) == 1:
		return True
	else:
		return (args[0] == args[1]) and _equalSign(*args[1:])

@Export('eq?', 1, True)
def _eq(*args):
	"""Tests if two things point to the same memory."""
	_equalSign(*args)

@Export('eqv?', 1, True)
def _eqv(*args):
	"""Tests if two things are equivalent."""
	_equalSign(*args)

@Export('equal?', 1, True)
def _equal(*args):
	"""Tests if two things have the same values."""
	_equalSign(*args)

# These could probably be combined.
# NOTE: Turns out AND has a higher precedence than < > <= >= etc
# NOTE: Not thunked!  This is probably bad.

@Export('<', 1, True)
def _lt(*args):
	"""Tests less than."""
	a = args[0]()
	for i in range(len(args) - 1):
		b = args[i + 1]()
		if not (a < b):
			return False
		a = b
	return True

@Export('<=', 1, True)
def _lte(*args):
	"""Tests less than or equal to."""
	a = args[0]()
	for i in range(len(args) - 1):
		b = args[i + 1]()
		if not (a <= b):
			return False
		a = b
	return True

@Export('>', 1, True)
def _gt(*args):
	"""Tests greater than."""
	a = args[0]()
	for i in range(len(args) - 1):
		b = args[i + 1]()
		if not (a > b):
			return False
		a = b
	return True

@Export('>=', 1, True)
def _gte(*args):
	"""Tests greater than or equal to."""
	a = args[0]()
	for i in range(len(args) - 1):
		b = args[i + 1]()
		if not (a >= b):
			return False
		a = b
	return True

# ----- ----- ----- ----- ----- 
# Logical functions
# ----- ----- ----- ----- ----- 

@Export()
def car(pair):
	"""Take the car of a pair."""
	return pair[0]
	
@Export()
def cdr(pair):
	"""Take the cdr of a pair."""
	return pair[1]

@Export()
def cons(a, b):
	"""Create a pair."""
	return (a, b)
	
@Export('list', 0)
def list(*args):
	"""Create a list."""
	result = None
	for arg in reversed(args):
		result = (arg, result)
	return result

# ----- ----- ----- ----- ----- 
# Predicates
# ----- ----- ----- ----- ----- 

# TODO: Add rational? and complex? to numerical tower.

@Export('integer?')
def _integer(a):
	"""Tests if something is an integer."""
	return isinstance(a, int)

@Export('real?')
def _real(a):
	"""Tests if something is a real number (or simpler)."""
	return _integer(a) or isinstance(a, float)

@Export('number?')
def _real(a):
	"""Tests if something is a number of any sort."""
	return _real(a)

@Export('zero?')
def _zero(a):
	"""Test if a number equals zero."""
	return a == 0

@Export('pair?')
def _pair(a):
	"""Tests if something is a pair."""
	return type(a) == tuple

@Export('list?')
def _list(a):
	"""Tests if something is a list (a pair where the cdr is a list)."""
	if a == None:
		return True
	elif isinstance(a, tuple):
		return _list(cdr(a))
	else:
		return False

@Export('null?')
def _null(a):
	"""Tests if something is null."""
	return a == None

