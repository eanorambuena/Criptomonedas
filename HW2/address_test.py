from hw2 import S256Point

# Dictionary of test cases for Bitcoin addresses
# Each case should have 'x', 'y', 'compressed' (bool), 'testnet' (bool), and 'expected_address' (string)
address_test_cases = [
    # Example:
    # {"x": 0x852e3a8f4e64ee65624872095c466dccd460dcc85d4bab56ec2625b920677014d4,
    #  "y": 0x895949efe57596ee4ed9bad45fb24b2a9df7686bb700e672f62a56860c1380,
    #  "compressed": True,
    #  "testnet": True,
    #  "expected_address": "mnWaVwJYCFKK3nCriPFfHD9wLKhz9RVbcy"},
    { # https://learnmeabitcoin.com/beginners/guide/keys-addresses/
        "x": 0xef235aacf90d9f4aadd8c92e4b2562e1d9eb97f0df9ba3b508258739cb013db2,
        "y": 0x02b4632d08485ff1df2db55b9dafd23347d1c47a457072a1e87be26896549a8737,
        "compressed": True,
        "testnet": False,
        "expected_address": "1EUXSxuUVy2PC5enGXR1a3yxbEjNWMHuem"
    },
]

def test_address():
    for case in address_test_cases:
        point = S256Point(case["x"], case["y"])
        actual_address = point.address(compressed=case["compressed"], testnet=case["testnet"])
        assert actual_address == case["expected_address"], f"Address mismatch for x={case['x']}, y={case['y']}, compressed={case['compressed']}, testnet={case['testnet']}: expected {case['expected_address']}, got {actual_address}"
        
        # Check prefix
        if case["testnet"]:
            assert actual_address.startswith(('m', 'n')), f"Testnet address should start with 'm' or 'n', got {actual_address}"
        else:
            assert actual_address.startswith('1'), f"Mainnet address should start with '1', got {actual_address}"
        
        print(f"Test passed for x={case['x']}, y={case['y']}, compressed={case['compressed']}, testnet={case['testnet']}")

if __name__ == "__main__":
    test_address()
    print("All address tests passed!")