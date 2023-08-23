from flask import Flask, Blueprint, render_template, url_for, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    login_required,
    logout_user,
    current_user,
)
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SECRET_KEY"] = "8ghij938hy9gbh8gherg"

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)


class Post(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    is_reply = db.Column(db.Boolean, default=False, nullable=True)
    reply_id = db.Column(db.Integer, default=0, nullable=True)
    owner = db.Column(db.Integer)
    Title = db.Column(db.String(100), default="Untitled")
    Body = db.Column(db.String(1000), nullable=False)
    upvotes = db.Column(
        db.Integer, default=0, nullable=True
    )  # remember to change Title, Body, upvotes and downvotes to be mutable
    downvotes = db.Column(db.Integer, default=0, nullable=True)


class Tag(db.Model, UserMixin):
    id = db.Column(
        db.Integer, primary_key=True
    )  # don't rlly need this, just for the sake of having a unique id
    tag_string = db.Column(db.String(32), unique=True)
    tag_to = db.Column(db.Integer)


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


def retrieveTags(post_id):
    return [tag.tag_string for tag in Tag.query.filter_by(tag_to=post_id)]


class SignUpForm(FlaskForm):
    username = StringField(
        validators=[InputRequired(), Length(min=5, max=32)],
        render_kw={"placeholder": "Username"},
    )
    password = PasswordField(
        validators=[InputRequired(), Length(min=10, max=128)],
        render_kw={"placeholder": "Password"},
    )
    submit = SubmitField("Register")

    def username_exists(self, username):
        existing_user_name = User.query.filter_by(username=username.data).first()
        if existing_user_name:
            raise ValidationError("Username already exists!")


class LogInForm(FlaskForm):
    username = StringField(
        validators=[InputRequired(), Length(min=5, max=32)],
        render_kw={"placeholder": "Username"},
    )
    password = PasswordField(
        validators=[InputRequired(), Length(min=10, max=128)],
        render_kw={"placeholder": "Password"},
    )
    submit = SubmitField("Login")


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


class PostReplyForm(FlaskForm):
    Body = TextAreaField(
        validators=[InputRequired(), Length(min=5, max=1000)],
        render_kw={"placeholder": "Type your reply here: ", "rows": 10, "cols": 50},
    )

    submit = SubmitField("Post your reply")


@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    return redirect(url_for("login"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    f = SignUpForm()

    if f.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(f.password.data)
        new_user = User(username=f.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("home"))
    return render_template("signup.html", form=f)


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=User.query.get(current_user.id))


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


@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    user = User.query.filter_by(id=current_user.id).first()
    posts = Post.query.filter_by(is_reply=False).all()
    return render_template("home.html", user=user, posts=posts)


@app.route("/login", methods=["GET", "POST"])
def login():
    f = LogInForm()
    if f.validate_on_submit():
        user = User.query.filter_by(username=f.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, f.password.data):
                login_user(user)
                return redirect(url_for("home"))
    return render_template("login.html", form=f)


if __name__ == "__main__":
    app.run(debug=True)
