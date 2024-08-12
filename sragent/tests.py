#import pandas as pd
import sragent

#prjid = 'PRJNA643248'
#meta = fetch.fetch(prjid)

#model = 'gpt-4-0125-preview'
model = 'gpt-4o-mini'
#model = 'gpt-3.5-turbo-0125'
sragent.annotate('PRJNA262623', model)
#projects = pd.read_csv('scratch/projects-ALLHistone.csv')
#prjids = projects['project_id'].tolist()

#print(prjids)

#all_meta = pd.concat([fetch.fetch(prj) for prj in prjids]).drop_duplicates(subset='experiment_id', keep = 'first')

#experiment_metadata = all_meta[['project_id','experiment_id', 'title', 'attributes']]
#project_metadata = all_meta[['project_id','project_title','abstract','protocol']].drop_duplicates(subset='project_id', keep = 'first')

#experiment_metadata.to_csv('scratch/experiment_metaData-AllHistone.tsv', index = False, sep = '\t')
#project_metadata.to_csv('scratch/project_metaData-AllHistone.tsv', index = False, sep = '\t')
#all_meta.to_csv('scratch/all_metaData-AllHistone.tsv', index = False, sep = '\t')

#projectdf = pd.read_csv('scratch/project_metaData-AllHistone.tsv', sep = '\t')
#experimentdf = pd.read_csv('scratch/experiment_metaData-AllHistone.tsv', sep = '\t')
#print(projectdf)
#for n in range(3):
#    
#    project_id = random.choice(projectdf['project_id'])
##    project_id = 'PRJNA643248'
#    print(project_id)
#    prjMeta = projectdf[projectdf['project_id'] == project_id]
#    expMeta = experimentdf[experimentdf['project_id'] == project_id]
#
#    annotation = annotate.main(model = model,
#                               prjMeta = prjMeta,
#                               expMeta = expMeta,
#                               sample=15)
#
#
#    annotation.to_csv(f'scratch/240624_{model}_{n+1}.csv', index = False)
#    print(annotation)
#