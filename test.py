import binascii


# Convert string to hexadecimal string
string = "Hello, world!"
string += 'e'
print(string)
hex_string = binascii.hexlify(string.encode()).decode()

print("Hexadecimal string:", hex_string)

my_list = [1, 2, 3, 4, 5]
my_tuple = tuple(my_list)
print(my_tuple)

# Convert hexadecimal string to bytes
byte_string = binascii.unhexlify(hex_string.encode())

# Get the length of the byte string
byte_length = len(byte_string)

print("Length of the string (in bytes):", byte_length)
print(int('ff', 16))
