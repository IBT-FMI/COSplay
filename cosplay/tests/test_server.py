from cosplay.pkt import Packet
import cosplay.server
from cosplay.serial_port import SerialPort
import time, sys, os, errno

def test_pkt(port1, port2):
	print('Port 1: ',port1)
	sp1 = SerialPort()
	connected=False
	i=0
	while not connected and i<1000:
		connected = sp1.connect_serial(port1)
		i += 1
		time.sleep(0.1)
	if connected:
		print('Connected to {0}'.format(port1))
	pkt1 = Packet(sp1)
	print('Port 2: ',port2)
	sp2 = SerialPort()
	connected=False
	i=0
	while not connected and i<1000:
		connected = sp2.connect_serial(port2)
		i += 1
		time.sleep(0.1)
	if connected:
		print('Connected to {0}'.format(port2))
	pkt2 = Packet(sp2)

	pkt1.send("Test string!")
	s = pkt2.receive(time_out=200000)
	print(s)

def test_server(port):
	print('Port: ',port)
	sp = SerialPort()
	connected=False
	i=0
	while not connected and i<1000:
		connected = sp.connect_serial(port)
		i += 1
		time.sleep(0.1)
	if connected:
		print('Connected to {0}'.format(port))
	pkt = Packet(sp)
	pkt.send("Test string!")
	pkt.send(pkt.INS_check_for_sequences_on_server)
	answer = pkt.receive(time_out=200000)
	print('Answer: ',answer)
	assert answer==pkt.ANS_no
	try:
		os.makedirs(os.expanduser('~/.cosgen'))
	except OSError as e:
		if e.errno != errno.EEXIST:
			raise
	open(os.expanduser('~/.cosgen/sequence.tsv',a)).close()
	pkt.send(pkt.INS_check_for_sequences_on_server)
	answer = pkt.receive(time_out=200000)
	print('Answer: ',answer)
	assert answer==pkt.ANS_yes

if __name__=="__main__":
	test_pkt(sys.argv[1],sys.argv[2])
	test_server(sys.argv[1])
