import pickle
import socket
import struct
import threading
from BitVector import *
from Miller_Rabin_1805051 import *
from bitvector_demo_1805051 import InvSbox, InvMixer, AES_modulus
from keys_1805051 import generate_keys

choice = input("Enter 1 for Diffie-Hellman or else for normal operation: ")
bits = input("Enter the number of bits: ")
bits = int(bits)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Define the server address and port
server_address = ('localhost', 8080)

# Bind the socket to the server address and port
server_socket.bind(server_address)

# Listen for incoming connections
server_socket.listen(5)

print('\nServer is up and running. Waiting for connections...')

if choice == '1':
    current = time.time()
    b = get_modulo(bits // 2)[0]
    duration = time.time() - current
    print("Time taken to generate a prime number(b):", duration)

    # Accept a client connection
    client_socket, client_address = server_socket.accept()
    print("Connected to:", client_address)
    current = time.time()

    # Receive data from the client
    data = client_socket.recv(bits // 8)
    p = int.from_bytes(data, 'big')
    data = client_socket.recv(bits // 8)
    g = int.from_bytes(data, 'big')
    data = client_socket.recv(bits // 8)
    A = int.from_bytes(data, 'big')

    B = square_multiply(g, b, p)
    duration = time.time() - current
    print("Time taken to generate B:", duration)
    print("B:", B)

    client_socket.sendall(B.to_bytes((B.bit_length() + 7) // 8, 'big'))

    key = square_multiply(A, b, p)
    duration = time.time() - current
    print("Time taken to generate key:", duration)

    data = client_socket.recv(bits // 8)
    # Deserialize the received bytes into an integer
    received_key = int.from_bytes(data, 'big')
    print("Private key:", key)
    print("Received key:", received_key)

    if key == received_key:
        print("Key exchange successful!")
        client_socket.sendall("ok".encode())
    else:
        print("Key exchange unsuccessful!")
        client_socket.sendall("not ok".encode())
        client_socket.close()
        exit()
    s = key.to_bytes((key.bit_length() + 7) // 8, 'big').hex()
    print("Key in hex:", s)
    s = bytes.fromhex(s).decode('unicode-escape')
    file = open("key.txt", "w", encoding='utf-8')
    file.write(s)
    file.close()
    # Close the client socket
    client_socket.close()

encrypted = []

roundkeys = generate_keys(bits)
# print(len(roundkeys))

states = []


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
        state[i] = state[i][4 - i:] + state[i][:4 - i]


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
    hex_string = ''
    # print('Len of states:', len(states))

    for i in range(len(states)):
        for j in range(4):
            for k in range(4):
                ch = states[i][k][j]
                hex_string += ch
                ch = chr(int(ch, 16))
                temp += ch
    print('\nDeciphered text from', client_address, ':')
    print('In HEX:', hex_string[:msglen])
    print('In ASCII:', temp[:msglen])


def decrypt(msglen):
    for i in range(len(encrypted)):
        temp = [[], [], [], []]
        for j in range(16):
            temp[j % 4].append(encrypted[i][j])
        states.append(temp)

    if bits == 128:
        rounds = 10
    elif bits == 192:
        rounds = 12
    else:
        rounds = 14

    for j in range(rounds, -1, -1):
        for i in range(len(states)):
            if j == rounds:
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
            cur_time = time.time()
            decrypt(msglen)
            print('Decryption Time:', time.time() - cur_time, 'seconds')
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
