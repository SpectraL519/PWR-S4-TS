import argparse
from pathlib import Path

import common



FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_path", type=str, default=ROOT / "data.txt")
    parser.add_argument("-o", "--output_path", type=str, default=ROOT / "W.txt")
    parser.add_argument("-d", "--debug", action="store_true")
    opt = parser.parse_args()
    return vars(opt)


def encode(data: str, debug: bool) -> str:
    encoded = ""
    num_frames = 0

    for frame_begin in range(0, len(data), common.FRAME_LEN):
        # extract a frame from data
        frame = data[frame_begin : frame_begin + common.FRAME_LEN]
        if (debug): print(f"frame {num_frames}: {frame}")

        # add the control sum to the frame
        frame += common.CRC32(frame)
        
        encoded += common.ESCAPE_SEQ # frame begin
        num_ones = 0

        while frame:
            bit = frame[0]
            encoded += bit

            if bit == '1':
                num_ones += 1
                if num_ones == common.ESCAPE_COUNT - 1:
                    # add 0 to avoid passing an escape sequence in the middle of the frame
                    encoded += '0'
                    num_ones = 0
            else:
                num_ones = 0
            
            frame = frame[1:]
        
        encoded += common.ESCAPE_SEQ # frame end
        num_frames += 1

    if debug:
        print(f"{num_frames=}")
        
    return encoded
    


def main(
    input_path: str, 
    output_path: str, 
    debug: bool
):
    with open(input_path, 'r') as input:
        input_data = input.read().splitlines()

    output_data = [encode(data, debug) for data in input_data]
    with open(output_path, 'w') as output:
        output.write(common.get_lines(output_data))


if __name__ == "__main__":
    params = parse_args()
    main(**params)