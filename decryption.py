import math
import random
import subprocess
import os
import hashlib
from mpcconf import MPCConf

class Decryption(object):



	def fastExponentiation(self,e,r,p):
		res = 1
		e = e % p
		while (r > 0) :
			if ((r & 1) == 1) :
				res = (res * e) % p
			r = r >> 1
			e = (e * e) % p
		return res

	@staticmethod
	def modInverse(r,p):

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


	@staticmethod
	def decrypt(sk, C, p, shares):

		powdiff = MPCConf.powdiff

		decshares = []

		for row in shares :
			
			hasher = hashlib.sha256()
			hasher.update((row[2]).encode())
			pop = hasher.hexdigest()
			
			if hex(int(pop,16)) != hex(row[1]):
				print('Pop : ',hex(pop))
				print('shares row 1  : ',hex(row[1]))
				return 'Decryption Error : Hash Mismatch'

			if int(pop,16) > powdiff :
				return 'Decryption Error : Invalid Proof of Publish'

			share = row[0]
			ans = (share * Decryption.	modInverse((C*sk)%p,p))%p
			decshares.append(ans)

		return decshares


	def __init__(self):
		super(Publish, self).__init__()



