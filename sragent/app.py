from flask import Flask, render_template, request, jsonify, send_from_directory
import os
from sragent import gather
import pandas as pd
import json

app = Flask(__name__)

# Directory where the output files are stored
OUTPUT_DIR = 'sragent_output'

@app.route('/')
def index():
    # Render the single-page layout
    return render_template('index.html')

@app.route('/files')
def list_files():
    # List all files in the output directory
    files = os.listdir(OUTPUT_DIR)
    return jsonify(files)

@app.route('/file/<filename>')
def get_file(filename):

    if '.csv' in filename:
        with open(os.path.join(OUTPUT_DIR, filename), 'r') as f:
            df = pd.read_csv(f)
#            return df.to_html(header = 'true', index = False, table_id = 'csv-table')
            content = jsonify(content=json.loads(df.to_json(orient='split'))['data'],
                              columns=[{"title": str(col)} for col in json.loads(df.to_json(orient="split"))["columns"]])
            print(content)
            return content 

    elif '.txt' in filename:
        with open(os.path.join(OUTPUT_DIR, filename), 'r') as f:
            content = f.read()
        return jsonify(content=content)
    else:
        return send_from_directory(OUTPUT_DIR, filename)

@app.route('/file/edit/<filename>', methods=['POST'])
def edit_file(filename):
    # Save the modified content to the file
    new_content = request.json['content']
    with open(os.path.join(OUTPUT_DIR, filename), 'w') as f:
        f.write(new_content)
    return jsonify(success=True)

if __name__ == '__main__':
    app.run(debug=True)
