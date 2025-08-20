# Stuff we'll need to code our blockchain:
from hash import hash
import json  # this is for serializing blocks ... more on this in a bit

# What do we guard in a block?
# The data
# And the previous block hash

# Therefore our class will have the following:


class Block:
    def __init__(self, data):
        self.data = data
        self.prev_hash = None
        # An important note here: the block constructor will only set the data field
        # prev_hash value will be set by the blockchain class
        # If you do not like this, just extend the constructor; we will in fact do this a bit further ahead

    # To compute a hash of the entire block (data + prev hash) we need to convert it into bytes
    # Our approach is the following:
    # We will convert the Block object into a JSON document, and then convert this thing to bytes

    # The way we will serialize here (as opposed to the hashing exercize):
    # Why? Just to illustrate that many serializations are possible

    def serialize(self):
        if self.prev_hash == None:
            d = {"data": self.data}
        else:
            d = {"data": self.data, "prev_hash": self.prev_hash}
        return bytes(json.dumps(d, sort_keys=True).encode("utf-8"))
        # Strictly speaking, converting to bytes here is not necessary, as json dump is already in bytes
        # But this way it is more clear what is going on

    # We will also want to print blocks for debugging and checking results
    # So we will provide a method for this:

    def __str__(self):
        return "(Data: {} - Previous: {})".format(self.data, self.prev_hash)


# Let's create some blocks now, and see how they look

genesis = Block(0)
print(genesis)

genesis.prev_hash = "Is this dumb?"  # This is how to set the prev_hash field

print(genesis)

block1 = Block(hash(b"hola").hex())
print(block1)

# Next we move onto defining a blockchain class
# As stated in the class, a blockchain is a linked list of blocks
# To guard the blocks we will use a dictionary
# This will also allow us to implement hash pointers using the hash only (and no other piece of data)
# BTW this is, as far as I know, the only way people implement hash pointers these days

# Note that we could also use an array, and our hashpointers can consist of pairs (position,hash)


# Our blockchain clas will therefore guard blocks inside a dictionary (we'll call it elements)
# We will also remember the head of the chain at any given time
# As a side note; if you know what a 'fork' is, and are confused by our implementation, just be a bit patient


class Blockchain:
    def __init__(self):
        self.elements = {}
        self.head = None

    # Next, we need to enable adding the blocks to the blockchain
    # What happens here is that you will receive the data for the next block, and we will append it as the new head of the chain
    # Nothing compicated here:
    # Our method has the signature add_block(self,data)
    # 1) We receive the data
    # 2) We create a new block containing this data --> block = Block(data)
    # 3) We are always appending to the current head, so we just set block.prev_hash = self.head
    # 4) We also have to compute the hash of the block to add it to the elements dictionary
    # 		For this, we simply serialize the block --> block.serialize()
    # 		We compute the hash of this --> hash(block.serialize())
    # 		And we guard the hex value of this (to make things legible) --> hash(block.serialize()).hex()
    # 		We add our new block to the elements dictionary under this key

    # More precisely, we do something like the following:

    def add_block(self, data):
        block = Block(data)

        block.prev_hash = self.head  # first head is None by default

        serialize_to_hash = hash(block.serialize()).hex()  # compute the new key/i.e. the new hash pointer to the head
        self.elements[serialize_to_hash] = block  # insert the data in the dictionary under the computed key
        self.head = serialize_to_hash  # make the new hash pointer the head of the blockchain

    # We should be able to return the blockchain's head, so let us implement a method for this:

    def get_head(self):
        return self.head

    # We also need to print the entire blockchain
    # But this is easy, we can just scan the dictionary elements for this (it is already stored in the order of insertion)

    def print_blockchain(self):
        print("\n")
        for key in self.elements.keys():
            print("Key: {}".format(key))
            print("Block: {}".format(self.elements[key]))

    # Just a dummy function for now, will explain below
    def check(self, hash_pointer):
        return True


# Let's make a blockchain now:


blockchain = Blockchain()
blockchain.add_block("one")
# blockchain.elements = {h(bl1): bl1}
# blockchain.head = h(bl1)

blockchain.add_block("two")
# blockchain.elements = {h(bl1): bl1, h(bl2):bl2}
# blockchain.head = h(bl2)


blockchain.add_block("three")
# blockchain.elements = {h(bl1): bl1, h(bl2):bl2, h(bl3):bl3}
# blockchain.head = h(bl3)

blockchain.print_blockchain()

# The data itself can be anything:
blockchain.add_block(4)

blockchain.print_blockchain()

# A task for you: check if there are inconsistencies
# I.e. implement the following class method:

# def check(self, block_hash):
# The method receives the block_hash,
# and should follow hash pointers all the way to the first block in order to see if they were tampered with
# so you just have to: retrieve the block (check that it exists as well)
# hash it (you already saw how in the add_block)
# check that the hash matches
# get the prev_hash value
# continue till genesis

# here is some data to test your implementations:


# Insert data:

blockchain = Blockchain()
blockchain.add_block("one")
blockchain.add_block("42")
blockchain.add_block("three")
blockchain.add_block("44")

# Print:
blockchain.print_blockchain()

# Get head
x = blockchain.get_head()

# Check if valid
print(blockchain.check(x))

# Tamper with the data:
blockchain.elements[blockchain.elements[x].prev_hash].data = "1"
# Check again
print(blockchain.check(x))

# Some more test data:

blockchain_good = Blockchain()

blockchain_good.add_block("10")
blockchain_good.add_block("20")
blockchain_good.add_block("30")
blockchain_good.add_block("40")
blockchain_good.add_block("50")

blockchain_good.print_blockchain()

# Test with the third block
print(blockchain_good.check("83e18321fe0a34e69c94288d9d725cb9340dcf421db446bbf155d65a47956201"))


blockchain_bad = Blockchain()

blockchain_bad.add_block("11")
blockchain_bad.add_block("22")
blockchain_bad.add_block("33")
blockchain_bad.add_block("44")
blockchain_bad.add_block("55")

# Modifying the data of the third block
blockchain_bad.elements["770ca53c5b6d7d72ece11f56d53706331a7ffe5a2d67f81d7b97375c4d0e5146"].data = 34

blockchain_bad.print_blockchain()

# Test with the second and third block
print(blockchain_bad.check("dc92a16bc557bbddf0e16e0cbe341f1c7f08c5187b8b20338225be8c89816e9c"))
print(blockchain_bad.check("770ca53c5b6d7d72ece11f56d53706331a7ffe5a2d67f81d7b97375c4d0e5146"))

# test from head of thechain:
print(blockchain_bad.check("7d042ebae77f18ef5c9c48de337a12a86c141007fa0bbe4a003851b37cd7a5d7"))


blockchain_key_error = Blockchain()

blockchain_key_error.add_block("12")
blockchain_key_error.add_block("24")
blockchain_key_error.add_block("36")
blockchain_key_error.add_block("48")
blockchain_key_error.add_block("60")
blockchain_key_error.add_block("72")

blockchain_key_error.print_blockchain()

blockchain_key_error.elements[
    "a12349efcd4407932996a44dd56fd136710961314aaf29fe2f1ab7cf36adb1c1"
].prev_hash = "wrong key"

# Test with the head and the third block
print(blockchain_key_error.check("01d74f2fdee3805f55fdf6f767cf3ca61e53caf908fc4ae4805136c35cb2edea"))
print(blockchain_key_error.check("79203ae2f1b5ef3a70e93906be26a5f0540f0ad35adac5239dcf1350bcb07fd6"))
