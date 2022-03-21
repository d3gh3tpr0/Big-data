import random
import os
# low prime numbers to save time
lowPrimes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443,
             449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997]

temp_check = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41]
def generateLargePrime(keysize):
    """
        return random large prime number of keysize bits in size
    """

    while True:
        num = random.randrange(2 ** (keysize - 1), 2 ** keysize - 1)
        if (isPrime(num)):
            return num


def rabinMiller(n, d, a):
    #a = random.randint(2, (n - 2) - 2)
    x = pow(a, int(d), n)  # a^d%n
    if x == 1 or x == n - 1:
        return True

    # square x
    while d != n - 1:
        x = pow(x, 2, n)
        d *= 2

        if x == 1:
            return False
        elif x == n - 1:
            return True

    # is not prime
    return False


def isPrime(n):
    """
        return True if n prime
        fall back to rabinMiller if uncertain
    """

    # 0, 1, -ve numbers not prime
    if n < 2:
        return False

    # if in lowPrimes
    if n in lowPrimes:
        return True

    # if low primes divide into n
    for prime in lowPrimes:
        if n % prime == 0:
            return False

    # find number c such that 2 ^ r * d= n - 1
    d = n - 1  # c even because n not divisible by 2
    while d % 2 == 0:
        d /= 2  # make c odd
    #In this time, c 
    # prove not prime 128 times
    for a in temp_check:
        if not rabinMiller(n, d, a):
            return False

    return True


def generateKeys(keysize=1024):
    e = d = N = 0

    # get prime nums, p & q
    p = generateLargePrime(keysize)
    q = generateLargePrime(keysize)


    N = p * q  # RSA Modulus
    phiN = (p - 1) * (q - 1)  # totient

    # choose e
    # e is coprime with phiN & 1 < e <= phiN
    while True:
        e = random.randrange(2 ** (keysize - 1), 2 ** keysize - 1)
        if (isCoPrime(e, phiN)):
            break

    # choose d
    # d is mod inv of e with respect to phiN, e * d (mod phiN) = 1
    d = modularInv(e, phiN)

    return p, q, e, d, N


def isCoPrime(p, q):
    """
        return True if gcd(p, q) is 1
        relatively prime
    """

    return gcd(p, q) == 1


def gcd(p, q):
    """
        euclidean algorithm to find gcd of p and q
    """

    while q:
        p, q = q, p % q
    return p


def bezout(a, b):
    s = 0
    old_s = 1
    t = 1
    old_t = 0
    r = b
    old_r = a

    while r != 0:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t

    return old_r, old_s, old_t


def modularInv(a, b):
    gcd, x, y = bezout(a, b)

    if x < 0:
        x += b

    return x


class RSA(object):

    def __init__(self, keysize, keys):
        self.keysize = keysize
        keys = keys.split()
        keys = [int(keys[i]) for i in range(len(keys))]
        if (len(keys) == 2):
            self.e, self.N = keys
        if(len(keys) ==3):
            self.p, self.q, self.d = keys

    def encrypt(self, msg):
        cipher = ""

        for c in msg:
            m = ord(c)
            cipher += str(pow(m, self.e, self.N)) + " "

        return cipher
    
    def decrypt(self, cipher):
        msg = ""

        parts = cipher.split()
        for part in parts:
            if part:
                c = int(part)
                msg += chr(pow(c, self.d, self.N))

        return msg

    def encrypt_pixel(self, x):
        ans = pow(x, self.e, self.N)
        return ans

    def decrypt_pixel(self, x):
        ans = pow(x, self.d, self.N)
        return ans

def encrypt(auth_code, pub_keys):
    rsa = RSA(8, pub_keys)
    return rsa.encrypt(auth_code)

def decrypt(encrypted_code, pri_keys, N):
    rsa = RSA(8, pri_keys)
    rsa.N = N
    return rsa.decrypt(encrypted_code)


if __name__ == "__main__":

    #rsa = RSA(keysize=32)
    #enc = rsa.encrypt(msg=msg)
    #dec = rsa.decrypt(cipher=enc)
    

    
    choose = input("Encryption, decrpytion or generate keys?   E/D/G\t")
    if choose == "E":
        path_key = input("Input path file RSA pulic key:\t")
        path_plain = input("Input path file plain text:\t")
        file_keys = open(path_key, 'r')
        keys = file_keys.readline()
        file_keys.close()
        rsa = RSA(32, keys)
        file_plain = open(path_plain, 'r')
        file_encrypt = open("encrypted.txt", 'w')
        for line in file_plain.readlines():
            cipher = rsa.encrypt(line)
            file_encrypt.write(cipher)
        file_plain.close()
        file_encrypt.close()
        print("Done!")
            
    elif choose == "D":
        path_key = input("Input path file RSA private key:\t")
        path_pub = input("Input path file RSA public key:\t")
        path_cipher = input("Input path file cipher text:\t")
        file_keys = open(path_key, 'r')
        keys = file_keys.readline()
        file_keys.close()
        file_pub = open(path_pub, 'r')
        keys_pub = file_pub.readline().split()
        file_pub.close()
        
        rsa = RSA(32, keys)
        rsa.e, rsa.N = [int(keys_pub[i]) for i in range(len(keys_pub))]
        file_cipher = open(path_cipher, 'r')
        file_decrypt = open("decrypted.txt", 'w')
        for line in file_cipher.readlines():
            plain = rsa.decrypt(line)
            file_decrypt.write(plain)
        file_cipher.close()
        file_decrypt.close()
        print("Done!")
        
    elif choose == "G":
        p, q, e, d, N = generateKeys(keysize = 32)
        key_pri = str(p) + " " + str(q) + " " + str(d)
        key_pub = str(e) + " " + str(N)
        file_pri = open("rsa.txt", "w")
        file_pri.write(key_pri)
        file_pri.close()

        file_pub = open("rsa_pub.txt", 'w')
        file_pub.write(key_pub)
        file_pub.close()
        print("Done!")
    else:
        print("Syntax Error, the program is ending .....")
    
    
    
    
