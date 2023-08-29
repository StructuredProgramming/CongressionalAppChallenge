from imports import *


def create_viewPost(app, db, Post, User, login_manager):
    view_post = Blueprint('view_post', __name__, template_folder='templates')

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