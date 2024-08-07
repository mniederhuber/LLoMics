# sragent :female_detective:	
`sragent` is a set of python functions to access and process metadata from the Sequence Reads Archive (SRA) records. 
It was made in an attempt to help automate the handling of large numbers of records with frequently ambiguous metadata, and provide a structured output with standardized sample identification and classification. 
To do this, `sragent` relies on prompts to an LLM (currently any OpenAI model via their API) to interpret metadata and determine if/what perturbations (mutations, depletions, etc.) or controls are present in an experiment.  

The goal of `sragent` is to maximize accuracy while minimizing user effort without fine-tuning the LLM. 
Currently, all that is needed is an OpenAI API account, and an NCBI API key.

## Status :construction:
- `sragent` is actively under development. Expect bugs! :bug: :bug: :bug:
- Prompts and output are currently designed specifically for ChIP-seq experiments. ie. we expect certain controls in each project. But plan to test and optimize for all types of records in near term. 
- Development and testing has been done with records of yeast histone PTM ChIP-seq, near term goal is to check prompt language, response accuracy, for other organisms. 
- Issues and contributions are welcome!

# Installation

Clone the repository. 
```
git clone git@github.com:mniederhuber/sragent.git
```
Then install with pip. 
```
cd sragent 
pip install .
```

# Setup
`sragent` currenlty relies on the OpenAI API to access their LLMs, and an NCBI API key to access SRA metadata.
You'll need an account and API key for both services to use `sragent`. 
`sragent` looks for the following global variables:
- `OPENAI_API_KEY`
- `ENTREZ_API_KEY`
- `ENTREZ_EMAIL`

You can add these to a configuration file like `.bash_profile`:
```
export OPEN_API_KEY='My_OpenAI_Key'
export ENTREZ_API_KEY='My_Entrez_Key'
export ENTREZ_EMAIL='My_NCBI_Acct_Email'
```

# Running `sragent`
`sragent` is built around a two step process.
1. fetch record metadata 
2. summarize and annotate metadata (with LLM)

These two steps are combined in the single function `annotate()`
which takes either a single bioproject ID, a list of bioproject IDs, or a previously generated metadata table (as pandas dataframe).

`annotate()` takes the following required arguments:
- `input`: bioproject id(s) or pandas dataframe
- `model`: one of the OpenAI models, eg. 'gpt-4o', 'gpt-3.5-turbo-0125'

Additional default arguments:
- `validate`=`TRUE`, `bool` of wheter or not to check if there are obvious disagreements in sample classification within a project
- `tag`=`TRUE`, `bool` default if to generate a sample 'tag' or 'id' in the format of {chip_target}_{perturbation}_{perturbation_type}_{timepoint} *with some variation for WT and non-timecourse exps*
- `sample`=`None`, `int` of sub-samples to process within a project. This is useful for testing purposes mainly.
- `summary_reps`=1, `int` of number of times to summarise a project before classification step. This is depricated. Needs to be removed.
- `outFile`, `str` optional filename for output of csv of annotated metadata

```python
import sragent
sragent.annotate('PRJNA721183', # this is a small project with 6 samples, good for testing
                 'gpt-4o', 
                  outFile = 'test.csv') 
```

The current output is a pandas dataframe. 
