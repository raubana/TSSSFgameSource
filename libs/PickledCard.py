__author__ = 'Dylan J Raub'

import pygame.image
import gzip
import pickle
import tempfile
import os
import io
import string
import tarfile
import StringIO

class PickledCard(object):
    def __init__(self,img,attr):
        self.img = img
        self.attr = attr

def save_pickledcard(card,filename):
    out = tarfile.open(filename, mode='w')
    #we add the image to the archive
    info = tarfile.TarInfo('image.png')
    info.size = len(card.img)
    out.addfile(info, io.BytesIO(card.img))
    #we add the attributes to the archive
    info2 = tarfile.TarInfo('attributes')
    info2.size = len(card.attr)
    out.addfile(info2, StringIO.StringIO(card.attr))
    #finally, we close the archive
    out.close()
    """
    temp = open(filename,"wb")
    pickle.dump(card,temp)
    temp.close()
    """
    """
    temp = open(filename+".temp","wb")
    pickle.dump(card,temp)
    temp.close()
    temp = open(filename+".temp","rb")
    lines = temp.readlines()
    temp.close()
    os.remove(filename+".temp")
    f_out = gzip.open(filename, 'wb')
    f_out.writelines(lines)
    f_out.close()
    """

def open_pickledcard(filename):
    t = tarfile.open(filename, mode='r')
    #we get the image from the archive
    img = t.extractfile("image.png").read()
    #we get our attributes
    attr = t.extractfile("attributes").read()
    #we return our card
    return PickledCard(img,attr)
    """
    card = pickle.load(open(filename,"rb"))
    return card
    """
    """
    temp = open(filename+".temp","wb")
    f_in = gzip.open(filename, 'rb')
    temp.writelines(f_in.read())
    f_in.close()
    temp.close()
    temp = open(filename+".temp","rb")
    card = pickle.load(temp)
    temp.close()
    os.remove(filename+".temp")
    return card
    """