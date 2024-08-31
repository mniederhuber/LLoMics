import  sqlite3
from pathlib import Path

def insert_project_data(conn, project_data):
    """
    Insert project data into the projects table.
    """
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO projects (project_id, project_title, abstract, protocol)
        VALUES (?, ?, ?, ?)
    ''', (project_data['project_id'], project_data['project_title'], project_data['abstract'], project_data['protocol']))
    conn.commit()

def insert_experiment_data(conn, experiment_data):
    """
    Insert experiment data into the experiments table.
    """
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO experiments (
            experiment_id, project_id, title, attributes, gene_mutation, gene_deletion, protein_depletion,
            stress_condition, time_series, chip_input, antibody_control, chip_target, mutation,
            deletion, depletion, stress, time_point, perturbation, sample, control, warning
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        experiment_data['experiment_id'], experiment_data['project_id'], experiment_data['title'],
        experiment_data['attributes'], experiment_data['gene_mutation'], experiment_data['gene_deletion'],
        experiment_data['protein_depletion'], experiment_data['stress_condition'], experiment_data['time_series'],
        experiment_data['chip_input'], experiment_data['antibody_control'], experiment_data['chip_target'],
        experiment_data['mutation'], experiment_data['deletion'], experiment_data['depletion'], experiment_data['stress'],
        experiment_data['time_point'], experiment_data['perturbation'], experiment_data['sample'],
        experiment_data['control'], experiment_data['warning']
    ))
    conn.commit()

def initialize_database(db_path='sragent_output/sragent.db'):
    """
    Initialize the SQLite database and create tables if they don't exist.
    """
    # Ensure the output directory exists
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create table for projects
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            project_id TEXT PRIMARY KEY,
            project_title TEXT,
            abstract TEXT,
            protocol TEXT,
            summary TEXT
        )
    ''')

    # Create table for experiments
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS experiments (
            experiment_id TEXT PRIMARY KEY,
            project_id TEXT,
            title TEXT,
            attributes TEXT,
            gene_mutation BOOLEAN,
            gene_deletion BOOLEAN,
            protein_depletion BOOLEAN,
            stress_condition BOOLEAN,
            time_series BOOLEAN,
            chip_input BOOLEAN,
            antibody_control BOOLEAN,
            chip_target TEXT,
            mutation TEXT,
            deletion TEXT,
            depletion TEXT,
            stress TEXT,
            time_point TEXT,
            perturbation TEXT,
            sample TEXT,
            control TEXT,
            warning BOOLEAN,
            FOREIGN KEY(project_id) REFERENCES projects(project_id)
        )
    ''')

    conn.commit()
    conn.close()