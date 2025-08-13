from hash import hash, hash256

## LET'S PLAY FIRST

ID = 0xABCDEEEE

TARGET = 0x000000000000000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF

# We want sha256(ID || nonce) < TARGET

# Let's compute this for some values:


nonce = 0x72EA5C  # int value

nonce = hex(nonce)  # for good conversions I want hex

to_hash = str(ID) + str(nonce)

h = hash(bytes(to_hash, encoding="utf-8"))

int_h = int(h.hex(), 16)

int_target = int(str(TARGET), 16)

if int_h < int_target:
    print("Good solution!")
else:
    print("You suck!")


# How do we automatize this?
# let's program a mining module that receives the following:
# ID, TARGET, min_nonce, max_nonce


def mine_asc(puzzle_id, target, min_nonce, max_nonce):
    # the mining module traverses the range min_nonce to max_nonce in ASCENDING ORDER
    # the values min_nonce and max_nonce are int
    # to mine like above, remember to convert min_nonce and max_nonce to hex
    # basically replicate the code above within a loop
    # remember that you might not find a solution -- signal this if you scanned the entire range
    for nonce in range(min_nonce, max_nonce + 1):
        nonce = hex(nonce)  # for good conversions I want hex

        to_hash = str(puzzle_id) + str(nonce)

        h = hash(bytes(to_hash, encoding="utf-8"))

        int_h = int(h.hex(), 16)

        int_target = int(str(target), 16)

        if int_h < int_target:
            return nonce


nonce = mine_asc(ID, TARGET, 0, 2**23 - 1)
print(nonce)  # 0x284d83

nonce = mine_asc(ID, 0x0000000000000000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF, 0, 2**23 - 1)
print(nonce)  # None

nonce = mine_asc(ID, 0x0000000000000000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF, 0, 2**24 - 1)
print(nonce)  # 0xe91f12


def mine_desc(puzzle_id, target, min_nonce, max_nonce):
    for nonce in range(max_nonce, min_nonce + 1, -1):
        nonce = hex(nonce)  # for good conversions I want hex

        to_hash = str(puzzle_id) + str(nonce)

        h = hash(bytes(to_hash, encoding="utf-8"))

        int_h = int(h.hex(), 16)

        int_target = int(str(target), 16)

        if int_h < int_target:
            return nonce


nonce = mine_desc(ID, TARGET, 0, 2**23 - 1)
print(nonce)  # 0x72ea5c


def mine_asc_with_double_hash_like_bitcoin(puzzle_id, target, min_nonce, max_nonce):
    for nonce in range(min_nonce, max_nonce + 1):
        nonce = hex(nonce)  # for good conversions I want hex

        to_hash = str(puzzle_id) + str(nonce)

        h = hash256(bytes(to_hash, encoding="utf-8"))

        int_h = int(h.hex(), 16)

        int_target = int(str(target), 16)

        if int_h < int_target:
            return nonce


nonce = mine_asc_with_double_hash_like_bitcoin(ID, TARGET, 0, 2**23 - 1)
print(nonce)  # 0x1fc165
