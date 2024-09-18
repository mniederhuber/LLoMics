import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import os
from dash.dash_table import DataTable
from gather import gather, summarize

# Initialize the Dash app
app = dash.Dash(__name__)

# Directory where the app outputs files
OUTPUT_DIR = "./sragent_output"

# Ensure the output directory exists
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Function to list files in the output directory
def list_files():
    return os.listdir(OUTPUT_DIR)

# Layout of the Dash app
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),  # Track URL changes

    # Sidebar
    html.Div([
        html.H3("Output Files"),
        html.Div(id='file-list'),  # This will display the list of files as links
        html.Button("Reload File List", id='reload-button', style={'margin-top': '20px'}),

        html.Hr(),

        # Form to select specific project or all projects for metadata gathering
        html.H3("Fetch Metadata"),
        dcc.Dropdown(
            id='summary-type',
            options=[
                {'label': 'Summarize Specific Project', 'value': 'specific'},
                {'label': 'Summarize All Projects', 'value': 'all'}
            ],
            value='specific',  # Default selection
            style={'margin-bottom': '10px'}
        ),
        dcc.Input(id='project-id', type='text', placeholder="Enter Project ID (for specific project)", style={'margin-bottom': '10px'}),
        html.Button("Fetch and Summarize Metadata", id='fetch-button'),
        html.Div(id='metadata-output')
    ], style={'width': '20%', 'float': 'left', 'padding': '20px', 'border-right': '1px solid lightgrey'}),

    # Main content area for viewing and editing files
    html.Div([
        html.H3("File Content"),
        html.Div(id='file-content', style={'whiteSpace': 'pre-wrap'}),
        html.Div(id='file-editor')
    ], style={'width': '75%', 'float': 'right', 'padding': '20px'})
])

# Callback to reload the list of files and display them as clickable links
@app.callback(
    Output('file-list', 'children'),
    [Input('reload-button', 'n_clicks')]
)
def reload_file_list(n_clicks):
    files = list_files()
    return [
        html.A(file, href=f"/view/{file}", style={'display': 'block', 'margin-bottom': '10px'}) for file in files
    ]

# Callback to display the selected file content and provide editing options
@app.callback(
    [Output('file-content', 'children'),
     Output('file-editor', 'children')],
    [Input('url', 'pathname')]
)
def display_file(pathname):
    if not pathname or not pathname.startswith("/view/"):
        return "Select a file to view its contents.", ""

    # Extract the file name from the URL
    file_name = pathname.split("/view/")[1]
    file_path = os.path.join(OUTPUT_DIR, file_name)

    # Handle CSV and Excel files by displaying them as interactive DataTables
    if file_name.endswith('.csv'):
        df = pd.read_csv(file_path)

        # Create a DataTable for the CSV file with scrollable content
        table = DataTable(
            id='dataframe-table',
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict('records'),
            editable=True,
            style_table={'height': '300px', 'overflowY': 'auto'},  # Set table height with vertical scroll
            style_cell={'textAlign': 'left', 'minWidth': '150px', 'width': '150px', 'maxWidth': '150px'},  # Adjust cell width
        )
        return f"### {file_name} - DataFrame", table

    # Handle text files
    elif file_name.endswith('.txt'):
        with open(file_path, 'r') as file:
            content = file.read()
        editor = dcc.Textarea(
            id='text-editor',
            value=content,
            style={'width': '100%', 'height': '400px'}
        )
        return f"### {file_name}\n\n{content}", editor

    return "Unsupported file type.", ""

# Callback to fetch metadata based on project ID or summarize all projects
@app.callback(
    Output('metadata-output', 'children'),
    [Input('fetch-button', 'n_clicks')],
    [State('summary-type', 'value'), State('project-id', 'value')]
)
def fetch_metadata(n_clicks, summary_type, project_id):
    if summary_type == 'specific':
        if not project_id:
            return "Please enter a valid project ID."
        # Gather metadata and summarize it for a specific project
        try:
            metadata = gather(project_id)
            summary = summarize(metadata)
            return html.Pre(f"Summary of project {project_id}:\n{summary}")
        except Exception as e:
            return f"Error fetching metadata: {str(e)}"
    elif summary_type == 'all':
        # Logic to gather and summarize metadata for all projects
        try:
            all_summaries = ""
            for project_id in list_files():  # Assuming list_files() returns project IDs or files related to projects
                metadata = gather(project_id)
                summary = summarize(metadata)
                all_summaries += f"Summary of project {project_id}:\n{summary}\n\n"
            return html.Pre(all_summaries)
        except Exception as e:
            return f"Error fetching metadata: {str(e)}"

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
