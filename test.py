import binascii


# Convert string to hexadecimal string
string = "Hello, world!"
hex_string = binascii.hexlify(string.encode()).decode()

print("Hexadecimal string:", hex_string)

# Convert hexadecimal string to bytes
byte_string = binascii.unhexlify(hex_string.encode())

# Get the length of the byte string
byte_length = len(byte_string)

print("Length of the string (in bytes):", byte_length)
print(int('ff', 16))
