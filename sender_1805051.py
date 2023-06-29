import binascii
import pickle
import socket
import struct

from BitVector import *

from Miller_Rabin_1805051 import *
from bitvector_demo_1805051 import Sbox, Mixer, AES_modulus
from keys_1805051 import generate_keys

# Create a TCP/IP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Define the server address and port
server_address = ('localhost', 8080)
choice = input("Enter 1 for Diffie-Hellman or else for normal operation: ")
bits = input("Enter the number of bits for the key: ")
bits = int(bits)

if choice == '1':
    current = time.time()
    a = get_modulo(bits // 2)[0]
    duration = time.time() - current
    print("Time taken to generate a prime number(a):", duration)
    p, g = get_p_g(bits)
    A = square_multiply(g, a, p)
    duration = time.time() - current
    print("Time taken to generate A:", duration)
    # Connect to the server
    client_socket.connect(server_address)

    # Send data to the server
    client_socket.sendall(p.to_bytes((A.bit_length() + 7) // 8, 'big'))
    client_socket.sendall(g.to_bytes((A.bit_length() + 7) // 8, 'big'))
    client_socket.sendall(A.to_bytes((A.bit_length() + 7) // 8, 'big'))

    data = client_socket.recv(bits // 8)
    # Deserialize the received bytes into an integer
    B = int.from_bytes(data, 'big')
    print("Received:", B)

    key = square_multiply(B, a, p)
    duration = time.time() - current
    print("Time taken to generate key:", duration)

    client_socket.sendall(key.to_bytes((key.bit_length() + 7) // 8, 'big'))
    print("Private key:", key)
    data = client_socket.recv(1024)

    if(data.decode('utf-8') == "ok"):
        print("Keys matched")
    else:
        print("Keys didn't match")
        client_socket.close()
        exit()
    s = key.to_bytes((key.bit_length() + 7) // 8, 'big').hex()
    print("Key in hex:", s)
    s = bytes.fromhex(s).decode('unicode-escape')
    file = open("key.txt", "w", encoding="utf-8")
    file.write(s)
    file.close()
    # Close the socket
    client_socket.close()

# Open the file in read mode
file = open('input.txt', 'r')

# Read the entire contents of the file
content = file.read()
print("Plain text:")
print("In ASCII:", content)
file.close()
# Convert the string to bytes using a specific encoding (e.g., UTF-8)
byte_string = content.encode('utf-8')
# Get the length of the byte string
byte_length = len(byte_string)
print("In HEX:", binascii.hexlify(byte_string))

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

# start generating key for encryption using AES
# each word is (bits//8)//4 bytes long entries are in hexadecimal
roundkeys = generate_keys(bits)
columns = bits // 32

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
cur_time = time.time()
states = []
for i in range(byte_length // 16):
    temp = byte_string[16 * i:16 * (i + 1)]
    state = [[], [], [], []]
    for j in range(16):
        state[j % 4].append(temp[j])
    states.append(state)
# print(len(states))

if bits == 128:
    rounds = 11
elif bits == 192:
    rounds = 13
else:
    rounds = 15

for i in range(rounds):
    # print(states)
    for j in range(len(states)):
        if i == 0:
            addRoundKey(j, i)
            continue
        subBytes(j)
        shiftRows(j)
        if i != rounds-1:
            mixColumns(j)
        addRoundKey(j, i)
# print(states)

encrypted = []
hex_string = ""
ascii_string = ""
for i in range(len(states)):
    temp = []
    for j in range(4):
        for k in range(4):
            temp.append(states[i][k][j])
            hex_string += states[i][k][j]
            ascii_string += chr(int(states[i][k][j], 16))
    encrypted.append(temp)
encryption_time = time.time() - cur_time

print("\nCipher text:")
print("In HEX:", hex_string)
print("In ASCII:", ascii_string)

# print(len(roundkeys))

serialized = []

for i in range(len(encrypted)):
    ser_tuple = (encrypted[i], byte_length)
    serialized.append(pickle.dumps(ser_tuple))

print("\nEncryption time:", encryption_time, "seconds")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Connect to the server
client_socket.connect(server_address)

try:
    for i in range(len(encrypted)):
        # Send data to the server
        msg_key = (encrypted[i], byte_length)
        client_socket.sendall(struct.pack('!I', len(serialized[i])))
        client_socket.sendall(serialized[i])
finally:
    # Close the connection
    client_socket.close()
