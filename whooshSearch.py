                                     
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




vectorizer = TfidfVectorizer()
documents = [doc.get("body") for doc in ix.searcher().documents()]
titles= [doc.get("title") for doc in ix.searcher().documents()]
tfidf_matrix = vectorizer.fit_transform(documents)

def get_params(user_query, n=1):

    user_query_vector = vectorizer.transform([user_query])


    cosine_similarities = cosine_similarity(tfidf_matrix, user_query_vector)


    partitioned_indices = np.argpartition(cosine_similarities, -n, axis=0)[-n:]
    
    closest_match_indices = partitioned_indices[np.argsort(cosine_similarities[partitioned_indices].flatten(), axis=0)[::-1]]  
    
    closest_matches = [documents[idx[0]] for idx in closest_match_indices]
    t = [titles[idx[0]] for idx in closest_match_indices]

    return t

prompt = input("Enter a topic: ")


n = int(input("Enter the number of results to return: "))

# Invoke the function and print the output
output = get_params(prompt, n)
for i, result in enumerate(output, start=1):
    print(f"Result {i}:\n{result}\n")