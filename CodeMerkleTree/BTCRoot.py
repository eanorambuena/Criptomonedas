from hash import *
import math


def merkle_parent(hash1, hash2):
    '''Takes the binary hashes and calculates the hash256'''
    # return the hash256 of hash1 + hash2
    return hash256(hash1 + hash2)


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



##BTC Specific stuff:

# As a side note
# In Bitcoin computing the Merkle root id done in little-big-little-endian fashion:
# 1) First, every binary hash is represented in little endian
#       For us, this would mean we would have to do something like:
#       raw_hashes = [bytes.fromhex(h) in hex_hashes]
#       input_hashes = [h[::-1] for h in raw_hashes]
# 2) The array input_hashes is processed left to right (i.e. like a big-endian)
# 3) The Merkle root is computed in big endian, but the value that is used in Bitcoin is little-endian
#       So we would need to return:
#       merkle_root(input_hashes)[::-1].hex()
# Go figure :)

# If you have the time, you can code this into your MerkleTree implementation as a constructor parameter
#   I.e. you coud have init(self,hashes,bitcoin=False), and if bitcoin = True do the above encoding



def BTCMerkle(hashes):

	input_hashes = [h[::-1] for h in hashes] # little endian all the bytes in each hash

	root = merkle_root(input_hashes) # compute as before, now the array is procesed left to right
	# IMPORTANT: in BTC if there is a single hash it is the root

	return root[::-1].hex() # little endian the result



# Block 100000 in Bitcoin:
# See e.g. https://btc.com/000000000003ba27aa200b1cecaad478d2b00432346c3f1f3986da1afd33e506

hex_hashes = ["8c14f0db3df150123e6f3dbbf30f8b955a8249b62ac1d1ff16284aefa3d06d87",
"fff2525b8931402dd09222c50775608f75787bd2b87e56995a7bdd30f79702c4",
"6359f0868171b1d194cbee1af2f16ea598ae8fad666d9b012c8ed2b79a236ec4",
" e9a66845e05d5abc0ad04ec80f774a7e585c6e8db975962d069a522137b80c1d"
]

raw = [bytes.fromhex(h) for h in hex_hashes]

print('The correct root :',BTCMerkle(raw))

print('No endians : ',merkle_root(raw).hex())