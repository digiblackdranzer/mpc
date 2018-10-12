import socket
import sys

def connectClient(hostname,portno):
	try:
		sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	except socket.error as err:
		print('socket creation failed with error %s' %(err))
	port = portno
	try:
		host_ip = socket.gethostbyname(hostname)
	except socket.gaierror:
		print('there was an error resolving the host')
		sys.exit()

	sock.connect((host_ip, port))
	print('the socket has successfully connected to server %s on port = %s' %(hostname,portno))
	data = sock.recv(1024).decode()
	print('Message from Server : ',data)

hostname = input("Please Enter Server Hostname : ")
portno = int(input("Please Enter Port Number on which you want to Connect Server : "))
connectClient(hostname,portno)