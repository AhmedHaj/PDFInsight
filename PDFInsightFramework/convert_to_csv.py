import re
import pandas as pd
from tqdm import tqdm
import os

def feature_extraction1(path_to_pdf):
    # get the current working directory
    dir_path = os.getcwd()

    # iterate over all the files in the directory
    for file in os.listdir(dir_path):
        # check if the file is a regular file (not a directory)
        if os.path.isfile(os.path.join(dir_path, file)):
            print(file)
    with open(path_to_pdf) as f:
        f = f.read()
        test = f.split('PDFiD 0.2.1')

    #cols = ['pdf_header', 'file_name', 'obj', 'endobj', 'stream', 'endstream', 'xref', 'trailer', 'startxref', 'pageno', 'encrypt', 'objstm', 'JS', 'javascript', 'AA', 'OpenAction', 'AcroForm', 'JBIG2Decode', 'RichMedia', 'Launch', 'embeddedfile', 'XFA', 'title', 'nametag', 'font', 'FlatDecode', 'URI', 'colors', 'obfuscations', 'Class']
    cols = ['pdf_header', 'file_name', 'obj', 'endobj', 'stream', 'endstream', 'xref', 'trailer', 'startxref', 'pageno', 'encrypt', 'objstm', 'JS', 'javascript', 'AA', 'OpenAction', 'AcroForm', 'JBIG2Decode', 'RichMedia', 'Launch', 'embeddedfile', 'XFA', 'title', 'nametag', 'font', 'FlatDecode', 'URI', 'colors', 'obfuscations']

    col_map = {i: cols[i-1] for i in range(1,30)}
    lists = {i: [] for i in range(1,30)}

    print(f'''\n\nGenerating Features using modified PDFiD...''')
    for entry in tqdm(test):
        obfuscations = 0
        for k, line in enumerate(entry.split("\n")):
            if 'Not a PDF document' in line:
                break

            if k == 1:
                try:
                    value = re.search(r': (.*)', line).groups()
                except:
                    value = [-1]

                lists[k].append(value[0])
                #lists[30].append('Malicious')
            
            elif k == 2:
                try:
                    value = re.search(r'\/.*\/(.*)', line).groups()
                except:
                    value = [-1]

                lists[k].append(value[0])
                
            elif 3 <= k <= 28:
                try:
                    value = re.search(r'   (\d+)', line).groups()
                except:
                    value = [-1]
                
                try:
                    value_ob = re.search(r'   \d+\((\d+)\)', line).groups()
                except:
                    value_ob = [0]
                
                lists[k].append(value[0])
                obfuscations += int(value_ob[0])
            
            elif k == 29:
                lists[k].append(obfuscations)

            else:
                continue
        

    df = pd.DataFrame(columns=cols)
    for j in range(1, 30):
        df[col_map[j]] = lists[j]

    return df