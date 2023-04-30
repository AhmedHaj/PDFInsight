import pandas as pd
from pyfiglet import figlet_format
from parse_pdf import parse_pdf
from convert_to_csv import feature_extraction1
from pymupdf import process_files
from feature_engineering import valid_header, is_modified, is_malformed

#def parse_args():
    #parser = argparse.ArgumentParser(description='PDF Scanner')
    #parser.add_argument('pdf_path', nargs='?', default=None, help='Path to input PDF file or directory')
    #parser.add_argument('--output', '-o', help='Path to output file')
    #parser.add_argument('--format', '-f', choices=['csv', 'json'], default='csv', help='Output format')
    #parser.add_argument('--language', '-l', default='en', help='Language of input file')
    #return parser.parse_args()

if __name__ == '__main__':
    print(figlet_format('Parsing Module') + "\n")
    #args = parse_args()

    # Prompt user for input path
    input_path = input("Enter path to input directory: ")
    output_dir = "logs"

    print("Starting PDF parsing...")
    # Call the parse_pdf function with the specified input and output paths
    preprocessed_logs = parse_pdf(input_path, output_dir)
    
    print("PDF parsing complete, starting feature extraction...")
    df1 = feature_extraction1(preprocessed_logs)
    df2 = process_files(input_path)
    df = pd.merge(df1, df2, on='file_name', how='left')  # Merge df1 and df2 on file_name
    
    print("Feature extraction complete, starting feature engineering...")
    

    # apply function to each row 
    df['valid_header'] = df.apply(lambda row : valid_header(row['pdf_header']), axis = 1)
    df.drop(['pdf_header'], inplace=True, axis=1)
    
    # Create a dictionary of column names and their respective data types
    column_types = {col: 'int64' for col in df.columns if col != 'file_name'}

    # Apply the astype() method to the DataFrame with the created dictionary
    df = df.astype(column_types)


    df['modified'] = df.apply(lambda row : is_modified(row['xref']), axis = 1)
    df['malformed'] = df.apply(lambda row : is_malformed(row['obj'],row['endobj'], row['stream'], row['endstream']), axis = 1)

    df.to_csv(f'preprocessed-PDFs.csv', index = False)

    print("Outputted files to: preprocessed-PDFs.csv")