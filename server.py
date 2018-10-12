import socket
import sys

def startServer(portno):
	sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	print(socket.gethostname())
	sock.bind(('',portno))
	sock.listen(5)
	while True :
		cli,addr = sock.accept()
		print('Got connection from ',addr)
		constr = 'Thank you '+str(addr)+' for connecting'
		cli.send(constr.encode())
		cli.close()

portno = int(input("Please Enter Port Number on which you want to Run Server : "))
startServer(portno)





	


