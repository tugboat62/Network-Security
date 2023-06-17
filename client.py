import binascii
import socket
from bitvector_demo import Sbox, Mixer, Roc, AES_modulus
from keys import generate_keys
from BitVector import *
# Open the file in read mode
file = open('input.txt', 'r')

# Read the entire contents of the file
content = file.read()
print("String to be encrypted:", content)
file.close()
# Convert the string to bytes using a specific encoding (e.g., UTF-8)
byte_string = content.encode('utf-8')

# Get the length of the byte string
byte_length = len(byte_string)

if byte_length < 16:
    # append with a character that has no special or any control characters
    # or any of the characters that are used as separators
    for i in range(16 - byte_length):
        byte_string += ' '.encode('utf-8')

if byte_length > 16:
    remainder = byte_length % 16
    for i in range(16 - remainder):
        byte_string += ' '.encode('utf-8')

# byte_string = binascii.hexlify(byte_string)
# print("Hexadecimal string:", byte_string)
# print("Length of the string (in bytes):", byte_length)

# start generating key for encryption using AES
# each word is 4 bytes long entries are in hexadecimal
roundkeys = generate_keys()

# Necessary functions
def subBytes(state):
    for i in range(4):
        for j in range(4):
            state[i][j] = hex(int(Sbox[int(state[i][j], 16)]))[2:]
def shiftRows(state):
    for i in range(4):
        state[i] = state[i][1:] + [state[i][0]]

def mixColumns(state):
    for k in range(4):
        for i in range(4):
            x = 0
            for j in range(4):
                bv1 = BitVector(hexstring=state[j][i])
                bv2 = Mixer[i][j]
                bv3 = bv1.gf_multiply_modular(bv2, AES_modulus, 8)
                x = x ^ int(bv3.getHexStringFromBitVector(), 16)
            state[k][i] = hex(x)[2:]

def addRoundKey(state, r):
    for i in range(4):
        for j in range(4):
            state[i][j] = hex(int(state[i][j], 16) ^ int(roundkeys[r][i][j], 16))[2:]

encrypted = []
for i in range(byte_length//16):
    temp = byte_string[16*i:16*(i+1)]


# print(len(roundkeys))
# Create a TCP/IP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Define the server address and port
server_address = ('localhost', 8080)

# Connect to the server
client_socket.connect(server_address)

try:
    for i in range(len(encrypted)):
        # Send data to the server
        msg_key = (encrypted[i], byte_length)
        client_socket.sendall(str(msg_key).encode())
finally:
    # Close the connection
    client_socket.close()
