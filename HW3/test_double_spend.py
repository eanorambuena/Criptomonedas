import sys
sys.path.append('src')
from ecc import *
from transaction import *
from blockchain import *
from keys import *
from scroogecoin import Scroogecoin

def test_double_spend():
    outputs = [Output(10, addressA)]
    trans = Transaction('createCoins', [], outputs)
    to_sign = trans.dataForSigs
    trans.signatures[str(pubKeyScrooge)] = privKeyScrooge.sign(to_sign)
    sc = Scroogecoin()
    sc.utxo_pool.add((trans.id(), 0))
    inp = Input(trans.id(), 0, 10, addressA)
    out = Output(10, addressB)
    tx1 = Transaction('payCoins', [inp], [out])
    tx1.signatures[str(addressA)] = pkA.sign(tx1.dataForSigs)
    tx2 = Transaction('payCoins', [inp], [out])
    tx2.signatures[str(addressA)] = pkA.sign(tx2.dataForSigs)
    valid = sc.process_transactions([tx1, tx2])
    assert len(valid) == 1
    # El segundo intento de gastar el mismo input no debe ser válido

if __name__ == "__main__":
    test_double_spend()
    print("test_double_spend passed.")
