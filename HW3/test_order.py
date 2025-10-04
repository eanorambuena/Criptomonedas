import sys
sys.path.append('src')
from ecc import *
from transaction import *
from blockchain import *
from keys import *
from scroogecoin import Scroogecoin

def test_order_processing():
    outputs = [Output(10, addressA)]
    trans = Transaction('createCoins', [], outputs)
    trans.signatures[str(pubKeyScrooge)] = privKeyScrooge.sign(trans.dataForSigs)
    sc = Scroogecoin()
    sc.utxo_pool.add((trans.id(), 0))
    inp = Input(trans.id(), 0, 10, addressA)
    out = Output(10, addressB)
    tx1 = Transaction('payCoins', [inp], [out])
    tx1.signatures[str(addressA)] = pkA.sign(tx1.dataForSigs)
    tx2 = Transaction('payCoins', [inp], [out])
    tx2.signatures[str(addressA)] = pkA.sign(tx2.dataForSigs)
    valid = sc.process_transactions([tx2, tx1])
    # tx2 llega primero, lo gasta
    assert valid[0] == tx2
    assert len(valid) == 1

if __name__ == "__main__":
    test_order_processing()
    print("test_order_processing passed.")
