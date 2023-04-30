import os
import subprocess
import csv

import os
import subprocess
import re
import csv

def generate_hash(path):
    results = []

    def process_path(path):
        if os.path.isdir(path):
            for entry in os.listdir(path):
                entry_path = os.path.join(path, entry)
                process_path(entry_path)
        else:
            try:
                ssdeep_output = subprocess.check_output(['ssdeep', path])
                output = ssdeep_output.decode().strip()
                match = re.search(r'(\d+):(.+):(.+),', output)
                if match:
                    hash = match.group(2)
                    results.append((path, hash))
            except subprocess.CalledProcessError as e:
                print(f'Error processing file: {path}\n{e}\n')

    process_path(path)
    return results

def compare_hashes(generated_hashes, stored_hashes_file='hashes.csv'):
    with open(stored_hashes_file, 'r') as f:
        csv_reader = csv.reader(f)
        next(csv_reader)  # Skip the header
        stored_hashes = {(row[1]): (row[0], row[2]) for row in csv_reader}

    matching_hashes = [(file_path, hash, stored_hashes[hash][0], stored_hashes[hash][1]) for file_path, hash in generated_hashes if hash in stored_hashes]
    return matching_hashes

if __name__ == '__main__':
    path = '0_ea-2a_1108.pdf'
    results = generate_hash(path)

    for file_path, ssdeep_hash in results:
        print(f'File: {file_path}')
        print(f'SSDeep hash: {ssdeep_hash}\n')

    matching_hashes = compare_hashes(results)
    print('Matching hashes:')
    for file_path, matching_hash, file_name, link in matching_hashes:
        print(f'File: {file_path}')
        print(f'Matching hash: {matching_hash}')
        print(f'File name: {file_name}')
        print(f'Link: {link}\n')

