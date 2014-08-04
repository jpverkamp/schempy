from fractions import Fraction as rational

@Rename('integer?')
def isinteger(a):
	'''Tests if something is an integer.'''
	return isinstance(a, int)
	
@Rename('rational?')
def isrational(a):
	'''Tests if something is a rational.'''
	return isinteger(a) or isinstance(a, rational)

@Rename('real?')
def isreal(a):
	'''Tests if something is a real number.'''
	return isrational(a) or isinstance(a, float)

@Rename('complex?')
def iscomplex(a):
	'''Tests if something is a complex number.'''
	return isreal(a) or isinstance(a, complex)
	
@Rename('number?')
def isnumber(a):
	'''Tests if something is a number of any sort.'''
	return isreal(a)

@Rename('zero?')
def iszero(a):
	'''Test if a number equals zero.'''
	return a == 0

@Rename('pair?')
def ispair(a):
	'''Tests if something is a pair.'''
	
	return isinstance(a, list)

@Rename('list?')
def islist(a):
	'''Tests if something is a list (a pair where the cdr is a list).'''

	return isinstance(a, list) and (len(a) <= 2 or isinstance(a[-2], SchempyDot))

@Rename('null?')
def isnull(a):
	'''Tests if something is null.'''

	return a == []
