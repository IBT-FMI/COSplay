def cast(s):
	"""
	Cast string to float if possible.
	
	This functions casts a string to float if possible and returns
	the string otherwise.
	
	Parameters
	----------
	s : string
	    Input strings

	Returns
	-------
	float or string
	    Float number of string input s, if possible, s otherwise.
	"""
	try:
		return float(s)
	except ValueError:
		return s

def loads(s):
	"""
	Convert tsv formatted string into matrix.
	
	This function converts a 'Brain Image Data Structure' [BIDS] sequence tsv
	string into a matrix.
	
	Parameters
	----------
	s : string
	    String form BIDS sequence tsv file[BIDS].

	Returns
	-------
	2d array
	    First line contains names for columns.
	    First columns contains event numbers.
	"""
	s = s.split('\n')
	matrix = [[cast(x) for x in s[i].split('\t')] for i in range(1,len(s))]
	head = s[0].split('\t')
	matrix.insert(0,head)
	return matrix

def load(file_obj):
	"""
	Load BIDS sequence tsv file [BIDS].

	This function converts a BIDS sequence tsv file to a matrix.

	Parameters
	----------
	file_obj : file object
	    File object of BIDS sequence tsv file [BIDS].

	Returns
	-------
	2d array
	    First line contains names for columns.
	    First columns contains event numbers.
	"""
	s = file_obj.read()
	return loads(s)

def dumps(matrix):
	"""
	Serialize `matrix` to a tsv formatted string.

	Parameters
	----------
	matrix : 2d array
	    Input matrix.

	Returns
	-------
	string
	    tsv formatted string.
	"""
	s = '\t'.join(matrix[0])
	for i in range(1,len(matrix)):
		s = s + '\n'
		for l in range(len(matrix[i])-1):
			s = s + str(matrix[i][l]) + '\t'
		s = s + str(matrix[i][len(matrix[i])-1])
	return s

def dump(matrix,file_obj):
	"""
	Serialize `matrix` as a tsv formatted stream to `file_obj`.

	This function converts a matrix into a tsv formatted string and stores it in a file.

	Parameters
	----------
	matrix : 2d array
	    Input matrix.
	file_obj : file_obj
	    A .write()-supporting file-like object.
	"""

	file_obj.write(dumps(matrix))
