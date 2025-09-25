from hw2 import Signature

# Dictionary of test cases for DER encoding
# Each case should have 'r', 's', and 'expected_der' (hex string)
der_test_cases = [
    # Example:
    # {"r": 0x1b8702e527b5410464649721cffdead50944c251fb09727f55e2c54e1e56def,
    #  "s": 0x2a44f56715d0d9d4fa086539d261219f415fb474a2b74136c43ca462a862eda9,
    #  "expected_der": "3044022001b8702e527b5410464649721cffdead50944c251fb09727f55e2c54e1e56def02202a44f56715d0d9d4fa086539d261219f415fb474a2b74136c43ca462a862eda9"},
    # Add your test cases here
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
