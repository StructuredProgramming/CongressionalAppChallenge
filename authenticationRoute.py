from imports import *
#from app import db, login_manager, bcrypt, User, app

def create_auth(db, login_manager, bcrypt, User, app):
    authentication = Blueprint('authentication', __name__, template_folder='templates')

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


    @authentication.route("/signup", methods=["GET", "POST"])
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


    @authentication.route("/login", methods=["GET", "POST"])
    def login():
        f = LogInForm()
        if f.validate_on_submit():
            user = User.query.filter_by(username=f.username.data).first()
            if user:
                if bcrypt.check_password_hash(user.password, f.password.data):
                    login_user(user)
                    return redirect(url_for("home"))
        return render_template("login.html", form=f)



    @authentication.route("/logout", methods=["GET", "POST"])
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("authentication.login"))

    return authentication