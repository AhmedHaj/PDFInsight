import os
import pandas as pd
import sys
import fitz

def process_files(path):
    res = pd.DataFrame(columns=['file_name', 'pdfsize', 'metadata_size', 'pages', 'xref_length', 'title_chars', 'is_encrypted', 'embedded_files', 'images', 'contains_text'])

    def process_path(path):
        if os.path.isdir(path):
            print(path)
            for filename in os.listdir(path):
                filepath = os.path.join(path, filename)
                process_path(filepath)

        else:
            file_name = os.path.basename(path)
            try:
                pdf = fitz.open(path)
            except:
                res.loc[len(res)] = [file_name, -1, -1, -1, -1, -1, -1, -1, -1, -1]
                return

            # Initialize default values for features
            title = "-1"
            is_encrypted = -1
            metadata = pdf.metadata
            pdfsize = -1
            xref_length = -1
            pages = -1
            contains_text = -1
            embedded_files = -1
            images = -1

            try:
                title = metadata.get('title', '')
            except:
                pass

            try:
                is_encrypted = 1 if metadata.get('encryption') else 0
            except:
                pass

            try:
                xref_length = pdf.xref_length()
            except:
                pass

            try:
                pages = pdf.page_count
            except:
                pass

            try:
                pdfsize = os.path.getsize(path) // 1000
            except:
                pass

            try:
                contains_text = 1 if any(page.get_text() for page in pdf) else 0
            except:
                pass

            try:
                embedded_files = pdf.embfile_count()
            except:
                pass

            try:
                images = sum(len(pdf.get_page_images(p)) for p in range(pages))
            except:
                pass

            res.loc[len(res)] = [file_name, pdfsize, len(str(metadata).encode('utf-8')), pages, xref_length, len(title), is_encrypted, embedded_files, images, contains_text]

    process_path(path)
    return res

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_directory> <output_csv>")
        sys.exit(1)

    input_directory = sys.argv[1]
    output_csv = sys.argv[2]

    if not os.path.isdir(input_directory):
        print(f"Error: {input_directory} is not a valid directory.")
        sys.exit(1)

    result = process_files(input_directory)
    result.to_csv(output_csv, index=False)
    print(f"Features extracted and saved to {output_csv}")

if __name__ == "__main__":
    main()