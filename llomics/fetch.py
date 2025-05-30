import csv
import pandas as pd
from Bio import Entrez
import os
import xml.etree.ElementTree as ET
########

########
    
def fetch(prjid):

    if os.environ.get('ENTREZ_EMAIL') is None:
        raise ValueError('Please set the environment variable ENTREZ_EMAIL to your email address.')
    elif os.environ.get('ENTREZ_API_KEY') is None:
        raise ValueError('Please set the environment variable ENTREZ_API_KEY to your NCBI API key.')
    else:
        Entrez.email = os.environ.get('ENTREZ_EMAIL')
        api = os.environ.get('ENTREZ_API_KEY')

    print(f'Fetching {prjid}...')
    # search by bioproject id and gather sra IDs
    search = Entrez.read(Entrez.esearch(db = 'sra', term = prjid, retmax = 5000, api_key = api))
    sra_handle = Entrez.efetch(db = 'sra', id = search['IdList'], rettype = 'full', retmode = 'xml', api_key = api) # changing retmode to xml because there is, it seems, more data in that file
    # fetch the runinfo for all the ids returned by the search

    tree = ET.parse(sra_handle)
    root = tree.getroot()

    outRows = []
    for element in root.findall('.//EXPERIMENT_PACKAGE'):

        assay_id = element.find('.//LIBRARY_STRATEGY').text
        if assay_id.lower() != 'chip-seq':
            continue

        header = ['project_id','project_title','abstract','protocol','run_id','experiment_id','title','organism','assay_id','attributes',]

        experiment_id = element.find('.//EXPERIMENT').attrib.get('accession', '')

        title = element.find('.//SAMPLE/TITLE')
        if title is not None:
            title = title.text
        else:
            title = 'NO_TITLE'

        project_id = element.find(".//STUDY/IDENTIFIERS/EXTERNAL_ID[@namespace='BioProject']").text
        project_title = element.find(".//STUDY/DESCRIPTOR/STUDY_TITLE").text 
        #not saving this but using to fill missing organism
        taxn = element.find(".//SAMPLE/SAMPLE_NAME/TAXON_ID")
        if taxn is not None:
            taxn = taxn.text

        organism = element.find(".//SAMPLE/SAMPLE_NAME/SCIENTIFIC_NAME")
        if organism is not None:
            organism = organism.text.replace(' ','_')
        elif taxn == '4932':
            organism = 'Saccharomyces cerevisiae'
        else:
            organism = 'NO_ORGANISM_DATA'

        run_id = element.find(".//RUN_SET/RUN")
        if run_id is not None:
            run_id = run_id.attrib.get('accession','') 
        else:
            run_id = "NO_RUNID"

        abstract = element.find(".//STUDY/DESCRIPTOR/STUDY_ABSTRACT")
        
        if abstract is None:
            abstract = "NO_ABSTRACT"
        else:
            abstract = abstract.text

        protocol = element.find(".//EXPERIMENT/DESIGN/LIBRARY_DESCRIPTOR/LIBRARY_CONSTRUCTION_PROTOCOL")
        if protocol is None:
            protocol = "NO_PROTOCOL"
        elif protocol.text is None:
            protocol = "NO_PROTOCOL"
        else:
            protocol = protocol.text

        row = [project_id, project_title, abstract,protocol,run_id, experiment_id, title, organism, assay_id]

        attributes = []
        for attribute in element.findall('.//SAMPLE/SAMPLE_ATTRIBUTES/SAMPLE_ATTRIBUTE'):
            key = attribute.find('TAG')
            if key is not None:
                key = key.text
            else:
                key = "NO_KEY"

            val = attribute.find('VALUE')
            if val is not None:
                val = val.text
            else:
                val = "NO_VAL"
           # attributes.extend([key,val])
            attributes.append(' : '.join([key,val]))
        if not attributes:
            attributes = ['NO','ATTRIBUTES']

#        category = classify(header,row)
#        header.append('category')
#        row.append(category)
        #expText = ' -- '.join([title] + attributes)
        
        row.append(' '.join(attributes))
        #row.append(expText)

        outRows.append(row)
                 
    outDF = pd.DataFrame(outRows, columns = header)

    print(f'{prjid} fetch complete...')
    return(outDF)