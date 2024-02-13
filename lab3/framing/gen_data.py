import argparse
from pathlib import Path
import random

import common



FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--lines", type=int)
    parser.add_argument("-s", "--max_size", type=int)
    parser.add_argument("-o", "--output_path", type=str, default=ROOT / "data.txt")
    opt = parser.parse_args()
    return vars(opt)


def generate(lines: int, max_size: int) -> list:
    return [
        random.choices('01', k=random.randint(max_size / 2, max_size))
        for _ in range(lines)
    ]


def main(
    lines: int,
    max_size: int,
    output_path: str
):
    data = ["".join(line) for line in generate(lines, max_size)]
    with open(output_path, 'w') as output:
        output.write(common.get_lines(data))
    

if __name__ == "__main__":
    params = parse_args()
    main(**params)