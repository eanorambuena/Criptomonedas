from hw2 import S256Point, S256Field, A, B, P

def parse_sec(sec_bytes: bytes) -> S256Point:
    if sec_bytes[0] == 0x04:  # Uncompressed
        x = int.from_bytes(sec_bytes[1:33], 'big')
        y = int.from_bytes(sec_bytes[33:65], 'big')
        return S256Point(x, y)
    elif sec_bytes[0] in (0x02, 0x03):  # Compressed
        x = int.from_bytes(sec_bytes[1:33], 'big')
        # y^2 = x^3 + 7 mod P
        x_field = S256Field(x)
        y_squared = x_field ** 3 + S256Field(B)
        # Compute modular square root: for P ≡ 3 mod 4, sqrt = pow(y_squared.num, (P+1)//4, P)
        exp = (P + 1) // 4
        y_num = pow(y_squared.num, exp, P)
        # Verify
        if pow(y_num, 2, P) != y_squared.num:
            raise ValueError("Invalid SEC format: no square root")
        # Choose the correct parity
        if sec_bytes[0] == 0x02:
            y = y_num if y_num % 2 == 0 else P - y_num
        else:  # 0x03
            y = y_num if y_num % 2 == 1 else P - y_num
        return S256Point(x, y)
    else:
        raise ValueError("Invalid SEC format")

def test_sec_parser():
    # Test with some points
    test_points = [
        (0x7211a824f55b505228e4c3d5194c1fcfaa15a456abdf37f9b9d97a4040afc073,
         0xdee6c89064984f03385237d92167c13e236446b417ab79a0fcae412ae3316b77),
    ]
    
    for x, y in test_points:
        point = S256Point(x, y)
        # Test uncompressed
        sec_uncompressed = point.sec(compressed=False)
        parsed_point = parse_sec(sec_uncompressed)
        assert point == parsed_point, f"Uncompressed parse failed for point {point}"
        print(f"Uncompressed test passed for point {point}")
        
        # Test compressed
        sec_compressed = point.sec(compressed=True)
        parsed_point_comp = parse_sec(sec_compressed)
        assert point == parsed_point_comp, f"Compressed parse failed for point {point}"
        print(f"Compressed test passed for point {point}")

if __name__ == "__main__":
    test_sec_parser()
    print("All SEC parser tests passed!")