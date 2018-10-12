import socket
import math
import random
import subprocess
import os
import hashlib
import time
from publish import Publish
from mpcconst import MPCConst
from mpcconf import MPCConf
from numpy import matrix

def connectToParty(hostname,portno,msg,matrix):
	
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
		data = (msg).encode()
		print('Message : '+msg)
		sock.send(data)
		if msg == 'SSA' or msg == 'SSM':
			time.sleep(5)
			data = (matrix).encode()
			print('Matrix : '+msg)
			sock.send(data)

		

def matrixToString(matrix):
	ml = matrix.tolist()
	ans = ';'.join(','.join(str(y) for y in x) for x in ml)
	return ans




x = MPCConst(1672)

Amatrix = matrixToString(x.A)
Zmatrix = matrixToString(x.Z)

print(Amatrix)
print(Zmatrix)

#time.sleep(15)

connectToParty(MPCConf.hostname,MPCConf.party1Port, 'COM',Amatrix)
time.sleep(2)
connectToParty(MPCConf.hostname,MPCConf.party2Port, 'COM',Amatrix)
time.sleep(2)
connectToParty(MPCConf.hostname,MPCConf.party3Port, 'COM',Amatrix)

time.sleep(5)

connectToParty(MPCConf.hostname,MPCConf.party1Port, 'PK1',Amatrix)
connectToParty(MPCConf.hostname,MPCConf.party2Port, 'PK1',Amatrix)
connectToParty(MPCConf.hostname,MPCConf.party3Port, 'PK1',Amatrix)

time.sleep(15)

connectToParty(MPCConf.hostname,MPCConf.party1Port, 'PK2',Amatrix)
connectToParty(MPCConf.hostname,MPCConf.party2Port, 'PK2',Amatrix)
connectToParty(MPCConf.hostname,MPCConf.party3Port, 'PK2',Amatrix)

time.sleep(15)

connectToParty(MPCConf.hostname,MPCConf.party1Port, 'IN',Amatrix)
connectToParty(MPCConf.hostname,MPCConf.party2Port, 'IN',Amatrix)
connectToParty(MPCConf.hostname,MPCConf.party3Port, 'IN',Amatrix)

time.sleep(5)

connectToParty(MPCConf.hostname,MPCConf.party1Port, 'SSA',Amatrix)
connectToParty(MPCConf.hostname,MPCConf.party2Port, 'SSA',Amatrix)
connectToParty(MPCConf.hostname,MPCConf.party3Port, 'SSA',Amatrix)


time.sleep(25)

connectToParty(MPCConf.hostname,MPCConf.party1Port, 'SA12',Amatrix)
connectToParty(MPCConf.hostname,MPCConf.party2Port, 'SA12',Amatrix)
connectToParty(MPCConf.hostname,MPCConf.party3Port, 'SA12',Amatrix)
time.sleep(2)

connectToParty(MPCConf.hostname,MPCConf.party1Port, 'SM100',Amatrix)
connectToParty(MPCConf.hostname,MPCConf.party2Port, 'SM100',Amatrix)
connectToParty(MPCConf.hostname,MPCConf.party3Port, 'SM100',Amatrix)
time.sleep(2)

connectToParty(MPCConf.hostname,MPCConf.party1Port, 'SSM',Zmatrix)
connectToParty(MPCConf.hostname,MPCConf.party2Port, 'SSM',Zmatrix)
connectToParty(MPCConf.hostname,MPCConf.party3Port, 'SSM',Zmatrix)


time.sleep(150)


connectToParty(MPCConf.hostname,MPCConf.party1Port, 'ENC',Zmatrix)
connectToParty(MPCConf.hostname,MPCConf.party2Port, 'ENC',Zmatrix)
connectToParty(MPCConf.hostname,MPCConf.party3Port, 'ENC',Zmatrix)

time.sleep(20)

connectToParty(MPCConf.hostname,MPCConf.party1Port, 'DEC',Zmatrix)
connectToParty(MPCConf.hostname,MPCConf.party2Port, 'DEC',Zmatrix)
connectToParty(MPCConf.hostname,MPCConf.party3Port, 'DEC',Zmatrix)

time.sleep(15)