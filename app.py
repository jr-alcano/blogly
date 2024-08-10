from flask import Flask, render_template, redirect, url_for, request
from models import db, connect_db, User, Post, Tag, PostTag

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://johnalcano:jiBAi677@localhost/blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)

with app.app_context():
    db.create_all()


# Existing user and post routes here...

# Add tag routes
@app.route('/tags')
def list_tags():
    tags = Tag.query.all()
    return render_template('tags.html', tags=tags)


@app.route('/tags/new', methods=["GET", "POST"])
def add_tag():
    if request.method == "POST":
        new_tag = Tag(name=request.form['name'])
        db.session.add(new_tag)
        db.session.commit()
        return redirect(url_for('list_tags'))

    return render_template('new_tag.html')


@app.route('/tags/<int:tag_id>')
def show_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    return render_template('tag_detail.html', tag=tag)


@app.route('/tags/<int:tag_id>/edit', methods=["GET", "POST"])
def edit_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)

    if request.method == "POST":
        tag.name = request.form['name']
        db.session.commit()
        return redirect(url_for('list_tags'))

    return render_template('edit_tag.html', tag=tag)


@app.route('/tags/<int:tag_id>/delete', methods=["POST"])
def delete_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    return redirect(url_for('list_tags'))


# Update post routes to handle tags

@app.route('/posts/<int:post_id>')
def show_post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post_detail.html', post=post)


@app.route('/users/<int:user_id>/posts/new', methods=["GET", "POST"])
def add_post(user_id):
    user = User.query.get_or_404(user_id)
    tags = Tag.query.all()

    if request.method == "POST":
        tag_ids = request.form.getlist('tags')
        new_post = Post(
            title=request.form['title'],
            content=request.form['content'],
            user_id=user.id)
        db.session.add(new_post)
        db.session.commit()

        for tag_id in tag_ids:
            tag = Tag.query.get(tag_id)
            new_post.tags.append(tag)
        db.session.commit()

        return redirect(url_for('show_user', user_id=user.id))

    return render_template('new_post.html', user=user, tags=tags)


@app.route('/posts/<int:post_id>/edit', methods=["GET", "POST"])
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    tags = Tag.query.all()

    if request.method == "POST":
        post.title = request.form['title']
        post.content = request.form['content']
        tag_ids = request.form.getlist('tags')
        post.tags = [Tag.query.get(tag_id) for tag_id in tag_ids]
        db.session.commit()
        return redirect(url_for('show_post', post_id=post.id))

    return render_template('edit_post.html', post=post, tags=tags)


@app.route('/posts/<int:post_id>/delete', methods=["POST"])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('show_user', user_id=post.user_id))
