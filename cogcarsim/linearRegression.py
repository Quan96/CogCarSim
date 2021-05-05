import numpy as np
import matplotlib.pyplot as plt

X = np.array([[-0.00076, 0.0015, 0.0166, 0.0497, -0.03, -0.05, -0.11, 0.15]]).T
y = np.array([[-0.61, 1.222, 13.307, 39.768, -24.689, -40.161, -92.804, 127.603]]).T

# plt.figure()
# plt.plot(X, y, 'b*')
# plt.show()

one = np.ones((X.shape[0], 1))
Xbar = np.concatenate((one, X), axis = 1)

# Calculating weights of the fitting line 
A = np.dot(Xbar.T, Xbar)
b = np.dot(Xbar.T, y)
w = np.dot(np.linalg.pinv(A), b)
print('w = ', w)
# Preparing the fitting line 
w_0 = w[0][0]
w_1 = w[1][0]
x0 = np.linspace(-0.11, 0.15)
y0 = w_0 + w_1*x0

# Drawing the fitting line 
plt.plot(X.T, y.T, 'ro')     # data 
plt.plot(x0, y0)             # the fitting line
plt.show()