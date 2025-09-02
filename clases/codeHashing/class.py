from hash import hash

## LET'S PLAY FIRST

ID = 0xABCDEEEE
TARGET = 0x000000000000000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF

# We want sha256(ID || nonce) < TARGET

# Let's compute this for some values:

nonce = 0  # int value

nonce = hex(nonce)  # for good conversions I want hex

to_hash = str(ID) + str(nonce)
h = hash(bytes(to_hash, encoding="utf-8"))

int_h = int(h.hex(), 16)
int_target = int(str(TARGET), 16)

if int_h < int_target:
    print("Good solution!")
else:
    print("You suck!")


# A good solution:
nonce = 0x72EA5C  # still int for python (you suck python!!!)
nonce = hex(nonce)

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

# def mine_asc(puzzle_id, target, min_nonce, max_nonce):
# the mining module traverses the range min_nonce to max_nonce in ASCENDING ORDER
# the values min_nonce and max_nonce are int
# to mine like above, remember to convert min_nonce and max_nonce to hex
# basically replicate the code above within a loop
# remember that you might not find a solution -- signal this if you scanned the entire range

# now run your mining function on:

ID = 0xABCDEEEE
TARGET = 0x000000000000000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
c = 2**23  # nonce size
min = 0  # smallest nonce
max = c - 1  # biggest nonce

# implement descending mining:
# def mine_desc(puzzle_id, target, min_nonce, max_nonce):
# same as above, but now you go from max_nonce down to min_nonce

# now run your descending mining function on (same as above):

ID = 0xABCDEEEE
TARGET = 0x000000000000000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
c = 2**23  # nonce size
min = 0  # smallest nonce
max = c - 1  # biggest nonce

# Notice something?

# implement random mining: pick a nonce in the range randomly
# def mine_rand(puzzle_id, target, min_nonce, max_nonce):
# recall that there mighn not be a solution, so count up to max_nonce-min_nonce, after you did as many attempts give up

# run mine_rand() with the same parameters as above
# run it several times, do the results change? do you notice that sometimes it will pick up the min/max solution?

# Let's increase the puzzle difficulty now:
ID = 0xABCDEEEE
TARGET = 0x0000000000000000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
c = 2**23  # nonce size
min = 0  # smallest nonce
max = c - 1  # biggest nonce

# Looks like our nonce range will not do here;
# we either have to lower the difficulty back to the original one, or change the puzzle_id

# Let's play with some other parameters:

ID = 0xAAAAAAAA
TARGET = 0x000000000000000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
c = 2**23
min = 0
max = c - 1

# what is faster? asc? desc? rand? Did you try rand at least 5 times?

# Let's play with the parameters some more:
ID = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
TARGET = 0x000000000000000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
c = 2**23
min = 0
max = c - 1

# What is fastest here?

# Let us now go to the Bitcoin's nonce of 32 bits:

ID = 0xFAA
TARGET = 0x0000000000000000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
c = 2**32
min = 0
max = c - 1

# Try mining in descending order first
# You should get nonce = 0xff2a9f50 as a solution in about (50 sec - 2min, depending on your cpu)
# Try mining in ascending order
# solution = 0x14a822c takes a bit longer
# Let's try rand for a few minutes?
# Found: 0xcadf6421 with rand in 4 min -- significantly slower

# What do miners actually do?


# One interesting trick:
# Same puzzle as before, but let us try a different range of all 32 bit nonces:
# Let us mine in ascending order now

ID = 0xFAA
TARGET = 0x0000000000000000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
c = 2**32
min = (11 * c) // 12
max = c - 1

# What happened here?

# Let's simulate a mining pool:
ID = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
TARGET = 0x0000000000000000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
c = 2**32

# Group1:
min = (11 * c) // (12)
max = c - 1

# Group2:
min = (10 * c) // (12)
max = (11 * c) // (12) - 1

# Group3:
min = (9 * c) // (12)
max = (10 * c) // (12) - 1

# Group4:
min = (8 * c) // (12)
max = (9 * c) // (12) - 1

# Group5:
min = (7 * c) // (12)
max = (8 * c) // (12) - 1

# Group6:
min = (6 * c) // (12)
max = (7 * c) // (12) - 1

# Group7:
min = (5 * c) // (12)
max = (6 * c) // (12) - 1

# Group8:
min = (4 * c) // (12)
max = (5 * c) // (12) - 1

# Group9:
min = (3 * c) // (12)
max = (4 * c) // (12) - 1

# Group10:
min = (2 * c) // (12)
max = (3 * c) // (12) - 1

# Group11:
min = (1 * c) // (12)
max = (2 * c) // (12) - 1

# Group12:
min = 0
max = (1 * c) // (12) - 1

##One thing I lied about: Real nonce is of fixed size;
# so always 32 bits for example, and not an int range;
# we were actually wastefull, as 0x0 and 0x0000 are not the same for hashing (sha256 sees them as bytes)
# you can try to implement this as an exercise; and please send me a solution, so <i don't need to do it on my own :-)
