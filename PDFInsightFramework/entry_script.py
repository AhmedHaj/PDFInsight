import argparse
import os
import re
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
import plotly.express as px
import pandas as pd
from pyfiglet import figlet_format
from parse_pdf import parse_pdf
from convert_to_csv import feature_extraction1
from pymupdf import process_files
from feature_engineering import valid_header, is_modified, is_malformed
from ml_model import load_model
from ssdeep import generate_hash, compare_hashes

#def parse_args():
    #parser = argparse.ArgumentParser(description='PDF Scanner')
    #parser.add_argument('pdf_path', nargs='?', default=None, help='Path to input PDF file or directory')
    #parser.add_argument('--output', '-o', help='Path to output file')
    #parser.add_argument('--format', '-f', choices=['csv', 'json'], default='csv', help='Output format')
    #parser.add_argument('--language', '-l', default='en', help='Language of input file')
    #return parser.parse_args()

if __name__ == '__main__':
    print(figlet_format('PDF Analyzer DEMO (WIP!)') + "\n")
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
    
    file_names = df['file_name']
    df.drop(['file_name'], inplace=True, axis = 1)
    #df.drop(['pdf_path'], inplace = True, axis = 1)
    #df.drop(['contains_text'], inplace = True, axis = 1)
    


    print("Feature Engineering complete, outputting CSV file...")

    print("Generating predictions...")
    clf = load_model()

    predictions  = clf.predict(df)

    df['file_name'] = file_names
    df["Class"] = predictions
    print("Printing ssdeep hash...")
    generated_hashes = generate_hash(input_path)
    print("Comparing ssdeep hashes to known malicious hashes...")
    matching_hashes = compare_hashes(generated_hashes)
    print('Matching hashes:')
    for file_path, matching_hash, file_name, link in matching_hashes:
        print(f'File: {file_path}')
        print(f'Matching hash: {matching_hash}')
        print(f'File name: {file_name}')
        print(f'Link: {link}\n')
    
    # Dash web application
    app = dash.Dash(__name__)

    # Create visualizations
    malicious_pie_chart = px.pie(df, names='Class', title='Proportion of Malicious PDFs')
    top_features_bar_chart = px.bar(df, x='Class', y='JS', title='Top Features of Malicious PDFs')

    # Add the link column to the output_table DataFrame
    # Create a new DataFrame with the desired columns
    output_table = pd.DataFrame({'file_name': df['file_name'], 'prediction': df['Class']})
    output_table['link'] = ''
    for file_path, matching_hash, file_name, link in matching_hashes:
        output_table.loc[output_table['file_name'] == file_name, 'link'] = link

    # Dash layout
    app.layout = html.Div([
        html.H1("PDF Analyzer Dashboard"),
        html.H2("Proportion of Malicious PDFs"),
        dcc.Graph(figure=malicious_pie_chart),
        html.H2("Top Features of Malicious PDFs"),
        dcc.Graph(figure=top_features_bar_chart),
        html.H2("PDFs with Predictions and Matching Hashes"),
        dash_table.DataTable(
            id='pdf_table',
            columns=[{"name": i, "id": i} for i in output_table.columns],
            data=output_table.to_dict("records"),
            style_cell={'textAlign': 'left'},
            sort_action="native",
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                },
                {
                    'if': {'filter_query': '{prediction} = "malicious"'},
                    'backgroundColor': 'red',
                    'color': 'white'
                }
            ],
        )
        # Additional visualizations and components can be added here
    ]) 


    app.run_server(debug=False, host="0.0.0.0", port="8050")
