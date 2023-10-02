from imports import *

from whoosh import index
from whoosh.fields import Schema, TEXT
from whoosh.index import create_in
from whoosh.qparser import QueryParser
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def create_viewPost(app, db, Post, User, login_manager):
    view_post = Blueprint('view_post', __name__, template_folder='templates')
    # Define the schema for the index
    schema = Schema(title=TEXT(stored=True), body=TEXT(stored=True))

    # Create the index in a directory named "indexdir"
    indexdir = "Whoosh_folder"
    if not index.exists_in(indexdir):
        ix = create_in(indexdir, schema)
    else:
        ix = index.open_dir(indexdir)


    def retrieveReplies(post_id):
        post = Post.query.filter_by(id=post_id).first()
        ans = {
            "title": post.Title,
            "body": post.Body,
            "username": User.query.get(post.owner).username,
            "id": post_id,
            "children": [],
        }
        for reply in Post.query.filter_by(reply_id=post_id, is_reply=True):
            ans["children"].append(retrieveReplies(reply.id))
        return ans

    class PostReplyForm(FlaskForm):
        Body = TextAreaField(
            validators=[InputRequired(), Length(min=5, max=1000)],
            render_kw={"placeholder": "Type your reply here: ", "rows": 10, "cols": 50},
        )

        # reply_to_id = HiddenField(reply_to_id)

        submit = SubmitField("Post your reply")
    @app.route("/displaypost/<int:id>", methods=["GET", "POST"])
    @login_required
    def displaypost(id):
        post = Post.query.get(int(id))
        f = PostReplyForm()

        if f.validate_on_submit():
            body = f.Body.data
            reply = Post(Body=body, is_reply=True, reply_id=id, owner=current_user.id)
            db.session.add(reply)
            db.session.commit()
            writer = ix.writer()

            writer.add_document(title=str(reply.id), body=body)

            writer.commit()
            return render_template(
                "displaypost.html", post=post, form=f, retrieveReplies=retrieveReplies
            )
        print(f.errors)
        return render_template(
            "displaypost.html", post=post, form=f, retrieveReplies=retrieveReplies
        )


    @app.route("/api/repliesforpost/<int:id>", methods=["GET"])
    @login_required
    def getrepliesforpost(id):
        print(retrieveReplies(id))
        return jsonify(retrieveReplies(id))
    return view_post