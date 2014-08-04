from Exceptions import StopException
from Decorators import Rename

@Rename('exit')
def _exit():
	'''Stop evaluating.'''
	
	raise StopException()