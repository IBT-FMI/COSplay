def cast(s):
"""
Cast string to float if possible.

This functions casts a string to float if possible and returns
the string otherwise.

Parameters
----------
s : string
    input string

Retruns
-------
out : float or string
    Float number of string input s, if possible, s otherwise.
"""
	try:
		return float(s)
	except ValueError:
		return s

def loads(s):
"""
Convert tsv formated string into matrix.

This function converts a BIDS sequence tsv string to a matrix.

Parameters
----------
s : string
    string form BIDS sequence tsv file[BIDS]

Retruns
-------
out : 2d array
    First line contains names for columns.
    First columns contains event numbers.

References
----------
.. [BIDS] Brain Imaging Data Structure Specification
          (http://bids.neuroimaging.io/bids_spec1.0.1.pdf)
"""
	s = s.split('\n')
	matrix = [[cast(x) for x in s[i].split('\t')] for i in range(1,len(s))]
	head = s[0].split('\t')
	matrix.insert(0,head)
	return matrix

def load(file_obj):
"""
Load BIDS sequence tsv file[BIDS].

This function converts a BIDS sequence tsv file to a matrix.

Parameters
----------
file_obj : file object
    file_obj of BIDS sequence tsv file[BIDS]

Retruns
-------
out : 2d array
    First line contains names for columns.
    First columns contains event numbers.

References
----------
.. [BIDS] Brain Imaging Data Structure Specification
          (http://bids.neuroimaging.io/bids_spec1.0.1.pdf)
"""
	s = file_obj.read()
	return loads(s)

def dumps(matrix):
"""
Serialize matrix to a tsv formated string.

Parameters
----------
matrix : 2d array
    input matrix

Retruns
-------
out : string
    tsv formated string
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
Serialize matrix as a tsv formated stream to file_obj.

This function converts a matrix into a tsv formated string and stores it in a file.

Parameters
----------
matrix : 2d array
    input matrix
file_obj : file_obj
    a .write()-supporting file-like object
"""

	file_obj.write(dumps(matrix))
