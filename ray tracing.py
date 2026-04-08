# notes to follow for ray tracing project

import numpy as np

# create a 3-d vector
# [50,50,0]

vertices = np.array([[50,50,0]])
print(vertices)
    # we have to use a 4-dimensional coordinate system
    # to scale and translate and rotate a vector from one coordinate sysetem to another

# one coordinate system to another

#adding the fourth column in the vector with 1
vertices_4 = np.hstack((vertices,np.ones((vertices.shape[0],1))))
print(vertices,vertices_4)

#coordinate ranges for A (x), A(y)    0 to 500, 0 to 500
#coordinate ranges for P (x), P(y)    -1 to -1, 1 to 1
#z coordinates are the same in the A and P coordinate system

#example if we have a x point of 300 what is the same point in hte P coordinate system
Ax = 300
Axmin = 0
Axmax = 500
Pxmax = 1
Pxmin = -1
Aymin = 0
Aymax = 500
Pymax = 1
Pymin = -1
#if Ax is 500 then x_p = -1+1(2)/1=1
# if Ax is 0 then x_p = -1
#x_p = Pxmin=(Ax-Axmin)*(Pxmax-Pxmin)/(Axmax-Axmin)

#let's define out 4X4 matrix
scalex = (Pxmax - Pxmin)/(Axmax - Axmin)
Txmin = Pxmin
Tymin = Pymin
scaley = (Pymax - Pymin)/(Pymax - Pymin)

transMatrix = np.array([[scalex,0,0,Txmin], [0,scaley,0,Tymin],[0,0,1,0],[0,0,0,1]])

print(transMatrix)

#pass the vertices through the transmatrix
#1 transpose the vertices
vertices_T = vertices_4.T
print(vertices_T)
transformedMatrix = transMatrix @ vertices_T
print(transformedMatrix)

#change this back to our vector notation
# transpose the result
transformedMatrix = transformedMatrix.T

# remove the 4th coordinate
transformedMatrix = transformedMatrix[:,:3]/ transformedMatrix[:,3,np.newaxis]
print(transformedMatrix)
