#!/usr/bin/python3

import numpy as np
import sympy as sp

x, n = sp.symbols('x n')
M = sp.Matrix([
    [x,1,0,0],
    [0,x,1,0],
    [0,0,x,1],
    [0,0,0,x]
])
sp.pprint(M ** n)

'''# 创建矩阵
A = np.array([[1, 2, 3, ] , [4, 5, 6, ],[1, 2, 3, ], [4, 5, 6, ]])
B = np.array([[7, 8], [9, 10], [11, 12]])

print("Matrix A:")
print(A)
print()

print("Matrix B:")
print(B)
print()

# 矩阵乘法
C = np.dot(A, B)
print("A * B:")
print(C)
print()

# 或者使用 @ 运算符（Python 3.5+）
C = A @ B
print("A @ B:")
print(C)
print()

# 转置
AT = A.T
print("Transpose of A:")
print(AT)
print()

# 标量乘法
D = A * 2.5
print("A * 2.5:")
print(D)
'''