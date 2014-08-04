import os

files = [
	'environment.py',
	'lambda.py',
	'mathematical.py',
	'logical.py',
	'lists.py',
	'predicates.py',
	'control.py',
	'values.py',
]

for file in files:
	execfile(os.path.join('globals', file))