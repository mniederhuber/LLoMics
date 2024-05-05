import fetch
import annotate

prjid = 'PRJNA643248'
meta = fetch.fetch(prjid)

print(meta)

experiment_metadata = meta[['project_id','experiment_id', 'title', 'attributes']]
project_metadata = meta[['project_id','project_title','abstract','protocol']].drop_duplicates(subset='project_id', keep = 'first')

annotation = annotate.main(model = 'gpt-3.5-turbo-0125',
                               prjMeta = project_metadata,
                               expMeta = experiment_metadata)

print(annotation)