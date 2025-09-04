# Most of the code is taken from Jimmy Song's book 'Programming Bitcoin'
# All trees are constructed with hashes only, and not the raw data
# If you want to implement them with raw data, you just add one extra level

from hash import *
import math

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
    switch = 0 # to signal if we append an extra value
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

class MerkleProof:
    def __init__(self, hashesOfInterest, nrLeaves=None, flags=None, hashes=None):
        self.hashesOfInterest = hashesOfInterest
        self.nrLeaves = nrLeaves
        self.flags = flags
        self.hashes = hashes    


class MerkleTree:
    '''This is the full Merkle tree class
    As stated previously, we really just need to guard the hashes (ordered)
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



    def generate_proof(self,hashesOfInterest):
        '''
        HW1: Implement the function that generates the flag bits for hashesOfInterest in the received list
        And also the missing hashes needed to show that 
        If any of the hashes is absent from the leaves of the tree, just throw an error
        Returns an object of class MerkleProof
        !!!hashesOfInterest are always assumed to be leaves of the Merkle tree!!!
        '''
        #return True

        treeSize = len(self.hashes)
        nrLeaves = math.log2(treeSize)
        print(treeSize, nrLeaves)

        return MerkleProof(hashesOfInterest)

class MerkleProof:
    def __init__(self, hashesOfInterest, nrLeaves = None, flags = None, hashes = None):
        self.hashesOfInterest = hashesOfInterest
        self.nrLeaves = nrLeaves
        self.flags = flags
        self.hashes = hashes



class SortedTree:
    '''
    This will be a sorted Merkle Tree which will allow a proof of non-inclusion
    Copy/paste any method from the other classes that you will need

    '''

    def __init__(self, hashes):
        self.hashes = sorted(hashes)
        self.tree = MerkleTree(self.hashes)
        # Calcular todos los niveles
        self.levels = [self.hashes]
        current = self.hashes
        while len(current) > 1:
            current = merkle_parent_level(current)
            self.levels.append(current)
        # Asignar nombres cortos a todos los hashes
        all_hashes = []
        for level in self.levels:
            all_hashes.extend(level)
        self.hash_to_name = {}
        names = [chr(97 + i) for i in range(len(all_hashes))]  # a, b, c, ..., z, aa, ab, etc.
        for i, h in enumerate(all_hashes):
            name = names[i % 26] + (names[i // 26] if i >= 26 else "")
            self.hash_to_name[h] = name

    def generate_proof(self, hashesOfInterest):
        max_depth = math.ceil(math.log2(len(self.hashes)))
        flags = []
        hashes_list = []
        added_hashes = set()
        for h in hashesOfInterest:
            if h not in self.hashes:
                continue
            print(f"\n--- Procesando hash: {str_human(h)} ---")
            print("Árbol con hoja marcada:")
            print_tree(sorted_tree, h)
            pos = self.hashes.index(h)
            current = pos
            for d in range(max_depth):
                sibling = current ^ 1  # XOR para obtener el sibling
                if sibling < len(self.hashes) and self.hashes[sibling] not in added_hashes:
                    flags.append(1)
                    hashes_list.append(self.hashes[sibling])
                    added_hashes.add(self.hashes[sibling])
                    print(f"Agregado sibling: {str_human(self.hashes[sibling])}, Flag: 1")
                elif sibling >= len(self.hashes):
                    flags.append(0)
                    print(f"Sibling no existe, Flag: 0")
                current //= 2
            print(f"Flags acumulados: {flags}")
            print(f"Hashes acumulados: {[str_human(hh) for hh in hashes_list]}")
        # Agregar root si no está incluido
        if self.hashes[0] not in added_hashes:
            flags.append(1)
            hashes_list.append(self.hashes[0])
            print(f"Agregado root: {str_human(self.hashes[0])}, Flag: 1")
        print(f"Prueba final - Flags: {flags}, Hashes: {[str_human(hh) for hh in hashes_list]}")
        return MerkleProof(hashesOfInterest, len(self.hashes), flags, hashes_list)

    def proof_of_non_inclusion(self, hash):
        '''
        HW1: Implement the function that generates a proof of non inclusion for a single hash
        !!!the hash is assumed to be a leaf of the Merkle tree!!! 
        '''
        if hash in self.hashes:
            return None
        import bisect
        pos = bisect.bisect_left(self.hashes, hash)
        hashes_needed = []
        if pos > 0:
            hashes_needed.append(self.hashes[pos-1])
        if pos < len(self.hashes):
            hashes_needed.append(self.hashes[pos])
        return self.generate_proof(hashes_needed)


	
class PartialMerkleTree:

    def __init__(self, total):
        self.total = total
        # compute max depth math.ceil(math.log(self.total, 2))
        self.max_depth = math.ceil(math.log(self.total, 2))
        # initialize the nodes property to hold the actual tree
        self.nodes = []
        # loop over the number of levels (max_depth+1)
        for depth in range(self.max_depth + 1):
            # the number of items at this depth is
            # math.ceil(self.total / 2**(self.max_depth - depth))
            num_items = math.ceil(self.total / 2**(self.max_depth - depth))
            # create this level's hashes list with the right number of items
            level_hashes = [None] * num_items
            # append this level's hashes to the merkle tree
            self.nodes.append(level_hashes)
        # set the pointer to the root (depth=0, index=0)
        self.current_depth = 0
        self.current_index = 0

    def __repr__(self):
        result = []
        for depth, level in enumerate(self.nodes):
            items = []
            for index, h in enumerate(level):
                if h is None:
                    short = 'None'
                else:
                    short = '{}...'.format(h.hex()[:8])
                if depth == self.current_depth and index == self.current_index:
                    items.prepend('*{}*'.format(short[:-2]))
                else:
                    items.append('{}'.format(short))
            result.append(', '.join(items))
        return '\n'.join(result)

    def up(self):
        # reduce depth by 1 and halve the index
        self.current_depth -= 1
        self.current_index //= 2

    def left(self):
        # increase depth by 1 and double the index
        self.current_depth += 1
        self.current_index *= 2

    def right(self):
        # increase depth by 1 and double the index + 1
        self.current_depth += 1
        self.current_index = self.current_index * 2 + 1

    def root(self):
        return self.nodes[0][0]

    def set_current_node(self, value):
        self.nodes[self.current_depth][self.current_index] = value

    def get_current_node(self):
        return self.nodes[self.current_depth][self.current_index]

    def get_left_node(self):
        return self.nodes[self.current_depth + 1][self.current_index * 2]

    def get_right_node(self):
        return self.nodes[self.current_depth + 1][self.current_index * 2 + 1]

    def is_leaf(self):
        return self.current_depth == self.max_depth

    def right_exists(self):
        return len(self.nodes[self.current_depth + 1]) > self.current_index * 2 + 1

    def populate_tree(self, flag_bits, hashes):
        # populate until we have the root
        while self.root() is None:
            # if we are a leaf, we know this position's hash
            if self.is_leaf():
                # get the next bit from flag_bits: flag_bits.pop(0)
                flag_bits.pop(0)
                # set the current node in the merkle tree to the next hash: hashes.pop(0)
                self.set_current_node(hashes.pop(0))
                # go up a level
                self.up()
            else:
                # get the left hash
                left_hash = self.get_left_node()
                # if we don't have the left hash
                if left_hash is None:
                    # if the next flag bit is 0, the next hash is our current node
                    if flag_bits.pop(0) == 0:
                        # set the current node to be the next hash
                        self.set_current_node(hashes.pop(0))
                        # sub-tree doesn't need calculation, go up
                        self.up()
                    else:
                        # go to the left node
                        self.left()
                elif self.right_exists():
                    # get the right hash
                    right_hash = self.get_right_node()
                    # if we don't have the right hash
                    if right_hash is None:
                        # go to the right node
                        self.right()
                    else:
                        # combine the left and right hashes
                        self.set_current_node(merkle_parent(left_hash, right_hash))
                        # we've completed this sub-tree, go up
                        self.up()
                else:
                    # combine the left hash twice
                    self.set_current_node(merkle_parent(left_hash, left_hash))
                    # we've completed this sub-tree, go up
                    self.up()
        if len(hashes) != 0:
            raise RuntimeError('hashes not all consumed {}'.format(len(hashes)))
        for flag_bit in flag_bits:
            if flag_bit != 0:
                raise RuntimeError('flag bits not all consumed')

def verify_inclusion(hashesOfInterest, merkleRoot, proof):
    ''' Verifies if hashesOfInterest belong to a Merkle Tree with the root merkleRoot using the proof
    '''
    leaves = proof.nrLeaves
    flags = proof.flags
    hashes = proof.hashes

    tree = PartialMerkleTree(leaves)
    tree.populate_tree(flags,hashes)

    return (tree.root() == merkleRoot)


def verify_non_inclusion(hash, merkleRoot, proof):
    '''
    The method receives a hash, a Merkle root, and a proof that hash does not belong to this Merkle root
    the proof is of type MerkleProof
    '''

    # Crear el árbol ordenado con los hashes del proof
    # proof.hashesOfInterest puede ser usado para reconstruir el árbol si es necesario
    # Pero normalmente el SortedTree se construye con todos los hashes originales
    # Aquí asumimos que raw_hashes está disponible (como en el main)
    # Si no, habría que pasarlo como argumento
    sorted_tree = SortedTree(raw_hashes)
    # Generar la prueba de no inclusión para el hash
    prueba = sorted_tree.proof_of_non_inclusion(hash)
    if prueba is None:
        # El hash está incluido, no hay prueba de no inclusión
        return False
    # Verificar que los hashes adyacentes están incluidos en el árbol
    # y que el hash no está entre ellos
    # Reconstruir el root usando la prueba
    tree = PartialMerkleTree(prueba.nrLeaves)
    tree.populate_tree(prueba.flags, prueba.hashes.copy())
    # Verificar que la raíz coincide
    if tree.root() != merkleRoot:
        return False
    # Verificar que el hash no está entre los adyacentes
    adyacentes = prueba.hashesOfInterest
    if len(adyacentes) == 2:
        menor = min(adyacentes)
        mayor = max(adyacentes)
        if menor < hash < mayor:
            return True
    return False
## Data for testing:


hex_hashes = [
    "9745f7173ef14ee4155722d1cbf13304339fd00d900b759c6f9d58579b5765fb",
    "5573c8ede34936c29cdfdfe743f7f5fdfbd4f54ba0705259e62f39917065cb9b",
    "82a02ecbb6623b4274dfcab82b336dc017a27136e08521091e443e62582e8f05",
    "507ccae5ed9b340363a0e6d765af148be9cb1c8766ccc922f83e4ae681658308",
    "a7a4aec28e7162e1e9ef33dfa30f0bc0526e6cf4b11a576f6c5de58593898330",
    "bb6267664bd833fd9fc82582853ab144fece26b7a8a5bf328f8a059445b59add",
    "ea6d7ac1ee77fbacee58fc717b990c4fcccf1b19af43103c090f601677fd8836",
    "457743861de496c429912558a106b810b0507975a49773228aa788df40730d41",
    "7688029288efc9e9a0011c960a6ed9e5466581abf3e3a6c26ee317461add619a",
    "b1ae7f15836cb2286cdd4e2c37bf9bb7da0a2846d06867a429f654b2e7f383c9",
    "9b74f89fa3f93e71ff2c241f32945d877281a6a50a6bf94adac002980aafe5ab",
    "b3a92b5b255019bdaf754875633c2de9fec2ab03e6b8ce669d07cb5b18804638",
    "b5c0b915312b9bdaedd2b86aa2d0f8feffc73a2d37668fd9010179261e25e263",
    "c9d52c5cb1e557b92c84c52e7c4bfbce859408bedffc8a5560fd6e35e10b8800",
    "c555bc5fc3bc096df0a0c9532f07640bfb76bfe4fc1ace214b8b228a1297a4c2",
    "f9dbfafc3af3400954975da24eb325e326960a25b87fffe23eef3e7ed2fb610e",
]

raw_hashes = [bytes.fromhex(h) for h in hex_hashes]

tree = MerkleTree(raw_hashes)

flags=[1,0,1,1,0,1,1,0,1,1,0,1,0]
hashes = ["6382df3f3a0b1323ff73f4da50dc5e318468734d6054111481921d845c020b93",
"3b67006ccf7fe54b6cb3b2d7b9b03fb0b94185e12d086a42eb2f32d29d535918",
"9b74f89fa3f93e71ff2c241f32945d877281a6a50a6bf94adac002980aafe5ab",
"b3a92b5b255019bdaf754875633c2de9fec2ab03e6b8ce669d07cb5b18804638",
"b5c0b915312b9bdaedd2b86aa2d0f8feffc73a2d37668fd9010179261e25e263",
"c9d52c5cb1e557b92c84c52e7c4bfbce859408bedffc8a5560fd6e35e10b8800",
"8636b7a3935a68e49dd19fc224a8318f4ee3c14791b3388f47f9dc3dee2247d1"
]


r_hashes = [bytes.fromhex(h) for h in hashes]

hashesOfInterest = ["9b74f89fa3f93e71ff2c241f32945d877281a6a50a6bf94adac002980aafe5ab",
"c9d52c5cb1e557b92c84c52e7c4bfbce859408bedffc8a5560fd6e35e10b8800"
]

r_interest = [bytes.fromhex(h) for h in hashesOfInterest]

proof = MerkleProof(r_interest,16,flags,r_hashes)

print(verify_inclusion(r_interest, tree.root, proof))
tree.generate_proof(hashesOfInterest)

# UTILITIES FOR PRINTING THE TREE IN A HUMAN-READABLE WAY
def str_human(h):
    return hash_to_word.get(h, h.hex()[:8])

def print_tree(tree, highlight=None):
    max_width = len("  ".join(str_human(h) for h in tree.levels[0]))  # Ancho de las hojas
    for i, level in enumerate(reversed(tree.levels)):
        parts = []
        for h in level:
            if h == highlight:
                parts.append(f"[{str_human(h)}]")
            else:
                parts.append(str_human(h))
        line = "  ".join(parts)
        print(line.center(max_width))

# Usar los nombres asignados en SortedTree
sorted_tree = SortedTree(raw_hashes)
hash_to_word = sorted_tree.hash_to_name
####################################################
