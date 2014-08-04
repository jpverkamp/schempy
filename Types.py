from fractions import Fraction as rational

class dot:
	'''For lists.'''
	
	def __repr__(self):
		'''Representation of a dot.'''
		
		return '.'
		
class symbol:
	'''Symbols are distinct from strings.'''
	
	def __init__(self, s, row, col):
		'''Store the row and column.'''
		str.__init__(self, s)
		self.Symbol = s
		self.Row = row
		self.Col = col
	
	def __repr__(self):
		'''Make symbols look distinct from strings.'''
		
		return '%s @ %d:%d' % (self.Symbol, self.Row, self.Col)

class comment(str):
	'''Store comments in the parser tree.'''

	def __repr__(self):
		'''Display strings.'''

		return '<comment %s>' % str.__str__(self)
