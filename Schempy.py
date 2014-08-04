import os
import sys
import types

from Environment import Environment
from SchempyException import SchempyException
from SchempySymbol import SchempySymbol
from SchempyParser import SchempyParser
from SchempyDot import SchempyDot

# Big todo list of firey doom!
# TODO: Proper tail recursion.
# TODO: Vectors
# TODO: Macros


def Stackless(f):
	import stackless
	
	def new_f(*args, **kwargs):
		def wrap(channel, f, args, kwargs):
			channel.send(f(*args, **kwargs))

		channel = stackless.channel()
		stackless.tasklet(wrap)(channel, f, args, kwargs)
		return channel.receive()
	
	new_f.__name__ = f.__name__
	new_f.__doc__ = f.__doc__	
	
	return new_f

class Schempy:
	"""The main body of Schempy."""

	def __init__(self):
		"""Initialize Schempy."""

		# Initialize everything
		self.Parser = SchempyParser()
		self.Environment = SchempyEnvironment()

		# Add functions the tie directly into the interpreter to Schempy.
		self.Environment['exit'] = lambda : self.__stop__()
		self.Environment['load'] = lambda f : self.__load__(f)
		self.Environment['env'] = lambda : self.Environment
		self.Environment['blah'] = lambda x, y : x + y
		
		# Load the global functions.
		self.__load__('global.py')
		#self.__load__('global.ss')
		
		# Wrap the environments, shadowing is allowed, overwriting is not.
		self.Environment = SchempyEnvironment(self.Environment)
		
		# Schempy is read to run!
		self.Running = True
		
	def REPL(self):
		"""Activate a Read-Eval-Print-Loop"""
		
		# Keep going until (exit) or (quit)
		while self.Running:
			line = ''
			
			# Read at least one line, until parens match.
			# TODO: Add scheme-like tab support (maybe?)
			lparens = 0
			rparens = 0
			print '\nSchempy>',
			while line == '' or lparens > rparens:
				if line != '': print '        ',
				line += raw_input('')
				lparens = line.count('(') + line.count('[')
				rparens = line.count(')') + line.count(']')
				
			# Got the input, try to evaluate it.
			try:
				results = self(line)
				for line in results:
					print line
					
			# Something broke, report the error.
			except SchempyException as ex:
				print '\nError: %s' % str(ex)

	def __stop__(self):
		"""Stop evaluating things."""
		
		self.Running = False		

	def __call__(self, s):
		"""Evaluate a string containing Schempy code."""

		# Parse the string into a list of Schempy expressions.
		exps = self.Parser(s)

		# Evaluate each expression.
		results = []
		for exp in exps:
			if not self.Running:
				break
			else:
				# Run the code, look for problems.
				try:
					result = self.__toscheme__(self.__eval__(exp))
					if result:
						results.append(result)
						
				# User requested stop.  Stop executing.
				except KeyboardInterrupt as e:
					self.Running = False
				
				# Always catch SchempyExceptions.
				except SchempyException as e:
					print 'Error: %s' % e
					
				# Display anything else.
				# TODO: Enable this in final version
				#except Exception as e:
				#	print 'Error: %s' % e
				
	
		# Return the result.
		return results
	
	@Stackless
	def __eval__(self, exp, env = None):
		"""Evaluate a Schempy expression."""
		
		# If we've stopped, stop.
		if not self.Running:
			return None
		
		# If no environment was passed, create one.
		# Wrap the global environment in a new level.
		if not env:
			env = self.Environment
		
		# Lookup symbols in the environment.
		if isinstance(exp, SchempySymbol):
			return env[exp]
		
		# TODO: Apply macros (this will be fun!)
		
		# Run applications.
		elif isinstance(exp, list):
			# Error handling for empty lists.
			if (exp == []):
				raise SchempyException('Invalid syntax ()')
			
			# Get the function and annotate it with the current evaluator and environment.
			# NOTE: Changes to the environment will be preserved at the current level.
			#       To create a new environment, wrap the current environment.
			rator = self.__eval__(exp[0])
			rator.Eval = self.__eval__
			rator.Env = env
			
			# Collect the arguments, evaluate them if delay was not requested
			if '__delay__' in dir(rator) and rator.__delay__:
				rands = exp[1:]
			else:
				rands = [self.__eval__(rand, env) for rand in exp[1:]]
	
			# Trace if requested.
			if 'Trace' in dir(rator) and rator.Trace:
				print rator.__name__ + self.__toscheme__(rands)

			# Evaluate, finally.
			return rator(*rands)
			
		# Everything else is a literal, return it directly.
		else:
			return exp
		
	def __load__(self, filename):
		"""Load a file (either Scheme or Python) into Schempy."""

		# Make sure the file exists.
		if not os.path.exists(filename):
			raise SchempyException('Unable to load %s, file does not exist.' % filename)
		path, ext = os.path.splitext(filename)
			
		# Check if it's Python or Scheme.
		# Load Scheme files.
		if ext in ('.ss', '.scm'):
			text = open(filename, 'r').read()
			results = self(text)
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
				if isinstance(f, types.FunctionType):
					self.Environment[f.__name__.lower()] = f
										
		# Break on any other file types.
		else:
			raise SchempyException('Unable to load %s, unknown file type.' % filename)
			
	def __toscheme__(self, exp):
		"""Convert an expression to Scheme-like syntax."""
		
		# Nothing to represent
		if exp == None:
			return ''
			
		# Procedures
		elif isinstance(exp, types.FunctionType):
			if exp.__name__ != '<procedure>':
				return '#<procedure %s>' % exp.__name__
			else:
				return '#<procedure>'
				
		# Symbols
		elif isinstance(exp, SchempySymbol):
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
		elif isinstance(exp, float):
			return '%f' % exp
		elif isinstance(exp, str):
			return '"%s"' % exp
		
		# Lists
		elif isinstance(exp, SchempyDot):
			return '.'
		elif isinstance(exp, list):
			return '(' + ' '.join([self.__toscheme__(subexp) for subexp in exp]) + ')'
			
		# Unknown types
		else:
			raise SchempyException('Unabled to convert to Scheme format: %s', exp)

if __name__ == '__main__':
	ss = Schempy()
	ss.REPL()
