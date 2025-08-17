from rag import RisRag

def build_rag():
    rr = RisRag()

    # make db
    #rr.make_db_table()# may not be necessary if already run and virtual table exists..

    # readris
    loaded = rr.load_ris_file('post_duplicate_removal_22May2025.ris')

    # embed ris
    rr.embed_ris(loaded)

# To query:
def query_rag():
    rr = RisRag()
    query = "surgical treatment or surgery or operative procedures"
    surgery = rr.query_embedded_data(query,k=650)
    # Then do something like electronic cigarette use/vaping?
    electronic_cigarettes = 'vaping or electronic cigarettes or e-cigarette'
    import pdb; pdb.set_trace() 
    # can we do something to negate smoking?
    # Top interactions = most relevant?
    # sum ranks = lowest is most relevant?
    import json
    with open('embedding_results.json','w') as f:
        json.dump(select_,f)

#build_rag()
query_rag()
# Then python runrag.py
