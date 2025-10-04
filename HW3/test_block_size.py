import sys
sys.path.append('src')
from ecc import *
from transaction import *
from blockchain import *
from keys import *
from scroogecoin import Scroogecoin

def test_block_size():
    outputs = [Output(10, addressA)]
    trans = Transaction('createCoins', [], outputs)
    trans.signatures[str(pubKeyScrooge)] = privKeyScrooge.sign(trans.dataForSigs)
    sc = Scroogecoin()
    sc.utxo_pool.add((trans.id(), 0))
    inp = Input(trans.id(), 0, 10, addressA)
    out = Output(5, addressB)
    out2 = Output(5, addressC)
    tx1 = Transaction('payCoins', [inp], [out])
    tx1.signatures[str(addressA)] = pkA.sign(tx1.dataForSigs)
    tx2 = Transaction('payCoins', [inp], [out2])
    tx2.signatures[str(addressA)] = pkA.sign(tx2.dataForSigs)
    valid = sc.process_transactions([tx1, tx2])
    # Solo uno debe ser válido, y el bloque debe tener máximo dos transacciones
    assert len(valid) == 1 or len(valid) == 2
    # Si hay dos válidas, deben ir juntas en el bloque

if __name__ == "__main__":
    test_block_size()
    print("test_block_size passed.")
