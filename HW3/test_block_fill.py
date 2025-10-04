import sys
sys.path.append('src')
from ecc import *
from transaction import *
from blockchain import *
from keys import *
from scroogecoin import Scroogecoin

def test_block_fill_and_spending():
    outputs = [Output(10, addressA), Output(10, addressB)]
    trans = Transaction('createCoins', [], outputs)
    trans.signatures[str(pubKeyScrooge)] = privKeyScrooge.sign(trans.dataForSigs)
    sc = Scroogecoin()
    sc.utxo_pool.add((trans.id(), 0))
    sc.utxo_pool.add((trans.id(), 1))
    inp1 = Input(trans.id(), 0, 10, addressA)
    out1 = Output(10, addressC)
    tx1 = Transaction('payCoins', [inp1], [out1])
    tx1.signatures[str(addressA)] = pkA.sign(tx1.dataForSigs)
    inp2 = Input(tx1.id(), 0, 10, addressC)
    out2 = Output(10, addressD)
    tx2 = Transaction('payCoins', [inp2], [out2])
    tx2.signatures[str(addressC)] = pkC.sign(tx2.dataForSigs)
    valid = sc.process_transactions([tx1, tx2])
    # Ambos deben ir en el mismo bloque, y el segundo puede gastar el output del primero
    assert len(valid) == 2
    # Verifica que el bloque contiene ambas transacciones
    block_hash = sc.blockchain.head
    block = sc.blockchain.elements[block_hash]
    assert tx1.id() in block.tx_hashes and tx2.id() in block.tx_hashes

if __name__ == "__main__":
    test_block_fill_and_spending()
    print("test_block_fill_and_spending passed.")
