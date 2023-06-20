import socket
import pickle
import struct
import threading
from BitVector import *
from bitvector_demo import InvSbox, InvMixer, AES_modulus
from keys import generate_keys

encrypted = []

roundkeys = generate_keys()
# print(len(roundkeys))

# Create a TCP/IP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

states = []

# Define the server address and port
server_address = ('localhost', 8080)

# Bind the socket to the server address and port
server_socket.bind(server_address)

# Listen for incoming connections
server_socket.listen(5)

print('Server is up and running. Waiting for connections...')


def addRoundKey(state, r):
    for i in range(4):
        for j in range(4):
            state[i][j] = hex(int(state[i][j], 16) ^ int(roundkeys[r][i][j], 16))[2:]

def invSubBytes(state):
    for i in range(4):
        for j in range(4):
            state[i][j] = hex(int(InvSbox[int(state[i][j], 16)]))[2:]

def invShiftRows(state):
    for i in range(1, 4):
        state[i] = state[i][4-i:] + state[i][:4-i]

def invMixColumns(state):
    mat = [[], [], [], []]
    for i in range(4):
        for j in range(4):
            mat[i].append(state[i][j])

    for i in range(4):
        for j in range(4):
            x = 0
            for k in range(4):
                bv1 = BitVector(hexstring=mat[k][j])
                bv2 = InvMixer[i][k]
                bv3 = bv1.gf_multiply_modular(bv2, AES_modulus, 8)
                x = x ^ int(bv3)
            state[i][j] = hex(x)[2:]

def printPlainText(msglen):
    temp = ''
    print('Len of states:', len(states))
    for i in range(len(states)):
        for j in range(4):
            for k in range(4):
                ch = states[i][k][j]
                ch = chr(int(ch, 16))
                temp += ch
    print('Decrypted text from client', client_address, ':', temp[:msglen])

def decrypt(msglen):
    for i in range(len(encrypted)):
        temp = [[], [], [], []]
        for j in range(16):
            temp[j % 4].append(encrypted[i][j])
        states.append(temp)


    for j in range(10, -1, -1):
        for i in range(len(states)):
            if j == 10:
                addRoundKey(states[i], j)
                continue
            invShiftRows(states[i])
            invSubBytes(states[i])
            addRoundKey(states[i], j)
            if j != 0:
                invMixColumns(states[i])

    printPlainText(msglen)


def receive_data(length):
    data = b''
    remaining = length
    while remaining > 0:
        chunk = client_socket.recv(remaining)
        if not chunk:
            break
        data += chunk
        remaining -= len(chunk)
    return data

def handle_client(client_socket):
    while True:
        length_data = receive_data(4)
        if not length_data:
            decrypt(msglen)
            break
        length = struct.unpack('!I', length_data)[0]
        serialized_tuple = receive_data(length)
        received_tuple = pickle.loads(serialized_tuple)
        msglen = received_tuple[1]
        encrypted.append(received_tuple[0])

    # Close the connection
    client_socket.close()


while True:
    # Wait for a client connection
    client_socket, client_address = server_socket.accept()
    print('Received connection from:', client_address)

    # Create a new thread to handle the client
    client_thread = threading.Thread(target=handle_client, args=(client_socket,))
    client_thread.start()
