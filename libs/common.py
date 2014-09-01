__author__ = 'Dylan J Raub'

import math

def floorint(x):
    return int(math.floor(x))

def lerp(a,b,p):
    return a+(b-a)*p

def invlerp(a,b,x):
	return (x-a)/(b-a)