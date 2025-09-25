from hw2 import S256Point

# Dictionary of test cases for SEC encoding
# Each case should have 'x', 'y', 'compressed' (bool), and 'expected_sec' (hex string)
sec_test_cases = [
    # Example:
    # {"x": 0x852e3a8f4e64ee65624872095c466dccd460dcc85d4bab56ec2625b920677014d4,
    #  "y": 0x895949efe57596ee4ed9bad45fb24b2a9df7686bb700e672f62a56860c1380,
    #  "compressed": False,
    #  "expected_sec": "04852e3a8f4e64ee65624872095c466dccd460dcc85d4bab56ec2625b920677014d4895949efe57596ee4ed9bad45fb24b2a9df7686bb700e672f62a56860c1380"},
    { # https://www.oreilly.com/library/view/programming-bitcoin/9781492031482/ch04.html
        "x": 0x7211a824f55b505228e4c3d5194c1fcfaa15a456abdf37f9b9d97a4040afc073,
        "y": 0xdee6c89064984f03385237d92167c13e236446b417ab79a0fcae412ae3316b77,
        "compressed": False,
        "expected_sec": "047211a824f55b505228e4c3d5194c1fcfaa15a456abdf37f9b9d97a4040afc073dee6c89064984f03385237d92167c13e236446b417ab79a0fcae412ae3316b77"
    },
]

def test_sec():
    for case in sec_test_cases:
        point = S256Point(case["x"], case["y"])
        actual_sec = point.sec(case["compressed"]).hex()
        assert actual_sec == case["expected_sec"], f"SEC mismatch for x={case['x']}, y={case['y']}, compressed={case['compressed']}: expected {case['expected_sec']}, got {actual_sec}"
        print(f"Test passed for x={case['x']}, y={case['y']}, compressed={case['compressed']}")

if __name__ == "__main__":
    test_sec()
    print("All SEC tests passed!")