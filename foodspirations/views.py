# -*- coding: utf-8 -*-
import os.path
import json
from flask import render_template, flash
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from .database import User, session
from flask import request, redirect, url_for, send_from_directory, Response
from .utils import upload_path

from . import app
from . import decorators
from .database import session, Post, PictureFile, Comment, Like
from flask_login import login_required
from flask_login import current_user

UPLOAD_FOLDER = '/home/ubuntu/workspace/thinkful/projects/foodspirations/foodspirations/uploads'
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif', 'PDF', 'PNG', 'JPG', 'JPEG', 'GIF'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

PAGINATE_BY=10

def allowed_file(filename):
    return '.' in filename and \
          filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route("/")
def homepage():
    if current_user.is_authenticated:
         authenticate = True
         name = current_user.username
    else:
         authenticate = False
         name = "404"
    return render_template("homepage.html", authenticate=authenticate, name=name)
    
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("homepage"))
    
@app.route("/login", methods=["GET"])
def login_get():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login_post():
    email = request.form["email"]
    password = request.form["password"]
    
    user = session.query(User).filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        flash("Incorrect username or password", "danger")
        return redirect(url_for("login_get"))

    login_user(user)
    return redirect(request.args.get('next') or url_for("homepage"))
    
@app.route("/signup", methods=["GET"])
def signup_get():
    return render_template("signup.html")
    
@app.route("/signup", methods=["POST"])
def signup_post():
    password = request.form["password"]
    confirm_password = request.form["confirm-password"]
    if password != confirm_password:
        flash("Passwords don't match, please try again", "danger")
        return redirect(url_for("signup_get"))
    
    username = request.form["username"]
    same_username = session.query(User).filter_by(username=username).count()
    
    if same_username:
        flash("The username has already been taken, please choose another", "danger")
        return redirect(url_for("signup_get"))
        
    email = request.form["email"]
    same_email = session.query(User).filter_by(email=email).count()
    
    if same_email:
        flash("You entered an email address that has already been taken. Please try again", "danger")
        return redirect(url_for("signup_get"))

    user = User()
    user.username = request.form["username"]
    user.email = request.form["email"]
    user.password = generate_password_hash(request.form["password"])
    
    session.add(user)
    session.commit()
    login_user(user)
    return redirect(url_for("homepage"))
    
@app.route("/add/post", methods=["GET"])
@login_required
def add_post_get():
    return render_template("add_post.html")

@app.route("/add/post", methods=["POST"])
@login_required
def add_post_post():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
        
    file = request.files['file']
        
    if file.filename == '':
        flash('Please select a file')
        return redirect(request.url)
        
    if file and not allowed_file(file.filename):
        flash('Not an allowed file. Please try again')
        return redirect(request.url)
        
    file1 = PictureFile(filename=file.filename)
    session.add(file1)
    session.commit()
    
    post = Post(
        name=request.form["name"],
        ingredients=request.form["ingredients"],
        steps=request.form["steps"],
        ethnic_region=request.form["ethnic_region"],
        pic_filename=file1.filename,
        picturefile_id=file1.id,
        author=current_user
    )
    
    session.add(post)
    session.commit()
    
    print (post.name)
    print (post.pic_filename)
            
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        if post.ethnic_region == "American":
            return redirect(url_for("american_tab"))
        
        if post.ethnic_region == "Asian":
            return redirect(url_for("asian_tab"))
            
        if post.ethnic_region == "Greek":
            return redirect(url_for("greek_tab"))
            
        if post.ethnic_region == "French":
            return redirect(url_for("french_tab"))
            
        if post.ethnic_region == "Thai":
            return redirect(url_for("thai_tab"))
            
        if post.ethnic_region == "Mediterranean":
            return redirect(url_for("mediterranean_tab"))
            
        if post.ethnic_region == "Italian":
            return redirect(url_for("italian_tab"))
            
        if post.ethnic_region == "Indian":
            return redirect(url_for("indian_tab"))
            
        if post.ethnic_region == "Mexican":
            return redirect(url_for("mexican_tab"))
            
        else:
            return redirect(url_for("other_tab"))

    flash('Am error occured. Please try again.')
    return redirect(request.url)

@app.route("/american")
@app.route("/american/page/<int:page>")
def american_tab(page=1):
    page_index = page - 1

    count = session.query(Post).filter_by(ethnic_region="American").count()
    
    if count==0:
        empty=True
    else:
        empty=False

    start = page_index * PAGINATE_BY
    end = start + PAGINATE_BY

    total_pages = (count - 1) // PAGINATE_BY + 1
    has_next = page_index < total_pages - 1
    has_prev = page_index > 0

    posts = session.query(Post).filter_by(ethnic_region="American")
    posts = posts.order_by(Post.likes.desc())
    posts = posts[start:end]
    
    if current_user.is_authenticated:
         authenticate = True
         name = current_user.username
         user_likes=session.query(Like).filter_by(user_id=current_user.id)
    else:
         authenticate = False
         name = "404"
         user_likes=[]
         
    print(count)
    print(empty)
         
    return render_template("display_posts.html",
        posts=posts,
        has_next=has_next,
        has_prev=has_prev,
        page=page,
        total_pages=total_pages,
        authenticate=authenticate,
        name=name,
        user_likes=user_likes,
        empty=empty
    )
    
@app.route("/asian")
@app.route("/asian/page/<int:page>")
def asian_tab(page=1):
    page_index = page - 1

    count = session.query(Post).filter_by(ethnic_region="Asian").count()
    
    if count==0:
        empty=True
    else:
        empty=False

    start = page_index * PAGINATE_BY
    end = start + PAGINATE_BY

    total_pages = (count - 1) // PAGINATE_BY + 1
    has_next = page_index < total_pages - 1
    has_prev = page_index > 0

    posts = session.query(Post).filter_by(ethnic_region="Asian")
    posts = posts.order_by(Post.likes.desc())
    posts = posts[start:end]
    
    if current_user.is_authenticated:
         authenticate = True
         name = current_user.username
         user_likes=session.query(Like).filter_by(user_id=current_user.id)
    else:
         authenticate = False
         name = "404"
         user_likes=[]
         
    return render_template("display_posts.html",
        posts=posts,
        has_next=has_next,
        has_prev=has_prev,
        page=page,
        total_pages=total_pages,
        authenticate=authenticate,
        name=name,
        user_likes=user_likes,
        empty=empty
        )
    
@app.route("/greek")
@app.route("/greek/page/<int:page>")
def greek_tab(page=1):
    page_index = page - 1

    count = session.query(Post).filter_by(ethnic_region="Greek").count()
    
    if count==0:
        empty=True
    else:
        empty=False

    start = page_index * PAGINATE_BY
    end = start + PAGINATE_BY

    total_pages = (count - 1) // PAGINATE_BY + 1
    has_next = page_index < total_pages - 1
    has_prev = page_index > 0

    posts = session.query(Post).filter_by(ethnic_region="Greek")
    posts = posts.order_by(Post.likes.desc())
    posts = posts[start:end]
    
    if current_user.is_authenticated:
         authenticate = True
         name = current_user.username
         user_likes=session.query(Like).filter_by(user_id=current_user.id)
    else:
         authenticate = False
         name = "404"
         user_likes=[]
         
    return render_template("display_posts.html",
        posts=posts,
        has_next=has_next,
        has_prev=has_prev,
        page=page,
        total_pages=total_pages,
        authenticate=authenticate,
        name=name,
        user_likes=user_likes,
        empty=empty
    )
    
@app.route("/french")
@app.route("/french/page/<int:page>")
def french_tab(page=1):
    page_index = page - 1

    count = session.query(Post).filter_by(ethnic_region="French").count()
    
    if count==0:
        empty=True
    else:
        empty=False

    start = page_index * PAGINATE_BY
    end = start + PAGINATE_BY

    total_pages = (count - 1) // PAGINATE_BY + 1
    has_next = page_index < total_pages - 1
    has_prev = page_index > 0

    posts = session.query(Post).filter_by(ethnic_region="French")
    posts = posts.order_by(Post.likes.desc())
    posts = posts[start:end]
    
    if current_user.is_authenticated:
         authenticate = True
         name = current_user.username
         user_likes=session.query(Like).filter_by(user_id=current_user.id)
    else:
         authenticate = False
         name = "404"
         user_likes=[]
         
    return render_template("display_posts.html",
        posts=posts,
        has_next=has_next,
        has_prev=has_prev,
        page=page,
        total_pages=total_pages,
        authenticate=authenticate,
        name=name,
        user_likes=user_likes,
        empty=empty
    )
    
@app.route("/thai")
@app.route("/thai/page/<int:page>")
def thai_tab(page=1):
    page_index = page - 1

    count = session.query(Post).filter_by(ethnic_region="Thai").count()
    
    if count==0:
        empty=True
    else:
        empty=False

    start = page_index * PAGINATE_BY
    end = start + PAGINATE_BY

    total_pages = (count - 1) // PAGINATE_BY + 1
    has_next = page_index < total_pages - 1
    has_prev = page_index > 0

    posts = session.query(Post).filter_by(ethnic_region="Thai")
    posts = posts.order_by(Post.likes.desc())
    posts = posts[start:end]
    
    if current_user.is_authenticated:
         authenticate = True
         name = current_user.username
         user_likes=session.query(Like).filter_by(user_id=current_user.id)
    else:
         authenticate = False
         name = "404"
         user_likes=[]
         
    return render_template("display_posts.html",
        posts=posts,
        has_next=has_next,
        has_prev=has_prev,
        page=page,
        total_pages=total_pages,
        authenticate=authenticate,
        name=name,
        user_likes=user_likes,
        empty=empty
    )
    
@app.route("/mediterranean")
@app.route("/mediterranean/page/<int:page>")
def mediterranean_tab(page=1):
    page_index = page - 1

    count = session.query(Post).filter_by(ethnic_region="Mediterranean").count()
    
    if count==0:
        empty=True
    else:
        empty=False

    start = page_index * PAGINATE_BY
    end = start + PAGINATE_BY

    total_pages = (count - 1) // PAGINATE_BY + 1
    has_next = page_index < total_pages - 1
    has_prev = page_index > 0

    posts = session.query(Post).filter_by(ethnic_region="Mediterranean")
    posts = posts.order_by(Post.likes.desc())
    posts = posts[start:end]
    
    if current_user.is_authenticated:
         authenticate = True
         name = current_user.username
         user_likes=session.query(Like).filter_by(user_id=current_user.id)
    else:
         authenticate = False
         name = "404"
         user_likes=[]
         
    return render_template("display_posts.html",
        posts=posts,
        has_next=has_next,
        has_prev=has_prev,
        page=page,
        total_pages=total_pages,
        authenticate=authenticate,
        name=name,
        user_likes=user_likes,
        empty=empty
    )
    
@app.route("/italian")
@app.route("/italian/page/<int:page>")
def italian_tab(page=1):
    page_index = page - 1

    count = session.query(Post).filter_by(ethnic_region="Italian").count()
    
    if count==0:
        empty=True
    else:
        empty=False

    start = page_index * PAGINATE_BY
    end = start + PAGINATE_BY

    total_pages = (count - 1) // PAGINATE_BY + 1
    has_next = page_index < total_pages - 1
    has_prev = page_index > 0

    posts = session.query(Post).filter_by(ethnic_region="Italian")
    posts = posts.order_by(Post.likes.desc())
    posts = posts[start:end]
    
    if current_user.is_authenticated:
         authenticate = True
         name = current_user.username
         user_likes=session.query(Like).filter_by(user_id=current_user.id)
    else:
         authenticate = False
         name = "404"
         user_likes=[]
         
    return render_template("display_posts.html",
        posts=posts,
        has_next=has_next,
        has_prev=has_prev,
        page=page,
        total_pages=total_pages,
        authenticate=authenticate,
        name=name,
        user_likes=user_likes,
        empty=empty
    )
    
@app.route("/indian")
@app.route("/indian/page/<int:page>")
def indian_tab(page=1):
    page_index = page - 1

    count = session.query(Post).filter_by(ethnic_region="Indian").count()
    
    if count==0:
        empty=True
    else:
        empty=False

    start = page_index * PAGINATE_BY
    end = start + PAGINATE_BY

    total_pages = (count - 1) // PAGINATE_BY + 1
    has_next = page_index < total_pages - 1
    has_prev = page_index > 0

    posts = session.query(Post).filter_by(ethnic_region="Indian")
    posts = posts.order_by(Post.likes.desc())
    posts = posts[start:end]
    
    if current_user.is_authenticated:
         authenticate = True
         name = current_user.username
         user_likes=session.query(Like).filter_by(user_id=current_user.id)
    else:
         authenticate = False
         name = "404"
         user_likes=[]
         
    return render_template("display_posts.html",
        posts=posts,
        has_next=has_next,
        has_prev=has_prev,
        page=page,
        total_pages=total_pages,
        authenticate=authenticate,
        name=name,
        user_likes=user_likes,
        empty=empty
    )
    
@app.route("/mexican")
@app.route("/mexican/page/<int:page>")
def mexican_tab(page=1):
    page_index = page - 1

    count = session.query(Post).filter_by(ethnic_region="Mexican").count()
    
    if count==0:
        empty=True
    else:
        empty=False

    start = page_index * PAGINATE_BY
    end = start + PAGINATE_BY

    total_pages = (count - 1) // PAGINATE_BY + 1
    has_next = page_index < total_pages - 1
    has_prev = page_index > 0

    posts = session.query(Post).filter_by(ethnic_region="Mexican")
    posts = posts.order_by(Post.likes.desc())
    posts = posts[start:end]
    
    if current_user.is_authenticated:
         authenticate = True
         name = current_user.username
         user_likes=session.query(Like).filter_by(user_id=current_user.id)
    else:
         authenticate = False
         name = "404"
         user_likes=[]
         
    return render_template("display_posts.html",
        posts=posts,
        has_next=has_next,
        has_prev=has_prev,
        page=page,
        total_pages=total_pages,
        authenticate=authenticate,
        name=name,
        user_likes=user_likes,
        empty=empty
    )
    
@app.route("/other")
@app.route("/other/page/<int:page>")
def other_tab(page=1):
    page_index = page - 1

    count = session.query(Post).filter_by(ethnic_region="Other").count()
    
    if count==0:
        empty=True
    else:
        empty=False

    start = page_index * PAGINATE_BY
    end = start + PAGINATE_BY

    total_pages = (count - 1) // PAGINATE_BY + 1
    has_next = page_index < total_pages - 1
    has_prev = page_index > 0

    posts = session.query(Post).filter_by(ethnic_region="Other")
    posts = posts.order_by(Post.likes.desc())
    posts = posts[start:end]
    
    if current_user.is_authenticated:
         authenticate = True
         name = current_user.username
         user_likes=session.query(Like).filter_by(user_id=current_user.id)
    else:
         authenticate = False
         name = "404"
         user_likes=[]
         
    return render_template("display_posts.html",
        posts=posts,
        has_next=has_next,
        has_prev=has_prev,
        page=page,
        total_pages=total_pages,
        authenticate=authenticate,
        name=name,
        user_likes=user_likes,
        empty=empty
    )

@app.route("/post/<id>/edit", methods=["GET"])
@login_required
def edit_post_get(id):
    post = session.query(Post).filter_by(id=id).first()
    
    if current_user.username != post.author.username:
        return redirect(url_for("homepage"))
        
    return render_template("edit_post.html", post=post)
    
@app.route("/post/<id>/edit", methods=["POST"])
@login_required
def edit_post_post(id):
    post = session.query(Post).filter_by(id=id).first()
    post.name=request.form["name"]
    post.ingredients=request.form["ingredients"]
    post.steps=request.form["steps"]
    post.ethnic_region=request.form["ethnic_region"]
    
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    
    print("file is in request.files")
        
    if file.filename == '':
        session.commit()
        post = session.query(Post).filter_by(id=id).first()
    
        if post.ethnic_region == "American":
            return redirect(url_for("american_tab"))
            
        if post.ethnic_region == "Asian":
            return redirect(url_for("asian_tab"))
            
        if post.ethnic_region == "Greek":
            return redirect(url_for("greek_tab"))
            
        if post.ethnic_region == "French":
            return redirect(url_for("french_tab"))
            
        if post.ethnic_region == "Thai":
            return redirect(url_for("thai_tab"))
            
        if post.ethnic_region == "Mediterranean":
            return redirect(url_for("mediterranean_tab"))
            
        if post.ethnic_region == "Italian":
            return redirect(url_for("italian_tab"))
            
        if post.ethnic_region == "Indian":
            return redirect(url_for("indian_tab"))
            
        if post.ethnic_region == "Mexican":
            return redirect(url_for("mexican_tab"))
            
        else:
            return redirect(url_for("other_tab"))
            
    if file and not allowed_file(file.filename):
        flash('Not an allowed file. Please try again')
        return redirect(request.url)
        
    file1 = PictureFile(filename=file.filename)
    session.add(file1)
    session.commit()
    post.pic_filename=file.filename
    post.picturefile_id=file1.id
    
    session.commit()
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
    post = session.query(Post).filter_by(id=id).first()

    if post.ethnic_region == "American":
        return redirect(url_for("american_tab"))
    
    if post.ethnic_region == "Asian":
        return redirect(url_for("asian_tab"))
        
    if post.ethnic_region == "Greek":
        return redirect(url_for("greek_tab"))
        
    if post.ethnic_region == "French":
        return redirect(url_for("french_tab"))
        
    if post.ethnic_region == "Thai":
        return redirect(url_for("thai_tab"))
        
    if post.ethnic_region == "Mediterranean":
        return redirect(url_for("mediterranean_tab"))
        
    if post.ethnic_region == "Italian":
        return redirect(url_for("italian_tab"))
        
    if post.ethnic_region == "Indian":
        return redirect(url_for("indian_tab"))
        
    if post.ethnic_region == "Mexican":
        return redirect(url_for("mexican_tab"))
        
    return redirect(url_for("other_tab"))
        
@app.route("/post/<id>/delete", methods=["GET"])
@login_required
def delete_post_get(id):
    post=session.query(Post).filter_by(id=id).first()
    if current_user.username != post.author.username:
        return redirect(url_for("homepage"))
        
    return render_template("delete_post.html", post=post)
    
@app.route("/post/<id>/delete", methods=["POST"])
@login_required
def delete_post_post(id):
    post=session.query(Post).filter_by(id=id).first()
    session.delete(post)
    session.commit()
    
    if post.ethnic_region == "American":
        return redirect(url_for("american_tab"))
        
    if post.ethnic_region == "Asian":
        return redirect(url_for("asian_tab"))
        
    if post.ethnic_region == "Greek":
        return redirect(url_for("greek_tab"))
        
    if post.ethnic_region == "French":
        return redirect(url_for("french_tab"))
        
    if post.ethnic_region == "Thai":
        return redirect(url_for("thai_tab"))
        
    if post.ethnic_region == "Mediterranean":
        return redirect(url_for("mediterranean_tab"))
        
    if post.ethnic_region == "Italian":
        return redirect(url_for("italian_tab"))
        
    if post.ethnic_region == "Indian":
        return redirect(url_for("indian_tab"))
        
    if post.ethnic_region == "Mexican":
        return redirect(url_for("mexican_tab"))
        
    else:
        return redirect(url_for("other_tab"))
        
@app.route("/unlike/<id>")
def unliked_post(id):
    post=session.query(Post).filter_by(id=id).first()
    post.likes = post.likes-1
    session.commit()
    
    like=session.query(Like).filter_by(post_id=id).filter_by(user_id=current_user.id).first()
    session.delete(like)
    session.commit()
    
    if post.ethnic_region == "American":
        return redirect(url_for("american_tab"))
        
    if post.ethnic_region == "Asian":
        return redirect(url_for("asian_tab"))
        
    if post.ethnic_region == "Greek":
        return redirect(url_for("greek_tab"))
        
    if post.ethnic_region == "French":
        return redirect(url_for("french_tab"))
        
    if post.ethnic_region == "Thai":
        return redirect(url_for("thai_tab"))
        
    if post.ethnic_region == "Mediterranean":
        return redirect(url_for("mediterranean_tab"))
        
    if post.ethnic_region == "Italian":
        return redirect(url_for("italian_tab"))
        
    if post.ethnic_region == "Indian":
        return redirect(url_for("indian_tab"))
        
    if post.ethnic_region == "Mexican":
        return redirect(url_for("mexican_tab"))
        
    else:
        return redirect(url_for("other_tab"))
       
       
@app.route("/like/<id>")
def liked_post(id):
    post=session.query(Post).filter_by(id=id).first()
    post.likes = post.likes+1
    session.commit()
    like = Like(post_id=post.id, user_id=current_user.id)
    session.add(like)
    session.commit()
    
    if post.ethnic_region == "American":
        return redirect(url_for("american_tab"))
        
    if post.ethnic_region == "Asian":
        return redirect(url_for("asian_tab"))
        
    if post.ethnic_region == "Greek":
        return redirect(url_for("greek_tab"))
        
    if post.ethnic_region == "French":
        return redirect(url_for("french_tab"))
        
    if post.ethnic_region == "Thai":
        return redirect(url_for("thai_tab"))
        
    if post.ethnic_region == "Mediterranean":
        return redirect(url_for("mediterranean_tab"))
        
    if post.ethnic_region == "Italian":
        return redirect(url_for("italian_tab"))
        
    if post.ethnic_region == "Indian":
        return redirect(url_for("indian_tab"))
        
    if post.ethnic_region == "Mexican":
        return redirect(url_for("mexican_tab"))
        
    else:
        return redirect(url_for("other_tab"))
    
@app.route("/post/<id>", methods=["GET"])
def view_post(id):
    post = session.query(Post).filter_by(id=id).first()
    comments = session.query(Comment).filter_by(post_id=id)
    comments_number = session.query(Comment).filter_by(post_id=id).count()
    if current_user.is_authenticated:
         name = current_user.username
    else:
         name = "404"
    return render_template("view_single_post.html", post=post, name=name, comments=comments, comments_number=comments_number)
    
@app.route("/post/<id>", methods=['POST'])
@login_required
def add_comment_post(id):
    post = session.query(Post).filter_by(id=id).first()
    if current_user.is_authenticated:
         name = current_user.username
    else:
         name = "404"
         
    comment = Comment(content=request.form["comment"], author=name, post_id=post.id)
    session.add(comment)
    session.commit()
    
    return redirect(url_for('view_post', id=id))

    