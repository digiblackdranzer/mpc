import math
import random
import subprocess
import os
import hashlib
import socket
import sys
import time
import numpy as np
from publish import Publish
from mpcconf import MPCConf
from numpy import matrix
from mpcconst import MPCConst
from decryption import Decryption


class Party(object) :

	def fastExponentiation(self,e,r,p):
		res = 1
		e = e % p
		while (r > 0) :
			if ((r & 1) == 1) :
				res = (res * e) % p
			r = r >> 1
			e = (e * e) % p
		return res

	
	def modInverse(self,r,p):

		m0 = p
		y = 0
		x = 1
		if (p == 1) :
			return 0
		while (r > 1) :
			q = r // p
			t = p
			p = r % p
			r = t
			t = y
			y = x - q * y
			x = t
		if (x < 0) :
			x = x + m0
		return x

	def inversematrix(self,m, q):
		det = np.linalg.det(m)
		ans = ( m.I*det*self.modInverse(det,q))%q
		ans = np.asarray(ans)	
		for i in range(len(ans)):
			for j in range(len(ans)):
				ans[i][j] = int(round(ans[i][j]))
		return matrix(ans)
		

	def getShares(self):

		line = subprocess.check_output(['tail','-7','commonmpc.txt'])	
		lines = str(line.decode()).strip().split('\n')
		
		tokens = str(lines[1]).strip().split(':')
		tokenp = str(lines[0]).strip().split(':')
		share1 = [int(tokens[2]),int(tokens[4],16),tokenp[4]+tokens[0]+':'+tokens[1]+':'+tokens[2]+tokens[3]]

		tokens = str(lines[2]).strip().split(':')
		tokenp = str(lines[1]).strip().split(':')
		share2 = [int(tokens[2]),int(tokens[4],16),tokenp[4]+tokens[0]+':'+tokens[1]+':'+tokens[2]+tokens[3]]
		
		tokens = str(lines[3]).strip().split(':')
		tokenp = str(lines[2]).strip().split(':')
		share3 = [int(tokens[2]),int(tokens[4],16),tokenp[4]+tokens[0]+':'+tokens[1]+':'+tokens[2]+tokens[3]]
		
		tokens = str(lines[4]).strip().split(':')
		tokenp = str(lines[3]).strip().split(':')
		share4 = [int(tokens[2]),int(tokens[4],16),tokenp[4]+tokens[0]+':'+tokens[1]+':'+tokens[2]+tokens[3]]
		
		tokens = str(lines[5]).strip().split(':')
		tokenp = str(lines[4]).strip().split(':')
		share5 = [int(tokens[2]),int(tokens[4],16),tokenp[4]+tokens[0]+':'+tokens[1]+':'+tokens[2]+tokens[3]]
		
		tokens = str(lines[6]).strip().split(':')
		tokenp = str(lines[5]).strip().split(':')
		share6 = [int(tokens[2]),int(tokens[4],16),tokenp[4]+tokens[0]+':'+tokens[1]+':'+tokens[2]+tokens[3]]

		return [share1,share2,share3,share4,share5,share6]

	def createCommit(self):

		if self.name == MPCConf.party1Name:
			line = subprocess.check_output(['tail','-1','commonmpc.txt'])
		if self.name == MPCConf.party2Name:
			line = subprocess.check_output(['tail','-2','commonmpc.txt'])
		if self.name == MPCConf.party3Name:
			line = subprocess.check_output(['tail','-3','commonmpc.txt'])	

		lines = str(line).strip().split('\n')
		tokens = str(lines[0]).strip().split(':')
		self.chosenPrime = int(tokens[0][2:])
		print(self.chosenPrime)
		self.g = int(tokens[1])
		h = int(tokens[2])
		x = int(tokens[3])
		print(self.chosenPrime)
		print(self.g)
		print(h)
		print(x)
		self.s = random.randint(1,self.chosenPrime)
		self.r = random.randint(1,self.chosenPrime)
		self.y = random.randint(1,self.chosenPrime)		
		C = (self.g*self.s+h*self.r+x*self.y)%self.chosenPrime
		return C

	def getPK1(self):
	
		line = subprocess.check_output(['tail','-2','commonmpc.txt'])
		lines = str(line).strip().split('\n')
		tokens = str(lines[0]).strip().split(':')
		return  int(tokens[2])

	def getPK2(self):
	
		line = subprocess.check_output(['tail','-1','commonmpc.txt'])
		lines = str(line).strip().split('\n')
		tokens = str(lines[0]).strip().split(':')
		return  int(tokens[2])
	
	def getS(self):
	
		line = subprocess.check_output(['tail','-1','commonmpc.txt'])
		lines = str(line).strip().split('\n')
		tokens = str(lines[0]).strip().split(':')
		return  int(tokens[2])

	def getSK(self):
	
		line = subprocess.check_output(['tail','-1','commonmpc.txt'])
		lines = str(line).strip().split('\n')
		tokens = str(lines[0]).strip().split(':')
		return  int(tokens[2])	




	def connectToParty(self,hostname,portno):
	
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
		return sock

		
	def startServer(self,portno):
	
		sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		print(socket.gethostname())
		sock.bind(('',portno))
		sock.listen(5)
		while True :
			cli,addr = sock.accept()
			print('Got connection from ',addr)
			constr = 'Thank you '+str(addr)+' for connecting at Party '+self.name
			cli.send(constr.encode())


			data = cli.recv(1024).decode()
			print('Data received : '+str(data))



			if data == 'COM':
				commit = self.createCommit()
				publishString = self.name+':'+str(commit)
				Publish(publishString) 



			if data == 'PK1':
				#self.generatePK1()
				
				if self.name == MPCConf.party1Name :
					time.sleep(5)

					r = random.randint(1,self.chosenPrime)
					b = (r+self.s*self.g)%self.chosenPrime
					socksend = self.connectToParty(MPCConf.hostname,MPCConf.party2Port)
					socksend.send(str(b).encode())


					#time.sleep(10)
					cli3,addr3 = sock.accept()
					print('Got connection from ',addr3)
					constr = 'Thank you '+str(addr3)+' for connecting at Party '+self.name
					cli3.send(constr.encode())

					key = (int(cli3.recv(1024).decode())-r)%self.chosenPrime
					print('Data Received :'+str(key))
					Publish(MPCConf.party1Name+':'+'PK1'+':'+str(key))
					cli3.close()

				if self.name == MPCConf.party2Name:
					#time.sleep(5)
					cli1,addr1 = sock.accept()
					print('Got connection from ',addr1)
					constr = 'Thank you '+str(addr1)+' for connecting at Party '+self.name
					cli1.send(constr.encode())

					a = (int(cli1.recv(1024).decode()))
					print('Data Received :'+str(a))
					b = (a+self.s*self.g)%self.chosenPrime
					socksend = self.connectToParty(MPCConf.hostname,MPCConf.party3Port)
					socksend.send(str(b).encode())

				if self.name == MPCConf.party3Name:
					#time.sleep(10)
					cli2,addr2 = sock.accept()
					print('Got connection from ',addr2)
					constr = 'Thank you '+str(addr2)+' for connecting at Party '+self.name
					cli2.send(constr.encode())
					time.sleep(5)
					a = (int(cli2.recv(1024).decode()))
					print('Data Received :'+str(a))
					b = (a+self.s*self.g)%self.chosenPrime
					socksend = self.connectToParty(MPCConf.hostname,MPCConf.party1Port)
					socksend.send(str(b).encode())



			if data == 'PK2':
				#self.generatePK1()
				self.e = (self.g*self.g)%self.chosenPrime
				
				if self.name == MPCConf.party1Name :
					time.sleep(5)

					r = random.randint(1,self.chosenPrime)
					b = (r*self.fastExponentiation(self.e,self.r,self.chosenPrime))%self.chosenPrime
					socksend = self.connectToParty(MPCConf.hostname,MPCConf.party2Port)
					socksend.send(str(b).encode())


					#time.sleep(10)
					cli3,addr3 = sock.accept()
					print('Got connection from ',addr3)
					constr = 'Thank you '+str(addr3)+' for connecting at Party '+self.name
					cli3.send(constr.encode())

					key = (int(cli3.recv(1024).decode())*self.modInverse(r,self.chosenPrime))%self.chosenPrime
					print('Data Received :'+str(key))
					Publish(MPCConf.party1Name+':'+'PK2'+':'+str(key))
					cli3.close()

				if self.name == MPCConf.party2Name:
					#time.sleep(5)
					cli1,addr1 = sock.accept()
					print('Got connection from ',addr1)
					constr = 'Thank you '+str(addr1)+' for connecting at Party '+self.name
					cli1.send(constr.encode())

					a = (int(cli1.recv(1024).decode()))
					print('Data Received :'+str(a))
					b = (a*self.fastExponentiation(self.e,self.r,self.chosenPrime))%self.chosenPrime
					socksend = self.connectToParty(MPCConf.hostname,MPCConf.party3Port)
					socksend.send(str(b).encode())

				if self.name == MPCConf.party3Name:
					#time.sleep(10)
					cli2,addr2 = sock.accept()
					print('Got connection from ',addr2)
					constr = 'Thank you '+str(addr2)+' for connecting at Party '+self.name
					cli2.send(constr.encode())

					time.sleep(5)
					a = (int(cli2.recv(1024).decode()))
					print('Data Received :'+str(a))
					b = (a*self.fastExponentiation(self.e,self.r,self.chosenPrime))%self.chosenPrime
					socksend = self.connectToParty(MPCConf.hostname,MPCConf.party1Port)
					socksend.send(str(b).encode())



			if data == 'IN':
				self.x = 3#random.randint(0,self.chosenPrime)



			if data == 'SSA':
				#self.generatePK1()
				r1 = random.randint(0,self.chosenPrime)
				r2 = random.randint(0,self.chosenPrime)
				r3 = random.randint(0,self.chosenPrime)
				r4 = random.randint(0,self.chosenPrime)
				r5 = random.randint(0,self.chosenPrime)

				v = matrix([[self.x],[r1],[r2],[r3],[r4],[r5]])

				data = cli.recv(1024).decode()
				print('Data received : '+data)
				AAAA = np.matrix(data)
				shares =  AAAA * v
				shares = [int(shares[0][0]%self.chosenPrime),
							int(shares[1][0]%self.chosenPrime),
							int(shares[2][0]%self.chosenPrime),
							int(shares[3][0]%self.chosenPrime),
							int(shares[4][0]%self.chosenPrime),
							int(shares[5][0]%self.chosenPrime)]
				print('Shares : ',shares)
				if self.name == MPCConf.party1Name :
					time.sleep(5)

					P1S1 = shares[0]
					P1S2 = shares[1]

					socksend2 = self.connectToParty(MPCConf.hostname,MPCConf.party2Port)
					socksend2.send(str(shares[2]).encode())
					time.sleep(3)					
					socksend2.send(str(shares[3]).encode())

					socksend3 = self.connectToParty(MPCConf.hostname,MPCConf.party3Port)
					socksend3.send(str(shares[4]).encode())
					time.sleep(3)					
					socksend3.send(str(shares[5]).encode())

					#time.sleep(10)
					cli2,addr2 = sock.accept()
					print('Got connection from ',addr2)
					constr = 'Thank you '+str(addr2)+' for connecting at Party '+self.name
					cli2.send(constr.encode())

					P2S1 = (int(cli2.recv(1024).decode()))
					P2S2 = (int(cli2.recv(1024).decode()))

					cli2.close()

					#time.sleep(10)
					cli3,addr3 = sock.accept()
					print('Got connection from ',addr3)
					constr = 'Thank you '+str(addr3)+' for connecting at Party '+self.name
					cli3.send(constr.encode())

					P3S1 = (int(cli3.recv(1024).decode()))
					P3S2 = (int(cli3.recv(1024).decode()))

					cli3.close()

				if self.name == MPCConf.party2Name:
					
					P2S3 = shares[2]
					P2S4 = shares[3]

					#time.sleep(10)
					cli1,addr1 = sock.accept()
					print('Got connection from ',addr1)
					constr = 'Thank you '+str(addr1)+' for connecting at Party '+self.name
					cli1.send(constr.encode())

					P1S3 = (int(cli1.recv(1024).decode()))
					P1S4 = (int(cli1.recv(1024).decode()))

					cli1.close()

					socksend1 = self.connectToParty(MPCConf.hostname,MPCConf.party1Port)
					socksend1.send(str(shares[0]).encode())
					time.sleep(3)					
					socksend1.send(str(shares[1]).encode())

					socksend3 = self.connectToParty(MPCConf.hostname,MPCConf.party3Port)
					socksend3.send(str(shares[4]).encode())
					time.sleep(3)					
					socksend3.send(str(shares[5]).encode())

					

					#time.sleep(10)
					cli3,addr3 = sock.accept()
					print('Got connection from ',addr3)
					constr = 'Thank you '+str(addr3)+' for connecting at Party '+self.name
					cli3.send(constr.encode())

					P3S3 = (int(cli3.recv(1024).decode()))
					P3S4 = (int(cli3.recv(1024).decode()))

					cli3.close()

				if self.name == MPCConf.party3Name:
					
					P3S5 = shares[4]
					P3S6 = shares[5]

					#time.sleep(10)
					cli1,addr1 = sock.accept()
					print('Got connection from ',addr1)
					constr = 'Thank you '+str(addr1)+' for connecting at Party '+self.name
					cli1.send(constr.encode())

					P1S5 = (int(cli1.recv(1024).decode()))
					P1S6 = (int(cli1.recv(1024).decode()))

					cli1.close()

					#time.sleep(10)
					cli2,addr2 = sock.accept()
					print('Got connection from ',addr2)
					constr = 'Thank you '+str(addr2)+' for connecting at Party '+self.name
					cli2.send(constr.encode())

					P2S5 = (int(cli2.recv(1024).decode()))
					P2S6 = (int(cli2.recv(1024).decode()))

					cli2.close()

					socksend1 = self.connectToParty(MPCConf.hostname,MPCConf.party1Port)
					socksend1.send(str(shares[0]).encode())
					time.sleep(3)					
					socksend1.send(str(shares[1]).encode())

					socksend2 = self.connectToParty(MPCConf.hostname,MPCConf.party2Port)
					socksend2.send(str(shares[2]).encode())
					time.sleep(3)					
					socksend2.send(str(shares[3]).encode())



			if data == 'SA12':
				
				if self.name == MPCConf.party1Name :

					AS1 = (P1S1 + P2S1)%self.chosenPrime
					AS2 = (P1S2 + P2S2)%self.chosenPrime

					print('Share 1 of Addition : ',AS1)
					print('Share 2 of Addition : ',AS2)

				if self.name == MPCConf.party2Name:
				
					AS3 = (P1S3 + P2S3)%self.chosenPrime
					AS4 = (P1S4 + P2S4)%self.chosenPrime

					print('Share 3 of Addition : ',AS3)
					print('Share 4 of Addition : ',AS4)

				if self.name == MPCConf.party3Name:
					
					AS5 = (P1S5 + P2S5)%self.chosenPrime
					AS6 = (P1S6 + P2S6)%self.chosenPrime

					print('Share 5 of Addition : ',AS5)
					print('Share 6 of Addition : ',AS6)

					

			if data == 'SM100':
				
				if self.name == MPCConf.party1Name :

					MS1 = (P3S1*100)%self.chosenPrime
					MS2 = (P3S2*100)%self.chosenPrime

					print('Share 1 of Constant Multiplication : ',MS1)
					print('Share 2 of Constant Multiplication : ',MS2)

				if self.name == MPCConf.party2Name:
				
					MS3 = (P3S3*100)%self.chosenPrime
					MS4 = (P3S4*100)%self.chosenPrime

					print('Share 3 of Constant Multiplication : ',MS3)
					print('Share 4 of Constant Multiplication : ',MS4)
				
				if self.name == MPCConf.party3Name:
					
					MS5 = (P3S5*100)%self.chosenPrime
					MS6 = (P3S6*100)%self.chosenPrime

					print('Share 5 of Constant Multiplication : ',MS5)
					print('Share 6 of Constant Multiplication : ',MS6)


			




			if data == 'SSM':
				#self.generatePK1()
				
				r1 = random.randint(0,self.chosenPrime)
				r2 = random.randint(0,self.chosenPrime)				


				data = cli.recv(1024).decode()
				print('Data received : '+str(data))

				ZZZZ = np.matrix(str(data))
				print('SSM Z : ',ZZZZ)
				


				if self.name == MPCConf.party1Name :
					
					v = matrix([[AS1],[r1],[r2]])
					shares = ZZZZ * v
					sharesA1 = [int(shares[0][0]%self.chosenPrime),
							int(shares[1][0]%self.chosenPrime),
							int(shares[2][0]%self.chosenPrime),
							int(shares[3][0]%self.chosenPrime),
							int(shares[4][0]%self.chosenPrime),
							int(shares[5][0]%self.chosenPrime)]
					print('Shares : ',sharesA1)

					v = matrix([[AS2],[r1],[r2]])
					shares = ZZZZ * v
					sharesA2 = [int(shares[0][0]%self.chosenPrime),
							int(shares[1][0]%self.chosenPrime),
							int(shares[2][0]%self.chosenPrime),
							int(shares[3][0]%self.chosenPrime),
							int(shares[4][0]%self.chosenPrime),
							int(shares[5][0]%self.chosenPrime)]
					print('Shares : ',sharesA2)

					v = matrix([[MS1],[r1],[r2]])
					shares = ZZZZ * v
					sharesM1 = [int(shares[0][0]%self.chosenPrime),
							int(shares[1][0]%self.chosenPrime),
							int(shares[2][0]%self.chosenPrime),
							int(shares[3][0]%self.chosenPrime),
							int(shares[4][0]%self.chosenPrime),
							int(shares[5][0]%self.chosenPrime)]
					print('Shares : ',sharesM1)

					v = matrix([[MS2],[r1],[r2]])
					shares = ZZZZ * v
					sharesM2 = [int(shares[0][0]%self.chosenPrime),
							int(shares[1][0]%self.chosenPrime),
							int(shares[2][0]%self.chosenPrime),
							int(shares[3][0]%self.chosenPrime),
							int(shares[4][0]%self.chosenPrime),
							int(shares[5][0]%self.chosenPrime)]
					print('Shares : ',sharesM2)

					AS11 = sharesA1[0]
					AS21 = sharesA2[0]

					#AS31, AS41, AS51, AS61

					AS12 = sharesA1[1]					
					AS22 = sharesA2[1]

					#AS32, AS42, AS52, AS62

					MS11 = sharesM1[0]
					MS21 = sharesM2[0]

					#MS31, MS41, MS51, MS61

					MS12 = sharesM1[1]					
					MS22 = sharesM2[1]

					#MS32, MS42, MS52, MS62

					socksend2 = self.connectToParty(MPCConf.hostname,MPCConf.party2Port)
					socksend2.send(str(sharesA1[2]).encode())
					time.sleep(3)					
					socksend2.send(str(sharesA1[3]).encode())
					time.sleep(3)					
					socksend2.send(str(sharesA2[2]).encode())
					time.sleep(3)					
					socksend2.send(str(sharesA2[3]).encode())
					time.sleep(3)					
					socksend2.send(str(sharesM1[2]).encode())
					time.sleep(3)					
					socksend2.send(str(sharesM1[3]).encode())
					time.sleep(3)					
					socksend2.send(str(sharesM2[2]).encode())
					time.sleep(3)					
					socksend2.send(str(sharesM2[3]).encode())


					socksend3 = self.connectToParty(MPCConf.hostname,MPCConf.party3Port)
					socksend3.send(str(sharesA1[4]).encode())
					time.sleep(3)					
					socksend3.send(str(sharesA1[5]).encode())
					time.sleep(3)					
					socksend3.send(str(sharesA2[4]).encode())
					time.sleep(3)					
					socksend3.send(str(sharesA2[5]).encode())
					time.sleep(3)					
					socksend3.send(str(sharesM1[4]).encode())
					time.sleep(3)					
					socksend3.send(str(sharesM1[5]).encode())
					time.sleep(3)					
					socksend3.send(str(sharesM2[4]).encode())
					time.sleep(3)					
					socksend3.send(str(sharesM2[5]).encode())


					#time.sleep(10)
					cli2,addr2 = sock.accept()
					print('Got connection from ',addr2)
					constr = 'Thank you '+str(addr2)+' for connecting at Party '+self.name
					cli2.send(constr.encode())

					AS31 = (int(cli2.recv(1024).decode()))
					AS32 = (int(cli2.recv(1024).decode()))
					AS41 = (int(cli2.recv(1024).decode()))
					AS42 = (int(cli2.recv(1024).decode()))

					MS31 = (int(cli2.recv(1024).decode()))
					MS32 = (int(cli2.recv(1024).decode()))
					MS41 = (int(cli2.recv(1024).decode()))
					MS42 = (int(cli2.recv(1024).decode()))

					cli2.close()


					#time.sleep(10)
					cli3,addr3 = sock.accept()
					print('Got connection from ',addr3)
					constr = 'Thank you '+str(addr3)+' for connecting at Party '+self.name
					cli3.send(constr.encode())

					AS51 = (int(cli3.recv(1024).decode()))
					AS52 = (int(cli3.recv(1024).decode()))
					AS61 = (int(cli3.recv(1024).decode()))
					AS62 = (int(cli3.recv(1024).decode()))

					MS51 = (int(cli3.recv(1024).decode()))
					MS52 = (int(cli3.recv(1024).decode()))
					MS61 = (int(cli3.recv(1024).decode()))
					MS62 = (int(cli3.recv(1024).decode()))


					cli3.close()


					#reconstruct
					SM1AVector = matrix([[AS11,AS21,AS31,AS41,AS51,AS61]])
					SM2AVector = matrix([[AS12,AS22,AS32,AS42,AS52,AS62]])

					SM1MVector = matrix([[MS11,MS21,MS31,MS41,MS51,MS61]])
					SM2MVector = matrix([[MS12,MS22,MS32,MS42,MS52,MS62]])

					print('A inverse Matrix : ',self.inversematrix(AAAA,self.chosenPrime))#print(AAAA.I)

					SM1A = int((self.inversematrix(AAAA,self.chosenPrime) * SM1AVector.T)[0][0]%self.chosenPrime)#int((AAAA.I * SM1AVector.T)[0][0]%self.chosenPrime)
					SM2A = int((self.inversematrix(AAAA,self.chosenPrime) * SM2AVector.T)[0][0]%self.chosenPrime)#int((AAAA.I * SM2AVector.T)[0][0]%self.chosenPrime)
					SM1M = int((self.inversematrix(AAAA,self.chosenPrime) * SM1MVector.T)[0][0]%self.chosenPrime)#int((AAAA.I * SM1MVector.T)[0][0]%self.chosenPrime)
					SM2M = int((self.inversematrix(AAAA,self.chosenPrime) * SM2MVector.T)[0][0]%self.chosenPrime)#int((AAAA.I * SM2MVector.T)[0][0]%self.chosenPrime)
					
					#product shares
					SAns1 = (SM1A * SM1M)%self.chosenPrime
					SAns2 = (SM2A * SM2M)%self.chosenPrime
					print('Share Answer 1 : ' , SAns1)
					print('Share Answer 2 : ' , SAns2)





				if self.name == MPCConf.party2Name:
					
					v = matrix([[AS3],[r1],[r2]])
					shares = ZZZZ * v
					sharesA3 = [int(shares[0][0]%self.chosenPrime),
							int(shares[1][0]%self.chosenPrime),
							int(shares[2][0]%self.chosenPrime),
							int(shares[3][0]%self.chosenPrime),
							int(shares[4][0]%self.chosenPrime),
							int(shares[5][0]%self.chosenPrime)]
					print('Shares : ',sharesA3)

					v = matrix([[AS4],[r1],[r2]])
					shares = ZZZZ * v
					sharesA4 = [int(shares[0][0]%self.chosenPrime),
							int(shares[1][0]%self.chosenPrime),
							int(shares[2][0]%self.chosenPrime),
							int(shares[3][0]%self.chosenPrime),
							int(shares[4][0]%self.chosenPrime),
							int(shares[5][0]%self.chosenPrime)]
					print('Shares : ',sharesA4)

					v = matrix([[MS3],[r1],[r2]])
					shares = ZZZZ * v
					sharesM3 = [int(shares[0][0]%self.chosenPrime),
							int(shares[1][0]%self.chosenPrime),
							int(shares[2][0]%self.chosenPrime),
							int(shares[3][0]%self.chosenPrime),
							int(shares[4][0]%self.chosenPrime),
							int(shares[5][0]%self.chosenPrime)]
					print('Shares : ',sharesM3)

					v = matrix([[MS4],[r1],[r2]])
					shares = ZZZZ * v
					sharesM4 = [int(shares[0][0]%self.chosenPrime),
							int(shares[1][0]%self.chosenPrime),
							int(shares[2][0]%self.chosenPrime),
							int(shares[3][0]%self.chosenPrime),
							int(shares[4][0]%self.chosenPrime),
							int(shares[5][0]%self.chosenPrime)]
					print('Shares : ',sharesM4)

					AS33 = sharesA3[2]
					AS43 = sharesA4[2]

					#AS13, AS23, AS53, AS63

					AS34 = sharesA3[3]					
					AS44 = sharesA4[3]

					#AS14, AS24, AS54, AS64

					MS33 = sharesM3[2]
					MS43 = sharesM4[2]

					#MS13, MS23, MS53, MS63

					MS34 = sharesM3[3]					
					MS44 = sharesM4[3]

					#MS14, MS24, MS54, MS64


					#time.sleep(10)
					cli1,addr1 = sock.accept()
					print('Got connection from ',addr1)
					constr = 'Thank you '+str(addr1)+' for connecting at Party '+self.name
					cli1.send(constr.encode())

					AS13 = (int(cli1.recv(1024).decode()))
					AS14 = (int(cli1.recv(1024).decode()))
					AS23 = (int(cli1.recv(1024).decode()))
					AS24 = (int(cli1.recv(1024).decode()))

					MS13 = (int(cli1.recv(1024).decode()))
					MS14 = (int(cli1.recv(1024).decode()))
					MS23 = (int(cli1.recv(1024).decode()))
					MS24 = (int(cli1.recv(1024).decode()))

					cli1.close()


					socksend1 = self.connectToParty(MPCConf.hostname,MPCConf.party1Port)
					socksend1.send(str(sharesA3[0]).encode())
					time.sleep(3)					
					socksend1.send(str(sharesA3[1]).encode())
					time.sleep(3)					
					socksend1.send(str(sharesA4[0]).encode())
					time.sleep(3)					
					socksend1.send(str(sharesA4[1]).encode())
					time.sleep(3)					
					socksend1.send(str(sharesM3[0]).encode())
					time.sleep(3)					
					socksend1.send(str(sharesM3[1]).encode())
					time.sleep(3)					
					socksend1.send(str(sharesM4[0]).encode())
					time.sleep(3)					
					socksend1.send(str(sharesM4[1]).encode())


					socksend3 = self.connectToParty(MPCConf.hostname,MPCConf.party3Port)
					socksend3.send(str(sharesA3[4]).encode())
					time.sleep(3)					
					socksend3.send(str(sharesA3[5]).encode())
					time.sleep(3)					
					socksend3.send(str(sharesA4[4]).encode())
					time.sleep(3)					
					socksend3.send(str(sharesA4[5]).encode())
					time.sleep(3)					
					socksend3.send(str(sharesM3[4]).encode())
					time.sleep(3)					
					socksend3.send(str(sharesM3[5]).encode())
					time.sleep(3)					
					socksend3.send(str(sharesM4[4]).encode())
					time.sleep(3)					
					socksend3.send(str(sharesM4[5]).encode())


					#time.sleep(10)
					cli3,addr3 = sock.accept()
					print('Got connection from ',addr3)
					constr = 'Thank you '+str(addr3)+' for connecting at Party '+self.name
					cli3.send(constr.encode())

					AS53 = (int(cli3.recv(1024).decode()))
					AS54 = (int(cli3.recv(1024).decode()))
					AS63 = (int(cli3.recv(1024).decode()))
					AS64 = (int(cli3.recv(1024).decode()))

					MS53 = (int(cli3.recv(1024).decode()))
					MS54 = (int(cli3.recv(1024).decode()))
					MS63 = (int(cli3.recv(1024).decode()))
					MS64 = (int(cli3.recv(1024).decode()))


					cli3.close()


					#reconstruct
					SM3AVector = matrix([[AS13,AS23,AS33,AS43,AS53,AS63]])
					SM4AVector = matrix([[AS14,AS24,AS34,AS44,AS54,AS64]])

					SM3MVector = matrix([[MS13,MS23,MS33,MS43,MS53,MS63]])
					SM4MVector = matrix([[MS14,MS24,MS34,MS44,MS54,MS64]])

					SM3A = int((self.inversematrix(AAAA,self.chosenPrime) * SM3AVector.T)[0][0]%self.chosenPrime)#int((AAAA.I * SM3AVector.T)[0][0]%self.chosenPrime)
					SM4A = int((self.inversematrix(AAAA,self.chosenPrime) * SM4AVector.T)[0][0]%self.chosenPrime)#int((AAAA.I * SM4AVector.T)[0][0]%self.chosenPrime)
					SM3M = int((self.inversematrix(AAAA,self.chosenPrime) * SM3MVector.T)[0][0]%self.chosenPrime)#int((AAAA.I * SM3MVector.T)[0][0]%self.chosenPrime)
					SM4M = int((self.inversematrix(AAAA,self.chosenPrime) * SM4MVector.T)[0][0]%self.chosenPrime)#int((AAAA.I * SM4MVector.T)[0][0]%self.chosenPrime)
					
					#product shares
					SAns3 = (SM3A * SM3M)%self.chosenPrime
					SAns4 = (SM4A * SM4M)%self.chosenPrime
					print('Share Answer 3 : ' , SAns3)
					print('Share Answer 4 : ' , SAns4)





				if self.name == MPCConf.party3Name:
					

					v = matrix([[AS5],[r1],[r2]])
					shares = ZZZZ * v
					sharesA5 = [int(shares[0][0]%self.chosenPrime),
							int(shares[1][0]%self.chosenPrime),
							int(shares[2][0]%self.chosenPrime),
							int(shares[3][0]%self.chosenPrime),
							int(shares[4][0]%self.chosenPrime),
							int(shares[5][0]%self.chosenPrime)]
					print('Shares : ',sharesA5)

					v = matrix([[AS6],[r1],[r2]])
					shares = ZZZZ * v
					sharesA6 = [int(shares[0][0]%self.chosenPrime),
							int(shares[1][0]%self.chosenPrime),
							int(shares[2][0]%self.chosenPrime),
							int(shares[3][0]%self.chosenPrime),
							int(shares[4][0]%self.chosenPrime),
							int(shares[5][0]%self.chosenPrime)]
					print('Shares : ',sharesA6)

					v = matrix([[MS5],[r1],[r2]])
					shares = ZZZZ * v
					sharesM5 = [int(shares[0][0]%self.chosenPrime),
							int(shares[1][0]%self.chosenPrime),
							int(shares[2][0]%self.chosenPrime),
							int(shares[3][0]%self.chosenPrime),
							int(shares[4][0]%self.chosenPrime),
							int(shares[5][0]%self.chosenPrime)]
					print('Shares : ',sharesM5)

					v = matrix([[MS6],[r1],[r2]])
					shares = ZZZZ * v
					sharesM6 = [int(shares[0][0]%self.chosenPrime),
							int(shares[1][0]%self.chosenPrime),
							int(shares[2][0]%self.chosenPrime),
							int(shares[3][0]%self.chosenPrime),
							int(shares[4][0]%self.chosenPrime),
							int(shares[5][0]%self.chosenPrime)]
					print('Shares : ',sharesM6)

					AS55 = sharesA5[4]
					AS65 = sharesA6[4]

					#AS15, AS25, AS35, AS45

					AS56 = sharesA5[5]					
					AS66 = sharesA6[5]

					#AS16, AS26, AS36, AS46

					MS55 = sharesM5[4]
					MS65 = sharesM6[4]

					#MS15, MS25, MS35, MS45

					MS56 = sharesM5[5]					
					MS66 = sharesM6[5]

					#MS16, MS26, MS36, MS46


					#time.sleep(10)
					cli1,addr1 = sock.accept()
					print('Got connection from ',addr1)
					constr = 'Thank you '+str(addr1)+' for connecting at Party '+self.name
					cli1.send(constr.encode())

					AS15 = (int(cli1.recv(1024).decode()))
					AS16 = (int(cli1.recv(1024).decode()))
					AS25 = (int(cli1.recv(1024).decode()))
					AS26 = (int(cli1.recv(1024).decode()))

					MS15 = (int(cli1.recv(1024).decode()))
					MS16 = (int(cli1.recv(1024).decode()))
					MS25 = (int(cli1.recv(1024).decode()))
					MS26 = (int(cli1.recv(1024).decode()))

					cli1.close()



					#time.sleep(10)
					cli2,addr2 = sock.accept()
					print('Got connection from ',addr2)
					constr = 'Thank you '+str(addr2)+' for connecting at Party '+self.name
					cli2.send(constr.encode())

					AS35 = (int(cli2.recv(1024).decode()))
					AS36 = (int(cli2.recv(1024).decode()))
					AS45 = (int(cli2.recv(1024).decode()))
					AS46 = (int(cli2.recv(1024).decode()))

					MS35 = (int(cli2.recv(1024).decode()))
					MS36 = (int(cli2.recv(1024).decode()))
					MS45 = (int(cli2.recv(1024).decode()))
					MS46 = (int(cli2.recv(1024).decode()))

					cli2.close()


					
					socksend1 = self.connectToParty(MPCConf.hostname,MPCConf.party1Port)
					socksend1.send(str(sharesA5[0]).encode())
					time.sleep(3)					
					socksend1.send(str(sharesA5[1]).encode())
					time.sleep(3)					
					socksend1.send(str(sharesA6[0]).encode())
					time.sleep(3)					
					socksend1.send(str(sharesA6[1]).encode())
					time.sleep(3)					
					socksend1.send(str(sharesM5[0]).encode())
					time.sleep(3)					
					socksend1.send(str(sharesM5[1]).encode())
					time.sleep(3)					
					socksend1.send(str(sharesM6[0]).encode())
					time.sleep(3)					
					socksend1.send(str(sharesM6[1]).encode())


					socksend2 = self.connectToParty(MPCConf.hostname,MPCConf.party2Port)
					socksend2.send(str(sharesA5[2]).encode())
					time.sleep(3)					
					socksend2.send(str(sharesA5[3]).encode())
					time.sleep(3)					
					socksend2.send(str(sharesA6[2]).encode())
					time.sleep(3)					
					socksend2.send(str(sharesA6[3]).encode())
					time.sleep(3)					
					socksend2.send(str(sharesM5[2]).encode())
					time.sleep(3)					
					socksend2.send(str(sharesM5[3]).encode())
					time.sleep(3)					
					socksend2.send(str(sharesM6[2]).encode())
					time.sleep(3)					
					socksend2.send(str(sharesM6[3]).encode())



					#reconstruct
					SM5AVector = matrix([[AS15,AS25,AS35,AS45,AS55,AS65]])
					SM6AVector = matrix([[AS16,AS26,AS36,AS46,AS56,AS66]])

					SM5MVector = matrix([[MS15,MS25,MS35,MS45,MS55,MS65]])
					SM6MVector = matrix([[MS16,MS26,MS36,MS46,MS56,MS66]])

					SM5A = int((self.inversematrix(AAAA,self.chosenPrime) * SM5AVector.T)[0][0]%self.chosenPrime)#int((AAAA.I * SM5AVector.T)[0][0]%self.chosenPrime)
					SM6A = int((self.inversematrix(AAAA,self.chosenPrime) * SM6AVector.T)[0][0]%self.chosenPrime)#int((AAAA.I * SM6AVector.T)[0][0]%self.chosenPrime)
					SM5M = int((self.inversematrix(AAAA,self.chosenPrime) * SM5MVector.T)[0][0]%self.chosenPrime)#int((AAAA.I * SM5MVector.T)[0][0]%self.chosenPrime)
					SM6M = int((self.inversematrix(AAAA,self.chosenPrime) * SM6MVector.T)[0][0]%self.chosenPrime)#int((AAAA.I * SM6MVector.T)[0][0]%self.chosenPrime)
					
					#product shares
					SAns5 = (SM5A * SM5M)%self.chosenPrime
					SAns6 = (SM6A * SM6M)%self.chosenPrime
					print('Share Answer 5 : ' , SAns5)
					print('Share Answer 6 : ' , SAns6)






			if data == 'ENC':
				
				PKg = self.g
				PK1 = self.getPK1()
				PK2 = self.getPK2()

				print('Public Keys : '+ str(PK1) +' '+ str(PK2) +' '+ str(PKg))

				#compute s
				if self.name == MPCConf.party1Name :
					
					time.sleep(5)
					p1d = random.randint(0,self.chosenPrime)
					p1m = random.randint(0,self.chosenPrime)
					b = (p1d+p1m)%self.chosenPrime
					socksend = self.connectToParty(MPCConf.hostname,MPCConf.party2Port)
					socksend.send(str(b).encode())

					#time.sleep(10)
					cli3,addr3 = sock.accept()
					print('Got connection from ',addr3)
					constr = 'Thank you '+str(addr3)+' for connecting at Party '+self.name
					cli3.send(constr.encode())

					key = (int(cli3.recv(1024).decode())-p1m)%self.chosenPrime
					print('Data Received :'+str(key))
					Publish(MPCConf.party1Name+':'+'S'+':'+str(key))
					cli3.close()

				if self.name == MPCConf.party2Name:
					#time.sleep(5)
					cli1,addr1 = sock.accept()
					print('Got connection from ',addr1)
					constr = 'Thank you '+str(addr1)+' for connecting at Party '+self.name
					cli1.send(constr.encode())

					a = (int(cli1.recv(1024).decode()))
					print('Data Received :'+str(a))
					p2d = random.randint(0,self.chosenPrime)
					b = (a+p2d)%self.chosenPrime
					socksend = self.connectToParty(MPCConf.hostname,MPCConf.party3Port)
					socksend.send(str(b).encode())

				if self.name == MPCConf.party3Name:
					#time.sleep(10)
					cli2,addr2 = sock.accept()
					print('Got connection from ',addr2)
					constr = 'Thank you '+str(addr2)+' for connecting at Party '+self.name
					cli2.send(constr.encode())
					#time.sleep(5)
					a = (int(cli2.recv(1024).decode()))
					print('Data Received :'+str(a))
					p3d = random.randint(0,self.chosenPrime)
					b = (a+p3d)%self.chosenPrime
					socksend = self.connectToParty(MPCConf.hostname,MPCConf.party1Port)
					socksend.send(str(b).encode())
					
				time.sleep(3)

				#retrieve s as self
				self.STmp = self.getS()
				self.C1 = (PK1*self.STmp)%self.chosenPrime
				self.Ctemp = self.fastExponentiation(PK2,self.STmp,self.chosenPrime)

				if self.name == MPCConf.party1Name:
					ENCAns1 = (SAns1*self.Ctemp)%self.chosenPrime
					ENCAns2 = (SAns2*self.Ctemp)%self.chosenPrime
					Publish(MPCConf.party1Name+':'+'Share1'+':'+str(SAns1))#ENCAns1))
					Publish(MPCConf.party1Name+':'+'Share2'+':'+str(SAns2))#ENCAns2))

				if self.name == MPCConf.party2Name:
					ENCAns3 = (SAns3*self.Ctemp)%self.chosenPrime
					ENCAns4 = (SAns4*self.Ctemp)%self.chosenPrime
					time.sleep(5)
					Publish(MPCConf.party2Name+':'+'Share3'+':'+str(SAns3))#ENCAns3))
					Publish(MPCConf.party2Name+':'+'Share4'+':'+str(SAns4))#ENCAns4))										

				if self.name == MPCConf.party3Name:
					ENCAns5 = (SAns5*self.Ctemp)%self.chosenPrime
					ENCAns6 = (SAns6*self.Ctemp)%self.chosenPrime
					time.sleep(10)
					Publish(MPCConf.party3Name+':'+'Share5'+':'+str(SAns5))#ENCAns5))
					Publish(MPCConf.party3Name+':'+'Share6'+':'+str(SAns6))#ENCAns6))

				#claculate C, ~C and publish
			


			if data == 'DEC':
				
				shares = self.getShares()
				
				if self.name == MPCConf.party1Name :
					time.sleep(5)

					gam = random.randint(1,self.chosenPrime)
					#irnd = random.randint(1,self.chosenPrime)
					b = (gam*self.g*(self.r)*self.modInverse(self.s,self.chosenPrime))%self.chosenPrime#b = (gam*self.g*(self.r+irnd)*self.modInverse(self.s,self.chosenPrime))%self.chosenPrime
					socksend = self.connectToParty(MPCConf.hostname,MPCConf.party2Port)
					socksend.send(str(b).encode())


					#time.sleep(10)
					cli3,addr3 = sock.accept()
					print('Got connection from ',addr3)
					constr = 'Thank you '+str(addr3)+' for connecting at Party '+self.name
					cli3.send(constr.encode())

					key = (int(cli3.recv(1024).decode())*self.modInverse(gam,self.chosenPrime))%self.chosenPrime
					print('Data Received :'+str(key))
					Publish(MPCConf.party1Name+':'+'SK'+':'+str(key))
					cli3.close()

				if self.name == MPCConf.party2Name:
					#time.sleep(5)
					cli1,addr1 = sock.accept()
					print('Got connection from ',addr1)
					constr = 'Thank you '+str(addr1)+' for connecting at Party '+self.name
					cli1.send(constr.encode())

					a = (int(cli1.recv(1024).decode()))
					print('Data Received :'+str(a))
					#irnd = random.randint(1,self.chosenPrime)
					b = (a*(self.r)*self.modInverse(self.s,self.chosenPrime))%self.chosenPrime#b = (a*(self.r+irnd)*self.modInverse(self.s,self.chosenPrime))%self.chosenPrime
					socksend = self.connectToParty(MPCConf.hostname,MPCConf.party3Port)
					socksend.send(str(b).encode())

				if self.name == MPCConf.party3Name:
					#time.sleep(10)
					cli2,addr2 = sock.accept()
					print('Got connection from ',addr2)
					constr = 'Thank you '+str(addr2)+' for connecting at Party '+self.name
					cli2.send(constr.encode())
					time.sleep(5)
					a = (int(cli2.recv(1024).decode()))
					print('Data Received :'+str(a))
					#irnd = random.randint(1,self.chosenPrime)
					b = (a*(self.r)*self.modInverse(self.s,self.chosenPrime))%self.chosenPrime#b = (a*(self.r+irnd)*self.modInverse(self.s,self.chosenPrime))%self.chosenPrime
					socksend = self.connectToParty(MPCConf.hostname,MPCConf.party1Port)
					socksend.send(str(b).encode())	

				time.sleep(10)
				print(shares)
				secsk = self.getSK()
				decshares = matrix([shares[0][0],shares[1][0],shares[2][0],shares[3][0],shares[4][0],shares[5][0]])#matrix(Decryption.decrypt(secsk, self.C1, self.chosenPrime, shares))

				print('Decryption Shares :',decshares)
				print('Z Matrix : ',ZZZZ)

				ZZZZ = np.squeeze(np.asarray(ZZZZ))
				#recon
				tmpmat = matrix([ [(ZZZZ[0][1]**3)%self.chosenPrime,(ZZZZ[0][1]**4)%self.chosenPrime],
					[(ZZZZ[1][1]**3)%self.chosenPrime,(ZZZZ[1][1]**4)%self.chosenPrime],
					[(ZZZZ[2][1]**3)%self.chosenPrime,(ZZZZ[2][1]**4)%self.chosenPrime],
					[(ZZZZ[3][1]**3)%self.chosenPrime,(ZZZZ[3][1]**4)%self.chosenPrime],
					[(ZZZZ[4][1]**3)%self.chosenPrime,(ZZZZ[4][1]**4)%self.chosenPrime],
					[(ZZZZ[5][1]**3)%self.chosenPrime,(ZZZZ[5][1]**4)%self.chosenPrime]
					])
				ZZ22 = np.c_[ZZZZ,tmpmat]
				ZZ22 = np.delete(ZZ22,5,0)

				print('Z Matrix Inverse : ',self.inversematrix(ZZ22,self.chosenPrime))
				print('Z*Z-1 : ',ZZ22*self.inversematrix(ZZ22,self.chosenPrime))

				#ONES = np.c_[ matrix(np.ones((5,5),dtype=int)),matrix([[0],[0],[0],[0],[0]])]
				ans = int((self.inversematrix(ZZ22,self.chosenPrime) * np.delete(decshares.T,5,0))[0][0]%self.chosenPrime)
				print('Final Answer : ',ans)




			cli.close()	



	def __init__(self,name,portno,hostname):
		
		super(Party, self).__init__()
		self.name = name
		
		
		self.startServer(portno)


name = sys.argv[1]#input('Name \n')
portno = int(sys.argv[2])#int(input('Port No\n'))
hostname = sys.argv[3]#input('Host Name\n')
p = Party(name,portno,hostname)
