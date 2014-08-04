import re

from Exceptions import ParserException
from Types import symbol, dot, comment, rational

class Parser:
	'''Parse Schempy strings into lists of expressions.'''

	def __init__(self):
		'''Initialize the parser.'''
		
		# Whitespace (remove it).
		self.Whitespace = re.compile(r'(\s*)')

		# Types.
		sym = re.escape('!$%&|*+-/:<=>?@^_~')
		Types = [
			['Comment',  r'\;([^\n]*)',                       lambda v, r, c : comment(v)],
			['String',   r'\"(([^\"\\]|\\.)*)\"',             lambda v, r, c : str(v)],
			['Complex',  r'(\d+(\.\d+)?(\+|\-)\d+(\.\d+)?)i', lambda v, r, c : complex(v + 'j')],
			['Real',     r'(\d*\.\d+)',                       lambda v, r, c : float(v)],
			['Rational', r'(\d+/\d+)',                        lambda v, r, c : rational(v)],
			['Integer',  r'(\d+)',                            lambda v, r, c : int(v)],
			['Boolean',  r'#([tf])',                          lambda v, r, c : v == 't'],
			['Symbol',   r'([\w' + sym + ']+)',               lambda v, r, c : symbol(v, r, c)],
			['Dot',      r'(\.)',                             lambda v, r, c : dot()],
		]
		
		# Compile regular expressions.
		self.Types = []
		for name, regex, action in Types:
			self.Types.append((re.compile(regex), action))
		
		# Quotelike chracters with their related rator.
		self.Quotelike = {
			"#":    'vector',
			"#vu8": 'bytevector',
			"'":    'quote',
			"`":    'quasiquote',
			",":    'unquote',
			",@":   'unquote-splicing',
			"#'":   'syntax',
			"#`":   'quasisyntax',
			"#,":   'unsyntax',
			"#,@":  'unsyntax-splicing',
		}
		
		# Bracketlike characters with their partner.
		self.Bracketlike = {
			'(':    ')',
			'[':    ']',
		}

	def __call__(self, s):
		'''Parse a string into a list of expressions.'''

		# Force all input to lower case.
		s = s.lower()

		# Parse the expression(s).
		exps, s, row, col = self.__parse__(s, 0, 0)

		# If there where characters left over, something went wrong.
		if s:
			raise ParserException("Leftover text after parsing: '%s'" % s)
		else:
			return exps

	def __parse__(self, s, row, col):
		'''Parse a string into a list of expressions. Return the list and the unparsed parts of the string.'''

		# Expressions found so far.
		exps = []

		# Keep going until we run out of things to parse.
		# If we ever don't advance, return to the parent step and hope they can.
		while s != '':
			exp, s, row, col = self.__parseone__(s, row, col)
			if exp == None:
				break
			else:
				exps.append(exp)
			
		# Return the expression list.
		return exps, s, row, col
	
	def __parseone__(self, s, row, col):
		'''
		Parse a single expression from the given string.
		Return (exp, s, row, col).
		'''
		
		# If we can't parse anything, return None.
		exp = None
		
		# Remove whitespace, stop if we removed everything.
		m = self.Whitespace.match(s).groups()[0]
		if '\n' in m:
			row += m.count('\n')
			col = len(m) - m.rfind('\n')
		else:
			col += len(m)
		s = s[len(m):]
		
		# Nothing left to parse.  We're done.
		if not s:
			return None, s, row, col
		
		# Quotelike things (quote, quasiquote, unquote, etc.)
		for k, v in self.Quotelike.items():
			if s.startswith(k):
				subexp, s, row, col = self.__parseone__(s[len(k):], row, col + len(k))
				if subexp:
					exp = [symbol(v), subexp]
				else:
					exp = [symbol(v), []]
		
		# S-Expressions
		for l, r in self.Bracketlike.items():
			if s.startswith(l):
				o_row, o_col = row, col
				subexps, s, row, col = self.__parse__(s[1:], row, col + 1)
				if not s or not s.startswith(r):
					raise ParserException("Unable to find '%s' to close '%s' at %d:%d" % (r, l, o_row, o_col))
				else:
					exp = subexps
					s = s[1:]
		
		# Anything else.
		else:
			for regex, action in self.Types:
				match = regex.match(s)
				if match:
					orig = match.groups()[0]
					exp = action(orig, row, col)
					col += len(orig)
					s = s[match.end():]
					break
				
		# Return the result.
		return exp, s, row, col

