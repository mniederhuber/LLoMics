### gpt 4.0 draft 9/17/24

from nicegui import ui
import pandas as pd
from pathlib import Path
import sragent.gather as gather
import sragent.fetch as fetch
import sragent.validate as validate

# Set up an initial empty DataFrame for storing metadata
metadata_df = pd.DataFrame()

# Function to fetch metadata based on the input project ID
def fetch_metadata(project_id):
    global metadata_df
    # Use the gather function to fetch the metadata
    metadata_df = fetch.fetch(project_id)
    if not metadata_df.empty:
        # Once metadata is fetched, display it in the GUI
        display_metadata()

def display_metadata():
    # Clear previous output before displaying new results
    ui.clear()
    
    # Display project summary
    ui.label("Project Summary").classes('text-xl')
    project_summary = metadata_df[['project_id', 'project_title', 'abstract', 'protocol']].drop_duplicates()
    
    for index, row in project_summary.iterrows():
        ui.label(f"Project ID: {row['project_id']}")
        ui.label(f"Project Title: {row['project_title']}")
        ui.label(f"Abstract: {row['abstract']}")
        ui.label(f"Protocol: {row['protocol']}")
    
    # Display experiment data
    ui.label("Experiments").classes('text-xl')
    experiment_data = metadata_df[['experiment_id', 'title', 'attributes']]
    
    for index, row in experiment_data.iterrows():
        ui.label(f"Experiment ID: {row['experiment_id']}")
        ui.label(f"Title: {row['title']}")
        ui.label(f"Attributes: {row['attributes']}")

    # Create buttons for user validation and corrections
    ui.button('Validate', on_click=validate_metadata)
    ui.button('Save', on_click=save_metadata)

# Function for human-in-the-loop validation and correction
def validate_metadata():
    global metadata_df
    metadata_df = validate.bool_check(metadata_df)
    
    # Display any warnings or issues detected
    if 'warning' in metadata_df.columns and metadata_df['warning'].any():
        ui.label("Validation Warnings Detected").classes('text-red-500')
        warnings = metadata_df[metadata_df['warning'] == True]
        
        for index, row in warnings.iterrows():
            ui.label(f"Warning for Experiment ID: {row['experiment_id']}").classes('text-red-500')
    
# Function to allow users to save the corrected data
def save_metadata():
    global metadata_df
    # Save the metadata dataframe to a CSV file
    metadata_df.to_csv('corrected_metadata.csv', index=False)
    ui.notify('Metadata saved successfully!', close_after=3)

# Main user interface for inputting project IDs
with ui.column():
    ui.label("SRA Metadata Fetcher").classes('text-2xl font-bold')
    project_id_input = ui.input(label="Enter Project ID").classes('w-full')
    
    # Button to fetch metadata based on the input project ID
    ui.button('Fetch Metadata', on_click=lambda: fetch_metadata(project_id_input.value))
    
# Start the NiceGUI application
ui.run()
