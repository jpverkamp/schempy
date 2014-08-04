import os
import sys
import copy
import types

import pyparsing

from SchempyExport import Export, Thunk
from SchempyException import SchempyException
from SchempyEnvironment import SchempyEnvironment
from pyparsing import ParseException

class Schempy:
	"""Main parsing engine."""

	def __init__(self):
		"""Initialize everything."""

		self.Trace = False
		self.Running = True
		
		self.__InitParser()
		self.__InitEnvironment()

	def Evaluate(self, exp):
		"""Evaluate an expression."""

		# Convert to lowercase, parse.
		# TODO: Handle other exception types.
		try:
			exps = self.SExp.parseString(exp.lower())
		except ParseException as ex:
			raise SchempyException(str(ex))
		
		# Loop through the expressions.
		results = []
		for exp in exps:
			result = self.__Eval(exp)
			if result != None:
				resultStr = self.__tostr(result)
				if resultStr:
					results.append(resultStr)
				
			# If (quit) or (exit) was called, stop now.
			if not self.Running:
				break
				
		# Return a list of results.
		return results

	def REPL(self):
		"""Runs a Read-Eval-Print-Loop"""

		# Keep going until (exit) or (quit)
		while self.Running:
			line = ''
			
			# Read at least one line, until parens match.
			# TODO: Add scheme-like tab support (maybe?)
			lparens = 0
			rparens = 0
			print '\nSchempy>',
			while line == '' or lparens != rparens:
				if line != '': print '        ',
				line += raw_input('')
				lparens = line.count('(') + line.count('[')
				rparens = line.count(')') + line.count(']')
				
			# Got the input, try to evaluate it.
			try:
				results = self.Evaluate(line)
				for line in results:
					print line
					
			# Something broke, report the error.
			except SchempyException as ex:
				print '\nError: %s' % str(ex)
				
	def Load(self, filename):
		"""Load a file."""

		# Make sure the file exists.
		if not os.path.exists(filename):
			raise SchempyException('Unable to load %s, file does not exist.' % filename)
		path, ext = os.path.splitext(filename)
			
		# Check if it's Python or Scheme.
		# Load Scheme files.
		if ext in ('.ss', '.scm'):
			text = open(filename, 'r').read()
			results = self.Evaluate(text)
			for line in results:
					print line
		
		# Load Python files.
		# TODO: Make previous bindings available to the import.
		# TODO: Might be able to do this using global(), but I don't know how to fix it afterwords.
		elif ext in ('.py', ):
			# Load the file as a module.
			sys.path += os.getcwd()
			newModule = __import__(path)
			sys.path = sys.path[:-1]
			
			# Look through the file, load any functions.
			for fname in dir(newModule):
				f = newModule.__dict__.get(fname)
				if isinstance(f, types.FunctionType) and 'SchempyFunction' in dir(f) and f.SchempyFunction:
					self.GlobalEnv[f.__name__] = f
										
		# Break on any other file types.
		else:
			raise SchempyException('Unable to load %s, unknown file type.' % filename)
			
	def __InitParser(self):
		"""Initialize the parser."""
		
		# Pyparsing really does most of the work.
		from pyparsing import alphas, nums, printables, oneOf, stringEnd, Word, Suppress, Forward, Group, ZeroOrMore, OneOrMore, QuotedString

		# What we're eventually trying to build.
		lparen = (Suppress('(') | Suppress('['))
		rparen = (Suppress(')') | Suppress(']'))
		exp = Forward()
		
		# Possible characters for us in symbols.
		validSymbolChars = alphas + nums + '!$%&|*+-/:<=>?@^_~'

		# Literals.
		string = (QuotedString(quoteChar='"', escChar='\\')).setParseAction(lambda v : v[0])
		boolean = (Suppress('#') + oneOf('t f')).setParseAction(lambda v : False if v[0] == 'f' else True)
		integer = (Word(nums)).setParseAction(lambda v : int(v[0]))
		real = (Word(nums) + Suppress('.') + Word(nums)).setParseAction(lambda v : float(v[0] + '.' + v[1]))
		null = (Suppress("'") + lparen + rparen).setParseAction(lambda v : None)
		literal = (string | boolean | integer | real | null)

		# Other identifiers (parse as strings).
		ident = Word(validSymbolChars).setParseAction(lambda v : [['symbol', v[0]]])

		# Quoted expressions.
		quote = (Suppress("'") + exp).setParseAction(lambda v : [['quote', v[0]]])

		# Final expression.
		exp << (literal |
				quote |
				ident |
				Group(lparen + OneOrMore(exp) + rparen))
		self.SExp = (ZeroOrMore(exp) + stringEnd)

	def __InitEnvironment(self):
		"""Create the global enviroment."""

		# Create an empty environment.
		self.GlobalEnv = SchempyEnvironment()

		# Base functions to load files, reset the environment, and quit.
		# Might want some more error checking here.
		self.GlobalEnv['trace-eval'] = Export('trace-eval')(lambda : self.__Trace())
		self.GlobalEnv['load'] = Export('load')(lambda f : self.Load(f))
		self.GlobalEnv['reset'] = Export('reset')(lambda : self.__InitEnvironment())
		self.GlobalEnv['exit'] = Export('exit')(lambda : self.__Stop())
		self.GlobalEnv['quit'] = Export('quit')(lambda : self.__Stop())
		self.GlobalEnv['trace'] = Export('trace')(lambda f : self.__Trace(f))
		
		# Load globals.
		self.Load('global.py')
		
	def __Trace(self, f = None):
		"""Start tracing."""
		if f:
			f.Trace = True
		else:
			self.Trace = True
		
	def __Stop(self):
		"""The user requested (quit/exit)."""
		self.Running = False

	def __Eval(self, exp, env = None, level = 0):
		"""Evaluate an expression."""
		
		# Setup an initial environment if it hasn't been done so before.
		if not env:
			env = SchempyEnvironment(self.GlobalEnv)

		# User requested tracing everything (good for them?)
		if self.Trace:
			for i in range(level):
				print '|',
			print '%s' % self.__tostr(exp)

		# Start with nothing.
		result = None
			
		# Anything that's not a list is a literal.
		if not (isinstance(exp, pyparsing.ParseResults) or isinstance(exp, tuple) or isinstance(exp, list)):
			result = exp
			
		# Look up symbols.
		elif exp[0] == 'symbol':
			result = env[exp[1]]
			
		# Defines alter the global environment.
		# TODO: Figure out how these are supposed to work in a non-global context.
		# TODO: Add short syntax for lambdas.
		elif exp[0] == ['symbol', 'define']:
			self.GlobalEnv[exp[1][1]] = self.__Eval(exp[2], env, level + 1)
			result = None

		# Bind lambdas.
		# TODO: Add the different lambda forms.
		elif exp[0] == ['symbol', 'lambda']:		
			def f(*args):
				# Something went horribly wrong.
				if len(args) != len(exp[1]):
					# TODO: Remove from final code.
					raise SchempyException("Unable to apply function because of mismtached argument count (THIS SHOULDN'T HAPPEN!)")

				# Create a new environment to work with.
				newEnv = copy.copy(env)
					
				# Bind parameters.
				# exp[1] is the parameter list,
				#   exp[1][i] is each specific paramter,
				#   exp[1][i][1] removes the ['symbol'] identifier
				for i in range(len(args)):
					newEnv[exp[1][i][1]] = args[i]()

				# Evaluate the body.
				return self.__Eval(exp[2], newEnv, level + 1)
			
			# Set all the extra variables to make this a Schempy function.
			closure = Export(None, len(exp[1]), thunkify = True)(f)
			closure.Name = None
			result = closure
			
		# Handle quoted arguments.
		elif exp[0] == 'quote':
			def quotify(a):
				if isinstance(a, list) and a[0] == 'symbol':
					return ['quote', a[1]]
				elif isinstance(a, list) or isinstance(a, pyparsing.ParseResults):
					result = None
					for b in reversed(a):
						result = (quotify(b), result)
					return result
				else:
					return a

			result = quotify(exp[1])

		# Otherwise, it's an application.
		# The first argument must evaluate to a function.
		else:
			# Get the function, make sure it actually is a Schempy-created function.
			f = self.__Eval(exp[0], env, level + 1)
			if not isinstance(f, types.FunctionType):
				raise SchempyException('Attempted to apply non-procedure %s' % str(f))
			elif not 'SchempyFunction' in dir(f) or not f.SchempyFunction:
				raise SchempyException('Attempted to apply incorrectly created function %s' % str(f))

			# Give it a name if we had to look it up.
			if exp[0][0] == 'symbol' and not f.Name:
				f.Name = exp[0][1]
				
			# Check the argument counts.
			argCount = len(exp) - 1
			if f.CollectArgs and argCount < f.ArgCount:
				raise SchempyException("Incorrect number of arguments to %s, expected at least %d, got %d." % (f.Name, f.ArgCount, argCount))
			elif not f.CollectArgs and argCount != f.ArgCount:
				raise SchempyException("Incorrect number of arguments to %s, expected %d, got %d." % (f.Name, f.ArgCount, argCount))
				
			# Get the arguments, thunkify if requested.
			args = []
			for arg in exp[1:]:
				if f.Thunkify:
					args.append(Thunk(self.__Eval, arg, env, level + 1))
				else:
					args.append(self.__Eval(arg, env, level + 1))
					
			# Apply the function (finally) and return the result.
			result = apply(f, args)
			
		# Got the result, trace it?
		if self.Trace:
			for i in range(level):
				print '>',
			print '%s' % self.__tostr(result)
		
		# Return it in any case, all sorts of fun errors if you forget.
		return result

	def __tostr(self, exp):
		"""Stringify a result in Scheme style."""

		# Bool has to be before int because isinstance(True / False) is True

		if exp == None:
			return "()"
		elif isinstance(exp, bool):
			return '#t' if exp else '#f'
		elif isinstance(exp, int) or isinstance(exp, float):
			return str(exp)
		elif isinstance(exp, list) and exp[0] == 'quote':
			return exp[1]
 		elif isinstance(exp, str):
			return '"' + exp + '"'
		elif isinstance(exp, types.FunctionType):
			if 'Name' in dir(exp) and exp.Name:
				return '#<procedure %s>' % exp.Name
			else:
				return '#<procedure>'
		elif isinstance(exp, tuple):
			result = '(' + self.__tostr(exp[0])
			b = exp[1]
			while isinstance(b, tuple):
				result += ' ' + self.__tostr(b[0])
				b = b[1]
			if b == None:
				result += ')'
			else:
				result += ' . ' + self.__tostr(b) + ')'
			return result
		elif isinstance(exp, list) and exp[0] == 'symbol':
			return exp[1]
		elif isinstance(exp, list) or isinstance(exp, pyparsing.ParseResults):
			return '(' + ' '.join([self.__tostr(x) for x in exp]) + ')'
		else:
			# Remove from final code.
			raise SchempyException('Unkown type to __tostr: %s' % str(type(exp)))

