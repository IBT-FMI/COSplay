def cast(s):
	try:
		return float(s)
	except ValueError:
		return s

def loads(s):
	s = s.split('\n')
	matrix = [[cast(x) for x in s[i].split('\t')] for i in range(1,len(s))]
	head = s[0].split('\t')
	matrix.insert(0,head)
	return matrix

def load(file_obj):
	s = file_obj.read()
	return loads(s)

def dumps(matrix):
	s = '\t'.join(matrix[0])
	for i in range(1,len(matrix)):
		s = s + '\n'
		for l in range(len(matrix[i])-1):
			s = s + str(matrix[i][l]) + '\t'
		s = s + str(matrix[i][len(matrix[i])-1])
	return s

def dump(matrix,file_obj):
	file_obj.write(dumps(matrix))
