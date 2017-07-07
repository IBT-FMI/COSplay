from cosplay.pkt import Packet
import cosplay.server
from cosplay.serial_port import SerialPort

def test_server():
	sp = SerialPort()
	sp.connect_serial('/dev/pts/3')
	pkt = Packet(sp)
	pkt.send("Test string!")
	pkt.send(pkt.INS_check_for_sequences_on_server)
	assert pkt.receive()==pkt.ANS_no

if __name__=="__main__":
	test_server()
