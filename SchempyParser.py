import re
import types

from SchempyException import SchempyException
from SchempySymbol import SchempySymbol
from SchempyDot import SchempyDot

class SchempyParser:
	"""Parse Schempy strings into lists of expressions."""

	def __init__(self):
		"""Initialize the parser."""
		
		# Whitespace (remove it).
		self.Whitespace = re.compile('\\s*')

		# Types of literals.
		sym = re.escape('!$%&|*+-/:<=>?@^_~')
		Literals = [
			['Comment', '\\;([^\\n]*)',              lambda v : None],
			['String',  '\\"(([^\\"\\\\]|\\.)*)\\"', lambda v : str(v)],
			['Integer', '(\\d+)',                    lambda v : int(v)],
			['Real',    '(\\d*\\.\\d+)',             lambda v : float(v)],
			['Boolean', '#([tf])',                   lambda v : v == 't'],
			['Symbol',  '([\w' + sym + ']+)',        lambda v : SchempySymbol(v)],
			['Dot',     '(\.)',                      lambda v : SchempyDot()],
		]
		
		# Compile regular expressions.
		self.Literals = []
		for name, regex, action in Literals:
			self.Literals.append((re.compile(regex), action))
		
		# Quotelike chracters with their related rator.
		self.Quotelike = {
			'\'': 'quote',
			'`':  'quasiquote',
			',':  'unquote',
		}
		
		# Bracketlike characters with their partner.
		self.Bracketlike = {
			'(':  ')',
			'[':  ']',
		}

	def __call__(self, s):
		"""Parse a string into a list of expressions."""

		# Force all input to lower case.
		s = s.lower()

		# Parse the expression(s).
		exps, s = self.__parse__(s)

		# If there where characters left over, something went wrong.
		if s:
			raise SchempyException("Leftover text after parsing: '%s'" % s)
		else:
			return exps

	def __parse__(self, s):
		"""Parse a string into a list of expressions. Return the list and the unparsed parts of the string."""

		# TODO: Track line number and character for error messages.
		# TODO: Add nicer error messages (for quotes and the like).

		# Expressions found so far.
		exps = []

		# Keep going until we run out of things to parse.
		# If we ever don't advance, return to the parent step and hope they can.
		while s != '':
			exp, s = self.__parseone__(s)
			if exp == None:
				break
			else:
				exps.append(exp)
			
		# Return the expression list.
		return exps, s
	
	def __parseone__(self, s):
		"""Parse a single expression from the given string, return the expression and the string."""
		
		# If we can't parse anything, return None.
		exp = None
		
		# Remove whitespace, stop if we removed everything.
		s = s[self.Whitespace.match(s).end():]
		if not s:
			return None, s
		
		# Quotelike things (quote, quasiquote, unquote)
		if s[0] in self.Quotelike:
			# Remember which quote we were doing.
			toAppend = self.Quotelike[s[0]]
			subexp, s = self.__parseone__(s[1:])
			if subexp:
				exp = [SchempySymbol(toAppend), subexp]
			else:
				exp = [SchempySymbol(toAppend), []]
		
		# S-Expressions
		elif s[0] in self.Bracketlike:
			fromMatch = s[0]
			toMatch = self.Bracketlike[fromMatch]
			subexps, s = self.__parse__(s[1:])
			if not s or s[0] != toMatch:
				raise SchempyException("Unable to find '%s' to close '%s': %s" % (toMatch, fromMatch, s))
			else:
				exp = subexps
				s = s[1:]
		
		# Literals and errors.
		else:
			# Literals.
			matched = False
			for regex, action in self.Literals:
				match = regex.match(s)
				if match:
					exp = action(match.groups()[0])
					s = s[match.end():]
					matched = True
					break
				
		# Return the result.
		return exp, s

