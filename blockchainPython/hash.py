import hashlib


# normal sha256
def hash(message):
    # will return bytes of the created sha256 object
    return hashlib.sha256(message).digest()


# double sha256
def hash256(message):
    """two rounds of sha256"""
    # will return bytes of the created sha256 object
    return hashlib.sha256(hashlib.sha256(message).digest()).digest()
