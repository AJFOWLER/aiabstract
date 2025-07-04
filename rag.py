import sqlite3
import sqlite_vec
import rispy
import requests
from typing import List, Dict
#db setup
#Create the virtual table which will allow embedding to be held in SQLITE db

# +m  means aux field
# We will load all of our .ris files into this...
# Using a small mistral XB LLM for the embedding.
 # runs with --server --nobrowser --embedding

class RisRag:
    def __init__(self, embedding_url: str = "http://localhost:8080"):
        self.embedding_url = embedding_url
        self.endpoint = f"{embedding_url}/embedding"
        self.db_n = 'rag.db'

    def connect_db(self):
        db = sqlite3.connect(self.db_n)
        db.enable_load_extension(True)
        sqlite_vec.load(db)
        db.enable_load_extension(False) # Turn off extension loading
        return db
#Create the virtual table which will allow embedding to be held in SQLITE db

        # This may need to change depending on the vector length spat out by the llm; mistral does 1024
    def make_db_table(self):
        db = self.connect_db()
        cursor = db.cursor()
        cursor.execute("""
                   CREATE VIRTUAL TABLE files USING vec0(
                   embedding float[1024],
                   +file_name TEXT,
                   +content TEXT)
                   """
                  )
        db.commit()
        db.close()

    def load_ris_file(self, filepath: str) -> List[Dict]:
        with open(filepath, 'r', encoding='UTF-8') as f:
            entries = rispy.load(f)
        return entries

    def embed(self, content: str):
        payload = {
            'content':content,
        }
        try:
            response = requests.post(self.endpoint, json=payload)
            response.raise_for_status()
            embedding = response.json()['embedding']
            return embedding

        except requests.exceptions.RequestException as e:
            print(f"Error querying Llama: {e}")
            return None

    def embed_ris(self, entries: List[Dict]):
        db = self.connect_db()
        tracker = 0
        for file in entries:
            title = file.get('title')
            abstract = file.get('abstract') 
            content = title + str(abstract)
            # generate embedding
            embedding = self.embed(content)
            if embedding:
                #insert embedding into the embedding table!
                cur = db.cursor()
                cur.execute(
                    'INSERT INTO files (embedding, file_name, content) VALUES (?,?,?)',
                    (sqlite_vec.serialize_float32(embedding), title, content)
                    )
            tracker +=1
            print(tracker, '\n')
            db.commit()
        db.close()

    def query_embedded_data(self, query, k=5):
        db = self.connect_db()
        query_embedding = self.embed(query)
        cursor = db.cursor()
        rows = db.execute(""" 
                          SELECT file_name, content, distance
                          FROM files
                          WHERE embedding MATCH ?
                          and k=?
                          ORDER BY distance
                          """, [sqlite_vec.serialize_float32(query_embedding), k]).fetchall()
        #use where k=5 as five closest matches!
        selected = [x for x in rows]
        db.close()
        return selected
        #Then join this as context and stuff together!
