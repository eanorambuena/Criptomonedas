from ecc import *  # noqa
from hash import *  # noqa
from keys import *  # noqa
import json


# The first thing we want to define is transactions
# Recall the components of transactions: ID, type, inputs, outputs, and signatures
# We will begin by defining inputs and outputs
# IMPORTANT: For us the ID of a transaction will be its hash --> same as in Bitcoin


'''
# To define an input for a transaction we need four things:
    1) ID of the transaction where the coins were created (i.e. where these inputs are outputs)
    2) The output number for this transaction (recall coinID 0xffab07...(32) -- 0xffab07... is txID, and 32 the output)
    3) The value
    4) The owner
Let's code this:
'''


class Input:
    def __init__(self, txID, nrOutput, amount, address):
        self.whereCreated = txID
        self.nrOutput = nrOutput
        self.value = amount
        self.owner = address  # raw public key (as a curve point object)

    # for hashing an input
    def serialize(self):
        d = {'whereCreated': self.whereCreated,
             'output_number': self.nrOutput,
             'value': self.value,
             'owner': str(self.owner)}

        return json.dumps(d, sort_keys=False).encode('utf-8')

    # for printing and debugging
    def __str__(self):
        return '(Origin tx: {} - Origin output: {} - Value: {} - Owner: {})'.\
            format(self.whereCreated, self.nrOutput,
                   self.value, str(self.owner))


'''
The next class will represent transaction outputs. These are defined by:
    1) The value they have
    2) The owner of this output
The txID and output number will be implicit from the context where we define
the outputs.
'''


class Output:
    def __init__(self, amount, address):
        self.value = amount
        self.recipient = address  # raw public key

    # for hashing an output
    def serialize(self):
        d = {'value': self.value,
             'recipient': str(self.recipient)}

        return json.dumps(d, sort_keys=False).encode('utf-8')

    # for printing
    def __str__(self):
        return '(Value: {} - Recipient: {})'.format(
            self.value,
            str(self.recipient)
        )


'''
The next class will be the transaction class

A tranasaction is defined by:
    1) type (createCoins or payCoins)
    2) inputs (a list of objects of class Input)
    3) outputs (a list of objects of class Output)
    4) signatures of **all** input owners)
    5) its ID --> this will just be a hash of its serialization to bytes (not a class field)
'''


class Transaction:
    def __init__(self, txType, inputCoins, outputCoins):
        self.type = txType
        self.inputs = inputCoins
        self.outputs = outputCoins

        self.dataForSigs = self.DataForSigs()
        # this is the data we will sign (serialization of the above)

        self.signatures = {}
        # raw signatures (as a ECC signature object);
        # stored in a  dictionary ['str(pubKeyX)'] = sig for pubkeyX
        # really we should have der signatures here, but since this would solve
        # your homework ...
        # also, we should probably index by hash256(SEC(PubKey)).hex(), but no
        # one is perfect

    # Transaction ID; this is our hash pointer in the UTXO set
    def id(self):
        '''Human-readable hexadecimal of the transaction hash'''
        return self.hash().hex()

    # Well, just the hash
    # Note that the hash is given in "little-endian"
    def hash(self):
        '''Binary hash of the legacy serialization'''
        return hash256(self.serialize())[::-1]

    def DataForSigs(self):

        rawInputs = ''

        for coin in self.inputs:
            rawInputs = rawInputs + str(coin.serialize())

        rawOutputs = ''

        for coin in self.outputs:
            rawOutputs = rawOutputs + str(coin.serialize())

        rawData = {'type': str(self.type),
                   'inputs': rawInputs,
                   'outputs': rawOutputs}

        # recall what I'm signing: hash of the message;
        # which is the same as a scalar in the group of my curve (as an int)
        return int(hash(
            bytes(json.dumps(rawData, sort_keys=False).encode('utf-8'))
        ).hex(), 16)

    # checks that all the signatures match up

    def CheckSignatures(self):
        toSign = self.dataForSigs

        if (self.type == 'payCoins'):

            if (len(self.inputs) == 0):
                return False

            for x in self.inputs:
                if (str(x.owner) not in self.signatures.keys()):
                    return False
                else:
                    if (not x.owner.verify(
                        toSign,
                        self.signatures[str(x.owner)]
                    )):
                        return False

            return True

        if (self.type == 'createCoins'):
            if (len(self.signatures) > 1):
                return False

            if (str(pubKeyScrooge) not in self.signatures.keys()):
                return False

            if (not pubKeyScrooge.verify(
                toSign,
                self.signatures[str(pubKeyScrooge)]
            )):
                return False

            return True

        return False

    # checks that all the input values >= output values

    def CheckValues(self):

        if (self.type == 'createCoins'):
            return True

        inValue = 0
        for x in self.inputs:
            if (x.value < 0):
                return False
            else:
                inValue += x.value

        outValue = 0
        for x in self.outputs:
            if (x.value < 0):
                return False
            else:
                outValue += x.value

        return (inValue >= outValue)

    def serialize(self):

        rawInputs = []

        for coin in self.inputs:
            rawInputs.append(str(coin.serialize()))

        rawOutputs = []

        for coin in self.outputs:
            rawOutputs.append(str(coin.serialize()))

        sigs = []

        for sig in self.signatures:
            sigs.append(str(self.signatures[sig]))

        rawData = {'type': str(self.type),
                   'inputs': rawInputs,
                   'outputs': rawOutputs,
                   'signatures': sigs}

        return json.dumps(rawData, sort_keys=True).encode('utf-8')


if __name__ == '__main__':
    inputs = []

    input0 = Input(hash256(b'hola').hex(), 0, 7.35, addressA)
    input1 = Input(hash256(b'chao').hex(), 1, 4.12, addressB)

    inputs.append(input0)
    inputs.append(input1)

    outputs = []

    out0 = Output(11.46, addressA)
    outputs.append(out0)

    trans = Transaction('payCoins', inputs, outputs)

    # print(trans.serialize())

    toSign = trans.dataForSigs

    # Alice signs:
    sigAlice = pkA.sign(toSign)
    # Bob signs:
    sigBob = pkB.sign(toSign)

    # they complete the transaction:

    trans.signatures[str(addressA)] = sigAlice
    trans.signatures[str(addressB)] = sigBob

    # print(trans.id())

    # Is alice's signatureOK:
    # print(addressA.verify(toSign,sigAlice))

    # where is Alice's signature: sigs[str(addressA)]

    sigsOK = trans.CheckSignatures()
    print(sigsOK)

    checkValue = trans.CheckValues()
    print(checkValue)

    ##################
    ### EXAMPLE 1: ###
    ##################

    inputs = []

    input0 = Input(1, 0, 1, addressB)
    input1 = Input(1, 1, 2, addressB)

    inputs.append(input0)
    inputs.append(input1)

    outputs = []

    out0 = Output(3, addressB)
    outputs.append(out0)

    trans = Transaction('payCoins', inputs, outputs)
    toSign = trans.dataForSigs

    sigBob = pkB.sign(toSign)
    trans.signatures[str(addressB)] = sigBob

    print('Example 1: ', trans.CheckSignatures())

    ##################
    ### EXAMPLE 2: ###
    ##################

    inputs = []

    input0 = Input(1, 0, 1, addressB)
    input1 = Input(1, 1, 2, addressB)

    inputs.append(input0)
    inputs.append(input1)

    outputs = []

    out0 = Output(3, addressB)
    outputs.append(out0)

    trans = Transaction('payCoins', inputs, outputs)
    toSign = trans.dataForSigs

    # they complete the transaction:
    trans.signatures[str(addressB)] = Signature(
        0x5ca60b383203e5bf92b88f0274f04e58e727b9f5de109b6c3583c0fc9ff192ad,
        0x6018b04962393d2198bf3c877f35a6b60a1a7633458b2bc2349952c1041af457
    )

    print('Example 2: ', trans.CheckSignatures())

    ##################
    ### EXAMPLE 3: ###
    ##################

    inputs = []

    input0 = Input(1, 0, 1, addressB)
    input1 = Input(1, 1, 2, addressA)

    inputs.append(input0)
    inputs.append(input1)

    outputs = []

    out0 = Output(3, addressB)
    outputs.append(out0)

    trans = Transaction('payCoins', inputs, outputs)
    toSign = trans.dataForSigs

    # they complete the transaction:
    trans.signatures[str(addressA)] = Signature(
        0x604b61b126dda950f6d4bc8d5d89552f14e5bdb108fe301482042e0fe71975a1,
        0x2158b0e795ea84c79cba8eb4ebd7d76658472486cbc9890afeffad79c2975bbe
    )
    trans.signatures[str(addressB)] = Signature(
        0xbe6f90eb5f2bfdd0aa487afe05d17bd709b461e080633a65161f2508264f324e,
        0x3f24d15b0e00116e91c5f840ee9ba9be34bd889adcb55c745b39cf5ca2c94242
    )

    print('Example 3: ', trans.CheckSignatures())

    # they complete the transaction:
    trans.signatures[str(addressA)] = Signature(
        0x4c062dcdef8d31ed3764f75b27b8c330ce477f8e0992063d4ebcdcbb3c1100c,
        0x5a1eb466236fc2c2a1467d43158a673c694d6d6318fb66ba3020ac8e1b3f1b40
    )
    trans.signatures[str(addressB)] = Signature(
        0x5ae24e739768ff6acfab787733cd3b18ac743b8a01b1bcc3bfbee55353fcdb56,
        0x399a57a1fad13ce5447cf5ab31b5fd5c232267d88e49b63214a96fc0fb2eb9b8
    )

    print('Example 3: ', trans.CheckSignatures())

    ##################
    ### EXAMPLE 4: ###
    ##################

    inputs = []
    outputs = []
    out0 = Output(3, addressA)
    outputs.append(out0)
    trans = Transaction('createCoins', inputs, outputs)
    # they complete the transaction:
    trans.signatures[str(pubKeyScrooge)] = Signature(
        0x30a55d4773295c5874a020eadd498ddb42a78410f6236dd506572e43ca11d956,
        0x7a06e7b8cc5c5982764fc4996bdea2d386563954eb13750022b2bd013e26175f
    )
    print('Example 4: ', trans.CheckSignatures())
