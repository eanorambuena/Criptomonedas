# As usual, most of the code is stolen from Jimmy Song's book, I just made it worse

# IMPORTANT: validation for P2SH is not implemented!!!!
# However, you can sign things for P2SH and generate P2SH spends!!!!


from io import BytesIO
from unittest import TestCase

import json
import requests

from ecc import PrivateKey
from base58 import *
from scriptSimplified import *


# This method connects to a full node to receive a transaction in order to later validate it
# The API we're using is a bit weird, but you can try with another one if you prefer
class TxFetcher:
    cache = {}

    @classmethod
    def get_url(cls, testnet=False):
        if testnet:
            return 'http://testnet.programmingbitcoin.com'
        else:
            return 'http://mainnet.programmingbitcoin.com'

    @classmethod
    def fetch(cls, tx_id, testnet=False, fresh=False):
        if fresh or (tx_id not in cls.cache):
            url = '{}/tx/{}.hex'.format(cls.get_url(testnet), tx_id)
            response = requests.get(url)
            try:
                raw = bytes.fromhex(response.text.strip())
            except ValueError:
                raise ValueError('unexpected response: {}'.format(response.text))
            # make sure the tx we got matches to the hash we requested
            if raw[4] == 0:
                # zero imputs = coinbase
                raw = raw[:4] + raw[6:]
                tx = Tx.parse(BytesIO(raw), testnet=testnet)
                tx.locktime = little_endian_to_int(raw[-4:])
            else:
                tx = Tx.parse(BytesIO(raw), testnet=testnet)
#            if tx.id() != tx_id:
#                raise ValueError('not the same id: {} vs {}'.format(tx.id(), tx_id))
            cls.cache[tx_id] = tx
        cls.cache[tx_id].testnet = testnet
        return cls.cache[tx_id]

    @classmethod
    def load_cache(cls, filename):
        disk_cache = json.loads(open(filename, 'r').read())
        for k, raw_hex in disk_cache.items():
            raw = bytes.fromhex(raw_hex)
            if raw[4] == 0:
                raw = raw[:4] + raw[6:]
                tx = Tx.parse(BytesIO(raw))
                tx.locktime = little_endian_to_int(raw[-4:])
            else:
                tx = Tx.parse(BytesIO(raw))
            cls.cache[k] = tx

    @classmethod
    def dump_cache(cls, filename):
        with open(filename, 'w') as f:
            to_dump = {k: tx.serialize().hex() for k, tx in cls.cache.items()}
            s = json.dumps(to_dump, sort_keys=True, indent=4)
            f.write(s)

'''
# The transaction class
'''
class Tx:

    '''
    What defines a transaction:
    1. Version
    2. Locktime
    3. Inputs
    4. Outputs
    5. Network (testnet or not)
    '''
    def __init__(self, version, tx_ins, tx_outs, locktime, testnet=False):
        self.version = version
        self.tx_ins = tx_ins
        self.tx_outs = tx_outs
        self.locktime = locktime
        self.testnet = testnet

    # As usual, our prettyprint for printing the transaction; nothing interesting here
    def __repr__(self):
        tx_ins = ''
        for tx_in in self.tx_ins:
            tx_ins += tx_in.__repr__() + '\n'
        tx_outs = ''
        for tx_out in self.tx_outs:
            tx_outs += tx_out.__repr__() + '\n'
        return 'tx: {}\nversion: {}\ntx_ins:\n{}tx_outs:\n{}locktime: {}'.format(
            self.id(),
            self.version,
            tx_ins,
            tx_outs,
            self.locktime,
        )

    # Transaction ID; this is our hash pointer in the UTXO set
    # I.e. when you ask for a transaction to a full node, it guards it under this key
    def id(self):
        '''Human-readable hexadecimal of the transaction hash'''
        return self.hash().hex()

    # Well, just the hash
    # Note that the hash is given in "little-endian"
    def hash(self):
        '''Binary hash of the legacy serialization'''
        return hash256(self.serialize())[::-1]

    # When we receive raw transaction (bytes) we want to parse it to figure out what's what
    @classmethod
    def parse(cls, s, testnet=False):
        '''Takes a byte stream and parses the transaction at the start
        return a Tx object
        '''
        # s.read(n) will return n bytes
        # version is an integer in 4 bytes, little-endian
        version = little_endian_to_int(s.read(4))
        # num_inputs is a varint, use read_varint(s)
        num_inputs = read_varint(s)
        # parse num_inputs number of TxIns
        inputs = []
        for _ in range(num_inputs):
            inputs.append(TxIn.parse(s))
        # num_outputs is a varint, use read_varint(s)
        num_outputs = read_varint(s)
        # parse num_outputs number of TxOuts
        outputs = []
        for _ in range(num_outputs):
            outputs.append(TxOut.parse(s))
        # locktime is an integer in 4 bytes, little-endian
        locktime = little_endian_to_int(s.read(4))
        # return an instance of the class (see __init__ for args)
        return cls(version, inputs, outputs, locktime, testnet=testnet)

    # When we have a transaction object, to send it to the network we need to serialize it
    def serialize(self):
        '''Returns the byte serialization of the transaction'''
        # serialize version (4 bytes, little endian)
        result = int_to_little_endian(self.version, 4)
        # encode_varint on the number of inputs
        result += encode_varint(len(self.tx_ins))
        # iterate inputs
        for tx_in in self.tx_ins:
            # serialize each input
            result += tx_in.serialize()
        # encode_varint on the number of outputs
        result += encode_varint(len(self.tx_outs))
        # iterate outputs
        for tx_out in self.tx_outs:
            # serialize each output
            result += tx_out.serialize()
        # serialize locktime (4 bytes, little endian)
        result += int_to_little_endian(self.locktime, 4)
        return result

    # Computes the transaction fee
    # Recall that this will need to connect to a full node to get the input transaction!!!
    def fee(self):
        '''Returns the fee of this transaction in satoshi'''
        # initialize input sum and output sum
        input_sum, output_sum = 0, 0
        # use TxIn.value() to sum up the input amounts
        for tx_in in self.tx_ins:
            input_sum += tx_in.value(self.testnet)
        # use TxOut.amount to sum up the output amounts
        for tx_out in self.tx_outs:
            output_sum += tx_out.amount
        # fee is input sum - output sum
        return input_sum - output_sum

    # Here we compute the serialization of what will be signed in a transaction
    def sig_hash(self, input_index, redeem_script=None):
        '''Returns the integer representation of the hash that needs to get
        signed for index input_index'''
        # redeem_script is used in p2sh transaction to replace ScriptSig
        # if input_index is not in tx_ins, then all ScriptSigs will be empty!!!
        # start the serialization with version
        # use int_to_little_endian in 4 bytes
        s = int_to_little_endian(self.version, 4)
        # add how many inputs there are using encode_varint
        s += encode_varint(len(self.tx_ins))
        # loop through each input using enumerate, so we have the input index
        for i, tx_in in enumerate(self.tx_ins):
            # if the input index is the one we're signing
            if i == input_index:
                # if the RedeemScript was passed in, that's the ScriptSig
                if redeem_script:
                    script_sig = redeem_script
                # otherwise the previous tx's ScriptPubkey is the ScriptSig
                else:
                    script_sig = tx_in.script_pubkey(self.testnet)
            # Otherwise, the ScriptSig is empty
            else:
                script_sig = None
            # add the serialization of the input with the ScriptSig we want
            s += TxIn(
                prev_tx=tx_in.prev_tx,
                prev_index=tx_in.prev_index,
                script_sig=script_sig,
                sequence=tx_in.sequence,
            ).serialize()
        # add how many outputs there are using encode_varint
        s += encode_varint(len(self.tx_outs))
        # add the serialization of each output
        for tx_out in self.tx_outs:
            s += tx_out.serialize()
        # add the locktime using int_to_little_endian in 4 bytes
        s += int_to_little_endian(self.locktime, 4)
        # add SIGHASH_ALL using int_to_little_endian in 4 bytes
        s += int_to_little_endian(SIGHASH_ALL, 4)
        # hash256 the serialization
        h256 = hash256(s)
        # convert the result to an integer using int.from_bytes(x, 'big')
        # this is because we sign a scalar (recall ecc implementation)
        return int.from_bytes(h256, 'big')

    def verify_input(self, input_index, redeem_script = None):
        '''Returns whether the input has a valid signature'''
        # If it's a p2sh the redeem_script is used generate sig_hash
        # get the relevant input
        tx_in = self.tx_ins[input_index]
        # grab the previous ScriptPubKey
        script_pubkey = tx_in.script_pubkey(testnet=self.testnet)

        # passing the redeemscript in case of P2SH
        z = self.sig_hash(input_index, redeem_script)

        # combine the current ScriptSig and the previous ScriptPubKey
        # This is checked once the transaction has been signed
        combined = tx_in.script_sig + script_pubkey
        # evaluate the combined script
        return combined.evaluate(z)

    def verify(self, redeem_script = None):
        '''Verify this transaction'''
        # check that we're not creating money
        if self.fee() < 0:
            return False
        # check that each input has a valid ScriptSig
        for i in range(len(self.tx_ins)):
            if not self.verify_input(i, redeem_script):
                return False
        return True

    # This sets the ScriptSig for spending stuff; it basically provides the correct signature
    # Useful for p2pk and p2pkh
    def sign_input(self, input_index, private_key, redeem_script=None):
        '''Signs the input using the private key'''
        # get the signature hash (z)
        z = self.sig_hash(input_index,redeem_script)
        # get der signature of z from private key
        der = private_key.sign(z).der()
        # append the SIGHASH_ALL to der (use SIGHASH_ALL.to_bytes(1, 'big'))
        sig = der + SIGHASH_ALL.to_bytes(1, 'big')
        # calculate the sec
        sec = private_key.point.sec()
        # Handle p2pkh first
        if redeem_script == None:
            # initialize a new script with [sig, sec] as the cmds        
            script_sig = Script([sig, sec])
        # Else we are dealing with a p2sh
        else:
            script_sig = Script([sig, sec, redeem_script.raw_serialize()])
        # change input's script_sig to new script
        self.tx_ins[input_index].script_sig = script_sig
        # return whether sig is valid using self.verify_input
        return self.verify_input(input_index,redeem_script)

class TxIn:

    def __init__(self, prev_tx, prev_index, script_sig=None, sequence=0xffffffff):
        self.prev_tx = prev_tx
        self.prev_index = prev_index
        if script_sig is None:
            self.script_sig = Script()
        else:
            self.script_sig = script_sig
        self.sequence = sequence

    def __repr__(self):
        return '{}:{}'.format(
            self.prev_tx.hex(),
            self.prev_index,
        )

    @classmethod
    def parse(cls, s):
        '''Takes a byte stream and parses the tx_input at the start
        return a TxIn object
        '''
        # prev_tx is 32 bytes, little endian
        prev_tx = s.read(32)[::-1]
        # prev_index is an integer in 4 bytes, little endian
        prev_index = little_endian_to_int(s.read(4))
        # use Script.parse to get the ScriptSig
        script_sig = Script.parse(s)
        # sequence is an integer in 4 bytes, little-endian
        sequence = little_endian_to_int(s.read(4))
        # return an instance of the class (see __init__ for args)
        return cls(prev_tx, prev_index, script_sig, sequence)

    def serialize(self):
        '''Returns the byte serialization of the transaction input'''
        # serialize prev_tx, little endian
        result = self.prev_tx[::-1]
        # serialize prev_index, 4 bytes, little endian
        result += int_to_little_endian(self.prev_index, 4)
        # serialize the script_sig
        result += self.script_sig.serialize()
        # serialize sequence, 4 bytes, little endian
        result += int_to_little_endian(self.sequence, 4)
        return result

    def fetch_tx(self, testnet=False):
        return TxFetcher.fetch(self.prev_tx.hex(), testnet=testnet)

    def value(self, testnet=False):
        '''Get the outpoint value by looking up the tx hash
        Returns the amount in satoshi
        '''
        # use self.fetch_tx to get the transaction
        tx = self.fetch_tx(testnet=testnet)
        # get the output at self.prev_index
        # return the amount property
        return tx.tx_outs[self.prev_index].amount

    def script_pubkey(self, testnet=False):
        '''Get the ScriptPubKey by looking up the tx hash
        Returns a Script object
        '''
        # use self.fetch_tx to get the transaction
        tx = self.fetch_tx(testnet=testnet)
        # get the output at self.prev_index
        # return the script_pubkey property
        return tx.tx_outs[self.prev_index].script_pubkey


class TxOut:

    def __init__(self, amount, script_pubkey):
        self.amount = amount
        self.script_pubkey = script_pubkey

    def __repr__(self):
        return '{}:{}'.format(self.amount, self.script_pubkey)

    @classmethod
    def parse(cls, s):
        '''Takes a byte stream and parses the tx_output at the start
        return a TxOut object
        '''
        # amount is an integer in 8 bytes, little endian
        amount = little_endian_to_int(s.read(8))
        # use Script.parse to get the ScriptPubKey
        script_pubkey = Script.parse(s)
        # return an instance of the class (see __init__ for args)
        return cls(amount, script_pubkey)

    def serialize(self):
        '''Returns the byte serialization of the transaction output'''
        # serialize amount, 8 bytes, little endian
        result = int_to_little_endian(self.amount, 8)
        # serialize the script_pubkey
        result += self.script_pubkey.serialize()
        return result


'''
######################
########TEST1#########
######################
# Here we just check that the parser works, that we can fetch an output from a full node, and that fees add up

raw_tx = bytes.fromhex('0100000001813f79011acb80925dfe69b3def355fe914bd1d96a3f5f71bf8303c6a989c7d1000000006b483045022100ed81ff192e75a3fd2304004dcadb746fa5e24c5031ccfcf21320b0277457c98f02207a986d955c6e0cb35d446a89d3f56100f4d7f67801c31967743a9c8e10615bed01210349fc4e631e3624a545de3f89f5d8684c7b8138bd94bdd531d2e213bf016b278afeffffff02a135ef01000000001976a914bc3b654dca7e56b04dca18f2566cdaf02e8d9ada88ac99c39800000000001976a9141c4bc762dd5423e332166702cb75f40df79fea1288ac19430600')
stream = BytesIO(raw_tx)
tx = Tx.parse(stream)

print('Output1:',tx.fee())

## Hints:

# Which transaction is the first input using
# This has to be in hex()
ttIN = tx.tx_ins[0].prev_tx.hex()

# Which output of this transaction is being spent?
ttIndex = tx.tx_ins[0].prev_index

# How do we receive this? We fetch it!
txInput = TxFetcher.fetch(ttIN, testnet = True)

# How much is the amount?
print(txInput.tx_outs[ttIndex].amount)

'''


###########################################
########P2PKH to P2PKH transaction#########
###########################################

'''

#My address:
#secret = hash256(b'IIC3272Sucks')
#intSecret = int(secret.hex(),16)
#privKey = PrivateKey(intSecret)
#address = privKey.point.address(compressed = True, testnet = True)
#print(address)
# this is n3jKhCmVjvaVgg8C5P7E48fdRkQAAvf7Wc
# ask testcoins to the faucet: https://coinfaucet.eu/en/btc-testnet/

# GOTO :
# https://blockstream.info/testnet/address/n3jKhCmVjvaVgg8C5P7E48fdRkQAAvf7Wc

#newSecret = hash256(b'ThisIsDumb##JKl45')
#newIntSecret = int(newSecret.hex(),16)
#newPrivKey = PrivateKey(newIntSecret)
#newAddress = newPrivKey.point.address(compressed = True, testnet = True)
# what is computed above:
newAddress = 'mgQrZpj8BctqKqBXojUwdnHMaJMLpSYq68'

# First, we need to know which output we will be spending
# For the class:
tx_hash = '8fa9e05ef0212880434a0a2d18d36babe17b7a3310cc1679e9798f268acfd5a4'
tx_index = 1
# value = 141510


# Defining the input of our transaction (i.e. the output we will be spending)
newInput = TxIn(bytes.fromhex(tx_hash),tx_index)

# To define the output, we need an address
targetAddress = 'mgQrZpj8BctqKqBXojUwdnHMaJMLpSYq68'
# Since it's a p2pkh address we generate the script for this
ScriptPubkey = p2pkh_script_from_address(targetAddress)
# input value = 141510  -> output = 140000 for tx fee
newOutput = TxOut(140000,ScriptPubkey)

# Define a new testnet transaction
newTx = Tx(1,[newInput],[newOutput],0,True)

# We need to sign our input
# For this, we need the private key that controls this output:
secret = hash256(b'IIC3272Sucks')
intSecret = int(secret.hex(),16)
privKey = PrivateKey(intSecret)

input_index = 0
newTx.sign_input(input_index,privKey)

# Check that the transaction parses (fee>=0, sigs OK)
print(newTx.verify())

# Output the serialization:
print(newTx.serialize().hex())

# Push the previous hex here:
# https://live.blockcypher.com/btc/pushtx/

print('Tx hash:',newTx.id())

'''


#################################
########  P2PKH to P2SH #########
#################################
'''

# First, we need to know which output we will be spending
tx_hash = '230b66e03d9e6ac774ac1e9b93c4833505eca8c9e2cfb547c4d927271d9c1905'
tx_index = 1

# Defining the input of our transaction (i.e. the output we will be spending)
newInput = TxIn(bytes.fromhex(tx_hash),tx_index)

# To define the output, we need an address
targetAddress = '2NGZrVvZG92qGYqzTLjCAewvPZ7JE8S8VxE'
# Since it's a p2pkh address we generate the script for this
ScriptPubkey = p2sh_script_from_address(targetAddress)
# Define the output, leave some transaction fee here output = 1000, txfee = 9000
newOutput = TxOut(1000,ScriptPubkey)

# Define a new testnet transaction
newTx = Tx(1,[newInput],[newOutput],0,True)

# We need to sign our input
# For this, we need the private key that controls this output:
secret = hash256(b'IIC3272Sucks')
intSecret = int(secret.hex(),16)
privKey = PrivateKey(intSecret)

input_index = 0
newTx.sign_input(input_index,privKey)

# Check that the transaction parses (fee>=0, sigs OK)
print(newTx.verify())

# Output the serialization:
print(newTx.serialize().hex())

print('Tx hash:',newTx.id())
'''


'''
##################
### P2SH spend ###
##################
def addressP2SH(h160, testnet=False):
    #Returns the address string
    if testnet:
        prefix = b'\xc4'
    else:
        prefix = b'\x05'
    return encode_base58_checksum(prefix + h160)

newSecret = hash256(b'Jedan2Tri4Pet#$JKl45')
newIntSecret = int(newSecret.hex(),16)
newPrivKey = PrivateKey(newIntSecret)
#newAddress = newPrivKey.point.address(compressed = True, testnet = True)

#print(newAddress)

# Hard code the new p2pkh address (same as newAddress):
newAddress = 'n4LzQsUVB69f8mqytRrBzKLadFnR6go4dg'

# Generate script to be wrapped in P2SH:
redeemScript = p2pkh_script_from_address(newAddress)
# This needs to be raw serialized (no length prefix attached)
h160 = hash160(redeemScript.raw_serialize())

# The hash160 allows us to generate a p2sh address to receive funds 
address = addressP2SH(h160, testnet = True)

# The redeem script is wrapped up in this address (same as address; hardcoded)
miP2SHaddress = '2NGFxbNsuYN1dR7JkhBfUs4aMh4iXgtvWM9'

# To redeem: need to provide the redeem script + sign the thing
#unlocking = Script([sig,pubkey,redeemScript.raw_serialize()])

# Define the input:
tx_hash = 'b2c6107a3d6cd0f4d4fc5a92b48d310b27400da8e5d45a990573e0a4bc050a12'
tx_index = 1
#From tx fetcher I get the data: 10000:OP_HASH160 fc6e753c1ab33934ae26acbed2fbde8cf6d02b5f OP_EQUAL

# Input:
newInput = TxIn(bytes.fromhex(tx_hash),tx_index)

# To define the output, we need an address
targetAddress = 'n3jKhCmVjvaVgg8C5P7E48fdRkQAAvf7Wc'
# Since it's a p2pkh address we generate the script for this
ScriptPubkey = p2pkh_script_from_address(targetAddress)
# input value = 10000 output 5000; 5000 tx fee
newOutput = TxOut(5000,ScriptPubkey)

# Define a new testnet transaction
newTx = Tx(1,[newInput],[newOutput],0,True)
# Still unsigned

#What we will sign here (since it's a p2sh need to pass the redeemScript):
#to_sign = newTx.sig_hash(0,redeemScript)
#print(to_sign)

input_index = 0
newTx.sign_input(input_index,newPrivKey,redeemScript)

# This is what I will send to the network:
print('Signed transaction:', newTx.serialize().hex())
# The transaction hash in hex:
print('Transaction hash:', newTx.id())




'''






# What follows is a breakdown of the serializations we need:

##what we're signing: 
#'''
#01000000 01 120a05bca4e07305995ad4e5a80d40270b318db4925afcd4f4d06c3d7a10c6b2 01000000 
#19 76a914fa6880440b3d30769851b637bf829142597a708d88ac <---- REDEEM SCRIPT
#ffffffff 01 88 13000000000000 19 76 a9 14f3a99f3392f0d4a8d87c05841335d9f66c1ae32c 88 ac 00000000 01000000
#
#IMPORTANT: the redeem script is raw_serialize() (without the 19 for length);
#this is because it will get serialized again when we put it into the scriptSig for signing
#if we pushed serialize(), we would get a1 19 76a914fa6880440b3d30769851b637bf829142597a708d88ac
#That is, the length would be of the complete serialization, and not just of the scrupt itself
#
#
#
## This is the result of signing broken down into pieces:
#
## The signed Tx:
#
#01000000 .. version
#
#01 .. nr inputs
#
#120a05bca4e07305995ad4e5a80d40270b318db4925afcd4f4d06c3d7a10c6b2 .. prev tx hash
#01000000 .. prev index
#
#84 -- full length of scriptsig
#
#47 .. length of der sig
#
#.. der sig:
#304402206f43e6c19c20baef931593a6a41cf2da0f5737d62b6ba399e8f067e19affaa61022069d5993f67004c63975657e760ba5f822ecf2e4aa348a6f8e4bf91d688179cb5
#
#01 --- SIGHASHALL
#
#21 03152c6f90a2d0269e1358696c739641c267339cb2b23e8e6cb6298377c64b177b .. len of key/sec pub key 
#
#19 .. length of redeem script 
#76a914fa6880440b3d30769851b637bf829142597a708d88ac .. redeem script
#
#ffffffff 01 88 13000000000000 19 76 a9 14f3a99f3392f0d4a8d87c05841335d9f66c1ae32c 88 ac 00000000 .. the rest; OK
#'''


####################
###P2SH spend end###
####################
