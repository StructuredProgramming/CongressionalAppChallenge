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




def get_params(posts_visited, total_posts):
    visited_content = [content for _, content in posts_visited]
    all_content = [content for _, content in total_posts]

    # Convert content to numerical vectors using TfidfVectorizer
    vectorizer = TfidfVectorizer(stop_words='english')
    content_vectors = vectorizer.fit_transform(all_content)

    # Compute cosine similarity between visited posts and all posts
    visited_vectors = vectorizer.transform(visited_content)
    cosine_similarities = cosine_similarity(visited_vectors, content_vectors)

    # Get indices of all posts and sort them based on similarity
    all_post_indices = range(len(total_posts))
    sorted_indices = sorted(all_post_indices, key=lambda x: cosine_similarities[0][x], reverse=True)

    # Get recommended posts based on sorted indices (excluding visited posts)
    recommended_posts = [(total_posts[i][0], total_posts[i][1]) for i in sorted_indices if total_posts[i] not in posts_visited]

    # Print recommended posts
    ans=[]
    print("Recommended Posts:")
    for title, content in recommended_posts:
        print("Title:", title)
        ans.append(title)
        print("Content:", content)
    return ans

def recommendRoute(app, db, Post, User, Tag, login_manager):
    recommender = Blueprint('recommender', __name__, template_folder='templates')

    @recommender.route("/api/recommend/<string:query>", methods=["GET","POST"])
    def recommend(query):
        #print(query)
        #print(documents)
        #print(titles)
        userid=query
        documents = [doc.get("body") for doc in ix.searcher().documents()]
        titles= [doc.get("title") for doc in ix.searcher().documents()]
        total_posts=[]
        for i in range(min(len(documents),len(titles))):
            total_posts.append((titles[i],documents[i]))
        visited_post_ids=User.query.filter_by(id=current_user.id).first().get_posts_viewed()
        posts_visited=[]
        for id in visited_post_ids:
            post = Post.query.get(id)
            posts_visited.append((id,post.Body))
        print(posts_visited)
        print(total_posts)
        return str(get_params(posts_visited, total_posts))

    return recommender