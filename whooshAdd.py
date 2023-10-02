from whoosh import index
from whoosh.fields import Schema, TEXT
from whoosh.index import create_in
from whoosh.qparser import QueryParser
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Define the schema for the index
schema = Schema(title=TEXT(stored=True), body=TEXT(stored=True))

# Create the index in a directory named "indexdir"
indexdir = "Whoosh_folder"
if not index.exists_in(indexdir):
    ix = create_in(indexdir, schema)
else:
    ix = index.open_dir(indexdir)


writer = ix.writer()
writer.add_document(title="Document 1", body="World War 2 started in 1964, during which the Allies fought the Axis Powers.")
writer.add_document(title="Document 2", body="The brain is an organ in your head. It helps you think and perform various tasks.")
writer.add_document(title="Document 3", body="The topelitz square is one of the most difficult and intricate mathematics problems with various proposed solutions.")
writer.add_document(title="Document 4", body="The travelling salesman problem is one of the most difficult and complex computer science problems.")

writer.commit()
