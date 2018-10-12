import math
import random
import subprocess
import os
import hashlib
from mpcconf import MPCConf

class Publish(object):

	def proofOfPublish(self,publishString):

		commonFile = open("commonmpc.txt","a")		
		line = subprocess.check_output(['tail','-1','commonmpc.txt'])

		nonce = random.randint(1,100000)
		hasher = hashlib.sha256()
		
		if len(line) == 0 :
	
			hasher.update((publishString+str(nonce)).encode())
			pop = hasher.hexdigest()

		else :
			print(str(line).strip() )
			tokens = str(line).strip().split(':')
			popprev = tokens[-1][:-3]
			print(popprev)

			publishString = popprev + publishString
			hasher.update((publishString+str(nonce)).encode())
			pop = hasher.hexdigest()

		powdiff = MPCConf.powdiff

		pop = int(pop,16)
		while pop > powdiff :
				nonce = random.randint(1,100000)
				hasher = hashlib.sha256()
				hasher.update((publishString+str(nonce)).encode())
				pop = hasher.hexdigest()
				pop = int(pop,16)

		return [nonce,pop]


	def __init__(self, publishString):
		super(Publish, self).__init__()

		pop = self.proofOfPublish(publishString)
		print(hex(pop[1]))
		commonFile = open("commonmpc.txt","a")
		self.publishString = publishString+':'+str(pop[0])+':'+hex(pop[1])
		commonFile.write(self.publishString+'\n')
		commonFile.close()



