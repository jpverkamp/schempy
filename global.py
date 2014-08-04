from __future__ import division

import types
import stackless

from Schempy import SchempyEnvironment
from Schempy import SchempySymbol
from Schempy import SchempyDot
from SchempyDecorators import *

# ----- ----- ----- ----- ----- 
# Environment functions
# ----- ----- ----- ----- ----- 

@DelayEval
def define(key, valExp):
	"""Add a variable to the environment."""
	
	# The first variable has to be a symbol.
	if not isinstance(key, SchempySymbol):
		raise ValueError('define expects a symbol for its first argument, %s given' % str(type(args[0])))
	
	# Bind the variable.
	define.Env[key] = define.Eval(valExp, define.Env)
	
	# If it was an unnamed function, remember this as the name.
	if isinstance(define.Env[key], types.FunctionType) and define.Env[key].__name__ == '<procedure>':
		define.Env[key].__name__ = str(key)
		
@DelayEval
@Rename("define-syntax")
def define_syntax(*args):
	"""Define new syntax for the language."""
	
	# TODO: Implement this.
	
	pass
	

	
@DelayEval
@Rename("lambda")
def _lambda(params, *bodies):
	"""Create a function."""
	
	# 'Fix' the formatting on (lambda <symbol> body)
	if isinstance(params, SchempySymbol):
		params = [SchempyDot(), params]
		
	# Check that the params list is valid otherwise.
	else:
		# All should by symbols or dots.
		for param in params:
			if not (isinstance(param, SchempySymbol) or isinstance(param, SchempyDot)):
				raise ValueError('Error in lambda definition, %s is not a symbol' % param)

		# Dots can only be second last.
		for param in params[0:-2] + params[-1:]:
			if isinstance(param, SchempyDot):
				raise ValueError('Error in lambda definition, only one element allowed after dot')
	
	# Use stackless to evaluate the lambdas.
	# Stackless code.
	def call_wrapper(f, args, kwargs, result_ch):
		result_ch.send(f(*args, **kwargs))
	
	def call(f, *args, **kwargs):
		result_ch = stackless.channel()
		stackless.tasklet(call_wrapper)(f, args, kwargs, result_ch)
	
	# Create the new function.
	def f(*args):
		# Extend the environment.
		localEnv = SchempyEnvironment(_lambda.Env)
		
		# Get parameter counts, check if they are valid.
		if len(params) >= 2 and isinstance(params[-2], SchempyDot):
			dotted = True
			paramCount = len(params) - 2
			if len(args) < paramCount:
				raise ValueError('%s expects at least %d argument%s, given %d, arguments were: %s' %
					(f.__name__, paramCount, '' if paramCount == 1 else 's', len(args), args))
		else:
			dotted = False
			paramCount = len(params) 
			if len(args) != paramCount:
				raise ValueError('%s expects exactly %d argument%s, given %d, arguments were: %s' %
					(f.__name__, paramCount, '' if paramCount == 1 else 's', len(args), args))
					
		# Bind parameters.
		for i in range(paramCount):
			localEnv[params[i]] = args[i]
			
		# Bind everything else to the dot parameter (if set).
		if dotted:
			localEnv[params[-1]] = list(args[paramCount:])
			
		# Evaluate the bodies in the new environment.
		result = None
		for body in bodies:
			result = _lambda.Eval(body, localEnv)
		return result
					
	# Anon it and return.
	f.__name__ = '<procedure>'
	return f

def trace(f):
	"""Toggle tracing on a function."""
	
	if not isinstance(f, types.FunctionType):
		raise ValueError('Cannot trace non-procedure: %s' % f)
	else:
		if not 'Trace' in dir(f):
			f.Trace = True
		else:
			f.Trace = not f.Trace

# ----- ----- ----- ----- ----- 
# Mathematical functions
# ----- ----- ----- ----- ----- 

@Rename('+')
def add(*args):
	"""Add numbers."""
	result = 0
	for arg in args:
		result += arg
	return result

@Rename('-')
def sub(*args):
	"""Subtract numbers."""
	if len(args) < 1:
		raise ValueError('- expects at least 1 argument, given %d' % len(args))
	result = args[0]
	for arg in args[1:]:
		result -= arg
	return result
	
@Rename('*')
def mul(*args):
	"""Multiply numbers."""
	result = 1
	for arg in args:
		result *= arg
	return result
	
@Rename('/')
def div(*args):
	"""Divide numbers."""
	if len(args) < 1:
		raise ValueError('/ expects at least 1 argument, given %d' % len(args))
	result = args[0]
	for arg in args[1:]:
		result /= arg
	return result
	
def add1(n):
	"""Add one to a number."""
	return n + 1

def sub1(n):
	"""Subtract one from a number."""
	return n - 1
	
# ----- ----- ----- ----- ----- 
# Logical functions
# ----- ----- ----- ----- ----- 

@Rename('and')
def _and(*args):
	"""Logical and."""
	if args:
		if args[0] == False:
			return False
		else:
			return _and(*args[1:])
	else:
		return True

@Rename('or')
def _or(*args):
	"""Logical or."""
	if args:
		if args[0] != False:
			return True
		else:
			return _or(*args[1:])
	else:
		return False

@Rename('not')
def _not(a):
	"""Logical not."""
	return a == False

@DelayEval
@Rename('if')
def _if(test, then, alt):
	"""If statements."""
	
	if _if.Eval(test, _if.Env) != False:
		return _if.Eval(then, _if.Env)
	else:
		return _if.Eval(alt, _if.Env)
		
# TODO: Figure out how these should be different.
# NOTE: Turns out AND has a higher precedence than < > <= >= etc

@Rename('=')
def _equalSign(*args):
	"""Tests if numbers or symbols are equal."""
	if len(args) < 1:
		raise ValueError('= expects at least 1 argument, given %d' % len(args))
	if len(args) == 1:
		return True
	else:
		return (args[0] == args[1]) and _equalSign(*args[1:])

@Rename('eq?')
def _eq(*args):
	"""Tests if two things point to the same memory."""
	_equalSign(*args)

@Rename('eqv?')
def _eqv(*args):
	"""Tests if two things are equivalent."""
	_equalSign(*args)

@Rename('equal?')
def _equal(*args):
	"""Tests if two things have the same values."""
	_equalSign(*args)

# These could probably be combined.
# NOTE: Turns out AND has a higher precedence than < > <= >= etc

@Rename('<')
def _lt(*args):
	"""Tests less than."""
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
	"""Tests less than or equal to."""
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
	"""Tests greater than."""
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
	"""Tests greater than or equal to."""
	if len(args) < 1:
		raise ValueError('>= expects at least 1 argument, given %d' % len(args))
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

def car(ls):
	"""Take the car of a pair."""

	return ls[0]
	
def cdr(ls):
	"""Take the cdr of a pair."""
	
	l = len(ls)
	if l == 0:
		raise ValueError("Cannot take the cdr of an empty list.")
	elif l == 1:
		return []
	elif l == 3 and isinstance(l[1], SchempyDot):
		return l[2]
	else:
		return ls[1:]

def cons(a, b):
	"""Create a pair."""
	
	if isinstance(b, list):
		return a + b
	else:
		return [a, SchempyDot(), b]
	
@Rename('list')
def _list(*args):
	"""Create a list."""
	
	return list(args)
	
@DelayEval
def quote(arg):
	"""Quote something (don't evaluate it)."""
	
	return arg
	
@DelayEval
def quasiquote(arg):
	"""Quasiquote something (only evaluate unquoted things)."""
	
	if not isinstance(arg, list):
		return arg
	elif arg == []:
		return []
	elif arg[0] == 'unquote':
		return quasiquote.Eval(arg[1], quasiquote.Env)
	else:
		return [quasiquote(item) for item in arg]

def unquote(arg):
	"""Unquote something."""
	
	raise SchempyException("Misplaced unquote: ,%s", arg)

# ----- ----- ----- ----- ----- 
# Predicates
# ----- ----- ----- ----- ----- 

# TODO: Add rational? and complex? to numerical tower.

@Rename('integer?')
def isinteger(a):
	"""Tests if something is an integer."""
	return isinstance(a, int)

@Rename('real?')
def isreal(a):
	"""Tests if something is a real number (or simpler)."""
	return isinteger(a) or isinstance(a, float)

@Rename('number?')
def isreal(a):
	"""Tests if something is a number of any sort."""
	return isreal(a)

@Rename('zero?')
def iszero(a):
	"""Test if a number equals zero."""
	return a == 0

@Rename('pair?')
def ispair(a):
	"""Tests if something is a pair."""
	
	return isinstance(a, list)

@Rename('list?')
def islist(a):
	"""Tests if something is a list (a pair where the cdr is a list)."""

	return isinstance(a, list) and (len(a) <= 2 or isinstance(a[-2], SchempyDot))

@Rename('null?')
def isnull(a):
	"""Tests if something is null."""

	return a == []

