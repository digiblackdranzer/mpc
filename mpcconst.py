import math
import random
import subprocess
import os
import hashlib
from publish import Publish
from numpy import matrix

class MPCConst(object):

	# A = matrix( [ [0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0] ] )
	# Z = matrix( [ [0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0] ] )Z

	def isPrime(self,n):
		
		for j in range(2,int(math.sqrt(n))+1):
			if(n%j==0):
				return False
		return True


	def prime(self,n):

		ans = 1
		if n == 1 :
			return ans+1
		else :
				for i in range(ans+1,100000000):
					if self.isPrime(i):
						n = n-1
						ans = i
					if n == 0 :
						break

		return ans

	@staticmethod	
	def sschemeA(p):

		a1 = random.randint(0,p)
		a2 = random.randint(0,p)
		a3 = random.randint(0,p)
		a4 = random.randint(0,p)
		a5 = random.randint(0,p)
		a6 = random.randint(0,p)
		return matrix( [ [1,0,0,0,0,0], 
						 [0,1,0,0,0,0], 
						 [0,0,1,0,0,0], 
						 [0,0,0,1,0,0],
						 [0,0,0,0,1,0], 
						 [0,0,0,0,0,1] ] )
		# return matrix( [ [1,a1,(a1**2)%p,(a1**3)%p,(a1**4)%p,(a1**5)%p], 
		# 				 [1,a2,(a2**2)%p,(a2**3)%p,(a2**4)%p,(a2**5)%p], 
		# 				 [1,a3,(a3**2)%p,(a3**3)%p,(a3**4)%p,(a3**5)%p], 
		# 				 [1,a4,(a4**2)%p,(a4**3)%p,(a4**4)%p,(a4**5)%p],
		# 				 [1,a5,(a5**2)%p,(a5**3)%p,(a5**4)%p,(a5**5)%p], 
		# 				 [1,a6,(a6**2)%p,(a6**3)%p,(a6**4)%p,(a6**5)%p] ] )

	@staticmethod	
	def sschemeZ(p):

		z1 = random.randint(0,p)
		z2 = random.randint(0,p)
		z3 = random.randint(0,p)
		z4 = random.randint(0,p)
		z5 = random.randint(0,p)
		z6 = random.randint(0,p)
		
		return matrix( [ [1,z1,(z1**2)%p], 
						 [1,z2,(z2**2)%p], 
						 [1,z3,(z3**2)%p], 
						 [1,z4,(z4**2)%p],
						 [1,z5,(z5**2)%p], 
						 [1,z6,(z6**2)%p] ] )		


	def __init__(self, p):
		super(MPCConst, self).__init__()

		# Initialize Parameters for Current MPC Round
		
		self.p = self.prime(p)  #shared
		self.g = random.randint(1,self.p) #shared
		self.h = random.randint(1,self.p) #shared
		while self.h == self.g :
			self.h = random.randint(1,self.p)
		self.x = random.randint(1,self.p) #shared
		
		self.publishString = str(self.p)+':'+str(self.g)+':'+str(self.h)+':'+str(self.x)
		Publish(self.publishString) 

		self.A = MPCConst.sschemeA(self.p)
		self.Z = MPCConst.sschemeZ(self.p)
		# print(self.A)
		# print(self.Z)




