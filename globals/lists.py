from Decorators import *
from Exceptions import SchempyException
from Evaluate import Evaluate
from Schemify import Schemify
from Types import dot

def car(ls):
	'''Take the car of a pair.'''

	return ls[0]
	
def cdr(ls):
	'''Take the cdr of a pair.'''
	
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
	'''Create a pair.'''
	
	if isinstance(b, list):
		return a + b
	else:
		return [a, SchempyDot(), b]
	
@Rename('list')
def _list(*args):
	'''Create a list.'''
	
	return list(args)
	
@Syntax
def quote(exp, env):
	'''Quote something (don't evaluate it).'''
	
	# Expect exactly two parts.
	if len(exp) != 2:
		raise SchempyException('Invalid syntax: %s' % Schemify(exp))
		
	# Otherwise, don't do anything.
	return exp[1]
	
@Syntax
def quasiquote(exp, env):
	'''Quasiquote something (only evaluate unquoted things).'''
	
	# Expect exactly two parts.
	if len(exp) != 2:
		raise SchempyException('Invalid syntax: %s' % Schemify(exp))
	
	# Deal with the paramter.
	if not isinstance(exp[1], list):
		return exp[1]
	elif exp[1] == []:
		return []
	else:
		new_exp = []
		for item in exp[1]:
			if isinstance(item, list) and item[0] == 'unquote':
				new_exp.append(Evaluate.Evaluate(item[1], env))
			else:
				new_exp.append(item)
		return new_exp

def unquote(arg):
	'''Unquote something. This should be covered by quasiquote.'''
	
	raise SchempyException('Invalid syntax: %s' % Schemify(exp), 'Misplaced unquote')
