from Decorators import Syntax, Rename
import Evaluate
import Exceptions

def values(*args):
	'''Tests if something is an integer.'''
	
	return ['**values**'] + list(args)

@Syntax
@Rename('let-values')
def let_values(exp, env):
	'''Let values.'''
	
	# Check syntax.
	if len(exp) < 3:
		raise InvalidSyntaxException(exp)
		
	# Bind parts.
	kv_pairs = exp[1]
	bodies = exp[2:]
	
	# Bind variables.
	local_env = env.Extend()
	for kv_pair in kv_pairs:
		ks = kv_pair[0]
		value_exp = kv_pair[1]
		values = Evaluate.Evaluate(value_exp, env)
		
		# Possible problems.
		if not isinstance(values, list) or len(values) == 0 or values[0] != '**values**':
			raise InvalidSyntaxException(exp, 'Values used out of context')
		if len(ks) != len(values) - 1:
			raise InvalidSyntaxException(exp, 'Incorrect number of values to unpack, expected %d got %d' % (len(keys), len(values) - 1))

		# Bind the variables.
		for i in range(len(ks)):
			local_env[ks[i]] = Evaluate.Evaluate(values[i + 1], env)
	
	# Evalute the bodies.
	result = None
	for body in bodies:
		result = Evaluate.Evaluate(body, local_env)
	return result
