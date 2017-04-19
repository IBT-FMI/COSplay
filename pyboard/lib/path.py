import uos

def exists(path):
	try:
		mode = uos.stat(path)
		return True
	except OSError:
		return False
