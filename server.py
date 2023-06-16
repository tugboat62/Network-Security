import socket
import threading

# Create a TCP/IP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Define the server address and port
server_address = ('localhost', 8080)

# Bind the socket to the server address and port
server_socket.bind(server_address)

# Listen for incoming connections
server_socket.listen(5)

print('Server is up and running. Waiting for connections...')

def handle_client(client_socket):
    while True:
        # Receive data from the client
        data = client_socket.recv(1024)
        if data:
            print('Received:', data.decode())

            # Echo the received data back to the client
            client_socket.sendall(data)
        else:
            # No more data from client
            break

    # Close the connection
    client_socket.close()

while True:
    # Wait for a client connection
    client_socket, client_address = server_socket.accept()
    print('Received connection from:', client_address)

    # Create a new thread to handle the client
    client_thread = threading.Thread(target=handle_client, args=(client_socket,))
    client_thread.start()

