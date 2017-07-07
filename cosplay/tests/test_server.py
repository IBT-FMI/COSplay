import os, pty, serial, thread
from cosplay.pkt import Packet
import cosplay.server
from cosplay.serial_port import SerialPort

def main():
	sp = SerialPort()
	sp.connect_serial('/dev/pts/3')
	pkt = Packet(sp)
	pkt.send("Test string!")
	pkt.send(pkt.INS_check_for_sequences_on_server)
	assert pkt.receive()==pkt.ANS_no
	#pkt.send()
	

#def main():
#	s = socket.socket(socket.AF_INET, socket.SOCK_STEAM)
#	s.setsocketopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#	s.bind(('127.0.0.1',7788))
#	
#	while True:
#		s.listen(1)
#		conn, addr = s.accept()
#		sp = SocketPort(conn)
#		pkt = Packet(sp)
#		pkt.send("Test string!")
#		pkt.send(pkt.INS_check_for_sequences_on_server)
#		assert pkt.receive()==pkt.ANS_no
#		#pkt.send()
		

if __name__=="__main__":
	main()
