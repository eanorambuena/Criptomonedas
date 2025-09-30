from ecc import *

# Let's Define who the boss is
privKeyScrooge = PrivateKey(256)
pubKeyScrooge = privKeyScrooge.point
# Obviously this is a dumb PrivateKey and you should never use something like this
# All things have to be validated by Scrooge
# All coins need to be created by Scrooge
# So he will sign a lot of stuff


#participants in the system:

pkA = PrivateKey(100)
pkB = PrivateKey(200)
pkC = PrivateKey(300)
pkD = PrivateKey(400)
pkE = PrivateKey(500)

addressA = pkA.point
addressB = pkB.point
addressC = pkC.point
addressD = pkD.point
addressE = pkE.point
