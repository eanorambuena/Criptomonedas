from hash import hash

data1 = b"Cryptocurrency"
hash1 = hash(data1)
print("Bytes: ", hash1)
hash1_hex = hash1.hex()
print("Hex:   ", hash1_hex)

data2 = b"cryptocurrency"
hash2 = hash(data2)
print("Bytes: ", hash2)
hash2_hex = hash2.hex()
print("Hex:   ", hash2_hex)
