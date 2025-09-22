from hw2 import PrivateKey, Signature, hash256

def assertEqualStr(a, b):
    assert str(a) == str(b), f"{a} != {b}"

secret = hash256(b'BitcoinSucks')
intSecret = int(secret.hex(), 16)

privKey = PrivateKey(intSecret)

# Displaying the public key in the two SEC formats:
assertEqualStr(privKey.point.sec(False).hex(), '04852e3a8f4e64ee65624872095c466dccd460dcc85d4bab56ec2625b920677014d4895949efe57596ee4ed9bad45fb24b2a9df7686bb700e672f62a56860c1380')
assertEqualStr(privKey.point.sec(True).hex(), '02852e3a8f4e64ee65624872095c466dccd460dcc85d4bab56ec2625b920677014')

# Signing a message:
message = hash256(b'This course is boring!')
z = int(message.hex(), 16)

# signature = privKey.sign(z);
signature = Signature(
    0x1b8702e527b5410464649721cffdead50944c251fb09727f55e2c54e1e56def,
    0x2a44f56715d0d9d4fa086539d261219f415fb474a2b74136c43ca462a862eda9
)
assertEqualStr(privKey.point.verify(z, signature), True)

# What is the signature: raw vs DER
assertEqualStr(signature, 'Signature(1b8702e527b5410464649721cffdead50944c251fb09727f55e2c54e1e56def,2a44f56715d0d9d4fa086539d261219f415fb474a2b74136c43ca462a862eda9)')
assertEqualStr(signature.der().hex(), '3044022001b8702e527b5410464649721cffdead50944c251fb09727f55e2c54e1e56def02202a44f56715d0d9d4fa086539d261219f415fb474a2b74136c43ca462a862eda9')

# Bitcoin address assuming compressed SEC format for the public key
testnet = privKey.point.address(compressed=True, testnet=True)
mainnet = privKey.point.address(compressed=True, testnet=False)

assertEqualStr(testnet, 'mnWaVwJYCFKK3nCriPFfHD9wLKhz9RVbcy')
assertEqualStr(mainnet, '17zdCtDZPDt4GfjEzpHHTHwcUL7HBW6k2a')
print("All tests passed!")
