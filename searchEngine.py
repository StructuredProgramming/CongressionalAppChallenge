from imports import *

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




def get_params(user_query, vectorizer, documents, titles, tfidf_matrix, n=1):

    user_query_vector = vectorizer.transform([user_query])


    cosine_similarities = cosine_similarity(tfidf_matrix, user_query_vector)


    partitioned_indices = np.argpartition(cosine_similarities, -n, axis=0)[-n:]
    
    closest_match_indices = partitioned_indices[np.argsort(cosine_similarities[partitioned_indices].flatten(), axis=0)[::-1]]  
    
    closest_matches = [documents[idx[0]] for idx in closest_match_indices]
    t = [titles[idx[0]] for idx in closest_match_indices]

    return t

def searchEngineRoute(app, db, Post, User, Tag, login_manager):
    search_engine = Blueprint('searchEngine', __name__, template_folder='templates')

    @search_engine.route("/api/search/<string:query>", methods=["GET","POST"])
    def search(query):
        print(query)
        vectorizer = TfidfVectorizer()
        documents = [doc.get("body") for doc in ix.searcher().documents()]
        titles= [doc.get("title") for doc in ix.searcher().documents()]
        tfidf_matrix = vectorizer.fit_transform(documents)
        return get_params(query, vectorizer, documents, titles, tfidf_matrix, 2)

    @search_engine.route("/search-results", methods=["GET"])
    def resultsPage():
        query = request.args.get("query")
        titles = map(int, search(query))
        posts = Post.query.filter(Post.id.in_(titles)).all()

        posts_tags = {
            post.id: Tag.query.filter_by(tag_to=post.id)
            for post in posts
        }
        return render_template("searchResults.html", posts=posts, tags=posts_tags)


    return search_engine