import random
import time


# OK tested
def is_prime(n, k=5):
    # Miller-Rabin primality test
    if n == 2 or n == 3:
        return True
    if n <= 1 or n % 2 == 0:
        return False

    # Write (n-1) as 2^r * d
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    # Perform Miller-Rabin test k times
    for _ in range(k):
        a = random.randint(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def generate_prime(bits):
    # Generate a random number with the specified number of bits
    while True:
        n = random.getrandbits(bits)
        # Set the most significant and least significant bits to 1
        n |= (1 << bits - 1) | 1
        if is_prime(n):
            return n


def get_modulo(bits=128):
    # Example usage
    while True:
        prime_number = generate_prime(bits)
        phi_n = prime_number - 1
        prime_factors = [2]
        k = phi_n // 2
        if is_prime(k):
            prime_factors.append(k)
            return prime_number, prime_factors


# Function to square the multiply
def square_multiply(base, exp, mod):
    b = 1
    A = base % mod
    if exp & 1:
        b = base % mod
    exp >>= 1
    while exp > 0:
        A = (A * A) % mod
        if exp & 1:
            b = (A * b) % mod
        exp >>= 1
    return b % mod


def is_primitive_root(g, p, prime_factors):
    for i in prime_factors:
        if square_multiply(g, (p - 1) // i, p) == 1:
            return False
    return True


def get_primitive_root(p, prime_factors):
    while True:
        g = random.randint(2, p - 1)
        if is_primitive_root(g, p, prime_factors):
            return g


def get_p_g(bits=128):
    current = time.time()
    p, prime_factors = get_modulo(bits)
    duration = time.time() - current
    print("Time taken to generate prime number(p):", duration)
    g = get_primitive_root(p, prime_factors)
    duration = time.time() - current
    print("Time taken to generate primitive root(g):", duration)
    return p, g
