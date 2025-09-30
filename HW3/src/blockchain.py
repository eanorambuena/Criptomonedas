import json
from keys import *  # noqa


def merkle_parent(hash1, hash2):
    '''Takes the binary hashes and calculates the hash256'''
    # return the hash256 of hash1 + hash2
    return hash256(hash1 + hash2)


def merkle_parent_level(hashes):
    '''Takes a list of binary hashes and returns a list that's half
    the length'''
    # if the list has exactly 1 element raise an error
    if len(hashes) == 1:
        raise RuntimeError('Cannot take a parent level with only 1 item')
    # if the list has an odd number of elements, duplicate the last one
    # and put it at the end so it has an even number of elements
    switch = 0  # to signal if we append an extra value
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
    # convert from hexadecimal to bytes to be able to hash
    current_level = [bytes.fromhex(h) for h in hashes]

    # loop until there's exactly 1 element
    while len(current_level) > 1:
        # current level becomes the merkle parent level
        current_level = merkle_parent_level(current_level)
    # return the 1st item of the current level
    return current_level[0].hex()


class Block:
    def __init__(self, tx_hashes, prev_hash):
        self.tx_hashes = tx_hashes  # these need to be in hex
        self.prev_hash = prev_hash  # prev hash in hex
        self.merkle_root = self.root()  # calculate merkle root for tx_hashes in the leaves
        self.ScroogeSig = privKeyScrooge.sign(
            int(hash(self.toSign()).hex(), 16))  # sign by Scrooge
        self.block_hash = self.id()  # compute the block hash

    def root(self):  # populate the Merkle tree with tx_hashes -- check max 2 hashes present
        assert len(
            self.tx_hashes) <= 2, "We have at most 2 transactions per block"
        return merkle_root(self.tx_hashes)

    def toSign(self):
        # merkle_root encodes all the leaf hashes, so no need to serialize these
        if self.prev_hash == None:
            d = {'root': self.merkle_root}
        else:
            d = {'root': self.merkle_root,
                 'prev_hash': self.prev_hash}
        return bytes(json.dumps(d, sort_keys=True).encode('utf-8'))

    def serialize(self):
        if self.prev_hash == None:
            d = {'root': self.merkle_root,
                 'sig': str(self.ScroogeSig)}
        else:
            d = {'root': self.merkle_root,
                 'prev_hash': self.prev_hash,
                 'sig': str(self.ScroogeSig)}
        return bytes(json.dumps(d, sort_keys=True).encode('utf-8'))

    # Transaction ID; this is our hash pointer in the UTXO set
    def id(self):
        '''Human-readable hexadecimal of the transaction hash'''
        return self.hash().hex()

    # Well, just the hash
    # Note that the hash is given in "little-endian"
    def hash(self):
        '''Binary hash of the legacy serialization'''
        return hash256(self.serialize())[::-1]

    def __str__(self):
        return '(Block Hash: {} Merkle Root: {} - Tx Hashes: {} - Previous Block: {}) \n'.format(
            self.block_hash,
            self.merkle_root,
            self.tx_hashes,
            self.prev_hash
        )


class Blockchain:
    def __init__(self):
        self.elements = {}
        self.head = None

    def add_block(self, block):

        if ((block.prev_hash in self.elements.keys()) or
                (len(self.elements.keys()) == 0) and (block.prev_hash == None)):

            self.elements[block.block_hash] = block
            self.head = block.block_hash

        else:
            return None

    def check(self, block_hash):
        if (block_hash not in self.elements.keys()):
            return False

        serialize_to_hash = self.elements[block_hash].id()
        if (block_hash != serialize_to_hash):
            return False

        current = self.elements[block_hash]
        while (current.prev_hash):
            if (current.prev_hash not in self.elements.keys()):
                return False

            serialize_to_hash = self.elements[current.prev_hash].id()
            if (current.prev_hash != serialize_to_hash):
                return False

            current = self.elements[current.prev_hash]

        return True

    def print_blockchain(self):
        for key in self.elements.keys():
            print('Key: {}'.format(key))
            print('Block: {}'.format(self.elements[key]))


if __name__ == '__main__':

    ##################
    ###### TEST ######
    ##################

    hex_hashes = [
        "9745f7173ef14ee4155722d1cbf13304339fd00d900b759c6f9d58579b5765fb",
        "5573c8ede34936c29cdfdfe743f7f5fdfbd4f54ba0705259e62f39917065cb9b"
    ]

    bl1 = Block(hex_hashes, None)

    bchain = Blockchain()
    bchain.add_block(bl1)

    bl2 = Block(
        ["5573c8ede34936c29cdfdfe743f7f5fdfbd4f54ba0705259e62f39917065cb9b"],
        '835f2fde84cd67b03d1391c2fdbe73b31d27af54b0d95485e90b799acbaccab5'
    )

    bchain.add_block(bl2)

    bchain.print_blockchain()

    print(bchain.check(
        '835f2fde84cd67b03d1391c2fdbe73b31d27af54b0d95485e90b799acbaccab5'
    ))

    print(bchain.head)
