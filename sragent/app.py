import streamlit as st
import os
from gather import gather, summarize
from fetch import fetch
from validate import bool_check

# Directory where the app outputs files
OUTPUT_DIR = "./sragent_output"

# Ensure the output directory exists
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Set the page title
st.set_page_config(page_title="Project Metadata Annotator")

# Title of the app
st.title("Project Metadata Annotator")

# Sidebar for file listing
st.sidebar.title("Available Output Files")

# List available files in the output directory
files = os.listdir(OUTPUT_DIR)

# Display the list of files in the sidebar
selected_file = st.sidebar.selectbox("Select a file to view", files)

# If a file is selected, display its contents
if selected_file:
    st.sidebar.subheader(f"Viewing File: {selected_file}")
    
    file_path = os.path.join(OUTPUT_DIR, selected_file)
    
    # Determine how to display the file based on its extension
    if selected_file.endswith(".json"):
        with open(file_path, "r") as f:
            file_contents = f.read()
            st.sidebar.json(file_contents)  # Display as JSON
    elif selected_file.endswith(".txt"):
        with open(file_path, "r") as f:
            file_contents = f.read()
            st.sidebar.text(file_contents)  # Display as plain text
    else:
        st.sidebar.warning(f"Unsupported file format: {selected_file}")
else:
    st.sidebar.write("No file selected.")

# Input form for project ID
project_id = st.text_input("Enter Project ID:")

if st.button("Fetch and Summarize Metadata"):
    if project_id:
        # Fetch metadata
        with st.spinner('Fetching metadata...'):
            metadata = gather(project_id)
        
        # Display raw metadata
        st.subheader("Raw Metadata")
        st.dataframe(metadata)
        
        # Gather and summarize metadata
        #with st.spinner('Summarizing metadata...'):
        #    exp_data = gather(project_id)
        #    summary = summarize(exp_data)

        ## Display summary for human-in-the-loop validation
        #st.subheader("Generated Project Summary")
        #edited_summary = st.text_area("Review and edit the project summary below:", value=summary, height=300)
        
        ## Validation button
        #if st.button("Validate Summary"):
        #    # Validate the edited summary
        #    with st.spinner('Validating summary...'):
        #        validation_report = bool_check(edited_summary)

        #    st.subheader("Validation Report")
        #    st.json(validation_report)

        # Save summary to a new output file
#        if st.button("Save Summary"):
#            file_name = f"summary_{project_id}.txt"
#            file_path = os.path.join(OUTPUT_DIR, file_name)
#            
#            with open(file_path, "w") as f:
#                f.write(edited_summary)
#            
#            st.success(f"Summary saved to {file_name}")
    else:
        st.error("Please enter a valid Project ID.")
