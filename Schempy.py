from fractions import Fraction as rational

import Environment
import Exceptions
import Schemify
import Evaluate
import Parser

if __name__ == '__main__':
	'''Run from the command line.'''
	
	import os, sys
	
	# Create the base environment.
	base_environment = Environment.Environment()
	
	# Load the global environment.
	if os.path.isdir('globals'):
		base_environment.Import('globals')
	
	# Run files as given.
	if len(sys.argv) > 1:
		for filename in sys.argv[:1]:
			base_environment.Load(Evaluate, filename)
			
	# Start the REPL.
	
	# Generate a parser.
	parse = Parser.Parser()
	
	# Keep going until (exit) or (quit)
	while True:
		code = ''
		
		# Read at least one line, until parens match.
		# TODO: Add scheme-like tab support (maybe?)
		lparens = 0
		rparens = 0
		print '\nSchempy>',
		while code == '' or lparens > rparens:
			if code != '': print '        ',
			code += raw_input('')
			lparens = code.count('(') + code.count('[')
			rparens = code.count(')') + code.count(']')
			
		# Got the input, try to evaluate it.
		try:
			exps = parse(code)
			for exp in exps:
				result = Schemify.Schemify(Evaluate.Evaluate(exp, base_environment))
				if result:
					print result
		
		# Something broke, report the error.
		except Exceptions.ParserException as ex:
			print '\nParse Error: %s' % str(ex)
			
		# Something broke, report the error.
		except Exceptions.SchempyException as ex:
			print '\nSchempy Error: %s' % str(ex)
			
		# Stop requested.
		except Exceptions.StopException:
			break
