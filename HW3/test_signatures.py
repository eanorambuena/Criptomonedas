import sys
sys.path.append('src')
from ecc import *
from transaction import *
from blockchain import *
from keys import *
from scroogecoin import Scroogecoin

def test_valid_signatures():
    # Transacción con firma válida
    outputs = [Output(10, addressA)]
    trans = Transaction('createCoins', [], outputs)
    to_sign = trans.dataForSigs
    trans.signatures[str(pubKeyScrooge)] = privKeyScrooge.sign(to_sign)
    sc = Scroogecoin()
    valid = sc.process_transactions([trans])
    assert len(valid) == 1
    # Transacción con firma inválida (firmada por otra clave)
    trans_bad = Transaction('createCoins', [], outputs)
    to_sign_bad = trans_bad.dataForSigs
    # Usamos pkA en vez de privKeyScrooge
    trans_bad.signatures[str(pubKeyScrooge)] = pkA.sign(to_sign_bad)
    valid = sc.process_transactions([trans_bad])
    assert len(valid) == 0

if __name__ == "__main__":
    test_valid_signatures()
    print("test_valid_signatures passed.")
