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

def create_hashes_csv(results, output_file='hashes.csv'):
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['file_name', 'hash', 'link']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for file_path, ssdeep_hash in results:
            file_name = os.path.basename(file_path)
            link = f'https://example.com/{file_name}'  # Replace with actual link
            writer.writerow({'file_name': file_name, 'hash': ssdeep_hash, 'link': link})

if __name__ == '__main__':
    path = '../testing'
    results = generate_hash(path)

    for file_path, ssdeep_hash in results:
        print(f'File: {file_path}')
        print(f'SSDeep hash: {ssdeep_hash}\n')

    create_hashes_csv(results)
