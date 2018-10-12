import numpy as np
from numpy import matrix
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

'''def identitymatrix(n):
		return [[int(x == y) for x in range(0, n)] for y in range(0, n)]

def inversematrix(matrix, q):
		n = len(matrix)
		A = np.matrix([[ matrix[j, i] for i in range(0,n)] for j in range(0, n)], dtype = int)
		Ainv = np.matrix(identitymatrix(n), dtype = int)
		for i in range(0, n):
			factor = modInverse(A[i,i], q)
		if factor is None:
			raise ValueError("TODO: deal with this case")
		A[i] = (A[i] * factor) % q
		Ainv[i] = (Ainv[i] * factor) % q
		for j in range(0,n):
			if (i != j):
				factor = A[j, i]
				A[j] = (A[j] - factor * A[i]) % q
				Ainv[j] = (Ainv[j] - factor * Ainv[i]) % q
		return Ainv 
'''


def getMatrixInverse(m,p):
	print(m.I)
	det = np.linalg.det(m)
	ans = ( m.I*det*modInverse(det,p))%p
	ans = np.asarray(ans)
	for i in range(len(ans)):
		for j in range(len(ans)):
			ans[i][j] = int(round(ans[i][j]))

	return matrix(ans)


print(getMatrixInverse(matrix([[    1 ,13140  ,2439]
 ,[    1 , 8783 , 6385]
 ,[    1  ,3710 ,12393]
 ]),5))