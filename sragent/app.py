from flask import Flask, render_template, request, jsonify, send_from_directory
import os
from sragent import gather 
import pandas as pd
import json

app = Flask(__name__)

# Directory where the output files are stored
OUTPUT_DIR = 'sragent_output'
#OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
#ENTREZ_API_KEY = os.getenv('ENTREZ_API_KEY')
#ENTREZ_EMAIL = os.getenv('ENTREZ_EMAIL')

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
            #df = df[["project_id", "project_title", "run_id","experiment_id","title","organism","assay_id"]]
            content = jsonify(content=json.loads(df.to_json(orient='split'))['data'],
                              columns=[{"title": str(col)} for col in json.loads(df.to_json(orient="split"))["columns"]])
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

@app.route('/gather', methods=['POST'])
def run_gather():
   project_id = request.json['project_id']
   project_list = project_id.split(',')
   metadata = gather(project_list)
   if metadata is not None:
       return 'success!'
   else:
       return 'failed!'

@app.route('/annotate', methods=['POST'])
def run_annotate():
    data = request.json['data']
    columns = request.json['columns']
    summary_model = request.json['summary_model']
    annotation_model = request.json['annotation_model']
    df = pd.DataFrame(data, columns = columns)
    annotation = gather(df, summary_model, annotation_model, annotate_meta=True)
    print(annotation)
    return 'butt' 


if __name__ == '__main__':
    app.run(debug=True, port = 6942)
