
""" Run this script to test if your ChromaDB was successfully populated after running build_database.py, 
    or if you'd like to delete a specific ChromaDB collection"""

from vector_store import VectorStore
import chromadb

vector_store = VectorStore("PartSelect")
print(f"Number of Entries Present: {vector_store.collection.count()}") # prints total entry count
# print(vector_store.collection.peek()) # prints top 10 entries

# delete the database (irreversible)
# vector_store.delete_collection() # will delete the collection specified in line 8

