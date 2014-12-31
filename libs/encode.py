from Crypto.Cipher import AES # encryption library
import base64

BLOCK_SIZE = 32

# the character used for padding--with a block cipher such as AES, the value
# you encrypt must be a multiple of BLOCK_SIZE in length.  This character is
# used to ensure that your value is always a multiple of BLOCK_SIZE
PADDING = '{'

# one-liner to sufficiently pad the text to be encrypted
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING

# one-liners to encrypt/encode and decrypt/decode a string
# encrypt with AES, encode with base64
EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)

# create a cipher object using the random secret
cipher = AES.new('kT7dDSuR+8+/c6uWmUwWvnhgvQMKLLcs')

def encode(s):
	# encode a string
	encoded = EncodeAES(cipher, s)
	return encoded
	#print 'Encrypted string: %s' % encoded

def decode(s):
	# decode the encoded string
	decoded = DecodeAES(cipher, s)
	return decoded
	#print 'Decrypted string: %s' % decoded

if __name__ == "__main__":
	print encode(raw_input(">>>"))

