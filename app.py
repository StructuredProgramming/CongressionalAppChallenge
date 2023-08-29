from imports import *

from authenticationRoute import create_auth
from createPostRoute import create_post_route
from viewPost import create_viewPost
# from models import _User, _Post, _Tag

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

authentication=create_auth(db, login_manager, bcrypt, User, app)
app.register_blueprint(authentication)


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

create_post=create_post_route(db, login_manager, User, app, Post)
app.register_blueprint(create_post)


view_post=create_viewPost(app, db, Post, User, login_manager)
app.register_blueprint(view_post)

class Tag(db.Model, UserMixin):
    id = db.Column(
        db.Integer, primary_key=True
    )  # don't rlly need this, just for the sake of having a unique id
    tag_string = db.Column(db.String(32), unique=True)
    tag_to = db.Column(db.Integer)

def retrieveTags(post_id):
    return [tag.tag_string for tag in Tag.query.filter_by(tag_to=post_id)]

@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    return redirect(url_for("authentication.login"))

@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=User.query.get(current_user.id))

@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    user = User.query.filter_by(id=current_user.id).first()
    posts = Post.query.filter_by(is_reply=False).all()
    return render_template("home.html", user=user, posts=posts)

if __name__ == "__main__":
    app.run(debug=True)
