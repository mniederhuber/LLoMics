import llomics
import json
import pandas as pd


model = 'gpt-4o-mini'

if __name__ == '__main__':
    llomics.annotate('PRJNA262623', model)
