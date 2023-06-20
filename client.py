import binascii
import socket
import pickle
import struct

from bitvector_demo import Sbox, Mixer, AES_modulus
from keys import generate_keys
from BitVector import *
from copy import copy

# Open the file in read mode
file = open('input.txt', 'r')

# Read the entire contents of the file
content = file.read()
# print("String to be encrypted:", content)
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

byte_string = [hex(byte)[2:] for byte in byte_string]
byte_length = len(byte_string)
# print(byte_length)

# byte_string = binascii.hexlify(byte_string)
# print("Hexadecimal string:", byte_string)
# print("Length of the string (in bytes):", byte_length)

# start generating key for encryption using AES
# each word is 4 bytes long entries are in hexadecimal
roundkeys = generate_keys()

# for i in range(11):
#     print(roundkeys[i])

# Necessary functions
def subBytes(n):
    for i in range(4):
        for j in range(4):
            states[n][i][j] = hex(int(Sbox[int(states[n][i][j], 16)]))[2:]
    # print(state)


def shiftRows(n):
    for i in range(4):
        states[n][i] = states[n][i][i:] + states[n][i][:i]
    # print(state)


def mixColumns(n):
    # print(states[n])
    mat = [[], [], [], []]
    for i in range(4):
        for j in range(4):
            mat[i].append(states[n][i][j])

    for i in range(4):
        for j in range(4):
            x = 0
            for k in range(4):
                bv1 = Mixer[i][k]
                bv2 = BitVector(hexstring=mat[k][j])
                bv3 = bv2.gf_multiply_modular(bv1, AES_modulus, 8)
                x = x ^ bv3.intValue()
            states[n][i][j] = hex(x)[2:]
    # print(states)


def addRoundKey(n, r):
    for i in range(4):
        for j in range(4):
            states[n][i][j] = hex(int(states[n][i][j], 16) ^ int(roundkeys[r][i][j], 16))[2:]
    # print(state)

states = []
for i in range(byte_length // 16):
    temp = byte_string[16 * i:16 * (i + 1)]
    state = [[], [], [], []]
    for j in range(16):
        state[j % 4].append(temp[j])
    states.append(state)
# print(len(states))

for i in range(11):
    # print(states)
    for j in range(len(states)):
        if i == 0:
            addRoundKey(j, i)
            continue
        subBytes(j)
        shiftRows(j)
        if i != 10:
            mixColumns(j)
        addRoundKey(j, i)
# print(states)

encrypted = []
for i in range(len(states)):
    temp = []
    for j in range(4):
        for k in range(4):
            temp.append(states[i][k][j])
    encrypted.append(temp)

# print(len(roundkeys))
# Create a TCP/IP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Define the server address and port
server_address = ('localhost', 8080)
serialized = []

for i in range(len(encrypted)):
    ser_tuple = (encrypted[i], byte_length)
    serialized.append(pickle.dumps(ser_tuple))

# print(len(serialized))

# Connect to the server
client_socket.connect(server_address)

try:
    for i in range(len(encrypted)):
        # Send data to the server
        print("Sending encrypted message to the server:", encrypted[i])
        msg_key = (encrypted[i], byte_length)
        client_socket.sendall(struct.pack('!I', len(serialized[i])))
        client_socket.sendall(serialized[i])
finally:
    # Close the connection
    client_socket.close()
