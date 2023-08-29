from imports import *


def create_post_route(db, login_manager, User, app, Post):
    create_post = Blueprint('create_post', __name__, template_folder='templates')


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
            return redirect(url_for("home"))
        return render_template("createpost.html", form=f)
    return create_post