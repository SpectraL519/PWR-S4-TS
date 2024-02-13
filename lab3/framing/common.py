import binascii



# Constants
FRAME_LEN = 32
ESCAPE_COUNT = 6
ESCAPE_SEQ = '0' + '1' * ESCAPE_COUNT + '0'
CRC_LEN = 32

def CRC32(data: str) -> str:
    # split the data into 8-bit chunks
    int_arr = [int(data[i : i + 8], 2) for i in range(0, len(data), 8)] 
    control_sum = binascii.crc32(bytes(int_arr))
    return format(control_sum, 'b').rjust(32, '0')

def get_lines(data: list) -> str:
    return '\n'.join(data) + '\n'