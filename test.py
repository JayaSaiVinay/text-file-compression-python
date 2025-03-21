import os
from pathlib import Path
import main
from main import compress_file, decompress_file, stats

def test_compression(file_path):
    """
    Compresses and decompresses a file, checks if decompression is successful,
    and prints file size statistics.
    """
    compressed_file_path = file_path.with_suffix(".bin")
    decompressed_file_path = file_path.with_name(file_path.stem + "_decompressed.txt")

    print(f"\nProcessing {file_path.name}...")

    # Compress the file
    compress_file(file_path, compressed_file_path)

    # Decompress the file
    decompress_file(compressed_file_path, decompressed_file_path)

    # Verify decompression correctness
    with open(file_path, 'r') as orig, open(decompressed_file_path, 'r') as decomp:
        if orig.read() == decomp.read():
            print(f"{file_path.name}: Decompression successful.")
        else:
            print(f"{file_path.name}: Decompression failed! Files do not match.")

    # Print compression stats
    stats(file_path, compressed_file_path)
    print("-" * 50)

if __name__ == '__main__':
    test_dir = Path(".") 
    for i in range(1, 7):
        file_path = test_dir / f"test{i}.txt"
        if file_path.exists():
            test_compression(file_path)
        else:
            print(f"{file_path.name} not found. Skipping.")
