import path as ospath

class error_handler:
	def __init__(self, use_wo_server, pkt=None, storage_path=None):
		self.use_wo_server = use_wo_server
		if use_wo_server:
			self.storage_path = storage_path
		else:
			self.pkt = pkt

	def send(self,s):
		"""
		Store error message in file or send it to server if connected.

		This function stores an error message in a file named errorN.txt,
		where N is the number of the sequence that is currently delivered.

		Parameters
		----------
		s : string
		    string containing error message
		"""
		if self.use_wo_server:
			path = self.storage_path + '/sequence'
			idx = 0
			while ospath.exists(path + str(idx)):
				idx += 1
			with open(self.storage_path + '/errors'+str(idx)+'.txt','w+') as f:
				print(s,f)

		else:
			self.pkt.send(s)
