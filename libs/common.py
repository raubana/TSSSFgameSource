__author__ = 'Dylan J Raub'

import math

def floorint(x):
    return int(math.floor(x))

def lerp(a,b,p):
    return a+(b-a)*p

def lerp_colors(a,b,p):
    return (int(lerp(a[0],b[0],p)), int(lerp(a[1],b[1],p)), int(lerp(a[2],b[2],p)))

def invlerp(a,b,x):
	return (x-a)/(b-a)