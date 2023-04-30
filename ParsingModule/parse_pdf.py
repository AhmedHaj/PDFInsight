import os
import subprocess
from datetime import datetime

def parse_pdf(input_path, output_dir):
    # Set the path to the directory containing pdfid.py
    pdfid_dir = "./"

    # Add the directory to the system PATH environment variable
    os.environ["PATH"] += os.pathsep + pdfid_dir

    # Get the current time and format it as a string
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Set the filename for the output file
    output_filename = current_time + ".log"
    output_path = os.path.join(output_dir, output_filename)

    # Set the arguments for running pdfid
    pdfid_args = ["python", "pdfid.py", "-s", input_path, "-o", output_path]

    # Run pdfid with the specified arguments
    subprocess.check_output(pdfid_args)

    return output_path


if __name__ == "__main__":
    # Prompt user for input and output paths
    input_path = input("Enter path to input directory: ")
    output_dir = "logs"

    # Call the parse_pdf function with the specified input and output paths
    parse_pdf(input_path, output_dir)

    print("PDF parsing complete.")

