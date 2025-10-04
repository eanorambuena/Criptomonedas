import sys
sys.path.append('src')
from ecc import *
from transaction import *
from blockchain import *
from keys import *
from scroogecoin import Scroogecoin

def test_input_output_values():
    # Input value >= output value
    outputs = [Output(10, addressA)]
    trans = Transaction('createCoins', [], outputs)
    to_sign = trans.dataForSigs
    trans.signatures[str(pubKeyScrooge)] = privKeyScrooge.sign(to_sign)
    sc = Scroogecoin()
    sc.utxo_pool.add((trans.id(), 0))
    # Transacción con input = output
    inp = Input(trans.id(), 0, 10, addressA)
    out = Output(10, addressB)
    tx = Transaction('payCoins', [inp], [out])
    to_sign2 = tx.dataForSigs
    tx.signatures[str(addressA)] = pkA.sign(to_sign2)
    valid = sc.process_transactions([tx])
    assert len(valid) == 1
    # Transacción con input < output
    out2 = Output(20, addressB)
    tx2 = Transaction('payCoins', [inp], [out2])
    to_sign3 = tx2.dataForSigs
    tx2.signatures[str(addressA)] = pkA.sign(to_sign3)
    valid = sc.process_transactions([tx2])
    assert len(valid) == 0

if __name__ == "__main__":
    test_input_output_values()
    print("test_input_output_values passed.")
