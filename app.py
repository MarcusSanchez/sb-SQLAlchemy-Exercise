"""Blogly application."""

from flask import Flask, redirect, render_template, request
from models import db, connect_db, Users, Posts

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

DEFAULT_IMAGE_URL = "https://www.freeiconspng.com/uploads/icon-user-" + \
                    "blue-symbol-people-person-generic--public-domain--21.png"

with app.app_context():
    connect_db(app)
    db.create_all()


@app.route('/')
def redirect_to_users():
    return redirect('/users')


# USERS ROUTES
@app.route('/users')
def render_users():
    users = Users.query.order_by(Users.last_name, Users.first_name).all()
    return render_template('users/users.jinja2', users=users)


@app.route('/users/new')
def render_new():
    return render_template('users/new.jinja2')


@app.route("/users/new", methods=["POST"])
def create_new_user():
    try:
        fn = request.form['first_name']
        ln = request.form['last_name']
    except KeyError:
        return render_template('error.jinja2', error="Missing form data")

    url = request.form.get('image_url', None)

    new_user = Users(
        first_name=fn,
        last_name=ln,
        image_url=url or DEFAULT_IMAGE_URL
    )

    db.session.add(new_user)
    db.session.commit()

    return redirect("/users")


@app.route('/users/<int:user_id>')
def render_user(user_id):
    user = Users.query.get(user_id)
    if user is None:
        return render_template('error.jinja2', error="User not found")
    return render_template('users/show.jinja2', user=user)


@app.route('/users/<int:user_id>/edit')
def render_user_edit(user_id):
    user = Users.query.get(user_id)
    if user is None:
        return render_template('error.jinja2', error="User not found")
    if user.image_url == DEFAULT_IMAGE_URL:
        user.image_url = ""
    return render_template('users/edit.jinja2', user=user)


@app.route('/users/<int:user_id>/edit', methods=["POST"])
def update_user(user_id):
    try:
        fn = request.form['first_name']
        ln = request.form['last_name']
    except KeyError:
        return render_template('error.jinja2', error="Missing form data")

    url = request.form.get('image_url', None)

    user = Users.query.get(user_id)
    if user is None:
        return render_template('error.jinja2', error="User not found")

    user.first_name = fn
    user.last_name = ln
    user.image_url = url or DEFAULT_IMAGE_URL

    db.session.add(user)
    db.session.commit()

    return redirect("/users")


@app.route('/users/<int:user_id>/delete', methods=["POST"])
def delete_user(user_id):
    user = Users.query.get(user_id)
    if user is None:
        return render_template('error.jinja2', error="User not found")

    db.session.delete(user)
    db.session.commit()

    return redirect("/users")


# POSTS ROUTES
@app.route('/users/<int:user_id>/posts/new')
def render_new_post(user_id):
    user = Users.query.get(user_id)
    if user is None:
        return render_template('error.jinja2', error="User not found")
    return render_template('posts/new.jinja2', user=user)


@app.route('/users/<int:user_id>/posts/new', methods=["POST"])
def create_new_post(user_id):
    user = Users.query.get(user_id)
    if user is None:
        return render_template('error.jinja2', error="User not found")

    try:
        title = request.form['title']
        content = request.form['content']
    except KeyError:
        return render_template('error.jinja2', error="Missing form data")

    post = Posts(title=title, content=content, user=user)

    db.session.add(post)
    db.session.commit()

    return redirect(f"/users/{user_id}")


@app.route('/posts/<int:post_id>')
def render_post(post_id):
    post = Posts.query.get(post_id)
    if post is None:
        return render_template('error.jinja2', error="Post not found")
    return render_template('posts/show.jinja2', post=post)


@app.route('/posts/<int:post_id>/edit')
def render_post_edit(post_id):
    post = Posts.query.get(post_id)
    if post is None:
        return render_template('error.jinja2', error="Post not found")
    return render_template('posts/edit.jinja2', post=post)


@app.route('/posts/<int:post_id>/edit', methods=["POST"])
def update_post(post_id):
    try:
        title = request.form['title']
        content = request.form['content']
    except KeyError:
        return render_template('error.jinja2', error="Missing form data")

    post = Posts.query.get(post_id)
    if post is None:
        return render_template('error.jinja2', error="Post not found")

    post.title = title
    post.content = content

    db.session.add(post)
    db.session.commit()

    return redirect(f"/posts/{post_id}")


@app.route('/posts/<int:post_id>/delete', methods=["POST"])
def delete_post(post_id):
    post = Posts.query.get(post_id)
    if post is None:
        return render_template('error.jinja2', error="Post not found")

    user_id = post.user.id

    db.session.delete(post)
    db.session.commit()

    return redirect(f"/users/{user_id}")
