from Decorators import Rename

@Rename('+')
def add(*args):
	'''Add numbers.'''
	result = 0
	for arg in args:
		result += arg
	return result

@Rename('-')
def sub(*args):
	'''Subtract numbers.'''
	if len(args) < 1:
		raise ValueError('- expects at least 1 argument, given %d' % len(args))
	result = args[0]
	for arg in args[1:]:
		result -= arg
	return result
	
@Rename('*')
def mul(*args):
	'''Multiply numbers.'''
	result = 1
	for arg in args:
		result *= arg
	return result
	
@Rename('/')
def div(*args):
	'''Divide numbers.'''
	if len(args) < 1:
		raise ValueError('/ expects at least 1 argument, given %d' % len(args))
	result = args[0]
	for arg in args[1:]:
		result /= arg
	return result
	
def add1(n):
	'''Add one to a number.'''
	return n + 1

def sub1(n):
	'''Subtract one from a number.'''
	return n - 1
