from ecc import *  # noqa
from transaction import *  # noqa
from blockchain import *  # noqa
from keys import *  # noqa


class Scroogecoin:
    def __init__(self):
        self.transactions = {}  # a dictionary containing all the **VALID** transactions
        self.blockchain = Blockchain()
        # set storing references to unspent UTXOs of the form (txID, index)
        self.utxo_pool = set()

    def process_transactions(self, tx_list: list[Transaction]):
        # Logging utilities ------------
        IS_LOGGING_ENABLED = False
        IS_TESTING_ENV = True
        
        def log(*msgs: str):
            if IS_LOGGING_ENABLED:
                print(f"[Scroogecoin]> {' '.join(msgs)}")

        def get_transaction_label(tx: Transaction):
            if not IS_LOGGING_ENABLED or IS_TESTING_ENV:
                return f"...{tx.id()[:6]}"
            names ={
                trans1.id(): "Tx1",
                trans2.id(): "Tx2",
                trans3.id(): "Tx3",
                trans4.id(): "Tx4",
                trans5.id(): "Tx5",
                trans6.id(): "Tx6",
                trans7.id(): "Tx7"
            }
            if tx.id() in names:
                return names[tx.id()]
            return f"...{tx.id()[:6]}"
        # -------------------------------

        log("Processing a new batch of transactions...")

        valid_txs: list[Transaction] = []

        for tx in tx_list:
            if tx.id() in self.transactions:
                log(f"Transaction {get_transaction_label(tx)} is a duplicate.")
                continue

            self.transactions[tx.id()] = tx

            are_signatures_valid = tx.CheckSignatures()

            if not are_signatures_valid:
                log(f"Transaction {get_transaction_label(tx)} has invalid signatures.")
                continue

            is_balance_valid = tx.CheckValues()

            if not is_balance_valid:
                log(f"Transaction {get_transaction_label(tx)} has invalid input/output values.")
                continue

            are_inputs_unspent = all((inp.whereCreated, inp.nrOutput) in self.utxo_pool for inp in tx.inputs)

            if not are_inputs_unspent and tx.type != 'createCoins':
                log(f"Transaction {get_transaction_label(tx)} attempts to double spend UTXOs.")
                continue

            log(f"Transaction {get_transaction_label(tx)} is valid.")

            for inp in tx.inputs:
                self.utxo_pool.remove((inp.whereCreated, inp.nrOutput))

            for i in range(len(tx.outputs)):
                self.utxo_pool.add((tx.id(), i))

            valid_txs.append(tx)
            
        # Create new Blocks for every two valid transactions
        valid_tx_pairs = [valid_txs[i:i + 2] for i in range(0, len(valid_txs), 2)]
        for tx_pair in valid_tx_pairs:
            tx_hashes = [tx.id() for tx in tx_pair]
            block = Block(tx_hashes, self.blockchain.head)
            self.blockchain.add_block(block)

        log(f"[UTXO]> {[(get_transaction_label(self.transactions[txid]), idx) for (txid, idx) in self.utxo_pool]}")

        # Return the list of valid transactions
        return valid_txs


if __name__ == '__main__':
    # Tx1:
    outputs = [
        Output(10, addressA),
        Output(10, addressB),
        Output(10, addressC),
        Output(10, addressD),
        Output(10, addressD),
    ]
    trans1 = Transaction('createCoins', [], outputs)
    to_sign = trans1.dataForSigs
    trans1.signatures[str(pubKeyScrooge)] = privKeyScrooge.sign(to_sign)
    ####

    # Tx2:
    inputs = []
    input0 = Input(
        '8ef5f3797d0f245c3435067e611a2ef511266da3e7b96d0f8f7549a5fdb2c626',
        0,
        10,
        addressA
    )
    input1 = Input(
        '8ef5f3797d0f245c3435067e611a2ef511266da3e7b96d0f8f7549a5fdb2c626',
        1,
        10,
        addressB
    )
    inputs.append(input0)
    inputs.append(input1)
    outputs = []
    out0 = Output(20, addressC)
    outputs.append(out0)
    trans2 = Transaction('payCoins', inputs, outputs)
    toSign = trans2.dataForSigs
    sigBob = pkB.sign(toSign)
    trans2.signatures[str(addressB)] = sigBob
    sigAlice = pkA.sign(toSign)
    trans2.signatures[str(addressA)] = sigAlice
    #####

    # TX3:
    inputs = []
    input0 = Input(
        '9f94542b0898ffaa65fcf397c07e59fcb8d49e7809879c72983dcf7caf88e440',
        0,
        20,
        addressC
    )
    inputs.append(input0)
    outputs = []
    out0 = Output(10, addressC)
    out1 = Output(10, addressD)
    outputs.append(out0)
    outputs.append(out1)
    trans3 = Transaction('payCoins', inputs, outputs)
    toSign = trans3.dataForSigs
    sigC = pkC.sign(toSign)
    trans3.signatures[str(addressC)] = sigC
    #####

    # TX4 -- double spend
    inputs = []
    input0 = Input(
        '9f94542b0898ffaa65fcf397c07e59fcb8d49e7809879c72983dcf7caf88e440',
        0,
        20,
        addressC
    )
    inputs.append(input0)
    outputs = []
    out1 = Output(20, addressD)
    outputs.append(out1)
    trans4 = Transaction('payCoins', inputs, outputs)
    toSign = trans4.dataForSigs
    sigC = pkC.sign(toSign)
    trans4.signatures[str(addressC)] = sigC
    #####

    # TX5 -- bad sig
    inputs = []
    input0 = Input(
        '8ef5f3797d0f245c3435067e611a2ef511266da3e7b96d0f8f7549a5fdb2c626',
        4,
        10,
        addressE
    )
    inputs.append(input0)
    outputs = []
    out1 = Output(10, addressD)
    outputs.append(out1)
    trans5 = Transaction('payCoins', inputs, outputs)
    toSign = trans5.dataForSigs
    sigC = pkC.sign(toSign)
    trans5.signatures[str(addressC)] = sigC
    #####

    # TX6-- good tx
    inputs = []
    input0 = Input(
        '1f57f33ad501e031fb7de02ca681876a9a0a3ad6cefedae3b79d6280da7078ce',
        1,
        10,
        addressD
    )
    inputs.append(input0)
    outputs = []
    out0 = Output(10, addressE)
    outputs.append(out0)
    trans6 = Transaction('payCoins', inputs, outputs)
    toSign = trans6.dataForSigs
    sigD = pkD.sign(toSign)
    trans6.signatures[str(addressD)] = sigD
    #####

    # TX7-- good tx
    inputs = []
    input0 = Input(
        'a7452e6d420b35b413f16fa7d32d6b8282d004f887b354cc50e9f3ec77defcb9',
        0,
        10,
        addressE
    )
    inputs.append(input0)
    outputs = []
    out0 = Output(10, addressA)
    outputs.append(out0)
    trans7 = Transaction('payCoins', inputs, outputs)
    toSign = trans7.dataForSigs
    sigE = pkE.sign(toSign)
    trans7.signatures[str(addressE)] = sigE
    #####

    test = Scroogecoin()
    test.process_transactions(
        [
            trans1,
            trans2,
            trans3,
            trans4,
            trans5,
            trans6,
            trans7,
            trans1,
            trans3,
        ]
    )
    test.blockchain.print_blockchain()

    print('The UTXO pool:')

    for x in test.utxo_pool:
        print(x)

    '''
    EXPECTED OUTPUT:

    Key: d42cc9926cb75f115da4e2f852e7a297ec39fe36f5ff3e3514015ab47f9b7b87
    Block: (Block Hash: d42cc9926cb75f115da4e2f852e7a297ec39fe36f5ff3e3514015ab47f9b7b87 Merkle Root: 7d0868f033269487a66d3b0dbdfa5eb8a3a79996a38d2458f4342d5a6f48b6ec - Tx Hashes: ['8ef5f3797d0f245c3435067e611a2ef511266da3e7b96d0f8f7549a5fdb2c626', '9f94542b0898ffaa65fcf397c07e59fcb8d49e7809879c72983dcf7caf88e440'] - Previous Block: None) 

    Key: 06aa06c86f6ad6064808362db63c4cdf4a865c11cd7f89833f63a49b2195eaff
    Block: (Block Hash: 06aa06c86f6ad6064808362db63c4cdf4a865c11cd7f89833f63a49b2195eaff Merkle Root: ede530623269e79e00f9b1cc4c5d4af49c2a07cb7ea5a28e52a0aaa8700358a2 - Tx Hashes: ['1f57f33ad501e031fb7de02ca681876a9a0a3ad6cefedae3b79d6280da7078ce', 'a7452e6d420b35b413f16fa7d32d6b8282d004f887b354cc50e9f3ec77defcb9'] - Previous Block: d42cc9926cb75f115da4e2f852e7a297ec39fe36f5ff3e3514015ab47f9b7b87) 

    Key: b47ded88d87345720442e805b147c2ebb1287f9e62123153fb995b87d07b0a9a
    Block: (Block Hash: b47ded88d87345720442e805b147c2ebb1287f9e62123153fb995b87d07b0a9a Merkle Root: 729ae2c7b51b0ad2449b91ac8cd06c5f08ab1ea0d6ced0eece3f7a215eac9456 - Tx Hashes: ['729ae2c7b51b0ad2449b91ac8cd06c5f08ab1ea0d6ced0eece3f7a215eac9456'] - Previous Block: 06aa06c86f6ad6064808362db63c4cdf4a865c11cd7f89833f63a49b2195eaff) 

    The UTXO pool:
    ('8ef5f3797d0f245c3435067e611a2ef511266da3e7b96d0f8f7549a5fdb2c626', 4)
    ('1f57f33ad501e031fb7de02ca681876a9a0a3ad6cefedae3b79d6280da7078ce', 0)
    ('8ef5f3797d0f245c3435067e611a2ef511266da3e7b96d0f8f7549a5fdb2c626', 3)
    ('729ae2c7b51b0ad2449b91ac8cd06c5f08ab1ea0d6ced0eece3f7a215eac9456', 0)
    ('8ef5f3797d0f245c3435067e611a2ef511266da3e7b96d0f8f7549a5fdb2c626', 2)
    '''
