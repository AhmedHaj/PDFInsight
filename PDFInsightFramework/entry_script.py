import argparse
import os
import hashlib
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

def sha256_hash(file_path):
    with open(file_path, 'rb') as f:
        bytes = f.read()
        return hashlib.sha256(bytes).hexdigest()

def vt_detections(file_path):
    # Use your existing code to get the number of detections on VirusTotal
    detections = 0  # Replace this line with your implementation
    total_vendors = 60
    percentage = (detections / total_vendors) * 100
    return f"{detections}/{total_vendors} ({percentage:.1f}%)"

if __name__ == '__main__':
    print(figlet_format('PDFInsight') + "\n")

    input_path = input("Enter path to input directory: ")
    output_dir = "logs"

    print("Starting PDF parsing...")
    preprocessed_logs = parse_pdf(input_path, output_dir)
    
    print("PDF parsing complete, starting feature extraction...")
    df1 = feature_extraction1(preprocessed_logs)
    df2 = process_files(input_path)
    df = pd.merge(df1, df2, on='file_name', how='left')
    
    print("Feature extraction complete, starting feature engineering...")
    
    df['valid_header'] = df.apply(lambda row : valid_header(row['pdf_header']), axis = 1)
    df.drop(['pdf_header'], inplace=True, axis=1)
    
    column_types = {col: 'int64' for col in df.columns if col != 'file_name'}
    df = df.astype(column_types)

    df['modified'] = df.apply(lambda row : is_modified(row['xref']), axis = 1)
    df['malformed'] = df.apply(lambda row : is_malformed(row['obj'],row['endobj'], row['stream'], row['endstream']), axis = 1)

    df.to_csv(f'preprocessed-PDFs.csv', index = False)
    
    file_names = df['file_name']
    df.drop(['file_name'], inplace=True, axis = 1)

    print("Feature Engineering complete, outputting CSV file...")

    print("Generating predictions...")
    clf = load_model()

    predictions  = clf.predict(df)
    confidence_scores = clf.predict_proba(df)[:, 1] * 100

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

    app = dash.Dash(__name__)

    malicious_pie_chart = px.pie(df, names='Class', title='Proportion of Malicious PDFs')
    top_features_bar_chart = px.bar(df, x='Class', y='JS', title='Top Features of Malicious PDFs')

    output_table = pd.DataFrame({'file_name': df['file_name'], 'sha256': '', 'VT Detections': '', 'prediction': df['Class'], 'Confidence Score': confidence_scores})
    for index, row in output_table.iterrows():
        file_path = os.path.join(input_path, row['file_name'])
        output_table.loc[index, 'sha256'] = sha256_hash(file_path)
        output_table.loc[index, 'VT Detections'] = vt_detections(file_path)
    
    output_table['link'] = ''
    for file_path, matching_hash, file_name, link in matching_hashes:
        output_table.loc[output_table['file_name'] == file_name+'.pdf', 'link'] = link

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
            style_cell={
                'textAlign': 'left',
                'fontFamily': 'Arial',
                'fontSize': 16,
            },
            sort_action="native",
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                },
                {
                    'if': {'filter_query': '{prediction} = "malicious"'},
                    'backgroundColor': '#ff9999',
                    'color': 'black'
                }
            ],
        )
    ])

    app.run_server(debug=False, host="0.0.0.0", port="8050")

