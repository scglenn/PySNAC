#This is public key encryption
'''import nacl.utils
from nacl.public import PrivateKey, Box

# Generate Bob's private key, which must be kept secret
skbob = PrivateKey.generate()

# Bob's public key can be given to anyone wishing to send
#   Bob an encrypted message
pkbob = skbob.public_key

# Alice does the same and then Alice and Bob exchange public keys
skalice = PrivateKey.generate()
pkalice = skalice.public_key

# Bob wishes to send Alice an encrypted message so Bob must make a Box with
#   his private key and Alice's public key
bob_box = Box(skbob, pkalice)

# This is our message to send, it must be a bytestring as Box will treat it
#   as just a binary blob of data.
message = b"humans"

# Encrypt our message, it will be exactly 40 bytes longer than the
#   original message as it stores authentication information and the
#   nonce alongside it.
#encrypted = bob_box.encrypt(message)

# This is a nonce, it *MUST* only be used once, but it is not considered
#   secret and can be transmitted or stored alongside the ciphertext. A
#   good source of nonces are just sequences of 24 random bytes.
nonce = nacl.utils.random(Box.NONCE_SIZE)

encrypted = bob_box.encrypt(message, nonce)

# Alice creates a second box with her private key to decrypt the message
alice_box = Box(skalice, pkbob)

# Decrypt our message, an exception will be raised if the encryption was
#   tampered with or there was otherwise an error.
plaintext = alice_box.decrypt(encrypted)

print ("plaintext: %s" % plaintext.decode('ascii'))
'''
#this is for secret key encryption
import nacl.secret
import nacl.utils
from hashlib import blake2b

#key = b'12345'

#h = blake2b(key,digest_size=32)
#h.update(b'12345',digest_size=)
#h.hexdigest()
# This must be kept secret, this is the combination to your safe
#key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
key = (12345).to_bytes(32,byteorder='big')
# This is your safe, you can use it to encrypt or decrypt messages
box = nacl.secret.SecretBox(key)#was key

# This is our message to send, it must be a bytestring as SecretBox will
#   treat it as just a binary blob of data.
message = b'\x00'
print(message)
# Encrypt our message, it will be exactly 40 bytes longer than the
#   original message as it stores authentication information and the
#   nonce alongside it.
nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)

encrypted = box.encrypt(message,nonce)
# Decrypt our message, an exception will be raised if the encryption was
#   tampered with or there was otherwise an error.
box2 = nacl.secret.SecretBox(key)

plaintext = box2.decrypt(encrypted)
print ("plaintext: %s" % plaintext.decode('ascii'))
