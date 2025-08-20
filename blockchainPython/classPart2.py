# OK, what was all that forking bussiness?
# Well, it's basically not a list, but a treeish thing (SLIDES)

# So how do we implement that?
# It's basically the same, but now we define the prev_hash part of the block explicitly:


class Block:
    def __init__(self, data, prev_hash=None):
        self.data = data
        self.prev_hash = prev_hash

    def serialize(self):
        if self.prev_hash == None:
            d = {"data": self.data}
        else:
            d = {"data": self.data, "prev_hash": self.prev_hash}
        return bytes(json.dumps(d, sort_keys=True).encode("utf-8"))

    def __str__(self):
        return "(Data: {} - Previous: {})".format(self.data, self.prev_hash)


# So now we can assume no head is explicity available:


class Blockchain:
    def __init__(self):
        self.elements = {}

    def add_block(self, block):
        # This is for you to implement
        # Assume only one genesis block is available
        # Now you do not extend, just add it in if it is valid (i.e. prev_hash exists)
        # The function should return the hash of the current block, just so that we know what it is!!!!!!!!!!!!!!!!!!!!!!!
        
        if block.prev_hash is None:
            return None
            
        if block.prev_hash  not in self.elements:
            return None
        
        self.elements[block.prev_hash].children.append(block)
        self.elements[block.hash] = block
        return block.hash

    def check(self, hash_pointer):
        if hash_pointer is None:
            return True
        
        if hash_pointer not in self.elements:
            return False

        block = self.elements[hash_pointer]
        real_block_hash = hash(block.serialize()).hex()
        if real_block_hash != hash_pointer:
            return False

        return self.check(block.prev_hash)

    # Printing is just printing
    def print_blockchain(self):
        for key in self.elements.keys():
            print("Key: {}".format(key))
            print("Block: {}".format(self.elements[key]))


# Let us create a chain with these things in mind:

#############
##EXAMPLE 1##
#############

blockchain = Blockchain()

genesis = Block("1", None)
prev = blockchain.add_block(genesis)
bl1 = Block("2", prev)
prev2 = blockchain.add_block(bl1)
bl2 = Block("3", prev2)
prev3 = blockchain.add_block(bl2)
bl3 = Block("4", prev3)
prev4 = blockchain.add_block(bl3)

print(blockchain.check(prev4))

# Let's do a fork
bl4 = Block("88", prev)
prev4 = blockchain.add_block(bl4)

# See what's up:
print(blockchain.check(prev4))

#############
##EXAMPLE 2##
#############

blockchain_bueno = Blockchain()

genesis = Block("genesis", None)
hash_g = blockchain_bueno.add_block(genesis)
bl1 = Block("10", hash_g)
hash_1 = blockchain_bueno.add_block(bl1)
bl2 = Block("20", hash_1)
hash_2 = blockchain_bueno.add_block(bl2)
bl3 = Block("30", hash_2)
hash_3 = blockchain_bueno.add_block(bl3)

# First branch
bl3_1 = Block("30 - 1", hash_3)
hash_3_1 = blockchain_bueno.add_block(bl3_1)
bl4_1 = Block("40 - 1", hash_3_1)
hash_4_1 = blockchain_bueno.add_block(bl4_1)


# Second branch (i.e. first fork)
bl3_2 = Block("30 - 2", hash_3)
hash_3_2 = blockchain_bueno.add_block(bl3_2)
bl4_2 = Block("40 - 2", hash_3_2)
hash_4_2 = blockchain_bueno.add_block(bl4_2)

blockchain_bueno.print_blockchain()

# Test with the two heads
print(blockchain_bueno.check(hash_4_1))
print(blockchain_bueno.check(hash_4_2))


#############
##EXAMPLE 3##
#############


blockchain_malo = Blockchain()

genesis = Block("genesis", None)
hash_g = blockchain_malo.add_block(genesis)
bl1 = Block("10", hash_g)
hash_1 = blockchain_malo.add_block(bl1)
bl2 = Block("20", hash_1)
hash_2 = blockchain_malo.add_block(bl2)
bl3 = Block("30", hash_2)
hash_3 = blockchain_malo.add_block(bl3)

bl3_1 = Block("30 - 1", hash_3)
hash_3_1 = blockchain_malo.add_block(bl3_1)

# First tampering
bl3_1.data = "30 - 1 - corrupted"

# A good branch
bl3_2 = Block("30 - 2", hash_3)
hash_3_2 = blockchain_malo.add_block(bl3_2)

# Continue the bad branch
bl4_1 = Block("40 - 1", hash_3_1)
hash_4_1 = blockchain_malo.add_block(bl4_1)

# Continue the good branch
bl4_2 = Block("40 - 2", hash_3_2)
hash_4_2 = blockchain_malo.add_block(bl4_2)

blockchain_malo.print_blockchain()

# Test with the two heads
print(blockchain_malo.check(hash_4_1))  # Bad
print(blockchain_malo.check(hash_4_2))  # Good

#############
##EXAMPLE 3##
#############


blockchain_malo_doble = Blockchain()

genesis = Block("genesis", None)
hash_g = blockchain_malo_doble.add_block(genesis)
bl1 = Block("10", hash_g)
hash_1 = blockchain_malo_doble.add_block(bl1)
bl2 = Block("20", hash_1)
hash_2 = blockchain_malo_doble.add_block(bl2)
bl3 = Block("30", hash_2)
hash_3 = blockchain_malo_doble.add_block(bl3)

bl3_1 = Block("30 - 1", hash_3)
hash_3_1 = blockchain_malo_doble.add_block(bl3_1)

# Branch 1 corrupted
bl3_1.data = "30 - 1 - corrupted"

bl3_2 = Block("30 - 2", hash_3)
hash_3_2 = blockchain_malo_doble.add_block(bl3_2)

bl4_1 = Block("40 - 1", hash_3_1)
hash_4_1 = blockchain_malo_doble.add_block(bl4_1)
bl4_2 = Block("40 - 2", hash_3_2)
hash_4_2 = blockchain_malo_doble.add_block(bl4_2)

# Branch 2 corrupted
bl4_2.data = "40 - 2 - corrupted"

bl5_2 = Block("50 - 2", hash_4_2)
hash_5_2 = blockchain_malo_doble.add_block(bl5_2)

blockchain_malo_doble.print_blockchain()

# Test with the two heads
print(blockchain_malo_doble.check(hash_4_1))
print(blockchain_malo_doble.check(hash_5_2))

#############
##EXAMPLE 4##
#############


blockchain_malo_root = Blockchain()

genesis = Block("genesis", None)
hash_g = blockchain_malo_root.add_block(genesis)
bl1 = Block("10", hash_g)
hash_1 = blockchain_malo_root.add_block(bl1)
bl2 = Block("20", hash_1)
hash_2 = blockchain_malo_root.add_block(bl2)

# Branch root corrupted
bl2.data = "20 - corrupted"

bl3 = Block("30", hash_2)
hash_3 = blockchain_malo_root.add_block(bl3)

bl3_1 = Block("30 - 1", hash_3)
hash_3_1 = blockchain_malo_root.add_block(bl3_1)

bl3_2 = Block("30 - 2", hash_3)
hash_3_2 = blockchain_malo_root.add_block(bl3_2)

bl4_1 = Block("40 - 1", hash_3_1)
hash_4_1 = blockchain_malo_root.add_block(bl4_1)
bl4_2 = Block("40 - 2", hash_3_2)
hash_4_2 = blockchain_malo_root.add_block(bl4_2)

bl5_2 = Block("50 - 2", hash_4_2)
hash_5_2 = blockchain_malo_root.add_block(bl5_2)

blockchain_malo_root.print_blockchain()

# Test with the two heads
print(blockchain_malo_root.check(hash_4_1))
print(blockchain_malo_root.check(hash_5_2))
