""" This is the code used in build_database.py to create and query
    a vector store that you create from a json-formatted database. 
    
    The database must have a "text" field for every given entry, as
    this is the field that will be converted to an embedding and
    stored as a document associated with that embedding."""


import chromadb
from sentence_transformers import SentenceTransformer
import time

class VectorStore:

    # creates a new persistent vector store if one under the specified name does not already exist
    def __init__(self, collection_name, db_path="./chroma"):
        self.embedding_model = SentenceTransformer('sentence-transformers/multi-qa-MiniLM-L6-cos-v1')
        self.chroma_client = chromadb.PersistentClient(path=db_path)
        self.collection = self.chroma_client.get_or_create_collection(name=collection_name)
        print(f"Referencing or creating chromaDB {collection_name}")

    # populate vector store using specified field from dataset, storing embeddings linked to their asscoiated documents 
    def populate_vectors(self, dataset):
        print("Populating the ChromaDB...")
        current_time = int(time.time())  
        for i, item in enumerate(dataset):
            combined_text = f"{item['text']}"  
            embeddings = self.embedding_model.encode(combined_text).tolist()
            unique_id = f"id_{i}_{current_time}"
            self.collection.add(embeddings=[embeddings], documents=[item['text']], ids=[unique_id])
        
        count = self.collection.count()
        print(f"Successfully added {count} documents to ChromaDB.")

    # convert the query phrase to an embedding used to query the vector store, returns top N results 
    def search_context(self, query, n_results=1):
        query_embeddings = self.embedding_model.encode(query).tolist()
        return self.collection.query(query_embeddings=query_embeddings, n_results=n_results)
    
    # delete collection
    def delete_collection(self):
        self.chroma_client.delete_collection(name=self.collection.name)