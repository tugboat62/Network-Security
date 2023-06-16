import socket

# Open the file in read mode
file = open('input.txt', 'r')

# Read the entire contents of the file
content = file.read()

# Close the file
file.close()

# Convert the string to bytes using a specific encoding (e.g., UTF-8)
byte_string = content.encode('utf-8')

# Get the length of the byte string
byte_length = len(byte_string)

if byte_length < 128:
    # append with a character that has no special or any control characters
    # or any of the characters that are used as separators
    for i in range(128 - byte_length):
        byte_string += ' '.encode('utf-8')

# start generating key for encryption using AES


# Create a TCP/IP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Define the server address and port
server_address = ('localhost', 8080)

# Connect to the server
client_socket.connect(server_address)

key = "1234567890123456"

try:
    while True:
        # Send data to the server
        message = input('Enter a message: ')
        client_socket.sendall(message.encode())
        # Receive the response from the server
        # data = client_socket.recv(1024)
        # print('Received:', data.decode())
        client_socket.sendall(key.encode())

finally:
    # Close the connection
    client_socket.close()
