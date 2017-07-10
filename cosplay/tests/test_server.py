from cosplay.pkt import Packet
import cosplay.server
from cosplay.serial_port import SerialPort
import time
import sys

def test_server(port):
	sp = SerialPort()
	connected=False
	i=0
	while not connected and i<1000:
		connected = sp.connect_serial(port)
		i += 1
		time.sleep(0.1)
	if connected:
		print('Connected to /dev/pts/3')
	pkt = Packet(sp)
	pkt.send("Test string!")
	pkt.send(pkt.INS_check_for_sequences_on_server)
	assert pkt.receive(time_out=10000)==pkt.ANS_no

if __name__=="__main__":
	test_server(sys.argv[1])
