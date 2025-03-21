import heapq
import pickle
import os
from collections import defaultdict, Counter
from pathlib import Path

class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

    def is_leaf(self):
        return self.left is None and self.right is None

def build_huffman_tree(text):
    frequency = Counter(text)
    priority_queue = [Node(char, freq) for char, freq in frequency.items()]
    heapq.heapify(priority_queue)

    while len(priority_queue) > 1:
        left = heapq.heappop(priority_queue)
        right = heapq.heappop(priority_queue)
        merged = Node(None, left.freq + right.freq)
        merged.left = left
        merged.right = right
        heapq.heappush(priority_queue, merged)

    return priority_queue[0]

def build_codes(root, prefix='', codebook=None):
    if codebook is None:
        codebook = defaultdict(str)
    if root is not None:
        if root.is_leaf():
            codebook[root.char] = prefix
        build_codes(root.left, prefix + '0', codebook)
        build_codes(root.right, prefix + '1', codebook)
    return codebook

def encode(text, codebook):
    return ''.join(codebook[char] for char in text)

def decode(encoded_text, root):
    decoded_chars = []
    current_node = root
    for bit in encoded_text:
        if bit == '0':
            current_node = current_node.left
        else:
            current_node = current_node.right

        if current_node is None:
            raise ValueError("Decoding error: reached a None node in Huffman tree")

        if current_node.is_leaf():
            decoded_chars.append(current_node.char)
            current_node = root

    return ''.join(decoded_chars)

def write_bits(filename, bit_string):
    with open(filename, 'wb') as file:
        # Corrected padding calculation: no extra padding if already a multiple of 8.
        padding = (8 - len(bit_string) % 8) % 8
        bit_string = bit_string + '0' * padding  # Add padding bits
        byte_array = bytearray(int(bit_string[i:i + 8], 2) for i in range(0, len(bit_string), 8))
        file.write(bytes([padding]))
        file.write(byte_array)

def read_bits(filename):
    with open(filename, 'rb') as file:
        padding = file.read(1)[0]
        bit_string = ''.join(f'{byte:08b}' for byte in file.read())
        if padding:
            bit_string = bit_string[:-padding]
        return bit_string

def compress_file(input_file_path, output_file_path):
    with open(input_file_path, 'r') as file:
        text = file.read()

    root = build_huffman_tree(text)
    codebook = build_codes(root)
    encoded_text = encode(text, codebook)

    print(f"Text to be encoded (first 100 chars): {text[:100]}")
    print(f"Encoded text (first 100 bits): {encoded_text[:100]}")
    print(f"Codebook: {codebook}")

    # Save the codebook in a separate file (with .codebook extension)
    codebook_path = output_file_path.with_suffix(".codebook")
    with open(codebook_path, 'wb') as file:
        pickle.dump(codebook, file)

    # Save the encoded bits to the output file
    write_bits(output_file_path, encoded_text)

def build_tree_from_code(codebook):
    root = Node(None, 0)
    for char, code in codebook.items():
        node = root
        for bit in code:
            if bit == '0':
                if node.left is None:
                    node.left = Node(None, 0)
                node = node.left
            else:
                if node.right is None:
                    node.right = Node(None, 0)
                node = node.right
        node.char = char
    return root

def decompress_file(input_file_path, output_file_path):
    # Load the codebook from the separate file
    codebook_path = input_file_path.with_suffix(".codebook")
    with open(codebook_path, 'rb') as file:
        codebook = pickle.load(file)

    encoded_text = read_bits(input_file_path)
    root = build_tree_from_code(codebook)

    if root is None:
        raise ValueError("Failed to build Huffman tree from codebook.")

    decoded_text = decode(encoded_text, root)

    with open(output_file_path, 'w') as file:
        file.write(decoded_text)

def stats(uncompressed_file_path, compressed_file_path):
    uncompressed_size = os.path.getsize(uncompressed_file_path)
    compressed_size = os.path.getsize(compressed_file_path)
    print(f"Size of Uncompressed File: {uncompressed_size / 1e6:.2f} MB")
    print(f"Size of Compressed File: {compressed_size / 1e6:.2f} MB")
    print(f"Compression Ratio: {compressed_size / uncompressed_size:.2f}")

if __name__ == '__main__':
    input_file_path = Path('/home/saivinay/Documents/Projects/text-compression/test.txt')
    compressed_file_path = Path('/home/saivinay/Documents/Projects/text-compression/compressed.bin')
    decompressed_file_path = Path('/home/saivinay/Documents/Projects/text-compression/decompressed.txt')

    compress_file(input_file_path, compressed_file_path)
    decompress_file(compressed_file_path, decompressed_file_path)
    stats(input_file_path, compressed_file_path)
