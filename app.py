"""Blogly application."""

from flask import Flask, redirect, render_template, request
from models import db, connect_db, Users, Posts, Tags

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
    tags = Tags.query.all()
    return render_template('posts/new.jinja2', user=user, tags=tags)


@app.route('/users/<int:user_id>/posts/new', methods=["POST"])
def create_new_post(user_id):
    try:
        title = request.form['title']
        content = request.form['content']
    except KeyError:
        return render_template('error.jinja2', error="Missing form data")

    tags_ids = request.form.getlist('tags')
    tags_ids = [int(tag_id) for tag_id in tags_ids]

    tags = Tags.query.filter(Tags.id.in_(tags_ids)).all()

    user = Users.query.get(user_id)
    if user is None:
        return render_template('error.jinja2', error="User not found")

    post = Posts(title=title, content=content, user=user, tags=tags)

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

    tags = Tags.query.all()
    return render_template('posts/edit.jinja2', post=post, tags=tags)


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

    tags_ids = request.form.getlist('tags')
    tags_ids = [int(tag_id) for tag_id in tags_ids]

    post.tags = Tags.query.filter(Tags.id.in_(tags_ids)).all()
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


# Tags Routes
@app.route('/tags')
def render_tags():
    tags = Tags.query.all()
    return render_template('tags/tags.jinja2', tags=tags)


@app.route('/tags/new')
def render_new_tag():
    posts = Posts.query.all()
    return render_template('tags/new.jinja2', posts=posts)


@app.route('/tags/new', methods=["POST"])
def create_new_tag():
    try:
        name = request.form['name']
    except KeyError:
        return render_template('error.jinja2', error="Missing form data")

    post_ids = request.form.getlist('posts')
    post_ids = [int(post_id) for post_id in post_ids]

    posts = Posts.query.filter(Posts.id.in_(post_ids)).all()

    tag = Tags(name=name, posts=posts)

    db.session.add(tag)
    db.session.commit()

    return redirect("/tags")


@app.route('/tags/<int:tag_id>')
def render_tag(tag_id):
    tag = Tags.query.get(tag_id)
    if tag is None:
        return render_template('error.jinja2', error="Tag not found")
    return render_template('tags/show.jinja2', tag=tag)


@app.route('/tags/<int:tag_id>/edit')
def render_tag_edit(tag_id):
    tag = Tags.query.get(tag_id)
    if tag is None:
        return render_template('error.jinja2', error="Tag not found")
    posts = Posts.query.all()
    return render_template('tags/edit.jinja2', tag=tag, posts=posts)


@app.route('/tags/<int:tag_id>/edit', methods=["POST"])
def update_tag(tag_id):
    try:
        name = request.form['name']
    except KeyError:
        return render_template('error.jinja2', error="Missing form data")

    post_ids = request.form.getlist('posts')
    post_ids = [int(post_id) for post_id in post_ids]

    posts = Posts.query.filter(Posts.id.in_(post_ids)).all()

    tag = Tags.query.get(tag_id)
    if tag is None:
        return render_template('error.jinja2', error="Tag not found")

    tag.name = name
    tag.posts = posts

    db.session.add(tag)
    db.session.commit()

    return redirect("/tags")


@app.route('/tags/<int:tag_id>/delete', methods=["POST"])
def delete_tag(tag_id):
    tag = Tags.query.get(tag_id)
    if tag is None:
        return render_template('error.jinja2', error="Tag not found")

    db.session.delete(tag)
    db.session.commit()

    return redirect("/tags")
