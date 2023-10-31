from imports import *

from flask import send_file

import os

from whoosh import index
from whoosh.fields import Schema, TEXT
from whoosh.index import create_in
from whoosh.qparser import QueryParser
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

import pickle

def create_viewPost(app, db, Post, User, Vote, login_manager):
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

    def numVotes(post_id):
        count = 0
        for vote in Vote.query.filter_by(vote_post=post_id).all():
            if vote.cur:
                count += 1
            else:
                count -= 1

        return count

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
        #User.query.filter_by(id=current_user.id).first()
        
        User.query.filter_by(id=current_user.id).first().add_post_viewed(id)
        db.session.commit()

        #print(User.query.filter_by(id=current_user.id).first().get_posts_viewed())
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
                "displaypost.html", post=post, form=f, retrieveReplies=retrieveReplies, numVotes=numVotes, send_file=send_file
            )
        print(f.errors)
        return render_template(
            "displaypost.html", post=post, form=f, retrieveReplies=retrieveReplies, numVotes=numVotes, send_file=send_file
        )

    @app.route("/downloadNotes/<int:id>", methods=["GET"])
    @login_required
    def donwloadNotes(id):
        post = Post.query.get(id)
        location = os.path.join(os.getcwd(),post.note_file_location)
        return send_file(location, as_attachment=True)

    @app.route("/api/repliesforpost/<int:id>", methods=["GET"])
    @login_required
    def getrepliesforpost(id):
        print(retrieveReplies(id))
        return jsonify(retrieveReplies(id))

    @app.route("/api/votesforpost/<int:post_id>", methods=["GET"])
    @login_required
    def votesforpost(post_id):
        return f'{numVotes(post_id)}'

    @app.route("/api/upvote/<int:post_id>/<int:voteType>", methods=["GET"])
    @login_required
    def upvote(post_id, voteType):
        vote=None
        if len(Vote.query.filter_by(vote_post=post_id, owner=current_user.id).all()):
            Vote.query.filter_by(vote_post=post_id, owner=current_user.id).delete()
            db.session.commit()
        if voteType==1: #upvote
            vote = Vote(vote_post=post_id, cur=True, owner=current_user.id)
        elif voteType==0: #downvote
            vote = Vote(vote_post=post_id, cur=False, owner=current_user.id)
        else:
            return "Invalid"
        db.session.add(vote)
        db.session.commit()        
        # return Vote.query.filter_by(vote_post=post_id, owner=current_user.id).all()
        return "Success"
    

    return view_post


