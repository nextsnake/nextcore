from nextcore.endpoint.interactions.request_verifier import RequestVerifier
from nacl.signing import SigningKey
from nacl.utils import random
from datetime import datetime
from pytest import mark

def test_works():
    timestamp = str(datetime.now())
    body = "Hello, world"

    secret = random()
    signing_key = SigningKey(secret)
    signed_message = signing_key.sign(f"{timestamp}{body}".encode())
    signature = signed_message.signature.hex()
    
    public_key = signing_key.verify_key.encode()
    request_verifier = RequestVerifier(public_key)

    assert request_verifier.is_valid(signature, timestamp, body), "Was marked as invalid"

def test_modified_body():
    timestamp = str(datetime.now())
    body = "Hello, world"

    secret = random()
    signing_key = SigningKey(secret)
    signed_message = signing_key.sign(f"{timestamp}{body}".encode())
    signature = signed_message.signature.hex()
    
    public_key = signing_key.verify_key.encode()
    request_verifier = RequestVerifier(public_key)

    body = body.replace("world", "space")

    assert not request_verifier.is_valid(signature, timestamp, body), "Was marked as valid even though body was modified"

def test_modified_timestamp():
    timestamp = str(datetime.now())
    body = "Hello, world"

    secret = random()
    signing_key = SigningKey(secret)
    signed_message = signing_key.sign(f"{timestamp}{body}".encode())
    signature = signed_message.signature.hex()
    
    public_key = signing_key.verify_key.encode()
    request_verifier = RequestVerifier(public_key)
    
    timestamp = "".join(reversed(timestamp))
    
    assert not request_verifier.is_valid(signature, timestamp, body), "Was marked as valid even though timestamp was modified"


def test_modified_signature():
    timestamp = str(datetime.now())
    body = "Hello, world"

    secret = random()
    signing_key = SigningKey(secret)
    signed_message = signing_key.sign(f"{timestamp}{body}".encode())
    signature = signed_message.signature.hex()
    
    public_key = signing_key.verify_key.encode()
    request_verifier = RequestVerifier(public_key)

    signature = "0x" + "".join(reversed(signature.replace("0x", "")))

    assert not request_verifier.is_valid(signature, timestamp, body), "Was marked as valid even though signature was modified"


@mark.parametrize("signature", [
    (bytes([0x0])),
    (bytes([0xFF])),
    (bytes([0xFF]*50)),
])
def test_malformed_signature(signature: bytes):
    timestamp = str(datetime.now())
    body = "Hello, world"

    secret = random()
    signing_key = SigningKey(secret)
    
    public_key = signing_key.verify_key.encode()
    request_verifier = RequestVerifier(public_key)

    assert not request_verifier.is_valid(signature, timestamp, body), "Was marked as valid even though signature is wrong"
