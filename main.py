from flask import Flask, render_template, redirect, url_for, flash,get_flashed_messages
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import CreatePostForm,CreateRegisterForm,CreateLoginForm,Commentform
from flask_gravatar import Gravatar
from functools import wraps
from flask import abort


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##CONFIGURE TABLES
class BlogDb(UserMixin,db.Model):
    __tablename__ = "blog_db"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    posts=relationship("BlogPost",backref="author")
    comments=relationship('Comments',backref="author")


class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    # author = db.Column(db.String(250), nullable=False)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("blog_db.id"))
    comments = relationship('Comments', backref="parent_post")



class Comments(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    author_id=db.Column(db.Integer,db.ForeignKey("blog_db.id"))
    post_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id'))



gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)





# with app.app_context():
#     db.create_all()


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view="login"


@login_manager.user_loader
def load_user(user_id):
    return BlogDb.query.get(user_id)




@app.route('/')
def get_all_posts():

    posts = BlogPost.query.all()
    is_admin=0
    if current_user.is_authenticated:
        if current_user.id==1:
            is_admin=1
    return render_template("index.html", all_posts=posts,logged_in=current_user.is_authenticated,is_admin=is_admin,messages_json=get_flashed_messages())


@app.route('/register',methods=["GET","POST"])
def register():
    form=CreateRegisterForm()
    if form.validate_on_submit():
        if db.session.query(BlogDb).filter_by(email=form.email.data).count() < 1:
            new_user=BlogDb(
               email=form.email.data,
               password=generate_password_hash(form.password.data,method='pbkdf2', salt_length=8),
               name=form.name.data
            )
            db.session.add(new_user)
            db.session.commit()
            user=db.session.query(BlogDb).filter_by(email=form.email.data).first()
            login_user(user)
            return redirect(url_for("get_all_posts"))
        else:
            flash("you already signup with this email try to sign in!")
            return redirect(url_for('login'))
    return render_template("register.html",form=form,logged_in=current_user.is_authenticated)


@app.route('/login',methods=["GET","POST"])
def login():
    form=CreateLoginForm()
    if form.validate_on_submit():
        user=db.session.query(BlogDb).filter_by(email=form.email.data).first()
        print(user)
        if user:
            print(form.password.data)
            print(check_password_hash(form.password.data,user.password))
            if check_password_hash(user.password,form.password.data):
                flash("login successfull!")
                login_user(user)
                return redirect(url_for('get_all_posts'))
            else:
                flash("wrong password...try again!")

        else:
                flash("there is no user by this email...try again")


    return render_template("login.html",form=form,messages_json=get_flashed_messages(),logged_in=current_user.is_authenticated)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route("/post/<int:post_id>",methods=["GET","POST"])
def show_post(post_id):
    form=Commentform()
    requested_post = BlogPost.query.get(post_id)
    post_comments=db.session.query(Comments).filter_by(post_id=post_id).all()
    print(post_comments)
    print("helooo")
    for thing in requested_post.comments:
        print(thing.body)
    is_admin=0
    if current_user.is_authenticated:
        if current_user.id==1:
            is_admin=1
        if form.validate_on_submit():
            new_comment=Comments(
                body=form.comment.data,
                author_id=current_user.id,
                post_id=requested_post.id
            )
            db.session.add(new_comment)
            db.session.commit()


    return render_template("post.html", post=requested_post,logged_in=current_user.is_authenticated,is_admin=is_admin,form=form,comments=reversed(requested_post.comments))


@app.route("/about")
def about():
    return render_template("about.html",logged_in=current_user.is_authenticated)


@app.route("/contact")
def contact():
    return render_template("contact.html",logged_in=current_user.is_authenticated)




def is_admin(self):
    is_admin=0
    if self.id==1:
        is_admin=1
    return is_admin

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("you need to sign in")
                return redirect(url_for("login"))
            if not is_admin(current_user):
                return abort(403)

            return f(*args, **kwargs)
    return decorated_function




@app.route("/new-post",methods=["GET","POST"])
@admin_required
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form,logged_in=current_user.is_authenticated)






@app.route("/edit-post/<int:post_id>",methods=["GET","POST"])
@admin_required
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form,logged_in=current_user.is_authenticated)


@app.route("/delete/<int:post_id>")
@admin_required
def delete_post(post_id):
        post_to_delete = BlogPost.query.get(post_id)
        db.session.delete(post_to_delete)
        db.session.commit()
        return redirect(url_for('get_all_posts'))




if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
