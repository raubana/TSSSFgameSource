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
	def __init__(self, img, attr):
		self.img = img
		self.attr = attr


def save_pickledcard(card, f):
	out = tarfile.open(f, mode='w')
	# we add the image to the archive
	info = tarfile.TarInfo('image.png')
	info.size = len(card.img)
	out.addfile(info, io.BytesIO(card.img))
	# we add the attributes to the archive
	info2 = tarfile.TarInfo('attributes')
	info2.size = len(card.attr)
	out.addfile(info2, StringIO.StringIO(card.attr))
	#finally, we close the archive
	out.close()


def open_pickledcard(f):
	if type(f) == str:
		t = tarfile.open(f, mode='r')
	else:
		t = tarfile.open(fileobj=f, mode='r')
	# we get the image from the archive
	img = t.extractfile("image.png").read()  # we get our attributes
	attr = t.extractfile("attributes").read()
	# we return our card
	return PickledCard(img, attr)