import Procedure
import Syntax

from Types import dot, symbol

from fractions import Fraction as rational

def Schemify(exp):
	'''Convert an expression to Scheme syntax for display purposes.'''
	
	# Nothing to represent
	if exp == None:
		return ''
		
	# Procedures
	elif isinstance(exp, Procedure.Procedure):
		if exp.Name:
			return '#<procedure %s>' % exp.Name
		else:
			return '#<procedure>'
			
	# Syntax
	elif isinstance(exp, Syntax.Syntax):
		if exp.Name:
			return '#<syntax %s>' % exp.Name
		else:
			return '#<syntax>'
			
	# Symbols
	elif isinstance(exp, symbol):
		return str(exp)
	
	# Literals
	# NOTE: bool has to be before int because bools are ints in Python :-\
	elif isinstance(exp, bool):
		if exp:
			return '#t'
		else:
			return '#f'
	elif isinstance(exp, int) or isinstance(exp, long):
		return '%d' % exp
	elif isinstance(exp, rational):
		if exp.denominator == 1:
			return '%d' % exp.numerator
		else:
			return '%d/%d' % (exp.numerator, exp.denominator)
	elif isinstance(exp, float):
		return '%f' % exp
	elif isinstance(exp, complex):
		return str(exp)[1:-2] + 'i'
	elif isinstance(exp, str):
		return '"%s"' % exp
	
	# Lists
	elif isinstance(exp, dot):
		return '.'
	elif isinstance(exp, list):
		if len(exp) == 0:
			return ''
		elif exp[0] == 'quote':
			return '\'' + Schemify(exp[1])
		elif exp[0] == 'quasiquote':
			return '`' + Schemify(exp[1])
		else:
			return '(' + ' '.join([Schemify(subexp) for subexp in exp]) + ')'
		
	# Unknown types
	else:
		raise SchempyException('Unabled to convert to Scheme format: %s', exp)