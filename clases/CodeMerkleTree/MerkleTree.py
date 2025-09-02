# Most of the code is taken from Jimmy Song's book 'Programming Bitcoin'
# All trees are constructed with hashes only, and not the raw data
# If you want to implement them with raw data, you just add one extra level

from hash import *
import math

# How do we calculate a parent node of two children nodes?
# Well, we just take their hashes, concatenate them, and hash again
# In Bitcoin one uses hash256(x) = hash(hash(x)) = sha256(sha256(x))
# The reason: Satoshi did it like that and we need backwards compatibility
# A more secure solution would be to use sha256(x + sha256(x)), but hey... 

def merkle_parent(hash1, hash2):
    '''Takes the binary hashes and calculates the hash256'''
    # return the hash256 of hash1 + hash2
    return hash256(hash1 + hash2)

# Let's compute some parents

hex_hashes = [
     'ba412a0d1480e370173072c9562becffe87aa661c1e4a6dbc305d38ec5dc088a',
     '7cf92e6458aca7b32edae818f9c2c98c37e06bf72ae0ce80649a38655ee1e27d',
     '34d9421d940b16732f24b94023e9d572a7f9ab8023434a4feb532d2adfc8c2c2',
     '158785d1bd04eb99df2e86c54bc13e139862897217400def5d72c280222c4cba'
]

# As we will be hashing, we need to convert this to bytes

raw_hashes = [bytes.fromhex(x) for x in hex_hashes] 
# Yes, I hate lambda calculus as well, this is just bad coding, sorry Python

# Let's compute some parents:

papa = merkle_parent(raw_hashes[0],raw_hashes[1])

print('Merkle parent of first two hashes: ',papa.hex())



# Using the Merkle Parent function we can compute the entire Parent level for any level in a Merkle tree
# We stop when we reach a single hash

def merkle_parent_level(hashes):
    '''Takes a list of **binary** hashes and returns a list that's half
    the length'''
    # if the list has exactly 1 element raise an error
    if len(hashes) == 1:
        raise RuntimeError('Cannot take a parent level with only 1 item')
    # if the list has an odd number of elements, duplicate the last one
    # and put it at the end so it has an even number of elements
    switch = 0 # This is used to signal if we append an extra value
    if len(hashes) % 2 == 1:
        switch = 1
        hashes.append(hashes[-1])
    # initialize next level
    parent_level = []
    # loop over every pair (use: for i in range(0, len(hashes), 2))
    for i in range(0, len(hashes), 2):
        # get the merkle parent of the hashes at index i and i+1
        parent = merkle_parent(hashes[i], hashes[i + 1])
        # append parent to parent level
        parent_level.append(parent)
    # return parent level, remove the extra stuff for consistency 
    if (switch == 1):
        hashes.pop(-1)
    return parent_level

# OK, so we can now compute the entire parent level

parent_level = merkle_parent_level(raw_hashes)

print('\nPrinting the parent level:')
for x in parent_level:
	print(x.hex())
print('\n')

# What we really need is the Merkle Root, as this one has all the necessary information
# We construct it by applying the merkle_parent_level() function until we reach a single hash

def merkle_root(hashes):
    '''Takes a list of binary hashes and returns the merkle root
    '''
    # current level starts as hashes
    current_level = hashes
    # loop until there's exactly 1 element
    while len(current_level) > 1:
        # current level becomes the merkle parent level
        current_level = merkle_parent_level(current_level)
    # return the 1st item of the current level
    return current_level[0]

# We can now compute a Merkle root of our list of hashes

root = merkle_root(raw_hashes)

print('The root is: ',root.hex())

# We can also check this manually:

root2 = merkle_parent(parent_level[0],parent_level[1])
print('Checking equality: ',root == root2)

# We can also check if our implementation works for an odd number of hashes

hex_hashes = [
     'ba412a0d1480e370173072c9562becffe87aa661c1e4a6dbc305d38ec5dc088a',
     '7cf92e6458aca7b32edae818f9c2c98c37e06bf72ae0ce80649a38655ee1e27d',
     '34d9421d940b16732f24b94023e9d572a7f9ab8023434a4feb532d2adfc8c2c2',
     '158785d1bd04eb99df2e86c54bc13e139862897217400def5d72c280222c4cba',
     'ee7261831e1550dbb8fa82853e9fe506fc5fda3f7b919d8fe74b6282f92763ce'
]

raw_hashes = [bytes.fromhex(x) for x in hex_hashes]

print('\nThe new root: ',merkle_root(raw_hashes).hex(),'\n')

# We can also define the MerkleTree class now

class MerkleTree:
    '''This is the full Merkle tree class
    As stated previously, we really just need to guard the hashes
    No need to guard all the intermediate nodes
    To speed up accessing the root, we will also compute the root of the tree
    '''
    def __init__(self, hashes):
        self.hashes = hashes
        self.root = merkle_root(hashes)


    def __str__(self):
        tmp = ''
        print('\nPrinting the merkle tree level by level:')
        current_level = self.hashes

        items = ''

        for h in current_level:
            if (h == None):
                short = h
            else:
                short = '{}... '.format(h.hex()[:8])
            tmp = tmp + short
        items = tmp

        while len(current_level) > 1:
            tmp = ''
            current_level = merkle_parent_level(current_level)
            for h in current_level:
                if (h == None):
                    short = h
                else:
                    short = '{}... '.format(h.hex()[:8])
                tmp = tmp + short
            tmp = tmp + '\n'
            items = tmp + items
        
        return items          


# We can now create a tree and print it bottom up

tree = MerkleTree(raw_hashes)
print(tree)

# Block 100000 in Bitcoin:
# See e.g. https://btc.com/000000000003ba27aa200b1cecaad478d2b00432346c3f1f3986da1afd33e506

hex_hashes = ["8c14f0db3df150123e6f3dbbf30f8b955a8249b62ac1d1ff16284aefa3d06d87",
"fff2525b8931402dd09222c50775608f75787bd2b87e56995a7bdd30f79702c4",
"6359f0868171b1d194cbee1af2f16ea598ae8fad666d9b012c8ed2b79a236ec4",
" e9a66845e05d5abc0ad04ec80f774a7e585c6e8db975962d069a522137b80c1d"
]

raw = [bytes.fromhex(h) for h in hex_hashes]


print('\n\nRoot of BTC block 100000: ',merkle_root(raw).hex())

# As a side note
# In Bitcoin computing the Merkle root id done in little-big-little-endian fashio:
# 1) First, every binary hash is represented in little endian
#       For us, this would mean we would have to do something like:
#       raw_hashes = [bytes.fromhex(h) in hex_hashes]
#       input_hashes = [h[::-1] for h in raw_hashes]
# 2) The array input_hashes is processed left to right (i.e. like a big-endian)
# 3) The Merkle root is computed in big endian, but the value that is used in Bitcoin is little.endian
#       So we would need to return:
#       merkle_root(input_hashes)[::-1].hex()
# Go figure :)

# If you have the time, you can code this into your MerkleTree implementation as a constructor parameter
#   I.e. you coud have init(self,hashes,bitcoin=False), and if bitcoin = True do the above encoding
