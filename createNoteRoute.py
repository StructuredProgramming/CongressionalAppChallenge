from imports import *


from whoosh import index
from whoosh.fields import Schema, TEXT
from whoosh.index import create_in
from whoosh.qparser import QueryParser
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from fileinput import filename
import pathlib
from flask_wtf.file import FileField, FileRequired

from werkzeug.utils import secure_filename



def create_note_route(db, login_manager, User, app, Post):
    create_note = Blueprint('create_note', __name__, template_folder='templates')

    # Define the schema for the index
    schema = Schema(title=TEXT(stored=True), body=TEXT(stored=True))

    # Create the index in a directory named "indexdir"
    indexdir = "Whoosh_folder"
    if not index.exists_in(indexdir):
        ix = create_in(indexdir, schema)
    else:
        ix = index.open_dir(indexdir)


    class PostNoteForm(FlaskForm):
        Title = StringField(
            validators=[InputRequired(), Length(min=5, max=100)],
            render_kw={"placeholder": "Enter the title here"},
        )
        Body = FileField(
            'Note File',
            
            # render_kw={"placeholder": "Enter your question here: ", "rows": 10, "cols": 50},
        )

        description = TextAreaField(
            validators=[InputRequired(), Length(min=5,max=2000)],
            render_kw={"placeholder": "Write a short description of the contents of these notes"}
        )

        submit = SubmitField("Post")

    @app.route("/createnote", methods=["GET", "POST"])
    @login_required
    def createnote():
        user = User.query.filter_by(id=current_user.id).first()
        f = PostNoteForm()
        print('got here')
        if f.validate_on_submit():
            print('also got here')
            title = f.Title.data
            body = f.Body.data
            desc = f.description.data
            # print(request.files)
            # body = request.files['Note file']
            # print(body)

            # f.file.data.save('./static/FileStorage/'+filename)
            # ext = (pathlib.Path(body.filename).suffix)
            # id='123'
            filename = secure_filename(body.filename)

            body.save('./static/FileStorage/'+filename)  
            post = Post(
                Title=title, Body=desc, is_reply=False, reply_id=0, is_note=True, owner=current_user.id, note_file_location='./static/FileStorage/'+filename
            )
            db.session.add(post)
            db.session.commit()
            writer = ix.writer()

            print(filename)

            writer.add_document(title=f'{post.id}', body=f'{title}\n{desc}')

            writer.commit()
            return redirect(url_for("home"))
        return render_template("createnote.html", form=f)
    return create_note