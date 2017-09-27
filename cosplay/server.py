import time
import argparse
import os
import os.path
import glob
import signal
import serial

try:
	from cosplay import tsv
	from cosplay import serial_port
	from cosplay.pkt import Packet
except ImportError:
	import tsv
	import serial_port
	from pkt import Packet

keep_running = True


def signal_handler_end_program(signal, frame):
	global keep_running
	keep_running = False

def find_current_scan_dir(vendor):
	"""
	Find directory of current scan.

	This function finds the scan directory with the most
	recent inode change time of the fid file.

	Parameters
	----------
	vendor : string
	    Name of the MRI vendor, currently only Bruker
	    is supported.

	Returns
	-------
	 string
	    Path to current scan directory.
	"""
	if vendor == 'bruker':
		general_directory = glob.glob('/opt/PV*/data/mri/')
		if len(general_directory)>1:
			raise RuntimeError('Multiple versions of ParaVision found. List of folders found: ' + str(general_directory))
		elif len(general_directory) == 0:
			raise RuntimeError('No directory found in /opt/PV*/data/mri/. Specify path where the delivered sequences are stored using the --storage_path flag.')
		return max(glob.iglob(general_directory[0] + '*/*/fid'), key = os.path.getctime)[:-3]   # :-3 removes the fid (which is one of the files the data from the scanner is written to)
	raise ValueError('Finding standard data path is not supported for {0} systems.'.format(vendor))

def process_message(obj,error_msgs):
	"""
	Add obj to `error_msgs` if it is an error message.

	Parameters
	----------
	obj : string
	    Input message.
	error_msgs : string
	    Already accumulated error messages.

	Returns
	-------
	string
	    updated `error_msgs`
	"""
	print(obj + '\n')
	if obj[:6] == 'Missed':
		return error_msgs + obj + '\n'
	return error_msgs

def save_sequence(obj, storage_path, error_msgs, vendor, verbose=0):
	"""
	Save sequence in `storage_path`.

	This function saves a sequence and error messages in two separate files.
	If `storage_path` is None, the files are saved in the most recent scan
	directory (see 'find_current_scan_dir').

	Parameters
	----------
	obj : 2d matrix
	    Sequence.
	storage_path : string
	    Path to directory, where files shall be stored. If it is None, the
	    most recent scan directory is used.
	error_msgs : string
	    String containing error messages. Is stored in same directory as
	    the sequence.
	vendor : string
	    Name of MRI vendor.
	verbose : int, optional
	    If 'verbose' is larger than 1, the sequence is printed to the screen.
	    Default is 0.
	"""
	if type(obj) != list:
		raise TypeError('save_sequence only stores sequences in dictionary format.')
	if verbose > 1:
		print('Received sequence:\n' + str(obj))
	if storage_path is None:
		path = find_current_scan_dir(vendor)
		with open(path+'sequence.tsv','w+') as fp:
			tsv.dump(obj,fp)
			print('Sequence saved as {0}'.format(path+'sequence.tsv\n'))
		if error_msgs != '':
			with open(path+'sequence_errors.txt','w+') as fp:
				try:
					eval('print(error_msgs,file=fp)')
				except SyntaxError:
					print >>fp, error_msgs
				print('Error messages saved as {0}'.format(path+'errors.txt\n'))
	else:
		file_idx = 0
		while os.path.exists(storage_path+'sequence'+str(file_idx)+'.tsv'):
			file_idx += 1
		with open(storage_path+'sequence'+str(file_idx)+'.tsv','w+') as fp:
			tsv.dump(obj,fp)
			print('Sequence saved as {0}'.format(storage_path+'sequence'+str(file_idx)+'.tsv\n'))
			if error_msgs != '':
				with open(storage_path+'sequence_errors'+str(file_idx)+'.txt','w+') as fp:
					try:
						eval('print(error_msgs,file=fp)')
					except SyntaxError:
						print >>fp, error_msgs
					print('Error messages saved as {0}\n'.format(storage_path+'errors'+str(file_idx)+'.txt'))

def listdir_nohidden(path):
	"""
	List all entries in `path` excluding hidden ones.

	This function implements the same functionality as `os.listdir`
	but ignores hidden entires.

	Parameters
	----------
	path : string
	    Path to directory

	Returns
	-------
	list
	    List of all non-hidden entries in the directory.
	"""
	for f in os.listdir(path):
		if not f.startswith('.'):
			yield f

def check_for_sequences(sequences_arg=None):
	"""
	Try to find sequences.

	This function returns a list of paths to all files ending with
	'.tsv' in `sequence_arg`. Shell-style wildcards can be used.
	sequences_arg can be directories, files or a mixture of both.
	Directories are searched non-recursively on the first level.
	If no `sequence_arg` is specified, the default location of COSgen is
	used.

	Parameters
	----------
	sequences_arg : string, optional
	    Path to sequence files, can be None.

	Returns
	-------
	list
	    List of paths to sequence files. None if no sequences were
	    found.
	"""
	if sequences_arg is not None:

		sequences_paths = glob.glob(os.path.expanduser(sequences_arg))
		extension = []
		for p in sequences_paths:
			if os.path.isdir(p):
				extension.extend([os.path.join(p,s) for s in listdir_nohidden(p)])
		sequences_paths.extend(extension)
		i = 0
		while i < len(sequences_paths):
			p = sequences_paths[i]
			if os.path.isdir(p):
				sequences_paths.remove(p)
				continue
			if not p.endswith('.tsv'):
				sequences_paths.remove(p)
				continue
			i += 1

		if len(sequences_paths) == 0:
			print('There are no sequences in {0}.\n'.format(sequences_arg))
		else:
			return sequences_paths
	#TODO find newest sequences generated with cosgen
	sequences_paths = glob.glob(os.path.expanduser('~/.cosgen/sequence*.tsv'))
	if len(sequences_paths) >= 1:
		print('Found sequences on computer!\n')
		return sequences_paths
	return None

def ask_user():
	"""
	Ask user whether sequences on server or microcontroller shall
	be used.

	Returns
	-------
	bool
	    True if sequences on server shall be used, False otherwise.
	"""
	while True:
		try:
			var = raw_input('Shall the sequences on the computer be used instead of the sequences on the pyboard? (y/n)')
		except NameError:
			var = input('Shall the sequences on the computer be used instead of the sequences on the pyboard? (y/n)')
		if var == 'y':
			return True
		elif var == 'n':
			return False
		print('"{0}" is not a valid answer. Try again!'.format(var))

def send_sequences(sequences_paths,pkt,verbose):
	"""
	Send sequences to microcontroller.

	Parameters
	----------
	sequences_paths : list
	    List of paths (strings) to sequences that are sent.
	pkt : cosplay.pkt Packet object
	    Object that sends the sequences.
	verbose : int
	    If larger than 1, print path to every sequence sent.
	    If larger than 2, print every sequence sent.
	"""
	if sequences_paths is not None:
		print('sending {0} sequences\n'.format(len(sequences_paths)))
		for path in sequences_paths:
			with open(path) as data_file:
				seq = tsv.load(data_file)
				pkt.send(seq)
			if verbose >= 1:
				print('Sequence {0} sent to board\n'.format(path))
			elif verbose >= 2:
				print('Sent sequences:\n' + str(seq))
	else:
		print('sequences_paths contains no sequences. No sequences were sent!\n')
	pkt.send(pkt.ANS_no) #Indicates that all sequences have been sent

def connect(port_name=None):
	"""
	Establish connection to pyboard.

	This function tries to connect to `port_name`. If `port_name`
	is None, tries to connect to the first serial port with a
	maching VID:PID for the MicroPython Pyboard.

	Parameters
	----------
	port_name : string, optional
	    Name of port the microcontroller is connected to. If None,
	    tries to automatically detected port and connect.
	    Default is None.

	Returns
	-------
	port : `cosplay.serial_port.SerialPort` object
	    Port object that is connected. None if no connection could be
	    establish.
	"""
	port = serial_port.SerialPort()
	connected = False

	if port_name is not None:
		print('Trying to connect to {0}...'.format(port_name))
		i = 0
		while not connected and i < 100 and keep_running:
			connected = port.connect_serial(port_name)
			i += 1
			time.sleep(0.1)
		if not connected:
			print('Could not connect to {0}. Trying to auto connect...'.format(port_name))

	print('Searching port...')
	while not connected and keep_running:
		port_name = serial_port.autoscan()
		if port_name is not None:
			connected = port.connect_serial(port_name)
	if not connected:
		return None
	print('Connection to {0} established.\n'.format(port_name))
	return port


def main(verbose, vendor, port_name, sequences, storage_path=None):
	"""
	Main function running on server.

	This function constantly tries to receive data from pyboard.
	It acts according to the instructions received from the board.
	Exit this function by pressing CTRL-C.

	Parameters
	----------
	verbose : int
	    Verbosity level.
	vendor : string
	    Vendor of the MRI scanner.
	port_name : string
	    Port name.
	sequences : string
	    Path to sequences (can include wildcards).
	storage_path : string
	    String to storage location for delivered sequences.
	"""
	sequences_paths = None			#List with all paths to all sequences that will be sent to the microcontroller if requested

	if storage_path is None:
		find_current_scan_dir(vendor)			#this checks if the path can be found to notify the user of potential problems before they start the experiment
		storage_path = None
	else:
		if not os.path.isdir(storage_path):
			raise ValueError('No directory {0} exists.'.format(storage_path))
		if storage_path[-1] != '/':		#this ensures the path ends with /
			storage_path = storage_path + '/'



	error_msgs = ''		#stores error messages that occurer while delivering one sequence

	signal.signal(signal.SIGINT, signal_handler_end_program)
	print('\nPress Ctrl+c when you are done to close the program.\n')

	while keep_running:
		try:
			port = connect(port_name)

			if port is None:
				continue

			if verbose >= 2:
				pkt = Packet(port,show_packets=True)
			else:
				pkt = Packet(port)

			message_type = None
			try:
				message_type = unicode		#str is unicode in Python 3
			except NameError:
				message_type = str

			while keep_running:
				obj = pkt.receive(time_out=2)
				if obj == None:
					continue
				if type(obj) == message_type:
					error_msgs = process_message(obj,error_msgs)
				elif type(obj) == list:
					save_sequence(obj,storage_path,error_msgs,vendor,verbose)
				elif obj == pkt.INS_check_for_sequences_on_server:
					sequences_paths = check_for_sequences(sequences)
					if sequences_paths is None:
						pkt.send(pkt.ANS_no)
					else:
						pkt.send(pkt.ANS_yes)
					print('Sequences found on computer:')
					print(sequences_paths)
				elif obj == pkt.INS_ask_user:
					answer = ask_user()
					if answer == True:
						pkt.send(pkt.ANS_yes)
					else:
						pkt.send(pkt.ANS_no)
				elif obj == pkt.INS_send_sequences:
					send_sequences(sequences_paths,pkt,verbose)
				else:
					print('\n\nMicrocontroller sent unrecognised instruction of type {0}! {1}\n\n'.format(type(obj),str(obj)))
			port.close_serial()
		except serial.serialutil.SerialException:
			print('Serial connection interrupted\n')
			port_name = None

