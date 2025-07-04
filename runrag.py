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
    query = "surgical treatment or surgery"
    select_ = rr.query_embedded_data(query,k=100)
    import pdb; pdb.set_trace() 

#build_rag()
query_rag()
# Then python runrag.py
