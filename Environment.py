import os
import sys
import types

import Exceptions
import Procedure
import Evaluate
import Schemify
import Parser
import Syntax

class Environment:
	'''Represents a current environment in Schempy.'''

	def __init__(self, base = None):
		'''Create a new environment with a base environment. '''

		self.Base = base
		self.Vars = {}

	def __getitem__(self, key):
		'''Get an item from this environment.'''

		if key in self.Vars:
			return self.Vars[key]
		elif self.Base:
			return self.Base[key]
		else:
			raise Exceptions.SchempyException('Unbound variable: %s' % key)

	def __setitem__(self, key, val):
		'''Set an item in this environment.'''

		self.Vars[key] = val
		
	def Extend(self):
		'''Create a new, extended environment (for lambdas and the like).'''
		
		return Environment(self)
	
	def Import(self, module_name):
		'''Import a python package.'''
		
		# Load the file as a module.
		sys.path += os.getcwd()
		newModule = __import__(module_name)
		sys.path = sys.path[:-1]
		
		# Look through the file, load any functions.
		for fname in dir(newModule):
			f = newModule.__dict__.get(fname)
			if isinstance(f, types.FunctionType):
				# Load syntax functions.
				if 'Syntax' in dir(f) and f.Syntax:
					self[f.__name__.lower()] = Syntax.Syntax(f)
			
				# Load procedures.
				else:
					self[f.__name__.lower()] = Procedure.Procedure(f)
		
	def Load(self, filename):
		'''Load a file (scheme or python) into the environment.'''
		
		# Make sure the file exists.
		if not os.path.exists(filename):
			raise Exceptions.SchempyException('Unable to load %s, file does not exist.' % filename)
		path, ext = os.path.splitext(filename)
			
		# Check if it's Python or Scheme.
		# Load Scheme files.
		if ext in ('.ss', '.scm'):
			parse = Parser.Parser()
			text = open(filename, 'r').read()
			exps = parse(text)
			for exp in exps:
				result = Schemify.Schemify(Evaluate.Evaluate(exp, self))
				if result:
					print result
		
		# Load Python files.
		elif ext in ('.py', ):
			# Use self.Import
			self.Import(path)
										
		# Break on any other file types.
		else:
			raise Exceptions.SchempyException('Unable to load %s, unknown file type.' % filename)
		
	def __str__(self):
		'''Stringify the environment.'''
		
		result = '[env ' + ', '.join([Schemify.Schemify(k) + ':' + Schemify.Schemify(v) for k, v in self.Vars.items()])
		if self.Base:
			result += ' ' + str(self.Base)
		result += ']'
		return result
		
	def __repr__(self):
		'''Return a representation of the environment.'''
		
		return str(self)
