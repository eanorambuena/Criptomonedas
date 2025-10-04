import sys
sys.path.append('src')
from ecc import *
from transaction import *
from blockchain import *
from keys import *
from scroogecoin import Scroogecoin

def test_blockchain_and_state():
    # Creamos 3 transacciones válidas
    outputs1 = [Output(10, addressA)]
    trans1 = Transaction('createCoins', [], outputs1)
    trans1.signatures[str(pubKeyScrooge)] = privKeyScrooge.sign(trans1.dataForSigs)
    outputs2 = [Output(10, addressB)]
    inp2 = Input(trans1.id(), 0, 10, addressA)
    trans2 = Transaction('payCoins', [inp2], outputs2)
    trans2.signatures[str(addressA)] = pkA.sign(trans2.dataForSigs)
    outputs3 = [Output(10, addressC)]
    inp3 = Input(trans2.id(), 0, 10, addressB)
    trans3 = Transaction('payCoins', [inp3], outputs3)
    trans3.signatures[str(addressB)] = pkB.sign(trans3.dataForSigs)

    sc = Scroogecoin()
    # Procesamos las transacciones
    valid = sc.process_transactions([trans1, trans2, trans3])
    # Deben estar en el blockchain
    block_hash = sc.blockchain.head
    blocks = []
    while block_hash:
        block = sc.blockchain.elements[block_hash]
        blocks.append(block)
        block_hash = block.prev_hash
    blocks = blocks[::-1]
    tx_ids_in_blocks = [txid for block in blocks for txid in block.tx_hashes]
    assert trans1.id() in tx_ids_in_blocks
    assert trans2.id() in tx_ids_in_blocks
    assert trans3.id() in tx_ids_in_blocks
    # Deben estar en el diccionario transactions
    assert trans1.id() in sc.transactions
    assert trans2.id() in sc.transactions
    assert trans3.id() in sc.transactions
    # UTXO pool debe tener solo el último output válido
    expected_utxos = set([(trans3.id(), 0)])
    assert set(sc.utxo_pool) == expected_utxos

if __name__ == "__main__":
    test_blockchain_and_state()
    print("test_blockchain_and_state passed.")
