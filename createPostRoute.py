from imports import *


from whoosh import index
from whoosh.fields import Schema, TEXT
from whoosh.index import create_in
from whoosh.qparser import QueryParser
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np



def create_post_route(db, login_manager, User, app, Post):
    create_post = Blueprint('create_post', __name__, template_folder='templates')

    # Define the schema for the index
    schema = Schema(title=TEXT(stored=True), body=TEXT(stored=True))

    # Create the index in a directory named "indexdir"
    indexdir = "Whoosh_folder"
    if not index.exists_in(indexdir):
        ix = create_in(indexdir, schema)
    else:
        ix = index.open_dir(indexdir)


    class PostQuestionForm(FlaskForm):
        Title = StringField(
            validators=[InputRequired(), Length(min=5, max=100)],
            render_kw={"placeholder": "Enter the title here"},
        )
        Body = TextAreaField(
            validators=[InputRequired(), Length(min=5, max=1000)],
            render_kw={"placeholder": "Enter your question here: ", "rows": 10, "cols": 50},
        )

        submit = SubmitField("Post")

    @app.route("/createpost", methods=["GET", "POST"])
    @login_required
    def createpost():
        user = User.query.filter_by(id=current_user.id).first()
        f = PostQuestionForm()
        if f.validate_on_submit():
            title = f.Title.data
            body = f.Body.data
            post = Post(
                Title=title, Body=body, is_reply=False, reply_id=0, owner=current_user.id
            )
            db.session.add(post)
            db.session.commit()
            writer = ix.writer()

            writer.add_document(title=f'{post.id}', body=f'{title}\n{body}')

            writer.commit()
            return redirect(url_for("home"))
        return render_template("createpost.html", form=f)
    return create_post