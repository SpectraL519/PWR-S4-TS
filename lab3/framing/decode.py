import argparse
from pathlib import Path

import common



FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_path", type=str, default=ROOT / "W.txt")
    parser.add_argument("-o", "--output_path", type=str, default=ROOT / "Z.txt")
    parser.add_argument("-d", "--debug", action="store_true")
    opt = parser.parse_args()
    return vars(opt)


def decode(data: str, debug: bool) -> str:
    decoded = ""
    frame = ""

    num_ones = 0
    num_correct_frames = 0

    while data:
        bit = data[0]

        if bit == '1':
            num_ones += 1
            frame = "" if num_ones > common.ESCAPE_COUNT else frame + bit
        else:
            if num_ones == common.ESCAPE_COUNT:
                # remove trailing escape sequence
                frame = frame[:-(common.ESCAPE_COUNT + 1)]
                if frame:
                    payload = frame[:-common.CRC_LEN]
                    crc = frame[-common.CRC_LEN:]

                    # verify the crc
                    if crc == common.CRC32(payload):
                        if (debug): print(f"frame {num_correct_frames}: {frame}")
                        num_correct_frames += 1
                        decoded += payload
                    else: 
                        if (debug): print("Frame with invalid CRC")
                frame = ""

            elif num_ones == common.ESCAPE_COUNT - 1:
                pass # additional 0 added by encoding
            else: frame += bit
            num_ones = 0

        data = data[1:]

    if debug:
        print(f"{num_correct_frames=}")

    return decoded
    


def main(
    input_path: str, 
    output_path: str, 
    debug: bool
):
    with open(input_path, 'r') as input:
        input_data = input.read().splitlines()

    output_data = [decode(data, debug) for data in input_data]
    with open(output_path, 'w') as output:
        output.write(common.get_lines(output_data))


if __name__ == "__main__":
    params = parse_args()
    main(**params)