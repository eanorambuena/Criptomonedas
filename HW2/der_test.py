from hw2 import Signature

# Dictionary of test cases for DER encoding
# Each case should have 'r', 's', and 'expected_der' (hex string)
der_test_cases = [
    { # https://github.com/jimmysong/programmingbitcoin/blob/master/code-ch04/answers.py
        "r": 0x37206a0610995c58074999cb9767b87af4c4978db68c06e8e6e81d282047a7c6,
        "s": 0x8ca63759c1157ebeaec0d03cecca119fc9a75bf8e6d0fa65c841c8e2738cdaec,
        "expected_der": "3045022037206a0610995c58074999cb9767b87af4c4978db68c06e8e6e81d282047a7c60221008ca63759c1157ebeaec0d03cecca119fc9a75bf8e6d0fa65c841c8e2738cdaec"
    },
]

def test_der():
    for case in der_test_cases:
        sig = Signature(case["r"], case["s"])
        actual_der = sig.der().hex()
        assert actual_der == case["expected_der"], f"DER mismatch for r={case['r']}, s={case['s']}: expected {case['expected_der']}, got {actual_der}"
        print(f"Test passed for r={case['r']}, s={case['s']}")

if __name__ == "__main__":
    test_der()
    print("All DER tests passed!")
