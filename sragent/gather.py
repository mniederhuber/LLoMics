import os
import json
import random
from pathlib import Path
import pandas as pd
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import Literal, List, Optional
import sragent.fetch as fetch

class experiment_model(BaseModel):
    """Fill in the metatdata for a ChIP-seq experiment, let's think this through step by step."""
    experiment_id: str = Field(description = "The experiment ID")
    exp_title: str = Field(description = "The experiment title") 
    gene_mutation: bool = Field(description = "Based on experiment **title** and the **look up table** is this experiment testing the effect of a gene mutation? Let's think this through step by step.")
    gene_deletion: bool = Field(description = "Based on experiment **title** and the **look up table** is this experiment testing the effect of the complete removal/deletion of a gene? Let's think this through step by step.")
    protein_depletion: bool = Field(description = "If this experiment uses a protein depletion system, is depletion being induced or is this a control treatment? Let's think this through step by step.")
    stress_condition: bool = Field(description = "Based on experiment **title** and the **look up table** is this experiment testing the effect of a stress condition? Let's think this through step by step.")
    time_series: bool = Field(description = "Based on experiment **title**, **attributes**, and the **look up table** is this experiment part of a time series or from a specific growth phase? Let's think this through step by step.")
    chip_input: bool = Field(description = "Is this experiment an input control? This is normally indicated by 'input' or similar in **title**. Let's think this through step by step.")
    antibody_control: bool = Field(description = "Is this experiment an antibody control? (e.g. IgG control or another non-specific antibody) Let's think this through step by step.")
    chip_target: str = Field('',description = "What protein is being profiled by ChIP-seq in this experiment? Be careful, in some cases the actual target protein might be profiled indirectly via a synthetic peptide tag fusion, in those cases report the protein target and not the peptide tag. Use Brno notation for histone modifications and UCSC Gene Symbols for non-histone targets. Answer should be a single word, e.g. 'H3K27ac' or 'H3K4me3' or 'Set1'. Let's think this through step by step.") 
    #perturbation_type: Literal["gene_mutation", "gene_deletion", "protein_depletion", "stress_condition","None]
    #perturbation: str = Field('',description = "If the experiment is a perturbation condition, what is the perturbation? Use only 1-2 words in snake case.")
    mutation: str = Field('',description = "If the experiment is testing a gene mutation what is the name of the gene and mutation? Field should be a single token without spaces and follow standard format of: 'GeneName-Mutation' (e.g. PolII-A54R, H3-K4R, Set2-Δ2-30). Let's think this through step by step.")
    deletion: str = Field('',description = "If the experiment is testing a gene deletion what is the name of the gene being deleted? Field should follow standard format of: 'ΔGeneName'. Let's think this through step by step.")
    depletion: str = Field('',description = "If this experiment uses a protein depletion system, and depletion being induced in this experiment, what is the name of the depleted protein? Let's think this through step by step.")
    stress: str = Field('',description = "If the experiment is testing a chemical or environmental stress what is the stress? Let's think this through step by step.")
    time_point: str = Field('',description = "Based on experiment **title**, **attributes**, and the **look up table** if this experiment is part of a time series or from a specific growth phase, what is the name of that time point? Let's think this through step by step.") 


class project_model(BaseModel):
    """project level json class for experiments"""
    project_id: str 
    project_title: str
    experimentMeta: List[experiment_model]
    
tools = [
    {
        "name": "json_output",
        "description": "Extract metadata from summary for json output.",
        "parameters": experiment_model.model_json_schema()
    }
]

# function to check for necessary environment variables
def check_env():

    if os.environ.get('OPENAI_API_KEY') is None:
        raise ValueError("OPENAI_API_KEY environment variable must be set")
    else:
        global client
        client = OpenAI(api_key = os.environ.get('OPENAI_API_KEY')) 

# utility functions to convert project and experiment metadat to a string object for prompting
def project_text(prjMeta):
    project_title = prjMeta['project_title'].iloc[0]
    project_id = prjMeta['project_id'].iloc[0]
    project_abstract = prjMeta['abstract'].iloc[0]
    project_protocol = prjMeta['protocol'].iloc[0]

    text = f"Project ID: {project_id}\nProject Title: '{project_title}'\nProject Abstract:\n{project_abstract}\nProject Protocol:\n{project_protocol}\n"

    return text

def exp_text(expMeta):
    experiments = []
    for index, row in expMeta.iterrows():
        experiment_id = row['experiment_id']
        experiment_title = row['title']
        attributes = row['attributes']
        text = f"Experiment ID: {experiment_id}\nExperiment Title: '{experiment_title}'\nAttributes: '{attributes}'\n"
        experiments.append(text)

    return '\n'.join(experiments)

def summarize(model, 
              prjMeta, 
              expMeta):

    print(f'Summarizing project {prjMeta["project_id"].iloc[0]}...')

    system_prompt = "You are an assistant with domain expertise in yeast genetics and molecular biology, you are skilled in analyzing and summarizing metadata from high-throughput sequencing experiments."
    summary_prompt = """Analyze the metadata for this ChIP-seq project and the experiments in the project.
Briefly summarize the main goal of the project. What is the project testing? What are the different experimental conditions?
Using the project **abstract**, project **protocol**, and the experiment **titles** and **attributes** answer the following questions. Let's think these through step by step.
- What key words indicate if there are experiments with gene mutations in the project? Epitope tags should not be considered mutations. Some projects use cell lines or strains with common baseline genetic mutations or deletions that should be ignored, only mutations or deletions that are relevant to the project goal should be listed. 
- What key words indicate if there are experiments with gene deletions in the project? A gene deletion must involve the complete removal of the gene. Ignore cases where only specific regions or domains are deleted. Some projects use cell lines or strains with common baseline genetic mutations or deletions that should be ignored, only mutations or deletions that are relevant to the project goal should be listed. 
- What key words indicate if there are experiments with protein depletions in the project? How is the depletion controlled or induced?
- What key words indicate different chemical treatments or stress conditions in the project and what do they signify?
- What key words indicate if the project involves experiments separated over time or from specific stages of development/growth? Experimental replicates are not the same as time points.
- What key words indicate if an experiment a ChIP Input control? 
- What key words indicate if an experiment a non-specific antibody control? 
- What key words indicate the ChIP-seq protein targets in the project? 
    In some experiments the protein target be tagged with a synthetic peptide (FLAG, HA, V5, etc.). 
    It is important that we can correctly identify the protein target of experimental interest and not just the tag. Use Brno notation for histone modifications and UCSC Gene Symbols for non-histone targets.
    If an experiment is identified as 'Input' **protein target must be 'None'**.
- What key words indicate experimental replicates if there are any?
- What key words indicate any small molecules being used in the project to induce stress or protein depletion in specific experiments?
Your responses should be designed to be used by an LLM assistant tasked with classifying and generated structured metadata for each experiment in the project.
"""
    project = project_text(prjMeta)
    experiment = exp_text(expMeta)

    prompt = f"Here is study-level metadata for a series of ChIP-seq experiments in yeast:\n{project}\nHere is the NCBI metadata for all of the experiments included in this project:\n{experiment}\n{summary_prompt}"

    response = client.chat.completions.create(
        model = model,
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1)

    return response

def jsonOut(model,
            responses_text, 
            expMeta,
            summary_reps):

    system_prompt = "You are an assistant with domain expertise in yeast genetics and molecular biology, you are skilled in analyzing and summarizing metadata from high-throughput sequencing experiments."
    exptext = exp_text(expMeta)
    if summary_reps == 1:
        prompt = f"Here is a summary of a ChIP-seq project that was made using the whole project metadata:\n\n{responses_text}\n\nExtract details about the following experiment and use the **json_output** function to generate a structured output. Let's think this through step by step:\n\n{exptext}\n\n " # 24.03.31 changed method A3
    elif summary_reps > 1:
        prompt = f"Here are {summary_reps} summaries generated by an llm of the same ChIP-seq project in yeast using the whole project metadata:\n\n{responses_text}\n\nExamine these summaries for consensus and extract details about the following experiment and use the **json_output** function to generate a structured output. Let's think this through step by step:\n\n{exptext}\n\n "

    response = client.chat.completions.create(
        model = model,
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        functions = tools,
        temperature=0.1,
        function_call = {"name": "json_output"})

    return response

#### control functions

# function the loop experiments for testing

def sampleExps(model, 
               expMeta,
               project_summary,
               summary_reps,
               sample = None):

    exp_list = list(expMeta['experiment_id'].unique())

    if sample is not None and sample < len(expMeta):
        exp_list = random.sample(exp_list, sample)
    # get all of the unique experiments in the project

    expMeta_list = []
    for exp in exp_list:
        # get the experiment metadata from the full dataframe of experiments 
        exp_details = expMeta[expMeta['experiment_id'] == exp][['experiment_id', 'title', 'attributes']]
        print(f'annotating experiment {exp_details["experiment_id"]}...')

        json_response = jsonOut(model, 
                                project_summary, 
                                summary_reps = summary_reps,
                                expMeta = exp_details)
        
        json_out = experiment_model.model_validate_json(json_response.choices[0].message.function_call.arguments) 
        expMeta_list.append(json_out)

    return expMeta_list 

def bool_check(df):
    """
    Check for inconsistencies between boolean and character variables
    """
    var_dict = {'mutation':'gene_mutation',
                'deletion':'gene_deletion',
                'depletion':'protein_depletion',
                'stress':'stress_condition',
                'time_point':'time_series'}

    # loop through the rows and check for inconsistencies
    checks = []
    # for each row in the df, check if any of the bool and char variables disagree
    for i in range(len(df)):
        warn = False 
        warnings = []
        for var in var_dict:
            test = True
            if df.loc[i, var_dict[var]] == False and df.loc[i, var] == '':
                test = False 
            elif df.loc[i, var_dict[var]] == True and df.loc[i, var] != '':
                test = False
            warnings.append(test)
            print(warnings) 
        if any(warnings): # if any of the checks fail, set warn to True, all(warnings) is False if any of the checks fail
            warn = True
        if df.loc[i, 'gene_mutation'] and df.loc[i, 'gene_deletion']: # if both gene mutation and gene deletion are true, set warn to True
            print(f'Warning: experiment {df.loc[i, "experiment_id"]} has both gene mutation and gene deletion set to True')
            warn = True
        print(warn)
        checks.append(warn)
    df['warning'] = checks

    return df

def tagExps(annotated_exps):
    print('tagging...')

    for row in range(len(annotated_exps)):
        timepoint = str(annotated_exps.loc[row,'time_point']).replace(' ','_')

        if annotated_exps.loc[row,'chip_input'] == True:
            target = 'Input'
        else:
            target = annotated_exps.loc[row,'chip_target']
        
        if any(annotated_exps.loc[row,'gene_mutation':'stress_condition']):
            if annotated_exps.loc[row,'gene_mutation']:
                pertype = 'gene_mutation'
                per = annotated_exps.loc[row,'mutation']
            elif annotated_exps.loc[row,'gene_deletion']:
                pertype = 'gene_deletion'
                per = annotated_exps.loc[row,'deletion']
            elif annotated_exps.loc[row,'protein_depletion']:
                pertype = 'protein_depletion'
                per = annotated_exps.loc[row,'depletion']
            elif annotated_exps.loc[row,'stress_condition']:
                pertype = 'stress_condition'
                per = annotated_exps.loc[row,'stress'] 

            if annotated_exps.loc[row,'time_series']:
                annotated_exps.loc[row,'sample'] = f'{target}-{per}-{pertype}-{timepoint}'
            else:
                annotated_exps.loc[row,'sample'] = f'{target}-{per}-{pertype}'

            annotated_exps.loc[row,'perturbation'] = f'{pertype}'

        else:
            if annotated_exps.loc[row,'time_series']:
                annotated_exps.loc[row,'sample'] = f'{target}-WT-{timepoint}'
            else:
                annotated_exps.loc[row,'sample'] = f'{target}-WT'

            annotated_exps.loc[row,'perturbation'] = 'none'

    return annotated_exps

def setControl(annotated_proj):
    # designed for grouped apply to projects within annotated table
    # first find out what the controls are in the project if any
    # then iterate the rows and match control to experiment

    print('setting controls...')

    controls = pd.DataFrame()
    exps = pd.DataFrame()
    if not any(annotated_proj['chip_input']): # if there are no samples labelled as inputs
        if any(annotated_proj['antibody_control']): # check if any are labelled as antibody controls
            controls = annotated_proj[annotated_proj['antibody_control'] == True] # and if so then make a list of controls
            exps = annotated_proj[annotated_proj['antibody_control'] == False] # and a list of experiments
    else:
        controls = annotated_proj[annotated_proj['chip_input'] == True]
        exps = annotated_proj[annotated_proj['chip_input'] == False] # and a list of experiments

    for index, row in exps.iterrows():
        if 'WT' in row['sample']:
            if row['time_series']:
                ctrl = controls.loc[(controls['gene_mutation'] == False) & (controls['gene_deletion'] == False) & (controls['protein_depletion'] == False) & (controls['stress_condition'] == False) & (controls['time_point'] == row['time_point']), 'sample']
            else:
                ctrl = controls.loc[(controls['gene_mutation'] == False) & (controls['gene_deletion'] == False) & (controls['protein_depletion'] == False) & (controls['stress_condition'] == False), 'sample']
        else:
            if row['gene_mutation']:
                pertype = 'mutation'
            elif row['gene_deletion']:
                pertype = 'deletion'
            elif row['protein_depletion']:
                pertype = 'depletion'
            elif row['stress_condition']:
                pertype = 'stress'

            if row['time_series']:
                ctrl = controls[(controls[pertype].str.lower() == row[pertype].lower()) & (controls['time_point'] == row['time_point'])]['sample']
            else:
                ctrl = controls[(controls[pertype].str.lower() == row[pertype].lower())]['sample']
        
        if not ctrl.empty:
            exps.loc[index, 'control'] = ctrl.iloc[0]
        else:
            exps.loc[index, 'control'] = 'None'

    annotated_proj = pd.concat([exps, controls])
    return annotated_proj

# default settings to 1 rep 1 sample for testing
def gather(input,
         model_summary = None,
         model_annotation = None,
         annotate = False,
         validate = True, 
         tag = True,
         sample = None,
         summary_reps = 1,
         use_corrected = False,
         save_output = True):

    if save_output:
        if not os.path.exists('sragent_output'):
            os.mkdir('sragent_output')

    check_env()

    if type(input) == list:
        meta = pd.concat([fetch.fetch(prj) for prj in input]).drop_duplicates(subset='experiment_id', keep = 'first')    
    elif type(input) == str:
        meta = pd.DataFrame(fetch.fetch(input).drop_duplicates(subset='experiment_id', keep = 'first'))
    elif type(input) == pd.DataFrame:
        meta = input
    elif type(input) not in ['str','list','pd.DataFrame']:
        raise ValueError("Input must be a project_id, list of project_ids, or a pandas dataframe of processed metadata")

    if type(annotate) != bool:
        raise ValueError("Annotate must be set to True or False")
    elif not annotate:
        outdf = meta
    elif annotate:
        if Path('sragent_output/annotation_FULL.csv').exists():
            outdf = pd.read_csv('sragent_output/annotation_FULL.csv', keep_default_na=False)
            print('Annotation exists, loading annotation...')
        else:
            if model_summary is None or model_annotation is None:
                raise ValueError("Model names must be provided for annotation")

        # parse meta table, isolate individual projects and their experiments
            unique_projects = meta['project_id'].unique() 

            expdf_list = []
            for project_id in unique_projects:
                prjMeta = meta[meta['project_id'] == project_id][['project_id','project_title','abstract','protocol']].drop_duplicates(subset='project_id', keep = 'first')
                expMeta = meta[meta['project_id'] == project_id][['project_id','experiment_id', 'title', 'attributes']]

                project_title = prjMeta['project_title'].iloc[0]
                #project_id = prjMeta['project_id'].iloc[0]

                if use_corrected:
                    if Path(f'sragent_output/{project_id}_summary-corrected.txt').exists():
                        with open(f'sragent_output/{project_id}_summary.txt', 'r') as f:
                            print(f'Corrected summary exists, loading {project_id} summary...')
                            project_summary = f.read()
                    else:
                        print(f'Corrected summary does not exist, summarizing {project_id}...')
                else: 
                    if Path(f'sragent_output/{project_id}_summary.txt').exists():
                        with open(f'sragent_output/{project_id}_summary.txt', 'r') as f:
                            print(f'Summary exists, loading {project_id} summary...')
                            project_summary = f.read()
                    else:
                        print(f'Summary does not exist, summarizing {project_id}...')
                        summary = summarize(model_summary,
                                            prjMeta,
                                            expMeta)
                        project_summary = summary.choices[0].message.content
          #      summaries.append(project_summary)

                expMeta_list = sampleExps(model_annotation,
                                          expMeta,
                                          project_summary,
                                          summary_reps,
                                          sample)

         ### handling response output ### 
         # use the project_model class to format the experiment jsons under the parent project
                output = project_model(project_id = project_id, 
                                       project_title = project_title, 
                                       experimentMeta = expMeta_list)        

                # validate and store the json output 
                json_args = json.loads(output.model_dump_json())

                # convert json output to dataframe
                expdf = pd.json_normalize(json_args['experimentMeta'])
                expdf['project_id'] = project_id
                expdf['model_summary'] = model_summary
                expdf['model_annotation'] = model_annotation
                #expdf['summary'] = '\n'.join(summaries)
                expdf_list.append(expdf)

                # save project summary for each project
                if save_output:
                    with open(f'sragent_output/{project_id}_summary.txt', 'w') as f:
                        f.write(project_summary)

                print(f'project {project_id} done!')

            outdf = pd.concat(expdf_list, ignore_index=True)

        if validate:
            outdf = bool_check(outdf)

        if tag:
           outdf = tagExps(outdf) 
           outdf = outdf.groupby('project_id').apply(setControl)

    ### outputs
    if save_output:
        meta.to_csv(f'sragent_output/metadata.csv', index = False, sep = ',') 
        if annotate:    
            outdf.to_csv(f'sragent_output/annotation_FULL.csv', index = False, sep = ',')
            if tag:
                outdf[['project_id','experiment_id','exp_title','perturbation','sample','control','warning']].to_csv('sragent_output/annotation.csv', index = False, sep = ',')

    return outdf


