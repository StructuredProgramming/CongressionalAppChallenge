from imports import *

from authenticationRoute import create_auth
from createPostRoute import create_post_route
from createNoteRoute import create_note_route
from viewPost import create_viewPost
from searchEngine import searchEngineRoute
# from models import _User, _Post, _Tag

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SECRET_KEY"] = "8ghij938hy9gbh8gherg"

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "authentication.login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    credits=db.Column(db.Integer, default=0, nullable=True)

authentication=create_auth(db, login_manager, bcrypt, User, app)
app.register_blueprint(authentication)

class Vote(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    vote_post = db.Column(db.Integer, default=0, nullable=True)
    cur = db.Column(db.Boolean, default=False, nullable=True) #False means downvote, True means upvote
    owner = db.Column(db.Integer)

class Post(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    is_reply = db.Column(db.Boolean, default=False, nullable=True)
    reply_id = db.Column(db.Integer, default=0, nullable=True)
    is_note = db.Column(db.Boolean, default=False, nullable=True)
    note_file_location = db.Column(db.String(500), nullable=True)
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
    tag_color = db.Column(db.String(9)) #   #rrggbbaa


create_post=create_post_route(db, login_manager, User, app, Post)
app.register_blueprint(create_post)

create_note=create_note_route(db, login_manager, User, app, Post)
app.register_blueprint(create_note)

view_post=create_viewPost(app, db, Post, User, Vote, login_manager)
app.register_blueprint(view_post)

searchEngine=searchEngineRoute(app, db, Post, User, Tag, login_manager)
app.register_blueprint(searchEngine)



def retrieveTags(post_id):
    return [tag.tag_string for tag in Tag.query.filter_by(tag_to=post_id)]

def numVotes(post_id):
        count = 0
        for vote in Vote.query.filter_by(vote_post=post_id).all():
            if vote.cur:
                count += 1
            else:
                count -= 1

        return count

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
    notes = Post.query.filter_by(is_note=True).all()
    posts_tags = {
        post.id: list(Tag.query.filter_by(tag_to=post.id))
        for post in posts
    }
    return render_template("home.html", user=user, posts=posts, tags=posts_tags, numVotes=numVotes)

if __name__ == "__main__":
    app.run(debug=True)