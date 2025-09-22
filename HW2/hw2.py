import hmac
import hashlib


# hash160
def hash160(s: bytes) -> bytes:
    '''sha256 followed by ripemd160'''
    return hashlib.new('ripemd160', hashlib.sha256(s).digest()).digest()  # <1>


# double sha256
def hash256(s: bytes) -> bytes:
    '''two rounds of sha256'''
    return hashlib.sha256(hashlib.sha256(s).digest()).digest()


# the alhabet we use
BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


# compute base58 encoding of s (but not the checksum)
def encode_base58(s: bytes) -> str:
    count = 0
    for c in s:  # z
        if c == 0:
            count += 1
        else:
            break
    num = int.from_bytes(s, 'big')
    prefix = '1' * count
    result = ''
    while num > 0:  # <2>
        num, mod = divmod(num, 58)
        result = BASE58_ALPHABET[mod] + result
    return prefix + result  # <3>


class FieldElement:

    def __init__(self, num: int, prime: int):
        if num >= prime or num < 0:
            error = 'Num {} not in field range 0 to {}'.format(
                num, prime - 1)
            raise ValueError(error)
        self.num = num
        self.prime = prime

    def __repr__(self) -> str:
        return 'FieldElement_{}({})'.format(self.prime, self.num)

    def __eq__(self, other) -> bool:
        if other is None:
            return False
        return self.num == other.num and self.prime == other.prime

    def __ne__(self, other) -> bool:
        # this should be the inverse of the == operator
        return not (self == other)

    def __add__(self, other) -> 'FieldElement':
        if self.prime != other.prime:
            raise TypeError('Cannot add two numbers in different Fields')
        # self.num and other.num are the actual values
        # self.prime is what we need to mod against
        num = (self.num + other.num) % self.prime
        # We return an element of the same class
        return self.__class__(num, self.prime)

    def __sub__(self, other) -> 'FieldElement':
        if self.prime != other.prime:
            raise TypeError('Cannot subtract two numbers in different Fields')
        # self.num and other.num are the actual values
        # self.prime is what we need to mod against
        num = (self.num - other.num) % self.prime
        # We return an element of the same class
        return self.__class__(num, self.prime)

    def __mul__(self, other) -> 'FieldElement':
        if self.prime != other.prime:
            raise TypeError('Cannot multiply two numbers in different Fields')
        # self.num and other.num are the actual values
        # self.prime is what we need to mod against
        num = (self.num * other.num) % self.prime
        # We return an element of the same class
        return self.__class__(num, self.prime)

    def __pow__(self, exponent) -> 'FieldElement':
        n = exponent % (self.prime - 1)
        num = pow(self.num, n, self.prime)
        return self.__class__(num, self.prime)

    def __truediv__(self, other) -> 'FieldElement':
        if self.prime != other.prime:
            raise TypeError('Cannot divide two numbers in different Fields')
        # self.num and other.num are the actual values
        # self.prime is what we need to mod against
        # use fermat's little theorem:
        # self.num**(p-1) % p == 1
        # this means:
        # 1/n == pow(n, p-2, p)
        num = (self.num * pow(other.num, self.prime - 2, self.prime)) \
            % self.prime
        # We return an element of the same class
        return self.__class__(num, self.prime)

    def __rmul__(self, coefficient) -> 'FieldElement':
        num = (self.num * coefficient) % self.prime
        return self.__class__(num=num, prime=self.prime)


class Point:

    def __init__(self, x, y, a, b):
        self.a = a
        self.b = b
        self.x = x
        self.y = y
        # x being None and y being None represents the point at infinity
        # Check for that here since the equation below won't make sense
        # with None values for both.
        if self.x is None and self.y is None:
            return
        # make sure that the elliptic curve equation is satisfied
        # y**2 == x**3 + a*x + b
        if self.y**2 != self.x**3 + a * x + b:
            # if not, throw a ValueError
            raise ValueError('({}, {}) is not on the curve'.format(x, y))

    def __eq__(self, other) -> bool:
        return self.x == other.x and self.y == other.y \
            and self.a == other.a and self.b == other.b

    def __ne__(self, other) -> bool:
        # this should be the inverse of the == operator
        return not (self == other)

    def __repr__(self) -> str:
        if self.x is None:
            return 'Point(infinity)'
        elif isinstance(self.x, FieldElement):
            return 'Point({},{})_{}_{} FieldElement({})'.format(
                self.x.num, self.y.num, self.a.num, self.b.num, self.x.prime)
        else:
            return 'Point({},{})_{}_{}'.format(self.x, self.y, self.a, self.b)

    def __add__(self, other) -> 'Point':
        if not isinstance(other, Point):
            raise TypeError
        if self.a != other.a or self.b != other.b:
            raise TypeError(
                'Points {}, {} are not on the same curve'.format(self, other))
        # Case 0.0: self is the point at infinity, return other
        if self.x is None:
            return other
        # Case 0.1: other is the point at infinity, return self
        if other.x is None:
            return self

        # Case 1: self.x == other.x, self.y != other.y
        # Result is point at infinity
        if self.x == other.x and self.y != other.y:
            return self.__class__(None, None, self.a, self.b)

        # Case 2: self.x ≠ other.x
        # Formula (x3,y3)==(x1,y1)+(x2,y2)
        # s=(y2-y1)/(x2-x1)
        # x3=s**2-x1-x2
        # y3=s*(x1-x3)-y1
        if self.x != other.x:
            s = (other.y - self.y) / (other.x - self.x)
            x = s**2 - self.x - other.x
            y = s * (self.x - x) - self.y
            return self.__class__(x, y, self.a, self.b)

        # Case 4: if we are tangent to the vertical line,
        # we return the point at infinity
        # note instead of figuring out what 0 is for each type
        # we just use 0 * self.x
        if self == other and self.y == 0 * self.x:
            return self.__class__(None, None, self.a, self.b)

        # Case 3: self == other
        # Formula (x3,y3)=(x1,y1)+(x1,y1)
        # s=(3*x1**2+a)/(2*y1)
        # x3=s**2-2*x1
        # y3=s*(x1-x3)-y1
        if self == other:
            s = (3 * self.x**2 + self.a) / (2 * self.y)
            x = s**2 - 2 * self.x
            y = s * (self.x - x) - self.y
            return self.__class__(x, y, self.a, self.b)

        raise TypeError

    def __rmul__(self, coefficient: int) -> 'Point':
        coef = coefficient
        current = self
        result = self.__class__(None, None, self.a, self.b)
        while coef:
            if coef & 1:
                result += current
            current += current
            coef >>= 1
        return result


# a and b of secp256k1
A = 0
B = 7
# field order
P = 2**256 - 2**32 - 977
# subgroup order for secp256k1
N = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141


# instantiate the finite field needed for secp256k1
class S256Field(FieldElement):

    def __init__(self, num: int, prime=None):
        super().__init__(num=num, prime=P)

    def __repr__(self) -> str:
        return '{:x}'.format(self.num).zfill(64)

    # square root of the number
    def sqrt(self) -> 'S256Field':
        elem = self**((P + 1) // 4)
        return self.__class__(elem.num)


class Signature:

    def __init__(self, r, s):
        self.r = r
        self.s = s

    def __repr__(self) -> str:
        return 'Signature({:x},{:x})'.format(self.r, self.s)

    # DER fromat of a raw signature
    # You just return bytes (as usual)
    def der(self) -> bytes:
        return hash256(b'Not really!')


# point on secp256k1 curve
class S256Point(Point):

    def __init__(self, x, y, a=None, b=None):
        a, b = S256Field(A), S256Field(B)
        if type(x) is int:
            super().__init__(x=S256Field(x), y=S256Field(y), a=a, b=b)
        else:
            super().__init__(x=x, y=y, a=a, b=b)  # point at infinity

    def __repr__(self) -> str:
        if self.x is None:
            return 'S256Point(infinity)'
        else:
            return 'S256Point({}, {})'.format(self.x, self.y)

    # speeding up the scalar multiplication by modding with the group order
    def __rmul__(self, coefficient) -> 'S256Point':
        coef = coefficient % N  # mod by group order does the same thing
        point = super().__rmul__(coef)
        return self.__class__(point.x, point.y)

    # signature verification algorithm
    def verify(self, z: int, sig: Signature) -> bool:
        # By Fermat's Little Theorem, 1/s = pow(s, N-2, N)
        s_inv = pow(sig.s, N - 2, N)
        # u = z / s
        u = z * s_inv % N
        # v = r / s
        v = sig.r * s_inv % N
        # u*G + v*Pub should have as the x coordinate, r
        total = u * G + v * self
        return total.x.num == sig.r

    # return the point in sec format
    def sec(self, compressed=True) -> bytes:
        '''returns the binary version of the SEC format'''
        # The object you return has to be in bytes
        # Make sure that you use the correct endians
        # The compressed parameter tells you which version of SEC you'll be
        # using

        # To check that it works OK, you can code a parser for a SEC format
        # Then you go from a point to sec and back; if you get the same point
        # you're good
        return b'Not really!'

    # compute a Bitcoin address from public key in SEC format
    def address(self, compressed=True, testnet=False) -> str:
        '''Returns the address string'''
        # The compressed parameter tells us if we want compressed or
        # uncompressed SEC
        # The testnet parameter tells us whether we want a testnet of mainnet
        # address
        return 'Not really!'


G = S256Point(
    0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798,
    0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8)


class PrivateKey:

    def __init__(self, secret: int):
        self.secret = secret
        self.point: S256Point = secret * G

    def hex(self):
        return '{:x}'.format(self.secret).zfill(64)

    def sign(self, z) -> Signature:
        k = self.deterministic_k(z)
        # r is the x coordinate of the resulting point k*G
        r = (k * G).x.num
        # remember 1/k = pow(k, N-2, N)
        k_inv = pow(k, N - 2, N)
        # s = (z+r*secret) / k
        s = (z + r * self.secret) * k_inv % N
        if s > N / 2:
            s = N - s
        # return an instance of Signature:
        # Signature(r, s)
        return Signature(r, s)

    def deterministic_k(self, z) -> int:
        k = b'\x00' * 32
        v = b'\x01' * 32
        if z > N:
            z -= N
        z_bytes = z.to_bytes(32, 'big')
        secret_bytes = self.secret.to_bytes(32, 'big')
        s256 = hashlib.sha256
        k = hmac.new(k, v + b'\x00' + secret_bytes + z_bytes, s256).digest()
        v = hmac.new(k, v, s256).digest()
        k = hmac.new(k, v + b'\x01' + secret_bytes + z_bytes, s256).digest()
        v = hmac.new(k, v, s256).digest()
        while True:
            v = hmac.new(k, v, s256).digest()
            candidate = int.from_bytes(v, 'big')
            if candidate >= 1 and candidate < N:
                return candidate
            k = hmac.new(k, v + b'\x00', s256).digest()
            v = hmac.new(k, v, s256).digest()


if __name__ == '__main__':
    # ########TEST DATA########
    # Generating my private key:
    secret = hash256(b'BitcoinSucks')
    intSecret = int(secret.hex(), 16)

    privKey = PrivateKey(intSecret)

    # Displaying the public key in the two SEC formats:
    print('Uncompressed SEC format: ', privKey.point.sec(False).hex())
    print('Compressed sec format: ', privKey.point.sec(True).hex())

    # Signing a message:
    message = hash256(b'This course is boring!')
    z = int(message.hex(), 16)

    # signature = privKey.sign(z);
    signature = Signature(
        0x1b8702e527b5410464649721cffdead50944c251fb09727f55e2c54e1e56def,
        0x2a44f56715d0d9d4fa086539d261219f415fb474a2b74136c43ca462a862eda9
    )
    print(privKey.point.verify(z, signature))

    # What is the signature: raw vs DER
    print('Raw signature: ', signature)
    print('DER signature: ', signature.der().hex())  # always print as hex

    # Bitcoin address assuming compressed SEC format for the public key
    testnet = privKey.point.address(compressed=True, testnet=True)
    mainnet = privKey.point.address(compressed=True, testnet=False)

    print('Testnet address: ', testnet)
    print('Mainnet address: ', mainnet)

    # >>>Output of the above code should be:
    # Uncompressed SEC format:  04852e3a8f4e64ee65624872095c466dccd460dcc85d4bab56ec2625b920677014d4895949efe57596ee4ed9bad45fb24b2a9df7686bb700e672f62a56860c1380
    # Compressed sec format:  02852e3a8f4e64ee65624872095c466dccd460dcc85d4bab56ec2625b920677014
    # True
    # Raw signature:  Signature(1b8702e527b5410464649721cffdead50944c251fb09727f55e2c54e1e56def,2a44f56715d0d9d4fa086539d261219f415fb474a2b74136c43ca462a862eda9)
    # DER signature:  3044022001b8702e527b5410464649721cffdead50944c251fb09727f55e2c54e1e56def02202a44f56715d0d9d4fa086539d261219f415fb474a2b74136c43ca462a862eda9
    # Testnet address:  mnWaVwJYCFKK3nCriPFfHD9wLKhz9RVbcy
    # Mainnet address:  17zdCtDZPDt4GfjEzpHHTHwcUL7HBW6k2a
