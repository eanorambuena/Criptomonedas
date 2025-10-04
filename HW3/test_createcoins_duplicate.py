import sys
sys.path.append('src')
from ecc import *
from transaction import *
from blockchain import *
from keys import *
from scroogecoin import Scroogecoin

def test_createCoins_duplicate():
    outputs = [Output(10, addressA)]
    trans = Transaction('createCoins', [], outputs)
    trans.signatures[str(pubKeyScrooge)] = privKeyScrooge.sign(trans.dataForSigs)
    sc = Scroogecoin()
    valid = sc.process_transactions([trans, trans])
    # Solo la primera debe ser válida
    assert len(valid) == 1

if __name__ == "__main__":
    test_createCoins_duplicate()
    print("test_createCoins_duplicate passed.")
