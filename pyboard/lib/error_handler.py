import path as ospath
import uos

class ErrorHandler:
	def __init__(self, use_wo_server, pkt=None, storage_path=None):
		self.use_wo_server = use_wo_server
		if use_wo_server:
			self.msgstr = ''
			self.storage_path = storage_path
		else:
			self.pkt = pkt

	def send(self,s):
		"""
		Sends `s` to the server if connected.

		If the server is not connected `s` is stored and can be
		written to file using the `save` function.

		Parameters
		----------
		s : string
		    string containing error message
		"""
		if self.use_wo_server:
			self.msgstr = self.msgstr + s + '\n'

		else:
			self.pkt.send(s)

	def save(self):
		"""
		Save error messages to file.

		This function stores error message in a file named errorN.txt,
		where N is the number of the sequence that is currently delivered.

		Parameters
		----------
		s : string
		    string containing error message
		"""
		if not self.use_wo_server:
			return
		idx = 0
		while ospath.exists(self.storage_path + '/sequence' + str(idx) + '.tsv'):
			idx += 1
		with open(self.storage_path + '/errors'+str(idx)+'.txt','w+') as f:
			f.write(self.msgstr)
		self.msgstr = ''
