import os
import json
import random
import pandas as pd
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import Literal, List, Optional

client = OpenAI(api_key = os.environ.get('OPENAI_API_KEY'))

system_prompt = "You are an assistant with domain expertise in yeast genetics and molecular biology, you are skilled in analyzing and summarizing metadata from high-throughput sequencing experiments."

prompts = {'summary':"""Analyze the metadata for this ChIP-seq project and the experiments in the project.
Briefly summarize the main goal of the project. What is the project testing? What are the different experimental conditions?
Using the project **abstract**, project **protocol**, and the experiment **titles** and **attributes** answer the following questions. Let's think these through step by step.
- What key words indicate if an experiment is a 'Perturbed' condition in this project? 'Perturbed' should exclusively indicate experiments that test the effect of a gene mutation, gene deletion, protein depletion, or stress conditions. Careful, some projects may not have any perturbed conditions, and many cell lines and strains have baseline mutations that should not be considered 'Perturbed'.
- What key words indicate if the project involves experiments separated over time or from specific stages of development/growth? Experimental replicates are not the same as time points.
- What key words indicate if an experiment a ChIP Input control? 
- What key words indicate if an experiment a non-specific antibody control? 
- What key words indicate the ChIP-seq protein targets in the project? 
    In some experiments the protein target be tagged with a synthetic peptide (FLAG, HA, V5, etc.). 
    It is important that we can correctly identify the protein target of experimental interest and not just the tag. Use Brno notation for histone modifications and UCSC Gene Symbols for non-histone targets.
    If an experiment is identified as 'Input' **protein target must be 'None'**.
- What key words indicate experimental replicates if there are any?
- What key words indicate any small molecules being used in the project to induce stress or protein depletion in specific experiments?
- What is a simple naming pattern that could be used to name the experiments in this project? Names should be short (<10 characters), uniquely identify conditions, and follow the structure [chip_target]_[genotype] with no spaces. For example: 'H3K27ac_WT', 'PolII_Swi6del', 'H3K4me3_30m', 'Input_Spt6mut'.
Your responses should be designed to be used by an LLM assistant tasked with classifying and generated structured metadata for each experiment in the project.
"""
}

class experiment_model(BaseModel):
    """Fill in the metatdata for a ChIP-seq experiment, let's think this through step by step."""
    experiment_id: str = Field(description = "The experiment ID")
    expTitle: str = Field(description = "The experiment title") 
    perturbed: bool = Field(description = "Based on experiment **title**, **attributes**, and the **look up table** is this exerpiment 'Perturbed' (i.e. it tests the effect of a gene mutation, deletion, depletion, or stress condition)? If 'WT' is in the experiment title the experiment must not be 'Perturbed'. Let's think this through step by step.")
    time_series: bool = Field(description = "Based on experiment **title**, **attributes**, and the **look up table** is this experiment part of a time series or from a specific growth phase? Let's think this through step by step.")
    chip_input: bool = Field(description = "Is this experiment an input control? Let's think this through step by step.")
    antibody_control: bool = Field(description = "Is this experiment an antibody control? (e.g. IgG control or another non-specific antibody)")
    chip_target: Optional[str] = Field(None,description = "What protein is being profiled by ChIP-seq in this experiment? Be careful, in some cases the actual target protein might be profiled indirectly via a synthetic peptide tag fusion. Answer should be a single word, e.g. 'H3K27ac' or 'H3K4me3' or 'Set1'. Let's think this through step by step.") # method_A
    perturbation_type: Literal["gene_mutation", "gene_deletion", "protein_depletion", "stress_condition",None]
    replicate: Optional[int] = Field(None,description = "If the experiment is a replicate of another experiment, provide the replicate number.")
    sample_name: str = Field(description = "Short name that uniquely identifies the experiment. Let's think this through step by step")
#    time_point: Optional[str] = Field(None,description = "The most likely time point of an experiment in a time series. e.g. '30m' or 'G1' phase") 


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
    summary_prompt = prompts['summary'] 
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

def validator(response):
    json_response = json.loads(response)
    validated = True
    if not json_response['perturbed']:
        if json_response['perturbation'] is not None or json_response['perturbation_type'] is not None:
            validated = False
    if not json_response['time_series'] and json_response['time_point'] is not None:
        validated = False
    if json_response['chip_input'] and json_response['chip_target'] is not None:
        validated = False

    return validated

def jsonOut(model,
            responses_text, 
            expMeta,
            summary_reps):

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

    project_summary = '\n'.join(project_summary)

    expMeta_list = []
    for exp in exp_list:
        # get the experiment metadata from the full dataframe of experiments 
        exp_details = expMeta[expMeta['experiment_id'] == exp][['experiment_id', 'title', 'attributes']]
        print(f'annotating experiment {exp_details["experiment_id"]}')

        json_response = jsonOut(model, 
                                project_summary, 
                                summary_reps = summary_reps,
                                expMeta = exp_details)
        
        json_out = experiment_model.model_validate_json(json_response.choices[0].message.function_call.arguments) 
        expMeta_list.append(json_out)

    return expMeta_list 


# default settings to 1 rep 1 sample for testing
def main(model,
         prjMeta,
         expMeta,
         sample = None,
         summary_reps = 1,
         outFile = None):

    project_title = prjMeta['project_title'].iloc[0]
    project_id = prjMeta['project_id'].iloc[0]
    
    expdf_list = []
    summaries = []
    if summary_reps == 1:
        summary = summarize(model,
                            prjMeta,
                            expMeta)
        project_summary = summary.choices[0].message.content
        summaries.append(project_summary)
        
    else:
        for n in range(summary_reps):
            summary = summarize(model,
                                prjMeta,
                                expMeta)

            project_summary = summary.choices[0].message.content
            summaries.append(f"Summary {n}:\n{project_summary}\n\n")

    expMeta_list = sampleExps(model,
                              expMeta,
                              summaries,
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
    expdf['model'] = model
    #expdf['summary'] = '\n'.join(summaries)
    expdf_list.append(expdf)

    outdf = pd.concat(expdf_list)

    if outFile is not None:
        outdf.to_csv(outFile, index = False, sep = '\t')

    return outdf


if __name__ == "__main__":
    # test the functions
    #model = "gpt-3.5-turbo-0125"
    model = "gpt-4-0125-preview"
    projectdf = pd.read_csv('db_sheets/project_metaData-AllHistone.tsv', sep = '\t')
    experimentdf = pd.read_csv('db_sheets/experiment_metaData-AllHistone.tsv', sep = '\t')

    for n in range(3):

        project_id = random.choice(projectdf['project_id'])
        prjMeta = projectdf[projectdf['project_id'] == project_id]
        expMeta = experimentdf[experimentdf['project_id'] == project_id]

        out = main(model, 
                   prjMeta, 
                   expMeta,
                   sample = 10, 
                   summary_reps=1,
                   outFile = f'data/240502_{model}_{n+1}.csv')

        print(out)